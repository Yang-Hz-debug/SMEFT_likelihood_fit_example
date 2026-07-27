# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
# import pandas as pd

# # 定义HB值（从列名中提取）
# HB_values = np.array([0.01, 0.0848, 0.1595, 0.18, 0.2343, 0.309, 0.3838, 0.45, 0.4585, 
#                       0.5333, 0.608, 0.6828, 0.7575, 0.8323, 0.9, 0.907, 0.9818, 1.0565, 
#                       1.1313, 1.206, 1.2808, 1.35, 1.3555, 1.4303, 1.505, 1.5798, 1.6545, 
#                       1.7293, 1.804, 1.8787, 1.9535, 2.0282, 2.103, 2.1778, 2.2525, 2.3273])

# # 定义分bin边界
# bin_edges = [0, 60, 120, 200, 300, 450, 9999999]
# bin_labels = ['0-60', '60-120', '120-200', '200-300', '300-450', '450+']

# # 从数据中提取每个bin的ratio值（这里我重新整理数据）
# # 根据你提供的数据，每个bin有36个ratio值对应36个HB值
# ratios_data = {
#     '0-60': np.array([1.00069, 0.99720, 0.99692, 1.00125, 0.99622, 0.99606, 0.99619, 0.99544, 
#                       0.98934, 0.99468, 0.99320, 0.98879, 0.98473, 0.99194, 0.98555, 0.98767, 
#                       0.98453, 0.98106, 0.98199, 0.97922, 0.97431, 0.97804, 0.97327, 0.97411, 
#                       0.97235, 0.96937, 0.96529, 0.96131, 0.96090, 0.95743, 0.95601, 0.95039, 
#                       0.94712, 0.94431, 0.94413, 0.93892]),
#     '60-120': np.array([0.99981, 1.00929, 1.00371, 1.00246, 1.00488, 1.00273, 0.99888, 0.99976, 
#                         1.00573, 0.99970, 0.99789, 1.00168, 1.00269, 0.99841, 1.00042, 0.99713, 
#                         1.00179, 0.99879, 0.99619, 0.99580, 1.00117, 0.99311, 0.99612, 0.99215, 
#                         0.99675, 0.99111, 0.99461, 0.99584, 0.99196, 0.99198, 0.98777, 0.98946, 
#                         0.98818, 0.98958, 0.98498, 0.98840]),
#     '120-200': np.array([1.00307, 0.98935, 0.99964, 0.99983, 0.99785, 1.00134, 1.00917, 1.00560, 
#                          1.00987, 1.00621, 1.01168, 1.01307, 1.01597, 1.00889, 1.02140, 1.01680, 
#                          1.01268, 1.02438, 1.02280, 1.02522, 1.02288, 1.02798, 1.03617, 1.03893, 
#                          1.02678, 1.03826, 1.04757, 1.04640, 1.04963, 1.05222, 1.06220, 1.06426, 
#                          1.06493, 1.07574, 1.07560, 1.07591]),
#     '200-300': np.array([0.97506, 0.96968, 0.98779, 0.97010, 0.97703, 0.98541, 1.00228, 1.00197, 
#                          0.99534, 1.01635, 1.02080, 1.01097, 1.03487, 1.01852, 1.02142, 1.04532, 
#                          1.03849, 1.05691, 1.06467, 1.07305, 1.07946, 1.09498, 1.08350, 1.09053, 
#                          1.10419, 1.12468, 1.11029, 1.12654, 1.13844, 1.16275, 1.16327, 1.17600, 
#                          1.20486, 1.20083, 1.21469, 1.22359]),
#     '300-450': np.array([1.01491, 1.02237, 1.03885, 0.97881, 1.06907, 1.08163, 1.03964, 1.08359, 
#                          1.09027, 1.06319, 1.08791, 1.13579, 1.12716, 1.12912, 1.13344, 1.12245, 
#                          1.15777, 1.16523, 1.22174, 1.23783, 1.25000, 1.25235, 1.27826, 1.30455, 
#                          1.31044, 1.35871, 1.33870, 1.37480, 1.41954, 1.42543, 1.47881, 1.54945, 
#                          1.58634, 1.54082, 1.60126, 1.65424]),
#     '450+': np.array([1.05463, 1.08498, 1.03035, 0.97724, 1.11836, 1.08649, 1.09712, 1.12443, 
#                       1.12291, 1.09256, 1.13354, 1.20637, 1.25493, 1.29287, 1.31715, 1.37633, 
#                       1.42185, 1.47951, 1.44765, 1.64036, 1.67375, 1.68589, 1.66616, 1.73445, 
#                       1.81032, 1.98483, 1.94234, 2.10622, 2.19879, 2.24431, 2.31563, 2.42792, 
#                       2.54173, 2.45220, 2.70258, 2.72382])
# }

