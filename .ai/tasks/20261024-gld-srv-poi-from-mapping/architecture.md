RESULT: PASS

## Main brief

### Decision
RESULT: PASS. Each gold table is a lib `run_node` MERGE node under `PL_VV_TRANS_SLV_TO_GLD_30P` with six RECOMPUTE edges. Builds recompute everything; a pure-Python UDF computes hours; any shape outside the mapping stops the run.
DDL goes in place in `NB_SETUP_INITIAL_DDL` plus an appended `srvpoimd`/`srvpoipy` in `NB_CREATE_DDL`.
The appended cells break the tail-id tests in two test files outside scope. Triage must add those files (and the new `tests/test_gld_srv_poi_contract.py`) before any edit.
multi_lang ends FAILED with "empty required input" until the landing table has data (D-SRV-23). That is the expected runtime result for this task.

### Invariants Main must preserve
- Live rows are unique on `(poi_id, lang)` / `poi_id`. Keys are NOT NULL in DDL. QG `pk_null`/`pk_duplicate` stops the run before any write.
- Builds return the full target set every run. All inputs use `ctx.input(role, live_only=False)`. Nothing reads `lh_vv_gold`.
- `operating_hours`:
  - null exactly when the source text is null;
  - otherwise every day 1..7 appears, non-decreasing;
  - partner always has 7 objects; Google repeats a day for each extra period (rule 9);
  - keys follow §1.4 order, and omitted keys are absent.
- Shapes outside the mapping return an error code. The build raises `QualityGateError` with counts per code before MERGE.
- Destination: the greatest `updated_at` wins. A duplicated `poi_id` with a null or tied maximum stops the run. No second sort key.
- i18n key is `uuid_md5(F.col("business_service_id"), F.lit(PARTNER))` with `PARTNER = "partner"`.
- The build `OUT_COLS` plus `row_hash, created_at, updated_at, deleted_at` equal `srvpoipy` `GOLD_COLS` and `TABLE_SPECS`, by name, type and order.
- `srvpoipy`:
  - lock first, stop before any write, then exactly one ALTER, `CREATE IF NOT EXISTS`, one guarded INSERT, and a check after write;
  - no DROP, DELETE or UPDATE of data.
- The entity spec stays last in `TABLE_SPECS`.
- Every active gold edge belongs to GLD_30P only.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` `TABLE_SPECS` | Destination: append the 5 columns after `updated_at`. Insert the 2 gold specs before the entity spec (doc "DDL / NB_SETUP_INITIAL_DDL"). | 18 specs; entity spec last |
| 2 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` | Add `_GLD30, _G`; append 6 rows in `EDGES_ON` order. | 59 rows |
| 3 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_plan` count check | Change `16` to `18` (check and message). | plan passes |
| 4 | notebooks/NB_CREATE_DDL.ipynb | new last cells `srvpoimd`, `srvpoipy` | Per doc "NB_CREATE_DDL srvpoimd + srvpoipy". | rerun changes nothing |
| 5 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | new; `srvmlbuild` (+ md/param/run/res/exit) | Per doc "NB_GLD_SRV_POI_MULTI_LANG" and "Notebook shells". | tests green; DEV FAILED (empty input), no write |
| 6 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | new; `srvinfohours` | `BEGIN_HOURS_PURE` block verbatim from doc. | §1.4 tests pass |
| 7 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` (+ md/param/run/res/exit) | Per doc "NB_GLD_SRV_POI_INFO, cell srvinfobuild". | DEV RUN 24 rows; rerun diff 0 |
| 8 | tests/test_initial_ddl_contract.py | `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_pipeline_config_rows_match_sources`, `test_flag_patch_create_matches_init`; new `test_gld_srv_patch_create_matches_init`, `test_gld_srv_patch_guards` | Per doc "Verification". | green |
| 9 | tests/test_gld_srv_poi_contract.py (scope add) | new file | The hours, node-spec and column tests listed in doc "Verification". | green |
| 10 | tests/test_enr_poi_contract.py (scope add) | `test_info_patch_cell_guards` L231–233 | Change slices to `[-12:-6]`, `[-6:-4]`, `[-4:-2]`; add `ids[-2:] == ["srvpoimd","srvpoipy"]`. | green |
| 11 | tests/test_poi_entity_contract.py (scope add) | `test_create_ddl_patch` L628–630 | Same as row 10. | green |

The mapping docs, the probes and `model-design.md` don't change.

### Order and stop points
1. Triage adds `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py` and `tests/test_gld_srv_poi_contract.py` to `scope.files`. **STOP: scope.** If triage declines the new file, put row 9's tests in `tests/test_initial_ddl_contract.py` under `# gld_srv`.
2. Edit rows 1–4, then rows 5–7.
3. Edit rows 8–11. Run local tests. **STOP: local verification.**
4. In Fabric DEV:
   - run `srvpoipy` twice;
   - run `NB_SETUP_INITIAL_DDL p_apply=false`;
   - run `NB_GLD_SRV_POI_INFO` `DRY_RUN`, then `RUN`, then `RUN` again;
   - run `NB_GLD_SRV_POI_MULTI_LANG` `RUN` and expect FAILED, empty input;
   - run `NB_00_ORCHES_SLV_TO_GLD` with `p_pl_name=PL_VV_TRANS_SLV_TO_GLD_30P` and `p_mode=PLAN`;
   - run the Google hours Counter snippet (doc "Verification").
   **STOP: runtime evidence.**
5. Don't schedule a GLD_30P pipeline before the D-SRV-23 follow-up. **STOP: user decision**, outside this task.

