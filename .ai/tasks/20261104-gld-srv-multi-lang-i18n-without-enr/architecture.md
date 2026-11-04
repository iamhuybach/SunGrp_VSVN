RESULT: PASS

## Main brief

### Decision
`srvmlbuild` = P1, unchanged, `unionByName` P2. P2 is i18n rows with a valid key, `left_anti` ML keys on `(poi_id, lang)`. One MERGE, and `SPEC` does not change.
P2 values: `poi_id = uuid_md5(business_service_id,'partner')`, `lang = locale`, `source_name = 'partner'`, three measures null, `description = bio`, `experience = usps`, no fallback. No locale, `deleted`, entity or text filter.
UD-BLANK: drop an i18n row from P2 when `business_service_id` or `locale` is null or blank after trim, and count it in warn `multi_lang_i18n_key_blank`.
D-ML-SRC / D-ML-WRITER: new `NB_CREATE_DDL` cells `mlsrcmd` + `mlsrcpy` add `source_name STRING` (nullable) AFTER `experience` on `slv_enr_poi_info_multi_lang`. `init_tables` gets the same column. No writer or reader.
D-ML-NOMATCH: `NB_ENR_POI_INFO` is not edited. One test pins that it still takes `source_name` from entity.

### Invariants Main must preserve
- The gold output is unique on `(poi_id, lang)`. The anti-match uses `["_pid","_loc"]` only. P2 never reads `source_name`, `partner` or `ent`.
- For ML keys, P1 output is byte-identical to today's. The only P1 edit is `return (` → `p1 = (`.
- Each P2 column is cast to the P1 type via `p1.schema`. `OUT_COLS`, `ML_COLS`, `pk`, `inputs`, `required_inputs=("multi_lang","entity")` and `write_mode` do not change.
- `srvmlbuild` has exactly three `live_only=False`, and no `deleted` or `lh_vv_gold` token.
- The blank-key guard applies to P2 only, never to the `bio` frame that P1 uses.
- `ml.select(*ML_COLS)` stays before the entity join. No reader of the ML table selects `source_name`.
- After `mlsrcpy`, the ML schema = the `mlexppy` contract with `("source_name","STRING")` inserted after `experience`. `init_tables` renders the identical CREATE.
- `mlsrcpy`: GLD_30M lease, every check before the write, `_refresh_lock()` right before the single `ALTER … AFTER`, post-check, and the `finally` release. No CREATE, INSERT, MERGE, DROP or gold write.
- `mlexppy` and the `rvi18n*` cells are not edited. The two new cells are appended last.
- `NB_ENR_POI_INFO`: `REQUIRED_COLS["multi_lang"] == ("poi_id",)` and `source_name` comes from `e.source_name`.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | `id:srvmlbuild` | Replace the source with architecture §16.1 | §17.1 tests pass; existing `test_node_specs`, `test_multi_lang_experience_rule` stay green |
| 2 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | `id:srvmlmd` | Append the two P2 lines from §16.1 | Markdown mentions P2 |
| 3 | docs/context/mapping_gld_srv_poi_multi_lang.md | whole file | Save the §16.2 FILE block verbatim | `test_multi_lang_mapping_targets` passes |
| 4 | notebooks/NB_CREATE_DDL.ipynb | after `rvi18ngldpy` | Append `mlsrcmd` (markdown) and `mlsrcpy` (code) from §16.3 | `test_multi_lang_source_name_patch` passes; `ids[-2:] == ["mlsrcmd","mlsrcpy"]` |
| 5 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, ML spec, first `('experience', 'STRING', None),` | Insert the comment and `('source_name', 'STRING', None),` (§16.4) | `test_columns_match_sources`, `test_flag_patch_create_matches_init`, `test_no_destructive_sql` pass |
| 6 | docs/context/gld_enr_poi_info_review.md | table row `Nguồn đang dùng` (line 12) | Append the §16.5 sentence | Text present |
| 7 | tests/test_gld_srv_poi_contract.py | after `test_multi_lang_experience_rule` | Add `ML_MAPPING` and the 3 tests in §17.1 | Pass |
| 8 | tests/test_gld_srv_poi_contract.py | `test_info_rating_patch`, `test_review_source_patch_cell` | Shift the tail slices by 2 and add the `ids[-2:]` assert (§17.1) | Pass |
| 9 | tests/test_enr_poi_contract.py | `test_info_patch_cell_guards` lines 223–232 | Shift the slices by 2 and add the `ids[-2:]` assert | Pass |
| 10 | tests/test_enr_poi_contract.py | after `test_flag_node_contract` | Add `test_info_source_name_stays_entity` (§17.2) | Pass |
| 11 | tests/test_initial_ddl_contract.py | `test_columns_match_sources` l.312; `test_flag_patch_create_matches_init` l.662 | `ml_cols = {**mlexppy TABLE_COLS, **mlsrcpy TABLE_COLS}` (§17.2) | Pass |
| 12 | tests/test_poi_entity_contract.py (NOT in scope.files) | `test_create_ddl_patch` lines 635–644 | Only after stop 1 approval: shift the slices by 2 and add the `ids[-2:]` assert (§17.3) | Full suite green |

### Order and stop points
1. STOP (user decision), before rows 4, 5 and 12:
   - (a) confirm `source_name STRING` nullable AFTER `experience`;
   - (b) approve adding `tests/test_poi_entity_contract.py` to `scope.files`. Appending cells to `NB_CREATE_DDL` breaks its tail-id test. No other placement is valid (§18 H, I).
   - If (b) is refused, do rows 1–3 and 7 (the new P2 tests only), and report D-ML-SRC DDL as blocked.
2. Rows 1–3. Run `pytest tests/test_gld_srv_poi_contract.py -q`.
3. Rows 4–11, then row 12 after approval. Run the full commands below.
4. `python scripts/vv.py run-gate 20261104-gld-srv-multi-lang-i18n-without-enr`.
5. STOP (evidence, recommended, not a gate): Dev, per §14.
   - Run P-3, run `mlsrcpy`, check `DESCRIBE`.
   - DRY_RUN with `p_force="true"`. Expect: no QG block, `inserted` = P-1, `multi_lang_i18n_only_rows` = `inserted`, `multi_lang_i18n_key_blank` = P-2, `updated = deactivated = 0`.
   - Then one RUN.

### Tests and verification
- `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py -q`
- `python -m pytest tests -q`
- New tests: `test_multi_lang_i18n_only_branch`, `test_multi_lang_mapping_targets`, `test_multi_lang_source_name_patch`, `test_info_source_name_stays_entity`.
- Must stay green without edits: `test_node_specs`, `test_build_columns_match_ddl`, `test_multi_lang_experience_rule`, `test_multi_lang_experience_patch`, `test_landing_multi_lang_experience`, `test_flag_node_contract`, `test_create_sql_renders`, `test_no_destructive_sql`.
- `python scripts/vv.py run-gate 20261104-gld-srv-multi-lang-i18n-without-enr`

