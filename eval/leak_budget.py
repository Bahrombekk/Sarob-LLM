"""O'ylash chegarasi urilganda o'ylash javobga oqib chiqadimi — o'lchov.
Qiyin masala + kichik chegara (o'ylash albatta kesiladi), N marta. Oqish: ko'rinadigan javobda inglizcha
fikrlash belgilari yoki javob haddan tashqari uzun.  Ishlatish: python3 leak_budget.py [chegara] [N]
"""
import json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 128
N = int(sys.argv[2]) if len(sys.argv) > 2 else 6
SYS = (Path.home() / "sarob" / "sarob_prompt.md").read_text(encoding="utf-8")
QS = [
    "Tenglamani yeching: x + x/(1+2) + x/(1+2+3) + ... + x/(1+2+3+...+7) = 7",
    "Bir hovuzni birinchi quvur 6 soatda, ikkinchisi 4 soatda to'ldiradi, uchinchisi esa 12 soatda bo'shatadi. "
    "Uchalasi birga ochilsa, hovuz necha soatda to'ladi? Yechimini tushuntir.",
]
EN = re.compile(r"\b(Wait|Let's|Let me|I will|I'll|Actually|The user|Final check|Okay)\b")


def one(q):
    body = {"model": "gemma-4-26b", "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": q}],
            "max_tokens": 3000, "temperature": 0.7, "thinking_token_budget": BUDGET,
            "chat_template_kwargs": {"enable_thinking": True},
            "repetition_detection": {"max_pattern_size": 256, "min_pattern_size": 24, "min_count": 5}}
    req = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=600))
    c = d["choices"][0]["message"].get("content") or ""
    head = c[:400].lower()
    en_head = len(re.findall(r"\b(the|is|of|to|and|per|we|this|wait|let)\b", head))
    uz_head = len(re.findall(r"\b(va|uchun|bu|bir|ushbu|har|bilan|qilamiz|yechish)\b", head))
    leak = len(EN.findall(c)) >= 2 or en_head > uz_head or d["usage"]["completion_tokens"] >= 2900
    return leak, d["usage"]["completion_tokens"], c[:110].replace("\n", " ")


with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(one, [q for q in QS for _ in range(N)]))
for leak, n, head in res:
    print(("OQISH " if leak else "toza  ") + f"{n:5d} tok | {head}")
print(f"chegara={BUDGET}: oqish {sum(r[0] for r in res)}/{len(res)}")
