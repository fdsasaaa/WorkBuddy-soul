# -*- coding: utf-8 -*-
"""箱体检测 - 修复后的逻辑验证"""
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

print("=" * 90)
print("修复后：状态机逐行追踪（使用 times[i - strength]）")
print("=" * 90)

darvas_state = 0
darvas_confirmed = 0
box_start_time = 0
box_top = None; box_bottom = None

for i in range(n - 1, length - 2, -1):
    if darvas_state == 0:
        if pivot_high[i] > 0:
            bar_idx = i - strength
            print(f"\n[i={i}] 发现 pivot_high={pivot_high[i]:.2f}  来自 bar[{bar_idx}]")
            print(f"       times[{i}]={times[i]}  ->  实际 bar 的时间 times[{bar_idx}]={times[bar_idx]}")
            print(f"       设置 box_start_time = {times[bar_idx]}")
            print(f"       darvas_state: 0 -> 1")
            darvas_state = 1
            box_top = pivot_high[i]
            box_start_time = times[bar_idx]
        elif pivot_low[i] > 0:
            bar_idx = i - strength
            print(f"\n[i={i}] 发现 pivot_low={pivot_low[i]:.2f}  来自 bar[{bar_idx}]")
            print(f"       times[{i}]={times[i]}  ->  实际 bar 的时间 times[{bar_idx}]={times[bar_idx]}")
            print(f"       设置 box_start_time = {times[bar_idx]}")
            print(f"       darvas_state: 0 -> -1")
            darvas_state = -1
            box_bottom = pivot_low[i]
            box_start_time = times[bar_idx]
    elif darvas_state == 1:
        if pivot_low[i] > 0:
            bar_idx = i - strength
            actual_time = times[bar_idx]
            expr = f"times[{bar_idx}]={actual_time} < box_start_time={box_start_time}"
            result = actual_time < box_start_time
            print(f"\n[i={i}] 发现 pivot_low={pivot_low[i]:.2f}  来自 bar[{bar_idx}]")
            print(f"       比较: {expr}")
            print(f"       结果: {result}")
            if result:
                print(f"       -> 箱体确认!")
                box_bottom = pivot_low[i]
                darvas_confirmed = 1
                break
    elif darvas_state == -1:
        if pivot_high[i] > 0:
            bar_idx = i - strength
            actual_time = times[bar_idx]
            expr = f"times[{bar_idx}]={actual_time} < box_start_time={box_start_time}"
            result = actual_time < box_start_time
            print(f"\n[i={i}] 发现 pivot_high={pivot_high[i]:.2f}  来自 bar[{bar_idx}]")
            print(f"       比较: {expr}")
            print(f"       结果: {result}")
            if result:
                print(f"       -> 箱体确认!")
                box_top = pivot_high[i]
                darvas_confirmed = 1
                break

print("\n" + "=" * 90)
print(f"最终结果: darvas_state={darvas_state}, darvas_confirmed={darvas_confirmed}")
print("=" * 90)
if darvas_confirmed == 1:
    top = max(box_top, box_bottom)
    bot = min(box_top, box_bottom)
    h = top - bot
    print(f"\n箱体检测成功!")
    print(f"  top:    {top:.2f}")
    print(f"  bottom: {bot:.2f}")
    print(f"  height: {h:.2f}")
else:
    print(f"\n箱体检测失败")
