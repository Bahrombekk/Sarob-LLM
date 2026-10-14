"""
title: Internet (Sarob)
description: Internetdan qidirish, sahifani ochib o'qish va GitHub repozitoriylarini ko'rish.
version: 1.0
"""

import json
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux aarch64) Sarob/1.0"}
MAX_CHARS = 15000
SEARXNG = "http://127.0.0.1:8095/search"
BRAUZER = "http://127.0.0.1:8097/amal"


def _clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "form"]):
        t.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _relevant(text, words, limit=2500):
    """Sahifadan so'rovdagi so'zlar (va raqamlar) uchraydigan paragraflarni asl tartibda qaytaradi."""
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if len(p.strip()) > 40]
    scored = [(sum(w in p.lower() for w in words) + (1 if re.search(r"\d", p) else 0), i, p) for i, p in enumerate(paras)]
    out, size = [], 0
    for s in sorted([s for s in scored if s[0] > 0], key=lambda s: -s[0]):
        if size + len(s[2]) <= limit:
            out.append(s)
            size += len(s[2])
    return "\n".join(p for _, _, p in sorted(out, key=lambda s: s[1])) if out else text[:limit]


def _fast_fetch(url, timeout=5):
    """Tezkor sahifa o'qish (avtomatik ochish va chuqur tadqiqot uchun): brauzer zaxirasiz, 5 soniyagacha."""
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        r.raise_for_status()
    except Exception as e:
        return f"XATO: {e}"
    ctype = r.headers.get("content-type", "")
    if "html" not in ctype and "text" not in ctype:
        return "XATO: matn emas"
    text = _clean_html(r.text) if "html" in ctype else r.text
    return f"URL: {url}\n\n{text[:MAX_CHARS]}"


_ZIP_CACHE = {}


def _repo_zip(owner: str, repo: str):
    """Repozitoriyni zip ko'rinishida yuklaydi (GitHub API limitiga bog'liq emas), 10 daqiqa keshlaydi."""
    import io, time, zipfile

    key = f"{owner}/{repo}".lower()
    hit = _ZIP_CACHE.get(key)
    if hit and time.time() - hit[0] < 600:
        return hit[1]
    r = requests.get(f"https://codeload.github.com/{owner}/{repo}/zip/HEAD", headers=UA, timeout=60)
    r.raise_for_status()
    if len(r.content) > 200 * 1024 * 1024:
        raise ValueError("repozitoriy juda katta (200 MB dan ortiq)")
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    _ZIP_CACHE[key] = (time.time(), zf)
    return zf


