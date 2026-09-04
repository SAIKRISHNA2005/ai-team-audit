# Final Verdicts on Hypothesis Registry (Phase 2 → Phase 7)

This document records the definitive, evidence-backed verdicts for all 10 hypotheses evaluated throughout the audit of `fertility.py` and `REPORT_v0.md`. Every verdict is supported by measured experimental data from Phase 3, Phase 4, and Phase 6.

---

## Verdict Summary Table

| ID | Hypothesis Focus | Final Verdict | Primary Evidence / Justification | Distortion on Original Headline Numbers |
|---|---|---|---|---|
| **H1** | `line.split(" ")` vs `line.split()` | **confirmed bug** | Consecutive whitespace inserts empty strings, artificially depressing `tok/word` by 50% on synthetic multi-space lines. | On the original sample corpus, fixing `line.split(" ")` increases English fertility from 1.265 to 1.278 (+1.04%) and Hindi from 7.450 to 7.502 (+0.70%), shifting the reported fertility ratio from 5.887× to 5.868× (-0.32%). |
| **H2** | Unweighted Mean of Ratios vs Corpus Aggregate (`sum/sum`) | **confirmed bug** | Unweighted per-line mean introduces Jensen's inequality bias and disproportionately weights short lines. | Corpus aggregate (`sum/sum`) reduces English fertility from 1.265 to 1.253 (-0.95%) and Hindi from 7.450 to 7.405 (-0.61%), shifting the true corpus ratio from 5.887× to 5.908× (+0.35%). |
| **H3** | Asymmetric `line.lower()` Preprocessing | **confirmed bug** | Lowercasing alters English tokenization while acting as a no-op on Devanagari, creating an asymmetric baseline. | Removing `line.lower()` raises English fertility from 1.265 to 1.302 (+2.84%) while leaving Hindi unchanged at 7.450 (0.00%), compressing the reported fertility ratio from 5.887× to 5.720× (-2.84%). |
| **H4** | NFC Normalization (`unicodedata.normalize("NFC")`) | **harmless-but-suspicious** | All 20 sample lines in the toy corpus were already in NFC format, resulting in 0 modified characters and identical outputs across NFC/NFD/raw. | Metric shift on original sample is exactly 0.00% (ENG: 1.265, HIN: 7.450). However, on FLORES-200, 93 Hindi lines contain non-NFC nukta characters (`U+0958`–`U+095F`) requiring NFC handling for BPE consistency. |
| **H5** | Code Point Counting (`chars = len(line)`) | **conceptual problem** | Python `len()` counts Unicode scalar values rather than visual grapheme clusters, failing to treat combining matras and viramas as single linguistic units. | Tok/char ratio is 6.99× under code points (1.579 vs 0.226) but expands to 10.86× under true grapheme clusters (2.614 vs 0.241), a +55.4% measurement divergence. |
| **H6** | Tok/Char "Confirms" Tok/Word Metric | **misleading interpretation** | Both metrics share the identical numerator (`len(tokens)`) and differ algebraically only by the language's average characters-per-word factor ($\approx 1.21$). | Claiming 6.99× "confirms" 5.89× is statistically invalid; the correlation is an algebraic identity ($\frac{\text{tok}}{\text{char}} = \frac{\text{tok}}{\text{word}} \times \frac{\text{words}}{\text{chars}}$), not an independent replication. |
| **H7** | "Property of the script, not the tokenizer" | **misleading interpretation** | Cross-tokenizer testing demonstrates that fertility is governed by tokenizer vocabulary coverage, not inherent script defects. | Switching from GPT-2 to Indic-trained MuRIL reduces Hindi sentence tokens from 198.1 to 31.6 (-84.0%) and flips the tok/word ratio so Hindi (1.247) matches English (1.259, 0.99×). |
| **H8** | Budgeting 6× Serving Cost based on GPT-2 | **conceptual problem** | Extrapolating production serving costs from an English-only BPE tokenizer ignores Indic-specialized architectures. | Under MuRIL on FLORES-200, Hindi serving token overhead is only 1.16× (31.6 vs 27.3 tok/sent), Tamil is 1.06× (28.9 tok/sent), and Kannada is 1.07× (29.1 tok/sent), completely invalidating the "6× serving budget" claim. |
| **H9** | Subjective "Worse/Better" Tokenization Label | **conceptual problem** | Higher tokens/word in agglutinative languages reflects grammatical compounding (morpheme density), not inferior model quality. | Malayalam requires 2.19 tok/word under MuRIL (+74% vs English) but consumes only 32.3 tokens per sentence (+18% vs English), proving `tok/word` is uncalibrated to serving cost or representation quality. |
| **H10** | Table Display vs Full Precision Discrepancy (5.89× vs 5.87×) | **harmless-but-suspicious** | Full-precision calculation `7.45012 / 1.26549 = 5.88715` correctly rounds to 5.89×, whereas dividing pre-rounded table cells (`7.45 / 1.27 = 5.866`) yields 5.87×. | Display-only rounding artifact; zero effect on underlying computation or code execution. |

---

## Detailed Verdict Justifications

