# Bench inventory: `model_spec.md` + `bench_log.csv`

Paths: `starterkit(1)/starter_kit/bench/model_spec.md`, `starterkit(1)/starter_kit/bench/bench_log.csv`.  
No serving job was re-run. Values below are read from those files.

## Setup stated in `model_spec.md`

- Model: FLM-4B-Instruct (dense). Parameters 4.2 B; 28 layers; d_model 3072; 24 Q heads; 8 KV heads (GQA); head_dim 128; vocab 128k; weights fp16; KV cache fp16 (table L6–L15).
- Hardware: 1× NVIDIA L4 24 GB; peak memory bandwidth 300 GB/s; peak fp16 dense ~121 TFLOPS (L21–L23).
- Serving: `max_model_len` 4096; `gpu_memory_utilization` 0.92; non-KV runtime overhead **assume ~1.6 GB** (L24–L26) — the word “assume” means this overhead is **not** claimed as measured in the CSV.
- Load-test protocol (L30–L32): each CSV row is one run; `num_requests` identical requests submitted **simultaneously**; given `prompt_len` and `gen_len`; all requests generate **exactly** `gen_len` tokens, no early stopping.

## CSV shape

Header + 13 data rows. Two prompt/gen families:

- Short: `prompt_len=512`, `gen_len=256`, `batch_size` in {1,2,4,8,16,32,64}, and in every such row `batch_size == num_requests`.
- Long: `prompt_len=3584`, `gen_len=512`, `batch_size` in {4,8,16,24,32,48}, again `batch_size == num_requests` on every row.

That equality is an observation in this file, not a definition in `model_spec.md`.

## Column dictionary

| Column | What `model_spec.md` says | Unit (stated or inferred) | Measured vs derived (as specified) | Ambiguity / not 100% sure |
|---|---|---|---|---|
| `batch_size` | Not in “Column notes.” Protocol talks about simultaneous identical requests with given `prompt_len` / `gen_len`. | dimensionless count | **Unclear** — appears as an independent CSV field | **High.** No sentence defines batch_size vs `num_requests`. In this log they are always equal. Could mean scheduler max batch, engine `--max-num-seqs`, or just a duplicate of `num_requests`. |
| `prompt_len` | Protocol: requests submitted with the given `prompt_len` | tokens (implied; not labeled) | Stated as an input to the run (controlled), not a measured outcome | **Medium.** Prefill tokens? With or without special/BOS tokens? Truncation vs `max_model_len` 4096? 3584+512=4096, which equals `max_model_len` — whether that includes both sides is not stated. |
| `gen_len` | Protocol: all requests generate exactly `gen_len` tokens, no early stopping | tokens (implied) | Controlled input | **Low–medium.** Decode steps excluding prompt, presumably. EOS handling given “no early stopping” is not described. |
| `num_requests` | Protocol: that many identical requests submitted simultaneously | count | Controlled input | **Low** for the count itself. “Simultaneously” vs queued vs continuous batching over `wall_clock_s` is not detailed. |
| `wall_clock_s` | **Not defined** in `model_spec.md` | seconds (name) | **Unspecified.** Present only in the CSV | **High.** Start/stop: first submit → last token of last request? includes startup/compile? sync CUDA? This matters if anyone later reconstructs tok/s from wall clock. |
| `reported_tok_s` | “the harness's built-in throughput counter” (L36) | tokens / second (name) | Described as harness-reported; **not** given as a formula | **High — Part B critical.** Numerator unknown: generated tokens only vs prompt+gen vs all sequences summed. Denominator unknown: `wall_clock_s` vs decode-only vs excluding TTFT. Prefill vs decode mix. REPORT_v0 treats this as the throughput to plan from. |
| `ttft_ms_p50` | “median time to first token” (L37) | milliseconds | Described as a latency statistic (measured by harness) | **Medium.** Median across requests? Across tokens? Clock start: tokenize / queue / first GPU kernel? First token = first decode token after prefill? |
| `itl_ms_p50` | “median inter-token latency during decode” (L38) | milliseconds | Measured (harness) | **Medium.** Per-request then median, or median over all inter-token gaps in the run? Includes or excludes first token? |
| `e2e_ms_p95` | “p95 end-to-end request latency” (L39) | milliseconds | Measured (harness) | **Medium.** p95 over the `num_requests` in that row? Definition of end-to-end (submit → last token)? For n=1, p95 is degenerate. |
| `preempted_seqs` | “sequences the scheduler preempted at least once” (L40) | count of sequences | Measured (harness) | **Medium.** Preempt = KV swap / recompute? Count of sequences vs preemption events? Rows show 0 until long bs=32 (7) and bs=48 (23). |
| `kv_cache_util` | “peak KV cache block utilization” (L41) | **Unstated.** Values in {0.01,…,0.97} look like **fractions in [0,1]**, not percents | Measured peak (harness) | **High.** Fraction of allocated KV blocks? of GPU memory? of `gpu_memory_utilization` budget after the assumed 1.6 GB? Peak over time vs end-of-run? |

## Cross-checks recorded (reads only, not a new bench)

REPORT_v0 §2 numbers vs this CSV (same files):

| Report text | Closest CSV fields | CSV `reported_tok_s` |
|---|---|---|
| batch 16, long prompts, 1311 tok/s | `batch_size=16`, `prompt_len=3584`, `gen_len=512` | **1311.4** |
| 883 tok/s short prompts | `batch_size=16`, `prompt_len=512`, `gen_len=256` | **883.2** |
| ~1600 tok/s best observed | long-prompt max is **1607.4** at bs=24; global max is **2267.3** at short bs=64 | see both |
| batch 48 ~3200 tok/s (extrapolation) | row exists: bs=48, prompt 3584, gen 512 | **1298.5** |

`kv_cache_util` at those batch-16 rows: 0.12 (short) vs 0.62 (long). REPORT_v0’s “better GPU utilization” is **not** a defined column; this is the nearest named utilization-like field.

Naive `num_requests * gen_len / wall_clock_s` is **not** computed here (would be a later-phase derivation). Flag only: `reported_tok_s` may or may not equal that; definition is ambiguous.

## What we are not 100% sure of (carry to Part B)

1. Exact formula for `reported_tok_s`.
2. Meaning of `batch_size` when `num_requests` already exists.
3. Whether `wall_clock_s` is the denominator of `reported_tok_s`.
4. Unit/scale of `kv_cache_util` (fraction vs other).
5. Whether long vs short comparisons hold `gen_len` constant (they do not: 512 vs 256).
6. Whether 3584+512 vs `max_model_len` 4096 is coincidence or a packed-to-limit setup.
7. Whether the 1.6 GB non-KV overhead is measured or an assumption for later arithmetic.
