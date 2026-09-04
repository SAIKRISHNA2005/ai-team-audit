#!/usr/bin/env python3
"""
exp_h5_charcount.py  — Experiment for Hypothesis H5
=====================================================
Hypothesis: chars = len(line) measures Unicode code points, NOT grapheme
clusters and NOT UTF-8 bytes. For Hindi text with combining marks/matras,
code-point count can exceed grapheme count. Using len() as "characters" for
cross-script comparison is conceptually problematic.

Part A: Synthetic — for Hindi strings containing conjuncts/matras:
        - show len(text) = Unicode code points
        - show grapheme cluster count (via regex \X)
        - show UTF-8 byte count
        - show what each denominator does to tok/char
Part B: Real corpus — compare the three denominators on the actual sample
        corpora and report per-language ratios and whether ranking is stable.
"""

import sys
import unicodedata
import tiktoken
import regex   # for grapheme cluster split via \X

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENG_PATH = "starterkit(1)/starter_kit/corpus_sample/eng_sample.txt"
HIN_PATH = "starterkit(1)/starter_kit/corpus_sample/hin_sample.txt"


def grapheme_count(s):
    """Count grapheme clusters using regex \\X."""
    return len(regex.findall(r"\X", s))


def utf8_bytes(s):
    return len(s.encode("utf-8"))


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
    print("PART A  Synthetic: code-point vs grapheme vs byte counting")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    # Construct Hindi test strings targeting conjuncts and matras
    test_cases = [
        # (label, string)
        # क = U+0915  ा = U+093E (aa-matra, combining)
        # ka + aa = का (1 visible char, 2 code points)
        ("Hindi: का (ka+matra)",        "\u0915\u093e"),
        # क्ष = k+halant+SHA = conjunct (3 code points, 1 grapheme)
        ("Hindi: क्ष (conjunct)",       "\u0915\u094d\u0937"),
        # ट्र = T+halant+R (3 code points, 1 grapheme cluster)
        ("Hindi: ट्र (halant conjunct)", "\u0920\u094d\u0930"),
        # anusvara: हैं  (hai + anusvara = 3 code points, 2 grapheme clusters)
        ("Hindi: हैं (vowel+anusvara)",  "\u0939\u0948\u0902"),
        # Full word with matras: किताब (5 code points, 5 grapheme clusters)
        ("Hindi: किताब",                "\u0915\u093f\u0924\u093e\u092c"),
        # Full word with halant: क्रिकेट
        ("Hindi: क्रिकेट (cricket)",    "\u0915\u094d\u0930\u093f\u0915\u0947\u091f"),
        # Devanagari sentence
        ("Hindi sentence",              "\u092e\u0941\u091d\u0947 \u0938\u0941\u092c\u0939 \u0915\u0940 \u091a\u093e\u092f \u092a\u0938\u0902\u0926 \u0939\u0948"),
        # English for comparison
        ("English: hello",              "hello"),
        ("English: NASA",               "nasa"),
        ("English sentence",            "the train arrived exactly on time."),
    ]

    print(f"\n{'Case':<40} {'code_pts':>9} {'graphemes':>10} {'utf8_bytes':>11} "
          f"{'cp/gr':>7} {'bytes/gr':>9}")
    print("-" * 92)
    for label, text in test_cases:
        cp    = len(text)
        gr    = grapheme_count(text)
        by    = utf8_bytes(text)
        cpgr  = cp / gr if gr else float("nan")
        bygr  = by / gr if gr else float("nan")
        print(f"{label:<40} {cp:>9} {gr:>10} {by:>11} {cpgr:>7.3f} {bygr:>9.3f}")

    print()
    print("--- tok/char under three denominators ---")
    print(f"\n{'Case':<40} {'tokens':>7} {'tok/cp':>8} {'tok/gr':>8} {'tok/byte':>9}")
    print("-" * 75)
    for label, text in test_cases:
        text_l = text.lower()
        tokens = encode(text_l)
        cp = len(text_l)
        gr = grapheme_count(text_l)
        by = utf8_bytes(text_l)
        tpc  = len(tokens) / cp   if cp else float("nan")
        tpg  = len(tokens) / gr   if gr else float("nan")
        tpb  = len(tokens) / by   if by else float("nan")
        print(f"{label:<40} {len(tokens):>7} {tpc:>8.4f} {tpg:>8.4f} {tpb:>9.4f}")

    print()
    print("--- What chars = len(line) actually measures ---")
    text = "\u0915\u093f\u0924\u093e\u092c"  # किताब
    print(f"  Text: {text!r}  (visual: {text})")
    print(f"  len(text) = {len(text)}  (Unicode code points, includes matras as separate code points)")
    print(f"  grapheme clusters = {grapheme_count(text)}  (visible character units)")
    print(f"  UTF-8 bytes = {utf8_bytes(text)}")
    print()
    print("  Code points per character:")
    for ch in text:
        name = unicodedata.name(ch, "UNKNOWN")
        cat  = unicodedata.category(ch)
        print(f"    U+{ord(ch):04X}  {name:40s}  cat={cat}")


# ---------------------------------------------------------------------------
# Part B: Real corpus
# ---------------------------------------------------------------------------