### Tests and verification
- `python -m pytest tests/test_initial_ddl_contract.py tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
- `python -m pytest -q`
- New: `test_gld_srv_patch_create_matches_init`, `test_gld_srv_patch_guards`, `test_google_case1`, `test_google_case2_all_day`, `test_google_multi_period_rule9`, `test_google_null_and_empty`, `test_google_stop_codes`, `test_partner_single_hours`, `test_partner_closed_forms`, `test_partner_stop_codes`, `test_unknown_source_stops`, `test_node_specs`, `test_build_columns_match_ddl`.
- Updated:
  - `test_table_inventory_matches_sources` (16→18);
  - `test_columns_match_sources` (destination + `DEST_NEW_COLS`, gold specs);
  - `test_pipeline_config_rows_match_sources` (53→59);
  - `test_flag_patch_create_matches_init`;
  - `test_info_patch_cell_guards`, `test_create_ddl_patch` (tail slices).
- DEV checks:
  - info live `count(*) = count(DISTINCT poi_id) = 24`;
  - 13 null `operating_hours`;
  - 11 with `json_array_length = 7`;
  - `is_recommended` all true;
  - `is_verified`, `is_bookable` and destination columns null;
  - second RUN diff 0/0/0 with no new Delta version;
  - multi_lang target 0 rows;
  - Google Counter shows only `None`.

### Read only if needed
- "Status" → stop 1, rows 9–11
- "DDL / NB_SETUP_INITIAL_DDL" → rows 1–3
- "NB_CREATE_DDL srvpoimd + srvpoipy" → row 4, row 8 guards
- "Build design / NB_GLD_SRV_POI_MULTI_LANG" → row 5
- "NB_GLD_SRV_POI_INFO, cell srvinfohours" → row 6, row 9 hours tests
- "NB_GLD_SRV_POI_INFO, cell srvinfobuild" → row 7
- "Notebook shells" → rows 5–7
- "Invariants", "Grain and keys" → all rows
- "Ordering", "Concurrency", "Transaction and commit boundaries", "Partial failure" → row 4, stop 4
- "Alternatives" → the `required_inputs` and test-location choices
- "Verification" → rows 8–11, stops 3–4

# Architecture: 20261024-gld-srv-poi-from-mapping

## Status

Round 1 was blocked on B1–B5. All five are now closed:
- B1: D-SRV-24 (write path A) and D-SRV-27 (a null key stops the run).
- B2: D-SRV-25 (Google null gives null).
- B3: D-SRV-26 and mapping info §1.3 rule 9 (every period is emitted).
- B4: the ledger `Còn mở` says an equal or null `updated_at` stops the run. Probe: 0 duplicate destination rows.
- B5: probe shows no partner `hours` array longer than 1.

`model-design.md` now records the technical columns and NOT NULL keys, and it matches the ledger. Evidence: `evidence/results/gld_srv_input_shape.txt` and `partner_hours_shape.txt`.

One **scope gap** remains. It needs a triage action, not new evidence. Appending two cells to `NB_CREATE_DDL` breaks two existing tests that pin the tail cell ids:
- `tests/test_enr_poi_contract.py::test_info_patch_cell_guards`, lines 231–233;
- `tests/test_poi_entity_contract.py::test_create_ddl_patch`, lines 628–630.

Neither file is in `scope.files`. The request also requires appending the cells at the end, so a fix that stays inside scope does not exist. In the same triage step, add `tests/test_gld_srv_poi_contract.py` (new) for the hours and node contract tests. If triage declines the new file, put those tests in `tests/test_initial_ddl_contract.py` under a `# gld_srv` comment.

## Scope

- New node notebooks:
  - `NB_GLD_SRV_POI_MULTI_LANG` writes `lh_vv_gold.dbo.gld_srv_poi_multi_lang`.
  - `NB_GLD_SRV_POI_INFO` writes `lh_vv_gold.dbo.gld_srv_poi_info`.
  - Both use lib `run_node` MERGE (D-SRV-24).
- DDL:
  - both gold tables;
  - five nullable columns on `slv_enr_poi_destination` (D-SRV-11);
  - in place in `NB_SETUP_INITIAL_DDL`, and as an appended `srvpoimd` + `srvpoipy` in `NB_CREATE_DDL`.
- Six RECOMPUTE edges in `ctrl_mng_pipeline_config` under `PL_VV_TRANS_SLV_TO_GLD_30P` (D-SRV-22). `_resolve_node` raises `ConfigError` without them ("cần đúng 1 bảng đích active").
- Contract tests.

## Non-goals

- The Fabric pipeline object `PL_VV_TRANS_SLV_TO_GLD_30P`, manifests, schedules, and `PL_VV_TRANS_SLV_TO_ENR_15P` edges.
- Lib changes. Any writer for the five destination columns (D-SRV-23).
- `gld_srv_poi_registry` and `gld_srv_poi_destination_membership`.
- Any `DROP`. Any `deleted`/`deleted_at` input filter (`Còn mở`).
- Changes to the mapping docs: `model-design.md` and mapping §1.3–§1.5 already agree with the ledger.

## Invariants

1. Live rows (`deleted_at IS NULL`) are unique on `(poi_id, lang)` and on `poi_id`. Lib QG `pk_null`/`pk_duplicate` stops the run before any write (D-SRV-19, D-SRV-20, D-SRV-27).
2. Each build returns the full target set. `WHEN NOT MATCHED BY SOURCE` soft-deletes every key it leaves out.
3. No notebook reads `lh_vv_gold`. All inputs use `ctx.input(role, live_only=False)`, so no input filter is applied.
4. `operating_hours` is a STRING JSON array, or null when the source text is null (§1.3 rule 8, §1.5).
   - Every day 1..7 appears, in non-decreasing order.
   - Google has one object per source element, so a day can repeat (rule 9). Partner always has exactly 7 objects.
   - Key order is `day_of_week, label, value, open_time, close_time, is_open_all_day, is_closed`. Keys that a form omits are absent, not null.
