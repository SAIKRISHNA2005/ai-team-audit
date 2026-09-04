# AI usage log

Tool: Cursor (agent collaborator). Role: senior research-engineer pair for “The Audit.”

## Phase 0

- Located extracted zip on disk; inventoried full tree including `__MACOSX/` and `.DS_Store`.
- Scaffolded repo directories and placeholder memos.
- Mirrored zip into `starterkit(1)/` without renaming; verified 17/17 files SHA-256 identical.
- Wrote `requirements.txt` with pinned versions from `pip index versions` / local install on 2026-09-04.
- Wrote `artifacts/raw/env.txt` from live `sys.version`, `platform.*`, and `python -m pip freeze`.
- Recorded filename discrepancy vs the Phase 0 diagram; did not rename evidence files to match the diagram.
- Re-verified with GNU `diff -r` (exit 0, 17=17 files), installed `requirements.txt` in a fresh `%TEMP%` venv (`pip install` 0, `pip check` clean), then deleted the duplicate `starter_kit (1)/` folder.

No analysis of fertility, corpus, or bench logs in this phase. No git commands.
