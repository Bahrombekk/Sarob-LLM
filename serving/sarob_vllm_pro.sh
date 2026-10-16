#!/bin/bash
# Sarob Pro miyasi: Qwen3.8 27B (NVFP4) + MTP, vLLM'da. Port: 8001 (faqat lokal)
IMAGE=${IMAGE:-vllm/vllm-openai:v0.31.0}
SPEC=${SPEC:-'{"method":"mtp","num_speculative_tokens":3}'}
docker rm -f sarob-vllm-pro >/dev/null 2>&1
docker run -d --name sarob-vllm-pro --restart unless-stopped \
  --device nvidia.com/gpu=all --ipc host --shm-size 16g \
  --network host \
  -v "$HOME/models:/models:ro" \
  -v "$HOME/.cache/vllm:/root/.cache/vllm" \
  "$IMAGE" \
  --model /models/qwen38-27b-nvfp4 \
  --served-model-name qwen3.8-27b \
  --host 127.0.0.1 --port 8001 \
  --kv-cache-dtype fp8_e4m3 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.28 \
  --max-num-seqs 4 \
  --max-num-batched-tokens 4096 \
  --kernel-config '{"enable_flashinfer_autotune": false}' \
  --speculative-config "$SPEC" \
  --limit-mm-per-prompt '{"image":32,"video":0}' \
  --reasoning-parser qwen3 \
  --reasoning-config '{"reasoning_parser":"qwen3","reasoning_start_str":"<think>","reasoning_end_str":"</think>"}' \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --enable-prefix-caching --enable-chunked-prefill
