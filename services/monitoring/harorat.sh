#!/bin/bash
# Spark haroratini har daqiqada ~/sarob/bot/data/harorat.json ga yozadi (Telegram bot o'qiydi)
OUT="$HOME/sarob/bot/data/harorat.json"
while true; do
  IFS=',' read -r gpu power util reasons < <(nvidia-smi --query-gpu=temperature.gpu,power.draw,utilization.gpu,clocks_event_reasons.active \
    --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
  board=0
  for z in /sys/class/thermal/thermal_zone*/temp; do
    t=$(( $(cat "$z" 2>/dev/null || echo 0) / 1000 )); [ "$t" -gt "$board" ] && board=$t
  done
  printf '{"ts":%s,"gpu":%s,"board":%s,"power":"%s","util":"%s","reasons":"%s"}\n' \
    "$(date +%s)" "${gpu:-0}" "$board" "${power:-?}" "${util:-?}" "${reasons:-0x0}" > "$OUT.tmp" && mv "$OUT.tmp" "$OUT"
  sleep 60
done
