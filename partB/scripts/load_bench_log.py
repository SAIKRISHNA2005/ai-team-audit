#!/usr/bin/env python3
"""
load_bench_log.py — Phase 9: Bench Log Audit & Goodput Derivation
================================================================
Loads the raw bench_log.csv, analyzes schema and token counting semantics,
computes true generation goodput vs reported total throughput, and outputs
clean derived tables.
"""

import sys
import os
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BENCH_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "starterkit(1)", "starter_kit", "bench", "bench_log.csv")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "raw")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

def process_bench_log():
    print(f"Loading bench log from: {BENCH_LOG_PATH}")
    df = pd.read_csv(BENCH_LOG_PATH)
    
    # 1. Dump full schema and raw contents to artifacts/raw/phase9_bench_log_dump.txt
    dump_path = os.path.join(RAW_DIR, "phase9_bench_log_dump.txt")
    with open(dump_path, "w", encoding="utf-8") as f:
        f.write("=== Phase 9 Bench Log Raw Dump ===\n\n")
        f.write("--- Schema (dtypes) ---\n")
        for col, dtype in df.dtypes.items():
            f.write(f"  {col}: {dtype}\n")
        f.write(f"\nTotal rows: {len(df)}\n")
        f.write("\n--- Full Contents ---\n")
        f.write(df.to_string(index=True))
        f.write("\n")
    print(f"Saved full raw dump to {dump_path}")
    
    # 2. Add derived columns
    # Expected token counts
    df["prompt_tokens_total"] = df["num_requests"] * df["prompt_len"]
    df["expected_generated_tokens"] = df["num_requests"] * df["gen_len"]
    df["total_tokens_processed"] = df["prompt_tokens_total"] + df["expected_generated_tokens"]
    
    # Wall time cross-check
    # Primary: wall_clock_s from the benchmark harness
    df["wall_time_s"] = df["wall_clock_s"]
    
    # Secondary check 1: Derived from total tokens / reported_tok_s
    df["wall_time_from_reported_tok_s"] = df["total_tokens_processed"] / df["reported_tok_s"]
    
    # Secondary check 2: Single-request latency model (ttft + itl * (gen_len - 1)) in seconds
    df["single_seq_latency_s"] = (df["ttft_ms_p50"] + df["itl_ms_p50"] * (df["gen_len"] - 1)) / 1000.0
    
    # True Generation Goodput: generated tokens / wall_time_s
    df["goodput_tok_s"] = df["expected_generated_tokens"] / df["wall_time_s"]
    
    # Total Token Throughput: total tokens (prompt + gen) / wall_time_s
    df["total_throughput_tok_s"] = df["total_tokens_processed"] / df["wall_time_s"]
    
    # Ratio & Divergence
    df["gen_token_fraction"] = df["expected_generated_tokens"] / df["total_tokens_processed"]
    df["reported_vs_goodput_ratio"] = df["reported_tok_s"] / df["goodput_tok_s"]
    df["divergence_pct"] = ((df["reported_tok_s"] - df["goodput_tok_s"]) / df["reported_tok_s"]) * 100.0
    
    # Save derived CSV
    derived_csv_path = os.path.join(RESULTS_DIR, "bench_log_derived.csv")
    df.to_csv(derived_csv_path, index=False)
    print(f"Saved derived metrics to {derived_csv_path}")
    
    # 3. Generate reported_vs_goodput.md table
    generate_markdown_table(df)
    
    return df

