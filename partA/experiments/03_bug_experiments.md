# Phase 3 — Controlled Bug Experiments

**Date:** 2026-09-04  
**Raw output files:** `artifacts/raw/phase3_h*.txt`  
**Scripts:** `partA/scripts/exp_h1_whitespace.py` … `exp_h5_charcount.py`  
**Corpora:** `starterkit(1)/starter_kit/corpus_sample/eng_sample.txt` (10 lines), `hin_sample.txt` (10 lines)  
**Tokenizer:** `gpt2` via tiktoken 0.14.0  
**Python:** 3.10.5, `fertility.py` left untouched in `starterkit(1)/`

Each section: (A) synthetic isolation → (B) real-corpus impact → verdict.

---

## Experiment 1 — Whitespace splitting: `split(" ")` vs `split()` (H1)

**Script:** `exp_h1_whitespace.py`  
**Raw output:** `artifacts/raw/phase3_h1_whitespace.txt`

### Part A: Synthetic isolation

`split(" ")` inserts **empty strings** between consecutive spaces; `split()` collapses all whitespace.

| Case | `split(" ")` count | `split()` count | Empty strings |
|---|---|---|---|
| ENG single space | 5 | 5 | 0 |
| ENG double space | 8 | 7 | **1** |
| ENG triple space | 7 | 3 | **4** |
| ENG leading space | 3 | 2 | **1** |
| ENG trailing space | 3 | 2 | **1** |
| ENG leading+trailing | 4 | 2 | **2** |
| ENG tab | 1 | 2 | 0 (tab not split) |
| ENG newline embedded | 1 | 2 | 0 (newline not split) |
| HIN single space | 6 | 6 | 0 |
| HIN double space | 6 | 5 | **1** |
| HIN triple space | 7 | 3 | **4** |
| HIN double space (Devanagari) | 4 | 3 | **1** |

**Fertility distortion (mock: token_count = `len(split())` words, to isolate split effect alone):**

| Case | fertility `split(" ")` | fertility `split()` | delta | %change |
|---|---|---|---|---|
| single spaces only | 1.0000 | 1.0000 | 0.0000 | 0.00% |
| one double space | 0.8750 | 1.0000 | +0.1250 | **+14.29%** |
| two double spaces | 0.6667 | 1.0000 | +0.3333 | **+50.00%** |
| leading + trailing | 0.6000 | 1.0000 | +0.4000 | **+66.67%** |
| tab separated | 3.0000 | 1.0000 | −2.0000 | **−66.67%** |
| HIN double space | 0.7500 | 1.0000 | +0.2500 | **+33.33%** |

Note: tabs are _not_ split by `split(" ")`, so a tab-separated line produces a _single_ word and artificially high fertility (inverse of the double-space case).

### Part B: Real-corpus impact

Per-line empty-string audit:

```
[ENG line 7] empties=1  text='please keep the books  in the cupboard.'
[ENG] total empty strings across all lines: 1

[HIN line 10] empties=1  text='किताबें  अलमारी में रखी हैं।'
[HIN] total empty strings across all lines: 1
```

**Exact before/after fertility numbers:**

| Metric | BEFORE `split(" ")` | AFTER `split()` | Δ% |
|---|---|---|---|
| ENG fertility | 1.265206 | 1.283063 | **+1.411%** |
| HIN fertility | 7.448452 | 7.598452 | **+2.014%** |
| HIN/ENG ratio | 5.887148 | 5.922121 | **+0.594%** |
| ENG tok/char | 0.225636 | 0.225636 | 0.000% |
| HIN tok/char | 1.579108 | 1.579108 | 0.000% |

**At 2 d.p. (as reported by fertility.py):**

| | ENG | HIN | ratio |
|---|---|---|---|
| BEFORE `split(" ")` | 1.27 | 7.45 | 5.89× |
| AFTER `split()` | **1.28** | **7.60** | **5.92×** |

tok/char is unaffected because it uses `len(line)`, not `len(words)`.

