# -*- coding: utf-8 -*-
"""箱体检测 - 精确时间比较调试（修正版）"""
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

print("=" * 70)
print("[1] times 数组顺序验证")
print("=" * 70)
print(f"\ntimes[114] = {times[114]}")
print(f"times[117] = {times[117]}")
print(f"\n索引 110~119 对应的 times 值:")
for i in range(110, 120):
    print(f"  times[{i}] = {times[i]}")
print()
ascending = all(times[i] < times[i+1] for i in range(n-1))
descending = all(times[i] > times[i+1] for i in range(n-1))
print(f"索引递增时，times 是否严格递增: {ascending}")
print(f"索引递增时，times 是否严格递减: {descending}")
if descending:
    print("=> times 是倒序: 索引越大，时间戳越小（越早）")

print(f"\ntimes[114] < times[117] = {times[114]} < {times[117]} = {times[114] < times[117]}")
print(f"times[117] < times[114] = {times[117]} < {times[114]} = {times[117] < times[114]}")

print("\n" + "=" * 70)
print("[2] pivot 识别（索引 110~119）")
print("=" * 70)

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

print()
for i in range(110, 120):
    ph = pivot_high[i]
    pl = pivot_low[i]
    ph_str = f"{ph:.2f}" if ph > 0 else "---"
    pl_str = f"{pl:.2f}" if pl > 0 else "---"
    print(f"  [{i}] pivot_high={ph_str}  pivot_low={pl_str}  times={times[i]}")

print("\n" + "=" * 70)
print("[3] 状态机逐行执行追踪")
print("=" * 70)

darvas_state = 0
darvas_confirmed = 0
box_start_time = 0

for i in range(n - 1, length - 2, -1):
    if darvas_state == 0:
        if pivot_high[i] > 0:
            print(f"\n[i={i}] pivot_high={pivot_high[i]:.2f}  times={times[i]}")
            print(f"       设置 box_start_time = {times[i]}")
            print(f"       darvas_state: 0 -> 1")
            darvas_state = 1
            box_start_time = times[i]
        elif pivot_low[i] > 0:
            print(f"\n[i={i}] pivot_low={pivot_low[i]:.2f}  times={times[i]}")
            print(f"       设置 box_start_time = {times[i]}")
            print(f"       darvas_state: 0 -> -1")
            darvas_state = -1
            box_start_time = times[i]
    elif darvas_state == 1:
        if pivot_low[i] > 0:
            expr = f"times[{i}]={times[i]} < box_start_time={box_start_time}"
            result = times[i] < box_start_time
            print(f"\n[i={i}] pivot_low={pivot_low[i]:.2f}")
            print(f"       比较: {expr}")
            print(f"       结果: {result}")
            if result:
                darvas_confirmed = 1
                break
    elif darvas_state == -1:
        if pivot_high[i] > 0:
            expr = f"times[{i}]={times[i]} < box_start_time={box_start_time}"
            result = times[i] < box_start_time
            print(f"\n[i={i}] pivot_high={pivot_high[i]:.2f}")
            print(f"       比较: {expr}")
            print(f"       结果: {result}")
            if result:
                darvas_confirmed = 1
                break

print("\n" + "=" * 70)
print("[4] 最终结论")
print("=" * 70)
if darvas_confirmed == 1:
    print("箱体检测成功")
else:
    print(f"箱体检测失败: darvas_state={darvas_state}, darvas_confirmed={darvas_confirmed}")
