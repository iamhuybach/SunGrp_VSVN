RESULT: PASS

## Main brief

### Decision
New ref table `lh_vv_silver.dbo.ref_dictionary_place_type`, created and seeded insert-only by a new `NB_SETUP_POI_ENTITY` (`p_apply` defaults to false). New L2 node `slv_poi_entity`, built by a new `NB_SLV_POI_ENTITY` on `NB_LIB_TRANSFORM_SLV_GLD` (MERGE on `row_hash`, pk `poi_id`). The node is wired by two `RECOMPUTE` edges under a new, unscheduled `PL_VV_TRANS_SLV_TO_SLV_1H`. The seed is a literal in the notebook, and a local test checks it against an independent parser of `mapping_place_type.md`. Category resolution is a broadcast join: `primary_type` first, then `posexplode(types_json)` + `min_by(pos)`, then `other`/`other`/NULL. No pipeline JSON, no `NB_CREATE_DDL` change, and no `ref_business_category` change.

### Invariants Main must preserve
- `SEED_ROWS` equals `parse_mapping(md)[0]`, element by element and in order. `validate_seed` passes.
- No `place_type` in {`Partner Portal bổ sung`, `Partner Portal Bổ sung`, `Fallback`, `Không có`}. Dropping one cell never drops the other column of the same row. `extended_stay_hotel` is `google` only.
- `(source_name, place_type)` is unique. Google tokens match `^[a-z0-9_]+$`. Sectors are only the seven normalized values.
- The seed is one MERGE with `WHEN NOT MATCHED` only and `updated_at = current_timestamp()`, so a rerun inserts 0 rows and there is one timestamp per seed run.
- The entity keeps every `slv_3p_poi` column except `created_at`/`updated_at` (the lib owns those names), in source order, then the 3 category columns. The column list is dynamic, not hard-coded.
- Rows: only `lower(trim(source_name)) = 'google'`. Dictionary: `source_name = google` and `is_active = true`. Keys are compared as `lower(trim())` on both sides.
- All three category columns come from one branch, chosen by whether the struct is NULL (`_p`, then `_m`, then default). Never coalesce column by column.
- `posexplode` (not `_outer`) and `min_by(_cat, _pos)`. On the unmatched branch, `business_category_vi` is `CAST(NULL AS STRING)`.
- The node fails closed: a duplicate google key in the dictionary, a category/tech column clash in `slv_3p_poi`, or 0 google rows when the input is non-empty each raise before any write.
- Edge insert uses `NOT EXISTS` and raises if `slv_poi_entity` already belongs to another active `pl_name`.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | `.ai/tasks/20261016-ref-place-type-poi-entity/task-state.yaml` | `scope.files` | Add the paths in full doc §15 | `vv.py verify` accepts the scope |
| 2 | `docs/context/3p-google/mapping_place_type.md` | §1.2 Fast Food row | `shawarma_restaurant. hamburger_restaurant` → `shawarma_restaurant, hamburger_restaurant` (only if U3(a) is approved) | Parser raises no bad-token error |
| 3 | `tests/test_poi_entity_contract.py` | new file; `parse_mapping` | Parser exactly as in full doc §7.1, plus the 8 tests in §17.1 | Tests collect; parser output is used to generate the literal |
| 4 | `notebooks/NB_SETUP_POI_ENTITY.ipynb` | new; parameter cell | `p_apply = "false"` | Test asserts it |
| 5 | same | `# BEGIN_PLACE_TYPE_SEED` … `# END_PLACE_TYPE_SEED` | `SEED_SECTORS`, `SEED_SKIP`, `SEED_ROWS` (5-tuples), `validate_seed` (full doc §9 step 3) | `test_seed_matches_mapping_file` passes |
| 6 | same | DDL cell | `CREATE TABLE IF NOT EXISTS` from full doc §6, then a schema and nullability check that raises `ConfigError` | `test_setup_contract` passes |
| 7 | same | seed cell | MERGE from full doc §9 step 6, then the post-check from step 7 (dup = 0, all keys present, drift counted only) | Same |
| 8 | same | edges cell | Owner pre-check, then the INSERT from full doc §9 step 8; exit JSON | Same |
| 9 | `notebooks/NB_SLV_POI_ENTITY.ipynb` | new; `build`, `SPEC` | Code exactly as in full doc §8.1; cell layout and Fabric metadata copied from `NB_SLV_PN_POI` | `test_entity_node_contract` passes |
| 10 | `docs/context/01_DATA_MODEL.md` | §6 table and §6.1 table | Add a `slv_poi_entity` row (grain `poi_id`, inputs, created_at/updated_at = entity lifecycle) and a `ref_dictionary_place_type` row (key, seed counts) | Rows present |
| 11 | `docs/context/CTRL_TABLES_CONTEXT.md` | §3 "Dữ liệu hiện có" | Add the 2 edges of `PL_VV_TRANS_SLV_TO_SLV_1H` (unscheduled, run manually) | Rows present |