5. Shapes outside §1.3/§1.5 stop the run before MERGE. Messages carry counts per code, never raw values. §1.5 says to stop on more than one `hours` element.
6. Destination winner: the greatest `updated_at` per `poi_id`, with no second key. A duplicated `poi_id` with a null or tied maximum `updated_at` stops the run.
7. The i18n join key is `uuid_md5(F.col("business_service_id"), F.lit(PARTNER))` with `PARTNER = "partner"`, the same as `NB_SLV_POI_ENTITY_NON_ENRICH` (D-SRV-12).
8. The physical columns are the same in four places: the build output, `TABLE_SPECS`, `srvpoipy` `GOLD_COLS`, and what `ensure_target` would create. That set is the build columns in model-design order plus `row_hash, created_at, updated_at, deleted_at`.
9. `srvpoipy` is idempotent and append-only:
   - `ADD COLUMNS` only for missing columns;
   - `CREATE TABLE IF NOT EXISTS`;
   - edge `INSERT … WHERE NOT EXISTS`;
   - no DROP/DELETE/UPDATE of data.
10. Each gold table has exactly one active owner pl, `PL_VV_TRANS_SLV_TO_GLD_30P`.

## State ownership

| State | Sole writer | Readers |
|---|---|---|
| `gld_srv_poi_multi_lang` rows | `NB_GLD_SRV_POI_MULTI_LANG` (`run_node`) | external product |
| `gld_srv_poi_info` rows | `NB_GLD_SRV_POI_INFO` (`run_node`) | external product |
| `slv_enr_poi_destination` schema | `srvpoipy` / `NB_SETUP_INITIAL_DDL` | info node; `NB_ENR_POI_INFO` (key only) |
| `slv_enr_poi_destination` rows | external enrich writer (unchanged) | same |
| GLD_30P edges | `srvpoipy` / `init_seed_ctrl` | lib `load_config_rows` |
| `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P` lock row | lib `ensure_lock_row`; `srvpoipy` MERGE-inserts it if missing | lib |
| edge watermarks `wm_e__gld_srv_poi_*__*` | `NB_00_ORCHES_SLV_TO_GLD` `advance_edges` | lib |

## Grain and keys

From `model-design.md` `## Entities and grain` and `## Keys`, with nothing added:
- MERGE keys `("poi_id","lang")` and `("poi_id",)`, declared NOT NULL in DDL.
- Entity `poi_id` is unique: it is the entity MERGE key, and the probe found `entity_poi_id_dup 0`. The entity join can't fan out.
- i18n `(business_service_id, locale)` is the registry key (probe `i18n_key_dup 0`). Any fan-out reaches QG `pk_duplicate` and stops the run.
- Google vs partner uses `lower(trim(source_name))`, the same expression as the entity build (`b1entitybuild` `GOOGLE` filter). `source_name` itself is copied 1-1.

## Build design

### NB_GLD_SRV_POI_MULTI_LANG (cell `srvmlbuild`)

```python
PARTNER = "partner"
ML_COLS = ("poi_id", "lang", "time_to_spend", "best_time", "cost_vnd", "description")
OUT_COLS = ("poi_id", "lang", "source_name", "time_to_spend", "best_time", "cost_vnd", "description")


def _require(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ConfigError(f"gld_srv_poi_multi_lang: {name} thiếu {missing}")


def build(ctx):
    ml = ctx.input("multi_lang", live_only=False)
    ent = ctx.input("entity", live_only=False)
    i18n = ctx.input("i18n", live_only=False)
    _require(ml, ML_COLS, "slv_enr_poi_info_multi_lang")
    _require(ent, ("poi_id", "source_name"), "slv_poi_entity_non_enrich")
    _require(i18n, ("business_service_id", "locale", "bio"), "slv_pn_business_service_i18ns")
    bio = i18n.select(uuid_md5(F.col("business_service_id"), F.lit(PARTNER)).alias("_pid"),  # D-SRV-12
                      F.col("locale").alias("_loc"), "bio")
    partner = F.coalesce(F.lower(F.trim(F.col("source_name"))) == PARTNER, F.lit(False))
    rows = (ml.select(*ML_COLS).join(ent.select("poi_id", "source_name"), "poi_id", "left")      # D-SRV-10, D-SRV-28
            .join(bio, partner & (F.col("poi_id") == F.col("_pid")) & (F.col("lang") == F.col("_loc")), "left"))
    ctx.warn("multi_lang_source_name_null", rows.where(F.col("source_name").isNull()).count())
    description = F.when(partner, F.coalesce(F.col("bio"), F.col("description"))).otherwise(F.col("description"))
    return rows.withColumn("description", description).select(*OUT_COLS)                          # D-SRV-13


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

`required_inputs` includes `multi_lang` to block mass soft-deletes. Consequence: while the landing table is empty (D-SRV-23), every run ends `FAILED` with "Đầu vào bắt buộc rỗng" and writes nothing. That outcome is this task's expected runtime result. The data path gets tested in the D-SRV-23 follow-up task.

### NB_GLD_SRV_POI_INFO, cell `srvinfohours` (pure Python, no Spark)

```python
# BEGIN_HOURS_PURE
import json

DAY_LABELS = {1: "Thứ Hai", 2: "Thứ Ba", 3: "Thứ Tư", 4: "Thứ Năm", 5: "Thứ Sáu", 6: "Thứ Bảy", 7: "Chủ Nhật"}
PARTNER_DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
CLOSED_VALUE = "Đóng cửa"
ALL_DAY = {"open_hour": 0, "open_minute": 0, "day_of_week": 0}
TIME_KEYS = ("open_hour", "open_minute", "close_hour", "close_minute")


def _int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _open(day, open_time, close_time):
    return {"day_of_week": day, "label": DAY_LABELS[day], "value": f"{open_time} - {close_time}",
            "open_time": open_time, "close_time": close_time, "is_open_all_day": False, "is_closed": False}


def _closed(day):
    return {"day_of_week": day, "label": DAY_LABELS[day], "value": CLOSED_VALUE,
            "is_open_all_day": False, "is_closed": True}


def _all_day(day):
    return {"day_of_week": day, "label": DAY_LABELS[day], "is_open_all_day": True, "is_closed": False}


def _dump(days):
    return json.dumps(days, ensure_ascii=False, separators=(",", ":"))


