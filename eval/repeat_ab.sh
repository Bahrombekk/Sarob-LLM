#!/bin/bash
# A/B takroriy sinov: shubhali savollarni ikkala checkpoint'da N martadan ishlatadi.
# Ishlatish: ./repeat_ab.sh "15 23 24 27 29" 4
cd ~/sarob
Q=${1:-"15 23 24 27 29"}; N=${2:-4}
w() { for i in $(seq 1 90); do curl -sf localhost:8000/v1/models >/dev/null && return; sleep 10; done; }
for variant in D A; do
  if [ $variant = D ]; then MODEL=/models/gemma4-26b-nvfp4-lmfp8 ./sarob_vllm.sh >/dev/null; else ./sarob_vllm.sh >/dev/null; fi
  w
  for i in $(seq 1 $N); do
    SAROB_BUDGET=1024 ~/sarob/venv/bin/python sarob_eval.py rep_${variant}_$i.md 1 $Q > /dev/null 2>&1
    echo "$(date +%H:%M) $variant $i tayyor"
  done
done
echo TUGADI