### Order and stop points
1. **STOP S0 (user decision):** ask the user about U1–U4 (full doc §3) and record the answers in `decision.md`. Recommended: U1(a) §1.7 `business_category` = Fabric Enum, `vi` NULL, google rows only; U2(a) first occurrence in document order wins; U3(a) fix the md comma; U4(a) lib-owned `created_at`/`updated_at`. Do not write `SEED_ROWS` before the answers.
2. Edit row 1, then row 2 if U3(a).
3. Row 3. Run the parser and paste its output as `SEED_ROWS` (row 5). If the counts differ from 297 google / 59 partner (under the recommended choices), **STOP and report the difference**. Do not edit the expected numbers to match.
4. Rows 4–8, then row 9.
5. Rows 10–11.
6. Run the tests and `vv.py verify`, then go to review.
7. **STOP S1 (user, Fabric DEV, later runbook):** setup with `p_apply=false`, then `true`; node `DRY_RUN`, then `RUN`; read-only checks from full doc §17.2. Not part of this phase.

### Tests and verification
- `python -m pytest tests/test_poi_entity_contract.py -q`, covering `test_seed_matches_mapping_file`, `test_seed_excludes_placeholders`, `test_seed_keys_unique_and_tokens_valid`, `test_seed_sector_normalization`, `test_seed_conflicts_pinned`, `test_seed_counts`, `test_entity_node_contract`, `test_setup_contract`.
- `python -m pytest -q` (the whole suite stays green).
- `python scripts/vv.py verify 20261016-ref-place-type-poi-entity`.

### Read only if needed
- §3 Open user decisions → stop S0, rows 2, 5
- §4 Invariants, §6 Grain and keys → rows 6, 9
- §7 Seed parsing rules, §7.1 Parser → rows 3, 5
- §8.1 `build` and `SPEC` → row 9
- §9 Setup notebook → rows 4–8
- §10 Ordering/idempotency, §11 Recovery → rows 7, 8, 9
- §14 Alternatives → justification for rows 8, 9 and the flow choice
- §15 Rollout, §16 Rollback → row 1, stop S1
- §17 Verification → test file, stop S1

# Architecture: 20261016-ref-place-type-poi-entity

## 1. Scope

- New ref table `lh_vv_silver.dbo.ref_dictionary_place_type` with the seven requested columns, created and seeded once by a new manual setup notebook `notebooks/NB_SETUP_POI_ENTITY.ipynb`.
- New silver L2 node `lh_vv_silver.dbo.slv_poi_entity`, Google only, built by a new node notebook `notebooks/NB_SLV_POI_ENTITY.ipynb` on the existing `NB_LIB_TRANSFORM_SLV_GLD` node framework (`NodeSpec`, `run_node`, MERGE on `row_hash`).
- Two `RECOMPUTE` edges in `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` (`slv_3p_poi` → `slv_poi_entity`, `ref_dictionary_place_type` → `slv_poi_entity`) under a new, unscheduled flow `PL_VV_TRANS_SLV_TO_SLV_1H`. The node framework cannot run a node without its edges (`_resolve_node` requires exactly one active owner).
- A local contract test `tests/test_poi_entity_contract.py` that parses `docs/context/3p-google/mapping_place_type.md` independently and checks that it equals the notebook seed literal.
- Context doc rows: `docs/context/01_DATA_MODEL.md` §6 and §6.1, and `docs/context/CTRL_TABLES_CONTEXT.md` §3 "Dữ liệu hiện có".

`scope.files` is empty today. Before any edit, Main must add the paths listed in §15. No `FILE:` blocks are emitted for that reason.

## 2. Non-goals

- No change to `ref_business_category`, N2 `slv_poi`, extract notebooks, `NB_LIB_*`, `NB_CREATE_DDL`, or any pipeline JSON.
- No Fabric pipeline or schedule for `PL_VV_TRANS_SLV_TO_SLV_1H`. Scheduling needs a later task that includes a pipeline review.
- No partner rows in the entity, no Vietnamese label on the unmatched branch, and no sectors beyond the seven.
- The seed does not update rows that already exist. Changing a mapping later means editing the ref row (see §11).

## 3. Open user decisions (stop S0, before the seed literal is written)

The mapping file has four cases the request does not settle. Each recommended default is mechanical and invents no labels. The test pins whichever option the user chooses.

