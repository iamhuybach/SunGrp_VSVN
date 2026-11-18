RESULT: PASS

## Main brief

### Decision
Add a partner branch to `NB_SLV_POI_AMENITY` `d1amenbuild` and union it with the unchanged google branch:
- `poi_id = uuid_md5(id, 'partner')`. Labels from `$.facilities.specialty_tags`: the `vi` value, then the svc value when the `vi` value is NULL.
- `business_sector` from svc. Left join to active partner dictionary rows. On no match, `amenity_group = 'specialty_tags'`.
- Stop the node on a multi-match label or a NULL sector. Two new RECOMPUTE edges (svc and i18n into `slv_poi_amenity`, ENR_15M) through a new `NB_CREATE_DDL` cell and the `NB_SETUP_INITIAL_DDL` seed.
- Grain, key, `OUT_COLS`, gold, info, and entity are unchanged. Record A-1 to A-8 and R-1 in `decision.md` first.

### Invariants Main must preserve
- Google output rows and their `row_hash` are unchanged. Only the final `return` becomes `out.select(*OUT_COLS).unionByName(partner)`.
- Partner `poi_id` is the literal `uuid_md5(F.col("id"), F.lit(PARTNER))`, the same as `b1entitybuild` `_partner`, and is inner joined to live entity rows with `source_name = partner`.
- `pk`, `OUT_COLS`, and `write_mode="MERGE"` stay byte-identical. `srvamenitybuild`, `srvinfobuild`, and `b1entitybuild` are not edited.
- The partner dictionary filter is `lower(trim(source_name)) == 'partner'` and `is_active == True`. `business_sector` never comes from the dictionary.
- A label present in the data that matches more than one partner dictionary row (after `trim`) raises `QualityGateError` before return. A NULL partner `business_sector` raises `QualityGateError`. `''` is passed through and warned.
- Only `$.facilities.specialty_tags`, through `from_json(…, PARTNER_TAGS)`. No `get_json_object`, no `explode_outer`.
- `required_inputs` includes `svc` and `i18n`. `spec.inputs` equals the active edges exactly.
- After the patch: exactly five active RECOMPUTE edges into `slv_poi_amenity` on `PL_VV_TRANS_SLV_TO_ENR_15M`, the same in `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL`.
- Every partner seed row has `service_flags` None, so `gld_enr_poi_info.service_flag` for partners stays `"[]"`.
- An empty partner branch does not raise.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenmatch` before `# END_AMENITY_MATCH` | Add `PARTNER`, `PARTNER_GROUP`, `PARTNER_TAGS`, `partner_multi_match` (doc: "Partner helpers") | `test_partner_helpers` passes |
| 2 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenbuild` new `PN_*`, `_live`, `_partner_rows` | Copy from doc "Partner branch" | `test_partner_branch_contract`, `test_partner_live_filter_matches_entity`, `test_partner_poi_id_matches_entity` pass |
| 3 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenbuild` `build` tail and `SPEC` | `n_google`, `_partner_rows`, `rows_google`, `rows=n`, `metrics.update(**pm)`, union return. Add `svc` and `i18n` to inputs and `required_inputs` (doc: "`build` and `SPEC` changes") | `test_amenity_node_contract` (updated) and `test_google_branch_unchanged` pass |
| 4 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenmd` | Describe the partner source, the rule, and D-2/D-11/D-12 | Text matches mapping §0 |
| 5 | notebooks/NB_CREATE_DDL.ipynb | new `amenpnmd` and `amenpnpy` at the end | Lock-guarded edge patch, `MODE` ON/OFF, `EDGES_ON` literal (doc: "`NB_CREATE_DDL` `amenpnmd` / `amenpnpy`") | `test_amenity_partner_edges_patch` passes. No old cell edited |
| 6 | notebooks/NB_SETUP_INITIAL_DDL.ipynb (S0) | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` | Two tuples right after the three `slv_poi_amenity` rows | `test_initial_seed_has_partner_amenity_edges` passes |
| 7 | docs/context/mapping_gld_srv_poi_amenity.md | §0 and §1 | `poi_id` and sector origin per source, partner rule, five edges, inputs, `amenpnpy`, API note | No `MISSING` left for `poi_id`. Doc matches code |
| 8 | tests/test_poi_amenity_contract.py | `test_amenity_node_contract` and new tests | Update `required_inputs` and inputs. Add the new tests listed under "Verification" | All pass |
| 9 | tests/test_initial_ddl_contract.py (S0) | `test_pipeline_config_rows_match_sources` `slv_poi_amenity` loop | Extend the sources with `amenpnpy` `EDGES_ON` srcs, in seed order | Test passes |
| 10 | tests/test_poi_media_amenity_contract.py (S0) | `test_amenity_untouched` | Expected `slv_poi_amenity` seed rows become five | Test passes |
| 11 | notebooks/NB_GLD_SRV_POI_AMENITY, NB_GLD_SRV_POI_INFO, NB_SLV_POI_ENTITY_NON_ENRICH | n/a | No edit | `git diff` is empty for these files |