# # 定义多项式拟合函数
# def poly2(x, a, b, c):
#     return a + b*x + c*x**2

# def poly3(x, a, b, c, d):
#     return a + b*x + c*x**2 + d*x**3

# # 存储拟合结果
# results = {}

# # 对每个bin进行拟合
# for bin_label, ratios in ratios_data.items():
#     results[bin_label] = {}
    
#     # 二次多项式拟合
#     popt2, pcov2 = curve_fit(poly2, HB_values, ratios)
#     perr2 = np.sqrt(np.diag(pcov2))
#     results[bin_label]['poly2'] = {'params': popt2, 'errors': perr2, 'cov': pcov2}
    
#     # 三次多项式拟合
#     popt3, pcov3 = curve_fit(poly3, HB_values, ratios)
#     perr3 = np.sqrt(np.diag(pcov3))
#     results[bin_label]['poly3'] = {'params': popt3, 'errors': perr3, 'cov': pcov3}

# # 打印结果
# print("=" * 80)
# print("拟合结果汇总")
# print("=" * 80)

# for bin_label in bin_labels:
#     print(f"\n{'='*40}")
#     print(f"pT Bin: {bin_label}")
#     print(f"{'='*40}")
    
#     # 二次多项式
#     popt2 = results[bin_label]['poly2']['params']
#     perr2 = results[bin_label]['poly2']['errors']
#     print(f"\n二次多项式: f(x) = a + b*x + c*x^2")
#     print(f"  a = {popt2[0]:.6f} ± {perr2[0]:.6f}")
#     print(f"  b = {popt2[1]:.6f} ± {perr2[1]:.6f}")
#     print(f"  c = {popt2[2]:.6f} ± {perr2[2]:.6f}")
    
#     # 三次多项式
#     popt3 = results[bin_label]['poly3']['params']
#     perr3 = results[bin_label]['poly3']['errors']
#     print(f"\n三次多项式: f(x) = a + b*x + c*x^2 + d*x^3")
#     print(f"  a = {popt3[0]:.6f} ± {perr3[0]:.6f}")
#     print(f"  b = {popt3[1]:.6f} ± {perr3[1]:.6f}")
#     print(f"  c = {popt3[2]:.6f} ± {perr3[2]:.6f}")
#     print(f"  d = {popt3[3]:.6f} ± {perr3[3]:.6f}")

# # 绘图
# fig, axes = plt.subplots(2, 3, figsize=(18, 10))
# axes = axes.flatten()

# HB_smooth = np.linspace(0, 2.4, 1000)

# for idx, bin_label in enumerate(bin_labels):
#     ax = axes[idx]
#     ratios = ratios_data[bin_label]
    
#     # 绘制原始数据点
#     ax.scatter(HB_values, ratios, color='blue', s=30, label='Data', zorder=5)
    
#     # 二次多项式拟合曲线
#     popt2 = results[bin_label]['poly2']['params']
#     y_smooth2 = poly2(HB_smooth, *popt2)
#     ax.plot(HB_smooth, y_smooth2, 'r-', linewidth=2, label='Quadratic fit', zorder=3)
    
#     # 三次多项式拟合曲线
#     popt3 = results[bin_label]['poly3']['params']
#     y_smooth3 = poly3(HB_smooth, *popt3)
#     ax.plot(HB_smooth, y_smooth3, 'g--', linewidth=2, label='Cubic fit', zorder=4)
    
