"""Sarob Telegram boti: Sarob agentiga telefondan ulanish.

- Faqat egasi bilan gaplashadi: birinchi /start yozgan odam egasi bo'ladi (owner.json), keyin bot qulflanadi.
- Miyasi: vLLM'dagi Gemma 4 (thinking), asboblari Open WebUI'dagi bilan bir xil (internet, bazalar)
  + kod bajarish Sarobning alohida kompyuterida (Open Terminal) — bot tokeni u yerga hech qachon tushmaydi.
- Yaratilgan fayllar (Excel, Word, grafik) Telegramga to'g'ridan-to'g'ri yuboriladi.
- Rejali vazifalar: har kuni ertalab hisobot va kamera uzilishlari haqida ogohlantirish.
"""
import asyncio, base64, contextvars, datetime as dt, json, logging, os, re, time, types, uuid

import requests
from telegram import BotCommand, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sarob-bot")
logging.getLogger("httpx").setLevel(logging.WARNING)  # aks holda URL ichidagi bot tokeni logga yoziladi

TOKEN = open("/run/secrets/telegram_token").read().strip()
TERMINAL_KEY = open("/run/secrets/terminal_key").read().strip()
LLM_URL = os.environ.get("SAROB_LLM", "http://127.0.0.1:8000/v1/chat/completions")
LLM_MODEL = os.environ.get("SAROB_MODEL", "gemma-4-26b")
TERMINAL = "http://127.0.0.1:8099"
FAYLLAR = "/fayllar"                       # = Open Terminal'dagi ~/fayllar = Spark ~/sarob/workspace/fayllar
STATE = "/data"                            # egasi, suhbat tarixi, kuzatuv holati
TZ = dt.timezone(dt.timedelta(hours=5))    # Toshkent vaqti
MAX_HISTORY = 12                           # oxirgi xabarlar soni (kontekst)

os.makedirs(STATE, exist_ok=True)


def load_module(path, name):
    m = types.ModuleType(name)
    exec(open(path, encoding="utf-8").read(), m.__dict__)
    return m.Tools()


NET = load_module("/tools/tool_internet.py", "tool_internet")
DB = load_module("/tools/tool_baza.py", "tool_baza")

# Rasmlardan Excel: Open WebUI'dagi bilan bir xil asbob, natija bot papkasiga yoziladi
OUT = f"{STATE}/out"
os.makedirs(OUT, exist_ok=True)
_rasm = types.ModuleType("tool_rasm")
exec(open("/tools/tool_rasm.py", encoding="utf-8").read(), _rasm.__dict__)
_rasm.OUT_DIR = OUT
RASM = _rasm.Tools()
CURRENT_CHAT = contextvars.ContextVar("chat_id", default=None)


def rasm_dir(chat_id):
    d = f"{STATE}/rasmlar/{chat_id}"
    os.makedirs(d, exist_ok=True)
    return d


def rasmlardan_excel(fayl_nomi: str = "jadval", shart: str = "", usul: str = "aniq") -> str:
    """Bu suhbatda yuborilgan barcha rasmlardagi jadvallarni bitta Excel faylga yig'adi."""
    d = rasm_dir(CURRENT_CHAT.get())
    imgs = sorted(os.listdir(d))
    if not imgs:
        return "Bu suhbatda rasm yo'q. Foydalanuvchidan jadval skrinshotlarini yuborishni so'ra."
    files = [{"file": {"path": os.path.join(d, f), "filename": f, "meta": {"content_type": "image/jpeg"}}} for f in imgs]
    r = RASM.rasmlardan_excel(fayl_nomi, shart, usul, __files__=files)
    return r.replace(_rasm.PUBLIC, "(Telegramga yuboriladi)")


# ---------------------------------------------------------------- egasi (faqat bitta foydalanuvchi)
def owner_id():
    try:
        return json.load(open(f"{STATE}/owner.json"))["id"]
    except Exception:
        return None


def is_owner(update: Update) -> bool:
    return update.effective_user is not None and update.effective_user.id == owner_id()


