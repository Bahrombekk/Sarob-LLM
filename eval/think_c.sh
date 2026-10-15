#!/bin/bash
# Tajriba C: qisqa qoralama o'ylash, lekin majburiy 3 qadam (maqsad, asbob kerakmi, tekshiruv).
cd ~/sarob
python3 - <<'PY'
p = open("sarob_prompt.md", encoding="utf-8").read()
old = [l for l in p.split("\n") if l.startswith("- Ichki fikrlashni (thinking)")][0]
new = ("- Ichki fikrlashni (thinking) ingliz tilida, QISQA QORALAMA ko'rinishida yurit (to'liq gaplar, kirish so'zlari, "
       "savolni qayta aytish va javob matnini oldindan yozish yo'q), lekin uni O'TKAZIB YUBORMA. Har doim 3 qadam: "
       "1) maqsad; 2) asbob kerakmi — hisob, sana/kun soni, joriy fakt, narx, kurs, yangilik yoki fayl bo'lsa asbobni "
       "ALBATTA chaqir (ko'z bilan hisoblama, xotiradan aytma); 3) javobni tekshir (raqamlar, tartib, kod sintaksisi). "
       "Oddiy savolda bu 2-4 qator, murakkabida ~15 qatordan oshmasin. YAKUNIY JAVOB doim o'zbek tilida (lotin yozuvida). "
       "Salom, rahmat, tarjima, ta'rif kabi oddiy savolga asbobsiz darhol qisqa javob ber.")
open("/tmp/sarob_prompt_c.md", "w", encoding="utf-8").write(p.replace(old, new))
PY
SAROB_BUDGET=1024 SAROB_PROMPT=/tmp/sarob_prompt_c.md ~/sarob/venv/bin/python sarob_eval.py eval_think_c.md 1 > /tmp/think_c.log 2>&1
python3 - <<'PY'
import re
t = open("eval_think_c.md", encoding="utf-8").read()
th = [int(x) for x in re.findall(r"think=(\d+)", t)]
vq = [int(x) for x in re.findall(r"\*Vaqt: (\d+)s", t)]
print(f"C: o'ylash jami {sum(th)} token (o'rtacha {sum(th)/max(1,len(th)):.0f}), vaqt jami {sum(vq)} s, {len(vq)} savol")
PY
echo TUGADI
