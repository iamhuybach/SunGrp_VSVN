RESULT: PASS

## Main brief

### Decision
Remove the four op columns from the entity. Add `website_url`: google through a left join to `slv_3p_poi_contact` on `poi_id`, partner through `top_level_text`, a Python top-level JSON lookup. Add the five estimates by widening the dictionary structs that are already matched (`_cat` for google, `_pc` for partner). They are NULL when there is no matched row.
Carry `service_flags` on the amenity condition tuple. Add the edge `slv_3p_poi_contact → slv_poi_entity_non_enrich`, giving 6 entity edges.
DEV recovery is drop and reinit of the two node tables. `NB_SETUP_POI_AMENITY` recreates the amenity table, `ensure_target` recreates the entity table, and NB_00 recreates the edge watermarks.
D8 note: `get_json_object` returns non-string JSON values as text, which breaks D8's "giá trị không phải chuỗi JSON thì null". The mechanism therefore changes; the semantics stay.

### Invariants Main must preserve
- Entity has one row per `poi_id`. A duplicate non-null `poi_id` in contact raises `QualityGateError` inside `build()`, before any MERGE.
- The four op columns are absent from the `b1entitybuild` output and from `TABLE_SPECS`. `TABLE_CONFIGS_3P` and `SNAPSHOT_TECH_COLUMNS` do not change.
- Partner `website_url` is the top-level value only when it is a JSON string. `""` is kept and nothing is trimmed. Everything else is NULL.
- The node adds no new join to either dictionary. Estimates come from `_p`/`_m`/`_pc`, and `service_flags` comes from `cond`.
- `SPEC.inputs` equals the active edges: 6 for the entity and 3 for the amenity. `required_inputs` includes `contact`.
- Entity `TABLE_SPECS` equals the build columns plus `TECH_COLUMNS`, in this order: `POI_COLS`, `website_url`, `ADDRESS_COLS`, `CATEGORY_COLS`, `ESTIMATE_COLS`, then tech columns. Amenity `TABLE_SPECS` equals `c1setupddl`, with `service_flags` after `amenity_vi`.
- The `BEGIN_EDGE_PRECHECK` block stays byte-identical in both setup notebooks.
- `NB_CREATE_DDL`: only appended cells. No DROP, DELETE, ALTER or UPDATE.
- The runbook drops only the two tables and deletes only `wm_e__` rows whose `trg_tbl` is one of them. It never deletes `wm_flow__`. The setup PLAN must show `missing_keys = 0` before apply.
- A second NB_00 run gives `NO_DATA` for both nodes.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | `.ai/tasks/.../decision.md` | `Quyết định hiện hành` | Add D11 (NULL estimates when there is no match) and D12 (positions). Amend D8 with the `top_level_text` mechanism and the last-key-wins rule. | Rows present |
| 2 | `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` | `b1entityjson` | Add `JSON_NOT_STRING` and `top_level_text` inside the markers (doc §7.1) | The block execs and the new test passes |
| 3 | same | `b1entitybuild` constants | Drop the op columns from `POI_COLS`. Add `CONTACT_COLS`, `ESTIMATE_COLS`, `ESTIMATE_TYPES` and the new `OUT_COLS`. Add the `website_url_of` UDF. | Matches §7.1 |
| 4 | same | `_google` | Add `ESTIMATE_COLS` to the `_cat` struct. Add the contact duplicate guard and the left join. Add the `with_website` metric. Add estimate picks with a `F.lit(None)` default. | Matches §7.1 |
| 5 | same | `_partner` | Add the `_web` UDF column. Add `ESTIMATE_COLS` to the `_pc` struct. Add the `partner_website` metric. Add `website_url` and the estimates to `cols`. | Matches §7.1 |
| 6 | same | `build`, `SPEC` | Add column checks for contact and svc, and the estimate type check. Add the `dict_estimate_null` metric. Add the `contact` input and required role. | Matches §7.1 |
| 7 | same | `b1entitymd` | One line on the contact and `website_urls` inputs | Text updated |
| 8 | `notebooks/NB_SLV_POI_AMENITY.ipynb` | `d1amenmatch` `match_conditions` docstring | Rows may carry `service_flags`, and the condition tail is `(kind, path, value)` | Docstring only |
| 9 | same | `d1amenbuild` | `COND_SCHEMA` and `OUT_COLS` gain `service_flags`. Add the dictionary type check. Collect `service_flags`. Use `n_flag` with `c[-3]`. Add the `conditions_service_flags` metric. | Matches §7.2 |
| 10 | `notebooks/NB_SETUP_POI_ENTITY.ipynb` | `a1setupplan` `planned_edges` | Add `slv_3p_poi_contact` | 6 entries |
| 11 | same | `a1setupedges` `_write_edges` | Add the contact UPSERT at seq 6 (renumber amenity to 7–9). Add contact to the `dup` IN list. Add contact to `entity_upserts`. | §7.3 |
| 12 | `notebooks/NB_SETUP_POI_AMENITY.ipynb` | `c1setupedges` | Add contact to the `entity_edges_ok` IN list, and change `!= 5` to `!= 6` | §7.3 |
| 13 | same | `c1setupddl` | Add `service_flags STRING` after `amenity_vi` in the CREATE and in `EXPECTED[AMENITY_FQ]` | §7.3 |
| 14 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_tables` `TABLE_SPECS` | Entity columns per §7.4. Amenity gets `service_flags`. Mark the comment `[SỬA 20/10]`. | Tests in row 19 pass |
| 15 | same | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` | Add the contact edge row after the i18ns entity row | 54 rows |
| 16 | `notebooks/NB_CREATE_DDL.ipynb` | end of notebook | Append `entwebmd` and `entwebpy` (doc §7.5 verbatim) | Last two ids |
| 17 | `tests/test_poi_entity_contract.py` | `test_entity_node_contract`, `_ENTITY_UPSERTS`, `test_setup_contract`, `test_create_ddl_patch`; new `test_partner_website_top_level`, `test_create_ddl_contact_edge_patch` | Per §20.1 | Pass |
| 18 | `tests/test_poi_amenity_contract.py` | `test_amenity_node_contract`, `test_setup_contract`; new `test_match_conditions_carries_service_flags`, `test_amenity_ddl_matches_node` | Per §20.1 | Pass |
| 19 | `tests/test_initial_ddl_contract.py` | `test_poi_entity_columns_derived`, `test_pipeline_config_rows_match_sources` | Per §20.1 (no snapshot columns, contact and estimate types, 54 rows) | Pass |
| 20 | `docs/context/01_DATA_MODEL.md` | §6 rows N6 and N7 | Contact input, `website_url`, estimates, no op columns, `service_flags` | Text |
| 21 | `docs/context/CTRL_TABLES_CONTEXT.md` | §3 L114–126, §4 Thao tác, §10 | 6 edges with the contact row, a DEV reset note, and a 20/10 history row | Text |
| 22 | `.ai/tasks/.../runtime-runbook.md` | whole file | Write R0–R5 from doc §17 in Vietnamese, with the SQL as given | User can run it |

