#!/bin/bash
# Sarob miyasi: Gemma 4 26B-A4B (unsloth NVFP4, Marlin'siz) + MTP spekulyativ dekodlash, vLLM'da
# Taxminchi: o'zbekchaga o'qitilgan (training/), k=2 — o'zbekcha javob 43.8 -> 70.5 tok/s
# Sinov: NVIDIA nusxasidan ~30% tez (59-70 tok/s) va o'ylash javobga kamroq aralashadi (1/12 vs 3-4/12)
# Port: 8000 (OpenAI API), faqat lokal (127.0.0.1)
IMAGE=${IMAGE:-vllm/vllm-openai:v0.31.0}
docker rm -f sarob-vllm >/dev/null 2>&1
docker run -d --name sarob-vllm --restart unless-stopped \
  --device nvidia.com/gpu=all --ipc host --shm-size 16g \
  --network host \
  -v "$HOME/models:/models:ro" \
  -v "$HOME/.cache/vllm:/root/.cache/vllm" \
  "$IMAGE" \
  --model /models/gemma4-26b-unsloth-nvfp4 \
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
  --reasoning-config '{"reasoning_parser":"gemma4","reasoning_start_str":"<|channel>","reasoning_end_str":"<channel|>"}' \
  --enable-auto-tool-choice --tool-call-parser gemma4 \
  --enable-prefix-caching