# ---------------------------------------------------------------- kod bajarish (Open Terminal)
def run_python(code: str) -> str:
    """Kodni Sarobning alohida kompyuterida (Open Terminal) bajaradi."""
    h = {"Authorization": f"Bearer {TERMINAL_KEY}"}
    path = f"/home/user/.sarob_run/{uuid.uuid4().hex[:8]}.py"
    try:
        requests.post(f"{TERMINAL}/files/write", headers=h, json={"path": path, "content": code}, timeout=20).raise_for_status()
        r = requests.post(f"{TERMINAL}/execute", headers=h, timeout=20,
                          json={"command": f"cd ~/fayllar && timeout 120 python3 {path}; echo __EXIT__$?"}).json()
        pid, deadline = r["id"], time.time() + 130
        while time.time() < deadline:
            s = requests.get(f"{TERMINAL}/execute/{pid}/status", headers=h, timeout=20).json()
            if s.get("status") != "running":
                out = "".join(o.get("data", "") for o in s.get("output", []))
                code_m = re.search(r"__EXIT__(\d+)", out)
                out = re.sub(r"__EXIT__\d+\s*$", "", out).strip()[-6000:]
                status = "ok" if code_m and code_m.group(1) == "0" else "error"
                return json.dumps({"status": status, "output": out}, ensure_ascii=False)
            time.sleep(1)
        return json.dumps({"status": "error", "output": "vaqt tugadi (120 s)"})
    except Exception as e:
        return json.dumps({"status": "error", "output": f"kod muhiti javob bermadi: {e}"})


FUNCS = {
    "internetdan_qidirish": NET.internetdan_qidirish,
    "sahifani_ochish": NET.sahifani_ochish,
    "github_korish": NET.github_korish,
    "valyuta_kursi": NET.valyuta_kursi,
    "chuqur_tadqiqot": NET.chuqur_tadqiqot,
    "bazalar_tuzilishi": DB.bazalar_tuzilishi,
    "baza_sorov": DB.baza_sorov,
    "execute_code": run_python,
    "rasmlardan_excel": rasmlardan_excel,
}


def spec(fn, name, props, req):
    return {"type": "function", "function": {"name": name, "description": (fn.__doc__ or "").strip(),
            "parameters": {"type": "object", "properties": props, "required": req}}}


S = {"type": "string"}
TOOLS = [
    spec(NET.internetdan_qidirish, "internetdan_qidirish", {"query": S, "max_results": {"type": "integer"}, "sahifalar": {"type": "integer"}}, ["query"]),
    spec(NET.sahifani_ochish, "sahifani_ochish", {"url": S}, ["url"]),
    spec(NET.github_korish, "github_korish", {"repo_url": S, "path": S}, ["repo_url"]),
    spec(NET.valyuta_kursi, "valyuta_kursi", {"valyuta": S, "sana": S}, []),
    spec(NET.chuqur_tadqiqot, "chuqur_tadqiqot", {"sorovlar": {"type": "array", "items": S}, "sahifalar_soni": {"type": "integer"}}, ["sorovlar"]),
    spec(DB.bazalar_tuzilishi, "bazalar_tuzilishi", {"baza": S}, []),
    spec(DB.baza_sorov, "baza_sorov", {"baza": S, "sql": S}, ["baza", "sql"]),
    {"type": "function", "function": {"name": "execute_code",
     "description": "Execute Python code in Sarob's own Linux computer (pandas, openpyxl, xlsxwriter, python-docx, "
                    "matplotlib, reportlab). Working dir is ~/fayllar: save every file for the user THERE "
                    "(e.g. 'hisobot.xlsx', 'grafik.png') — it is sent to Telegram automatically.",
     "parameters": {"type": "object", "properties": {"code": S}, "required": ["code"]}}},
    {"type": "function", "function": {"name": "rasmlardan_excel",
     "description": (_rasm.Tools.rasmlardan_excel.__doc__ or "").strip(),
     "parameters": {"type": "object", "properties": {"fayl_nomi": S, "shart": S,
                                                     "usul": {"type": "string", "enum": ["aniq", "hujjat"]}},
                    "required": []}}},
]