### Order and stop points
1. Edit row 1 (ledger). **Stop (user decision, optional):** if the user rejects D11 or D12, only the constants and the column order change.
2. Rows 2–9 (nodes). Then rows 10–16 (setup and DDL). Then rows 17–19 (tests). Run the pytest commands. **Stop (evidence)** until they pass.
3. Rows 20–22 (docs and runbook). Then reviewers.
4. Runtime, run by the user on DEV:
   1. R0: deploy.
   2. R1: pre-checks. **Stop (user decision)** if the contact duplicate count is above 0 (D3) or any type check fails.
   3. R2: setup PLAN. **Stop** if any `missing_keys` is above 0 or `unseeded_rows` is not 0, because applying would be a reseed.
   4. R3: reset (separate apply step).
   5. R4: rebuild.
   6. R5: verify. **Stop (evidence)** and save the results under `evidence/results/`. Main does not set `gates.runtime`.

### Tests and verification
- `python -m pytest tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest -q`
- New tests:
  - `test_partner_website_top_level`
  - `test_create_ddl_contact_edge_patch`
  - `test_match_conditions_carries_service_flags`
  - `test_amenity_ddl_matches_node`
- Updated tests:
  - `test_entity_node_contract`
  - `test_setup_contract` (both files)
  - `test_create_ddl_patch`
  - `test_amenity_node_contract`
  - `test_poi_entity_columns_derived`
  - `test_pipeline_config_rows_match_sources`
- DEV checks: doc §20.2 items 1–11. These cover schema, grain, google and partner `website_url` parity, estimate parity, `service_flags` parity, recreated watermarks, `NO_DATA` on rerun, and unchanged dictionaries.

### Read only if needed
- §3 Inputs and resolved open points → rows 1, 3–5
- §4 Invariants → all rows
- §7.1 Entity node (code) → rows 2–7
- §7.2 Amenity node (code) → rows 8–9
- §7.3 Setup notebooks and edges → rows 10–13
- §7.4 NB_SETUP_INITIAL_DDL → rows 14–15
- §7.5 NB_CREATE_DDL patch cell (code) → row 16
- §7.6 Docs → rows 20–21
- §8 Alternatives → rows 2, 5, 9, 13, 16
- §9–§14 Ordering, commits, idempotency, concurrency, retry, partial failure → row 22
- §17 Rollout runbook spec → row 22
- §18 Rollback and forward recovery → row 22
- §20 Verification → rows 17–19, 22

# Architecture — 20261020-entity-drop-op-cols-add-website

Risk: high. This document sets the code design for the two node notebooks, the three setup or DDL notebooks, the tests and the docs. It also specifies what the DEV runbook must contain. `runtime-runbook.md` is a task artifact that Main writes; §17 gives its required content. No `FILE:` blocks are used, because every target is a large notebook or test file that Main edits in place. Code longer than 15 lines is under the headings that the brief's edit list cites.

## 1. Scope

- `NB_SLV_POI_ENTITY_NON_ENRICH`:
  - Drop the four op columns.
  - Add `website_url`, as a google left join to `slv_3p_poi_contact` and a partner top-level JSON key.
  - Add the five estimate columns, carried on the dictionary row that is already matched.
  - Add the `contact` input role.
- `NB_SLV_POI_AMENITY`: carry `service_flags` on the matched condition row.
- `NB_SETUP_POI_ENTITY`: add the edge `slv_3p_poi_contact → slv_poi_entity_non_enrich` to the canonical edge set. There are then 6 entity edges.
- `NB_SETUP_POI_AMENITY`: the entity-edge prerequisite becomes 6. The `slv_poi_amenity` DDL and `EXPECTED` gain `service_flags`.
- `NB_SETUP_INITIAL_DDL`: `TABLE_SPECS` for both node tables changes, and `PIPELINE_CONFIG_ROWS` gains the contact edge.
- `NB_CREATE_DDL`: one patch cell at the end. It inserts the contact edge and reports whether a reset is needed. It does no DROP and no ALTER.
- Tests in the three contract files.
- Docs: `01_DATA_MODEL.md` §6 N6/N7, and `CTRL_TABLES_CONTEXT.md` §3, §4 and §10.
- The DEV runbook specification (§17).

## 2. Non-goals

- The four op columns on `slv_3p_*`, and the 3P registry. `TABLE_CONFIGS_3P` does not change.
- Reseeding `ref_dictionary_place_type` or `ref_dictionary_amenities`, and any change to `BEGIN_PLACE_TYPE_SEED` or `BEGIN_AMENITY_SEED`.
- The partner `poi_id` formula (D6), and `AGENTS.md`.
- Dropping source tables or dictionaries. Environments other than DEV.
- Setting `gates.runtime`.

## 3. Inputs and resolved open points

Grain and keys come from `model-design.md` "Entities and grain" and "Keys". Columns and types come from "Columns". The design resolves the open questions in "Conflicts and questions" as follows:

| Item | Resolution | Basis |
|---|---|---|
| Conflicts 1 (partner estimate row) | Closed by ledger D9. Partner rows use the active partner `dp` row joined exactly on `primary_type`, which is the existing `_pc` struct. | D9 |
| Conflicts 2 (no match) | NULL for all five columns. No default. Google: neither `_p` nor `_m`. Partner: `primary_type` NULL or no `dp` row. | D9 says "from the row already matched; no second rule". With no row there is no value. Any default would be a new rule. Main records this as **D11**. |
| Conflicts 3 (positions) | `website_url` goes after `primary_type` (D8). The five estimates go after `category_group`, in `a1setupddl` order. `service_flags` goes after `amenity_vi`. | Layout only. `ensure_target`, MERGE and `row_hash` use column names. Main records this as **D12**. |
| Conflicts 4 (DDL sources) | Read. `TABLE_SPECS` (cell `init_tables`) repeats the op columns and has no new columns. `c1setupddl` has no `service_flags` on `slv_poi_amenity`. See §7.3 and §7.4. | Source read |
| D8 mechanism | Use a pure Python top-level lookup (`top_level_text`) as a UDF, not `get_json_object`. | `get_json_object(x, '$.website_url')` returns the raw JSON text for non-string values (`1` → `"1"`, `true` → `"true"`, `{...}` → `"{...}"`). `from_json` with a `string` field does the same. Either one would break D8's rule "giá trị không phải chuỗi JSON thì null". The semantics of D8 hold unchanged; only the mechanism differs. Main amends the D8 text (**D8 note**). |

Duplicate top-level keys in partner JSON follow `json.loads`: the last key wins. Main records this with the D8 note.

## 4. Invariants

