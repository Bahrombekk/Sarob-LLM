import json, time, urllib.request

URL = "http://127.0.0.1:8000/v1/chat/completions"
SYSTEM = open("/home/dasuty/sarob_prompt.md", encoding="utf-8").read()
QUESTIONS = [
    "O'zingni tanishtir, kimsan va nimalar qila olasan?",
    "Amir Temur haqida 5 jumlada qisqacha ma'lumot ber.",
    "Kichik do'kon uchun oylik foyda-zarar hisobotini Excelda qanday tuzish kerak? Ustunlar va formulalarni ayt.",
]

for q in QUESTIONS:
    body = json.dumps({
        "model": "gemma-4-26b",
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}],
        "max_tokens": 600, "temperature": 0.7, "stream": True,
        "stream_options": {"include_usage": True},
    }).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    t0 = time.time(); first = None; text = ""; usage = None
    with urllib.request.urlopen(req, timeout=300) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            d = json.loads(line[6:])
            if d.get("usage"):
                usage = d["usage"]
            for ch in d.get("choices", []):
                c = ch["delta"].get("content") or ""
                if c and first is None:
                    first = time.time()
                text += c
    t1 = time.time()
    n = usage["completion_tokens"] if usage else 0
    print("=" * 70)
    print("SAVOL:", q)
    print("-" * 70)
    print(text.strip())
    print("-" * 70)
    print(f"[{n} token, {n / (t1 - (first or t0)):.1f} tok/s, birinchi token {((first or t1) - t0):.2f}s]")
