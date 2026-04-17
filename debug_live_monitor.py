# -*- coding: utf-8 -*-
"""live 监控：收集边界样本和 volume_ok=True 被拦截的案例"""
import re, sys, time, os
sys.path.insert(0, r"C:\Users\Administrator\ai-trader-for-mt4\ai-trader-for-mt4-main")

LOG_FILE  = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_log.txt"
DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

print("=" * 65)
print("Live 监控：volume_ok 边界样本收集")
print("=" * 65)
print("目标：")
print("  A. current_vol/avg_vol 接近 1.10~1.20 的边界样本")
print("  B. volume_ok=True 但 cmd=None 的案例")
print()
print("持续监控中，Ctrl+C 停止...\n")

seen_lines = 0
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, encoding="utf-8", errors="replace") as f:
        seen_lines = len(f.readlines())

last_log_size = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0

typeA_samples = []   # 边界样本：1.05 <= ratio < 1.20
typeB_samples = []  # volume_ok=True 但无 cmd

def get_current_data():
    """读取当前数据文件的最新成交数据（vol info）"""
    from ai_brain import safe_read
    raw = safe_read(DATA_FILE)
    m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
    if not m:
        return {}
    pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)
    def sf(s): return [float(x) for x in s.split(",")] if s else []
    vols = sf(pairs.get("VOL", ""))
    return {"vols": vols, "count": int(m.group(1))}

def parse_ratio_from_smart(s):
    """从 SMART_DEBUG 提取 ratio"""
    m_cur = re.search(r"current_vol=([0-9.]+)", s)
    m_avg = re.search(r"avg_vol=([0-9.]+)", s)
    if m_cur and m_avg:
        cur = float(m_cur.group(1))
        avg = float(m_avg.group(1))
        if avg > 0:
            return cur / avg
    return None

def is_box_qualified_from_debug(d):
    m = re.search(r"box=(exists|None|\S+)", d)
    q = re.search(r"qualified=(T|F)", d)
    if m and q:
        return m.group(1) != "None" and q.group(1) == "T"
    return False

def has_cmd(line):
    return "有指令" in line and "最终 cmd=" in line

# tick 分组
tick_groups = {}

POLL = 5  # 秒
last_print = time.time()

while True:
    time.sleep(POLL)

    if not os.path.exists(LOG_FILE):
        continue

    cur_size = os.path.getsize(LOG_FILE)
    if cur_size == last_log_size:
        continue

    last_log_size = cur_size

    with open(LOG_FILE, encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()

    new_lines = all_lines[seen_lines:]
    seen_lines = len(all_lines)

    if not new_lines:
        continue

    # 仅处理今日行
    today_new = [l.strip() for l in new_lines if "2026-04-09" in l]
    if not today_new:
        continue

    # 更新 tick_groups
    for line in today_new:
        ts = line[:19]
        if ts not in tick_groups:
            tick_groups[ts] = {"DEBUG": None, "SMART": None, "CMD": None}
        if "[DEBUG]" in line and "box=" in line:
            tick_groups[ts]["DEBUG"] = line
        if "[SMART_DEBUG]" in line:
            tick_groups[ts]["SMART"] = line
        if "[最终 cmd=" in line:
            tick_groups[ts]["CMD"] = line

    now = time.time()
    if now - last_print < 30:
        continue
    last_print = now

    print("-" * 65)
    print(f"[{time.strftime('%H:%M:%S')}] Tick groups: {len(tick_groups)}  New lines: {len(today_new)}")

    new_A = 0
    new_B = 0

    for ts, g in list(tick_groups.items()):
        d = g["DEBUG"]
        s = g["SMART"]
        c = g["CMD"]

        if not d or not s:
            continue
        if not is_box_qualified_from_debug(d):
            continue

        ratio = parse_ratio_from_smart(s)
        if ratio is None:
            continue

        vol_ok = re.search(r"volume_ok=(T|F)", s)
        vol_ok_bool = vol_ok.group(1) == "T" if vol_ok else False
        age_ok = re.search(r"age_ok=(T|F)", s)
        vol_ok_age = age_ok.group(1) == "T" if age_ok else True

        # Type A: 边界
        if 1.05 <= ratio < 1.20:
            typeA_samples.append({
                "ts": ts, "ratio": ratio,
                "vol_ok": vol_ok_bool,
                "age_ok": vol_ok_age,
                "cmd": c,
            })
            new_A += 1

        # Type B: volume_ok=True 但无 cmd
        has_final_cmd = c and "有指令" in c
        if vol_ok_bool and vol_ok_age and not has_final_cmd:
            typeB_samples.append({
                "ts": ts, "ratio": ratio,
                "cmd": c,
            })
            new_B += 1

    if new_A > 0 or new_B > 0:
        print(f"  新增 Type A (边界 1.05~1.20): +{new_A}  累计: {len(typeA_samples)}")
        print(f"  新增 Type B (vol_ok=T 但无cmd): +{new_B}  累计: {len(typeB_samples)}")

        if typeA_samples:
            print("\n  Type A 边界样本:")
            for s in typeA_samples[-5:]:
                print(f"    {s['ts']}  ratio={s['ratio']:.3f}  vol_ok={s['vol_ok']}  age_ok={s['age_ok']}")

        if typeB_samples:
            print("\n  Type B 反常样本 (vol_ok=T 但 cmd=None):")
            for s in typeB_samples[-5:]:
                print(f"    {s['ts']}  ratio={s['ratio']:.3f}  cmd={s['cmd']}")

    else:
        print(f"  无新增样本，继续监控...")
