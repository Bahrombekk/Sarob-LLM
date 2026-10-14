"""Aralashgan javob qanday ko'rinishini ushlab olish (tozalash filtri uchun)."""
import json, urllib.request

SYS = open("/home/dasuty/sarob/sarob_prompt.md").read().replace("{{CURRENT_DATE}}", "2026-10-13") \
    .replace("{{CURRENT_WEEKDAY}}", "Tuesday")
QS = ["Kreditni muddatidan oldin to'lash foydalimi yoki pulni depozitga qo'yganim maqulmi? 24% kredit, 20% depozit.",
      "Toshkent va Samarqand orasidagi masofa qancha va Afrosiyobda qancha vaqt ketadi?",
      "Kichik do'kon uchun biznes reja tuz: 5 ta asosiy band."]
for i in range(8):
    q = QS[i % len(QS)]
    body = {"model": "gemma-4-26b", "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": q}],
            "max_tokens": 3000, "temperature": 0.3, "chat_template_kwargs": {"enable_thinking": True},
            "thinking_token_budget": 512}
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}),
        timeout=300))
    m = r["choices"][0]["message"]
    c = m.get("content") or ""
    if "<thought" in c or "Thinking:" in c or "<|channel" in c:
        print("ARALASHGAN JAVOB, boshi:\n" + c[:700])
        print("\n... oxiri:\n" + c[-300:])
        print("\nreasoning maydoni uzunligi:", len(m.get("reasoning_content") or m.get("reasoning") or ""))
        break
else:
    print("8 urinishda aralashish yo'q")
