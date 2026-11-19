RESULT: PASS

## Main brief

### Decision
RESULT: PASS. D-4 B and D-5 override are now recorded, so the design can be built. The keys are already stated in `model-design.md` `## Keys`, so no model change is needed.
- Identity uses a notebook-only override: a synthetic `_doc__poi_source_name`. `IDENTITY_KEY_COLUMNS = ("poi_id", "review_id", "media_dedup_key")`. The registry is unchanged, and a fail-closed guard protects the override.
- D-3: a set of google-owned `poi_id`s skips `sgm` documents as `IGNORED` / `GOOGLE_PRIORITY`. D-5: a takeover flag bypasses the stale filter and the MERGE guard. The run deletes the state of takeover keys before the wave. When there is a takeover, `slv_3p_poi` runs last behind a gate.
- `sources = google,sgm`. Backfill is one `full_reload` run. The only downstream code change is the `sgm`→`google` mapping in `NB_SLV_POI_ENTITY_NON_ENRICH`.

### Invariants Main must preserve
- For bronze names other than `sgm`, derived keys hash the exact bronze value. Existing `google` keys and `source_name` values do not change (V-3).
- For `sgm`, `poi_id`, `review_id`, and `media_dedup_key` hash `'google'` with the exact bronze `source_id` (V-2).
- `slv_3p_poi.source_name` stores the bronze value and is never rewritten from `google` to `sgm`.
- A `VALID` `sgm` document on a google-owned `poi_id` (stored row `google`, or a `VALID` `google` document in the same run) is `IGNORED` / `GOOGLE_PRIORITY`, with no MERGE, state, or reject row.
- A `VALID` `google` document on a stored `sgm` row applies in all tables at any `crawled_at`. Afterwards the state equals the order of the `google` event (V-10).
- When the takeover set `T` is not empty, `slv_3p_poi` runs only after the other tables. A takeover reaches it only if every other table is `SUCCESS` or `NO_DATA` and the run has no `table_filter`.
- The owner snapshot is read with `VERSION AS OF` the version at run start.
- Outside takeover, the existing MERGE guard text, the stale filter, `resolve_latest`, and the lib state stay byte-identical.
- Rerunning the same range, incremental or `full_reload`, inserts 0 rows in all 9 tables (V-5).
- No `sgm` reaches entity, gold, or dictionaries. `sources = google,sgm` is set only in the notebook default and the FL_00 3P activity.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb | cell `e3eb64e4` `sources` | `"google,sgm"`, comment | default includes `sgm` |
| 2 | same | cell `1ccbf8fd` constants | `IDENTITY_SOURCE`, `PRIORITY_SOURCE`, `POI_TABLE`, `IDENTITY_DOC_COL`, `TAKEOVER_DOC_COL`, `SYNTHETIC_DOC_COLS`, `IDENTITY_KEY_COLUMNS` (D-4 B), `IGNORE_REASONS` += `GOOGLE_PRIORITY`, `identity_source`, `identity_path` (doc: Code sketch / Constants) | `sgm` is the only mapped name |
| 3 | same | cell `803f3d1d` `classify_docs` | add `_doc__poi_source_name = identity_source(_doc__source_name)`; rules unchanged | column on every row |
| 4 | same | cell `803f3d1d` new `poi_owner_snapshot`, `apply_source_priority` | doc: Code sketch / Owner snapshot and priority | returns (docs, `takeover_ids`); behavior matches the Ordering table |
| 5 | same | cell `65ab1f40` `build_table_rows` | multi-part `raw_cols` use `part_value(identity_path(c, p))`; `is_stale` adds `& ~_doc__poi_takeover` | the `sgm` keys hash `'google'` |
| 6 | same | cell `65ab1f40` `build_merge_sql`, `merge_into_target` | takeover clause `OR` before the unchanged guard; add the column to `cols` (doc: Code sketch / MERGE guard) | guard text otherwise identical |
| 7 | same | cell `65ab1f40` new `reset_takeover_state` | MERGE `whenMatchedDelete` on `ctrl_cdc_state` with `src_partition_cond` (doc: Code sketch) | deletes only `T` × run specs |
| 8 | same | cell `84cc99f5` `check_config` | I-12 guards (doc: Code sketch / check_config) | a wrong shape raises `ConfigError` before the lock |
| 9 | same | cell `84cc99f5` `process_run` | snapshot, priority, reset before `load_state`, two-phase `run_tables`, gate, counters (doc: Code sketch / Wiring) | counters in exit JSON |
| 10 | same | markdown `266a7442`, `0e22c079`, `e2a3d4ba`, `ed47805a` | rule 2b `GOOGLE_PRIORITY`; takeover bypass and `slv_3p_poi` last; identity; ops (backfill, `table_filter` defers takeover, rollback order) | docs match code |
| 11 | pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json | 3P extract activity `sources` | `"google"` → `"google,sgm"` | CMS `sources` unchanged |
| 12 | notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb | cell `b1entitybuild` `build` after `src = ctx.input("poi")` | `sgm`→`google`, metric `sgm_as_google_rows` (doc: Code sketch / Entity) | entity has no `sgm` |
| 13 | same | cell `b1entitymd` | one line on the effective source | — |
| 14 | docs/context/mapping_gld_srv_poi_info.md | §1.2 `source_name` | `google` includes bronze `sgm` via entity | — |
| 15 | docs/context/mapping_gld_srv_poi_multi_lang.md | §1.2 `source_name` | same note | — |
| 16 | docs/context/mapping_gld_srv_poi_amenity.md | §0 | POIs that originate from `sgm` use the `google` dictionary | — |
| 17 | docs/context/mapping_poi_media_info.md | §1.1 / §1.2 | rows that originate from `sgm` are included; literal `google`; `scraper-` photos stay separate (D-4 B) | — |
| 18 | docs/context/mapping_gld_srv_poi_review.md | `source_name` / `review_id` row | `sgm` reviews hash `google`; exact matches converge (D-4 B) | — |
| 19 | docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md (after scope add) | §4 `sources`, §7 rule table | `google,sgm`; `GOOGLE_PRIORITY`; takeover | — |
| 20 | tests/test_3p_sgm_identity_contract.py (after scope add) | new file | tests listed below | tests pass |
| — | NB_SLV_POI_AMENITY, NB_SLV_POI_MEDIA_INFO, NB_ENR_POI_INFO, NB_GLD_SRV_POI_INFO, NB_CREATE_DDL | — | no edit; verify only | V-7, V-8 pass |

