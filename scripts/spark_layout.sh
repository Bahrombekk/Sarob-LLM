#!/bin/bash
# Spark'da Sarobni bitta joyga yig'adi: ~/Desktop/Sarob-LLM
#   kod (git clone) + runtime/ (avvalgi ~/sarob) + models -> ~/models + logs/
# ~/sarob o'rnida runtime/ ga havola qoladi — skriptlar, Docker konteynerlari va bot o'zgarishsiz ishlaydi.
# Bir marta ishga tushiriladi; qayta ishga tushirilsa, bajarilgan qadamlar o'tkazib yuboriladi.
set -e
ROOT=$HOME/Desktop/Sarob-LLM
REPO=https://github.com/Bahrombekk/Sarob-LLM.git

# 1) Kod
if [ ! -d "$ROOT/.git" ]; then
  git clone -q "$REPO" "$ROOT"
else
  git -C "$ROOT" pull -q --ff-only
fi

# 2) Ishlab turgan fayllar: ~/sarob -> runtime/ (bir fayl tizimida mv — ochiq fayllar va konteynerlar uzilmaydi)
if [ -d "$HOME/sarob" ] && [ ! -L "$HOME/sarob" ]; then
  mv "$HOME/sarob" "$ROOT/runtime"
  ln -s "$ROOT/runtime" "$HOME/sarob"
fi

# 3) Modellar (katta, ko'chirilmaydi — havola)
[ -e "$ROOT/models" ] || ln -s "$HOME/models" "$ROOT/models"

# 4) Uy papkasida sochilib qolgan Sarob fayllari (faqat shu loyihaga tegishlilari)
mkdir -p "$ROOT/logs" "$ROOT/runtime/bin"
for f in sarob_fetch.log bf16_fetch.log e2b_fetch.log unsloth_fetch.log q36_fetch.log qwen_fetch.log \
         vllm_fetch.log vllm_pull.log owui_pull.log stopped_containers_2026-10-12.txt; do
  [ -f "$HOME/$f" ] && mv "$HOME/$f" "$ROOT/logs/"
done
for f in sarob_fetch.sh qwen_fetch.sh vllm_fetch.sh; do
  [ -f "$HOME/$f" ] && mv "$HOME/$f" "$ROOT/runtime/bin/"
done
# eski nusxalar (asl nusxasi kodda)
for f in sarob_prompt.md sarob_vllm.sh; do
  [ -f "$HOME/$f" ] && mv "$HOME/$f" "$ROOT/logs/eski_$f"
done
# hf_fetch.sh: o'qitish va yuklash skriptlari ~/hf_fetch.sh ni chaqiradi — havola qoldiramiz
if [ -f "$HOME/hf_fetch.sh" ] && [ ! -L "$HOME/hf_fetch.sh" ]; then
  mv "$HOME/hf_fetch.sh" "$ROOT/runtime/bin/hf_fetch.sh"
  ln -s "$ROOT/runtime/bin/hf_fetch.sh" "$HOME/hf_fetch.sh"
fi

echo "Tayyor: $ROOT"
ls -la "$ROOT"
