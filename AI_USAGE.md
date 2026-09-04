# AI Usage & Methodological Disclosure

**Author:** Sai Krishnaa  
**Project:** AI Team Evaluation Audit & Serving Optimization  
**Date:** 2026-09-04  

---

## Tools Used

- **AI Development Environment:** Google Antigravity (Advanced Agentic AI Coding Assistant).
- **Execution Engine:** Local Python 3.10.5 execution runtime with pinned packages (`tiktoken==0.14.0`, `transformers==5.16.1`, `tokenizers==0.23.1`, `pandas==2.3.3`, `numpy==2.2.6`, `regex==2026.7.19`, `unicodedata2==17.0.1`).
- **Role & Workflow:** Google Antigravity was utilized as an autonomous, rigorous pair-programming research assistant. The human engineer (Sai Krishnaa) provided domain direction, problem framing, architectural constraints, hypothesis vetting, and final editorial judgment, while Antigravity assisted in script scaffolding, algebraic verification, parallel data extraction, and benchmark matrix generation.

---

## Where AI Accelerated Work

1. **Synthetic Isolation & Bug Experiment Scaffolding (Phase 3):**
   - Antigravity rapidly wrote the 5 isolated experiment scripts in `partA/scripts/exp_h1_whitespace.py` through `exp_h5_charcount.py`, generating both hand-crafted synthetic edge cases (e.g. multi-space strings, capitalized English acronyms) and real-corpus test harnesses.
2. **Parallel Corpus Acquisition & Data Wrangling (Phase 5):**
   - Handled the direct stream downloading and decompression of the 25.5 MB Meta FLORES-200 tarball (`partA/scripts/build_corpus.py`), extracting 6 parallel languages (6,072 sentences total), building aligned JSONL datasets, and executing a comprehensive 10-point Unicode quality audit in seconds.
3. **Cross-Language Matrix Computation (Phase 6):**
   - Executed 12,144 tokenizations across 6 languages $\times$ 2 tokenizers (GPT-2 BPE and MuRIL WordPiece) across 4 structural denominators (whitespace words, grapheme clusters, UTF-8 bytes, parallel sentences), producing structured CSV summaries and distribution percentiles (p50, p90).
4. **Algebraic Consistency Checks & LaTeX Formatting (Phases 8 & 9):**
   - Accelerated the formatting of mathematical step-by-step proofs for KV-cache memory sizing ($N_{\text{max}} = 25$) and goodput divergence in `partB/calculations.md`.

---

## Where AI Was Used for Brainstorming

1. **Hypothesis Generation & Classification (Phase 2):**
   - Antigravity was used to enumerate potential failure modes in `starterkit(1)/starter_kit/fertility.py` and `REPORT_v0.md`, creating the initial 10-hypothesis registry (`partA/experiments/02_hypothesis_registry.md`) spanning implementation bugs (H1, H2), preprocessing asymmetries (H3), Unicode semantics (H4, H5), and conceptual misinterpretations (H6, H7, H8, H9, H10).
2. **Alternative Explanations for Serving Collapse (Phase 10):**
   - Brainstormed candidate engineering causes for the long-context batch-48 throughput drop, listing compute FLOPS saturation, memory bandwidth limits, scheduler queue overhead, and measurement artifacts before systematically ruling them out using empirical signatures in `bench_log.csv`.
3. **Constraint-Driven Strategy Options (Phase 11):**
   - Explored trade-offs across Supervised Fine-Tuning (SFT / LoRA), Dedicated Inference Rewriters, and In-Context Prompt Engineering under the strict 1× A100 / 1 reviewer / 3-week timeline constraints.

---

## Where AI Was Wrong

1. **Phase 3 — The NFC Normalization Mutation Hypothesis (H4):**
   - *AI Initial Claim:* Antigravity hypothesized that calling `unicodedata.normalize("NFC", line)` in `fertility.py` was actively altering Devanagari text on the sample corpus, merging combining characters and skewing token counts.
   - *Experimental Reality:* Running `partA/scripts/exp_h4_nfc.py` revealed that exactly **0 out of 20 sample lines changed** (all lines were already NFC canonical). The hypothesis that NFC was actively distorting the baseline numbers on this sample was **rejected** by experiment and classified as `harmless-but-suspicious` in `partA/results/final_verdicts.md`.