### Order and stop points
1. **STOP S0 (user/orchestrator decision).** Add `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, `tests/test_initial_ddl_contract.py`, and `tests/test_poi_media_amenity_contract.py` to `scope.files`. `docs/context/02_NAMING_CONVENTION.md` §2.1 rule 1 requires both DDL notebooks in the same task. Do not edit rows 6, 9, or 10 before approval. Do not finish the task without them.
2. Record A-1 to A-8 and R-1 in `decision.md`.
3. Rows 1 to 4, then row 8, then run the pytest command.
4. Rows 5, 6, 9, 10, then row 7.
5. `python scripts/vv.py verify`. Reviews: `sql-data-reviewer` and `spark-runtime-reviewer`.
6. Write `runtime-runbook.md`: P5 pre-check, pause trigger, deploy, `amenpnpy` ON, run, post-checks, rollback (doc: "Rollout", "Rollback and forward recovery").
7. **STOP for evidence (user, Fabric DEV).** Run P5 first. If `pois_sector_null > 0` or `labels_multi_match > 0`, stop for a user decision. Main does not run Fabric.

### Tests and verification
- Update: `test_amenity_node_contract`. After S0: `test_pipeline_config_rows_match_sources` and `test_amenity_untouched`.
- New tests in `tests/test_poi_amenity_contract.py`:
  - `test_partner_helpers`
  - `test_partner_poi_id_matches_entity`
  - `test_partner_live_filter_matches_entity`
  - `test_partner_branch_contract`
  - `test_partner_seed_service_flags_null`
  - `test_google_branch_unchanged`
  - `test_srv_info_and_entity_untouched`
  - `test_amenity_partner_edges_patch`
  - `test_initial_seed_has_partner_amenity_edges` (after S0)
- Commands:
  - `python -m pytest tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py tests/test_poi_media_amenity_contract.py tests/test_poi_entity_contract.py tests/test_enr_poi_contract.py -q`
  - `python scripts/vv.py verify`
- Runtime (user): P5 SQL from doc "Rollout". After the run, rerun `amenity-poi-id-side.sql` and `amenity-poi-id-overlap.sql`: google ids stay 15995; partner `in_gld_srv_poi_info` is above 0 and at most P5 `pois`.

### Read only if needed
- "Decisions closing model-design open items" → rows 2, 3, and the `decision.md` entry.
- "Implementation plan / Partner helpers" → row 1.
- "Implementation plan / Partner branch" → row 2.
- "Implementation plan / `build` and `SPEC` changes" → row 3.
- "Implementation plan / `NB_CREATE_DDL` `amenpnmd` / `amenpnpy`" → row 5.
- "Implementation plan / `NB_SETUP_INITIAL_DDL`" → rows 6 and 9.
- "Implementation plan / Mapping doc" → rows 4 and 7.
- "Verification" → rows 8 to 10.
- "Ordering", "Rollout" (P5 SQL, R-1), "Rollback and forward recovery" → step 6 runbook.
- "Alternatives" → reviewer questions on the from_json, stop, and edge-owner choices.

# Architecture: 20261118-amenity-poi-id-align (round 2)

## Status

The ledger now settles the partner path. `D-2` sets `poi_id = uuid_md5(id, 'partner')`. `D-11` fixes the JSON path, the fallback, and the left join. `D-12` fixes `business_sector`, `amenity_group`, and the multi-match stop. `model-design.md` `## Keys` and `## Columns` give the grain and the key. This document closes open items 1 and 3 to 9 of `model-design.md` `## Conflicts and questions` as engineering choices (A-1 to A-7 below). Each choice is grounded in existing engine behaviour or in the evidence. None of them invents a business value. Item 2 (ledger IDs) is cosmetic.

One scope gap blocks part of the edit list. `docs/context/02_NAMING_CONVENTION.md` §2.1 rule 1 says every config `INSERT` must change both `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL` in the same task. `NB_SETUP_INITIAL_DDL.ipynb`, `tests/test_initial_ddl_contract.py`, and `tests/test_poi_media_amenity_contract.py` (`test_amenity_untouched` pins exactly three `slv_poi_amenity` edges) are not in `scope.files`. That is stop S0, a user or orchestrator decision. It is not missing evidence.

## Scope

- `NB_SLV_POI_AMENITY`:
  - `d1amenmatch`: pure partner helpers.
  - `d1amenbuild`: a partner branch unioned with the unchanged google branch, plus two new inputs.
  - `d1amenmd`: the markdown.
- `NB_CREATE_DDL`: a new cell pair `amenpnmd` / `amenpnpy` at the end. It adds two RECOMPUTE edges, `slv_pn_business_services → slv_poi_amenity` and `slv_pn_business_service_i18ns → slv_poi_amenity`, on `PL_VV_TRANS_SLV_TO_ENR_15M`.
- `NB_SETUP_INITIAL_DDL` `init_seed_ctrl`: the same two rows in `PIPELINE_CONFIG_ROWS`. Needs S0.
- `docs/context/mapping_gld_srv_poi_amenity.md` §0 and §1.
- Tests:
  - `tests/test_poi_amenity_contract.py`.
  - After S0: `tests/test_initial_ddl_contract.py` and `tests/test_poi_media_amenity_contract.py`.
- No edit; checked by tests only: `NB_GLD_SRV_POI_AMENITY`, `NB_GLD_SRV_POI_INFO`, `NB_SLV_POI_ENTITY_NON_ENRICH`.