### Read only if needed
- §0 Verdict and ledger mapping → all rows (ledger to code, model-design conflicts settled)
- §5 Grain and keys → row 1 (why there is no entity predicate in the anti-match), row 4 (column position)
- §8 Idempotency → rows 1 and 4 (P1↔P2 moves, the ALTER makes ML edges dirty, `_align_snapshot`)
- §9 Concurrency, §10 Retry → row 1 (blank guard, why `required_inputs` stays), row 4 (lease, partial failure)
- §14 Rollout, §15 Rollback → stops 1 and 5
- §16.1 → rows 1–2; §16.2 → row 3; §16.3 → row 4; §16.4 → row 5; §16.5 → row 6
- §17.1–§17.3 → rows 7–12
- §18 Alternatives → stop 1 (H, I, J), row 1 (A–G), row 10 (K)

# Architecture: 20261104-gld-srv-multi-lang-i18n-without-enr

## 0. Verdict and ledger mapping

PASS. Two pieces of work, in one task:

- A. `gld_srv_poi_multi_lang` gains population P2 (i18n-only partner rows). P2 is unioned with the unchanged P1 and written in one MERGE.
- B. `slv_enr_poi_info_multi_lang` gains the DDL column `source_name STRING` (nullable) AFTER `experience`, in both DDL notebooks. No reader or writer uses it (D-ML-SRC, D-ML-WRITER, D-ML-NOMATCH).

One governance stop: appending cells to `NB_CREATE_DDL` breaks `tests/test_poi_entity_contract.py::test_create_ddl_patch`, which pins the tail cell ids and is not in `scope.files` (§14, §17.3). The design does not change. Only the scope needs approval.

| Ledger row | How the design implements it |
|---|---|
| D-I18N-ROW, UD-INPUT (per key) | P2 = i18n rows `left_anti` ML keys on `(poi_id, lang)` |
| D-I18N-KEY | `poi_id = uuid_md5(business_service_id, 'partner')`, `lang = locale` |
| D-I18N-COLS | P2 `description = bio`, `experience = usps`, no fallback. `OUT_COLS` unchanged |
| UD-SRC, D-ML-SRC sentence 2 | P2 `source_name = F.lit(PARTNER)`. P2 does not read entity |
| UD-MEASURES | P2 `time_to_spend`, `best_time`, `cost_vnd` = null (cast to the P1 types) |
| UD-LOCALE | No locale filter or allow-list |
| UD-DELETED | No `deleted` filter. All three inputs keep `live_only=False` |
| UD-INPUT (table level) | `required_inputs` stays `("multi_lang", "entity")`. UD-INPUT covers a key that does not match, not an empty table (§10) |
| UD-BLANK ("Chốt theo kiến trúc") | Drop an i18n row whose `business_service_id` or `locale` is null or blank after `trim` from P2, and count it in warn `multi_lang_i18n_key_blank` (§10) |
| D-KEEP | The P1 lines are unchanged. The only P1 edit is `return (` → `p1 = (` |
| D-ML-SRC sentence 1, D-ML-WRITER | New cell `mlsrcpy` adds the column with `ALTER TABLE ... ADD COLUMNS ... AFTER`. A new `init_tables` row covers empty environments. No writer |
| D-ML-NOMATCH (overrides D-ML-GATE and the D-ML-SRC clause) | `NB_ENR_POI_INFO` is not edited. A new test pins that it reads only `poi_id` from ML and takes `source_name` from `e.` |
| D-ML-PICK | Recorded. No rule here depends on it |
| D-REF | No edit to task `20261104-poi-review-src-and-partner-i18n` or its `rvi18n*` cells |

Model-design items, settled as the architecture:

- Conflicts 3 (type and nullability): `STRING` nullable. Every other `source_name` in the repo is STRING. Delta `ADD COLUMNS` on an existing table can only add a nullable column. With no writer, existing rows are null. Landing tables keep NOT NULL only on the key column (`test_flag_patch_constants`). Stop point 1 lets the user override this before the DDL rows run.
- Conflicts 1 (registry): no `ctrl_cfg_schema_registry` row. The registry configures bronze → silver loads. This landing table is written by an external job, and `slv_enr_poi_info_multi_lang` has no registry entry today.
- Conflicts 4: anti-match on `(poi_id, lang)`, with no entity predicate.
- Conflicts 6: no `bio` / `usps` non-null filter (D-I18N-ROW sets none).
- Conflicts 7: reading confirmed in the UD-MEASURES row above.

## 1. Scope

- `NB_GLD_SRV_POI_MULTI_LANG.ipynb`: cell `id:srvmlbuild` (P2 branch) and cell `id:srvmlmd` (two description lines).
- `NB_CREATE_DDL.ipynb`: append markdown `mlsrcmd` and code `mlsrcpy`.
- `NB_SETUP_INITIAL_DDL.ipynb`: cell `init_tables`, one column row in the `slv_enr_poi_info_multi_lang` spec.
- Docs: `mapping_gld_srv_poi_multi_lang.md` (FILE block) and `gld_enr_poi_info_review.md` (one sentence).
- Tests: `test_gld_srv_poi_contract.py`, `test_enr_poi_contract.py`, `test_initial_ddl_contract.py`. After approval, also `test_poi_entity_contract.py` (tail slice only).

## 2. Non-goals

- Grain, `OUT_COLS`, `ML_COLS`, `pk`, `inputs`, `required_inputs` and `write_mode` of `gld_srv_poi_multi_lang` do not change. No gold column is added.
- P1 does not change: joins, partner predicate, `bio` / `usps` fallback, warn `multi_lang_source_name_null`.
- No reader of `slv_enr_poi_info_multi_lang.source_name` is added (`NB_ENR_POI_INFO`, `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_MULTI_LANG` all keep their explicit projections).
- No writer for the new column. No ctrl edge, watermark or pipeline JSON change.
- No change to `docs/context/03_OPERATOR_GUIDE.md` §2.3 (out of scope by request).
- No edit to `mlexppy` or to any `rvi18n*` cell. The DDL patch cells are append-only history.

## 3. Invariants

