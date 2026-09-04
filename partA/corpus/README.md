# Evaluation Corpus — FLORES-200 devtest

## Summary

| Field | Value |
|---|---|
| Source | FLORES-200 |
| Source URL | https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz |
| Split | devtest |
| Sentence count | 1012 (per language, perfectly aligned) |
| Languages | 6 (English, Hindi, Kannada, Tamil, Telugu, Malayalam) |
| License | CC BY-SA 4.0 |
| Download date | 2026-09-04 |
| Preprocessing | None beyond UTF-8 decode and trailing newline removal |
| Subsampling | None — entire devtest split used |

## Language Statistics

| Language code | Language | Sentences | Lines with irregular whitespace |
|---|---|---|---|
| eng_Latn | English (Latin) | 1012 | 0 |
| hin_Deva | Hindi (Devanagari) | 1012 | 6 |
| kan_Knda | Kannada (Kannada script) | 1012 | 213 |
| tam_Taml | Tamil (Tamil script) | 1012 | 75 |
| tel_Telu | Telugu (Telugu script) | 1012 | 136 |
| mal_Mlym | Malayalam (Malayalam script) | 1012 | 54 |

## Domain

FLORES-200 sentences are sourced from **English Wikipedia and Wikinews** articles. They were 
translated into 200+ languages by professional translators through the NLLB (No Language 
Left Behind) project at Meta AI. The domain is therefore **formal, encyclopaedic text**, 
covering a range of topics representative of Wikipedia: science, geography, history, 
current events, and general knowledge. The sentences are not conversational, spoken-style,
or code-switching text.

## Sentence Alignment

Sentence alignment is guaranteed by construction: FLORES-200 uses a fixed sentence inventory 
with consistent sentence IDs across all languages. `sentence_id=0` in `eng_Latn.txt` 
corresponds exactly to `sentence_id=0` in `hin_Deva.txt`, etc. This alignment was verified 
during corpus build — all 6 languages yielded exactly 1012 sentences.

## Preprocessing

Only minimal preprocessing was applied:
1. UTF-8 decode of the raw tarball content.
2. Strip trailing `\n` from each line.
3. No lowercasing, no NFC normalization, no tokenization, no filtering.

## Quality Checks (full report: `artifacts/raw/phase5_corpus_build.txt`)

All checks run on 1012 lines × 6 languages = 6,072 lines total.

| Check | ENG | HIN | KAN | TAM | TEL | MAL |
|---|---|---|---|---|---|---|
| Empty lines | 0 | 0 | 0 | 0 | 0 | 0 |
| Duplicate lines | 0 | 0 | 0 | 0 | 0 | 0 |
| Very short (< 5 chars) | 0 | 0 | 0 | 0 | 0 | 0 |
| Very long (> 500 chars) | 0 | 0 | 0 | 0 | 0 | 0 |
| Lines with URLs | 0 | 0 | 0 | 0 | 0 | 0 |
| Irregular whitespace | 0 | 6 | 213 | 75 | 136 | 54 |
| Zero-width characters | 1 | 3 | 289 | 5 | 154 | 250 |
| Non-NFC lines | 0 | **93** | 7 | 2 | 1 | 4 |
| Embedded Latin (> 5 alpha) | N/A | 11 | 13 | 14 | 82 | 6 |
| Punctuation-only | 0 | 0 | 0 | 0 | 0 | 0 |
| Digit runs (≥ 5 digits) | 0 | 0 | 0 | 0 | 0 | 0 |

**Notable findings and decisions:**

**hin_Deva — 93 non-NFC lines (RETAIN):** These lines contain Devanagari pre-composed letters that are not NFC-stable: U+095C (DDDHA, 55 occurrences), U+095B (ZA, 40), U+095E (FA, 14), U+095D (RHA, 9), U+0959 (KHHA, 2), U+0958 (QA, 1), U+095A (GHHA, 1). These code points (`U+0958–U+095F`) represent borrowed/foreign sounds (ZA from Arabic/Persian; QA, KHHA, etc.) used in transliteration. Under NFC, they expand from 1 code point to 2 (base letter + nukta, e.g. ZA → JA+NUKTA), making the NFC string *longer*. Decision: **retain as-is** — these are valid Hindi text. Phase 6 should apply `unicodedata.normalize("NFC", line)` before tokenization to ensure consistent GPT-2 encoding (this is what `fertility.py` already does).

