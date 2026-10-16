#!/bin/bash
# Hujjat/jadval o'qish modeli: PaddleOCR-VL-1.6 (0.9B, Apache-2.0; OmniDocBench v1.6 — 96.3), vLLM'da. Port: 8002 (faqat lokal)
# rasmlardan_excel asbobi jadval matnini shu model bilan o'qiydi (rangli belgilar va shartlar — Gemma).
IMAGE=${IMAGE:-vllm/vllm-openai:v0.31.0}
docker rm -f sarob-vllm-ocr >/dev/null 2>&1
docker run -d --name sarob-vllm-ocr --restart unless-stopped \
  --device nvidia.com/gpu=all --ipc host --shm-size 4g \
  --network host \
  -v "$HOME/models:/models:ro" \
  -v "$HOME/.cache/vllm:/root/.cache/vllm" \
  "$IMAGE" \
  --model /models/paddleocr-vl-1.6 \
  --served-model-name paddleocr-vl \
  --host 127.0.0.1 --port 8002 \
  --max-model-len 16384 \
  --max-num-batched-tokens 16384 \
  --gpu-memory-utilization 0.07 \
  --max-num-seqs 8 \
  --no-enable-prefix-caching \
  --mm-processor-cache-gb 0