> **VERDICT: confirmed bug.** `split(" ")` produces 1 empty string in each corpus (eng L7, hin L10), inflating the word denominator and biasing fertility DOWN by +1.4% for English and +2.0% for Hindi. The hin/eng ratio changes by +0.594% (5.887→5.922) — small at 6 significant figures, but the 2 d.p. printed values change (ENG 1.27→1.28, HIN 7.45→7.60, ratio 5.89→5.92), meaning even the REPORT_v0 table cells are wrong under the standard definition of word count.

---

## Experiment 2 — Per-line average vs corpus aggregate (H2)

**Script:** `exp_h2_aggregation.py`  
**Raw output:** `artifacts/raw/phase3_h2_aggregation.txt`

### Part A: Synthetic isolation

| Scenario | Line | words | tokens | ratio_i |
|---|---|---|---|---|
| S1 | 1-word line | 1 | 4 | 4.0000 |
| S1 | 100-word line | 100 | 110 | 1.1000 |
| S2 | 1-word line | 1 | 10 | 10.0000 |
| S2 | 1000-word line | 1000 | 1005 | 1.0050 |
| S3 | all same | 10 | 15 | 1.5000 (×3) |

| Scenario | mean-of-ratios | ratio-of-totals | delta | %change |
|---|---|---|---|---|
| S1 (1-word + 100-word) | 2.5500 | 1.1287 (114/101) | −1.4213 | **−55.74%** |
| S2 (1-word + 1000-word) | 5.5025 | 1.0140 (1015/1001) | −4.4885 | **−81.57%** |
| S3 (equal lines) | 1.500000 | 1.500000 | 0.000000 | **0.00%** |

The divergence is maximised when one very short line has anomalously high fertility — which dominates the unweighted mean but contributes almost nothing to the totals.

### Part B: Real-corpus impact

Per-line breakdown (using `split(" ")` to match fertility.py):

| Line | ENG words | ENG tokens | ENG ratio_i | HIN words | HIN tokens | HIN ratio_i |
|---|---|---|---|---|---|---|
| 1 | 8 | 12 | 1.5000 | 7 | 47 | 6.7143 |
| 2 | 7 | 9 | 1.2857 | 8 | 61 | 7.6250 |
| 3 | 12 | 13 | 1.0833 | 7 | 47 | 6.7143 |
| 4 | 7 | 8 | 1.1429 | 7 | 51 | 7.2857 |
| 5 | 6 | 7 | 1.1667 | 5 | 34 | 6.8000 |
| 6 | 8 | 11 | 1.3750 | 5 | 40 | 8.0000 |
| 7 | 8 | 10 | 1.2500 | 7 | 59 | 8.4286 |
| 8 | 6 | 9 | 1.5000 | 4 | 35 | 8.7500 |
| 9 | 6 | 7 | 1.1667 | 6 | 40 | 6.6667 |
| 10 | 11 | 13 | 1.1818 | 6 | 45 | 7.5000 |

**Totals:** ENG tokens=99, words=79, chars=448 | HIN tokens=459, words=62, chars=290

| Metric | mean-of-ratios | ratio-of-totals | delta | Δ% |
|---|---|---|---|---|
| ENG fertility | 1.265206 | 1.253165 | −0.012041 | **−0.952%** |
| HIN fertility | 7.448452 | 7.403226 | −0.045227 | **−0.607%** |
| HIN/ENG ratio | 5.887148 | 5.907625 | +0.020477 | **+0.348%** |
| ENG tok/char | 0.225636 | 0.220982 | −0.004654 | **−2.063%** |
| HIN tok/char | 1.579108 | 1.582759 | +0.003650 | **+0.231%** |

**At 2 d.p.:**

| | ENG fertility | HIN fertility | ratio |
|---|---|---|---|
| mean-of-ratios | 1.27 | 7.45 | 5.89× |
| ratio-of-totals | **1.25** | **7.40** | **5.91×** |

> **VERDICT: aggregation bug / conceptual problem.** The two aggregation methods diverge on this corpus: ENG shifts from 1.27→1.25, HIN from 7.45→7.40 at 2 d.p. (−0.95% and −0.61% respectively). The hin/eng ratio shifts by +0.35% in the opposite direction. The delta is not catastrophic at this sample size (lines are fairly even in length), but it is real — the mean-of-ratios method gives _more weight_ to short lines, which biases the result relative to the corpus-level total-tokens/total-words figure that "fertility of the corpus" most naturally refers to. The direction of bias is non-trivially language-dependent on this data.

