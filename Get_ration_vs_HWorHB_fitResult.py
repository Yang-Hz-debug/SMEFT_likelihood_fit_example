import re

def parse_fit_results(text):
    """
    解析拟合结果文本，提取每个区间的二次拟合系数 (b, err_b, c, err_c)
    支持区间格式：数字-数字 或 数字+（如 450.0+ GeV）
    返回字典：{区间key: (b, err_b, c, err_c)}
    key 格式为 "pTH_低_高"，低/高均为整数（'inf' 表示无穷）
    """
    pattern = re.compile(
        r'([\d.]+)\s*([-+])\s*([\d.]+)?\s*GeV\s*\n'          # 区间行
        r'二次\s*\([^)]+\):\s*'                               # "二次 (...):"
        r'b=([+-]?\d+\.\d+)±([+-]?\d+\.\d+),\s*'              # b=值±误差
        r'c=([+-]?\d+\.\d+)±([+-]?\d+\.\d+)',                 # c=值±误差
        re.MULTILINE
    )
    results = {}
    for match in pattern.finditer(text):
        low = float(match.group(1))
        low_str = str(int(low))               # 0.0 → "0"
        sep = match.group(2)
        high = match.group(3)
        if high is not None:
            high_val = float(high)
            high_str = str(int(high_val))     # 60.0 → "60"
        else:
            # 若分隔符为 '+' 且无数字，则视为无穷大
            high_str = 'inf'
        key = f"pTH_{low_str}_{high_str}"     # 例如 "pTH_0_60"
        b = float(match.group(4))
        err_b = float(match.group(5))
        c = float(match.group(6))
        err_c = float(match.group(7))
        results[key] = (b, err_b, c, err_c)
    return results

def combine_coeffs(hw_results, hb_results):
    """
    合并 HW 和 HB 结果，生成 (a, err_a, b, err_b, c, err_c, d, err_d)
    其中 a,b 来自 HB (一次项, 二次项)
         c,d 来自 HW (一次项, 二次项)
    """
    combined = {}
    for key, hw_vals in hw_results.items():
        if key in hb_results:
            a, ea, b, eb = hb_results[key]   # HB: (b, err_b, c, err_c) → 赋值给 a,b
            c, ec, d, ed = hw_vals           # HW: (b, err_b, c, err_c) → 赋值给 c,d
            combined[key] = (a, ea, b, eb, c, ec, d, ed)
        else:
            print(f"Warning: key {key} not found in HB results")
    return combined

def print_coeffs(combined):
    """打印中心值、带误差的元组和相对不确定度"""
    print("# --- bin coefficients (central values) ---")
    print("coeffs_central = {")
    for key, vals in combined.items():
        a, _, b, _, c, _, d, _ = vals
        print(f'    "{key}":    ({a:.6f}, {b:.6f}, {c:.6f}, {d:.6f}),')
    print("}\n")

    print("# --- bin coefficients with uncertainties (8-tuple) ---")
    print("coeffs_with_err = {")
    for key, vals in combined.items():
        a, ea, b, eb, c, ec, d, ed = vals
        print(f'    "{key}":    ({a:.6f}, {ea:.6f}, {b:.6f}, {eb:.6f}, {c:.6f}, {ec:.6f}, {d:.6f}, {ed:.6f}),')
    print("}\n")

    print("# --- relative uncertainties (%) ---")
    print("rel_unc = {")
    for key, vals in combined.items():
        a, ea, b, eb, c, ec, d, ed = vals
        rel_a = (ea / abs(a) * 100) if a != 0 else float('inf')
        rel_b = (eb / abs(b) * 100) if b != 0 else float('inf')
        rel_c = (ec / abs(c) * 100) if c != 0 else float('inf')
        rel_d = (ed / abs(d) * 100) if d != 0 else float('inf')
        print(f'    "{key}":    a: {rel_a:.2f}%, b: {rel_b:.2f}%, c: {rel_c:.2f}%, d: {rel_d:.2f}%,')
    print("}")

# ==================== 读取文件 ====================
try:
    with open('HB_results.txt', 'r', encoding='utf-8') as f:
        hb_text = f.read()
    with open('HW_results.txt', 'r', encoding='utf-8') as f:
        hw_text = f.read()
except FileNotFoundError as e:
    print(f"错误：找不到文件 - {e.filename}")
    exit(1)

# 解析
hw = parse_fit_results(hw_text)
hb = parse_fit_results(hb_text)

# 调试：打印键，确认格式正确
print("HW keys:", list(hw.keys()))
print("HB keys:", list(hb.keys()))

# 合并
combined = combine_coeffs(hw, hb)

# 按指定顺序输出
ordered_keys = ["pTH_0_60", "pTH_60_120", "pTH_120_200", "pTH_200_300", "pTH_300_450", "pTH_450_inf"]
combined_sorted = {k: combined[k] for k in ordered_keys if k in combined}

if not combined_sorted:
    print("警告：合并后没有有效数据，请检查文件内容和键名是否匹配。")

# 打印
print_coeffs(combined_sorted)