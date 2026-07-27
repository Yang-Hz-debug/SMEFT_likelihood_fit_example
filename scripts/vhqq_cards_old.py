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
    '-o','--output_folder', default='vhqq_Run3', help="""Subdirectory of ./output/ where the cards are written out to""")
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
        chns = ['Zee','Zmm','Znn']
        #chns = ['Wen','Wmn','Znn','Zee','Zmm']
    if 'Zll' in args.channel or 'Zmm' in args.channel:
        chns.append('Zmm')
    if 'Zll' in args.channel or 'Zee' in args.channel:
        chns.append('Zee')
    if 'Wln' in args.channel or 'Wmn' in args.channel:
        chns.append('Wmn')
    if 'Wln' in args.channel or 'Wen' in args.channel:
        chns.append('Wen')
    if 'Znn' in args.channel:
        chns.append('Znn')
    
    year = args.year
    if year not in ["2016","2017","2018",'2022_preEE','2022_postEE','2023_preBPix','2023_postBPix','2024']:
        print("Year ", year, " not supported!")
        sys.exit()

    bkg_procs = {
        # 'Zmm' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
        'Zee' : [ 'VZbb', 'VZcc', 'VZlx', 'WW', 'TT', 'ST','VJetbx','VJetcx','VJetll'], #['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
        # 'Wmn' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
        # 'Wen' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
        # 'Znn' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
    }

    sig_procs = {
        # 'Zmm' : [ 'ZH_hbb', 'ggZH_hbb' ],#'ZH_hcc',,'ggZH_hcc'
        'Zee' :[ 'ZH_hbb', 'ggZH_hbb'],# ['ZH_hcc', 'ZH_hbb', 'ggZH_hbb', 'ggZH_hcc'],
        # 'Wmn' : ['WH_hcc','WH_hbb'],
        # 'Wen' : ['WH_hcc','WH_hbb'],
        # 'Znn' : ['ZH_hcc', 'ZH_hbb', 'ggZH_hbb', 'ggZH_hcc'],
    }

    cats = {
        'Zee' : [
            (1, 'CR_Zee_BB'),           # CR bin
            (2, 'SR_Zee_BB'),           # SR bin (inclusive)
            (3, 'SR_Zee_BB_pt0_60'),    # pt分 bin
            (4, 'SR_Zee_BB_pt60_120'),
            (5, 'SR_Zee_BB_pt120_200'),
            (6, 'SR_Zee_BB_pt200_300'),
            (7, 'SR_Zee_BB_pt300_450'),
            (8, 'SR_Zee_BB_pt450_inf'),
            (9, 'CR_Zee_BB_dielectron_SF'),   # SF CR bin
            (10, 'SR_Zee_BB_dielectron_SF')   # SF SR bin
        ],
        # ... 其他通道
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
            input_root_file = "./vhqq_shapes_"+year+"_2L.root"
        elif chn in ['Wln','Wmn','Wen']:
            input_root_file = "./vhqq_shapes_"+year+"_1L.root"
        elif chn in ['Znn']:
            input_root_file = "./vhqq_shapes_"+year+"_0L.root"

        cb.cp().channel([chn]).signals().bin_id([1,2,3,4,5,6,7,8,9,10]).ExtractShapes( #,3,4,5,6,7,8,9,10,11,12,13
            # input_root_file, year+'_$BIN/$PROCESS_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')
            input_root_file, year+'_$BIN/$PROCESS_nominal', year+'_$BIN/$PROCESS_$SYSTEMATIC')
        cb.cp().channel([chn]).backgrounds().bin_id([1,2,3,4,5,6,7,8,9,10]).ExtractShapes( #,3,4,5,6,7,8,9,10,11,12,13
            # input_root_file, year+'_$BIN/$PROCESS_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')
            input_root_file, year+'_$BIN/$PROCESS_nominal', year+'_$BIN/$PROCESS_$SYSTEMATIC')


    # Use one bin in TT CR for Zll channels:
    # cb.cp().channel(['Zee','Zmm']).bin_id([7,8]).VariableRebin([0.,1.])

    ch.SetStandardBinNames(cb)


    writer=ch.CardWriter("output_Hqq/" + args.output_folder + "_" + year + "/$TAG/$BIN_"+year+".txt",
                         "output_Hqq/" + args.output_folder + "_" + year +"/$TAG/shapes/shapes_$BIN_"+year+".root")



    cb.FilterProcs(lambda x: drop_zero_procs(cb,x))
    cb.FilterSysts(lambda x: drop_zero_systs(x))


    writer.SetWildcardMasses([])
    writer.SetVerbosity(0)

    writer.WriteCards("./",cb)



if __name__ == "__main__":

    print("Hello world")

    createCards()

    print("... and goodbye.")
