# -*- coding: utf-8 -*-
"""箱体检测 - 修复后完整验证"""
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

print("SECTION A: Data orientation check")
print("BEFORE reversal: times[0]=%d, times[119]=%d" % (times[0], times[119]))
print("Max time at index %d, Min time at index %d" % (times.index(max(times)), times.index(min(times))))

# Apply reversal (matching the actual fix in ai_brain.py)
highs  = highs[::-1]
lows   = lows[::-1]
times  = times[::-1]

print("AFTER reversal:  times[0]=%d, times[119]=%d" % (times[0], times[119]))
print("Index 0 = oldest, Index 119 = newest: %s" % (times[0] < times[119]))

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
    if is_max:
        pivot_high[i] = center_val

pivot_low = [0.0] * n
for i in range(length - 1, n):
    center_val = lows[i - strength]
    is_min = True
    for j in range(length):
        if j == strength: continue
        if lows[i - j] <= center_val:
            is_min = False; break
    if is_min:
        pivot_low[i] = center_val

print("\nSECTION B: Pivot table (with bar index)")
print("pivot_idx | pivot_val | actual_bar | bar_high/low | times[bar] | offset")
print("-" * 80)
for i in range(length - 1, n):
    if pivot_high[i] > 0:
        bar = i - strength
        print("PH[%3d]   | %9.2f | bar[%3d]   | %9.2f      | %10d | %d" % (
            i, pivot_high[i], bar, highs[bar], times[bar], strength))
    if pivot_low[i] > 0:
        bar = i - strength
        print("PL[%3d]   | %9.2f | bar[%3d]   | %9.2f      | %10d | %d" % (
            i, pivot_low[i], bar, lows[bar], times[bar], strength))

print("\nSECTION C: State machine trace")
print("=" * 80)

darvas_state = 0
darvas_confirmed = 0
box_start_time = 0
box_top = None; box_bottom = None

for i in range(n - 1, length - 2, -1):
    if darvas_state == 0:
        if pivot_high[i] > 0:
            bar = i - strength
            ts = times[bar]
            print("i=%3d PH=%8.2f bar[%d] times[%d]=%d -> set box_start_time=%d state=1" % (
                i, pivot_high[i], bar, bar, ts, ts))
            darvas_state = 1
            box_top = pivot_high[i]
            box_start_time = times[bar]
        elif pivot_low[i] > 0:
            bar = i - strength
            ts = times[bar]
            print("i=%3d PL=%8.2f bar[%d] times[%d]=%d -> set box_start_time=%d state=-1" % (
                i, pivot_low[i], bar, bar, ts, ts))
            darvas_state = -1
            box_bottom = pivot_low[i]
            box_start_time = times[bar]
    elif darvas_state == 1:
        if pivot_low[i] > 0:
            bar = i - strength
            ts = times[bar]
            result = ts < box_start_time
            print("i=%3d PL=%8.2f bar[%d] times[%d]=%d < box_start_time=%d -> %s" % (
                i, pivot_low[i], bar, bar, ts, box_start_time, result))
            if result:
                darvas_confirmed = 1
                box_bottom = pivot_low[i]
                break
    elif darvas_state == -1:
        if pivot_high[i] > 0:
            bar = i - strength
            ts = times[bar]
            result = ts < box_start_time
            print("i=%3d PH=%8.2f bar[%d] times[%d]=%d < box_start_time=%d -> %s" % (
                i, pivot_high[i], bar, bar, ts, box_start_time, result))
            if result:
                darvas_confirmed = 1
                box_top = pivot_high[i]
                break

print("=" * 80)
print("RESULT: darvas_state=%d darvas_confirmed=%d" % (darvas_state, darvas_confirmed))
if darvas_confirmed == 1:
    top = max(box_top, box_bottom)
    bot = min(box_top, box_bottom)
    print("BOX DETECTED: top=%.2f bottom=%.2f height=%.2f" % (top, bot, top-bot))
else:
    print("NO BOX DETECTED")
