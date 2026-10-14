"""MTP taxminchisi tillar bo'yicha: qabul qilish uzunligi va tok/s (o'zbekcha / inglizcha / ruscha)."""
import json, time, urllib.request

PROMPTS = {
    "o'zbekcha": "Toshkent shahri tarixi, madaniyati va iqtisodiyoti haqida batafsil maqola yoz (o'zbek tilida, lotin yozuvida).",
    "inglizcha": "Write a detailed article about the history, culture and economy of Tashkent city (in English).",
    "ruscha": "Напиши подробную статью об истории, культуре и экономике города Ташкента (на русском языке).",
}


def metrics():
    t = urllib.request.urlopen("http://127.0.0.1:8000/metrics").read().decode()
    g = lambda k: sum(float(l.split()[-1]) for l in t.splitlines() if l.startswith(k))
    return g("vllm:spec_decode_num_accepted_tokens_total"), g("vllm:spec_decode_num_drafts_total")


for lang, p in PROMPTS.items():
    acc, dr, toks, secs = 0, 0, 0, 0
    for rep in range(3):
        a0, d0 = metrics()
        body = {"model": "gemma-4-26b", "messages": [{"role": "user", "content": p}], "max_tokens": 500,
                "temperature": 0.3, "chat_template_kwargs": {"enable_thinking": False}}
        t = time.time()
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}),
            timeout=300))
        secs += time.time() - t
        toks += r["usage"]["completion_tokens"]
        time.sleep(1.5)  # metrikalar yangilanishi uchun
        a1, d1 = metrics()
        acc += a1 - a0
        dr += d1 - d0
    print(f"{lang:10s} tok/s={toks / secs:5.1f}  qabul uzunligi={1 + acc / max(dr, 1):4.2f} (4 dan)  "
          f"taxminlar qabul qilindi={acc / max(dr * 4, 1):5.1%}")
