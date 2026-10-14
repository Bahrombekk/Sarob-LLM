"""prompts.jsonl dan javob yaratish uchun kichikroq, o'zbekchaga og'irroq to'plam ajratadi (~16k).
Allaqachon javob yozilgan so'rovlar albatta kiritiladi (mehnat yo'qolmasin)."""
import json, random, sys, collections
from pathlib import Path

SRC, DST = Path(sys.argv[1]), Path(sys.argv[2])
DONE = Path(sys.argv[3]) if len(sys.argv) > 3 else None
QUOTA = {"uz_alpaca": 3000, "uz_slimorca": 2400, "uz_oasst2": 2200, "uz_selfinst": 1500, "uz_instruct": 1300,
         "uz_news": 1800, "uz_transl": 600, "uz_support": 400,
         "en_ultrachat": 900, "en_wildchat": 900, "ru_wildchat": 700, "tools_hermes": 700}
random.seed(1)
rows = [json.loads(l) for l in open(SRC, encoding="utf-8")]
done = set()
if DONE and DONE.exists():
    done = {json.loads(l)["id"] for l in open(DONE, encoding="utf-8")}
by = collections.defaultdict(list)
for r in rows:
    by[r["src"]].append(r)
out = [r for r in rows if r["id"] in done]
for s, q in QUOTA.items():
    rest = [r for r in by[s] if r["id"] not in done]
    random.shuffle(rest)
    have = sum(1 for r in out if r["src"] == s)
    out += rest[: max(0, q - have)]
random.shuffle(out)
with open(DST, "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
c = collections.Counter(r["lang"] for r in out)
print(len(out), dict(c), f"(oldin tayyor: {len(done)})")
