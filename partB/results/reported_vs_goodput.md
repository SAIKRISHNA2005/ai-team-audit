# Throughput Audit: Reported Throughput vs True Generation Goodput

## Overview

This audit compares the benchmark harness's `reported_tok_s` against the true generation **goodput** ($	ext{Goodput} = rac{	ext{Generated Tokens}}{	ext{Wall Clock Time}}$).

### Key Finding: The Prefill Token Counting Confound
- `reported_tok_s` counts **ALL tokens** (prompt prefill + generated decode tokens) divided by wall-clock time:
  $$\text{reported\_tok\_s} = \frac{\text{num\_requests} \times (\text{prompt\_len} + \text{gen\_len})}{\text{wall\_clock\_s}}$$
- Because prompt prefill is computed in parallel matrix multiplications across all prompt tokens at high compute efficiency, counting prompt tokens inflates reported throughput by **3.0× at prompt_len=512** and by **8.0× at prompt_len=3584**.
- For serving capacity and client SLA planning, user-facing output rate is governed by **goodput**, not prefill-inflated throughput.

---
## Full Benchmark Log: Reported vs Goodput Comparison

| Batch | Prompt Len | Gen Len | Requests | Wall Clock (s) | Total Tokens | Generated Tokens | Reported Tok/s | Goodput Tok/s | Ratio (Rep/Good) | Inflation (%) | Preempted | KV Util |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 512 | 256 | 1 | 10.94 | 768 | 256 | **70.2** | **23.4** | 3.00× | +66.7% | 0 | 0.01 |
| 2 | 512 | 256 | 2 | 11.61 | 1,536 | 512 | **132.3** | **44.1** | 3.00× | +66.7% | 0 | 0.01 |
| 4 | 512 | 256 | 4 | 11.77 | 3,072 | 1,024 | **261.0** | **87.0** | 3.00× | +66.7% | 0 | 0.03 |
| 8 | 512 | 256 | 8 | 12.40 | 6,144 | 2,048 | **495.4** | **165.2** | 3.00× | +66.7% | 0 | 0.06 |
| 16 | 512 | 256 | 16 | 13.91 | 12,288 | 4,096 | **883.2** | **294.5** | 3.00× | +66.7% | 0 | 0.12 |
| 32 | 512 | 256 | 32 | 16.50 | 24,576 | 8,192 | **1489.6** | **496.5** | 3.00× | +66.7% | 0 | 0.23 |
| 64 | 512 | 256 | 64 | 21.68 | 49,152 | 16,384 | **2267.3** | **755.7** | 3.00× | +66.7% | 0 | 0.47 |
| 4 | 3584 | 512 | 4 | 28.98 | 16,384 | 2,048 | **565.4** | **70.7** | 8.00× | +87.5% | 0 | 0.16 |
| 8 | 3584 | 512 | 8 | 36.30 | 32,768 | 4,096 | **902.6** | **112.8** | 8.00× | +87.5% | 0 | 0.31 |
| 16 | 3584 | 512 | 16 | 49.97 | 65,536 | 8,192 | **1311.4** | **163.9** | 8.00× | +87.5% | 0 | 0.62 |
| 24 | 3584 | 512 | 24 | 61.16 | 98,304 | 12,288 | **1607.4** | **200.9** | 8.00× | +87.5% | 0 | 0.93 |
| 32 | 3584 | 512 | 32 | 94.71 | 131,072 | 16,384 | **1384.0** | **173.0** | 8.00× | +87.5% | 7 | 0.97 |
| 48 | 3584 | 512 | 48 | 151.41 | 196,608 | 24,576 | **1298.5** | **162.3** | 8.00× | +87.5% | 23 | 0.97 |

---
## Analytical Observations by Workload Regime

### 1. Short-Context Regime (`prompt_len=512, gen_len=256`, Seq Len = 768)
- **Prompt Fraction:** Prompt tokens make up $512 / 768 = 66.7\%$ of the workload; generated tokens are only $33.3\%$.
- **Throughput Divergence:** `reported_tok_s` is exactly **3.00× higher** than `goodput_tok_s` across all batch sizes.
- **Scaling:** At batch size 64, reported throughput reaches **2,267.3 tok/s**, but actual generation goodput is only **755.7 tok/s**.

### 2. Long-Context Regime (`prompt_len=3584, gen_len=512`, Seq Len = 4096)
- **Prompt Fraction:** Prompt tokens make up $3584 / 4096 = 87.5\%$ of the workload; generated tokens are only $12.5\%$.
- **Throughput Divergence:** `reported_tok_s` is exactly **8.00× higher** than `goodput_tok_s` across all batch sizes.
- **Peak Goodput:** Peak generation goodput occurs at **batch size 24** (**200.9 tok/s**), despite reported throughput showing **1,607.4 tok/s**.
- **Preemption Degradation:** Above batch 24, KV cache thrashing causes generation goodput to collapse from 200.9 tok/s down to **162.3 tok/s** at batch 48 (-19.2% loss).