1. **Entity grain.** `slv_poi_entity_non_enrich` has one row per `poi_id`. The contact join cannot multiply rows. A duplicate non-null `poi_id` in `slv_3p_poi_contact` raises `QualityGateError` inside `build()`, before any write. The `SPEC.pk` gate still applies.
2. **Op columns.** The entity build output and `TABLE_SPECS` contain none of `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`. `TABLE_CONFIGS_3P` and `SNAPSHOT_TECH_COLUMNS` do not change.
3. **Google `website_url`** equals `slv_3p_poi_contact.website_url` for the same `poi_id`. It is NULL when there is no contact row.
4. **Partner `website_url`** is the top-level `website_url` value only when that value is a JSON string. An empty string is kept. No trim. Every other case is NULL.
5. **Estimates.**
   - Google: each of the five values comes from the same struct (`_p`, else `_m`) as `business_category`.
   - Partner: the values come from `_pc`.
   - When there is no match the values are NULL.
   - The node adds no new join to `ref_dictionary_place_type`.
6. **`service_flags`** comes from the condition tuple of the matched google active row. The node adds no join to `ref_dictionary_amenities` after matching.
7. **Inputs match edges.** `SPEC.inputs` equals the active config edges: 6 for the entity (`poi`, `address`, `contact`, `dict`, `svc`, `i18n`) and 3 for the amenity. `_resolve_node` fails on any mismatch.
8. **Entity `TABLE_SPECS`** equals the entity build columns plus `TECH_COLUMNS`, in build order. Amenity `TABLE_SPECS` equals `c1setupddl`.
9. **DEV reset limits.**
   - It drops only `slv_poi_entity_non_enrich` and `slv_poi_amenity`.
   - It deletes only `wm_e__` rows whose `trg_tbl` is one of those two.
   - It never deletes `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`.
   - The dictionaries get zero inserted rows: the setup PLAN must show `missing_keys = 0` before apply.
10. **Idempotent rerun.** A second NB_00 run with no source change gives `NO_DATA` for both nodes. A `p_force` run gives `inserted = updated = deactivated = 0` and creates no target commit.

## 5. State ownership

| State | Writer | Change in this task |
|---|---|---|
| `slv_poi_entity_non_enrich` data | `NB_SLV_POI_ENTITY_NON_ENRICH` via `run_node` MERGE. `ensure_target` creates the table when it is missing. | New columns. The table is recreated on DEV. |
| `slv_poi_amenity` DDL | `NB_SETUP_POI_AMENITY` (`c1setupddl`) and `NB_SETUP_INITIAL_DDL` | Adds `service_flags` |
| `slv_poi_amenity` data | `NB_SLV_POI_AMENITY` | Adds `service_flags` |
| `ctrl_mng_pipeline_config` entity edges | `NB_SETUP_POI_ENTITY` (under the flow lock). Also `NB_SETUP_INITIAL_DDL` (empty environment) and the `NB_CREATE_DDL` patch (contact edge only, insert-if-absent). | +1 edge |
| `ctrl_mng_watermark` `wm_e__*` | NB_00 only (`advance_edges`). The DEV runbook DELETE is a one-off exception (D5). | Rows for the two targets are deleted. NB_00 recreates them as NEW_EDGE. |
| `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` | NB_00, manual node runs, setup notebooks, and the runbook during reset (same lock protocol) | Never deleted |
| `ref_dictionary_*` | Setup notebooks, insert-only | Read-only here. The setup apply must insert 0 rows. |

## 6. Grain and keys

See `model-design.md` "Entities and grain" and "Keys". No grain or key changes. `website_url`, the estimates and `service_flags` are non-key attributes, and all of them feed `row_hash`. The logical FK `poi_id → slv_3p_poi_contact.poi_id` applies to google rows only and uses a left join (D7).

## 7. Design

### 7.1 Entity node

**Cell `b1entityjson`.** Add the following inside the `BEGIN_PARTNER_JSON`/`END_PARTNER_JSON` markers, after `first_child_value`. The tests exec this block.

```python
JSON_NOT_STRING = "NOT_STRING"


def top_level_text(text, key):
    """Giá trị chuỗi của khoá `key` ở tầng gốc object JSON. Không tìm ở độ sâu khác, không trim.

    Input : text — chuỗi JSON hoặc None ; key — tên khoá
    Output: (chuỗi | None, OK | NO_VALUE | NULL_JSON | INVALID_JSON | NOT_STRING)
    Ví dụ : top_level_text('{"website_url": "https://a.example/"}', "website_url") -> ("https://a.example/", "OK")
            top_level_text('{"website_url": 1}', "website_url") -> (None, "NOT_STRING")
    """
    if text is None:
        return None, JSON_NULL
    try:
        doc = json.loads(text)
    except (TypeError, ValueError, RecursionError):
        return None, JSON_INVALID
    if doc is None:
        return None, JSON_NULL
    if not isinstance(doc, dict) or doc.get(key) is None:
        return None, JSON_NO_VALUE
    value = doc[key]
    return (value, JSON_OK) if isinstance(value, str) else (None, JSON_NOT_STRING)
```

**Cell `b1entitybuild`.** Full replacement of the constants, `_google`, `_partner` changes, `build` and `SPEC`. Unchanged lines are kept as they are now.

```python
GOOGLE = "google"
PARTNER = "partner"
OTHER = "other"
OTHER_GROUP = "Other"
POI_COLS = ("poi_id", "source_name", "source_id", "language_code", "poi_name", "poi_name_normalized", "types_json",
            "operating_status", "primary_type")
CONTACT_COLS = ("website_url",)
ADDRESS_COLS = ("house_number", "street", "ward", "city", "full_address", "lat", "lng")
CATEGORY_COLS = ("business_sector", "business_category", "business_category_vi", "category_group")
# D9: lấy từ đúng dòng ref_dictionary_place_type đã khớp; không có dòng khớp thì NULL (D11).
ESTIMATE_COLS = ("range_low_min", "range_high_min", "avg_range_min", "candidate_best_time_code", "canonical_candidate")
ESTIMATE_TYPES = ("int", "int", "int", "string", "string")
OUT_COLS = POI_COLS + CONTACT_COLS + ADDRESS_COLS + CATEGORY_COLS + ESTIMATE_COLS
PARTNER_ADDRESS = {...unchanged...}
main_category_of = ...unchanged...
website_url_of = F.udf(lambda text: top_level_text(text, "website_url"), "struct<value:string,status:string>")
```

Changes in `_google(ctx, poi, d)`:

```python
    g = (d.where(F.lower(F.trim("source_name")) == GOOGLE)
         .select(F.lower(F.trim("place_type")).alias("_k"), F.struct(*CATEGORY_COLS, *ESTIMATE_COLS).alias("_cat")))
    ...dup check, by_primary, by_types, addr unchanged...
    # D3, D7: website_url left join theo poi_id; poi_id trùng thì dừng, không chọn dòng, không ghi.
    contact = ctx.input("contact").where(F.col("poi_id").isNotNull()).select("poi_id", *CONTACT_COLS)
    dup_contact = contact.groupBy("poi_id").count().where("count > 1").count()
    if dup_contact:
        raise QualityGateError(f"slv_3p_poi_contact: {dup_contact} poi_id trùng, cần USER_DECISION; không ghi entity")
    out = (poi.join(by_primary, "poi_id", "left").join(by_types, "poi_id", "left").join(addr, "poi_id", "left")
           .join(contact, "poi_id", "left"))
    agg = out.agg(..., F.count("_a").alias("with_address"), F.count("website_url").alias("with_website")).first()
    ctx.metrics.update(..., google_with_address=agg["with_address"], google_with_website=agg["with_website"],
                       dict_google_rows=g.count())
    ...pick unchanged...
    return out.select(*POI_COLS, *CONTACT_COLS, *ADDRESS_COLS, pick("business_sector", F.lit(OTHER)),
                      pick("business_category", F.lit(OTHER)),
                      pick("business_category_vi", F.lit(None).cast("string")),
                      pick("category_group", F.lit(OTHER_GROUP)),
                      *[pick(c, F.lit(None)) for c in ESTIMATE_COLS])
```

