# Research & Audit Lab Notebook

This chronological lab notebook documents the step-by-step investigation, empirical experiments, derivations, and decisions across all 12 phases of the AI Team Evaluation Audit.

---

## Master Phase Index & Artifact Map

| Phase | Title | Focus / Question | Key Produced Artifacts |
|---|---|---|---|
| **Phase 0** | Workspace Scaffold & Environment | Clean environment capture and byte-for-byte evidence mirroring | [`artifacts/raw/env.txt`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/artifacts/raw/env.txt) |
| **Phase 1** | Evidence Inventory & Reproduction | Exact reproduction of `REPORT_v0.md` baseline numbers | [`partA/experiments/00_script_inventory.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/experiments/00_script_inventory.md), [`01_claims_table.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/experiments/01_claims_table.md), [`02_bench_inventory.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/experiments/02_bench_inventory.md) |
| **Phase 2** | Hypothesis Registry | Formulating 10 falsifiable hypotheses (H1–H10) across code and metrics | [`partA/experiments/02_hypothesis_registry.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/experiments/02_hypothesis_registry.md) |
| **Phase 3** | Controlled Bug Experiments | Synthetic isolation + real sample corpus runs for code bugs | [`partA/scripts/exp_h1_whitespace.py`..`exp_h5_charcount.py`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/scripts), [`partA/experiments/03_bug_experiments.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/experiments/03_bug_experiments.md) |
| **Phase 4** | Metric & Denominator Audit | Mathematical critique of `tok/word` and `tok/char` across scripts | [`partA/experiments/04_denominator_audit.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/experiments/04_denominator_audit.md) |
| **Phase 5** | Multilingual Evaluation Corpus (A1) | Building 6-language parallel FLORES-200 corpus (6,072 sentences) | [`partA/scripts/build_corpus.py`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/scripts/build_corpus.py), [`partA/corpus/`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/corpus), [`partA/corpus/README.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/corpus/README.md) |
| **Phase 6** | Corrected Cross-Language Comparison (A3) | GPT-2 vs MuRIL across 4 denominators with corpus aggregation | [`partA/scripts/corrected_analysis.py`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/scripts/corrected_analysis.py), [`partA/results/corrected_metrics.csv`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/results/corrected_metrics.csv), [`partA/results/denominator_recommendation.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/results/denominator_recommendation.md) |
| **Phase 7** | Part A Synthesis & Executive Memo (A2, A4) | Final hypothesis verdicts and executive routing memo | [`partA/results/final_verdicts.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/results/final_verdicts.md), [`partA/memo.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partA/memo.md) |
| **Phase 8** | KV Cache Sizing & Concurrency (B1) | First-principles KV memory derivation ($N_{\text{max}}=25$) | [`partB/calculations.md` (Sections 1–6)](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/calculations.md) |
| **Phase 9** | Bench Log Column Semantics & Goodput (B2) | Auditing prefill counting confound (`reported_tok_s` vs `goodput`) | [`partB/scripts/load_bench_log.py`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/scripts/load_bench_log.py), [`partB/results/bench_log_derived.csv`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/results/bench_log_derived.csv), [`partB/results/reported_vs_goodput.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/results/reported_vs_goodput.md) |
| **Phase 10** | Long-Context Anomaly & Section 2 Correction | Mechanism diagnosis, dual goodput derivations, production counters | [`partB/calculations.md` (Sections 7–10)](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partB/calculations.md) |
| **Phase 11** | Part C Decision Memo | Constraint-driven casualization strategy (Prompt Engineering) | [`partC/memo.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/partC/memo.md) |
| **Phase 12** | Consolidation Pass | Chronological synthesis, index map, and dead-end audit | [`NOTEBOOK.md`](file:///c:/Users/saikr/OneDrive/Desktop/flam-ai-task-starter-kit/NOTEBOOK.md) |

---

# Phase 0 — Workspace Scaffold & Operating Spec
**Date:** 2026-09-04T10:29:52Z  
**Question:** Can we establish a pristine, byte-for-byte read-only evidence base and lock experimental operating rules before touching code?

### Starter Kit Source Base
The provided starter kit is stored in `starterkit(1)/` as the **sole read-only evidence copy**.

Observed top-level structure and filenames (verbatim):
```
starterkit(1)/
├── __MACOSX/                          # macOS zip metadata
│   ├── ._starter_kit
│   └── starter_kit/
│       ├── ._.DS_Store
│       ├── ._bench
│       ├── ._corpus_sample
│       ├── ._fertility.py
│       ├── ._REPORT_v0.md
│       ├── bench/
│       │   ├── ._bench_log.csv
│       │   └── ._model_spec.md
│       └── corpus_sample/
│           ├── ._eng_sample.txt
│           └── ._hin_sample.txt
└── starter_kit/
    ├── .DS_Store
    ├── fertility.py
    ├── REPORT_v0.md
    ├── bench/
    │   ├── bench_log.csv
    │   └── model_spec.md
    └── corpus_sample/
        ├── eng_sample.txt
        └── hin_sample.txt
```

`starterkit(1)/` is **read-only evidence** preserved byte-for-byte across all audit phases. No modifications are made to `starterkit(1)/`; all instrumented copies, scripts, and evaluation runs live under `partA/`, `partB/`, `partC/`, and `artifacts/`.

### Fresh venv install
Command: `python -m venv %TEMP%\flam-phase0-venv` then `pip install -r requirements.txt` (Python 3.10.5).
- Pinned packages present: `tiktoken==0.14.0`, `transformers==5.16.1`, `sentencepiece==0.2.2`, `pandas==2.3.3`, `numpy==2.2.6`, `matplotlib==3.10.9`, `unicodedata2==17.0.1`, `tokenizers==0.23.1`.
- Hardware & Platform: Windows 10 x64, Intel Core i7 architecture, Python 3.10.5. Full environment captured in `artifacts/raw/env.txt`.

### Operating Rules (Locked for all phases)
1. **EVIDENCE** — No bug / misleading-metric / performance / “better config” claim without an experiment or derivation. Otherwise write: `Not yet experimentally verified`.
2. **NO FABRICATION** — No invented numbers, tokenizer output, timings, or file contents. Produce numbers by running code and showing raw output.
3. **TRACE** — Every numeric claim: command/code, input, raw output, formula/interpretation.
4. **STRUCTURE** — observation → hypothesis → alternative explanations → minimal isolated experiment → baseline vs modified → measured result (absolute + %) → direction/magnitude → verdict → limitations/confounders.
5. **PHASING** — Only the named phase. No pre-solving later phases.

---

# Phase 1 — Evidence Inventory & Baseline Reproduction
**Date:** 2026-09-04T11:15:00Z  
**Question:** Can we reproduce exactly what `REPORT_v0.md` reported, and can we inventory every claim and every bench column without judging bugs yet?

### What we did
- Read `starterkit(1)/starter_kit/fertility.py` line by line; wrote `partA/experiments/00_script_inventory.md`.
- Read `starterkit(1)/starter_kit/REPORT_v0.md`; wrote `partA/experiments/01_claims_table.md` covering every factual claim, number, and causal statement.
- Ran unmodified `fertility.py` with `gpt2` on both sample corpora (`corpus_sample/eng_sample.txt`, `hin_sample.txt`).
- Inventoried `model_spec.md` and `bench_log.csv` in `partA/experiments/02_bench_inventory.md`.

### Baseline Output (`artifacts/raw/phase1_baseline_run.txt`)
```
tokenizer: gpt2
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.27       0.226
hin                       7.45       1.579

hin is 5.89x the fertility of eng (worse tokenization)
```

### Initial Observations & Open Questions
- Exact reproduction confirmed (ENG 1.27 / 0.226, HIN 7.45 / 1.579, Ratio 5.89×).
- Printed-decimal divisions: $1.579 / 0.226 = 6.9867$; $7.45 / 1.27 = 5.8661$. Notice that 5.89× does not equal $7.45 / 1.27 = 5.87$, nor does tok/char ratio (6.99×) match 5.89×.
- Open question: Is 5.89× a display artifact or an arithmetic error? Are `tok/char` and `tok/word` independent?

---

# Phase 2 — Hypothesis Registry (No Verdicts Yet)
**Date:** 2026-09-04T12:30:00Z  
**Question:** Which falsifiable hypotheses about `fertility.py` and `REPORT_v0`’s methodology should be rigorously tested?

### What we did
- Authored `partA/experiments/02_hypothesis_registry.md` specifying 10 distinct hypotheses (H1 to H10):
  - H1: `line.split(" ")` empty string insertion on multi-space lines.
  - H2: Unweighted mean-of-ratios vs corpus ratio-of-totals.
  - H3: Asymmetric `line.lower()` preprocessing.
  - H4: `unicodedata.normalize("NFC", line)` normalization effect.
  - H5: Code point counting (`len(line)`) vs grapheme clusters.
  - H6: Claim that `tok/char` "confirms" `tok/word`.
  - H7: Causal claim: "property of the script, not the tokenizer".
  - H8: Extrapolating 6× serving cost from GPT-2 alone.
  - H9: Labeling higher tokens/word as "worse tokenization".
  - H10: Display vs full-precision rounding discrepancy.

---

# Phase 3 — Controlled Bug Experiments
**Date:** 2026-09-04T14:10:00Z  
**Question:** For each hypothesis in the registry (H1–H5), does an isolated synthetic test confirm the mechanism, and does running it on real sample corpora move the numbers?

### What we did
- Wrote 5 dedicated isolation scripts under `partA/scripts/exp_h1_whitespace.py` .. `exp_h5_charcount.py`.
- Ran both synthetic corner cases and before/after sample corpus runs. Raw outputs stored in `artifacts/raw/phase3_h1_whitespace.txt` .. `phase3_h5_charcount.txt`.
- Documented complete findings in `partA/experiments/03_bug_experiments.md`.

### Key Results
- **H1 (Whitespace Bug):** Confirmed. `line.split(" ")` inserted empty words on ENG line 7 and HIN line 10. Fixing shifts ENG 1.265 $\rightarrow$ 1.278 (+1.04%) and HIN 7.450 $\rightarrow$ 7.502 (+0.70%).
- **H2 (Aggregation Bug):** Confirmed. Unweighted mean overstates ENG by +0.95% (1.265 vs 1.253 aggregate) and HIN by +0.61% (7.450 vs 7.405).
- **H3 (Lowercase Asymmetry):** Confirmed. `line.lower()` stripped capitalization on English acronyms (e.g. `NASA`), lowering English tokens by -2.84% while acting as a 100% no-op on Hindi.
- **H4 (NFC Normalization):** **Harmless-but-Suspicious (Dead End on sample corpus).**
- **H5 (Character Counting Semantics):** Confirmed conceptual bug. Tok/char ratio is 6.99× under code points vs **10.86×** under visual grapheme clusters (+55.4% discrepancy).

### Belief Revision / Dead End: The "NFC Normalization Hypothesis"
- **Prior Hypothesis:** We hypothesized that calling `unicodedata.normalize("NFC", line)` was aggressively mutating Devanagari text, merging combining marks, and altering tokenization.
- **Experimental Reality:** Running NFC vs NFD vs Raw across all 20 lines in the sample corpus resulted in **0 modified characters** and **0.00% metric shift**. The sample files had already been saved in NFC form. While synthetic Latin tests showed NFD expands `é` into 3 tokens vs 1 token, on the toy sample corpus, the NFC call was a complete no-op.

---

# Phase 4 — Metric & Denominator Audit
**Date:** 2026-09-04T15:45:00Z  
**Question:** What is each candidate denominator holding constant across languages, and does `tok/char` provide independent validation of `tok/word`?

### What we did
- Authored `partA/experiments/04_denominator_audit.md` evaluating 5 denominators: whitespace words, code points, grapheme clusters, UTF-8 bytes, and parallel sentences.
- Proved algebraically that `tok/char` and `tok/word` are collinear:
  $$\frac{\text{tok}}{\text{char}} = \frac{\text{tok}}{\text{word}} \times \frac{\text{words}}{\text{chars}}$$
  Agreement between 5.89× and 6.99× is purely a mechanical consequence of average word length ($5.67 / 4.68 \approx 1.21$).
- Formulated the linguistic critique of `tok/word`: In synthetic/agglutinative scripts (Devanagari, Dravidian), words carry dense inflectional affixes and postpositions, making whitespace words an inherently biased denominator against Indic languages.

---

# Phase 5 — Real Multilingual Evaluation Corpus (A1)
**Date:** 2026-09-04T16:35:00Z  
**Question:** Can we build a high-quality, 6-language parallel evaluation corpus covering English, Hindi, and Dravidian languages with sentence alignment and rigorous quality checks?

### What we did
- Built `partA/scripts/build_corpus.py` to download FLORES-200 `devtest` directly from Meta CDN (`dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz`).
- Extracted 6 parallel languages: `eng_Latn`, `hin_Deva`, `kan_Knda`, `tam_Taml`, `tel_Telu`, `mal_Mlym` (1,012 sentences each, 6,072 sentences total).
- Saved per-language `.txt` files and `flores200_devtest.jsonl`.
- Documented quality findings, domain traits, and limitations in `partA/corpus/README.md`.

### Surprise & Discovery: Non-NFC Letters in FLORES Hindi
- **Finding:** While Phase 3 showed NFC was a no-op on the toy sample, FLORES-200 Hindi (`hin_Deva`) contained **93 lines with non-NFC precomposed nukta letters** (`U+0958`–`U+095F`, e.g. ZA `U+095B`, DDDHA `U+095C`, FA `U+095E`).
- Under standard NFC normalization, these precomposed characters decompose into base letter + nukta (e.g. `ZA` $\rightarrow$ `JA + NUKTA`), making the NFC string code point count *longer*. Retained as valid authentic orthography.
- Also verified 289 lines with Zero-Width Non-Joiner (`U+200C`) in Kannada used correctly for locative suffix separation.

---

# Phase 6 — Corrected Cross-Language Comparison (A3)
**Date:** 2026-09-04T17:25:00Z  
**Question:** When recomputed with corpus-level aggregation across multiple denominators and an Indic-trained tokenizer (MuRIL), does the English-vs-Indic fertility disparity persist?

### What we did
- Built `partA/scripts/corrected_analysis.py` comparing **GPT-2 BPE** (50k vocab) vs **MuRIL WordPiece** (197k vocab) across all 6 languages and 4 denominators.
- Applied corpus-level aggregation ($\frac{\sum \text{tokens}}{\sum \text{units}}$) and distributional reporting (p50, p90, std).
- Saved results to `partA/results/corrected_metrics.csv` and `partA/results/corrected_metrics.md`.
- Authored `partA/results/denominator_recommendation.md`.

### Key Results & Belief Revisions
1. **The "Hindi Fertility Penalty" is an Artifact of Tokenizer Choice:**
   - Under GPT-2: Hindi tok/word is 7.82 (6.33× English); sentence tokens = 198.1 (7.41× English).
   - Under MuRIL: Hindi tok/word **FLIPS to 1.25** (0.99× of English 1.26); sentence tokens = **31.6** (only 1.16× English, an **84.0% reduction**).
2. **Dravidian Tokenization Collapse Solved:**
   - Sentence token counts under MuRIL drop by **90.5% to 93.0%** (Tamil: 28.9 tok/sent; Kannada: 29.1; Malayalam: 32.3; Telugu: 32.8), achieving near-parity with English (27.3).
3. **Surprise: The Byte-Density Inversion:**
   - Under MuRIL, Indic languages are over 2× *more dense per byte* than English (0.069–0.095 tok/byte vs 0.209 for English), because Indic WordPiece subwords compress multiple 3-byte characters into a single token ID.

---

# Phase 7 — Part A Synthesis & Executive Memo (A2, A4)
**Date:** 2026-09-04T18:15:00Z  
**Question:** Can we synthesize all findings into locked hypothesis verdicts and author an executive serving memo?

### What we did
- Authored `partA/results/final_verdicts.md` locking in verdicts for H1–H10 with exact distortion numbers.
- Authored `partA/memo.md` (From: Sai Krishnaa) delivering corrected numbers, routing policy, translationese caveat, and the $\text{p90}[\text{tok/byte}]$ production monitoring metric.

---

# Phase 8 — KV Cache Sizing & Concurrency Derivation (B1)
**Date:** 2026-09-04T19:00:00Z  
**Question:** What is the exact theoretical KV cache memory footprint and maximum 4096-token sequence concurrency for FLM-4B-Instruct on an NVIDIA L4 GPU?

### What we did
- Derived exact per-token KV cache memory: $28 \times 8 \times 128 \times 2 \times 2 = 114,688\text{ bytes/token}$ ($112.0\text{ KiB/token}$).
- Derived 4096-token sequence footprint: $4096 \times 114,688 = 469,762,048\text{ bytes}$ ($0.4375\text{ GiB} = 448.0\text{ MiB}$).
- Derived usable KV pool: $24\text{ GB} \times 0.92 - (4.2\text{ B} \times 2\text{ B}) - 1.6\text{ GB} = 12.08\text{ GB}$.
- Derived max concurrency: $\lfloor \frac{12.08 \times 10^9}{469,762,048} \rfloor = \lfloor 25.715 \rfloor = \mathbf{25\text{ sequences (floor)}}$.
- Cross-checked against `bench_log.csv`: Predicted preemption knee after batch 24 matched logged data with 100% precision (batch 24 util = 0.93, preempted = 0; batch 32 preempted = 7; batch 48 preempted = 23).

---

# Phase 9 — Bench Log Column Semantics & Goodput Audit (B2 Ground Truth)
**Date:** 2026-09-04T19:45:00Z  
**Question:** What are the exact token counting semantics of `reported_tok_s` in `bench_log.csv`?

### What we did
- Built `partB/scripts/load_bench_log.py`, dumped raw schema to `artifacts/raw/phase9_bench_log_dump.txt`, and generated `partB/results/bench_log_derived.csv`.
- Discovered that `reported_tok_s = \frac{\text{total tokens (prompt + gen)}}{\text{wall\_clock\_s}}`.
- Proved that `reported_tok_s` was inflated by **3.0× on short prompts** (512 prompt) and by **8.0× on long prompts** (3584 prompt) because it counted prompt prefill tokens.
- Generated `partB/results/reported_vs_goodput.md`.

---

# Phase 10 — Long-Context Anomaly & Section 2 Correction (B2, B3, B4)
**Date:** 2026-09-04T20:30:00Z  
**Question:** What is the physical mechanism behind the batch-scaling collapse beyond batch 24, and how should Section 2 be corrected?

### What we did
- Diagnosed that scaling beyond batch 24 triggers KV cache exhaustion ($N_{\text{max}} = 25$), causing preemption recompute thrashing.
- Evaluated and ruled out compute saturation, bandwidth limits, scheduler overhead, and measurement artifacts in `partB/calculations.md` Section 8.
- Computed honest batch-24 goodput using two independent methods ($200.916\text{ tok/s}$ vs $200.925\text{ tok/s}$, agreeing within $0.0045\%$).
- Wrote corrected report-ready Section 2 prose and specified production Prometheus counter `vllm:num_preemptions_total`.

---

# Phase 11 — Part C Decision Memo: Multilingual Tone Strategy
**Date:** 2026-09-04T21:15:00Z  
**Question:** Under 1× A100 / 2 weeks, 1 reviewer for Hindi/Kannada only, 3-week deadline, and $0 API budget, what is the optimal tone adaptation strategy?

### What we did
- Internalized all 5 constraints and highlighted the critical mismatch (human review covers only 2 of 6 languages).
- Built an 8-dimension decision matrix in `partC/memo.md` (From: Sai Krishnaa).
- Selected **In-Context Prompt Engineering with Language-Isolated Few-Shot Exemplars**; rejected SFT due to unmonitored catastrophic weight drift on Tamil/Telugu/Bengali/Marathi.
- Formulated complete arithmetic: 450 total human reviews, 2.11 GPU-hours compute per sweep (<1% of budget), and +12 ms TTFT overhead.
- Defined success metrics ($\ge 80\%$ casual, $\ge 95\%$ meaning preservation), Day 8 kill criterion, and Day 1 experiment.

---

# Phase 12 — NOTEBOOK.md Consolidation Pass
**Date:** 2026-09-04T22:10:00Z  
**Question:** Can we consolidate all prior phase logs into a unified, chronological, defense-ready research record with full artifact traceability and explicit dead-end documentation?

### Consolidation Audit Summary
- Added top-level **Master Phase Index & Artifact Map**.
- Preserved all 4 major empirical dead ends and belief revisions (Phase 3 NFC sample no-op, Phase 5 FLORES precomposed nukta expansion, Phase 6 Byte-Density Inversion, Phase 9/10 Prefill Throughput Confound).
- Verified strict consistency across all deliverables in `partA/`, `partB/`, `partC/`, and `artifacts/raw/`.
- All investigations complete and locked.
