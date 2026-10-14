"""Tezlik o'lchovi: haqiqiy Sarob prompti + asboblar bilan birinchi token vaqti (TTFT) va tok/s."""
import json, sys, time, types, urllib.request

URL, MODEL, PROMPT = sys.argv[1], sys.argv[2], sys.argv[3]
THINK = len(sys.argv) > 4 and sys.argv[4] == "1"
mod = types.ModuleType("t")
exec(open("/home/dasuty/sarob/tool_internet.py", encoding="utf-8").read(), mod.__dict__)
T = mod.Tools()
tools = [{"type": "function", "function": {"name": n, "description": getattr(T, n).__doc__.strip(),
          "parameters": {"type": "object", "properties": {"q": {"type": "string"}}}}}
         for n in ("internetdan_qidirish", "sahifani_ochish", "github_korish", "valyuta_kursi", "chuqur_tadqiqot",
                   "brauzer", "chatdagi_fayllar")]
system = open(PROMPT, encoding="utf-8").read().replace("{{CURRENT_DATE}}", "2026-10-13") \
    .replace("{{CURRENT_WEEKDAY}}", "Tuesday").replace("{{CURRENT_TIME}}", time.strftime("%H:%M:%S"))


def run(q):
    body = {"model": MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": q}],
            "tools": tools, "max_tokens": 400, "temperature": 0.3, "stream": True, "stream_options": {"include_usage": True}}
    if THINK:
        body["chat_template_kwargs"] = {"enable_thinking": True}
    t0 = time.time(); first = None; usage = None
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data: ") or line.endswith("[DONE]"):
                continue
            d = json.loads(line[6:])
            usage = d.get("usage") or usage
            for ch in d.get("choices", []):
                dl = ch.get("delta", {})
                if first is None and (dl.get("content") or dl.get("reasoning_content") or dl.get("reasoning")):
                    first = time.time()
    t1 = time.time()
    n = usage["completion_tokens"]
    print(f"  {q[:28]:28s} prompt={usage['prompt_tokens']:5d}  TTFT={first - t0:5.2f}s  "
          f"gen={n / (t1 - first):5.1f} tok/s  jami={t1 - t0:5.1f}s")


for q in ["salom", "salom!", "Excel'da VLOOKUP qanday ishlaydi? Qisqa tushuntir.",
          "Toshkentdagi eng mashhur 5 ta tarixiy joyni sanab ber."]:
    run(q)
