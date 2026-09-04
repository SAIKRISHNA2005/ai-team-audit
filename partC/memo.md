# Strategic Decision Memo: Casual Multilingual Tone Adaptation

**To:** VP of Product & AI Architecture  
**From:** Sai Krishnaa  
**Date:** 2026-09-04  
**Subject:** Multilingual Tone Strategy under Hardware & Reviewer Constraints  

---

## 1. Operating Constraints & Mismatch Analysis

We operate under five hard boundaries:
1. **Compute:** 1× NVIDIA A100-80GB GPU for 2 weeks (336 GPU-hours total).
2. **Reviewer Capacity:** 1 native-speaker reviewer (Hindi + Kannada ONLY) for 10 h/week over 3 weeks (30 hours total).
3. **Timeline:** Launch review gate in exactly 3 weeks.
4. **API Budget:** $0 external API budget (no commercial frontier models for synthetic data distillation or evaluation).
5. **Target Languages (6):** Hindi, Kannada, Tamil, Telugu, Bengali, Marathi.

> [!WARNING]
> **Critical Reviewer Mismatch:** The reviewer covers only **2 of the 6 target languages** (Hindi, Kannada). Tamil, Telugu, Bengali, and Marathi have **zero human validation bandwidth**. Any architectural path that modifies shared model weights (SFT) introduces unmonitored regression risk across 67% of our supported linguistic base.

---

## 2. Strategy Decision Matrix

| Evaluation Dimension | Supervised Fine-Tuning (SFT / LoRA) | Dedicated Inference Rewriter | In-Context Prompt Engineering (Recommended) |
|---|:---:|:---:|:---:|
| **Implementation Time** | 12–14 days (data curation + training) | 10–12 days (rewriter training) | **1–2 days (immediate Day 1 start)** |
| **Compute Budget (1× A100, 2 wks)** | High risk (A100 saturated with runs) | Moderate risk (training 1B rewriter) | **Zero training risk (<25 hrs eval sweeps)** |
| **Reviewer Burden** | Requires paired dataset curation | Requires paired dataset curation | **100% focused on evaluating candidate prompts** |
| **Quality & Persona Consistency** | High (in-distribution) / Overfit risk | Moderate (potential rewriter hallucination) | **High (steered via few-shot exemplars)** |
| **Latency & Serving Cost Impact** | **0 ms decode overhead** | **+80–120% latency (sequential 2nd model)** | **+10–15 ms TTFT (~180 prompt tokens)** |
| **Rollback Risk** | Severe (redeploy baseline weights) | Moderate (bypass rewriter flag) | **Trivial (<1 second config/prompt rollback)** |
| **Cross-Language Risk (4 unreviewed)**| **CRITICAL (Weight drift on Tam/Tel/Ben/Mar)**| High (Rewriter untested on 4 langs) | **LOW (Per-language isolated prompt configs)** |
| **Week 3 Launch Readiness** | Low (<20% confidence) | Low (<30% confidence) | **HIGH (>90% confidence)** |

**Strategic Choice:** **In-Context Prompt Engineering with Language-Isolated Few-Shot Exemplars.**

---

## 3. Engineering Derivations

### Assumptions
- Reviewer throughput: **15 samples/hour** (4 mins/sample to score casual register naturalness and semantic preservation).
- Generation length: 200 tokens output; prompt overhead: 180 tokens (system persona + 2 colloquial few-shot exemplars per language).
- A100-80GB generation speed on FLM-4B: ~1,500 tok/s.

### Arithmetic
- **Human Review Budget:** $10\text{ h/wk} \times 3\text{ wks} \times 15\text{ samples/hr} = \mathbf{450\text{ samples total}}$ ($225\text{ Hindi}, 225\text{ Kannada}$).
- **Compute Budget:** 25 prompt variants $\times$ 200 test queries across 6 languages = $30,000\text{ generations} \times 380\text{ tokens} = 11.4\text{M tokens}$. Compute time = $\frac{11.4\text{M}}{1,500\text{ tok/s}} = 7,600\text{ s} = \mathbf{2.11\text{ GPU hours}}$ per sweep ($< 1\%$ of A100 capacity, leaving 330+ GPU-hours for automated validation sweeps and embedding-based semantic drift checks).
- **Serving Overhead:** $+180\text{ prompt tokens}$ on a 256-token query adds $\approx 12\text{ ms}$ TTFT on L4, while decode latency and KV cache footprint during generation remain unaffected.

---

## 4. Governance & Execution Plan

### Success Metric
- **Hindi & Kannada (Human Review):** $\ge \mathbf{80\%}$ of sampled responses rated natural/casual by the native reviewer **AND** $\ge \mathbf{95\%}$ rated meaning-preserving relative to formal baseline.
- **Tamil, Telugu, Bengali, Marathi (Automated Proxy):** Cross-lingual embedding cosine similarity (via multilingual sentence embeddings) $\ge \mathbf{0.92}$ vs formal baseline to guarantee zero hallucination/semantic drift.

### Kill Criterion
- If by **Day 8 (End of Week 1 Review)**, candidate prompts fail to achieve $\ge \mathbf{70\%}$ casual rating or meaning preservation drops below $\mathbf{90\%}$ in Hindi/Kannada human review, **terminate prompt tuning and fall back to baseline formal persona with scoped UI tone disclaimers** for the Week 3 launch.

### First Experiment on Day 1
- Deploy a 2-hour A100 batch job generating outputs for 50 golden benchmark queries across 4 prompt archetypes (Baseline Formal, Direct Instruction, Colloquial Lexicon Steering, 2-Shot Casual Exemplars) for Hindi and Kannada ($400\text{ generations total}$). Deliver the first 60 randomized outputs to the reviewer on Day 1 afternoon to establish baseline scoring calibration.
