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
