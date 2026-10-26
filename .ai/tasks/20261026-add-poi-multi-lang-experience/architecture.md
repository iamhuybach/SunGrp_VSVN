RESULT: PASS

## Main brief

### Decision
- Append the patch pair `mlexpmd`/`mlexppy` at the end of `NB_CREATE_DDL`, after `plcadpy`. It adds `experience STRING` (nullable) `AFTER description` on `slv_enr_poi_info_multi_lang` and `gld_srv_poi_multi_lang`, under the lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`. It writes no edges and creates no tables.
- `init_tables` gets the same column in both specs. The gold build implements ledger Q1: `F.when(partner, F.coalesce(usps, experience)).otherwise(experience)`.
- Q1 supersedes the request line "no coalesce/partner branch". `experience` joins `row_hash` automatically, so no `hash_exclude` (closes model-design Q3). The column goes after `description` (closes Q4).
- Blocking: `tests/test_initial_ddl_contract.py` and `tests/test_poi_entity_contract.py` must be added to `scope.files`. They pin trailing cell ids and the `init_tables` columns.

### Invariants Main must preserve
- `srvmlbuild` `SPEC` (pk `(poi_id, lang)`, inputs, required_inputs, MERGE) is byte-identical. `test_node_specs` passes unchanged.
- `ML_COLS[-1] == OUT_COLS[-1] == "experience"`, and `list(OUT_COLS) + TECH` equals the gold names in `mlexppy` `TABLE_COLS`.
- `mlexppy` `TABLE_COLS` equals the `init_tables` specs for both tables, columns in order.
- Each `TABLE_COLS` entry equals its old contract (`enrflagpy` `LANDING_COLS[ml]` / `srvpoipy` `GOLD_COLS[ml]`) with `("experience","STRING")` inserted after `description`.
- `mlexppy` non-comment code has no `CREATE TABLE`, `INSERT INTO {CFG}`, `UPDATE {CFG}`, `MERGE INTO {WM}`, `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE` or `columnMapping`, and contains `ALTER TABLE` exactly once.
- Token order in `mlexppy`: `held = True` < `Dừng trước khi ghi` < `_refresh_lock()` < `ALTER TABLE` < `Sau khi ghi` < `finally:`.
- `mlexppy` `PL == "PL_VV_TRANS_SLV_TO_GLD_30M"` equals `plcadpy` `RENAMES[1][1]`, and `LEASE_MINUTES = 90`.
- The i18n `_require` includes `"usps"`. No trim, empty-string handling, or truncation on `usps`/`experience`.
- `enrflagpy`, `srvpoipy` and `plcadpy` cells, the `LANDING` test constant and `test_flag_patch_constants` stay unchanged.
- The cell stops before any write if a table is missing, the lock row count ≠ 1, the active `gld_srv_poi_multi_lang` edges ≠ 3 rows on 30M, or the schema is neither "before" nor "after".

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, spec `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` | add `('experience', 'STRING', None),` after `description` | spec has 9 cols |
| 2 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, spec `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | add `('experience', 'STRING', None),` after `description` | spec has 12 cols |
| 3 | notebooks/NB_CREATE_DDL.ipynb | new markdown `mlexpmd` after `plcadpy` | header `# [THÊM 26/10] 20261026-add-poi-multi-lang-experience` + one line | ids[-2] == mlexpmd |
| 4 | notebooks/NB_CREATE_DDL.ipynb | new code `mlexppy` (last cell) | per doc "NB_CREATE_DDL patch cell" | ids[-1] == mlexppy; invariants 3–7, 10 |
| 5 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | `srvmlmd` | add the `experience` rule line | text present |
| 6 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | `srvmlbuild` `ML_COLS`/`OUT_COLS`/`build` | per doc "Gold build" | invariants 1, 2, 8 |
| 7 | tests/test_gld_srv_poi_contract.py | `test_build_columns_match_ddl` | multi_lang contract from `mlexppy` `TABLE_COLS` | passes |
| 8 | tests/test_gld_srv_poi_contract.py | `test_info_rating_patch` | slices `[-12:-4]`, `[-4:-2]` plcad, `[-2:]` mlexp | passes |
| 9 | tests/test_gld_srv_poi_contract.py | new `test_multi_lang_experience_patch` | per doc "Verification" | passes |
| 10 | tests/test_gld_srv_poi_contract.py | new `test_multi_lang_experience_rule` | pin the Q1 expression, `usps` in `_require`, no `hash_exclude`, last col | passes |
| 11 | tests/test_enr_poi_contract.py | `test_info_patch_cell_guards` | shift slices by 2, add `ids[-2:] == ["mlexpmd","mlexppy"]` | passes |
| 12 | tests/test_enr_poi_contract.py | new `LANDING_ML` + `test_landing_multi_lang_experience` | `mlexppy` `TABLE_COLS[ml] == LANDING_ML`; NOT NULL only on first column | passes |
| 13 | tests/test_initial_ddl_contract.py (scope widen) | `test_columns_match_sources`, `test_flag_patch_create_matches_init`, `test_gld_srv_patch_create_matches_init` | for the two multi_lang fqs, take expected cols from `mlexppy` `TABLE_COLS` | pass |
| 14 | tests/test_initial_ddl_contract.py (scope widen) | `test_pl_cadence_patch_cell` | `ids[-4:-2] == ["plcadmd","plcadpy"]` | passes |
| 15 | tests/test_poi_entity_contract.py (scope widen) | `test_create_ddl_patch` | shift slices by 2, add the mlexp pair | passes |

