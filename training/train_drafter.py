"""Gemma 4 MTP taxminchisini (assistant, 4 qatlam) o'zbekchaga moslab o'qitish.

vLLM'dagi ishlashi bilan aynan bir xil (vllm/v1/spec_decode/gemma4.py, models/gemma4_mtp.py):
  1-qadam, pozitsiya i:  kirish = [embed(x[i+1]) ; H[i]]  ->  x[i+2] taxmini
  2-qadam, o'sha i:      kirish = [embed(x̂[i+2]) ; post_projection(1-qadam)]  ->  x[i+3]
  - H[i]   — Gemma'ning oxirgi (normlangan) yashirin holati
  - embed  — Gemma'ning embed_tokens'i (×sqrt(2816), HF'da ichida bor)
  - diqqat — taxminchining o'z K/V'si yo'q: Gemma'ning 28-(sliding, oyna 1024) va 29-(full) qatlamlari K/V'sini
             o'qiydi, j <= i pozitsiyalargacha; pozitsiya (RoPE) barcha qadamlarda i.
Taxminchida o'z KV yo'qligi sababli faqat javob qismidagi pozitsiyalar hisoblanadi.
Yo'qotish: Gemma taqsimotiga KL (distillatsiya) + kichik CE.

Ishlatish: python3 train_drafter.py --data responses.jsonl --out ~/models/gemma4-26b-assistant-uz
"""
import argparse, json, math, os, random, shutil, time
import torch
import torch.nn.functional as F
from transformers import AutoConfig, AutoTokenizer, Gemma4AssistantForCausalLM, Gemma4ForCausalLM

ap = argparse.ArgumentParser()
ap.add_argument("--target", default="/models/gemma4-26b-bf16")
ap.add_argument("--drafter", default="/models/gemma4-26b-assistant")
ap.add_argument("--data", default="/data/responses.jsonl")
ap.add_argument("--out", default="/models/gemma4-26b-assistant-uz")
ap.add_argument("--steps", type=int, default=3, help="o'qitiladigan taxmin qadamlari (vLLM'da k)")
ap.add_argument("--step_w", default="1.0,0.8,0.6")
ap.add_argument("--lr", type=float, default=5e-5)
ap.add_argument("--epochs", type=float, default=1.0)
ap.add_argument("--accum", type=int, default=8)
ap.add_argument("--max_len", type=int, default=4096)
ap.add_argument("--kl_chunk", type=int, default=128)
ap.add_argument("--ce_w", type=float, default=0.1)
ap.add_argument("--eval_n", type=int, default=200, help="o'qitilmaydigan sinov namunalari soni")
ap.add_argument("--limit", type=int, default=0, help="faqat shuncha namuna (sinov uchun)")
ap.add_argument("--save_every", type=int, default=2000)
ap.add_argument("--warmup", type=int, default=100)
ap.add_argument("--load_test", action="store_true", help="faqat Gemma'ni yuklab, xotirani ko'rsatadi")
ap.add_argument("--max_pos", type=int, default=768, help="o'qitishda bir namunadan olinadigan pozitsiyalar (xotira)")
ap.add_argument("--overfit", action="store_true", help="tekshiruv: sinov namunalarida ham o'qitadi")
args = ap.parse_args()
torch.manual_seed(0); random.seed(0)
dev = "cuda"
W = [float(x) for x in args.step_w.split(",")][: args.steps]

