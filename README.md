# 🌅 Sarob-LLM

**Sarob** — NVIDIA DGX Spark'da to'liq lokal ishlaydigan shaxsiy o'zbekcha AI agent.
Internetdan qidiradi, Excel/Word/grafik yaratadi, rasmdagi jadvallarni o'qiydi, biznes bazalaridan
(faqat o'qish) hisobot tayyorlaydi, Telegram orqali ham ishlaydi. Hech qanday ma'lumot tashqi bulutga chiqmaydi.

## Arxitektura

```
 Foydalanuvchi ──► Open WebUI (:3000)  ──┐            Telegram ──► sarob-bot
                    │ filtrlar:           │                          │ (o'z agent tsikli)
                    │  • tezlik (o'ylash  │                          │
                    │    chegarasi, halqa │                          │
                    │    himoyasi, tozal.)│                          │
                    │  • yengil suhbat ⚡ │                          │
                    ▼                     ▼                          ▼
   ┌─────────── Modellar (vLLM 0.31) ───────────┐      ┌──── Asboblar ────────────────────┐
   │ Sarob / Sarob Tez : Gemma 4 26B-A4B NVFP4  │      │ internet: SearXNG (:8095)        │
   │   (unsloth) + MTP k=2, :8000, ~45-69 tok/s    │      │ sahifa/brauzer: Playwright (:8097)│
   │ Sarob Pro : Qwen3.8 27B NVFP4 + MTP, :8001 │      │ chuqur tadqiqot, valyuta (CBU)   │
   │ Embedding : bge-m3 (Ollama, :11435)        │      │ bazalar: SQLite/PostgreSQL (o'qish)│
   └────────────────────────────────────────────┘      │ rasmlardan Excel                 │
                                                        │ kod: Jupyter (:8888)             │
                                                        │ Linux kompyuter: Open Terminal (:8099)│
                                                        │ fayllar: http://…:8090           │
                                                        └──────────────────────────────────┘
```

## Papkalar

| Papka | Ichida nima bor |
|---|---|
| `serving/` | vLLM'da modellarni ishga tushirish: `sarob_vllm.sh` (Gemma, asosiy), `sarob_vllm_pro.sh` (Qwen3.8 Pro), `sarob_vllm_q36.sh` (sinov: Qwen3.6-A3B) |
| `webui/` | Open WebUI konteyneri (`sarob_webui.sh`), Sarob modellarini yaratish (`make_sarob.py`), tizim prompti (`sarob_prompt.md`), asbob/filtr o'rnatuvchilari, logo |
| `tools/` | Sarob asboblari: internet (qidiruv, sahifa, brauzer, chuqur tadqiqot, GitHub, valyuta, chatdagi fayllar), bazalar, rasmlardan Excel |
| `filters/` | `filter_tezlik.py` — savol turiga qarab o'ylash chegarasi (32/512/1024), halqadan himoya, aralashgan o'ylashni tozalash; `filter_yengil.py` — "Yengil suhbat" tugmasi |
| `services/` | Yordamchi xizmatlar: Jupyter, brauzer, SearXNG, harorat kuzatuvi; `start_services.sh` hammasini ishga tushiradi |
| `bot/` | Telegram bot (`sarob_bot.py`), ishga tushirish va tokenni xavfsiz kiritish skriptlari |
| `database/` | Bazani maxfiy ustunlarsiz nusxalash (`sanitize_db.py`), PostgreSQL'da faqat-o'qish foydalanuvchisi (`sarob_ro.sql`) |
| `eval/` | Sinov poligoni (`sarob_eval.py`, 31 savol), tezlik/kesh/MTP/tokenlar o'lchovlari, natijalar |
| `training/` | O'zbekcha MTP taxminchisini o'qitish rejasi va ma'lumot yuklovchilari (jarayonda) |
| `docs/research/` | 41 agentlik tadqiqot natijalari va tajriba rejalari |
| `scripts/deploy.sh` | Loyihani Spark'ga yuborib, hammasini bir buyruq bilan o'rnatadi |

## O'rnatish / yangilash

```bash
# kompyuterdan (Git Bash)
bash scripts/deploy.sh

# Spark'da birinchi marta (yordamchi xizmatlar va modellar)
ssh dasuty@192.168.136.153
cd ~/sarob && ./start_services.sh && ./sarob_vllm.sh && ./sarob_vllm_pro.sh && ./sarob_webui.sh
```

### Spark'dagi tuzilma

Spark'da hammasi bitta joyda — `~/Desktop/Sarob-LLM` (`scripts/spark_layout.sh` yig'adi):

