# -*- coding: utf-8 -*-
"""箱体检测 - 直接调用 ai_brain.py 的 detect_darvas_box 方法"""
import re
import sys
sys.path.insert(0, r"C:\Users\Administrator\ai-trader-for-mt4\ai-trader-for-mt4-main")

from ai_brain import EnergyBlockEngine

DATA_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_data.txt"

with open(DATA_FILE, encoding="utf-8") as f:
    raw = f.read()

m = re.search(r"H1:COUNT=(\d+)\|(.+)", raw)
pairs = dict(p.split("=") for p in m.group(2).split("|") if "=" in p)

def sf(s): return [float(x) for x in s.split(",")] if s else []
def si(s): return [int(x) for x in s.split(",")] if s else []

h1 = {
    "close": sf(pairs.get("CLOSE", "")),
    "high":  sf(pairs.get("HIGH", "")),
    "low":   sf(pairs.get("LOW", "")),
    "time":  si(pairs.get("TIME", "")),
}

ai = EnergyBlockEngine()
ai.p = {
    "PivotStrength": 3,
    "MinBars": 50,
}
ai.darvas_state = 0
ai.darvas_confirmed = 0

result = ai.detect_darvas_box(h1)

print("=" * 60)
print("Real call to ai_brain.detect_darvas_box()")
print("=" * 60)
if result is None:
    print("RESULT: None (box not detected)")
else:
    print("RESULT: Box detected!")
    print("  top:    %.2f" % result["top"])
    print("  bottom: %.2f" % result["bottom"])
    print("  height: %.2f" % result["height"])
    print("  state:  %d" % ai.darvas_state)
    print("  confirmed: %d" % ai.darvas_confirmed)
