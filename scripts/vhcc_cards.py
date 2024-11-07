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
    '-y','--year', default='2022_postEE', help="""Yea/Era to produce datacards""")

args = parser.parse_args()

    
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
        'Zmm' : ['TT','Zj_ll','WW','WZ','ZZ'],
        'Zee' : ['TT','Zj_ll','WW','WZ','ZZ'],
    }
    
    sig_procs = {
        'Zmm' : ['ZH_hcc'],
        'Zee' : ['ZH_hcc'],
    }
    
    cats = {
        'Zmm' : [
            (1, 'Zmm_SR'), (2, 'Zmm_SR'), (3, 'Zmm_CR_HF'), (4,'Zmm_CR_LF'), (5,'Zmm_CR_TT'), (6,'Zmm_CR_CC')
            #(1, 'SR_high_Zmm'), (2, 'SR_low_Zmm'), (3, 'Zlf_high_Zmm'), (4,'Zlf_low_Zmm'),
            #(5, 'Zhf_high_Zee'), (6, 'Zhf_low_Zee'),
            #(7,'ttbar_high_Zee'), (8,'ttbar_low_Zee'),(9,'Zcc_high_Zee'), (10,'Zcc_low_Zee')
        ],
        'Zee' : [
            (1, 'Zee_SR'), (2, 'Zee_SR'), (3, 'Zee_CR_HF'), (4,'Zee_CR_LF'), (5,'Zee_CR_TT'), (6,'Zee_CR_CC')
            #(1, 'SR_high_Zmm'), (2, 'SR_low_Zmm'), (3, 'Zlf_high_Zmm'), (4,'Zlf_low_Zmm'),
            #(5, 'Zhf_high_Zee'), (6, 'Zhf_low_Zee'),
            #(7,'ttbar_high_Zee'), (8,'ttbar_low_Zee'),(9,'Zcc_high_Zee'), (10,'Zcc_low_Zee')
        ]
    }
    for chn in chns:
        cb.AddObservations( ['*'], ['vhcc'], ['13p6TeV'], [chn], cats[chn])
        cb.AddProcesses( ['*'], ['vhcc'], ['13p6TeV'], [chn], bkg_procs[chn], cats[chn], False)
        cb.AddProcesses( ['*'], ['vhcc'], ['13p6TeV'], [chn], sig_procs[chn], cats[chn], True)
    
    systs.AddCommonSystematics(cb)
    
    
    for chn in chns:
        if chn in ['Zll','Zmm','Zee']:
            input_root_file = "./vhcc_shapes_2L.root"
        elif chn in ['Wln','Wmn','Wen']:
            input_root_file = "./vhcc_shapes_1L.root"
        elif chn in ['Znn']:
            input_root_file = "./vhcc_shapes_0L.root"
        
        cb.cp().channel([chn]).backgrounds().bin_id([1,2,3,4,5,6]).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_Shape_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')
        cb.cp().channel([chn]).signals().bin_id([1,2,3,4,5,6]).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_Shape_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')    
        
    
    ch.SetStandardBinNames(cb)
    
    
    
    writer=ch.CardWriter("output/" + args.output_folder + "_" + year + "/$TAG/$BIN_"+year+".txt",
                         "output/" + args.output_folder + "_" + year +"/$TAG/shapes_$BIN_"+year+".root")
    
    writer.SetWildcardMasses([])
    writer.SetVerbosity(0)
    
    writer.WriteCards("./",cb)


    
if __name__ == "__main__":

    print("Hello world")

    createCards()
    
    print("... and goodbye.")
