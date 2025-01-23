#!/usr/bin/env python3

import CombineHarvester.CombineTools.ch as ch
import syst as systs

import ROOT as R
import glob
import numpy as np
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '-c', '--channel', default='all', help="""Which channels to run? Supported options: 'all', 'Zee', 'Zmm', 'Zll', 'Wen', 'Wmn','Wln','Znn'""")
parser.add_argument(
    '-o','--output_folder', default='vhcc_Run3', help="""Subdirectory of ./output/ where the cards are written out to""")
parser.add_argument(
    '-y','--year', default='2022_preEE', help="""Year/Era to produce datacards""")
parser.add_argument(
    '--bbb', default=1, type=int, help="""Sets the type of bin-by-bin uncertainty. 0: no bin-by-bins, 1: autoMCStats""")

args = parser.parse_args()


def matching_proc(p,s):
    return ((p.bin()==s.bin()) and (p.process()==s.process()) and (p.signal()==s.signal())
            and (p.analysis()==s.analysis()) and  (p.era()==s.era())
            and (p.channel()==s.channel()) and (p.bin_id()==s.bin_id()) and (p.mass()==s.mass()))

def drop_zero_procs(chob, proc):
    null_yield = not (proc.rate() > 0.)
    if(null_yield):
        chob.FilterSysts(lambda sys: matching_proc(proc,sys))
    return null_yield

def drop_zero_systs(syst):
    null_yield = (not (syst.value_u() > 0. and syst.value_d()>0.) ) and syst.type() in 'shape'
    if(null_yield):
        print('Dropping systematic ',syst.name(),' for region ', syst.bin(), ' ,process ', syst.process(), '. up norm is ', syst.value_u() , ' and down norm is ', syst.value_d())
        #chob.FilterSysts(lambda sys: matching_proc(proc,sys))
    return null_yield



