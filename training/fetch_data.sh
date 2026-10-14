#!/bin/bash
# Taxminchini o'zbekchaga o'qitish uchun so'rovlar (prompt) manbalari: ochiq datasetlardan kichik qismlar
D=$HOME/sarob/train/raw
mkdir -p "$D"
get() {  # get <dataset_id> <fayl> <saqlash_nomi>
  for i in 1 2 3 4 5; do
    curl -sSL -C - --speed-limit 10240 --speed-time 60 -o "$D/$3" \
      "https://huggingface.co/datasets/$1/resolve/main/$2" && { echo "$(date +%H:%M) tayyor: $3"; return; }
    sleep 3
  done
  echo "$(date +%H:%M) XATO: $3"
}
get behbudiy/alpaca-cleaned-uz data/train-00000-of-00001.parquet uz_alpaca.parquet
get UAzimov/uzbek-instruct-llm uzbek-instruct-dataset-openai.jsonl uz_instruct.jsonl
get MLDataScientist/oasst2_uzbek data/train-00000-of-00001.parquet uz_oasst2.parquet
get koyiljon-s/uz.self-instruct self_instruct_uz.json uz_selfinst.json
get AsrorAsr/uzbek-customer-support-dialogs data/train-00000-of-00001.parquet uz_support.parquet
get behbudiy/translation-instruction data/train-00000-of-00001.parquet uz_transl.parquet
get MLDataScientist/SlimOrca-Dedup-Uzbek-cleaned data/train-00000-of-00002.parquet uz_slimorca.parquet
get tahrirchi/uz-crawl data/news-00002-of-00007.parquet uz_news.parquet
get NousResearch/hermes-function-calling-v1 func-calling-singleturn.json tools_hermes.json
get HuggingFaceH4/ultrachat_200k data/test_sft-00000-of-00001-f7dfac4afe5b93f4.parquet en_ultrachat.parquet
get allenai/WildChat-1M data/train-00000-of-00014.parquet wildchat_0.parquet
echo "$(date +%H:%M) HAMMASI TAYYOR"
