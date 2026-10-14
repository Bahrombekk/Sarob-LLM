"""Toza so'rovlarga Sarobning o'zi (Gemma, :8000) javob yozadi — taxminchi aynan shu modelning tokenlarini
o'rganishi kerak. Ishlab chiqarishdagidek: Sarob tizim prompti, o'ylash chegarasi (32/512/1024), asboblar.
Aniq token ID'lari saqlanadi (return_token_ids), shuning uchun keyin qayta tokenlash xatosi bo'lmaydi.

Ishlatish:  python3 gen_responses.py prompts.jsonl responses.jsonl [parallel=40]
To'xtab qolsa, qayta ishga tushiring — tayyor javoblar o'tkazib yuboriladi.
"""
import json, random, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SRC, DST = Path(sys.argv[1]), Path(sys.argv[2])
PAR = int(sys.argv[3]) if len(sys.argv) > 3 else 40
URL = "http://127.0.0.1:8000/v1/chat/completions"
SAROB = Path(__file__).with_name("sarob_prompt.md").read_text(encoding="utf-8").strip()
# Open WebUI ishlab chiqarishda Sarobga har doim shu asboblarni beradi (sarob_internet/baza/rasm)
SAROB_TOOLS = json.loads(Path(__file__).with_name("sarob_tools.json").read_text(encoding="utf-8"))

done = set()
if DST.exists():
    for l in open(DST, encoding="utf-8"):
        try:
            done.add(json.loads(l)["id"])
        except Exception:
            pass
todo = [json.loads(l) for l in open(SRC, encoding="utf-8")]
todo = [r for r in todo if r["id"] not in done]
print(f"tayyor {len(done)}, qoldi {len(todo)}", flush=True)

lock, out = threading.Lock(), open(DST, "a", encoding="utf-8")
stat = {"ok": 0, "err": 0, "tok": 0, "t0": time.time()}


def one(r):
    rnd = random.Random(r["id"])
    msgs, tools = r["messages"], r.get("tools")
    if msgs[0]["role"] != "system":                      # datasetda tizim xabari bo'lmasa — Sarobniki
        msgs = [{"role": "system", "content": SAROB}] + msgs
        tools = tools or SAROB_TOOLS
    budget = rnd.choice([32, 512, 512, 1024])             # filtrdagi kabi tasodifiy o'ylash chegarasi
    body = {"model": "gemma-4-26b", "messages": msgs, "max_tokens": budget + 1536,
            "temperature": 0.7, "top_p": 0.95, "thinking_token_budget": budget,
            "chat_template_kwargs": {"enable_thinking": True}, "return_token_ids": True,
            "repetition_detection": {"max_pattern_size": 256, "min_pattern_size": 24, "min_count": 5}}
    if tools:
        body["tools"] = tools
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=900))
            ch = d["choices"][0]
            rec = {"id": r["id"], "src": r["src"], "lang": r["lang"], "budget": budget,
                   "finish": ch.get("finish_reason"),
                   "prompt_ids": d.get("prompt_token_ids"), "ids": ch.get("token_ids"),
                   "reasoning": ch["message"].get("reasoning_content") or ch["message"].get("reasoning"),
                   "content": ch["message"].get("content"), "tool_calls": ch["message"].get("tool_calls")}
            with lock:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
                stat["ok"] += 1; stat["tok"] += len(rec["ids"] or [])
                if stat["ok"] % 200 == 0:
                    dt = time.time() - stat["t0"]
                    print(f"{time.strftime('%H:%M')} {stat['ok']}/{len(todo)}  {stat['tok']/dt:.0f} tok/s  "
                          f"xato {stat['err']}  qolgan ~{(len(todo)-stat['ok'])*dt/stat['ok']/3600:.1f} soat", flush=True)
            return
        except Exception as e:
            err = str(e)[:200]
            time.sleep(5 * (attempt + 1))
    with lock:
        stat["err"] += 1
        print("XATO", r["id"], err, flush=True)


with ThreadPoolExecutor(PAR) as ex:
    list(ex.map(one, todo))
print("HAMMASI TAYYOR", stat, flush=True)
