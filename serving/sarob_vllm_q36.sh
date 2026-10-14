#!/bin/bash
# Sinov: Qwen3.6-35B-A3B (NVFP4, MoE) + MTP. Port: 8002 (faqat lokal)
IMAGE=${IMAGE:-vllm/vllm-openai:v0.31.0}
SPEC=${SPEC:-'{"method":"mtp","num_speculative_tokens":3}'}
docker rm -f sarob-vllm-q36 >/dev/null 2>&1
docker run -d --name sarob-vllm-q36 --restart unless-stopped \
  --device nvidia.com/gpu=all --ipc host --shm-size 16g \
  --network host \
  -v "$HOME/models:/models:ro" \
  -v "$HOME/.cache/vllm:/root/.cache/vllm" \
  "$IMAGE" \
  --model /models/qwen36-35b-a3b-nvfp4 \
  --served-model-name qwen3.6-35b-a3b \
  --host 127.0.0.1 --port 8002 \
  --kv-cache-dtype fp8_e4m3 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.28 \
  --max-num-seqs 4 \
  --max-num-batched-tokens 4096 \
  --kernel-config '{"enable_flashinfer_autotune": false}' \
  --speculative-config "$SPEC" \
  --limit-mm-per-prompt '{"image":4,"video":0}' \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --enable-prefix-caching --enable-chunked-prefill