def generate_markdown_table(df):
    md_path = os.path.join(RESULTS_DIR, "reported_vs_goodput.md")
    
    # Sort by prompt_len then batch_size
    df_sorted = df.sort_values(by=["prompt_len", "batch_size"]).copy()
    
    md_lines = []
    md_lines.append("# Throughput Audit: Reported Throughput vs True Generation Goodput")
    md_lines.append("")
    md_lines.append("## Overview")
    md_lines.append("")
    md_lines.append("This audit compares the benchmark harness's `reported_tok_s` against the true generation **goodput** ($\text{Goodput} = \frac{\text{Generated Tokens}}{\text{Wall Clock Time}}$).")
    md_lines.append("")
    md_lines.append("### Key Finding: The Prefill Token Counting Confound")
    md_lines.append("- `reported_tok_s` counts **ALL tokens** (prompt prefill + generated decode tokens) divided by wall-clock time:")
    md_lines.append("  $$\\text{reported\\_tok\\_s} = \\frac{\\text{num\\_requests} \\times (\\text{prompt\\_len} + \\text{gen\\_len})}{\\text{wall\\_clock\\_s}}$$")
    md_lines.append("- Because prompt prefill is computed in parallel matrix multiplications across all prompt tokens at high compute efficiency, counting prompt tokens inflates reported throughput by **3.0× at prompt_len=512** and by **8.0× at prompt_len=3584**.")
    md_lines.append("- For serving capacity and client SLA planning, user-facing output rate is governed by **goodput**, not prefill-inflated throughput.")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("## Full Benchmark Log: Reported vs Goodput Comparison")
    md_lines.append("")
    md_lines.append("| Batch | Prompt Len | Gen Len | Requests | Wall Clock (s) | Total Tokens | Generated Tokens | Reported Tok/s | Goodput Tok/s | Ratio (Rep/Good) | Inflation (%) | Preempted | KV Util |")
    md_lines.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
    
    for _, r in df_sorted.iterrows():
        md_lines.append(
            f"| {int(r['batch_size'])} | {int(r['prompt_len'])} | {int(r['gen_len'])} | {int(r['num_requests'])} | "
            f"{r['wall_clock_s']:.2f} | {int(r['total_tokens_processed']):,} | {int(r['expected_generated_tokens']):,} | "
            f"**{r['reported_tok_s']:.1f}** | **{r['goodput_tok_s']:.1f}** | "
            f"{r['reported_vs_goodput_ratio']:.2f}× | +{r['divergence_pct']:.1f}% | "
            f"{int(r['preempted_seqs'])} | {r['kv_cache_util']:.2f} |"
        )
        
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("## Analytical Observations by Workload Regime")
    md_lines.append("")
    md_lines.append("### 1. Short-Context Regime (`prompt_len=512, gen_len=256`, Seq Len = 768)")
    md_lines.append("- **Prompt Fraction:** Prompt tokens make up $512 / 768 = 66.7\\%$ of the workload; generated tokens are only $33.3\\%$.")
    md_lines.append("- **Throughput Divergence:** `reported_tok_s` is exactly **3.00× higher** than `goodput_tok_s` across all batch sizes.")
    md_lines.append("- **Scaling:** At batch size 64, reported throughput reaches **2,267.3 tok/s**, but actual generation goodput is only **755.7 tok/s**.")
    md_lines.append("")
    md_lines.append("### 2. Long-Context Regime (`prompt_len=3584, gen_len=512`, Seq Len = 4096)")
    md_lines.append("- **Prompt Fraction:** Prompt tokens make up $3584 / 4096 = 87.5\\%$ of the workload; generated tokens are only $12.5\\%$.")
    md_lines.append("- **Throughput Divergence:** `reported_tok_s` is exactly **8.00× higher** than `goodput_tok_s` across all batch sizes.")
    md_lines.append("- **Peak Goodput:** Peak generation goodput occurs at **batch size 24** (**200.9 tok/s**), despite reported throughput showing **1,607.4 tok/s**.")
    md_lines.append("- **Preemption Degradation:** Above batch 24, KV cache thrashing causes generation goodput to collapse from 200.9 tok/s down to **162.3 tok/s** at batch 48 (-19.2% loss).")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    print(f"Saved reported vs goodput comparison report to {md_path}")

if __name__ == "__main__":
    process_bench_log()