TELEGRAM_RULES = """

## Telegram rejimi (bu suhbat Telegram orqali)
- Javoblar qisqa bo'lsin (telefon ekrani). Jadvalni kam ustunli qil.
- Fayl va grafiklar: `execute_code` ichida joriy papkaga saqla (masalan `hisobot.xlsx`, `grafik.png`, `plt.show()` emas). Fayl foydalanuvchiga AVTOMATIK yuboriladi — havola yozma, faqat "faylni yubordim" de.
- Brauzer va terminal asboblari bu yerda yo'q."""


def system_prompt():
    p = open("/tools/sarob_prompt.md", encoding="utf-8").read()
    now = dt.datetime.now(TZ)
    p = p.replace("{{CURRENT_DATE}}", now.strftime("%Y-%m-%d")).replace("{{CURRENT_WEEKDAY}}", now.strftime("%A"))
    return p + TELEGRAM_RULES


_tez = types.ModuleType("filter_tezlik")
exec(open("/tools/filter_tezlik.py", encoding="utf-8").read(), _tez.__dict__)
TEZLIK = _tez.Filter()  # Open WebUI'dagi bilan bir xil: savol turiga qarab o'ylash chegarasi (32 / 512 / 1024)


def llm(messages, tools=True):
    body = {"model": LLM_MODEL, "messages": messages, "temperature": 0.3, "max_tokens": 4096,
            "chat_template_kwargs": {"enable_thinking": True}}
    body = TEZLIK.request(body)
    if tools:
        body["tools"] = TOOLS
    r = requests.post(LLM_URL, json=body, timeout=600)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]


def agent(history, user_content, chat_id=None):
    """Agent tsikli: model asbob chaqiradi, natijani oladi, tugaguncha davom etadi."""
    CURRENT_CHAT.set(chat_id)
    msgs = [{"role": "system", "content": system_prompt()}] + history + [{"role": "user", "content": user_content}]
    said, retried = [], False
    for _ in range(10):
        msg = llm(msgs)
        calls = msg.get("tool_calls") or []
        raw = msg.get("content") or ""
        if not calls and _tez.has_fake_tool_call(raw) and not retried:
            # Model asbobni haqiqatan chaqirmay, matn sifatida "chaqirgan" — bir marta tuzatib qayta so'raymiz
            retried = True
            log.info("soxta asbob chaqiruvi aniqlandi, qayta so'ralmoqda")
            msgs.append({"role": "user", "content": "[Tizim: siz asbob chaqiruvini oddiy matn sifatida yozdingiz, u bajarilmadi. "
                                                    "Asbobni haqiqiy function call orqali chaqiring.]"})
            continue
        msg["content"] = _tez.clean_leak(raw)
        msgs.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls") and v})
        if (msg.get("content") or "").strip():
            said.append(msg["content"].strip())
        if not calls:
            break
        for c in calls:
            fn, args = c["function"]["name"], c["function"]["arguments"]
            try:
                res = FUNCS[fn](**json.loads(args))
            except Exception as e:
                res = f"XATO: {e}"
            log.info("asbob %s(%s)", fn, args[:120])
            msgs.append({"role": "tool", "tool_call_id": c["id"], "content": str(res)[:20000]})
    return "\n\n".join(said) or "Kechirasiz, javob tayyorlay olmadim."


# ---------------------------------------------------------------- suhbat tarixi
def hist_path(chat_id):
    return f"{STATE}/tarix_{chat_id}.json"


def load_hist(chat_id):
    try:
        return json.load(open(hist_path(chat_id)))
    except Exception:
        return []


def save_hist(chat_id, h):
    json.dump(h[-MAX_HISTORY:], open(hist_path(chat_id), "w"), ensure_ascii=False)


def new_files_since(t0):
    out = []
    for d in (FAYLLAR, OUT):
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p) and os.path.getmtime(p) >= t0 - 1:
                out.append(p)
    return sorted(out, key=os.path.getmtime)