`when(...).when(...).otherwise(lit(None))` takes its type from the struct field (int or string). Do not add a cast that could hide a type drift. `build` checks the types first.

Changes in `_partner(ctx, d, schema)`:

```python
    base = (svc.join(vi, "id").withColumn("_mc", main_category_of(F.col("amentities")))
            .withColumn("_web", website_url_of(F.col("website_urls")))
            .withColumn("primary_type", F.col("_mc.value")))
    dp = (d.where(F.lower(F.trim("source_name")) == PARTNER)
          .select(F.col("place_type").alias("primary_type"),
                  F.struct("business_category", "business_category_vi", *ESTIMATE_COLS).alias("_pc")))
    ...joins, persist, agg unchanged...
    web = {r["s"]: r["n"] for r in out.groupBy(F.col("_web.status").alias("s")).count()
           .withColumnRenamed("count", "n").collect()}
    ctx.metrics.update(..., partner_website=web)
    cols = {
        ...existing entries...,
        "website_url": F.col("_web.value"),  # D8: key gốc, chỉ chuỗi JSON
        **{c: F.col(f"_pc.{c}") for c in ESTIMATE_COLS},  # D9: dòng partner đã khớp qua primary_type
        **{c: F.get_json_object("address", f"$.{k}") for c, k in PARTNER_ADDRESS.items()},
    }
```

`out` is persisted, so each UDF runs once per row. The final `select` over `OUT_COLS` with `.cast(schema[c].dataType)` is unchanged.

Changes in `build(ctx)` and `SPEC`:

```python
    if "website_url" not in ctx.input("contact").columns:
        raise ConfigError("slv_poi_entity_non_enrich: slv_3p_poi_contact thiếu cột website_url")
    if "website_urls" not in ctx.input("svc").columns:
        raise ConfigError("slv_poi_entity_non_enrich: slv_pn_business_services thiếu cột website_urls")
    d = ctx.input("dict")
    ...category_group check unchanged...
    types = dict(d.dtypes)
    bad = [(c, types.get(c)) for c, t in zip(ESTIMATE_COLS, ESTIMATE_TYPES) if types.get(c) != t]
    if bad:
        raise ConfigError(f"ref_dictionary_place_type thiếu hoặc sai kiểu cột ước tính {bad}: chạy cell dictseedpy của NB_CREATE_DDL")
    d = d.where(F.col("is_active") == F.lit(True))
    ...no_group check unchanged...
    ctx.metrics.update(dict_estimate_null=d.where(" OR ".join(f"{c} IS NULL" for c in ESTIMATE_COLS)).count())

SPEC = NodeSpec(
    trg_tbl="slv_poi_entity_non_enrich",
    inputs={"poi": "slv_3p_poi", "address": "slv_3p_poi_address", "contact": "slv_3p_poi_contact",
            "dict": "ref_dictionary_place_type", "svc": "slv_pn_business_services", "i18n": "slv_pn_business_service_i18ns"},
    pk=("poi_id",),
    build=build,
    required_inputs=("poi", "address", "contact", "dict", "svc", "i18n"),
    ...unique_checks, warn_checks, write_mode unchanged...
)
```

Also update the markdown cell `b1entitymd` with one line: it now reads contact, and partner `website_urls`.

### 7.2 Amenity node

Cell `d1amenmatch`: only the `match_conditions` docstring changes. Rows are the dictionary columns, now ending with `service_flags`. A condition is those columns plus `(kind, path, value)` at the tail. The function body is width-agnostic and stays unchanged; it keys on `c[:3]`.

Cell `d1amenbuild`:

```python
COND_SCHEMA = ("business_sector string, amenity_group string, amenity_raw string, amenity string, "
               "amenity_vi string, service_flags string, _kind string, _path string, _v string")
OUT_COLS = ("poi_id", "business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_vi", "service_flags")


def build(ctx: NodeContext) -> DataFrame:
    d = ctx.input("dict")
    if dict(d.dtypes).get("service_flags") != "string":
        raise ConfigError("ref_dictionary_amenities thiếu cột service_flags STRING: chạy cell dictseedpy của NB_CREATE_DDL")
    # D10: service_flags đi cùng dòng điều kiện đã khớp; không join từ điển lần hai.
    rows = [tuple(r) for r in (d
            .where((F.lower(F.trim("source_name")) == GOOGLE) & (F.col("is_active") == F.lit(True)))
            .select("business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_vi", "service_flags").collect())]
    ...unchanged through out...
    n_flag = sum(c[-3] == "flag" for c in conds)
    ctx.metrics.update(..., conditions_service_flags=sum(c[5] is not None for c in conds), ...)
```

`out_one` and `out_in` carry `service_flags` from `cond`. `dropDuplicates(list(OUT_COLS) + ["_kind"])` stays. `service_flags` is a function of the 3-column key, because the `dup` check fails on a duplicate key.

### 7.3 Setup notebooks and edges

`NB_SETUP_POI_ENTITY`:
- Cell `a1setupplan`: `planned_edges` gains `"slv_3p_poi_contact"` after `"slv_3p_poi_address"`.
- Cell `a1setupedges`, `edge_rows`: renumber so the entity edges stay contiguous. Add `(6, 'lh_vv_silver.dbo', 'slv_3p_poi_contact', 'lh_vv_silver.dbo', 'slv_poi_entity_non_enrich', 'UPSERT')`. The amenity UPSERTs move to seq 7, 8, 9. The `seq` value only offsets `MAX(id)` inside one MERGE.
- Cell `a1setupedges`, `dup` query: the `slv_poi_entity_non_enrich` `IN` list gains `'slv_3p_poi_contact'`.
- Cell `a1setupedges`, `entity_upserts`: gains `("slv_3p_poi_contact", "slv_poi_entity_non_enrich")`.
- The `BEGIN_EDGE_PRECHECK` block does not change. It must stay byte-identical to the amenity setup.

