# -*- coding: utf-8 -*-
"""箱体检测 - 验证同一索引下各数组是否对齐同一根 bar"""
import re

DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

with open(DATA_FILE, encoding="utf-8") as f:
    raw = f.read()

m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
n = int(m.group(1))
pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)

def sf(s): return [float(x) for x in s.split(",")] if s else []
def si(s): return [int(x) for x in s.split(",")] if s else []

closes = sf(pairs.get("CLOSE", ""))
highs  = sf(pairs.get("HIGH", ""))
lows   = sf(pairs.get("LOW", ""))
times  = si(pairs.get("TIME", ""))

strength = 3
length = strength + 2

pivot_high = [0.0] * n
for i in range(length - 1, n):
    center_val = highs[i - strength]
    is_max = True
    for j in range(length):
        if j == strength: continue
        if highs[i - j] >= center_val:
            is_max = False; break
    if is_max: pivot_high[i] = center_val

pivot_low = [0.0] * n
for i in range(length - 1, n):
    center_val = lows[i - strength]
    is_min = True
    for j in range(length):
        if j == strength: continue
        if lows[i - j] <= center_val:
            is_min = False; break
    if is_min: pivot_low[i] = center_val

print("=" * 90)
print("索引  |  times           |  high     |  low      |  pivot_high |  pivot_low")
print("=" * 90)
for i in range(110, 120):
    ph = pivot_high[i]
    pl = pivot_low[i]
    print(f"[{i:3d}]  |  {times[i]:>12}  |  {highs[i]:>8.2f}  |  {lows[i]:>8.2f}  |  {ph:>10.2f}  |  {pl:>10.2f}")

print("\n" + "=" * 90)
print("同向性检查（索引增大时，high/low/close 是否同步变化）")
print("=" * 90)

print("\n索引 110~117 的 high / low / close 对应关系:")
for i in range(110, 120):
    c = closes[i] if i < len(closes) else 0
    print(f"  [{i}] close={c:.2f}  high={highs[i]:.2f}  low={lows[i]:.2f}  (close应在high和low之间)")

print("\n索引 117 是 pivot_low=4667.11，验证该 bar 的数据:")
print(f"  high[{i}]={highs[117]:.2f}")
print(f"  low[{i}] ={lows[117]:.2f}")
print(f"  pivot_low[{i}]={pivot_low[117]:.2f}")
print(f"  断言: pivot_low[{i}] == low[{i}] -> {pivot_low[117] == lows[117]}")

print("\n索引 114 是 pivot_high=4747.83，验证该 bar 的数据:")
print(f"  high[{i}]={highs[114]:.2f}")
print(f"  low[{i}] ={lows[114]:.2f}")
print(f"  pivot_high[{i}]={pivot_high[114]:.2f}")
print(f"  断言: pivot_high[{i}] == high[{i}] -> {pivot_high[114] == highs[114]}")