# ---------------------------------------------------------------- modellar
def load_target(path):
    """Faqat matn modelini to'g'ridan-to'g'ri GPU'da quradi va og'irliklarni fayldan bittadan ko'chiradi.
    from_pretrained Spark'da (umumiy xotira) CPU+GPU nusxalari tufayli ~3x xotira olib, tizimni qotirgan."""
    def mem(tag):
        a = int(open("/proc/meminfo").read().split("MemAvailable:")[1].split()[0]) / 2**20
        print(f"  [{tag}] bo'sh {a:.0f} GiB, GPU {torch.cuda.memory_allocated()/2**30:.1f} GiB "
              f"(zaxira {torch.cuda.memory_reserved()/2**30:.1f})", flush=True)

    cfg = AutoConfig.from_pretrained(path).get_text_config()
    cfg._attn_implementation = "sdpa"
    mem("boshida")
    torch.set_default_dtype(torch.bfloat16)
    with torch.device(dev):
        m = Gemma4ForCausalLM._from_config(cfg, dtype=torch.bfloat16)
    torch.set_default_dtype(torch.float32)
    mem("model qurildi")
    sd = m.state_dict()
    idx = json.load(open(os.path.join(path, "model.safetensors.index.json")))["weight_map"]
    pre, done = "model.language_model.", set()
    # safetensors'ni mmap'siz, tensorma-tensor o'qiymiz va o'qilgan qismni keshdan darhol bo'shatamiz:
    # mmap bilan butun shard (~25 GB) vaqtincha "band" ko'rinib, bo'sh xotirani 31 GB ga tushirgan.
    DT = {"BF16": torch.bfloat16, "F16": torch.float16, "F32": torch.float32, "I64": torch.int64,
          "I32": torch.int32, "U8": torch.uint8, "BOOL": torch.bool}
    for shard in sorted(set(idx.values())):
        with open(os.path.join(path, shard), "rb", buffering=0) as f:
            hl = int.from_bytes(f.read(8), "little")
            header = json.loads(f.read(hl))
            base = 8 + hl
            for k, info in header.items():
                if k == "__metadata__" or not k.startswith(pre):
                    continue                           # rasm/ovoz qismlari kerak emas
                name = "model." + k[len(pre):]
                if name not in sd:
                    continue
                a, b = info["data_offsets"]
                f.seek(base + a)
                buf = bytearray(b - a)
                f.readinto(buf)
                t = torch.frombuffer(buf, dtype=DT[info["dtype"]]).view(info["shape"])
                sd[name].copy_(t)
                del t, buf
                os.posix_fadvise(f.fileno(), base + a, b - a, os.POSIX_FADV_DONTNEED)
                done.add(name)
                if len(done) % 200 == 0:
                    mem(f"{len(done)} tensor")
    missing = [k for k in sd if k not in done and k != "lm_head.weight"]
    if missing:
        print("DIQQAT, yuklanmagan:", missing[:10], flush=True)
    m.lm_head.weight = m.model.embed_tokens.weight     # bog'langan
    return m


t0 = time.time()
target = load_target(args.target)
lm = target.model                                      # Gemma4TextModel
lm_head_w = target.lm_head.weight                      # [V, 2816] (embed bilan bog'langan)
softcap = target.config.final_logit_softcapping
target.requires_grad_(False).eval()
torch.cuda.empty_cache()
print(f"Gemma yuklandi {time.time()-t0:.0f}s, GPU {torch.cuda.memory_allocated()/2**30:.1f} GiB", flush=True)
if args.load_test:
    raise SystemExit

drafter = Gemma4AssistantForCausalLM.from_pretrained(args.drafter, dtype=torch.float32,
                                                     attn_implementation="sdpa").to(dev)
drafter.train()
print(f"modellar yuklandi {time.time()-t0:.0f}s, GPU {torch.cuda.memory_allocated()/2**30:.1f} GiB", flush=True)
SW = drafter.config.get_text_config().sliding_window  # 1024
THINK_END = AutoTokenizer.from_pretrained(args.drafter).convert_tokens_to_ids("<channel|>")
print("o'ylash oxiri tokeni:", THINK_END, flush=True)


def target_pass(seq):
    """Gemma: yashirin holatlar va 28/29-qatlam K/V (o'qitilmaydi)."""
    with torch.no_grad():
        out = lm(input_ids=seq[None], use_cache=False, return_shared_kv_states=True)
    kv = {k: (v[0].detach(), v[1].detach()) for k, v in out.shared_kv_states.items()}
    return out.last_hidden_state[0], kv


