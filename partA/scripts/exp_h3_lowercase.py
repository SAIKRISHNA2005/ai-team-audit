#!/usr/bin/env python3
"""
exp_h3_lowercase.py  — Experiment for Hypothesis H3
=====================================================
Hypothesis: line.lower() before encode changes English token counts more than
Hindi (Devanagari has no case), so lowercasing is NOT a language-symmetric
preprocessing step. Measure the direction and magnitude.

Part A: Synthetic — show token count differences for individual tokens and
        sentences with mixed case.
Part B: Real-corpus — run the actual sample corpora with vs without .lower()
        and report token-count deltas and fertility changes per language.
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


def analyze(lines, encode, do_lower):
    per_line_fertility = []
    per_line_tpc = []
    total_tokens = 0
    for line in lines:
        if do_lower:
            line = line.lower()
        tokens = encode(line)
        words = line.split(" ")
        chars = len(line)
        total_tokens += len(tokens)
        per_line_fertility.append(len(tokens) / len(words))
        per_line_tpc.append(len(tokens) / chars)
    n = len(per_line_fertility)
    return sum(per_line_fertility) / n, sum(per_line_tpc) / n, total_tokens


# ---------------------------------------------------------------------------
# Part A: Synthetic isolation
# ---------------------------------------------------------------------------

def part_a():
    print("=" * 70)
    print("PART A  Synthetic: .lower() impact on token counts")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    test_cases = [
        # (label, text)
        ("ENG all upper",         "NASA AND ISRO ANNOUNCED"),
        ("ENG mixed case",        "Bengaluru International Airport"),
        ("ENG proper noun",       "NASA"),
        ("ENG acronym",           "ISRO"),
        ("ENG normal lower",      "hello world"),
        ("ENG sentence-start cap","The train arrived on time."),
        ("ENG all lower",         "the train arrived on time."),
        # Hindi — Devanagari has no uppercase at all
        ("HIN devanagari",        "\u092e\u0941\u091d\u0947 \u0938\u0941\u092c\u0939 \u0915\u0940 \u091a\u093e\u092f \u092a\u0938\u0902\u0926 \u0939\u0948"),
        ("HIN with digit",        "\u092c\u0947\u0902\u0917\u0932\u0941\u0930\u0941 5G"),
        ("HIN with latin word",   "NASA \u0914\u0930 ISRO"),
    ]

    print(f"\n{'Case':<35} {'tokens_orig':>12} {'tokens_lower':>13} {'delta':>7} {'%change':>9}")
    print("-" * 80)
    for label, text in test_cases:
        t_orig  = encode(text)
        t_lower = encode(text.lower())
        d = len(t_lower) - len(t_orig)
        pct = 100 * d / len(t_orig) if t_orig else float("nan")
        flag = " <-- CHANGED" if d != 0 else ""
        print(f"{label:<35} {len(t_orig):>12} {len(t_lower):>13} {d:>7} {pct:>8.2f}%{flag}")

    print()
    print("--- Token-by-token breakdown for key cases ---")
    key_cases = [
        ("NASA", "nasa"),
        ("ISRO", "isro"),
        ("Bengaluru", "bengaluru"),
    ]
    for orig, lower in key_cases:
        t_orig  = encode(orig)
        t_lower = encode(lower)
        print(f"  {orig!r} -> {t_orig}  ({len(t_orig)} tokens)")
        print(f"  {lower!r} -> {t_lower}  ({len(t_lower)} tokens)")
        print()


# ---------------------------------------------------------------------------
# Part B: Real corpus
# ---------------------------------------------------------------------------

def part_b():
    print()
    print("=" * 70)
    print("PART B  Real-corpus: with vs without .lower()")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    eng_lines = read_lines(ENG_PATH)
    hin_lines = read_lines(HIN_PATH)

    print(f"\n  English corpus: {len(eng_lines)} lines")
    print(f"  Hindi corpus:   {len(hin_lines)} lines")

    print()
    print("--- Per-line token delta (with lower vs without lower) ---")
    for lang, lines in [("ENG", eng_lines), ("HIN", hin_lines)]:
        print(f"\n  {lang}:")
        print(f"  {'line':>5} {'tok_lower':>10} {'tok_orig':>9} {'delta':>7}")
        print(f"  " + "-" * 35)
        any_changed = False
        for i, line in enumerate(lines):
            line_l = line.lower()
            t_lower = encode(line_l)
            t_orig  = encode(line)
            d = len(t_lower) - len(t_orig)
            flag = " <--" if d != 0 else ""
            if d != 0:
                any_changed = True
            print(f"  {i+1:>5} {len(t_lower):>10} {len(t_orig):>9} {d:>7}{flag}")
        if not any_changed:
            print(f"  [{lang}] No lines changed token count under .lower()")

    print()
    print("--- Corpus-level fertility comparison ---")

    results = {}
    for lang, lines in [("eng", eng_lines), ("hin", hin_lines)]:
        f_lower, tpc_lower, tt_lower = analyze(lines, encode, do_lower=True)
        f_orig,  tpc_orig,  tt_orig  = analyze(lines, encode, do_lower=False)
        results[lang] = dict(
            f_lower=f_lower, tpc_lower=tpc_lower, tt_lower=tt_lower,
            f_orig=f_orig,   tpc_orig=tpc_orig,   tt_orig=tt_orig,
        )

    def pct(before, after):
        return 100 * (after - before) / before if before else float("nan")

    eng = results["eng"]
    hin = results["hin"]

    ratio_lower = hin["f_lower"] / eng["f_lower"]
    ratio_orig  = hin["f_orig"]  / eng["f_orig"]

    print(f"\n{'Metric':<35} {'with .lower()':>15} {'without .lower()':>17} {'delta %':>9}")
    print("-" * 78)
    print(f"{'ENG fertility':35} {eng['f_lower']:>15.6f} {eng['f_orig']:>17.6f} {pct(eng['f_lower'], eng['f_orig']):>8.3f}%")
    print(f"{'HIN fertility':35} {hin['f_lower']:>15.6f} {hin['f_orig']:>17.6f} {pct(hin['f_lower'], hin['f_orig']):>8.3f}%")
    print(f"{'HIN/ENG ratio':35} {ratio_lower:>15.6f} {ratio_orig:>17.6f} {pct(ratio_lower, ratio_orig):>8.3f}%")
    print(f"{'ENG total tokens':35} {eng['tt_lower']:>15} {eng['tt_orig']:>17} {pct(eng['tt_lower'], eng['tt_orig']):>8.3f}%")
    print(f"{'HIN total tokens':35} {hin['tt_lower']:>15} {hin['tt_orig']:>17} {pct(hin['tt_lower'], hin['tt_orig']):>8.3f}%")
    print(f"{'ENG tok/char':35} {eng['tpc_lower']:>15.6f} {eng['tpc_orig']:>17.6f} {pct(eng['tpc_lower'], eng['tpc_orig']):>8.3f}%")
    print(f"{'HIN tok/char':35} {hin['tpc_lower']:>15.6f} {hin['tpc_orig']:>17.6f} {pct(hin['tpc_lower'], hin['tpc_orig']):>8.3f}%")

    print()
    print("--- 2 d.p. display ---")
    print(f"  with .lower():    ENG {eng['f_lower']:.2f}  HIN {hin['f_lower']:.2f}  ratio {ratio_lower:.2f}x")
    print(f"  without .lower(): ENG {eng['f_orig']:.2f}  HIN {hin['f_orig']:.2f}  ratio {ratio_orig:.2f}x")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    part_a()
    part_b()
    print()
    print("=" * 70)
    print("END OF EXP_H3")
