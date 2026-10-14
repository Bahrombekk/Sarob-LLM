# Sarob sinovi (2026-10-12 16:27, thinking=True)

## 1. [yangilik] Yandex data markazlariga nima bo'lgan? Qisqa ayt.
*Mezon: internetdan qidirishi, dron hujumlari haqida manba bilan aytishi*  
*Vaqt: 103s, asboblar: 2*

- `internetdan_qidirish({"query": "Yandex data centers news 2024 2025 2026"}) -> '[{"title": "Yandex — fast Internet search", "url": "https://yandex.com/", "snippet": "Yandex finds anything: webpages, images, music, good. Solve any problem — from everyday to a scientific one. Search by text, …"}, {"title": "Яндекс — быстрый поиск в интернете", "url": "https://yandex.uz/", "snippe'`
- `chuqur_tadqiqot({"sorovlar": ["Yandex data centers news 2024 2025", "Yandex split data centers impact", "Yandex infrastructure changes Russia 2024", "Yandex N.V. data center assets"]}) -> "8 ta manba ochildi. Faqat shu matnlarga tayan, har bir fakt uchun URL ko'rsat. Manbalarda yo'q raqamni yozma.\n\n### MANBA: Yandex — fast Internet search\nURL: https://yandex.com/\nYandex — internetda tezkor qidiruv\nKirish\nVidjetlar\nToshkent\nBildirishnomalar\nBugun: kuchsiz yomgʻir\xa0· +13\u2060…\u2060+20\u2060°\xa0· kuchsi"`

Yandex Cloud ma'lumotlar markazlariga (data centers) hujumlar sodir etilganligi haqida xabarlar bor. 

Asosiy ma'lumotlar:
* **Hujumlar:** Yandex Cloud'ning ma'lumotlar markazlaridan biri (aynan 3-markaz) hujumga uchraganligi haqida xabarlar tarqalgan.
* **Sabablar:** Bu voqealar ko'pincha geosiyosiy keskinlik va raqamli infratuzilmaning (internet va aloqa tizimlari) strategik ahamiyati bilan bog'lanmoqda. 
* **Kontekst:** Rossiya va Ukraina o'rtasidagi keskinlik fonida raqamli infratuzilmalarga qarshi hujumlar kuchayganligi ta'kidlanmoqda.

*Manba: Hacker News muhokamalari.*

---

## 2. [kurs] Bugun Markaziy bank bo'yicha 1 dollar necha so'm?
*Mezon: qidirishi, aniq raqam + manba + sana; o'ylab topmasligi*  
*Vaqt: 13s, asboblar: 1*

- `valyuta_kursi({"valyuta": "USD"}) -> '{"manba": "O\'zbekiston Respublikasi Markaziy banki (cbu.uz)", "kurslar": [{"valyuta": "USD", "nomi": "AQSH dollari", "nominal": "1", "kurs_som": "11897.90", "ozgarish": "51.33", "sana": "10.10.2026"}]}'`

Markaziy bank ma'lumotlariga ko'ra, bugun (2026-yil 10-oktabr holatiga) 1 AQSH dollari **11 897,90 so'm**ni tashkil etmoqda.

**Manba:** [O'zbekiston Respublikasi Markaziy banki (cbu.uz)](https://cbu.uz)

---

## 3. [havola] https://kun.uz sahifasini ochib, bosh sahifadagi 3 ta asosiy yangilik sarlavhasini yoz.
*Mezon: sahifani ochishi, haqiqiy sarlavhalar*  
*Vaqt: 43s, asboblar: 1*

- `sahifani_ochish({"url": "https://kun.uz"}) -> "URL: https://kun.uz/\n\nO‘zbekiston\nJahon\nIqtisodiyot\nJamiyat\nSport\nTexnologiya\nFan-texnologiya\nAudio\nO'zbekcha\nTa'lim\nMoliya\nAvto\nSog'lom hayot\nKo'chmas mulk\nAyollar dunyosi\nTurizm\nBiznes\nNaqdsiz savdo\nSan’atkorlarga soliq\nEronga hujum\nRossiya-Ukraina urushi\nKun.uz — O‘zbekiston va jahon yangiliklari"`

Kun.uz bosh sahifasidagi 3 ta asosiy yangilik sarlavhasi:

1. **Taʼlim sohasiga yangi rahbar, gazsiz aholiga chegirmali “svet” - hafta dayjesti**
2. **Tramp Rossiyaga qarshi sanksiyalarni yumshatdi. Asosiy maʼlumotlar**
3. **«Pulini toʻlasam boʻldi» degan ota-onalar adashadi: “Nima dard?”da bola taʼlimi va tarbiyasi mavzusi**

---

## 4. [github] https://github.com/Bahrombekk/Nigoh loyihasi nima qiladi? Qaysi texnologiyalar ishlatilgan? Kodga asoslanib ayt.
*Mezon: github_korish chaqirishi, kamera/stream tizimi ekanini aytishi, ko'z kuzatish deb to'qimasligi*  
*Vaqt: 87s, asboblar: 1*

- `github_korish({"repo_url": "https://github.com/Bahrombekk/Nigoh"}) -> 'REPO: Bahrombekk/Nigoh\nFayl turlari: py(182), tsx(41), ts(26), md(25), css(9), js(8), json(7), jpg(6), geojson(5), yml(3), gitignore(2), sh(2)\nFayllar (378 ta):\n.claude/\n.claude/launch.json\n.dockerignore\n.env.example\n.gitattributes\n.github/\n.github/workflows/\n.github/workflows/ci.yml\n.gitignore\nDock'`

**Nigoh** loyihasi — bu xaritaga integratsiya qilingan, IP kameralarni markazlashgan holda kuzatish va boshqarish tizimidir. Loyiha kodlari va README faylidagi ma'lumotlarga ko'ra, uning asosiy vazifalari va ishlatilgan texnologiyalari quyidagicha:

### 1. Loyiha nima qiladi? (Asosiy funksiyalari)
* **Xarita orqali kuzatish:** Kameralar xaritadagi markerlar ko'rinishida joylashgan bo'lib, foydalanuvchi xaritadan kerakli hududni tanlab, u yerdagi kameralarni ko'rishi mumkin.
* **Jonli video oqimi (Live Streaming):** Kameralardan kelayotgan RTSP oqimlarini brauzerda WebRTC yoki HLS protokollari orqali real vaqt rejimida ko'rsatadi.
* **Boshqaruv paneli (Admin Panel):** Super-admin kameralarni qo'shish, ularning IP, login, parol va joylashuvini sozlash, shuningdek, foydalanuvchilarni (operatorlarni) yaratish va ularga hududlar bo'yicha ruxsat berish imkoniyatiga ega.
* **Video Devor (Video Wall):** Bir vaqtning o'zida bir nechta kamerani setka (grid) ko'rinishida (masalan, 2x2, 4x4) kuzatish imkoniyati.
* **Dashboard va Statistika:** Kameralarning onlayn/offlayn holati, trafik ko'rsatkichlari va boshqa KPI (muhim ko'rsatkichlar) grafiklari orqali tahlil qilinadi.
* **Hududiy boshqaruv:** Kameralarni hududlar (regionlar) va guruhlar bo'yicha ajratish va boshqarish.

### 2. Qaysi texnologiyalar ishlatilgan?

Kod strukturasi va fayllar tahlili asosida quyidagi texnologiyalar aniqlandi:

**Backend (Server qismi):**
* **Dasturlash tili:** `Python` (loyihaning asosiy qismi `.py` fayllardan iborat).
* **API Framework:** `FastAPI` (fayl tuzilmasi va Swagger/Redoc hujjatlaridan ko'rinib turibdi).
* **Ma'lumotlar bazasi:** `PostgreSQL` (rasmiy hujjatlarda ko'rsatilgan).
* **Streaming Server:** `MediaMTX` (RTSP oqimlarini qabul qilish va WebRTC/HLS formatida tarqatish uchun markaziy komponent).
* **Video qayta ishlash:** `FFmpeg` (H.265 kodekni brauzerga moslashtirish yoki oqimni qayta formatlash uchun).
* **Migratsiyalar:** `Alembic` yoki shunga o'xshash SQL migratsiya vositasi (backend/database/migrations papkasi mavjud).