def target_logits(h):
    lg = (h @ lm_head_w.T).float()
    if softcap:
        lg = torch.tanh(lg / softcap) * softcap
    return lg


def masks(pos, L):
    j = torch.arange(L, device=dev)[None, :]
    i = pos[:, None]
    full = j <= i
    slide = full & (j > i - SW)
    return {"full_attention": full[None, None], "sliding_attention": slide[None, None]}


def draft_step(emb, hid, pos, kv, m):
    x = drafter.pre_projection(torch.cat([emb, hid], -1))[None]
    out = drafter.model(inputs_embeds=x, attention_mask=m, position_ids=pos[None],
                        shared_kv_states=kv, use_cache=False)
    h = out.last_hidden_state[0]                       # normlangan, 1024
    return h, drafter.post_projection(h)


def kl_ce(h_draft, t_hidden, labels):
    """Bo'laklab: KL(p_gemma || p_draft) + ce_w * CE. Har pozitsiya uchun argmax mosligi (bool) ham qaytadi."""
    tot, hits, n = 0.0, [], h_draft.shape[0]
    for a in range(0, n, args.kl_chunk):
        b = min(n, a + args.kl_chunk)
        dl = (h_draft[a:b] @ drafter.lm_head.weight.T).float()
        with torch.no_grad():
            tl = target_logits(t_hidden[a:b])
            tp = F.softmax(tl, -1)
            tlog = F.log_softmax(tl, -1)
        kl = (tp * (tlog - F.log_softmax(dl, -1))).sum(-1).sum()
        ce = F.cross_entropy(dl, labels[a:b], reduction="sum")
        tot = tot + kl + args.ce_w * ce
        hits.append((dl.argmax(-1) == tl.argmax(-1)).detach())
        del tl, tp, tlog
    return tot / n, torch.cat(hits)


def run(rec, train=True):
    seq = torch.tensor((rec["prompt_ids"] + rec["ids"])[-args.max_len:], device=dev)
    L, start = seq.numel(), max(2, seq.numel() - len(rec["ids"]))
    pos = torch.arange(start - 2, L - 1 - args.steps, device=dev)   # x[i+1+s] mavjud bo'lishi uchun
    if pos.numel() < 4:
        return None
    if train and pos.numel() > args.max_pos:                        # xotira: tasodifiy uzluksiz oyna
        a = random.randint(0, pos.numel() - args.max_pos)
        pos = pos[a: a + args.max_pos]
    # o'ylash tugagan joy (<channel|>): undan keyingi tokenlar — foydalanuvchiga ko'rinadigan javob
    ends = (seq == THINK_END).nonzero()
    think_end = int(ends[-1]) if ends.numel() else start
    H, kv = target_pass(seq)
    m = masks(pos, L)
    embed = lm.embed_tokens
    hid, losses, hits = H[pos].float(), [], []
    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx, torch.autocast("cuda", dtype=torch.bfloat16):
        for s in range(args.steps):
            emb = embed(seq[pos + 1 + s]).float()
            h, hid = draft_step(emb, hid, pos, kv, m)
            loss, hit = kl_ce(h, H[pos + 1 + s], seq[pos + 2 + s])
            losses.append(loss); hits.append(hit)
    total = sum(w * l for w, l in zip(W, losses)) / sum(W)
    answer = (pos + 2) > think_end                                  # bashorat qilinayotgan token javobda
    return total, [l.item() for l in losses], hits, answer


# ---------------------------------------------------------------- ma'lumot
recs = []
for l in open(args.data, encoding="utf-8"):
    r = json.loads(l)
    if r.get("ids") and r.get("prompt_ids") and len(r["ids"]) >= 8:
        recs.append(r)
random.shuffle(recs)
if args.limit:
    recs = recs[: args.limit + args.eval_n]
