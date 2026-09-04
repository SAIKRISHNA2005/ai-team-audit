# Denominator Recommendation for Multilingual Model Routing and Serving Cost Decisions

## Executive Summary

When designing an LLM serving stack, pricing tier, or intelligent model-routing policy across multilingual workloads (English, Hindi, and Dravidian languages), engineering teams must choose a normalization baseline. 

**Recommendation:** The single metric that must drive model routing, capacity planning, and serving cost projections is:
$$\mathbf{\text{Tokens per Parallel Semantic Task / Sentence}}\quad (\text{tok/task}\text{ or }\text{tok/sentence})$$
aggregated at the **corpus / batch level** ($\frac{\sum \text{tokens}}{\sum \text{semantic units}}$).

All whitespace-word-based metrics ($\text{tok/word}$) must be **strictly rejected** as cross-script cost drivers.

---

## 1. The Serving Cost Ground Truth: What Needs to be Held Constant?

An LLM serving cost equation is governed by two fundamental invariants:

1. **Hardware & Billing Invariant:** Modern LLMs compute attention and KV-cache per **token**, and commercial LLM APIs bill per **token** (prompt + completion tokens). The raw financial cost to the provider or customer is strictly:
   $$\text{Cost} = N_{\text{tokens}} \times P_{\text{token}}$$
   
2. **User & Business Value Invariant:** The end user is not paying for characters, whitespace tokens, or UTF-8 bytes; they are paying for **a semantic payload** — answering a customer query, translating an article, or summarizing a document.

Therefore, an honest cross-language cost comparison **must hold semantic content constant** while measuring token consumption.

---

## 2. Audit of Candidate Denominators for Serving Cost

| Denominator Unit | What it Holds Constant | Why it FAILS or SUCCEEDS for Serving Cost Decisions |
|---|---|---|
| **Whitespace Words (`tok/word`)** | Space characters | **CRITICAL FAILURE (Misleading Cost Signal):** Languages distribute semantic information across words differently. Dravidian languages (Tamil, Malayalam, Kannada, Telugu) are highly agglutinative: a single Malayalam word (e.g., `പ്രമേഹമില്ലാത്ത`) expresses what requires 4 English words ("that are non-diabetic"). Under MuRIL, Malayalam uses 2.19 tok/word vs English 1.26 tok/word (+74% higher per word), but uses almost the exact same tokens per sentence (32.3 vs 27.3, only +18%). Using tok/word would cause routing algorithms to falsely believe Malayalam is 74% more expensive to serve than English. |
| **UTF-8 Bytes (`tok/byte`)** | Network Wire / Ingress Size | **FAILS (Orthographic Storage Artifact):** UTF-8 uses 1 byte for ASCII Latin and 3 bytes for Indic code points (Devanagari, Tamil, Kannada, etc.). As a result, Indic text naturally contains 2.5×–3.5× more bytes than equivalent English text. While tok/byte is useful for network bandwidth capacity planning, it measures byte-packing density, not semantic serving cost. |
| **Unicode Code Points (`tok/char`)** | Abstract character scalars | **FAILS (Collinear with tok/word):** As proven algebraically in Phase 4, tok/char is mathematically coupled to tok/word via average word length ($\frac{\text{tok}}{\text{char}} = \frac{\text{tok}}{\text{word}} \times \frac{\text{words}}{\text{chars}}$). In Indic scripts where vowels/viramas are separate code points, code point counts do not correspond to semantic density. |
| **Grapheme Clusters (`tok/grapheme`)** | Visual Aksharas (Syllables) | **PARTIAL (UI / Rendering metric):** Holds typographic visual density constant. Useful for frontend token budget estimators or UI streaming latency benchmarks, but does not track semantic unit cost. |
| **Parallel Semantic Task / Sentences (`tok/sentence`)** | **Exact Semantic Meaning** | **RECOMMENDED (Optimal Decision Metric):** Sourced from parallel corpora (e.g., FLORES-200), holding the underlying proposition/meaning 100% constant across all languages. Directly predicts prompt token length and KV cache memory footprint for equivalent user requests. |

---

## 3. Empirical Demonstration from Phase 6 Data

Our corrected analysis on the 1,012 FLORES-200 parallel sentences demonstrates how choosing the wrong denominator leads to disastrous engineering decisions:

### Case Study: Malayalam vs English under MuRIL Tokenizer

- **If you look at `tok/word`:**
  - English: **1.26** tokens/word
  - Malayalam: **2.19** tokens/word
  - *False Conclusion:* "Malayalam is +74% more expensive to serve than English. We must charge Indian users 74% more or route them to cheaper downgraded models."
  
- **If you look at `tok/sentence` (True Semantic Cost):**
  - English: **27.3** tokens/sentence (1,012 sentences = 27,651 tokens)
  - Malayalam: **32.3** tokens/sentence (1,012 sentences = 32,654 tokens)
  - *True Reality:* Serving Malayalam costs only **+18%** more tokens than English for identical semantic tasks, because Malayalam sentences contain far fewer whitespace words (average 9.5 words/sent vs English 21.6 words/sent).

### Case Study: Hindi vs English under MuRIL Tokenizer

- Under MuRIL, Hindi requires **31.6 tokens/sentence** vs English **27.3 tokens/sentence** (only a 1.16× ratio).
- Under the broken GPT-2 baseline, Hindi required **198.1 tokens/sentence** (7.41× English).
- **Architecture Insight:** The 7.4× cost penalty previously attributed to Hindi was 100% caused by deploying an English-centric BPE tokenizer (GPT-2), not by any intrinsic property of Hindi. Upgrading the tokenizer to an Indic-trained vocabulary (MuRIL) slashes Hindi token serving cost by **84.0%**.

---

## 4. Serving Architecture and Routing Guidelines

For infrastructure and ML platform teams deploying multilingual systems:

1. **Routing Policy Metric:** When estimating context-window utilization, KV-cache allocation, and inference latency for multilingual prompts, calibrate prompt budgets in **normalized semantic units (sentences/tasks)**, not character or word counts.
2. **Tokenizer Selection as a Cost Optimization:**
   - Deploying an Indic-aware tokenizer (MuRIL, Llama-3, Gemma-2, Qwen-2, or IndicBERT) reduces token processing costs by **84% to 93%** across Indic and Dravidian languages compared to legacy English-centric tokenizers.
   - For all 5 evaluated Indic languages (Hindi, Kannada, Tamil, Telugu, Malayalam), MuRIL achieves near-parity with English (serving overhead between **+6% and +20%**, rather than the +600% to +2100% under GPT-2).
3. **Bandwidth vs Inference Decoupling:**
   - Network ingress/egress bandwidth cost must be budgeted on **UTF-8 bytes**.
   - Model inference compute and GPU memory must be budgeted on **Tokens per Semantic Task**.