## Non-goals

- The google filter in `NB_GLD_SRV_POI_INFO` `srvinfobuild` (D-2). The 15995 google amenity ids stay off info.
- The google amenity rows, `FLAG_MATCH`, `TYPE_MATCH`, `JSON_MATCH`, and the google dictionary guards.
- Any other `facilities` key, or `store_profile.specialty_tags` (D-11).
- Grain, key, `OUT_COLS`, or DDL changes. The amenities API. A third `poi_id` formula.
- `NB_SETUP_POI_AMENITY` and `NB_SETUP_POI_ENTITY`. Their edge prechecks will stop on a rerun (see Rollout, R-1).
- Any Fabric run, commit, or push.

## Invariants

- **I1.** For the same inputs, google output rows are identical before and after: same keys, same values, same `row_hash`. Only the final `return` of the google code path changes, from `out.select(*OUT_COLS)` to a union.
- **I2.** Every partner `poi_id` is `uuid_md5(F.col("id"), F.lit(PARTNER))`, with `id = business_service_id` of the live `vi` row. That is the same expression as `_partner` in `NB_SLV_POI_ENTITY_NON_ENRICH` `b1entitybuild`. Every partner row's `poi_id` is on a live entity row with `source_name = partner` (inner join).
- **I3.** The key `(poi_id, business_sector, amenity_group, amenity_raw)` has no NULL and no duplicate. The engine already blocks both: `quality_gate` in `NB_LIB_TRANSFORM_SLV_GLD` checks `pk_null` and `pk_duplicate`. The partner branch also raises an explicit `QualityGateError` before return when a partner row has a NULL `business_sector`. No filler value (D-12).
- **I4.** Partner rows join only active partner dictionary rows: `lower(trim(source_name)) = 'partner'` and `is_active = true`. Any label present in the data that matches more than one such row (after `trim`) raises `QualityGateError` before return (D-12). The google dictionary path is untouched.
- **I5.** On a match, `amenity_group` is the dictionary row's `amenity_group`. Otherwise it is the literal `specialty_tags`. On no match, `amenity`, `amenity_en`, `amenity_vi`, and `service_flags` are NULL and the row is still written (D-11, D-12). `business_sector` always comes from `slv_pn_business_services` and never from the dictionary.
- **I6.** Labels come only from `$.facilities.specialty_tags`. The fallback works on that value: the `vi` value is used if it is not NULL, otherwise the `svc` value. A non-NULL empty array means zero labels and no fallback.
- **I7.** These stay byte-for-byte: `NodeSpec.pk`, `OUT_COLS`, and `write_mode="MERGE"` in `d1amenbuild`. These notebooks stay unchanged: `srvamenitybuild`, `srvinfobuild`, `b1entitybuild`.
- **I8.** After the patch there are exactly five active RECOMPUTE edges into `lh_vv_silver.dbo.slv_poi_amenity`, all on `PL_VV_TRANS_SLV_TO_ENR_15M`. `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL` declare the same set.
- **I9.** Every partner dictionary seed row has `service_flags = None`. So `gld_enr_poi_info.service_flag` for partner POIs stays `"[]"` (`NB_ENR_POI_INFO` `_service_flag` ignores NULLs).
- **I10.** A partner branch with zero rows is valid and does not raise.

## State ownership

- `slv_poi_amenity`: single writer `NB_SLV_POI_AMENITY` through `run_node` (MERGE, RECOMPUTE soft-delete). Unchanged.
- `gld_srv_poi_amenity`: single writer `NB_GLD_SRV_POI_AMENITY`, 1-1 copy. Unchanged.
- Read-only inputs:
  - `slv_pn_business_service_i18ns` and `slv_pn_business_services`: partner L1, owned by the extraction.
  - `ref_dictionary_amenities`: owned by the seed notebooks.
  - `slv_poi_entity_non_enrich`: owned by its node.
- `ctrl_mng_pipeline_config` edges: on an existing environment, `amenpnpy` owns the two new rows. On an empty environment, `NB_SETUP_INITIAL_DDL` owns them.
- Edge watermarks `wm_e__slv_poi_amenity__slv_pn_*`: the library creates and advances them (`edge_wm_id`; an edge never read counts as a New Edge). The patch cell writes no watermark row.

## Grain and keys

See `model-design.md` `## Entities and grain` (grain unchanged) and `## Keys` (`slv_poi_amenity` primary key and MERGE key; partner `poi_id`; business key of a partner row).

Collision analysis:

- Google ids come from `HASH_MD5_UUID(source_name, source_id)` and partner ids from `md5(concat(id, 'partner'))`. The input strings are disjoint, so the ids are disjoint.
- Inside the partner branch, `(poi_id, amenity_raw)` is made unique (`dropDuplicates`). `amenity_group` is a function of `amenity_raw` once the multi-match stop holds. `business_sector` is a function of `poi_id`: one live svc row per `id`. A duplicate there would already fail the entity node.
- The engine `pk_duplicate` gate is the backstop.

## Decisions closing model-design open items

