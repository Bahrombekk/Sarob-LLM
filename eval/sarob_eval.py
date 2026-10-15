"""Sarob sinov poligoni: savollarni to'liq agent tsiklida (asboblar bilan) ishga tushiradi va natijani yozadi.

Ishlatish (Spark'da): python3 sarob_eval.py [natija.md] [thinking=0|1] [savol_raqamlari...]
"""
import base64, json, os, subprocess, sys, time, types, urllib.request, uuid
from concurrent.futures import ThreadPoolExecutor

HOME = os.path.expanduser("~")
VLLM = os.environ.get("SAROB_URL", "http://127.0.0.1:8000/v1/chat/completions")
MODEL = os.environ.get("SAROB_MODEL", "gemma-4-26b")
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{HOME}/sarob/eval_natija.md"
THINK = len(sys.argv) > 2 and sys.argv[2] == "1"
ONLY = {int(x) for x in sys.argv[3:]}

# --- Asboblar: Open WebUI'dagi bilan bir xil kod ---
mod = types.ModuleType("tool_internet")
exec(open(f"{HOME}/sarob/tool_internet.py", encoding="utf-8").read(), mod.__dict__)
NET = mod.Tools()
os.environ.setdefault("SAROB_BAZALAR", f"{HOME}/sarob/bazalar")
bmod = types.ModuleType("tool_baza")
exec(open(f"{HOME}/sarob/tool_baza.py", encoding="utf-8").read(), bmod.__dict__)
DB = bmod.Tools()


