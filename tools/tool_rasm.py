"""
title: Rasmlardan Excel (Sarob)
description: Skrinshot/rasmlardagi jadvallarni o'qib, bitta Excel faylga yig'adi (har bir rasm alohida, yuqori aniqlikda).
version: 1.0
"""

import base64
import glob
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

import requests

VLLM = "http://127.0.0.1:8000/v1/chat/completions"
MODEL = "gemma-4-26b"
UPLOADS = "/app/backend/data/uploads"
OUT_DIR = "/fayllar"
PUBLIC = "http://192.168.136.153:8090"

PROMPT = """Bu rasmda jadval bor. Jadvaldagi BARCHA ko'rinadigan qatorlarni o'qib, faqat JSON qaytar:
{"ustunlar": ["...", "..."], "qatorlar": [["...", "..."], ...]}
Qoidalar:
- Ustun nomlarini jadval sarlavhasidan aynan ol. Sarlavha ko'rinmasa, ustunlarni mazmuniga qarab nomla.
- Har bir katakni AYNAN rasmdagidek yoz (raqamlar, harflar, kirill/lotin, belgilar). Tarjima qilma, tuzatma.
- Rasm (foto, ikonka) yoki tugma ustunlarini tashlab ket. Qator holati (masalan "Ulangan"/"Ulanmagan") — matn sifatida yoz.
- O'qib bo'lmaydigan belgi o'rniga ? qo'y. Chala kesilgan qatorni ham yoz, ko'rinmagan qismini bo'sh qoldir.
- Hech qanday izoh yozma, faqat JSON."""


def _image_files(files):
    out = []
    for f in files or []:
        info = f.get("file") or f
        meta = info.get("meta") or {}
        ctype = meta.get("content_type") or f.get("content_type") or ""
        name = info.get("filename") or meta.get("name") or f.get("name") or ""
        if not (ctype.startswith("image/") or re.search(r"\.(png|jpe?g|webp|bmp)$", name, re.I)):
            continue
        path = info.get("path") or ""
        if not path or not os.path.exists(path):
            hits = glob.glob(os.path.join(UPLOADS, f"{info.get('id', '')}_*"))
            path = hits[0] if hits else ""
        if path:
            out.append((name, path))
    return out


def _read_table(name_path):
    name, path = name_path
    data = base64.b64encode(open(path, "rb").read()).decode()
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    body = {"model": MODEL, "temperature": 0, "max_tokens": 8000,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
                {"type": "text", "text": PROMPT}]}],
            "response_format": {"type": "json_object"}}
    try:
        r = requests.post(VLLM, json=body, timeout=300).json()
        txt = r["choices"][0]["message"]["content"]
        d = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
        return name, d.get("ustunlar") or [], d.get("qatorlar") or [], ""
    except Exception as e:
        return name, [], [], str(e)[:150]


