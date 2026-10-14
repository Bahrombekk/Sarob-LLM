# Sarob latency and quality experiment plan (one DGX Spark, serial execution)

**Ranking rule:** experiments are ordered by expected gain divided by (effort × risk). Run them top to bottom. Change one thing per restart and keep a change only if it passes its gate.

**Standard measurements, referred to by name below**
- **SPEED**: the existing speed benchmark. TTFT p50 and decode tok/s on the 4 Uzbek prompts, 3 runs each, temperature 0.
- **EVAL**: the 30-test Uzbek agent eval, run through the Open WebUI `/api/chat/completions` endpoint with the Sarob model id, so the tools, system prompt and thinking budgets are all included. Record the score, the tool-call rate on fact questions, invented numbers, loops (any 8-gram repeated 3 or more times), share of Cyrillic characters, thinking tokens, and p50/p90 wall time.
- **PC**: prefix-cache delta. Run `curl -s localhost:8000/metrics | grep -E 'vllm:(prefix_cache_(queries|hits)|prompt_tokens)'` before and after a test turn, and report Δhits/Δqueries.
- **ACC**: speculative-decoding acceptance. Mean acceptance length = 1 + Δaccepted/Δdrafts, from the `vllm:spec_decode_num_*` counters.
- **MEM**: `grep MemAvailable /proc/meminfo` with every service running. This must stay at 15 GiB or more.
- **Global gate:** EVAL score must not drop, and the number of loops and invented numbers must not rise.

**Before you start (no GPU needed, start at minute 0):** run these downloads in the background, about 2 hours in total at 5-8 MB/s:
- `huggingface-cli download unsloth/gemma-4-26B-A4B-it-NVFP4` (~16 GB), first.
- `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic` (~28 GB), second.

---

## A) Quick wins (each under 15 minutes)

### A0. Baseline and instrumentation (do this first)
- **Change:**
  - Add `--enable-prompt-tokens-details` to both serve commands. Make sure `--disable-log-stats` is not set.
  - Create `~/bin/pc.sh` containing `curl -s localhost:${1:-8000}/metrics | grep -E '^vllm:(prefix_cache_(queries|hits)|prompt_tokens)'`.
- **Measure:**
  - SPEED, EVAL, ACC.
  - A 4-turn chat (plain question, follow-up, web-search question, follow-up) with PC and `usage.prompt_tokens_details.cached_tokens` recorded for every turn.
  - A context-length curve: the same 400-token Uzbek generation with padded prefixes of 1k, 4k, 8k and 16k tokens, recording tok/s and ACC at each.
  - Grep the startup log for `max_num_batched_tokens`, `GPU KV cache size`, `Maximum concurrency`, any kv-scale or "default scale" warnings, and "Using … MoE backend".
- **Success:** you have a baseline JSON. Within a turn, tool-round PC should be above 80%.
  - If turn 2 and later show hits stuck at roughly the size of the system prompt, the cache is being broken from Open WebUI's side. Go to A1.
  - If even identical repeated curl prompts show about 0 cached tokens, you have hit the hybrid-SWA + MTP bug (vLLM #40624/#44082/#48435). A/B two variants: `--disable-hybrid-kv-cache-manager --max-model-len 65536` at util 0.35, and the same with `--speculative-config` removed. Make that the top priority.
- **Rollback:** none needed. These are read-only checks.

### A1. Remove the things that break the prefix cache (biggest latency lever for multi-turn chats)
Apply the four changes separately, measuring PC and follow-up TTFT after each one.
- **a) Time variables.** Run `grep -o '{{[A-Z_]*}}'` on the Sarob, Sarob Tez and Pro system prompts. Replace `{{CURRENT_TIME}}` or `{{CURRENT_DATETIME}}` with `{{CURRENT_DATE}} {{CURRENT_WEEKDAY}}`. These two variables render with seconds, so every request is a full cache miss.
- **b) Memory system context.** Set env `ENABLE_MEMORY_SYSTEM_CONTEXT=false` and also turn off Admin › Settings › General › Memory System Context, because the value stored in the DB wins over env. Keep `ENABLE_MEMORIES=true` so the memory tools still work. Copy the 5-10 most stable user facts into the system prompt, plus the line: "Foydalanuvchi haqida savol bo'lsa avval xotira vositasini chaqir." If you want automatic memory back later, see B3.
- **c) Citations.** In Admin › Models › Sarob, Sarob Tez and Pro › Capabilities, untick Citations. Add "Manbalarni URL bilan keltir" to the static prompt.
  - This only helps if your custom tools emit source events. If PC does not change, revert.