| ID | Case in `mapping_place_type.md` | Options | Recommended |
|---|---|---|---|
| U1 | §1.7 has no `Hiển thị (VI/EN)` columns. Its columns are `Nhóm địa điểm (Category)`, `Fabric Enum`, `Google Place API - Place Types`. | (a) `business_category` = Fabric Enum cell (e.g. `airport`), `business_category_vi` = NULL; (b) group label split into VI/EN (fails on `Giáo dục & Y tế (Công cộng)`, which has no EN part); (c) skip §1.7 entirely | (a). §1.7 emits only `google` rows, because its enum column is not `Partner Portal Enum`. |
| U2 | Conflicting Google duplicates: `national_park` and `hiking_area` appear under §1.5 Nature Reserve and under §1.5 Public POI. `church`, `hindu_temple`, `mosque`, `synagogue` appear under §1.5 Religious Site and under §1.7. | (a) first occurrence in document order wins; (b) a specific table wins (e.g. Public POI) | (a). Winners: Nature Reserve (×2) and Religious Site/`attraction` (×4). |
| U3 | §1.2 Fast Food cell has `shawarma_restaurant. hamburger_restaurant`, a period where a comma belongs. | (a) fix the source cell to a comma and keep the parser strict (comma split plus token regex); (b) also split on `.`; (c) fail | (a). This adds the md file to scope and needs one-character user approval. |
| U4 | `NB_LIB_TRANSFORM_SLV_GLD` reserves `created_at`, `updated_at`, `row_hash`, `deleted_at` (`add_row_hash` raises if `build` returns them). | (a) entity `created_at`/`updated_at` are entity-row lifecycle columns from the lib, and the L1 values are not carried; (b) also carry them as `src_created_at`/`src_updated_at` | (a). All `slv_3p_poi` column names are still present, and the requested column set stays as is. |

Expected seed under the recommended defaults: 297 `google` rows, 59 `partner` rows, 356 in total. The counts are §1.1 17/6, §1.2 140/17, §1.3 26/10, §1.4 39/9, §1.5 52/12, §1.6 4/5, and §1.7 25/0, minus the 6 conflict drops. These are hand counts. If the parser disagrees, Main stops and reports the difference instead of editing the number. With U1(c), the `google` count is 276.

## 4. Invariants

1. Every dictionary row satisfies `(source_name, place_type)` unique, `source_name ∈ {google, partner}`, and `business_sector` is one of the seven normalized values.
2. No row has `place_type` in {`Partner Portal bổ sung`, `Partner Portal Bổ sung`, `Fallback`, `Không có`}. Dropping one cell never drops the other column of the same source row.
3. Every `google` `place_type` matches `^[a-z0-9_]+$`. `extended_stay_hotel` has a `google` row and no `partner` row.
4. The notebook `SEED_ROWS` equals the output of the independent test parser on the md file, element by element and in order.
5. The seed is insert-only, keyed on `(source_name, place_type)`. A rerun inserts 0 rows. All rows inserted by one run share one `updated_at`, which is `current_timestamp()` in one MERGE statement.
6. The entity has one row per `poi_id` and contains only rows with `lower(trim(source_name)) = 'google'`. It includes every column name of `slv_3p_poi`, in source order, followed by the three category columns. The lib's technical columns come last.
7. Resolution uses only dictionary rows with `lower(trim(source_name)) = 'google'` and `is_active = true`. Keys are compared as `lower(trim(x))` on both sides.
8. A `primary_type` hit takes all three category columns from that one row, and `types_json` is ignored. Otherwise the lowest array position that hits supplies all three columns. Otherwise the result is `other`, `other`, NULL. The three columns always come from one branch and are never mixed column by column.
9. Rebuilding from the same input versions gives the same `row_hash` per `poi_id`, so the MERGE changes 0 rows.

## 5. State ownership

| State | Owner (writer) | Readers |
|---|---|---|
| `ref_dictionary_place_type` rows | `NB_SETUP_POI_ENTITY` (insert only) and later manual edits by the user | `NB_SLV_POI_ENTITY` |
| `slv_poi_entity` | `NB_SLV_POI_ENTITY` via `run_node`, sole writer | Future consumers (filter `deleted_at IS NULL`) |
| Two edge rows in `ctrl_mng_pipeline_config` | `NB_SETUP_POI_ENTITY` (insert if missing) | `NB_LIB_TRANSFORM_SLV_GLD` |
| Edge watermarks `wm_e__slv_poi_entity__*` and lock `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` | `NB_LIB_TRANSFORM_SLV_GLD` | Same |
| `slv_3p_poi` | Extract (unchanged) | Node, read at one Delta version |

## 6. Grain and keys

- Dictionary: one row per `(source_name, place_type)`. Delta does not enforce the key. The seed pre-check, the post-check, and the node's duplicate check enforce it.
- Entity: one row per `poi_id`. The lib QG blocks on a NULL or duplicate `pk`. A fan-out from a duplicated dictionary key would show up as `pk_duplicate`, and the node also checks for it explicitly first.