- I1. The gold output is unique on `(poi_id, lang)`, so P1 and P2 are disjoint.
- I2. For every ML key, the P1 row is byte-identical to today's output, so its `row_hash` is unchanged.
- I3. P2 keys = valid i18n keys minus ML keys, compared by exact string equality (no trim or lower), the same as the P1 join.
- I4. P2 values: `poi_id = uuid_md5(business_service_id,'partner')`, `lang = locale`, `source_name = 'partner'`, three measures null, `description = bio`, `experience = usps`, no fallback.
- I5. The only P2 filters are the blank-key guard and the anti-match.
- I6. Each P2 column is cast to the type of the P1 column with the same name, so `unionByName` never widens P1.
- I7. `multi_lang_source_name_null` counts P1 rows only.
- I8. `srvmlbuild` has exactly three `ctx.input(..., live_only=False)` calls and no `deleted` token.
- I9. One build gives one MERGE, which gives at most one Delta commit.
- I10. Every reader of `slv_enr_poi_info_multi_lang` projects explicit columns before any join, so the new `source_name` can never collide with entity `source_name`:
  - `srvmlbuild` uses `ml.select(*ML_COLS)` and `ml.select(poi_id, lang)`.
  - `NB_GLD_SRV_POI_INFO` uses `ml.select("poi_id")`.
  - `NB_ENR_POI_INFO` uses `_present(..., "poi_id", ...)`.
- I11. After `mlsrcpy`, the `slv_enr_poi_info_multi_lang` schema equals the `mlexppy` contract with `("source_name","STRING")` inserted after `experience`. `init_tables` renders the same `CREATE TABLE`.
- I12. `gld_enr_poi_info.source_name` stays `F.col("e.source_name")`. `REQUIRED_COLS["multi_lang"]` stays `("poi_id",)`.

## 4. State ownership

- `gld_srv_poi_multi_lang` still has one writer: `NB_GLD_SRV_POI_MULTI_LANG` → `run_node` → `merge_target`.
- Key ownership is new:
  - A key is owned by P1 while an ML row exists for it. Otherwise it is owned by P2, through its `slv_pn_business_service_i18ns(business_service_id, locale)` row.
  - Ownership moves through an UPDATE on the same key (§8).
- Schema of `slv_enr_poi_info_multi_lang`: `NB_CREATE_DDL` (`mlsrcpy`) owns it in existing environments, and `NB_SETUP_INITIAL_DDL` (`init_tables`) owns it in empty ones. The row content is owned by the external enrich job. This task does not change that.
- No ctrl, watermark or lock table changes. `mlsrcpy` only takes and releases the existing `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` lease.

## 5. Grain and keys

This section cites `model-design.md` `## Keys` and `## Entities and grain`. The grain stays `(poi_id, lang)` on both tables.

- Anti-match: `left_anti` USING `["_pid","_loc"]` against `ml.select(poi_id → _pid, lang → _loc)`.
  - It has no `source_name` partner predicate. With that predicate, an ML row at the same key with a non-partner or null entity `source_name` would make P1 and P2 both emit the key. That breaks I1, and QG `pk_duplicate` would block the whole node.
  - The USING string list avoids self-join lineage ambiguity.
- P1 keys are exactly the ML keys. The `bio` join cannot fan out while the i18n key is unique. P2 keys are i18n keys that are not ML keys. Disjointness (I1) follows.
- P2 keys are unique among themselves, because `(business_service_id, locale)` is unique (`CTRL_TABLES_CONTEXT.md` §5) and `uuid_md5` is deterministic. If the source key is ever not unique, QG `pk_duplicate` blocks the run. That is the same failure P1 already has for matched partner rows. Silent dedupe is rejected because it would pick one of two conflicting texts.
- The anti-match is per `(poi_id, lang)`. A locale without an ML row emits P2 even when the `poi_id` has ML rows in other languages (UD-LOCALE, D-I18N-ROW). UD-INPUT's "không có poi_id khớp" case is a subset of this.
- Types: P2 is projected and then cast with `types` from `p1.schema` (I6).
- `slv_enr_poi_info_multi_lang.source_name` is not a key. Its position is after `experience`, so only the two system timestamps shift position. Business columns keep their ordinals.

## 6. Ordering

Inside `build`:

1. Three inputs.
2. Three `_require` calls.
3. P1 and its warn (unchanged).
4. `p1 = ….select(*OUT_COLS)`.
5. `_i18n_only`: blank-key guard and warn → keyed → `left_anti` → project and cast → warn with the P2 count.
6. `p1.unionByName(p2)`.

The guard runs before the anti-join, so the warn counts only invalid keys.

Deployment order between B (`mlsrcpy`) and A (notebook): either order is safe, because no reader selects `source_name` (I10). Recommended order is B, then A (§14).

Across nodes: `priority = 1` on `PL_VV_TRANS_SLV_TO_GLD_30M` does not change. Inputs are read at pinned versions, so P1 and P2 see one snapshot.

## 7. Transaction and commit boundaries

- A: `build` → `add_row_hash` → `quality_gate` → `diff_counts` → one `MERGE INTO`. A zero diff gives no commit.
  - A second MERGE or a separate node for P2 is rejected. `NOT MATCHED BY SOURCE` soft-delete would make each population delete the other, and it would break I9.
- B: one `ALTER TABLE … ADD COLUMNS` is one Delta metadata commit. The pre-check runs before it and the post-check after it. The lease is renewed and its owner re-checked right before the ALTER.

## 8. Idempotency

A. `build` is a pure function of the pinned input versions. A rerun gives the same rows and the same hash, so diff = 0 and there is no commit.

| Case | Next run |
|---|---|
| A P2 key gains an ML row | P2 → P1 on the same key. Hash changes → UPDATE |
| An ML row disappears and the i18n row stays | P1 → P2 → UPDATE, not a soft-delete |
| An i18n row disappears (or its key becomes blank) and no ML row exists | Not matched by source → soft-delete |
| A soft-deleted key reappears | Matched with `deleted_at` set → UPDATE and `deleted_at = NULL` |
| An i18n row is flagged deleted by the partner | Still emits P2 (UD-DELETED). It leaves gold only when it leaves silver |

B. `mlsrcpy` accepts exactly two states:

- full contract → no write;
- the contract minus `source_name` → ALTER.

Anything else stops before writing. A rerun after success is a no-op.

The ALTER commit makes the three ML edges dirty:

- `gld_srv_poi_multi_lang` and `gld_srv_poi_info` are recomputed. P1 and `gld_srv_poi_info` give diff 0, because they never select the column.
- For `gld_enr_poi_info`, `ctx.changed("multi_lang")` is empty. `_align_snapshot` gives the old version the new column as NULL, so `subtract` returns no rows.

This dirty edge also means the first scheduled GLD_30M run after B inserts P2, even without `p_force`.

## 9. Concurrency

