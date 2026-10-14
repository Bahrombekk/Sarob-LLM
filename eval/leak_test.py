"""O'ylash javob matniga aralashadimi? 12 ta o'ylash talab qiladigan savol, 512 token chegarasi bilan."""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

SYS = open("/home/dasuty/sarob/sarob_prompt.md").read().replace("{{CURRENT_DATE}}", "2026-10-13") \
    .replace("{{CURRENT_WEEKDAY}}", "Tuesday")
QS = ["Ota o'g'lidan 30 yosh katta. 5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi. Hozir har biri necha yoshda?",
      "Toshkent va Samarqand orasidagi masofa qancha va Afrosiyobda qancha vaqt ketadi?",
      "Moshinamni moykaga olib bormoqchiman, moyka 500 m uzoqda. Piyoda borganim maqulmi yoki mashinada?",
      "Bir savat olmada 24 ta olma bor. Uchdan biri chirigan, qolganining yarmini sotdim. Nechta qoldi?",
      "Kichik do'kon uchun biznes reja tuz: 5 ta asosiy band.",
      "Nima uchun osmon ko'k rangda? Qisqa tushuntir.",
      "Python'da ro'yxatdagi takroriy elementlarni o'chiradigan funksiya yoz.",
      "Kreditni muddatidan oldin to'lash foydalimi yoki pulni depozitga qo'yganim maqulmi? 24% kredit, 20% depozit.",
      "Alining 3 ta singlisi bor, har birining 1 tadan akasi bor. Oilada nechta o'g'il?",
      "Ertaga uchrashuv uchun 3 ta muhim savol tayyorla: men yangi xodim yollayapman.",
      "Agar 5 ta mashina 5 ta detalni 5 daqiqada yasasa, 100 ta mashina 100 ta detalni necha daqiqada yasaydi?",
      "Toshkentda qishda issiq kiyim olish uchun qaysi oy eng arzon? Mantiqiy fikr yurit."]


def one(q):
    body = {"model": "gemma-4-26b", "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": q}],
            "max_tokens": 3000, "temperature": 0.3, "chat_template_kwargs": {"enable_thinking": True},
            "thinking_token_budget": 512}
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}),
        timeout=300))
    c = r["choices"][0]["message"].get("content") or ""
    leak = any(x in c for x in ["<thought", "<|channel", "channel|>", "Thinking:", "thought\n"])
    return leak, time.time() - t


with ThreadPoolExecutor(2) as ex:
    res = list(ex.map(one, QS))
print(f"aralashish: {sum(l for l, _ in res)}/{len(res)}  o'rtacha vaqt: {sum(t for _, t in res) / len(res):.1f}s")
