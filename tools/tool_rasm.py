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
- Foto/rasm ustunlarini va tugmalarni (tahrirlash, o'chirish) tashlab ket. Qator holati (masalan "Ulangan"/"Ulanmagan") — matn sifatida yoz.
- Ma'noga ega rangli belgilar, nuqtalar, ikonkalar, rang bilan ajratilgan kataklar (masalan qizil/yashil/sariq nuqta,
  yulduzcha, ogohlantirish belgisi) bo'lsa — ularni oxirgi "Belgi" ustuniga matn bilan yoz (masalan "qizil nuqta");
  belgisi yo'q qatorda bu katak bo'sh qolsin.
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


def _images_from_messages(messages):
    """Zaxira: __files__ bo'sh bo'lsa (masalan, javob qayta yaratilganda Open WebUI fayllarni uzatmaydi),
    rasmlarni suhbat xabarlaridan olamiz — rasmli eng oxirgi foydalanuvchi xabaridan."""
    import tempfile

    for m in reversed(messages or []):
        if m.get("role") != "user":
            continue
        out = _image_files(m.get("files") or [])
        content = m.get("content")
        for i, p in enumerate(content if isinstance(content, list) else []):
            if not (isinstance(p, dict) and p.get("type") == "image_url"):
                continue
            url = (p.get("image_url") or {}).get("url") or ""
            if url.startswith("data:image"):
                head, b64 = url.split(",", 1)
                ext = ".png" if "png" in head else ".jpg"
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext, prefix="sarob_rasm_")
                tmp.write(base64.b64decode(b64)); tmp.close()
                out.append((f"rasm_{i + 1}{ext}", tmp.name))
            else:
                fid = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", url)
                hits = glob.glob(os.path.join(UPLOADS, f"{fid.group(0)}_*")) if fid else []
                if hits and all(h != hits[0] for _, h in out):
                    out.append((os.path.basename(hits[0]).split("_", 1)[-1], hits[0]))
        if out:
            return out
    return []


PIXEL_BUDGET = 2.5e6   # Gemma 4 (max_soft_tokens=1120) shu maydongacha kichraytirmasdan ko'radi


def _prepare(name_path):
    """Rasmni o'qishga tayyorlaydi:
    - kichik shriftli skrinshot ~2.5 MP gacha (2x dan ko'p emas) kattalashtiriladi — sinov: poyezd indeksi
      "7235" 5 urinishdan 1 marta to'g'ri o'qilardi, kattalashtirilgach 5/5;
    - bo'yi enidan ancha uzun skrinshot ustma-ust tushadigan bo'laklarga bo'linadi (har bo'lak to'liq aniqlikda),
      ulanish joyidagi takror qatorlar keyin olib tashlanadi."""
    import math
    import tempfile

    from PIL import Image

    name, path = name_path
    try:
        im = Image.open(path).convert("RGB")
    except Exception:
        return [name_path]
    w, h = im.size
    parts = [im]
    if h > 1.4 * w:
        n = math.ceil(h / (0.9 * w))
        step = h / n
        pad = int(step * 0.12)
        parts = [im.crop((0, max(0, int(i * step) - pad), w, min(h, int((i + 1) * step) + pad))) for i in range(n)]
    out = []
    for i, p in enumerate(parts):
        pw, ph = p.size
        f = min(2.0, math.sqrt(PIXEL_BUDGET / (pw * ph)))
        if f > 1.05:
            p = p.resize((int(pw * f), int(ph * f)), Image.LANCZOS)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png", prefix="sarob_tayyor_")
        p.save(tmp.name)
        out.append((name if len(parts) == 1 else f"{name} ({i + 1}/{len(parts)})", tmp.name))
    return out