`NB_SETUP_POI_AMENITY`:
- Cell `c1setupedges`: the `entity_edges_ok` `IN` list gains `'slv_3p_poi_contact'`, and `!= 5` becomes `!= 6`. The error text does not change.
- Cell `c1setupddl`, `CREATE TABLE IF NOT EXISTS lh_vv_silver.dbo.slv_poi_amenity`: add `service_flags   STRING,` after `amenity_vi`.
- Cell `c1setupddl`, `EXPECTED[AMENITY_FQ]`: add `("service_flags", "string", True)` after `amenity_vi`.
- Consequence: on any environment where `slv_poi_amenity` exists without `service_flags`, the `EXPECTED` check fails. An in-place `ensure_target` ADD COLUMNS would also put the column after `deleted_at`. The only supported path for an existing table is drop and reinit (§17).

### 7.4 NB_SETUP_INITIAL_DDL

In cell `init_tables` (`TABLE_SPECS`), change the comment to `# [SỬA 20/10] ...`.

The entity `cols` become:
- `poi_id`, `source_name`, `source_id`, `language_code`, `poi_name`, `poi_name_normalized`, `types_json`, `operating_status`, `primary_type`, all `STRING`;
- `website_url` `STRING`;
- `house_number`, `street`, `ward`, `city`, `full_address`, all `STRING`;
- `lat`, `lng`, both `DOUBLE`;
- `business_sector`, `business_category`, `business_category_vi`, `category_group`, all `STRING`;
- `range_low_min`, `range_high_min`, `avg_range_min`, all `INT`;
- `candidate_best_time_code`, `canonical_candidate`, both `STRING`;
- `row_hash` `STRING`;
- `created_at`, `updated_at`, `deleted_at`, all `TIMESTAMP`.

The four op columns are removed.

In the amenity spec, add `('service_flags', 'STRING', None)` after `amenity_vi`.

In cell `init_seed_ctrl` (`PIPELINE_CONFIG_ROWS`), add the following right after the `slv_pn_business_service_i18ns → slv_poi_entity_non_enrich` row:

`(_SLV1H, _S, 'slv_3p_poi_contact', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),`

No ALTER, UPDATE or DELETE is added (§2.1 rule 2).

### 7.5 NB_CREATE_DDL patch cell

Append a markdown cell `entwebmd` (`# [THÊM 20/10] 20261020-entity-drop-op-cols-add-website`) and a code cell `entwebpy` at the end of the notebook. Earlier cells do not change.

```python
CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_SLV_1H"
ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich"
AMENITY_FQ = "lh_vv_silver.dbo.slv_poi_amenity"
OP_COLS = ("_crawled_at", "_event_id", "_first_seen_at", "_last_seen_at")
EDGE = ("lh_vv_silver.dbo", "slv_3p_poi_contact", "lh_vv_silver.dbo", "slv_poi_entity_non_enrich")

# Không chèn cạnh khi luồng đang giữ khoá: node đang chạy sẽ thấy cạnh lạ và fail.
lock = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = 'wm_flow__{PL}'").collect()
if lock and lock[0]["lock_exec_id"]:
    raise RuntimeError(f"Luồng {PL} đang giữ khoá ({lock[0]['lock_exec_id']}): chạy lại sau hoặc dùng NB_SETUP_POI_ENTITY")
has_nb = "nb_name" in {f.name.lower() for f in spark.table(CFG).schema.fields}
nb_col, nb_val = (", nb_name", ", CAST(NULL AS STRING)") if has_nb else ("", "")
spark.sql(f"""
INSERT INTO {CFG}
    (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order{nb_col})
SELECT COALESCE((SELECT MAX(id) FROM {CFG}), 0) + 1, '{PL}', '{EDGE[0]}', '{EDGE[1]}', '{EDGE[2]}', '{EDGE[3]}',
       1, 1, 'RECOMPUTE', CAST(NULL AS STRING), CAST(NULL AS STRING){nb_val}
WHERE NOT EXISTS (
    SELECT 1 FROM {CFG} c
    WHERE c.pl_name = '{PL}' AND c.src_schema = '{EDGE[0]}' AND c.src_tbl = '{EDGE[1]}'
      AND c.trg_schema = '{EDGE[2]}' AND c.trg_tbl = '{EDGE[3]}')
""")
n = spark.sql(f"""
SELECT count(*) AS n FROM {CFG}
WHERE pl_name = '{PL}' AND src_schema = '{EDGE[0]}' AND src_tbl = '{EDGE[1]}'
  AND trg_schema = '{EDGE[2]}' AND trg_tbl = '{EDGE[3]}' AND is_active = 1
""").first()["n"]
if n != 1:
    raise RuntimeError(f"{CFG}: cần đúng 1 cạnh active {EDGE[1]} -> {EDGE[3]}, có {n}; cạnh tắt thì chạy NB_SETUP_POI_ENTITY")

# Bỏ cột op và thêm cột đúng vị trí cần xoá bảng và init lại (runbook task); cell này không DROP / ALTER.
reset = []
if spark.catalog.tableExists(ENTITY_FQ):
    left = [c for c in OP_COLS if c in {f.name.lower() for f in spark.table(ENTITY_FQ).schema.fields}]
    if left:
        reset.append(f"{ENTITY_FQ} còn {left}")
if spark.catalog.tableExists(AMENITY_FQ):
    if "service_flags" not in {f.name.lower() for f in spark.table(AMENITY_FQ).schema.fields}:
        reset.append(f"{AMENITY_FQ} chưa có service_flags")
print("Cần chạy runbook 20261020-entity-drop-op-cols-add-website: " + "; ".join(reset) if reset
      else "Cạnh contact có; bảng node không cần reset")
```

The cell uses the same column values as the setup MERGE UPSERT branch, so a later `NB_SETUP_POI_ENTITY` run matches the row and does not change it. If an inactive row exists, the cell inserts nothing and raises. Reactivation belongs to the lock-holding setup.

### 7.6 Docs

`01_DATA_MODEL.md` §6:
- N6 inputs gain `slv_3p_poi_contact`.
- N6 decision text adds:
  - no op columns;
  - `website_url` (google: contact left join, a duplicate `poi_id` fails; partner: top-level string key in `website_urls`);
  - the five estimates from the matched dictionary row, NULL when there is no match.
- N7 adds `service_flags` from the matched dictionary row.

`CTRL_TABLES_CONTEXT.md`:
- §3: the entity edge table gains the `slv_3p_poi_contact` row. "5 cạnh" becomes "6 cạnh" at L124 and L126.
- §4 "Thao tác thường gặp": add a note on DEV node reset. Drop the table, then delete its `wm_e__` rows, using the task runbook. Never delete `wm_flow__`.
- §10: add a 20/10 row.

## 8. Alternatives and trade-offs

