"""Yuklangan datasetlarning tuzilishi va sifatini tekshiradi: ustunlar, qator soni, til/yozuv,
bo'sh/takror qatorlar, buzilgan kodlash, tarjima qilinmay qolgan matn, apostrof turlari."""
import json, re, sys, collections
from pathlib import Path
import pandas as pd

RAW = Path(sys.argv[1] if len(sys.argv) > 1 else "/data/raw")
CYR = re.compile(r"[Ѐ-ӿ]")
LAT = re.compile(r"[A-Za-z]")
UZ_MARK = re.compile(r"\b\w+(lar|ning|dagi|gan|moq|ish|siz|miz|ingiz)\b|o['ʻʼ‘’`]|g['ʻʼ‘’`]", re.I)
EN_WORDS = re.compile(r"\b(the|and|is|are|of|to|with|that|this|for|you)\b", re.I)
MOJI = re.compile(r"Ã.|Â.|â€|Ð.|Ñ.|�")
APOS = {"'": "ascii '", "ʻ": "U+02BB ʻ", "ʼ": "U+02BC ʼ", "‘": "U+2018 ‘", "’": "U+2019 ’", "`": "backtick `"}
AI_JUNK = re.compile(r"as an ai|language model|sun'iy intellekt (til )?modeli sifatida|men ai|I'm sorry", re.I)


def load(p):
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    if p.suffix == ".jsonl":
        return pd.read_json(p, lines=True)
    d = json.load(open(p, encoding="utf-8"))
    return pd.DataFrame(d if isinstance(d, list) else d.get("data", d))


def flat(v):
    """Ustun qiymatini matnga aylantiradi (ro'yxat/lug'at bo'lsa ham)."""
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    try:
        return json.dumps(v.tolist() if hasattr(v, "tolist") else v, ensure_ascii=False, default=str)
    except Exception:
        return str(v)


def lang(t):
    c, l = len(CYR.findall(t)), len(LAT.findall(t))
    if c + l < 10:
        return "qisqa"
    if c > l:
        return "kirill"
    words = max(1, len(t.split()))
    en = len(EN_WORDS.findall(t)) / words
    uz = len(UZ_MARK.findall(t)) / words
    if en > 0.08 and en > uz:
        return "ingliz"
    return "lotin-uz" if uz > 0.03 else "lotin-?"


for p in sorted(RAW.iterdir()):
    try:
        df = load(p)
    except Exception as e:
        print(f"\n### {p.name}: O'QILMADI {e}")
        continue
    print(f"\n### {p.name}  qatorlar={len(df)}  ustunlar={list(df.columns)}", flush=True)
    df = df.sample(min(len(df), 20000), random_state=0)
    text = df.apply(lambda r: " \n".join(flat(r[c]) for c in df.columns), axis=1)
    lens = text.str.len()
    print(f"  uzunlik (belgi): median={int(lens.median())} p95={int(lens.quantile(.95))} max={int(lens.max())}")
    print(f"  bo'sh(<20 belgi)={int((lens < 20).sum())}  to'liq takror={int(text.duplicated().sum())}")
    s = text.sample(min(len(text), 3000), random_state=1)
    print("  til:", dict(collections.Counter(s.map(lang)).most_common()))
    print(f"  buzilgan kodlash={int(s.str.contains(MOJI).sum())}  'AI sifatida' kabi={int(s.str.contains(AI_JUNK).sum())}")
    ap = collections.Counter()
    for t in s:
        for ch in re.findall(r"(?<=[oOgG])['ʻʼ‘’`]", t):
            ap[APOS[ch]] += 1
    print("  o'/g' apostroflari:", dict(ap.most_common()))
    # birinchi qatorning qisqa namunasi
    r = df.iloc[0]
    for c in df.columns[:4]:
        print(f"  [{c}] {flat(r[c])[:220]!r}")
