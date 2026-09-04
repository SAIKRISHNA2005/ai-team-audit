#!/usr/bin/env python3
"""
exp_h2_aggregation.py  — Experiment for Hypothesis H2
======================================================
Hypothesis: mean(per_line_fertility_i) != sum(tokens)/sum(words) whenever
lines differ in length. fertility.py uses the per-line mean (H2).

Part A: Synthetic isolation — construct a corpus with deliberately uneven
        line lengths (1-word line vs 100-word line) and show the two
        aggregation methods diverging.
Part B: Real-corpus impact — compute both (A) current mean-of-ratios and
        (B) total-tokens / total-words on the actual sample corpora and
        report the delta for eng, hin, and the hin/eng ratio.
"""

import sys
import unicodedata
import tiktoken

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENG_PATH = "starterkit(1)/starter_kit/corpus_sample/eng_sample.txt"
HIN_PATH = "starterkit(1)/starter_kit/corpus_sample/hin_sample.txt"


def read_lines(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            line = unicodedata.normalize("NFC", line)
            lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Part A: Synthetic
# ---------------------------------------------------------------------------

def part_a():
    print("=" * 70)
    print("PART A  Synthetic: mean-of-ratios vs ratio-of-totals divergence")
    print("=" * 70)

    # Construct corpora with uneven line lengths using mock token counts
    # so we can compute both aggregation methods without a tokenizer.
    # In the mock: token_count(line) = word_count(line) * fertility_factor
    #              where fertility_factor = 2.0 per word for ALL lines
    # Then:
    #   mean-of-ratios = mean([2.0, 2.0, ...]) = 2.0   (correct regardless)
    # But with DIFFERENT fertility per word:
    #   1-word line:   1 word, 4 tokens  → ratio_i = 4.0
    #   100-word line: 100 words, 110 tokens → ratio_i = 1.1
    #   mean-of-ratios = (4.0 + 1.1) / 2 = 2.55
    #   total-tokens / total-words = (4 + 110) / (1 + 100) = 114/101 = 1.129

    print("\nScenario 1: One short line (high fertility) + one long line (low fertility)")
    scenarios = [
        ("1-word line",   1,   4),    # 1 word, 4 tokens (e.g. "hello" → [h, ell, o, \n])
        ("100-word line", 100, 110),  # 100 words, 110 tokens
    ]
    words_total = 0
    tokens_total = 0
    ratios = []
    for label, nw, nt in scenarios:
        r = nt / nw
        ratios.append(r)
        words_total += nw
        tokens_total += nt
        print(f"  {label}: {nw} words, {nt} tokens → ratio_i = {r:.4f}")

    mean_of_ratios = sum(ratios) / len(ratios)
    ratio_of_totals = tokens_total / words_total
    delta = ratio_of_totals - mean_of_ratios
    pct = 100 * delta / mean_of_ratios

    print(f"\n  mean-of-ratios          = {mean_of_ratios:.4f}")
    print(f"  ratio-of-totals         = {ratio_of_totals:.4f}  ({tokens_total}/{words_total})")
    print(f"  delta                   = {delta:.4f}")
    print(f"  % change (totals / mean) = {pct:.2f}%")

    print()
    print("Scenario 2: Extreme case — one 1-word line at very high fertility")
    extreme_scenarios = [
        ("1-word line",    1,   10),
        ("1000-word line", 1000, 1005),
    ]
    words_total2 = 0
    tokens_total2 = 0
    ratios2 = []
    for label, nw, nt in extreme_scenarios:
        r = nt / nw
        ratios2.append(r)
        words_total2 += nw
        tokens_total2 += nt
        print(f"  {label}: {nw} words, {nt} tokens → ratio_i = {r:.4f}")

    mean_of_ratios2 = sum(ratios2) / len(ratios2)
    ratio_of_totals2 = tokens_total2 / words_total2
    delta2 = ratio_of_totals2 - mean_of_ratios2
    pct2 = 100 * delta2 / mean_of_ratios2

    print(f"\n  mean-of-ratios          = {mean_of_ratios2:.4f}")
    print(f"  ratio-of-totals         = {ratio_of_totals2:.4f}  ({tokens_total2}/{words_total2})")
    print(f"  delta                   = {delta2:.4f}")
    print(f"  % change (totals / mean) = {pct2:.2f}%")

    print()
    print("Scenario 3: Three identical lines (should give zero delta)")
    equal_lines = [("line1", 10, 15), ("line2", 10, 15), ("line3", 10, 15)]
    wt3 = sum(nw for _, nw, _ in equal_lines)
    tt3 = sum(nt for _, _, nt in equal_lines)
    r3 = [nt/nw for _, nw, nt in equal_lines]
    mor3 = sum(r3) / len(r3)
    rot3 = tt3 / wt3
    print(f"  All lines: 10 words, 15 tokens → ratio = {15/10:.4f}")
    print(f"  mean-of-ratios   = {mor3:.6f}")
    print(f"  ratio-of-totals  = {rot3:.6f}")
    print(f"  delta = {rot3 - mor3:.8f}  (should be ~0)")


# ---------------------------------------------------------------------------
# Part B: Real corpus
# ---------------------------------------------------------------------------

def part_b():
    print()
    print("=" * 70)
    print("PART B  Real-corpus: mean-of-ratios (fertility.py) vs ratio-of-totals")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    def compute_both(lines):
        """
        Returns:
          mean_of_ratios_fert, ratio_of_totals_fert,
          mean_of_ratios_tpc, ratio_of_totals_tpc,
          per_line data for inspection
        """
        per_line_fertility = []
        per_line_tpc = []
        total_tokens = 0
        total_words = 0
        total_chars = 0
        per_line_data = []

        for line in lines:
            line = line.lower()
            tokens = encode(line)
            words = line.split(" ")   # original fertility.py uses split(" ")
            chars = len(line)
            nt = len(tokens)
            nw = len(words)
            nc = chars
            per_line_fertility.append(nt / nw)
            per_line_tpc.append(nt / nc)
            total_tokens += nt
            total_words += nw
            total_chars += nc
            per_line_data.append((nt, nw, nc))

        n = len(per_line_fertility)
        mor_fert = sum(per_line_fertility) / n
        rot_fert = total_tokens / total_words
        mor_tpc  = sum(per_line_tpc) / n
        rot_tpc  = total_tokens / total_chars

        return mor_fert, rot_fert, mor_tpc, rot_tpc, per_line_data, \
               total_tokens, total_words, total_chars

    eng_lines = read_lines(ENG_PATH)
    hin_lines = read_lines(HIN_PATH)

    print(f"\n  English corpus: {len(eng_lines)} lines")
    print(f"  Hindi corpus:   {len(hin_lines)} lines")

    # Per-line detail
    print()
    print("--- Per-line token/word breakdown (to show line-length variation) ---")
    for lang, lines in [("ENG", eng_lines), ("HIN", hin_lines)]:
        print(f"\n  {lang}:")
        print(f"  {'line':>5} {'words':>7} {'tokens':>8} {'ratio_i':>9} {'chars':>7}")
        print(f"  " + "-" * 42)
        enc_tmp = tiktoken.get_encoding("gpt2")
        for i, line in enumerate(lines):
            line_l = line.lower()
            t = enc_tmp.encode(line_l)
            w = line_l.split(" ")
            c = len(line_l)
            r = len(t)/len(w) if len(w) > 0 else float("nan")
            print(f"  {i+1:>5} {len(w):>7} {len(t):>8} {r:>9.4f} {c:>7}")

    eng_r = compute_both(eng_lines)
    hin_r = compute_both(hin_lines)

    mor_fert_e, rot_fert_e, mor_tpc_e, rot_tpc_e, _, tt_e, tw_e, tc_e = eng_r
    mor_fert_h, rot_fert_h, mor_tpc_h, rot_tpc_h, _, tt_h, tw_h, tc_h = hin_r

    print()
    print("--- Aggregation comparison ---")
    print(f"\n{'Metric':<35} {'mean-of-ratios':>16} {'ratio-of-totals':>17} {'delta':>10} {'delta%':>8}")
    print("-" * 90)

    def row(label, mor, rot):
        d = rot - mor
        p = 100 * d / mor if mor else float("nan")
        print(f"{label:<35} {mor:>16.6f} {rot:>17.6f} {d:>10.6f} {p:>7.3f}%")

    row("ENG fertility (tok/word)", mor_fert_e, rot_fert_e)
    row("HIN fertility (tok/word)", mor_fert_h, rot_fert_h)

    # hin/eng ratio under both methods
    ratio_mor = mor_fert_h / mor_fert_e
    ratio_rot = rot_fert_h / rot_fert_e
    d_ratio = ratio_rot - ratio_mor
    p_ratio = 100 * d_ratio / ratio_mor
    print(f"{'HIN/ENG ratio':<35} {ratio_mor:>16.6f} {ratio_rot:>17.6f} {d_ratio:>10.6f} {p_ratio:>7.3f}%")

    row("ENG tok/char", mor_tpc_e, rot_tpc_e)
    row("HIN tok/char", mor_tpc_h, rot_tpc_h)

    print()
    print("--- Totals summary ---")
    print(f"  ENG: tokens={tt_e}  words={tw_e}  chars={tc_e}")
    print(f"  HIN: tokens={tt_h}  words={tw_h}  chars={tc_h}")

    print()
    print("--- 2 d.p. display ---")
    print(f"  mean-of-ratios:   ENG {mor_fert_e:.2f}  HIN {mor_fert_h:.2f}  ratio {ratio_mor:.2f}x")
    print(f"  ratio-of-totals:  ENG {rot_fert_e:.2f}  HIN {rot_fert_h:.2f}  ratio {ratio_rot:.2f}x")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    part_a()
    part_b()
    print()
    print("=" * 70)
    print("END OF EXP_H2")
