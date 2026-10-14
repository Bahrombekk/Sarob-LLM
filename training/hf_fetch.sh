#!/bin/bash
# Modelni HuggingFace'dan yuklash: curl -C - bilan to'xtagan joyidan davom ettiradi
REPO=${1:-nvidia/Qwen3.8-27B-NVFP4}
DIR=${2:-$HOME/models/qwen38-27b-nvfp4}
mkdir -p "$DIR"
FILES=$(curl -s "https://huggingface.co/api/models/$REPO" | python3 -c "import sys,json;print('\n'.join(s['rfilename'] for s in json.load(sys.stdin)['siblings']))")
for f in $FILES; do
  mkdir -p "$DIR/$(dirname "$f")"
  for i in $(seq 1 50); do
    # 2 daqiqa davomida tezlik 10 KB/s dan past bo'lsa, ulanishni uzib qayta urinadi
    curl -sSL -C - --speed-limit 10240 --speed-time 120 -o "$DIR/$f" "https://huggingface.co/$REPO/resolve/main/$f" && break
    echo "$(date +%H:%M) qayta $f ($i)"; sleep 5
  done
  echo "$(date +%H:%M) tayyor: $f"
done
echo "$(date +%H:%M) HAMMASI TAYYOR"
