# -*- coding: utf-8 -*-
"""箱体检测 - 精确 pivot 来源验证"""
import re

DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

with open(DATA_FILE, encoding="utf-8") as f:
    raw = f.read()

m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
n = int(m.group(1))
pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)

def sf(s): return [float(x) for x in s.split(",")] if s else []
def si(s): return [int(x) for x in s.split(",")] if s else []

highs  = sf(pairs.get("HIGH", ""))
lows   = sf(pairs.get("LOW", ""))
times  = si(pairs.get("TIME", ""))

strength = 3
length = strength + 2

pivot_high = [0.0] * n
pivot_high_bar = [-1] * n
for i in range(length - 1, n):
    center_val = highs[i - strength]
    is_max = True
    for j in range(length):
        if j == strength: continue
        if highs[i - j] >= center_val:
            is_max = False; break
    if is_max:
        pivot_high[i] = center_val
        pivot_high_bar[i] = i - strength

pivot_low = [0.0] * n
pivot_low_bar = [-1] * n
for i in range(length - 1, n):
    center_val = lows[i - strength]
    is_min = True
    for j in range(length):
        if j == strength: continue
        if lows[i - j] <= center_val:
            is_min = False; break
    if is_min:
        pivot_low[i] = center_val
        pivot_low_bar[i] = i - strength

print("=" * 95)
print("索引    | times        | high       | pivot_high | pivot来自bar | 该bar的high  | 是否匹配")
print("=" * 95)
for i in range(110, 120):
    ph = pivot_high[i]
    bar_h = pivot_high_bar[i]
    if bar_h >= 0:
        actual_h = highs[bar_h]
        match = "是" if abs(ph - actual_h) < 0.01 else "否"
    else:
        actual_h = "-"; match = "-"
    ph_str = f"{ph:>10.2f}" if ph > 0 else "         -"
    bar_h_str = f"{bar_h:>5d}" if bar_h >= 0 else "    -"
    actual_h_str = f"{actual_h:>10.2f}" if isinstance(actual_h, float) else "          -"
    print(f"[{i:3d}]  |  {times[i]:>10}  |  {highs[i]:>8.2f}  |  {ph_str}  |  bar={bar_h_str}  |  {actual_h_str}  | {match}")

print("\n" + "=" * 95)
print("索引    | times        | low        | pivot_low  | pivot来自bar | 该bar的low   | 是否匹配")
print("=" * 95)
for i in range(110, 120):
    pl = pivot_low[i]
    bar_l = pivot_low_bar[i]
    if bar_l >= 0:
        actual_l = lows[bar_l]
        match = "是" if abs(pl - actual_l) < 0.01 else "否"
    else:
        actual_l = "-"; match = "-"
    pl_str = f"{pl:>10.2f}" if pl > 0 else "         -"
    bar_l_str = f"{bar_l:>5d}" if bar_l >= 0 else "    -"
    actual_l_str = f"{actual_l:>10.2f}" if isinstance(actual_l, float) else "          -"
    print(f"[{i:3d}]  |  {times[i]:>10}  |  {lows[i]:>8.2f}  |  {pl_str}  |  bar={bar_l_str}  |  {actual_l_str}  | {match}")

print("\n" + "=" * 95)
print("结论")
print("=" * 95)
print("\n所有 pivot 的来源 bar 对齐验证:")
for i in range(110, 120):
    ph = pivot_high[i]; pl = pivot_low[i]
    if ph > 0:
        bar = pivot_high_bar[i]
        match = abs(ph - highs[bar]) < 0.01
        print(f"  pivot_high[{i}]={ph:.2f} 来自 bar[{bar}]={highs[bar]:.2f}  匹配={match}")
    if pl > 0:
        bar = pivot_low_bar[i]
        match = abs(pl - lows[bar]) < 0.01
        print(f"  pivot_low[{i}] ={pl:.2f}  来自 bar[{bar}]={lows[bar]:.2f}  匹配={match}")
