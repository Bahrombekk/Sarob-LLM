#!/bin/bash
# Ishlab chiqarish darajalari bilan: oddiy savollar chegarasi 512 (hozirgi) va 256. Murakkab/rasm — 1024, salom — 32.
cd ~/sarob
for b in 512 256; do
  SAROB_FILTER=1 SAROB_DEFAULT=$b ~/sarob/venv/bin/python sarob_eval.py eval_def$b.md 1 > /tmp/def$b.log 2>&1
  python3 - "$b" <<'PY'
import re, sys
b = sys.argv[1]
t = open(f"eval_def{b}.md", encoding="utf-8").read()
th = [int(x) for x in re.findall(r"think=(\d+)", t)]
vq = [int(x) for x in re.findall(r"\*Vaqt: (\d+)s", t)]
print(f"chegara {b}: o'ylash jami {sum(th)} token, vaqt jami {sum(vq)} s, savollar {len(vq)}")
PY
done
echo TUGADI