### Order and stop points
1. STOP (scope): triage adds `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` and `tests/test_3p_sgm_identity_contract.py` to `scope.files`.
2. Edits 12–18 (entity and mapping docs). These are a no-op while silver has no `sgm` rows.
3. Edits 1–11, then edits 19 and 20.
4. Run the local tests, then `run-gate`.
5. STOP (runtime evidence): on DEV, run these in order:
   - `dry_run` + `full_reload`. Expect `sgm_valid = 2630`, `google_priority_skipped = 402`, `takeover_poi = 0`.
   - Record `v0` for the 9 tables and `ctrl_cdc_state`.
   - The real `full_reload` run. Expect 2228 `sgm` rows in `slv_3p_poi`.
   - An incremental rerun, then a `full_reload` rerun. Both must show 0 inserts.
   - The downstream nodes, then V-1 to V-9.
6. STOP (user decision): to prove D-5 (V-10 and V-11), you need a DEV fixture with an older `google` bronze event for one `sgm`-only `source_id`. Writing to DEV bronze needs explicit user confirmation. Otherwise, the user accepts static tests plus the first natural takeover as proof.
7. Rollback: revert `sources` to `google` first. Any DELETE of `sgm` rows needs explicit user confirmation.

### Tests and verification
- `python -m pytest tests/test_3p_l1_contract.py tests/test_3p_raw_rules.py tests/test_pipeline_precheck_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_enr_poi_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_3p_visibility_sql.py tests/test_l1_ts_contract.py -q`
- `python -m pytest tests/test_3p_sgm_identity_contract.py -q`. Tests:
  - `test_sources_default_and_fl00_include_sgm`
  - `test_identity_source_only_maps_sgm`
  - `test_identity_key_columns_match_d4b`
  - `test_google_priority_is_ignore_reason`
  - `test_check_config_guards_identity_and_synthetic_cols`
  - `test_registry_key_paths_unchanged`
  - `test_merge_guard_takeover_bypass`
  - `test_stale_filter_excludes_takeover`
  - `test_poi_owner_snapshot_version_pinned`
  - `test_takeover_state_reset_before_load_state`
  - `test_poi_table_last_when_takeover`
  - `test_entity_maps_sgm_to_google_before_filter`
  - `test_no_sgm_dictionary_rows`
- `python scripts/vv.py run-gate 20261119-gsm-as-google-extract`
- DEV runtime V-1 to V-11 (doc: Verification):
  - key uniqueness
  - the `sgm` key formulas
  - `google` rows unchanged against `v0`
  - backfill counts
  - 0 inserts on reruns
  - no `sgm` in entity, gold, or dictionaries
  - no state for skipped `sgm` documents
  - takeover and gate behavior

### Read only if needed
- Status of the previous blocker → why PASS; model-design Conflicts items 1–6.
- Ordering (sets O/G/T, rule table, takeover mechanics, failure-point table) → edits 4–7, 9.
- Alternatives → edits 2–9, 11 (override vs. registry; why the reset and the gate instead of a post-commit overwrite or a rank).
- Code sketch → edits 2, 4, 6, 7, 8, 9, 12.
- Transaction and commit boundaries, Idempotency, Concurrency, Retry and recovery, Partial failure → edits 7 and 9; V-5, V-10, V-11.
- Observability → edits 9 and 12 (counters).
- Rollout, Rollback and forward recovery → stop points 5–7, edit 10 ops note.
- Scope → edits 12–19 and the no-edit row.

# Architecture: 20261119-gsm-as-google-extract

## Status of the previous blocker

The previous run returned `EVIDENCE_REQUIRED` because the `review_id` and `media_dedup_key` formulas for `sgm` events had not been decided. That gap is now closed.

- Probe p2 ran. `evidence/results/p2_sgm_overlap_detail.txt` shows:
  - `NAME` has exactly two values, `google` and `sgm`.
  - `overlap_exact = overlap_trimmed = 402` and `silver_hit = 402`.
  - `sgm_newer = 402`, `equal = 0`, `sgm_only = 2228`.
  - `match_exact = 93` of the 2041 `sgm` reviews. `match_name = 0` and `scraper_named = 2814` for photos.
- The ledger records D-4 B and D-5 override.
- `model-design.md` `## Keys` states the final formulas.

D-5 override changes one part of the previous design. A `google` event that is older than a stored `sgm` row must now be applied, even though the per-table stale filter, the MERGE guard, and the lib state, which never moves backward, would all block it. The `## Ordering` section adds the takeover mechanism. The rest of the previous design stays.

The open items in model-design `## Conflicts and questions` are resolved here and need no model change:

- **Item 1.** The ledger, D-1 to D-5, is the accepted source.
- **Item 2.** A notebook override sets the identity. See `## Alternatives`.
- **Item 3.** Ties are broken by source priority, not by time. See `## Ordering`.
- **Item 4.** No column, type, or nullability changes.
- **Item 5.** Only the entity node reads `slv_3p_poi.source_name`. See `## Scope`.
- **Item 6.** p1 shows `silver_sgm = 0`, so no stored row uses the old key formula.

## Scope

- **`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`**:
  - Admit `sgm` through `sources`.
  - Derive key identity from the effective source. `poi_id`, `review_id`, and `media_dedup_key` hash `'google'` for `sgm` events (D-1, D-4 B).
  - Enforce D-3 with a document-level filter that runs before the table wave.
  - Enforce D-5 with a takeover flag. The flag bypasses the stale filter and the MERGE guard, and the run resets state for the affected keys.
  - When a takeover happens, run `slv_3p_poi` after the other tables, behind a gate.
  - Add fail-closed config guards.
