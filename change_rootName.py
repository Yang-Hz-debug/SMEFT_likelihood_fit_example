import ROOT
import os
import re
import shutil
import gc

def get_year_period_from_filename(filename):
    """从文件名提取完整时期标识，如 2022_preEE"""
    basename = os.path.basename(filename)
    # 匹配各种时期格式
    patterns = [
        r'(2022_preEE)',
        r'(2022_postEE)',
        r'(2023_preBPix)',
        r'(2023_postBPix)',
        r'(2024)',
    ]
    for pattern in patterns:
        m = re.search(pattern, basename)
        if m:
            return m.group(1)
    # 如果没有找到具体时期，只返回年份
    m = re.search(r'(20\d{2})', basename)
    return m.group(1) if m else None

def should_rename(name, period, bases):
    # 定义需要特殊处理的直方图
    stats_systs = ["sf_btag_hfstats1", "sf_btag_hfstats2", "sf_btag_lfstats1", "sf_btag_lfstats2"]
    correlated_systs = ["sf_btag_cferr1", "sf_btag_cferr2", "sf_btag_hf", "sf_btag_lf"]
    
    for base in bases:
        pattern = rf'^(.*{re.escape(base)}_?)(Up|Down)$'
        m = re.match(pattern, name)
        if m:
            # JetID 保持不变
            if base == "JetID":
                return False, name
            
            # stats_systs: 加 _Uncorrelated_{period}
            if base in stats_systs:
                return True, f"{m.group(1)}_Uncorrelated_{period}{m.group(2)}"
            
            # correlated_systs: 加 _Correlated
            if base in correlated_systs:
                return True, f"{m.group(1)}_Correlated{m.group(2)}"
            
            # 其他情况保持原逻辑
            return True, f"{m.group(1)}_{period}{m.group(2)}"
    return False, name

def clone_and_rename(src_file, dst_file, period, bases):
    """递归复制所有对象，对直方图按规则重命名"""
    for key in src_file.GetListOfKeys():
        obj = key.ReadObj()
        
        if obj.InheritsFrom("TDirectory"):
            # 创建同名目录
            new_dir = dst_file.mkdir(obj.GetName())
            # 递归处理子目录
            clone_and_rename(obj, new_dir, period, bases)
        elif obj.InheritsFrom("TH1"):
            # 直方图：决定新名字
            old_name = obj.GetName()
            do_rename, new_name = should_rename(old_name, period, bases)
            if do_rename:
               # print(f"  Renaming: {old_name} -> {new_name}")
                new_hist = obj.Clone(new_name)
                dst_file.WriteTObject(new_hist, new_name, "Overwrite")
            else:
                dst_file.WriteTObject(obj, old_name, "Overwrite")
        else:
            # 非直方图（TTree、TList等）直接复制
            dst_file.WriteTObject(obj, obj.GetName(), "Overwrite")
    dst_file.Write()

def process_file(in_path, out_path, period, bases):
    if os.path.exists(out_path):
        os.remove(out_path)
    
    src = ROOT.TFile.Open(in_path, "READ")
    if not src or src.IsZombie():
        return False
    
    dst = ROOT.TFile.Open(out_path, "RECREATE")
    clone_and_rename(src, dst, period, bases)
    
    # 关闭文件
    src.Close()
    dst.Close()
    
    # 最简单的清理：删除文件引用并强制垃圾回收
    del src
    del dst
    gc.collect()
    
    return True

def main():
    files = [
        "vhqq_shapes_2022_preEE_2L.root",
        "vhqq_shapes_2022_postEE_2L.root",
        "vhqq_shapes_2023_preBPix_2L.root",
        "vhqq_shapes_2023_postBPix_2L.root",
        "vhqq_shapes_2024_2L.root"
    ]
    
    bases = ["sf_btag_hfstats1", "sf_btag_hfstats2", "sf_btag_lfstats1", "sf_btag_lfstats2", "JetID",
             "sf_btag_cferr1", "sf_btag_cferr2", "sf_btag_hf", "sf_btag_lf"]
    
    for f in files:
        if not os.path.exists(f):
            print(f"Warning: {f} not found, skipping...")
            continue
        
        period = get_year_period_from_filename(f)
        if not period:
            print(f"Warning: Cannot extract period from {f}, skipping...")
            continue
        
        out = f.replace(".root", "_renamed.root")
        print(f"\nProcessing {f} -> {out}")
        print(f"Using period: {period}")
        
        if process_file(f, out, period, bases):
            print("Done.")
        else:
            print("Failed.")

if __name__ == "__main__":
    main()