# Doimiy tugmalar: buyruqlarni eslab qolish shart emas
BTN_KURS, BTN_KAMERA, BTN_HARORAT, BTN_YANGI = "💵 Kurs", "📹 Kameralar", "🌡️ Harorat", "✨ Yangi suhbat"
BTN_KUZATUV = "🔔 Kamera kuzatuvi"
KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton(BTN_KURS), KeyboardButton(BTN_KAMERA)],
     [KeyboardButton(BTN_HARORAT), KeyboardButton(BTN_KUZATUV)],
     [KeyboardButton(BTN_YANGI)]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Savolingizni yozing yoki tugmani bosing")


async def send_long(bot, chat_id, text):
    parts = [text[i:i + 3900] for i in range(0, len(text), 3900)] or ["…"]
    for n, part in enumerate(parts):
        markup = KEYBOARD if n == len(parts) - 1 and chat_id == owner_id() else None
        try:
            await bot.send_message(chat_id, part, parse_mode="Markdown", reply_markup=markup)
        except Exception:
            await bot.send_message(chat_id, part, reply_markup=markup)  # Markdown xato bo'lsa, oddiy matn


async def keep_typing(bot, chat_id, stop: asyncio.Event):
    while not stop.is_set():
        try:
            await bot.send_chat_action(chat_id, ChatAction.TYPING)
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop.wait(), timeout=4)
        except asyncio.TimeoutError:
            pass


async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    chat_id = update.effective_chat.id
    text = update.message.text or update.message.caption or ""
    # Tugmalar
    if text == BTN_KURS:
        return await send_long(ctx.bot, chat_id, await asyncio.to_thread(kurs_text))
    if text == BTN_KAMERA:
        return await hisobot(update, ctx)
    if text == BTN_HARORAT:
        return await harorat(update, ctx)
    if text == BTN_KUZATUV:
        return await kuzatuv(update, ctx)
    if text == BTN_YANGI:
        return await yangi(update, ctx)
    content = text
    doc = update.message.document
    is_img_doc = bool(doc and (doc.mime_type or "").startswith("image/"))
    if update.message.photo or is_img_doc:
        # Rasm: suhbat papkasiga saqlaymiz. Albom (bir nechta rasm) bo'lsa, hammasi kelguncha kutib, bir marta javob beramiz
        f = await (doc.get_file() if is_img_doc else update.message.photo[-1].get_file())
        ext = ".png" if is_img_doc and (doc.mime_type or "").endswith("png") else ".jpg"
        name = f"{time.time():.3f}_{update.message.message_id}{ext}"
        with open(os.path.join(rasm_dir(chat_id), name), "wb") as fh:
            fh.write(bytes(await f.download_as_bytearray()))
        gid = update.message.media_group_id
        if gid:
            key = f"album_{chat_id}_{gid}"
            pend = ctx.chat_data.setdefault(key, {"caption": "", "n": 0})
            pend["n"] += 1
            pend["caption"] = pend["caption"] or text
            if pend["n"] == 1:
                ctx.job_queue.run_once(album_done, 3.0, data={"chat_id": chat_id, "key": key}, chat_id=chat_id)
            return
        return await run_and_reply(ctx.bot, chat_id, image_request(chat_id, text, 1))
    if update.message.document:  # hujjat: Sarob kompyuteriga saqlaymiz
        d = update.message.document
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", d.file_name or "fayl")
        f = await d.get_file()
        raw = bytes(await f.download_as_bytearray())
        h = {"Authorization": f"Bearer {TERMINAL_KEY}"}
        # Matnli bo'lmagan fayllarni base64 qilib yozamiz va terminalda dekodlaymiz
        requests.post(f"{TERMINAL}/files/write", headers=h, timeout=60,
                      json={"path": f"/home/user/yuklangan/{safe}.b64", "content": base64.b64encode(raw).decode()})
        requests.post(f"{TERMINAL}/execute", headers=h, timeout=20,
                      json={"command": f"base64 -d ~/yuklangan/{safe}.b64 > ~/yuklangan/{safe} && rm ~/yuklangan/{safe}.b64"})
        content = f"{text or 'Bu faylni tahlil qil.'}\n\n[Foydalanuvchi fayl yubordi: /home/user/yuklangan/{safe} — execute_code ichida shu yo'l bilan och]"
    await run_and_reply(ctx.bot, chat_id, content, text)


