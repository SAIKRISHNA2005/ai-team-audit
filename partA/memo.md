# Executive Memo: Multilingual Tokenizer Audit & Serving Cost Recommendation

**To:** AI Infrastructure & Platform Leadership  
**From:** Antigravity AI Evaluation Team  
**Date:** 2026-09-04  
**Subject:** Correction of Indic Tokenization Penalty & Model Routing Strategy  

---

### 1. Corrected Headline Numbers

The previous baseline report (`REPORT_v0.md`) claimed that Hindi suffers an inherent **5.89× to 7.45× fertility penalty** over English and budgeted a **6× serving cost multiplier**. Our rigorous audit across 6,072 parallel FLORES-200 sentences disproves this claim. The disparity was an artifact of deploying an English-centric tokenizer (GPT-2) and evaluating `tokens/word` without controlling for morphology.

Using our primary serving metric (**Tokens per Parallel Sentence / Semantic Unit**) with an Indic-trained tokenizer (**MuRIL**, 197k vocab), Indic serving overhead relative to English collapses from **+640%–1450% down to +6%–20%**:

| Language | Script | Baseline GPT-2 (tok/sent) | Corrected MuRIL (tok/sent) | Overhead vs English | Corrected MuRIL (tok/word) | Corrected MuRIL (tok/byte) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **English** | Latin | 26.7 | **27.3** | 1.00× (base) | 1.26 | 0.209 |
| **Hindi** | Devanagari | 198.1 | **31.6** | **1.16×** (-84.0% vs GPT-2) | 1.25 | 0.095 |
| **Tamil** | Tamil | 415.2 | **28.9** | **1.06×** (-93.0% vs GPT-2) | 1.74 | 0.069 |
| **Kannada** | Kannada | 363.1 | **29.1** | **1.07×** (-92.0% vs GPT-2) | 1.83 | 0.078 |
| **Malayalam** | Malayalam | 405.1 | **32.3** | **1.18×** (-92.0% vs GPT-2) | 2.19 | 0.079 |
| **Telugu** | Telugu | 346.6 | **32.8** | **1.20×** (-90.5% vs GPT-2) | 1.96 | 0.094 |

*Data cited directly from `partA/results/corrected_metrics.csv` and `partA/results/final_verdicts.md`.*

---

### 2. Model Routing & Capacity Recommendation

1. **Routing Policy:** Route all Indic and Dravidian traffic exclusively to models with natively trained multilingual vocabularies (e.g., MuRIL, Gemma-2, Llama-3, IndicBERT). Deprecate English-centric BPE tokenizers (GPT-2/GPT-3) for Indic endpoints.
2. **Infrastructure Sizing:** Budget Indic inference compute, KV-cache allocations, and API pricing at **+10% to +20% over English**, not +500% (6×).
3. **Reject `tok/word` for Pricing:** Dravidian languages exhibit higher `tok/word` (1.74–2.19) solely due to agglutinative morphology (fewer words per sentence, e.g., Malayalam = 9.5 words/sent vs English = 21.6 words/sent). Their semantic token cost is near parity with English.

---

### 3. Key Operational Caveat

**Translationese & Formal Domain Bias in FLORES-200:** The evaluation dataset consists of professionally translated, formal Wikipedia/news text originally authored in English. It utilizes standardized, high-register Sanskritised vocabulary and lacks the conversational code-switching (e.g., Hinglish, Romanized Indic script) and colloquial compounds characteristic of production customer support chat. Token compression on conversational mixed-script traffic will exhibit higher variance than reported here.

---

### 4. Production Monitoring Metric to Catch Domain Shifts

**Monitor: 90th Percentile Token-to-Byte Ratio ($\text{p90}\left[\frac{\text{Tokens}}{\text{UTF-8 Byte}}\right]$) on Inbound Ingestion:**
- **Baseline Target:** Under healthy Indic tokenization (MuRIL), inbound Indic text operates at $\le 0.10$ tokens/byte.
- **Alert Threshold:** Trigger a P2 alert if rolling $\text{p90}(\text{tok/byte}) \ge 0.35$. An upward spike indicates that incoming user queries contain out-of-vocabulary slang, unhandled script transliteration, or encoding corruptions that have forced the tokenizer into catastrophic single-byte fallbacks, exhausting context windows and breaching latency SLAs.
