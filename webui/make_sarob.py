"""Open WebUI bazasida Sarob modellarini yaratadi (yoki yangilaydi): Sarob, Sarob Tez, Sarob Pro."""
import base64, json, os, sqlite3, sys, time

DB = "/app/backend/data/webui.db"
prompt = open(sys.argv[1], encoding="utf-8").read()
now = int(time.time())

c = sqlite3.connect(DB)
uid = c.execute("select id from user where role='admin' limit 1").fetchone()[0]

# Model avatari: Sarob logosi (data URI, har qanday sahifada ko'rinadi)
logo_path = "/app/build/static/favicon-96x96.png"
avatar = ("data:image/png;base64," + base64.b64encode(open(logo_path, "rb").read()).decode()
          if os.path.exists(logo_path) else "/static/favicon.png")

# Ishlatilmaydigan yoki o'zimizning asboblar bilan takrorlanadigan Open WebUI ichki asboblari o'chiriladi.
# Har bir asbob tavsifi har xabarda modelga yuboriladi, shuning uchun ortiqchasi javobni sekinlashtiradi.
BUILTIN_OFF = {k: False for k in (
    "automations", "calendar", "channels", "chats", "image_generation", "notes", "notifications",
    "skills", "subagents", "tasks", "time", "user_input", "web_search", "files",
)}

meta = {
    "profile_image_url": avatar,
    "capabilities": {
        "vision": True, "file_upload": True, "web_search": False, "image_generation": False,
        "code_interpreter": True, "citations": True, "usage": True, "status_updates": True, "memory": True,
        "terminal": False,
    },
    "suggestion_prompts": [
        {"content": "Bu Excel fayldagi ma'lumotlarni tahlil qilib, qisqa hisobot tayyorla"},
        {"content": "Rasmdagi matnni o'qib, Word faylga yozib ber"},
        {"content": "Bugungi dollar kursi qancha?"},
        {"content": "Menga rasmiy xat namunasini Word formatida tayyorla"},
    ],
    "tags": [{"name": "sarob"}],
    "toolIds": ["sarob_internet", "sarob_baza", "sarob_rasm"],
    "builtinTools": dict(BUILTIN_OFF),
    "filterIds": ["sarob_tezlik", "sarob_yengil"],
    "defaultFeatureIds": ["code_interpreter", "memory"],
}
params = {
    "system": prompt,
    "temperature": 0.3,
    "top_p": 0.95,
    "max_tokens": 8192,
    "function_calling": "native",
}


def upsert(model_id, name, description, extra_params, base="gemma-4-26b", **meta_over):
    m = dict(meta, description=description, **meta_over)
    p = dict(params, **extra_params)
    c.execute(
        "insert into model (id,user_id,base_model_id,name,meta,params,created_at,updated_at,is_active) values (?,?,?,?,?,?,?,?,1) "
        "on conflict(id) do update set user_id=excluded.user_id, base_model_id=excluded.base_model_id, name=excluded.name, "
        "meta=excluded.meta, params=excluded.params, updated_at=excluded.updated_at",
        (model_id, uid, base, name, json.dumps(m), json.dumps(p), now, now),
    )


# Asosiy: o'ylab javob beradi (aniqroq)
upsert("sarob", "Sarob", "O'ylab, tekshirib javob beradi: hujjatlar, Excel/Word, rasmlar, internet, xotira",
       {"custom_params": {"chat_template_kwargs": {"enable_thinking": True}}})

# Tez: asboblarsiz, o'ylamasdan — suhbat, tarjima, matn tahriri
TEZ_PROMPT = (
    "Sening isming Sarob. Sen egangning shaxsiy yordamchisisan va uning DGX Spark serverida lokal ishlaysan. "
    "Bugun: {{CURRENT_DATE}}. Doim o'zbek tilida (lotin yozuvida), qisqa va aniq javob ber. "
    "Javobdan oldin savolni diqqat bilan o'qi: foydalanuvchining ASL MAQSADI nima va unga erishish uchun nima shart "
    "(kim yoki nima qayerda bo'lishi kerak)? Ko'zga tashlanadigan tafsilotlarga (masofa, son) emas, maqsadga qarab "
    "mantiqiy javob ber. Ichki fikrlashni qisqa qil. "
    "Bilmagan narsangni o'ylab topma: yangi ma'lumot (kurs, yangilik, narx) kerak bo'lsa, "
    "foydalanuvchiga \"Sarob\" modelini tanlashni tavsiya qil, chunki u internetdan qidira oladi."
)
upsert("sarob-tez", "Sarob Tez", "Tez javob: suhbat, tarjima, matn tahriri, mantiqiy savollar (internet va fayllarsiz)",
       {"system": TEZ_PROMPT,
        "custom_params": {"chat_template_kwargs": {"enable_thinking": True}}},
       toolIds=[], defaultFeatureIds=[],
       builtinTools=dict(BUILTIN_OFF, code_interpreter=False, knowledge=False),
       capabilities=dict(meta["capabilities"], code_interpreter=False))

# Pro: Qwen3.8 (eng aqlli) + shaxsiy Linux kompyuter (terminal)
upsert("sarob-pro", "Sarob Pro", "Eng aqlli agent (Qwen3.8): murakkab tadqiqot, kod, o'z kompyuterida ishlaydi. Sekinroq.",
       {"temperature": 0.4}, base="qwen3.8-27b",
       terminalId="sarob-terminal", capabilities=dict(meta["capabilities"], terminal=True))

c.execute("insert into config (key, value, updated_at) values ('ui.default_models', ?, ?) "
          "on conflict(key) do update set value=excluded.value, updated_at=excluded.updated_at",
          (json.dumps("sarob"), now))
c.commit()
print("Sarob, Sarob Tez, Sarob Pro tayyor")
