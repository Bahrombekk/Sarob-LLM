#!/bin/bash
# Javob yaratish tugashini kutadi, so'ng taxminchini o'qitishni boshlaydi. Spark'da: nohup ./chain.sh > chain.log 2>&1 &
cd ~/sarob/train
while pgrep -f "[r]un_gen.sh" >/dev/null; do sleep 60; done
echo "$(date +%H:%M) javob yaratish tugadi: $(wc -l < responses.jsonl) ta javob"
ARGS="--data /data/responses.jsonl --out /models/gemma4-26b-assistant-uz --lr 1e-4 --warmup 50 --save_every 1000 --eval_n 200" \
  ./run_train.sh > train.log 2>&1
echo "$(date +%H:%M) o'qitish bosqichi tugadi"
