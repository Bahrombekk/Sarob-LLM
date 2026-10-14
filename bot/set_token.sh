#!/bin/bash
# Telegram bot tokenini himoyalangan faylga saqlaydi (ekranda ko'rinmaydi)
umask 077
mkdir -p ~/sarob/bot
read -r -s -p "Telegram bot tokenini qo'ying (ko'rinmaydi) va Enter bosing: " T
echo
if [[ ! "$T" =~ ^[0-9]+:[A-Za-z0-9_-]{30,}$ ]]; then echo "XATO: token formati noto'g'ri"; exit 1; fi
printf '%s' "$T" > ~/sarob/bot/.telegram_token
chmod 600 ~/sarob/bot/.telegram_token
echo "Saqlandi ✅ Endi bu oynani yopishingiz mumkin."