def _read_table_vlm(name_path, shart="", ustunlar=None):
    name, path = name_path
    data = base64.b64encode(open(path, "rb").read()).decode()
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    prompt = PROMPT + (f"\n- FAQAT shu shartga mos qatorlarni yoz: {shart}. Mos qator bo'lmasa, \"qatorlar\": [] qaytar."
                       if shart else "")
    if ustunlar:
        # Bir jadvalning davomi: har rasmda ustunlar boshqacha nomlanib, natija bir necha varaqqa bo'linib ketardi
        prompt += ("\n- Bu bitta jadvalning davomi. \"ustunlar\" AYNAN shular va shu tartibda bo'lsin (sarlavha "
                   f"ko'rinmasa ham): {json.dumps(ustunlar, ensure_ascii=False)}. Har qatordagi qiymatlar shu ustunlarga "
                   "mos joyda tursin. Faqat rasmdagi jadval butunlay boshqa bo'lsa, o'z ustunlarini yoz.")
    body = {"model": MODEL, "temperature": 0, "max_tokens": 8000,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
                {"type": "text", "text": prompt}]}],
            "response_format": {"type": "json_object"}}
    try:
        r = requests.post(VLLM, json=body, timeout=300).json()
        txt = r["choices"][0]["message"]["content"]
        d = json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
        return name, d.get("ustunlar") or [], d.get("qatorlar") or [], ""
    except Exception as e:
        return name, [], [], str(e)[:150]


OCR_URL = "http://127.0.0.1:8002/v1/chat/completions"   # PaddleOCR-VL-1.6 (serving/sarob_vllm_ocr.sh)


def _read_table_ocr(name_path, shart="", ustunlar=None):
    """Hujjat usuli: maxsus OCR modeli (PaddleOCR-VL) jadvalni OTSL ko'rinishida qaytaradi.
    Sinov: 19 ta telefon fotosi 16 soniyada (Gemma ~100 s), qamrov 92% (Gemma 97%); rangli belgilarni ko'rmaydi."""
    name, path = name_path
    data = base64.b64encode(open(path, "rb").read()).decode()
    body = {"model": "paddleocr-vl", "temperature": 0, "max_tokens": 8000,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}},
                {"type": "text", "text": "Table Recognition:"}]}]}
    try:
        txt = requests.post(OCR_URL, json=body, timeout=300).json()["choices"][0]["message"]["content"]
    except Exception as e:
        return name, [], [], f"OCR: {str(e)[:120]}"
    grid = []
    for line in txt.split("<nl>"):
        cells = re.findall(r"<(fcel|ecel|lcel|ucel|xcel)>([^<]*)", line)
        if cells:
            grid.append([v.strip() if t == "fcel" else "" for t, v in cells])
    if not grid:
        return name, [], [], "jadval topilmadi"
    # Birinchi qator sarlavhami (raqam bilan boshlanmasa)
    if grid[0] and not re.match(r"\s*\d", grid[0][0] or "x"):
        return name, grid[0], grid[1:], ""
    return name, [], grid, ""