def image_request(chat_id, text, n_new):
    """Rasm(lar) kelganda modelga beriladigan so'rov: oxirgi 3 tasini ko'rsatamiz, hammasi asbob uchun saqlangan."""
    d = rasm_dir(chat_id)
    imgs = sorted(os.listdir(d))
    note = (f"[Foydalanuvchi {n_new} ta rasm yubordi (bu suhbatda jami {len(imgs)} ta saqlangan). "
            "Jadvalni Excel/CSV/jadvalga o'tkazish so'ralsa — FAQAT `rasmlardan_excel` asbobini chaqir. "
            "Boshqa savol bo'lsa, quyidagi rasmlarga qarab javob ber.]")
    content = [{"type": "text", "text": (text or "Bu rasmda nima bor? Matn bo'lsa o'qib ber.") + "\n\n" + note}]
    for f in imgs[-min(n_new, 3):]:
        data = base64.b64encode(open(os.path.join(d, f), "rb").read()).decode()
        mime = "image/png" if f.endswith(".png") else "image/jpeg"
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}})
    return content


async def album_done(ctx: ContextTypes.DEFAULT_TYPE):
    data = ctx.job.data
    pend = ctx.application.chat_data[data["chat_id"]].pop(data["key"], None)
    if pend:
        await run_and_reply(ctx.bot, data["chat_id"], image_request(data["chat_id"], pend["caption"], pend["n"]),
                            pend["caption"] or f"[{pend['n']} ta rasm]")


async def run_and_reply(bot, chat_id, content, text_for_history=None):
    stop = asyncio.Event()
    typing = asyncio.create_task(keep_typing(bot, chat_id, stop))
    t0 = time.time()
    hist = load_hist(chat_id)
    try:
        answer = await asyncio.to_thread(agent, hist, content, chat_id)
    except Exception as e:
        log.exception("agent xatosi")
        answer = f"Xatolik yuz berdi: {e}"
    finally:
        stop.set()
        await typing
    answer = re.sub(r"!?\[([^\]]*)\]\(http://192\.168\.136\.153:8090/[^)]*\)", r"📎 \1", answer)
    await send_long(bot, chat_id, answer)
    for p in new_files_since(t0):
        with open(p, "rb") as fh:
            if p.lower().endswith((".png", ".jpg", ".jpeg")):
                await bot.send_photo(chat_id, fh, caption=os.path.basename(p))
            else:
                await bot.send_document(chat_id, fh, filename=os.path.basename(p))
    hist_text = text_for_history if text_for_history is not None else (content if isinstance(content, str) else "[rasm]")
    hist += [{"role": "user", "content": hist_text or "[rasm/fayl]"}, {"role": "assistant", "content": answer[:4000]}]
    save_hist(chat_id, hist)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if owner_id() is None:
        json.dump({"id": u.id, "name": u.full_name, "since": time.time()}, open(f"{STATE}/owner.json", "w"))
        log.info("Egasi belgilandi: %s (%s)", u.full_name, u.id)
        await update.message.reply_text(
            f"Salom, {u.first_name}! Men Sarobman 🌅\nSiz endi mening egamsiz — boshqa hech kim men bilan gaplasha olmaydi.\n\n"
            "Savolingizni yozing, rasm yoki fayl yuboring. Tez-tez kerak bo'ladiganlar pastdagi tugmalarda 👇",
            reply_markup=KEYBOARD)
    elif is_owner(update):
        await update.message.reply_text("Men shu yerdaman 🙂 Savol yozing yoki pastdagi tugmalardan foydalaning 👇",
                                        reply_markup=KEYBOARD)


