# Request

## User outcome

Silver L1 for the 3rd-party crawl (`slv_3p_poi_*`) matches the new raw `normalized_payload`. Extract only splits structure, casts types, builds MERGE keys, and writes snapshot technical columns. Business choices move to Silver L2.

## Scope

### In scope

- Compare one attached raw sample of `normalized_payload` with the current L1 model. Record keys and JSON types only.
- Redesign active L1 tables, `ctrl_cfg_schema_registry` seed, and `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` so every path exists in the raw payload.
- Move language filtering, canonical names, sector/category mapping, slug, destination, and enrichment inference to L2 (`slv_poi`, `slv_poi_localization`, and the other `slv_poi_*` nodes under `NB_00_ORCHES_SLV_TO_GLD`).
- Disable or remove an L1 table that no longer has a source block, and update every L2 edge that reads it.
- Align `docs/context/01_DATA_MODEL.md`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, and `CTRL_TABLES_CONTEXT.md`.

### Out of scope

- Partner CDC (`partner_raw_data`, `slv_pn_*`), except a shared L2 node whose column contract changes.
- Renaming `brz_3rd_crawler_poi_stream` or moving control tables. That work is task `20261008-migrate-ctrl-lakehouse-rename-3p-raw`.
- Reading gold from extract, or putting business rules in gold.
- Adding a 3P activity to `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` unless a later architecture explicitly approves it.
- Expanding `raw_payload` unless evidence shows extract must read it.

## Acceptance criteria

- `architecture.md` has the sample key tree, the L1 old/new comparison, the extract-to-L2 behavior list, grain, keys, commit order, idempotency, and rollback.
- Registry and extract paths are limited to paths confirmed against the raw payload.
- `lang_object_path` / `lang_map_path` do not point at enrichment when those blocks are absent.
- L2 nodes read the new L1 tables and state where each former enrichment decision now comes from, or that the column is intentionally NULL.
- `python scripts/vv.py verify <task-id>` passes.
- Context docs match the new model.
- Task artifacts contain no payload values and no personal data.

## Constraints

- One sample row does not prove coverage, null rate, or uniqueness. Missing facts stay at `waiting_evidence`.
- No crawl delete signal. Child tables upsert only. L2 uses `_last_seen_at` to notice a disappeared element.
- Watermark `wm_transform_brz_3rd_crawler_poi_stream` advances only after every active table succeeds, and never moves backward.
- L2 recomputes and MERGEs on `row_hash`.
- Third-party `poi_id` stays `HASH_MD5_UUID` of bronze `source_name` + `source_id` while those two fields remain the source identity.
- Main is Grok 4.7 Medium. For this task the user approved Cursor subagents: architect `claude-opus-5-5-medium` (medium), reviewers `gpt-5.6-sol-medium` (medium), read-only. Do not call `python scripts/vv.py run-gate`.
- Do not commit, push, or merge.

## Classification rationale

- Complexity: high. L1 grain, the extract/L2 boundary, and extract state all change.
- Risk: high. Watermark, CDC state, MERGE order, and L2 inputs change together. Rollback is a full rescan, not a silent repair.
- Architecture: required. Table grain, key ownership, and the bronze/L1/L2 commit boundary change.
- Evidence: required. The sample fixes the key tree of one document. It does not prove that `extra_info.enrichment` and `enrichmentSiblings` are absent in bronze, or that null blocks stay null.
- Runtime proof: required. Dry-run full scan, rerun, watermark monotonicity, state/reject, and L1/L2 rollback.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, and `fabric-pipeline-reviewer` because the extract exit contract (`langs`, LANG profile) is expected to change. `risk-gate` is required by the high risk level.

## Repository facts that affect later gates

- L2 node notebooks (`NB_<UPPER(trg_tbl)>` for `slv_poi`, `slv_poi_localization`, and the other L2 tables) are not in this repository. `NB_00_ORCHES_SLV_TO_GLD` only calls `orchestrate()`. Their SQL is described in `docs/context/01_DATA_MODEL.md` section 6. Implementation of N2/N4 cannot start until those notebooks are in the repo or the user points at them.
- Current L1 is seeded in `notebooks/NB_CREATE_DDL.ipynb` as `TABLE_CONFIGS_3P`: 14 tables, 13 active. `slv_3p_poi_policy` is already inactive.