- **`PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json`**: change `sources` on the 3P extract activity from `google` to `google,sgm`. The CMS activity's `sources` stays unchanged.
- **`NB_SLV_POI_ENTITY_NON_ENRICH`**: map `sgm` to `google` on `ctx.input("poi")` before the `GOOGLE` filter at `build`. This is the only downstream code change.
  - The previous run showed that every later consumer reads `source_name` from `slv_poi_entity_non_enrich`: amenity, enr, gold info, and multi-lang.
  - `NB_SLV_POI_MEDIA_INFO` and the review gold write the literal `google`.
  - No other notebook reads `slv_3p_poi.source_name`.
  - The place-type and amenity dictionaries filter `source_name = 'google'` on dictionary rows. The entity rows reaching them are already `google`, so the dictionaries need no change.
- **Mapping docs**: add notes on `sgm` provenance and the effective-source rule.
- **Verify only, no edit**: `NB_SLV_POI_AMENITY`, `NB_SLV_POI_MEDIA_INFO`, `NB_ENR_POI_INFO`, `NB_GLD_SRV_POI_INFO`, and `NB_CREATE_DDL`. Registry rows stay unchanged.
- **Scope gaps**: Main must ask triage to add two files to `scope.files`:
  - `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`. Its §4 `sources` default and its §7 rule table become stale.
  - `tests/test_3p_sgm_identity_contract.py`.

## Non-goals

- No change to registry rows, `json_path`, tables, columns, dictionaries, `NB_LIB_*`, the serving API, or gold column sets and keys.
- No source rank in `ctrl_cdc_state` ordering or in the lib.
- No delete or soft delete of `sgm`-keyed review or media rows left behind after a takeover. D-4 accepts these leftovers.
- No change to how absent and JSON-null keys are handled. `profile_docs` counts a key that is present with a null value as present. p1 shows `absent = 0` for every one of the 35 keys across all 2630 `sgm` rows.

## Invariants

- **I-1.** For any bronze `source_name` other than `sgm`, the derived-key hash input is the exact bronze value, as it is today. Existing `google` `poi_id`, `review_id`, `media_dedup_key`, and `source_name` values do not change.
- **I-2.** For bronze `sgm`, matched case- and space-insensitively:
  - `poi_id = HASH_MD5_UUID('google', source_id)`.
  - `review_id = HASH_SHA256('google', source_id, displayName, publishTime)`.
  - `media_dedup_key = HASH_SHA256_PIPE('google', source_id, name)`.
  - `source_id` is the exact bronze `RAW_DOC_ID` value, never the payload `id`.
- **I-3.** `slv_3p_poi.source_name` stores the bronze value and is never rewritten from `google` to `sgm`.
- **I-4 (D-3).** A `VALID` `sgm` document whose identity `poi_id` is google-owned is `IGNORED` / `GOOGLE_PRIORITY` for all tables. Google-owned means either the stored `slv_3p_poi` row is `google`, or the same run has a `VALID` `google` document for that `poi_id`. The skipped document writes no MERGE, no state row, and no reject row.
- **I-5 (D-5).** A `VALID` `google` document whose `poi_id` has a stored `slv_3p_poi` row with `source_name = sgm` is a takeover document. It is applied in every table regardless of `(crawled_at, event_id)`. After a successful run, `slv_3p_poi.source_name = google`, and `ctrl_cdc_state` holds the order of the `google` event.
- **I-6.** A takeover reaches `slv_3p_poi` only after every other table in the run is `SUCCESS` or `NO_DATA`, and only in runs without `table_filter`. Because of this, `slv_3p_poi` never turns `google` while a child table still holds `sgm` content that a later run could not take over.
- **I-7.** Outside takeover, ordering is unchanged:
  - The stale filter is unchanged.
  - The MERGE guard is unchanged: `(_crawled_at, _event_id)`.
  - `resolve_latest` and `doc_state_latest` are unchanged.
  - The lib `STATE_NOT_OLDER` is unchanged.
- **I-8.** The owner snapshot of `slv_3p_poi` is read with `VERSION AS OF` a version fixed at run start. If a cached frame is recomputed, the flags do not change mid-run.
- **I-9.** Rerunning the same raw range inserts 0 rows in all 9 tables, both incremental and `full_reload`. The rerun's takeover set is empty or identical.
- **I-10.** `slv_poi_entity_non_enrich.source_name` is in `{google, partner}`. No `sgm` value reaches gold. No dictionary row has `source_name = 'sgm'`.
- **I-11.** The notebook default and the FL_00 3P activity both set `sources = google,sgm`. Any other name stays `IGNORED OUT_OF_SCOPE`.
- **I-12.** `check_config` raises `ConfigError` before the lock in these cases:
  - The registry `poi_id` is not `HASH_MD5_UUID` over `_doc.source_name,_doc.source_id`.
  - An identity key column does not start with `_doc.source_name`.
  - `slv_3p_poi` has no single-path `source_name` column.
  - The specs span more than one `trg_schema`.
  - The raw table already has a column named `poi_source_name` or `poi_takeover`.

## State ownership

| State | Owner | Change |
|---|---|---|
| `slv_3p_poi*` rows | extract | `sgm` rows are added. D-3 skip and D-5 takeover are decided once per document, before the wave. |
| `slv_3p_poi.source_name` | extract | The only provenance marker. The takeover gate (I-6) makes it the last thing written. |
| `ctrl_cdc_state` (`src_tbl = brz_3rd_crawler_poi_stream`, `entity_key = poi_id`) | lib `commit_state`, plus the extract `reset_takeover_state` | `sgm` and `google` share one state row per table and `poi_id`. For takeover keys only, the extract deletes those rows before the wave. |
| `ctrl_mng_watermark` | lib `run_controlled` | Unchanged. It advances only on `SUCCESS` / `NO_DATA` for full incremental runs. |
| `ctrl_cdc_reject` | extract `commit` | Unchanged. `GOOGLE_PRIORITY` is not a reject. |
| `slv_poi_entity_non_enrich` and later | transform nodes, `RECOMPUTE` from `VERSION AS OF` | The effective source is applied in entity `build` only. |
| `ctrl_cfg_schema_registry` | `NB_CREATE_DDL` cell 14 | Unchanged |

