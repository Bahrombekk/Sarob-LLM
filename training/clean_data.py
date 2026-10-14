"""Xom datasetlardan taxminchini o'qitish uchun toza so'rovlar to'plamini yasaydi.

Javoblar datasetdan olinmaydi: ularni keyin Sarobning o'zi (Gemma) yozadi. Shuning uchun bu yerda faqat
so'rovlar sifati muhim: tabiiy o'zbekcha, takrorsiz, shablonlar cheklangan, Sarob ishiga yaqin.

Natija: /data/prompts.jsonl  ({"id","src","lang","messages",["tools"]})  va  /data/data_report.md
"""
import json, re, random, hashlib, unicodedata, collections, sys
from pathlib import Path
import pandas as pd

RAW = Path(sys.argv[1] if len(sys.argv) > 1 else "/data/raw")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "/data")
random.seed(42)

# Har bir manbadan olinadigan eng ko'p so'rov soni (umumiy aralashma ~60k: ~70% o'zbekcha)
QUOTA = {"uz_alpaca": 11000, "uz_slimorca": 9000, "uz_oasst2": 7000, "uz_selfinst": 6000, "uz_instruct": 5000,
         "uz_news": 5000, "uz_transl": 3000, "uz_support": 800,
         "en_ultrachat": 5000, "en_wildchat": 4000, "ru_wildchat": 3500, "tools_hermes": 1100}
TEMPLATE_CAP = 12          # bir xil boshlanishli (shablon) so'rovlar soni chegarasi
MIN_LEN, MAX_LEN = 8, 6000

# ---------------------------------------------------------------- normallashtirish
APOS = str.maketrans({"ʻ": "'", "ʼ": "'", "‘": "'", "’": "'", "`": "'", "´": "'", "ʹ": "'"})
ZW = re.compile(r"[​-‏⁠﻿­]")


EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
PHONE = re.compile(r"\+?998[\s-]?\(?\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}")


def norm(t):
    t = unicodedata.normalize("NFC", str(t or ""))
    t = PHONE.sub("+998 90 123 45 67", EMAIL.sub("namuna@example.uz", t))  # shaxsiy aloqa ma'lumotlari
    t = ZW.sub("", t).translate(APOS)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


CYR = re.compile(r"[Ѐ-ӿ]")
LAT = re.compile(r"[A-Za-z]")
# apostrofli o'zbekcha so'zlar ("to'g'ri", "to'rt") inglizcha "to" deb sanalmasligi uchun ' ham chegara hisoblanadi
EN = re.compile(r"(?<![\w'])(the|and|is|are|of|to|with|that|this|for|you|what|how|in|on)(?![\w'])", re.I)


def script_share(t):
    c, l = len(CYR.findall(t)), len(LAT.findall(t))
    return c / max(1, c + l)


def en_ratio(t):
    return len(EN.findall(t)) / max(1, len(t.split()))


def tkey(t, n):
    return re.sub(r"[^a-zа-я0-9]+", "", t.lower())[:n]


# ---------------------------------------------------------------- yig'uvchi
rows, stats, EXAMPLES = [], collections.defaultdict(collections.Counter), {}


class Pool:
    """Bitta manbadan so'rovlarni yig'adi: uzunlik, til, takror va shablon filtrlari bilan."""

    def __init__(self, src, lang):
        self.src, self.lang, self.items = src, lang, []
        self.seen, self.tmpl, self.ex = set(), collections.Counter(), collections.defaultdict(list)

    def drop(self, why, t):
        stats[self.src][why] += 1
        if len(self.ex[why]) < 4 and random.random() < 0.05:
            self.ex[why].append(t[:160].replace("\n", " "))

    def add(self, user, system=None, tools=None, check_lang=True, tmpl_key=None):
        st = stats[self.src]
        st["kirdi"] += 1
        user = norm(user)
        if not (MIN_LEN <= len(user) <= MAX_LEN):
            st["uzunlik"] += 1; return
        if "{{" in user or re.search(r"<noinput>|\{input\}|\[insert", user, re.I):
            st["to'ldirilmagan shablon"] += 1; return
        if check_lang:
            if self.lang == "uz" and (script_share(user) > 0.3 or en_ratio(user) > 0.12):
                self.drop("til mos emas", user); return
            if self.lang == "ru" and script_share(user) < 0.3:
                self.drop("til mos emas", user); return
            if self.lang == "en" and (script_share(user) > 0.1 or len(user) < 25):
                self.drop("til mos emas", user); return
        k = hashlib.md5(tkey(user, 400).encode()).hexdigest()
        if k in self.seen:
            st["takror"] += 1; return
        t = tkey(tmpl_key if tmpl_key is not None else user, 45)
        if self.tmpl[t] >= TEMPLATE_CAP:
            self.drop("shablon ko'p", user); return
        self.seen.add(k); self.tmpl[t] += 1
        msgs = ([{"role": "system", "content": norm(system)}] if system and norm(system) else [])
        msgs.append({"role": "user", "content": user})
        it = {"src": self.src, "lang": self.lang, "messages": msgs}
        if tools:
            it["tools"] = tools
        self.items.append(it)

    def done(self):
        random.shuffle(self.items)
        keep = self.items[:QUOTA[self.src]]
        stats[self.src]["qoldi"] = len(keep)
        EXAMPLES[self.src] = dict(self.ex)
        rows.extend(keep)


