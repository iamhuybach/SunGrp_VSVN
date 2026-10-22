# Review round 1: 20261022-agent-speed-and-context-review

## Model and scope

- Session: Claude Code, `claude-opus-5-5`, effort `high` (`CLAUDE_EFFORT=high`). Matches `EXC-02`. `run-gate` not called (`EXC-02`, `DEC-04`).
- Baseline: `reviews/agent-speed-review.md` §8, rows 1-15 (`DEC-01`).
- Reviewed: the uncommitted diff of the 15 files in `scope.files`, checked against the §8 check column.
- Not reviewed: `notebooks/NB_CREATE_DDL.ipynb`, `notebooks/NB_ENR_POI_INFO.ipynb`, `notebooks/NB_ENR_POI_REVIEW.ipynb`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, `tests/test_enr_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_poi_entity_contract.py`. They are in `scope.files` of `20261022-enr-landing-and-gld-flags`. Commit the two tasks separately.

## Gate verdict

`FIX_REQUIRED`

No P0 or P1. Rows 9 and 14 do not yet match the locked §8 intent (DIFF-001, DIFF-004).

## Section 8 rows

| # | File | Result | Evidence |
|---|---|---|---|
| 1 | `docs/context/01_DATA_MODEL.md` | met | `gld_srv_` / `lh_vv_gold.dbo` match only in §11; `gld_enr_poi_info` count 5. See DIFF-006 |
| 2 | `docs/context/01_DATA_MODEL.md` | met | No `14 bảng`, `13 active`, `10 bảng` |
| 3 | `docs/context/CTRL_TABLES_CONTEXT.md` | met | 9 rows match `NB_SETUP_INITIAL_DDL` cell 7, including media `display_order ASC`; the other task's diff does not touch those seed rows. `LANG_ARRAY` only in §10 |
| 4 | `docs/context/02_NAMING_CONVENTION.md` | met | `ENR_15P` on 2 lines; `_15P` row matches `DEC-08` |
| 5 | `docs/context/NB_00_ORCHES_SLV_TO_GLD.md` | met | 2/15/25/35 and 3/20/45/90 match cell 1 of both notebooks; timeout `0.00:32:00`, retry 0, `@pipeline().Pipeline` match `PL_VV_TRANS_SLV_TO_ENR_15P.json`. See DIFF-005 |
| 6 | `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md` | met | Code-cell `%run` count = the 9 notebooks in §1; `APPEND_*` values match lib cell 1; `APPEND` count 4 |
| 7 | `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` | met | `True` / `12` match cell 1; `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` in the FL_00 pipeline JSON |
| 8 | `docs/context/NB_LIB_EXTRACT_RAWDATA.md` | met | `True/True`, `12/12` match cell 1 of both extract notebooks |
| 9 | `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` | deviates | Grep check passes. Dead-code label contradicts the notebook. DIFF-001, DIFF-002, DIFF-003 |
| 10 | `.cursor/skills/vsvn-extract-notebook/SKILL.md` | met | No `in full` / `Known differences`; `doctor` PASS |
| 11 | `.cursor/skills/vsvn-notebook-library/SKILL.md` | met | 9 + 3 callers match code-cell `%run` counts |
| 12 | `docs/context/00_README.md` | met | Every `docs/context/*.md` listed; no `claude/`. See DIFF-007 |
| 13 | `AGENTS.md` | met | 8126 bytes; `doctor` PASS |
| 14 | `CLAUDE.md` | deviates | Old sentence removed; `validate --all` PASS. A remaining line still contradicts the new role table. DIFF-004 |
| 15 | `scripts/vv.py`, `tests/test_vv.py` | met | Timing around architect, review, author; `Elapsed:` printed; `elapsed_seconds` in `round-N.json`; test asserts the key; `tests/test_vv.py` 37 passed |

## Findings

