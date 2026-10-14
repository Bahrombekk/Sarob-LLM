#!/bin/bash
# Javoblarni yaratish (xavfsiz rejim). Spark'da: nohup ~/sarob/train/run_gen.sh > ~/sarob/train/gen.log 2>&1 &
#  - MTP o'chiriladi (javob matniga ta'sir qilmaydi, faqat tezlik; ko'p parallelda o'zbekchada foydasiz)
#  - Qwen Pro vaqtincha to'xtatiladi (34 GB bo'shaydi), oxirida qayta yoqiladi
#  - qo'riqchi: bo'sh xotira 12 GB dan kamaysa, yaratish to'xtatiladi (2026-10-14 da Spark xotira tanqisligidan qotgan)
cd ~/sarob/train
PAR=${PAR:-32}
PROMPTS=${PROMPTS:-prompts_gen.jsonl}
wait_up() { for i in $(seq 1 90); do curl -sf localhost:8000/v1/models >/dev/null && return; sleep 10; done; }
avail_gb() { awk '/MemAvailable/ {print int($2/1048576)}' /proc/meminfo; }

restore() {
  pkill -f "[g]en_responses.py" 2>/dev/null
  ~/sarob/sarob_vllm.sh >/dev/null; wait_up
  docker start sarob-vllm-pro >/dev/null
  echo "$(date +%H:%M) server oddiy rejimga qaytdi, Pro yoqildi"
}
trap restore EXIT

docker stop sarob-vllm-pro >/dev/null
sed -e '/--speculative-config/d' -e "s/\${MAX_SEQS:-8}/$PAR/" ~/sarob/sarob_vllm.sh > /tmp/vllm_gen.sh
bash /tmp/vllm_gen.sh >/dev/null; wait_up
echo "$(date +%H:%M) server tayyor: MTP'siz, $PAR parallel, bo'sh xotira $(avail_gb) GB"

python3 gen_responses.py "$PROMPTS" responses.jsonl "$PAR" &
GEN=$!
while kill -0 $GEN 2>/dev/null; do
  if [ "$(avail_gb)" -lt 12 ]; then
    echo "$(date +%H:%M) XOTIRA KAM ($(avail_gb) GB) — yaratish to'xtatildi"; kill $GEN; break
  fi
  sleep 5
done
wait $GEN 2>/dev/null
