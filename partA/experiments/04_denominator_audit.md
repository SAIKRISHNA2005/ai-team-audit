# Phase 4 — Metric & Denominator Audit

**Date:** 2026-09-04  
**Objective:** Separate "is the code buggy?" from "is tok/word even the right metric?" Evaluate the conceptual validity of various denominators for cross-script tokenizer comparison.

---

## 1. Candidate Denominators for "Fertility"

When measuring tokenizer efficiency across languages, the choice of denominator determines what is being held "constant." If the denominator itself varies in semantic density between scripts, the resulting ratio will be skewed.

| Denominator | What it holds constant | Strength | Weakness | Best use case |
|---|---|---|---|---|
| **Whitespace words** | Space-delimited orthographic chunks. | Easy to compute; maps to human intuition for English text. | Highly dependent on linguistic typology (analytic vs. synthetic) and orthographic conventions (e.g., compound words, attached postpositions). A "word" is not a uniform unit of meaning across languages. | Monolingual analysis (e.g., comparing two English tokenizers against each other). |
| **Unicode code points** (`len()`) | Number of encoded character units (Unicode scalar values). | Standardized; native string length in Python (`len(str)`). | Disconnect between visual characters and code points. Inflates complex scripts (like Devanagari) where single visual characters are built from multiple combining code points. | Low-level text processing; storage estimation when encoding is fixed. |
| **Grapheme clusters** | Number of user-perceived visual characters (glyphs). | Script-agnostic measure of visual length; fair across complex text layouts. | Harder to compute (requires regex `\X` or specialized libraries); doesn't perfectly correlate with semantic density or byte size. | UX sizing; reading speed estimation; fair cross-script character density comparisons. |
| **UTF-8 bytes** | Storage and transmission size. | Perfectly objective; directly correlates with network/disk I/O and sometimes model embedding limits. | Severely penalizes non-Latin scripts (ASCII = 1 byte; Devanagari = 3 bytes; Emoji = 4+ bytes). | Network bandwidth budgeting; storage cost modeling. |
| **Parallel sentences** | Semantic content (meaning / information). | The only denominator that holds true "information" constant across languages. | Requires perfectly aligned, high-quality parallel corpora; cannot be computed on arbitrary raw text. | Cross-lingual tokenizer efficiency (e.g., how many tokens are required to express the exact same meaning). |

---

## 2. Why "Tokens per Whitespace Word" is Not a Fair Cross-Script Unit

The core metric in `REPORT_v0.md` is **tokens per word** (fertility). This implicitly assumes that 1 English word ≈ 1 Hindi word in terms of information content. 

However, Hindi orthography and morphology differ from English in ways that systematically alter word counts:
1. **Morphological density:** Hindi often attaches postpositions and case markers directly to words (especially pronouns, e.g., "उसमें" = "in that"), whereas English uses separate words (prepositions).
2. **Conjunct consonants and Matras:** Hindi uses the *virama* (halant) to combine consonants into conjuncts (e.g., "क्ष") and vowel signs (*matras*) that attach to base consonants. This allows for phonetically and grammatically dense constructs within a single unbroken string of characters.
3. **Compound words:** Similar to German, Hindi often forms compound concepts that might be written as a single continuous word, whereas English might separate them with spaces.

Because a Hindi "word" can pack more morphological and semantic information than an English "word", we expect a Hindi word to naturally require more tokens to encode that information. 

**Hypothesis:** *Tokens per whitespace word unfairly penalizes morphologically dense or agglutinative-leaning orthographies. The fertility gap (HIN/ENG) measured in "tokens/word" will be significantly larger than the gap measured in "tokens/parallel-sentence", confirming that the space-delimited word is not a stable unit of cross-lingual information.* (To be verified in Phase 6 using parallel corpora).

---

## 3. Does `tok/char` "Confirm" `tok/word`?

In `REPORT_v0.md`, the author claims:
> *"The tok/char column agrees: 1.579 vs 0.226 = 7.0× worse per character, which confirms the per-word number... the two metrics agree, so the result is robust."*

This is a **conceptual metric problem**. The two columns are not statistically independent evidence; they are mechanically linked by the average word length in each corpus.

### Derivation

Let $T$ = total tokens, $W$ = total words, $C$ = total characters.

1. Fertility (tokens per word) = $T / W$
2. Tokens per character = $T / C$
3. Characters per word = $C / W$

Notice the algebraic relationship:
$$ \text{Tokens per Character} = \frac{T}{C} = \frac{T / W}{C / W} = \frac{\text{Fertility}}{\text{Characters per Word}} $$

When computing the HIN/ENG ratio for Tokens per Character, we get:
$$ \text{Ratio}_{tok/char} = \frac{(T/C)_{HIN}}{(T/C)_{ENG}} = \frac{\text{Fertility}_{HIN}}{\text{Fertility}_{ENG}} \times \frac{(C/W)_{ENG}}{(C/W)_{HIN}} $$
$$ \text{Ratio}_{tok/char} = \text{Ratio}_{fertility} \times \frac{\text{Chars/Word}_{ENG}}{\text{Chars/Word}_{HIN}} $$

### Conclusion

The two metrics share the exact same numerator ($T$, the tokens produced by the tokenizer). They only differ by a scaling factor of $(C/W)$, the average word length. 

If Hindi and English happen to have roughly similar characters-per-word in the sample corpora, the two ratios will naturally be similar. **This does not "confirm" that the tokenizer is 6x-7x worse; it merely confirms that the numerator ($T$) diverged by that amount, and algebraic restatement preserved the gap.** Treating a correlated derivative metric as independent corroborating evidence is a methodological error.

### Synthetic Counter-Example
Imagine a tokenizer that produces exactly 10 tokens for an English sentence (10 words, 50 chars) and exactly 100 tokens for its Hindi translation (10 words, 50 chars).

*   $\text{Fertility}_{ENG} = 10/10 = 1$
*   $\text{Fertility}_{HIN} = 100/10 = 10$
*   **Fertility Ratio = 10x**

*   $\text{Tok/Char}_{ENG} = 10/50 = 0.2$
*   $\text{Tok/Char}_{HIN} = 100/50 = 2.0$
*   **Tok/Char Ratio = 10x**

The ratios match perfectly because both sentences average 5 chars/word. The second metric provides zero new information about the "robustness" of the tokenizer's performance; it is just the first metric divided by a constant.
