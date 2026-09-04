# AI Team Audit: Tokenization, Serving Capacity & Multilingual Adaptation

**Author:** Sai Krishnaa  
**Repository:** [https://github.com/SAIKRISHNA2005/ai-team-audit.git](https://github.com/SAIKRISHNA2005/ai-team-audit.git)

This repository provides an adversarial, first-principles technical audit and serving optimization analysis correcting an internal team's flawed preliminary report (`REPORT_v0.md`), scripts (`fertility.py`), and inference benchmarks (`bench_log.csv` for FLM-4B-Instruct on an NVIDIA L4 24GB GPU). By auditing tokenization on a 6,072-sentence parallel FLORES-200 corpus across Indo-Aryan and Dravidian languages, we disprove the reported 6× Hindi "fertility penalty," demonstrating that the disparity was an artifact of English-centric BPE tokenization (GPT-2) and morphological word-segmentation artifacts; under multilingual tokenization (MuRIL) and semantic sentence metrics, Indic serving overhead collapses to **+6% to +20% over English**. In serving infrastructure, we derive exact KV cache sizing ($114,688\text{ B/tok}$, $448.0\text{ MiB/seq}$, $12.08\text{ GB usable}$), proving that the throughput collapse beyond batch 24 is governed by an exact capacity knee ($N_{\text{max}} = 25\text{ sequences}$) triggering preemption thrashing, and correct an 8.0× prefill inflation in reported throughput via dual independent derivations ($200.9\text{ tok/s}$ true goodput). Finally, we deliver a constraint-driven strategy memo establishing in-context prompt engineering as the only viable path under strict hardware (1× A100, 2 weeks) and reviewer limitations (1 reviewer for Hindi/Kannada only).

---

## Deliverables Directory & Map

| Deliverable Key | Description | Primary Deliverable File | Supporting Script / Evidence |
|---|---|---|---|
| **A1** | **Corrected Tokenizer Matrix** | [`partA/results/corrected_metrics.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/results/corrected_metrics.md) | [`partA/scripts/corrected_analysis.py`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/scripts/corrected_analysis.py) |
| **A2** | **Linguistic & Morphological Audit** | [`partA/corpus/README.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/corpus/README.md) | [`partA/scripts/build_corpus.py`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/scripts/build_corpus.py) |
| **A3** | **Serving Metric & Denominator Recommendation** | [`partA/results/denominator_recommendation.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/results/denominator_recommendation.md) | [`partA/results/corrected_metrics.csv`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/results/corrected_metrics.csv) |
| **A4** | **Executive Serving Memo** | [`partA/memo.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/memo.md) | [`partA/results/final_verdicts.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/results/final_verdicts.md) |
| **B1** | **Theoretical KV Cache Sizing ($N_{\text{max}}=25$)** | [`partB/calculations.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/calculations.md#1-exact-kv-cache-memory-per-token) | Hand derivation against `model_spec.md` |
| **B2** | **Long-Context Anomaly & Mechanism Diagnosis** | [`partB/calculations.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/calculations.md#8-b2-long-context-scaling-anomaly--mechanism-analysis) | [`partB/scripts/load_bench_log.py`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/scripts/load_bench_log.py) |
| **B3** | **Section 2 Correction & Dual Goodput Derivations** | [`partB/calculations.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/calculations.md#9-b3-section-2-correction--dual-independent-goodput-derivations) | [`partB/results/reported_vs_goodput.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/results/reported_vs_goodput.md) |
| **B4** | **Production Serving Monitoring Metric** | [`partB/calculations.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/calculations.md#10-b4-production-serving-stack-metric-for-preemption-verification) | Prometheus metric specification |
| **Part C** | **Multilingual Adaptation Strategy Memo** | [`partC/memo.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partC/memo.md) | Decision matrix & capacity arithmetic |
| **Meta** | **Chronological Lab Notebook** | [`NOTEBOOK.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/NOTEBOOK.md) | Full research & dead-end audit log |
| **Meta** | **Honest AI Usage Disclosure** | [`AI_USAGE.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/AI_USAGE.md) | Human oversight & error documentation |
| **Meta** | **Final Quality Gate & Checklist** | [`artifacts/FINAL_AUDIT.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/artifacts/FINAL_AUDIT.md) | Adversarial audit verification table |

---

## Reproduction Guide (Exact Commands in Order)

### 1. Environment Setup
```bash
python -m venv .venv
# Activate virtual environment:
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Phase 1: Baseline Reproduction
Reproduce the original flawed numbers reported in `REPORT_v0.md`:
```bash
python starterkit(1)/starter_kit/tokenization/fertility.py
```

### 3. Phase 3: Bug Isolation Controlled Experiments
Isolate potential code-level bugs in whitespace handling, aggregation, casing, Unicode normalization, and character counting:
```bash
python partA/scripts/exp_h1_whitespace.py
python partA/scripts/exp_h2_aggregation.py
python partA/scripts/exp_h3_lowercase.py
python partA/scripts/exp_h4_nfc.py
python partA/scripts/exp_h5_charcount.py
```

### 4. Phase 5: Build & Verify 6-Language FLORES-200 Corpus
Construct the 1,012-sentence parallel evaluation dataset across English, Hindi, Tamil, Kannada, Malayalam, and Telugu:
```bash
python partA/scripts/build_corpus.py
python partA/scripts/_verify_corpus.py
```

### 5. Phase 6: Run Corrected Multilingual Tokenization Matrix
Execute the corrected evaluation across both GPT-2 and MuRIL tokenizers, generating summary tables and sentence-level distributions:
```bash
python partA/scripts/corrected_analysis.py
```

### 6. Phase 9 & 10: Process Benchmark Log & Audit Goodput
Parse the raw serving benchmark logs, derive true generation goodput, audit prefill inflation, and confirm the KV cache preemption knee:
```bash
python partB/scripts/load_bench_log.py
```

### 7. Phase 14: Verify Calculations Live
Re-derive KV cache sizing and dual goodput numbers live from Python one-liners:
```bash
# 1. KV cache memory per token (114,688 bytes/tok = 112 KiB/tok)
python -c "print(28 * 8 * 128 * 2 * 2, 'bytes/tok')"

# 2. Maximum concurrency (floor of 25 sequences)
python -c "usable = 24*0.92 - 8.4 - 1.6; seq = 4096 * 114688 / 1e9; print(f'Usable: {usable:.2f} GB, Concurrency: {usable/seq:.3f} -> floor {int(usable//seq)}')"

# 3. Dual goodput derivations at batch 24 (200.916 vs 200.925 tok/s)
python -c "g1 = (24 * 512) / 61.16; g2 = 1607.4 * (512 / 4096); print(f'M1: {g1:.3f} tok/s, M2: {g2:.3f} tok/s, Diff: {abs(g1-g2):.4f} tok/s')"
```

---

## Pristine Evidence Preservation Note
The extracted starter kit remains untouched under `starterkit(1)/` as a read-only byte-for-byte baseline. All new experiments, scripts, and results are segregated under `partA/`, `partB/`, `partC/`, and `artifacts/`.
