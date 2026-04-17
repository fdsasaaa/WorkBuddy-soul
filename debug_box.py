# -*- coding: utf-8 -*-
"""箱体检测调试脚本"""
import re, sys

DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

def parse_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = f.read()
    m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
    if not m:
        print("[ERR] H1数据未找到"); return None

    n = int(m.group(1))
    pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)

    def safe_float(s): return [float(x) for x in s.split(",")] if s else []
    def safe_int(s): return [int(x) for x in s.split(",")] if s else []

    return {
        "close": safe_float(pairs.get("CLOSE", "")),
        "high":  safe_float(pairs.get("HIGH", "")),
        "low":   safe_float(pairs.get("LOW", "")),
        "time":  safe_int(pairs.get("TIME", "")),
    }

def detect_darvas_box(h1, strength=3):
    closes = h1["close"]
    highs  = h1["high"]
    lows   = h1["low"]
    times  = h1["time"]
    n = len(closes)
    length = strength + 2

    if n < 20:
        print(f"[ERR] K线数量不足: {n}"); return None

    # pivot high
    pivot_high = [0.0] * n
    for i in range(length - 1, n):
        center_val = highs[i - strength]
        is_max = True
        for j in range(length):
            if j == strength: continue
            if highs[i - j] >= center_val:
                is_max = False; break
        if is_max: pivot_high[i] = center_val

    # pivot low
    pivot_low = [0.0] * n
    for i in range(length - 1, n):
        center_val = lows[i - strength]
        is_min = True
        for j in range(length):
            if j == strength: continue
            if lows[i - j] <= center_val:
                is_min = False; break
        if is_min: pivot_low[i] = center_val

    # 状态机（从后往前）
    darvas_state = 0
    darvas_confirmed = 0
    box_top = None; box_bottom = None; box_start_time = 0

    print(f"[DEBUG] 总K线数: {n}, 从 {n-1} 遍历到 {length-1}")
    print(f"[DEBUG] pivot_high 有效索引: {[i for i,v in enumerate(pivot_high) if v > 0][-5:]}")
    print(f"[DEBUG] pivot_low  有效索引: {[i for i,v in enumerate(pivot_low) if v > 0][-5:]}")
    print(f"[DEBUG] 最新5个pivot_high: {[(i, pivot_high[i], times[i]) for i in range(n-5, n) if pivot_high[i] > 0]}")
    print(f"[DEBUG] 最新5个pivot_low:  {[(i, pivot_low[i], times[i]) for i in range(n-5, n) if pivot_low[i] > 0]}")

    found_top = None; found_bottom = None
    for i in range(n - 1, length - 2, -1):
        if darvas_state == 0:
            if pivot_high[i] > 0:
                found_top = (i, pivot_high[i], times[i])
                darvas_state = 1
                box_start_time = times[i]
            elif pivot_low[i] > 0:
                found_bottom = (i, pivot_low[i], times[i])
                darvas_state = -1
                box_start_time = times[i]
        elif darvas_state == 1:
            if pivot_low[i] > 0 and times[i] < box_start_time:
                found_bottom = (i, pivot_low[i], times[i])
                darvas_confirmed = 1
                break
        elif darvas_state == -1:
            if pivot_high[i] > 0 and times[i] < box_start_time:
                found_top = (i, pivot_high[i], times[i])
                darvas_confirmed = 1
                break

    print(f"[RESULT] state={darvas_state}, confirmed={darvas_confirmed}")
    print(f"[RESULT] found_top={found_top}")
    print(f"[RESULT] found_bottom={found_bottom}")

    if darvas_confirmed != 1:
        print("[RESULT] 箱体检测失败 - 未能找到成对pivot")
        return None

    box_top_v = max(found_top[1], found_bottom[1])
    box_bot_v = min(found_top[1], found_bottom[1])
    box_h = box_top_v - box_bot_v
    return {"top": box_top_v, "bottom": box_bot_v, "height": box_h}

if __name__ == "__main__":
    print("="*60)
    print("箱体检测调试脚本")
    print("="*60)
    h1 = parse_data()
    if h1:
        box = detect_darvas_box(h1)
        if box:
            print(f"\n[SUCCESS] 箱体检测成功!")
            print(f"  top:    {box['top']}")
            print(f"  bottom: {box['bottom']}")
            print(f"  height: {box['height']}")
        else:
            print("\n[FAIL] 箱体检测失败")
