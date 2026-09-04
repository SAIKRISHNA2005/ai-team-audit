#!/usr/bin/env python3
"""
exp_h4_nfc.py  — Experiment for Hypothesis H4
===============================================
Hypothesis: unicodedata.normalize("NFC", line) can merge combining marks and
change len(line) and tokenizer output. If the sample files are already NFC,
the call is a no-op on these specific files.

Part A: Synthetic — build strings with NFD/NFC variants of Devanagari
        characters (including combining marks / matras) and show:
        - Whether NFC normalization changes the string
        - Whether len() changes
        - Whether GPT-2 token counts change
Part B: Real corpus — check every line in both sample files; count how many
        change under NFC; compare metrics under NFC vs NFD vs no normalize.
"""

import sys
import unicodedata
import tiktoken

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENG_PATH = "starterkit(1)/starter_kit/corpus_sample/eng_sample.txt"
HIN_PATH = "starterkit(1)/starter_kit/corpus_sample/hin_sample.txt"


def read_lines_raw(path):
    """Read lines WITHOUT applying NFC — to see the original bytes."""
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            lines.append(line)
    return lines


def read_lines_nfc(path):
    """fertility.py default: apply NFC after strip."""
    return [unicodedata.normalize("NFC", l) for l in read_lines_raw(path)]


def read_lines_nfd(path):
    return [unicodedata.normalize("NFD", l) for l in read_lines_raw(path)]


def analyze_lines(lines, encode):
    per_line_fertility = []
    per_line_tpc = []
    for line in lines:
        line = line.lower()
        tokens = encode(line)
        words = line.split(" ")
        chars = len(line)
        per_line_fertility.append(len(tokens) / len(words))
        per_line_tpc.append(len(tokens) / chars)
    n = len(per_line_fertility)
    return sum(per_line_fertility) / n, sum(per_line_tpc) / n


# ---------------------------------------------------------------------------
# Part A: Synthetic — combining characters
# ---------------------------------------------------------------------------

def part_a():
    print("=" * 70)
    print("PART A  Synthetic: NFC vs NFD with combining characters")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    # Build synthetic test strings using NFD (decomposed) versions
    # of common Devanagari matras / combining marks
    # ka + aa-matra (NFC: U+0915 U+093E = क + ा = का)
    ka_nfc = "\u0915\u093E"          # क + ा  (single matra, NFC)
    ka_nfd = "\u0915\u093E"          # same in NFD for these (both are base + matra)
    # Some characters that DO differ between NFC and NFD:
    # anusvara-style: ं = U+0902, combined diacritic
    # Use Latin combining example that is guaranteed to differ:
    # e + combining acute (NFD) vs é (NFC)
    e_nfd = "e\u0301"                # e + combining acute = NFD form of é
    e_nfc = unicodedata.normalize("NFC", e_nfd)  # é = U+00E9

    # Devanagari nukta combining: ड + ़ (U+0093C) = ड़  (NFD)
    # NFC: U+0095C (ड़ as single code point)
    da_nfd = "\u0921\u093C"          # ड + ़ (nukta combining)
    da_nfc = unicodedata.normalize("NFC", da_nfd)

    # ra + halant (U+094D) + ya (U+092F) -- conjunct -- no difference NFC/NFD for these
    rya_nfc = "\u0930\u094D\u092F"
    rya_nfd = unicodedata.normalize("NFD", rya_nfc)

    test_cases = [
        ("Latin e-acute NFD",         e_nfd),
        ("Latin e-acute NFC",         e_nfc),
        ("Devanagari ड+nukta (NFD)",   da_nfd),
        ("Devanagari ड़  (NFC)",        da_nfc),
        ("Devanagari क+ा  (NFC)",       ka_nfc),
        ("Devanagari r+hal+ya",        rya_nfc),
        ("HIN sentence NFC",          "\u092e\u0941\u091d\u0947 \u0938\u0941\u092c\u0939 \u0915\u0940 \u091a\u093e\u092f \u092a\u0938\u0902\u0926 \u0939\u0948"),
        ("HIN sentence NFD",          unicodedata.normalize("NFD", "\u092e\u0941\u091d\u0947 \u0938\u0941\u092c\u0939 \u0915\u0940 \u091a\u093e\u092f \u092a\u0938\u0902\u0926 \u0939\u0948")),
    ]

    print(f"\n{'Case':<35} {'len_orig':>9} {'len_NFC':>8} {'len_NFD':>8} "
          f"{'tok_NFC':>8} {'tok_NFD':>8} {'changed':>8}")
    print("-" * 92)

    for label, text in test_cases:
        nfc = unicodedata.normalize("NFC", text)
        nfd = unicodedata.normalize("NFD", text)
        len_orig = len(text)
        len_nfc = len(nfc)
        len_nfd = len(nfd)
        tok_nfc = len(encode(nfc))
        tok_nfd = len(encode(nfd))
        changed = "YES" if (nfc != text or nfc != nfd) else "no"
        print(f"{label:<35} {len_orig:>9} {len_nfc:>8} {len_nfd:>8} "
              f"{tok_nfc:>8} {tok_nfd:>8} {changed:>8}")

    # Show the nukta case in detail
    print()
    print("--- Nukta (ड+◌़) NFC vs NFD detail ---")
    print(f"  da_nfd: codepoints={[hex(ord(c)) for c in da_nfd]}  len={len(da_nfd)}")
    print(f"  da_nfc: codepoints={[hex(ord(c)) for c in da_nfc]}  len={len(da_nfc)}")
    print(f"  da_nfd same as da_nfc? {da_nfd == da_nfc}")
    print(f"  da_nfd NFC check: {unicodedata.is_normalized('NFC', da_nfd)}")
    print(f"  da_nfc NFC check: {unicodedata.is_normalized('NFC', da_nfc)}")

    # Latin e-acute detail
    print()
    print("--- Latin e-acute NFD vs NFC detail ---")
    print(f"  e_nfd: codepoints={[hex(ord(c)) for c in e_nfd]}  len={len(e_nfd)}")
    print(f"  e_nfc: codepoints={[hex(ord(c)) for c in e_nfc]}  len={len(e_nfc)}")
    print(f"  e_nfd tokens: {encode(e_nfd)}")
    print(f"  e_nfc tokens: {encode(e_nfc)}")


