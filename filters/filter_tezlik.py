"""
title: Sarob tezlik filtri
description: Har bir model chaqiruvidan oldin savol turiga qarab o'ylash chegarasini tanlaydi (oddiy suhbat — kam, mantiq — ko'p).
version: 1.0
"""

import re

# Oddiy suhbat: salomlashish, minnatdorchilik, xayrlashish, holat so'rash
CHAT = re.compile(r"^\W*(salom|assalomu|assalom|hello|hi|привет|здравствуй|rahmat|raxmat|tashakkur|spasibo|спасибо|"
                  r"xayr|ko'rishguncha|qalaysan|qalesan|qandaysan|yaxshimisan|ishlayapsanmi|ishlayabsanmi|ok|okey|"
                  r"tushunarli|zo'r|ajoyib|yaxshi|mayli|ha|yo'q)\b", re.I)
# Oddiy (murakkab emas) savollar uchun o'ylash chegarasi
DEFAULT_BUDGET = 512
# Bitta so'rovdagi rasmlar chegarasi (Gemma va Pro serverlarida --limit-mm-per-prompt image=32)
MAX_IMAGES = 32

# Sarobning o'zi haqidagi savollar (kimsan, nima qila olasan, qanday yordam bera olasan) — o'ylash kerak emas
META = re.compile(r"(\bkimsan\b|sen kim|isming|o'zingni tanishtir|nima(lar)? qila olasan|nima(lar)?ni bilasan|"
                  r"qanday yordam|yordam bera olasan|nimaga qodirsan|imkoniyatlaring|nima ish qila|"
                  r"кто ты|что ты умеешь|who are you|what can you do)", re.I)
# Matnni o'zgartirish (tarjima, tahrir) — fikrlash kam kerak
REWRITE = re.compile(r"(tarjima|ruschaga|inglizchaga|o'zbekchaga|lotinga|kirillga|переведи|imlo|xatolarini tuzat|"
                     r"qisqartir|soddalashtir|qayta yoz)", re.I)
# Mantiq, hisob, tuzoq savollar — ko'proq o'ylash kerak
HARD = re.compile(r"(\d+\s*[-+*/x×÷%^]\s*\d+|hisobla|isbotla|nega |nima uchun|tenglama|masala|mantiq|"
                  r"agar .+ bo'lsa|qaysi biri|maqulmi|ma'qulmi|to'g'rimi|reja tuz|kod yoz)", re.I)
# "nechta/qancha" — faqat savolda raqamlar ham bo'lsa (masalan, "10 ta sham ... nechta qoladi?") mantiqiy masala
COUNT = re.compile(r"(nechta|necha|qancha|qanchasi)", re.I)


# O'ylash chegarasiga yetganda model ba'zan fikrlarini va soxta asbob chaqiruvlarini oddiy matn sifatida yozadi
LEAK_BLOCK = re.compile(r"<(thought|tool_call|think)>.*?</\1>\s*", re.S | re.I)
LEAK_OPEN = re.compile(r"^\s*<(thought|think)>.*?(\n\s*\n|$)", re.S | re.I)
LEAK_TAGS = re.compile(r"</?(thought|tool_call|think)>|<\|channel>|<channel\|>", re.I)


def clean_leak(text: str) -> str:
    if not text or "<" not in text:
        return text
    t = LEAK_BLOCK.sub("", text)
    t = LEAK_OPEN.sub("", t)
    return LEAK_TAGS.sub("", t).strip()


def has_fake_tool_call(text: str) -> bool:
    return bool(text) and "<tool_call>" in text


def _last_user_text(messages):
    for m in reversed(messages or []):
        if m.get("role") == "user":
            c = m.get("content")
            if isinstance(c, list):
                return " ".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text"), \
                    any(isinstance(p, dict) and p.get("type") == "image_url" for p in c)
            return str(c or ""), False
    return "", False