| Decision | Options | Selected | Why |
|---|---|---|---|
| Partner JSON extraction | (a) `get_json_object`; (b) `from_json` struct<string>; (c) pure Python top-level lookup as a UDF | (c) | (a) and (b) turn non-string tokens into text, which breaks D8. (c) is unit-testable without Spark. It follows the existing `main_category_of` pattern on the same rows. Partner volume is small and `out` is persisted, so the cost is one Python pass. |
| Contact cardinality | (a) left join after a duplicate guard; (b) `row_number` pick; (c) inner join | (a) | (b) is forbidden by D3 and D7. (c) drops google rows that have no contact row, which breaks grain (D7). |
| Estimates | (a) widen the struct that is already matched (`_cat`, `_pc`); (b) re-join the dictionary on (`source_name`, `place_type`) after `pick` | (a) | (b) is a second match rule (forbidden by D9). It would also diverge for `_m` rows, whose match key is a `types_json` element, not `primary_type`. |
| `service_flags` | (a) carry it in the condition tuple; (b) join the dictionary after `out` | (a) | Same reason as above. (a) needs no extra Spark job. |
| Op-column removal on an existing table | (a) drop and reinit (DEV); (b) `ALTER TABLE DROP COLUMNS`; (c) leave the columns | (a) | (b) needs `delta.columnMapping.mode = name`, which is an irreversible protocol upgrade. The `NB_CREATE_DDL` rules also forbid DROP COLUMN. (c) fails D1 because `ensure_target` only warns. Both tables are pure RECOMPUTE outputs, so they can be regenerated from inputs. |
| Recreating `slv_poi_amenity` | (a) `NB_SETUP_POI_AMENITY` CREATE; (b) `ensure_target` | (a) | (b) creates nullable PK columns. The later `c1setupddl` `EXPECTED` check would then fail. |
| Contact edge on DEV | (a) `NB_SETUP_POI_ENTITY` apply, under the lock with full edge validation; (b) the `NB_CREATE_DDL` cell; (c) `NB_SETUP_INITIAL_DDL` apply | (a) | (a) is lock-protected and validates the whole canonical set. (b) exists for §2.1 parity and does the same thing idempotently. (c) touches every table, which is a wider blast radius. |
| Contact duplicate scope | (a) the whole contact table, non-null `poi_id`; (b) only `poi_id`s present in google `slv_3p_poi` | (a) | It is stricter and simpler, and it matches D7 "Trùng `poi_id`: fail run". |

## 9. Ordering

- **Build order.** Deploy all six notebooks to Fabric DEV before any config or runtime step. Run the old node against the new edge, or the new node without the edge, and `_resolve_node` raises `ConfigError`. The run fails cleanly with no write.
- **Inside the entity node.**
  1. Column and type checks.
  2. The contact duplicate guard.
  3. The joins.
  4. The quality gate.
  5. MERGE.

  Every failure before step 5 leaves the target untouched.
- **Runbook order** (§17):
  1. Read-only pre-checks.
  2. Setup PLAN, for both notebooks.
  3. Take the lock.
  4. DROP both tables.
  5. DELETE the `wm_e__` rows.
  6. Release the lock.
  7. Apply `NB_SETUP_POI_ENTITY`.
  8. Apply `NB_SETUP_POI_AMENITY`.
  9. Run NB_00 for `PL_VV_TRANS_SLV_TO_SLV_1H`.

  DROP comes before DELETE. In the reverse order, a run in the gap would recompute into the old table and keep the op columns.
- **DAG order.** NB_00 runs the entity node before the amenity node (edge `slv_poi_entity_non_enrich → slv_poi_amenity`). The amenity setup needs 6 entity edges, so the entity setup apply must run first.

## 10. Transaction and commit boundaries

- Each node run makes at most one Delta commit on its target (the MERGE), plus one append to `ctrl_log_table_run`. A schema change on a missing table is a separate CREATE commit by `ensure_target`.
- NB_00 advances the edges after `runMultiple`, in one MERGE on `ctrl_mng_watermark`. A FAILED node advances nothing.
- In the runbook, DROP of each table and the DELETE on `ctrl_mng_watermark` are three independent commits; nothing makes them atomic. The flow lock gives isolation, and §14 shows that every intermediate state converges on rerun.
- Each setup notebook's edge MERGE is one commit under the flow lock. The `NB_CREATE_DDL` INSERT is one commit.

## 11. Idempotency

- The nodes run RECOMPUTE plus a `row_hash` MERGE. A rerun on the same input versions gives an empty diff and skips the MERGE. The UDF and `min_by` are deterministic: positions are unique and `dp` is unique by the duplicate guard.
- Setup edge MERGE: the second run matches every row and updates nothing. The `NB_CREATE_DDL` INSERT runs only when the row is absent (`WHERE NOT EXISTS`).
- Runbook: `DROP TABLE IF EXISTS` and the keyed DELETE are re-runnable. The lock UPDATE is conditional on `lock_exec_id IS NULL` or on the runbook's own id.

## 12. Concurrency

- Every input is read `VERSION AS OF` the pinned version. A concurrent FL_00 extract write to `slv_3p_poi_contact` cannot tear the contact snapshot. The duplicate guard and the join see the same version.
- The setup notebooks and the runbook reset take `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`. NB_00 and manual node runs cannot overlap them.
- The `NB_CREATE_DDL` cell checks the lock but does not take it. A race window is still possible. Its worst case is one node run that fails on a `ConfigError` with no write. Accepted: the pipeline is manual and unscheduled (CTRL §3).
- The runbook must not run while the SQL analytics endpoint or a user query holds the tables (DEV only). DROP may also fail on Fabric metadata sync. Retry once, then stop.

## 13. Retry and recovery

- MERGE uses the existing `with_retry`. A failed node leaves the edges unadvanced, and the next NB_00 run recomputes everything. No manual watermark repair is needed.
- `QualityGateError` (contact duplicate, dictionary duplicate) is not transient. Do not retry; stop and raise a `USER_DECISION` (D3).
- `ConfigError` (missing column, type drift, edge mismatch) means deployment or config order was wrong. Fix the order, then rerun.

## 14. Partial failure

| Failure point | State | Recovery |
|---|---|---|
| After DROP of amenity only | Entity has old schema, amenity missing | Rerun the reset from the start. It is idempotent. |
| After both DROPs, before DELETE | Tables missing, old `wm_e__` rows present | Rerun DELETE, or skip it: a missing target forces the run, and the entity edge to amenity reports `TABLE_RECREATED`. Converges. |
| Lock not released (runbook aborted) | Flow blocked | Run the release UPDATE keyed on the runbook `lock_exec_id`. The lock also expires after the manual timeout. |
| Entity setup apply fails | Edges unchanged | The cell raises before or within one MERGE. Rerun after fixing. |
| Amenity setup fails at `EXPECTED` | `slv_poi_amenity` exists with the wrong shape | It means the table was created by `ensure_target` or by an old DDL. Drop `slv_poi_amenity` again and rerun the amenity setup. |
| Entity node fails (contact duplicate) | Entity table missing or empty, amenity skipped (parent failed) | Stop. `USER_DECISION` under D3. No row is picked. |
| Amenity node fails | Entity written, entity edges advanced, amenity edges not | Fix, then rerun NB_00. Only amenity is dirty. |

## 15. Observability