DDL (setup notebook):

```sql
CREATE TABLE IF NOT EXISTS lh_vv_silver.dbo.ref_dictionary_place_type (
    source_name          STRING NOT NULL,
    place_type           STRING NOT NULL,
    business_sector      STRING,
    business_category    STRING,
    business_category_vi STRING,
    is_active            BOOLEAN,
    updated_at           TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true')
```

After the CREATE, compare `spark.table(...).schema` with the expected `(name, simpleString, nullable)` list, the same way cell `enrddlpy` does in `NB_CREATE_DDL`, and raise `ConfigError` on any difference. `CREATE TABLE IF NOT EXISTS` is silent on an existing table with a different schema, so the check is needed.

The lib creates the entity table from the build schema (`ensure_target`). It has no static DDL, so it cannot drift from the physical `slv_3p_poi`. That includes legacy columns that the L1 timestamp backfill kept as extras. New L1 columns arrive through `ALTER TABLE ADD COLUMNS`.

## 7. Seed parsing rules (test parser, which also generates the literal)

- Section: `^#\s+\*\*1\.(\d)` maps digits 1–7 to `accommodation`, `fnb`, `spa_n_wellness`, `shopping_n_retail`, `attraction`, `vehicle_rental`, `other`. The §1.7 heading text differs ("1.7." and a suffix), which is why the match uses the number.
- Cell cleanup: remove `**` and backticks, replace NBSP with a space, and strip. An empty cell becomes `None`. Skip separator rows and all-empty rows.
- A header row is any row with a cell containing `Google Place API`. Role columns: `Partner Portal Enum` → partner, `Google Place API` → google, `(VI)` → vi, `(EN)` → en, `Fabric Enum` → fabric. The §1.5 Public POI table has no partner column.
- Partner cell: if it is not `None` and not in SKIP, emit `("partner", cell, sector, en, vi)` with the cell kept verbatim.
- Google cell: if it is not `None` and not in SKIP, split on `,`, strip each part, drop empty parts, and require `^[a-z0-9_]+$` on each token (raise otherwise). Emit `("google", token, sector, en, vi)` per token. For §1.7 under U1(a), `en` is the Fabric Enum cell and `vi` is `None`.
- Dedupe by `(source, place_type)`, keeping the first one in document order. Identical duplicates (`Homestay` ×2) are dropped silently. Conflicting duplicates are dropped and collected. The test asserts that the conflict set equals exactly the six U2 tokens, so any new conflict in a future md edit fails the test.
- Empty display cells stay NULL (e.g. partner `Car with Driver`, and `Campervan Rental` EN).

### 7.1 Parser (test file)

```python
SECTOR = {"1": "accommodation", "2": "fnb", "3": "spa_n_wellness", "4": "shopping_n_retail",
          "5": "attraction", "6": "vehicle_rental", "7": "other"}
SKIP = {"Partner Portal bổ sung", "Partner Portal Bổ sung", "Fallback", "Không có"}
SECTION_RE = re.compile(r"^#\s+\*\*1\.(\d)")
TOKEN_RE = re.compile(r"[a-z0-9_]+")
ROLES = (("Partner Portal Enum", "partner"), ("Google Place API", "google"), ("(VI)", "vi"),
         ("(EN)", "en"), ("Fabric Enum", "fabric"))


def _cell(text):
    text = text.replace("**", "").replace("`", "").replace("\xa0", " ").strip()
    return text or None


def parse_mapping(md):
    rows, sector, cols = [], None, None
    for line in md.splitlines():
        m = SECTION_RE.match(line)
        if m:
            sector, cols = SECTOR[m.group(1)], None
            continue
        if not line.lstrip().startswith("|"):
            continue
        cells = [_cell(c) for c in line.strip().strip("|").split("|")]
        if all(c is None or set(c) <= {"-"} for c in cells):
            continue
        if any(c and "Google Place API" in c for c in cells):
            cols = {role: i for i, c in enumerate(cells) for key, role in ROLES if c and key in c}
            continue
        if cols is None:
            continue
        get = lambda r: cells[cols[r]] if r in cols else None
        en, vi = (get("fabric"), None) if "fabric" in cols else (get("en"), get("vi"))
        partner, google = get("partner"), get("google")
        if partner and partner not in SKIP:
            rows.append(("partner", partner, sector, en, vi))
        if google and google not in SKIP:
            for tok in (t.strip() for t in google.split(",")):
                if tok and not TOKEN_RE.fullmatch(tok):
                    raise ValueError(f"bad token {tok!r} in {sector}")
                if tok:
                    rows.append(("google", tok, sector, en, vi))
    seen, out, conflicts = {}, [], set()
    for r in rows:
        k = r[:2]
        if k not in seen:
            seen[k] = r
            out.append(r)
        elif seen[k] != r:
            conflicts.add(k)
    return out, conflicts
