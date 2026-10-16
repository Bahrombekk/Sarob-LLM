#!/bin/bash
# Tajriba D: o'ylash ichida javob qoralamasini yozmaslik (reja + tekshiruv; hisob va mantiq to'liq).
# A bilan bir xil sharoit: 31 savol, o'ylash yoqiq, chegara 1024.
cd ~/sarob
python3 - <<'PY'
p = open("sarob_prompt.md", encoding="utf-8").read()
old = [l for l in p.split("\n") if l.startswith("- Ichki fikrlashni (thinking)")][0]
new = ("- Ichki fikrlash (thinking) faqat REJA va TEKSHIRUV uchun, ingliz tilida: savol nimani talab qiladi, qaysi asbob "
       "kerak, qaysi faktlar va raqamlar muhim, qayerda xato qilish mumkin. Javob matnini, misollar, jadvallar, formulalar "
       "va kodni o'ylash ichida YOZMA — ularni faqat yakuniy javobda, bir marta, o'zbekcha yoz. Murakkab hisob-kitob va "
       "mantiqiy masalalarni esa o'ylashda oxirigacha to'liq bajar va tekshir. YAKUNIY JAVOB doim o'zbek tilida "
       "(lotin yozuvida). Oddiy savolga (salom, rahmat, tarjima, ta'rif) asbobsiz darhol qisqa javob ber.")
open("/tmp/sarob_prompt_noDraft.md", "w", encoding="utf-8").write(p.replace(old, new))
PY
SAROB_BUDGET=1024 SAROB_PROMPT=/tmp/sarob_prompt_noDraft.md ~/sarob/venv/bin/python sarob_eval.py eval_think_noDraft.md 1 > /tmp/think_noDraft.log 2>&1
python3 - <<'PY'
import re
for f in ("eval_think_hozir.md", "eval_think_noDraft.md"):
    t = open(f, encoding="utf-8").read()
    th = [int(x) for x in re.findall(r"think=(\d+)", t)]
    vq = [int(x) for x in re.findall(r"\*Vaqt: (\d+)s", t)]
    first = [int(m) for m in re.findall(r"\n- `LLM_T [^`]*think=(\d+)`", t)]
    print(f"{f}: o'ylash jami {sum(th)} token, vaqt jami {sum(vq)} s, savollar {len(vq)}")
PY
echo TUGADI