The values below go into `ctrl_log_table_run.qg_json` through `ctx.metrics`:
- Entity:
  - `google_with_website`;
  - `partner_website` (status counts for `OK`, `NO_VALUE`, `NULL_JSON`, `INVALID_JSON`, `NOT_STRING`);
  - `dict_estimate_null` (active dictionary rows with any NULL estimate);
  - the existing `by_primary`, `by_types`, `unmatched` and `partner_primary_matched`. Their sum bounds the number of rows that can have estimates.
- Amenity: `conditions_service_flags`.
- Errors name the table and the count. They never include URL values.
- The runbook saves only counts and `DESCRIBE` output in `evidence/results/`.

## 16. Security

- No secrets.
- `website_url` holds business URLs, not personal data. Partner URLs may point to internal staging hosts, so do not copy URL values into evidence, tests or seeds. The sample URL is not used anywhere. Tests use `https://a.example/`.
- The `NB_CREATE_DDL` cell builds its SQL only from constants.

## 17. Rollout — required DEV runbook content

Main writes `runtime-runbook.md` (Vietnamese prose) with these steps. Every step names environment **DEV** (`lh_vv_silver`, `lh_vv_ctrl` in the DEV workspace). The user runs each step. The agent does not set `gates.runtime`.

**R0. Deploy.** Sync the six notebooks to the Fabric DEV workspace. Confirm that `b1entitybuild` in Fabric contains `"contact": "slv_3p_poi_contact"`.

**R1. Read-only pre-checks.** Save the output. Each line gives the expected result; on any other result, stop.
- `SELECT watermark_id, lock_exec_id, lock_at, status FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H'` → `lock_exec_id IS NULL`.
- Counts before the delete:
  - `SELECT count(*), count_if(deleted_at IS NULL) FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich`;
  - the same query for `lh_vv_silver.dbo.slv_poi_amenity`.
- Watermark rows that the delete will remove (the rollback reference):
  - `SELECT watermark_id, src_tbl, trg_tbl, last_src_version, last_src_table_id, status FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE substr(watermark_id, 1, 6) = 'wm_e__' AND trg_schema = 'lh_vv_silver.dbo' AND trg_tbl IN ('slv_poi_entity_non_enrich', 'slv_poi_amenity') ORDER BY watermark_id`.
- Contact duplicates:
  - `SELECT count(*) FROM (SELECT poi_id FROM lh_vv_silver.dbo.slv_3p_poi_contact WHERE poi_id IS NOT NULL GROUP BY poi_id HAVING count(*) > 1)` → 0. If not 0, stop: `USER_DECISION` under D3.
  - `SELECT count(*) FROM lh_vv_silver.dbo.slv_3p_poi_contact` → greater than 0.
- Dictionary types:
  - `DESCRIBE lh_vv_silver.dbo.ref_dictionary_place_type` → the three range columns are `int`, the other two estimate columns are `string`.
  - `DESCRIBE lh_vv_silver.dbo.ref_dictionary_amenities` → `service_flags string`.
- `DESCRIBE lh_vv_silver.dbo.slv_3p_poi` → it has the four op columns (baseline for D1).

**R2. Setup PLAN.** Run `NB_SETUP_POI_ENTITY` and `NB_SETUP_POI_AMENITY`, both with `p_apply = "false"` (the default).
- Entity: `missing_keys = 0`, `unseeded_rows = 0`, and `planned_edges` lists 6 entries including `slv_3p_poi_contact`.
- Amenity: `missing_keys = 0`.
- If any `missing_keys` is above 0, applying would insert dictionary rows, which is a reseed. Stop.

**R3. Reset.** This is the separate apply step. Do it only after R1 and R2 pass.

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
SET lock_exec_id = 'runbook-20261020-entity-reset', lock_at = current_timestamp(), status = 'RUNNING', updated_at = current_timestamp()
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H' AND lock_exec_id IS NULL;
-- Kiểm tra lock_exec_id = 'runbook-20261020-entity-reset'; khác thì DỪNG, không DROP.
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_amenity;
DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_entity_non_enrich;
DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE substr(watermark_id, 1, 6) = 'wm_e__'
  AND trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_poi_entity_non_enrich', 'slv_poi_amenity');
