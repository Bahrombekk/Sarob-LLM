import json, time, urllib.request

Q = "Ota o'g'lidan 30 yosh katta. 5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi. Hozir har biri necha yoshda? Qisqa javob."
for b in [None, 128, 512]:
    body = {"model": "gemma-4-26b", "messages": [{"role": "user", "content": Q}], "max_tokens": 3000,
            "chat_template_kwargs": {"enable_thinking": True}}
    if b is not None:
        body["thinking_token_budget"] = b
    t = time.time()
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(),
                                     {"Content-Type": "application/json"})
        r = json.load(urllib.request.urlopen(req, timeout=300))
        u, m = r["usage"], r["choices"][0]["message"]
        rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens")
        reasoning = m.get("reasoning_content") or m.get("reasoning") or ""
        print(f"budget={b}: {time.time() - t:.1f}s completion={u['completion_tokens']} reasoning_tokens={rt} "
              f"reasoning_chars={len(reasoning)} javob={(m.get('content') or '')[:90]!r}")
    except Exception as e:
        body_txt = e.read()[:300] if hasattr(e, "read") else b""
        print("budget", b, "XATO", str(e)[:150], body_txt)