evals, recs = recs[: args.eval_n], (recs if args.overfit else recs[args.eval_n:])
print(f"o'qitish {len(recs)}, sinov {len(evals)}", flush=True)


def evaluate(tag):
    """Til va qism (o'ylash / javob) bo'yicha har qadamdagi argmax mosligi."""
    drafter.eval()
    by = {}
    for r in evals:
        o = run(r, train=False)
        if o is None:
            continue
        _, _, hits, answer = o
        for part, msk in (("o'ylash", ~answer), ("javob", answer)):
            if msk.sum() == 0:
                continue
            d = by.setdefault((r["lang"], part), [[0.0] * args.steps, 0])
            for s in range(args.steps):
                d[0][s] += hits[s][msk].sum().item()
            d[1] += int(msk.sum())
    drafter.train()
    print(f"[SINOV {tag}] argmax mosligi, qadamlar 1/2/3:", flush=True)
    for (lg, part), (v, c) in sorted(by.items()):
        print(f"    {lg:2s} {part:8s} " + " / ".join(f"{x/c:5.1%}" for x in v) + f"   ({c} token)", flush=True)


# ---------------------------------------------------------------- o'qitish
total_steps = int(len(recs) * args.epochs)
opt = torch.optim.AdamW(drafter.parameters(), lr=args.lr, betas=(0.9, 0.95), weight_decay=0.0)
warm = args.warmup
sched = torch.optim.lr_scheduler.LambdaLR(
    opt, lambda u: min(1, (u + 1) / warm) * 0.5 * (1 + math.cos(math.pi * min(1, u * args.accum / max(1, total_steps)))))
evaluate("boshlang'ich")
t0, run_l, run_a = time.time(), [], []
for it in range(total_steps):
    o = run(recs[it % len(recs)])
    if o is None:
        continue
    loss, ls, hits, _ = o
    (loss / args.accum).backward()
    del loss
    run_l.append(ls); run_a.append([h.float().mean().item() for h in hits])
    if it == 0 or it == 9:
        print(f"  [{it+1}-namuna] xotira cho'qqisi {torch.cuda.max_memory_allocated()/2**30:.1f} GiB, bo'sh "
              f"{int(open('/proc/meminfo').read().split('MemAvailable:')[1].split()[0])/2**20:.0f} GiB", flush=True)
    if (it + 1) % args.accum == 0:
        torch.nn.utils.clip_grad_norm_(drafter.parameters(), 1.0)
        opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
    if (it + 1) % 100 == 0:
        k = len(run_l)
        la = [sum(x[s] for x in run_l) / k for s in range(args.steps)]
        aa = [sum(x[s] for x in run_a) / k for s in range(args.steps)]
        el = time.time() - t0
        print(f"{time.strftime('%H:%M')} {it+1}/{total_steps} loss " + "/".join(f"{x:.3f}" for x in la) +
              "  mos " + "/".join(f"{x:.1%}" for x in aa) +
              f"  {el/(it+1):.2f}s/namuna  qoldi ~{(total_steps-it-1)*el/(it+1)/3600:.1f} soat"
              f"  xotira cho'qqisi {torch.cuda.max_memory_allocated()/2**30:.0f} GiB", flush=True)
        run_l, run_a = [], []
    if (it + 1) % args.save_every == 0 or it + 1 == total_steps:
        evaluate(f"{it+1}")
        sd = {k: v.detach().to(torch.bfloat16) for k, v in drafter.state_dict().items()}
        drafter.save_pretrained(args.out, state_dict=sd)
        for f in ("tokenizer.json", "tokenizer_config.json", "generation_config.json"):
            if os.path.exists(os.path.join(args.drafter, f)):
                shutil.copy(os.path.join(args.drafter, f), args.out)
        os.system(f"chmod -R a+rX {args.out}")
        print(f"saqlandi: {args.out}", flush=True)
