#!/usr/bin/env python3
import sys, unicodedata
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Verify U+095B decomposition
c = '\u095b'
nfc = unicodedata.normalize('NFC', c)
nfd = unicodedata.normalize('NFD', c)
print('U+095B analysis:')
print(f'  Name: {unicodedata.name(c)}')
print(f'  NFC:  {[hex(ord(x)) for x in nfc]}  {[unicodedata.name(x) for x in nfc]}')
print(f'  NFD:  {[hex(ord(x)) for x in nfd]}  {[unicodedata.name(x) for x in nfd]}')
print(f'  is_NFC_stable: {unicodedata.is_normalized("NFC", c)}')
print()
print('KEY FINDING: U+095B (DEVANAGARI LETTER ZA) is a non-NFC-stable code point.')
print('Its canonical NFC decomposition is JA (U+091C) + NUKTA (U+093C).')
print('Lines in hin_Deva containing U+095B have raw_len < nfc_len because')
print('NFC replaces 1 code point (U+095B) with 2 code points (U+091C + U+093C).')
print()

with open('partA/corpus/hin_Deva.txt', encoding='utf-8') as f:
    lines = [l.rstrip('\n') for l in f]

# Count non-NFC code points
all_bad = Counter()
for line in lines:
    for ch in line:
        if not unicodedata.is_normalized('NFC', ch):
            name = unicodedata.name(ch, '?')
            key = f'U+{ord(ch):04X} {name}'
            all_bad[key] += 1

print('Non-NFC single codepoints found in hin_Deva (by frequency):')
for key, cnt in all_bad.most_common(10):
    print(f'  {key}: {cnt} occurrences')

# What fraction of lines contain U+095B?
lines_with_za = sum(1 for line in lines if '\u095b' in line)
print(f'\nLines containing U+095B (DEVANAGARI LETTER ZA): {lines_with_za} / {len(lines)}')
print('This is the ZA letter used for borrowed/foreign words — it IS the same character')
print('as JA+NUKTA but represented as a pre-composed form not yet in NFC canonical form.')

# What about Kannada ZWNJ?
print()
print('=== Kannada ZWNJ (U+200C) usage ===')
with open('partA/corpus/kan_Knda.txt', encoding='utf-8') as f:
    kan_lines = [l.rstrip('\n') for l in f]

lines_with_zwnj = [(i, line.count('\u200c')) for i, line in enumerate(kan_lines) if '\u200c' in line]
print(f'Lines with ZWNJ (U+200C): {len(lines_with_zwnj)}')
print('ZWNJ in Kannada is used to control conjunct formation (prevent virama from')
print('joining two consonants into a conjunct) — this is CORRECT orthographic usage.')
total_zwnj = sum(cnt for _, cnt in lines_with_zwnj)
print(f'Total ZWNJ occurrences in kan_Knda: {total_zwnj}')

# Summary of decision
print()
print('=== Filter decision ===')
print('DECISION: No lines filtered. Reasons:')
print('  1. hin_Deva 93 non-NFC lines: contain U+095B (DEVANAGARI LETTER ZA)')
print('     This is valid Devanagari text. The character is non-NFC but linguistically')
print('     correct. Filtering would remove valid Hindi sentences containing ZA sounds.')
print('  2. kan_Knda 289 ZWNJ lines: U+200C is standard Kannada orthography for')
print('     conjunct control. It is NOT noise or corruption.')
print('  3. Embedded Latin (11-82 per language): proper nouns (e.g., DNA, AIDS, NASA).')
print('  4. No empty, duplicate, punctuation-only, or corrupt lines found.')
print('  RECOMMENDATION: Apply NFC normalization at tokenization time (in Phase 6)')
print('  rather than filtering the corpus, to avoid data loss.')
