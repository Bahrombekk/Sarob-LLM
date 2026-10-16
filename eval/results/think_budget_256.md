# Tajriba: o'ylash ichida javob qoralamasi (2026-10-16)

Kuzatuv (foydalanuvchi): model o'ylash ichida javobni inglizcha yozib chiqadi, keyin o'zbekcha qayta yozadi — ikki ish.
Tasdiqlandi: VLOOKUP savolida 512 tokenlik o'ylash = sintaksis + misol jadvali + formula (qoralama).

| Variant | O'ylash tokenlari | Vaqt (31 savol) | PASS / PARTIAL / FAIL |
|---|---|---|---|
| Prompt: "o'ylashda javob matnini yozma" (chegara 1024) | 25 399 (o'zgarmadi) | 930 s | — (model ko'rsatmaga amal qilmadi) |
| Filtr darajalari, oddiy savol 512 (hozirgi) | 18 160 | 826 s | **21 / 8 / 2** |
| Filtr darajalari, oddiy savol 256 | 14 009 | 640 s (−22%) | 18 / 6 / 7 |

256 da internet/brauzer/ko'p qadamli vazifalarda qadam tashlab ketildi va raqamlar o'ylab topildi (Q18, Q21, Q22, Q25).
Xulosa: o'ylash uslubini na prompt, na chegara bilan xavfsiz qisqartirib bo'lmaydi — 512 qoldirildi.