class Tools:
    def __init__(self):
        pass

    def internetdan_qidirish(self, query: str, max_results: int = 6, sahifalar: int = 0) -> str:
        """
        Search the internet for fresh information: news, prices, exchange rates, events, products, people.
        ALWAYS use this for anything recent or uncertain instead of answering from memory.
        Read the snippets; open the 1-2 most relevant results with sahifani_ochish when you need exact numbers.
        :param query: Search query. Use English or Russian keywords for international topics, Uzbek for local ones.
        :param max_results: Number of results (1-10).
        :param sahifalar: Optional: open this many top pages automatically (0-3). Default 0.
        :return: JSON with results (title, url, snippet) and extracts of the opened pages.
        """
        found = self._search(query, max_results)
        k = max(0, min(int(sahifalar or 0), 3))
        if k == 0 or not found.startswith("["):
            return found
        try:
            items = json.loads(found)
        except Exception:
            return found
        # Eng yaxshi sahifalarni parallel ochamiz (10 soniyada ulgurganlari bilan)
        from concurrent.futures import ThreadPoolExecutor, wait

        words = set(re.findall(r"\w{4,}", query.lower()))
        urls = [it["url"] for it in items if it.get("url") and not re.search(r"youtube|facebook|instagram|tiktok", it["url"])][:k]

        def grab(u):
            txt = _fast_fetch(u)
            if txt.startswith("XATO"):
                return None
            return {"url": u, "matn": _relevant(txt.split("\n\n", 1)[-1], words, 2500)}

        ex = ThreadPoolExecutor(3)
        futs = [ex.submit(grab, u) for u in urls]
        done, _ = wait(futs, timeout=6)
        ex.shutdown(wait=False, cancel_futures=True)
        pages = [f.result() for f in futs if f in done and f.result()]
        return json.dumps({"natijalar": items, "ochilgan_sahifalar": pages}, ensure_ascii=False)

    def _search(self, query: str, max_results: int = 6) -> str:
        n = max(1, min(int(max_results), 10))
        res, errors = [], []
        # 1) O'zimizning SearXNG (bir nechta qidiruv tizimi bir vaqtda)
        try:
            # Til ko'rsatilmasa SearXNG natijalari ancha yomon (sinovda): kirill — ruscha, aks holda inglizcha
            lang = "ru-RU" if re.search(r"[а-яёўқғҳА-ЯЁЎҚҒҲ]", query) else "en-US"
            d = requests.get(SEARXNG, params={"q": query, "format": "json", "language": lang}, timeout=20).json()
            if len(d.get("results", [])) < 3:
                d = requests.get(SEARXNG, params={"q": query, "format": "json"}, timeout=20).json()
            seen = set()
            for r in d.get("results", []):
                if r.get("url") in seen:
                    continue
                seen.add(r.get("url"))
                res.append({"title": r.get("title"), "href": r.get("url"), "body": r.get("content", "")})
                if len(res) >= n:
                    break
        except Exception as e:
            errors.append(f"searxng: {str(e)[:80]}")
        if res:
            return json.dumps(
                [{"title": r["title"], "url": r["href"], "snippet": r["body"]} for r in res], ensure_ascii=False
            )

        # 2) Zaxira: ddgs orqali qidiruv tizimlarini navbat bilan sinaymiz
        from ddgs import DDGS

        for backend in ("duckduckgo", "brave", "google", "mojeek", "yahoo", "auto"):
            try:
                res = list(DDGS(timeout=12).text(query, max_results=n, backend=backend))
            except Exception as e:
                errors.append(f"{backend}: {str(e)[:80]}")
                continue
            res = [r for r in res if "bing.com/aclick" not in r.get("href", "")]
            if res:
                break
        if not res:
            return ("Hech narsa topilmadi (" + "; ".join(errors[-2:]) + "). So'rovni boshqacha so'zlar bilan "
                    "yoki boshqa tilda (inglizcha/ruscha) qayta qidirib ko'r. Baribir topilmasa, foydalanuvchiga ochiq ayt.")
        return json.dumps(
            [{"title": r.get("title"), "url": r.get("href"), "snippet": r.get("body")} for r in res],
            ensure_ascii=False,
        )

    def chuqur_tadqiqot(self, sorovlar: list[str], sahifalar_soni: int = 8) -> str:
        """
        Deep research: runs several web searches in parallel, automatically OPENS the best result pages and returns
        their extracted text. Use for questions that need multiple sources: comparisons, reports, prices, laws, market
        analysis, "chuqur o'rgan", "tadqiqot qil". Base the answer ONLY on the returned page texts and cite their URLs.
        :param sorovlar: 3-6 different search queries covering sub-questions (mix Uzbek, Russian and English).
        :param sahifalar_soni: How many pages to open in total (4-12).
        :return: Page extracts with URLs.
        """
        from concurrent.futures import ThreadPoolExecutor

        sorovlar = [q for q in (sorovlar or []) if q][:6]
        if not sorovlar:
            return "XATO: kamida bitta so'rov bering."
        n = max(4, min(int(sahifalar_soni), 12))
        with ThreadPoolExecutor(6) as ex:
            found = list(ex.map(lambda q: self._search(q, 6), sorovlar))
        urls, seen = [], set()
        for raw in found:
            try:
                items = json.loads(raw)
            except Exception:
                continue
            for it in items:
                u = it.get("url") or ""
                dom = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
                if not u or u in seen or any(b in dom for b in ("youtube.", "facebook.", "instagram.", "tiktok.")):
                    continue
                seen.add(u)
                urls.append((u, it.get("title") or ""))
        # Turli saytlardan olishga harakat: har bir domendan 2 tadan ko'p emas
        picked, per_dom = [], {}
        for u, t in urls:
            dom = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
            if per_dom.get(dom, 0) < 2:
                per_dom[dom] = per_dom.get(dom, 0) + 1
                picked.append((u, t))
            if len(picked) >= n:
                break

        # So'rovlardagi so'zlar: sahifadan faqat shu so'zlar uchraydigan paragraflarni olamiz
        words = {w for q in sorovlar for w in re.findall(r"\w{4,}", q.lower())}

        def relevant(text, limit=2500):
            paras = [p.strip() for p in re.split(r"\n\s*\n|\n", text) if len(p.strip()) > 40]
            scored = [(sum(w in p.lower() for w in words) + (1 if re.search(r"\d", p) else 0), i, p)
                      for i, p in enumerate(paras)]
            best = sorted([s for s in scored if s[0] > 0], key=lambda s: -s[0])
            out, size = [], 0
            for s in best:
                if size + len(s[2]) > limit:
                    continue
                out.append(s)
                size += len(s[2])
            if not out:
                return text[:limit]
            return "\n".join(p for _, _, p in sorted(out, key=lambda s: s[1]))

        def grab(ut):
            u, t = ut
            txt = _fast_fetch(u)
            if txt.startswith("XATO"):
                return None
            body = relevant(txt.split("\n\n", 1)[-1])
            return f"### MANBA: {t}\nURL: {u}\n{body}"

        # 20 soniyada ochilgan sahifalar bilan ishlaymiz — sekin saytlarni kutib o'tirmaymiz
        from concurrent.futures import wait

        ex = ThreadPoolExecutor(8)
        futs = [ex.submit(grab, p) for p in picked]
        done, _ = wait(futs, timeout=8)
        ex.shutdown(wait=False, cancel_futures=True)
        pages = [f.result() for f in futs if f in done and f.result()]
        if not pages:
            return "Hech qanday sahifani ochib bo'lmadi. Foydalanuvchiga buni ochiq ayt."
        return (f"{len(pages)} ta manba ochildi. Faqat shu matnlarga tayan, har bir fakt uchun URL ko'rsat. "
                "Manbalarda yo'q raqamni yozma.\n\n" + "\n\n".join(pages))

    def brauzer(
        self,
        amal: str,
        url: str = "",
        matn: str = "",
        joy: str = "",
        x: int = -1,
        y: int = -1,
        tugma: str = "",
        yonalish: str = "pastga",
        __chat_id__: str = "",
    ) -> str:
        """
        Control a real Chromium browser (renders JavaScript). Use it when sahifani_ochish returns empty/incomplete text
        (dynamic sites: e-commerce, banks, railway/airline tickets, maps), or when you must interact with a page:
        fill a search box, press buttons, open menus, scroll. The browser keeps state between calls in this chat.
        Every call returns the page URL, title, visible text, links and a screenshot link.
        :param amal: Action: "ochish" (open url), "bosish" (click element by its visible text `matn`, or by x,y),
                     "yozish" (type `matn` into field whose placeholder/label is `joy`; empty joy = focused field),
                     "tugma" (press key `tugma`, e.g. Enter, Tab, Escape), "aylantirish" (scroll, yonalish=pastga|yuqoriga),
                     "korish" (look at current page again), "yopish" (close browser session).
        :param url: URL for "ochish".
        :param matn: Text to click (bosish) or to type (yozish).
        :param joy: Placeholder or label of the input field for "yozish".
        :param x: X coordinate for clicking (optional, with y).
        :param y: Y coordinate for clicking (optional, with x).
        :param tugma: Key name for "tugma".
        :param yonalish: "pastga" or "yuqoriga" for scrolling.
        :return: JSON with url, title, page text, links and screenshot URL, or an error.
        """
        body = {"sessiya": __chat_id__ or "asosiy", "amal": amal, "url": url or None, "matn": matn or None,
                "joy": joy or None, "tugma": tugma or None, "yonalish": yonalish}
        if x >= 0 and y >= 0:
            body.update(x=int(x), y=int(y))
        try:
            r = requests.post(BRAUZER, json=body, timeout=90).json()
        except Exception as e:
            return f"XATO: brauzer xizmati javob bermadi ({e})."
        return json.dumps(r, ensure_ascii=False)

    def chatdagi_fayllar(self, __files__: list = None) -> str:
        """
        List files the user attached to this chat (Excel, Word, PDF, CSV, images) with their paths inside the
        execute_code environment. Call this first whenever you need to process an attached file with Python code,
        then open it in execute_code by the returned path (e.g. pd.read_excel(path)).
        :return: JSON list of attached files with name and path.
        """
        out = []
        for f in __files__ or []:
            info = f.get("file") or f
            path = info.get("path") or (info.get("meta") or {}).get("path") or ""
            name = info.get("filename") or f.get("name") or (info.get("meta") or {}).get("name") or ""
            if path:
                out.append({"nomi": name, "yol": "/yuklanganlar/" + path.rsplit("/", 1)[-1]})
        if not out:
            return "Bu chatga hech qanday fayl biriktirilmagan. Foydalanuvchidan faylni chatga yuklashni so'ra."
        return json.dumps(out, ensure_ascii=False)

    def valyuta_kursi(self, valyuta: str = "USD", sana: str = "") -> str:
        """
        Official exchange rates of the Central Bank of Uzbekistan (cbu.uz) to UZS. Use this for any exchange rate question
        instead of web search.
        :param valyuta: Currency code like USD, EUR, RUB, CNY, KZT, GBP, or "all" for every currency.
        :param sana: Optional date YYYY-MM-DD for historical rate; empty means the latest official rate.
        :return: JSON with currency, rate in UZS, change and the official date.
        """
        v = (valyuta or "USD").strip().upper()
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/" + ("all" if v == "ALL" else v) + "/"
        if sana:
            url += sana.strip() + "/"
        try:
            data = requests.get(url, headers=UA, timeout=20).json()
        except Exception as e:
            return f"XATO: Markaziy bank sayti javob bermadi ({e})."
        if not data:
            return f"'{v}' valyutasi topilmadi."
        out = [{"valyuta": d["Ccy"], "nomi": d["CcyNm_UZ"], "nominal": d["Nominal"], "kurs_som": d["Rate"],
                "ozgarish": d["Diff"], "sana": d["Date"]} for d in data]
        return json.dumps({"manba": "O'zbekiston Respublikasi Markaziy banki (cbu.uz)", "kurslar": out}, ensure_ascii=False)

    def sahifani_ochish(self, url: str) -> str:
        """
        Open a web page and return its readable text. Use it to read a link the user gave, or a search result,
        before describing its content. Never describe a page you have not opened with this tool.
        For GitHub repositories prefer github_korish.
        :param url: Full URL starting with http:// or https://
        :return: Page text (truncated) or an error message.
        """
        try:
            r = requests.get(url, headers=UA, timeout=12)
            r.raise_for_status()
        except Exception as e:
            # Sayt oddiy so'rovni bloklagan bo'lishi mumkin: haqiqiy brauzer bilan urinib ko'ramiz
            try:
                b = requests.post(BRAUZER, json={"sessiya": "sahifa", "amal": "ochish", "url": url}, timeout=30).json()
                if b.get("holat") == "ok" and b.get("matn"):
                    return f"URL: {b.get('url')}\n\n{b['matn']}\n\n[Brauzerda ochildi. Skrinshot: {b.get('skrinshot')}]"
            except Exception:
                pass
            return f"XATO: sahifa ochilmadi ({e}). Foydalanuvchiga ocha olmaganingni ochiq ayt, mazmunini taxmin qilma."
        ctype = r.headers.get("content-type", "")
        text = _clean_html(r.text) if "html" in ctype else r.text
        # JavaScript bilan chiziladigan sahifa: matn juda kam bo'lsa, haqiqiy brauzerda ochamiz
        if "html" in ctype and len(text) < 1500:
            try:
                b = requests.post(BRAUZER, json={"sessiya": "sahifa", "amal": "ochish", "url": url}, timeout=30).json()
                if b.get("holat") == "ok" and len(b.get("matn", "")) > len(text):
                    text = b["matn"] + f"\n\n[Brauzerda ochildi. Skrinshot: {b.get('skrinshot')}]"
            except Exception:
                pass
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + "\n\n[... matn qisqartirildi]"
        return f"URL: {url}\n\n{text}"

    def github_korish(self, repo_url: str, path: str = "") -> str:
        """
        Inspect a public GitHub repository: with empty path returns description, languages, full file tree and README;
        with a file path returns that file's source code; with a folder path lists the folder.
        Call it several times to read the important source files before analysing a project.
        :param repo_url: Repository URL, e.g. https://github.com/owner/repo
        :param path: Optional file or folder path inside the repo, e.g. src/main.py
        :return: Repository information or file content.
        """
        m = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", repo_url)
        if not m:
            return "XATO: GitHub havolasi noto'g'ri."
        owner, repo = m.group(1), m.group(2).removesuffix(".git")
        try:
            zf = _repo_zip(owner, repo)
        except Exception as e:
            return f"XATO: repozitoriyni yuklab bo'lmadi ({e}). U yopiq (private) yoki mavjud emas bo'lishi mumkin."
        names = zf.namelist()
        root = names[0].split("/")[0] + "/"
        files = [n[len(root):] for n in names if n != root]
        path = path.strip("/")
        if path:
            if path in files:
                body = zf.read(root + path).decode("utf-8", errors="replace")
                if len(body) > MAX_CHARS:
                    body = body[:MAX_CHARS] + "\n\n[... fayl qisqartirildi]"
                return f"FAYL: {path}\n\n{body}"
            inside = [f for f in files if f.startswith(path + "/")]
            if inside:
                return f"PAPKA: {path}\n" + "\n".join(inside[:400])
            return f"XATO: '{path}' topilmadi."
        exts = {}
        for f in files:
            if "." in f.rsplit("/", 1)[-1] and not f.endswith("/"):
                e = f.rsplit(".", 1)[-1].lower()
                exts[e] = exts.get(e, 0) + 1
        readme = next((f for f in files if f.lower() in ("readme.md", "readme.rst", "readme.txt", "readme")), None)
        out = [
            f"REPO: {owner}/{repo}",
            "Fayl turlari: " + ", ".join(f"{k}({v})" for k, v in sorted(exts.items(), key=lambda x: -x[1])[:12]),
            f"Fayllar ({len(files)} ta):",
            "\n".join(files[:400]) + ("\n[... yana bor]" if len(files) > 400 else ""),
            "README:",
            zf.read(root + readme).decode("utf-8", errors="replace")[:6000] if readme else "(README yo'q)",
        ]
        return "\n".join(out)
