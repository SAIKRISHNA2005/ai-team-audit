#!/usr/bin/env python3
"""
exp_h1_whitespace.py  — Experiment for Hypothesis H1
======================================================
Hypothesis: `line.split(" ")` inserts empty strings between consecutive spaces,
inflating len(words) and biasing fertility DOWN. `split()` (no arg) collapses
all whitespace and gives the standard word count.

Part A: Synthetic isolation — show empty-string counts, word count diffs, and
        fertility diffs on hand-crafted strings.
Part B: Real-corpus impact — re-run the actual sample corpora with split() vs
        split(" ") and report exact before/after fertility numbers and % change.

fertility.py is left untouched. This script copies only the relevant logic.
"""

import sys
import unicodedata
import tiktoken

# Windows console may be cp1252; force UTF-8 so Devanagari prints safely.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENG_PATH = "starterkit(1)/starter_kit/corpus_sample/eng_sample.txt"
HIN_PATH = "starterkit(1)/starter_kit/corpus_sample/hin_sample.txt"

# ---------------------------------------------------------------------------
# Helpers: replicate fertility.py read_lines and analyze, parameterised on
# the split function so we can swap split(" ") vs split().
# ---------------------------------------------------------------------------

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


def analyze_split_variant(lines, encode, split_fn):
    """Return (fertility, tpc) like fertility.py but with the given split function."""
    per_line_fertility = []
    per_line_tpc = []
    for line in lines:
        line = line.lower()
        tokens = encode(line)
        words = split_fn(line)
        chars = len(line)
        per_line_fertility.append(len(tokens) / len(words))
        per_line_tpc.append(len(tokens) / chars)
    n = len(per_line_fertility)
    return sum(per_line_fertility) / n, sum(per_line_tpc) / n


def split_space(s):
    return s.split(" ")


def split_any(s):
    return s.split()


# ---------------------------------------------------------------------------
# Part A: Synthetic isolation test
# ---------------------------------------------------------------------------

def part_a():
    print("=" * 70)
    print("PART A  Synthetic isolation: split(' ') vs split() empty-string counts")
    print("=" * 70)

    synthetic_cases = [
        ("ENG single space",       "hello world how are you"),
        ("ENG double space",       "please keep the books  in the cupboard"),
        ("ENG triple space",       "word1   word2   word3"),
        ("ENG leading space",      " leading word"),
        ("ENG trailing space",     "trailing word "),
        ("ENG leading+trailing",   " both sides "),
        ("ENG tab",                "word1\tword2"),
        ("ENG newline embedded",   "word1\nword2"),
        ("HIN single space",       "mujhe subah ki chai pasand hai"),
        ("HIN double space",       "kitaaben  almaari mein rakhi hain"),
        ("HIN triple space",       "shabd1   shabd2   shabd3"),
        ("HIN leading space",      " pehla shabd"),
        ("HIN trailing space",     "antim shabd "),
        ("HIN double space (dev)", "\u0915\u093f\u0924\u093e\u092c\u0947\u0902  \u0905\u0932\u092e\u093e\u0930\u0940 \u092e\u0947\u0902"),
    ]

    print(f"\n{'Case':<36} {'split_sp':>9} {'split()':>8} {'empties':>8}")
    print("-" * 65)
    for label, text in synthetic_cases:
        ws = text.split(" ")
        wany = text.split()
        empties = sum(1 for w in ws if w == "")
        print(f"{label:<36} {len(ws):>9} {len(wany):>8} {empties:>8}")

    # Fertility distortion on synthetic cases (mock token count = non-empty words)
    print()
    print("--- Fertility distortion (mock: token_count = len(split()) words) ---")
    print()

    distortion_cases = [
        ("single spaces only",     "one two three four five"),
        ("one double space",       "please keep the books  in the cupboard"),
        ("two double spaces",      "aa  bb  cc dd"),
        ("leading + trailing",     " aa bb cc "),
        ("tab separated",          "aa\tbb\tcc"),
        ("HIN double space",       "\u0915\u093f\u0924\u093e\u092c\u0947\u0902  \u0905\u0932\u092e\u093e\u0930\u0940 \u092e\u0947\u0902"),
    ]

    print(f"{'Case':<30} {'fert_split_sp':>14} {'fert_split()':>13} {'delta':>8} {'%change':>9}")
    print("-" * 78)
    for label, text in distortion_cases:
        ws = text.split(" ")
        wany = text.split()
        # Mock: token count = word count from split() — isolates the split effect.
        mock_tokens = len(wany)
        if len(ws) == 0 or len(wany) == 0:
            continue
        f_sp = mock_tokens / len(ws)
        f_any = mock_tokens / len(wany)
        delta = f_any - f_sp
        pct = 100 * delta / f_sp if f_sp else float("nan")
        print(f"{label:<30} {f_sp:>14.4f} {f_any:>13.4f} {delta:>8.4f} {pct:>8.2f}%")


