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
    
    # Define your channels
    chns = ['Zee']  # Add other channels as needed
                    #, 'Zmm'
    
    year = args.year
    
    # 定义背景过程
    bkg_procs = {
        'Zee': ['VZbb', 'VZcc', 'VZlx', 'WW', 'TT', 'ST', 'VJetbx', 'VJetcx', 'VJetll'],
    }
    
    # 定义信号过程
    sig_procs = {
        'Zee': ['ZH_hbb', 'ggZH_hbb'],
    }
    
    # Define your categories with bin IDs
    cats = {
        ######## for any year
        'Zee': [
            # CR区域（按pt分bin）
            (1, 'CR_Zee_BB_pt0_60'),
            (2, 'CR_Zee_BB_pt60_120'),
            (3, 'CR_Zee_BB_pt120_200'),
            (4, 'CR_Zee_BB_pt200_300'),
            (5, 'CR_Zee_BB_pt300_450'),
            (6, 'CR_Zee_BB_pt450_inf'),

            # SR区域（按pt分bin）
            (7, 'SR_Zee_BB_pt0_60'),
            (8, 'SR_Zee_BB_pt60_120'),
            (9, 'SR_Zee_BB_pt120_200'),
            (10, 'SR_Zee_BB_pt200_300'),
            (11, 'SR_Zee_BB_pt300_450'),
            (12, 'SR_Zee_BB_pt450_inf'),

            # inclusive bins
            (13, 'CR_Zee_BB'),      # inclusive CR bin
            (14, 'SR_Zee_BB'),      # inclusive SR bin
            (15, 'CR_Zee_BB_GNN'),      # inclusive CR bin
            (16, 'SR_Zee_BB_GNN'),      # inclusive SR bin
        ],
        #######for 2024 test
        # 'Zee': [
        #     # CR区域（按pt分bin）
        #     # (1, 'CR_Zee_BB_pt0_60'),
        #     # (2, 'CR_Zee_BB_pt60_120'),
        #     # (3, 'CR_Zee_BB_pt120_200'),
        #     # (4, 'CR_Zee_BB_pt200_300'),
        #     # (5, 'CR_Zee_BB_pt300_450'),
        #     # (6, 'CR_Zee_BB_pt450_inf'),

        #     # # SR区域（按pt分bin）
        #     (7, 'SR_Zee_BB_pt0_60'),
        #     (8, 'SR_Zee_BB_pt60_120'),
        #     (9, 'SR_Zee_BB_pt120_200'),
        #     (10, 'SR_Zee_BB_pt200_300'),
        #     (11, 'SR_Zee_BB_pt300_450'),
        #     (12, 'SR_Zee_BB_pt450_inf'),

        #     # inclusive bins
        #     (13, 'CR_Zee_BB'),      # inclusive CR bin
        #     (14, 'SR_Zee_BB'),      # inclusive SR bin

        # ],
    }
    
    # Add observations and processes
    for chn in chns:
        cb.AddObservations(['*'], ['vhqq'], ['13p6TeV'], [chn], cats[chn])
        cb.AddProcesses(['*'], ['vhqq'], ['13p6TeV'], [chn], sig_procs[chn], cats[chn], True)
        cb.AddProcesses(['*'], ['vhqq'], ['13p6TeV'], [chn], bkg_procs[chn], cats[chn], False)
    
    # 添加公共系统误差（syst.py 中的 rateParams 已经修改为支持 1-14 bins）
    systs.AddCommonSystematics(cb, year)

    if args.bbb==0:
        cb.AddDatacardLineAtEnd("* autoMCStats -1")
    elif args.bbb==1:
        cb.AddDatacardLineAtEnd("* autoMCStats 0")

    for chn in chns:
        if chn in ['Zll','Zmm','Zee']:
            input_root_file = "vhqq_shapes_"+year+"_2L.root"
        elif chn in ['Wln','Wmn','Wen']:
            input_root_file = "vhqq_shapes_"+year+"_1L.root"
        elif chn in ['Znn']:
            input_root_file = "vhqq_shapes_"+year+"_0L.root"

        # 提取所有 14 个 bins 的形状
        all_bins = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #[7,8,9,10,11,12,13,14]# [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        cb.cp().channel([chn]).signals().bin_id(all_bins).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_nominal', year+'_$BIN/$PROCESS_$SYSTEMATIC')
        cb.cp().channel([chn]).backgrounds().bin_id(all_bins).ExtractShapes(
            input_root_file, year+'_$BIN/$PROCESS_nominal', year+'_$BIN/$PROCESS_$SYSTEMATIC')


    # 设置标准bin名称
    ch.SetStandardBinNames(cb)

    # 创建CardWriter
    writer = ch.CardWriter("output_Hqq/" + args.output_folder + "_" + year + "/$TAG/$BIN_"+year+".txt",
                           "output_Hqq/" + args.output_folder + "_" + year +"/$TAG/shapes/shapes_$BIN_"+year+".root")

    # 过滤零产额的过程和系统误差
    cb.FilterProcs(lambda x: drop_zero_procs(cb,x))
    cb.FilterSysts(lambda x: drop_zero_systs(x))

    writer.SetWildcardMasses([])
    writer.SetVerbosity(0)

    # 写入datacards
    writer.WriteCards("./", cb)


if __name__ == "__main__":
    print("Hello world")
    createCards()
    print("... and goodbye.")