## Grain and keys

Grain and keys follow `model-design.md` `## Entities and grain` and `## Keys`:

- `slv_3p_poi` and the other `poi_id`-keyed tables have one row per `poi_id`.
- `slv_3p_poi_review` has one row per `review_id`.
- `slv_3p_poi_media` has one row per `media_dedup_key`.
- No column is added.

Under D-4 B, `sgm` reviews converge with `google` reviews only when the hashed strings match exactly. `sgm` photos named `scraper-NN` never converge and stay as separate rows under the shared `poi_id`. D-4 accepts this.

## Ordering

**Per-run sets.** These are computed once, inside `run_controlled`, after the lock and `pin_snapshot`, and before `profile_docs`:

- `O`: the `(poi_id, owner)` pairs from `slv_3p_poi VERSION AS OF v_poi`, where `v_poi` is the latest version at run start. If the table is missing, `O` is empty.
- `Gr`: the identity `poi_id` of every `VALID` `google` document in this run.
- `G` (google-owned) = `{O.owner = google} ∪ Gr`.
- `T` (takeover) = `{O.owner = sgm} ∩ Gr`. It applies only when `takeover_enabled = not ctx.table_filter`. Otherwise `T` is empty.

**Document rules:**

| Case | Result | Ledger |
|---|---|---|
| `sgm` event, stored row `google`, any `crawled_at` | `IGNORED` / `GOOGLE_PRIORITY` | D-3 |
| `sgm` and `google` events in the same run, any order (this covers the 402 on backfill) | `sgm` skipped; `google` follows the normal path, or the takeover path if the stored row is `sgm` | D-3 |
| `google` event, stored row `sgm`, `google` newer, older, or equal | Takeover: applied in all tables; `source_name = google` | D-3, D-5 |
| `google` event, stored row `google` | Unchanged: stale filter, then guard, then `event_id` tie-break | I-7 |
| `sgm` event, stored row `sgm` or none, no `google` in the run | Unchanged ordering. Stored as `sgm` with the I-2 keys. | D-1, D-3 |
| Two `google` documents for one takeover `poi_id` in the run | `resolve_latest` keeps the newest per key, as today | I-7 |

**Ties (model-design Conflicts item 3).** Source priority decides ties, not time. With equal `crawled_at`, an `sgm` event never wins over `google` (D-3), and a `google` event always wins over a stored `sgm` row (D-5).

**Takeover mechanics (D-5).** Each takeover document carries the boolean `_doc__poi_takeover`. `expand_rows` and `build_table_rows` already carry every `_doc__*` column through to the rows.

1. **Stale filter** in `build_table_rows`: `_is_stale` also requires `NOT _doc__poi_takeover`. This keeps `dry_run` accurate.
2. **MERGE guard** in `build_merge_sql`: `WHEN MATCHED AND (s._doc__poi_takeover OR <existing guard>)`. `merge_into_target` adds the column to the source select. The column is not in `UPDATE SET` or `INSERT`.
3. **State reset** with `reset_takeover_state`. Before `load_state`, and only if not `dry_run` and `T` is not empty, the extract deletes `ctrl_cdc_state` rows where:
   - `src_tbl` is this source,
   - `(trg_schema, trg_tbl)` is in the run's specs, and
   - `entity_key` is in `T`.

   Then the lib `commit_state` inserts the order of the `google` event. Without this reset, `STATE_NOT_OLDER` would keep the newer `sgm` order. A later `google` event between the two crawl times would then be marked stale, even though it is newer than the stored `google` row.
4. **Phase order and gate.** If `T` is empty, there is one `run_tables(specs)` call, as today. If `T` is not empty, the run uses two phases:
   - Phase A: `run_tables` over every spec except `slv_3p_poi`.
   - Gate: check whether every phase-A result is `SUCCESS` or `NO_DATA`.
   - Phase B: `run_tables([slv_3p_poi])`. If the gate fails, phase B runs on `docs.where(NOT _doc__poi_takeover)` and records `takeover_deferred = |T|`. If the gate fails and `stop_on_failure` is set, `slv_3p_poi` is appended as `SKIPPED` instead.
   - A failed gate always means the run is `PARTIAL_FAILED`, so the watermark does not advance.

**Why `T` is stable and self-healing across failures.** `slv_3p_poi.source_name` is the only marker of a takeover, and the gate ensures it is written last.

| Failure point | Next run |
|---|---|
| Before or during the state reset | Nothing is written yet; `T` is identical |
| After the reset, before phase B commits | `O` is still `sgm` → `T` is identical. State for `T` is missing, so nothing is marked stale. The flag bypasses the guard. The rewrite produces identical values with 0 inserts. |
| Phase-A table fails | `slv_3p_poi` keeps its `sgm` row → `T` is identical; the watermark does not advance |
| After phase B, before `commit_state` | `O` is `google` → `T` is empty. State for `T` is missing, so the documents are re-read. The normal guard sees an equal `(crawled_at, event_id)` and makes no change. `commit_state` inserts the `google` order. |

**Why `G` only grows.** No path rewrites a `google` row to `sgm` (I-3). Within a run, `Gr` already contains every `poi_id` that the run can turn `google`.

## Transaction and commit boundaries

- `reset_takeover_state` is one Delta MERGE `whenMatchedDelete` on `ctrl_cdc_state`. It is scoped to this source's `src_tbl` partition with `src_partition_cond` and wrapped in lib `with_retry`. It runs under the run's lock, before any table write.
- Each table MERGE is its own Delta commit, as today. When `T` is not empty, `slv_3p_poi` commits last.
- `commit` is unchanged: state, then rejects, then table log. The lib advances the watermark only on `SUCCESS` or `NO_DATA`.
- The `O` read is a version-pinned snapshot (I-8). It is not part of any transaction.