#     # 绘制误差带（二次拟合的1-sigma）
#     # 计算预测值的标准差（简化版本，只考虑参数误差）
#     y_std = np.sqrt(np.diag(np.column_stack([np.ones_like(HB_smooth), 
#                                              HB_smooth, 
#                                              HB_smooth**2]) @ results[bin_label]['poly2']['cov'] @ 
#                             np.column_stack([np.ones_like(HB_smooth), HB_smooth, HB_smooth**2]).T))
#     ax.fill_between(HB_smooth, y_smooth2 - y_std, y_smooth2 + y_std, 
#                     color='red', alpha=0.2, label='1σ band (quadratic)')
    
#     ax.set_xlabel('HB', fontsize=12)
#     ax.set_ylabel('Ratio (SMEFT/SM)', fontsize=12)
#     ax.set_title(f'pT bin: {bin_label} GeV', fontsize=14)
#     ax.grid(True, alpha=0.3)
#     ax.legend(loc='best')
#     ax.set_xlim([0, 2.4])
    
#     # 添加拟合信息到图上
#     chi2_2 = np.sum(((ratios - poly2(HB_values, *popt2))**2) / (ratios**2 + 1e-10))
#     chi2_3 = np.sum(((ratios - poly3(HB_values, *popt3))**2) / (ratios**2 + 1e-10))
#     ax.text(0.05, 0.95, f'χ²_quad = {chi2_2:.3f}\nχ²_cubic = {chi2_3:.3f}', 
#             transform=ax.transAxes, verticalalignment='top',
#             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# # 隐藏多余的子图
# for idx in range(len(bin_labels), 6):
#     axes[idx].set_visible(False)

# plt.tight_layout()
# plt.savefig('HB_pT_bin_fits.png', dpi=300, bbox_inches='tight')
# plt.show()

# # 保存详细结果到CSV
# results_df = []
# for bin_label in bin_labels:
#     popt2 = results[bin_label]['poly2']['params']
#     perr2 = results[bin_label]['poly2']['errors']
#     popt3 = results[bin_label]['poly3']['params']
#     perr3 = results[bin_label]['poly3']['errors']
    
#     results_df.append({
#         'pT_bin': bin_label,
#         'poly2_a': popt2[0], 'poly2_a_err': perr2[0],
#         'poly2_b': popt2[1], 'poly2_b_err': perr2[1],
#         'poly2_c': popt2[2], 'poly2_c_err': perr2[2],
#         'poly3_a': popt3[0], 'poly3_a_err': perr3[0],
#         'poly3_b': popt3[1], 'poly3_b_err': perr3[1],
#         'poly3_c': popt3[2], 'poly3_c_err': perr3[2],
#         'poly3_d': popt3[3], 'poly3_d_err': perr3[3]
#     })

# df_results = pd.DataFrame(results_df)
# df_results.to_csv('fit_results.csv', index=False)
# print("\n拟合结果已保存到 fit_results.csv")

# # 额外计算每个拟合的R²值
# print("\n" + "="*80)
# print("拟合优度 (R²)")
# print("="*80)

# for bin_label in bin_labels:
#     ratios = ratios_data[bin_label]
#     popt2 = results[bin_label]['poly2']['params']
#     popt3 = results[bin_label]['poly3']['params']
    
#     y_pred2 = poly2(HB_values, *popt2)
#     y_pred3 = poly3(HB_values, *popt3)
    
#     ss_res2 = np.sum((ratios - y_pred2)**2)
#     ss_res3 = np.sum((ratios - y_pred3)**2)
#     ss_tot = np.sum((ratios - np.mean(ratios))**2)
    
#     r2_2 = 1 - ss_res2/ss_tot
#     r2_3 = 1 - ss_res3/ss_tot
    
#     print(f"\n{bin_label} GeV:")
#     print(f"  Quadratic R² = {r2_2:.6f}")
#     print(f"  Cubic R²     = {r2_3:.6f}")

import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys

# 定义HB值
HB_values = np.array([0.01, 0.0848, 0.1595, 0.18, 0.2343, 0.309, 0.3838, 0.45, 0.4585, 
                      0.5333, 0.608, 0.6828, 0.7575, 0.8323, 0.9, 0.907, 0.9818, 1.0565, 
                      1.1313, 1.206, 1.2808, 1.35, 1.3555, 1.4303, 1.505, 1.5798, 1.6545, 
                      1.7293, 1.804, 1.8787, 1.9535, 2.0282, 2.103, 2.1778, 2.2525, 2.3273])