### Order and stop points
1. STOP (user decision / Main): add `tests/test_initial_ddl_contract.py` and `tests/test_poi_entity_contract.py` to `scope.files`. Optionally add `docs/context/mapping_gld_srv_poi_multi_lang.md` for an `experience` row in §1.2; otherwise log it as backlog in `decision.md`.
2. STOP (evidence): the task `20261026-pl-name-cadence-suffix` must be committed first, because its files overlap and `mlexppy` depends on `plcadpy` being the previous cell.
3. Rows 1–2, then rows 3–4, then rows 5–6, then rows 7–15.
4. Run pytest. If any failure is outside rows 7–15, stop and report it.
5. Main writes the task `runtime-runbook.md` from doc "Rollout" (R0, P1, R1–R6).
6. STOP (runtime, user in DEV):
   - R0: the lock row exists.
   - P1: `usps string`.
   - R1: run `mlexppy`, then rerun it and expect `+[]`.
   - R2: `DESCRIBE` both tables.
   - R3: `NB_SETUP_INITIAL_DDL` `p_apply="false"` returns PLAN.
   - R4: publish the gold notebook, then run GLD-30M.
   - R5: mismatch = 0.
   - R6: updated ≈ nonnull, no duplicate PKs.
   - Do not publish the gold notebook before R1. Do not mark runtime as passed.

### Tests and verification
- `python -m pytest tests -q` (full run; the cell-order pins span several files).
- Focused runs:
  - `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py -q`
  - `python -m pytest tests/test_gld_srv_poi_contract.py::test_multi_lang_experience_patch tests/test_gld_srv_poi_contract.py::test_multi_lang_experience_rule tests/test_gld_srv_poi_contract.py::test_build_columns_match_ddl tests/test_gld_srv_poi_contract.py::test_node_specs tests/test_enr_poi_contract.py::test_landing_multi_lang_experience tests/test_enr_poi_contract.py::test_info_patch_cell_guards tests/test_initial_ddl_contract.py::test_columns_match_sources tests/test_initial_ddl_contract.py::test_pl_cadence_patch_cell tests/test_poi_entity_contract.py::test_create_ddl_patch -q`
- Runtime: doc "Runtime rule check" (PySpark probe; expect `mismatch 0`).

### Read only if needed
- "Scope" and "Alternatives" → stop 1, rows 13–15 (why the out-of-scope tests must change)
- "Selected design / NB_CREATE_DDL patch cell" → rows 3–4
- "Selected design / Gold build" → rows 5–6
- "Selected design / NB_SETUP_INITIAL_DDL init_tables" → rows 1–2
- "Grain and keys" (row_hash) → row 10 (no `hash_exclude`)
- "Ordering", "Concurrency" → stop 2, stop 6
- "Partial failure", "Rollback and forward recovery" → stop 6 failures
- "Rollout", "Runtime rule check" → stop 5–6
- "Verification" → rows 7–15