class Filter:
    def __init__(self):
        pass

    def _budget(self, body):
        msgs = body.get("messages") or []
        text, has_img = _last_user_text(msgs)
        t = text.strip().lower()
        after_tool = bool(msgs) and msgs[-1].get("role") == "tool"
        if after_tool:
            return None                      # asbob natijasidan keyin — model sozlamasidagi standart (512)
        if has_img:
            return 1024                      # rasmdagi masala/jadval ko'pincha murakkab: 512 da o'ylash kesilib, javobga oqqan
        if len(t.split()) <= 4 and CHAT.match(t) and not re.search(r"\d", t):
            return 32                        # salom / rahmat — deyarli o'ylamaydi
        if META.search(t) and len(t.split()) <= 10 and not HARD.search(t):
            return 32                        # o'zi haqida savol — tayyor javob, o'ylash shart emas
        if REWRITE.search(t) and len(t) < 600 and not HARD.search(t):
            return 32                        # tarjima / tahrir
        if HARD.search(t) or (COUNT.search(t) and len(re.findall(r"\d+", t)) >= 2):
            return 1024                      # mantiq / hisob / tuzoq
        return None

    def inlet(self, body: dict, __metadata__: dict = None) -> dict:
        # Kod bajarish (execute_code) har doim yoqiq bo'lsin: chatdagi "Code Interpreter" tugmasi o'chiq qolsa,
        # Open WebUI asbobni bermaydi, prompt esa undan foydalanishni buyuradi -> "Tool not found" va halqa.
        # Asbob ro'yxati metadata["features"] dan tuziladi, shuning uchun ikkalasini ham yoqamiz.
        # (Sarob Tez'da model imkoniyati o'chiq — u yerda baribir berilmaydi.)
        try:
            for d in (body, __metadata__):
                if isinstance(d, dict):
                    if not isinstance(d.get("features"), dict):
                        d["features"] = {}
                    d["features"]["code_interpreter"] = True
        except Exception:
            pass
        return body

    def _cap_images(self, body):
        """Butun suhbat tarixidagi rasmlar vLLM chegarasidan (--limit-mm-per-prompt) oshmasin:
        eng oxirgi MAX_IMAGES ta rasm qoladi, eskilari matnli belgi bilan almashtiriladi.
        Aks holda chatda rasm ko'payganda har bir yangi savol "At most N image(s)" xatosini beradi."""
        msgs = body.get("messages") or []
        seen = 0
        for m in reversed(msgs):
            c = m.get("content")
            if not isinstance(c, list):
                continue
            new = []
            for p in reversed(c):
                if isinstance(p, dict) and p.get("type") == "image_url":
                    seen += 1
                    if seen > MAX_IMAGES:
                        p = {"type": "text", "text": "[oldingi rasm olib tashlandi]"}
                new.append(p)
            m["content"] = list(reversed(new))

    def request(self, body: dict, __user__: dict = None, __model__: dict = None) -> dict:
        # Eslatma: Open WebUI model parametrlarini (custom_params) bu filtrdan KEYIN qo'llaydi,
        # shuning uchun thinking_token_budget model sozlamalarida bo'lmasligi kerak — uni faqat shu filtr belgilaydi.
        try:
            self._cap_images(body)
        except Exception:
            pass
        try:
            ids = " ".join(str(x) for x in (body.get("model"), (__model__ or {}).get("id"),
                                            ((__model__ or {}).get("info") or {}).get("base_model_id")))
            default = 1024 if ("pro" in ids.lower() or "qwen" in ids.lower()) else DEFAULT_BUDGET
            b = self._budget(body)
            body["thinking_token_budget"] = b if b is not None else default
            body["max_tokens"] = max(int(body.get("max_tokens") or 0), body["thinking_token_budget"] + 2048)
            # Halqadan himoya: 24+ tokenli bo'lak ketma-ket 5 marta takrorlansa, generatsiya to'xtaydi
            # (sinovda jadvallarni kesmadi, halqani 5-takrordan keyin to'xtatdi)
            body["repetition_detection"] = {"max_pattern_size": 256, "min_pattern_size": 24, "min_count": 5}
        except Exception:
            pass
        return body

    def outlet(self, body: dict, __user__: dict = None) -> dict:
        # Javob tugagach: matnga aralashgan o'ylash va soxta asbob chaqiruvlarini tozalaymiz
        try:
            for m in body.get("messages") or []:
                if m.get("role") == "assistant" and isinstance(m.get("content"), str):
                    m["content"] = clean_leak(m["content"])
        except Exception:
            pass
        return body
