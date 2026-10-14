import json, time, urllib.request

SYS = open("/home/dasuty/sarob/sarob_prompt.md").read().replace("{{CURRENT_DATE}}", "2026-10-13") \
    .replace("{{CURRENT_WEEKDAY}}", "Tuesday")
CASES = [(32, "salom"), (32, "Rahmat, yaxshi ishlading"), (32, "Ushbu gapni ruschaga tarjima qil: Ertaga uchrashamiz."),
         (64, "qalaysan?"), (192, "Bugun ob-havo qanday?")]
for b, q in CASES:
    body = {"model": "gemma-4-26b", "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": q}],
            "max_tokens": 2500, "temperature": 0.3, "chat_template_kwargs": {"enable_thinking": True},
            "thinking_token_budget": b}
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}),
        timeout=300))
    m = r["choices"][0]["message"]
    c = (m.get("content") or "").replace("\n", " ")
    leak = any(x in c for x in ["<|channel", "channel|>", "<thought", "thought "])
    rt = (r["usage"].get("completion_tokens_details") or {}).get("reasoning_tokens")
    calls = [x["function"]["name"] for x in (m.get("tool_calls") or [])]
    print(f"budget={b:4d} {time.time() - t:4.1f}s leak={leak} reasoning={rt} calls={calls} | {c[:90]}")