---

## Experiment 3 — Lowercasing (H3)

**Script:** `exp_h3_lowercase.py`  
**Raw output:** `artifacts/raw/phase3_h3_lowercase.txt`

### Part A: Synthetic isolation

| Case | tokens_orig | tokens_lower | delta | %change |
|---|---|---|---|---|
| ENG all upper ("NASA AND ISRO ANNOUNCED") | 8 | 6 | −2 | **−25.00%** |
| ENG mixed case ("Bengaluru International Airport") | 6 | 6 | 0 | 0.00% |
| ENG proper noun ("NASA") | 1 | 2 | **+1** | **+100.00%** |
| ENG acronym ("ISRO") | 2 | 2 | 0 | 0.00% |
| ENG normal lower ("hello world") | 2 | 2 | 0 | 0.00% |
| ENG sentence-start cap ("The train…") | 6 | 6 | 0 | 0.00% |
| HIN devanagari (pure) | 37 | 37 | 0 | 0.00% |
| HIN with digit | 18 | 18 | 0 | 0.00% |
| HIN with latin word ("NASA और ISRO") | 7 | 8 | **+1** | **+14.29%** |

Token-by-token detail:
```
'NASA'  -> [29998]      (1 token)
'nasa'  -> [77, 15462]  (2 tokens)  ← lowercasing ADDS a token

'ISRO'  -> [1797, 13252]  (2 tokens)
'isro'  -> [271, 305]     (2 tokens)  ← no change

'Bengaluru' -> [33, 1516, 282, 14717]  (4 tokens)
'bengaluru' -> [65, 1516, 282, 14717]  (4 tokens)  ← no change
```

### Part B: Real-corpus impact

Per-line token delta (lowercased vs original):

| ENG line | tok_lower | tok_orig | delta |
|---|---|---|---|
| 1 (Bengaluru…) | 12 | 12 | 0 |
| 2 (Quarterly Review…) | 9 | 8 | **+1** |
| 3 | 13 | 13 | 0 |
| 4 | 8 | 8 | 0 |
| 5 | 7 | 7 | 0 |
| 6 (NASA and ISRO…) | 11 | 10 | **+1** |
| 7–9 | 10, 9, 7 | 10, 9, 7 | 0 |
| 10 (GPU…) | 13 | 12 | **+1** |

**HIN: 0/10 lines changed token count under .lower().**

Corpus-level:

| Metric | with `.lower()` | without `.lower()` | Δ% |
|---|---|---|---|
| ENG fertility | 1.265206 | 1.229329 | **−2.836%** |
| HIN fertility | 7.448452 | 7.448452 | **0.000%** |
| HIN/ENG ratio | 5.887148 | 6.058958 | **+2.918%** |
| ENG total tokens | 99 | 96 | −3.030% |
| HIN total tokens | 459 | 459 | 0.000% |
| ENG tok/char | 0.225636 | 0.219562 | −2.692% |
| HIN tok/char | 1.579108 | 1.579108 | 0.000% |

**At 2 d.p.:**

| | ENG | HIN | ratio |
|---|---|---|---|
| with `.lower()` | 1.27 | 7.45 | 5.89× |
| without `.lower()` | **1.23** | 7.45 | **6.06×** |

> **VERDICT: confirmed bug / misleading interpretation.** Lowercasing is _not_ noise-free and _not_ language-symmetric: it adds 3 extra tokens to English (lowercasing "NASA" from 1→2 tokens; acronym effects), zero to Hindi. Removing `.lower()` increases the ENG/HIN gap from 5.89× to **6.06×** (+2.92% on the ratio), because English becomes cheaper relative to the lowercased baseline. The comment "so casing doesn't add noise" is backwards for GPT-2: lowercasing English _depresses_ ENG fertility and thereby _understates_ the hin/eng ratio compared to a mixed-case run. This is a real preprocessing asymmetry, not a harmless choice.

---

## Experiment 4 — NFC Normalization (H4)

**Script:** `exp_h4_nfc.py`  
**Raw output:** `artifacts/raw/phase3_h4_nfc.txt`

