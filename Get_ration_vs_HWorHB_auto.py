# import numpy as np
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
# import os
# import re

# base_path = "/eos/user/h/haozhong/genNANOAOD_SMEFT_gridpick/genproductions/bin/MadGraph5_aMCatNLO/Draw_new_20260706_for_reweight"
# hb_file = os.path.join(base_path, "ratio_hpt_HB_norm.txt")
# hw_file = os.path.join(base_path, "ratio_hpt_HW_norm.txt")

# def poly2(x, a, b, c):
#     return a + b*x + c*x**2

# def poly3(x, a, b, c, d):
#     return a + b*x + c*x**2 + d*x**3

# def extract_parameter_values(header_line):
#     """从header中提取参数值（数字部分），按出现顺序返回（不排序）"""
#     pattern = r'(?:HB|HW)([0-9]+p[0-9]+)'
#     matches = re.findall(pattern, header_line)
#     values = []
#     for m in matches:
#         val = float(m.replace('p', '.'))
#         values.append(val)
#     return values  # 不排序

# def read_ratio_file(filename):
#     print(f"\n读取文件: {filename}")
#     with open(filename, 'r') as f:
#         lines = f.readlines()
    
#     # 查找包含 "=== Per 10 GeV bins" 的行，从该行之后开始找表头
#     start_idx = None
#     for i, line in enumerate(lines):
#         if '#=== Per 10 GeV bins' in line:
#             start_idx = i + 1
#             break
#     if start_idx is None:
#         # 如果没找到，从头开始
#         start_idx = 0
#         print("警告: 未找到 '=== Per 10 GeV bins'，从文件开头读取")
    
#     # 从start_idx开始查找表头和数据行
#     header_line = None
#     data_lines = []
#     for i in range(start_idx, len(lines)):
#         line = lines[i]
#         if line.startswith('#') and 'bin_low' in line:
#             header_line = line
#         elif '||' in line and not line.startswith('#'):
#             data_lines.append(line)
    
#     if not header_line:
#         raise ValueError("未找到header行")
#     if not data_lines:
#         raise ValueError("未找到数据行")
    
#     # 提取参数值（不排序）
#     param_values = extract_parameter_values(header_line)
#     if not param_values:
#         raise ValueError("无法从header提取参数值")
#     param_values = np.array(param_values)
#     print(f"提取到 {len(param_values)} 个参数值，顺序与header一致")
#     print(f"前5个: {param_values[:5]}")
#     print(f"后5个: {param_values[-5:]}")
    
#     param_type = 'HW' if 'HW' in filename else 'HB'
    
#     all_bins = []
#     all_ratios = []
#     for line in data_lines:
#         parts = line.split('||')
#         if len(parts) != 2:
#             continue
#         left = parts[0].strip().split()
#         right = parts[1].strip().split()
#         if len(left) < 2:
#             continue
#         bin_low = float(left[0])
#         bin_high = float(left[1])
#         all_bins.append((bin_low, bin_high))
#         ratios = [float(x) for x in right]
#         all_ratios.append(ratios)
    
#     # 检查所有bin的ratio数量是否一致
#     n_ratios = len(all_ratios[0]) if all_ratios else 0
#     for i, ratios in enumerate(all_ratios):
#         if len(ratios) != n_ratios:
#             raise ValueError(f"bin {all_bins[i]} 的ratio数量 ({len(ratios)}) 与其他bin不同 ({n_ratios})")
    
#     # 检查数量是否与参数值匹配
#     if n_ratios != len(param_values):
#         print(f"警告: ratio数量 ({n_ratios}) 与参数值数量 ({len(param_values)}) 不一致")
#         min_len = min(n_ratios, len(param_values))
#         param_values = param_values[:min_len]
#         all_ratios = [r[:min_len] for r in all_ratios]
#         print(f"已调整为 {min_len} 个数据点")
    
#     print(f"共有 {len(all_bins)} 个pT bin，每个有 {len(param_values)} 个数据点")
#     # 打印第一个和最后一个bin的部分ratio
#     if all_ratios:
#         print(f"第一个bin (0-60) 前5个ratio: {all_ratios[0][:5]}")
#         print(f"最后一个bin ({all_bins[-1][0]}-{all_bins[-1][1]}) 前5个ratio: {all_ratios[-1][:5]}")
    
