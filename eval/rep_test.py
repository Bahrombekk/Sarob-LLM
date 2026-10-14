import json, urllib.request

RD = {"max_pattern_size": 256, "min_pattern_size": 24, "min_count": 5}
CASES = [
    ("halqa", "Quyidagi jumlani 40 marta aynan takrorlab yoz, boshqa hech narsa yozma: "
              "'Fayl yaratildi va havola tayyor, iltimos yuklab oling, rahmat sizga katta.'"),
    ("jadval", "30 qatorli markdown jadval tuz: ustunlar: No, Kamera nomi, Filial. Kamera nomlari PCH-1 dan PCH-30 gacha, "
               "filial hamma qatorda bir xil: 'Xovos signallashtirish va aloqa masofasi filiali'."),
]
for name, q in CASES:
    for rd in (None, RD):
        body = {"model": "gemma-4-26b", "messages": [{"role": "user", "content": q}], "max_tokens": 2500, "temperature": 0.3}
        if rd:
            body["repetition_detection"] = rd
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:8000/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}),
            timeout=300))
        c = r["choices"][0]["message"].get("content") or ""
        rows = c.count("PCH-")
        print(f"{name:7s} himoya={'ha ' if rd else 'yoq'} tokens={r['usage']['completion_tokens']:5d} "
              f"finish={r['choices'][0]['finish_reason']:6s} takror={c.count('Fayl yaratildi'):3d} jadval_qator={rows}")
