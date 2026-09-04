# Part B: KV Cache Sizing, Concurrency Limits & Empirical Verification

This document derives the theoretical KV cache sizing, memory allocation, and maximum sequence concurrency for **FLM-4B-Instruct** serving on an **NVIDIA L4 (24 GB)** GPU, followed by empirical validation against `bench_log.csv`.

---

## 1. Exact KV Cache Memory per Token

### Architectural Parameters (from `model_spec.md`)
- **Layers ($L$):** 28
- **Attention Heads ($H_Q$):** 24
- **KV Heads ($H_{KV}$ — Grouped-Query Attention):** 8
- **Head Dimension ($d_h$):** 128
- **KV Cache Precision:** fp16 (2 bytes per element)
- **Key & Value Tensors:** 2 (1 Key tensor, 1 Value tensor per layer)

### Analytical Formula
$$\text{Bytes per Token} = L \times H_{KV} \times d_h \times 2 \times \text{bytes\_per\_element}$$

### Step-by-Step Calculation
$$\text{Bytes per Token} = 28\text{ layers} \times 8\text{ KV heads} \times 128\text{ elements/head} \times 2\text{ (K + V)} \times 2\text{ bytes/element}$$
$$= 28 \times 8 = 224\text{ head-elements per token}$$
$$= 224 \times 128 = 28,672\text{ elements per token}$$
$$= 28,672 \times 2 = 57,344\text{ total K+V elements per layer-token}$$
$$= 57,344 \times 2\text{ bytes} = \mathbf{114,688\text{ bytes/token}}$$

In alternate units:
- **Exact:** $114,688\text{ bytes/token}$
- **KiB (binary):** $114,688 / 1,024 = 112.0\text{ KiB/token}$
- **MiB (binary):** $112.0 / 1,024 = 0.109375\text{ MiB/token}$
- **KB (decimal):** $114.688\text{ KB/token}$

---

## 2. Bytes per Full 4096-Token Sequence

Given `max_model_len` = 4096 tokens:
$$\text{Bytes per 4096-token Sequence} = 4,096\text{ tokens} \times 114,688\text{ bytes/token} = \mathbf{469,762,048\text{ bytes}}$$

In standard memory units:
- **Binary (GiB):** $\frac{469,762,048}{1,024^3} = \mathbf{0.4375\text{ GiB}} = \frac{7}{16}\text{ GiB} = 448.0\text{ MiB}$
- **Decimal (GB):** $\frac{469,762,048}{10^9} = \mathbf{0.469762048\text{ GB}} \approx 0.470\text{ GB}$

---

## 3. Usable KV Cache Memory Derivation

### Hardware & Allocation Constants (from `model_spec.md`)
- **Total GPU VRAM:** 24 GB (NVIDIA L4)
- **`gpu_memory_utilization`:** 0.92
- **Model Parameters:** 4.2 B ($4.2 \times 10^9$ parameters)
- **Weights Precision:** fp16 (2 bytes per parameter)
- **Runtime Non-KV Overhead (activations, CUDA graphs, workspace):** ~1.6 GB

### Step-by-Step Allocation Arithmetic

#### A. Total VRAM Allocated by Serving Engine
$$\text{Allocated VRAM} = 24.00\text{ GB} \times 0.92 = \mathbf{22.08\text{ GB}}\quad (22,080,000,000\text{ bytes})$$
*(In binary: $24.00\text{ GiB} \times 0.92 = 22.08\text{ GiB} = 23,708,219,474\text{ bytes}$)*

#### B. Static Model Weights Footprint
$$\text{Weight Memory} = 4.2 \times 10^9\text{ params} \times 2\text{ bytes/param} = \mathbf{8.40\text{ GB}}\quad (8,400,000,000\text{ bytes})$$
*(In binary: $8.40 \times 10^9 / 1024^3 = 7.8231\text{ GiB}$)*

#### C. Non-KV Runtime Overhead
$$\text{Overhead} = \mathbf{1.60\text{ GB}}\quad (1,600,000,000\text{ bytes})$$
*(In binary: $1.60 \times 10^9 / 1024^3 = 1.4901\text{ GiB}$)*

