#!/bin/bash
# Sarobning yordamchi xizmatlarini (qayta) ishga tushiradi. Spark'da ~/sarob ichidan ishga tushiriladi.
# Maxfiy kalitlar fayllardan o'qiladi (ular loyihada saqlanmaydi):
#   ~/sarob/.jupyter_token, ~/sarob/.terminal_key  — `openssl rand -hex 24 > fayl` bilan yaratiladi
set -e
cd ~/sarob

# 1) Ollama (Docker) — bge-m3 embedding uchun (tizimdagi Ollama buzilgani sababli), port 11435
docker rm -f sarob-ollama >/dev/null 2>&1 || true
docker run -d --name sarob-ollama --restart unless-stopped --network host --device nvidia.com/gpu=all \
  -e OLLAMA_HOST=127.0.0.1:11435 -e OLLAMA_KEEP_ALIVE=30m -e OLLAMA_MAX_LOADED_MODELS=3 \
  -v /usr/share/ollama/.ollama/models:/root/.ollama/models ollama/ollama:latest

# 2) Jupyter — Python kod bajarish (Excel/Word/grafik), port 8888 (faqat lokal)
docker build -q -t sarob-jupyter jupyter/ >/dev/null
docker rm -f sarob-jupyter >/dev/null 2>&1 || true
docker run -d --name sarob-jupyter --restart unless-stopped -p 127.0.0.1:8888:8888 --memory 16g --cpus 8 \
  -e JUPYTER_TOKEN="$(cat ~/sarob/.jupyter_token)" \
  -v ~/sarob/workspace:/workspace -v ~/sarob/bazalar:/bazalar:ro \
  --mount type=volume,src=open-webui,dst=/yuklanganlar,readonly,volume-subpath=uploads sarob-jupyter

# 3) Fayllarni yuklab olish serveri — http://192.168.136.153:8090/
docker rm -f sarob-files >/dev/null 2>&1 || true
docker run -d --name sarob-files --restart unless-stopped -p 8090:8090 --memory 512m \
  -v ~/sarob/workspace/fayllar:/srv:ro --entrypoint python3 sarob-jupyter -m http.server 8090 --directory /srv

# 4) SearXNG — o'z qidiruv tizimimiz, port 8095 (faqat lokal)
docker rm -f sarob-search >/dev/null 2>&1 || true
docker run -d --name sarob-search --restart unless-stopped -p 127.0.0.1:8095:8080 --memory 1g \
  -v ~/sarob/searxng/settings.yml:/etc/searxng/settings.yml:ro searxng/searxng:latest

# 5) Brauzer (Playwright/Chromium API), port 8097 (faqat lokal)
docker build -q -t sarob-browser browser/ >/dev/null
docker rm -f sarob-browser >/dev/null 2>&1 || true
docker run -d --name sarob-browser --restart unless-stopped -p 127.0.0.1:8097:8097 --memory 4g --shm-size 1g \
  -v ~/sarob/workspace/fayllar:/workspace/fayllar -v ~/sarob/browser/browser_server.py:/app/browser_server.py:ro sarob-browser

# 6) Open Terminal — Sarob Pro'ning shaxsiy Linux kompyuteri, port 8099 (faqat lokal)
docker rm -f sarob-terminal >/dev/null 2>&1 || true
docker run -d --name sarob-terminal --restart unless-stopped -p 127.0.0.1:8099:8000 --memory 8g --cpus 8 \
  -e OPEN_TERMINAL_API_KEY="$(cat ~/sarob/.terminal_key)" \
  -v sarob-terminal-home:/home/user -v ~/sarob/workspace/fayllar:/home/user/fayllar \
  ghcr.io/open-webui/open-terminal:latest

# 7) Harorat kuzatuvi (systemd foydalanuvchi xizmati)
mkdir -p ~/.config/systemd/user
cp monitoring/sarob-harorat.service ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now sarob-harorat

echo "Yordamchi xizmatlar ishga tushdi."
