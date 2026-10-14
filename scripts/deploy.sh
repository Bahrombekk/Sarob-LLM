#!/bin/bash
# Loyihani Spark'ga yuboradi va Open WebUI'ga asboblar/filtrlar/modellarni o'rnatadi.
# Ishlatish (kompyuteringizdan, Git Bash'da):  bash scripts/deploy.sh
# Faqat kod va sozlamalarni yuboradi; maxfiy fayllar (.jupyter_token, .terminal_key, bot tokeni, pg/*.dsn) Spark'da qoladi.
set -e
HOST=${HOST:-dasuty@192.168.136.153}
cd "$(dirname "$0")/.."

echo "1) Fayllarni Spark'ga yuborish (~/sarob)..."
ssh "$HOST" 'mkdir -p ~/sarob/{jupyter,browser,searxng,monitoring,bot/tools,bazalar,workspace/fayllar,branding}'
scp -q serving/*.sh webui/*.sh webui/*.py webui/sarob_prompt.md tools/*.py filters/*.py "$HOST:~/sarob/"
scp -q eval/*.py "$HOST:~/sarob/"
scp -q services/start_services.sh "$HOST:~/sarob/"
scp -q services/jupyter/Dockerfile "$HOST:~/sarob/jupyter/"
scp -q services/browser/Dockerfile services/browser/browser_server.py "$HOST:~/sarob/browser/"
scp -q services/monitoring/harorat.sh "$HOST:~/sarob/bot/"
scp -q services/monitoring/sarob-harorat.service "$HOST:~/sarob/monitoring/"
scp -q bot/sarob_bot.py bot/sarob_bot_run.sh bot/set_token.sh bot/Dockerfile "$HOST:~/sarob/bot/"
# SearXNG sozlamasi: Spark'dagi nusxada haqiqiy secret_key bor — uni ustidan yozmaymiz
ssh "$HOST" 'test -f ~/sarob/searxng/settings.yml' || scp -q services/searxng/settings.yml "$HOST:~/sarob/searxng/"

echo "2) Qator oxirlarini tuzatish va ruxsatlar..."
ssh "$HOST" 'cd ~/sarob && sed -i "s/\r$//" *.sh *.py *.md bot/*.sh bot/*.py browser/*.py && chmod +x *.sh bot/*.sh'

echo "3) Open WebUI: asboblar, filtrlar va Sarob modellari..."
ssh "$HOST" 'cd ~/sarob
for f in tool_internet.py tool_baza.py tool_rasm.py filter_tezlik.py filter_yengil.py install_tool.py install_filter.py make_sarob.py sarob_prompt.md; do docker cp $f open-webui:/tmp/; done
E="docker exec -w /app/backend -e PYTHONPATH=/app/backend open-webui python3"
$E /tmp/install_tool.py /tmp/tool_internet.py sarob_internet "Internet (Sarob)"
$E /tmp/install_tool.py /tmp/tool_baza.py sarob_baza "Bazalar (Sarob)"
$E /tmp/install_tool.py /tmp/tool_rasm.py sarob_rasm "Rasmlardan Excel (Sarob)"
$E /tmp/install_filter.py /tmp/filter_tezlik.py sarob_tezlik "Sarob tezlik filtri"
$E /tmp/install_filter.py /tmp/filter_yengil.py sarob_yengil "Yengil suhbat"
$E /tmp/make_sarob.py /tmp/sarob_prompt.md'

echo "4) Telegram botni yangilash..."
ssh "$HOST" 'cd ~/sarob/bot && ./sarob_bot_run.sh >/dev/null'

echo "Tayyor. (Modellar o'zgargan bo'lsa: ssh $HOST \"cd ~/sarob && ./sarob_vllm.sh\")"