# 从数据中提取每个bin的ratio值
ratios_data = {
    '0-60': np.array([1.00069, 0.99720, 0.99692, 1.00125, 0.99622, 0.99606, 0.99619, 0.99544, 
                      0.98934, 0.99468, 0.99320, 0.98879, 0.98473, 0.99194, 0.98555, 0.98767, 
                      0.98453, 0.98106, 0.98199, 0.97922, 0.97431, 0.97804, 0.97327, 0.97411, 
                      0.97235, 0.96937, 0.96529, 0.96131, 0.96090, 0.95743, 0.95601, 0.95039, 
                      0.94712, 0.94431, 0.94413, 0.93892]),
    '60-120': np.array([0.99981, 1.00929, 1.00371, 1.00246, 1.00488, 1.00273, 0.99888, 0.99976, 
                        1.00573, 0.99970, 0.99789, 1.00168, 1.00269, 0.99841, 1.00042, 0.99713, 
                        1.00179, 0.99879, 0.99619, 0.99580, 1.00117, 0.99311, 0.99612, 0.99215, 
                        0.99675, 0.99111, 0.99461, 0.99584, 0.99196, 0.99198, 0.98777, 0.98946, 
                        0.98818, 0.98958, 0.98498, 0.98840]),
    '120-200': np.array([1.00307, 0.98935, 0.99964, 0.99983, 0.99785, 1.00134, 1.00917, 1.00560, 
                         1.00987, 1.00621, 1.01168, 1.01307, 1.01597, 1.00889, 1.02140, 1.01680, 
                         1.01268, 1.02438, 1.02280, 1.02522, 1.02288, 1.02798, 1.03617, 1.03893, 
                         1.02678, 1.03826, 1.04757, 1.04640, 1.04963, 1.05222, 1.06220, 1.06426, 
                         1.06493, 1.07574, 1.07560, 1.07591]),
    '200-300': np.array([0.97506, 0.96968, 0.98779, 0.97010, 0.97703, 0.98541, 1.00228, 1.00197, 
                         0.99534, 1.01635, 1.02080, 1.01097, 1.03487, 1.01852, 1.02142, 1.04532, 
                         1.03849, 1.05691, 1.06467, 1.07305, 1.07946, 1.09498, 1.08350, 1.09053, 
                         1.10419, 1.12468, 1.11029, 1.12654, 1.13844, 1.16275, 1.16327, 1.17600, 
                         1.20486, 1.20083, 1.21469, 1.22359]),
    '300-450': np.array([1.01491, 1.02237, 1.03885, 0.97881, 1.06907, 1.08163, 1.03964, 1.08359, 
                         1.09027, 1.06319, 1.08791, 1.13579, 1.12716, 1.12912, 1.13344, 1.12245, 
                         1.15777, 1.16523, 1.22174, 1.23783, 1.25000, 1.25235, 1.27826, 1.30455, 
                         1.31044, 1.35871, 1.33870, 1.37480, 1.41954, 1.42543, 1.47881, 1.54945, 
                         1.58634, 1.54082, 1.60126, 1.65424]),
    '450+': np.array([1.05463, 1.08498, 1.03035, 0.97724, 1.11836, 1.08649, 1.09712, 1.12443, 
                      1.12291, 1.09256, 1.13354, 1.20637, 1.25493, 1.29287, 1.31715, 1.37633, 
                      1.42185, 1.47951, 1.44765, 1.64036, 1.67375, 1.68589, 1.66616, 1.73445, 
                      1.81032, 1.98483, 1.94234, 2.10622, 2.19879, 2.24431, 2.31563, 2.42792, 
                      2.54173, 2.45220, 2.70258, 2.72382])
}

# 定义多项式拟合函数
def poly2(x, a, b, c):
    return a + b*x + c*x**2

def poly3(x, a, b, c, d):
    return a + b*x + c*x**2 + d*x**3

# 存储拟合结果
results = {}

