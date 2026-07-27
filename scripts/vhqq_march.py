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
        'Zmm' : ['VJet', 'VZbb', 'VZlx', 'TT','ST'],
        #'Zee' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
        'Zee' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST'],
        'Wmn' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
        'Wen' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
        'Znn' : ['TT','VJetbx','VJetcx','VJetll','WW', 'VZbb', 'VZcc', 'VZlx', 'ST','QCD'],
    }

    sig_procs = {
        'Zmm': ["VH_pTH_0_60",
                "VH_pTH_60_120",
                "VH_pTH_120_200",
                "VH_pTH_200_300",
                "VH_pTH_300_450",
                "VH_pTH_450_inf"],
        #'Zmm' : ['ZH_bb', 'ggZH_hbb'],
        'Zee' : ["ZH_hbb_pTH_0_60",
                "ZH_hbb_pTH_60_120",
                "ZH_hbb_pTH_120_200",
                "ZH_hbb_pTH_200_300",
                "ZH_hbb_pTH_300_450",
                "ZH_hbb_pTH_450_inf"],
        'Wmn' : ['WH_hcc','WH_hbb'],
        'Wen' : ['WH_hcc','WH_hbb'],
        'Znn' : ['ZH_hcc', 'ZH_hbb', 'ggZH_hbb', 'ggZH_hcc'],
    }

    cats = {
        'Zmm' : [
            (1,"Zmm_SR_pT0_60"),
            (2,"Zmm_SR_pT60_120"),
            (3,"Zmm_SR_pT120_200"),
            (4,"Zmm_SR_pT200_300"),
            (5,"Zmm_SR_pT300_450"),
            (6,"Zmm_SR_pT450_inf"),
         #   (1, 'Zmm_SR'), (2, 'Zmm_CR')
        ],
        'Zee' : [
            (1,"SR_Zee_BB_pt0_60"),
            (2,"SR_Zee_BB_pt60_120"),
            (3,"SR_Zee_BB_pt120_200"),
            (4,"SR_Zee_BB_pt200_300"),
            (5,"SR_Zee_BB_pt300_450"),
            (6,"SR_Zee_BB_pt450_inf"),
            (7,"CR_Zee_BB"),
            # (7,"CR_Zee_BB_pt0_60"),
            # (8,"CR_Zee_BB_pt60_120"),
            # (9,"CR_Zee_BB_pt120_200"),
            # (10,"CR_Zee_BB_pt200_300"),
            # (11,"CR_Zee_BB_pt300_450"),
            # (12,"CR_Zee_BB_pt450_inf"),
            # (13,"SR_Zee_BB"),
           
        ],
        'Wen' : [
            (1, 'SR_Wen_2J_cJ'), (2, 'SR_Wen_BB'), 
            (3, 'CR_Wen_B'), (4, 'CR_Wen_HF'),
            (5, 'CR_Wen_HF'), (6, 'CR_Wen_4J_TT'), 
            (7, 'CR_Wen_BB'), (8, 'CR_Wen_2J_CC')
        ],
        'Wmn' : [
            (1, 'SR_Wmn_2J_cJ'), (2, 'SR_Wmn_BB'), 
            (3, 'CR_Wmn_B'), (4, 'CR_Wmn_HF'),
            (5, 'CR_Wmn_LF'), (6, 'CR_Wmn_4J_TT'), 
            (7, 'CR_Wmn_BB'), (8, 'CR_Wmn_2J_CC')
        ],
        'Znn' : [
            (1, 'SR_Znn_2J_cJ'), (2, 'SR_Znn_BB'), 
            (3, 'CR_Znn_B'), (4,'CR_Znn_HF'), 
            (5, 'CR_Znn_LF'), (6, 'CR_Znn_4J_TT'), 
            (7, 'CR_Znn_BB'), (8, 'CR_Znn_2J_CC')
        ],
    }

    for chn in chns:
        cb.AddObservations( ['*'], ['vhqq'], ['13p6TeV'], [chn], cats[chn])
        cb.AddProcesses( ['*'], ['vhqq'], ['13p6TeV'], [chn], sig_procs[chn], cats[chn], True)
        cb.AddProcesses( ['*'], ['vhqq'], ['13p6TeV'], [chn], bkg_procs[chn], cats[chn], False)

    systs.AddCommonSystematics(cb, year)


    if args.bbb==0:
        cb.AddDatacardLineAtEnd("* autoMCStats -1")
    elif args.bbb==1:
        cb.AddDatacardLineAtEnd("* autoMCStats 0")

    for chn in chns:
        if chn in ['Zll','Zmm','Zee']:
            input_root_file = "./vhqq_shapes_"+year+"_2L_renamed.root"
        elif chn in ['Wln','Wmn','Wen']:
            input_root_file = "./vhqq_shapes_"+year+"_1L.root"
        elif chn in ['Znn']:
            input_root_file = "./vhqq_shapes_"+year+"_0L.root"

        cb.cp().channel([chn]).signals().bin_id([1,2,3,4,5,6,7,8,9,10,11,12,13,14]).ExtractShapes(
            # input_root_file, year+'_$BIN/$PROCESS_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')
            input_root_file, year+'_$BIN/$PROCESS_nominal', year+'_$BIN/$PROCESS_$SYSTEMATIC')
        cb.cp().channel([chn]).backgrounds().bin_id([1,2,3,4,5,6,7,8,9,10,11,12,13,14]).ExtractShapes(
            # input_root_file, year+'_$BIN/$PROCESS_nominal', 'Shape_$BIN_$PROCESS_$SYSTEMATIC')
            input_root_file, year+'_$BIN/$PROCESS_nominal', year+'_$BIN/$PROCESS_$SYSTEMATIC')


    # Use one bin in TT CR for Zll channels:
    # cb.cp().channel(['Zee','Zmm']).bin_id([7,8]).VariableRebin([0.,1.])

    ch.SetStandardBinNames(cb)

    # writer=ch.CardWriter("output_Hbb_20260414/" + args.output_folder +  "/$TAG/$BIN_"+year+".txt",
    #                      "output_Hbb_20260414/" + args.output_folder  +  "/$TAG/shapes/shapes_$BIN_"+year+".root")

    writer=ch.CardWriter("output_Hbb_20260414/" + year +  "/$TAG/$BIN_"+year+".txt",
                         "output_Hbb_20260414/" + year  +  "/$TAG/shapes/shapes_$BIN_"+year+".root")

    cb.FilterProcs(lambda x: drop_zero_procs(cb,x))
    cb.FilterSysts(lambda x: drop_zero_systs(x))


    writer.SetWildcardMasses([])
    writer.SetVerbosity(0)

    writer.WriteCards("./",cb)


    # 修改observation值
    output_base = f"output_Hbb_20260414/{year}"
    #modify_observation_in_cards(output_base, target_value=999999)


def modify_observation_in_cards(output_dir, target_value=999999):
    """修改datacard中的observation值"""
    import re
    
    modified_count = 0
    file_count = 0
    
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.txt'):
                filepath = os.path.join(root, file)
                file_count += 1
                
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                modified = False
                for line in lines:
                    if re.match(r'^\s*observation\s+', line, re.IGNORECASE):
                        old_parts = line.split()
                        if len(old_parts) >= 2:
                            old_value = old_parts[1]
                            new_line = f"observation  {target_value}.0\n"
                            new_lines.append(new_line)
                            modified = True
                            print(f"  {os.path.basename(filepath)}: {old_value} -> {target_value}.0")
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                if modified:
                    with open(filepath, 'w') as f:
                        f.writelines(new_lines)
                    modified_count += 1
    
    if modified_count == 0:
        print("  No observation lines found to modify!")
    else:
        print(f"\n  Summary: Modified {modified_count} out of {file_count} datacard files")



if __name__ == "__main__":

    print("Hello world")

    createCards()

    print("... and goodbye.")