## Idempotency

- **Same range, incremental.** Applied documents are stale against state. `T` is empty because `O` is now `google`. `GOOGLE_PRIORITY` re-labels the same `sgm` documents. Result: 0 inserts.
- **`full_reload` rerun.** There is no state. `T` is empty. The guard sees equal values and updates rows to the same values. Result: 0 inserts. `updated_at` moves, which is today's `full_reload` behavior.
- **Takeover rerun after a partial failure.** The same `T`, the same flagged documents, and the same `resolve_latest` choice produce identical values and 0 inserts.
- **State reset rerun.** Deleting missing rows is a no-op.

## Concurrency

- FL_00 has `concurrency = 1`. The extract lock is on the watermark row. The partner extract writes another `ctrl_cdc_state` partition, and the reset MERGE carries the `src_tbl` partition condition.
- Downstream nodes recompute from `VERSION AS OF` through edge watermarks. While a takeover run is in progress, they can see child tables already taken over while `slv_3p_poi` is still `sgm`. Entity maps `sgm` to `google` anyway, and `poi_id` is shared, so no node sees two rows for one `poi_id`.
- A takeover can move `slv_3p_poi._crawled_at` backward. Downstream nodes read by Delta version, not by `_crawled_at`, so the backward move is invisible to them.

## Retry and recovery

- Per-table `process_with_retry` is unchanged. Flags and `T` are computed once per run. A recomputed cached frame gives the same result because of I-8.
- `CastNullError`, `VersionGapError`, and `SKIPPED_CONCURRENT` behave as today.
- See the failure-point table in `## Ordering` for each crash point.

## Partial failure

- **A phase-A table fails while `T` is not empty.** `slv_3p_poi` writes everything except the takeover documents. The run is `PARTIAL_FAILED` and the watermark holds. The next run redoes the same takeover.
- **A `table_filter` run.** Takeover is disabled. D-3 skipping still applies. `google` documents follow the normal rules. The next full incremental run re-reads the range, because filtered runs never move the watermark, and performs the takeover.
- **A `google` takeover document has no block for a `DOC` table, for example no opening hours.** No row is produced for that table, so the `sgm` row stays. This is today's semantics for a missing block, because there is no delete branch.

## Observability

New extract `out.extra` keys:

| Key | Meaning |
|---|---|
| `sgm_valid` | `VALID` `sgm` documents before the D-3 rule |
| `google_priority_skipped` | `sgm` documents re-labelled `GOOGLE_PRIORITY` |
| `google_owned_stored` | Rows in `O` with owner `google` |
| `google_owned_in_run` | Size of `Gr` |
| `takeover_enabled` | `True` when the run has no `table_filter` |
| `takeover_poi` | Size of `T` |
| `takeover_state_keys` | `|T|` times the number of specs |
| `takeover_deferred` | `|T|` when the gate failed, otherwise 0 |
| `poi_owner_version` | `v_poi` |

`profile.ignored_detail` already splits counts by `source_name`. The entity node adds the metric `sgm_as_google_rows`. The output contains no IDs, names, or text.

## Security

Nothing new: the same lakehouses and the same identities. Probes and logs print aggregates only.

## Alternatives

| Concern | Option | Verdict |
|---|---|---|
| Identity mechanism | **A. Notebook override.** A synthetic `_doc__poi_source_name`. `identity_path` remaps `_doc.source_name` for the columns in `IDENTITY_KEY_COLUMNS`. A shape guard protects it. | **Selected.** One artifact, no change to control data, rollback is a revert. |
| | B. Registry path `_doc.poi_source_name` on 3 keys, with a reseed | Rejected. Needs a live reseed and coupled deploys. An old registry with a new notebook would silently hash `sgm`. |
| | C. New lib rule | Rejected. `NB_LIB_*` is out of scope. |
| D-3 enforcement | **A. Document-level filter before the wave** | **Selected.** Uniform across the 9 tables, writes no state for skipped documents, deterministic on retry. |
| | B. Per-table MERGE guard on `source_name` | Rejected. Child tables have no `source_name` column. |
| D-5 enforcement | **A. Takeover flag, plus pre-wave state reset, plus `slv_3p_poi` last behind the gate** | **Selected.** Applies across all tables, needs no lib change, and recovers on its own (`## Ordering`). |
| | B. A `slv_3p_poi`-only MERGE condition `t.source_name <> 'google'` | Rejected. Child tables would keep `sgm` content behind the guard. The state would also stay ahead. |
| | C. Source rank in the ordering tuple | Rejected. Changes lib state ordering. |
| | D. Unconditional state overwrite after `commit_state` | Rejected. A crash between the two writes leaves the state ahead, with no marker to repair it. |
| | E. Always run `slv_3p_poi` last | Rejected. Serializes every run. The two-phase run happens only when `T` is not empty. |
| Owner snapshot | **A. `VERSION AS OF v_poi`** | **Selected** (I-8) |
| | B. Collect to the driver | Rejected. Grows with the table. |
| Admitting `sgm` | **`sources = google,sgm`** in the notebook and FL_00 | **Selected.** Explicit, and rollback is a one-value change. |
| Backfill | **One `full_reload` run without `table_filter`** (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §10) | **Selected.** The previously `IGNORED` `sgm` rows are behind the watermark. |

## Rollout

1. Scope stop: triage adds the two scope-gap files.
2. Merge the entity change and the mapping docs. This is a no-op while `slv_3p_poi` has no `sgm` rows.
3. Merge the extract and the pipeline JSON. Run the local tests and `run-gate`.
4. DEV preview with `dry_run = True, full_reload = True, allow_full_scan = True`. Expected:
   - `sgm_valid = 2630`
   - `google_priority_skipped = 402`. p1 shows one document per `sgm` `source_id`.
   - `takeover_poi = 0`
   - `cast_null = 0`
   - no new reject reasons