### Part A: Synthetic isolation

| Case | len_orig | len_NFC | len_NFD | tok_NFC | tok_NFD | Changed? |
|---|---|---|---|---|---|---|
| Latin e-acute NFD (`e` + combining acute) | 2 | 1 | 2 | 1 | **3** | YES |
| Latin e-acute NFC (`é`) | 1 | 1 | 2 | 1 | 3 | YES (NFC≠NFD) |
| Devanagari ड + nukta (NFD) | 2 | 2 | 2 | 4 | 4 | no |
| Devanagari ड़ (NFC) | 2 | 2 | 2 | 4 | 4 | no |
| Devanagari क + ा | 2 | 2 | 2 | 3 | 3 | no |
| HIN sentence (NFC input) | 24 | 24 | 24 | 37 | 37 | no |
| HIN sentence (NFD input) | 24 | 24 | 24 | 37 | 37 | no |

Key: for the Latin é case, NFD produces 3 tokens vs NFC's 1 token — a 3× difference on synthetic text. However, **the sample corpora contain no such decomposed characters**.

Nukta detail: ड + ◌़ (U+0921 + U+093C) is already the NFC canonical form — `unicodedata.is_normalized('NFC', da_nfd) = True`. So this particular Devanagari combining sequence does _not_ produce an NFC vs NFD difference.

### Part B: Real-corpus impact

```
ENG: Lines changed under NFC = 0/10 — all already NFC.
HIN: Lines changed under NFC = 0/10 — all already NFC.
```

Metrics under NFC vs NFD vs no-normalize:

| Normalize | ENG fertility | ENG tok/char | HIN fertility | HIN tok/char |
|---|---|---|---|---|
| none (raw) | 1.265206 | 0.225636 | 7.448452 | 1.579108 |
| NFC | 1.265206 | 0.225636 | 7.448452 | 1.579108 |
| NFD | 1.265206 | 0.225636 | 7.448452 | 1.579108 |

All three are identical — normalization is a no-op on these files.

> **VERDICT: harmless-but-suspicious (on this specific sample).** Both sample files are already NFC, so `unicodedata.normalize("NFC", line)` produces zero change in string content, zero change in `len()`, and zero change in GPT-2 token counts on these 20 lines. The call is correct defensive programming — NFC _does_ matter for NFD-encoded corpora (the Latin é synthetic test showed 1 token NFC vs 3 tokens NFD). The verdict is narrow: "harmless _for this sample_," not "harmless in general." If the pipeline runs on NFD Devanagari corpora (e.g. some Telugu corpora are delivered in NFD), NFC normalization before tokenization is important.

---

## Experiment 5 — Character counting semantics: `len()` vs graphemes vs bytes (H5)

**Script:** `exp_h5_charcount.py`  
**Raw output:** `artifacts/raw/phase3_h5_charcount.txt`

### Part A: Synthetic isolation

Selected Hindi strings (NFC, post-lower):

| String | Code points | Grapheme clusters | UTF-8 bytes | cp/gr | bytes/gr |
|---|---|---|---|---|---|
| का (ka+matra) | 2 | 1 | 6 | 2.000 | 6.000 |
| क्ष (conjunct) | 3 | 1 | 9 | 3.000 | 9.000 |
| हैं (vowel+anusvara) | 3 | 1 | 9 | 3.000 | 9.000 |
| किताब (5-letter word) | 5 | 3 | 15 | 1.667 | 5.000 |
| क्रिकेट (cricket) | 7 | 3 | 21 | 2.333 | 7.000 |
| Hindi sentence (24 cp) | 24 | 17 | 62 | 1.412 | 3.647 |
| English: "hello" | 5 | 5 | 5 | 1.000 | 1.000 |
| English sentence (34 cp) | 34 | 34 | 34 | 1.000 | 1.000 |

tok/char under three denominators (sample strings):

