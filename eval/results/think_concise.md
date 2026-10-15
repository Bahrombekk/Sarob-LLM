# Tajriba: o'ylashni prompt orqali qisqartirish (2026-10-15)

31 savol, o'ylash yoqiq, chegara 1024 token, o'zbekchaga o'qitilgan taxminchi bilan.

| Variant | Prompt | O'ylash tokenlari | Umumiy vaqt | PASS / PARTIAL / FAIL |
|---|---|---|---|---|
| **A (hozirgi)** | "qisqa va ingliz tilida o'ylasang bo'ladi" | 23 483 | 1025 s | **24 / 6 / 1** |
| B | "qisqa qoralama, 1-3 qator" | 10 299 | 732 s | 24 / 4 / 3 |
| C | B + "o'tkazib yuborma, 3 qadam: maqsad, asbob, tekshiruv" | 4 339 | 527 s | 19 / 7 / 5 |

**Xulosa:** "qisqa o'yla" ko'rsatmasi o'ylashni qisqartirmaydi — model uni deyarli butunlay o'chiradi
(birinchi chaqiruvda think ≤ 5 token: B'da 28/31, C'da 29/31). Natijada asbob chaqirilmaydi
(sana "77 kun", tarixiy faktlar xato, tuzoq savolda tekshirilmagan), C'da esa 3 qadamli shablon javob matniga chiqib qoladi.
**A qoldirildi.** Tezlik filtr chegaralari orqali olinadi (`filters/filter_tezlik.py`: oddiy/o'zi haqida savol — 32 token).

Ikkala variantda ham uchragan muammo: kod javoblarida o'zgaruvchi nomida apostrof (`fayl_yo'li`) — SyntaxError.
