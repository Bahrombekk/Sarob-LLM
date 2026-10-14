#!/bin/bash
# Sarob interfeysi: Open WebUI (port 3000), host tarmog'ida
IMAGE=${IMAGE:-ghcr.io/open-webui/open-webui:main}
JT=$(cat "$HOME/sarob/.jupyter_token")
# Sarob logosi: har bir faylni ikkala static papkaga ham ulaymiz
B="$HOME/sarob/branding"
LOGO=()
for f in "$B"/*; do
  n=$(basename "$f")
  LOGO+=(-v "$f:/app/build/static/$n:ro" -v "$f:/app/backend/open_webui/static/$n:ro")
done
LOGO+=(-v "$B/favicon.png:/app/build/favicon.png:ro")
docker rm -f open-webui >/dev/null 2>&1
docker run -d --name open-webui --restart always \
  --network host \
  "${LOGO[@]}" \
  -v open-webui:/app/backend/data \
  -v "$HOME/sarob/bazalar:/bazalar:ro" \
  -v "$HOME/sarob/pg:/run/sarob_pg:ro" \
  -v "$HOME/sarob/workspace/fayllar:/fayllar" \
  -e PORT=3000 \
  -e WEBUI_SECRET_KEY="$(cat "$HOME/.owui_secret")" \
  -e WEBUI_NAME=Sarob \
  -e DEFAULT_LOCALE=uz-UZ \
  -e ENABLE_SIGNUP=false \
  -e OLLAMA_BASE_URL=http://127.0.0.1:11435 \
  -e ENABLE_OPENAI_API=true \
  -e OPENAI_API_BASE_URLS="http://127.0.0.1:8000/v1;http://127.0.0.1:8001/v1" \
  -e OPENAI_API_KEYS="none;none" \
  -e RAG_EMBEDDING_ENGINE=ollama \
  -e RAG_OLLAMA_BASE_URL=http://127.0.0.1:11435 \
  -e RAG_EMBEDDING_MODEL=bge-m3:latest \
  -e ENABLE_RAG_HYBRID_SEARCH=true \
  -e RAG_RERANKING_MODEL=BAAI/bge-reranker-v2-m3 \
  -e RAG_TOP_K=8 \
  -e RAG_TOP_K_RERANKER=4 \
  -e CHUNK_SIZE=1200 \
  -e CHUNK_OVERLAP=150 \
  -e PDF_EXTRACT_IMAGES=true \
  -e ENABLE_WEB_SEARCH=true \
  -e WEB_SEARCH_ENGINE=duckduckgo \
  -e WEB_SEARCH_RESULT_COUNT=5 \
  -e ENABLE_CODE_INTERPRETER=true \
  -e CODE_INTERPRETER_ENGINE=jupyter \
  -e CODE_INTERPRETER_JUPYTER_URL=http://127.0.0.1:8888 \
  -e CODE_INTERPRETER_JUPYTER_AUTH=token \
  -e CODE_INTERPRETER_JUPYTER_AUTH_TOKEN="$JT" \
  -e CODE_EXECUTION_ENGINE=jupyter \
  -e CODE_EXECUTION_JUPYTER_URL=http://127.0.0.1:8888 \
  -e CODE_EXECUTION_JUPYTER_AUTH=token \
  -e CODE_EXECUTION_JUPYTER_AUTH_TOKEN="$JT" \
  -e ENABLE_MEMORIES=true \
  -e CHAT_RESPONSE_MAX_TOOL_CALL_ITERATIONS=10 \
  "$IMAGE"
