#!/bin/bash
# Sarob miyasi: Gemma 4 26B-A4B (unsloth NVFP4, Marlin'siz) + MTP spekulyativ dekodlash, vLLM'da
# Taxminchi: o'zbekchaga o'qitilgan (training/), k=2 — o'zbekcha javob 43.8 -> 70.5 tok/s
# lm_head FP8 (serving/tools/untie_lmhead_fp8.py): +12% — o'zbekcha 69 -> 77 tok/s, sifat takroriy sinovda o'zgarmadi
# Sinov: NVIDIA nusxasidan ~30% tez (59-70 tok/s) va o'ylash javobga kamroq aralashadi (1/12 vs 3-4/12)
# Port: 8000 (OpenAI API), faqat lokal (127.0.0.1)
IMAGE=${IMAGE:-vllm/vllm-openai:v0.31.0}
# O'ylash chegarasi urilganda qo'shiladigan matn. Faqat <channel|> bo'lsa model o'ylashni javob ichida davom ettirardi
# (sinov: 6/12 javobga oqdi); o'tish iborasi bilan 0/12 (eval/leak_ab.sh).
REASON_END=${REASON_END:-'\n\nTime is up. I must stop thinking now and write the final answer directly, in Uzbek.<channel|>'}
docker rm -f sarob-vllm >/dev/null 2>&1
docker run -d --name sarob-vllm --restart unless-stopped \
  --device nvidia.com/gpu=all --ipc host --shm-size 16g \
  --network host \
  -v "$HOME/models:/models:ro" \
  -v "$HOME/.cache/vllm:/root/.cache/vllm" \
  "$IMAGE" \
  --model ${MODEL:-/models/gemma4-26b-nvfp4-lmfp8} \
  --served-model-name gemma-4-26b \
  --host 127.0.0.1 --port 8000 \
  --kv-cache-dtype fp8 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.35 \
  --max-num-seqs ${MAX_SEQS:-8} \
  --speculative-config "{\"method\":\"mtp\",\"model\":\"${DRAFTER:-/models/gemma4-26b-assistant-uz}\",\"num_speculative_tokens\":${MTP_K:-2}}" \
  --limit-mm-per-prompt '{"image":32,"audio":0,"video":0}' \
  --mm-processor-kwargs '{"max_soft_tokens":1120}' \
  --reasoning-parser gemma4 \
  --reasoning-config "{\"reasoning_parser\":\"gemma4\",\"reasoning_start_str\":\"<|channel>\",\"reasoning_end_str\":\"${REASON_END}\"}" \
  --enable-auto-tool-choice --tool-call-parser gemma4 \
  --enable-prefix-caching