def first(msgs, roles=("user", "human", "prompter")):
    for m in msgs:
        if (m.get("role") or m.get("from")) in roles:
            return m.get("content") or m.get("value") or ""
    return ""


def system_of(msgs):
    for m in msgs:
        if (m.get("role") or m.get("from")) == "system":
            return m.get("content") or m.get("value") or ""
    return None


rp = lambda f: pd.read_parquet(RAW / f)

# --- uz_alpaca: instruction + input
p = Pool("uz_alpaca", "uz")
for r in rp("uz_alpaca.parquet").itertuples():
    p.add(r.instruction + ("\n\n" + r.input if str(r.input).strip() else ""))
p.done()

# --- uz_selfinst
p = Pool("uz_selfinst", "uz")
for x in json.load(open(RAW / "uz_selfinst.json", encoding="utf-8")):
    p.add(x["instruction"] + ("\n\n" + x["input"] if str(x.get("input", "")).strip() else ""))
p.done()

# --- uz_instruct (dolly tarjimasi): system ichida kontekst bo'ladi -> foydalanuvchi xabariga qo'shiladi
p = Pool("uz_instruct", "uz")
for m in pd.read_json(RAW / "uz_instruct.jsonl", lines=True).messages:
    ctx = (system_of(m) or "").strip()
    q = first(m)
    p.add(q + ("\n\nMatn:\n" + ctx if ctx else ""))
p.done()

# --- uz_slimorca: tizim xabari + birinchi so'rov; javobi so'rovga sizib chiqqanlar ("**Summary:**") tashlanadi
p = Pool("uz_slimorca", "uz")
for c in rp("uz_slimorca.parquet").conversations:
    c = list(c)
    q = first(c)
    if re.search(r"\*\*(Summary|Answer|Output)\*\*|^\(.*\)$", q):
        stats["uz_slimorca"]["javob sizgan/bo'sh"] += 1; continue
    p.add(q, system=system_of(c))
p.done()

# --- uz_oasst2: faqat ildiz so'rovlar, o'chirilmagan va tekshiruvdan o'tgan
p = Pool("uz_oasst2", "uz")
d = rp("uz_oasst2.parquet")
d = d[d.parent_id.isna() & (d.role == "prompter") & ~d.deleted.astype(bool) & (d.review_result == True)]
for t in d.text:
    p.add(t)
p.done()

# --- uz_transl: 8 xil tarjima/javob vazifasi; inglizcha javob talab qiladiganlari kamroq olinadi
p = Pool("uz_transl", "uz")
d = rp("uz_transl.parquet")
for r in d.itertuples():
    ins = str(r.instruction)
    if re.search(r"ingliz tilida javob|in English:", ins) and random.random() > 0.25:
        continue
    body = str(r.input).strip()
    p.add(ins + ("\n\n" + body if body else ""), check_lang=False, tmpl_key=body or ins.split("\n", 1)[-1])
p.done()

# --- uz_support: {{Order Number}} kabi bo'sh joylar real qiymatlar bilan to'ldiriladi
FILL = {"order number": ["#A48213", "#U-20931", "#771045"], "account type": ["Premium", "Biznes", "Standart"],
        "delivery city": ["Toshkent", "Samarqand", "Namangan"], "person name": ["Aziz", "Dilnoza", "Jasur"],
        "invoice number": ["INV-3381", "2024-1157"], "refund amount": ["250 000 so'm", "1,2 mln so'm"],
        "delivery country": ["Qozog'iston", "Turkiya"], "client first name": ["Aziz", "Malika"],
        "account category": ["Premium", "Oilaviy"], "currency symbol": ["so'm"], "website url": ["shop.uz"]}


def fill(t):
    def rep(m):
        v = FILL.get(m.group(1).strip().lower())
        return random.choice(v) if v else m.group(0)
    return re.sub(r"\{\{([^}]+)\}\}", rep, t)


p = Pool("uz_support", "uz")
for m in rp("uz_support.parquet").messages:
    p.add(fill(first(list(m))))
p.done()