# Architecture — 20261026-add-poi-multi-lang-experience

## Basis

- Grain and keys: `model-design.md` `## Entities and grain` and `## Keys`. Gold `(poi_id, lang)` and the landing table are unchanged. This document does not add to the model design.
- Mapping rule: `decision.md` `## Quyết định hiện hành` Q1 (option 4). This replaces model-design `## Conflicts and questions` item 1. It also replaces the request acceptance line "No coalesce, fallback, … partner / non-partner branch", because the user chose a partner branch with a null fallback. Reviewers check against Q1, not that request line.
- Model-design questions closed here: Q3 (`row_hash`) in "Grain and keys". Q4 (column position) in "Selected design". Q2 (landing writer) stays out of scope, as the request says. Q5 (mapping doc) is in "Scope".

## Scope

- `NB_CREATE_DDL`: add one patch cell pair at the end, `mlexpmd` + `mlexppy`, after `plcadpy`. It adds `experience STRING` (nullable) `AFTER description` on `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` and on `lh_vv_gold.dbo.gld_srv_poi_multi_lang`.
- `NB_SETUP_INITIAL_DDL` cell `init_tables`: add `('experience', 'STRING', None)` after `description` in both table specs.
- `NB_GLD_SRV_POI_MULTI_LANG` cells `srvmlmd` and `srvmlbuild`: read `usps`, emit `experience` per Q1.
- Tests: `tests/test_gld_srv_poi_contract.py` and `tests/test_enr_poi_contract.py` (both in scope).
- **Scope widening required (blocking):** `tests/test_initial_ddl_contract.py` and `tests/test_poi_entity_contract.py`. Today they break as soon as a cell is appended to `NB_CREATE_DDL` or a column is added to `init_tables`:
  - `test_initial_ddl_contract.py::test_pl_cadence_patch_cell` pins `ids[-2:] == ["plcadmd", "plcadpy"]`.
  - `test_initial_ddl_contract.py::test_columns_match_sources`, `::test_flag_patch_create_matches_init` and `::test_gld_srv_patch_create_matches_init` compare `init_tables` against `enrflagpy` `LANDING_COLS` and `srvpoipy` `GOLD_COLS`.
  - `test_poi_entity_contract.py::test_create_ddl_patch` pins the trailing cell ids.
  - No design meets the request without editing these tests (see "Alternatives").
- Recommended, not blocking: add an `experience` row to `docs/context/mapping_gld_srv_poi_multi_lang.md` §1.2. No test reads that table. If scope is not widened, record it as backlog in `decision.md`.

## Non-goals

- No writer for `slv_enr_poi_info_multi_lang`, and no backfill of `experience` on the landing table.
- No new input, ctrl edge, watermark, pipeline JSON, or lib change. No `hash_exclude`.
- No trim, empty-string handling, truncation, or dedup for `usps` / `experience`. An empty-string `usps` wins over the enr value, because Q1 says "khi usps null".
- Old cells `enrflagpy` and `srvpoipy` are not edited, and their constants stay as history.

## Invariants

1. Gold PK stays `(poi_id, lang)`. `SPEC.pk`, `inputs`, `required_inputs` and `write_mode="MERGE"` do not change.
2. `experience` on a gold row = `coalesce(usps, enr.experience)` when `coalesce(lower(trim(source_name)) = 'partner', false)`; otherwise `enr.experience`. `usps` comes from the existing i18n left join on `(_pid, _loc) = (poi_id, lang)`, which is applied only to partner rows.
3. Both new columns are `STRING`, nullable, and directly after `description`. Gold DDL order = `OUT_COLS + (row_hash, created_at, updated_at, deleted_at)`.
4. `NB_CREATE_DDL` `mlexppy` `TABLE_COLS` equals the `init_tables` spec for both tables, column for column and in order.
5. `mlexppy` does not create tables. It writes no ctrl config rows and runs no DROP, DELETE, TRUNCATE, REPLACE, RESTORE, or columnMapping. Its only writes are at most two `ALTER TABLE … ADD COLUMNS`, plus the lock row of `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`.
6. Every ALTER runs while the cell holds that lock, and is preceded by `_refresh_lock()`.
7. A rerun after success changes nothing. A table whose schema is neither "before" nor "after" stops the cell before any write.
8. The gold build fails closed (`ConfigError`, no write) if `experience` is missing on the landing table or `usps` is missing on i18n.