### H1 — `line.split(" ")` vs `line.split()`
- **Verdict:** **confirmed bug**
- **Evidence:** Synthetic isolation testing confirmed that `line.split(" ")` treats consecutive spaces as empty string tokens. On `corpus_sample/eng_sample.txt` (line 7: `"books  in"`) and `hin_sample.txt` (line 10: `"किताबें  अलमारी"`), the bug inflated word counts by 1. Real-corpus testing demonstrated that fixing this bug shifts English fertility from 1.265 to 1.278 (+1.04%) and Hindi from 7.450 to 7.502 (+0.70%), shifting the fertility ratio from 5.887× to 5.868× (-0.32%).

### H2 — Unweighted Mean-of-Ratios vs Corpus-Level Aggregate (`sum/sum`)
- **Verdict:** **confirmed bug**
- **Evidence:** Computing $\frac{1}{N} \sum \frac{\text{tokens}_i}{\text{words}_i}$ gives equal weight to short sentences with extreme ratios. Aggregate calculation ($\frac{\sum \text{tokens}}{\sum \text{words}}$) on the sample corpus reduces English fertility from 1.265 to 1.253 (-0.95%) and Hindi fertility from 7.450 to 7.405 (-0.61%), altering the reported ratio from 5.887× to 5.908× (+0.35%).

### H3 — Asymmetric `line.lower()` Preprocessing
- **Verdict:** **confirmed bug**
- **Evidence:** `line.lower()` reduces English BPE token splits on capitalized proper nouns (e.g. `Bengaluru` $\rightarrow$ `bengaluru`, `NASA` $\rightarrow$ `nasa`), decreasing English fertility by 2.84% (from 1.302 to 1.265). Because Devanagari lacks case distinction, Hindi tokenization is 100% unaffected (7.450). This asymmetric preprocessing artificially inflated the reported Hindi/English gap from 5.720× to 5.887× (+2.92%).

### H4 — NFC Normalization (`unicodedata.normalize("NFC")`)
- **Verdict:** **harmless-but-suspicious**
- **Evidence:** On the 10-line sample corpora, all lines were already in NFC canonical form; running NFC vs NFD vs raw text resulted in exactly 0 character differences and 0.00% metric shift (1.265 ENG, 7.450 HIN). However, on FLORES-200, 93 Hindi lines contain non-NFC nukta characters (`U+0958`–`U+095F`), proving NFC normalization is necessary for robust production pipelines.

### H5 — Code Point Character Counting (`chars = len(line)`)
- **Verdict:** **conceptual problem**
- **Evidence:** Python `len()` counts code points, treating combining vowel signs (matras) and viramas as full characters. On the sample corpus, tok/code-point is 1.579 for Hindi vs 0.226 for English (6.99× ratio). When evaluated on linguistic grapheme clusters (aksharas), Hindi tok/grapheme expands to 2.614 vs 0.241 for English (10.86× ratio), demonstrating a 55.4% measurement discrepancy.

### H6 — Metric Independence ("tok/char confirms tok/word")
- **Verdict:** **misleading interpretation**
- **Evidence:** Algebraically, $\frac{\text{tok}}{\text{char}} = \frac{\text{tok}}{\text{word}} \times \frac{\text{words}}{\text{chars}}$. Since the sample corpus has 5.67 chars/word in English and 4.68 chars/word in Hindi, the tok/char ratio is mechanically $5.887 \times \frac{5.67}{4.68} \approx 7.13$. The two metrics share the exact same numerator (`len(tokens)`) and do not provide independent confirmation.

### H7 — Causal Claim ("Property of the script, not the tokenizer")
- **Verdict:** **misleading interpretation**
- **Evidence:** Phase 6 evaluation across 1,012 parallel sentences disproved this claim. Under GPT-2, Hindi uses 198.1 tokens/sentence; under MuRIL (trained on 17 Indic languages), Hindi uses 31.6 tokens/sentence (an 84.0% reduction). In tok/word, Hindi under MuRIL requires 1.247 vs English 1.259 (0.99×), proving that high fertility was an artifact of GPT-2's vocabulary, not Devanagari script.

### H8 — Budgeting 6× Serving Cost Based on GPT-2
- **Verdict:** **conceptual problem**
- **Evidence:** Budgeting serving capacity on GPT-2 BPE misallocates infrastructure. Under MuRIL on FLORES-200, the token overhead relative to English (27.3 tok/sent) is only +16% for Hindi (31.6 tok/sent), +6% for Tamil (28.9 tok/sent), +7% for Kannada (29.1 tok/sent), and +18% for Malayalam (32.3 tok/sent). Serving cost overhead for Indic workloads is under 20%, not 500% (6×).

### H9 — Subjective "Worse/Better" Labeling
- **Verdict:** **conceptual problem**
- **Evidence:** `fertility.py` printed "worse tokenization" for any ratio > 1.0. In agglutinative languages like Malayalam and Tamil, higher tokens/word reflects morphological synthesis (fewer words per sentence), not poor tokenization. Malayalam averages 9.5 words/sent vs English 21.6 words/sent; its sentence token count (32.3) is within 18% of English (27.3).

### H10 — Rounding Display Discrepancy (5.89× vs 5.87×)
- **Verdict:** **harmless-but-suspicious**
- **Evidence:** The script calculated `7.45012 / 1.26549 = 5.88715` and formatted it as `5.89×`. Dividing the displayed rounded values (`7.45 / 1.27 = 5.866`) gives `5.87×`. This is a cosmetic display formatting issue with zero impact on underlying computations.