```

Main generates `SEED_ROWS` once by running this parser and pasting the result as a literal. The test then guards parity.

## 8. Entity resolution (node notebook)

### 8.1 `build` and `SPEC` for `NB_SLV_POI_ENTITY`

```python
GOOGLE = "google"
OTHER = "other"
CATEGORY_COLS = ("business_sector", "business_category", "business_category_vi")


def build(ctx: NodeContext) -> DataFrame:
    # Giữ mọi cột slv_3p_poi trừ created_at / updated_at (lib thêm cột kỹ thuật của bảng đích).
    # Khớp: primary_type -> phần tử đầu tiên của types_json khớp (theo vị trí mảng) -> other / other / NULL.
    src = ctx.input("poi")
    clash = [c for c in src.columns if c.lower() in CATEGORY_COLS + ("row_hash", "deleted_at")]
    if clash:
        raise ConfigError(f"slv_poi_entity: slv_3p_poi đã có cột {clash}")
    keep = [c for c in src.columns if c.lower() not in TECH_NAMES]
    poi = src.where(F.lower(F.trim("source_name")) == GOOGLE).select(*keep)
    d = (ctx.input("dict")
         .where((F.lower(F.trim("source_name")) == GOOGLE) & (F.col("is_active") == F.lit(True)))
         .select(F.lower(F.trim("place_type")).alias("_k"), F.struct(*CATEGORY_COLS).alias("_cat")))
    dup = d.groupBy("_k").count().where("count > 1").count()
    if dup:
        raise QualityGateError(f"ref_dictionary_place_type: {dup} place_type google trùng")
    d = F.broadcast(d)
    by_primary = (poi.select("poi_id", F.lower(F.trim("primary_type")).alias("_k"))
                  .join(d, "_k").select("poi_id", F.col("_cat").alias("_p")))
    by_types = (poi.select("poi_id", F.posexplode(F.from_json("types_json", "array<string>")).alias("_pos", "_t"))
                .withColumn("_k", F.lower(F.trim("_t"))).join(d, "_k")
                .groupBy("poi_id").agg(F.min_by("_cat", "_pos").alias("_m")))
    out = poi.join(by_primary, "poi_id", "left").join(by_types, "poi_id", "left")
    agg = out.agg(F.count(F.lit(1)).alias("rows"), F.count("_p").alias("by_primary"),
                  F.count(F.when(F.col("_p").isNull(), F.col("_m"))).alias("by_types")).first()
    total = src.count()
    ctx.metrics.update(rows=agg["rows"], by_primary=agg["by_primary"], by_types=agg["by_types"],
                       unmatched=agg["rows"] - agg["by_primary"] - agg["by_types"],
                       non_google_rows=total - agg["rows"], dict_google_rows=d.count())
    if total and not agg["rows"]:
        raise QualityGateError("slv_poi_entity: slv_3p_poi không có dòng google")

    def pick(c, default):
        return (F.when(F.col("_p").isNotNull(), F.col(f"_p.{c}"))
                .when(F.col("_m").isNotNull(), F.col(f"_m.{c}"))
                .otherwise(default).alias(c))

    return out.select(*keep, pick("business_sector", F.lit(OTHER)), pick("business_category", F.lit(OTHER)),
                      pick("business_category_vi", F.lit(None).cast("string")))


