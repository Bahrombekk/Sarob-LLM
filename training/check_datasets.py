"""O'qitish uchun datasetlar mavjudligi va hajmini tekshiradi."""
import json, urllib.request

IDS = ["behbudiy/alpaca-cleaned-uz", "UAzimov/uzbek-instruct-llm", "behbudiy/translation-instruction",
       "MLDataScientist/oasst2_uzbek", "koyiljon-s/uz.self-instruct", "AsrorAsr/uzbek-customer-support-dialogs",
       "MLDataScientist/SlimOrca-Dedup-Uzbek-cleaned", "tahrirchi/dilmash", "tahrirchi/uz-crawl",
       "HuggingFaceH4/ultrachat_200k", "NousResearch/hermes-function-calling-v1", "allenai/WildChat-1M",
       "IlyaGusev/ru_turbo_alpaca", "d0rj/OpenOrca-ru"]
for i in IDS:
    try:
        d = json.load(urllib.request.urlopen(f"https://huggingface.co/api/datasets/{i}?blobs=true", timeout=20))
        size = sum((s.get("size") or 0) for s in d.get("siblings", [])) / 1e6
        files = [s["rfilename"] for s in d.get("siblings", []) if s["rfilename"].endswith((".parquet", ".json", ".jsonl", ".csv"))]
        print(f"OK  {i:45s} gated={d.get('gated')} {size:8.1f} MB  {len(files)} fayl  {files[:2]}")
    except Exception as e:
        print(f"YOQ {i:45s} {str(e)[:60]}")