# 对每个bin进行拟合
for bin_label, ratios in ratios_data.items():
    results[bin_label] = {}
    
    # 二次多项式拟合
    try:
        popt2, pcov2 = curve_fit(poly2, HB_values, ratios)
        perr2 = np.sqrt(np.diag(pcov2))
        results[bin_label]['poly2'] = {'params': popt2, 'errors': perr2, 'cov': pcov2}
    except:
        print(f"Warning: Quadratic fit failed for bin {bin_label}")
        results[bin_label]['poly2'] = {'params': np.zeros(3), 'errors': np.zeros(3), 'cov': np.eye(3)}
    
    # 三次多项式拟合
    try:
        popt3, pcov3 = curve_fit(poly3, HB_values, ratios)
        perr3 = np.sqrt(np.diag(pcov3))
        results[bin_label]['poly3'] = {'params': popt3, 'errors': perr3, 'cov': pcov3}
    except:
        print(f"Warning: Cubic fit failed for bin {bin_label}")
        results[bin_label]['poly3'] = {'params': np.zeros(4), 'errors': np.zeros(4), 'cov': np.eye(4)}

# 打印结果
print("=" * 80)
print("拟合结果汇总")
print("=" * 80)

bin_labels = ['0-60', '60-120', '120-200', '200-300', '300-450', '450+']

for bin_label in bin_labels:
    print(f"\n{'='*40}")
    print(f"pT Bin: {bin_label} GeV")
    print(f"{'='*40}")
    
    # 二次多项式
    popt2 = results[bin_label]['poly2']['params']
    perr2 = results[bin_label]['poly2']['errors']
    print(f"\n二次多项式: f(x) = a + b*x + c*x^2")
    print(f"  a = {popt2[0]:.6f} ± {perr2[0]:.6f}")
    print(f"  b = {popt2[1]:.6f} ± {perr2[1]:.6f}")
    print(f"  c = {popt2[2]:.6f} ± {perr2[2]:.6f}")
    
    # 三次多项式
    popt3 = results[bin_label]['poly3']['params']
    perr3 = results[bin_label]['poly3']['errors']
    print(f"\n三次多项式: f(x) = a + b*x + c*x^2 + d*x^3")
    print(f"  a = {popt3[0]:.6f} ± {perr3[0]:.6f}")
    print(f"  b = {popt3[1]:.6f} ± {perr3[1]:.6f}")
    print(f"  c = {popt3[2]:.6f} ± {perr3[2]:.6f}")
    print(f"  d = {popt3[3]:.6f} ± {perr3[3]:.6f}")

# 绘图
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

HB_smooth = np.linspace(0, 2.4, 1000)