async def post_init(app: Application):
    # Telegram'dagi "/" menyusi — buyruqlar izohi bilan
    await app.bot.set_my_commands([
        BotCommand("start", "Tugmalarni ko'rsatish"),
        BotCommand("hisobot", "Kameralar hisoboti"),
        BotCommand("harorat", "Spark harorati"),
        BotCommand("kuzatuv", "Kamera ogohlantirishlarini yoqish/o'chirish"),
        BotCommand("yangi", "Yangi suhbat (eski suhbatni unutish)"),
    ])
    # Tugmalar versiyasi yangilangan bo'lsa, egasiga bir marta ko'rsatamiz
    ver_f = f"{STATE}/keyboard_ver"
    if owner_id() and (not os.path.exists(ver_f) or open(ver_f).read() != "1"):
        open(ver_f, "w").write("1")
        await app.bot.send_message(owner_id(), "🆕 Pastda tugmalar paydo bo'ldi — endi buyruqlarni eslab qolish shart emas 👇",
                                   reply_markup=KEYBOARD)


async def yangi(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_owner(update):
        save_hist(update.effective_chat.id, [])
        d = rasm_dir(update.effective_chat.id)
        for f in os.listdir(d):  # yangi suhbat — eski rasmlar ham unutiladi
            os.remove(os.path.join(d, f))
        await update.message.reply_text("Yangi suhbat boshlandi ✨")


# ---------------------------------------------------------------- rejali vazifalar
def camera_report():
    """Jonli bazadan (bo'lmasa nusxadan) kamera holati hisoboti uchun ma'lumot."""
    return agent([], "Kamera bazasidan (avval jonli PostgreSQL, bo'lmasa nusxa) qisqa kunlik hisobot tayyorla: "
                     "jami kameralar, hozir onlayn/oflayn (agar aniqlash mumkin bo'lsa), oxirgi 24 soatda eng ko'p "
                     "uzilgan 5 ta kamera. Faqat bazadagi raqamlar. Qisqa, telefon uchun.")


def kurs_text():
    """Markaziy bank kurslari: USD, EUR, RUB (sanasi bilan)."""
    try:
        rows = {k["valyuta"]: k for k in json.loads(NET.valyuta_kursi("all"))["kurslar"]}
        out = [f"💵 *Markaziy bank kursi* ({rows['USD']['sana']})"]
        for v, icon in (("USD", "🇺🇸"), ("EUR", "🇪🇺"), ("RUB", "🇷🇺")):
            k = rows[v]
            out.append(f"{icon} 1 {v} = {k['kurs_som']} so'm ({'+' if not k['ozgarish'].startswith('-') else ''}{k['ozgarish']})")
        return "\n".join(out)
    except Exception:
        return "💵 Kursni olib bo'lmadi"


async def morning(ctx: ContextTypes.DEFAULT_TYPE):
    oid = owner_id()
    if not oid:
        return
    kurs_txt = await asyncio.to_thread(kurs_text)
    rep = await asyncio.to_thread(camera_report)
    await send_long(ctx.bot, oid, f"☀️ *Xayrli tong!*\n{kurs_txt}\n\n📹 *Kameralar:*\n{rep}")


async def hisobot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_owner(update):
        await update.message.reply_text("Hisobot tayyorlanyapti... ⏳")
        await send_long(ctx.bot, update.effective_chat.id, await asyncio.to_thread(camera_report))


def kuzatuv_on():
    return os.path.exists(f"{STATE}/kuzatuv.on")


async def kuzatuv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    if kuzatuv_on():
        os.remove(f"{STATE}/kuzatuv.on")
        await update.message.reply_text("🔕 Kamera ogohlantirishlari o'chirildi.")
    else:
        open(f"{STATE}/kuzatuv.on", "w").write("1")
        await update.message.reply_text("🔔 Kamera ogohlantirishlari yoqildi: kamera uzilsa yoki qayta ulansa xabar beraman.")


async def watch_cameras(ctx: ContextTypes.DEFAULT_TYPE):
    """Har 2 daqiqada jonli bazadagi yangi offline/online hodisalarini tekshiradi."""
    oid = owner_id()
    if not oid or not kuzatuv_on():
        return
    names = [n.split(" ")[0] for n in DB.bazalar_tuzilishi().replace("Mavjud bazalar: ", "").split(", ")]
    baza = next((n for n in names if n.endswith("_jonli")), None)
    if not baza:
        return
    last_f = f"{STATE}/kuzatuv_last.txt"
    last = open(last_f).read().strip() if os.path.exists(last_f) else ""
    if not last:  # birinchi ishga tushishda faqat joriy nuqtani eslab qolamiz
        r = json.loads(DB.baza_sorov(baza, "SELECT max(id) FROM events"))
        open(last_f, "w").write(str(r["qatorlar"][0][0] or 0))
        return
    r = DB.baza_sorov(baza, f"SELECT id, ts, kind, slug, detail FROM events WHERE id > {int(last)} "
                            "AND kind IN ('offline','online') ORDER BY id LIMIT 50")
    if r.startswith("XATO"):
        return
    d = json.loads(r)
    if not d["qatorlar"]:
        return
    open(last_f, "w").write(str(d["qatorlar"][-1][0]))
    lines = [("🔴" if k == "offline" else "🟢") + f" {slug or '?'} — {k} ({str(ts)[11:16]})"
             for _, ts, k, slug, _ in d["qatorlar"]]
    await send_long(ctx.bot, oid, "📹 *Kamera holati o'zgardi:*\n" + "\n".join(lines[:30]))


# ---------------------------------------------------------------- harorat kuzatuvi
GPU_LIMIT, BOARD_LIMIT = 85, 90          # °C
THERMAL_BITS = 0x8 | 0x20 | 0x40 | 0x80  # HW slowdown, SW/HW thermal slowdown, power brake


def read_temp():
    try:
        d = json.load(open(f"{STATE}/harorat.json"))
    except Exception:
        return None
    d["stale"] = time.time() - d.get("ts", 0) > 300
    try:
        d["throttle"] = bool(int(d.get("reasons", "0x0"), 16) & THERMAL_BITS)
    except ValueError:
        d["throttle"] = False
    return d


def temp_text(d):
    return (f"🌡️ GPU: *{d['gpu']} °C*, plata: *{d['board']} °C*\n⚡ Quvvat: {d['power']} W, yuklama: {d['util']}%\n"
            + ("🐢 Qizib ketgani uchun SEKINLASHGAN!" if d["throttle"] else "✅ Sekinlashish yo'q"))


async def harorat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    d = read_temp()
    if not d:
        await update.message.reply_text("Harorat ma'lumoti hali yo'q.")
        return
    await send_long(ctx.bot, update.effective_chat.id,
                    temp_text(d) + ("\n⚠️ Ma'lumot eskirgan (kuzatuv skripti ishlamayapti)" if d["stale"] else ""))


async def watch_temp(ctx: ContextTypes.DEFAULT_TYPE):
    """Har daqiqada tekshiradi; muammo bo'lsa xabar beradi (30 daqiqada bir martadan ko'p emas), tiklanganda ham aytadi."""
    oid, d = owner_id(), read_temp()
    if not oid or not d or d["stale"]:
        return
    hot = d["gpu"] >= GPU_LIMIT or d["board"] >= BOARD_LIMIT or d["throttle"]
    flag, last_f = f"{STATE}/harorat_alert", f"{STATE}/harorat_last"
    if hot:
        last = float(open(last_f).read()) if os.path.exists(last_f) else 0
        if time.time() - last > 1800:
            open(last_f, "w").write(str(time.time()))
            open(flag, "w").write("1")
            await send_long(ctx.bot, oid, "🔥 *Spark qizib ketyapti!*\n" + temp_text(d)
                            + "\n\nShamollatishni tekshiring: atrofida bo'sh joy bormi, havo teshiklari to'silmaganmi?")
    elif os.path.exists(flag) and d["gpu"] < GPU_LIMIT - 10:
        os.remove(flag)
        await send_long(ctx.bot, oid, "✅ Spark harorati normal holatga qaytdi.\n" + temp_text(d))


def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yangi", yangi))
    app.add_handler(CommandHandler("hisobot", hisobot))
    app.add_handler(CommandHandler("kuzatuv", kuzatuv))
    app.add_handler(CommandHandler("harorat", harorat))
    app.job_queue.run_repeating(watch_temp, interval=60, first=45)
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND, handle))
    app.job_queue.run_daily(morning, time=dt.time(8, 30, tzinfo=TZ))
    app.job_queue.run_repeating(watch_cameras, interval=120, first=30)
    log.info("Sarob boti ishga tushdi")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
