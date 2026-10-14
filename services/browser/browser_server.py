"""Sarob brauzeri: haqiqiy Chromium (Playwright) orqali sahifalarni ochish va boshqarish.

API (faqat 127.0.0.1): POST /amal  {"sessiya": "...", "amal": "...", ...}
Amallar: ochish(url), bosish(matn | x,y), yozish(matn, joy), tugma(tugma), aylantirish(yonalish), korish(), yopish()
Har bir amaldan keyin sahifaning matni va skrinshot havolasi qaytadi.
"""
import asyncio, os, re, time, uuid

from fastapi import FastAPI
from playwright.async_api import async_playwright
from pydantic import BaseModel

SHOTS = "/workspace/fayllar/skrinshot"
PUBLIC = "http://192.168.136.153:8090/skrinshot"
MAX_TEXT = 12000
IDLE_SEC = 900  # 15 daqiqa ishlatilmagan sessiya yopiladi

os.makedirs(SHOTS, exist_ok=True)
app = FastAPI()
state = {"pw": None, "browser": None, "sessions": {}}
lock = asyncio.Lock()


class Amal(BaseModel):
    sessiya: str = "asosiy"
    amal: str
    url: str | None = None
    matn: str | None = None
    joy: str | None = None
    x: int | None = None
    y: int | None = None
    tugma: str | None = None
    yonalish: str | None = "pastga"


async def browser():
    if state["browser"] is None or not state["browser"].is_connected():
        state["pw"] = state["pw"] or await async_playwright().start()
        state["browser"] = await state["pw"].chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    return state["browser"]


async def page_for(sid: str):
    s = state["sessions"].get(sid)
    if s is None or s["page"].is_closed():
        ctx = await (await browser()).new_context(
            viewport={"width": 1366, "height": 900}, locale="uz-UZ",
            user_agent="Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36",
        )
        s = {"ctx": ctx, "page": await ctx.new_page()}
        state["sessions"][sid] = s
    s["used"] = time.time()
    return s["page"]


async def snapshot(page, note=""):
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    name = f"{time.strftime('%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
    await page.screenshot(path=f"{SHOTS}/{name}")
    text = await page.evaluate("() => document.body ? document.body.innerText : ''")
    text = re.sub(r"\n\s*\n+", "\n\n", text or "").strip()
    links = await page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]')).slice(0, 60)
             .map(a => (a.innerText || '').trim().slice(0, 60) + ' -> ' + a.href).filter(t => t.length > 5)"""
    )
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT] + "\n[... matn qisqartirildi]"
    return {
        "holat": "ok", "izoh": note, "url": page.url, "sarlavha": await page.title(),
        "skrinshot": f"{PUBLIC}/{name}", "matn": text, "havolalar": links[:40],
    }


@app.post("/amal")
async def amal(a: Amal):
    async with lock:
        try:
            if a.amal == "yopish":
                s = state["sessions"].pop(a.sessiya, None)
                if s:
                    await s["ctx"].close()
                return {"holat": "ok", "izoh": "sessiya yopildi"}
            page = await page_for(a.sessiya)
            if a.amal == "ochish":
                await page.goto(a.url, wait_until="domcontentloaded", timeout=45000)
            elif a.amal == "bosish":
                if a.x is not None and a.y is not None:
                    await page.mouse.click(a.x, a.y)
                else:
                    await page.get_by_text(a.matn, exact=False).first.click(timeout=10000)
            elif a.amal == "yozish":
                # Maydonni bir necha usulda qidiramiz: placeholder, label, keyin istalgan ko'rinadigan qidiruv/matn maydoni
                candidates = []
                if a.joy:
                    candidates += [page.get_by_placeholder(a.joy, exact=False), page.get_by_label(a.joy, exact=False),
                                   page.get_by_role("textbox", name=a.joy), page.get_by_role("searchbox", name=a.joy)]
                candidates += [page.locator("input[type=search]:visible"), page.get_by_role("searchbox"),
                               page.locator("input[name*=q]:visible, input[name*=search]:visible, input[id*=search]:visible"),
                               page.locator("input[type=text]:visible, textarea:visible")]
                done = False
                for loc in candidates:
                    try:
                        if await loc.count() > 0:
                            await loc.first.fill(a.matn or "", timeout=4000)
                            done = True
                            break
                    except Exception:
                        continue
                if not done:
                    await page.keyboard.type(a.matn or "", delay=20)
            elif a.amal == "tugma":
                await page.keyboard.press(a.tugma or "Enter")
            elif a.amal == "aylantirish":
                await page.mouse.wheel(0, 800 if (a.yonalish or "pastga") == "pastga" else -800)
            elif a.amal != "korish":
                return {"holat": "xato", "izoh": f"noma'lum amal: {a.amal}"}
            await asyncio.sleep(1.0)
            return await snapshot(page, a.amal)
        except Exception as e:
            return {"holat": "xato", "izoh": f"{type(e).__name__}: {str(e)[:300]}"}


@app.on_event("startup")
async def cleanup_loop():
    async def loop():
        while True:
            await asyncio.sleep(60)
            now = time.time()
            for sid, s in list(state["sessions"].items()):
                if now - s.get("used", now) > IDLE_SEC:
                    state["sessions"].pop(sid, None)
                    await s["ctx"].close()
            # eski skrinshotlarni (1 kundan oshgan) o'chirish
            for f in os.listdir(SHOTS):
                p = f"{SHOTS}/{f}"
                if now - os.path.getmtime(p) > 86400:
                    os.remove(p)
    asyncio.create_task(loop())