```
~/Desktop/Sarob-LLM/
├── serving/ webui/ tools/ ...   kod (shu repozitoriy, git clone)
├── runtime/                     ishlab turgan fayllar: bazalar, workspace, bot, o'qitish ma'lumotlari, kalitlar
├── models -> ~/models           modellar (havola)
└── logs/                        yuklash loglari
~/sarob -> ~/Desktop/Sarob-LLM/runtime   (eski yo'llar ishlashda davom etadi)
```

Maxfiy fayllar faqat Spark'da turadi va loyihaga kirmaydi (`.gitignore`):
`~/sarob/.jupyter_token`, `~/sarob/.terminal_key`, `~/.owui_secret`, `~/sarob/bot/.telegram_token`, `~/sarob/pg/*.dsn`.

## O'lchangan natijalar (2026-10-13/14)

| Ko'rsatkich | Avval | Hozir |
|---|---|---|
| Gemma tezligi | 46–53 tok/s | **59–70 tok/s** (unsloth nusxasi, Marlin'siz) |
| O'zbekcha javob tezligi (MTP k=4 → k=2) | 34.5 tok/s | 44.6 tok/s (+29%) |
| O'zbekcha javob tezligi (taxminchi o'zbekchaga o'qitildi) | 44.6 tok/s | 70.5 tok/s (+58%) |
| O'zbekcha javob tezligi (`lm_head` FP8) | 69.1 tok/s | **77.6 tok/s (+12%; kun boshidan 2.25×)** |
| Takroriy internet so'rovi / valyuta kursi | 1–2 s | **0 s** (kesh) |
| Mavjud bo'lmagan sahifa (404) | 30 s gacha | **0.1 s** |
| 26 ta vazifa umumiy vaqti | 1549 s | **855 s (−45%)** |
| Salom / tarjima | 3–8 s | **0.4–2 s** |
| Chuqur tadqiqot asbobi | 17–23 s | **5 s** |
| Uzun suhbat ("Yengil suhbat" yoqilganda) | 22 178 token, 6.8 s | **4 169 token, 2.3 s** |

**Topilgan asosiy muammo:** MTP taxminchisi o'zbekchada atigi 10% to'g'ri taxmin qilardi (inglizcha 43%),
o'zbekcha matn 2× ko'p tokenga bo'linadi → o'zbekcha javob inglizchadan ancha sekin edi.

**Yechim (`training/`):** taxminchi (Gemma 4 assistant, 4 qatlam) 16 400 ta Sarob javobida (80% o'zbekcha)
Gemma taqsimotiga KL-distillatsiya bilan o'qitildi (~15 soat Spark'da). Natija:

| | Oldin | Keyin |
|---|---|---|
| O'zbekcha javob, Gemma bilan mos kelish (1-qadam) | 55.3% | **82.2%** |
| O'zbekcha, vLLM'da qabul qilingan taxminlar | 9.4% | **29.3%** |
| O'zbekcha javob tezligi | 43.8 tok/s | **70.5 tok/s** |
| Inglizcha / ruscha tezlik | 69.8 / 68.0 | 66.1 / 64.8 (−5%) |

O'qitilgan taxminchi Spark'da: `~/models/gemma4-26b-assistant-uz` (840 MB, repozitoriyga kirmaydi).
Eskisiga qaytish: `DRAFTER=/models/gemma4-26b-assistant ./sarob_vllm.sh`.

## Muhim saboqlar

- Model parametrlarida `thinking_token_budget` bo'lmasin — Open WebUI ularni filtrdan **keyin** qo'llaydi.
- SearXNG'ga `language` (en-US/ru-RU) berilmasa, natijalar yomon.
- Spark xotirasi umumiy (121 GiB): har bir model ishga tushganda kamida 15 GiB bo'sh qolishi kerak;
  FlashInfer autotune Qwen'da xotirani deyarli tugatgan — o'chirilgan.
- O'ylash inglizcha bo'lsa aniqroq (12/12 vs 11/12), yakuniy javob doim o'zbekcha.