def google_hours(text):
    if text is None:
        return None, None                                            # rule 8, D-SRV-25
    try:
        doc = json.loads(text)
    except (TypeError, ValueError, RecursionError):
        return None, "GOOGLE_INVALID_JSON"
    if not isinstance(doc, list):
        return None, "GOOGLE_NOT_ARRAY"
    if len(doc) == 1 and isinstance(doc[0], dict) and doc[0] == ALL_DAY and all(_int(v) for v in doc[0].values()):
        return _dump([_all_day(day) for day in range(1, 8)]), None   # rule 3.1, 3.3
    by_day = {day: [] for day in range(1, 8)}
    for item in doc:
        if not isinstance(item, dict):
            return None, "GOOGLE_BAD_ELEMENT"
        src = item.get("day_of_week")
        if not _int(src) or not 0 <= src <= 6:
            return None, "GOOGLE_BAD_DAY"
        if not all(_int(item.get(key)) for key in TIME_KEYS):
            return None, "GOOGLE_BAD_TIME"
        day = 7 if src == 0 else src                                 # rule 1; close_day not read
        by_day[day].append(_open(day, f"{item['open_hour']:02d}:{item['open_minute']:02d}",
                                 f"{item['close_hour']:02d}:{item['close_minute']:02d}"))   # rules 4, 5, 7, 9
    return _dump([obj for day in range(1, 8) for obj in (by_day[day] or [_closed(day)])]), None   # rule 6


def partner_hours(text):
    if text is None:
        return None, None                                            # §1.5
    try:
        doc = json.loads(text)
    except (TypeError, ValueError, RecursionError):
        return None, "PARTNER_INVALID_JSON"
    if not isinstance(doc, dict):
        return None, "PARTNER_NOT_OBJECT"
    days = []
    for day, key in enumerate(PARTNER_DAYS, start=1):
        if key not in doc:
            days.append(_closed(day))                                # no day key
            continue
        entry = doc[key]
        if not isinstance(entry, dict):
            return None, "PARTNER_BAD_DAY"
        if "hours" not in entry or entry["hours"] == []:
            days.append(_closed(day))                                # no / empty hours; status not read
            continue
        hours = entry["hours"]
        if not isinstance(hours, list):
            return None, "PARTNER_BAD_HOURS"
        if len(hours) > 1:
            return None, "PARTNER_MULTI_HOURS"                       # §1.5 stop
        item = hours[0]
        if not isinstance(item, dict) or not isinstance(item.get("open_time"), str) \
                or not isinstance(item.get("close_time"), str):
            return None, "PARTNER_BAD_HOURS"
        days.append(_open(day, item["open_time"], item["close_time"]))
    return _dump(days), None


def operating_hours(source_name, text):
    source = (source_name or "").strip().lower()
    if source == "google":
        return google_hours(text)
    if source == "partner":
        return partner_hours(text)
    return None, "SOURCE_NOT_GOOGLE_PARTNER"
# END_HOURS_PURE
```

How this code reads the rules:
- Google `[]`: no element on any day, so rules 6 and 9 give seven closed objects. That is the literal rule; the probe found 0 such rows.
- Partner `hours: null` and a day value of JSON `null` are not among the §1.5 forms, so they stop the run (`PARTNER_BAD_*`). The probe found 0 such rows.
- Serialization is compact with `ensure_ascii=False`. The §1.4 contract is the parsed JSON value plus key order.

What the probe says about current data:
- Google `missing_close 3` equals `all_day_exact 3`. Every all-day row is also tagged `missing_close`, so the two sets are the same. No Google row stops today.
- Partner rows are 13 null, 10 with a single `hours` element, and 1 with missing `hours`, so no partner row stops either.

### NB_GLD_SRV_POI_INFO, cell `srvinfobuild`

```python
ENT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_category", "types_json", "phone",
            "email", "website_url", "operating_status", "opening_hours_text", "holiday_exceptions")
DEST_COLS = ("poi_id", "updated_at", "destination_id", "full_address", "street", "ward", "district", "city",
             "country_code", "postal_code", "lat", "lng")
OUT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_category", "subcategory_tags",
            "destination_id", "full_address", "street", "ward", "district", "city", "country_code", "postal_code",
            "lat", "lng", "phone", "email", "website_url", "operating_status", "is_verified", "is_recommended",
            "is_bookable", "operating_hours", "holiday_exceptions")
HOURS_TYPE = T.StructType([T.StructField("value", T.StringType()), T.StructField("error", T.StringType())])
_hours = F.udf(lambda source, text: operating_hours(source, text), HOURS_TYPE)
SRC = F.lower(F.trim(F.col("source_name")))


def _require(df, cols, name, hint=""):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ConfigError(f"gld_srv_poi_info: {name} thiếu {missing}{hint}")


def _destination(des, keys):
    # D-SRV-21: updated_at lớn nhất; trùng mà updated_at NULL hoặc bằng nhau -> dừng, không chọn dòng.
    w = Window.partitionBy("poi_id")
    d = (des.join(keys, "poi_id", "left_semi")
         .withColumn("_n", F.count(F.lit(1)).over(w))
         .withColumn("_nulls", F.count(F.when(F.col("updated_at").isNull(), 1)).over(w))
         .withColumn("_max", F.max("updated_at").over(w))
         .withColumn("_top", F.count(F.when(F.col("updated_at") == F.col("_max"), 1)).over(w)))
    bad = d.where("_n > 1 AND (_nulls > 0 OR _top > 1)").select("poi_id").distinct().count()
    if bad:
        raise QualityGateError(f"gld_srv_poi_info: slv_enr_poi_destination {bad} poi_id trùng, updated_at NULL hoặc bằng nhau")
    ctx_dup = d.where("_n > 1").select("poi_id").distinct().count()
    return d.where("_n = 1 OR updated_at = _max").drop("_n", "_nulls", "_max", "_top", "updated_at"), ctx_dup