## State ownership

| State | Owner | This task |
|---|---|---|
| `slv_enr_poi_info_multi_lang` schema | DDL notebooks; rows come from an external writer | `mlexppy` ALTER |
| `slv_enr_poi_info_multi_lang` rows | external, unknown (model-design Q2) | none |
| `gld_srv_poi_multi_lang` schema | DDL notebooks (lib `ensure_target` is only a fallback) | `mlexppy` ALTER |
| `gld_srv_poi_multi_lang` rows | `NB_GLD_SRV_POI_MULTI_LANG` via lib `run_node` MERGE | new column value |
| `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` lock | GLD orchestrator; DDL cells borrow it | held while the cell runs |
| `ctrl_mng_pipeline_config` edges | `srvpoipy` / `plcadpy` / seed | read-only check |

## Grain and keys

- Grain and keys: see `model-design.md` `## Entities and grain` and `## Keys`. Unchanged.
- The i18n join cannot fan out. i18n's business key is `(business_service_id, locale)`, so `(uuid_md5(business_service_id,'partner'), locale)` is unique. The lib exit quality gate already blocks duplicate PKs.
- `row_hash` (model-design Q3): lib `add_row_hash` hashes every build column not in `hash_exclude`, and the hash is `sha2(to_json(struct(...)))`. `experience` joins the hash automatically, and it should, because it is a business column. Spark `to_json` drops null fields by default, so rows whose new `experience` is null should keep their old hash. Only rows with a non-null `experience` should UPDATE on the first run. This bounds churn, but it is expected behaviour, not a guarantee. Runtime step R6 measures it.

## Selected design

### Column position (model-design Q4)

The new column goes directly after `description` on both tables, using `ALTER TABLE … ADD COLUMNS (`experience` STRING AFTER `description`)`:
- One anchor rule covers both tables.
- On gold, it keeps business columns ahead of the four technical columns, which is what `test_build_columns_match_ddl` requires.
- On the landing table, it sits next to its sibling text column.
- `ADD COLUMNS … AFTER` has already run on DEV through `srvratepy` and `enrflagpy`.

### Gold build (`srvmlbuild`)

Replace the constants and the body of `build` as below. Everything else in the cell stays.

```python
PARTNER = "partner"
ML_COLS = ("poi_id", "lang", "time_to_spend", "best_time", "cost_vnd", "description", "experience")
OUT_COLS = ("poi_id", "lang", "source_name", "time_to_spend", "best_time", "cost_vnd", "description", "experience")
```

```python
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
    return (rows.withColumn("description", description).withColumn("experience", experience)
            .select(*OUT_COLS))
```

`srvmlmd`: after the `description` line, add the line ``Partner: `experience` = `usps`; khi `usps` null thì lấy `experience` của `slv_enr_poi_info_multi_lang`. Nguồn khác lấy `experience` của enr.``

### NB_CREATE_DDL patch cell (`mlexpmd`, `mlexppy`)

`mlexpmd` (markdown): `# [THÊM 26/10] 20261026-add-poi-multi-lang-experience`, then one line: ``Thêm `experience` STRING sau `description` trên `slv_enr_poi_info_multi_lang` và `gld_srv_poi_multi_lang`. Không tạo bảng, không đổi cạnh. Chạy lại không đổi gì.``

`mlexppy` follows `srvratepy`, with three deliberate differences:
- It does not MERGE-create the lock row. A missing lock row means `plcadpy` has not been applied, so the cell stops.
- It does not write edges.
- It ALTERs two tables.

Dict keys and `NEW_COL` are literals so that tests can `ast.literal_eval` them.