- **A-1 (item 3, NULL or blank sector).**
  - NULL `business_sector`: the node stops before the write with an explicit `QualityGateError`. That is the engine's behaviour today (`pk_null`). The explicit raise only gives a clearer message.
  - Blank `''`: passed through as the source value, counted in `partner_sector_blank`, and reported with `ctx.warn`. `''` is not invented data, and the amenity API does not expose `business_sector`.
  - Evidence: `partner-amenity-label-column.txt` shows `facilities.specialty_tags` only under `f_n_b`, so today there are 0 NULL or blank-sector rows. Pre-check P5 confirms this under the exact D-11 rule.
  - If the user wants drop-and-count instead, it is a one-line change. It is not made here.
- **A-2 (item 4).** The partner dictionary filter is `lower(trim(source_name)) == 'partner'` and `is_active == True`, the same form as the google path and D-6.
- **A-3 (item 5).** Live filter `_live` = `~coalesce(deleted, false)` on both L1 tables. The lead table is the live `vi` row, with a left join to live svc on `id`. Same as `_partner`. Services with no live `vi` row produce nothing, same as the entity. A `vi` row with no live svc row has a NULL sector, which A-1 handles.
- **A-4 (item 6).** Inner join to live entity rows with `source_name = partner`, on `poi_id`. It mirrors the google branch and enforces I2. Rows dropped by the join are counted in `partner_without_entity`. Evidence P3 shows 295/295 entity partner ids on info.
- **A-5 (item 7).**
  - Labels: `trim`, then drop NULL and `''`.
  - Match: exact on the `trim`-ed `amenity_raw`. D-9 shows exact and case-insensitive counts are equal.
  - Repeated labels: `dropDuplicates(["poi_id", "amenity_raw"])`.
  - `amenity_raw` is written as the trimmed label.
- **A-6 (item 8).** Parse with `from_json(am, PARTNER_TAGS)`, where `PARTNER_TAGS = "struct<facilities:struct<specialty_tags:array<string>>>"`. JSON that does not parse gives a NULL struct, which is skipped and counted in `partner_unparsed_json`. A value that is not an array gives a NULL field, which is skipped. `explode`, not `explode_outer`. No `get_json_object`. This keeps the existing guard in `test_amenity_node_contract`.
- **A-7 (item 9).** The multi-match stop covers labels present in the current partner rows only (literal reading of D-12). A duplicate partner dictionary `amenity_raw` that no data uses does not stop the node.
- **A-8 (item 1).** Two new inputs, `svc` and `i18n`, both in `required_inputs`, so an empty L1 table cannot soft-delete the partner rows. The new edges come from the `amenpnpy` and `NB_SETUP_INITIAL_DDL` rows. The engine requires `spec.inputs` to equal the active edges exactly (`spec.inputs lệch config`).

Main records A-1 to A-8 in `decision.md` as one architecture entry before code.

## Alternatives

| Topic | Option | Verdict |
|---|---|---|
| Where partner rows are built | (a) A branch in `d1amenbuild`, two new edges | **Selected.** Stays inside D-2. One writer, one MERGE. |
| | (b) An `amentities`-derived column on `slv_poi_entity_non_enrich` | Rejected: a model change D-2 did not approve, and it widens the blast radius to info and enr. |
| | (c) A separate node or table | Rejected: changes the grain and lineage of gold. |
| JSON extraction | (a) `from_json` with a struct schema | **Selected:** one parse, and it keeps the existing guard against `get_json_object`. |
| | (b) `get_json_object` then `from_json(array<string>)` (the probe form) | Rejected: it would relax a pinned guard test for no gain. P5 uses the struct form, so the probe and the code agree. |
| NULL or blank sector | (a) Engine stop for NULL; pass-through and warn for `''` | **Selected:** no new rule, no invented value. |
| | (b) Drop and count | Not chosen: dropping rows is a business rule D-12 did not give. |
| Multi-match scope | (a) Labels present in the data | **Selected:** literal D-12. |
| | (b) Any duplicated partner `amenity_raw` in the dictionary | Rejected: it can block on dictionary rows no data uses. |
| Edge owner | (a) New `NB_CREATE_DDL` cell plus `NB_SETUP_INITIAL_DDL` seed | **Selected:** this is the §2.1 rule. |
| | (b) Widen the UPSERT sets of `NB_SETUP_POI_AMENITY` / `NB_SETUP_POI_ENTITY` | Not chosen: they are superseded by `NB_SETUP_INITIAL_DDL` on empty environments and are not in scope. Residual risk R-1. |

## Ordering

- **Inside the node:**
  1. The google branch, unchanged.
  2. `_partner_rows`, which includes the column checks, the multi-match stop, and the NULL-sector stop.
  3. Metrics.
  4. `unionByName`.
  5. The engine `quality_gate`.
  6. One MERGE.
- **Between nodes:** the existing edge `slv_poi_entity_non_enrich → slv_poi_amenity` still orders entity before amenity. The partner L1 tables are external sources of `PL_VV_TRANS_SLV_TO_ENR_15M`, as they already are for the entity node. `gld_srv_poi_amenity` (`PL_VV_TRANS_SLV_TO_GLD_1H`) and `gld_enr_poi_info` (an existing edge from `slv_poi_amenity`) follow through their existing edges.
- **Deployment:** the notebook and the edges must change together. With the old notebook and new edges, the run raises `ConfigError` "cạnh từ … không có vai trò". With the new notebook and old edges, it raises "vai trò 'svc' … không có cạnh". Both fail before any write. Rollout therefore pauses the trigger, deploys, runs `amenpnpy`, then resumes.