# --- uz_news: maqolalardan Sarobga xos vazifalar (xulosa, faktlar jadvali, sarlavha, savollar, tarjima)
JUNK_LINE = re.compile(r"t\.me/|videosharh|obuna bo'ling|^manba:|telegram|instagram|facebook|youtube|^\W*$", re.I)
TASKS = ["Quyidagi maqolaning qisqacha mazmunini 3-4 gapda yozib ber:\n\n{a}",
         "Ushbu yangilikdagi asosiy faktlarni (kim, nima, qachon, qayerda) jadval ko'rinishida chiqar:\n\n{a}",
         "{a}\n\nShu matnga mos qisqa va qiziqarli sarlavha o'ylab top, 3 ta variant ber.",
         "Matnni o'qib, unga oid 3 ta savol tuz va javoblarini yoz:\n\n{a}",
         "{a}\n\nBu xabarni ingliz tiliga tarjima qil.",
         "Quyidagi matnni rasmiy hisobot uslubida qayta yoz:\n\n{a}",
         "{a}\n\nMatnda qanday raqamlar va sanalar keltirilgan? Ro'yxat qilib ber.",
         "Quyidagi xabar asosida rahbarga 5 qatorlik qisqa ma'lumotnoma tayyorla:\n\n{a}",
         "{a}\n\nBu yangilikning asosiy g'oyasi nima va kimlarga ta'sir qiladi?"]


def article(t, limit=2500):
    lines = [l.strip() for l in norm(t).split("\n") if l.strip() and not JUNK_LINE.search(l.strip())]
    out = ""
    for l in lines:
        if len(out) + len(l) > limit:
            break
        out += l + "\n"
    return out.strip()


p = Pool("uz_news", "uz")
d = rp("uz_news.parquet")
d["host"] = d.source.str.extract(r"https?://([^/]+)")[0]
d = pd.concat([d[d.host != "sports.uz"].sample(9000, random_state=1),
               d[d.host == "sports.uz"].sample(2000, random_state=1)])  # sport ulushi cheklanadi
for t in d.text:
    a = article(t)
    if len(a) < 300:
        stats["uz_news"]["juda qisqa maqola"] += 1; continue
    if script_share(a) > 0.3:
        stats["uz_news"]["kirill"] += 1; continue
    p.add(random.choice(TASKS).format(a=a), check_lang=False, tmpl_key=a)
p.done()

# --- inglizcha: ultrachat + wildchat; ruscha: wildchat
BAD_WC = re.compile(r"^CONSTRAINTS:|ignore previous instructions|act as a writer|shooting script|ролевую игру|"
                    r"as a prompt generator|midjourney|nsfw|jailbreak|DAN\b", re.I)
p = Pool("en_ultrachat", "en")
for t in rp("en_ultrachat.parquet").prompt:
    p.add(t)
p.done()
wc = rp("wildchat_0.parquet")
wc = wc[~wc.toxic.astype(bool)]
for lang, src, name in [("en", "en_wildchat", "English"), ("ru", "ru_wildchat", "Russian")]:
    p = Pool(src, lang)
    for c in wc[wc.language == name].conversation:
        q = first(list(c))
        if BAD_WC.search(q or ""):
            stats[src]["yomon shablon"] += 1; continue
        p.add(q)
    p.done()

# --- asbob chaqirish (Hermes): tizim xabari tashlanadi, asboblar OpenAI 'tools' ko'rinishida beriladi
p = Pool("tools_hermes", "en")
for x in json.load(open(RAW / "tools_hermes.json", encoding="utf-8")):
    tools = x["tools"]
    if isinstance(tools, str):
        try:
            tools = json.loads(tools)
        except Exception:
            stats["tools_hermes"]["asbob o'qilmadi"] += 1; continue
    q = first(x["conversations"])
    if q.startswith("Can you help me extract queries"):
        if random.random() > 0.1:
            stats["tools_hermes"]["shablon ko'p"] += 1; continue
    p.add(q, tools=tools, check_lang=False)
p.done()

# ---------------------------------------------------------------- yozish va hisobot
random.shuffle(rows)
with open(OUT / "prompts.jsonl", "w", encoding="utf-8") as f:
    for i, r in enumerate(rows):
        f.write(json.dumps({"id": f"p{i:06d}", **r}, ensure_ascii=False) + "\n")

lang = collections.Counter(r["lang"] for r in rows)
L = ["# O'qitish so'rovlari: tozalash hisoboti", "",
     f"Jami: **{len(rows)}** so'rov — " + ", ".join(f"{k}: {v} ({v/len(rows):.0%})" for k, v in lang.most_common()), "",
     "| Manba | Kirdi | Qoldi | Tashlanganlar |", "|---|---|---|---|"]
for s, c in stats.items():
    drop = ", ".join(f"{k} {v}" for k, v in c.most_common() if k not in ("kirdi", "qoldi"))
    L.append(f"| {s} | {c['kirdi']} | {c['qoldi']} | {drop} |")
L += ["", "## Tashlangan so'rovlardan namunalar", ""]
for s, ex in EXAMPLES.items():
    for why, items in ex.items():
        for t in items:
            L.append(f"- **{s} / {why}:** {t}")
(OUT / "data_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
