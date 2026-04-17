# -*- coding: utf-8 -*-
"""结合 H1 边界 bar + 日志历史样本，综合评估边界效应"""
import re, statistics

LOG_FILE  = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_log.txt"
DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

with open(LOG_FILE, encoding="utf-8", errors="replace") as f:
    log_lines = f.readlines()
with open(DATA_FILE, encoding="utf-8", errors="replace") as f:
    data_raw = f.read()

m = re.search(r"H1:COUNT=(\d+)\|(.+)", data_raw)
pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)
def sf(s): return [float(x) for x in s.split(",")] if s else []
def si(s): return [int(x) for x in s.split(",")] if s else []

vols   = sf(pairs.get("VOL", ""))
times  = si(pairs.get("TIME", ""))

# 20-bar SMA
avg_vols = []
for i in range(len(vols)):
    if i < 19:
        avg_vols.append(sum(vols[:i+1])/(i+1))
    else:
        avg_vols.append(sum(vols[i-19:i+1])/20)

ratios = [(vols[i]/avg_vols[i]) if avg_vols[i]>0 else 0 for i in range(len(vols))]
valid_r = ratios[19:]

# 日志 tick 分组
tick_groups = {}
for line in log_lines:
    if "2026-04-09" not in line:
        continue
    ts = line[:19]
    if ts not in tick_groups:
        tick_groups[ts] = {"DEBUG": None, "SMART": None}
    if "[DEBUG]" in line and "box=" in line:
        tick_groups[ts]["DEBUG"] = line
    if "[SMART_DEBUG]" in line:
        tick_groups[ts]["SMART"] = line

# 历史日志样本
log_samples = []
for ts, g in tick_groups.items():
    d = g["DEBUG"]
    s = g["SMART"]
    if not d or not s:
        continue
    m_box = re.search(r"box=(exists|None|\S+)", d)
    m_q   = re.search(r"qualified=(T|F)", d)
    if not (m_box and m_q and m_box.group(1)!="None" and m_q.group(1)=="T"):
        continue
    m_cur  = re.search(r"current_vol=([0-9.]+)", s)
    m_avg  = re.search(r"avg_vol=([0-9.]+)", s)
    if not (m_cur and m_avg):
        continue
    cur, avg, ratio = float(m_cur.group(1)), float(m_avg.group(1)), float(m_cur.group(1))/float(m_avg.group(1))
    log_samples.append({"ts":ts,"cur_vol":int(cur),"avg_vol":round(avg,2),"ratio":round(ratio,4)})

print("=" * 65)
print("综合评估报告")
print("=" * 65)

# 1. H1 边界 bar 分析
print("\n【1】H1 历史边界 bar (ratio 1.00~1.20, 排除前19根不稳定区):")
boundary_bars = [(i, ratios[i], vols[i], avg_vols[i], times[i] if i < len(times) else 0)
                 for i in range(19, len(ratios)) if 1.00 <= ratios[i] < 1.20]
for idx, r, cv, av, t in boundary_bars:
    print(f"  bar idx={idx:>3}  ratio={r:.3f}  cur={int(cv):>7}  avg={av:>8.1f}  "
          f"time={t}  gap_to_1.20={r-1.20:+.3f}")

print(f"\n  边界 bar 总数: {len(boundary_bars)}")
if boundary_bars:
    tight_bars = [b for b in boundary_bars if 1.10 <= b[1] < 1.20]
    print(f"  其中 1.10~1.20 紧边界: {len(tight_bars)}")
    for b in tight_bars:
        print(f"    bar idx={b[0]:>3}  ratio={b[1]:.3f}  cur={int(b[2]):>7}  avg={b[3]:>8.1f}")

# 2. 阈值覆盖率
print("\n【2】阈值覆盖率分析:")
for thr in [1.20, 1.15, 1.10, 1.05]:
    n_above = sum(1 for r in valid_r if r >= thr)
    pct = n_above / len(valid_r) * 100
    gap_pct = (thr - statistics.mean(valid_r)) / statistics.mean(valid_r) * 100 if statistics.mean(valid_r) > 0 else 0
    print(f"  >= {thr:.2f}: {n_above}/{len(valid_r)} ({pct:.1f}%)  均值偏离={gap_pct:+.1f}%")

# 3. 日志样本 gap 分析
print("\n【3】日志历史样本 gap 分析:")
print(f"{'#':>3}  {'ratio':>6}  {'gap_to_1.20':>10}  {'gap_to_1.10':>10}  {'gap_to_1.05':>10}")
print("-" * 50)
for i, s in enumerate(log_samples):
    g120 = s["ratio"] - 1.20
    g110 = s["ratio"] - 1.10
    g105 = s["ratio"] - 1.05
    print(f"{i+1:>3}  {s['ratio']:>6.3f}  {g120:>+10.3f}  {g110:>+10.3f}  {g105:>+10.3f}")

print("\n  关键观察:")
for s in log_samples:
    if s["ratio"] >= 1.05:
        print(f"  {s['ts']}: ratio={s['ratio']:.3f} > 1.05，理论上可被 1.05 放行但被 1.20 拦住")
    else:
        print(f"  {s['ts']}: ratio={s['ratio']:.3f} < 1.05，即使 1.05 也不放行")

print("\n【4】综合结论:")
print(f"  历史 H1 bar 中有 {len(boundary_bars)} 个边界 bar (ratio 1.00~1.20)")
print(f"  其中 {len(tight_bars)} 个在 1.10~1.20 紧边界区")

all_ratios = [s["ratio"] for s in log_samples]
if all_ratios:
    mean_log = statistics.mean(all_ratios)
    max_log = max(all_ratios)
    if max_log < 1.20:
        below = 1.20 - max_log
        print(f"\n  日志样本 ratio 均值: {mean_log:.3f}，最大值: {max_log:.3f}")
        print(f"  最大样本距 1.20 差距: {below:.3f} ({below/max_log*100:.1f}%)")
        if max_log < 1.10:
            print("  [结论] 当前日志样本全部在 1.10 以下，ratio 偏低，无边界样本")
            print("  [结论] volume filter 拦截合理，无证据表明 1.20 过严")
            print("  [结论] 继续等待：若未来出现 ratio 在 1.10~1.20 的新 qualified 样本，再重新评估")
        elif max_log < 1.20:
            print("  [结论] 当前日志样本最大 ratio 在 1.10~1.20 区间")
            print("  [结论] 这是潜在的边界样本，应持续监控等待新样本确认")