#     return param_values, all_bins, all_ratios, param_type

# def fit_and_plot(param_values, all_bins, all_ratios, param_type, outprefix):
#     all_fits = {}
#     for idx, (bl, bh) in enumerate(all_bins):
#         label = f"{bl}-{bh}" if bh < 9999 else f"{bl}+"
#         ydata = np.array(all_ratios[idx])
#         xdata = param_values
        
#         # 拟合
#         try:
#             popt2, pcov2 = curve_fit(poly2, xdata, ydata)
#             perr2 = np.sqrt(np.diag(pcov2))
#         except:
#             popt2, pcov2, perr2 = np.zeros(3), np.eye(3), np.zeros(3)
#         try:
#             popt3, pcov3 = curve_fit(poly3, xdata, ydata)
#             perr3 = np.sqrt(np.diag(pcov3))
#         except:
#             popt3, pcov3, perr3 = np.zeros(4), np.eye(4), np.zeros(4)
        
#         all_fits[label] = {
#             'poly2': (popt2, perr2, pcov2),
#             'poly3': (popt3, perr3, pcov3),
#             'x': xdata,
#             'y': ydata
#         }
    
#     # 绘图
#     n = len(all_fits)
#     ncols = 3
#     nrows = (n + ncols - 1) // ncols
#     fig, axes = plt.subplots(nrows, ncols, figsize=(18, 6*nrows))
#     if nrows == 1:
#         axes = axes.flatten()
#     else:
#         axes = axes.flatten()
    
#     # 确定全局x范围（基于所有数据点）
#     all_x = np.concatenate([fit['x'] for fit in all_fits.values()])
#     x_min, x_max = all_x.min(), all_x.max()
#     x_margin = 0.05 * (x_max - x_min) if x_max > x_min else 0.1
#     x_plot_min = max(0, x_min - x_margin)
#     x_plot_max = x_max + x_margin
    
#     x_smooth = np.linspace(x_plot_min, x_plot_max, 1000)
    
#     for i, (label, fit) in enumerate(all_fits.items()):
#         ax = axes[i]
#         x = fit['x']
#         y = fit['y']
#         ax.scatter(x, y, color='blue', s=30, label='Data', alpha=0.7)
        
#         popt2, perr2, pcov2 = fit['poly2']
#         if np.sum(np.abs(popt2)) > 1e-10:
#             ys2 = poly2(x_smooth, *popt2)
#             ax.plot(x_smooth, ys2, 'r-', lw=2, label='Quadratic')
#             try:
#                 X = np.column_stack([np.ones_like(x_smooth), x_smooth, x_smooth**2])
#                 y_std = np.sqrt(np.diag(X @ pcov2 @ X.T))
#                 ax.fill_between(x_smooth, ys2 - y_std, ys2 + y_std, color='red', alpha=0.15, label='1σ band')
#             except:
#                 pass
        
#         popt3, perr3, pcov3 = fit['poly3']
#         if np.sum(np.abs(popt3)) > 1e-10:
#             ys3 = poly3(x_smooth, *popt3)
#             ax.plot(x_smooth, ys3, 'g--', lw=2, label='Cubic')
        
#         ax.set_xlabel(param_type)
#         ax.set_ylabel('Ratio')
#         ax.set_title(f'pT {label} GeV')
#         ax.grid(alpha=0.3)
#         ax.legend(loc='best', fontsize=9)
#         ax.set_xlim([x_plot_min, x_plot_max])
        
#         # R²
#         y_pred2 = poly2(x, *popt2)
#         y_pred3 = poly3(x, *popt3)
#         ss_tot = np.sum((y - np.mean(y))**2)
#         r2_2 = 1 - np.sum((y - y_pred2)**2)/ss_tot if ss_tot>0 else 0
#         r2_3 = 1 - np.sum((y - y_pred3)**2)/ss_tot if ss_tot>0 else 0
#         ax.text(0.05, 0.95, f'R²_quad={r2_2:.4f}\nR²_cubic={r2_3:.4f}',
#                 transform=ax.transAxes, va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
#     for j in range(len(all_fits), len(axes)):
#         axes[j].set_visible(False)
#     plt.tight_layout()
#     plt.savefig(f"{outprefix}_fits.png", dpi=300)
#     plt.close()
#     print(f"图表保存为: {outprefix}_fits.png")
    