def _align(cols, canon):
    """cols ustunlarini canon qolipiga nom bo'yicha moslaydi: [canon indeksi yoki None, ...].
    Ustunlarning yarmidan kami mos kelsa — None (sarlavha o'ylab topilgan, qayta o'qish kerak)."""
    import difflib

    def nz(s):
        s = str(s).strip().lower()
        # tartib raqami ustuni turlicha yoziladi: №, N°, N', #, No — hammasi bitta ("№" \w emas, aks holda bo'sh bo'lib qoladi)
        if re.fullmatch(r"(№|n[°'ºo]?\.?|#|no\.?|t/r|т/р)", s):
            return "tartibraqam"
        return re.sub(r"[\W_]+", "", s)

    cn = [nz(c) for c in canon]
    mp, hits = [], 0
    for c in cols:
        best = difflib.get_close_matches(nz(c), cn, n=1, cutoff=0.6)
        j = cn.index(best[0]) if best else None
        if j is not None and j in mp:
            j = None
        mp.append(j)
        hits += j is not None
    return mp if hits >= max(1, len(cols) // 2) else None


def _filter_rows(cols, rows, shart):
    """Shartni tayyor jadvalga qo'llaydi (matn bo'yicha, rasmsiz): mos qatorlar indekslarini qaytaradi."""
    # Belgi bo'yicha oddiy shartlar (qizil/yashil/sariq ...) — model chaqirmasdan, aniq
    bi = next((i for i, c in enumerate(cols) if "belgi" in str(c).lower()), None)
    colors = [c for c in ("qizil", "yashil", "sariq", "ko'k", "qora", "to'q sariq") if c in shart.lower()]
    if bi is not None and colors and re.search(r"nuqta|belgi|rang|bor", shart.lower()):
        return [k for k, r in enumerate(rows) if bi < len(r) and any(c in str(r[bi]).lower() for c in colors)]
    table = "\n".join(f"{k}: " + json.dumps(dict(zip(cols, r)), ensure_ascii=False) for k, r in enumerate(rows))
    body = {"model": MODEL, "temperature": 0, "max_tokens": 4000,
            "chat_template_kwargs": {"enable_thinking": False}, "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content":
                          f"Quyidagi jadval qatorlaridan shartga mos kelganlarining indekslarini top.\nShart: {shart}\n\n"
                          f"{table}\n\nFaqat JSON qaytar: {{\"mos\": [indekslar]}}"}]}
    try:
        r = requests.post(VLLM, json=body, timeout=300).json()
        txt = r["choices"][0]["message"]["content"]
        return [int(x) for x in json.loads(txt[txt.find("{"): txt.rfind("}") + 1]).get("mos", [])]
    except Exception:
        return list(range(len(rows)))