#### D. Usable KV Memory Pool
$$\text{Usable KV Memory} = \text{Allocated VRAM} - \text{Weight Memory} - \text{Runtime Overhead}$$
$$\text{Usable KV Memory} = 22.08\text{ GB} - 8.40\text{ GB} - 1.60\text{ GB} = \mathbf{12.08\text{ GB}}\quad (12,080,000,000\text{ bytes})$$

*(Under binary arithmetic: $22.08\text{ GiB} - 7.8231\text{ GiB} - 1.4901\text{ GiB} = 12.7668\text{ GiB} = 13,708,219,474\text{ bytes}$; or if all specs are binary: $22.08 - 8.40 - 1.60 = 12.08\text{ GiB}$)*

---

## 4. Maximum Concurrent 4096-Token Sequences

$$\text{Max Concurrency} = \frac{\text{Usable KV Cache Memory}}{\text{Bytes per 4096-Token Sequence}}$$

### Decimal Units Calculation:
$$\text{Max Concurrency} = \frac{12,080,000,000\text{ bytes}}{469,762,048\text{ bytes/seq}} \approx \mathbf{25.715\text{ sequences}}$$
Taking the **floor** (since fractional sequences cannot be served concurrently without preemption):
$$\lfloor 25.715 \rfloor = \mathbf{25\text{ full 4096-token sequences}}$$

### Binary Units Calculation ($12.08\text{ GiB}$):
$$\text{Max Concurrency} = \frac{12.08\text{ GiB}}{0.4375\text{ GiB/seq}} = \mathbf{27.611\text{ sequences}} \rightarrow \lfloor 27.611 \rfloor = \mathbf{27\text{ sequences}}$$

---

## 5. Sensitivity Analysis

We test the sensitivity of the maximum concurrency estimate against variations in runtime memory pressure:

| Scenario | Usable KV Memory | Max Concurrency (Exact) | Max Concurrency (Floor) | Delta vs Baseline (25) |
|---|:---:|:---:|:---:|:---:|
| **Baseline (util=0.92, overhead=1.6 GB)** | **12.08 GB** | **25.72** | **25** | **0** |
| **5% Lower Usable Memory** ($12.08 \times 0.95$) | 11.48 GB | 24.43 | **24** | -1 seq (-4.0%) |
| **Higher Overhead (2.5 GB vs 1.6 GB)** | 11.18 GB | 23.79 | **23** | -2 seq (-8.0%) |
| **Lower GPU Utilization (0.87 vs 0.92)** | 10.88 GB | 23.16 | **23** | -2 seq (-8.0%) |
| **Combined Worst Case (util=0.87, overhead=2.5 GB)** | 9.98 GB | 21.24 | **21** | -4 seq (-16.0%) |

**Conclusion:** The headline concurrency limit of **25 sequences** is highly stable; even severe memory pressure shifts the boundary by at most 1–4 sequences.

---

## 6. Empirical Validation Against `bench_log.csv`

We compare the theoretical prediction of **25 concurrent 4096-token sequences** against the benchmark log for 4096-token requests (`prompt_len=3584, gen_len=512`, sum = 4096 tokens):

### Actual Rows from `starterkit(1)/starter_kit/bench/bench_log.csv`

```csv
batch_size,prompt_len,gen_len,num_requests,wall_clock_s,reported_tok_s,ttft_ms_p50,itl_ms_p50,e2e_ms_p95,preempted_seqs,kv_cache_util
4,3584,512,4,28.98,565.4,483.2,51.33,32673.3,0,0.16
8,3584,512,8,36.3,902.6,519.0,62.26,39982.9,0,0.31
16,3584,512,16,49.97,1311.4,498.3,77.2,54602.1,0,0.62
24,3584,512,24,61.16,1607.4,500.5,96.07,69221.3,0,0.93
32,3584,512,32,94.71,1384.0,636.9,101.79,97465.7,7,0.97
48,3584,512,48,151.41,1298.5,955.4,100.0,105427.5,23,0.97
```

### Direct Empirical Comparison