# ---------------------------------------------------------------------------
# Part B: Real-corpus impact
# ---------------------------------------------------------------------------

def part_b():
    print()
    print("=" * 70)
    print("PART B  Real-corpus impact: split(' ') vs split() on sample corpora")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    eng_lines = read_lines(ENG_PATH)
    hin_lines = read_lines(HIN_PATH)

    print(f"\n  English corpus: {len(eng_lines)} lines")
    print(f"  Hindi corpus:   {len(hin_lines)} lines")

    # Detailed per-line breakdown to show exactly which lines have doubles
    print()
    print("--- Per-line empty-string counts in split(' ') ---")
    for lang, lines in [("ENG", eng_lines), ("HIN", hin_lines)]:
        total_empties = 0
        for i, raw_line in enumerate(lines):
            line = raw_line.lower()
            ws = line.split(" ")
            empties = sum(1 for w in ws if w == "")
            if empties > 0:
                print(f"  [{lang} line {i+1}] empties={empties}  text={repr(line)}")
            total_empties += empties
        print(f"  [{lang}] total empty strings across all lines: {total_empties}")

    print()
    print("--- Fertility comparison (original split(' ') vs split()) ---")

    results = {}
    for lang, lines in [("eng", eng_lines), ("hin", hin_lines)]:
        f_sp, tpc_sp = analyze_split_variant(lines, encode, split_space)
        f_any, tpc_any = analyze_split_variant(lines, encode, split_any)
        results[lang] = {
            "split_sp_fert":  f_sp,
            "split_any_fert": f_any,
            "split_sp_tpc":   tpc_sp,
            "split_any_tpc":  tpc_any,
        }

    eng = results["eng"]
    hin = results["hin"]

    fert_sp_e  = eng["split_sp_fert"]
    fert_any_e = eng["split_any_fert"]
    fert_sp_h  = hin["split_sp_fert"]
    fert_any_h = hin["split_any_fert"]

    tpc_sp_e  = eng["split_sp_tpc"]
    tpc_any_e = eng["split_any_tpc"]
    tpc_sp_h  = hin["split_sp_tpc"]
    tpc_any_h = hin["split_any_tpc"]

    ratio_sp  = fert_sp_h  / fert_sp_e
    ratio_any = fert_any_h / fert_any_e

    def pct(before, after):
        return 100 * (after - before) / before if before else float("nan")

    hdr_before = 'BEFORE split(" ")'
    print(f"\n{'Metric':<30} {hdr_before:>18} {'AFTER split()':>14} {'Delta %':>8}")
    print("-" * 73)
    print(f"{'ENG fertility':30} {fert_sp_e:>18.6f} {fert_any_e:>14.6f} {pct(fert_sp_e, fert_any_e):>7.3f}%")
    print(f"{'HIN fertility':30} {fert_sp_h:>18.6f} {fert_any_h:>14.6f} {pct(fert_sp_h, fert_any_h):>7.3f}%")
    print(f"{'HIN/ENG ratio':30} {ratio_sp:>18.6f} {ratio_any:>14.6f} {pct(ratio_sp, ratio_any):>7.3f}%")
    print(f"{'ENG tok/char':30} {tpc_sp_e:>18.6f} {tpc_any_e:>14.6f} {pct(tpc_sp_e, tpc_any_e):>7.3f}%")
    print(f"{'HIN tok/char':30} {tpc_sp_h:>18.6f} {tpc_any_h:>14.6f} {pct(tpc_sp_h, tpc_any_h):>7.3f}%")

    # Also 2 d.p. as the report shows them
    print()
    print("--- 2 d.p. display (as in REPORT_v0 / fertility.py output) ---")
    print(f"  BEFORE: ENG {fert_sp_e:.2f}  HIN {fert_sp_h:.2f}  ratio {ratio_sp:.2f}x")
    print(f"  AFTER:  ENG {fert_any_e:.2f}  HIN {fert_any_h:.2f}  ratio {ratio_any:.2f}x")
    ratio_sp_rounded = round(fert_sp_h, 2) / round(fert_sp_e, 2)
    ratio_any_rounded = round(fert_any_h, 2) / round(fert_any_e, 2)
    print(f"  BEFORE ratio from displayed cells: {ratio_sp_rounded:.4f}x")
    print(f"  AFTER  ratio from displayed cells: {ratio_any_rounded:.4f}x")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    part_a()
    part_b()
    print()
    print("=" * 70)
    print("END OF EXP_H1")
