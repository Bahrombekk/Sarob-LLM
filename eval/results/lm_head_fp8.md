# Tajriba: lm_head (chiqish qatlami) BF16 -> FP8 (2026-10-15)

Unsloth NVFP4 checkpoint'ida lm_head embedding bilan bog'langan va BF16 (har tokenda ~1.5 GB o'qish).
`serving/tools/untie_lmhead_fp8.py` (tenhkspark/gemma4-spark asosida, Apache-2.0) bilan ajratib, FP8 W8A8 qilindi
(kosinus 0.99965). Diqqat: unsloth config'ida group_1 MoE ekspertlari — yangi guruh bo'sh nom bilan qo'shilishi shart.

| | BF16 | FP8 |
|---|---|---|
| O'zbekcha / inglizcha / ruscha tok/s | 69.1 / 66.7 / 64.5 | **77.6 / 73.4 / 71.1** |
| Taxminlar qabul qilinishi (uz) | 28.7% | 29.8% |
| 31 savol (1 marta) | 24 / 6 / 1 | 24 / 2 / 5 |
| 5 shubhali savol x 4 marta | 13 / 5 / 2, fakt xatosi 8 | **17 / 3 / 0, fakt xatosi 4** |

Birinchi yugurishdagi farq tasodif bo'lib chiqdi (takroriy 40 javobda FP8 yomonroq emas, o'ylash oqib chiqishi 0). FP8 qoldirildi.

## Qo'shimcha: to'liq FP8 model (RedHatAI/gemma-4-26B-A4B-it-FP8-dynamic)

Boshqa Spark'da (inglizcha, k=4) NVFP4'dan tez deb e'lon qilingan edi. Bizda o'zbekcha taxminchi bilan sekinroq:

| | NVFP4 + lm_head FP8 (hozirgi) | To'liq FP8, k=2 | To'liq FP8, k=3 |
|---|---|---|---|
| O'zbekcha tok/s | **77.6** | 55.6 | 53.6 |
| Qabul qilinish (uz) | 29.8% | 32.1% | 40.5% |

Rad etildi: og'irliklar 27 GB (NVFP4 17 GB) — o'qish ko'p, tezlik past.

## Taxminchi lm_head FP8 va moslashuvchan tekshiruv

| Variant | O'zbekcha | Inglizcha | Ruscha |
|---|---|---|---|
| Hozirgi (BF16 taxminchi, k=2) | 77.6 | 73.4 | 71.1 |
| **FP8 taxminchi, k=2** | **85.2** | **81.3** | **77.9** |
| FP8 taxminchi, k=3 | 83.4 | 78.7 | 74.1 |
| Moslashuvchan tekshiruv, k=3 | 67.2 | 67.7 | 64.8 |
| Moslashuvchan tekshiruv, k=4 | 58.6 | 62.4 | 56.2 |

FP8 taxminchi qoldirildi (qabul qilinish 29.5% — o'zgarmadi; spekulyativ dekodlash yo'qotishsiz, javob sifatiga ta'sir yo'q).
Moslashuvchan tekshiruv rad etildi.