SPEC = NodeSpec(
    trg_tbl="slv_poi_entity",
    inputs={"poi": "slv_3p_poi", "dict": "ref_dictionary_place_type"},
    pk=("poi_id",),
    build=build,
    required_inputs=("poi", "dict"),
    warn_checks=(("types_json_unparsed",
                  "types_json IS NOT NULL AND from_json(types_json, 'array<string>') IS NULL"),),
    write_mode="MERGE",
)
```

Notes:
- `posexplode` (not `_outer`) yields nothing for a NULL or unparsable array, so those rows fall through to `other`. `min_by(_cat, _pos)` is deterministic because positions are unique per `poi_id`.
- Branches are chosen by whether the struct is NULL, so a matched row whose category fields are NULL (§1.7 `vi`) stays NULL instead of falling back to `other`.
- No arrays are in the output, so the lib's `array_sort` requirement does not apply. `_crawled_at`/`_last_seen_at` stay in `row_hash` so that the entity values keep matching L1. That means an entity row is updated on every crawl, which is about 19k rows per run. This is acceptable.
- Notebook cells follow `NB_SLV_PN_POI` exactly: a markdown title, a parameter cell, `%run NB_LIB_TRANSFORM_SLV_GLD`, `build` + `SPEC`, `RES = run_node(...)`, and `notebookutils.notebook.exit(finish_node(RES))`. Copy the notebook-level Fabric metadata (lakehouse dependencies) from `NB_SLV_PN_POI`.

## 9. Setup notebook `NB_SETUP_POI_ENTITY`

Cells:
1. Parameters: `p_apply = "false"`.
2. `%run NB_LIB_TRANSFORM_SLV_GLD`, for `ConfigError`, `with_retry`, `quote_name`, `table_exists`, and `T_PIPELINE_CONFIG`.
3. A pure block between `# BEGIN_PLACE_TYPE_SEED` and `# END_PLACE_TYPE_SEED`, holding `SEED_SECTORS`, `SEED_SKIP`, `SEED_ROWS` (5-tuples in parser order), and `validate_seed(rows) -> None`. `validate_seed` raises on a duplicate key, a source outside {google, partner}, a sector outside the seven, a place_type in SKIP, or a google token that fails `^[a-z0-9_]+$`. The block imports only `re`.
4. Plan: run `validate_seed(SEED_ROWS)`, then print the count by source, the number of keys missing from the table (0 if the table is absent), and the planned edges. If `p_apply` is false, exit with the plan JSON.
5. DDL plus the schema check from §6.
6. Seed, as one statement over a temp view built with `spark.createDataFrame(SEED_ROWS, "source_name string, place_type string, business_sector string, business_category string, business_category_vi string")`:

```sql
MERGE INTO lh_vv_silver.dbo.ref_dictionary_place_type AS t
USING {view} AS s
ON t.source_name = s.source_name AND t.place_type = s.place_type
WHEN NOT MATCHED THEN INSERT
    (source_name, place_type, business_sector, business_category, business_category_vi, is_active, updated_at)
VALUES (s.source_name, s.place_type, s.business_sector, s.business_category, s.business_category_vi,
        true, current_timestamp())
```

7. Post-check. Duplicate `(source_name, place_type)` in the table must be 0. All seed keys must be present. Rows whose values differ from the seed are reported as `drift` (count only) and are not overwritten. Any failure raises before step 8.
8. Edges. First, if `slv_poi_entity` already has an active edge under another `pl_name`, raise. Then:

```sql
INSERT INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
    (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order)
SELECT COALESCE((SELECT MAX(id) FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config), 0) + t.seq,
       'PL_VV_TRANS_SLV_TO_SLV_1H', 'lh_vv_silver.dbo', t.src_tbl, 'lh_vv_silver.dbo', 'slv_poi_entity',
       1, 1, 'RECOMPUTE', CAST(NULL AS STRING), CAST(NULL AS STRING)
FROM VALUES (1, 'slv_3p_poi'), (2, 'ref_dictionary_place_type') AS t(seq, src_tbl)
WHERE NOT EXISTS (
    SELECT 1 FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config c
    WHERE c.pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND c.src_schema = 'lh_vv_silver.dbo'
      AND c.src_tbl = t.src_tbl AND c.trg_schema = 'lh_vv_silver.dbo' AND c.trg_tbl = 'slv_poi_entity')
```

`nb_name` is left NULL, so the lib derives `NB_SLV_POI_ENTITY`. That works whether or not the optional column exists.

9. Print and exit with a JSON summary: `inserted`, `drift`, `edges_inserted`, `status`. Print no row samples.

## 10. Ordering, transactions, idempotency, concurrency

- Run order: setup (DDL → seed → post-check → edges) → node `DRY_RUN` → node `RUN`. The node cannot resolve until the edges exist.
- Commits: the seed is one Delta commit and the edges are one separate commit. The node writes one MERGE commit on the target plus the lib's log appends. Each Delta commit is atomic.
- Idempotency: a seed rerun inserts 0 rows, and the edges are covered by `NOT EXISTS`. A node rerun on unchanged inputs returns `NO_DATA`, or makes a MERGE with diff 0 that the lib skips.
- Concurrency: the node reads `slv_3p_poi` and the ref at fixed versions, so an extract running at the same time is isolated. The lib's flow lock `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` serializes node runs. Only the node writes the target. The setup notebook is manual and one-shot, and the lib's `with_retry` covers commit conflicts on its MERGE.

## 11. Retry, recovery, partial failure

