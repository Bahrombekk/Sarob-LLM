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