class Tools:
    def __init__(self):
        pass

    def rasmlardan_excel(self, fayl_nomi: str = "jadval", shart: str = "", usul: str = "aniq", __files__: list = None,
                         __messages__: list = None) -> str:
        """
        Convert tables in the screenshots/images attached to this chat into ONE Excel file. Reads every image
        separately at high resolution (small text is upscaled, tall screenshots are split), merges rows in image order,
        removes duplicate rows from overlapping screenshots. Colored markers/dots/icons are kept in a "Belgi" column.
        Use this whenever the user sends screenshots of a table and asks for Excel/CSV/a table — do NOT transcribe
        rows yourself, even if the user wants only some rows: pass the condition in `shart`.
        :param fayl_nomi: Output file name without extension, Latin letters/digits/underscore only (e.g. "kameralar").
        :param shart: Optional row filter in plain words, e.g. "faqat qizil nuqtali qatorlar" or "faqat Ulanmagan". Empty = all rows.
        :param usul: "aniq" (default: screen screenshots, colored markers/dots, Cyrillic UI text) or "hujjat"
                     (scanned/photographed PAPER documents, forms, invoices, printed tables, many pages — specialized
                     OCR model, ~6x faster; does not see colored markers).
        :return: Summary with row count, columns, preview and the download link.
        """
        imgs = _image_files(__files__) or _images_from_messages(__messages__)
        if not imgs:
            return "Bu chatda rasm topilmadi. Foydalanuvchidan jadval skrinshotlarini yuborishni so'ra."
        reader = _read_table_ocr if (usul or "").lower().startswith("hujjat") else _read_table_vlm
        unified = None

        with ThreadPoolExecutor(4) as ex:
            parts = [p for ps in ex.map(_prepare, imgs) for p in ps]
            # Har doim BARCHA qatorlar (belgisi bilan) o'qiladi; shart keyin tayyor jadvalga qo'llanadi —
            # sinov: rasmga shart berilganda 6 ta qizil qator bir urinishda butunlay tushib qoldi, bu usulda 6/6.
            # 1) hamma bo'lak erkin o'qiladi; 2) eng to'liq ustunlar ro'yxati — qolip; 3) ustunlar soni qolipga
            # to'g'ri kelmagan bo'laklar (masalan, sarlavhasi ko'rinmagan fotolar) shu qolip bilan qayta o'qiladi.
            results = list(ex.map(reader, parts))
            cols_all = [c for _, c, _, _ in results if c]
            if cols_all:
                # Qolip: eng ko'p uchragan ustunlar soni (bitta rasmdagi xato o'qish qolip bo'lib qolmasin),
                # teng bo'lsa — eng uzuni
                from collections import Counter

                cnt = Counter(len(c) for c in cols_all)
                best_n = max(cnt, key=lambda n: (cnt[n], n))
                canon = [str(c) for c in next(c for c in cols_all if len(c) == best_n)]
                # OCR modeli qolip ko'rsatmasini olmaydi — u uchun qayta o'qish befoyda
                redo = ([i for i, (_, c, _, _) in enumerate(results) if c and _align(c, canon) is None]
                        if reader is _read_table_vlm else [])
                for i, res in zip(redo, ex.map(lambda i: reader(parts[i], "", canon), redo)):
                    if res[2]:          # qolip bilan bo'sh chiqsa, erkin o'qilgani qoladi
                        results[i] = res
                # Hammasi bitta qolipga: nom bo'yicha, bo'lmasa tartib bo'yicha (bitta jadval — bitta varaq)
                aligned = []
                for name, c, rws, err in results:
                    if rws:
                        # sarlavhasiz bo'lak (c bo'sh) — tartib bo'yicha
                        mp = (_align(c, canon) if c else None) or list(range(min(max(map(len, rws)), len(canon))))
                        new = []
                        for r in rws:
                            row = [""] * len(canon)
                            for src, dst in enumerate(mp):
                                if dst is not None and src < len(r):
                                    row[dst] = r[src]
                            new.append(row)
                        rws, c = new, canon
                    aligned.append((name, c, rws, err))
                results = aligned
                unified = canon
                # Shart (masalan, qizil nuqta) berilsa — har bo'lak ikkinchi marta o'qiladi va birlashtiriladi:
                # sinovda bitta o'qish ba'zan belgini ko'rmay qolardi (7 dan 6), ikkinchisi bo'shliqni to'ldiradi.
                if shart and reader is _read_table_vlm:
                    second = list(ex.map(lambda p: reader(p, "", canon), parts))
                    for name, c, rws, err in second:
                        if rws and c:
                            mp = _align(c, canon) or list(range(min(max(map(len, rws)), len(canon))))
                            new = []
                            for r in rws:
                                row = [""] * len(canon)
                                for src, dst in enumerate(mp):
                                    if dst is not None and src < len(r):
                                        row[dst] = r[src]
                                new.append(row)
                            results.append((name + " (2)", canon, new, ""))

        import pandas as pd

        # Har xil jadvallarni (ustunlar soni/nomlari farq qiladigan) alohida varaqlarga ajratamiz
        tables, errors = [], []  # [{"cols": [...], "rows": [...], "seen": set()}]

        def sig(cols):
            return tuple(re.sub(r"\W+", "", str(c).lower()) for c in cols)

        if unified:
            # Hammasi bitta qolipda: qatorlar yig'iladi, takrorlar faqat KALIT ustun bo'yicha olib tashlanadi.
            # (Avvalgi "chegara takrorlari" usuli rasmlar teskari tartibda kelganda kerakli qatorlarni ham tashlardi:
            # 19 fotoda 188 o'rniga 126 qator qolgan.)
            allrows = []
            for name, cols, rws, err in results:
                if err or not rws:
                    errors.append(f"{name}: {err or 'jadval topilmadi'}")
                    continue
                allrows += [[("" if v is None else str(v).strip()) for v in r] for r in rws if any(r)]
            nz = lambda v: re.sub(r"[\s⭐★]+", " ", v).strip().lower()
            n = len(unified)
            filled = lambda j: [nz(r[j]) for r in allrows if j < len(r) and nz(r[j])]
            # kalit: deyarli har qatorda to'la va eng ko'p noyob qiymatli ustun (teng bo'lsa — chaproqdagisi)
            cand = [j for j in range(n) if len(filled(j)) >= 0.8 * max(1, len(allrows))]
            key = max(cand or range(n), key=lambda j: (len(set(filled(j))), -j))
            bi = next((j for j, c in enumerate(unified) if "belgi" in str(c).lower()), None)
            seen, rows = {}, []
            for r in allrows:
                k = nz(r[key]) if key < len(r) else ""
                k = k or tuple(r)
                if k in seen:
                    # takror qator: bo'sh kataklarini (ayniqsa Belgi) ikkinchi o'qishdan to'ldiramiz
                    old = rows[seen[k]]
                    for j in range(min(len(old), len(r))):
                        if not old[j] and r[j]:
                            old[j] = r[j]
                    continue
                seen[k] = len(rows)
                rows.append(list(r))
            tables.append({"cols": list(unified), "rows": rows, "seen": set()})

        for name, cols, rws, err in ([] if unified else results):
            if err or not rws:
                errors.append(f"{name}: {err or 'jadval topilmadi'}")
                continue
            width = max(len(r) for r in rws)
            cols = [str(c) for c in cols] if cols else [f"Ustun {i + 1}" for i in range(width)]
            cols = (cols + [f"Ustun {i + 1}" for i in range(len(cols), width)])[:max(width, len(cols))]
            rws = [[("" if v is None else str(v).strip()) for v in r] + [""] * (len(cols) - len(r)) for r in rws]
            # Bo'sh ustunlar shu yerda emas, birlashtirilgan jadvalda o'chiriladi: bitta rasmda bo'sh bo'lgan ustun
            # (masalan "Kl. tashxis") boshqa rasmda to'la bo'lishi mumkin — aks holda jadval varaqlarga bo'linib ketardi.
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
        for t in tables:  # butunlay bo'sh ustunlar (rasm, tugma ustunlari) — butun jadval bo'yicha
            keep = [i for i in range(len(t["cols"])) if any(r[i] for r in t["rows"])]
            t["cols"], t["rows"] = [t["cols"][i] for i in keep], [[r[i] for i in keep] for r in t["rows"]]
        if shart:
            for t in tables:
                t["mos"] = _filter_rows(t["cols"], t["rows"], shart)

        safe = re.sub(r"[^A-Za-z0-9_-]", "_", fayl_nomi or "jadval").strip("_") or "jadval"
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, f"{safe}.xlsx")
        summary, unclear = [], 0
        def write(w, df, sheet):
            df.to_excel(w, index=False, sheet_name=sheet)
            ws = w.sheets[sheet]
            for j, col in enumerate(df.columns, 1):  # ustun kengligi
                width = min(60, max(10, int(df[col].astype(str).str.len().max() * 1.1) if len(df) else 10,
                                    len(str(col)) + 2))
                ws.column_dimensions[ws.cell(1, j).column_letter].width = width
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions

        with pd.ExcelWriter(path, engine="openpyxl") as w:
            for i, t in enumerate(tables, 1):
                df = pd.DataFrame(t["rows"], columns=t["cols"])
                sfx = f" {i}" if len(tables) > 1 else ""
                if shart:
                    sel = df.iloc[[k for k in t["mos"] if 0 <= k < len(df)]]
                    write(w, sel, f"Tanlangan{sfx}")
                    write(w, df, f"Hammasi{sfx}")
                    summary.append({"varaq": f"Tanlangan{sfx}", "qatorlar": len(sel), "jami_oqilgan": len(df),
                                    "shart": shart, "ustunlar": list(df.columns),
                                    "namuna": sel.head(3).to_string(index=False)[:800]})
                else:
                    write(w, df, f"Jadval{sfx}")
                    summary.append({"varaq": f"Jadval{sfx}", "qatorlar": len(df), "ustunlar": list(df.columns),
                                    "namuna": df.head(3).to_string(index=False)[:800]})
                unclear += int(df.apply(lambda s: s.astype(str).str.contains(r"\?")).sum().sum())
        return json.dumps({
            "holat": "ok", "rasmlar": len(imgs), "jadvallar": summary, "noaniq_kataklar": unclear, "xatolar": errors,
            "havola": f"{PUBLIC}/{safe}.xlsx",
            "izoh": "Foydalanuvchiga har bir varaqdagi qatorlar sonini va havolani ayt. Noaniq kataklar (?) bo'lsa, tekshirishni so'ra.",
        }, ensure_ascii=False)