def build(ctx):
    ent = ctx.input("entity", live_only=False)
    des = ctx.input("destination", live_only=False)
    ml = ctx.input("multi_lang", live_only=False)
    _require(ent, ENT_COLS, "slv_poi_entity_non_enrich")
    _require(des, DEST_COLS, "slv_enr_poi_destination", ": chạy srvpoipy của NB_CREATE_DDL")
    _require(ml, ("poi_id",), "slv_enr_poi_info_multi_lang")
    ent = ent.select(*ENT_COLS)
    des, dup = _destination(des.select(*DEST_COLS), ent.select("poi_id"))
    both = (ent.select("poi_id").join(des.select("poi_id"), "poi_id", "left_semi")
            .join(ml.select("poi_id").distinct(), "poi_id", "left_semi").withColumn("_both", F.lit(True)))
    is_google = F.coalesce(SRC == "google", F.lit(False))
    rows = (ent.join(both, "poi_id", "left").where(~is_google | F.col("_both").isNotNull())
            .join(des, "poi_id", "left").withColumn("_h", _hours(F.col("source_name"), F.col("opening_hours_text"))))
    out = rows.select(
        *ENT_COLS[:5], F.col("types_json").alias("subcategory_tags"), *DEST_COLS[2:], "phone", "email",
        "website_url", "operating_status", F.lit(None).cast("boolean").alias("is_verified"),
        F.coalesce(SRC == "partner", F.lit(False)).alias("is_recommended"),
        F.lit(None).cast("boolean").alias("is_bookable"), F.col("_h.value").alias("operating_hours"),
        "holiday_exceptions", F.col("_h.error").alias("_err"))
    errors = {r["_err"]: r["n"] for r in out.where("_err IS NOT NULL").groupBy("_err").count()
              .withColumnRenamed("count", "n").collect()}
    if errors:
        raise QualityGateError("gld_srv_poi_info: operating_hours " + json_dumps(errors))
    out = out.drop("_err")
    ctx.metrics.update(destination_dup_poi=dup, partner_rows=out.where(SRC == "partner").count(),
                       google_rows_kept=out.where(SRC == "google").count(),
                       operating_hours_null=out.where("operating_hours IS NULL").count())
    return out.select(*OUT_COLS)


SPEC = NodeSpec(
    trg_tbl="gld_srv_poi_info",
    inputs={"entity": "slv_poi_entity_non_enrich", "destination": "slv_enr_poi_destination",
            "multi_lang": "slv_enr_poi_info_multi_lang"},
    pk=("poi_id",),
    build=build,
    required_inputs=("entity",),
    write_mode="MERGE",
)
```

Notes:
- `*DEST_COLS[2:]` expands to the ten mapped destination columns in model-design order.
- An unknown `source_name` survives the filter, because it isn't Google, and then stops on `SOURCE_NOT_GOOGLE_PARTNER`. There is no separate `block_checks` entry.
- `Window`, `F`, `T`, `json_dumps`, `uuid_md5`, `ConfigError` and `QualityGateError` all come from `%run NB_LIB_TRANSFORM_SLV_GLD`.

### Notebook shells

Copy the cell layout and notebook `metadata` from `NB_SLV_POI_ENTITY_NON_ENRICH.ipynb`. It already knows the three lakehouses that `NB_ENR_POI_INFO` uses for gold.
- multi_lang cells: `srvmlmd`, `srvmlparam`, `srvmlrun`, `srvmlbuild`, `srvmlres`, `srvmlexit`.
- info cells: `srvinfomd`, `srvinfoparam`, `srvinforun`, `srvinfohours`, `srvinfobuild`, `srvinfores`, `srvinfoexit`.
- The params cells are identical to `b1entityparam` (same 8 params, `tags: ["parameters"]`).
- `res` is `RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_name, p_trg_fq, p_history_limit)`.
- `exit` is `notebookutils.notebook.exit(finish_node(RES))`.

## DDL

### NB_SETUP_INITIAL_DDL

- `init_tables` `TABLE_SPECS`, edited in place:
  - In the `slv_enr_poi_destination` spec, after `('updated_at', 'TIMESTAMP', None)`, add `('destination_id','STRING',None)`, `('country_code','STRING',None)`, `('postal_code','STRING',None)`, `('lat','DOUBLE',None)`, `('lng','DOUBLE',None)`. `ADD COLUMNS` appends at the end, so new and patched environments come out identical.
  - Insert the two gold specs after `slv_enr_poi_review_multi_lang` and before the entity spec. Mark them with `# [THÊM 24/10] 20261024-gld-srv-poi-from-mapping: gold serving, cột = build + TECH_COLUMNS (D-SRV-24).`
  - Each gold spec uses `"partition": None, "comment": None, "props": PROPS`, with columns exactly equal to `srvpoipy` `GOLD_COLS` as `(name, dtype, None)`.
  - The entity spec stays last, because `test_poi_entity_columns_derived` uses `specs[-1]`.
- `init_seed_ctrl`:
  - Add `_GLD30, _G = "PL_VV_TRANS_SLV_TO_GLD_30P", "lh_vv_gold.dbo"`.
  - Append six rows under `# [THÊM 24/10] 20261024-gld-srv-poi-from-mapping`, in `EDGES_ON` order. Each row is `(_GLD30, _S, '<src>', _G, '<trg>', 1, 1, 'RECOMPUTE', None, None, '<nb>')`.
  - The row count goes from 53 to 59.
- `init_plan`: change `16` to `18` in both the check and the message.

No `ALTER`/`INSERT INTO`/`ADD COLUMNS` goes in this notebook (`test_no_destructive_sql`, `test_example_patch_dual_update`).

### NB_CREATE_DDL `srvpoimd` + `srvpoipy` (appended last)

- Markdown `srvpoimd`: `[THÊM 24/10] 20261024-gld-srv-poi-from-mapping`.
- Code `srvpoipy`:

```python
# [THÊM 24/10] 20261024-gld-srv-poi-from-mapping
# 1. slv_enr_poi_destination: thêm destination_id, country_code, postal_code STRING, lat, lng DOUBLE cho phép NULL
#    sau updated_at (D-SRV-11), một lệnh. Task này không nạp 5 cột (D-SRV-23).
# 2. Tạo lh_vv_gold.dbo.gld_srv_poi_multi_lang, gld_srv_poi_info theo NB_SETUP_INITIAL_DDL (D-SRV-24). Không DROP.
# 3. Thêm 6 cạnh RECOMPUTE trên PL_VV_TRANS_SLV_TO_GLD_30P (D-SRV-22). Không gắn PL_VV_TRANS_SLV_TO_ENR_15P.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P suốt cell. Chạy lại: không đổi gì.
# Sau cell này không chạy lại enrflagpy: hợp đồng slv_enr_poi_destination trong đó là bản 8 cột.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30P"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
DEST_FQ = "lh_vv_silver.dbo.slv_enr_poi_destination"
DEST_BASE = [
    ("poi_id", "STRING NOT NULL"), ("street", "STRING"), ("ward", "STRING"), ("district", "STRING"),
    ("city", "STRING"), ("full_address", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
]
DEST_NEW_COLS = [
    ("destination_id", "STRING"), ("country_code", "STRING"), ("postal_code", "STRING"), ("lat", "DOUBLE"),
    ("lng", "DOUBLE"),
]
GOLD_COLS = {
    "lh_vv_gold.dbo.gld_srv_poi_multi_lang": [
        ("poi_id", "STRING NOT NULL"), ("lang", "STRING NOT NULL"), ("source_name", "STRING"),
        ("time_to_spend", "STRING"), ("best_time", "STRING"), ("cost_vnd", "STRING"), ("description", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
    ],
    "lh_vv_gold.dbo.gld_srv_poi_info": [
        ("poi_id", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
        ("business_sector", "STRING"), ("business_category", "STRING"), ("subcategory_tags", "STRING"),
        ("destination_id", "STRING"), ("full_address", "STRING"), ("street", "STRING"), ("ward", "STRING"),
        ("district", "STRING"), ("city", "STRING"), ("country_code", "STRING"), ("postal_code", "STRING"),
        ("lat", "DOUBLE"), ("lng", "DOUBLE"), ("phone", "STRING"), ("email", "STRING"), ("website_url", "STRING"),
        ("operating_status", "STRING"), ("is_verified", "BOOLEAN"), ("is_recommended", "BOOLEAN"),
        ("is_bookable", "BOOLEAN"), ("operating_hours", "STRING"), ("holiday_exceptions", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
    ],
}
EDGES_ON = [
    (1, "slv_enr_poi_info_multi_lang", "lh_vv_gold.dbo", "gld_srv_poi_multi_lang", "RECOMPUTE", "NB_GLD_SRV_POI_MULTI_LANG", 1),
    (2, "slv_poi_entity_non_enrich", "lh_vv_gold.dbo", "gld_srv_poi_multi_lang", "RECOMPUTE", "NB_GLD_SRV_POI_MULTI_LANG", 1),
    (3, "slv_pn_business_service_i18ns", "lh_vv_gold.dbo", "gld_srv_poi_multi_lang", "RECOMPUTE", "NB_GLD_SRV_POI_MULTI_LANG", 1),
    (4, "slv_poi_entity_non_enrich", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
    (5, "slv_enr_poi_destination", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
    (6, "slv_enr_poi_info_multi_lang", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
]
LOCK = "srvpoi-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


def _create_sql(fq, cols):
    # Cùng câu với create_sql(spec) của NB_SETUP_INITIAL_DDL (test kiểm tra).
    body = ",\n    ".join(f"`{name}` {dtype}" for name, dtype in cols)
    return f"CREATE TABLE IF NOT EXISTS {fq} (\n    {body}\n) USING DELTA\nTBLPROPERTIES ({PROPS})"


def _edge_rows():
    trgs = ", ".join(sorted({f"'{trg}'" for _q, _src, _s, trg, _m, _n, _p in EDGES_ON}))
    return [(r["pl_name"], r["src_tbl"], r["trg_tbl"], r["is_active"], r["n"]) for r in spark.sql(f"""
    SELECT pl_name, src_tbl, trg_tbl, is_active, count(*) AS n FROM {CFG}
    WHERE trg_schema = '{GLD}' AND trg_tbl IN ({trgs})
    GROUP BY pl_name, src_tbl, trg_tbl, is_active
    """).collect()]
```

The rest of the cell, in order:

1. **Lock.** Copy the `enrflagpy` lock-row `MERGE INTO {WM} … WHEN NOT MATCHED THEN INSERT`, then `held = False` / `failed = None` / `try:`. Inside the `try`, copy the lease `UPDATE {WM} … WHERE watermark_id = '{WID}' AND (lock_exec_id IS NULL OR coalesce(lock_at < … {LEASE_MINUTES} MINUTES, true))`, the owner check (`raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")`), `held = True`, and the `nb_name` column check.
2. **`# Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.`** Collect every failure into `issues`, then `raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))`. Write nothing before this point.
   - `DEST_FQ` missing: stop and point to `enrflagpy` / `NB_SETUP_INITIAL_DDL`.
   - Destination schema: `got = _schema(DEST_FQ)` must satisfy `len(got) >= len(DEST_BASE)` and `got == _want(DEST_BASE + DEST_NEW_COLS)[:len(got)]` (name, type, nullability, position). Then `add = DEST_NEW_COLS[len(got) - len(DEST_BASE):]`.
   - Gold tables: `create = [fq for fq in GOLD_COLS if not spark.catalog.tableExists(fq)]`. Each existing fq must satisfy `_schema(fq) == _want(GOLD_COLS[fq])`.
   - Edges, from `_edge_rows()`: no row with `pl != PL and is_active == 1`. Every `PL` row must have `(src, trg)` in `EDGES_ON`, `is_active == 1` and `n == 1` ("Cell không tự bật cạnh").