**kan_Knda — 289 lines with ZWNJ (U+200C, 458 occurrences total) (RETAIN):** Zero-width non-joiner is standard Kannada orthographic usage, used to prevent virama (halant) from joining adjacent consonants into a conjunct. Examples: `ಹ್ಯಾಲಿಫ್ಯಾಕ್ಸ್‌ನ` (where ZWNJ separates the locative suffix `-ನ` from the preceding consonant cluster). This is linguistically correct; filtering would corrupt the text.

**Irregular whitespace in Indic scripts (RETAIN):** These are spaces within numerals and proper nouns (e.g., "4- ತಿಂಗಳ") and are content features, not encoding errors.

**Embedded Latin in Indic scripts (RETAIN):** Proper nouns (DNA, NASA, COVID-19, etc.) transliterated into Latin within otherwise Indic-script sentences. Expected in translated Wikipedia text. tel_Telu has 82 such sentences — Telugu uses Latin script heavily for brand names and technical terms.

**Filter decision: zero lines removed.** FLORES-200 devtest is a curated benchmark; removing any line breaks the guaranteed cross-language alignment. All observed "issues" are content features or correct orthographic practice.

## Source and Justification

**Why FLORES-200 rather than the starter-kit toy samples?**

The starter-kit samples are 10 sentences of informal, locally-composed Hindi/English text,
with no alignment guarantee and no Dravidian coverage. FLORES-200 is:
- Sentence-parallel across 200+ languages (exact alignment).
- Large enough (1012 sentences) for statistically meaningful per-language fertility estimates.
- Covers all 6 required languages including 4 Dravidian scripts.
- Publicly available and versioned (CC BY-SA 4.0).

**Why not HuggingFace `facebook/flores`?**

The HuggingFace Hub endpoint returned HTTP 403 during this phase (network restrictions
on the evaluation environment). The same data is served directly from Meta's CDN 
(`dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz`) with no authentication — this
is the canonical distribution channel referenced in the FLORES-200 paper and README.
The direct URL is used in `build_corpus.py` with a documented fallback.

## What this corpus cannot tell us

The FLORES-200 devtest corpus is a valuable but narrow instrument. Several limitations
must be kept in mind when interpreting tokenizer fertility results derived from it.

**Translated-from-English pivot text.** Although FLORES-200 was professionally translated,
the source text is English Wikipedia. This creates a structural asymmetry: Hindi, Kannada,
Tamil, Telugu, and Malayalam sentences are translations *of* English sentences, not
independently written natural text in those languages. Hindi translations of Wikipedia
sentences tend to use formal Sanskritised vocabulary and written register that may not
reflect the morphological complexity or word-length distribution of colloquial Hindi, 
journalistic Hindi, or social-media Hindi. Fertility numbers derived here may therefore
understate the complexity of high-register or colloquial Indic text for tokenisers that
were trained on those registers.

**Formal/encyclopaedic register only.** Wikipedia sentences tend to be dense with proper
nouns (which may tokenise differently from common vocabulary), numbers, and technical
terms. The tok/word and tok/char metrics computed on FLORES-200 reflect this register.
Serving-cost projections for a production system handling conversational queries,
instruction following, or customer-support text would need corpora matched to those
domains. FLORES-200 fertility numbers are a reasonable starting estimate, not a
general-purpose serving benchmark.

**No code-switching.** Real multilingual deployments frequently encounter sentences that
mix Indic scripts with English words (named entities, brand names, technical terms). 
FLORES-200 contains some embedded Latin characters in Indic lines (proper nouns), but 
does not contain the systematic code-switching that appears in Hinglish social-media
text or South Indian technical forums. Tokenisers behave differently on mixed-script 
text; results here will not generalise to code-switched corpora.

**No spoken-style text.** FLORES-200 has no transcribed speech, no colloquialisms, no
sandhi contractions, and no spoken-register vowel elisions common in Tamil and Malayalam. 
Indic tokenisers tuned on formal text may behave very differently on speech transcripts.

**Size limits for statistical confidence.** 1012 sentences is sufficient to compare
mean fertility across languages at 2–3 decimal places, but confidence intervals on
per-sentence distributions will be wide. Outlier sentences (very long or very short)
will have disproportionate influence on the mean-of-ratios estimate. Phase 6 analysis
should report bootstrap confidence intervals in addition to point estimates.

**Script-specific caveat (Dravidian).** Tamil, Telugu, Kannada, and Malayalam have very
different morphological structures: Tamil is highly agglutinative; Malayalam uses 
complex conjunct consonants even more densely than Hindi; Kannada mixes agglutinative
and fusional morphology. A single fertility number per language conflates these
differences. Fertility comparisons between Dravidian languages should be interpreted
with caution until per-language morphological complexity is separately characterised.