5. Record the Delta version `v0` of the 9 tables and of `ctrl_cdc_state`. Then run the DEV real run with `full_reload = True, allow_full_scan = True, max_retries = 1`. Expected: `slv_3p_poi` inserts 2228 rows with `source_name = 'sgm'`, plus any new `google` data.
6. DEV incremental rerun with no new data, then a second `full_reload` rerun. Both must show 0 inserts.
7. Run the downstream nodes in order: entity, then amenity and media, then enr, then gold. Run V-1 to V-11.
8. Production only after the DEV runtime gate passes, with steps 4 to 6.

## Rollback and forward recovery

- **Stop intake.** Set `sources = google` in the pipeline JSON first, then in the notebook default. New `sgm` events become `OUT_OF_SCOPE` again. Rows already written stay; they are valid rows under the `google` identity. The takeover logic keeps working for `google` events.
- **Notebook revert.** Revert `sources` first, or in the same deploy. If the notebook is reverted while `sgm` rows remain, D-3 and D-5 are no longer enforced. Older `google` events go stale against `sgm` rows again.
- **Remove `sgm` data.** This is destructive and needs explicit user confirmation.
  - Take the set `P` of `poi_id` values in `slv_3p_poi` where `source_name = 'sgm'`. Delete those rows from all 9 tables. Delete the `ctrl_cdc_state` rows of this `src_tbl` whose `entity_key` is in `P`.
  - Leftover `sgm` child rows on POIs that `google` took over are found by matching child `_event_id` to bronze `RAW_EVENT_ID` where `source_name = 'sgm'`.
  - Then let the `RECOMPUTE` nodes run.

## Implementation plan

Anchors are the cell ids. Code is in `## Code sketch`.

1. Extract `e3eb64e4`: set `sources = "google,sgm"` and update the comment.
2. Extract `1ccbf8fd`: add the constants and the helpers `identity_source` and `identity_path`.
3. Extract `803f3d1d` `classify_docs`: after the first select, add `_doc__poi_source_name = identity_source(_doc__source_name)`. The rules stay the same.
4. Extract `803f3d1d`: add `poi_owner_snapshot(specs)` and `apply_source_priority(classified, owners, takeover_enabled)`.
5. Extract `65ab1f40` `build_table_rows`: multi-part `raw_cols` use `part_value(identity_path(c, p))`. `is_stale` is combined with `& ~F.col("_doc__poi_takeover")`.
6. Extract `65ab1f40` `build_merge_sql`: put the takeover clause before the guard. `merge_into_target` adds `_doc__poi_takeover` to `cols`.
7. Extract `65ab1f40`: add `reset_takeover_state(takeover_ids, specs, ctx)`.
8. Extract `84cc99f5` `check_config`: add the I-12 guards.
9. Extract `84cc99f5` `process_run`: wire the snapshot, the priority rule, the reset, the two-phase `run_tables`, the gate, and the counters.
10. Extract markdown:
    - `266a7442`: rule 2b, `GOOGLE_PRIORITY`.
    - `0e22c079`: the takeover bypass of the stale filter and the guard; `slv_3p_poi` runs last.
    - `e2a3d4ba`: identity summary.
    - `ed47805a`: `sgm` backfill with `full_reload`, the takeover rules with `table_filter`, and rollback order.
11. FL_00 JSON: the 3P extract activity gets `"sources":{"value":"google,sgm","type":"string"}`.
12. Entity `b1entitybuild` `build`: after `src = ctx.input("poi")`, add the `sgm`-to-`google` mapping and the metric. Entity `b1entitymd`: add one line.
13. Mapping docs:
    - `mapping_gld_srv_poi_info.md` §1.2, `mapping_gld_srv_poi_multi_lang.md` §1.2, and `mapping_gld_srv_poi_amenity.md` §0: `google` includes bronze `sgm`, mapped in the entity node.
    - `mapping_poi_media_info.md` §1.1 and §1.2: rows that originate from `sgm` are included. The literal `google` is unchanged. `scraper-` photos stay separate (D-4 B).
    - `mapping_gld_srv_poi_review.md`, `review_id` row: under D-4 B, `sgm` reviews hash `google`, and exact matches converge.
14. After the scope add:
    - `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §4 and §7.
    - `tests/test_3p_sgm_identity_contract.py`.

## Code sketch

### Constants (cell `1ccbf8fd`)

```python
IDENTITY_SOURCE = {"sgm": "google"}            # D-1: bronze source_name -> identity used in derived keys
PRIORITY_SOURCE = "google"                     # D-3 / D-5
POI_TABLE = "slv_3p_poi"                       # only table with source_name: provenance marker
IDENTITY_DOC_COL = "poi_source_name"           # synthetic _doc__poi_source_name; never read from raw
TAKEOVER_DOC_COL = "poi_takeover"              # synthetic _doc__poi_takeover (D-5)
SYNTHETIC_DOC_COLS = (IDENTITY_DOC_COL, TAKEOVER_DOC_COL)
IDENTITY_KEY_COLUMNS = ("poi_id", "review_id", "media_dedup_key")   # D-4 B
IGNORE_REASONS = ("OUT_OF_SCOPE", "GOOGLE_PRIORITY")


def identity_source(col: Column) -> Column:
    """sgm -> 'google'; every other value kept byte-for-byte (I-1)."""
    name, out = F.lower(F.trim(col)), col.cast("string")
    for src, target in IDENTITY_SOURCE.items():
        out = F.when(name == F.lit(src), F.lit(target)).otherwise(out)
    return out


def identity_path(column, path: str) -> str:
    if column.name in IDENTITY_KEY_COLUMNS and path == "_doc.source_name":
        return f"_doc.{IDENTITY_DOC_COL}"
    return path
```

### Owner snapshot and priority (cell `803f3d1d`)

```python
def poi_owner_snapshot(specs: list) -> tuple:
    """(DataFrame _k, _owner of slv_3p_poi VERSION AS OF the version at run start, version) (I-8)."""
    fq = f"{specs[0].trg_schema}.{POI_TABLE}"
    if not spark.catalog.tableExists(fq):
        return spark.createDataFrame([], "_k string, _owner string"), None
    v = int(spark.sql(f"DESCRIBE HISTORY {fq} LIMIT 1").first()["version"])
    return spark.sql(f"SELECT poi_id AS _k, lower(trim(source_name)) AS _owner FROM {fq} VERSION AS OF {v}"), v


