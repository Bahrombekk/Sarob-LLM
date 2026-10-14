#!/bin/bash
# Sarob Telegram botini (qayta) ishga tushiradi
cd ~/sarob/bot && docker build -q -t sarob-bot . >/dev/null
mkdir -p ~/sarob/bot/tools ~/sarob/bot/data
cp ~/sarob/tool_internet.py ~/sarob/tool_baza.py ~/sarob/tool_rasm.py ~/sarob/filter_tezlik.py ~/sarob/sarob_prompt.md ~/sarob/bot/tools/
docker rm -f sarob-bot >/dev/null 2>&1
docker run -d --name sarob-bot --restart unless-stopped --network host --memory 2g \
  -v ~/sarob/bot/tools:/tools:ro -v ~/sarob/workspace/fayllar:/fayllar:ro \
  -v ~/sarob/bazalar:/bazalar:ro -v ~/sarob/pg:/run/sarob_pg:ro \
  -v ~/sarob/bot/.telegram_token:/run/secrets/telegram_token:ro \
  -v ~/sarob/.terminal_key:/run/secrets/terminal_key:ro \
  -v ~/sarob/bot/data:/data sarob-bot