## Transaction and commit boundaries

- **Node:** one Delta MERGE through `run_node`. Google and partner rows commit together or not at all. Every partner guard raises inside `build`, before the MERGE.
- **`amenpnpy`:** a control-plane transaction under the flow lock `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M`. All checks run before the first write. The write is one `MERGE … WHEN NOT MATCHED THEN INSERT`, plus a conditional `UPDATE is_active` only when the value differs. A post-check follows the write. The lock is released in `finally`.

## Idempotency

- The node is a pure function of its pinned inputs. A rerun gives the same `row_hash` values and no updates.
- `amenpnpy` reruns are no-ops: the MERGE only inserts missing rows, and the UPDATE only fires when `is_active` differs. `NB_SETUP_INITIAL_DDL` is insert-only by design.

## Concurrency

- Single writer per table.
- `amenpnpy` takes and refreshes the flow lock before writing (`_refresh_lock`, lease 35 minutes), following the pattern in `rvi18nenrpy`. If another holder has the lock, the cell stops.
- If the entity and amenity nodes read different L1 versions in one run, the inner join drops at most the difference. That shows in `partner_without_entity`, and the next run converges.

## Retry and recovery

- Any QG or `ConfigError` leaves the target and the watermarks unchanged.
- The new edges stay "New Edge" until a successful run, so the next scheduled run retries automatically once the cause is fixed.

## Partial failure

| Failure | Effect | Handling |
|---|---|---|
| Multi-match label, NULL sector, or missing L1 column | Whole node FAILED. Google rows keep their previous state. | Accepted. Matches the google guards and D-12. |
| Partner L1 table empty | `required_inputs` → FAILED | Prevents a mass soft-delete. |
| JSON does not parse, or no tags | Zero partner rows for that POI | Metric only. |
| `amenpnpy` fails mid-cell | Nothing written, or the post-check raises | Rerun after the fix. The MERGE is idempotent. |

## Observability

New `ctx.metrics` keys:

- `partner_src_rows`
- `partner_tags_vi`
- `partner_tags_svc`
- `partner_unparsed_json`
- `partner_labels`
- `partner_without_entity`
- `partner_labels_unmatched` (distinct labels)
- `partner_sector_blank`
- `dict_partner_active`
- `rows_partner`
- `rows_google`

`rows` becomes google plus partner. The existing google metrics keep their meaning.

`ctx.warn` fires when `partner_labels_unmatched > 0`, `partner_sector_blank > 0`, or `partner_without_entity > 0`. QG messages name the labels (at most 20) and the D-12 reason.

## Security

No credentials, hosts, or personal data. P5 returns counts only, plus at most 50 amenity labels when multi-match is above 0. Amenity tags are not personal data.

## Rollout

1. S0 resolved. Edits, tests, `vv.py verify`, and reviews pass.
2. Main writes `runtime-runbook.md`, then stops before Fabric DEV. Steps for the user:
   1. Run pre-check P5 (below). Proceed only if `pois_sector_null = 0` and `labels_multi_match = 0`. Otherwise stop for a user decision: the first run would fail under A-1 or A-7.
   2. Pause the trigger of `PL_VV_TRANS_SLV_TO_ENR_15M`. Deploy `NB_SLV_POI_AMENITY`. Run the `NB_CREATE_DDL` cell `amenpnpy` with `MODE = "ON"`. Resume the trigger, or run the pipeline once.
   3. Let `PL_VV_TRANS_SLV_TO_GLD_1H` copy to gold.
   4. Post-checks:
      - Rerun `amenity-poi-id-side.sql` and `amenity-poi-id-overlap.sql`.
      - Google amenity `poi_id` count is still 15995.
      - Partner amenity `poi_id` count is above 0 and at most P5 `pois`.
      - `in_gld_srv_poi_info` equals the partner count.
      - `gld_enr_poi_info.service_flag` for partner rows is still `"[]"`.
- **R-1 (accepted risk, to record in `decision.md`).** After this patch, a rerun of `NB_SETUP_POI_AMENITY` or `NB_SETUP_POI_ENTITY` with apply stops at `setup_edge_issues` with "còn cạnh active ngoài cạnh chuẩn". It fails closed and writes nothing. The `amenpnmd` markdown says so.

P5 `partner-amenity-precheck.sql` (Fabric DEV, read-only, Spark SQL). Main saves it into the runbook:

```sql
WITH vi AS (
  SELECT business_service_id AS id, amentities AS am
  FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
  WHERE coalesce(deleted, false) = false AND locale = 'vi'),
svc AS (
  SELECT id, amentities AS am, business_sector
  FROM lh_vv_silver.dbo.slv_pn_business_services
  WHERE coalesce(deleted, false) = false),
tags AS (
  SELECT vi.id, svc.business_sector,
         coalesce(from_json(vi.am, 'struct<facilities:struct<specialty_tags:array<string>>>').facilities.specialty_tags,
                  from_json(svc.am, 'struct<facilities:struct<specialty_tags:array<string>>>').facilities.specialty_tags) AS t
  FROM vi LEFT JOIN svc ON vi.id = svc.id),
labels AS (
  SELECT DISTINCT id, business_sector, trim(l) AS label
  FROM tags LATERAL VIEW explode(t) e AS l
  WHERE l IS NOT NULL AND trim(l) <> ''),
dict AS (
  SELECT trim(amenity_raw) AS amenity_raw, count(*) AS n
  FROM lh_vv_silver.dbo.ref_dictionary_amenities
  WHERE is_active = true AND lower(trim(source_name)) = 'partner'
  GROUP BY trim(amenity_raw))
SELECT count(DISTINCT l.id) AS pois,
       count(*) AS rows,
       count(DISTINCT CASE WHEN l.business_sector IS NULL THEN l.id END) AS pois_sector_null,
       count(DISTINCT CASE WHEN trim(l.business_sector) = '' THEN l.id END) AS pois_sector_blank,
       count(DISTINCT CASE WHEN d.n > 1 THEN l.label END) AS labels_multi_match,
       count(DISTINCT CASE WHEN d.n = 1 THEN l.label END) AS labels_matched,
       count(DISTINCT CASE WHEN d.n IS NULL THEN l.label END) AS labels_unmatched
FROM labels l LEFT JOIN dict d ON l.label = d.amenity_raw;
```

If `labels_multi_match > 0`, list those labels (at most 50) with the same CTEs plus `WHERE d.n > 1`.

## Rollback and forward recovery

- **Rollback:**
  1. Pause the trigger.
  2. Revert `NB_SLV_POI_AMENITY`.
  3. Run `amenpnpy` with `MODE = "OFF"`. It sets `is_active = 0` on the two edges and keeps the rows. It never deletes.
  4. Run the node with `p_force = "true"`. RECOMPUTE soft-deletes the partner rows. Google rows are unchanged.
  5. Gold follows.
  6. Resume.
- **Forward:** fix the dictionary or the rule, then rerun. L1 still holds the source, so nothing is lost.

## Implementation plan

### Partner helpers (`d1amenmatch`, inside `BEGIN_AMENITY_MATCH` / `END_AMENITY_MATCH`, after `match_coverage`)

```python
PARTNER = "partner"
PARTNER_GROUP = "specialty_tags"  # D-12: amenity_group khi nhãn không khớp từ điển
PARTNER_TAGS = "struct<facilities:struct<specialty_tags:array<string>>>"  # D-11: chỉ $.facilities.specialty_tags


def partner_multi_match(dict_raws, labels):
    """D-12: nhãn có trong dữ liệu khớp > 1 dòng từ điển partner active. Đầu vào đã trim. Trả list sort."""
    seen = {}
    for raw in dict_raws:
        seen[raw] = seen.get(raw, 0) + 1
    return sorted(label for label in set(labels) if seen.get(label, 0) > 1)
```

### Partner branch (`d1amenbuild`, new functions before `build`)

```python
PN_I18N_COLS = ("business_service_id", "locale", "deleted", "amentities")
PN_SVC_COLS = ("id", "deleted", "amentities", "business_sector")


def _live(df: DataFrame) -> DataFrame:
    # Partner L1 CDC: deleted = true là dòng đã xoá (cùng _live của NB_SLV_POI_ENTITY_NON_ENRICH).
    return df.where(~F.coalesce(F.col("deleted"), F.lit(False)))


def _partner_rows(ctx: NodeContext, d: DataFrame):
    for role, cols in (("i18n", PN_I18N_COLS), ("svc", PN_SVC_COLS)):
        missing = [c for c in cols if c not in ctx.input(role).columns]
        if missing:
            raise ConfigError(f"slv_poi_amenity: đầu vào {role} thiếu cột {missing}")
    vi = (_live(ctx.input("i18n")).where(F.col("locale") == "vi")
          .select(F.col("business_service_id").alias("id"), F.col("amentities").alias("_vi_am")))
    svc = _live(ctx.input("svc")).select("id", F.col("amentities").alias("_svc_am"), "business_sector")
    # D-11: fallback theo giá trị specialty_tags, không theo cả khối amentities. D-12: sector từ svc.
    base = (vi.join(svc, "id", "left")
              .withColumn("_vi_js", F.from_json("_vi_am", PARTNER_TAGS))
              .withColumn("_svc_js", F.from_json("_svc_am", PARTNER_TAGS))
              .withColumn("_vi_tags", F.col("_vi_js.facilities.specialty_tags"))
              .withColumn("_svc_tags", F.col("_svc_js.facilities.specialty_tags"))
              .withColumn("_tags", F.coalesce("_vi_tags", "_svc_tags"))
              .withColumn("poi_id", uuid_md5(F.col("id"), F.lit(PARTNER)))  # D-2, cùng _partner
              .persist())
    ctx.cached.append(base)
    labels = (base.select("poi_id", "business_sector", F.explode("_tags").alias("_l"))
                  .select("poi_id", "business_sector", F.trim("_l").alias("amenity_raw"))
                  .where(F.col("amenity_raw").isNotNull() & (F.col("amenity_raw") != ""))
                  .dropDuplicates(["poi_id", "amenity_raw"]))
    ent = ctx.input("entity").where(F.lower(F.trim("source_name")) == PARTNER).select("poi_id").distinct()
    kept = labels.join(ent, "poi_id")
    pd = (d.where((F.lower(F.trim("source_name")) == PARTNER) & (F.col("is_active") == F.lit(True)))
           .select(F.trim("amenity_raw").alias("amenity_raw"), F.col("amenity_group").alias("_dict_group"),
                   "amenity", "amenity_en", "amenity_vi", "service_flags", F.lit(True).alias("_hit")))
    raws = [r[0] for r in pd.select("amenity_raw").collect()]
    multi = partner_multi_match(raws, [r[0] for r in kept.select("amenity_raw").distinct().collect()])
    if multi:
        raise QualityGateError(f"ref_dictionary_amenities: {len(multi)} nhãn partner khớp > 1 dòng partner "
                               f"{multi[:20]}; D-12 dừng, không ghi")
    out = (kept.join(F.broadcast(pd), "amenity_raw", "left")
               .withColumn("amenity_group", F.when(F.col("_hit"), F.col("_dict_group")).otherwise(F.lit(PARTNER_GROUP))))
    null_sector = out.where(F.col("business_sector").isNull()).count()
    if null_sector:
        raise QualityGateError(f"slv_poi_amenity: {null_sector} dòng partner business_sector NULL; "
                               "D-12 không có giá trị thay thế; không ghi")
    n_labels, n_kept = labels.count(), kept.count()
    m = dict(partner_src_rows=base.count(),
             partner_tags_vi=base.where(F.col("_vi_tags").isNotNull()).count(),
             partner_tags_svc=base.where(F.col("_vi_tags").isNull() & F.col("_svc_tags").isNotNull()).count(),
             partner_unparsed_json=base.where((F.col("_vi_am").isNotNull() & F.col("_vi_js").isNull())
                                              | (F.col("_svc_am").isNotNull() & F.col("_svc_js").isNull())).count(),
             partner_labels=n_labels, partner_without_entity=n_labels - n_kept,
             partner_labels_unmatched=out.where(F.col("_hit").isNull()).select("amenity_raw").distinct().count(),
             partner_sector_blank=out.where(F.trim("business_sector") == "").count(),
             dict_partner_active=len(raws), rows_partner=n_kept)
    for name in ("partner_labels_unmatched", "partner_sector_blank", "partner_without_entity"):
        ctx.warn(name, m[name])
    return out.select(*OUT_COLS), m
```

