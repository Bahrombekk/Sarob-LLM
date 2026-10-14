#!/bin/bash
# Taxminchini o'qitish (xavfsiz rejim). Spark'da: ~/sarob/train/start_train.sh
#  - Qwen Pro to'xtatiladi, Gemma kamroq xotira bilan (0.25) ishlab turadi — Sarob o'qitish paytida ham javob beradi
#  - BF16 Gemma (52 GB) + taxminchi o'qitish konteynerda; qo'riqchi bo'sh xotira 10 GB dan kamaysa to'xtatadi
#  - oxirida hammasi oddiy holatga qaytadi
cd ~/sarob/train
ARGS=${ARGS:-}
wait_up() { for i in $(seq 1 90); do curl -sf localhost:8000/v1/models >/dev/null && return; sleep 10; done; }
avail_gb() { awk '/MemAvailable/ {print int($2/1048576)}' /proc/meminfo; }

restore() {
  docker rm -f sarob-train-run >/dev/null 2>&1
  ~/sarob/sarob_vllm.sh >/dev/null; wait_up
  docker start sarob-vllm-pro >/dev/null
  echo "$(date +%H:%M) oddiy holatga qaytdi (Gemma 0.35, Pro yoqildi)"
}
trap restore EXIT

docker stop sarob-vllm-pro >/dev/null
sed -e 's/--gpu-memory-utilization 0.35/--gpu-memory-utilization 0.25/' ~/sarob/sarob_vllm.sh > /tmp/vllm_train.sh
bash /tmp/vllm_train.sh >/dev/null; wait_up
echo "$(date +%H:%M) Gemma 0.25 bilan ishlayapti, bo'sh xotira $(avail_gb) GB"

docker rm -f sarob-train-run >/dev/null 2>&1
docker run -d --name sarob-train-run --device nvidia.com/gpu=all --ipc host \
  -v ~/models:/models -v ~/sarob/train:/data --entrypoint python3 vllm/vllm-openai:v0.31.0 \
  -u /data/train_drafter.py $ARGS >/dev/null
docker logs -f sarob-train-run &
LOGS=$!
while [ "$(docker inspect -f '{{.State.Running}}' sarob-train-run 2>/dev/null)" = "true" ]; do
  if [ "$(avail_gb)" -lt 10 ]; then
    echo "$(date +%H:%M) XOTIRA KAM ($(avail_gb) GB) — o'qitish to'xtatildi"; docker stop -t 5 sarob-train-run >/dev/null; break
  fi
  sleep 5
done
kill $LOGS 2>/dev/null
echo "$(date +%H:%M) o'qitish tugadi: $(docker inspect -f '{{.State.ExitCode}}' sarob-train-run)"