- A: Not applicable. There is one writer under the existing flow lock. No new writer, lock or edge.
- B: `mlsrcpy` holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`, following the precedent of `mlexppy`.
  - An `NB_ENR_POI_INFO` run on `PL_VV_TRANS_SLV_TO_ENR_15M` reads at a pinned version and is unaffected by a concurrent metadata commit.
  - A concurrent external append can get a Delta metadata-conflict and must retry. That is the external job's normal retry path. With no writer implemented yet (D-ML-WRITER), the risk is minimal.

## 10. Retry, recovery and partial failure

- Blank or null P2 keys (UD-BLANK):
  - What happens without a guard:
    - A null `business_service_id` gives a null `_pid` (`concat`), so QG `pk_null` fails the whole node, P1 included.
    - A blank `business_service_id` gives a fake `md5('partner')` key.
    - A blank `locale` gives `lang = ''`.
  - Selected: drop such rows from P2 and count them in `multi_lang_i18n_key_blank`. P1 still reads the unguarded `bio` frame (D-KEEP).
  - Rejected: letting QG block (one bad partner row would freeze serving), passing blanks through (fake keys), guarding the shared `bio` frame (changes P1).
- Empty ML table: `required_inputs` stays, so the node FAILS before `build`. This is the existing guard against mass soft-delete. If ML were optional, an empty ML would soft-delete every P1 key. Empty entity also still fails, as today.
- A retry: `merge_target` uses `with_retry`, and a Delta MERGE is atomic. A build failure writes nothing, the node log shows FAILED, and a rerun is safe.
- B partial failure:
  - A failure before the ALTER writes nothing.
  - An ALTER that succeeds followed by a failing post-check leaves a valid schema. A rerun takes the full-contract path and is a no-op.
  - The `finally` block always releases the lease it owns and records the status.

## 11. Observability

- New warns:
  - `multi_lang_i18n_key_blank`: i18n rows dropped by the guard.
  - `multi_lang_i18n_only_rows`: P2 row count.
- Unchanged: `multi_lang_source_name_null` (P1 only). The diff log and `node_log.inserted_rows` show P2 arriving.
- Cost: two more `count()` jobs over small silver frames. If spark-runtime-reviewer objects, merge them into one `agg`.
- `mlsrcpy` prints `source_name: +<fq>` or `source_name: =<fq>`. The watermark row records SUCCESS or FAILED with `error_message`.
- Accepted consequences, recorded for reviewers:
  - P2 includes partner-deleted i18n rows (UD-DELETED).
  - A P2 `poi_id` with no entity row has no `gld_srv_poi_info` row (UD-SRC, UD-INPUT).
  - Optional probe P-1 sizes both.

## 12. Security

Not applicable: no new source, credential or external surface. Partner `bio` and `usps` already flow into this table. The new silver column carries a source label only.

## 13. Optional probes (read-only, Dev; not a gate)

```sql
-- P-1: expected P2 insert count by locale, deleted flag, entity presence, empty text
WITH i AS (
  SELECT regexp_replace(md5(concat(business_service_id, 'partner')),
         '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5') AS pid,
         locale, deleted, bio, usps
  FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
  WHERE coalesce(trim(cast(business_service_id AS string)), '') <> ''
    AND coalesce(trim(cast(locale AS string)), '') <> '')
SELECT i.locale, coalesce(i.deleted, false) AS deleted,
       e.poi_id IS NULL AS no_entity, i.bio IS NULL AND i.usps IS NULL AS no_text, count(*) AS n
FROM i
LEFT ANTI JOIN lh_vv_silver.dbo.slv_enr_poi_info_multi_lang m ON m.poi_id = i.pid AND m.lang = i.locale
LEFT JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e ON e.poi_id = i.pid
GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;

-- P-2: expected multi_lang_i18n_key_blank
SELECT count_if(coalesce(trim(cast(business_service_id AS string)), '') = ''
             OR coalesce(trim(cast(locale AS string)), '') = '') AS key_blank
FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns;

