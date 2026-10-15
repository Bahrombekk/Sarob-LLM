"""2-raund so'rovlari: prompts.jsonl dan 1-raundda (prompts_gen.jsonl) ishlatilmaganlarini tanlaydi.
Ishlatish: python3 make_r2.py   ->  prompts_r2.jsonl
"""
import json, random, collections
from pathlib import Path

D = Path(__file__).parent
random.seed(11)
QUOTA = {"uz_alpaca": 3200, "uz_slimorca": 2800, "uz_oasst2": 2000, "uz_selfinst": 2000, "uz_instruct": 1500,
         "uz_news": 1800, "uz_transl": 600, "uz_support": 100,
         "en_ultrachat": 700, "en_wildchat": 600, "ru_wildchat": 500, "tools_hermes": 300}

used = {json.loads(l)["id"] for l in open(D / "prompts_gen.jsonl", encoding="utf-8")}
by = collections.defaultdict(list)
for l in open(D / "prompts.jsonl", encoding="utf-8"):
    r = json.loads(l)
    if r["id"] not in used:
        by[r["src"]].append(r)
out = []
for s, q in QUOTA.items():
    random.shuffle(by[s])
    out += by[s][:q]
random.shuffle(out)
with open(D / "prompts_r2.jsonl", "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(out), dict(collections.Counter(r["lang"] for r in out)))
print({s: min(q, len(by[s])) for s, q in QUOTA.items()})