1. **At `batch_size = 24`:**
   - Predicted KV Cache Util: $24 / 25.715 = \mathbf{0.9333}$ (93.3%)
   - Actual `kv_cache_util`: **`0.93`** (Exact match!)
   - Actual `preempted_seqs`: **`0`** (No preemption occurs, as $24 \le 25$)
   - Peak throughput achieved: **`1607.4 tok/s`**

2. **At `batch_size = 32` (Above Capacity):**
   - Predicted Preemptions: $32 - 25 = \mathbf{7\text{ sequences}}$
   - Actual `preempted_seqs`: **`7`** (Exact integer match!)
   - Actual `kv_cache_util`: **`0.97`** (Saturates at max block pool allocation)
   - Throughput collapses from $1607.4$ down to **`1384.0 tok/s`** (-13.9% degradation due to preemption recompute/swapping overhead).

3. **At `batch_size = 48`:**
   - Predicted Preemptions: $48 - 25 = \mathbf{23\text{ sequences}}$
   - Actual `preempted_seqs`: **`23`** (Exact integer match!)
   - Actual `kv_cache_util`: **`0.97`**
   - Throughput degrades further to **`1298.5 tok/s`** (-19.2%).

### Final Verdict on Prediction
- **Prediction Accuracy:** **EXACT MATCH.**
- The analytical formula $N_{\text{max}} = 25$ predicted the exact transition point where preemption begins (`batch_size=24` has 0 preemptions; `batch_size=32` has exactly $32 - 25 = 7$ preemptions; `batch_size=48` has exactly $48 - 25 = 23$ preemptions).
- The predicted KV cache utilization at batch size 24 ($\frac{24}{25.72} = 0.933$) matches the logged `0.93` to two decimal places.

---

## 7. Throughput Column Semantics: `reported_tok_s` vs True Generation `goodput_tok_s`

### What Does `reported_tok_s` Count?
An audit of `starterkit(1)/starter_kit/bench/bench_log.csv` against `model_spec.md` reveals that the harness's built-in `reported_tok_s` metric computes:
$$\text{reported\_tok\_s} = \frac{\text{Total Tokens Processed (Prompt Prefill + Generated Decode)}}{\text{Wall Clock Seconds}}$$
$$\text{reported\_tok\_s} = \frac{\text{num\_requests} \times (\text{prompt\_len} + \text{gen\_len})}{\text{wall\_clock\_s}}$$

### Proof from Benchmark Data:
1. **At `prompt_len=512, gen_len=256` (Batch 1):**
   - Total Tokens = $1 \times (512 + 256) = 768\text{ tokens}$
   - Wall Clock = $10.94\text{ s}$
   - $\frac{768}{10.94} = \mathbf{70.201\text{ tok/s}}$ $\rightarrow$ Logged `reported_tok_s`: **`70.2`** (Exact match).
2. **At `prompt_len=3584, gen_len=512` (Batch 24):**
   - Total Tokens = $24 \times (3584 + 512) = 24 \times 4096 = 98,304\text{ tokens}$
   - Wall Clock = $61.16\text{ s}$
   - $\frac{98,304}{61.16} = \mathbf{1607.325\text{ tok/s}}$ $\rightarrow$ Logged `reported_tok_s`: **`1607.4`** (Exact match).

### Why This Distorts Serving Capacity Analysis (Goodput Inflation)
- **Prefill vs Decode Asymmetry:** In LLM serving, prompt prefill is computed in parallel across thousands of tokens at high arithmetic intensity (compute-bound, achieving high FLOPS), whereas token generation (decode) runs sequentially token-by-token (memory-bandwidth-bound, achieving low token/s per stream).
- **Goodput Formula:** The client-visible generation rate (the speed at which usable output is delivered) is:
  $$\text{goodput\_tok\_s} = \frac{\text{num\_requests} \times \text{gen\_len}}{\text{wall\_clock\_s}}$$
- **Divergence by Prompt Length:**
  - **At `prompt_len=512, gen_len=256`:** Prompt tokens are $66.7\%$ of the total. `reported_tok_s` is exactly **$3.00\times$ higher** than goodput ($\frac{768}{256} = 3.0$). At batch 64, reported is $2,267.3\text{ tok/s}$ vs goodput of $755.7\text{ tok/s}$.
  - **At `prompt_len=3584, gen_len=512`:** Prompt tokens are $87.5\%$ of the total. `reported_tok_s` is exactly **$8.00\times$ higher** than goodput ($\frac{4096}{512} = 8.0$). At batch 24, reported is $1,607.4\text{ tok/s}$ vs goodput of only $200.9\text{ tok/s}$.