#     # 输出结果
#     with open(f"{outprefix}_results.txt", 'w') as f:
#         f.write(f"拟合结果 - {param_type}\n\n")
#         for label, fit in all_fits.items():
#             f.write(f"{'='*40}\n{label} GeV\n")
#             popt2, perr2, _ = fit['poly2']
#             f.write(f"二次: a={popt2[0]:.6f}±{perr2[0]:.6f}, b={popt2[1]:.6f}±{perr2[1]:.6f}, c={popt2[2]:.6f}±{perr2[2]:.6f}\n")
#             popt3, perr3, _ = fit['poly3']
#             f.write(f"三次: a={popt3[0]:.6f}±{perr3[0]:.6f}, b={popt3[1]:.6f}±{perr3[1]:.6f}, c={popt3[2]:.6f}±{perr3[2]:.6f}, d={popt3[3]:.6f}±{perr3[3]:.6f}\n")
#             x = fit['x']; y = fit['y']
#             yp2 = poly2(x, *popt2); yp3 = poly3(x, *popt3)
#             ss_tot = np.sum((y - np.mean(y))**2)
#             r2_2 = 1 - np.sum((y - yp2)**2)/ss_tot if ss_tot>0 else 0
#             r2_3 = 1 - np.sum((y - yp3)**2)/ss_tot if ss_tot>0 else 0
#             f.write(f"R²: quadratic={r2_2:.6f}, cubic={r2_3:.6f}\n\n")
#     print(f"结果保存为: {outprefix}_results.txt")

# def process_file(filename, prefix):
#     if not os.path.exists(filename):
#         print(f"文件不存在: {filename}")
#         return
#     try:
#         pvals, bins, ratios, ptype = read_ratio_file(filename)
#         fit_and_plot(pvals, bins, ratios, ptype, prefix)
#     except Exception as e:
#         print(f"处理 {filename} 时出错: {e}")

# if __name__ == "__main__":
#     print("处理HB文件...")
#     process_file(hb_file, "HB")
#     print("\n处理HW文件...")
#     process_file(hw_file, "HW")
#     print("\n完成。")


#常数项固定为1##################################
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import re

base_path = "/eos/user/h/haozhong/genNANOAOD_SMEFT_gridpick/genproductions/bin/MadGraph5_aMCatNLO/Draw_new_20260706_for_reweight"
hb_file = os.path.join(base_path, "ratio_hpt_HB_norm.txt")
hw_file = os.path.join(base_path, "ratio_hpt_HW_norm.txt")

# ===== 固定常数项为 1 的多项式 =====
def poly2_fixed(x, b, c):
    return 1.0 + b*x + c*x**2

def poly3_fixed(x, b, c, d):
    return 1.0 + b*x + c*x**2 + d*x**3
# ===================================

def extract_parameter_values(header_line):
    """从header中提取参数值（数字部分），按出现顺序返回（不排序）"""
    pattern = r'(?:HB|HW)([0-9]+p[0-9]+)'
    matches = re.findall(pattern, header_line)
    values = []
    for m in matches:
        val = float(m.replace('p', '.'))
        values.append(val)
    return values  # 不排序