-- P-3: schema before mlsrcpy (must equal the mlexppy contract)
DESCRIBE TABLE lh_vv_silver.dbo.slv_enr_poi_info_multi_lang;
```

If the `deleted` column does not exist, drop it from P-1.

## 14. Rollout

1. Stop point 1 (user decision): confirm `source_name STRING` nullable AFTER `experience`, and approve adding `tests/test_poi_entity_contract.py` to `scope.files`. The only edit there is the tail slice in §17.3, which is needed because `mlsrcmd` and `mlsrcpy` are appended after `rvi18ngldpy`.
   - If the user refuses the scope change, edits A (notebook, mapping, the matching tests) can still land. Edit B cannot be added to `NB_CREATE_DDL` without breaking that test. Inserting the cells earlier is rejected (§18 H).
2. Implement §16 and run the tests in §17.
3. Dev:
   - Run P-3.
   - Run `mlsrcpy` once. The GLD_30M lease must be free.
   - Check that `DESCRIBE` shows `source_name string` after `experience`.
4. Deploy `NB_GLD_SRV_POI_MULTI_LANG`. Run it by hand with `p_mode="DRY_RUN"`, `p_force="true"`. Accept only if all of these hold:
   - No QG block.
   - `inserted` = Σn of P-1.
   - `multi_lang_i18n_only_rows` = `inserted`.
   - `multi_lang_i18n_key_blank` = P-2.
   - `updated = deactivated = 0` (proves I2, provided no input committed since the last run).
5. One RUN with `p_force="true"`, or let the next scheduled run pick up the dirty ML edge (§8).
6. Other environments: in a fresh environment, `NB_SETUP_INITIAL_DDL` creates the column directly. In an existing one, run `mlsrcpy` once.

Runtime proof is recommended but is not a gate (`runtime_required=False`).

## 15. Rollback and forward recovery

- A, rollback: revert the notebook commit and run once with `p_force="true"`. P2 keys leave the source, so the MERGE soft-deletes them. P1 is untouched. Do not use Delta `RESTORE`, because it would desynchronise the ctrl watermarks.
- A, forward recovery: fix the cell and rerun with force. Keys soft-deleted by a rollback are revived by the matched-with-`deleted_at` UPDATE.
- B is forward-only:
  - Dropping a Delta column needs column mapping. All patch cells forbid that (`columnMapping` token tests).
  - The nullable, unread column is harmless. Rollback means leaving the column in place and reverting the repo cells only if the user withdraws D-ML-SRC.
  - A wrong type can be fixed forward later, when a writer exists, while the column is still all-null.

## 16. Implementation plan

### 16.1 Cell `id:srvmlbuild`: full source

Replace the whole cell source. Keep JSON `source` as a list of lines ending in `\n`. Lines from `bio = i18n.select(` through `experience = …` are textually identical to today's. The only P1 edit: `return (rows.withColumn(` becomes `p1 = (rows.withColumn(`, and its continuation line is re-indented by 2 spaces.

```python
PARTNER = "partner"
ML_COLS = ("poi_id", "lang", "time_to_spend", "best_time", "cost_vnd", "description", "experience")
OUT_COLS = ("poi_id", "lang", "source_name", "time_to_spend", "best_time", "cost_vnd", "description", "experience")
MEASURE_COLS = ("time_to_spend", "best_time", "cost_vnd")
I18N_ONLY_WARN = "multi_lang_i18n_only_rows"
I18N_KEY_BLANK_WARN = "multi_lang_i18n_key_blank"


def _require(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ConfigError(f"gld_srv_poi_multi_lang: {name} thiếu {missing}")


def _filled(name):
    """Cột khoá khác null và khác rỗng sau trim."""
    return F.coalesce(F.trim(F.col(name).cast("string")), F.lit("")) != ""


def _i18n_only(ctx, ml, i18n, schema):
    """P2: dòng i18n có khoá hợp lệ và không có dòng multi_lang cùng (poi_id, lang). Ép kiểu theo P1."""
    key_ok = _filled("business_service_id") & _filled("locale")
    ctx.warn(I18N_KEY_BLANK_WARN, i18n.where(~key_ok).count())
    keyed = i18n.where(key_ok).select(uuid_md5(F.col("business_service_id"), F.lit(PARTNER)).alias("_pid"),
                                      F.col("locale").alias("_loc"), "bio", "usps")
    ml_keys = ml.select(F.col("poi_id").alias("_pid"), F.col("lang").alias("_loc"))
    only = keyed.join(ml_keys, ["_pid", "_loc"], "left_anti")
    types = {f.name: f.dataType for f in schema.fields}
    p2 = (only.select(F.col("_pid").alias("poi_id"), F.col("_loc").alias("lang"),
                      F.lit(PARTNER).alias("source_name"), *[F.lit(None).alias(c) for c in MEASURE_COLS],
                      F.col("bio").alias("description"), F.col("usps").alias("experience"))
          .select(*[F.col(c).cast(types[c]).alias(c) for c in OUT_COLS]))
    ctx.warn(I18N_ONLY_WARN, p2.count())
    return p2


def build(ctx):
    ml = ctx.input("multi_lang", live_only=False)
    ent = ctx.input("entity", live_only=False)
    i18n = ctx.input("i18n", live_only=False)
    _require(ml, ML_COLS, "slv_enr_poi_info_multi_lang")
    _require(ent, ("poi_id", "source_name"), "slv_poi_entity_non_enrich")
    _require(i18n, ("business_service_id", "locale", "bio", "usps"), "slv_pn_business_service_i18ns")
    bio = i18n.select(uuid_md5(F.col("business_service_id"), F.lit(PARTNER)).alias("_pid"),
                      F.col("locale").alias("_loc"), "bio", "usps")
    partner = F.coalesce(F.lower(F.trim(F.col("source_name"))) == PARTNER, F.lit(False))
    rows = (ml.select(*ML_COLS).join(ent.select("poi_id", "source_name"), "poi_id", "left")
            .join(bio, partner & (F.col("poi_id") == F.col("_pid")) & (F.col("lang") == F.col("_loc")), "left"))
    ctx.warn("multi_lang_source_name_null", rows.where(F.col("source_name").isNull()).count())
    description = F.when(partner, F.coalesce(F.col("bio"), F.col("description"))).otherwise(F.col("description"))
    experience = F.when(partner, F.coalesce(F.col("usps"), F.col("experience"))).otherwise(F.col("experience"))
    p1 = (rows.withColumn("description", description).withColumn("experience", experience)
          .select(*OUT_COLS))
    return p1.unionByName(_i18n_only(ctx, ml, i18n, p1.schema))


SPEC = NodeSpec(
    trg_tbl="gld_srv_poi_multi_lang",
    inputs={"multi_lang": "slv_enr_poi_info_multi_lang", "entity": "slv_poi_entity_non_enrich",
            "i18n": "slv_pn_business_service_i18ns"},
    pk=("poi_id", "lang"),
    build=build,
    required_inputs=("multi_lang", "entity"),
    write_mode="MERGE",
)
```

Notes:

- `F.lit(None)` is NullType. The cast gives it the P1 type (I6). `p1.schema` is analysis only and starts no job.
- The code, docstrings included, must not contain `deleted` or `lh_vv_gold`, and must have exactly three `live_only=False` (`test_node_specs`).
- `ml.select(*ML_COLS)` must stay before the entity join (I10).

Cell `id:srvmlmd`: append these two lines after the last line:

```
P2: dòng `slv_pn_business_service_i18ns` không có dòng `slv_enr_poi_info_multi_lang` cùng `(poi_id, lang)` vẫn ra gold: `poi_id` = `uuid_md5(business_service_id, 'partner')`, `lang` = `locale`, `source_name` = `partner`.
P2: `description` = `bio`, `experience` = `usps`, không fallback; `time_to_spend`, `best_time`, `cost_vnd` null. Khoá rỗng bị bỏ (cảnh báo `multi_lang_i18n_key_blank`).
```

### 16.2 Mapping doc (save verbatim)

FILE: docs/context/mapping_gld_srv_poi_multi_lang.md
Sau mỗi thay đổi nghiệp vụ của bảng trong file này, cùng task cập nhật file này trước review.

## 1. Table: `gld_srv_poi_multi_lang`

Lakehouse.schema: `lh_vv_gold.dbo`.

### 1.1. Xử lý

- `SPEC.inputs`: `multi_lang` = `slv_enr_poi_info_multi_lang`, `entity` = `slv_poi_entity_non_enrich`, `i18n` = `slv_pn_business_service_i18ns`. `required_inputs` = (`multi_lang`, `entity`). `i18n` không bắt buộc. Cả ba gọi `live_only=False`. `write_mode = MERGE`.
- Bảng đích có hai nhóm dòng. P1 là dòng do `slv_enr_poi_info_multi_lang` dẫn. P2 là dòng chỉ có `slv_pn_business_service_i18ns`. Notebook hợp P1 và P2 bằng `unionByName` rồi MERGE một lần.
- P1: nguồn là `slv_enr_poi_info_multi_lang` LEFT JOIN `slv_poi_entity_non_enrich` theo `poi_id`. `source_name` lấy từ entity. `slv_enr_poi_info_multi_lang` có cột `source_name` (chỉ DDL, cell `mlsrcpy` của `NB_CREATE_DDL`, chưa có writer) nhưng node không đọc cột này: `ML_COLS` không có `source_name`. `source_name` null thì notebook cảnh báo `multi_lang_source_name_null`. Cảnh báo này chỉ đếm P1.
- P1: partner là `lower(trim(source_name)) = 'partner'`. Null không phải partner.
- P1: partner LEFT JOIN `slv_pn_business_service_i18ns` khi `poi_id` bằng `uuid_md5(business_service_id, 'partner')` và `lang` = `locale`. Cùng cách `NB_SLV_POI_ENTITY_NON_ENRICH` tính `poi_id` dòng partner.
- P1: partner có `description` = `bio`, `bio` null thì `description` của enr. `experience` = `usps`, `usps` null thì `experience` của enr.
- P1: dòng không phải partner lấy `description` và `experience` của `slv_enr_poi_info_multi_lang`.
- P2: mỗi dòng `slv_pn_business_service_i18ns` tạo một dòng gold khi `slv_enr_poi_info_multi_lang` không có dòng cùng `(poi_id, lang)`, với `poi_id` = `uuid_md5(business_service_id, 'partner')` và `lang` = `locale`. So khớp bằng `left_anti` theo `(poi_id, lang)`. Không xét `source_name` của entity, nên P1 và P2 không trùng khoá.
- P2 lấy mọi `locale`. Không lọc dòng partner đã xoá, giữ như hiện tại (`live_only=False`). Dòng P2 vẫn tạo khi `bio` và `usps` cùng null.
- P2: `source_name` = `'partner'`. `description` = `bio`, `experience` = `usps`, không fallback. `time_to_spend`, `best_time`, `cost_vnd` = null. P2 không đọc `slv_poi_entity_non_enrich`. Mỗi cột P2 ép về kiểu của cột P1 cùng tên.
- P2: `business_service_id` hoặc `locale` null hoặc rỗng sau `trim` thì bỏ dòng và đếm vào cảnh báo `multi_lang_i18n_key_blank`. Số dòng P2 ghi vào cảnh báo `multi_lang_i18n_only_rows`.
- Khoá P2 có thêm dòng `slv_enr_poi_info_multi_lang` thì chuyển sang P1 (UPDATE cùng khoá). Dòng multi_lang mất mà dòng i18n còn thì chuyển sang P2. Cả hai trường hợp đều không xoá mềm.
- Bảng `slv_enr_poi_info_multi_lang` rỗng thì node vẫn FAILED vì `required_inputs`. P2 chỉ áp cho khoá không khớp, không áp cho bảng rỗng.
- MERGE theo grain `(poi_id, lang)`. `lang` nguồn `slv_enr_poi_info_multi_lang` là `STRING`; DDL landing không ghi `NOT NULL`. Target `gld_srv_poi_multi_lang.lang` là `STRING NOT NULL`. `quality_gate` trong `NB_LIB_TRANSFORM_SLV_GLD` chặn dòng khóa NULL, nên `poi_id` hoặc `lang` null thì dừng.
- `pl_name` hiện hành: `PL_VV_TRANS_SLV_TO_GLD_30M` (`plcadpy` đổi từ `PL_VV_TRANS_SLV_TO_GLD_30P`). `load_mode = RECOMPUTE`, `priority = 1`. Ba cạnh `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, `slv_pn_business_service_i18ns` → `gld_srv_poi_multi_lang`, `nb_name = NB_GLD_SRV_POI_MULTI_LANG`. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15M`.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| P1: slv_enr_poi_info_multi_lang.poi_id<br>P2: slv_pn_business_service_i18ns.business_service_id | string NOT NULL | P1: transform 1-1<br>P2: uuid_md5(business_service_id, 'partner') | poi_id |
| P1: slv_enr_poi_info_multi_lang.lang<br>P2: slv_pn_business_service_i18ns.locale | string | P1: transform 1-1<br>P2: transform 1-1, mọi locale | lang |
| P1: slv_poi_entity_non_enrich.source_name | string | P1: transform 1-1 theo poi_id<br>P2: hằng 'partner', không đọc entity | source_name |
| P1: slv_enr_poi_info_multi_lang.time_to_spend | string | P1: transform 1-1<br>P2: null | time_to_spend |
| P1: slv_enr_poi_info_multi_lang.best_time | string | P1: transform 1-1<br>P2: null | best_time |
| P1: slv_enr_poi_info_multi_lang.cost_vnd | string | P1: transform 1-1<br>P2: null | cost_vnd |
| P1: slv_pn_business_service_i18ns.bio, fallback slv_enr_poi_info_multi_lang.description<br>P2: slv_pn_business_service_i18ns.bio | string | P1: partner: bio, bio null thì description enr; nguồn khác: description enr<br>P2: bio, không fallback | description |
| P1: slv_pn_business_service_i18ns.usps, fallback slv_enr_poi_info_multi_lang.experience<br>P2: slv_pn_business_service_i18ns.usps | string | P1: partner: usps, usps null thì experience enr; nguồn khác: experience enr<br>P2: usps, không fallback | experience |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |
END_FILE

### 16.3 `NB_CREATE_DDL`: append two cells after `rvi18ngldpy`

Markdown cell, `"id": "mlsrcmd"`, `"metadata": {}`:

```
# [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr

Thêm `source_name` STRING sau `experience` trên `slv_enr_poi_info_multi_lang` (chỉ DDL, chưa có writer). Không đổi cạnh, không đổi gold. Chạy lại không đổi gì.
```

Code cell, `"id": "mlsrcpy"`. Use the same `metadata.microsoft` block as `mlexppy` (`language: python`, `language_group: synapse_pyspark`), `execution_count: null`, `outputs: []`. Source:

```python
# [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr
# Thêm source_name STRING cho phép NULL ngay sau experience trên slv_enr_poi_info_multi_lang (landing, chỉ DDL, không nạp).
# D-ML-SRC, D-ML-WRITER: không có notebook ghi cột này. D-ML-NOMATCH: gld_enr_poi_info không đọc cột này.
# Bảng chưa có -> dừng. Đúng hợp đồng -> không đổi. Thiếu đúng cột source_name -> ALTER. Lệch khác -> dừng trước khi ghi.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M suốt cell. Không ghi cạnh, không ghi bảng gold.
import uuid

WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
ML_FQ = "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang"
NEW_COL = ("source_name", "STRING")
TABLE_COLS = {
    "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang": [
        ("poi_id", "STRING NOT NULL"), ("lang", "STRING"), ("time_to_spend", "STRING"), ("best_time", "STRING"),
        ("cost_vnd", "STRING"), ("description", "STRING"), ("experience", "STRING"), ("source_name", "STRING"),
        ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
}
LOCK = "mlsrc-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


n_lock = spark.sql(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{WID}'").first()["n"]
if n_lock != 1:
    raise RuntimeError(f"{WM} không có đúng 1 dòng {WID}: chạy plcadpy trước")
held = False
failed = None
try:
    spark.sql(f"""
    UPDATE {WM}
    SET lock_exec_id = '{LOCK}', lock_at = current_timestamp(), status = 'RUNNING', updated_at = current_timestamp()
    WHERE watermark_id = '{WID}' AND (
        lock_exec_id IS NULL
        OR coalesce(lock_at < current_timestamp() - INTERVAL {LEASE_MINUTES} MINUTES, true))
    """)
    owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
    if not owner or owner["lock_exec_id"] != LOCK:
        other = None if owner is None else owner["lock_exec_id"]
        raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")
    held = True

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    want = _want(TABLE_COLS[ML_FQ])
    add = False
    if not spark.catalog.tableExists(ML_FQ):
        issues.append(f"{ML_FQ} chưa có: chạy NB_SETUP_INITIAL_DDL hoặc enrflagpy / mlexppy")
    else:
        got = _schema(ML_FQ)
        if got == [col for col in want if col[0] != NEW_COL[0]]:
            add = True
        elif got != want:
            issues.append(f"{ML_FQ} không khớp hợp đồng, không sửa: có {got}, cần {want}")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    def _refresh_lock():
        # STATE-001: gia hạn và kiểm lại chủ khoá ngay trước mỗi lần ghi.
        spark.sql(f"""
        UPDATE {WM}
        SET lock_at = current_timestamp(), updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
        owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
        if not owner or owner["lock_exec_id"] != LOCK:
            raise RuntimeError(f"Luồng {PL} mất khoá trước khi ghi")

    if add:
        names = [name for name, _dtype in TABLE_COLS[ML_FQ]]
        anchor = names[names.index(NEW_COL[0]) - 1]
        _refresh_lock()
        spark.sql(f"ALTER TABLE {ML_FQ} ADD COLUMNS (`{NEW_COL[0]}` {NEW_COL[1]} AFTER `{anchor}`)")

    # Sau khi ghi: chỉ xét phần cell thêm.
    if _schema(ML_FQ) != want:
        raise RuntimeError(f"Sau khi ghi: {ML_FQ} lệch cột")
    print(f"source_name: {'+' if add else '='}{ML_FQ}")
except Exception as exc:
    failed = exc
    raise
finally:
    if held:
        status = "FAILED" if failed else "SUCCESS"
        detail = "" if failed is None else str(failed).replace("'", " ")[:500]
        spark.sql(f"""
        UPDATE {WM}
        SET lock_exec_id = NULL, lock_at = NULL, status = '{status}', error_message = '{detail}',
            updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
```

### 16.4 `NB_SETUP_INITIAL_DDL` cell `init_tables`

In the spec `{"fq": 'lh_vv_silver.dbo.slv_enr_poi_info_multi_lang', …}`, insert one line right after its `('experience', 'STRING', None),`. This is the first occurrence. The second one belongs to `gld_srv_poi_multi_lang` and must not change.

```
        # [THÊM 04/11] 20261104-gld-srv-multi-lang-i18n-without-enr: source_name, chỉ DDL.
        ('source_name', 'STRING', None),
```

Keep the notebook's JSON source indentation. Do not add `ALTER TABLE` (`test_no_destructive_sql`).

### 16.5 `gld_enr_poi_info_review.md`

In the table row `| Nguồn đang dùng | … Không chép nội dung enrich sang gold |` (line 12), append before the closing ` |`:

`. [SỬA 04/11] \`slv_enr_poi_info_multi_lang\` có thêm cột \`source_name\` (chỉ DDL); node vẫn chỉ đọc \`poi_id\`, \`source_name\` của gold vẫn lấy \`slv_poi_entity_non_enrich.source_name\` (D-ML-NOMATCH)`

`NB_ENR_POI_INFO.ipynb` itself is not edited.

## 17. Verification

```
python -m pytest tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py -q
python -m pytest tests -q
python scripts/vv.py run-gate 20261104-gld-srv-multi-lang-i18n-without-enr
```

These must stay green without edits:

- `test_node_specs`, `test_build_columns_match_ddl`, `test_multi_lang_experience_rule`, `test_multi_lang_experience_patch`
- `test_landing_multi_lang_experience` (pins `mlexppy` history)
- `test_flag_node_contract`, `test_create_sql_renders`, `test_no_destructive_sql`

### 17.1 `tests/test_gld_srv_poi_contract.py`

Add `ML_MAPPING` after `MAPPING`. Add the three tests after `test_multi_lang_experience_rule`.

```python
ML_MAPPING = ROOT / "docs" / "context" / "mapping_gld_srv_poi_multi_lang.md"


def test_multi_lang_i18n_only_branch():
    source = _cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild")
    code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
    assert _assign(source, "MEASURE_COLS") == ("time_to_spend", "best_time", "cost_vnd")
    assert _assign(source, "I18N_ONLY_WARN") == "multi_lang_i18n_only_rows"
    assert _assign(source, "I18N_KEY_BLANK_WARN") == "multi_lang_i18n_key_blank"
    assert "source_name" not in _assign(source, "ML_COLS")
    for line in (
        'bio = i18n.select(uuid_md5(F.col("business_service_id"), F.lit(PARTNER)).alias("_pid"),',
        'partner = F.coalesce(F.lower(F.trim(F.col("source_name"))) == PARTNER, F.lit(False))',
        'rows = (ml.select(*ML_COLS).join(ent.select("poi_id", "source_name"), "poi_id", "left")',
        '.join(bio, partner & (F.col("poi_id") == F.col("_pid")) & (F.col("lang") == F.col("_loc")), "left"))',
        'ctx.warn("multi_lang_source_name_null", rows.where(F.col("source_name").isNull()).count())',
        'description = F.when(partner, F.coalesce(F.col("bio"), F.col("description"))).otherwise(F.col("description"))',
        'p1 = (rows.withColumn("description", description).withColumn("experience", experience)',
        "return p1.unionByName(_i18n_only(ctx, ml, i18n, p1.schema))",
    ):
        assert line in source
    assert code.count("unionByName") == 1
    assert 'return F.coalesce(F.trim(F.col(name).cast("string")), F.lit("")) != ""' in source
    branch = source.split("def _i18n_only", 1)[1].split("\ndef ", 1)[0]
    for line in (
        'key_ok = _filled("business_service_id") & _filled("locale")',
        "ctx.warn(I18N_KEY_BLANK_WARN, i18n.where(~key_ok).count())",
        'ml_keys = ml.select(F.col("poi_id").alias("_pid"), F.col("lang").alias("_loc"))',
        'only = keyed.join(ml_keys, ["_pid", "_loc"], "left_anti")',
        'F.lit(PARTNER).alias("source_name"), *[F.lit(None).alias(c) for c in MEASURE_COLS],',
        'F.col("bio").alias("description"), F.col("usps").alias("experience"))',
        ".select(*[F.col(c).cast(types[c]).alias(c) for c in OUT_COLS]))",
        "ctx.warn(I18N_ONLY_WARN, p2.count())",
    ):
        assert line in branch
    assert 'F.col("source_name")' not in branch and "partner &" not in branch
    assert "coalesce(F.col(" not in branch and not re.search(r"\bent\b", branch)
    assert ".isin(" not in code and '"vi"' not in code


def test_multi_lang_mapping_targets():
    text = ML_MAPPING.read_text(encoding="utf-8")
    handling = text.split("### 1.1. Xử lý", 1)[1].split("### 1.2", 1)[0]
    for token in ("left_anti", "(poi_id, lang)", "'partner'", "mọi `locale`", "chỉ DDL", "mlsrcpy",
                  "multi_lang_i18n_only_rows", "multi_lang_i18n_key_blank", "`required_inputs`"):
        assert token in handling
    table = text.split("### 1.2. Field Mapping", 1)[1]
    rows = [line.split("|")[1:-1] for line in table.splitlines() if line.startswith("|")][2:]
    out = _assign(_cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"), "OUT_COLS")
    assert [cells[3].strip() for cells in rows] == list(out) + ["created_at", "updated_at"]
    transform = {cells[3].strip(): cells[2] for cells in rows}
    for name in out:
        assert "P2:" in transform[name]
    for name in _assign(_cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"), "MEASURE_COLS"):
        assert "P2: null" in transform[name]


def test_multi_lang_source_name_patch():
    patch = _cell("NB_CREATE_DDL.ipynb", "mlsrcpy")
    ml = "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang"
    new = ("source_name", "STRING")
    assert _assign(patch, "NEW_COL") == new and _assign(patch, "ML_FQ") == ml
    tables = _assign(patch, "TABLE_COLS")
    assert list(tables) == [ml]
    base = _assign(_cell("NB_CREATE_DDL.ipynb", "mlexppy"), "TABLE_COLS")[ml]
    assert tables[ml] == _insert_after(base, "experience", new)
    assert _assign(patch, "PL") == _assign(_cell("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")[1][1]
    assert "LEASE_MINUTES = 90" in patch and "lock_exec_id = '{LOCK}'" in patch
    order = ["held = True", "Dừng trước khi ghi", "_refresh_lock()", "ALTER TABLE", "Sau khi ghi", "finally:"]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("CREATE TABLE", "INSERT INTO", "UPDATE {CFG}", "MERGE INTO", "DROP", "DELETE", "TRUNCATE",
                  "REPLACE", "RESTORE", "columnMapping", "lh_vv_gold"):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and " AFTER " in code
```

Edits to existing tests in the same file:

- `test_info_rating_patch`: shift every tail slice by 2, `ids[-18:-10]` → `ids[-20:-12]`, `[-10:-8]` → `[-12:-10]`, `[-8:-6]` → `[-10:-8]`, `[-6:-4]` → `[-8:-6]`, `ids[-4:]` → `ids[-6:-2]`, then add `assert ids[-2:] == ["mlsrcmd", "mlsrcpy"]`.
- `test_review_source_patch_cell` (last line): `ids[-4:]` → `ids[-6:-2]`, then add `assert ids[-2:] == ["mlsrcmd", "mlsrcpy"]`.

### 17.2 `tests/test_enr_poi_contract.py` and `tests/test_initial_ddl_contract.py`

- `test_info_patch_cell_guards` (lines 223–232): shift every slice by 2 (`[-28:-22]` → `[-30:-24]`, …, `ids[-4:]` → `ids[-6:-2]`), then add `assert ids[-2:] == ["mlsrcmd", "mlsrcpy"]`.
- New test, after `test_flag_node_contract`:

```python
def test_info_source_name_stays_entity():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    assert '"multi_lang": ("poi_id",),' in info
    assert 'ml = _present(ctx, "multi_lang", "poi_id", changed).alias("ml")' in info
    assert 'source = F.lower(F.trim(F.col("e.source_name")))' in info
    assert 'F.col("e.source_name").alias("source_name")' in info
    assert "ml.source_name" not in info
```

- `test_initial_ddl_contract.py` `test_columns_match_sources` (line 312) and `test_flag_patch_create_matches_init` (line 662): replace the `ml_cols` assignment with
  `{**_assign(_cell(<nb>, "mlexppy"), "TABLE_COLS"), **_assign(_cell(<nb>, "mlsrcpy"), "TABLE_COLS")}`.
  `<nb>` is `ddl` in the first test and `_notebook("NB_CREATE_DDL.ipynb")` in the second. The silver key then takes the new contract and the gold key stays `mlexppy`'s.

### 17.3 `tests/test_poi_entity_contract.py` (only after the scope approval at stop point 1)

In `test_create_ddl_patch` (lines 635–644): shift every slice by 2, as in §17.2, and add `assert ids[-2:] == ["mlsrcmd", "mlsrcpy"]`. Do not change anything else in the file.

## 18. Alternatives compared

| Option | Result | Decision |
|---|---|---|
| A. P1 unchanged ∪ P2 = guarded i18n `left_anti` ML keys, one MERGE | P1 is textually unchanged, the populations are disjoint, one commit | Selected |
| B. Full outer join of ML and i18n, then entity | Rewrites P1. A non-partner ML row plus its i18n row can emit a duplicate key | Rejected |
| C. Second MERGE or a separate node for P2 | Mutual soft-delete, two commits, or a new edge | Rejected |
| D. Blank keys passed through, or left to QG to block | Fake keys, or one bad row freezes the node | Rejected |
| E. Guard on the shared `bio` frame | Changes P1 (D-KEEP) | Rejected |
| F. P2 casts hard-coded as `"string"` | Breaks if a source type differs. Casting to `p1.schema` stays correct | Rejected |
| G. `multi_lang` made optional | An empty ML table would soft-delete every P1 key | Rejected |
| H. `mlsrcpy` inserted before `enrinfomd`, to keep out-of-scope tail tests green | It would run before `mlexppy` in cell order, and its pre-check expects `experience`. It would also break the append-only history of the patch cells | Rejected. A scope approval is requested instead |
| I. Add `source_name` inside `mlexppy` | Rewrites a cell that already ran. Dev (has `experience`, lacks `source_name`) would match neither accepted state | Rejected |
| J. `source_name` placed after `lang` (gold order) | Shifts the ordinals of five business columns for the external writer | Rejected. AFTER `experience` shifts only the system timestamps |
| K. `NB_ENR_POI_INFO` reads the new column (D-ML-GATE text) | Overridden by D-ML-NOMATCH | Rejected |