2. **Phase 5 — NFC Decomposition Direction in FLORES-200 Hindi:**
   - *AI Initial Assumption:* Antigravity initially assumed that NFC normalization always shortens or maintains string length by precomposing characters.
   - *Experimental Reality:* When auditing `hin_Deva.txt`, Antigravity discovered that 93 lines became *longer* under NFC (e.g. 143 $\rightarrow$ 144 code points). Deep investigation in `partA/scripts/_verify_corpus.py` revealed that Devanagari precomposed nukta letters (`U+0958`–`U+095F`, such as ZA `U+095B`) are canonically decomposed into base + nukta (`U+091C + U+093C`) under NFC, correcting the initial misconception.
3. **Phase 9 — Initial Interpretation of `reported_tok_s`:**
   - *AI Initial Assumption:* Antigravity initially treated `reported_tok_s` as potentially reflecting generation decode rate with slight measurement overhead.
   - *Experimental Reality:* Algebraic cross-checks against `wall_clock_s` and total token counts proved that `reported_tok_s` was strictly counting **total tokens (prompt prefill + generated decode)**, which artificially inflated reported throughput by **8.0×** on long prompts (where prompt tokens represented $87.5\%$ of the load).

---

## What Was Independently Verified

Every technical claim in this repository was subjected to multi-step validation:

1. **Dual Independent Mathematical Derivations (Phases 9 & 10):**
   - Long-context generation goodput at batch 24 was derived via two mathematically independent paths:
     - *Method 1 (Direct Count / Time):* $\frac{24 \times 512}{61.16\text{ s}} = \mathbf{200.916\text{ tok/s}}$
     - *Method 2 (Ratio-Adjusted Reported Rate):* $1607.4 \times \frac{512}{4096} = \mathbf{200.925\text{ tok/s}}$
     - Confirmed agreement within **0.0045% error** in `partB/calculations.md` Section 9.
2. **First-Principles KV Cache Memory & Preemption Validation (Phase 8):**
   - The theoretical limit $N_{\text{max}} = 25$ derived purely from `model_spec.md` ($12.08\text{ GB} / 469.76\text{ MB}$) was verified against the empirical benchmark log, matching the exact integer preemption counts ($32 - 25 = 7$ preemptions at batch 32; $48 - 25 = 23$ preemptions at batch 48) and block utilization ($24 / 25.72 = 0.933 \approx 0.93$).
3. **Full Baseline Reproduction (Phase 1):**
   - Unmodified reproduction of `fertility.py` was executed directly in a clean virtual environment, logging stdout to `artifacts/raw/phase1_baseline_run.txt` and verifying that the original table values (1.27 / 7.45 / 5.89×) matched verbatim.
4. **Linguistic Grapheme vs. Code-Point Counting (Phases 3 & 6):**
   - Extended grapheme cluster segmentation was verified using Unicode Standard Annex #29 (`regex` `\X`), ensuring conjunct aksharas (e.g. `कि`, `म्न`, `हैं`) were counted as single visual units rather than multi-scalar code points.

---

## What I Do Not Fully Rely On AI For

1. **Strategic Architectural Decisions (Part C Memo):**
   - Deciding to **reject Supervised Fine-Tuning (SFT)** in favor of In-Context Prompt Engineering was a human engineering decision driven by risk management: with human review available for only 2 of the 6 target languages (Hindi and Kannada), fine-tuning shared weights would create an unmonitored regression risk across 67% of the user base (Tamil, Telugu, Bengali, Marathi).
2. **Serving Metric Selection (Part A Recommendation):**
   - Choosing **Tokens per Parallel Semantic Task / Sentence** as the primary serving metric (and explicitly rejecting `tok/word`) required human domain understanding of agglutinative morphology (e.g., recognizing that Malayalam's higher `tok/word` of 2.19 reflects fewer, denser words per sentence rather than poor tokenizer performance).
3. **Governance Thresholds & Operational Kill Criteria:**
   - Setting the **Day 8 Kill Criterion** (abort prompt tuning if casual rating $< 70\%$ or meaning preservation $< 90\%$) and the production P2 alert threshold ($\text{p90}[\text{tok/byte}] \ge 0.35$) required human calibration to balance business agility with customer SLA guarantees.
4. **Final Deliverable Authorship & Attribution:**
   - Reviewing, auditing, and signing off on all executive memos (`partA/memo.md` and `partC/memo.md`) to guarantee that every single cited number is backed by an auditable artifact on disk.