-- Kiểm tra: 0 dòng còn lại theo cùng WHERE; SHOW TABLES IN lh_vv_silver.dbo không còn hai bảng.
UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark
SET lock_exec_id = NULL, lock_at = NULL, status = 'SUCCESS', updated_at = current_timestamp()
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H' AND lock_exec_id = 'runbook-20261020-entity-reset';
```

If the `wm_flow__` row does not exist at all, the flow has never run. Skip both lock UPDATEs and record that. The lock UPDATEs follow the manual-run lock protocol in CTRL §4. The row is never deleted (D5).

**R4. Rebuild.**
1. Run `NB_SETUP_POI_ENTITY` with `p_apply = "true"`. Expect `inserted = 0`, `edges_inserted = 1`, `edges_retired = 0`.
2. Run `NB_SETUP_POI_AMENITY` with `p_apply = "true"`. Expect `inserted = 0`. It creates `slv_poi_amenity` with `service_flags`, and the `EXPECTED` check passes.
3. Run NB_00 with `p_pl_name = PL_VV_TRANS_SLV_TO_SLV_1H`. Use NB_00, not manual node runs, because only NB_00 rewrites the edge watermarks. The entity table is created by `ensure_target`.

**R5. Verify.** See §20.2.

## 18. Rollback and forward recovery

- **Data loss on DROP.** The tables are fully derived (RECOMPUTE). What is lost: the original `created_at` values, soft-deleted rows, and Delta history. The DEV request accepts this. The R1 counts and the saved watermark rows are the comparison baseline.
- **Rollback to the previous schema.**
  1. The user reverts the task commit in Git and syncs the notebooks to DEV.
  2. Deactivate the contact edge: `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0 WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND src_schema = 'lh_vv_silver.dbo' AND src_tbl = 'slv_3p_poi_contact' AND trg_schema = 'lh_vv_silver.dbo' AND trg_tbl = 'slv_poi_entity_non_enrich' AND is_active = 1`. The old setup's precheck rejects an active extra edge, and the old node rejects an unknown edge.
  3. Repeat R3 (drop and delete).
  4. Run the old `NB_SETUP_POI_AMENITY` apply.
  5. Run NB_00.

  The old schema, with the op columns, is rebuilt from sources. The watermark rows do not need to be restored, because missing rows mean NEW_EDGE.
- **Forward recovery.**
  - Code defect: fix it and rerun NB_00. RECOMPUTE converges.
  - Schema or type defect (`ensure_target` `ConfigError`): repeat R3 and R4.
  - Contact duplicate: stop for a `USER_DECISION`. Nothing was written.

## 19. Implementation plan

1. **Record in the ledger.** Main adds D11 (NULL estimates when there is no match) and D12 (column positions). Main amends D8 with the mechanism note, `top_level_text` replacing `get_json_object`, and the last-key-wins rule (§3).
2. **Entity node.** Edit `b1entityjson`, `b1entitybuild` and `b1entitymd` (§7.1).
3. **Amenity node.** Edit `d1amenmatch` (docstring) and `d1amenbuild` (§7.2).
4. **Setup notebooks.** Edit `NB_SETUP_POI_ENTITY` (`a1setupplan`, `a1setupedges`) and `NB_SETUP_POI_AMENITY` (`c1setupddl`, `c1setupedges`) (§7.3).
5. **Initial DDL.** Edit `NB_SETUP_INITIAL_DDL` `init_tables` and `init_seed_ctrl` (§7.4).
6. **Patch cells.** Append `entwebmd` and `entwebpy` to `NB_CREATE_DDL` (§7.5).
7. **Tests** (§20.1).
8. **Docs** (§7.6).
9. **Runbook.** Main writes `runtime-runbook.md` from §17.

## 20. Verification

### 20.1 Local tests (no Spark)

`tests/test_poi_entity_contract.py`:
- `test_entity_node_contract`:
  - add the role `'"contact": "slv_3p_poi_contact"'`;
  - `required_inputs=("poi", "address", "contact", "dict", "svc", "i18n")`;
  - assert that `website_url_of`, `top_level_text`, `"_web.value"`, `*ESTIMATE_COLS` and `"slv_3p_poi_contact: "` are present;
  - assert that none of the four op names occurs in cell `b1entitybuild`;
  - assert that `get_json_object("website_urls"` is absent.
- `_ENTITY_UPSERTS`: add `("slv_3p_poi_contact", "slv_poi_entity_non_enrich")`.
- `test_setup_contract`: add `slv_3p_poi_contact` to the edge-name loop.
- `test_create_ddl_patch`:
  - locate `dictseedpy` by id, not by position;
  - assert that the last two cell ids are `["entwebmd", "entwebpy"]`.
- New `test_partner_website_top_level`. Exec the `BEGIN_PARTNER_JSON` block and check `top_level_text`:

  | Input | Expected |
  |---|---|
  | `'{"website_url": "https://a.example/"}'` | `OK` with that value |
  | `'{"website_url": ""}'` | `("", "OK")` |
  | `'{"website_url": " x "}'` | `(" x ", "OK")` |
  | `1`, `true`, `{"a": 1}` or `["u"]` as the value | `NOT_STRING` |
  | `'{"website_url": null}'` | `NO_VALUE` |
  | `'{"x": {"website_url": "u"}}'` | `NO_VALUE` |
  | `'["u"]'` | `NO_VALUE` |
  | `None` and `"null"` | `NULL_JSON` |
  | `"{"` and `"[" * 3000 + "]" * 3000` | `INVALID_JSON` |

- New `test_create_ddl_contact_edge_patch` on cell `entwebpy`:
  - it contains `INSERT INTO`, `WHERE NOT EXISTS`, `'slv_3p_poi_contact'`, `wm_flow__` and `RECOMPUTE`;
  - it contains none of `DROP `, `DELETE FROM`, `ALTER TABLE`, `UPDATE `.

`tests/test_poi_amenity_contract.py`:
- `test_amenity_node_contract`:
  - assert `"service_flags"` is in the parsed `OUT_COLS`, and that it is the last element;
  - assert that `COND_SCHEMA` contains `service_flags string, _kind`;
  - assert that `c[-3] == "flag"` is present and `c[5] == "flag"` is absent in `d1amenbuild`.
- `test_setup_contract`: both `"entity_edges_ok != 5"` assertions become `!= 6`; add an assertion that `'slv_3p_poi_contact'` is in the `c1setupedges` source.
- New `test_match_conditions_carries_service_flags`:
  - build 6-tuples by appending `row[6]` to each `_google` seed row;
  - assert that every condition has `c[5]` equal to the input `service_flags`, and that `c[-3]` is in `{"flag", "type", "json_in"}`;
  - assert that the counts match the 5-tuple run (53 conditions, 27 flag).
- New `test_amenity_ddl_matches_node`: the names in the `c1setupddl` `slv_poi_amenity` CREATE equal `OUT_COLS` plus `row_hash`, `created_at`, `updated_at`, `deleted_at`.

`tests/test_initial_ddl_contract.py`:
- `test_poi_entity_columns_derived`:
  - `expected` = the active `slv_3p_poi` registry columns minus `TECH_NAMES`;
  - then `CONTACT_COLS` with types from the active `slv_3p_poi_contact` registry rows;
  - then the address columns, the category columns, `ESTIMATE_COLS` with types from `a1setupddl` `EXPECTED`, and `TECH_COLUMNS`;
  - remove `SNAPSHOT_TECH_COLUMNS` from the expectation;
  - add an assertion that no `SNAPSHOT_TECH_COLUMNS` name appears in the entity spec.
- `test_pipeline_config_rows_match_sources`:
  - the entity `src` tuple gains `"slv_3p_poi_contact"` after `"slv_pn_business_service_i18ns"`;
  - `len(expected) == 54`.

Commands:
- `python -m pytest tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest -q`

### 20.2 DEV runtime checks (R5, user-run)

1. **Entity schema.** `DESCRIBE lh_vv_silver.dbo.slv_poi_entity_non_enrich`:
   - none of the four op columns;
   - `website_url string` immediately after `primary_type`;
   - the five estimate columns after `category_group`.
2. **Source schema unchanged.** `DESCRIBE lh_vv_silver.dbo.slv_3p_poi` still has the four op columns.
3. **Grain.** On rows with `deleted_at IS NULL`, `count(*) = count(DISTINCT poi_id)`.
4. **Google `website_url` parity** → 0: `SELECT count(*) FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich e LEFT JOIN lh_vv_silver.dbo.slv_3p_poi_contact c ON c.poi_id = e.poi_id WHERE e.source_name = 'google' AND NOT (e.website_url <=> c.website_url)`.
5. **Partner `website_url`.**
   - `qg_json.metrics.partner_website` counts sum to `partner_rows`.
   - Parity against `get_json_object(s.website_urls, '$.website_url')` (join on `s.id = e.source_id`, partner rows): the number of mismatches equals the `NOT_STRING` count.
   - If `NO_VALUE` equals `partner_rows` while the raw JSON visibly has the key, stop (possible double encoding).
6. **Google estimate parity** → 0. Run it for `range_low_min`, using a `primary_type` match on the active google dictionary row, for rows where `business_category` is not `other`. Rows matched by `types_json` (`by_types`) are checked through the qg metrics.
7. **Partner estimate parity** → 0: `e.range_low_min <=> d.range_low_min` against active partner `d` with `d.place_type = e.primary_type`.
8. **Amenity.**
   - `DESCRIBE` shows `service_flags string` after `amenity_vi`.
   - Parity against the active google dictionary on (`business_sector`, `amenity_group`, `amenity_raw`) → 0 mismatches.
9. **Watermarks.** The `wm_e__` rows for the two targets were recreated: 6 for the entity and 3 for the amenity, all `status = SUCCESS`.
10. **Idempotency.** A second NB_00 run gives `NO_DATA` for both nodes, and no new target version.
11. **Dictionaries.** The version and row count of both dictionaries match R1 (0 inserted).