- **Root Cause of `REPORT_v0` Section 2 Error:** The author of `REPORT_v0` treated `reported_tok_s` as generation throughput, concluding that long-context throughput was comparable to short-context throughput ($1607.4$ vs $2267.3$), failing to recognize that $87.5\%$ of the long-context "throughput" was just prompt prefill, while actual generation rate plummeted from $755.7$ to $200.9\text{ tok/s}$ (a $73.4\%$ generation throughput collapse).

---

## 8. B2: Long-Context Scaling Anomaly & Mechanism Analysis

### 8.1 Empirical Tabulation of Long-Context Sweep (`prompt_len=3584, gen_len=512`)

| Batch Size | Requests | Wall Time (s) | Total Tokens | Generated Tokens | Reported Tok/s | Goodput Tok/s | Preempted Seqs | KV Cache Util | ITL p50 (ms) | E2E p95 (ms) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **4** | 4 | 28.98 | 16,384 | 2,048 | 565.4 | 70.7 | **0** | 0.16 | 51.33 | 32,673.3 |
| **8** | 8 | 36.30 | 32,768 | 4,096 | 902.6 | 112.8 | **0** | 0.31 | 62.26 | 39,982.9 |
| **16** | 16 | 49.97 | 65,536 | 8,192 | 1,311.4 | 163.9 | **0** | 0.62 | 77.20 | 54,602.1 |
| **24** | 24 | 61.16 | 98,304 | 12,288 | **1,607.4** | **200.9** | **0** | **0.93** | 96.07 | **69,221.3** |
| **32** | 32 | 94.71 | 131,072 | 16,384 | **1,384.0** | **173.0** | **7** | **0.97** | 101.79 | **97,465.7** |
| **48** | 48 | 151.41 | 196,608 | 24,576 | **1,298.5** | **162.3** | **23** | **0.97** | 100.00 | **105,427.5** |

### 8.2 Identification of the Throughput Knee / Break Point
- **Scaling Regime (Batches 4 to 24):** Throughput and goodput scale monotonically. Goodput increases from **$70.7\text{ tok/s}$** (batch 4) to peak at **$200.9\text{ tok/s}$** (batch 24) with **`0` preemptions** and `kv_cache_util` reaching **`0.93`**.
- **Collapse Regime (Batches 32 and 48):** The scaling pattern completely breaks between **batch 24 and batch 32**. 
  - At **batch 32**, reported throughput drops from $1607.4$ to **$1384.0\text{ tok/s}$** (-13.9%), goodput drops from $200.9$ to **$173.0\text{ tok/s}$**, `kv_cache_util` saturates at **`0.97`**, and **`preempted_seqs` jumps from 0 to 7**. E2E p95 latency spikes from $69.2\text{ s}$ to **$97.5\text{ s}$ (+40.8%)**.
  - At **batch 48**, reported throughput falls further to **$1298.5\text{ tok/s}$** (-19.2% from peak), goodput drops to **$162.3\text{ tok/s}$**, and **`preempted_seqs` reaches 23**. E2E latency degrades to **$105.4\text{ s}$ (+52.3%)**.

### 8.3 Evaluation of Alternative Explanations

