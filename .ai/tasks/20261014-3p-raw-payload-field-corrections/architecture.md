RESULT: PASS

## Main brief

### Decision
PASS. Switch the 3P extract source to `normalized_payload` (constant only). Add `phone` (`nationalPhoneNumber`) and `blob_url` (`blob_url`, NONE). Add `photographer` with a new generic snapshot rule `ARRAY_AT {"index":0,"take":"displayName"}` on path `authorAttributions`. Add `is_visible` with the path-free rule `LATEST_DOC_FLAG`, computed by the extract through a hide-aware single MERGE with no delete. Round 1's `CONST_NULL` is withdrawn.
Schema change: additive `ensure_target` ADD COLUMNS, then a `full_reload` of all nine 3P tables. Before deploy, the read-only P9 parity probe must pass.
Scope expansion is required first: tests, docs/context, and the runbook are not in `scope.files`, and `test_3p_l1_contract.py` breaks on the constant change.

### Invariants Main must preserve
- S1: the extract reads only `normalized_payload`. No code cell contains `raw_payload`. The identifier stays `RAW_PAYLOAD`.
- S2: after the backfill, rows whose stamp is unchanged have 0 differences, against the baseline version, on every pre-existing column of the nine tables.
- P1: `ARRAY_AT` = `get_json_object(try_element_at(from_json(raw,'array<string>'), index+1), '$.take')`. Out of range or missing → NULL (not cast-null). A non-null value that is not an array → `_cn__`.
- V1: no `DELETE` and no `NOT MATCHED BY SOURCE` in any MERGE. Non-visibility specs produce byte-identical MERGE SQL to today.
- V2/V3: after a SUCCESS run, `is_visible = (review_id ∈ the latest applied doc's reviews[])` for every row of an anchored POI. Never NULL after the backfill.
- V4: hide writes pass the existing guard, and hidden rows take the latest doc's `(_crawled_at, _event_id)`.
- V5/V7: `_hide` rows never insert, and they update only `is_visible`, `_crawled_at`, `_event_id`, `updated_at`.
- V8: no Google key or target column name in code. The visibility column is found by rule; the photographer pick lives entirely in `convert_arg`.
- V9: a latest `reviews` that is non-null and not an array → `CastNullError` before the MERGE, whatever the policy (dry_run: WARN only).
- Registry: 56 columns, 0 inactive, 11 non-null `convert_arg`, exactly 1 NULL `json_path` (`is_visible`).

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 0 | .ai/tasks/…/task-state.yaml | scope.files, gates, review_plan | Add the tests, docs/context files, and runbook from full doc §1. Set architecture pass. Set reviewers per §16.5 | `vv.py` validator OK |
| 1 | notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb | §6 constants (`ARG_RULES`, `SNAPSHOT_ONLY_RULES`) | Add `ARRAY_AT` to both. Add `LATEST_DOC_FLAG` to `SNAPSHOT_ONLY_RULES`. New `NO_PATH_RULES = ("LATEST_DOC_FLAG",)` | Partner CDC row with either rule → `ConfigError` |
| 2 | same | `# BEGIN_RULE_PURE` | `_MAX_INDEX`, `_index`, `ARRAY_AT` branch in `parse_convert_arg`, `array_at_sql` (§6.2 verbatim) | `test_array_at_*` pass |
| 3 | same | `convert_sql`, `cast_null_sql` | `ARRAY_AT` → `array_at_sql`. `NO_PATH_RULES` → `CAST(NULL AS <dt>)`. `ARRAY_AT` cast-null → `array_pick_cn_sql` | Self-check passes |
| 4 | same | `assert_rule_sql` | Add cases `at_hit`, `at_miss`, `at_bad` (§6.2) | `rule self-check PASS` on Fabric |
| 5 | same | `ColumnSpec` | `paths` → `[]` when the path is empty or None. `can_cast_null`: True for `ARRAY_AT`, False for `LATEST_DOC_FLAG`. Add `is_visibility` | No `""` reaches the path consumers |
| 6 | same | `TableResult` | Append `extra: dict = field(default_factory=dict)` | Partner unchanged |
| 7 | same | `build_table_specs` | Matrix in §6.1, including empty-path messages and `LATEST_DOC_FLAG` limits (DOC_ARRAY, boolean, non-key, ≤1 per table). `ARRAY_AT` must be string | Dry run: no `ConfigError` |
| 8 | same | markdown §1 json_path table, rules table, change-log | Document both rules and the NULL path | Reviewed |
| 9 | notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb | cell `1ccbf8fd` and markdown `26225682` | `RAW_PAYLOAD    = "normalized_payload"` | Contract test passes |
| 10 | same | `presence` | Return `F.lit(True)` for a spec with a visibility column | `docs_by_table[review]` = VALID docs |
| 11 | same | `build_table_rows` | Skip `_raw__` creation and projection for columns with no paths | Dry run passes |
| 12 | same | new `visibility_anchors` (cell `65ab1f40`) | Full doc §7.2 | Self-check cases 1–9 pass |
| 13 | same | new `# BEGIN_VIS_PURE` block | `visibility_source_sql` (§7.3 verbatim) and `build_merge_sql` moved inside, with a hide branch (§7.4) | `test_3p_visibility_sql.py` passes |
| 14 | same | `merge_into_target` | Accept the source frame. Project `_hide` only for visibility specs | Non-visibility path unchanged |
| 15 | same | `_run_table` | Flow §7.5 steps 1–9, including the bad-shape fail-closed rule and anchor-based `state_df` | DEV acceptance §16.3 |
| 16 | same | `check_config` | Visibility spec ⇒ `state_key == "doc"`, and the doc key is derived or single-path with `_doc.`/`_root.` paths | `ConfigError` before the lock |
| 17 | same | new `assert_visibility_sql`, called in `run_extract` | 9 cases (§16.2), temp views over literals, dropped in `finally` | `visibility SQL self-check PASS` |
| 18 | same | `process_run` | `out.extra["visibility"]` from `res.extra` | Exit JSON shows it |
| 19 | same | markdown A, B, C | Source column, soft hide, new functions | Reviewed |
| 20 | notebooks/NB_CREATE_DDL.ipynb | seed cell `0f228dc1…` (`KNOWN_RULES`, `REGISTRY_SCHEMA`, `flatten_table_configs`, `validate_rows`) | Per §6.1 `NB_CREATE_DDL` bullets | Seed validates |
| 21 | same | `TABLE_CONFIGS_3P` and its header comment | The 4 rows of §5.2, appended last. Header: normalized_payload, 56 columns | `test_corrected_columns` passes |
| 22 | same | 3P seed cell `0271d481…` comment, registry `CREATE TABLE` comments | "9 bảng, 56 cột, 0 cột tắt". `json_path`/`convert_rule` comment text | Reviewed |
| 23 | tests/test_3p_l1_contract.py | `EXPECTED`, `test_registry_shape`, `test_paths_are_structural`, the `RAW_PAYLOAD` assert, new `test_corrected_columns` | Per §16.1 | pytest green |
| 24 | tests/test_3p_raw_rules.py | new `test_array_at_arg`, `test_array_at_sql` | Per §16.1 | pytest green |
| 25 | tests/test_3p_visibility_sql.py (new) | 4 tests | Per §16.1 | pytest green |
| 26 | docs/context/*.md (4 files + 3p-google/README.md) | Relevant sections | Per §15 item 5 | Reviewed |
| 27 | .ai/tasks/…/decision.md | New section | Vietnamese entries from §15 item 6 | Recorded |
| 28 | .ai/tasks/…/runtime-runbook.md | All headings | Vietnamese §13.2 steps plus §16.3/§17 queries | Ready for the user |

### Order and stop points
1. Row 0 (scope expansion). **STOP if the workflow requires the user to approve the scope expansion.**
2. Rows 1–8 (lib), then rows 9–19 (extract), then rows 20–22 (DDL), then rows 23–25 (tests), then rows 26–28.
3. Local verification, then reviewers and `risk-gate`.
4. **STOP (user decision): UA-VIS1** recorded in `decision.md`.
5. DEV runbook step 1: baseline (all nine tables).
6. **STOP (evidence): P9** (full doc §17). Any non-zero gate count → user decision. No deploy before P9 passes.
7. Deploy, seed, partner dry run, 3P dry run (§13.2 steps 4–7). **STOP on any failing criterion.**
8. Backfill of the nine tables, idempotency run, incremental, DEV hide/show proof (§13.2 steps 8–10).
9. **STOP (evidence): acceptance** §16.3 items 1–8. On failure: R1/R2 (§13.3) or a user decision.
10. Prod: **STOP (evidence)** for P7, P8, P9, and parent P1–P5 on prod, plus user acknowledgment (§13.5).

### Tests and verification
- `python -m pytest tests`
- `python scripts/vv.py verify 20261014-3p-raw-payload-field-corrections`
- New or changed tests:
  - `tests/test_3p_l1_contract.py::test_registry_shape`
  - `::test_paths_are_structural`
  - `::test_extract_notebook_has_no_language_contract`
  - `::test_corrected_columns`
  - `tests/test_3p_raw_rules.py::test_array_at_arg`
  - `::test_array_at_sql`
  - `tests/test_3p_visibility_sql.py::test_source_sql_shape`
  - `::test_merge_hide_clause_first`
  - `::test_merge_no_delete`
  - `::test_merge_non_visibility_unchanged`
- Runtime:
  - `rule self-check PASS` (with `at_*` cases) and `visibility SQL self-check PASS`;
  - dry-run criteria in §13.2 step 7;
  - acceptance queries in §16.3 (parity, phone oracle, media oracle, visibility oracle);
  - crash check in §16.4.

### Read only if needed
| Full-document heading | Justifies rows |
|---|---|
| 1. Scope (scope expansion list) | 0, 23–28 |
| 3. Invariants | All |
| 5. Column and source changes | 9, 21, 22, 27 |
| 6.1 Validation matrix | 1, 3, 5, 7, 20 |
| 6.2 `ARRAY_AT` code | 2, 4, 24 |
| 6.3 `LATEST_DOC_FLAG` in the extract | 11, 16 |
| 7.2 `visibility_anchors` | 12 |
| 7.3 Source builder | 13, 25 |
| 7.4 MERGE | 13, 14, 25 |
| 7.5 `_run_table` flow / 7.6 edge cases | 10, 15, 17, 18 |
| 8–10 Ordering, idempotency, partial failures | 15, 28 |
| 11 Observability | 6, 18, 28 |
| 12 Security (blob_url signed-URL gate) | 28 |
| 13 Rollout, rollback | 28 |
| 14 Alternatives | Review only |
| 16 Verification | 4, 17, 23–25, 28 |
| 17 P9/P8 probes | 28 |
| 18 User acknowledgments | 27 |

# Architecture: 3P field corrections (`phone`, `blob_url`, `photographer`, `is_visible`) and source switch to `normalized_payload`

Task: `20261014-3p-raw-payload-field-corrections`. Parent: `20261013-3p-extract-from-raw-payload` (`ready_to_merge`, not touched). Architect: `claude-opus-5-5`, effort `high`. Round 2. This document replaces round 1 completely.

## 0. Verdict rationale

Every open item from round 1 is now closed by a user decision or by evidence:

- `photographer`: P7 showed 0/280 for the singular path and 280/280 for `authorAttributions[0].displayName`, with every array of size 1. The user chose option 1, the first element. This design delivers it with a generic, registry-driven rule, `ARRAY_AT` (§6.2). There is no Google-specific code.
- `blob_url`: the user named the path `photos[].blob_url`. P7 shows the key on 280/280 elements and a non-null value on 140/280. The column is now a plain string path. Round 1's `CONST_NULL` rule is withdrawn.
- The source column is now `normalized_payload` (decision "Quyết định nguồn và blob_url"). No design choice depends on whether `normalized_payload` really equals `raw_payload` plus `photos[].blob_url`. That premise only decides go or no-go, so it is a mandatory read-only gate (P9) before any write in DEV and in prod (§13). It does not block architecture.
- `is_visible`: Q-VIS (b) is unchanged from round 1. Its design is carried forward, without `CONST_NULL`.

There are two user acknowledgments: UA-VIS1 (§18) and the P9 outcome. Both are stop points before the DEV runtime. Neither blocks implementation or review.

## 1. Scope

Current repository state relevant to this design (verified on 2026-10-14):

- In `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, cell `1ccbf8fd` has `RAW_PAYLOAD = "raw_payload"`. `doc_columns`, `classify_docs`, and the reject paths all read through this constant. No other code names the payload column.
- In `NB_LIB_EXTRACT_RAWDATA`:
  - `JSON_PATH_RE` is `[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*` and has no index segments.
  - `path_value` and `elem_fields` split paths on `.`, so `authorAttributions[0].displayName` cannot be expressed as a path.
  - An empty `json_path` fails `snapshot_path_error`, so a row with no path cannot be loaded today.
  - `ColumnSpec.paths` would yield `[""]` for an empty path.
- In `NB_CREATE_DDL`, `TABLE_CONFIGS_3P` has 9 tables, 52 columns, 0 inactive columns, and 10 non-null `arg` values. `REGISTRY_SCHEMA.json_path` is `nullable=False`. `flatten_table_configs` reads `col_cfg["path"]`.
- `ensure_target` adds missing columns with `ALTER TABLE … ADD COLUMNS` and never drops a column.
- `build_merge_sql` has one guarded `WHEN MATCHED` clause, one `WHEN NOT MATCHED INSERT`, and no delete clause.
- `tests/test_3p_l1_contract.py` asserts `RAW_PAYLOAD    = "raw_payload"`, 52 columns, and `spec["path"].split(",")` (which fails on `None`).

In scope:

1. Source column switch to `normalized_payload` (§5.1).
2. Registry and DDL rows for the four columns (§5.2).
3. Lib rule `ARRAY_AT`, a positional array pick (§6.2).
4. Lib rule `LATEST_DOC_FLAG`, a path-free flag computed by the extract (§6.3).
5. The extract computes `is_visible` and hides reviews with a hide-aware MERGE. No row is ever deleted (§7).
6. Additive physical schema change through `ensure_target`, then a `full_reload` of the nine 3P tables gated by P9 (§13).
7. Self-checks, local tests, context docs, a Vietnamese runbook, and `decision.md` entries.

Scope expansion Main must record in `task-state.yaml` before editing, because these paths are not in `scope.files`:

- `tests/test_3p_l1_contract.py`
- `tests/test_3p_raw_rules.py`
- `tests/test_3p_visibility_sql.py` (new)
- `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`
- `docs/context/NB_LIB_EXTRACT_RAWDATA.md`
- `docs/context/CTRL_TABLES_CONTEXT.md`
- `docs/context/01_DATA_MODEL.md`
- the one-line source mention in `docs/context/3p-google/README.md`
- the task's own `runtime-runbook.md`

`tests/test_3p_l1_contract.py` fails as soon as the constant changes, so this expansion is required, not optional.

## 2. Non-goals

- Any column change on the other six 3P tables, or any other column of the three affected tables. Parent decisions Q1–Q16, `dropped_columns_confirmed`, and UA1 stay as they are. `slv_3p_poi_contact.phone_raw` stays removed. The source switch must leave every pre-existing value unchanged (invariant S2).
- Reading `raw_payload` anywhere, or reading both columns.
- Phone formatting. `phone` is a structural copy of `nationalPhoneNumber`.
- An element-selection rule other than "element at index N". There is no matching, no "longest name", and no handling for an `authorAttributions` of size > 1 beyond taking index 0, as the user chose.
- Storing the `authorAttributions` JSON (option 3 was not chosen).
- A hash column for the soft delete, a physical DELETE, or `WHEN NOT MATCHED BY SOURCE`.
- Gold changes, including filtering `is_visible`. This is recorded for the gold task in §11.3.
- Partner behavior. The lib changes are additive and snapshot-only.
- Pipeline JSON and `ctrl_mng_pipeline_config`. Review stays `DOC_ARRAY` with key `review_id`. Media keeps `dedup_order = display_order ASC`.
- The parent task's status.

## 3. Invariants

Parent invariants I1–I12 still hold. These are added:

- **S1, single source column.** The 3P extract reads only `normalized_payload`. `raw_payload` is not in `doc_columns`. There is one constant, `RAW_PAYLOAD`, whose value is `"normalized_payload"`.
- **S2, switch parity.** For every row whose `(_crawled_at, _event_id)` stamp is unchanged by the backfill, every pre-existing column of the nine 3P tables equals its baseline value. Updated-at timestamps are excluded. This is gated by P9 before the write and by the parity check after it (§16.3).
- **P1, `ARRAY_AT` semantics.** The value is `get_json_object(element_at(array, index + 1), '$.<take>')`.
  - If the index is out of range, `take` is absent, or `take` is JSON null, the value is NULL and is not counted as cast-null.
  - If the raw value is non-null and not a JSON array, the row is counted in `_cn__` and falls under `cast_null_policy`, exactly like `ARRAY_PICK`.
- **V1, no physical delete.** No MERGE has a delete clause. Visibility changes only through UPDATE.
- **V2, visibility semantics (Q-VIS b).** Let L be the latest applied VALID document for `poi_id` P, ordered by `(crawled_at, event_id)`. After a SUCCESS run that applied L, every review row of P has `is_visible = (review_id ∈ keys of L.reviews[])`. This holds for:
  - reviews inserted in this run;
  - reviews seen only in older documents of the run;
  - reviews that exist only in the target.
- **V3, non-null.** The extract writes only `true` or `false`. After the backfill, 0 rows are NULL.
- **V4, ordering.** Every visibility write passes the existing guard `(s._crawled_at, s._event_id) >= (t._crawled_at, t._event_id)`. Hidden rows take L's stamp, so an older document can never show them again.
- **V5, hide rows never insert.** Rows with `_hide = true` only match existing rows, or do nothing.
- **V6, source uniqueness.** The MERGE source has at most one row per `review_id`. The resolved set R and the hide set H are disjoint, because H is anti-joined to R.
- **V7, hide preserves data.** A hide sets only `is_visible`, `_crawled_at`, `_event_id`, and `updated_at`.
- **V8, registry-driven.** No source key name and no target column name is hard-coded in notebook code. The visibility column is found by `convert_rule = LATEST_DOC_FLAG`. The photographer pick is entirely in `convert_arg`.
- **V9, fail closed on an ambiguous latest shape.** If the latest document of a POI has `reviews` that is non-null and not a JSON array, the review table fails before the MERGE. It is never read as "all reviews removed".

## 4. State ownership, grain, and keys

| State | Only writer | Grain / key | Change |
|---|---|---|---|
| `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` | Collector | 1 row per event | Read only. The column read changes to `normalized_payload` |
| `slv_3p_poi_contact` | 3P extract | `poi_id` | + `phone STRING` |
| `slv_3p_poi_media` | 3P extract | `media_dedup_key` | + `blob_url STRING`, + `photographer STRING` |
| `slv_3p_poi_review` | 3P extract | `review_id` (`HASH_SHA256`) | + `is_visible BOOLEAN`. Rows are never deleted |
| The other six `slv_3p_*` tables | 3P extract | Unchanged | Values must not change (S2) |
| `ctrl_cfg_schema_registry` (3P partition) | Operator via `NB_CREATE_DDL` | (source, target, column) | 56 rows, 0 inactive, 11 non-null `convert_arg`, 1 NULL `json_path` |
| `ctrl_cdc_state` (3P) | 3P extract, main thread | (target, `poi_id`) under `state_key = doc` | No schema change. For review, state now advances for every applicable VALID document (§7.5) |
| `ctrl_cdc_reject` (3P) | 3P extract | `event_hash` | No schema change. One-time new hashes for previously rejected items (§11.1) |
| Watermark, `ctrl_log_*` | 3P extract | Unchanged | Unchanged |
| `gld_enr_*` | Gold nodes | APPEND | Untouched. 15P stays disabled (UA1) |

Only the review table's single MERGE per attempt writes `is_visible`. There is one writer thread per table (I9). The DEV-only test in §13.2 step 10 is the one exception, and it removes what it writes.

## 5. Column and source changes

### 5.1 Source column

In the extract constants cell: `RAW_PAYLOAD    = "normalized_payload"`. Keep the identifier name to keep the diff minimal. Update the markdown row "`RAW_PAYLOAD` | Cột chứa tài liệu JSON (`normalized_payload`)". Reject messages derive from the constant, for example `thiếu normalized_payload`.

`check_config` already fails before the lock if the bronze table lacks the column.

### 5.2 Registry rows

Each new column is appended at the end of its table's `columns` dict. Existing `column_order` values do not change.

| `trg_tbl` | `col_name` | `column_order` | `src_object` | `json_path` | `data_type` | `convert_rule` | `convert_arg` | `is_active` |
|---|---|---|---|---|---|---|---|---|
| `slv_3p_poi_contact` | `phone` | 4 | `$` | `nationalPhoneNumber` | string | `NONE` | NULL | true |
| `slv_3p_poi_media` | `blob_url` | 7 | `photos` | `blob_url` | string | `NONE` | NULL | true |
| `slv_3p_poi_media` | `photographer` | 8 | `photos` | `authorAttributions` | string | `ARRAY_AT` | `{"index":0,"take":"displayName"}` | true |
| `slv_3p_poi_review` | `is_visible` | 8 | `reviews` | NULL | boolean | `LATEST_DOC_FLAG` | NULL | true |

Python form in `TABLE_CONFIGS_3P`:

- contact: `"phone": _str("nationalPhoneNumber"),`
- media: `"blob_url": _str("blob_url"),`
- media: `"photographer": {"path": "authorAttributions", "type": "string", "rule": "ARRAY_AT", "arg": {'index': 0, 'take': 'displayName'}},`
- review: `"is_visible": {"path": None, "type": "boolean", "rule": "LATEST_DOC_FLAG"},`

Header comment: `# [SỬA 14/10] TABLE_CONFIGS_3P đọc normalized_payload. 9 bảng, 56 cột, 0 cột tắt.`

Update the seed cell comment to "9 bảng slv_3p_poi_*, 56 cột (0 cột tắt)".

Record in `decision.md` that the proposal's "không có" for `convert_rule` on `photographer` and `is_visible` is delivered by `ARRAY_AT` and `LATEST_DOC_FLAG`. Neither rule invents a source field.

## 6. Rule mechanism

### 6.1 Validation matrix (lib `build_table_specs`, all errors collected into one `ConfigError`)

| Rule | Modes | `json_path` | `data_type` | `convert_arg` | Key allowed | Per table | `_cn__` |
|---|---|---|---|---|---|---|---|
| `ARRAY_AT` | any snapshot mode | exactly 1 part, structural (`snapshot_path_error`) | `string` | required, `{index: int 0..63, take: path}` | no | any | `array_pick_cn_sql` (raw non-null and not an array) |
| `LATEST_DOC_FLAG` | `DOC_ARRAY` only | must be NULL or empty | `boolean` | must be NULL | no | at most 1 | never |

Constant changes (lib §6 constants):

- `ARG_RULES` gains `ARRAY_AT`.
- `SNAPSHOT_ONLY_RULES` gains `ARRAY_AT` and `LATEST_DOC_FLAG`, so partner CDC rows using either rule are rejected.
- New `NO_PATH_RULES = ("LATEST_DOC_FLAG",)`.

`build_table_specs`, snapshot branch:

- If the rule is in `NO_PATH_RULES`:
  - a non-empty `json_path` is an error: "`json_path` phải rỗng với rule LATEST_DOC_FLAG";
  - set `parts = []` and skip the per-part checks.
- Otherwise, an empty `json_path` is an error: "`json_path` rỗng chỉ dùng với LATEST_DOC_FLAG". This replaces today's generic message and stays fail-closed.
- `LATEST_DOC_FLAG` errors:
  - `mode != "DOC_ARRAY"`;
  - `data_type != "boolean"`;
  - `is_key`;
  - more than one such column in the table (checked after the column loop).
- `ARRAY_AT`: the arg is parsed in the existing `ARG_RULES` block. Error if `data_type != "string"`. Multi-part paths are already rejected because `ARRAY_AT` is not in `MULTI_PART_RULES`.
- `COALESCE` and `len(parts) < 2` must still see `parts` defined in every branch.

`ColumnSpec`:

- `paths` returns `[]` when `json_path` is empty or None. `part_cols`, `spec_paths`, `top_fields`, `elem_fields`, `expand_rows`, the `profile_docs` heads, and the `check_config` forbidden-head scan therefore never see `""`.
- `can_cast_null`:
  - `True` for `ARRAY_AT`: add it to the set with `ENUM_MAP`, `ARRAY_PROJECT`, `ARRAY_PICK`, and `JSON_PICK`;
  - `False` for `LATEST_DOC_FLAG`: return early, before the string check.
- New property `is_visibility`: `convert_rule == "LATEST_DOC_FLAG"`.

Lib `convert_sql`:

- `ARRAY_AT` → `array_at_sql(raw_col, parse_convert_arg(rule, arg))`;
- a rule in `NO_PATH_RULES` → `f"CAST(NULL AS {data_type})"`, a placeholder that does not reference `_raw__`.

Lib `cast_null_sql`: `ARRAY_AT` → `array_pick_cn_sql(c.raw_col)`.

`NB_CREATE_DDL`:

- `KNOWN_RULES` gains `ARRAY_AT` and `LATEST_DOC_FLAG`.
- In `REGISTRY_SCHEMA`, `json_path` becomes `nullable=True`.
- `flatten_table_configs` uses `col_cfg.get("path")`.
- `validate_rows` adds:
  - `ARRAY_AT` to both arg-rule sets;
  - `json_path is None` if and only if the rule is `LATEST_DOC_FLAG`;
  - `LATEST_DOC_FLAG` only with `boolean`, not as a key, and at most once per `trg_tbl`;
  - `ARRAY_AT` only with `string`.
- The multi-part check already uses `(r["json_path"] or "")`.
- Registry `CREATE TABLE` comment text:
  - `json_path`: append "NULL chỉ với LATEST_DOC_FLAG";
  - `convert_rule`: list the snapshot rules, including `ARRAY_AT` and `LATEST_DOC_FLAG`.

  This changes text only and needs no ALTER.

### 6.2 `ARRAY_AT` code (inside `# BEGIN_RULE_PURE` … `# END_RULE_PURE`)

```python
_MAX_INDEX = 63


def _index(value, label):
    if type(value) is not int or not 0 <= value <= _MAX_INDEX:
        raise ValueError(f"{label} phải là int 0..{_MAX_INDEX}")
    return value


# parse_convert_arg: add "ARRAY_AT" to the first rule set, and add this branch before the JSON_PICK fall-through
    if rule == "ARRAY_AT":
        if set(obj) != {"index", "take"}:
            raise ValueError("ARRAY_AT chỉ có index, take")
        return {"index": _index(obj["index"], "index"), "take": _path(obj["take"], "take")}


def array_at_sql(raw_col, arg):
    """SQL ARRAY_AT. Ví dụ index 0, take displayName -> displayName của phần tử đầu."""
    raw = f"`{raw_col}`"
    elem = f"try_element_at(from_json({raw}, 'array<string>', {_JSON_OPTS}), {arg['index'] + 1})"
    return f"get_json_object({elem}, '$.{arg['take']}')"
```

`index` is 0-based to match the JSON path `[0]` the user named. `take` reuses `_path`, so it is a structural dotted path with no injection surface. `type(True) is not int` rejects booleans.

`assert_rule_sql` gains three cases with `at_arg = parse_convert_arg("ARRAY_AT", '{"index":0,"take":"displayName"}')`:

- `at_hit`: raw `'[{"displayName":"a"},{"displayName":"b"}]'` → `'a'`;
- `at_miss`: raw `'[]'` → `CAST(NULL AS STRING)`;
- `at_bad`: `array_pick_cn_sql` over `'not-array'` → `'true'`.

### 6.3 `LATEST_DOC_FLAG` in the extract

- `build_table_rows`: skip `_raw__` for columns with no paths, both in the `raw_cols` loop and in the `F.col(c.raw_col)` projection. The filter is `if c.paths`. `typed(c)` produces the NULL placeholder.
- `check_config` additions, raised before the lock, for a spec that has a visibility column:
  - the notebook parameter `state_key` must be `"doc"`;
  - the `doc_key_column` column must be derived or single-path, and every one of its paths must start with `_doc.` or `_root.`. Review's `poi_id` is `HASH_MD5_UUID(_doc.source_name, _doc.source_id)`, which satisfies this.

## 7. `is_visible` design

### 7.1 Terms

- **R**: `resolve_latest(spec, applicable)`, unchanged. One row per `review_id`, taken from the latest applicable document of the run that contains it.
- **Anchor**: an applicable VALID document of the run at document level, whatever its `reviews` content.
- **A**: one anchor per `poi_id`, the latest by `(_cdc_ts_ms DESC, _raw_ingested_at DESC, _event_id DESC)`. This order is the same as `resolve_latest` and `doc_state_latest`, and it is equivalent to the MERGE guard, because `_raw_ingested_at = crawled_at`.
- **H**: target rows whose `poi_id` is in A, whose `review_id` is not in R, and whose `is_visible` is true or NULL.

### 7.2 `visibility_anchors(spec, docs, state_df)` (extract, cell `65ab1f40`)

1. Take `kc` = the `doc_key_column` ColumnSpec.
2. Select from `docs` the event columns `_op, _cdc_ts_ms, _cdc_lsn, _raw_ingested_at, _event_id, _crawled_at`, plus:
   - `bad_shape(spec)` as `_vis_bad`;
   - `part_value(p)` aliased to `kc.part_cols`, or `kc.raw_col` for a single path.
3. Compute `_entity_key` with `derived_sql(kc.part_cols, kc.convert_rule)` when `kc.is_derived`, else with `convert_sql(...)`. Drop rows with a NULL key. This is defensive only: VALID documents always have a non-blank `source_name` and `source_id`.
4. Staleness: the same rule as `build_table_rows`. Left-join `state_df`, filtered to this `(trg_schema, trg_tbl)`, on `_entity_key = _st_key`. `_is_stale = _st_key IS NOT NULL AND NOT (event_order() > _st_order)`. Under `full_reload`, `state_df` is None and nothing is stale.
5. Keep the applicable rows. Take `row_number` over `_entity_key` with the order of §7.1, and keep `rn = 1`.
6. Persist with `MEMORY_AND_DISK` and add to `res.cached`.

### 7.3 Source builder (extract, inside `# BEGIN_VIS_PURE` … `# END_VIS_PURE`)

This is a pure text builder. Its only inputs are validated identifiers.

```python
def visibility_source_sql(spec, rows_view, anchors_view, target_view, doc_key):
    keys = spec.key_cols
    vis = next(c.name for c in spec.columns if c.convert_rule == "LATEST_DOC_FLAG")
    q = lambda n: f"`{n}`"
    r_cols, h_cols = [], []
    for c in spec.columns:
        if c.name == vis:
            r_cols.append("CASE WHEN a.a_key IS NULL THEN raise_error('visibility: row without anchor') "
                          "ELSE (r.`_cdc_ts_ms` = a.a_ts AND r.`_raw_ingested_at` <=> a.a_ing "
                          f"AND r.`_event_id` = a.a_eid) END AS {q(vis)}")
            h_cols.append(f"false AS {q(vis)}")
        else:
            r_cols.append(f"r.{q(c.name)}")
            h_cols.append(f"t.{q(c.name)}" if c.name in keys or c.name == doc_key
                          else f"CAST(NULL AS {c.data_type}) AS {q(c.name)}")
    stamp = ["a.a_crawled AS `_crawled_at`", "a.a_eid AS `_event_id`"]
    r_cols += stamp + ["r.`_first_seen_at`", "r.`_last_seen_at`", "false AS `_hide`"]
    h_cols += stamp + ["CAST(NULL AS TIMESTAMP) AS `_first_seen_at`",
                       "CAST(NULL AS TIMESTAMP) AS `_last_seen_at`", "true AS `_hide`"]
    anti = " AND ".join(f"t.{q(k)} = r.{q(k)}" for k in keys)
    return (
        f"WITH a AS (SELECT {q(doc_key)} AS a_key, `_cdc_ts_ms` AS a_ts, `_raw_ingested_at` AS a_ing, "
        f"`_event_id` AS a_eid, `_crawled_at` AS a_crawled FROM {anchors_view})\n"
        f"SELECT {', '.join(r_cols)}\nFROM {rows_view} r LEFT JOIN a ON r.{q(doc_key)} = a.a_key\n"
        f"UNION ALL\n"
        f"SELECT {', '.join(h_cols)}\nFROM {target_view} t JOIN a ON t.{q(doc_key)} = a.a_key\n"
        f"LEFT ANTI JOIN {rows_view} r ON {anti}\n"
        f"WHERE t.{q(vis)} IS NULL OR t.{q(vis)} = true"
    )
```

Views:

- `rows_view`: R, which carries the spec columns and the event and tech columns.
- `anchors_view`: `A.select(F.col("_entity_key").alias(doc_key_column), "_cdc_ts_ms", "_raw_ingested_at", "_event_id", "_crawled_at")`.
- `target_view`: `spark.table(spec.fq_name).select(*keys, doc_key_column, vis)`, de-duplicated by name if `doc_key_column` is a key.

View names are `_vr_/_va_/_vt_<exec8>_<trg_tbl>`. They are unique per thread and dropped in `finally`.

`raise_error` can fire only on a code defect: R and A come from the same `docs` and the same staleness rule. It fires in the count job (§7.5 step 6), before the MERGE.

### 7.4 MERGE (`build_merge_sql`, moved inside `BEGIN_VIS_PURE`)

Specs without a visibility column produce byte-identical SQL to today (local test). With a visibility column:

```sql
MERGE INTO {target} AS t USING {view} AS s ON <keys>
WHEN MATCHED AND s.`_hide` AND <GUARD> THEN UPDATE SET
     t.`V` = s.`V`, t.`_crawled_at` = s.`_crawled_at`, t.`_event_id` = s.`_event_id`, t.`updated_at` = <clock>
WHEN MATCHED AND NOT s.`_hide` AND <GUARD> THEN UPDATE SET <existing update list, includes V>
WHEN NOT MATCHED AND NOT s.`_hide` THEN INSERT <existing column list, includes V>
```

- `<GUARD>` is today's guard text, factored into one local string.
- `merge_into_target(spec, source, ctx)` projects the existing columns, plus `_hide` only for visibility specs.
- There is no `DELETE` and no `NOT MATCHED BY SOURCE`.
- Stamp semantics: rows hidden in a run carry L's stamp, whether they are R-false or H rows. A newer document that contains the review again passes the guard and shows it. An older document is stale by state, and the guard blocks it even if state is bypassed.

### 7.5 `_run_table` flow for a visibility spec

1. Recreated-target guard, then `ensure_target`, which adds `is_visible BOOLEAN` the first time.
2. `rows = build_table_rows(...)`, then stats, cast-null, and element rejects. All unchanged.
3. `A = visibility_anchors(...)`. Count `anchors` and `vis_bad` in one aggregation.
   - If `vis_bad > 0` and not `dry_run`: set `res.cast_null_detail[V] = vis_bad` and raise `CastNullError(f"{V}: {vis_bad} tài liệu mới nhất có {src_object} không phải mảng JSON")`. This applies whatever `cast_null_policy` is.
   - Under `dry_run`, log a WARN instead.
4. Early return:
   - under `dry_run`, after logging the visibility counts;
   - otherwise only when `applicable_rows == 0` **and** `anchors == 0`.
5. `latest = resolve_latest(spec, rows.where("_applicable"))`, persisted. If there are no applicable rows it is empty, which is valid: H can still hide.
6. Register the views and build `source = spark.sql(visibility_source_sql(...))`. Persist it, and count `hidden_from_target` (`_hide`) and `hidden_in_run` (`NOT _hide AND NOT V`) in one aggregation. Drop the views in `finally`.
7. `res.inserted_rows, res.updated_rows = merge_into_target(spec, source, ctx)`.
8. `res.state_df = state_rows(spec, doc_state_latest(A), ctx)`. State advances for every applicable anchor, so a document with empty `reviews` still blocks older documents later.
9. `res.extra["visibility"] = {"anchors": …, "hidden_from_target": …, "hidden_in_run": …, "bad_latest": vis_bad}`.

`presence(spec)` returns `F.lit(True)` for a visibility spec, so `docs_by_table[review]` is the number of VALID documents. `bad_shape` counting in `profile_docs` is unchanged.

### 7.6 Shape and edge cases

| Case | Behavior |
|---|---|
| Latest `reviews` is a non-empty array | Normal |
| Latest `reviews` is `[]`, JSON null, or absent | Every stored review of that POI becomes `false`. It reverses itself on the next crawl that contains them. **UA-VIS1** |
| Latest `reviews` is non-null and not an array | Fail closed (V9). `data` failure, the watermark holds, nothing is hidden |
| An older document is bad-shape | Ignored for visibility (the existing WARN) |
| A latest element lacks author or `publishTime` | The element is rejected as today. The target row it would match is hidden. The reject row records why |
| Author renamed, or `publishTime` changed | The new `review_id` is inserted as true. The old one becomes false |
| Two documents share the order triple | Both count as latest, and their reviews are true |

## 8. Ordering and transaction boundaries

The run framework is unchanged: checks and self-checks → lock → pin snapshot → one wave → commit (state → rejects → table log) → watermark → release.

Per table there is exactly one target commit, the MERGE. For review, R and H go into the same MERGE, so no state exists in which new rows are visible but stale rows are not yet hidden.

Config and schema changes:

- C1: 3P `seed_registry`. One Delta commit, `replaceWhere` by source.
- C2: `ADD COLUMNS` on contact, media, and review. Each is issued by `ensure_target` in the first non-dry run, before that table's MERGE. These are three independent commits.

Partial states:

| State | Behavior |
|---|---|
| Registry seeded, code not deployed | Old lib: `convert_rule không hỗ trợ` for `ARRAY_AT` and `LATEST_DOC_FLAG`, plus the empty `json_path` error. `ConfigError` before the lock. Fail closed |
| Code deployed, registry not seeded | The extract reads `normalized_payload` for the existing 52 columns. There is no visibility spec, and the MERGE SQL is unchanged. Safe only after P9 passes, which is why P9 precedes deploy (§13.2) |
| Columns added, backfill not yet run | Incremental runs fill the new columns only for anchored POIs. Other rows stay NULL. Gold is disabled. The backfill converges |

## 9. Idempotency, concurrency, retry and recovery

Idempotency:

- An identical `full_reload` reproduces R. H is empty, because hidden rows are already false.
  - `inserted_rows = 0`, and `hidden_from_target = 0`.
  - `updated_rows = |R|`: equal stamps still update, as today.
  - Values are identical.
- An incremental re-run after success is `NO_DATA`.
- A crash after the MERGE and before the state commit reprocesses the same documents with the same R. H has shrunk by the rows already hidden. The final state is the same.
- `process_with_retry` recomputes H from the current target. This is idempotent.
- `ARRAY_AT` and the source switch are pure functions of bronze.

Determinism: the anchor order, the `resolve_latest` order, and the SQL column order are fixed. `UNION ALL` order does not matter (V6).

Concurrency:

- One writer thread per table (I9). The target projection and the MERGE run on the same thread with no writer in between.
- An OPTIMIZE or auto-compaction conflict is retried by the existing `with_retry`.
- The source lock prevents overlapping 3P runs.
- Partner has a separate lock, state partition, and tables.

Recovery:

| Failure | Action |
|---|---|
| Review FAILED, transient | `full_reload = True, table_filter = slv_3p_poi_review` |
| `CastNullError` on `is_visible` (bad-shape latest) | `data` failure. Run counts-only probes; the user decides. Never bypass with WARN, because the policy does not apply to this check |
| `CastNullError` on `photographer` (`authorAttributions` not an array) | `data` failure. Same route. `WARN` is allowed only by a user decision |
| `ConfigError` from `assert_rule_sql` or `assert_visibility_sql` | `code` failure. Nothing has been read or written |
| `ConfigError` from `check_config` (`state_key = row`, or a bad doc key) | Fix the parameter or the registry |
| `raise_error('visibility: row without anchor')` | `code` failure. The MERGE did not commit |
| Recreated-target guard | `full_reload` (unchanged) |

## 10. Partial failures

| Failure point | Durable effect | Behavior |
|---|---|---|
| P9 fails | None, because it is read only | STOP. User decision (§13.2 step 2) |
| Seed done, deploy pending | Registry ahead of code | Old code fails closed before the lock |
| `ADD COLUMNS` done, MERGE failed | Column exists, NULL | Retry or `full_reload` that table |
| Backfill: one table FAILED | Others committed. State only for SUCCESS tables. Watermark untouched (`table_filter`) | Re-run with `table_filter` set to the failed table |
| Crash between MERGE and state commit | Target ahead of state | Reprocess, which is idempotent |
| External incremental run between seed and backfill | Mixed NULL and filled values | The backfill converges. Acceptance requires 0 NULL |
| Parity check fails after the backfill | Silver differs from baseline | STOP. R1, then `full_reload` (§13.3). Classify the cause |

## 11. Observability

### 11.1 Exit JSON, logs, control tables

- `extra.visibility = {trg_tbl: {anchors, hidden_from_target, hidden_in_run, bad_latest}}`, assembled in `process_run` from `TableResult.extra`. The new lib field `extra: dict = field(default_factory=dict)` is appended last, so partner is unaffected.
- Per-table INFO line: `visibility anchors=… hidden_from_target=… hidden_in_run=…`.
- Self-check log lines: `rule self-check PASS` (now includes `ARRAY_AT`) and `visibility SQL self-check PASS`.
- `cast_null` can list `photographer` (non-array `authorAttributions`), or `is_visible` on a bad-shape latest document.
- `docs_by_table[slv_3p_poi_review]` now counts VALID documents. This is a documented behavior change.
- `ctrl_log_table_run.updated_rows` includes hide updates.
- `ctrl_cdc_reject`, a one-time effect: document-level reject hashes include the payload text, and element hashes include the element text. Items already rejected under `raw_payload` get new `event_hash` values under `normalized_payload`. Photo elements also differ because they now carry `blob_url`. Old reject rows stay unresolved and are not modified. The runbook records the 3P reject count before and after, and states that the difference is expected.

### 11.2 Operational queries

- `SELECT is_visible, count(*) FROM lh_vv_silver.dbo.slv_3p_poi_review GROUP BY 1`
- The §16.3 oracles.

### 11.3 Consumer impact (for the gold follow-up; no change here)

- `NB_ENR_POI_REVIEW` and `NB_ENR_POI_INFO` do not filter `is_visible`. When 15P resumes, the gold task must decide whether to filter `is_visible = true`. Hidden rows accumulate, because `reviews[]` is a short window.
- `phone`, `blob_url`, and `photographer` have no gold reader today.

## 12. Security and data handling

- `photographer` is a contributor display name, which is personal data. This is the same class as `slv_3p_poi_review.author_name`. No author URI or photo URI is stored.
- `blob_url` is a storage URL produced by the collector. It is the first URL-to-storage column in silver. Whether it embeds a credential (for example a SAS token) is not known. P9 adds a counts-only check: the number of non-null `blob_url` values containing `sig=` or `?`. If the count is non-zero, STOP before the write. Storing a signed URL is a user and security decision. No URL value is printed.
- `phone` is the business phone of a listing. The old normalized silver held this class of data.
- Probe and acceptance outputs are counts or key names only. They contain no names, text, URLs, or phone numbers, and at most 50 rows.
- The DEV synthetic test row has NULL business columns and is deleted afterwards.
- All generated SQL uses validated identifiers. `convert_arg` values pass `_index` and `_path`.

## 13. Rollout (DEV), rollback, and forward recovery

### 13.1 Preconditions

- Architecture `PASS`.
- Local verification `PASS`.
- Reviewers and `risk-gate` `PASS`.
- UA-VIS1 recorded in `decision.md`.
- `PL_VV_TRANS_SLV_TO_ENR_15P` still disabled.

### 13.2 Steps (Main writes the Vietnamese runbook in this order)

1. **Baseline.** First run one normal incremental with the old code, so silver is current. Then record:
   - the Delta version and row count of all nine `slv_3p_*` tables;
   - the 3P watermark row;
   - `ctrl_cdc_state` counts per 3P table;
   - the 3P `ctrl_cdc_reject` count.
2. **P9 source parity (read-only, §17).** **STOP** unless:
   - `norm_blank_when_raw_ok = 0`;
   - `top_mismatch_docs = 0`;
   - `photo_size_mismatch_docs = 0`;
   - `photo_elem_mismatch = 0`;
   - `blob_signed = 0`.

   If any is non-zero, report the counts and the mismatching key names to the user. The user decides.
3. **Optional:** pause the 3P trigger, or hold the manual lock from the parent pattern and release it before each run. Correctness does not depend on this; the parity check is stamp-based.
4. **Deploy:** `NB_LIB_EXTRACT_RAWDATA`, then `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, then `NB_CREATE_DDL`.
5. **Seed:** run only the 3P seed cell, then `show_registry`. Expect:
   - 9 tables and 56 columns;
   - 0 inactive;
   - 11 non-null `convert_arg`;
   - 1 NULL `json_path`.

   Do not reseed partner.
6. **Partner regression:** run the partner extract with `dry_run = True`. Pass means no `ConfigError` and an unchanged table count.
7. **3P dry run:** `dry_run = True, full_reload = True, allow_full_scan = True`. Pass means all of the following:
   - both self-checks PASS;
   - no `ConfigError`;
   - `cast_null` empty and `bad_shape` empty;
   - `extra.visibility.slv_3p_poi_review.bad_latest = 0`;
   - `docs_by_table[slv_3p_poi_review]` = VALID documents;
   - `ensure_target` notes add exactly `phone` (contact), `blob_url` and `photographer` (media), and `is_visible` (review), and nothing else.
8. **Backfill:** `full_reload = True, allow_full_scan = True, max_retries = 1`, with `table_filter` set to all nine 3P tables (`slv_3p_poi, slv_3p_poi_address, slv_3p_poi_contact, slv_3p_poi_price, slv_3p_poi_opening_hours, slv_3p_poi_rating, slv_3p_poi_amenity, slv_3p_poi_review, slv_3p_poi_media`).

   All nine are included because the source switch touches every table. One reload proves parity end to end against the baseline. The cost at DEV volume is negligible.
9. **Idempotency:** run the same backfill again. Pass means `inserted_rows = 0` on all tables and `hidden_from_target = 0`. Then run one normal incremental, which must be SUCCESS or NO_DATA.
10. **DEV-only hide/show proof** (DEV data may not contain a natural hide):
    1. Insert one synthetic review row:
       - `review_id = sha2('vis-selfcheck-<yyyymmdd>', 256)`;
       - an existing `poi_id`;
       - NULL business columns;
       - `is_visible = true`;
       - `_crawled_at = TIMESTAMP'2000-01-01 00:00:00'`, `_event_id = 'vis-selfcheck'`;
       - `_first_seen_at` and `_last_seen_at` set to that same timestamp;
       - `created_at` and `updated_at` = `current_timestamp()`.
    2. Update one real row to `is_visible = false` with the same 2000-01-01 stamp. Record its key.
    3. Run `full_reload` with `table_filter = slv_3p_poi_review`.
    4. Pass means:
       - the synthetic row is `false`, its `_crawled_at` equals the POI's latest bronze `crawled_at`, and its business columns and `_last_seen_at` are unchanged;
       - the real row is `true` with its latest stamp;
       - every other row is unchanged against step 9.
    5. Delete the synthetic row by its key. This is a manual DEV cleanup, not extract behavior.
    6. Run the review `full_reload` again, and require 0 differences against step 9.
11. **Acceptance (§16.3).** On any failure, STOP. Use R1 or R2, or ask the user. Never patch silver by hand outside step 10.
12. Gold stays disabled. Record this in the runbook.

### 13.3 Rollback

- **R1 (code and config, non-destructive):**
  1. Reseed the 3P registry from the previous `NB_CREATE_DDL` revision (52 rows).
  2. Redeploy the previous lib and extract, which read `raw_payload`.
  3. Run `full_reload` with `table_filter` set to the nine tables to restore values derived from `raw_payload`.

  The physical columns `phone`, `blob_url`, `photographer`, and `is_visible` remain. Their values are frozen, and inserts write NULL because the MERGE lists columns explicitly. No current reader uses them.
- **R2 (full physical revert):**
  1. Hold the lock.
  2. Apply R1 steps 1–2.
  3. `DROP TABLE` contact, media, and review, one statement per cell.
  4. Release the lock.
  5. Run `full_reload` with `table_filter` set to those three tables, using the old code. This rebuilds them from bronze (I8).

  Gold is disabled. `ctrl_cdc_state` stays valid, because `full_reload` ignores state for reading.
- Gold and `ctrl_cdc_reject` are never rolled back by this task.

### 13.4 Forward recovery

Follow §9. Never move the watermark or state by hand. Visibility, `ARRAY_AT`, and the source switch are all pure functions of bronze plus the target key set, so a `full_reload` always recomputes them after a fix. Classify each failure as `code` or `data` before re-running.

### 13.5 Prod gate

Run these read-only probes on prod before cutover:

- the parent P1–P5;
- P7 (blob key coverage, and the `authorAttributions` size histogram);
- P8 (§17);
- P9 (§17).

Pass criteria:

- P9 zeros, as in step 2;
- P8 non-array latest = 0.

The user acknowledges the expected `is_visible = false` volume, and the share of `authorAttributions` arrays with size > 1, where index 0 is taken.

## 14. Alternatives and trade-offs

1. **Photographer element pick.**
   - (a) New generic rule `ARRAY_AT {index, take}`. **Selected:**
     - registry-driven;
     - reuses the `ARRAY_PICK` parsing, cast-null, and self-check pattern;
     - a single-part structural path, so no path-grammar change;
     - partner-safe, because it is snapshot-only.
   - (b) Allow `[n]` in `JSON_PATH_RE`. Rejected:
     - the regex is shared with partner CDC, `src_object`, and `align_path` validation;
     - `path_value`, `elem_fields`, `top_fields`, the `profile_docs` heads, and the forbidden scan all split on `.`, and `getField("authorAttributions[0]")` fails;
     - large blast radius for one column.
   - (c) Add an optional `index` to `ARRAY_PICK`. Rejected: it overloads a rule whose argument grammar is exact (`{match, values, take}`) and that 7 live address columns depend on.
   - (d) Hard-code in the extract. Prohibited (V8).
2. **Source switch verification.**
   - Read-only P9 before deploy, plus a stamp-based parity check after the backfill. **Selected:** a premise failure costs nothing durable, and the post-write check catches what P9's text comparison cannot (extract semantics).
   - Post-write parity only. Rejected: a wrong premise would land in silver first.
   - Read both columns and take a per-path fallback. Rejected: the user chose a single source, and it would double the parse cost.
3. **Visibility mechanism.**
   - Hide rows in the MERGE source, with a multi-clause MERGE. **Selected:** one atomic commit, no delete, guard-protected, self-checked.
   - `WHEN NOT MATCHED BY SOURCE … UPDATE`. Rejected: it cannot restrict to POIs anchored in this run without a subquery, and without that it would hide every POI not crawled in the run.
   - A separate UPDATE after the MERGE. Rejected: two commits, and a crash window.
   - Compute visibility in gold or L2 at read time. Rejected: Q-VIS asks for a stored column.
   - Delete and reinsert a POI's reviews. Rejected: physical delete is forbidden.
4. **Stamp on hidden rows.** Move it to L. **Selected:** it blocks a re-show by older documents even without state. Keeping the old stamp would make correctness depend only on state.
5. **Empty, null, or absent latest `reviews`.** Hide all, the literal Q-VIS reading, pending UA-VIS1. The alternative, "unknown, change nothing", would be a new user decision; only §7.6 and self-check case 7 would change.
6. **Bad-shape latest document.** Fail closed. **Selected.** Skipping silently, or hiding everything, are both rejected.
7. **Schema change.** `ensure_target` `ADD COLUMNS` plus `full_reload`. **Selected:** non-destructive, and time travel is the baseline. The cost is that new columns sit physically after the tech columns; readers use names. Drop and recreate was rejected as destructive.
8. **Backfill scope.** All nine tables. **Selected:** the switch affects every table, and this gives one parity proof. Three tables only would leave the switch on the other six unverified until organic incremental runs.

## 15. Implementation plan (Main)

1. **`notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`**
   - §6 constants: `ARG_RULES`, `SNAPSHOT_ONLY_RULES`, and `NO_PATH_RULES` (§6.1).
   - `BEGIN_RULE_PURE`:
     - `_MAX_INDEX` and `_index`;
     - `parse_convert_arg` with the `ARRAY_AT` branch;
     - `array_at_sql` (§6.2).
   - `convert_sql`, `cast_null_sql`, and `assert_rule_sql`: three cases.
   - `ColumnSpec`: `paths`, `can_cast_null`, `is_visibility`.
   - `TableResult.extra`.
   - `build_table_specs`: the §6.1 matrix.
   - Markdown:
     - §1 `json_path` table: NULL only with `LATEST_DOC_FLAG`;
     - the rule table: `ARRAY_AT` and `LATEST_DOC_FLAG`;
     - a header change-log row.
2. **`notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`**
   - Constants: `RAW_PAYLOAD = "normalized_payload"`, plus the markdown.
   - `presence`.
   - `build_table_rows`: skip columns with no paths.
   - `visibility_anchors`.
   - `BEGIN_VIS_PURE` block: `visibility_source_sql` and `build_merge_sql`.
   - `merge_into_target`.
   - `_run_table` (§7.5).
   - `check_config`.
   - `assert_visibility_sql`, called in `run_extract` after `assert_rule_sql` and only when a visibility spec is configured. Its 9 cases are listed in §16.2.
   - `process_run`: `extra.visibility`.
   - Markdown sections B and C: the "Bảng con chỉ upsert" line becomes "review: soft hide qua `is_visible`".
3. **`notebooks/NB_CREATE_DDL.ipynb`**
   - `KNOWN_RULES`.
   - `REGISTRY_SCHEMA`.
   - `flatten_table_configs`.
   - `validate_rows`.
   - `TABLE_CONFIGS_3P`: the 4 rows and the header.
   - Seed cell comment.
   - Registry DDL comment text.
4. **Tests.** Scope expansion first (§1). See §16.1.
5. **Docs** (Vietnamese, existing style):
   - extract context: source column, §3 delete row → soft hide, functions;
   - lib context: rules and validation;
   - `CTRL_TABLES_CONTEXT`: nullable `json_path`, 56 columns, the new rules;
   - `01_DATA_MODEL`: 3P L1 columns;
   - `3p-google/README`: source column line.
6. **`decision.md`** (Vietnamese). Record:
   - the rule names behind "không có";
   - `ARRAY_AT` with index 0;
   - stamp semantics;
   - bad-shape fail-closed;
   - the P9 gate;
   - the one-time reject-hash effect;
   - the backfill of all nine tables;
   - UA-VIS1 when the user answers.

   **`runtime-runbook.md`** (Vietnamese): §13 and §16.3.
7. **`task-state.yaml`**:
   - scope expansion;
   - `architecture: pass`;
   - `specialist_review` required;
   - reviewers: `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`, `risk-gate`;
   - `fabric-pipeline-reviewer` is not needed, because no pipeline JSON changes.

## 16. Verification

### 16.1 Local (`python -m pytest tests`, then `python scripts/vv.py verify 20261014-3p-raw-payload-field-corrections`)

`tests/test_3p_l1_contract.py`:

- `EXPECTED`: contact 4, media 8, review 8. `test_registry_shape` totals 56 columns with 0 inactive.
- `test_paths_are_structural` skips `spec["path"] is None`.
- `test_extract_notebook_has_no_language_contract` asserts `RAW_PAYLOAD    = "normalized_payload"` and that `"raw_payload"` does not appear in the code cells. Comments that mention history are allowed only in markdown.
- New `test_corrected_columns`:
  - `phone.path == "nationalPhoneNumber"` and `NONE`;
  - `blob_url.path == "blob_url"` with no rule (so `NONE`);
  - `photographer`: path `authorAttributions`, rule `ARRAY_AT`, arg `{"index": 0, "take": "displayName"}`;
  - `is_visible`: path `None`, type `boolean`, rule `LATEST_DOC_FLAG`;
  - each is the last column of its table.

`tests/test_3p_raw_rules.py`:

- `test_array_at_arg`:
  - accepts `{"index":0,"take":"displayName"}`;
  - rejects a missing `take`, an extra key, `index` -1, `index` 64, `index` `true`, `index` `"0"`, and `take` `"a;b"`;
  - `parse_convert_arg("NONE", …)` with an arg still raises.
- `test_array_at_sql`: the SQL contains `try_element_at(` and `, 1)` for index 0, and `'$.displayName'`.

`tests/test_3p_visibility_sql.py` (new) executes the `BEGIN_VIS_PURE` block with injected `UTC_TS_RE`, `MIN_TS`, `SNAPSHOT_TECH_COLUMNS`, `ConfigError`, and lightweight spec stubs. It covers:

- `test_source_sql_shape`: `LEFT ANTI JOIN`, `raise_error`, `true AS `_hide``, `IS NULL OR`, and the same column count on both sides of `UNION ALL`;
- `test_merge_hide_clause_first`: the `_hide` clause precedes the full update, and the INSERT is conditioned on `NOT s.`_hide``;
- `test_merge_no_delete`: neither `DELETE` nor `NOT MATCHED BY SOURCE` appears;
- `test_merge_non_visibility_unchanged`: the SQL for a spec without the flag equals a golden string captured from today's builder.

Lib validation is not pure-testable today, because `build_table_specs` lives outside a pure block. It is covered by the runtime dry run (§13.2 step 7) and by the `NB_CREATE_DDL` `validate_rows` logic. Main may add an exec-able pure block if that is cheap; it is not required.

### 16.2 Runtime self-checks

- `assert_rule_sql`: adds `at_hit`, `at_miss`, and `at_bad`.
- `assert_visibility_sql`: generated temp views over literals, with no Delta write. It raises `ConfigError` on a mismatch. Cases:
  1. A review in the latest document → true, stamp L.
  2. A review only in an older document of the run → false, stamp L, with the older document's values.
  3. A target-only review of an anchored POI with true → H row, false, stamp L.
  4. As case 3, with NULL → H row.
  5. As case 3, with false → no row.
  6. A target row of an unanchored POI → no row.
  7. Latest `reviews` empty → every target row of that POI is in H.
  8. Equal order triples → both true.
  9. A resolved row without an anchor → `raise_error`, caught and asserted.

### 16.3 DEV acceptance (counts only; in the runbook)

1. All nine tables are SUCCESS in both backfill runs. The second run has `inserted_rows = 0`. The incremental run is SUCCESS or NO_DATA.
2. Keys are unique in every table. For each table, `count` ≥ baseline `count`; keys present only in the baseline must be 0, because nothing is deleted.
3. **Parity (S2)**, per table, with `cols` = the baseline schema columns minus `updated_at`:

```sql
SELECT count(*) AS same_stamp_rows,
       sum(CASE WHEN NOT (<n.c <=> o.c AND … for every c in cols>) THEN 1 ELSE 0 END) AS diffs
FROM {tbl} n JOIN {tbl} VERSION AS OF {baseline_version} o ON <n.k = o.k for keys>
WHERE n.`_crawled_at` <=> o.`_crawled_at` AND n.`_event_id` <=> o.`_event_id`
```

   Pass: `diffs = 0` on all nine tables. Also report the count of rows whose stamp changed. Expect 0 outside review hides and new bronze documents.
4. **Phone oracle:** the latest VALID document per `poi_id` (CTE `l` below). Count rows where `NOT (c.phone <=> get_json_object(l.n, '$.nationalPhoneNumber'))`. Must be 0.
5. **Media oracle** (`blob_url` and `photographer`):

```sql
WITH d AS (
  SELECT source_name, source_id, crawled_at, CAST(event_id AS STRING) AS eid, normalized_payload AS n
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'google' AND normalized_payload IS NOT NULL AND trim(normalized_payload) <> ''
    AND crawled_at IS NOT NULL AND trim(source_id) <> ''),
e AS (
  SELECT sha2(concat_ws('|', trim(source_name), trim(source_id), trim(get_json_object(x.e, '$.name'))), 256) AS k,
         crawled_at, eid, x.pos,
         get_json_object(x.e, '$.blob_url') AS blob_url,
         get_json_object(try_element_at(from_json(get_json_object(x.e, '$.authorAttributions'), 'array<string>'), 1),
                         '$.displayName') AS photographer
  FROM d LATERAL VIEW posexplode(from_json(get_json_object(n, '$.photos'), 'array<string>')) x AS pos, e),
l AS (SELECT * FROM (SELECT e.*, row_number() OVER (PARTITION BY k ORDER BY crawled_at DESC, eid DESC, pos ASC) AS rn
                     FROM e WHERE k IS NOT NULL) WHERE rn = 1)
SELECT count(*) AS media_rows,
       sum(CASE WHEN l.k IS NULL THEN 1 ELSE 0 END) AS no_oracle,
       sum(CASE WHEN NOT (s.blob_url <=> l.blob_url) THEN 1 ELSE 0 END) AS blob_diff,
       sum(CASE WHEN NOT (s.photographer <=> l.photographer) THEN 1 ELSE 0 END) AS photographer_diff,
       sum(CASE WHEN s.blob_url IS NOT NULL THEN 1 ELSE 0 END) AS blob_nonnull,
       sum(CASE WHEN s.photographer IS NULL THEN 1 ELSE 0 END) AS photographer_null
FROM lh_vv_silver.dbo.slv_3p_poi_media s LEFT JOIN l ON s.media_dedup_key = l.k
```

   Pass: `no_oracle = blob_diff = photographer_diff = 0`. Report `blob_nonnull` and `photographer_null`. P7 implies `photographer_null = 0`.
6. **Review visibility oracle:**

```sql
WITH d AS (
  SELECT regexp_replace(md5(concat(source_name, source_id)), '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5') AS poi_id,
         source_name, source_id, crawled_at, CAST(event_id AS STRING) AS eid, normalized_payload AS n
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'google' AND normalized_payload IS NOT NULL AND trim(normalized_payload) <> ''
    AND crawled_at IS NOT NULL AND trim(source_id) <> ''),
l AS (SELECT * FROM (SELECT d.*, row_number() OVER (PARTITION BY poi_id ORDER BY crawled_at DESC, eid DESC) AS rn FROM d) WHERE rn = 1),
lr AS (
  SELECT DISTINCT sha2(concat(l.source_name, l.source_id,
           get_json_object(x.e, '$.authorAttribution.displayName'), get_json_object(x.e, '$.publishTime')), 256) AS review_id
  FROM l LATERAL VIEW explode(from_json(get_json_object(l.n, '$.reviews'), 'array<string>')) x AS e)
SELECT sum(CASE WHEN lr.review_id IS NULL AND s.is_visible THEN 1 ELSE 0 END)          AS should_be_false,
       sum(CASE WHEN lr.review_id IS NOT NULL AND NOT s.is_visible THEN 1 ELSE 0 END)  AS should_be_true,
       sum(CASE WHEN s.is_visible IS NULL THEN 1 ELSE 0 END)                           AS null_rows,
       sum(CASE WHEN NOT s.is_visible THEN 1 ELSE 0 END)                               AS false_rows
FROM lh_vv_silver.dbo.slv_3p_poi_review s LEFT JOIN lr ON s.review_id = lr.review_id
```

   Pass: `should_be_false = should_be_true = null_rows = 0`. Report `false_rows`.
7. §13.2 step 10 passes and is cleaned up.
8. Reject delta: the 3P `ctrl_cdc_reject` count before and after is recorded. Any increase is limited to the item kinds named in §11.1.

### 16.4 Crash check

1. Cancel the review `full_reload` after the wave starts.
2. Re-run it.
3. Pass: the same final counts and oracle results, and state not regressed.

### 16.5 Reviewers

| Reviewer | Focus |
|---|---|
| `state-correctness-reviewer` | S1, S2, V1–V9, stamp semantics, anchor-based state, crash and retry timelines, partial deploy |
| `sql-data-reviewer` | `ARRAY_AT` SQL, `visibility_source_sql`, MERGE clauses, registry rows, the P9 and oracle queries |
| `spark-runtime-reviewer` | The extra target scan, persist and unpersist, temp-view naming per thread, `raise_error` timing, backfill cost |
| `risk-gate` | UA-VIS1, the P9 outcome, `blob_url` signed-URL handling, the gold note, the prod gate |

## 17. Runtime probes (not architecture blockers)

### P9: `normalized_payload` parity (DEV before deploy; prod before cutover)

- Read only. Output: `evidence/results/P9_payload_parity.md`, counts and key names only.
- Blocks: the go/no-go for §13.2 step 4 (deploy) and for the prod cutover.

```sql
WITH b AS (
  SELECT raw_payload AS r, normalized_payload AS n
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'google'),
p AS (
  SELECT r, n,
         from_json(r, 'map<string,string>') AS mr, from_json(n, 'map<string,string>') AS mn,
         from_json(get_json_object(r, '$.photos'), 'array<string>') AS rp,
         from_json(get_json_object(n, '$.photos'), 'array<string>') AS np
  FROM b)
SELECT count(*) AS docs,
  sum(CASE WHEN (n IS NULL OR trim(n) = '') AND r IS NOT NULL AND trim(r) <> '' THEN 1 ELSE 0 END) AS norm_blank_when_raw_ok,
  sum(CASE WHEN NOT (array_sort(map_entries(map_filter(mr, (k, v) -> k <> 'photos')))
                 <=> array_sort(map_entries(map_filter(mn, (k, v) -> k <> 'photos')))) THEN 1 ELSE 0 END) AS top_mismatch_docs,
  sum(CASE WHEN NOT (size(rp) <=> size(np)) THEN 1 ELSE 0 END) AS photo_size_mismatch_docs,
  sum(size(filter(sequence(1, greatest(size(np), 1)), i -> i <= size(np) AND NOT (
        array_sort(map_entries(from_json(try_element_at(rp, i), 'map<string,string>')))
        <=> array_sort(map_entries(map_filter(from_json(try_element_at(np, i), 'map<string,string>'), (k, v) -> k <> 'blob_url'))))))) AS photo_elem_mismatch,
  sum(size(filter(coalesce(np, array()), e -> NOT array_contains(map_keys(from_json(e, 'map<string,string>')), 'blob_url')))) AS photo_no_blob_key,
  sum(size(filter(coalesce(np, array()), e -> get_json_object(e, '$.blob_url') RLIKE '[?]|sig='))) AS blob_signed
FROM p
```

Second query, run only when `top_mismatch_docs > 0`: key names and counts, at most 50 rows.

```sql
SELECT k, count(*) AS docs FROM p LATERAL VIEW explode(array_union(map_keys(mr), map_keys(mn))) x AS k
WHERE k <> 'photos' AND NOT (mr[k] <=> mn[k]) GROUP BY k ORDER BY docs DESC LIMIT 50
```

Re-use the CTEs `b` and `p` from the first query.

Pass criteria: `norm_blank_when_raw_ok`, `top_mismatch_docs`, `photo_size_mismatch_docs`, `photo_elem_mismatch`, and `blob_signed` are all 0.

Nested values compare as compact JSON text, so key order inside nested objects matters. A mismatch caused only by key order is still a STOP for the user, who can accept it after the post-write parity (§16.3 item 3) or ask for a deeper comparison.

### P8: latest review shape (prod gate only)

- Read only, on prod. Output: `evidence/results/P8_review_latest_shape_prod.md`.
- Using CTEs `d` and `l` from §16.3 item 6, count latest documents in each class:
  - `reviews` absent or null;
  - `[]`;
  - non-array: `get_json_object(n,'$.reviews') IS NOT NULL AND from_json(...) IS NULL`;
  - non-empty array.
- Also run the visibility oracle with `lr` anti-joined to the current prod review keys, to give the expected `false_rows`.
- Blocks the prod cutover: the non-array count must be 0, and the user acknowledges the hide volume.

## 18. User acknowledgments before the DEV runtime step

These do not block implementation or review.

- **UA-VIS1:** when the latest document of a POI has `reviews` absent, null, or `[]`, every stored review of that POI becomes `is_visible = false` and is restored by the next crawl that contains it. If the user instead wants "unknown, change nothing", only §7.6 and self-check case 7 change.
- **P9 outcome:** any non-zero count stops the rollout for a user decision.
- **Parent UA1:** 15P stays disabled. The gold task decides whether to filter `is_visible`.