def apply_source_priority(classified: DataFrame, owners: DataFrame, takeover_enabled: bool) -> tuple:
    """D-3: VALID sgm doc on a google-owned poi_id -> IGNORED GOOGLE_PRIORITY.
    D-5: VALID google doc on an sgm-owned poi_id -> _doc__poi_takeover = true. Returns (docs, takeover_ids)."""
    valid = F.col("_status") == "VALID"
    src = F.lower(F.trim(F.col(f"_doc__{RAW_DOC_ID[0]}")))
    docs = (classified.withColumn("_gp_id", F.col(f"_doc__{RAW_DOC_ID[1]}").cast("string"))
                      .withColumn("_gp_poi", F.when(valid, F.expr(
                          derived_sql([f"_doc__{IDENTITY_DOC_COL}", "_gp_id"], "HASH_MD5_UUID")))))
    in_run = (docs.where(valid & (src == PRIORITY_SOURCE)).select(F.col("_gp_poi").alias("_k"))
                  .distinct().withColumn("_g_run", F.lit(True)))
    docs = (docs.join(F.broadcast(owners), F.col("_gp_poi") == owners["_k"], "left").drop("_k")
                .join(F.broadcast(in_run), F.col("_gp_poi") == in_run["_k"], "left").drop("_k"))
    owned = (F.col("_owner") == PRIORITY_SOURCE) | F.coalesce(F.col("_g_run"), F.lit(False))
    skip = valid & src.isin(*IDENTITY_SOURCE) & owned
    take = valid & (src == PRIORITY_SOURCE) & F.col("_owner").isin(*IDENTITY_SOURCE) & F.lit(takeover_enabled)
    docs = (docs.withColumn("_status", F.when(skip, F.lit("IGNORED")).otherwise(F.col("_status")))
                .withColumn("_reason", F.when(skip, F.lit("GOOGLE_PRIORITY")).otherwise(F.col("_reason")))
                .withColumn(f"_doc__{TAKEOVER_DOC_COL}", F.coalesce(take, F.lit(False))))
    for b in [c for c in docs.columns if c.startswith("_b__")]:
        docs = docs.withColumn(b, F.when(~skip, F.col(b)))
    takeover_ids = docs.where(f"_doc__{TAKEOVER_DOC_COL}").select(F.col("_gp_poi").alias("_k")).distinct()
    return docs.drop("_gp_id", "_gp_poi", "_owner", "_g_run"), takeover_ids
```

Main checks the broadcast-join column disambiguation at implementation time. The behavior must match the table in `## Ordering`.

### Takeover state reset (cell `65ab1f40`)

```python
def reset_takeover_state(takeover_ids: DataFrame, specs: list, ctx: RunContext) -> int:
    """D-5: delete ctrl_cdc_state of takeover poi_id for the tables of this run, before load_state."""
    targets = spark.createDataFrame([(s.trg_schema, s.trg_tbl) for s in specs], "trg_schema string, trg_tbl string")
    keys = takeover_ids.crossJoin(F.broadcast(targets)).select("trg_schema", "trg_tbl", F.col("_k").alias("entity_key"))
    cond = ("t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl AND t.entity_key = s.entity_key"
            + src_partition_cond(ctx.src_tbl))
    with_retry(lambda: DeltaTable.forName(spark, T_CDC_STATE).alias("t").merge(keys.alias("s"), cond)
               .whenMatchedDelete().execute(), "ctrl_cdc_state takeover")
    return keys.count()
```

### MERGE guard (cell `65ab1f40` `build_merge_sql`)

```python
f"WHEN MATCHED AND (s.`_doc__{TAKEOVER_DOC_COL}`\n"
f"                  OR s.`_crawled_at` > coalesce(t.`_crawled_at`, TIMESTAMP'...')\n"
f"                  OR (s.`_crawled_at` = t.`_crawled_at` AND s.`_event_id` >= coalesce(t.`_event_id`, ''))) THEN UPDATE SET\n"
```

The existing two-term guard stays byte-identical inside the `OR`. In `merge_into_target`, `cols` gains `f"_doc__{TAKEOVER_DOC_COL}"`.

### Wiring (cell `84cc99f5` `process_run`)

```python
    owners, poi_v = poi_owner_snapshot(specs)
    takeover_enabled = not ctx.table_filter and any(s.trg_tbl == POI_TABLE for s in specs)
    classified, takeover_ids = apply_source_priority(
        classify_docs(read_raw(ctx, doc_columns(specs)), top_fields(specs)), owners, takeover_enabled)
    classified = classified.persist(StorageLevel.MEMORY_AND_DISK)
    takeover_ids = takeover_ids.persist(StorageLevel.MEMORY_AND_DISK)
    out.cached += [classified, takeover_ids]
    n_take = takeover_ids.count()
    # ... profile_docs / logs / extra unchanged; add the counters of ## Observability ...
    if n_take and not ctx.dry_run:
        out.extra["takeover_state_keys"] = reset_takeover_state(takeover_ids, specs, ctx)
    state_df = None
    if not ctx.full_reload:
        state_df = load_state(specs).persist(StorageLevel.MEMORY_AND_DISK)
        out.cached.append(state_df)
    docs = classified.where("_status = 'VALID'")
    worker = lambda d: (lambda s, wave: process_table(s, d, state_df, ctx, wave))
    if not n_take:
        run_tables(specs, lambda s: counts[s.trg_tbl], worker(docs), ctx, out.results)
    else:
        rest = [s for s in specs if s.trg_tbl != POI_TABLE]
        poi = [s for s in specs if s.trg_tbl == POI_TABLE]
        run_tables(rest, lambda s: counts[s.trg_tbl], worker(docs), ctx, out.results)
        gate_ok = all(r.status in ("SUCCESS", "NO_DATA") for r in out.results)
        out.extra["takeover_deferred"] = 0 if gate_ok else n_take
        if not gate_ok and ctx.stop_on_failure:
            now = utc_now()
            out.results += [TableResult(spec=s, status="SKIPPED", started_at=now, ended_at=now,
                                        error_message="takeover gate: earlier tables failed") for s in poi]
        else:
            poi_docs = docs if gate_ok else docs.where(f"NOT _doc__{TAKEOVER_DOC_COL}")
            run_tables(poi, lambda s: counts[s.trg_tbl], worker(poi_docs), ctx, out.results)
    out.status = decide_status(out.results)
```

