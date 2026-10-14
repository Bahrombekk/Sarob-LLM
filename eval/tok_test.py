"""Token darajasidagi tahlil: o'zbekcha matn qancha tokenga bo'linadi, apostrof variantlari, inglizcha/ruscha bilan solishtirish."""
import json, urllib.request

URL = "http://127.0.0.1:8000/tokenize"
TEXT = ("O'zbekiston Respublikasi Markaziy banki bugungi kunda dollar kursini o'zgartirdi. "
        "G'alla yig'im-terimi to'liq yakunlandi, qo'shimcha ma'lumotlar keyinroq e'lon qilinadi. "
        "Toshkent shahrida yo'llar ta'mirlanmoqda va yangi bog'lar barpo etilmoqda.")
VARIANTS = {
    "o' (ASCII apostrof)": TEXT,
    "oʻ (rasmiy U+02BB)": TEXT.replace("o'", "oʻ").replace("g'", "gʻ").replace("O'", "Oʻ").replace("G'", "Gʻ").replace("'", "ʼ"),
    "o‘ (U+2018)": TEXT.replace("'", "‘"),
    "o’ (U+2019)": TEXT.replace("'", "’"),
    "kirill": ("Ўзбекистон Республикаси Марказий банки бугунги кунда доллар курсини ўзгартирди. "
               "Ғалла йиғим-терими тўлиқ якунланди, қўшимча маълумотлар кейинроқ эълон қилинади. "
               "Тошкент шаҳрида йўллар таъмирланмоқда ва янги боғлар барпо этилмоқда."),
    "inglizcha (bir xil ma'no)": ("The Central Bank of the Republic of Uzbekistan changed the dollar rate today. "
                                  "The grain harvest has been fully completed; additional information will be announced later. "
                                  "Roads are being repaired in Tashkent and new parks are being created."),
    "ruscha (bir xil ma'no)": ("Центральный банк Республики Узбекистан сегодня изменил курс доллара. "
                               "Уборка зерна полностью завершена, дополнительная информация будет объявлена позже. "
                               "В Ташкенте ремонтируются дороги и создаются новые парки."),
}


def tok(s):
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        URL, json.dumps({"model": "gemma-4-26b", "prompt": s}).encode(), {"Content-Type": "application/json"})))
    return r["count"], r.get("tokens", [])


base, _ = tok(VARIANTS["o' (ASCII apostrof)"])
for k, v in VARIANTS.items():
    n, _ = tok(v)
    print(f"{k:28s} {n:4d} token  ({n / base:5.0%} ASCII o' ga nisbatan, {len(v.split())} so'z, {n / len(v.split()):.2f} token/so'z)")

# Alohida so'zlar qanday bo'linadi
print()
for w in ["o'zbek", "oʻzbek", "o‘zbek", "g'alla", "gʻalla", "ma'lumot", "maʼlumot", "Toshkent", "qo'shimcha", "yig'im-terimi"]:
    n, ids = tok(" " + w)
    print(f"  {w:14s} -> {n} token")
