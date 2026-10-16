"""Javob vaqti qayerga ketadi: prompt (prefill), o'ylash, javob yozish — odatiy savollarda, ishlab chiqarish sozlamalari bilan
(Sarob tizim prompti + asboblar + filtrdagi o'ylash chegarasi). Ishlatish: python3 latency_breakdown.py
"""
import importlib.util, json, time, urllib.request
from pathlib import Path

H = Path.home() / "sarob"
SYS = (H / "sarob_prompt.md").read_text(encoding="utf-8").replace("{{CURRENT_DATE}}", time.strftime("%Y-%m-%d"))
TOOLS = json.loads((H / "train" / "sarob_tools.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location("ft", H / "filter_tezlik.py")
ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)
F = ft.Filter()

QS = ["salom", "menga qanday yordam bera olasan",
      "Excelda VLOOKUP qanday ishlaydi? Misol bilan tushuntir.",
      "Kichik do'kon uchun oylik xarajatlar rejasini tuzib ber.",
      "Inflyatsiya nima va u narxlarga qanday ta'sir qiladi?",
      "Ota o'g'lidan 30 yosh katta. 5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi. Hozir har biri necha yoshda?"]

print(f"{'savol':45s} {'chegara':>7s} {'1-token':>8s} {'o`ylash':>14s} {'javob':>14s} {'jami':>6s}")
for q in QS:
    body = {"model": "gemma-4-26b", "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": q}],
            "tools": TOOLS, "stream": True, "stream_options": {"include_usage": True}, "temperature": 0.7,
            "chat_template_kwargs": {"enable_thinking": True}}
    body = F.request(body)
    t0 = time.time(); t_first = t_think_end = None; usage = {}
    req = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    for line in urllib.request.urlopen(req, timeout=600):
        line = line.decode().strip()
        if not line.startswith("data: ") or line == "data: [DONE]":
            continue
        d = json.loads(line[6:])
        if d.get("usage"):
            usage = d["usage"]
        for ch in d.get("choices", []):
            delta = ch.get("delta", {})
            if (delta.get("reasoning") or delta.get("reasoning_content") or delta.get("content") or delta.get("tool_calls")) and t_first is None:
                t_first = time.time()
            if (delta.get("content") or delta.get("tool_calls")) and t_think_end is None:
                t_think_end = time.time()
    t1 = time.time()
    rt = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
    at = (usage.get("completion_tokens") or 0) - rt
    t_first = t_first or t1; t_think_end = t_think_end or t1
    print(f"{q[:45]:45s} {body['thinking_token_budget']:7d} {t_first-t0:7.1f}s {t_think_end-t_first:5.1f}s {rt:5d} tok "
          f"{t1-t_think_end:5.1f}s {at:5d} tok {t1-t0:5.1f}s")
