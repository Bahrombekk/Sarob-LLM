"""O'ylash tili: o'zbekcha vs inglizcha — tezlik, o'ylash tokenlari va to'g'rilik."""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = open("/home/dasuty/sarob/sarob_prompt.md").read().replace("{{CURRENT_DATE}}", "2026-10-14") \
    .replace("{{CURRENT_WEEKDAY}}", "Wednesday")
BASE = BASE.replace("- Ichki fikrlashni (thinking) ham o'zbekcha va qisqa yoz.", "- {THINK}")
MODES = {
    "o'zbekcha": "Ichki fikrlashni (thinking) o'zbek tilida va qisqa yoz.",
    "inglizcha": "Think internally in English, briefly. Write the final answer only in Uzbek (Latin script).",
}
QS = [
    ("moyka", "Moshinamni moyka qilmoqchiman, moyka uyimdan 500 m uzoqlikda. Piyoda borganim maqulmi yoki mashinada?", ["mashina", "moshina"]),
    ("ota", "Ota o'g'lidan 30 yosh katta. 5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi. Hozir har biri necha yoshda?", ["40"]),
    ("sham", "Xonada 10 ta sham yonib turibdi. 3 tasi o'chib qoldi. Ertalab nechta sham qoladi?", ["3 "]),
    ("aka", "Alining 3 ta singlisi bor. Har bir singlisining 1 tadan akasi bor. Alining oilasida nechta o'g'il bor?", ["1 "]),
    ("detal", "5 ta mashina 5 ta detalni 5 daqiqada yasaydi. 100 ta mashina 100 ta detalni necha daqiqada yasaydi?", ["5 daqiqa"]),
    ("olma", "Savatda 24 ta olma bor. Uchdan biri chirigan, qolganining yarmini sotdim. Nechta olma qoldi?", ["8"]),
]


def run(mode, q):
    name, text, want = q
    body = {"model": "gemma-4-26b", "temperature": 0.3, "max_tokens": 3000,
            "messages": [{"role": "system", "content": BASE.replace("{THINK}", MODES[mode])}, {"role": "user", "content": text}],
            "chat_template_kwargs": {"enable_thinking": True}, "thinking_token_budget": 1024}
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=300))
    ans = (r["choices"][0]["message"].get("content") or "").lower()
    rt = (r["usage"].get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
    ok = any(w in ans + " " for w in want)
    return mode, name, ok, rt, time.time() - t


for mode in MODES:
    res = []
    for rep in range(2):
        with ThreadPoolExecutor(1) as ex:
            res += list(ex.map(lambda q: run(mode, q), QS))
    ok = sum(r[2] for r in res)
    print(f"{mode:10s} to'g'ri={ok}/{len(res)}  o'rtacha o'ylash={sum(r[3] for r in res) / len(res):5.0f} token  "
          f"o'rtacha vaqt={sum(r[4] for r in res) / len(res):4.1f}s  xato: {[r[1] for r in res if not r[2]]}")