class Tools:
    def __init__(self):
        pass

    def rasmlardan_excel(self, fayl_nomi: str = "jadval", __files__: list = None) -> str:
        """
        Convert tables in the screenshots/images attached to this chat into ONE Excel file. Reads every image
        separately at high resolution, merges rows in image order, removes duplicate rows from overlapping
        screenshots. Use this whenever the user sends screenshots of a table and asks for Excel/CSV/a table —
        do NOT transcribe rows yourself.
        :param fayl_nomi: Output file name without extension, Latin letters/digits/underscore only (e.g. "kameralar").
        :return: Summary with row count, columns, preview and the download link.
        """
        imgs = _image_files(__files__)
        if not imgs:
            return "Bu chatda rasm topilmadi. Foydalanuvchidan jadval skrinshotlarini yuborishni so'ra."
        with ThreadPoolExecutor(4) as ex:
            results = list(ex.map(_read_table, imgs))

        import pandas as pd

        # Har xil jadvallarni (ustunlar soni/nomlari farq qiladigan) alohida varaqlarga ajratamiz
        tables, errors = [], []  # [{"cols": [...], "rows": [...], "seen": set()}]

        def sig(cols):
            return tuple(re.sub(r"\W+", "", str(c).lower()) for c in cols)

        for name, cols, rws, err in results:
            if err or not rws:
                errors.append(f"{name}: {err or 'jadval topilmadi'}")
                continue
            width = max(len(r) for r in rws)
            cols = [str(c) for c in cols] if cols else [f"Ustun {i + 1}" for i in range(width)]
            cols = (cols + [f"Ustun {i + 1}" for i in range(len(cols), width)])[:max(width, len(cols))]
            rws = [[("" if v is None else str(v).strip()) for v in r] + [""] * (len(cols) - len(r)) for r in rws]
            # Butunlay bo'sh ustunlarni (rasm, tugma ustunlari) olib tashlaymiz
            keep = [i for i in range(len(cols)) if any(r[i] for r in rws)]
            cols, rws = [cols[i] for i in keep], [[r[i] for i in keep] for r in rws]
            # Avval ustun nomlari bir xil jadvalni qidiramiz; topilmasa — ustunlar soni bir xil oxirgi jadvalni
            # (davomiy skrinshotda sarlavha ko'rinmasligi yoki boshqacha nomlanishi mumkin)
            tbl = next((t for t in tables if sig(t["cols"]) == sig(cols)), None)
            if tbl is None:
                tbl = next((t for t in reversed(tables) if len(t["cols"]) == len(cols)), None)
            if tbl is None:
                tbl = {"cols": cols, "rows": [], "seen": set()}
                tables.append(tbl)
            n = len(tbl["cols"])
            rws = [(r + [""] * n)[:n] for r in rws]
            # Kalit ustun: nomi "nom/name/raqam" bo'lgan yoki eng ko'p noyob qiymatli ustun
            if "key" not in tbl:
                named = [i for i, c in enumerate(tbl["cols"]) if re.search(r"(?i)nom|name|raqam|№", c)
                         and len({r[i] for r in rws}) > 0.7 * len(rws)]
                tbl["key"] = named[0] if named else max(range(n), key=lambda i: len({r[i] for r in rws}))
            k = tbl["key"]
            norm = lambda v: re.sub(r"[\s⭐★]+", " ", v).strip().lower()
            # Rasmlar ulanish joyi: yangi rasmning boshidagi qatorlar oldingi rasm oxiridagi qatorlar bilan bir xil
            # (holati yoki vaqti o'zgargan bo'lsa ham) — ularni tashlab ketamiz
            tail = {norm(r[k]) for r in tbl["rows"][-8:]}
            skip = 0
            while skip < min(8, len(rws)) and norm(rws[skip][k]) in tail:
                skip += 1
            for r in rws[skip:]:
                key = tuple(r)
                if key in tbl["seen"] or not any(r):
                    continue  # aynan bir xil qator
                tbl["seen"].add(key)
                tbl["rows"].append(r)
        tables = [t for t in tables if t["rows"]]
        if not tables:
            return "Rasmlardan jadval o'qib bo'lmadi. " + "; ".join(errors)

        safe = re.sub(r"[^A-Za-z0-9_-]", "_", fayl_nomi or "jadval").strip("_") or "jadval"
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, f"{safe}.xlsx")
        summary, unclear = [], 0
        with pd.ExcelWriter(path, engine="openpyxl") as w:
            for i, t in enumerate(tables, 1):
                df = pd.DataFrame(t["rows"], columns=t["cols"])
                sheet = f"Jadval {i}" if len(tables) > 1 else "Jadval"
                df.to_excel(w, index=False, sheet_name=sheet)
                ws = w.sheets[sheet]
                for j, col in enumerate(df.columns, 1):  # ustun kengligi
                    width = min(60, max(10, int(df[col].astype(str).str.len().max() * 1.1), len(str(col)) + 2))
                    ws.column_dimensions[ws.cell(1, j).column_letter].width = width
                ws.freeze_panes = "A2"
                ws.auto_filter.ref = ws.dimensions
                unclear += int(df.apply(lambda s: s.astype(str).str.contains(r"\?")).sum().sum())
                summary.append({"varaq": sheet, "qatorlar": len(df), "ustunlar": list(df.columns),
                                "namuna": df.head(3).to_string(index=False)[:800]})
        return json.dumps({
            "holat": "ok", "rasmlar": len(imgs), "jadvallar": summary, "noaniq_kataklar": unclear, "xatolar": errors,
            "havola": f"{PUBLIC}/{safe}.xlsx",
            "izoh": "Foydalanuvchiga har bir varaqdagi qatorlar sonini va havolani ayt. Noaniq kataklar (?) bo'lsa, tekshirishni so'ra.",
        }, ensure_ascii=False)