def read_ratio_file(filename):
    print(f"\n读取文件: {filename}")
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # 查找包含 "=== Per 10 GeV bins" 的行，从该行之后开始找表头
    start_idx = None
    for i, line in enumerate(lines):
        if '#=== Per 10 GeV bins' in line:
            start_idx = i + 1
            break
    if start_idx is None:
        start_idx = 0
        print("警告: 未找到 '=== Per 10 GeV bins'，从文件开头读取")
    
    header_line = None
    data_lines = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        if line.startswith('#') and 'bin_low' in line:
            header_line = line
        elif '||' in line and not line.startswith('#'):
            data_lines.append(line)
    
    if not header_line:
        raise ValueError("未找到header行")
    if not data_lines:
        raise ValueError("未找到数据行")
    
    param_values = extract_parameter_values(header_line)
    if not param_values:
        raise ValueError("无法从header提取参数值")
    param_values = np.array(param_values)
    print(f"提取到 {len(param_values)} 个参数值，顺序与header一致")
    print(f"前5个: {param_values[:5]}")
    print(f"后5个: {param_values[-5:]}")
    
    param_type = 'HW' if 'HW' in filename else 'HB'
    
    all_bins = []
    all_ratios = []
    for line in data_lines:
        parts = line.split('||')
        if len(parts) != 2:
            continue
        left = parts[0].strip().split()
        right = parts[1].strip().split()
        if len(left) < 2:
            continue
        bin_low = float(left[0])
        bin_high = float(left[1])
        all_bins.append((bin_low, bin_high))
        ratios = [float(x) for x in right]
        all_ratios.append(ratios)
    
    n_ratios = len(all_ratios[0]) if all_ratios else 0
    for i, ratios in enumerate(all_ratios):
        if len(ratios) != n_ratios:
            raise ValueError(f"bin {all_bins[i]} 的ratio数量 ({len(ratios)}) 与其他bin不同 ({n_ratios})")
    
    if n_ratios != len(param_values):
        print(f"警告: ratio数量 ({n_ratios}) 与参数值数量 ({len(param_values)}) 不一致")
        min_len = min(n_ratios, len(param_values))
        param_values = param_values[:min_len]
        all_ratios = [r[:min_len] for r in all_ratios]
        print(f"已调整为 {min_len} 个数据点")
    
    print(f"共有 {len(all_bins)} 个pT bin，每个有 {len(param_values)} 个数据点")
    if all_ratios:
        print(f"第一个bin (0-60) 前5个ratio: {all_ratios[0][:5]}")
        print(f"最后一个bin ({all_bins[-1][0]}-{all_bins[-1][1]}) 前5个ratio: {all_ratios[-1][:5]}")
    
    return param_values, all_bins, all_ratios, param_type