```python
# [THÊM 26/10] 20261026-add-poi-multi-lang-experience
# Thêm experience STRING cho phép NULL ngay sau description:
#   slv_enr_poi_info_multi_lang (landing, chỉ DDL, không nạp) và gld_srv_poi_multi_lang (trước row_hash).
# Bảng chưa có -> dừng. Đúng hợp đồng -> không đổi. Thiếu đúng cột experience -> ALTER. Lệch khác -> dừng trước khi ghi.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M (tên sau plcadpy) suốt cell. Không ghi cạnh.
# Sau cell này không chạy lại enrflagpy, srvpoipy: hợp đồng hai bảng trong đó là bản cũ.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
NEW_COL = ("experience", "STRING")
TABLE_COLS = {
    "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang": [
        ("poi_id", "STRING NOT NULL"), ("lang", "STRING"), ("time_to_spend", "STRING"), ("best_time", "STRING"),
        ("cost_vnd", "STRING"), ("description", "STRING"), ("experience", "STRING"),
        ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
    "lh_vv_gold.dbo.gld_srv_poi_multi_lang": [
        ("poi_id", "STRING NOT NULL"), ("lang", "STRING NOT NULL"), ("source_name", "STRING"),
        ("time_to_spend", "STRING"), ("best_time", "STRING"), ("cost_vnd", "STRING"), ("description", "STRING"),
        ("experience", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
    ],
}
EDGES_KEEP = ("slv_enr_poi_info_multi_lang", "slv_poi_entity_non_enrich", "slv_pn_business_service_i18ns")
LOCK = "mlexp-" + uuid.uuid4().hex
```

The rest of the cell, in this order. The token strings in quotes are what the tests check.

1. `_want`, `_schema`, `_refresh_lock`: identical to `srvratepy`. `_edge_rows()`: the `srvratepy` query with `trg_tbl = 'gld_srv_poi_multi_lang'`.
2. Lock row check: if `SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{WID}'` is not 1, raise ``f"{WM} không có đúng 1 dòng {WID}: chạy plcadpy trước"``.
3. `held = False`, `failed = None`, then `try:`. Acquire the lock with the `srvratepy` UPDATE (`lock_exec_id IS NULL OR` lease expired), read back the owner, then `held = True`.
4. `# Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.` Collect `issues` and `add = []`:
   - For each `fq, cols` in `TABLE_COLS`:
     - Table missing: add issue ``f"{fq} chưa có: chạy NB_SETUP_INITIAL_DDL hoặc enrflagpy / srvpoipy"``.
     - Otherwise let `got = _schema(fq)` and `want = _want(cols)`:
       - `got == want`: nothing to do.
       - `got == [c for c in want if c[0] != NEW_COL[0]]`: `add.append(fq)`.
       - Anything else: add issue ``f"{fq} không khớp hợp đồng, không sửa: có {got}, cần {want}"``. This includes `experience` appended after `deleted_at` by the lib.
   - Edges: from `_edge_rows()`:
     - An active row on another `pl_name` is an issue.
     - The active rows must equal `{(PL, SLV, src, 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_MULTI_LANG") for src in EDGES_KEEP}`, each with `n == 1`. Otherwise add an issue. This proves `plcadpy` was applied and that the lock guards the node that writes the table.
   - If there are issues, raise `"Dừng trước khi ghi: " + "; ".join(issues)`.
5. Writes:
   - Loop `for fq in add:` in `TABLE_COLS` order (landing first, then gold).
   - Call `_refresh_lock()`, then run ``spark.sql(f"ALTER TABLE {fq} ADD COLUMNS (`{NEW_COL[0]}` {NEW_COL[1]} AFTER `{anchor}`)")``.
   - Set `anchor` to the name just before `NEW_COL[0]` in `TABLE_COLS[fq]`, which is `description`.
   - The text `ALTER TABLE` must appear exactly once in non-comment code.
6. `# Sau khi ghi: chỉ xét phần cell thêm.`
   - Every table must have `_schema(fq) == _want(cols)`, and the active edges must be unchanged. Otherwise raise `"Sau khi ghi: …"`.
   - Print ``f"experience: +{add}"``.
7. `except Exception as exc: failed = exc; raise`, then `finally:`. If `held`, release with the `srvratepy` UPDATE: `lock_exec_id = NULL`, status SUCCESS/FAILED, error message truncated to 500 characters, and `WHERE … AND lock_exec_id = '{LOCK}'`.

### NB_SETUP_INITIAL_DDL `init_tables`

