# Claims table: `starterkit(1)/starter_kit/REPORT_v0.md`

Source file on disk: `REPORT_v0.md` (markdown content). Line numbers below refer to that file.

**Column rules for this phase**

- **Reproduced by us?** Did we obtain the same printed number/string from the same procedure (script run or reading `bench_log.csv`)? Not whether the interpretation is justified.
- **Verified true?** Not copied from the report. Table numbers that match our stdout are marked yes *as quotations of script output*. Causal claims, serving-cost claims, tokenizer-vs-script claims, and capacity extrapolations are **Not yet experimentally verified**.
- **Needs audit?** Carried to later phases; this phase does not judge bugs.

Baseline run: `artifacts/raw/phase1_baseline_run.txt` (exit 0). Our stdout:

```
tokenizer: gpt2
lang      fertility (tok/word)    tok/char
------------------------------------------
eng                       1.27       0.226
hin                       7.45       1.579

hin is 5.89x the fertility of eng (worse tokenization)
```

Arithmetic on the **printed** table decimals (separate one-liner, not in `fertility.py`): `1.579/0.226 = 6.986725663716814`; `7.45/1.27 = 5.866141732283465`.

| Claim | Exact source (section/line of report) | Reproduced by us? | Verified true? | Needs audit? |
|---|---|---|---|---|
| Document is a draft; “numbers final”; do not edit conclusions because “the deck is already made.” | Header, L1–L4 | n/a (process note, not a measurement) | Not a scientific claim | No (meta) |
| `fertility.py` was run on the sample corpora with the `gpt2` tokenizer | §1, L7–L8 | Yes — we ran that invocation; stdout says `tokenizer: gpt2` | Yes — command and tokenizer match the report’s description | No |
| English fertility (tok/word) = **1.27** | §1 table, L12 | Yes — stdout `eng … 1.27` matches to 2 decimal places | Yes — as the value the unmodified script prints under this command | No for transcription; metric *meaning* later |
| English tok/char = **0.226** | §1 table, L12 | Yes — stdout `0.226` matches to 3 decimal places | Yes — as printed by the script | No for transcription |
| Hindi fertility (tok/word) = **7.45** | §1 table, L13 | Yes — stdout `hin … 7.45` | Yes — as printed by the script | No for transcription |
| Hindi tok/char = **1.579** | §1 table, L13 | Yes — stdout `1.579` | Yes — as printed by the script | No for transcription |
| “Hindi fertility is **5.89× worse** than English.” | §1 Findings item 1, L17–L18 | Yes — stdout `hin is 5.89x the fertility of eng (worse tokenization)` matches the 5.89× figure and the script’s “worse” label | The **print** matches. Whether 5.89 is the ratio of the *displayed* 7.45/1.27 is a different arithmetic fact: 7.45/1.27 = 5.866… (would display as 5.87 at 2 d.p.). Script uses unrounded means then `.2f` (see `00_script_inventory.md` L100–L102). **Not yet experimentally verified** as a claim about serving quality | Yes — rounding vs displayed table; “worse” wording |
| “Serving Hindi will cost us roughly **6× more per request** than English.” | §1 Findings item 1, L17–L18 | No — script does not print cost, latency, or $/request | **Not yet experimentally verified** | Yes |
| tok/char “1.579 vs 0.226 = **7.0× worse per character**” | §1 Findings item 2, L19–L20 | Partially — those two printed tok/char values reproduce; the script does **not** print 7.0×. From printed decimals: 1.579/0.226 = 6.9867… which rounds to 7.0 at 1 decimal place | The division of printed decimals is 6.9867…, reported as 7.0×. **Not yet experimentally verified** that this “confirms” fertility or that “worse per character” is the right interpretation | Yes |
| The 7.0× tok/char figure “confirms the per-word number.” | §1 Findings item 2, L19–L20 | No independent confirmation beyond noting 5.89× (fertility print) ≠ 7.0× (tok/char from table) | **Not yet experimentally verified** | Yes |
| Root cause: “Hindi simply has more Unicode characters per word, so any tokenizer will struggle.” | §1 Findings item 3, L21–L23 | No — we did not measure characters/word or any other tokenizer | **Not yet experimentally verified** | Yes |
| “This is a property of the script, not the tokenizer.” | §1 Findings item 3, L22–L23 | No — only `gpt2` was run | **Not yet experimentally verified** | Yes |
| Route all Indic traffic to a separate Indic-specialized tokenizer/model | §1 Recommendation, L25–L26 | No — recommendation, not an experiment | **Not yet experimentally verified** | Yes |
| Budget **6× serving cost** for Hindi | §1 Recommendation, L26 | No | **Not yet experimentally verified** | Yes |
| “**No further measurement needed** — the two metrics agree, so the result is robust.” | §1 Recommendation, L27–L28 | No — this is an extrapolation. The two printed ratios are 5.89× (fertility, from script) vs ~7.0× (tok/char, from table decimals) | **Not yet experimentally verified** | Yes |
| At **batch 16**, long prompts hit **1311 tok/s** | §2, L32–L33 | Yes as a **read** of `bench_log.csv` row `16,3584,512,16,…,1311.4,…` — report shows **1311** (no tenth). We did not re-run the server | CSV value is **1311.4**; report **1311**. Transcription rounding. Claim that this *is* long-prompt batch-16 throughput in the log: yes to 0 decimal places if rounded | Yes — rounding; what `reported_tok_s` counts (see bench inventory) |
| Short prompts at the implied comparison: **883 tok/s** | §2, L32–L33 | Yes as a read of row `16,512,256,16,…,883.2,…` — report **883** vs CSV **883.2** | Same rounding note as above | Yes |
| “Longer prompts clearly give **better GPU utilization**.” | §2, L33–L34 | No — we did not measure utilization. Log has `kv_cache_util` 0.12 (short, bs=16) vs 0.62 (long, bs=16), and `reported_tok_s` 883.2 vs 1311.4; “GPU utilization” is not a column | **Not yet experimentally verified** (causal / utilization) | Yes |
| Encourage clients to pack more context per request | §2 Recommendation, L36–L37 | n/a (recommendation) | **Not yet experimentally verified** | Yes |
| “Throughput improves with prompt length.” | §2 Recommendation, L36–L37 | Not as a controlled statement. In the log, batch 16 long vs short `reported_tok_s` is higher for long (1311.4 vs 883.2), but `gen_len` also differs (512 vs 256) and other rows exist | **Not yet experimentally verified** as a general rule | Yes |
| Capacity planning: assume **~1600 tok/s per L4 (best observed)** | §2 Recommendation, L37–L38 | Reading the log: max `reported_tok_s` is **2267.3** (batch 64, prompt 512, gen 256). Long-prompt max is **1607.4** (batch 24, prompt 3584, gen 512). Report’s ~1600 matches the long-prompt peak more closely than the global max | **Not yet experimentally verified** that ~1600 is the right planning number or that it is the “best observed” overall | Yes |
| Scale **linearly with batch size**, so **batch 48 should give ~3200 tok/s** | §2 Recommendation, L38–L39 | No. Log already has batch 48, prompt 3584, gen 512: `reported_tok_s` = **1298.5**, not 3200. Also batch 32 long = 1384.0, batch 24 long = 1607.4 | The **3200** figure is not in the CSV. Observed batch-48 long `reported_tok_s` is **1298.5**. Linear scaling **Not yet experimentally verified**; the existing row contradicts 3200 if that row is the intended condition | Yes |

## Table vs our stdout (decimal-place comparison)

| lang | Report fertility | Ours | Match? | Report tok/char | Ours | Match? |
|---|---|---|---|---|---|---|
| eng | 1.27 | 1.27 | exact | 0.226 | 0.226 | exact |
| hin | 7.45 | 7.45 | exact | 1.579 | 1.579 | exact |

Ratio line: report “5.89×”; our stdout “5.89x”. Exact match to the printed two decimals.
