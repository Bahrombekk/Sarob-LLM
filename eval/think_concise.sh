#!/bin/bash
# Tajriba: o'ylash uslubi — hozirgi prompt va "qisqa qoralama" prompt (31 savol, o'ylash yoqiq, chegara 1024).
# O'lchanadi: o'ylash tokenlari, vaqt; to'g'rilik natija fayllaridan ko'z bilan baholanadi.
cd ~/sarob
python3 - <<'EOF'
p = open("sarob_prompt.md", encoding="utf-8").read()
old = [l for l in p.split("\n") if l.startswith("- Ichki fikrlashni (thinking)")][0]
new = ("- Ichki fikrlashni (thinking) ingliz tilida, QISQA QORALAMA ko'rinishida yurit: to'liq gaplar, kirish so'zlari, "
       "savolni qayta aytib berish va javob matnini oldindan yozib chiqish YO'Q. Faqat kalit qadamlar: maqsad -> kerakli "
       "asbob yoki hisob -> tekshiruv. Oddiy savolda 1-3 qator, murakkabida ham ~15 qatordan oshmasin. "
       "YAKUNIY JAVOB doim o'zbek tilida (lotin yozuvida). Oddiy savolga (salom, rahmat, tarjima, ta'rif) asbobsiz darhol qisqa javob ber.")
open("/tmp/sarob_prompt_qisqa.md", "w", encoding="utf-8").write(p.replace(old, new))
print("qisqa prompt tayyor")
EOF
SAROB_BUDGET=1024 ~/sarob/venv/bin/python sarob_eval.py eval_think_hozir.md 1 > /tmp/think_hozir.log 2>&1
SAROB_BUDGET=1024 SAROB_PROMPT=/tmp/sarob_prompt_qisqa.md ~/sarob/venv/bin/python sarob_eval.py eval_think_qisqa.md 1 > /tmp/think_qisqa.log 2>&1
for f in eval_think_hozir.md eval_think_qisqa.md; do
  python3 - "$f" <<'EOF'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
th = [int(x) for x in re.findall(r"think=(\d+)", t)]
vq = [int(x) for x in re.findall(r"\*Vaqt: (\d+)s", t)]
print(f"{sys.argv[1]}: o'ylash jami {sum(th)} token (chaqiruvga o'rtacha {sum(th)/max(1,len(th)):.0f}), vaqt jami {sum(vq)} s, {len(vq)} savol")
EOF
done
echo TUGADI