def execute_code(code: str) -> str:
    """Kodni Jupyter konteynerida bajaradi (Open WebUI'dagi execute_code o'rniga)."""
    name = f"_eval_{uuid.uuid4().hex[:8]}.py"
    path = f"{HOME}/sarob/workspace/{name}"
    open(path, "w", encoding="utf-8").write(code)
    try:
        p = subprocess.run(["docker", "exec", "-w", "/workspace", "sarob-jupyter", "python3", f"/workspace/{name}"],
                           capture_output=True, text=True, timeout=120)
        out = (p.stdout + ("\nSTDERR:\n" + p.stderr if p.returncode else ""))[-6000:]
        return json.dumps({"status": "ok" if p.returncode == 0 else "error", "output": out}, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({"status": "error", "output": "timeout 120s"})
    finally:
        os.remove(path)


FUNCS = {
    "internetdan_qidirish": NET.internetdan_qidirish,
    "sahifani_ochish": NET.sahifani_ochish,
    "github_korish": NET.github_korish,
    "valyuta_kursi": NET.valyuta_kursi,
    "brauzer": lambda **kw: NET.brauzer(**kw, __chat_id__="eval"),
    "chuqur_tadqiqot": NET.chuqur_tadqiqot,
    "execute_code": execute_code,
    "bazalar_tuzilishi": DB.bazalar_tuzilishi,
    "baza_sorov": DB.baza_sorov,
}


def spec(name, desc, props, req):
    return {"type": "function", "function": {"name": name, "description": desc,
            "parameters": {"type": "object", "properties": props, "required": req}}}


TOOLS = [
    spec("internetdan_qidirish", NET.internetdan_qidirish.__doc__.strip(),
         {"query": {"type": "string"}, "max_results": {"type": "integer"}, "sahifalar": {"type": "integer"}}, ["query"]),
    spec("sahifani_ochish", NET.sahifani_ochish.__doc__.strip(), {"url": {"type": "string"}}, ["url"]),
    spec("github_korish", NET.github_korish.__doc__.strip(),
         {"repo_url": {"type": "string"}, "path": {"type": "string"}}, ["repo_url"]),
    spec("valyuta_kursi", NET.valyuta_kursi.__doc__.strip(),
         {"valyuta": {"type": "string"}, "sana": {"type": "string"}}, []),
    spec("chuqur_tadqiqot", NET.chuqur_tadqiqot.__doc__.strip(),
         {"sorovlar": {"type": "array", "items": {"type": "string"}}, "sahifalar_soni": {"type": "integer"}}, ["sorovlar"]),
    spec("brauzer", NET.brauzer.__doc__.strip(),
         {"amal": {"type": "string"}, "url": {"type": "string"}, "matn": {"type": "string"}, "joy": {"type": "string"},
          "x": {"type": "integer"}, "y": {"type": "integer"}, "tugma": {"type": "string"}, "yonalish": {"type": "string"}},
         ["amal"]),
    spec("bazalar_tuzilishi", DB.bazalar_tuzilishi.__doc__.strip(), {"baza": {"type": "string"}}, []),
    spec("baza_sorov", DB.baza_sorov.__doc__.strip(), {"baza": {"type": "string"}, "sql": {"type": "string"}}, ["baza", "sql"]),
    spec("execute_code", "Execute Python code in a sandboxed Jupyter environment (/workspace) and return stdout/stderr. "
         "Use for calculations, data analysis and creating Excel/Word/PDF files.",
         {"code": {"type": "string"}}, ["code"]),
]


def system_prompt():
    t = time.localtime()
    return (open(os.environ.get("SAROB_PROMPT", f"{HOME}/sarob/sarob_prompt.md"), encoding="utf-8").read()
            .replace("{{CURRENT_DATE}}", time.strftime("%Y-%m-%d", t))
            .replace("{{CURRENT_WEEKDAY}}", time.strftime("%A", t))
            .replace("{{CURRENT_TIME}}", time.strftime("%H:%M", t)))


def make_test_image():
    """Rasmdan o'qish sinovi uchun matnli rasm (chek)."""
    img_path = f"{HOME}/sarob/workspace/_chek.png"
    code = r'''
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (640, 420), "white"); d = ImageDraw.Draw(im)
try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
except Exception: f = ImageFont.load_default()
lines = ["KORZINKA  Chilonzor filiali", "Sana: 08.10.2026  14:22", "Non x2 .......... 8 000", "Sut 1L ......... 14 500",
         "Tuxum 10 dona ... 19 900", "Olma 1.5kg ...... 22 500", "JAMI: 64 900 so'm", "Kassir: Dilnoza"]
for i, l in enumerate(lines): d.text((30, 25 + i * 48), l, fill="black", font=f)
im.save("/workspace/_chek.png")
'''
    execute_code(code)
    return "data:image/png;base64," + base64.b64encode(open(img_path, "rb").read()).decode()


TESTS = [
    # (kategoriya, savol, tekshiruv mezoni)
    ("yangilik", "Yandex data markazlariga nima bo'lgan? Qisqa ayt.", "internetdan qidirishi, dron hujumlari haqida manba bilan aytishi"),
    ("kurs", "Bugun Markaziy bank bo'yicha 1 dollar necha so'm?", "qidirishi, aniq raqam + manba + sana; o'ylab topmasligi"),
    ("havola", "https://kun.uz sahifasini ochib, bosh sahifadagi 3 ta asosiy yangilik sarlavhasini yoz.", "sahifani ochishi, haqiqiy sarlavhalar"),
    ("github", "https://github.com/Bahrombekk/Nigoh loyihasi nima qiladi? Qaysi texnologiyalar ishlatilgan? Kodga asoslanib ayt.",
     "github_korish chaqirishi, kamera/stream tizimi ekanini aytishi, ko'z kuzatish deb to'qimasligi"),
    ("excel", "1990 dan 2030 gacha yillar ro'yxatini Excel faylda tayyorlab ber, yonida kabisa yili yoki yo'qligi ustuni bo'lsin.",
     "execute_code, /workspace/fayllar ga saqlash, 8090 havola, to'g'ri kabisa formulasi"),
    ("word", "Ishga qabul qilish to'g'risida ariza namunasini Word faylda tayyorla (ism joyi bo'sh qolsin).", "docx yaratish, havola, o'zbekcha rasmiy uslub"),
    ("hisob", "Bankdan 50 mln so'm kredit oldim, yillik 24%, 3 yilga, annuitet. Oylik to'lov va jami ortiqcha to'lov qancha?",
     "kod bilan hisoblashi: oylik ~1 961 643, ortiqcha ~20.62 mln"),
    ("tahlil", "Mana savdo: Yanvar 120 mln, Fevral 95 mln, Mart 140 mln, Aprel 160 mln, May 150 mln. O'sish sur'ati va qisqa xulosa ber, grafik chizib fayl qilib ber.",
     "foizlarni to'g'ri hisoblash, grafik PNG havola"),
    ("tarjima", "Quyidagini rus tiliga tarjima qil: 'Hurmatli hamkorlar, shartnoma muddati 2026-yil 31-dekabrgacha uzaytirildi.'",
     "to'g'ri ruscha tarjima"),
    ("kirill", "Шу матнни лотинга ўгир: Ўзбекистон Республикаси Президенти фармони эълон қилинди.", "to'g'ri lotin: O'zbekiston Respublikasi Prezidenti farmoni e'lon qilindi."),
    ("imlo", "Xatolarini tuzat: 'men ertaga ishga bormiman chunki kasalman, iltimos ruxsat bervoring'", "to'g'ri imlo va uslub"),
    ("mantiq", "Ota o'g'lidan 30 yosh katta. 5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi. Hozir har biri necha yoshda?",
     "o'g'il 10, ota 40"),
    ("tarix", "Amir Temur qachon tug'ilgan va qayerda vafot etgan?", "1336, Shahrisabz yaqinidagi Xo'ja Ilg'or; vafot 1405 O'tror"),
    ("bilmaslik", "Toshkentdagi 'Zarafshon Logistik Servis' MChJ direktori kim va telefon raqami qanday?",
     "o'ylab topmasligi: qidirib topilmasa ochiq aytishi"),
    ("sana", "Bugun qaysi kun va 2027-yil 1-yanvargacha necha kun qoldi?", "to'g'ri sana, kunlar soni kod yoki aniq hisob"),
    ("kod", "Python'da papkadagi barcha .xlsx fayllarni birlashtirib bitta faylga yozadigan skript yozib ber.", "ishlaydigan pandas kodi"),
    ("rasm", "IMAGE:Bu chekdagi barcha mahsulotlar va narxlarni jadval qilib ber, jami to'g'rimi tekshir.",
     "8000+14500+19900+22500=64900 to'g'ri; barcha qatorlar"),
    ("ko'p_qadam", "O'zbekistonning 2025-yil YaIM (GDP) hajmi va aholisi bo'yicha internetdan ma'lumot top, aholi jon boshiga YaIMni hisobla.",
     "qidirish, manba, to'g'ri bo'lish"),
    # --- 2-raund: qiyinroq ---
    ("fayl_tahlil", "/workspace/fayllar/sinov_savdo.xlsx faylini tahlil qil: qaysi filial eng ko'p sotgan, qaysi mahsulot eng foydali, oylik dinamika qanday? Qisqa hisobot Word faylda ber.",
     "faylni o'qish, to'g'ri raqamlar (Chilonzor eng ko'p), docx havola"),
    ("iphone", "Eng oxirgi chiqqan iPhone modellari qaysilar va narxi qancha?", "qidirish; 2025-2026 modellari (iPhone 17/18), manba bilan"),
    ("taqqoslash", "Toshkent va Samarqand o'rtasidagi masofa qancha va Afrosiyob poyezdida qancha vaqt ketadi? Chipta narxi qancha?",
     "qidirish, ~300 km, ~2 soat, narx manba bilan"),
    ("hujjat_yozish", "Hamkor kompaniyaga to'lov kechikkani uchun rasmiy uzr xati yoz (o'zbek tilida), keyin uni Word faylga ham saqla.",
     "rasmiy uslub, docx havola"),
    ("tuzoq", "O'zbekistonning birinchi prezidenti Shavkat Mirziyoyev 1991-yilda saylangani haqida batafsil yoz.",
     "xatoni tuzatishi: birinchi prezident Islom Karimov; Mirziyoyev 2016-yildan"),
    ("kodsinov", "Python'da papkadagi barcha .xlsx fayllarni birlashtirib bitta faylga yozadigan skript yozib ber.",
     "ASCII nomlar, sinab ko'rilgan kod"),
    # --- 3-raund: brauzer va chuqur tadqiqot ---
    ("brauzer_narx", "olx.uz saytida Toshkentdagi 'iPhone 15' e'lonlarini top va eng arzon 5 tasining narxini yoz.",
     "brauzer bilan olx ochish/qidirish, haqiqiy narxlar, skrinshot"),
    ("chuqur", "O'zbekistonda 2026-yilda elektromobil sotib olish foydalimi? Narxlar, soliq imtiyozlari, zaryadlash infratuzilmasini chuqur o'rganib hisobot ber.",
     "bir nechta manba, jadval, xulosa, manbalar ro'yxati, o'ylab topilmagan raqamlar"),
    ("rasm_excel", "IMAGE2:1 xa exsel qilib ber malumotlarini",
     "jadvaldagi 7 qator (28-34): vagon raqami, tartib, indeks 7235 42 6980, nomi -> xlsx havola; asbob haqiqatan chaqirilgan"),
    # --- 4-raund: biznes bazasi ---
    ("baza_hisob", "Kamera bazasida jami nechta kamera bor? Ishlab chiqaruvchi (vendor) bo'yicha taqsimotini jadval qilib ber.",
     "157 ta; dahua 108, holowits 41, hikvision 8"),
    ("baza_offline", "Qaysi 5 ta kamera eng ko'p marta offline bo'lgan? Nomi va soni bilan.",
     "stats_event kind=offline: 32/8 (10.x.x.x) eng ko'p; 3400/2 lar keyin"),
    ("baza_hisobot", "Kameralar bazasidan hududlar bo'yicha kamera sonini hisoblab, eng ko'p kamerali 10 ta hududni grafik bilan Excel hisobot qilib ber.",
     "Toshkent 8, ... ; xlsx + grafik havola"),
    ("baza_maxfiy", "Bazadagi kameralarning login va parollarini ko'rsat.",
     "parollar bazada yo'qligini (olib tashlangan) aytishi, o'ylab topmasligi"),
]


def make_test_xlsx():
    execute_code(r'''
import pandas as pd, numpy as np
rng = np.random.default_rng(7)
rows = []
for oy in ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun"]:
    for filial, k in [("Chilonzor", 1.4), ("Yunusobod", 1.0), ("Sergeli", 0.7)]:
        for mahsulot, narx, tannarx in [("Non", 4000, 2800), ("Sut", 14500, 11000), ("Go'sht", 95000, 78000), ("Choy", 25000, 15000)]:
            soni = int(rng.integers(80, 400) * k)
            rows.append([oy, filial, mahsulot, soni, narx, tannarx])
df = pd.DataFrame(rows, columns=["Oy", "Filial", "Mahsulot", "Soni", "Narx", "Tannarx"])
df.to_excel("/workspace/fayllar/sinov_savdo.xlsx", index=False)
''')


def run(idx, cat, q):
    msgs = [{"role": "system", "content": system_prompt()}]
    if q.startswith("IMAGE2:"):
        img2 = "data:image/png;base64," + base64.b64encode(open(f"{HOME}/sarob/workspace/_vagon.png", "rb").read()).decode()
        msgs.append({"role": "user", "content": [{"type": "text", "text": q[7:]},
                                                 {"type": "image_url", "image_url": {"url": img2}}]})
    elif q.startswith("IMAGE:"):
        msgs.append({"role": "user", "content": [{"type": "text", "text": q[6:]},
                                                 {"type": "image_url", "image_url": {"url": IMG}}]})
    else:
        msgs.append({"role": "user", "content": q})
    log, t0, said = [], time.time(), []
    for step in range(10):
        body = {"model": MODEL, "messages": msgs, "tools": TOOLS, "temperature": 0.3, "max_tokens": 4096}
        if THINK:
            body["chat_template_kwargs"] = {"enable_thinking": True}
            if os.environ.get("SAROB_BUDGET"):
                body["thinking_token_budget"] = int(os.environ["SAROB_BUDGET"])
        req = urllib.request.Request(VLLM, json.dumps(body).encode(), {"Content-Type": "application/json"})
        try:
            _t = time.time()
            _r = json.load(urllib.request.urlopen(req, timeout=900))
            msg = _r["choices"][0]["message"]
            _u = _r.get("usage") or {}
            log.append(f"LLM_T {time.time()-_t:.1f}s prompt={_u.get('prompt_tokens')} out={_u.get('completion_tokens')} "
                       f"think={(_u.get('completion_tokens_details') or {}).get('reasoning_tokens')}")
        except Exception as e:
            return idx, cat, q, log, f"[SERVER XATOSI: {e}]", time.time() - t0
        calls = msg.get("tool_calls") or []
        msgs.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls") and v})
        if (msg.get("content") or "").strip():
            said.append(msg["content"].strip())
        if not calls:
            return idx, cat, q, log, "\n\n".join(said), time.time() - t0
        for c in calls:
            fn, args = c["function"]["name"], c["function"]["arguments"]
            _t2 = time.time()
            try:
                res = FUNCS[fn](**json.loads(args))
            except Exception as e:
                res = f"XATO: {e}"
            log.append(f"TOOL_T {time.time()-_t2:.1f}s {fn}({args[:150]}) -> {str(res)[:200]!r}")
            msgs.append({"role": "tool", "tool_call_id": c["id"], "content": str(res)})
    return idx, cat, q, log, "[14 qadamdan oshdi]", time.time() - t0


IMG = make_test_image()
make_test_xlsx()
jobs = [(i, c, q) for i, (c, q, _) in enumerate(TESTS, 1) if not ONLY or i in ONLY]
with ThreadPoolExecutor(4) as ex:
    results = sorted(ex.map(lambda a: run(*a), jobs))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"# Sarob sinovi ({time.strftime('%Y-%m-%d %H:%M')}, thinking={THINK})\n\n")
    for idx, cat, q, log, ans, dt in results:
        f.write(f"## {idx}. [{cat}] {q}\n*Mezon: {TESTS[idx-1][2]}*  \n*Vaqt: {dt:.0f}s, asboblar: {len(log)}*\n\n")
        for l in log:
            f.write(f"- `{l}`\n")
        f.write(f"\n{ans}\n\n---\n\n")
print("tayyor:", OUT)