| ID | Severity | Row | File:line | Failure | Fix |
|---|---|---|---|---|---|
| DIFF-001 | P2 | 9 | `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md:68`, `:108` | Labels `LANG_MODES`, `uses_langs`, `need_langs`, `langs` as dead code that runs when the registry has `LANG*`. The notebook defines none of them in code, and `check_config` raises `ConfigError` for any mode outside `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`. | Remove both rows. Also remove or correct the remaining LANG-only text at `:66` (`ENTRY_TYPE`), `:110` (`lang_entries()`), `:112` (`presence` LANG*), and the LANG / LANG_ARRAY branch of `expand_rows`, after checking each against the notebook. |
| DIFF-002 | P3 | 9 | `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md:190` | The runbook names exit key `primary_without_lang`. Notebook code does not emit it; it appears only in markdown cell 14. | Remove the key from the runbook row, or point to the actual exit key after checking `profile_docs` / exit JSON in the notebook. |
| DIFF-003 | P3 | 9 | `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md:176` | The 04/10 run record changed from `13 bảng SUCCESS` to `các bảng active SUCCESS`, rewriting a historical result to satisfy the grep. | Restore the original count and mark it as historical (for example `13 bảng SUCCESS (registry lúc đó)`). If the grep then matches, record that in `decision.md`. |
| DIFF-004 | P2 | 14 | `CLAUDE.md:25` | `Do not edit ... reviews, ... runtime runbooks` contradicts the new table: Author writes `runtime-runbook.md`, and exception sessions write their named artifact (EXC-01 wrote `reviews/agent-speed-review.md`). | Narrow the line to files outside the role's artifact, for example: "Do not edit source code, task state, decisions, or any file other than the role's artifact." |
| DIFF-005 | P3 | 5 | `docs/context/NB_00_ORCHES_SLV_TO_GLD.md:3`, `:17`, `:36` | Not yet written for both orchestrators: header date 08/10 and only the GLD code path; `Luồng hiện có` still `Chưa chốt` although ENR_15P runs; `p_pl_name` meaning lists only `_15M/_1H/_1D` while the ENR default is `_15P`. | Update the header to list both notebooks, set `Luồng hiện có` to `PL_VV_TRANS_SLV_TO_ENR_15P`, and note that `_15P` hits the lib WARN path (same wording as `02_NAMING_CONVENTION.md` §3). |
| DIFF-006 | P3 | 1 | `docs/context/01_DATA_MODEL.md` §11 (around line 395) | Moving the three `gld_srv_*` tables to §11 dropped their column lists, Run 1 row counts, and the `vi, en, ko` filter (`has_required_langs`). Row 1 asked for a move, not a trim. | Restore the dropped detail under the §11 `[PROPOSED]` row, or record in `decision.md` that the trim is intended. |
| DIFF-007 | P3 | outside list (row 12 file) | `docs/context/00_README.md:49`, summary line 8 | The new sentence `Nguồn sự thật là notebook ... và bộ file ở bảng trên` puts context files on par with notebooks, against the order at `:47`. Summary line 8 also drops the open item `C2 lib extract` without a basis in row 12. | Delete the sentence at `:49`. Restore `C2 lib extract`, or record why it is closed. |

P0/P1: 0. P2: 2. P3: 5.

## Checks run

- §8 grep and count checks for rows 1-4, 6, 9, 10, 12-14: as listed in the Evidence column.
- `vv.py show ... cell:1` for both orchestrators and both extract notebooks; code-cell `%run` count over `notebooks/*.ipynb`; FL_00 and ENR_15P pipeline JSON.
- `python scripts/vv.py doctor`: PASS.
- `python scripts/vv.py validate --all`: PASS.
- `python -m pytest -q -p no:cacheprovider tests/test_vv.py`: 37 passed.

## Not run

- `python scripts/vv.py verify 20261022-agent-speed-and-context-review` (row 15): it writes task files. `resume.md` records PASS from Main. Re-run after the fixes.
