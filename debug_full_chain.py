# -*- coding: utf-8 -*-
"""模拟完整信号链路 - 使用真实系统参数"""
import re, sys
sys.path.insert(0, r"C:\Users\Administrator\ai-trader-for-mt4\ai-trader-for-mt4-main")
from ai_brain import EnergyBlockEngine, safe_read, PARAMS

DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

raw = safe_read(DATA_FILE)
m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)

def sf(s): return [float(x) for x in s.split(",")] if s else []
def si(s): return [int(x) for x in s.split(",")] if s else []

closes = sf(pairs.get("CLOSE", ""))
highs  = sf(pairs.get("HIGH", ""))
lows   = sf(pairs.get("LOW", ""))
times  = si(pairs.get("TIME", ""))
vols   = si(pairs.get("VOL", ""))

n = len(closes)
bid = closes[-1]
atr_raw = sf(pairs.get("ATR", ""))
atr_val = atr_raw[-1] if atr_raw else 0

print("=" * 65)
print("STEP 1: 原始数据检查")
print("=" * 65)
print(f"n={n} bid={bid} atr={atr_val:.4f}")
print(f"closes[0]={closes[0]}(最新) closes[119]={closes[119]}(最旧) -> {'[最新...最旧]' if closes[0]!=closes[119] else '?'}")
print(f"times[0]={times[0]} times[119]={times[119]} -> {'[最新...最旧]' if times[0]>times[119] else '[最旧...最新]'}")

data = {
    "bid": bid, "ask": bid + 0.5,
    "atr": atr_val,
    "position": {"dir": "FLAT", "size": 0.0, "avg": 0, "profit": 0},
    "time": times[-1],
    "H1": {"close": closes, "high": highs, "low": lows, "time": times, "vol": vols, "count": n},
    "M15": {"close": closes, "high": highs, "low": lows},
}

ai = EnergyBlockEngine()
ai.p = PARAMS.copy()
# 强制设为活跃时段
ai.p["StratStartHour"] = 0
ai.p["StratEndHour"] = 0
ai.last_bar_index = -1
ai.wait_bar_count = 0
ai.box_bar_count = 0
ai.state = "IDLE"
ai.darvas_state = 0
ai.darvas_confirmed = 0
ai.box = None
ai.box_score = 0.0
ai.qualified = False
ai.wait_ok = False
ai.bh_ok = False
ai.volume_ok = False
ai.age_ok = False
ai.volatility_ok = False
ai.smart_ok = False
ai.pending_orders = []
ai.trail_high_price = 0
ai.martin_count = 0
ai.is_recovery = False
ai.lock_box_top = 0
ai.lock_box_bottom = 0
ai.lock_box_h = 0
ai.cooldown_bars = 0
ai.next_trade_bar = -999
ai.position = "FLAT"

print("\n" + "=" * 65)
print("STEP 2: 关键参数")
print("=" * 65)
for k in ["PivotStrength","MinDisplayScore","TriggerMinBars","MinVolumeRatio","MaxBoxAgeBars","StratStartHour","StratEndHour"]:
    print(f"  {k} = {ai.p.get(k)}")

print("\n" + "=" * 65)
print("STEP 3: 执行 on_bar()")
print("=" * 65)
cmd = ai.on_bar(data)

print("\n" + "=" * 65)
print("STEP 4: 信号链路责任点确认")
print("=" * 65)
print(f"1. box 是否存在: {'是 -> top=%.2f bottom=%.2f' % (ai.box['top'], ai.box['bottom']) if ai.box else '否 -> box=None'}")
print(f"2. box_score: {ai.box_score:.1f} vs MinDisplayScore={ai.p['MinDisplayScore']} -> {'score_ok=T' if ai.box_score>=ai.p['MinDisplayScore'] else 'score_ok=F'}")
print(f"3. wait_bar_count: {ai.wait_bar_count} vs TriggerMinBars={ai.p['TriggerMinBars']} -> {'wait_ok=T' if ai.wait_bar_count>=ai.p['TriggerMinBars'] else 'wait_ok=F'}")
print(f"4. qualified: {ai.qualified}")
print(f"5. volume_ok={ai.volume_ok} age_ok={ai.age_ok} volatility_ok={ai.volatility_ok} smart_ok={ai.smart_ok}")
print(f"6. state={ai.state} cmd={cmd}")