| Failure | State left | Recovery |
|---|---|---|
| `validate_seed` raises | Nothing written | Fix the literal or the md (re-run the parser test), then rerun |
| Seed committed, post-check or edge insert fails | Dictionary seeded, edges missing | Rerun setup. The seed inserts 0 and the edges are inserted. |
| Node QG block (`pk_duplicate`, dictionary duplicate, no google rows, column clash) | `FAILED` log row, target unchanged | Fix the cause (the ref row, or the user decides on the clash), then rerun the node |
| Node MERGE fails | Delta unchanged, `FAILED` log | Rerun. The edge mailbox did not advance. |
| Wrong mapping found later | — | `UPDATE` the ref row (or set `is_active = false`). The ref edge becomes dirty, and the next node run recomputes the affected rows. Re-running the seed does not overwrite existing rows; this is the ref convention in `01_DATA_MODEL.md` §6.1. |

## 12. Observability

- `ctrl_log_table_run.qg_json` for each node run carries the lib's `rows` and `blocks`, the warn `types_json_unparsed`, and `metrics` {`rows`, `by_primary`, `by_types`, `unmatched`, `non_google_rows`, `dict_google_rows`}.
- The setup exit JSON gives the inserted, drift, and edge counts.

## 13. Security

The dictionary holds public taxonomy labels. The entity carries business POI fields only, which are already in silver. Neither notebook prints rows. There are no secrets, tokens, or personal data.

## 14. Alternatives and selected trade-offs

| Decision | Selected | Rejected and why |
|---|---|---|
| Dictionary placement | New `ref_dictionary_place_type` | Extending `ref_business_category`: its key is `(source_name, source_sector, source_category)` with different semantics, and it has no notebook in the repo. Merging them is a later consolidation. |
| Entity vs N2 `slv_poi` | Separate Google-only `slv_poi_entity` | Folding into N2: its notebook does not exist yet and it mixes partner rows, which the request excludes. |
| Build mechanism | Lib node, MERGE `row_hash`, soft delete | Standalone `INSERT OVERWRITE` would keep L1 `created_at`/`updated_at` literally, but it has no lineage, QG, or dirty-edge recompute, and it breaks L2 conventions (§6). A SQL view gives no stored table and repeats the parse on every read. |
| Seed source | Literal in notebook plus a local parity test against the md | Parsing the md at runtime from OneLake `Files`: an extra upload and an untracked runtime dependency. A hand-typed literal with no test: drift is invisible. |
| Matching | Broadcast join + `posexplode` + `min_by` | Higher-order functions over a driver-collected map: needs `try_element_at` to be ANSI-safe and is harder to review. Python UDF: slow and opaque. |
| Flow | New unscheduled `PL_VV_TRANS_SLV_TO_SLV_1H` | Attaching to `PL_VV_TRANS_SLV_TO_ENR_15P` would change a scheduled flow's runtime and lock window, which needs a pipeline review that is out of scope. Moving the edges later is a single data change. |
| Seed write | Insert-only MERGE | An upsert would overwrite manual ref edits, which goes against convention. Overwriting the table loses manual rows. |

## 15. Rollout

Paths to add to `scope.files`:
- `notebooks/NB_SETUP_POI_ENTITY.ipynb` (new)
- `notebooks/NB_SLV_POI_ENTITY.ipynb` (new)
- `tests/test_poi_entity_contract.py` (new)
- `docs/context/01_DATA_MODEL.md`
- `docs/context/CTRL_TABLES_CONTEXT.md`
- `docs/context/3p-google/mapping_place_type.md` (only if U3(a) is approved)

The Fabric DEV apply comes later through a user runbook (Main or Author writes `runtime-runbook.md`):
1. Setup with `p_apply=false`, then review the plan.
2. Setup with `p_apply=true`.
3. `NB_SLV_POI_ENTITY` with `p_mode=DRY_RUN`, then check QG and metrics.
4. `p_mode=RUN`.
5. Run the read-only checks in §17.2.

## 16. Rollback and forward recovery

- Stop: `UPDATE ctrl_mng_pipeline_config SET is_active = 0 WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND trg_tbl = 'slv_poi_entity'`. No reader exists yet, so stopping reads costs nothing.
- Dropping either table needs rollback and forward-recovery steps in `runtime-runbook.md` (AGENTS.md §8). This task does not drop anything.
- Forward fixes are row edits in the ref (§11) or a reseed after the user deletes the affected keys.

## 17. Verification

### 17.1 Local (`tests/test_poi_entity_contract.py`, no Spark)

