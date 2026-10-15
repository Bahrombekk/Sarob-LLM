#!/bin/bash
# O'ylash chegarasida oqish: eski yopish (faqat <channel|>) va o'tish iborasi bilan yopish.
cd ~/sarob
w() { for i in $(seq 1 90); do curl -sf localhost:8000/v1/models >/dev/null && return; sleep 10; done; }
NEW='\n\nTime is up. I must stop thinking now and write the final answer directly, in Uzbek.<channel|>'
echo "== ESKI (faqat <channel|>)"
./sarob_vllm.sh >/dev/null; w
python3 leak_budget.py 128 6 | tail -1
echo "== YANGI (o'tish iborasi)"
REASON_END="$NEW" ./sarob_vllm.sh >/dev/null; w
docker inspect sarob-vllm --format '{{.Args}}' | grep -o 'Time is up[^"]*' | head -1
python3 leak_budget.py 128 6
echo TUGADI
