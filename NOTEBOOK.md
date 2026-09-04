# Lab notebook

## Phase 0 — Workspace scaffold + operating spec

**Status:** complete and verified. Waiting for Phase 1 brief. No analysis performed.

### Zip source located

Original extract (used only for the mirror + `diff -r`, then deleted from this repo):

`C:\Users\saikr\OneDrive\Desktop\flam-ai-task-starter-kit\starter_kit (1)\`

Sole remaining evidence copy: `starterkit(1)/`.

This is the only extracted starter-kit tree found on disk (Desktop / Downloads / Documents / workspace). It is **not** identical to the tree drawn in the Phase 0 prompt. Observed top-level names and filenames (verbatim):

```
starter_kit (1)/
├── __MACOSX/                          # two underscores (macOS zip junk)
│   ├── ._starter_kit
│   └── starter_kit/
│       ├── ._.DS_Store
│       ├── ._bench
│       ├── ._corpus_sample
│       ├── ._fertility.py
│       ├── ._REPORT_v0.md
│       ├── bench/
│       │   ├── ._bench_log.csv
│       │   └── ._model_spec.md
│       └── corpus_sample/
│           ├── ._eng_sample.txt
│           └── ._hin_sample.txt
└── starter_kit/
    ├── .DS_Store
    ├── fertility.py
    ├── REPORT_v0.md
    ├── bench/
    │   ├── bench_log.csv
    │   └── model_spec.md
    └── corpus_sample/
        ├── eng_sample.txt
        └── hin_sample.txt
```

**Discrepancy vs Phase 0 diagram (recorded, not “fixed”):** the diagram used `_MACOSX/`, `starterkit/`, and extension-less names (`REPORT_v0`, `model_spec`, `bench_log`, `eng_sample`, `hin_sample`). Disk has `__MACOSX/`, `starter_kit/`, and extensions `.md` / `.csv` / `.txt`. Phase 0 rule is to preserve the zip byte-for-byte with **no renaming**. The mirror follows disk, not the diagram.

### Mirror

Copied entire source into `starterkit(1)/` with `robocopy /E /COPY:DAT` (includes hidden files).

Byte-for-byte check (Python SHA-256 of every file):

- SOURCE_FILE_COUNT 17
- DEST_FILE_COUNT 17
- ONLY_IN_SOURCE []
- ONLY_IN_DEST []
- IDENTICAL_FILES 17
- MISMATCHES []
- MIRROR_OK True

GNU `diff -r` (`C:\Program Files\Git\usr\bin\diff.exe`) of `starter_kit (1)` vs `starterkit(1)`: empty output, **exit code 0**. File counts **17 = 17**. After that check, `starter_kit (1)/` was removed so the submission tree contains only `starterkit(1)/`.

`starterkit(1)/` is **read-only evidence** from this point. Edits to `fertility.py` go to a copy under `partA/scripts/` only.

### Fresh venv install

Command: `python -m venv %TEMP%\flam-phase0-venv` then `pip install -r requirements.txt` (Python 3.10.5).

- `pip install` exit **0**
- `pip check`: `No broken requirements found.` (exit **0**)
- Pinned packages present: tiktoken 0.14.0, transformers 5.16.1, sentencepiece 0.2.2, pandas 2.3.3, numpy 2.2.6, matplotlib 3.10.9, unicodedata2 17.0.1, tokenizers 0.23.1

Venv lived only under `%TEMP%`; not added to the repo.

### Operating rules (locked for all later phases)

1. **EVIDENCE** — No bug / misleading-metric / performance / “better config” claim without an experiment or derivation. Otherwise write: `Not yet experimentally verified`.
2. **NO FABRICATION** — No invented numbers, tokenizer output, timings, or file contents. Produce numbers by running code and showing raw output.
3. **TRACE** — Every numeric claim: command/code, input, raw output, formula/interpretation.
4. **STRUCTURE** — observation → hypothesis → alternative explanations → minimal isolated experiment → baseline vs modified → measured result (absolute + %) → direction/magnitude → verdict → limitations/confounders.
5. **PHASING** — Only the named phase. No pre-solving later phases.
6. **GIT** — Agent does not run git. Commit message suggested at end of each phase.

### Environment

Captured by running Python/`pip freeze`/platform APIs into `artifacts/raw/env.txt` (not guessed).

# Phase 1 — Evidence inventory & baseline reproduction
Date: 2026-09-04

Question: Can we reproduce exactly what REPORT_v0 reported, and can we inventory every claim and every bench column without judging bugs yet?

What we did:
- Read `starterkit(1)/starter_kit/fertility.py` line by line; wrote `partA/experiments/00_script_inventory.md` (reads, preprocess order, tokenization, two metrics, aggregation, prints).
- Read `starterkit(1)/starter_kit/REPORT_v0.md`; wrote `partA/experiments/01_claims_table.md` covering every factual claim, number, causal statement, and recommendation (including “no further measurement needed” and “property of the script, not the tokenizer”).
- Ran unmodified `fertility.py` with gpt2 and both sample corpora, same flags as the report.
- Compared printed numbers to the report table to the decimals shown.
- Inventoried `bench/model_spec.md` and `bench/bench_log.csv` in `partA/experiments/02_bench_inventory.md`.
- Did not propose fixes or label bugs.

Command(s) run:
- cwd: `starterkit(1)/starter_kit`
- `C:\Users\saikr\AppData\Local\Temp\flam-phase0-venv\Scripts\python.exe fertility.py --corpus eng=corpus_sample/eng_sample.txt --corpus hin=corpus_sample/hin_sample.txt --tokenizer gpt2`
- Ratio check on printed decimals: `python -c "print(1.579/0.226); print(7.45/1.27)"`

Result (raw, or pointer to artifacts/raw/... file):
- Full command + stdout/stderr/exit: `artifacts/raw/phase1_baseline_run.txt`
- stdout (exit 0, stderr empty):

```
tokenizer: gpt2
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.27       0.226
hin                       7.45       1.579

hin is 5.89x the fertility of eng (worse tokenization)
```

- Report table vs stdout: eng 1.27 / 0.226 and hin 7.45 / 1.579 — exact match. Ratio line 5.89× — exact match to stdout.
- Printed-decimal divisions: 1.579/0.226 = 6.986725663716814; 7.45/1.27 = 5.866141732283465.
- Bench file reads (not a GPU rerun): batch 16 long `reported_tok_s=1311.4` (report 1311); batch 16 short `883.2` (report 883); long-prompt max `1607.4`; global max `2267.3`; batch 48 long `1298.5`.

Interpretation:
- We **can** reproduce the fertility table and the 5.89× line from the unmodified script. That is transcription fidelity, not a verdict on metric quality or serving cost.
- Causal claims (script vs tokenizer, 6× cost, metrics “agree” hence robust, GPU utilization, linear batch scaling to 3200 tok/s) were **not** tested. Not yet experimentally verified.
- `reported_tok_s` and several other bench columns are incompletely defined in `model_spec.md`.

Open questions carried to Phase 2:
- How much of the Hindi vs English gap is tokenizer vs measurement choices in `fertility.py` (lowercase, `split(" ")`, mean-of-ratios, NFC)?
- Do the two metrics “agree,” given 5.89× vs ~7.0×?
- What is the exact definition of `reported_tok_s`, `batch_size`, `wall_clock_s`, and `kv_cache_util`?
- Why does REPORT_v0’s ~3200 tok/s at batch 48 disagree with the existing CSV row 1298.5? (question only; no verdict this phase)