| Alternative Explanation | Expected Physical Signature | Available Evidence in Log | Verdict |
|---|---|---|---|
| **A. Compute Saturation (FLOPS bound)** | Throughput should plateau asymptotically to peak GPU TFLOPS, not decrease by ~20%. Decode ITL would scale linearly with batch size. | ITL increases moderately ($51.3\text{ ms} \rightarrow 96.1\text{ ms} \rightarrow 101.8\text{ ms}$), but total wall-clock time surges disproportionately ($61.2\text{ s} \rightarrow 94.7\text{ s}$, +54.9%) due to discarded/recomputed tokens. | **RULED OUT** (Compute limits cause plateaus, not throughput collapse). |
| **B. Memory Bandwidth Saturation** | Generation throughput reaches memory roofline ($\frac{\text{Memory Bandwidth}}{\text{Model Weight Bytes}}$) and flattens out. | At batch 24, decode memory bandwidth is well-utilized. The drop from 24 to 32 occurs simultaneously with block allocation saturation (`0.97`) and non-zero preemptions. | **RULED OUT** as cause of drop (Bandwidth saturation limits scaling, but does not cause negative throughput derivatives). |
| **C. Scheduler Overhead / CPU Bottleneck** | TTFT and ITL would show massive overhead spikes even before memory pool exhaustion. | TTFT stays relatively stable ($483\text{ ms} \rightarrow 500\text{ ms} \rightarrow 636\text{ ms}$), showing the scheduler is not CPU-bound until requests are queued behind preemption recomputation. | **RULED OUT** as primary driver. |
| **D. Pure Measurement Artifact** | Inconsistent wall-clock measurements or random variance across runs. | The correlation between batch size, `preempted_seqs` ($0 \rightarrow 7 \rightarrow 23$), `kv_cache_util` ($0.93 \rightarrow 0.97$), and wall-clock elongation is strictly deterministic and matches our theoretical $N_{\text{max}} = 25$ derivation to the integer. | **RULED OUT**. |
| **E. KV Cache Exhaustion & Preemption Thrashing** | When batch size exceeds available KV cache capacity ($N_{\text{max}} = 25$), the engine must evict active sequences to CPU or abort and recompute their prompts from scratch, wasting compute and GPU time. | `preempted_seqs` is exactly 0 up to batch 24, exactly 7 at batch 32 ($32 - 25 = 7$), and exactly 23 at batch 48 ($48 - 25 = 23$). | **CONFIRMED (Causal Driver)**. |

### 8.4 Mechanism Conclusion & Concrete Deployment Recommendation
- **Confidence Level:** **HIGH (Definitive)**.
- **Root Mechanism:** The throughput collapse at batch $> 24$ is caused by **KV Cache Memory Pool Exhaustion**, triggering preemption thrashing (sequence recomputation cycles) in the serving scheduler.
- **Proposed Production Config Change:**
  - Set the serving engine concurrency ceiling to **`max_num_seqs = 24`** (or `max_num_batched_tokens = 98,304`).
- **Conservative Quantitative Effect (derived directly from measured rows):**
  - Capping concurrency at **batch 24** guarantees **`200.9 tok/s` goodput**, recovering **`+23.8%` generation goodput** relative to unconstrained batch-48 execution ($200.9 / 162.3 = 1.2378$).
  - Reduces p95 request latency from **$105.4\text{ s}$ down to $69.2\text{ s}$ (a $34.3\%$ latency reduction)**.
  - Completely eliminates preemption overhead ($23 \rightarrow 0$ preempted sequences).

---

## 9. B3: Section 2 Correction & Dual Independent Goodput Derivations

### 9.1 The Misread Column in `REPORT_v0`
In `REPORT_v0.md` Section 2, the original author cited:
1. *"1,311 tokens/sec throughput at batch size 16"*
2. *"Projected throughput at batch 48 $\approx$ 3,200 tokens/sec"*

**What was misread:** Both statements misread **`reported_tok_s`** as generation throughput.
- At batch 16, `reported_tok_s` ($1,311.4\text{ tok/s}$) counts $65,536$ total tokens ($57,344$ prompt prefill tokens + $8,192$ generated tokens). Actual generation goodput was only **$163.9\text{ tok/s}$** (an **8.0× overstatement**).
- The linear extrapolation to $3,200\text{ tok/s}$ at batch 48 ignored the KV cache ceiling ($N_{\text{max}} = 25$). Actual reported throughput at batch 48 was **$1,298.5\text{ tok/s}$** (and goodput was **$162.3\text{ tok/s}$**), which is **$59.4\%$ lower** than the fictional 3,200 tok/s projection.

### 9.2 Honest Goodput Derivation for Peak Long-Prompt Run (Batch 24, `prompt_len=3584, gen_len=512`)

We derive the honest generation goodput using **two independent methods**:

#### Method 1: Direct Token-Count & Wall-Clock Timing Arithmetic
$$\text{Goodput}_1 = \frac{\text{num\_requests} \times \text{gen\_len}}{\text{wall\_clock\_s}}$$
$$\text{Goodput}_1 = \frac{24 \times 512\text{ tokens}}{61.16\text{ s}} = \frac{12,288\text{ tokens}}{61.16\text{ s}} = \mathbf{200.916\text{ tok/s}}$$

#### Method 2: Reported Throughput Adjusted by Generation Fraction
$$\text{Generation Fraction} = \frac{\text{gen\_len}}{\text{prompt\_len} + \text{gen\_len}} = \frac{512}{3584 + 512} = \frac{512}{4096} = \frac{1}{8} = 0.125$$
$$\text{Goodput}_2 = \text{reported\_tok\_s} \times \text{Generation Fraction} = 1607.4\text{ tok/s} \times 0.125 = \mathbf{200.925\text{ tok/s}}$$

#### Cross-Check & Tolerance:
$$\Delta = |200.916 - 200.925| = 0.009\text{ tok/s}\quad (\mathbf{0.0045\%\text{ relative difference}})$$
Both derivations agree with near-zero error ($< 0.01\%$).

---

### 9.3 Corrected `REPORT_v0` Section 2 Prose (Report-Ready Replacement)

> ### Corrected Section 2: Long-Context Serving Performance & Concurrency Limits
>
> Benchmark evaluation of FLM-4B-Instruct on an NVIDIA L4 GPU reveals two critical serving realities for long-context workloads (3,584 prompt / 512 generation tokens):
>
> 1. **Prefill vs Generation Throughput Distinction:** The benchmark harness's `reported_tok_s` metric aggregates both prompt prefill and token generation. For long-prompt workloads, prompt tokens constitute $87.5\%$ of processed volume. While reported throughput reaches $1,607.4\text{ tok/s}$ at batch size 24, the true client-visible generation goodput is **$200.9\text{ tok/s}$** ($12,288$ generated tokens in $61.16\text{ s}$).
>
> 2. **KV Cache Saturation Knee at Concurrency = 24:** Based on an available KV cache pool of $12.08\text{ GB}$, theoretical maximum concurrency for full 4,096-token sequences is exactly $25\text{ streams}$ ($448.0\text{ MiB}$ per sequence). Scaling concurrency beyond 24 triggers severe preemption thrashing. At batch size 32, 7 sequences are preempted, causing goodput to collapse by $-13.9\%$ ($173.0\text{ tok/s}$). At batch size 48, 23 sequences are preempted, degrading goodput to **$162.3\text{ tok/s}$** ($-19.2\%$ from peak) while inflating p95 latency to $105.4\text{ seconds}$.
>
> **Operational Directive:** To maximize serving efficiency, production schedulers must enforce a concurrency limit of **`max_num_seqs = 24`** for 4k-context workloads, securing peak goodput of $200.9\text{ tok/s}$ while avoiding preemption degradation.

---

## 10. B4: Production Serving-Stack Metric for Preemption Verification

To continuously confirm the KV cache preemption mechanism in production without relying on offline log auditing, infrastructure engineers should monitor the standard vLLM / TGI serving metric:

$$\mathbf{\text{vllm:num\_preemptions\_total}}\quad (\text{Counter, Prometheus})$$
alongside **`vllm:gpu_cache_usage_sys`** (Gauge).

### Expected Operational Patterns:
- **Healthy Operation (Concurrency $\le 24$):** `vllm:num_preemptions_total` must remain strictly **`0`**, while `gpu_cache_usage_sys` operates between **$0.80$ and $0.93$**. Under this regime, inter-token decode latency remains smooth ($\text{ITL} \le 96\text{ ms}$).
- **Over-Saturation / Preemption Failure Mode (Concurrency $\ge 25$):** `gpu_cache_usage_sys` saturates at $\ge 0.97$, and `vllm:num_preemptions_total` exhibits a positive derivative ($\frac{d}{dt} > 0$). Simultaneously, request p95 latency spikes by $> 40\%$ and effective generation goodput drops. Triggering an automated queue backpressure or autoscaling rule on `vllm:num_preemptions_total > 0` directly prevents SLA degradation.
