# Script inventory: `starterkit(1)/starter_kit/fertility.py`

Evidence path (on-disk names): `starterkit(1)/starter_kit/fertility.py` (106 lines).  
No edits. Line numbers refer to that file. This document is descriptive only.

Module docstring (L2–L18) states usage:

```
python fertility.py --corpus eng=corpus_sample/eng_sample.txt \
                    --corpus hin=corpus_sample/hin_sample.txt \
                    --tokenizer gpt2
```

Tokenizer specs (L13–L15): `gpt2` → tiktoken encoding named `"gpt2"` (default); `hf:<repo_id>` → HuggingFace `AutoTokenizer`.

`random` is imported (L21) and `random.seed(1337)` is called at import time (L25). No later call uses `random`. `sys` is imported (L22) and unused.

---

## `load_tokenizer(spec: str)` — L28–L38

**Reads:** string `spec` only. Does not read corpora.

**Behavior:**

1. If `spec.startswith("hf:")` (L29): import `transformers.AutoTokenizer` (L30), `AutoTokenizer.from_pretrained(spec[3:])` (L32), return `lambda s: tok.encode(s, add_special_tokens=False)` (L33).
2. Else (L34–L38): import `tiktoken`, `enc = tiktoken.get_encoding(spec)`, return `enc.encode`.

For REPORT_v0 (`--tokenizer gpt2`), this is branch 2: tiktoken encoding `"gpt2"`, callable `enc.encode`.

---

## `read_lines(path: str)` — L41–L51

**Reads:** file at `path`, `open(..., "r", encoding="utf-8")` (L43).

**Preprocessing, in this exact order, per raw file line `raw`:**

1. `line = raw.strip()` (L45) — leading/trailing whitespace (including newline) removed.
2. If `not line`: `continue` (L46–L47) — empty/whitespace-only lines dropped.
3. `line = unicodedata.normalize("NFC", line)` (L49).
4. `lines.append(line)` (L50).

**Does not:** lowercase, tokenize, or split into words. Returns `list[str]`.

---

## `analyze(lines, encode)` — L54–L67

Docstring (L55): return `(fertility, tokens_per_char)` averaged over lines.

**Per line, in this exact order:**

1. `line = line.lower()` (L60).
2. `tokens = encode(line)` (L61) — tokenizer applied to the lowercased NFC string.
3. `words = line.split(" ")` (L62) — split on **single ASCII space only**, not `str.split()` default (which collapses whitespace).
4. `chars = len(line)` (L63) — Python `len` of the lowercased string (Unicode code points, not bytes).
5. Append `len(tokens) / len(words)` to `per_line_fertility` (L64).
6. Append `len(tokens) / chars` to `per_line_tpc` (L65).

**Aggregation into corpus values (L66–L67):**

- `n = len(per_line_fertility)`
- fertility = `sum(per_line_fertility) / n`
- tok/char = `sum(per_line_tpc) / n`

That is an **unweighted mean of per-line ratios**, not tokens/words over the whole corpus (`sum(tokens)/sum(words)`). Same for tok/char.

No handling is written for `len(words)==0` or `chars==0`.

---

## `main()` — L70–L102

**CLI (L71–L80):**

- `--corpus LANG=PATH`, `action="append"`, required. Repeatable.
- `--tokenizer`, default `"gpt2"`.

**Flow:**

1. `encode = load_tokenizer(args.tokenizer)` (L82).
2. Print header (L84–L86): `tokenizer: {spec}`, then columns `lang`, `fertility (tok/word)`, `tok/char`, then 42 dashes.
3. For each `--corpus` spec, in CLI order (L88–L93):
   - `lang, path = spec.split("=", 1)` (L89)
   - `lines = read_lines(path)` (L90)
   - `fert, tpc = analyze(lines, encode)` (L91)
   - store `results[lang] = (fert, tpc)` (L92)
   - print `f"{lang:<8}{fert:>22.2f}{tpc:>12.3f}"` (L93) — fertility rounded to **2** decimals, tok/char to **3**.
4. If `len(results) >= 2` (L95–L102):
   - `langs = list(results)` — insertion order = CLI `--corpus` order.
   - `base = langs[0]` (first corpus).
   - For each later lang: `ratio = results[lang][0] / results[base][0]` using **full-precision** fertility floats, not the printed `.2f` values.
   - Print `f"{lang} is {ratio:.2f}x the fertility of {base} ({'worse' if ratio > 1 else 'better'} tokenization)"`.

**Does not print** a tok/char ratio. The report’s “7.0× worse per character” is not produced by this script.

---

## `__main__` — L105–L106

Calls `main()`.

---

## Two metrics (as implemented)

| Name in print | Formula per line | Corpus aggregation | Print format |
|---|---|---|---|
| fertility (tok/word) | `len(encode(line.lower())) / len(line.lower().split(" "))` | mean of per-line values | `.2f` |
| tok/char | `len(encode(line.lower())) / len(line.lower())` | mean of per-line values | `.3f` |

Tokenization for the REPORT_v0 run: tiktoken `get_encoding("gpt2")` then `enc.encode` on the lowercased NFC line, no special-token flag (tiktoken `encode` default).
