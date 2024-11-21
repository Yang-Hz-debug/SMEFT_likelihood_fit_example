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
    '-c', '--channel', default='all', help="""Which channels to run? Supported options: 'all', 'Zee', 'Zmm', 'Zll', 'Wen', 'Wmn','Wln'""")
parser.add_argument(
    '-o','--output_folder', default='vhcc_Run3', help="""Subdirectory of ./output/ where the cards are written out to""")
parser.add_argument(
    '-y','--year', default='2022_postEE', help="""Year/Era to produce datacards""")
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
        'Zmm' : ['TT','Zj_ll','Zj_cj','Zj_bj','WW','WZ','ZZ'],
        'Zee' : ['TT','Zj_ll','Zj_cj','Zj_bj','WW','WZ','ZZ'],
    }
    
    sig_procs = {
        'Zmm' : ['ZH_hcc'],
        'Zee' : ['ZH_hcc'],
    }
    
    cats = {
        'Zmm' : [
            (1, 'Zmm_SR'), (3, 'Zmm_CR_HF'), (4,'Zmm_CR_LF'), (5,'Zmm_CR_TT'), (6,'Zmm_CR_CC')
            #(1, 'SR_high_Zmm'), (2, 'SR_low_Zmm'), (3, 'Zlf_high_Zmm'), (4,'Zlf_low_Zmm'),
            #(5, 'Zhf_high_Zee'), (6, 'Zhf_low_Zee'),
            #(7,'ttbar_high_Zee'), (8,'ttbar_low_Zee'),(9,'Zcc_high_Zee'), (10,'Zcc_low_Zee')
        ],
        'Zee' : [
            (1, 'Zee_SR'), (3, 'Zee_CR_HF'), (4,'Zee_CR_LF'), (5,'Zee_CR_TT'), (6,'Zee_CR_CC')
            #(1, 'SR_high_Zmm'), (2, 'SR_low_Zmm'), (3, 'Zlf_high_Zmm'), (4,'Zlf_low_Zmm'),
            #(5, 'Zhf_high_Zee'), (6, 'Zhf_low_Zee'),
            #(7,'ttbar_high_Zee'), (8,'ttbar_low_Zee'),(9,'Zcc_high_Zee'), (10,'Zcc_low_Zee')
        ]
    }
    for chn in chns:
        cb.AddObservations( ['*'], ['vhcc'], ['13p6TeV'], [chn], cats[chn])
        cb.AddProcesses( ['*'], ['vhcc'], ['13p6TeV'], [chn], sig_procs[chn], cats[chn], True)
        cb.AddProcesses( ['*'], ['vhcc'], ['13p6TeV'], [chn], bkg_procs[chn], cats[chn], False)
    
    systs.AddCommonSystematics(cb, year)
    

    #if args.bbb==0:
    #    cb.AddDatacardLineAtEnd("* autoMCStats -1")
    #elif args.bbb==1:
    #    cb.AddDatacardLineAtEnd("* autoMCStats 0")
    
    for chn in chns:
        if chn in ['Zll','Zmm','Zee']:
            input_root_file = "./vhcc_shapes_"+year+"_2L.root"
        elif chn in ['Wln','Wmn','Wen']:
            input_root_file = "./vhcc_shapes_"+year+"_1L.root"
        elif chn in ['Znn']:
            input_root_file = "./vhcc_shapes_"+year+"_0L.root"
        
        cb.cp().channel([chn]).signals().bin_id([1,3,4,5,6]).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_Shape_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')    
        cb.cp().channel([chn]).backgrounds().bin_id([1,3,4,5,6]).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_Shape_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')
        

        
    #print('binning in TT CRs: [0., 1.0] for Zll channels')
    #cb.cp().channel(['Zee','Zmm']).bin_id([5]).VariableRebin([0., 1.0])
        
    ch.SetStandardBinNames(cb)
       
    
    writer=ch.CardWriter("output/" + args.output_folder + "_" + year + "/$TAG/$BIN_"+year+".txt",
                         "output/" + args.output_folder + "_" + year +"/$TAG/shapes_$BIN_"+year+".root")



    cb.FilterProcs(lambda x: drop_zero_procs(cb,x))
    cb.FilterSysts(lambda x: drop_zero_systs(x))

    
    writer.SetWildcardMasses([])
    writer.SetVerbosity(0)
    
    writer.WriteCards("./",cb)


    
if __name__ == "__main__":

    print("Hello world")

    createCards()
    
    print("... and goodbye.")