def fit_and_plot(param_values, all_bins, all_ratios, param_type, outprefix):
    all_fits = {}
    for idx, (bl, bh) in enumerate(all_bins):
        label = f"{bl}-{bh}" if bh < 9999 else f"{bl}+"
        ydata = np.array(all_ratios[idx])
        xdata = param_values
        
        # ---- 拟合（常数项固定为1） ----
        try:
            popt2, pcov2 = curve_fit(poly2_fixed, xdata, ydata, p0=[0, 0])
            perr2 = np.sqrt(np.diag(pcov2))
        except Exception as e:
            print(f"二次拟合失败 (bin {label}): {e}")
            popt2, pcov2, perr2 = np.zeros(2), np.eye(2), np.zeros(2)
        try:
            popt3, pcov3 = curve_fit(poly3_fixed, xdata, ydata, p0=[0, 0, 0])
            perr3 = np.sqrt(np.diag(pcov3))
        except Exception as e:
            print(f"三次拟合失败 (bin {label}): {e}")
            popt3, pcov3, perr3 = np.zeros(3), np.eye(3), np.zeros(3)
        
        all_fits[label] = {
            'poly2': (popt2, perr2, pcov2),
            'poly3': (popt3, perr3, pcov3),
            'x': xdata,
            'y': ydata
        }
    
    # ---- 绘图 ----
    n = len(all_fits)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(18, 6*nrows))
    if nrows == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    all_x = np.concatenate([fit['x'] for fit in all_fits.values()])
    x_min, x_max = all_x.min(), all_x.max()
    x_margin = 0.05 * (x_max - x_min) if x_max > x_min else 0.1
    x_plot_min = max(0, x_min - x_margin)
    x_plot_max = x_max + x_margin
    x_smooth = np.linspace(x_plot_min, x_plot_max, 1000)
    
    for i, (label, fit) in enumerate(all_fits.items()):
        ax = axes[i]
        x = fit['x']
        y = fit['y']
        ax.scatter(x, y, color='blue', s=30, label='Data', alpha=0.7)
        
        # 二次拟合（固定常数项）
        popt2, perr2, pcov2 = fit['poly2']
        if np.sum(np.abs(popt2)) > 1e-10:
            ys2 = poly2_fixed(x_smooth, *popt2)
            ax.plot(x_smooth, ys2, 'r-', lw=2, label='Quadratic (fixed const=1)')
            # 误差带
            try:
                X = np.column_stack([x_smooth, x_smooth**2])   # 只对应 b, c
                y_std = np.sqrt(np.diag(X @ pcov2 @ X.T))
                ax.fill_between(x_smooth, ys2 - y_std, ys2 + y_std, color='red', alpha=0.15, label='1σ band')
            except:
                pass
        
        # 三次拟合（固定常数项）
        popt3, perr3, pcov3 = fit['poly3']
        if np.sum(np.abs(popt3)) > 1e-10:
            ys3 = poly3_fixed(x_smooth, *popt3)
            ax.plot(x_smooth, ys3, 'g--', lw=2, label='Cubic (fixed const=1)')
        
        ax.set_xlabel(param_type)
        ax.set_ylabel('Ratio')
        ax.set_title(f'pT {label} GeV')
        ax.grid(alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        ax.set_xlim([x_plot_min, x_plot_max])
        
        # R² 计算
        y_pred2 = poly2_fixed(x, *popt2)
        y_pred3 = poly3_fixed(x, *popt3)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2_2 = 1 - np.sum((y - y_pred2)**2)/ss_tot if ss_tot>0 else 0
        r2_3 = 1 - np.sum((y - y_pred3)**2)/ss_tot if ss_tot>0 else 0
        ax.text(0.05, 0.95, f'R²_quad={r2_2:.4f}\nR²_cubic={r2_3:.4f}',
                transform=ax.transAxes, va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    for j in range(len(all_fits), len(axes)):
        axes[j].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{outprefix}_fits.png", dpi=300)
    plt.close()
    print(f"图表保存为: {outprefix}_fits.png")
    
    # ---- 输出结果 ----
    with open(f"{outprefix}_results.txt", 'w') as f:
        f.write(f"拟合结果 - {param_type} (常数项固定为 1)\n\n")
        for label, fit in all_fits.items():
            f.write(f"{'='*40}\n{label} GeV\n")
            popt2, perr2, _ = fit['poly2']
            f.write(f"二次 (1 + b*x + c*x²): b={popt2[0]:.6f}±{perr2[0]:.6f}, c={popt2[1]:.6f}±{perr2[1]:.6f}\n")
            popt3, perr3, _ = fit['poly3']
            f.write(f"三次 (1 + b*x + c*x² + d*x³): b={popt3[0]:.6f}±{perr3[0]:.6f}, c={popt3[1]:.6f}±{perr3[1]:.6f}, d={popt3[2]:.6f}±{perr3[2]:.6f}\n")
            x = fit['x']; y = fit['y']
            yp2 = poly2_fixed(x, *popt2)
            yp3 = poly3_fixed(x, *popt3)
            ss_tot = np.sum((y - np.mean(y))**2)
            r2_2 = 1 - np.sum((y - yp2)**2)/ss_tot if ss_tot>0 else 0
            r2_3 = 1 - np.sum((y - yp3)**2)/ss_tot if ss_tot>0 else 0
            f.write(f"R²: quadratic={r2_2:.6f}, cubic={r2_3:.6f}\n\n")
    print(f"结果保存为: {outprefix}_results.txt")

def process_file(filename, prefix):
    if not os.path.exists(filename):
        print(f"文件不存在: {filename}")
        return
    try:
        pvals, bins, ratios, ptype = read_ratio_file(filename)
        fit_and_plot(pvals, bins, ratios, ptype, prefix)
    except Exception as e:
        print(f"处理 {filename} 时出错: {e}")

if __name__ == "__main__":
    print("处理HB文件...")
    process_file(hb_file, "HB")
    print("\n处理HW文件...")
    process_file(hw_file, "HW")
    print("\n完成。")