3. **Writes:**
   - if `add`: one `spark.sql(f"ALTER TABLE {DEST_FQ} ADD COLUMNS (" + ", ".join(f"`{c}` {t}" for c, t in add) + ")")`;
   - `_create_sql` for each fq in `create`;
   - one `INSERT INTO {CFG} … SELECT COALESCE((SELECT MAX(id) FROM {CFG}), 0) + t.seq, '{PL}', '{SLV}', … FROM VALUES … WHERE NOT EXISTS (… c.pl_name = '{PL}' AND c.src_schema = '{SLV}' AND c.src_tbl = t.src_tbl AND c.trg_schema = t.trg_schema AND c.trg_tbl = t.trg_tbl)`. The text is the same as in `enrflagpy`.
4. **`# Sau khi ghi`:**
   - destination `== _want(DEST_BASE + DEST_NEW_COLS)`;
   - each gold fq `== _want(cols)`;
   - `{(src, trg): n for … if flag == 1}` equals `{(src, trg): 1 for EDGES_ON}`;
   - otherwise `raise RuntimeError("Sau khi ghi: " + …)`.
   - Print a summary with no data values.
5. **`except Exception as exc: failed = exc; raise`** and **`finally:`** with the `enrflagpy` release. It runs only `if held` and only `WHERE … lock_exec_id = '{LOCK}'`.

There is no ENR_15P lock, following the `peholpy` precedent. A nullable `ADD COLUMNS` is a non-data op (`DEFAULT_NON_DATA_OPS`), so it doesn't dirty ENR_15P edges. Run the cell while enrichment writers are idle.

## Ordering

1. Run `srvpoipy` before any node run. The nodes can't resolve without the edges. Also, if `ensure_target` created the gold tables first, it would make them with nullable keys, which `schema_diff` then reports.
2. In one `NB_00_ORCHES_SLV_TO_GLD` run, both nodes are level 0 and independent. NB_00 pins the input versions, so both tables read the same snapshot.
3. Manual node runs don't advance edges, so every manual run recomputes everything. That is correct, because builds are full anyway.

## Transaction and commit boundaries

- Node: at most one Delta commit per target per run (the MERGE). It is skipped when the diff is all zero. `ensure_target` adds nothing, because the DDL already matches.
- The two gold tables commit independently. There is no cross-table atomicity.
- `srvpoipy`: at most one ALTER, up to two CREATEs, and one INSERT, plus the lock-row updates. Each step is guarded, so a rerun repeats nothing.

## Idempotency

- Builds are deterministic:
  - the hours function is pure;
  - business columns contain no timestamps;
  - the destination winner is unique or the run stops.
- `row_hash` MERGE: a rerun on the same inputs gives `inserted = updated = deactivated = 0` and no commit. `updated_at` changes only when the hash changes.
- `srvpoipy` and `NB_SETUP_INITIAL_DDL` reruns change nothing.

## Concurrency

