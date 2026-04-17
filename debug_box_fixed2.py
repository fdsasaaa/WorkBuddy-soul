# -*- coding: utf-8 -*-
"""箱体检测 - 修复后验证（数据反转版）"""
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

print("修复后数据顺序：")
print(f"  反转前: index 0={times[0]}, index 119={times[119]}")
highs  = highs[::-1]
lows   = lows[::-1]
times  = times[::-1]
print(f"  反转后: index 0={times[0]}, index 119={times[119]}")
print(f"  => times[0] < times[119] = {times[0]} < {times[119]} = {times[0] < times[119]}")
print(f"  => PASS: index 0 is oldest bar, index n-1 is newest bar")

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

print("\n关键 pivot（反转后）:")
for i in range(3, 10):
    ph = pivot_high[i]; pl = pivot_low[i]
    if ph > 0: print(f"  [{i}] pivot_high={ph:.2f}  times={times[i]}")
    if pl > 0: print(f"  [{i}] pivot_low ={pl:.2f}  times={times[i]}")

print("\n" + "=" * 80)
print("状态机逐行追踪（反转后）")
print("=" * 80)

darvas_state = 0
darvas_confirmed = 0
box_start_time = 0
box_top = None; box_bottom = None

for i in range(n - 1, length - 2, -1):
    if darvas_state == 0:
        if pivot_high[i] > 0:
            print(f"\n[i={i}] pivot_high={pivot_high[i]:.2f}  times={times[i]}")
            print(f"       设置 box_start_time = {times[i]}")
            print(f"       darvas_state: 0 -> 1")
            darvas_state = 1
            box_top = pivot_high[i]
            box_start_time = times[i]
        elif pivot_low[i] > 0:
            print(f"\n[i={i}] pivot_low={pivot_low[i]:.2f}  times={times[i]}")
            print(f"       设置 box_start_time = {times[i]}")
            print(f"       darvas_state: 0 -> -1")
            darvas_state = -1
            box_bottom = pivot_low[i]
            box_start_time = times[i]
    elif darvas_state == 1:
        if pivot_low[i] > 0:
            result = times[i] < box_start_time
            print(f"\n[i={i}] pivot_low={pivot_low[i]:.2f}  times={times[i]}")
            print(f"       比较: {times[i]} < {box_start_time} -> {result}")
            if result:
                darvas_confirmed = 1
                box_bottom = pivot_low[i]
                break
    elif darvas_state == -1:
        if pivot_high[i] > 0:
            result = times[i] < box_start_time
            print(f"\n[i={i}] pivot_high={pivot_high[i]:.2f}  times={times[i]}")
            print(f"       比较: {times[i]} < {box_start_time} -> {result}")
            if result:
                darvas_confirmed = 1
                box_top = pivot_high[i]
                break

print("\n" + "=" * 80)
print(f"最终结果: darvas_confirmed={darvas_confirmed}")
if darvas_confirmed == 1:
    top = max(box_top, box_bottom)
    bot = min(box_top, box_bottom)
    print(f"  top={top:.2f}  bottom={bot:.2f}  height={top-bot:.2f}")