| String | tokens | tok/cp | tok/grapheme | tok/byte |
|---|---|---|---|---|
| Hindi: का | 3 | 1.5000 | 3.0000 | 0.5000 |
| Hindi: क्ष | 6 | 2.0000 | 6.0000 | 0.6667 |
| Hindi: किताब | 9 | 1.8000 | 3.0000 | 0.6000 |
| Hindi sentence | 37 | 1.5417 | 2.1765 | 0.5968 |
| English: "hello" | 1 | 0.2000 | 0.2000 | 0.2000 |
| English sentence | 7 | 0.2059 | 0.2059 | 0.2059 |

For English, all three denominators are equal (cp = grapheme = byte for ASCII).

### Part B: Real-corpus impact

| | ENG tok/cp | ENG tok/gr | ENG tok/byte | HIN tok/cp | HIN tok/gr | HIN tok/byte |
|---|---|---|---|---|---|---|
| mean (per-line) | 0.225636 | 0.225636 | 0.225636 | 1.579108 | **2.449732** | **0.598992** |

**HIN/ENG ratios under each denominator:**

| Denominator | HIN/ENG ratio |
|---|---|
| code points (`len()`) — what the script uses | **6.999×** |
| grapheme clusters (visually correct) | **10.857×** |
| UTF-8 bytes | **2.655×** |

Corpus denominator totals:

```
ENG: tokens=99   code_pts=448  graphemes=448  utf8_bytes=448
HIN: tokens=459  code_pts=290  graphemes=188  utf8_bytes=764
```

HIN cp/grapheme = 290/188 = **1.543** (each visible glyph is ~1.5 code points on average).
ENG cp/grapheme = 448/448 = **1.000** (every visible glyph is exactly 1 code point).

**What `chars = len(line)` actually measures:**

`len()` on a Python `str` counts Unicode code points (Unicode scalar values). For `किताब`:
- 5 code points: U+0915 (Letter KA), U+093F (Vowel Sign I, combining), U+0924 (Letter TA), U+093E (Vowel Sign AA, combining), U+092C (Letter BA)
- 3 grapheme clusters: `कि`, `ता`, `ब`
- 15 UTF-8 bytes (each Devanagari code point = 3 bytes)

The code points counted by `len()` include combining vowel signs (matras), which are not independent visible characters. Using this as "characters" in a cross-script comparison means Hindi gets a smaller denominator than a grapheme-cluster count would give (since some code points are combining marks invisible on their own), making Hindi's tok/char appear _smaller_ than it would be under grapheme counting. Concretely: the reported 7.0× tok/char ratio becomes **10.86×** under grapheme clusters — a 55% increase. This is the largest single-metric distortion across all five experiments.

> **VERDICT: conceptual metric problem.** `chars = len(line)` measures Unicode code points, not visual characters (grapheme clusters). For English ASCII text, these are identical. For Hindi Devanagari text, combining vowel signs (matras) and halant sequences inflate the code-point count relative to grapheme count by a factor of ~1.54 on this sample. This means the reported tok/char ratio of 7.0× (HIN/ENG) is **understated**; the grapheme-cluster ratio is 10.86×. The REPORT_v0 says "per character" without defining the unit, implying visual glyphs — the code uses a different denominator. This is not merely a presentation issue: the choice of denominator changes the HIN/ENG ratio by 55%, which meaningfully affects the "6× serving cost" narrative.

---

## Summary of Verdict Table

| ID | Hypothesis | Verdict | Measured impact |
|---|---|---|---|
| H1 | `split(" ")` inserts empties, biasing fertility down | **confirmed bug** | ENG +1.41%, HIN +2.01%, ratio +0.59%; 2 d.p. cells change |
| H2 | mean-of-ratios ≠ ratio-of-totals | **aggregation bug** | ENG −0.95%, HIN −0.61%, ratio +0.35% (opposite direction) |
| H3 | `.lower()` is not language-symmetric for GPT-2 | **confirmed bug / misleading** | ENG −2.84% fertility, HIN 0.00%; ratio widens from 5.89→6.06× |
| H4 | NFC normalize changes len() and tokenizer output | **harmless-but-suspicious (this sample)** | 0/20 lines changed; synthetic NFD Latin shows 1→3 token change |
| H5 | `len()` ≠ grapheme clusters; cross-script denominator problem | **conceptual metric problem** | tok/char ratio 7.0× (code points) vs **10.86×** (graphemes) — 55% gap |
