"""Sarob Tez uchun: o'ylashsiz va qisqa o'ylash bilan tuzoq savollar sifati va tezligi."""
import json, time, urllib.request

TEZ = ("Sening isming Sarob. Sen egangning shaxsiy yordamchisisan va uning DGX Spark serverida lokal ishlaysan. "
       "Bugun: 2026-10-13. Doim o'zbek tilida (lotin yozuvida), qisqa va aniq javob ber.")
QS = [
    ("moyka", "senga savol men moshinamni moyka qilmoqchima moyka uyimdan 500 m uzoqlikda shunga moykaga piyoda borganim maqulmi yokiy moshinada",
     "mashinada"),
    ("ota", "Ota o'g'lidan 30 yosh katta. 5 yildan keyin ota o'g'lidan 3 baravar katta bo'ladi. Hozir har biri necha yoshda?", "10"),
    ("shamlar", "Xonada 10 ta sham yonib turibdi. 3 tasi o'chib qoldi. Ertalab nechta sham qoladi?", "3"),
    ("opa", "Alining 3 ta singlisi bor. Har bir singlisining 1 tadan akasi bor. Alining oilasida nechta o'g'il bor?", "1"),
    ("salom", "salom", ""),
]
for mode, extra in [("o'ylashsiz", {}),
                    ("o'ylash 256", {"chat_template_kwargs": {"enable_thinking": True}, "thinking_token_budget": 256}),
                    ("o'ylash 512", {"chat_template_kwargs": {"enable_thinking": True}, "thinking_token_budget": 512})]:
    print(f"== {mode}")
    for name, q, want in QS:
        body = {"model": "gemma-4-26b", "temperature": 0.3, "max_tokens": 1500,
                "messages": [{"role": "system", "content": TEZ}, {"role": "user", "content": q}], **extra}
        t = time.time()
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=300))
        ans = (r["choices"][0]["message"].get("content") or "").replace("\n", " ")
        ok = "" if not want else ("✅" if want in ans.lower() else "❌")
        print(f"  {name:8s} {time.time() - t:4.1f}s {ok} {ans[:110]}")
