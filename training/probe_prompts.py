"""Har bir datasetdan faqat foydalanuvchi so'rovini ajratib, tasodifiy namunalar va eng ko'p takrorlangan
boshlanishlarni ko'rsatadi (tarjima sifati va shablon takrorlarini ko'z bilan tekshirish uchun)."""
import json, random, collections, sys
from pathlib import Path
import pandas as pd

RAW = Path(sys.argv[1] if len(sys.argv) > 1 else "/data/raw")
random.seed(3)


def first_user(msgs, keys=("user", "human", "prompter")):
    for m in msgs:
        r = m.get("role") or m.get("from")
        if r in keys:
            return m.get("content") or m.get("value") or ""
    return ""


def show(name, prompts, n=6):
    prompts = [p for p in prompts if isinstance(p, str)]
    print(f"\n##### {name}: {len(prompts)} so'rov")
    for p in random.sample(prompts, min(n, len(prompts))):
        print("  •", p[:300].replace("\n", " ⏎ "))
    top = collections.Counter(p[:60] for p in prompts).most_common(5)
    print("  eng ko'p boshlanish:", [(k, c) for k, c in top if c > 1])


rp = lambda f: pd.read_parquet(RAW / f)
d = rp("uz_alpaca.parquet"); show("uz_alpaca", (d.instruction + "\n" + d.input).tolist())
d = pd.read_json(RAW / "uz_instruct.jsonl", lines=True); show("uz_instruct", d.messages.map(first_user).tolist())
d = json.load(open(RAW / "uz_selfinst.json")); show("uz_selfinst", [x["instruction"] + "\n" + x["input"] for x in d])
d = rp("uz_slimorca.parquet"); show("uz_slimorca", d.conversations.map(lambda c: first_user(list(c))).tolist())
d = rp("uz_support.parquet"); show("uz_support", d.messages.map(lambda c: first_user(list(c))).tolist(), 3)
d = rp("uz_transl.parquet"); show("uz_transl", d.instruction.tolist())
print("  uz_transl yo'riqnoma turlari:", collections.Counter(d.instruction.str.split("\n").str[0]).most_common(8))
d = rp("uz_oasst2.parquet")
print("\n oasst2 lang:", d.lang.value_counts().head(8).to_dict(), " role:", d.role.value_counts().to_dict(),
      " deleted:", d.deleted.sum(), " review_result:", d.review_result.value_counts(dropna=False).to_dict())
root = d[d.parent_id.isna() & (d.role == "prompter")]
show("uz_oasst2 (ildiz so'rovlar)", root.text.tolist())
d = rp("uz_news.parquet")
print("\n news manbalar:", d.source.str.extract(r"https?://([^/]+)")[0].value_counts().head(8).to_dict())
tails = collections.Counter(t.strip().split("\n")[-1][:70] for t in d.text.sample(20000, random_state=0))
print(" news eng ko'p oxirgi qator (reklama/obuna):", tails.most_common(8))
d = rp("wildchat_0.parquet")
print("\n wildchat language:", d.language.value_counts().head(10).to_dict(), " toxic:", d.toxic.sum(), " redacted:", d.redacted.sum())
for lg in ["English", "Russian", "Uzbek"]:
    show(f"wildchat {lg}", d[(d.language == lg) & ~d.toxic].conversation.map(lambda c: first_user(list(c))).tolist(), 5)
d = rp("en_ultrachat.parquet"); show("en_ultrachat", d.prompt.tolist(), 4)
d = json.load(open(RAW / "tools_hermes.json")); show("tools_hermes", [first_user(x["conversations"]) for x in d], 4)
