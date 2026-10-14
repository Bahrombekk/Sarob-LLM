"""Yengil suhbat filtri sinovi: uzun suhbatda prompt hajmi va javob vaqti (filtrsiz va filtr bilan)."""
import base64, copy, json, sys, time, types, urllib.request

mod = types.ModuleType("f")
exec(open(sys.argv[1], encoding="utf-8").read(), mod.__dict__)
F = mod.Filter()
img = "data:image/png;base64," + base64.b64encode(open("/home/dasuty/sarob/workspace/_vagon.png", "rb").read()).decode()
SYS = open("/home/dasuty/sarob/sarob_prompt.md").read().replace("{{CURRENT_DATE}}", "2026-10-14").replace("{{CURRENT_WEEKDAY}}", "Wednesday")
big_tool = "Qidiruv natijasi: " + ("Toshkent shahri haqida ma'lumot, aholi 3 mln, maydoni 334 km2. " * 300)

# Real uzun suhbatga o'xshash: 3 ta rasmli savol, 2 ta katta asbob natijasi, keyin yangi oddiy savol
msgs = [{"role": "system", "content": SYS}]
for k in range(3):
    msgs.append({"role": "user", "content": [{"type": "text", "text": f"{k + 1}-rasmdagi jadvalni o'qi"},
                                             {"type": "image_url", "image_url": {"url": img}}]})
    msgs.append({"role": "assistant", "content": f"{k + 1}-jadval: 7 qator, vagon raqamlari o'qildi."})
for k in range(2):
    msgs.append({"role": "user", "content": f"Toshkent haqida qidir ({k})"})
    msgs.append({"role": "assistant", "content": None, "tool_calls": [{"id": f"c{k}", "type": "function",
                 "function": {"name": "internetdan_qidirish", "arguments": json.dumps({"query": "Toshkent"})}}]})
    msgs.append({"role": "tool", "tool_call_id": f"c{k}", "content": big_tool})
    msgs.append({"role": "assistant", "content": "Toshkent aholisi 3 mln."})
msgs.append({"role": "user", "content": "Rahmat. Endi qisqacha: birinchi jadvalda nechta qator bor edi?"})

for name, ms in [("filtrsiz", msgs), ("yengil", F.request({"messages": copy.deepcopy(msgs)})["messages"])]:
    body = {"model": "gemma-4-26b", "messages": ms, "max_tokens": 300, "temperature": 0,
            "chat_template_kwargs": {"enable_thinking": True}, "thinking_token_budget": 128}
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}),
        timeout=300))
    print(f"{name:8s} prompt={r['usage']['prompt_tokens']:6d} vaqt={time.time() - t:5.1f}s | "
          f"{(r['choices'][0]['message'].get('content') or '').strip()[:90]}")
