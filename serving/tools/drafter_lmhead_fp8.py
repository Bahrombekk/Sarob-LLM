#!/usr/bin/env python3
"""Gemma 4 MTP taxminchisining lug'at qatlamini (lm_head, 262144x1024 BF16) FP8 W8A8 ga o'tkazadi.

Taxminchi har siklda k marta ishlaydi va har safar lm_head'ni to'liq o'qiydi (~0.54 GB). vLLM'da embed_tokens
baribir Gemma'nikiga almashtiriladi, shuning uchun faqat lm_head chiqish uchun ishlatiladi.
vLLM taxminchi uchun faqat uning o'z quantization_config'ini o'qiydi (get_draft_quant_config).

Ishlatish (vLLM obrazida):  python3 drafter_lmhead_fp8.py /models/gemma4-26b-assistant-uz /models/gemma4-26b-assistant-uz-fp8
"""
import json
import os
import shutil
import sys

import torch
from safetensors import safe_open
from safetensors.torch import save_file

FP8_MAX = 448.0
# Gemma lm_head bilan bir xil sxema: og'irlik FP8 kanal bo'yicha, aktivatsiya dinamik token bo'yicha
# (faqat og'irlik FP8 bo'lsa vLLM ParallelLMHead'da yiqiladigan Humming yadrosini tanlaydi).
GROUP = {
    "format": "float-quantized",
    "targets": ["re:.*lm_head"],
    "weights": {"num_bits": 8, "type": "float", "strategy": "channel", "symmetric": True, "dynamic": False,
                "group_size": None, "actorder": None, "block_structure": None, "observer": None,
                "observer_kwargs": {}},
    "input_activations": {"num_bits": 8, "type": "float", "strategy": "token", "symmetric": True,
                          "dynamic": True, "group_size": None, "actorder": None, "block_structure": None,
                          "observer": None, "observer_kwargs": {}},
    "output_activations": None,
}


def main():
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=False)
    tensors = {}
    with safe_open(os.path.join(src, "model.safetensors"), framework="pt", device="cpu") as f:
        for k in f.keys():
            tensors[k] = f.get_tensor(k)
    w = tensors.pop("lm_head.weight").to(torch.float32)
    amax = w.abs().amax(dim=1, keepdim=True)
    scale = (amax / FP8_MAX).clamp_min(torch.finfo(torch.float32).tiny)
    wq = (w / scale).clamp(-FP8_MAX, FP8_MAX).to(torch.float8_e4m3fn)
    dq = wq.to(torch.float32) * scale
    cos = torch.nn.functional.cosine_similarity(dq.flatten().double(), w.flatten().double(), dim=0).item()
    print(f"lm_head FP8: kosinus {cos:.6f}", file=sys.stderr)
    tensors["lm_head.weight"] = wq.contiguous()
    tensors["lm_head.weight_scale"] = scale.contiguous()
    save_file(tensors, os.path.join(dst, "model.safetensors"), metadata={"format": "pt"})

    for name in os.listdir(src):
        if name != "model.safetensors" and os.path.isfile(os.path.join(src, name)):
            shutil.copy2(os.path.join(src, name), os.path.join(dst, name))
    cfg_path = os.path.join(dst, "config.json")
    cfg = json.load(open(cfg_path))
    cfg["tie_word_embeddings"] = False
    cfg["text_config"]["tie_word_embeddings"] = False
    cfg["quantization_config"] = {"quant_method": "compressed-tensors", "format": "float-quantized",
                                  "quantization_status": "compressed", "config_groups": {"group_0": GROUP},
                                  "ignore": [], "kv_cache_scheme": None}
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    os.system(f"chmod -R a+rX {dst}")
    print("tayyor:", dst, file=sys.stderr)


if __name__ == "__main__":
    main()