- `test_seed_matches_mapping_file`: exec the `BEGIN/END_PLACE_TYPE_SEED` block, then assert `SEED_ROWS == parse_mapping(md)[0]` and that `validate_seed(SEED_ROWS)` passes.
- `test_seed_excludes_placeholders`: no `place_type` in SKIP. `extended_stay_hotel` is `google` only. `Blind Massage` and `Local Specialty` are `partner` only.
- `test_seed_keys_unique_and_tokens_valid`: keys are unique, and every google token matches the regex.
- `test_seed_sector_normalization`: the set of sectors per section equals the §7 map, with `hotel` → `accommodation` and `airport` → `other`.
- `test_seed_conflicts_pinned`: the conflict set equals the six U2 tokens, and each winner's sector and category are as decided.
- `test_seed_counts`: 297 google, 59 partner (or the counts from the user's choices).
- `test_entity_node_contract`: the node source contains `trg_tbl="slv_poi_entity"`, both input roles, `pk=("poi_id",)`, `write_mode="MERGE"`, `required_inputs=("poi", "dict")`, `posexplode(`, `min_by(`, `"_pos"`, `F.lit(None).cast("string")`, and `== GOOGLE`. It does not contain `posexplode_outer` or `explode(`. The `_p` branch appears before the `_m` branch.
- `test_setup_contract`: `p_apply = "false"`; the DDL holds the 7 columns and types; the MERGE has `WHEN NOT MATCHED` and no `WHEN MATCHED`; the edges SQL has `PL_VV_TRANS_SLV_TO_SLV_1H`, `RECOMPUTE`, `NOT EXISTS`, and both `src_tbl` values.

Commands: `python -m pytest tests/test_poi_entity_contract.py -q`, `python -m pytest -q`, `python scripts/vv.py verify 20261016-ref-place-type-poi-entity`.

### 17.2 Fabric DEV read-only checks (for the runbook; each expects 0 unless stated)

```sql
SELECT count(*) FROM (SELECT source_name, place_type FROM lh_vv_silver.dbo.ref_dictionary_place_type
                      GROUP BY 1, 2 HAVING count(*) > 1);
SELECT count(*) FROM lh_vv_silver.dbo.ref_dictionary_place_type
WHERE place_type IN ('Fallback', 'Không có', 'Partner Portal bổ sung', 'Partner Portal Bổ sung');
SELECT source_name FROM lh_vv_silver.dbo.ref_dictionary_place_type WHERE place_type = 'extended_stay_hotel'; -- expect: google only
SELECT count(DISTINCT updated_at) FROM lh_vv_silver.dbo.ref_dictionary_place_type;                         -- expect: 1
WITH d AS (SELECT lower(trim(place_type)) pt, struct(business_sector, business_category, business_category_vi) c
           FROM lh_vv_silver.dbo.ref_dictionary_place_type WHERE lower(trim(source_name)) = 'google' AND is_active),
p AS (SELECT poi_id, primary_type, types_json FROM lh_vv_silver.dbo.slv_3p_poi WHERE lower(trim(source_name)) = 'google'),
tf AS (SELECT p.poi_id, min_by(d.c, x.pos) m FROM p
       LATERAL VIEW posexplode(from_json(p.types_json, 'array<string>')) x AS pos, ty
       JOIN d ON d.pt = lower(trim(x.ty)) GROUP BY p.poi_id),
e AS (SELECT p.poi_id, coalesce(dp.c, tf.m, named_struct('business_sector', 'other', 'business_category', 'other',
                                                         'business_category_vi', CAST(NULL AS STRING))) c
      FROM p LEFT JOIN d dp ON dp.pt = lower(trim(p.primary_type)) LEFT JOIN tf ON tf.poi_id = p.poi_id)
SELECT count(*) FROM e FULL JOIN (SELECT * FROM lh_vv_silver.dbo.slv_poi_entity WHERE deleted_at IS NULL) a
  ON a.poi_id = e.poi_id
WHERE a.poi_id IS NULL OR e.poi_id IS NULL
   OR NOT (e.c.business_sector <=> a.business_sector AND e.c.business_category <=> a.business_category
           AND e.c.business_category_vi <=> a.business_category_vi);
```

Run the parity query only when no extract is running. Otherwise compare at the `slv_3p_poi` version recorded in `ctrl_log_table_run.src_versions_json`. Column check in Python: `set(spark.table("lh_vv_silver.dbo.slv_3p_poi").columns) <= set(spark.table("lh_vv_silver.dbo.slv_poi_entity").columns)`.

## 18. Implementation plan

1. Stop S0: get the user's choices for U1–U4 and record them in `decision.md`.
2. Update `scope.files` (§15). If U3(a) is approved, fix the md cell.
3. Write the test with the parser (§7.1), then generate `SEED_ROWS` from it.
4. Write `NB_SETUP_POI_ENTITY` (§9) and `NB_SLV_POI_ENTITY` (§8.1).
5. Add the doc rows. §6 of `01_DATA_MODEL.md` gets a `slv_poi_entity` row (grain `poi_id`, inputs, the U4 note). §6.1 gets a `ref_dictionary_place_type` row (key, seed counts). `CTRL_TABLES_CONTEXT.md` §3 gets the two edges.
6. Run the local tests, then `vv.py verify`, then send to review.