- **d) Open Terminal connection.** Set `working_directory_context=false`. Set `user_shell_tools` to a non-auto option only if the UI offers one. Keep the enabled tool set identical across chats. Keep `RAG_SYSTEM_CONTEXT=False`.
- **Measure:** a chat of about 10k tokens (1 web search plus 2 screenshots) followed by 3 short follow-ups. Record PC and TTFT for each turn.
- **Success:** follow-up PC above 90%, follow-up TTFT under 0.5 s, and an EVAL memory/personalization regression of at most one test.
- **Rollback:** toggle each setting back.

### A2. Remove the hidden extra LLM call on document uploads
- **Change:**
  - `ENABLE_RETRIEVAL_QUERY_GENERATION=False`. This is the setting that actually removes the extra Gemma round trip. Setting `RAG_FULL_CONTEXT=True` alone does not.
  - `RAG_FULL_CONTEXT=True`, or `BYPASS_EMBEDDING_AND_RETRIEVAL=True` if you never need vector search over files.
  - Change these in the Admin UI as well as env.
- **Measure:** a 10-20 page Uzbek PDF with 2 questions. Record end-to-end time, whether the "retrieval" query-generation call appears in the Open WebUI log, and whether the answers are correct.
- **Success:** 2 s or more faster per document turn, with correct answers.
- **Rollback:** revert the flags.

### A3. Runaway-generation guard
- **Change:**
  - In Sarob and Sarob Tez › Advanced Params › Custom, add `repetition_detection = {"max_pattern_size":64,"min_pattern_size":8,"min_count":4}`. Leave it off the Excel/table path, or use `min_count` 6 there.
  - Set env `CHAT_RESPONSE_MAX_TOOL_CALL_ITERATIONS=10`.
- **Measure:**
  - One curl request with a known looping prompt and `max_tokens` 4000, with and without the field. The response must not be HTTP 400 when MTP is on.
  - SPEED, 5 normal chats, 1 Excel chat.
- **Success:** loops cut early, no normal answers truncated, tok/s within 2% of baseline.
- **Rollback:** remove the param.