Main checks the `ctx.warn(name, count)` signature against its use in `NB_ENR_POI_INFO` (`ctx.warn("review_poi_not_in_entity", dropped)`).

### `build` and `SPEC` changes (`d1amenbuild`)

- Before `ctx.metrics.update(...)`: `n_google = sum(by_kind.values())`, `partner, pm = _partner_rows(ctx, d)`, `n = n_google + pm["rows_partner"]`.
- Add `rows_google=n_google` to the existing update and keep `rows=n`. Then `ctx.metrics.update(**pm)`.
- Return `out.select(*OUT_COLS).unionByName(partner)`. Keep the existing comment about an empty result.
- `SPEC.inputs` adds `"svc": "slv_pn_business_services"` and `"i18n": "slv_pn_business_service_i18ns"`.
- `required_inputs=("amenity", "entity", "dict", "svc", "i18n")`.
- `pk` and `write_mode` stay the same.

### `NB_CREATE_DDL` `amenpnmd` / `amenpnpy` (append at the end)

- **Markdown `amenpnmd`:** `[THÊM 18/11] 20261118-amenity-poi-id-align`. Content:
  - It adds two edges into `slv_poi_amenity` on `PL_VV_TRANS_SLV_TO_ENR_15M`.
  - Run it after deploying `NB_SLV_POI_AMENITY` from this task, with the trigger paused.
  - `MODE = "OFF"` is the rollback.
  - After it runs, `NB_SETUP_POI_AMENITY` and `NB_SETUP_POI_ENTITY` apply reruns stop (R-1).
- **Code `amenpnpy`:** follow the lock skeleton of `rvi18nenrpy` (`_refresh_lock`, acquire, `try`/`finally` release).
  - Constants: `CFG`, `WM`, `PL = "PL_VV_TRANS_SLV_TO_ENR_15M"`, `WID`, `SLV = "lh_vv_silver.dbo"`, `TRG = "slv_poi_amenity"`, `LEASE_MINUTES = 35`, `MODE = "ON"`, `STD = ("slv_3p_poi_amenity", "slv_poi_entity_non_enrich", "ref_dictionary_amenities")`, `RETIRED = ("slv_poi_entity",)`.
  - `EDGES_ON = [(1, "slv_pn_business_services", SLV_LITERAL, "slv_poi_amenity", "RECOMPUTE", None, 1), (2, "slv_pn_business_service_i18ns", SLV_LITERAL, "slv_poi_amenity", "RECOMPUTE", None, 1)]`. Write literal strings so that `_assign` can parse it. Use the same 7-tuple shape as `amenddlpy` `EDGES_ON`.
  - Stop before any write when:
    - the lock row is not exactly one;
    - an active edge into `(SLV, TRG)` is outside STD and `EDGES_ON` srcs;
    - an STD edge is not exactly one active RECOMPUTE row on `PL`;
    - an `EDGES_ON` src has more than one row, or a row on another `pl_name`;
    - a source table, or one of its `PN_*` columns, is missing.
  - Write (with `_refresh_lock()` before each statement):
    - `MERGE INTO CFG … ON pl_name, src_schema, src_tbl, trg_schema, trg_tbl WHEN NOT MATCHED THEN INSERT`, only for `MODE == "ON"`. Copy the column list and the `nb_name` handling from the config `MERGE` in `NB_SETUP_INITIAL_DDL` `init_seed_write`.
    - `UPDATE CFG SET is_active = <1|0>`, limited to the two edges, `WHERE is_active <> <target>`.
  - Post-check: ON gives five active edges on `PL`, one each. OFF gives the STD edges active and both new edges `is_active = 0`.
  - No `DELETE`, `DROP`, or watermark write.