In the spec `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang`, add `('experience', 'STRING', None),` after `('description', 'STRING', None),`. Do the same in the spec `lh_vv_gold.dbo.gld_srv_poi_multi_lang`. Nothing else changes, and the table count stays 21.

## Alternatives

| Option | Result | Decision |
|---|---|---|
| A. New trailing patch cell with `ADD COLUMNS … AFTER description`, under the GLD-30M lock, plus `init_tables` and build edits | Existing DEV tables get the column in contract order. Fresh environments get it from `init_tables`. Two out-of-scope tests need edits that only shift indices and swap sources. | **Selected** |
| B. Edit `enrflagpy` `LANDING_COLS` / `srvpoipy` `GOLD_COLS` in place | `CREATE TABLE IF NOT EXISTS` never alters existing DEV tables, so DEV keeps the old schema. Breaks the append-only history convention and `test_flag_patch_constants`. | Rejected |
| C. Let lib `ensure_target` auto-add the gold column at the first run | The column lands after `deleted_at`, so the DDL contract and `OUT_COLS + TECH` diverge. The landing table still needs DDL. | Rejected |
| D. Append the column at the end of the table (no `AFTER`), as `ohpasspy` / `srvpoipy` did for landing tables | Avoids `AFTER`, but gold would end up after `deleted_at`. Using a different position per table adds a second rule for no benefit. | Rejected |
| E. Also hold the ENR-15M lock | ENR nodes only read `poi_id` from the landing table. A metadata commit does not conflict with Delta readers, and `srvpoipy` set the precedent of altering a landing table under the GLD lock only. | Rejected: more lock contention for no gain |

## Ordering

1. The task `20261026-pl-name-cadence-suffix` (uncommitted in the working tree) must be committed first. Its `plcadpy` must also have run in DEV. `mlexppy` depends on that cell's id position and on the 30M lock and edge names.
2. Repository: `init_tables` and the `mlexppy` cell, then the gold build, then the tests. Commit everything together.
3. DEV runtime:
   - First run `mlexppy`.
   - Then run `NB_SETUP_INITIAL_DDL` with `p_apply="false"`.
   - Only then publish the new `NB_GLD_SRV_POI_MULTI_LANG`. If the new build is published before the ALTER, every GLD run fails closed at `_require` (no write) until the cell runs.
   - If the lib's `ensure_target` ran first through some other path, the patch-cell precheck stops on the wrong position. Recovery is in "Rollback and forward recovery".

## Transaction and commit boundaries

- Each `ALTER TABLE` is one atomic Delta metadata commit. The cell makes two independent commits (landing, then gold) and no ctrl writes. Lock acquire and release are single UPDATEs on `ctrl_mng_watermark`.
- The gold MERGE is one Delta commit per run, done by the lib. The build change adds no new commit.

## Idempotency

- `mlexppy`: each table is in one of three states: "before" (ALTER it), "after" (no-op), or other (stop). A rerun after success prints `+[]` and writes only the lock row.
- Gold: RECOMPUTE MERGE on `row_hash`. With unchanged inputs, a rerun yields zero inserts and zero updates.

## Concurrency

- ALTER on gold and a running gold MERGE are mutually excluded by `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`. The edge check proves the node is on that flow.
- ALTER on the landing table and readers (ENR-15M `NB_ENR_POI_INFO`, GLD `NB_GLD_SRV_POI_INFO` and this node): readers use snapshots and select only `poi_id` or explicit columns, so they are unaffected.
- Remaining risk: an external writer committing to the landing table during the ALTER can hit a Delta metadata-change conflict and must retry. There is no in-repo writer to lock. Run the cell outside the external load window if one is known.

## Retry and recovery

- Lock busy: the cell raises `đang giữ khoá … chạy lại sau`. Rerun later; the lease is 90 minutes.
- Cell crash after the lock was taken: `finally` releases the lock. A hard kernel death leaves the lock to expire through the lease, as in precedent cells.
- Gold node failure: the orchestrator's existing retry and FAILED handling apply. The build has no new retry logic.

## Partial failure

