# -*- coding: utf-8 -*-
"""箱体检测 - 版本对照验证"""
import re

DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

with open(DATA_FILE, encoding="utf-8") as f:
    raw = f.read()

m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
n = int(m.group(1))
pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)

def sf(s): return [float(x) for x in s.split(",")] if s else []
def si(s): return [int(x) for x in s.split(",")] if s else []

highs_raw  = sf(pairs.get("HIGH", ""))
lows_raw   = sf(pairs.get("LOW", ""))
times_raw  = si(pairs.get("TIME", ""))

strength = 3
length = strength + 2

def build_pivots(highs, lows, times):
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
    return pivot_high, pivot_low

def run_state_machine(highs, lows, times, pivot_high, pivot_low, version_label):
    darvas_state = 0
    darvas_confirmed = 0
    box_start_time = 0
    box_top = None; box_bottom = None

    for i in range(n - 1, length - 2, -1):
        if darvas_state == 0:
            if pivot_high[i] > 0:
                bar = i - strength
                ts = times[bar]
                darvas_state = 1
                box_top = pivot_high[i]
                box_start_time = ts
            elif pivot_low[i] > 0:
                bar = i - strength
                ts = times[bar]
                darvas_state = -1
                box_bottom = pivot_low[i]
                box_start_time = ts
        elif darvas_state == 1:
            if pivot_low[i] > 0:
                bar = i - strength
                if times[bar] < box_start_time:
                    darvas_confirmed = 1
                    box_bottom = pivot_low[i]
                    break
        elif darvas_state == -1:
            if pivot_high[i] > 0:
                bar = i - strength
                if times[bar] < box_start_time:
                    darvas_confirmed = 1
                    box_top = pivot_high[i]
                    break

    return darvas_confirmed, box_top, box_bottom

print("=" * 65)
print("数据源检查")
print("=" * 65)
print("原始数据: times[0]=%d (最新)  times[119]=%d (最旧)" % (times_raw[0], times_raw[119]))
print("原始数据: times[0] > times[119] = %s  -> 排列=[最新...最旧]" % (times_raw[0] > times_raw[119]))

# ===== 版本1: 只修正 pivot 时间引用，不反转数组 =====
print("\n" + "=" * 65)
print("版本1: 仅修 pivot 时间索引 (times[i]->times[i-strength])，不反转")
print("=" * 65)

ph1, pl1 = build_pivots(highs_raw, lows_raw, times_raw)
c1, t1, b1 = run_state_machine(highs_raw, lows_raw, times_raw, ph1, pl1, "V1")

if c1 == 1:
    top = max(t1, b1); bot = min(t1, b1)
    print("结果: BOX DETECTED  top=%.2f bottom=%.2f height=%.2f" % (top, bot, top-bot))
else:
    print("结果: NO BOX  (darvas_confirmed=%d)" % c1)

# ===== 版本2: 修 pivot 时间引用 + 反转数组 =====
print("\n" + "=" * 65)
print("版本2: 修 pivot 时间索引 + 数组反转")
print("=" * 65)

highs_rev = highs_raw[::-1]
lows_rev  = lows_raw[::-1]
times_rev = times_raw[::-1]
print("反转后: times[0]=%d (最旧)  times[119]=%d (最新)" % (times_rev[0], times_rev[119]))

ph2, pl2 = build_pivots(highs_rev, lows_rev, times_rev)
c2, t2, b2 = run_state_machine(highs_rev, lows_rev, times_rev, ph2, pl2, "V2")

if c2 == 1:
    top = max(t2, b2); bot = min(t2, b2)
    print("结果: BOX DETECTED  top=%.2f bottom=%.2f height=%.2f" % (top, bot, top-bot))
else:
    print("结果: NO BOX  (darvas_confirmed=%d)" % c2)

print("\n" + "=" * 65)
print("对照结论")
print("=" * 65)
print("版本1 (仅修时间索引): darvas_confirmed=%d" % c1)
print("版本2 (+数组反转):   darvas_confirmed=%d" % c2)
if c1 == 1 and c2 == 1:
    print("结论: 两个版本都能识别 box，最小修复只需修 pivot 时间索引")
    print("      数组反转是非必要的额外修改")
elif c1 == 0 and c2 == 1:
    print("结论: 仅修时间索引不够，必须同时反转数组")
    print("      数组反转是最小修复的必要组成部分")
elif c1 == 1 and c2 == 0:
    print("结论: 修时间索引有效，但数组反转破坏了结构")
elif c1 == 0 and c2 == 0:
    print("结论: 两个版本都失败，根因判断可能有误")