### `check_config` additions (cell `84cc99f5`)

Each failure appends to `errors`:

- `len({s.trg_schema for s in specs}) == 1`.
- `doc_key_column == "poi_id"`.
- For every spec, `poi_id` has `convert_rule == "HASH_MD5_UUID"` and `list(paths) == ["_doc.source_name", "_doc.source_id"]`.
- Every column in `IDENTITY_KEY_COLUMNS` that a spec has satisfies `paths[0] == "_doc.source_name"`.
- If `POI_TABLE` is in specs, it has a column `source_name` with the single path `_doc.source_name`.
- `set(SYNTHETIC_DOC_COLS) & raw_cols == set()`.

### Entity (cell `b1entitybuild`, after `src = ctx.input("poi")`)

```python
SOURCE_AS_GOOGLE = ("sgm",)   # D-1: effective source after slv_3p_poi
as_google = F.lower(F.trim("source_name")).isin(*SOURCE_AS_GOOGLE)
ctx.metrics.update(sgm_as_google_rows=src.where(as_google).count())
src = src.withColumn("source_name", F.when(as_google, F.lit(GOOGLE)).otherwise(F.col("source_name")))
```

## Verification

### Local

```
python -m pytest tests/test_3p_l1_contract.py tests/test_3p_raw_rules.py tests/test_pipeline_precheck_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_enr_poi_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_3p_visibility_sql.py tests/test_l1_ts_contract.py -q
python -m pytest tests/test_3p_sgm_identity_contract.py -q
python scripts/vv.py run-gate 20261119-gsm-as-google-extract
```

`tests/test_3p_sgm_identity_contract.py` holds static tests over the notebook, pipeline, and DDL source. There is no local Spark.

- `test_sources_default_and_fl00_include_sgm`: notebook default and FL_00 3P activity are `google,sgm`; the CMS `sources` is unchanged.
- `test_identity_source_only_maps_sgm`
- `test_identity_key_columns_match_d4b`
- `test_google_priority_is_ignore_reason`
- `test_check_config_guards_identity_and_synthetic_cols`
- `test_registry_key_paths_unchanged`: the `POI_ID`, `review_id`, and `media_dedup_key` paths and rules in `NB_CREATE_DDL` cell 14 are unchanged.
- `test_merge_guard_takeover_bypass`: the takeover clause comes before the unchanged guard; the takeover column is not in `UPDATE SET` or `INSERT`.
- `test_stale_filter_excludes_takeover`
- `test_poi_owner_snapshot_version_pinned`: `VERSION AS OF` is present.
- `test_takeover_state_reset_before_load_state`: source order inside `process_run`.
- `test_poi_table_last_when_takeover`: two-phase `run_tables` and the gate.
- `test_entity_maps_sgm_to_google_before_filter`
- `test_no_sgm_dictionary_rows`

### DEV runtime

Record results in `runtime-runbook.md`. `v0` is the version before the run.

- **V-1.** `slv_3p_poi` and the 6 tables keyed by `poi_id`: `count(*) = count(DISTINCT poi_id)`. Review: `count(*) = count(DISTINCT review_id)`. Media: `count(*) = count(DISTINCT media_dedup_key)`.
- **V-2.** `sgm` rows whose `poi_id` differs from the formatted `md5(concat('google', source_id))`: 0. Spot-check that child rows of `sgm` `poi_id`s recompute `review_id` and `media_dedup_key` with `'google'`.
- **V-3.** The `google` rows at `v0`, minus the `google` rows now, on `(poi_id, source_name)`: 0. `sgm` rows whose `poi_id` was `google` at `v0`: 0.
- **V-4.** Backfill exit JSON: `sgm_valid = 2630`, `google_priority_skipped = 402`, `takeover_poi = 0`, no new reject reason. `slv_3p_poi` `sgm` rows = 2228.
- **V-5.** Incremental rerun and `full_reload` rerun: `inserted_rows = 0` for all 9 tables in `ctrl_log_table_run`; row counts unchanged.
- **V-6.** Entity: 0 rows with `sgm`. `google` rows = `slv_3p_poi` rows. `sgm_as_google_rows` = the `slv_3p_poi` `sgm` count.
- **V-7.** `gld_srv_poi_info`, `gld_srv_poi_multi_lang`, `gld_enr_poi_info`: 0 rows with `sgm`; column sets unchanged.
- **V-8.** `slv_poi_amenity` has rows for `poi_id`s that originate from `sgm`. `ref_dictionary_amenities` and `ref_dictionary_place_type` have 0 rows with `sgm`.
- **V-9.** `ctrl_cdc_state`: no entity key of an `sgm` document skipped by `GOOGLE_PRIORITY` gained a row from this run.
- **V-10. Takeover (D-5).** Needs one `sgm`-only `source_id` plus a `google` event with an older `crawled_at`. Expected:
  - `takeover_poi ≥ 1`
  - `slv_3p_poi.source_name = google` with the older `_crawled_at`
  - every `poi_id`-keyed child row carries the `google` `_event_id`
  - `ctrl_cdc_state` for that key in all 9 tables equals the order of the `google` event
  - a rerun shows `takeover_poi = 0` and 0 inserts

  This needs a DEV fixture. See stop point 6 in the Main brief.
- **V-11. Gate.** Under the same fixture, run once with `table_filter` set. Expected: `takeover_enabled = false`, and `slv_3p_poi` stays `sgm`. The next full run then performs the takeover.
