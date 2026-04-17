# -*- coding: utf-8 -*-
"""箱体检测 - 数据顺序和数组索引对应关系验证"""
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

print("=" * 80)
print("关键索引的时间戳")
print("=" * 80)
print(f"  times[  0] = {times[0]}")
print(f"  times[  1] = {times[1]}")
print(f"  times[  2] = {times[2]}")
print(f"  times[110] = {times[110]}")
print(f"  times[111] = {times[111]}")
print(f"  times[112] = {times[112]}")
print(f"  times[113] = {times[113]}")
print(f"  times[114] = {times[114]}")
print(f"  times[115] = {times[115]}")
print(f"  times[116] = {times[116]}")
print(f"  times[117] = {times[117]}")
print(f"  times[118] = {times[118]}")
print(f"  times[119] = {times[119]}")

print()
print("  最大时间戳 =", max(times), " 所在索引 =", times.index(max(times)))
print("  最小时间戳 =", min(times), " 所在索引 =", times.index(min(times)))

print("\n" + "=" * 80)
print("结论：索引 0 是最新 bar 还是最旧 bar？")
print("=" * 80)
if times[0] > times[119]:
    print("  times[0] > times[119] = " + str(times[0]) + " > " + str(times[119]))
    print("  => 索引越小 = 时间越大 = 越新")
    print("  => 索引 0 是最新 bar")
    print("  => 索引 119 是最旧 bar")
    print("  => 数据排列：[最新, ..., 最旧]")
    print("  => 算法从最大索引往后遍历 = 从[最旧]往[更新]走")
    print("  => 但状态机要找更早的 pivot = 需要往[更新]方向走 = 索引越小方向")
    print("  => 索引方向与时间方向相反！")
else:
    print("  times[0] < times[119]")
    print("  => 索引越小 = 时间越小 = 越旧")
    print("  => 索引 0 是最旧 bar")
    print("  => 索引 119 是最新 bar")
    print("  => 数据排列：[最旧, ..., 最新]")
    print("  => 算法从最大索引往后遍历 = 从[最新]往[更旧]走")
    print("  => 状态机要找更早的 pivot = 需要往[更旧]方向走 = 索引越大方向")
    print("  => 索引方向与时间方向一致 ✓")

print("\n" + "=" * 80)
print("如果数据是 [最旧...最新]，反转后索引对应")
print("=" * 80)
print("  当前: index 0  = times[" + str(times[0]) + "]")
print("  反转后: index 0  = times[" + str(times[119]) + "] = " + str(times[119]))
print("  当前: index 119 = times[" + str(times[119]) + "]")
print("  反转后: index 119 = times[" + str(times[0]) + "] = " + str(times[0]))
