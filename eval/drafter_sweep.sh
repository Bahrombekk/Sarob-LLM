#!/bin/bash
# Taxminchi variantlari: FP8 lm_head (k=2,3) va moslashuvchan tekshiruv (enable_adaptive_verification, k=3,4).
cd ~/sarob
w() { for i in $(seq 1 90); do curl -sf localhost:8000/v1/models >/dev/null && return 0; docker logs sarob-vllm 2>&1 | grep -q "initialization failed" && return 1; sleep 10; done; return 1; }
run() {  # run <nom> <spec-config JSON>
  sed "s|--speculative-config \"[^\"]*\(\\\\\"[^\"]*\)*\"|--speculative-config '$2'|" sarob_vllm.sh > /tmp/vllm_try.sh
  grep -q "$2" /tmp/vllm_try.sh || { echo "== $1: sed xato"; return; }
  bash /tmp/vllm_try.sh >/dev/null
  if w; then echo "== $1"; python3 mtp_lang.py; else echo "== $1: YUKLANMADI"; docker logs sarob-vllm 2>&1 | grep -E "Error" | tail -3 | cut -c1-250; fi
}
D=/models/gemma4-26b-assistant-uz
F=/models/gemma4-26b-assistant-uz-fp8
run "FP8 taxminchi k=2" "{\"method\":\"mtp\",\"model\":\"$F\",\"num_speculative_tokens\":2}"
run "FP8 taxminchi k=3" "{\"method\":\"mtp\",\"model\":\"$F\",\"num_speculative_tokens\":3}"
run "moslashuvchan k=3" "{\"method\":\"mtp\",\"model\":\"$D\",\"num_speculative_tokens\":3,\"enable_adaptive_verification\":true}"
run "moslashuvchan k=4" "{\"method\":\"mtp\",\"model\":\"$D\",\"num_speculative_tokens\":4,\"enable_adaptive_verification\":true}"
./sarob_vllm.sh >/dev/null; w; echo "== standart qaytdi"
echo TUGADI
