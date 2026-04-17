# -*- coding: utf-8 -*-
"""信号链路完整追踪 - 模拟最新 tick"""
import re
import sys
sys.path.insert(0, r"C:\Users\Administrator\ai-trader-for-mt4\ai-trader-for-mt4-main")

from ai_brain import EnergyBlockEngine

DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"
CMD_FILE  = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_cmd.txt"

with open(DATA_FILE, encoding="utf-8") as f:
    raw = f.read()

m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)

def sf(s): return [float(x) for x in s.split(",")] if s else []
def si(s): return [int(x) for x in s.split(",")] if s else []

closes = sf(pairs.get("CLOSE", ""))
highs  = sf(pairs.get("HIGH", ""))
lows   = sf(pairs.get("LOW", ""))
times  = si(pairs.get("TIME", ""))
count  = int(m.group(1))

bid    = closes[-1] if closes else 0
atr    = sf(pairs.get("ATR", ""))[-1] if pairs.get("ATR", "") else 0
tick_t = times[-1] if times else 0

print("=" * 60)
print("STEP 1: 构造 tick 数据")
print("=" * 60)
print(f"count={count} bid={bid} atr={atr} tick_t={tick_t}")

data = {
    "bid": bid, "atr": atr,
    "pos": "FLAT", "profit": 0.0,
    "bar_count": count, "new_bar": False
}
h1 = {
    "close": closes, "high": highs,
    "low": lows, "time": times
}

# ========= 模拟 EnergyBlockEngine.tick() 链路 =========
ai = EnergyBlockEngine()

print("\n" + "=" * 60)
print("STEP 2: 加载策略参数")
print("=" * 60)
ai.p = {
    "PivotStrength": 3,
    "MinBars": 50,
    "MinBoxHeightPips": 0,
    "MinDisplayScore": 1.0,
    "WaitBars": 1,
    "TrigModeBars": 1,
    "MinBreakPips": 0,
    "MaxBreakPips": 99999,
    "SmartMode": True,
    "VolumeThreshold": 0.5,
    "VolumePeriod": 20,
    "MinAge": 10,
    "VolatilityMin": 0.0,
    "VolatilityMax": 9999.0,
    "ScoreWeights": "close_score=1.0,volume_score=0.5,trend_score=0.3",
    "CooldownBars": 3,
    "MaxRetries": 3,
}
ai.darvas_state = 0
ai.darvas_confirmed = 0
ai.wait_bar_count = 0
ai.state = "IDLE"
ai.cooldown_bars = 0
ai.position = "FLAT"

print(f"参数: { {k:v for k,v in ai.p.items()} }")

print("\n" + "=" * 60)
print("STEP 3: 执行 tick() → 检测 box → check_conditions → decide")
print("=" * 60)

cmd = ai.tick(data, h1)

print("\n" + "=" * 60)
print("STEP 4: 结果汇总")
print("=" * 60)
print(f"box       = {ai.box}")
print(f"box_top   = {ai.box['top'] if ai.box else 'None'}")
print(f"box_bot   = {ai.box['bottom'] if ai.box else 'None'}")
print(f"darvas_state     = {ai.darvas_state}")
print(f"darvas_confirmed = {ai.darvas_confirmed}")
print(f"score      = {ai.box_score if ai.box else 0.0}")
print(f"wait_bar_count   = {ai.wait_bar_count}")
print(f"wait_ok    = {ai.wait_ok}")
print(f"bh_ok      = {ai.bh_ok}")
print(f"qualified  = {ai.qualified}")
print(f"volume_ok  = {ai.volume_ok}")
print(f"age_ok     = {ai.age_ok}")
print(f"vol_ok     = {ai.volatility_ok}")
print(f"smart_ok   = {ai.smart_ok}")
print(f"cmd        = {cmd}")