for idx, bin_label in enumerate(bin_labels):
    ax = axes[idx]
    ratios = ratios_data[bin_label]
    
    # 绘制原始数据点
    ax.scatter(HB_values, ratios, color='blue', s=30, label='Data', zorder=5)
    
    # 二次多项式拟合曲线
    popt2 = results[bin_label]['poly2']['params']
    if np.sum(np.abs(popt2)) > 0:  # 检查拟合是否成功
        y_smooth2 = poly2(HB_smooth, *popt2)
        ax.plot(HB_smooth, y_smooth2, 'r-', linewidth=2, label='Quadratic fit', zorder=3)
        
        # 绘制误差带（二次拟合的1-sigma）
        try:
            # 计算预测值的标准差
            X = np.column_stack([np.ones_like(HB_smooth), HB_smooth, HB_smooth**2])
            y_std = np.sqrt(np.diag(X @ results[bin_label]['poly2']['cov'] @ X.T))
            ax.fill_between(HB_smooth, y_smooth2 - y_std, y_smooth2 + y_std, 
                          color='red', alpha=0.2, label='1σ band (quadratic)')
        except:
            pass
    
    # 三次多项式拟合曲线
    popt3 = results[bin_label]['poly3']['params']
    if np.sum(np.abs(popt3)) > 0:
        y_smooth3 = poly3(HB_smooth, *popt3)
        ax.plot(HB_smooth, y_smooth3, 'g--', linewidth=2, label='Cubic fit', zorder=4)
    
    ax.set_xlabel('HB', fontsize=12)
    ax.set_ylabel('Ratio (SMEFT/SM)', fontsize=12)
    ax.set_title(f'pT bin: {bin_label} GeV', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    ax.set_xlim([0, 2.4])
    
    # 添加拟合信息到图上
    try:
        chi2_2 = np.sum(((ratios - poly2(HB_values, *popt2))**2) / (ratios**2 + 1e-10))
        chi2_3 = np.sum(((ratios - poly3(HB_values, *popt3))**2) / (ratios**2 + 1e-10))
        ax.text(0.05, 0.95, f'χ²_quad = {chi2_2:.3f}\nχ²_cubic = {chi2_3:.3f}', 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    except:
        pass

# 隐藏多余的子图
for idx in range(len(bin_labels), 6):
    axes[idx].set_visible(False)

plt.tight_layout()
plt.savefig('HB_pT_bin_fits.png', dpi=300, bbox_inches='tight')
print("\n图表已保存为 HB_pT_bin_fits.png")

# 保存结果到文本文件
with open('fit_results.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("拟合结果汇总\n")
    f.write("=" * 80 + "\n\n")
    
    for bin_label in bin_labels:
        f.write(f"\n{'='*40}\n")
        f.write(f"pT Bin: {bin_label} GeV\n")
        f.write(f"{'='*40}\n")
        
        popt2 = results[bin_label]['poly2']['params']
        perr2 = results[bin_label]['poly2']['errors']
        f.write(f"\n二次多项式: f(x) = a + b*x + c*x^2\n")
        f.write(f"  a = {popt2[0]:.6f} ± {perr2[0]:.6f}\n")
        f.write(f"  b = {popt2[1]:.6f} ± {perr2[1]:.6f}\n")
        f.write(f"  c = {popt2[2]:.6f} ± {perr2[2]:.6f}\n")
        
        popt3 = results[bin_label]['poly3']['params']
        perr3 = results[bin_label]['poly3']['errors']
        f.write(f"\n三次多项式: f(x) = a + b*x + c*x^2 + d*x^3\n")
        f.write(f"  a = {popt3[0]:.6f} ± {perr3[0]:.6f}\n")
        f.write(f"  b = {popt3[1]:.6f} ± {perr3[1]:.6f}\n")
        f.write(f"  c = {popt3[2]:.6f} ± {perr3[2]:.6f}\n")
        f.write(f"  d = {popt3[3]:.6f} ± {perr3[3]:.6f}\n")
        
        # 计算R²
        ratios = ratios_data[bin_label]
        y_pred2 = poly2(HB_values, *popt2)
        y_pred3 = poly3(HB_values, *popt3)
        ss_res2 = np.sum((ratios - y_pred2)**2)
        ss_res3 = np.sum((ratios - y_pred3)**2)
        ss_tot = np.sum((ratios - np.mean(ratios))**2)
        r2_2 = 1 - ss_res2/ss_tot
        r2_3 = 1 - ss_res3/ss_tot
        f.write(f"\n拟合优度:\n")
        f.write(f"  Quadratic R² = {r2_2:.6f}\n")
        f.write(f"  Cubic R²     = {r2_3:.6f}\n")

print("\n拟合结果已保存到 fit_results.txt")

# 打印R²值到屏幕
print("\n" + "="*80)
print("拟合优度 (R²)")
print("="*80)

for bin_label in bin_labels:
    ratios = ratios_data[bin_label]
    popt2 = results[bin_label]['poly2']['params']
    popt3 = results[bin_label]['poly3']['params']
    
    y_pred2 = poly2(HB_values, *popt2)
    y_pred3 = poly3(HB_values, *popt3)
    
    ss_res2 = np.sum((ratios - y_pred2)**2)
    ss_res3 = np.sum((ratios - y_pred3)**2)
    ss_tot = np.sum((ratios - np.mean(ratios))**2)
    
    r2_2 = 1 - ss_res2/ss_tot
    r2_3 = 1 - ss_res3/ss_tot
    
    print(f"\n{bin_label} GeV:")
    print(f"  Quadratic R² = {r2_2:.6f}")
    print(f"  Cubic R²     = {r2_3:.6f}")