### A4. Sampling audit
- **Change:**
  - Inspect the Advanced Params of each model and each checkpoint's `generation_config.json`. Remove any `repetition_penalty` above 1.0. Do not raise it for Uzbek, because it penalizes agglutinative suffixes and tool-call syntax.
  - A/B two Gemma settings: the current temperature (reportedly 0.3), against 1.0 / top_p 0.95 / top_k 64 (Google's recommendation).
  - Keep temperature at 0.2-0.3 for OCR and Excel calls.
- **Measure:** SPEED, ACC, EVAL loop count, 10 long Uzbek generations.
- **Success:** adopt 1.0/0.95/64 only if ACC stays at 3.0 or above and EVAL plus the loop count are not worse. Otherwise keep the current values. 0.7 is a middle option if neither is clearly better.
- **Rollback:** restore the previous params.

### A5. MTP verification mode A/B (lossless, two restarts)
- **Change:** test three variants of `--speculative-config`:
  - (i) `{"method":"mtp","model":"<assistant>","num_speculative_tokens":4,"draft_sample_method":"probabilistic"}`
  - (ii) (i) plus `"rejection_sample_method":"block"`
  - (iii) greedy plus `"rejection_sample_method":"block"`
- **Measure:** SPEED, ACC, and 3 long Uzbek prose prompts (8k context, 600 output tokens).
- **Success:** keep the variant with the best tok/s on long Uzbek prose, and only if it is at least 3% better. At temperature 0.3, probabilistic can lose to greedy.
- **Rollback:** restore the original config.

### A6. Replay Gemma's reasoning inside the tool loop
- **Change:** on the :8000 connection, set Admin › Connections › Advanced › Provider = `llama.cpp`. First check that the template contains `message.get('reasoning') or message.get('reasoning_content')`. Apply A3 first as a safety net.
- **Measure:**
  - `prompt_tokens` on the second loop iteration should rise by a few hundred tokens, which proves the reasoning is being sent.
  - 8 multi-step tasks from EVAL, 2 runs each, recording tool calls, thinking tokens, wall time, correctness and loops.
  - Watch for HTTP 400 errors and broken tool-call parsing.
- **Success:** fewer tool rounds or a better score, with no extra loops. Apply to :8001 only after Gemma passes.
- **Rollback:** set the provider back to blank.

### A7. CPU pinning and governor
- **Change:**
  - Check the real core map: `for c in /sys/devices/system/cpu/cpu[0-9]*; do echo $c $(cat $c/cpufreq/cpuinfo_max_freq); done`.
  - Pin both vLLM containers to the big X925 cores (reportedly `--cpuset-cpus=5-9,15-19`; trust your own map over this).
  - Pin Open WebUI, Chromium/Playwright, SearXNG, Jupyter, Terminal and Ollama to the little cores.
  - If the governor is not already `performance`, run `cpupower frequency-set -g performance`.
- **Measure:** SPEED idle, and SPEED while deep research or `stress-ng --cpu 10 --taskset <little>` runs. Also record end-to-end web-search time.
- **Success:** tok/s under load within 3% of idle, TTFT p90 not worse, and the web-search path not more than 10% slower.
- **Rollback:** remove `--cpuset-cpus`.

### A8. Warmup and IPC
- **Change:** in the start script, after `/health` returns OK, send one tiny chat request (`max_tokens` 3) plus one image request to Gemma. Keep `--ipc=host` on both vLLM containers.
- **Measure:** first real request after a restart, with and without the warmup.
- **Success:** the 10-25 s first-request penalty is gone.
- **Rollback:** remove the warmup step.

### A9. Open WebUI env hygiene
- **Change:**
  - `UVICORN_WS_PER_MESSAGE_DEFLATE=false`
  - `ENABLE_CHAT_RESPONSE_STREAM_INPLACE_APPEND=true`
  - `GLOBAL_LOG_LEVEL=WARNING`
  - Keep `UVICORN_WORKERS=1`, `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=1` and `ENABLE_TOOL_SEARCH=false`.
- **Measure:** a 1500-token answer 3 times, with `docker stats` CPU and wall time.
- **Success:** no regression.
- **Rollback:** revert the env.

### A10. Pro answer-language rule
- **Change:** add one line to the Sarob Pro system prompt: "Reason internally in English. Write the final answer only in Uzbek (Latin script); keep numbers, names, code unchanged."
- **Measure:** EVAL on Pro, Cyrillic %, share of English words, thinking tokens.
- **Success:** quality the same or better and no English leakage. The saving in thinking tokens may be close to zero.
- **Rollback:** remove the line.

### A11. Thermal and clock check (measure only)
- **Change:** none unless throttling shows up. During deep research plus the 11-screenshot job, log `nvidia-smi --query-gpu=timestamp,clocks.sm,power.draw,temperature.gpu,clocks_event_reasons.active --format=csv -l 1`.
- **If throttling appears or the box freezes again:** add a systemd unit that runs `nvidia-smi -pm 1; nvidia-smi -lgc 0,2100`, and apply DGX OS and firmware updates in a maintenance window.
- **Success:** with the cap, decode within 2% and prefill within 5% of uncapped.
- **Rollback:** `nvidia-smi -rgc`.

### A12. `max_num_batched_tokens` check
- **Change:** only if the A0 log shows a value below 16384, add `--max-num-batched-tokens 16384` on Gemma.
- **Measure:** a cold 15k-token prompt (unique first line) and the 11-image request, TTFT median of 3. Check that the KV cache size is still far above 131072 tokens.
- **Success:** at least 5% lower cold TTFT. If the current value is already 8192, expect only a marginal gain; a low-priority A/B is still fine.
- **Rollback:** remove the flag.

---

## B) Medium (30 minutes to half a day each)

### B1. Swap the Gemma checkpoint to `unsloth/gemma-4-26B-A4B-it-NVFP4` (first model change)
- **Change:**
  - Inside the 0.31 container, run `pip show flashinfer-python nvidia-cutlass-dsl` and confirm versions of at least 0.6.13 and 4.5.2.
  - Start a test container on :8002, or stop :8001 temporarily. Same flags as :8000, except:
    - no `--quantization`
    - drop `--moe-backend marlin` (auto; the model card says Marlin is about 2x slower; never use `flashinfer_b12x`)
    - util 0.35, fp8 KV only if the A0-style log shows calibrated scales, otherwise `auto` (see B11)
  - Sweep `num_speculative_tokens` over 2, 3 and 4. Use `VLLM_USE_V2_MODEL_RUNNER=1` only if the drafter fails with a "same reduction dim" error.
- **Measure:** SPEED, ACC, `vllm bench serve --backend openai-chat --dataset-name random --random-input-len 8000 --random-output-len 512 --num-prompts 10 --max-concurrency 1` against both ports, and EVAL including the 11-screenshot OCR case and a tool-call case.
- **Success:** median TPOT at 8k at least 10% better, and EVAL, OCR and tool calls equal. Expected: about 60-70 tok/s.
- **Rollback:** point Open WebUI back at the old container.

### B2. Thinking-budget router (request-level filter; `enable_thinking` stays fixed)
- **Change:** add an Open WebUI Filter that uses the 0.12 `request()` hook. That hook runs before every model call, including post-tool calls, so no proxy is needed for Open WebUI.
  - **Never toggle `enable_thinking`.** Gemma puts `<|think|>` at position 0 of the prompt, so flipping it invalidates the whole cached prefix. Set only `body["thinking_token_budget"]`:
    - last message has role `tool`: 192
    - greeting, rewrite, translation or short message with no digits: 32. Try 0 only after confirming no `<|channel>` text leaks into the content.
    - OCR or table extraction: 64
    - math, logic or trick markers (digits plus operators, nechta, qancha, hisobla, nega, isbotla, solishtir, "agar … bo'lsa"): 1024
    - everything else: 384
  - Always set `max_tokens` to at least budget + 2048.
  - Keep `reasoning_end_str` exactly `<channel|>` for Gemma and `</think>` for Qwen. Never add a transition phrase to it.
  - Port the same logic into the Telegram bot's agent loop.
- **Measure:**
  - EVAL, plus a 30-prompt set (10 easy, 10 tool, 10 trick), recording wall time, thinking tokens, tool calls and correctness.
  - Sweep the post-tool budget over 0, 128, 256 and 512 on the tool prompts.
  - PC across a 5-turn chat that alternates tiers. It must stay above 90%.
- **Success:** median latency down 30% or more, and trick-question accuracy at least as good as baseline. Expected: simple questions about 1.5-3 s, web answers 10-20 s faster.
- **Rollback:** disable the filter.

### B3. Context Slimmer request filter (keep automatic memory without breaking the cache; trim history)
- **Change:** the `request()` filter from the context-management lens, at priority 999.
  - Move the `<memory_context>` block out of the system message to the front of the last real user message (only if A1b was reverted).
  - Strip images from user turns older than `keep_image_turns=2`.
  - Trim tool results from older turns to `old_tool_chars=2500`.
  - Wrap the whole body in `try/except: return body`.
  - First debug-print the role and first 80 characters of every message, to confirm the exact 0.12 synthetic message wording "Here are the images from the tool results above".
- **Measure:** the long chat (11 screenshots to Excel, then 2 web turns). Record `prompt_tokens`, TTFT and PC, plus 5 recall questions about earlier turns.
- **Success:** prompt tokens down 60% or more, PC above 85%, no recall regression on questions the earlier answers can cover. Then tighten to `keep_image_turns=1` and `old_tool_chars=1500`.
- **Rollback:** disable the filter.

### B4. Fact-first filter (stops invented numbers)
- **Change:** in the same request filter or a separate inlet filter.
  - For narrow regex matches (`kurs|dollar|yevro|rubl|so'm|курс|USD|EUR`): call the CBU API directly (about 100 ms) and append `<fakt_manba vaqt=…>…</fakt_manba>` to the last user message.
  - For `narx|necha pul|yangilik|natija|ob-havo|kim yutdi`: append a suffix that names the exact tool: "[Eslatma: avval <tool_name> chaqir; tool natijasisiz raqam yozma.]"
  - Apply the suffix identically on every loop iteration, and never persist it to history.
  - Never use `tool_choice="required"`.
  - Add one stable system-prompt rule: changeable numbers must come from `<fakt_manba>` or a tool result, otherwise answer "aniq ma'lumot topilmadi".
- **Measure:** 15 prompts (5 currency, 5 price/news, 5 controls). Record tool rate, numbers that match the source, latency, and no prefetch on the controls.
- **Success:** tool or source use at 90% or more on fact prompts, zero invented numbers, currency answers in about 2-4 s.
- **Rollback:** disable the filter.

### B5. Batched web tool and output caps
- **Change:** rewrite the search tool as `web_search(queries: list[str], fetch_top: int = 3)`.
  - Run the SearXNG queries with `asyncio.gather` (concurrency 6 or less), deduplicate URLs, and fetch pages in parallel with httpx (4 s timeout). Fall back to Playwright (8 s) only for empty pages.
  - Rank paragraphs by keyword overlap and always keep paragraphs that contain digits or tables.
  - Caps: about 6000 characters per page, about 20000 characters in total. Deep research gets 3000 per page and 20000 in total.
  - Add `fetch_pages(urls: list[str])`.
  - Bilingual docstrings with "use when / do NOT use when" lines, plus "pass 2-4 queries (uz+ru/en) in ONE call".
  - Merge down to about 5-6 tools with flat schemas.
  - In the Telegram bot, run tool calls concurrently with `asyncio.gather`.
- **Measure:** 10 fixed Uzbek fact questions. Record end-to-end time, number of LLM iterations (count of POSTs in the vLLM log), final-hop `prompt_tokens`, and correctness.
- **Success:** median latency down 30% or more with no loss in correctness. Expected: 20-60 s down to 10-25 s.
- **Rollback:** reattach the old tools.

### B6. Excel tool rework
- **Change:**
  - Send one request per image with `asyncio.gather` and `Semaphore(4)` (also test 6). Body: `chat_template_kwargs {"enable_thinking": false}`, temperature 0, `max_tokens` 4096, and a fixed short system prompt asking for **TSV only**. Verify that `reasoning_content` comes back empty.
  - Pre-processing with PIL: crop borders and UI chrome. Split images only when height is more than twice the width and the image is over about 2.5 MP, into strips that overlap by 1-2 rows. Deduplicate only at strip boundaries. Upscale 2x only when text is under about 10 px.
  - Validation in Python: consistent column counts, numeric columns parse, totals match sums. Number normalization must handle NBSP, thin spaces and comma decimals, and keep codes with leading zeros as strings. On failure, retry that image once with thinking on (budget 512). Highlight unresolved cells yellow with openpyxl.
- **Measure:** the same 11 screenshots. Record wall time at semaphores 1, 4 and 6, total completion tokens, and wrong cells against hand-checked ground truth for 3 images. Also check chat TTFT while the job runs.
- **Success:** 30-60 s down to 15 s or less, wrong cells equal or fewer.
- **Rollback:** keep the old tool version as a second tool.

### B7. System prompt restructure and outlet filter
- **Change:**
  - **Prompt.** Use three blocks, all static and placed at the top, with nothing dynamic above them:
    - (a) English hard rules (about 400-600 tokens): tool before any changeable fact, step-by-step thinking for trick questions, also search in ru/en and translate the findings, at most 3 tool calls, cite [n] only for numbers that come from tools.
    - (b) Uzbek persona and output rules: Latin script only, consistent apostrophes.
    - (c) A glossary of 30-60 terms and 2 short exemplar Q → tool → answer dialogues.
  - Use the identical text in the Telegram bot. Confirm the rendered prompt once with `--enable-log-requests`, then turn that logging off.
  - **Outlet filter (regex only):**
    - Normalize to ASCII `o'` and `g'` so searches still match.
    - Transliterate Cyrillic to Latin only when Cyrillic is above 3% of letters and the user wrote in Latin. Skip code, URLs and Russian quotes.
    - Truncate repeated paragraphs.
    - Flag numbers of 3 or more digits (or followed by %, $ or so'm) that appear in no tool result or `<fakt_manba>`. Skip years, dates, numbers from the user's own message, and computed numbers.
- **Measure:** EVAL, 3 runs per variant. Record tool rate, numbers matching sources, Cyrillic %, trick-question accuracy and warm TTFT.
- **Success:** better tool rate and fewer invented numbers, no translationese according to a native-speaker spot check, warm TTFT unchanged.
- **Rollback:** keep the old prompt as a copy of the model.

### B8. Pro (Qwen3.8) MTP depth sweep
- **Change:** `num_speculative_tokens` 3, 4 and 5 with greedy drafting, then test `draft_sample_method: probabilistic` at the best N.
- **Measure:** SPEED on :8001 with thinking on, 2 long Uzbek prose prompts, and `vllm:spec_decode_num_accepted_tokens_per_pos`.
- **Success:** at least 8% more tok/s.
- **Rollback:** go back to N=3.

### B9. Adaptive verification on Gemma
- **Change:** `{"method":"mtp","model":"<assistant>","num_speculative_tokens":6,"enable_adaptive_verification":true}` plus the winning draft method from A5. No `--enforce-eager`. Use the default profile context of 8192.
- **Measure:** check the log for a ValueError about TRITON_ATTN and varlen decode (that would be a clean failure). Then SPEED, ACC, long Uzbek prose, and a 1k-token table-to-JSON prompt. Run MEM.
- **Success:** prose speed equal or better and structured output faster.
- **Rollback:** go back to the A5 config.

### B10. Memory hygiene
- **Change:**
  - `systemctl set-default multi-user.target` (headless).
  - `/etc/sysctl.d/99-llm.conf` with `vm.swappiness=1` and `vm.dirty_bytes=268435456`. No zram.
  - Run `sync; echo 3 > /proc/sys/vm/drop_caches` once, before the first engine starts.
  - Start the larger engine first, then the second.
  - Optionally size KV explicitly with `--kv-cache-memory-bytes` (for example Gemma 10G, Qwen 6G). Confirm the log reports a matching KV size and maximum concurrency of 2 or more at 131072.
- **Measure:** MEM before and after, `vmstat 1` with si/so, one 30-image 50k-token request in parallel with a Telegram request, and the logs for preemption.
- **Success:** 5 GiB or more additional free memory, no preemption, no swapping. That headroom pays for B11 and C1.
- **Rollback:** go back to `graphical.target` and remove the flags.

### B11. KV cache dtype, per checkpoint
- **Change:**
  - NVIDIA checkpoint: keep `fp8` (it ships calibrated scales; confirm there is no default-scale warning). Optionally A/B `auto` (BF16).
  - Unsloth and RedHat checkpoints: start with `auto`. If memory or speed suffers, A/B `fp8_per_token_head`, but only if `vllm serve --help` lists it.
- **Measure:** SPEED at 12k and 30k context, ACC, 10 long generations of 1500 tokens or more with a loop count, and MEM.
- **Success:** the loop count does not rise and decode or TTFT does not get worse by more than 3%.
- **Rollback:** restore the previous dtype.

### B12. Native context compaction
- **Change:** set these in the container env (plain env reads; recreate the container):
  - `ENABLE_CONTEXT_COMPACTION=true`
  - `CONTEXT_COMPACTION_TOKEN_THRESHOLD=30000` and `CONTEXT_COMPACTION_TOKEN_CAP=30000`
  - `CONTEXT_COMPACTION_RETENTION_PERCENTAGE=40`
  - `CONTEXT_COMPACTION_MODEL=<exact id of the Gemma no-think task model>`
  - an Uzbek prompt template that keeps `{{PREVIOUS_SUMMARY}}`, `{{COMPACTED_MESSAGES}}` and `{{RECENT_MESSAGES}}` and tells the model to keep numbers, URLs and file names
  - for Pro, the per-model param `compact_token_threshold=20000`
- **Measure:** temporarily lower the threshold to 6000 and run a 6-turn chat with specific numbers. Check for the "Compacted chat context" log line, ask 3 recall questions, and force a compaction in the middle of a tool loop to check that the second system message does not cause a template error in vLLM.
- **Success:** recall is correct and there are no template errors. If a mid-loop compaction errors, raise the threshold above the largest single-turn size.
- **Rollback:** `ENABLE_CONTEXT_COMPACTION=false`.

### B13. Two-engine interference
- **Change:** none. This is a measurement.
- **Measure:** the Gemma benchmark (5 runs × 8k input, 512 output) with Qwen (a) stopped, (b) idle, and (c) decoding at the same time.
- **Success and decision:** if (c) is more than 30% slower and that overlap happens often, test `--enable-sleep-mode` on Pro (needs `VLLM_SERVER_DEV_MODE=1`; experimental on GB10). Otherwise change nothing.

---

## C) Bigger bets (download, new code or more risk; run after A and B)

### C1. FP8-Dynamic Gemma target plus a GB10-tuned MoE config
Run this only if B1 stays below about 65 tok/s at 8k context, or as a direct A/B once the download finishes.
- **Change:**
  - Serve `RedHatAI/gemma-4-26B-A4B-it-FP8-Dynamic` (the `-it` variant is required).
  - Same MTP drafter, no `--moe-backend`, `--kv-cache-dtype auto` (see B11).
  - Util 0.40, then 0.42-0.45 only while MEM stays at 15 GiB or more. Lower Qwen to 0.25 or Gemma `max-model-len` to 65536 if needed.
  - Sweep gamma over 2, 3 and 4.
  - If the log says "Using default MoE config … E=128,N=704,device_name=NVIDIA_GB10,dtype=fp8_w8a8.json":
    - Stop both engines.
    - Run `benchmarks/kernels/benchmark_moe.py --model <local snapshot> --tp-size 1 --dtype fp8_w8a8 --tune --batch-size 1 2 4 5 8 10 16 20 32 40 64` from a v0.31.0 checkout inside the image. Check the script's arguments at that tag first. Expect 20-60 minutes unattended.
    - Mount the result with `-e VLLM_TUNED_CONFIG_FOLDER=/opt/vllm-tuned -v /opt/vllm-tuned:/opt/vllm-tuned`.
- **Measure:** same bench as B1, plus ACC, EVAL and MEM. Confirm the default-MoE-config warning is gone after tuning.
- **Success:** at least 15% better than the B1 winner, EVAL equal, MEM at 15 GiB or more. Realistic expectation: 65-85 tok/s, not 108.
- **Rollback:** go back to the B1 container.

### C2. "Sarob Auto" router and the `ask_pro` tool
- **Change:**
  - Create a workspace model "Sarob Auto" with native function calling, vision, and all tools.
  - Attach an inlet filter that rewrites `body["model"]`. Pin Open WebUI to 0.12.0, fall back to the original model in `try/except`, and validate target ids.
  - Fast and think tiers stay on **one** target model with the identical prompt and tools; only the B2 budget changes.
  - Pro is selected only on hard or code keywords in chats under about 4k tokens, and stays sticky for the rest of the chat.
  - Images always go to Gemma.
  - Overrides: `/tez`, `/pro`, `/o'yla`, or a "Pro" toggle filter detected through `__metadata__['filter_ids']`.
  - Log decisions to `/app/backend/data/router_log.jsonl`.
  - The `ask_pro(savol, kontekst)` tool calls :8001 with about 3k characters of context, `max_tokens` 2000, `thinking_token_budget` 1024 and a 90 s timeout. It returns the content, or a short error string if the content is empty.
- **Measure:**
  - Point every tier at Pro to confirm the rewrite reaches :8001.
  - Router overhead under 50 ms.
  - 20 prompts (8 trivial, 6 factual, 6 trick), plus PC across tiers.
  - 6 hard prompts, plus 5 easy prompts where `ask_pro` must not be called.
- **Success:** trivial-question median down 50% or more, trick accuracy above Sarob's.
- **Rollback:** go back to using "Sarob" directly.

### C3. Qwen3.6-35B-A3B as the "Tez" tier (already downloaded)
- **Change:** stop :8001 and serve Qwen3.6 there at util 0.28 with `--moe-backend` auto or `flashinfer_cutlass`, CUDA graphs on.
  - Thinking mode: temperature 1.0, top_p 0.95, top_k 20, min_p 0.
  - Test `presence_penalty` at 0.5, 1.0 and 1.5 (higher values risk mixing in Russian or Chinese).
  - Pass `chat_template_kwargs {"preserve_thinking": true}` in custom params, and confirm it arrives using the request log.
  - Test MTP on and off.
- **Measure:** the multi-step tasks where it looped before, EVAL, and the share of non-Uzbek tokens.
- **Success:** zero loops and EVAL within 5% of Gemma. Otherwise drop it.
- **Rollback:** restart Qwen3.8 on :8001.

### C4. RedHat all-linear NVFP4 (`RedHatAI/gemma-4-26B-A4B-it-NVFP4`)
- Run only after B1 and C1. Candidate for Sarob Tez only.
- **Success:** at least 15% faster than the main model's winner with **zero** regressions in EVAL and 10 trick questions. The FP4 penalty on Uzbek is a known risk.

### C5. DFlash2 for Pro
- **Change:** first check that `dflash` exists in 0.31's speculative methods. If it does not, drop this. If it does, serve `TH-44/FranQwen3.8-27B-NVFP4-DFlash2` with `{"method":"dflash","model":"z-lab/Qwen3.8-27B-DFlash2","num_speculative_tokens":7}` at util 0.31, with autotune still off.
- **Success:** Pro at least 20% faster, quality equal, MEM at 15 GiB or more. Keep the old Pro container for rollback.

### C6. DSpark drafter for Gemma
- Lowest priority. Use a test container with Pro stopped, `--max-model-len 32768`, `VLLM_USE_FLASHINFER_SAMPLER=0` and `{"method":"dspark","model":"<makora-ai/gemma4-26b-a4b-dspark>","num_speculative_tokens":6}`.
- **Success:** Uzbek prose at most 5% slower and table/JSON output clearly faster. Otherwise discard.

### C7. Dedicated OCR model (PaddleOCR-VL, or GLM-OCR)
- **Change:** on demand only, with MEM at 25 GiB or more: `--trust-remote-code --port 8002 --gpu-memory-utilization 0.06 --max-model-len 16384 --max-num-seqs 8 --no-enable-prefix-caching --mm-processor-cache-gb 0 --enforce-eager`.
  - PaddleOCR-VL returns OTSL markup (`<fcel>`, `<ecel>`, `<nl>`), so it needs a converter. GLM-OCR returns HTML that `pandas.read_html` can read.
- **Success:** wrong cells at most Gemma's and latency at least 2x lower. Start and stop it from inside the tool rather than keeping it resident.

### C8. Adaptive image budget
- **Change:** in an inlet filter, set `body["mm_processor_kwargs"]={"max_soft_tokens":560}` only when there are more than 4 images and the request is not an OCR or table task.
- **Check:** `usage.prompt_tokens` must drop. If it does not, per-request overrides are unsupported, so drop this.
- **Success:** large reductions in prompt size and TTFT on many-image chats, with no OCR loss.

### C9. Classifier for ambiguous tier decisions
- Use only if B2 or C2 heuristics misroute more than 10% of messages.
- **Change:** a separate request to :8000 with a fixed prompt, `enable_thinking` false (this is a separate request, so the main cache is unaffected), `structured_outputs {"choice":["tez","oyla","pro"]}`, `max_tokens` 8, and a 1.5 s timeout that falls back to "oyla". An alternative is bge-m3 centroids.
- **Success:** p50 under 250 ms and 85% or better accuracy.

### C10. Standard Uzbek benchmark baseline (optional)
- Run UzLiB with a 150-question subset at temperature 0 on Gemma and on Pro. Treat a difference of less than 4 points as noise.
- NeuronAI-4B as a proofreading action: only in a maintenance window with Pro stopped, util 0.10, `--max-model-len 8192 --max-num-seqs 2 --enforce-eager`. Never as a permanent third engine.

---

## Suggested serial schedule
- **Day 1:**
  - Start both downloads, then A0, A1, A2, A3, A4, A5, A7, A8, A9, A6, A10, A11, A12.
  - Then B2 and B4 (filters, no restarts).
- **Day 2:**
  - B1 (downloaded by now), B11, B10, B9, B8.
  - Then B5, B6, B3, B7, B12, B13.
- **Day 3 onward:** C1 (including tuning overnight), then C2, C3, and the rest of C as needed.

---

## Discarded recommendations and why

| Recommendation | Reason for discarding |
|---|---|
| Alternative attention backends (FA4, TRITON_FLASH_ATTN, TRITON_FLASHINFER, B12X, explicit FLASHINFER) | Either SM100-only or no 512 head dim on sm_121. FLASHINFER falls back to XQA without uniform CUDA graphs. Keep TRITON_ATTN. |
| MoE backend A/B on the current NVIDIA checkpoint (`flashinfer_cutlass`, `b12x`) | Measured within 1.4% on this checkpoint. The checkpoint swap (B1) is the real lever. `b12x` fails on Gemma (GELU-tanh). |
| ngram, ngram_gpu, suffix or EAGLE3 speculative methods for Gemma | Not dispatched in the 0.31 v2 runner. Only one method per engine, so they would lose MTP's ~3.3 acceptance. No public Gemma4 EAGLE3 checkpoint exists. |
| `"quantization":"fp8"` inside `speculative-config` | Ignored for MTP in 0.31. |
| z-lab DFlash for Gemma on stock 0.31 | Its required fixes (PR #41703) were closed without merging. |
| LMCache or native CPU KV offload | GB10 memory is unified, so offloading just copies within the same 273 GB/s pool, adds freeze risk, and historically disables the hybrid manager. |
| `--prefix-cache-retention-interval` CLI flag and `--log-stats` | Not valid flags. Retention is set through the `VLLM_PREFIX_CACHE_RETENTION_INTERVAL` env var; leave it at its default. Stats logging is on by default. |
| Toggling `enable_thinking` per request or turn in the main chat | Changes the first tokens of the prompt and invalidates the whole cached prefix. Use `thinking_token_budget` instead. It also risks tool calls leaking into text (vLLM #39043). |
| `tool_choice="required"` | Open WebUI reuses `form_data` in every loop round, so the model could never give a final answer. In vLLM it also goes through guided JSON instead of the gemma4 parser. |
| Switching between the Sarob and Sarob Tez workspace models within a chat | Different system prompts or tools invalidate the cache. Vary only the budget on one model. |
| Pipe or manifold router, Arena models, vLLM Semantic Router (vllm-sr) | Pipes lose Model controls and tool-loop behaviour. Arena picks at random. vllm-sr adds Envoy and BERT classifiers with no arm64/GB10 data. |
| `repetition_penalty` above 1.0 for Gemma (including the suggested 1.05) | Penalizes Uzbek suffix tokens and tool-call syntax. Use `repetition_detection` (A3) instead. |
| Raising `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE`, more Uvicorn workers, Redis | High-concurrency settings. For one user they only make streaming jerkier. |
| `ENABLE_TOOL_SEARCH` | Adds a `search_tools` round per tool use, and Gemma already skips tools. |
| Translate → think → translate pipeline | Adds 2-6 s per message and loses nuance. Covered by A10 and B7. |
| Uzbek fine-tune or LoRA of Gemma | No Gemma-4 Uzbek fine-tune exists, and LoRA on NVFP4 MoE in vLLM is unverified. Not a quick win. |
| New main model (Nemotron-3.5-Lightning, GLM-5.3-Flash, DeepSeek-V4.1-Flash, Qwen3.8-Flash-Next, Gemma 4 12B, Holo3, Ornith) | Text-only, no Turkic languages, too large for the memory budget, or slower. Gemma 4 26B stays. |
| Gemma-4-31B dense as Pro | Only +0.005 on UzLiB and slower at 273 GB/s. |
| Blanket per-model drop of the image budget to 280 | Uzbek chat screenshots are often documents, so OCR would suffer. Replaced by the adaptive C8. |
| `logit_bias` ban on Cyrillic | Would need thousands of token ids per request. The outlet transliteration in B7 is enough. |
| zram, or permanent third engines (NeuronAI-4B, OCR VLM) | Eat the same unified memory pool and raise freeze risk. On demand only. |
| Logging router decisions to the read-only SQL DB | That DB cannot be written to. Use a JSONL file. |
| `--enforce-eager` on the main engines | CUDA graphs were worth about 3x on NVFP4 MoE on GB10, and adaptive verification needs full graphs. |
| Treating the 108 tok/s FP8 + MTP result as the expectation | Measured at 4k context, no images, util 0.85, from a single source. Plan for 65-85 tok/s. |