| Point | State | Next action |
|---|---|---|
| Landing ALTER done, gold ALTER failed | Landing "after", gold "before" | Rerun the cell; it ALTERs gold only |
| Both ALTERs done, post-check failed | Schemas differ from the contract | Stop. Inspect `DESCRIBE` and fix by hand with user approval. The cell does not repair. |
| New column present, old build still published | The lib WARNs about an extra target column, and gold `experience` stays NULL | Publish the new build |
| New build published, landing ALTER missing | `ConfigError` "thiếu ['experience']", node FAILED, no write | Run `mlexppy` |
| i18n has no `usps` column | `ConfigError`, node FAILED, no write | Probe P1. The silver partner loader owns this column. |

## Observability

- The cell prints `experience: +[...]` and records SUCCESS or FAILED with the error on the wm_flow row.
- The gold node reports through the existing `ctrl_log_table_run` inserted, updated and deactivated counts, plus the existing `multi_lang_source_name_null` warn. No new warn is added, because Q1 defines no failure condition for `experience`.
- Runtime probes R5 and R6 cover the rule and the churn.

## Security

Not applicable: all SQL text is built from literals in the cell. There are no new parameters, secrets, or permissions, and the data is non-sensitive descriptive text.

## Rollout

The user runs these steps in Fabric DEV. This session must not mark runtime as passed.

- R0: `SELECT watermark_id, lock_exec_id FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'`. Expect 1 row with a null lock. This is the `plcadpy` precondition.
- P1: `DESCRIBE lh_vv_silver.dbo.slv_pn_business_service_i18ns`. Expect `usps string`. If it is absent or has another type, stop and return to Main.
- R1: run `NB_CREATE_DDL` cell `mlexppy` only. Expect `experience: +['lh_vv_silver…', 'lh_vv_gold…']`. Rerun it and expect `+[]`.
- R2: `DESCRIBE` both tables. `experience string` must come directly after `description`.
- R3: `NB_SETUP_INITIAL_DDL` with `p_apply="false"`. Expect status `PLAN` and no schema issues.
- R4: publish `NB_GLD_SRV_POI_MULTI_LANG` and run the GLD-30M flow once. Expect the node to succeed.
- R5: run the rule check below. Expect `0`.
- R6: compare the R4 `ctrl_log_table_run` `updated` count with the R5 `nonnull` count. Expected: `updated` ≈ `nonnull` (plus genuine source changes), `inserted` = 0 with unchanged sources, and PK duplicates = 0 (`SELECT poi_id, lang, count(*) … GROUP BY … HAVING count(*) > 1` returns no rows).

### Runtime rule check

```python
%run NB_LIB_TRANSFORM_SLV_GLD
g = spark.table("lh_vv_gold.dbo.gld_srv_poi_multi_lang").where("deleted_at IS NULL")
ml = spark.table("lh_vv_silver.dbo.slv_enr_poi_info_multi_lang").select("poi_id", "lang", F.col("experience").alias("ml_exp"))
pn = spark.table("lh_vv_silver.dbo.slv_pn_business_service_i18ns").select(
    uuid_md5(F.col("business_service_id"), F.lit("partner")).alias("poi_id"), F.col("locale").alias("lang"), "usps")
j = g.join(ml, ["poi_id", "lang"], "left").join(pn, ["poi_id", "lang"], "left")
partner = F.coalesce(F.lower(F.trim(F.col("source_name"))) == "partner", F.lit(False))
want = F.when(partner, F.coalesce(F.col("usps"), F.col("ml_exp"))).otherwise(F.col("ml_exp"))
print("mismatch", j.where(~F.col("experience").eqNullSafe(want)).count())  # cần 0
print("nonnull", g.where(F.col("experience").isNotNull()).count())
j.groupBy(partner.alias("partner"), F.col("usps").isNotNull().alias("usps"), F.col("ml_exp").isNotNull().alias("ml")).count().show()
```

## Rollback and forward recovery

- Forward recovery is preferred: fix the build and rerun.
- The column cannot be dropped. Precedent forbids `columnMapping` and `DROP COLUMNS` in cells, and the column is additive and nullable, so leaving it is harmless.
- Code rollback: revert `srvmlbuild`. The lib then WARNs about an extra target column, and the MERGE stops touching `experience`, so values from the last run stay stale. To clear them, the user runs this by hand and confirms first: `UPDATE lh_vv_gold.dbo.gld_srv_poi_multi_lang SET experience = NULL` while holding the GLD-30M lock. This is not part of the cell.
- Wrong position from the lib auto-add (Alternative C happened by accident): stop. Recovery needs a user-approved manual step, so record it in `decision.md` before acting.

