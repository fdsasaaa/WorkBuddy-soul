# -*- coding: utf-8 -*-
"""高亮日志监听器 - 等待 [HIGH_BOUNDARY] / [HIGH_VOL_OK] / [HIGH_VOL_OK_NO_CMD]"""
import re, time

LOG_FILE = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\5D49F47D1EA1ECFC0DDC965B6D100AC5\MQL4\Files\ai_brain_log.txt"

TAGS = ["HIGH_BOUNDARY", "HIGH_VOL_OK", "HIGH_VOL_OK_NO_CMD"]
seen_positions = {}  # tag -> last byte position

print("=" * 60)
print("高亮日志监听器已启动")
print("监控目标:", " / ".join(TAGS))
print("一旦命中，立即汇报。")
print("=" * 60)

# 初始化位置
for tag in TAGS:
    seen_positions[tag] = 0

while True:
    time.sleep(5)
    try:
        with open(LOG_FILE, encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)
            content = f.read()
    except:
        continue

    for tag in TAGS:
        # 找到 tag 在文件中的最后位置
        last_pos = content.rfind(f"[{tag}]")
        if last_pos > seen_positions[tag]:
            seen_positions[tag] = last_pos
            # 提取该行
            line_start = content.rfind("\n", 0, last_pos) + 1
            line = content[line_start:last_pos+200].split("\n")[0].strip()

            # 提取关联上下文（前后各2行 DEBUG 行）
            lines_all = content[:last_pos+200].split("\n")
            ctx = []
            for l in lines_all[-6:]:
                if any(t in l for t in ["[DEBUG]", "[HIGH_BOUNDARY]", "[HIGH_VOL_OK]", "[HIGH_VOL_OK_NO_CMD]", "[Tick]"]):
                    ctx.append(l.strip())
            ctx = ctx[-6:]  # 最多6行

            print("\n" + "!" * 60)
            print(f"!! 高亮命中: [{tag}]")
            print("!" * 60)
            print(f"命中行: {line}")
            if ctx:
                print("关联上下文:")
                for c in ctx:
                    print(f"  {c}")
            print("=" * 60)