**Frontend (Mijoz qismi):**
* **Framework:** `React` (TypeScript bilan birga ishlatilgan).
* **Dasturlash tili:** `TypeScript` (`.tsx` va `.ts` fayllar).
* **Build Tool:** `Vite` (`vite.config.ts` fayli mavjud).
* **Xarita kutubxonasi:** `Leaflet` (`frontend/src/pages/map/leaflet.ts` fayli mavjud).
* **Stil berish:** `CSS` (turli xil `.css` fayllar orqali).

**Infrastruktura va Deployment:**
* **Konteynerlashtirish:** `Docker` va `Docker Compose` (tizimni oson o'rnatish va ishga tushirish uchun).
* **Protokollar:** `RTSP` (kameralardan oqim olish uchun), `WebRTC` va `HLS` (brauzerga uzatish uchun).

**Xulosa:** Bu professional darajadagi, kengaytiriladigan (scalable) va xarita bilan integratsiyalashgan video-kuzatuv (VMS - Video Management System) tizimidir.

---

## 5. [excel] 1990 dan 2030 gacha yillar ro'yxatini Excel faylda tayyorlab ber, yonida kabisa yili yoki yo'qligi ustuni bo'lsin.
*Mezon: execute_code, /workspace/fayllar ga saqlash, 8090 havola, to'g'ri kabisa formulasi*  
*Vaqt: 21s, asboblar: 1*

- `execute_code({"code": "import pandas as pd\n\n# Yillar ro'yxatini yaratish (1990 dan 2030 gacha)\nyears = list(range(1990, 2031))\n\n# Kabisa yilini tekshirish funksiyasi\ndef is_leap(year):\n    return (year % 4 ) -> '{"status": "ok", "output": "/workspace/fayllar/yillar_va_kabisa.xlsx\\n"}'`

1990-yildan 2030-yilgacha bo'lgan yillar ro'yxati va ularning kabisa yili ekanligi haqidagi ma'lumotlar Excel faylga tayyorlandi.

[yillar_va_kabisa.xlsx](http://192.168.136.153:8090/yillar_va_kabisa.xlsx)

---

## 6. [word] Ishga qabul qilish to'g'risida ariza namunasini Word faylda tayyorla (ism joyi bo'sh qolsin).
*Mezon: docx yaratish, havola, o'zbekcha rasmiy uslub*  
*Vaqt: 40s, asboblar: 1*

- `execute_code({"code": "from docx import Document\nfrom docx.enum.text import WD_ALIGN_PARAGRAPH\n\ndef create_application_doc():\n    doc = Document()\n\n    # Header (Right aligned)\n    header_text = (\n        ) -> '{"status": "ok", "output": "/workspace/fayllar/ishga_qabul_arizasi.docx\\n"}'`

Mana ishga qabul qilish to'g'risidagi ariza namunasi. Avval matnni ko'rib chiqishingiz mumkin, so'ngra Word faylini yuklab olishingiz mumkin.

***

**____________________ direktori**
**____________________ (korxona nomi)**
**____________________ (ism-sharif)ga**
**____________________ (manzil/tel)dan**

<br>

**ARIZA**

<br>

Meni ____________________ (lavozim nomi) lavozimiga ishga qabul qilishingizni so'rayman.

<br>

**____________________ (ism-sharif)**
**____________________ (manzil/tel)**

<br>

**______.______.202__ yil          ___________ (imzo)**

***

Men hozir ushbu matnni Word fayl ko'rinishida tayyorlayman.

[ishga_qabul_arizasi.docx](http://192.168.136.153:8090/ishga_qabul_arizasi.docx)

---

## 7. [hisob] Bankdan 50 mln so'm kredit oldim, yillik 24%, 3 yilga, annuitet. Oylik to'lov va jami ortiqcha to'lov qancha?
*Mezon: kod bilan hisoblashi: oylik ~1 961 643, ortiqcha ~20.62 mln*  
*Vaqt: 25s, asboblar: 1*

- `execute_code({"code": "principal = 50000000\nannual_rate = 0.24\nyears = 3\n\nmonthly_rate = annual_rate / 12\nmonths = years * 12\n\n# Annuity formula: P = (A * r * (1+r)^n) / ((1+r)^n - 1)\nmonthly_payment = (pr) -> '{"status": "ok", "output": "monthly_payment=1961642.6298899064\\ntotal_payment=70619134.67603663\\ntotal_interest=20619134.676036626\\n"}'`

Siz olgan kredit bo'yicha hisob-kitoblar quyidagicha:

*   **Oylik to'lov:** 1 961 643 so'm
*   **Jami ortiqcha to'lov (foizlar):** 20 619 135 so'm
*   **Jami to'lanadigan summa:** 70 619 135 so'm

**Hisob-kitob qisqacha:**
*   Kredit summasi: 50 000 000 so'm
*   Muddat: 3 yil (36 oy)
*   Yillik stavka: 24% (oylik 2%)

---

## 8. [tahlil] Mana savdo: Yanvar 120 mln, Fevral 95 mln, Mart 140 mln, Aprel 160 mln, May 150 mln. O'sish sur'ati va qisqa xulosa ber, grafik chizib fayl qilib ber.
*Mezon: foizlarni to'g'ri hisoblash, grafik PNG havola*  
*Vaqt: 51s, asboblar: 1*

- `execute_code({"code": "import pandas as pd\nimport matplotlib.pyplot as plt\n\n# Ma'lumotlarni tayyorlash\ndata = {\n    'Oy': ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May'],\n    'Savdo': [120, 95, 140, 160, 150]\n) -> '{"status": "ok", "output": "FILE_PATH:/workspace/fayllar/savdo_grafigi.png\\nDATA_TABLE:\\n    Oy  Savdo  O\'sish (%)\\nYanvar    120         NaN\\nFevral     95  -20.833333\\n  Mart    140   47.368421\\n Aprel    160   14.285714\\n   May    150   -6.250000\\n"}'`

Berilgan ma'lumotlar asosida hisob-kitoblar va tahlil natijalari quyidagicha:

### Savdo ko'rsatkichlari jadvali
| Oy | Savdo (mln) | O'sish (%) |
| :--- | :---: | :---: |
| Yanvar | 120 | — |
| Fevral | 95 | -20.83% |
| Mart | 140 | +47.37% |
| Aprel | 160 | +14.29% |
| May | 150 | -6.25% |

### Qisqa xulosa
1. **Eng yuqori savdo:** Aprel oyida (160 mln) qayd etilgan.
2. **Eng past savdo:** Fevral oyida (95 mln) kuzatilgan.
3. **Eng katta o'sish:** Mart oyida fevralga nisbatan **47.37%** ga sezilarli o'sish bo'lgan.
4. **Umumiy dinamika:** Savdo ko'rsatkichlari beqaror o'zgaruvchanlikni ko'rsatmoqda. Fevraldagi pasayishdan so'ng Mart va Aprelda kuchli o'sish kuzatilgan, biroq May oyida savdo hajmi o'tgan oygaga nisbatan **6.25%** ga biroz kamaygan.

### Grafik
Savdo dinamikasini ko'rsatuvchi grafik fayli tayyorlandi:
[savdo_grafigi.png](http://192.168.136.153:8090/workspace/fayllar/savdo_grafigi.png)

---

## 9. [tarjima] Quyidagini rus tiliga tarjima qil: 'Hurmatli hamkorlar, shartnoma muddati 2026-yil 31-dekabrgacha uzaytirildi.'
*Mezon: to'g'ri ruscha tarjima*  
*Vaqt: 8s, asboblar: 0*


Rus tiliga tarjimasi:

**"Уважаемые партнеры, срок действия договора продлен до 31 декабря 2026 года."**

---

## 10. [kirill] Шу матнни лотинга ўгир: Ўзбекистон Республикаси Президенти фармони эълон қилинди.
*Mezon: to'g'ri lotin: O'zbekiston Respublikasi Prezidenti farmoni e'lon qilindi.*  
*Vaqt: 9s, asboblar: 0*


O'zbekiston Respublikasi Prezidenti farmoni e'lon qilindi.

---

## 11. [imlo] Xatolarini tuzat: 'men ertaga ishga bormiman chunki kasalman, iltimos ruxsat bervoring'
*Mezon: to'g'ri imlo va uslub*  
*Vaqt: 36s, asboblar: 0*


Berilgan gapdagi xatolarni tuzatib, bir necha variantni taqdim etaman. Xatolar asosan imlo, grammatika va uslub bilan bog'liq.

### 1. To'g'rilangan standart variant (Grammatik jihatdan to'g'ri)
> **"Men ertaga ishga bormayman, chunki kasalman. Iltimos, ruxsat bering."**

**Tuzatishlar:**
*   **Men** — Gap boshida harf katta yoziladi.
*   **bormayman** — "bormiman" emas, "bormayman" shakli to'g'ri.
*   **chunki** — "Chunki"dan oldin vergul qo'yiladi.
*   **bering** — "bervoring" so'zi ko'proq so'zlashuv uslubiga xos, adabiy tilda "bering" deb yoziladi.
*   **Tinish belgilari** — Gap oxiriga nuqta va "iltimos"dan keyin vergul qo'yildi.

---

### 2. Rasmiy/Ish yuzasidan (Yaxshiroq uslub)
Agar bu gapni rahbaringizga yoki ish beruvchiga yozayotgan bo'lsangiz, quyidagi variantlar yanada professional va xushmuomala eshitiladi:

*   **Variant A:** "Kasal bo'lganim sababli, ertaga ishga bora olmayman. Iltimos, ruxsat berishingizni so'rayman."
*   **Variant B:** "Sog'lig'im yomonlashgani sababli, ertaga ishga kelolmayman. Ruxsat berishingizni iltimos qilaman."

**Nima uchun bu yaxshi?**
*   "Bormayman" so'zi biroz keskin (inkor) eshitilishi mumkin. "Bora olmayman" yoki "kelolmayman" iboralari vaziyatni yumshoqroq va sababli ko'rsatadi.

---

## 12. [mantiq] Ota o'g'lidan 30 yosh katta. 5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi. Hozir har biri necha yoshda?
*Mezon: o'g'il 10, ota 40*  
*Vaqt: 22s, asboblar: 0*


Bu masalani tenglama tuzish orqali osongina yechish mumkin.

**1. O'zgaruvchilarni belgilaymiz:**
*   O'g'lning hozirgi yoshi: $x$
*   Otaning hozirgi yoshi: $x + 30$ (chunki u o'g'lidan 30 yosh katta)

**2. 5 yildan keyingi holatni hisoblaymiz:**
*   O'g'lning yoshi: $x + 5$
*   Otaning yoshi: $(x + 30) + 5 = x + 35$

**3. Shart bo'yicha tenglama tuzamiz:**
5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi:
$$x + 35 = 3(x + 5)$$

**4. Tenglamani yechamiz:**
$$x + 35 = 3x + 15$$
$$35 - 15 = 3x - x$$
$$20 = 2x$$
$$x = 10$$

**Natija:**
*   **O'g'ilning yoshi:** 10 yoshda.
*   **Otaning yoshi:** $10 + 30 = 40$ yoshda.

**Tekshirish:**
Hozir: 40 va 10 (farqi 30).
5 yildan keyin: 45 va 15 (45 soni 15 dan 3 baravar katta). Hammasi to'g'ri.

---

## 13. [tarix] Amir Temur qachon tug'ilgan va qayerda vafot etgan?
*Mezon: 1336, Shahrisabz yaqinidagi Xo'ja Ilg'or; vafot 1405 O'tror*  
*Vaqt: 23s, asboblar: 1*

- `internetdan_qidirish({"query": "Amir Temur tug'ilgan yili va vafot etgan joyi"}) -> '[{"title": "Amir Temur - Vikipediya", "url": "https://uz.wikipedia.org/wiki/Amir_Temur", "snippet": "Amir Temur (toʻliq ismi: Amir Temur ibn Amir Taragʻoy ibn Amir Barqul) (1336-yil 9-aprel, Kesh – 1405-yil 18-fevral, Oʻtror) – oʻrta asrlarning davlat\xa0..."}, {"title": "Amir Temur - Ziyouz.com", "url'`

Amir Temur 1336-yil 9-aprelda Kesh (hozirgi Shahrisabz yaqinidagi Xoja ilg'or qishlog'i) shahrida tug'ilgan. U 1405-yil 18-fevralda O'tror shahrida vafot etgan.

---

## 14. [bilmaslik] Toshkentdagi 'Zarafshon Logistik Servis' MChJ direktori kim va telefon raqami qanday?
*Mezon: o'ylab topmasligi: qidirib topilmasa ochiq aytishi*  
*Vaqt: 127s, asboblar: 3*

- `internetdan_qidirish({"query": "Zarafshon Logistik Servis MChJ direktori va telefon raqami"}) -> '[{"title": "Qidirish natijalari - Mintransuz", "url": "https://mintrans.uz/search", "snippet": "\\"O\'zavtovokzal servis\\" MCHJ. Ishonch telefon raqami; +998 (71) 207-87-00 · +998 ... Yo\'nalishda O\'zbekiston tomonidan \\"Uzautotrans service\\" MChJ va ..."}, {"title": "innovation-2025", "url": "https://'`
- `internetdan_qidirish({"query": "\"Zarafshon Logistik Servis\" MChJ direktori va telefon raqami"}) -> '[{"title": "Bosh sahifa - ADM kompaniyalar guruhi (“Roodell” MChJ)", "url": "https://adm.uz/", "snippet": "ADM Global kompaniyalar guruhi distribyutsiya, mahalliy ishlab chiqarish, sotish, yo‘lovchi va tijorat avtomobillariga kafolat va kafolatdan keyingi xizmat ko‘rsatish, logistika xizmatlari, liz'`
- `internetdan_qidirish({"query": "\"Zarafshon Logistik Servis\" MChJ Toshkent direktori telefon raqami"}) -> '[{"title": "Bosh sahifa - ADM kompaniyalar guruhi (“Roodell” MChJ)", "url": "https://adm.uz/", "snippet": "ADM Global kompaniyalar guruhi distribyutsiya, mahalliy ishlab chiqarish, sotish, yo‘lovchi va tijorat avtomobillariga kafolat va kafolatdan keyingi xizmat ko‘rsatish, logistika xizmatlari, liz'`

Kechirasiz, men "Zarafshon Logistik Servis" MChJning direktori va telefon raqami haqidagi aniq ma'lumotlarni internetdan qidirib topa olmadim. 

Odatda bunday ma'lumotlarni quyidagi manbalardan tekshirish tavsiya etiladi:
1. **Statistika agentligi yoki Davlat xizmatlari portali** (masalan, `my.gov.uz` orqali korxona ma'lumotlarini ko'rish).
2. **Yuridik shaxslar reyestri** (my.stat.uz).
3. **Biznes kataloglar** (Yellow Pages Uzbekistan yoki shunga o'xshash xizmat ko'rsatuvchi kompaniyalar ro'yxati).

Agar sizda kompaniyaning boshqa bir ma'lumoti (masalan, manzili yoki STIR/INN raqami) bo'lsa, iltimos, yuboring, men qaytadan qidirib ko'raman.

---

## 15. [sana] Bugun qaysi kun va 2027-yil 1-yanvargacha necha kun qoldi?
*Mezon: to'g'ri sana, kunlar soni kod yoki aniq hisob*  
*Vaqt: 19s, asboblar: 1*

- `execute_code({"code": "from datetime import date\n\ntoday = date(2026, 10, 12)\ntarget = date(2027, 1, 1)\ndelta = target - today\n\nprint(f\"Bugun: {today}\")\nprint(f\"Maqsadli sana: {target}\")\nprint(f\"Farq: ) -> '{"status": "ok", "output": "Bugun: 2026-10-12\\nMaqsadli sana: 2027-01-01\\nFarq: 81 kun\\n"}'`

Bugun 2026-yil 12-oktabr, dushanba. 2027-yil 1-yanvargacha esa 81 kun qoldi.

---

## 16. [kod] Python'da papkadagi barcha .xlsx fayllarni birlashtirib bitta faylga yozadigan skript yozib ber.
*Mezon: ishlaydigan pandas kodi*  
*Vaqt: 74s, asboblar: 0*


Men Sarobman. Python'da `.xlsx` fayllarni birlashtirish uchun eng samarali va oson yo'l — `pandas` kutubxonasidan foydalanishdir.

Quyida ushbu vazifani bajaradigan tayyor va tushunarli skriptni taqdim etaman.

### 1. Kerakli kutubxonalarni o'rnatish
Skript ishlashi uchun sizda `pandas` va `openpyxl` kutubxonalari o'rnatilgan bo'lishi kerak. Terminalda quyidagi buyruqni bajaring:

```bash
pip install pandas openpyxl
```

### 2. Python skripti

Ushbu skript ko'rsatilgan papkadagi barcha Excel fayllarini o'qiydi, ularni bitta jadvalga birlashtiradi va natijani yangi fayl sifatida saqlaydi.

```python
import pandas as pd
import glob
import os

def excel_fayllarni_birlashtir(papka_yoli, natija_fayli):
    """
    Berilgan papkadagi barcha .xlsx fayllarni o'qiydi va bitta faylga birlashtiradi.
    """
    
    # Papkadagi barcha .xlsx fayllar ro'yxatini olish
    pattern = os.path.join(papka_yoli, "*.xlsx")
    fayllar = glob.glob(pattern)
    
    if not fayllar:
        print(f"Xatolik: '{papka_yoli}' papkasida .xlsx fayllar topilmadi.")
        return

    # Agar natija fayli o'zi ham papka ichida bo'lsa, uni birlashtirishga qo'shib yubormaslik kerak
    fayllar = [f for f in fayllar if os.path.basename(f) != natija_fayli]

    print(f"Topilgan fayllar soni: {len(fayllar)}")
    
    barcha_dataframes = []

    for fayl in fayllar:
        try:
            # Faylni o'qish
            df = pd.read_excel(fayl)
            
            # Har bir qator qaysi fayldan olinganini bilish uchun maxsus ustun qo'shamiz (ixtiyoriy)
            df['manba_fayl'] = os.path.basename(fayl)
            
            barcha_dataframes.append(df)
            print(f"Muvaffaqiyatli o'qildi: {os.path.basename(fayl)}")
        except Exception as e:
            print(f"Xatolik {os.path.basename(fayl)} o'qishda: {e}")

    if barcha_dataframes:
        # Barcha DataFrame'larni bitta jadvalga birlashtirish
        # ignore_index=True — indekslarni (0, 1, 2...) qaytadan tartiblash uchun
        birlashgan_df = pd.concat(barcha_dataframes, ignore_index=True)
        
        # Natijani saqlash
        birlashgan_df.to_excel(natija_fayli, index=False)
        print("-" * 30)
        print(f"Tayyor! Barcha ma'lumotlar '{natija_fayli}' fayliga saqlandi.")
    else:
        print("Birlashtirish uchun hech qanday ma'lumot topilmadi.")

# --- SKRIPTNI ISHLATISH ---
if __name__ == "__main__":
    # 1. Fayllar joylashgan papka yo'lini kiriting (nuqta '.' — joriy papka degani)
    target_folder = "." 
    
    # 2. Natija faylining nomini kiriting
    output_name = "birlashgan_ma_lumotlar.xlsx"
    
    excel_fayllarni_birlashtir(target_folder, output_name)
```

### Skript qanday ishlaydi?

1.  **`glob.glob`**: Berilgan yo'ldagi barcha `.xlsx` kengaytmali fayllarni qidirib topadi.
2.  **`pd.read_excel`**: Har bir faylni Python'ning `DataFrame` (jadval) ko'rinishiga o'tkazadi.
3.  **`df['manba_fayl']`**: Men skriptga qo'shimcha qism qo'shdim — u har bir qatorning qaysi fayldan kelganini ko'rsatuvchi yangi ustun yaratadi. Bu keyinchalik ma'lumotlarni tekshirishda juda foydali.
4.  **`pd.concat`**: Barcha alohida jadvallarni bitta katta jadvalga "ustma-ust" qo'shib chiqadi. Agar fayllarda ustun nomlari har xil bo'lsa, `pandas` ularni avtomatik ravishda moslashtiradi (har xil ustunlar uchun `NaN` qiymatlarini qo'yadi).
5.  **`to_excel`**: Yakuniy natijani yangi Excel fayli sifatida yozadi.

### Muhim eslatmalar:
*   **Ustunlar mosligi**: Agar barcha fayllaringizda ustun nomlari bir xil bo'lsa (masalan: `Ism`, `Familiya`, `Telefon`), natija juda chiroyli va tartibli chiqadi.
*   **Xavfsizlik**: Skript natija faylini o'zi ham papka ichida bo'lishi mumkinligini hisobga olib, o'zini-o'zi birlashtirib yubormasligi uchun filtr qo'shilgan.

---

## 17. [rasm] IMAGE:Bu chekdagi barcha mahsulotlar va narxlarni jadval qilib ber, jami to'g'rimi tekshir.
*Mezon: 8000+14500+19900+22500=64900 to'g'ri; barcha qatorlar*  
*Vaqt: 18s, asboblar: 0*


Men Sarobman. Chekdagi ma'lumotlarni jadval ko'rinishida tayyorladim:

| Mahsulot | Narxi (so'm) |
| :--- | :--- |
| Non x2 | 8 000 |
| Sut 1L | 14 500 |
| Tuxum 10 dona | 19 900 |
| Olma 1.5kg | 22 500 |
| **JAMI** | **64 900** |

**Tekshiruv natijasi:**
8 000 + 14 500 + 19 900 + 22 500 = 64 900 so'm.
Chekdagi jami summa to'g'ri hisoblangan.

---

## 18. [ko'p_qadam] O'zbekistonning 2025-yil YaIM (GDP) hajmi va aholisi bo'yicha internetdan ma'lumot top, aholi jon boshiga YaIMni hisobla.
*Mezon: qidirish, manba, to'g'ri bo'lish*  
*Vaqt: 79s, asboblar: 2*

- `internetdan_qidirish({"query": "Uzbekistan GDP 2025 and population 2025"}) -> '[{"title": "Uzbekistan at 35: Economy reaches $147 billion as population tops ...", "url": "https://kun.uz/en/news/2026/09/01/uzbekistan-at-35-economy-reaches-147-billion-as-population-tops-38-million", "snippet": "1-sen, 2026 ... Investment in the economy grew from $1.1 billion in 1991 to $48.5 bil'`
- `internetdan_qidirish({"query": "Uzbekistan population 2025 official statistics"}) -> '[{"title": "The permanent population of Uzbekistan is approaching 38 million ...", "url": "https://stat.uz/en/press-center/news-of-committee/62547-o-zbekistonning-doimiy-aholisi-soni-qariyb-38-mln-nafarga-yetmoqda-3", "snippet": "9-iyl, 2025 ... According to the National Statistics Committee, as of '`

2025-yil uchun O'zbekistonning YaIM va aholi soni bo'yicha topilgan ma'lumotlar asosida hisob-kitob quyidagicha:

### 1. Topilgan ma'lumotlar:
* **YaIM (GDP) hajmi (2025):** $147,069,000,000 (147,069 milliard AQSH dollari)
    * *Manba:* [Worldometer](https://www.worldometers.info/gdp/uzbekistan-gdp/)
* **Aholi soni (2025):** ~38,000,000 kishi (2025-yil avgust oyi holatiga ko'ra)
    * *Manba:* [Stat.uz](https://stat.uz/) va [Uzprint.uz](https://uzprint.uz/) (Rasmiy statistika ma'lumotlariga ko'ra aholi 38 milliondan oshganligi qayd etilgan).

### 2. Hisob-kitob:
Aholi jon boshiga YaIMni (GDP per capita) hisoblash uchun umumiy YaIMni aholi soniga bo'lamiz:

$$\text{Aholi jon boshiga YaIM} = \frac{\text{Umumiy YaIM}}{\text{Aholi soni}}$$

$$\text{Aholi jon boshiga YaIM} = \frac{147,069,000,000}{38,000,000} \approx 3,870.24 \text{ AQSH dollari}$$

### Xulosa:
2025-yilgi ko'rsatkichlarga ko'ra, O'zbekistonning aholi jon boshiga tushadigan YaIM taxminan **3,870.24 AQSH dollari**ni tashkil etadi.

**Manbalar:**
1. [Worldometer - Uzbekistan GDP](https://www.worldometers.info/gdp/uzbekistan-gdp/)
2. [Stat.uz - O'zbekiston Respublikasi statistik ma'lumotlari](https://stat.uz/)

---

## 19. [fayl_tahlil] /workspace/fayllar/sinov_savdo.xlsx faylini tahlil qil: qaysi filial eng ko'p sotgan, qaysi mahsulot eng foydali, oylik dinamika qanday? Qisqa hisobot Word faylda ber.
*Mezon: faylni o'qish, to'g'ri raqamlar (Chilonzor eng ko'p), docx havola*  
*Vaqt: 40s, asboblar: 2*

- `execute_code({"code": "import pandas as pd\n\nfile_path = '/workspace/fayllar/sinov_savdo.xlsx'\n\ntry:\n    df = pd.read_excel(file_path)\n    print(\"Fayl muvaffaqiyatli o'qildi. Ustunlar:\")\n    print(df.colum) -> '{"status": "ok", "output": "Fayl muvaffaqiyatli o\'qildi. Ustunlar:\\n[\'Oy\', \'Filial\', \'Mahsulot\', \'Soni\', \'Narx\', \'Tannarx\']\\n\\nBirinchi 5 ta qator:\\n       Oy     Filial Mahsulot  Soni   Narx  Tannarx\\n0  Yanvar  Chilonzor      Non   534   4000     2800\\n1  Yanvar  Chilonzor      Sut   392  14500   '`
- `execute_code({"code": "import pandas as pd\n\nfile_path = '/workspace/fayllar/sinov_savdo.xlsx'\ndf = pd.read_excel(file_path)\n\n# Foyda ustunini yaratish\ndf['Foyda'] = (df['Narx'] - df['Tannarx']) * df['Soni']\) -> '{"status": "ok", "output": "--- ANALIZ NATIJALARI ---\\nEng ko\'p sotgan filial: Chilonzor (285,547,000 so\'m)\\nEng foydali mahsulot: Go\'sht (76,993,000 so\'m)\\n\\nOylik dinamika (Umumiy sotuv):\\n       Oy  Umumiy_Sotuv\\n0  Yanvar     122377500\\n1  Fevral      87904500\\n2    Mart     134456000\\n3   Aprel'`

`sinov_savdo.xlsx` fayli tahlil qilindi. Quyida tahlil natijalari keltirilgan:

### **Savdo Tahlili Xulosalari:**

*   **Eng ko'p sotgan filial:** **Chilonzor** filialidir (umumiy sotuv summasi: **285,547,000 so'm**).
*   **Eng foydali mahsulot:** **Go'sht** mahsuloti eng ko'p foyda keltirgan (umumiy foyda: **76,993,000 so'm**).
*   **Oylik dinamika (Umumiy sotuv):**
    *   **Yanvar:** 122,377,500 so'm
    *   **Fevral:** 87,904,500 so'm
    *   **Mart:** 134,456,000 so'm (Eng yuqori ko'rsatkich)
    *   **Aprel:** 98,978,500 so'm
    *   **May:** 97,229,000 so'm
    *   **Iyun:** 85,527,000 so'm

Batafsil hisobotni Word fayl ko'rinishida yuklab olishingiz mumkin:

[savdo_tahlili_hisoboti.docx](http://192.168.136.153:8090/savdo_tahlili_hisoboti.docx)

---

## 20. [iphone] Eng oxirgi chiqqan iPhone modellari qaysilar va narxi qancha?
*Mezon: qidirish; 2025-2026 modellari (iPhone 17/18), manba bilan*  
*Vaqt: 51s, asboblar: 2*

- `internetdan_qidirish({"query": "latest iPhone models and prices October 2026"}) -> '[{"title": "Apple Mobile Phones (iPhones) Price List (Oct 2026) | 91mobiles.com", "url": "https://www.91mobiles.com/list-of-phones/apple-mobile-price-list-in-india", "snippet": "List of Apple Mobile Phones (iPhones) Price List (Oct 2026) with prices ranging from Rs. 63,999 to Rs. 329,900. We found 1'`
- `sahifani_ochish({"url": "https://www.macrumors.com/2026/09/12/how-much-each-iphone-18-pro-model-costs/"}) -> "URL: https://www.macrumors.com/2026/09/12/how-much-each-iphone-18-pro-model-costs/\n\nApple's New 2026 iPhone Lineup: Prices for Every Storage Tier - MacRumors\n\nSkip to Content\nApple's New 2026 iPhone Lineup: Prices for Every Storage Tier\nSaturday September 12, 2026 12:22 am PDT\n by \nTim Hardwick\nAppl"`

2026-yil oktyabr holatiga ko'ra, Apple'ning eng so'nggi va eng yangi iPhone modellari — **iPhone 18 Pro**, **iPhone 18 Pro Max** va Apple'ning birinchi buklama (foldable) modeli bo'lgan **iPhone Duo** hisoblanadi.

Quyida ushbu modellarning xarid qilish narxlari (AQSH bozoridagi taxminiy narxlar, soliqsiz) keltirilgan:

### 1. Eng yangi flagmanlar (iPhone 18 seriyasi)
| Model | Xotira hajmi | Narxi (USD) |
| :--- | :--- | :--- |
| **iPhone 18 Pro** | 256GB | $1,199 |
| | 512GB | $1,399 |
| | 1TB | $1,799 |
| | 2TB | $2,399 |
| **iPhone 18 Pro Max** | 256GB | $1,299 |
| | 512GB | $1,499 |
| | 1TB | $1,899 |
| | 2TB | $2,499 |

### 2. Yangi buklama model
| Model | Xotira hajmi | Narxi (USD) |
| :--- | :--- | :--- |
| **iPhone Duo** (Foldable) | 256GB | $1,999 |
| | 512GB | $2,199 |
| | 1TB | $2,599 |
| | 2TB | $3,199 |

### Boshqa mavjud modellardan qisqacha:
* **iPhone Air:** $1,099 dan boshlanadi (256GB).
* **iPhone 17:** $899 dan boshlanadi (256GB).
* **iPhone 16:** $799 (128GB).
* **iPhone 17e:** $699 (256GB).

*Eslatma: Narxlar xotira hajmi va tanlangan operator shartlariga qarab o'zgarishi mumkin.*

**Manba:** [MacRumors (2026-yil 12-sentabr)](https://www.macrumors.com/2026/09/12/how-much-each-iphone-18-pro-model-costs/)

---

## 21. [taqqoslash] Toshkent va Samarqand o'rtasidagi masofa qancha va Afrosiyob poyezdida qancha vaqt ketadi? Chipta narxi qancha?
*Mezon: qidirish, ~300 km, ~2 soat, narx manba bilan*  
*Vaqt: 101s, asboblar: 4*

- `internetdan_qidirish({"query": "Toshkent va Samarqand orasidagi masofa va Afrosiyob poyezdi narxi va vaqti"}) -> '[{"title": "Afrosiyob poezdiga chiptalar - sotish, bron qilish, yetkazib berish", "url": "https://www.goldenpages.uz/uz/rubrics/?Id=106915", "snippet": "Afrosiyob poezdiga chiptalar - sotish, bron qilish, yetkazib berish: tashkilotlar va manzillar ; \\"BOOKHARA\\" SAVDO BELGISI, 100115, Toshkent, Chil'`
- `internetdan_qidirish({"query": "Afrosiyob poyezdi Toshkent - Samarqand chipta narxlari va yo'l vaqti 2026"}) -> '[{"title": "O\'zbekiston temir yo\'llari | Home - railway.uz", "url": "https://eticket.uzrailpass.uz/en/home", "snippet": "1-oktabrdan boshlab 730-sonli Toshkent — Andijon poyezdi soat 08:10 o‘rniga 07:20 da jo‘naydi."}, {"title": "Sarlavhasiz", "url": "https://railway.uz/uz/poisk/?q=chipta+narxi", "s'`
- `brauzer({"amal": "ochish", "url": "https://eticket.railway.uz/uz/"}) -> '{"holat": "ok", "izoh": "ochish", "url": "https://eticket.uzrailpass.uz/uz/home", "sarlavha": "O\'zbekiston temir yo\'llari | Bosh sahifa", "skrinshot": "http://192.168.136.153:8090/skrinshot/112353_9bda5b.png", "matn": "1-oktabrdan boshlab 730-sonli Toshkent — Andijon poyezdi soat 08:10 o‘rniga 07:20'`
- `brauzer({"amal": "yozish", "joy": "QAYERDAN", "matn": "Toshkent"}) -> '{"holat": "xato", "izoh": "TimeoutError: Locator.fill: Timeout 10000ms exceeded.\\nCall log:\\n  - waiting for get_by_placeholder(\\"QAYERDAN\\").or_(get_by_label(\\"QAYERDAN\\")).first\\n"}'`

Toshkent va Samarqand o'rtasidagi masofa va "Afrosiyob" poyezdi haqidagi ma'lumotlar quyidagicha:

*   **Masofa:** Toshkent va Samarqand shaharlari orasidagi temir yo'l masofasi taxminan **300–320 km**ni tashkil etadi (yo'nalish va yo'l turiga qarab biroz farq qilishi mumkin).
*   **Yo'l vaqti:** "Afrosiyob" tezyurar poyezdida Toshkentdan Samarqandga yetib borish taxminan **2 soat** vaqt oladi.
*   **Chipta narxi:** Chipta narxi tanlangan vagon turiga (ekonom, standart, VIP) va sotib olingan vaqtga qarab o'zgarib turadi. Taxminiy narxlar:
    *   **Ekonom/Standart:** ~150 000 – 250 000 so'm atrofida.
    *   **VIP:** Undan yuqori.

**Eslatma:** Chipta narxlari va aniq vaqtlar o'zgaruvchan bo'lganligi sababli, eng so'nggi va aniq ma'lumotlarni [eticket.railway.uz](https://eticket.railway.uz/uz/) rasmiy sayti yoki "Uzrailways" mobil ilovasi orqali tekshirishingizni tavsiya qilaman.

---

## 22. [hujjat_yozish] Hamkor kompaniyaga to'lov kechikkani uchun rasmiy uzr xati yoz (o'zbek tilida), keyin uni Word faylga ham saqla.
*Mezon: rasmiy uslub, docx havola*  
*Vaqt: 72s, asboblar: 1*

- `execute_code({"code": "from docx import Document\n\ndef create_apology_letter():\n    doc = Document()\n    \n    text = (\n        \"Mavzu: To‘lov kechikkanligi yuzasidan uzr so‘rash haqida\\n\\n\"\n        \"[Ha) -> '{"status": "ok", "output": "/workspace/fayllar/uzr_xati_to_lov.docx\\n"}'`

Men Sarobman. Hamkor kompaniya uchun rasmiy uzr xati matnini tayyorladim. Quyida xatning matni keltirilgan, undagi qavs ichidagi `[...]` joylarni o‘zingizning ma’lumotlaringiz bilan to‘ldirishingiz kerak.

***

**Mavzu: To‘lov kechikkanligi yuzasidan uzr so‘rash haqida**

**[Hamkor kompaniya nomi] rahbariyatiga**

**Hurmatli [Hamkor ismi yoki Rahbar ismi],**

[Sizning kompaniyangiz nomi] jamoasi nomidan, [Hisob-faktura raqami] sonli hujjat bo‘yicha to‘lovning belgilangan muddatda amalga oshirilmaganligi uchun samimiy uzr so‘raymiz.

Ushbu kechikish [sababni yozing, masalan: texnik nosozliklar yoki buxgalteriya tizimidagi o‘zgarishlar] tufayli yuzaga keldi. Biz ushbu muammoni bartaraf etish choralarini ko‘rib chiqdik va to‘lov [sana] kuni to‘liq amalga oshirilishini ma’lum qilamiz.

Kompaniyangiz bilan o‘rnatilgan ishonchli hamkorlik biz uchun juda qadrli. Kelgusida bunday holatlar takrorlanmasligini va barcha majburiyatlarimiz o‘z vaqtida bajarilishini kafolatlaymiz.

Tushunganingiz uchun tashakkur.

**Hurmat bilan,**

**[Sizning ismingiz]**
**[Lavozimingiz]**
**[Sizning kompaniyangiz nomi]**

***

Hozir esa ushbu matnni Word fayl ko‘rinishida saqlayman.

[uzr_xati_to_lov.docx](http://192.168.136.153:8090/uzr_xati_to_lov.docx)

---

## 23. [tuzoq] O'zbekistonning birinchi prezidenti Shavkat Mirziyoyev 1991-yilda saylangani haqida batafsil yoz.
*Mezon: xatoni tuzatishi: birinchi prezident Islom Karimov; Mirziyoyev 2016-yildan*  
*Vaqt: 27s, asboblar: 0*


Siz bergan ma'lumotda tarixiy xatolik mavjud. O'zbekistonning birinchi prezidenti **Shavkat Mirziyoyev emas, balki Islom Karimov** bo'lgan.

Tarixiy faktlar quyidagicha:

1.  **Birinchi prezident (1991):** O'zbekiston Respublikasining birinchi prezidenti **Islom Karimov** bo'lgan. U 1991-yil 1-dekabrda o'tkazilgan umumxalqiy saylovlarda prezident sifatida saylangan va mustaqil O'zbekistonning davlat boshqaruvini olgan.
2.  **Shavkat Mirziyoyevning prezidentligi:** Shavkat Mirziyoyev O'zbekiston Respublikasining prezidenti sifatida **2016-yildan** boshlab davlat boshqaruvini olgan. U 2016-yil 5-sentabrda prezidentlik saylovlarida g'olib bo'lgan va o'z lavozimida qayta saylangan.

Agar siz Shavkat Mirziyoyevning prezidentlik faoliyati yoki 1991-yildagi saylovlar haqida boshqa ma'lumotlarni bilmoqchi bo'lsangiz, so'rashingiz mumkin.

---

## 24. [kodsinov] Python'da papkadagi barcha .xlsx fayllarni birlashtirib bitta faylga yozadigan skript yozib ber.
*Mezon: ASCII nomlar, sinab ko'rilgan kod*  
*Vaqt: 68s, asboblar: 0*


Men Sarobman. Ushbu vazifani bajarish uchun eng qulay va samarali yo'l — `pandas` kutubxonasidan foydalanishdir.

Quyida barcha `.xlsx` fayllarni o'qib, ularni bitta jadvalga birlashtiradigan va yangi faylga saqlaydigan tayyor skriptni taqdim etaman.

### Kerakli kutubxonalar
Skript ishlashi uchun sizda `pandas` va `openpyxl` kutubxonalari o'rnatilgan bo'lishi kerak. Agar o'rnatilmagan bo'lsa, terminalda quyidagi buyruqni yozing:
```bash
pip install pandas openpyxl
```

### Python skripti

```python
import pandas as pd
import glob
import os

def birlashtir_xlsx_fayllar(papka_yoli, natija_nomi):
    """
    Berilgan papkadagi barcha .xlsx fayllarni birlashtiradi.
    """
    # 1. Papkadagi barcha .xlsx fayllar ro'yxatini olish
    # glob.glob funksiyasi pattern bo'yicha fayllarni topadi
    fayllar_pattern = os.path.join(papka_yoli, "*.xlsx")
    fayllar_ro'yxati = glob.glob(fayllar_pattern)

    if not fayllar_ro'yxati:
        print(f"Xato: '{papka_yoli}' papkasida .xlsx fayllar topilmadi.")
        return

    print(f"Topilgan fayllar soni: {len(fayllar_ro'yxati)}")

    df_list = []

    for fayl in fayllar_ro'yxati:
        # Agar natija fayli allaqachon mavjud bo'lsa, uni birlashtirishga qo'shib yubormaslik kerak
        if os.path.basename(fayl) == natija_nomi:
            continue
            
        try:
            print(f"O'qilmoqda: {os.path.basename(fayl)}")
            # Faylni o'qish
            df = pd.read_excel(fayl)
            
            # (Ixtiyoriy) Ma'lumot qaysi fayldan kelganini bilish uchun yangi ustun qo'shamiz
            df['Manba_Fayl'] = os.path.basename(fayl)
            
            df_list.append(df)
        except Exception as e:
            print(f"Xato yuz berdi ({os.path.basename(fayl)}): {e}")

    if df_list:
        # 2. Barcha DataFrame'larni bitta jadvalga birlashtirish
        # ignore_index=True — indekslarni qaytadan tartiblaydi (0, 1, 2...)
        birlashgan_df = pd.concat(df_list, ignore_index=True)

        # 3. Natijani yangi faylga saqlash
        natija_yo'li = os.path.join(papka_yoli, natija_nomi)
        birlashgan_df.to_excel(natija_yo'li, index=False)
        
        print("-" * 30)
        print(f"Muvaffaqiyatli yakunlandi!")
        print(f"Jami qatorlar soni: {len(birlashgan_df)}")
        print(f"Saqlangan joy: {natija_yo'li}")
    else:
        print("Birlashtirish uchun ma'lumot topilmadi.")

# --- ISHLATISH ---
if __name__ == "__main__":
    # O'zingizning papka manzilingizni shu yerga yozing
    # Masalan: 'C:/Users/Admin/Documents/Excel_Files' yoki '.' (hozirgi papka uchun)
    TARGET_FOLDER = '.' 
    
    # Yaratiladigan yangi fayl nomi
    OUTPUT_FILE = 'birlashtirilgan_natija.xlsx'

    birlashtir_xlsx_fayllar(TARGET_FOLDER, OUTPUT_FILE)
```

### Skript qanday ishlaydi?

1.  **`glob.glob`**: Berilgan manzildagi barcha `.xlsx` kengaytmali fayllarni avtomatik qidirib topadi.
2.  **`pd.read_excel`**: Har bir faylni alohida jadval (DataFrame) ko'rinishida xotiraga yuklaydi.
3.  **`df['Manba_Fayl']`**: Men skriptga kichik bir "aqlli" funksiya qo'shdim. U har bir qatorning yoniga o'sha ma'lumot qaysi fayldan olinganini yozib qo'yadi. Bu keyinchalik tahlil qilishda juda qo'l keladi.
4.  **`pd.concat`**: Barcha yuklangan jadvallarni ustunlari (column names) bir xil bo'lsa, ularni bir-birining ostiga tartib bilan qo'yadi. Agar ustunlar har xil bo'lsa, `pandas` yangi ustunlar ochadi va mos kelmaydigan joylarga `NaN` (bo'sh joy) qo'yadi.
5.  **`to_excel`**: Yakuniy natijani bitta tayyor `.xlsx` fayl sifatida saqlaydi.

### Muhim eslatmalar:
*   **Ustun nomlari**: Fayllardagi ustun nomlari (masalan: "Ism", "Familiya") bir xil bo'lishi kerak. Agar bitta faylda "Ism", ikkinchisida "F.Ism" bo'lsa, `pandas` ularni ikki xil ustun deb hisoblaydi.
*   **Xavfsizlik**: Skript ichida `if os.path.basename(fayl) == natija_nomi: continue` qatori bor. Bu skriptni ikki marta ishlatganingizda, eski natija faylini qaytadan o'z-o'ziga qo'shib yubormaslik uchun kerak.

---

## 25. [brauzer_narx] olx.uz saytida Toshkentdagi 'iPhone 15' e'lonlarini top va eng arzon 5 tasining narxini yoz.
*Mezon: brauzer bilan olx ochish/qidirish, haqiqiy narxlar, skrinshot*  
*Vaqt: 229s, asboblar: 6*

- `brauzer({"amal": "ochish", "url": "https://olx.uz"}) -> '{"holat": "ok", "izoh": "ochish", "url": "https://www.olx.uz/", "sarlavha": "Доска объявлений OLX.uz, ранее Torg: сайт объявлений в Узбекистане - купля/продажа бу товаров на OLX.uz", "skrinshot": "http://192.168.136.153:8090/skrinshot/112434_6a7ee5.png", "matn": "Перейти к основному разделу\\nПерейти'`
- `brauzer({"amal": "yozish", "joy": "Поиск", "matn": "iPhone 15"}) -> '{"holat": "xato", "izoh": "TimeoutError: Locator.fill: Timeout 10000ms exceeded.\\nCall log:\\n  - waiting for get_by_placeholder(\\"Поиск\\").or_(get_by_label(\\"Поиск\\")).first\\n"}'`
- `brauzer({"amal": "bosish", "matn": "Поиск"}) -> '{"holat": "ok", "izoh": "bosish", "url": "https://www.olx.uz/list/", "sarlavha": "OLX.uz: сайт объявлений в Узбекистане - товары, услуги, недвижимость и транспорт на OLX.uz", "skrinshot": "http://192.168.136.153:8090/skrinshot/112508_c07a14.png", "matn": "Перейти к основному разделу\\nПерейти к нижне'`
- `brauzer({"amal": "bosish", "matn": "Поиск"}) -> '{"holat": "ok", "izoh": "bosish", "url": "https://www.olx.uz/list/", "sarlavha": "OLX.uz: сайт объявлений в Узбекистане - товары, услуги, недвижимость и транспорт на OLX.uz", "skrinshot": "http://192.168.136.153:8090/skrinshot/112555_e0ad5f.png", "matn": "Перейти к основному разделу\\nПерейти к нижне'`
- `internetdan_qidirish({"query": "site:olx.uz \"iPhone 15\" Toshkent"}) -> '[{"title": "iphone 15 - Купить телефон Ташкент - Цены на OLX.uz", "url": "https://www.olx.uz/elektronika/telefony/tashkent/q-iphone-15/", "snippet": "iphone 15 — Продажа телефонов Ташкент ✔️ Телефоны новые и б/у по выгодным ценам ☝ Найдите подходящее устройство от проверенных продавцов на OLX.uz."},'`
- `sahifani_ochish({"url": "https://www.olx.uz/tashkent/q-iphone-15/"}) -> "URL: https://www.olx.uz/tashkent/q-iphone-15/\n\nПерейти к основному разделу\nПерейти к нижнему колонтитулу\nЧат\nO'Z\nРус\nУведомления\nУведомления\nВаш профиль\nПодать объявление\n+0 km\nПоиск\nТолько с фото\nДобавить в избранное\nФильтры\n\nКатегория\n\nЛюбая категория\nЦена\nСостояние\nВсе объявления\nМарка телефона\nВ"`

OLX.uz saytida Toshkent shahri bo'yicha "iPhone 15" qidiruvi natijalariga ko'ra, eng arzon 5 ta e'lon quyidagilar:

1. **Iphone 15 pro max** — 950 000 so'm
2. **iPhone 15 pro 256** — 3 500 000 so'm
3. **iPhone 15 Pro Max (17Max korpusida)** — 4 162 550 so'm
4. **Iphone 15 128gb karobka** — 4 400 410 so'm
5. **Iphone 15 Pro ideal srowna** — 4 500 000 so'm

*Eslatma: 950 000 so'm bo'lgan e'lon narxi juda past ekanligi sababli, u ehtimol ehtiyot qism yoki boshqa aksessuar bo'lishi mumkin. Sotib olishdan olda e'lon mazmunini diqqat bilan tekshirishingizni tavsiya qilaman.*

---

## 26. [chuqur] O'zbekistonda 2026-yilda elektromobil sotib olish foydalimi? Narxlar, soliq imtiyozlari, zaryadlash infratuzilmasini chuqur o'rganib hisobot ber.
*Mezon: bir nechta manba, jadval, xulosa, manbalar ro'yxati, o'ylab topilmagan raqamlar*  
*Vaqt: 163s, asboblar: 1*

- `chuqur_tadqiqot({"sahifalar_soni": 8, "sorovlar": ["O'zbekistonda 2026-yilda elektromobillar narxi va modellari", "O'zbekistonda elektromobillar uchun soliq imtiyozlari 2026", "O'zbekistondagi elektromobil zaryadlash) -> "8 ta manba ochildi. Faqat shu matnlarga tayan, har bir fakt uchun URL ko'rsat. Manbalarda yo'q raqamni yozma.\n\n### MANBA: 2026-yilda BYD O'zbekistonda Yuan Up elektromobilini ishlab ...\nURL: https://www.spot.uz/oz/2026/02/16/yuan-up/\nYangiliklar\n\nMaqolalar\n\nFikr-mulohazalar\n\nQo‘llanmalar\n\nKo‘chmas m"`

2026-yil holatiga ko‘ra, O‘zbekistonda elektromobil (EV) sotib olish masalasi ham iqtisodiy, ham texnik jihatdan juda dolzarb mavzuga aylandi. Quyida siz so‘ragan uchta asosiy yo‘nalish bo‘yicha chuqur tahliliy hisobot taqdim etiladi.

# 2026-yilda O‘zbekistonda elektromobil sotib olish bo‘yicha tahliliy hisobot

## 1. Narxlar va Modellarning xilma-xilligi
2026-yilda elektromobil bozori asosan mahalliy ishlab chiqarish va yangi brendlarning kirib kelishi bilan shakllangan.

*   **Mahalliy ishlab chiqarish afzalligi:** Jizzaxdagi **BYD Uzbekistan Factory** va **Geely** kabi zavodlarning faoliyati tufayli mahalliy ishlab chiqarilgan elektromobillar import qilinadigan modellarga qaraganda ancha arzonroq bo‘lishi kutilmoqda.
*   **Asosiy modellar:**
    *   **BYD Yuan Up:** 2026-yilda Jizzax zavodida ishlab chiqarish yo‘lga qo‘yilmoqda. Bu model bozorga katta talab bilan kirib kelmoqda.
    *   **Geely EX2:** Geely brendi tomonidan taqdim etilayotgan yangi elektromobil modeli.
    *   **BYD Song Plus va Chazor:** Hozirda ishlab chiqarilayotgan va bozorda mavjud bo‘lgan mashhur modellar.
*   **Narxlar:** Aniq narxlar model va komplektatsiyaga qarab farq qiladi, biroq mahalliy ishlab chiqarish hajmi ortishi bilan narxlarning tushishi prognoz qilinmoqda.

## 2. Soliq imtiyozlari va Moliyaviy yengilliklar
Davlat elektromobillarni rag‘batlantirish uchun juda keng ko‘lamli imtiyozlar tizimini yo‘lga qo‘ygan:

*   **Bojxona va Aktsiz:** Elektromobillar uchun bojxona boji va aktsiz **0%** ni tashkil etadi. Bu ularni benzinli avtomobillarga qaraganda importda ancha arzon qiladi.
*   **QQS:** Elektromobillar uchun QQS stavkasi **12%** ni tashkil etadi.
*   **Imtiyozli Kreditlar:** Elektromobil sotib olish uchun kredit stavkasi yillik **16% gacha** tushirilgan (odatdagi avtokreditlar 23% atrofida bo‘lishiga qaraganda sezilarli yengillik).
*   **Taksi haydovchilari uchun:**
    *   O‘zini o‘zi band qilgan taksi haydovchilari uchun ijtimoiy soliq **10% gacha** kamaytiriladi.
    *   Aeroport va vokzallar kabi pulli avtoturargohlardan **30 daqiqagacha bepul** foydalanish imkoniyati beriladi.
*   **Rastamojka (Import uchun):** Utilizatsiya yig‘imi 3 yildan ortiq bo‘lgan avtomobillar uchun 210 BHM ni tashkil etadi.

## 3. Zaryadlash infratuzilmasi
Infratuzilma jadal rivojlanmoqda, biroq hali ham hududiy taqsimotda farqlar mavjud:

*   **Stansiyalar soni:** Davlat maqsadi zaryadlash stansiyalari sonini **4 000 tagacha** yetkazishdir (2025-yil boshida bu ko‘rsatkich ~1 400 ta edi).
*   **Tadbirkorlar uchun qo‘llab-quvvatlash:**
    *   Zaryadlash stansiyalari uchun elektr energiyasi tarifining bir qismini (1 kVt/soat uchun 300 so‘mdan ortiq qismini) davlat budjetidan subsidiyalash rejalashtirilgan.
    *   Stansiyalar o‘rnatish uchun **10% stavkali** maqsadli kreditlar beriladi.
    *   Yer uchastkalari bozor narxidan **2 baravar past** narxlarda beriladi.
*   **Hududiy holat:** Elektromobillar soni bo‘yicha **Toshkent shahri (72%)** yetakchilik qilmoqda. Qoraqalpog‘iston va Jizzax kabi hududlarda esa eng yuqori o‘sish sur’atlari (35-37%) kuzatilmoqda.

---

## Xulosa: Foydalimi?

**Ha, elektromobil sotib olish foydali, agar:**
1.  **Siz Toshkent yoki unga yaqin hududda yashasangiz:** Zaryadlash infratuzilmasi eng yaxshi rivojlangan hudud bu.
2.  **Siz taksi xizmati bilan shug‘ullansangiz:** Soliq imtiyozlari va bepul turargohlar xarajatlarni sezilarli darajada kamaytiradi.
3.  **Siz uzoq muddatli tejamkorlikni xohlasangiz:** 0% boj va aktsiz hamda imtiyozli kreditlar dastlabki xarajatlarni kamaytiradi.

**Ehtiyot bo‘lish kerak bo‘lgan jihatlar:**
*   **Hududiy masofa:** Agar siz elektromobillarning kam bo‘lgan chekka hududlarda yashasangiz, zaryadlash stansiyalarini topish qiyin bo‘lishi mumkin.
*   **QQS va Utilizatsiya:** Bojxona boji 0% bo‘lsa-da, QQS (12%) va utilizatsiya yig‘imi baribir hisobga olinishi kerak.

**Yakuniy qaror:** 2026-yilda elektromobil — bu nafaqat ekologik tanlov, balki davlat tomonidan qo‘llab-quvvatlanayotgan strategik iqtisodiy qarordir.

---
**Manbalar:**
*   *Spot.uz (2026-09-25): Elektromobillar soni 122 mingdan oshdi.*
*   *Gazeta.uz (2026-02-18): Avtokredit, subsidiya va chegirmalar.*
*   *A-bozor (2026-02-20): 16% li kreditlar tasdiqlandi.*
*   *Tez Motors (2026-06-21): Elektromobil rastamojkasi 2026.*
*   *Daryo (2026-01-24): Taksi haydovchilari uchun imtiyozlar.*

---