### `NB_SETUP_INITIAL_DDL` `init_seed_ctrl` (after S0)

Append two tuples right after the three `slv_poi_amenity` rows, in the same shape:

- `("PL_VV_TRANS_SLV_TO_ENR_15M", "lh_vv_silver.dbo", "slv_pn_business_services", "lh_vv_silver.dbo", "slv_poi_amenity", 1, 1, "RECOMPUTE", None, None, None)`
- The same tuple with `slv_pn_business_service_i18ns`.

### Mapping doc

- §0:
  - Sources: add `amenpnpy`.
  - Five edges, and `SPEC.inputs` / `required_inputs` with `svc` and `i18n`.
  - Replace "`poi_id` … `MISSING`" with the origin per source: google from `slv_3p_poi_amenity.poi_id`; partner `uuid_md5(business_service_id, 'partner')`.
  - `business_sector` per source: google from the entity; partner from `slv_pn_business_services`.
  - The partner rule: D-11 path and value fallback, left join, `amenity_group` rule, multi-match stop, NULL-sector stop, `''` pass-through.
  - Update the markdown summary and the `NB_CREATE_DDL` line, which says three edges today.
- §1: partner rows reach gold 1-1 and therefore the API. Google ids are still not on `gld_srv_poi_info` (D-2).

## Verification

- **Existing tests:** they must pass unchanged, except:
  - `test_amenity_node_contract`: change `required_inputs` and add the two inputs.
  - After S0: `test_pipeline_config_rows_match_sources`, where the source tuple at the `slv_poi_amenity` loop is extended from `amenpnpy` `EDGES_ON`.
  - After S0: `test_amenity_untouched`, where the expected list becomes five rows.
- **New tests in `tests/test_poi_amenity_contract.py`:**
  - `test_partner_helpers`: run the match block with `exec`. `PARTNER == "partner"`, `PARTNER_GROUP == "specialty_tags"`, `PARTNER_TAGS` exact. `partner_multi_match(["a", "a", "b"], ["a", "b", "c"]) == ["a"]`. `partner_multi_match(["a", "a"], ["b"]) == []`.
  - `test_partner_poi_id_matches_entity`: `uuid_md5(F.col("id"), F.lit(PARTNER))` is in both `d1amenbuild` and `b1entitybuild`.
  - `test_partner_live_filter_matches_entity`: `~F.coalesce(F.col("deleted"), F.lit(False))` is in both notebooks.
  - `test_partner_branch_contract`. `d1amenbuild` contains:
    - `F.coalesce("_vi_tags", "_svc_tags")` and `locale") == "vi"`;
    - `vi.join(svc, "id", "left")` and `labels.join(ent, "poi_id")`;
    - `"amenity_raw", "left"` and `PARTNER_GROUP`;
    - `partner_multi_match(` and `business_sector").isNull()`.
    
    The `pd` select does not contain `business_sector`. There is no `get_json_object` and no `explode_outer`.
  - `test_partner_seed_service_flags_null` (I9): every `SEED_ROWS` row with `row[0] == "partner"` has `row[6] is None`.
  - `test_google_branch_unchanged`: the google dictionary filter, `match_coverage`, `legacy_blocks_write`, and `dropDuplicates(list(OUT_COLS) + ["_kind"])` are still present.
  - `test_srv_info_and_entity_untouched`: `srvinfobuild` still references `slv_enr_poi_destination` and `slv_enr_poi_info_multi_lang`. `srvamenitybuild` still returns `select(*OUT_COLS)`.
  - `test_amenity_partner_edges_patch`: `amenpnpy` `EDGES_ON` equals the two expected tuples. The cell contains `WHEN NOT MATCHED THEN INSERT`, `_refresh_lock()`, `MODE`, and `PL_VV_TRANS_SLV_TO_ENR_15M`. It has no `DELETE FROM` and no `DROP`.
  - `test_initial_seed_has_partner_amenity_edges` (after S0): `PIPELINE_CONFIG_ROWS` rows into `slv_poi_amenity` equal STD plus the two new sources, all active RECOMPUTE on ENR_15M.
- **Commands:**
  - `python -m pytest tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py tests/test_poi_media_amenity_contract.py tests/test_poi_entity_contract.py tests/test_enr_poi_contract.py -q`
  - `python scripts/vv.py verify`
- **Reviewers:** `sql-data-reviewer` and `spark-runtime-reviewer`. `state-correctness-reviewer` is not needed: the MERGE key and the write order are unchanged, and the new edges only add inputs.