## Implementation plan

1. Main widens `scope.files` with `tests/test_initial_ddl_contract.py` and `tests/test_poi_entity_contract.py`, and optionally the mapping doc. Confirm the plcad task is committed.
2. `NB_SETUP_INITIAL_DDL` `init_tables`: the two spec lines.
3. `NB_CREATE_DDL`: append `mlexpmd` and `mlexppy` after `plcadpy`.
4. `NB_GLD_SRV_POI_MULTI_LANG`: `srvmlmd` line and `srvmlbuild` per "Gold build".
5. Tests per "Verification".
6. `pytest`. Main writes the runtime runbook from "Rollout" into the task `runtime-runbook.md`.

## Verification

Static checks (no Spark), as part of the full `python -m pytest tests -q`:

- `tests/test_gld_srv_poi_contract.py`
  - `test_build_columns_match_ddl`: take the `gld_srv_poi_multi_lang` contract from `_assign(_cell("NB_CREATE_DDL.ipynb", "mlexppy"), "TABLE_COLS")`.
  - `test_info_rating_patch`: change to `ids[-12:-4] == [srvpoimd … amenddlpy]`, `ids[-4:-2] == ["plcadmd", "plcadpy"]` and `ids[-2:] == ["mlexpmd", "mlexppy"]`.
  - New `test_multi_lang_experience_patch`:
    - `NEW_COL == ("experience", "STRING")`.
    - Each `TABLE_COLS` entry equals its old contract with `NEW_COL` inserted right after `description`. The old contracts are `enrflagpy` `LANDING_COLS[ml]` and `srvpoipy` `GOLD_COLS[ml]`.
    - `PL` equals `plcadpy` `RENAMES[1][1]`, and `LEASE_MINUTES = 90`.
    - Token order: `held = True` < `Dừng trước khi ghi` < `_refresh_lock()` < `ALTER TABLE` < `Sau khi ghi` < `finally:`.
    - Non-comment code contains none of `CREATE TABLE`, `INSERT INTO {CFG}`, `UPDATE {CFG}`, `MERGE INTO {WM}`, `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE` or `columnMapping`.
    - `ALTER TABLE` appears once, ` AFTER ` is present, and `lock_exec_id = '{LOCK}'` is present.
  - New `test_multi_lang_experience_rule`:
    - `ML_COLS[-1] == OUT_COLS[-1] == "experience"`.
    - `F.when(partner, F.coalesce(F.col("usps"), F.col("experience"))).otherwise(F.col("experience"))` is in `srvmlbuild`.
    - The `_require` tuple for i18n contains `"usps"`.
    - `hash_exclude` is not in `srvmlbuild`.
    - `test_node_specs` stays unchanged and still passes.
- `tests/test_enr_poi_contract.py`
  - `test_info_patch_cell_guards`: shift every slice by 2 and add `ids[-2:] == ["mlexpmd", "mlexppy"]`.
  - New `LANDING_ML` constant (the `LANDING[ml]` list with `("experience", "STRING")` after `description`) and new `test_landing_multi_lang_experience`:
    - `mlexppy` `TABLE_COLS[ml] == LANDING_ML`.
    - The first column is NOT NULL, all others nullable, and no column is UNIQUE.
  - `LANDING` and `test_flag_patch_constants` stay unchanged, because they are history.
- `tests/test_initial_ddl_contract.py` (after the scope is widened)
  - `test_columns_match_sources`, `test_flag_patch_create_matches_init` and `test_gld_srv_patch_create_matches_init`: for the two multi_lang tables, take the expected columns from `mlexppy` `TABLE_COLS`.
  - `test_pl_cadence_patch_cell`: `ids[-4:-2] == ["plcadmd", "plcadpy"]`.
- `tests/test_poi_entity_contract.py::test_create_ddl_patch` (after the scope is widened): shift the slices by 2 and add the `mlexp` pair.

Runtime: R0–R6 above. These are the user's steps in DEV.
