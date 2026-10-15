#!/bin/bash
# To'liq FP8 Gemma (RedHatAI/gemma-4-26B-A4B-it-FP8-dynamic) + o'zbekcha taxminchi: k=2 va k=3 tezligi.
cd ~/sarob
w() { for i in $(seq 1 90); do curl -sf localhost:8000/v1/models >/dev/null && return 0; docker logs sarob-vllm 2>&1 | grep -q "initialization failed" && return 1; sleep 10; done; return 1; }
for k in 2 3; do
  MODEL=/models/gemma4-26b-fp8 MTP_K=$k ./sarob_vllm.sh >/dev/null
  if w; then
    echo "== FP8 toliq (k=$k)"
    python3 mtp_lang.py
  else
    echo "== FP8 k=$k YUKLANMADI"
    docker logs sarob-vllm 2>&1 | grep -E "Error" | tail -3
  fi
done
./sarob_vllm.sh >/dev/null
w
echo "== standart qaytdi"
echo TUGADI