# ---------------------------------------------------------------------------
# Part B: Real corpus — check NFC status of every line
# ---------------------------------------------------------------------------

def part_b():
    print()
    print("=" * 70)
    print("PART B  Real corpus: NFC status checks and metric comparison")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    for lang_label, path in [("ENG", ENG_PATH), ("HIN", HIN_PATH)]:
        print(f"\n--- {lang_label} ---")
        raw_lines = read_lines_raw(path)
        n_changed_nfc = 0
        n_changed_nfd = 0
        len_changes = 0

        for i, line in enumerate(raw_lines):
            nfc = unicodedata.normalize("NFC", line)
            nfd = unicodedata.normalize("NFD", line)
            if nfc != line:
                n_changed_nfc += 1
                print(f"  Line {i+1} CHANGES under NFC:  before_len={len(line)}  after_len={len(nfc)}")
            if nfd != line:
                n_changed_nfd += 1
                if nfd != nfc:
                    print(f"  Line {i+1} CHANGES under NFD and nfd!=nfc: before_len={len(line)}  nfd_len={len(nfd)}")
            if len(nfc) != len(line):
                len_changes += 1

        print(f"  Lines changed under NFC: {n_changed_nfc}/{len(raw_lines)}")
        print(f"  Lines changed under NFD: {n_changed_nfd}/{len(raw_lines)}")
        print(f"  Lines with len() change after NFC: {len_changes}/{len(raw_lines)}")

        if n_changed_nfc == 0:
            print(f"  => All {lang_label} lines are already NFC — normalize() is a no-op here.")

    # Metrics under NFC vs NFD vs raw
    print()
    print("--- Corpus metrics: NFC vs NFD vs no-normalize ---")

    for lang_label, path in [("eng", ENG_PATH), ("hin", HIN_PATH)]:
        raw_lines  = read_lines_raw(path)
        nfc_lines  = [unicodedata.normalize("NFC", l) for l in raw_lines]
        nfd_lines  = [unicodedata.normalize("NFD", l) for l in raw_lines]

        f_raw, tpc_raw  = analyze_lines(raw_lines,  encode)
        f_nfc, tpc_nfc  = analyze_lines(nfc_lines,  encode)
        f_nfd, tpc_nfd  = analyze_lines(nfd_lines,  encode)

        print(f"\n  {lang_label.upper()}:")
        print(f"    {'normalize':>12} {'fertility':>12} {'tok/char':>10}")
        print(f"    {'-'*36}")
        print(f"    {'none (raw)':>12} {f_raw:>12.6f} {tpc_raw:>10.6f}")
        print(f"    {'NFC':>12} {f_nfc:>12.6f} {tpc_nfc:>10.6f}")
        print(f"    {'NFD':>12} {f_nfd:>12.6f} {tpc_nfd:>10.6f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    part_a()
    part_b()
    print()
    print("=" * 70)
    print("END OF EXP_H4")
