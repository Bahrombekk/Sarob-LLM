"""Prefix kesh ishlayaptimi? Bir xil uzun promptni bir necha marta yuborib, keshdan olingan tokenlarni o'lchaydi."""
import json, sys, time, urllib.request

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
MODEL = sys.argv[2] if len(sys.argv) > 2 else "gemma-4-26b"
system = open("/home/dasuty/sarob/sarob_prompt.md", encoding="utf-8").read().replace("{{CURRENT_DATE}}", "2026-10-13") \
    .replace("{{CURRENT_WEEKDAY}}", "Tuesday")
history = "Oldingi suhbat: " + ("Toshkent haqida batafsil ma'lumot. " * 600)  # ~8k token


def metrics():
    t = urllib.request.urlopen(f"{URL}/metrics").read().decode()
    g = lambda k: sum(float(l.split()[-1]) for l in t.splitlines() if l.startswith(k))
    return g("vllm:prefix_cache_hits_total"), g("vllm:prefix_cache_queries_total")


def ask(q):
    h0, q0 = metrics()
    body = {"model": MODEL, "max_tokens": 20, "temperature": 0,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": history},
                         {"role": "assistant", "content": "Tushundim."}, {"role": "user", "content": q}]}
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        f"{URL}/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=300))
    dt = time.time() - t
    h1, q1 = metrics()
    cached = (r["usage"].get("prompt_tokens_details") or {}).get("cached_tokens")
    print(f"  {q[:30]:30s} prompt={r['usage']['prompt_tokens']:6d} cached_tokens={cached} "
          f"kesh_hit={(h1 - h0) / max(1, q1 - q0):5.1%} vaqt={dt:5.2f}s")


for q in ["Birinchi savol: salom", "Birinchi savol: salom", "Ikkinchi savol: rahmat", "Uchinchi savol: xayr"]:
    ask(q)
