#!/bin/bash
# 2-raund: hozirgi Gemma (lm_head FP8) bilan javob yaratish -> faqat 2-raund javoblarini ajratish ->
# joriy o'zbekcha taxminchidan davom ettirib o'qitish. Spark'da: nohup ./chain_r2.sh > chain_r2.log 2>&1 &
cd ~/sarob/train
cp ~/sarob/sarob_prompt.md sarob_prompt.md          # joriy tizim prompti
echo "$(date +%H:%M) javob yaratish boshlandi"
PAR=96 PROMPTS=prompts_r2.jsonl ./run_gen.sh > gen_r2.log 2>&1
python3 - <<'PY'
import json
ids = {json.loads(l)["id"] for l in open("prompts_r2.jsonl", encoding="utf-8")}
n = 0
with open("responses_r2.jsonl", "w", encoding="utf-8") as out:
    for l in open("responses.jsonl", encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r["id"] in ids:
            out.write(l); n += 1
print("2-raund javoblari:", n)
PY
echo "$(date +%H:%M) o'qitish boshlandi"
ARGS="--data /data/responses_r2.jsonl --drafter /models/gemma4-26b-assistant-uz --out /models/gemma4-26b-assistant-uz2 --lr 5e-5 --warmup 50 --step_w 1.0,0.9,0.8 --save_every 1000 --eval_n 200" \
  ./run_train.sh > train_r2.log 2>&1
echo "$(date +%H:%M) 2-raund tugadi"