def createCards():
    cb = ch.CombineHarvester()

    chns = []
    if args.channel=="all":
        # At the moment only 2L channels are supported:
        chns = ['Zee','Zmm']
        #chns = ['Wen','Wmn','Znn','Zee','Zmm']
    if 'Zll' in args.channel or 'Zmm' in args.channel:
        chns.append('Zmm')
    if 'Zll' in args.channel or 'Zee' in args.channel:
        chns.append('Zee')
    if 'Wln' in args.channel or 'Wmn' in args.channel or 'Znn' in args.channel:
        chns.append('Wmn')
    if 'Wln' in args.channel or 'Wen' in args.channel or 'Znn' in args.channel:
        chns.append('Wen')
    if 'Znn' in args.channel:
        chns.append('Znn')


    year = args.year
    if year not in ["2016","2017","2018",'2022_preEE','2022_postEE','2023_preBPix','2023_postBPix']:
        print("Year ", year, " not supported!")
        sys.exit()

    bkg_procs = {
        #'Zmm' : ['ZH_hbb','ggZH_hbb','s_Top','TT','Zj_ll','Zj_bj','Zj_cj','VVother','VZcc'],
        'Zmm' : ['TT','Zj_ll','Zj_cj','Zj_bj','WZ','ZZ'],
        'Zee' : ['TT','Zj_ll','Zj_cj','Zj_bj','WZ','ZZ'],
        'Wmn' : ['TT','Wj_ll','Wj_cj','Wj_bj','WW','WZ','ZZ'],
        'Wen' : ['TT','Wj_ll','Wj_cj','Wj_bj','WW','WZ','ZZ'],
        'Znn' : ['TT', 'TT_Had','Wj_ll','Wj_cj','Wj_bj','Zj_ll','Zj_cj','Zj_bj','WW','WZ','ZZ'],
    }

    sig_procs = {
        'Zmm' : ['ZH_hcc'],
        'Zee' : ['ZH_hcc'],
        'Wmn' : ['WH_hcc'],
        'Wen' : ['WH_hcc'],
        'Znn' : ['ZH_hcc']
    }

    cats = {
        'Zmm' : [
            (1, 'Zmm_SR_loZPT'), (2, 'Zmm_SR_hiZPT'),
            (3, 'Zmm_CR_HF_loZPT'), (4, 'Zmm_CR_HF_hiZPT'),
            (5, 'Zmm_CR_LF_loZPT'), (6, 'Zmm_CR_LF_hiZPT'),
            (7, 'Zmm_CR_TT_loZPT'), (8, 'Zmm_CR_TT_hiZPT'),
            (9, 'Zmm_CR_CC_loZPT'), (10, 'Zmm_CR_CC_hiZPT'),
        ],
        'Zee' : [
            (1, 'Zee_SR_loZPT'), (2, 'Zee_SR_hiZPT'),
            (3, 'Zee_CR_HF_loZPT'), (4, 'Zee_CR_HF_hiZPT'),
            (5, 'Zee_CR_LF_loZPT'), (6, 'Zee_CR_LF_hiZPT'),
            (7, 'Zee_CR_TT_loZPT'), (8, 'Zee_CR_TT_hiZPT'),
            (9, 'Zee_CR_CC_loZPT'), (10, 'Zee_CR_CC_hiZPT'),
        ],
        'Wmn' : [
            (1, 'Wmn_SR'), (3, 'Wmn_CR_HF'), (5,'Wmn_CR_LF'), (7,'Wmn_CR_TT'), (9,'Wmn_CR_CC')
        ],
        'Wen' : [
            (1, 'Wen_SR'), (3, 'Wen_CR_HF'), (5,'Wen_CR_LF'), (7,'Wen_CR_TT'), (9,'Wen_CR_CC')
        ],
        'Znn' : [
            (1, 'Znn_SR'), (3, 'Znn_CR_HF'), (5,'Znn_CR_LF'), (7,'Znn_CR_TT'), (9,'Znn_CR_CC')
        ],
    }
    for chn in chns:
        cb.AddObservations( ['*'], ['vhcc'], ['13p6TeV'], [chn], cats[chn])
        cb.AddProcesses( ['*'], ['vhcc'], ['13p6TeV'], [chn], sig_procs[chn], cats[chn], True)
        cb.AddProcesses( ['*'], ['vhcc'], ['13p6TeV'], [chn], bkg_procs[chn], cats[chn], False)

    systs.AddCommonSystematics(cb, year)


    if args.bbb==0:
        cb.AddDatacardLineAtEnd("* autoMCStats -1")
    elif args.bbb==1:
        cb.AddDatacardLineAtEnd("* autoMCStats 0")

    for chn in chns:
        if chn in ['Zll','Zmm','Zee']:
            input_root_file = "./vhcc_shapes_"+year+"_2L.root"
        elif chn in ['Wln','Wmn','Wen']:
            input_root_file = "./vhcc_shapes_"+year+"_1L.root"
        elif chn in ['Znn']:
            input_root_file = "./vhcc_shapes_"+year+"_0L.root"

        cb.cp().channel([chn]).signals().bin_id([1,2,3,4,5,6,7,8,9,10]).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_nominal', '$BIN_$PROCESS_$SYSTEMATIC')
        cb.cp().channel([chn]).backgrounds().bin_id([1,2,3,4,5,6,7,8,9,10]).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_nominal', '$BIN_$PROCESS_$SYSTEMATIC')


    # Use one bin in TT CR for Zll channels:
    cb.cp().channel(['Zee','Zmm']).bin_id([7,8]).VariableRebin([0.,1.])

    ch.SetStandardBinNames(cb)


    writer=ch.CardWriter("output/" + args.output_folder + "_" + year + "/$TAG/$BIN_"+year+".txt",
                         "output/" + args.output_folder + "_" + year +"/$TAG/shapes/shapes_$BIN_"+year+".root")



    cb.FilterProcs(lambda x: drop_zero_procs(cb,x))
    cb.FilterSysts(lambda x: drop_zero_systs(x))


    writer.SetWildcardMasses([])
    writer.SetVerbosity(0)

    writer.WriteCards("./",cb)



if __name__ == "__main__":

    print("Hello world")

    createCards()

    print("... and goodbye.")