def part_b():
    print()
    print("=" * 70)
    print("PART B  Real corpus: three char-count denominators")
    print("=" * 70)

    enc = tiktoken.get_encoding("gpt2")
    encode = enc.encode

    def analyze_three(lines):
        total_tokens = 0
        total_cp     = 0
        total_gr     = 0
        total_bytes  = 0
        per_line_tpc = []
        per_line_tpg = []
        per_line_tpb = []
        for line in lines:
            line = line.lower()
            tokens = encode(line)
            nt = len(tokens)
            cp = len(line)
            gr = grapheme_count(line)
            by = utf8_bytes(line)
            total_tokens += nt
            total_cp     += cp
            total_gr     += gr
            total_bytes  += by
            per_line_tpc.append(nt / cp if cp else 0)
            per_line_tpg.append(nt / gr if gr else 0)
            per_line_tpb.append(nt / by if by else 0)
        n = len(lines)
        return {
            "mean_tpc":  sum(per_line_tpc) / n,
            "mean_tpg":  sum(per_line_tpg) / n,
            "mean_tpb":  sum(per_line_tpb) / n,
            "tot_tpc":   total_tokens / total_cp  if total_cp else 0,
            "tot_tpg":   total_tokens / total_gr  if total_gr else 0,
            "tot_tpb":   total_tokens / total_bytes if total_bytes else 0,
            "total_tokens": total_tokens,
            "total_cp": total_cp,
            "total_gr": total_gr,
            "total_bytes": total_bytes,
        }

    eng_lines = read_lines(ENG_PATH)
    hin_lines = read_lines(HIN_PATH)

    print(f"\n  English corpus: {len(eng_lines)} lines")
    print(f"  Hindi corpus:   {len(hin_lines)} lines")

    eng_r = analyze_three(eng_lines)
    hin_r = analyze_three(hin_lines)

    print()
    print("--- Per-line mean tok/denominator ---")
    print(f"\n{'Lang':<6} {'mean tok/cp':>13} {'mean tok/gr':>13} {'mean tok/byte':>14}")
    print("-" * 50)
    print(f"{'eng':<6} {eng_r['mean_tpc']:>13.6f} {eng_r['mean_tpg']:>13.6f} {eng_r['mean_tpb']:>14.6f}")
    print(f"{'hin':<6} {hin_r['mean_tpc']:>13.6f} {hin_r['mean_tpg']:>13.6f} {hin_r['mean_tpb']:>14.6f}")

    print()
    print("--- HIN/ENG ratios ---")
    print(f"  tok/code-point ratio: {hin_r['mean_tpc'] / eng_r['mean_tpc']:.4f}x")
    print(f"  tok/grapheme  ratio: {hin_r['mean_tpg'] / eng_r['mean_tpg']:.4f}x")
    print(f"  tok/byte      ratio: {hin_r['mean_tpb'] / eng_r['mean_tpb']:.4f}x")

    print()
    print("--- Denominator totals ---")
    print(f"  ENG: tokens={eng_r['total_tokens']}  code_pts={eng_r['total_cp']}  "
          f"graphemes={eng_r['total_gr']}  utf8_bytes={eng_r['total_bytes']}")
    print(f"  HIN: tokens={hin_r['total_tokens']}  code_pts={hin_r['total_cp']}  "
          f"graphemes={hin_r['total_gr']}  utf8_bytes={hin_r['total_bytes']}")

    print()
    print("--- cp/grapheme ratios (measures decomposition level) ---")
    eng_cpgr = eng_r["total_cp"] / eng_r["total_gr"]
    hin_cpgr = hin_r["total_cp"] / hin_r["total_gr"]
    print(f"  ENG cp/grapheme: {eng_cpgr:.4f}  (expected ~1.0 for ASCII-heavy text)")
    print(f"  HIN cp/grapheme: {hin_cpgr:.4f}  (>1.0 means matras/combining marks)")

    print()
    print("--- One-paragraph explanation ---")
    print("""
  chars = len(line) in fertility.py measures Unicode code points. For English,
  this nearly equals grapheme clusters (cp/grapheme ~ 1.0) because most ASCII
  characters occupy one code point and one grapheme. For Hindi Devanagari, each
  visually written character (grapheme cluster) often consists of a base letter
  plus one or more combining matras or halant (e.g. 'क्ष' = 3 code points, 1
  grapheme cluster). This means the len()-based denominator is larger for Hindi
  than grapheme-count would be, making tok/char smaller than tok/grapheme for
  Hindi, inflating the ENGLISH side of the ratio relative to a grapheme-based
  measure. Whether code-point counting is defensible depends on purpose: if
  'cost per character' means 'cost per keystroke or visible glyph,' grapheme
  clusters are the correct unit. If it means 'cost per Unicode scalar value,'
  code points are defensible but must be stated explicitly. The script uses
  code points, the REPORT says 'per character,' implying glyphs — a conceptual
  mismatch that partially inflates the HIN/ENG tok/char ratio compared to a
  grapheme-cluster denominator.
    """)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    part_a()
    part_b()
    print()
    print("=" * 70)
    print("END OF EXP_H5")