- Flow lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`:
  - a manual RUN takes it;
  - NB_00 holds it and passes it on;
  - `srvpoipy` holds it while creating tables and inserting edges.
  - A DRY_RUN alongside a running flow only gets a WARN.
- One active owner pl per target (`build_dag`).
- `_30P` doesn't match `CADENCE_RE`, so the lib WARNs and skips the cadence check against the ENR_15P-owned entity. This is accepted.

## Retry and recovery

- Transient MERGE failures: lib `with_retry`.
- Any failure before MERGE leaves the target unchanged and logs `FAILED` in `ctrl_log_table_run`. Fix the cause and rerun; the full recompute converges.
- A stale lock clears after the 90-minute lease.

## Partial failure

- multi_lang FAILED (expected while the landing table is empty) and info SUCCESS: each table is internally consistent. NB_00 reports the run as failed and advances only the info edges.
- `srvpoipy` interrupted: every partial state passes the stop-before-write checks (a prefix of the new columns, an exact gold table, active edges), so a rerun completes.
- An hours or QG stop writes nothing.

## Observability

- `ctrl_log_table_run.qg_json` per node:
  - QG blocks;
  - warn `multi_lang_source_name_null`;
  - metrics `destination_dup_poi`, `partner_rows`, `google_rows_kept`, `operating_hours_null`;
  - plus inserted/updated/deactivated counts.
- Stop messages carry codes and counts only.
- Consumers read live rows with `deleted_at IS NULL`.

## Security

- No secrets. SQL identifiers are constants.
- `phone`, `email` and `holiday_exceptions` reach the product per mapping info §1.2. They already exist on silver.
- Logs and probes print no raw values.

## Rollout

1. Triage adds the three test paths (see Status).
2. Implement, then run local tests.
3. In DEV:
   - run `srvpoipy`;
   - run `NB_SETUP_INITIAL_DDL` with `p_apply=false`;
   - run info `DRY_RUN`, then `RUN`, then `RUN` again;
   - run multi_lang `RUN` and expect FAILED, empty input;
   - run `NB_00_ORCHES_SLV_TO_GLD` with `p_pl_name=PL_VV_TRANS_SLV_TO_GLD_30P` and `p_mode=PLAN`.
4. Don't schedule a GLD_30P pipeline before the D-SRV-23 follow-up. multi_lang fails until the landing table has rows.

## Rollback and forward recovery

- No DROP.
- To stop serving: a later patch cell sets the six GLD_30P edges to `is_active = 0`. The nodes then can't resolve and the tables freeze.
- Bad data: fix the code and rerun. MERGE overwrites by hash, and rows that disappear are soft-deleted and come back when they reappear (`deleted_at = NULL`).
- The new destination columns are nullable and can stay.

## Alternatives

| Choice | Selected | Rejected, and why |
|---|---|---|
| Write path | lib MERGE (D-SRV-24) | Hand-written MERGE: no lock, QG, log or edges. APPEND: breaks the grain. |
| Hours | pure Python UDF | Spark `from_json`/`transform`: omitting keys and stopping per code is awkward, and it can't be tested locally. |
| Destination dedup | window + stop on a null or tied maximum | `row_number`: non-deterministic, so `row_hash` would flap. A second sort key: the ledger forbids it. |
| multi_lang empty input | `required_inputs` guard; FAILED today | No guard: an empty landing table would later soft-delete every row. |
| Hours/node tests | new `tests/test_gld_srv_poi_contract.py` | Adding them to the DDL contract file mixes concerns. Kept only as the fallback. |

## Implementation plan

1. Stop for triage scope.
2. `NB_SETUP_INITIAL_DDL`: `init_tables`, `init_seed_ctrl`, `init_plan` (see "DDL").
3. `NB_CREATE_DDL`: append `srvpoimd` and `srvpoipy`.
4. Create the two notebooks (see "Build design").
5. Tests (see "Verification").
6. Run local tests, then DEV.

## Verification

`tests/test_initial_ddl_contract.py`:
- `test_table_inventory_matches_sources`: add `_assign(srv, "GOLD_COLS").keys()` to `found`; change `16` to `18`.
- `test_columns_match_sources`:
  - the destination expectation becomes enrflagpy `LANDING_COLS[dest] + srvpoipy DEST_NEW_COLS`;
  - each gold fq equals `[(c, t, None) for c, t in GOLD_COLS[fq]]`, with `props == PROPS`.
- `test_pipeline_config_rows_match_sources`: append `(PL, silver, src, schema, trg, 1, priority, mode, None, None, nb)` for each `srvpoipy` `EDGES_ON` row; change `53` to `59`.
- `test_flag_patch_create_matches_init`: the destination contract becomes `LANDING_COLS[dest] + DEST_NEW_COLS`.
- New `test_gld_srv_patch_create_matches_init`:
  - `srvpoipy._create_sql(fq, cols) == create_sql(spec)` for both gold fqs and for the destination with `DEST_BASE + DEST_NEW_COLS`;
  - `DEST_BASE == enrflagpy LANDING_COLS[dest]`.
- New `test_gld_srv_patch_guards`:
  - token order `held = True` < `Dừng trước khi ghi` < `ALTER TABLE` < `INSERT INTO {CFG}` < `Sau khi ghi` < `finally:`;
  - in code without comments: none of `DROP`, `DELETE`, `TRUNCATE`, `UPDATE {CFG}`, `REPLACE`, `columnMapping`, ` AFTER `;
  - `ALTER TABLE` appears once;
  - `LEASE_MINUTES = 90`;
  - `lock_exec_id = '{LOCK}'`.

`tests/test_gld_srv_poi_contract.py` (new): exec the `srvinfohours` cell.
- `test_google_case1` and `test_google_case2_all_day`: parse the "Trước" and "Sau" JSON blocks under `#### Case 1` and `#### Case 2` in `docs/context/mapping_gld_srv_poi_info.md`. Assert `json.loads(out) == after` and the per-element key lists are equal.
- `test_google_multi_period_rule9`: two Monday elements (08–12, 13–17). The first two output objects equal the §1.3 rule 9 example; the output has 8 elements.
- `test_google_null_and_empty`: `None` gives `(None, None)`; `"[]"` gives 7 closed objects.
- `test_google_stop_codes`: invalid JSON, an object at top level, `day_of_week` 7, a bool hour, missing `close_*` outside the all-day form, and the all-day form written with `0.0`. Each returns its expected code.
- `test_partner_single_hours`: strings are kept unchanged, there are 7 objects, and `status` is ignored.
- `test_partner_closed_forms`: a missing day key, missing `hours`, `hours: []`, and a status-only object.
- `test_partner_stop_codes`: two `hours` elements, `hours: null`, a day set to `null`, a non-string time.
- `test_unknown_source_stops`.
- `test_node_specs` (text/AST over `srvmlbuild` and `srvinfobuild`):
  - `pk`, `inputs`, `required_inputs`, `write_mode="MERGE"`;
  - `live_only=False` appears 3 times per notebook;
  - `PARTNER = "partner"` and `uuid_md5(F.col("business_service_id"), F.lit(PARTNER))`;
  - no `lh_vv_gold` and no `deleted` in code.
- `test_build_columns_match_ddl`: the `OUT_COLS` of each build cell plus the TECH names equals the names in `srvpoipy` `GOLD_COLS`.

Tail-position updates (scope addition):
- `test_info_patch_cell_guards` and `test_create_ddl_patch`: change the slices to `ids[-12:-6]`, `ids[-6:-4]`, `ids[-4:-2]`, and add `ids[-2:] == ["srvpoimd", "srvpoipy"]`.

Commands:
- `python -m pytest tests/test_initial_ddl_contract.py tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
- `python -m pytest -q`

Fabric DEV (runtime gate):
- `srvpoipy` printout. A second run changes nothing.
- `NB_SETUP_INITIAL_DDL p_apply=false`: 18 specs, `EXISTS_OK`, no `schema_issues`.
- Info `RUN`: SUCCESS with 24 rows inserted (partner only, because destination and multi_lang are empty). The second `RUN`: diff 0/0/0, no new Delta version.
- Info SQL:
  - `count(*) = count(DISTINCT poi_id) = 24` among live rows;
  - `operating_hours IS NULL` for 13 rows;
  - `json_array_length(operating_hours) = 7` for the other 11;
  - `is_recommended` true for all;
  - `is_verified`, `is_bookable` and the destination columns all null.
- multi_lang `RUN`: FAILED with "Đầu vào bắt buộc rỗng"; the target has 0 rows.
- NB_00 `PLAN`: the DAG has 2 nodes and no error.
- Google transform on real text (read-only, after running the `srvinfohours` cell in a scratch session). Expect only `None` codes:

```python
from collections import Counter
rows = spark.table("lh_vv_silver.dbo.slv_poi_entity_non_enrich").select("source_name", "opening_hours_text").collect()
print(Counter(operating_hours(r[0], r[1])[1] for r in rows))
```
