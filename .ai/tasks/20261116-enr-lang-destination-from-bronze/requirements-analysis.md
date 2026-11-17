ANALYSIS_STATUS: USER_DECISION

# Requirements analysis: 20261116-enr-lang-destination-from-bronze

## 1. Inputs

| field | value |
|---|---|
| task_id | 20261116-enr-lang-destination-from-bronze |
| mapping_path | docs/requirements/20261116-enr-lang-destination-from-bronze/MAPPING.md |
| mapping_id | MAP-20261116-enr-lang-destination-from-bronze |
| mapping_version | 5 |
| brd_path | docs/requirements/20261116-enr-lang-destination-from-bronze/BRD.md |
| brd_id | BRD-20261116-enr-lang-destination-from-bronze |
| brd_version | 4 |
| analyst | requirements-analyst |
| model | claude-opus-5-5 |
| effort | medium |
| analyzed_on | 2026-11-16 |
| skipped_example_rows | none |

## 2. Input problems

None. Both files pass input validation rules 1 to 14. The "Quy ước dùng chung" section is identical in `docs/templates/MAPPING_TEMPLATE.md` and `docs/templates/BRD_TEMPLATE.md` and matches the agent restatement, so there is no `TEMPLATE_MISMATCH`. Every reference cell names a filled row, including MQ-001 `blocks` (TRG-001, TRG-002) and COL-036 `src_id` (SRC-002, SRC-004). Neither file contains personal data, secrets, or production extracts.

## 3. Requirement coverage

| req_id | priority | coverage | trg_tbl | grain | key | ds_ids | col_ids | rule_ids | basis |
|---|---|---|---|---|---|---|---|---|---|
| BR-001 | MUST | MAPPED | slv_enr_poi_info_multi_lang | 1 row / (`poi_id`, `lang`) | `poi_id`, `lang` | DS-001 | COL-001 to COL-009 | | Grain and key are equal in BR-001 and TRG-001 and are stated in `docs/context/mapping_gld_srv_poi_multi_lang.md §2` ("một dòng cho `(poi_id, lang)`. MERGE đúng cặp đó"). The target columns exist in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` (`poi_id`, `lang`, `time_to_spend`, `best_time`, `cost_vnd`, `description`, `experience`, `source_name`). `cost` is the BR-004 rename. `probe_json_shape.txt` reports the `label,text` key set for 360/360 rows of `display.cost`, `best_time`, and `time_to_spend`. `probe_json_shape_rest.txt` reports `experiences` as an array in 360/360 rows and `translated_at` with `parse_null` 0. `probe_brz_enrichment_result.txt` `SCHEMA` lists `poi_id`, `lang`, `source`, and `data`. The source sets are equal: {`brz_enrichment_result`} in DS-001 and SRC-001. The legacy-target question is closed by MQ-001 (answered 2026-11-16, `blocks` TRG-001) |
| BR-002 | MUST | MAPPED | slv_enr_poi_destination | 1 row / `poi_id` | `poi_id` | DS-002 | COL-010 to COL-033 | | Grain and key are equal in BR-002 and TRG-002 and are stated in `docs/context/mapping_gld_srv_poi_info.md §1.6`. The AG-001 citation gap from the version 4 analysis is closed. COL-011, COL-013, COL-015, and COL-017 to COL-025 now list `USER_STATED, TASK_EVIDENCE` and cite `probe_brz_enrichment_result.txt`. Its `JSON_PATH_NONEMPTY` section lists every one of their paths, with counts that match the row notes (for example 93, 0, 111, and 112 of 113). `TABLE_SPECS` lists `ward`, `district`, `city`, `full_address`, `destination_id`, `country_code`, `postal_code`, `lat` and `lng` (`DOUBLE`), and `destination_name`. COL-029 to COL-031 are supported by `probe_json_shape_rest.txt` (113/113 arrays, 271 elements, 1 null `id`, 1 null `name`). The NULL values in COL-032 and COL-033 are a user decision in the BR-002 statement. The source sets are equal: {`brz_enrichment_result`}. The legacy-target question is closed by MQ-001 (`blocks` TRG-002). Observation: `$.address.new.district.name` and `...name_with_type` are non-empty in 0/113 rows, so COL-014 and COL-015 are NULL on the current DEV snapshot |
| BR-003 | MUST | PLATFORM_VIOLATION | gld_srv_poi_multi_lang | 1 row / (`poi_id`, `lang`) | `poi_id`, `lang` | DS-001, DS-003 | COL-004, COL-034 | | Grain and key are equal in BR-003 and TRG-003 (`docs/context/mapping_gld_srv_poi_multi_lang.md §1.1`, "MERGE theo grain `(poi_id, lang)`"). The non-bronze source SRC-003 has known grain and key (`§2`). COL-034 is known: `TABLE_SPECS` has `gld_srv_poi_multi_lang.cost_vnd STRING`, `§1.2` and `§1.1` state the P1 copy and the P2 null, and `§2` states the rename to `cost` with PostgreSQL kept as `text`, the API reading `cost`, and `practical_info.md` in scope. CSM-001 is supported by `AGENTS.md §7`. The source sets are equal: SRC-001 and SRC-003 against DS-001 and DS-003. COL-004 writes TRG-001, not this target. It is upstream lineage, not a target conflict. Violation: SRC-003 fails PC-01 |
| BR-004 | MUST | MAPPED | slv_enr_poi_info_multi_lang | 1 row / (`poi_id`, `lang`) | `poi_id`, `lang` | DS-001 | COL-004 | | Same target, grain, and key as BR-001 (`docs/context/mapping_gld_srv_poi_multi_lang.md §2`). COL-004 is known: `TABLE_SPECS` has `cost_vnd STRING`, `§2` states the rename, and `probe_json_shape.txt` reports 360/360 `label,text`. The source sets are equal. The legacy-target question is closed by MQ-001 |
| BR-005 | MUST | MAPPED | gld_srv_poi_info | 1 row / `poi_id` | `poi_id` | DS-004 | COL-035 | | Grain and key are equal in BR-005 and TRG-004 (`docs/context/mapping_gld_srv_poi_info.md §1.1`, "Grain một dòng `poi_id`. MERGE theo `poi_id`"). SRC-002 has grain and key `poi_id` (`notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` `pk=("poi_id",)`). `street` is in `ADDRESS_COLS` and in `TABLE_SPECS` for `gld_srv_poi_info`. `§1.6` states the new source. Every required gold cell of COL-035 is filled and known. The source sets are equal (SRC-002 and DS-004) |
| BR-006 | MUST | PLATFORM_VIOLATION | gld_srv_poi_info | 1 row / `poi_id` | `poi_id` | DS-004, DS-005 | COL-036 | | Grain and key are equal (TRG-004). `docs/context/mapping_gld_srv_poi_info.md §1.6` states the three-group formula, the `, ` delimiter, and the drop-the-whole-group-on-null rule. The COL-036 path cell now matches `§1.6`. The rule is gold-local logic of `gld_srv_poi_info`, which `docs/context/01_DATA_MODEL.md §2` allows. SRC-004 has known grain and key (`§1.6`). `house_number` and `street` are in `ADDRESS_COLS`. `full_address` is in `TABLE_SPECS` for `slv_enr_poi_destination`. `formatted_address`, `ward_with_type`, and `city_with_type` are new columns that BR-002 fills (COL-018, COL-013, COL-017). The source sets are equal (SRC-002 and SRC-004 against DS-004 and DS-005). Violation: SRC-004 fails PC-01 |

## 4. Rules and identifiers

| item_id | layer | rule_home_or_formula | status | basis |
|---|---|---|---|---|

BRD sections 7 and 8 have no filled rows, and no requirement lists `rule_ids` or `id_rule_ids`. `poi_id` is copied 1-1 from bronze `poi_id` (COL-001, COL-010) and has no new identifier formula. The silver latest-`version` rule (`mapping_gld_srv_poi_multi_lang.md §2`, `mapping_gld_srv_poi_info.md §1.6`) is an event-ordering contract for the MERGE, not a shared business rule. The Architect owns its design.

## 5. Platform checks

| check | item_ids | result | basis |
|---|---|---|---|
| PC-01 | SRC-001, SRC-002, TRG-003, TRG-004 | PASS | Bronze has no common prefix (`docs/context/02_NAMING_CONVENTION.md §1`). `slv_poi_` is the silver L2 prefix. `gld_srv_` is the gold serving prefix |
| PC-01 | TRG-001, TRG-002 | PASS | No layer prefix, so PC-01 treats them as legacy targets. The required user question is MQ-001, answered 2026-11-16: "Giữ hai tên bảng đã có" |
| PC-01 | SRC-003, SRC-004 | PLATFORM_VIOLATION | `slv_enr_` is not a silver L1 prefix (`slv_pn_`, `slv_3p_`, `slv_pm_`; `AGENTS.md §7`, `docs/context/02_NAMING_CONVENTION.md §1`). The legacy exemption in PC-01 covers targets only. MQ-001 records that the user accepts this deviation ("Chấp nhận tiền tố `slv_enr_` lệch PC-01"). That answer is a user decision, not a pass. This analysis cannot clear the check. Main records the acceptance in `decision.md` |
| PC-02 | TRG-001 to TRG-004 | PASS | No target has `layer` `bronze` |
| PC-03 | (none) | PASS | BRD section 7 has no rule rows |
| PC-04 | COL-001 to COL-033 | PASS | On every silver L1 row, `rule_ids` is blank and `src_object` (`$`) and `convert_rule` are filled. `key_order` is set on the key rows (COL-001, COL-003, COL-010). The `event_type` routing, the array-to-JSON-string mapping, and the NULL columns only shape the payload. They are not business rules |
| PC-05 | COL-034, COL-035, COL-036 | PASS | `rule_ids`, `src_object`, `convert_rule`, and `key_order` are blank. The sources are silver (SRC-002, SRC-003, SRC-004). No gold target reads gold. The BR-006 priority logic belongs to `gld_srv_poi_info` only |
| PC-06 | COL-001, COL-003, COL-010, BR-001 to BR-006 | PASS | `poi_id` comes 1-1 from bronze `poi_id`. `lang` is a separate key column (`key_order` 2), not part of `poi_id`. No row uses `poi_uid` (`AGENTS.md §7`) |
| PC-07 | FLOW-001, FLOW-003, FLOW-005, FLOW-006, FLOW-008, FLOW-010, FLOW-012 | PASS | `NB_00_ORCHES_SLV_TO_GLD`, `NB_GLD_SRV_POI_MULTI_LANG`, and `NB_GLD_SRV_POI_INFO` follow `docs/context/02_NAMING_CONVENTION.md §2`. `PL_VV_TRANS_SLV_TO_GLD_30M` matches `CADENCE_RE` (§3) and is confirmed by `mapping_gld_srv_poi_multi_lang.md §1.1`. FLOW-012 `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` follows the extract pattern, with `name_status` `PROPOSED` and `[PROPOSED]` in `note`. TRG-001 and TRG-002 have known grain and key, so Mapping rule 9 allows the name. No FLOW row sets `pl_name` for TRG-001 or TRG-002 |
| PC-08 | FLOW-002, FLOW-007, FLOW-011, COL-001 to COL-033 | PASS | `RECOMPUTE` and `DOC` are §6 `load_mode` values. `NONE` and `ISO_UTC_TS` are §6 `convert_rule` values, and `ISO_UTC_TS` goes with `timestamp` (COL-009). Keys have `key_order` 1 and 2 on TRG-001 and 1 on TRG-002 (`docs/context/CTRL_TABLES_CONTEXT.md §5`). For the Architect: §6 has no constant-NULL path form, so the path `null` in COL-032 and COL-033 needs an explicit configuration decision. §6 also does not define how an `a.b` path projects an array (COL-030, COL-031). `CTRL_TABLES_CONTEXT.md §3` limits `load_mode` per extract notebook, so the new notebook must accept `DOC` |
| PC-09 | COL-001 to COL-036 | PASS | No business column reuses a technical column of its layer (`docs/context/02_NAMING_CONVENTION.md §5.2`). `translated_at` is a business timestamp, not `created_at` or `updated_at` |

## 6. Gaps, conflicts, and missing evidence

| gap_id | blocks | missing_fact | kind | why_repo_cannot_answer | resolution_type | pass_fail_criterion |
|---|---|---|---|---|---|---|

No gaps remain. Mapping sections 6 and 7 and BRD sections 11 to 13 have no filled rows. The one question, MQ-001, is answered. The version 4 gaps are closed:

- AG-001 (unsupported `CONTEXT_STATED` citations on COL-011, COL-013, COL-015, and COL-017 to COL-025) is closed by the `TASK_EVIDENCE` citation of `probe_brz_enrichment_result.txt`.
- AG-002 (the legacy-target question for TRG-001 and TRG-002) is closed by MQ-001.

Non-blocking observations for Main:

- `docs/context/mapping_gld_srv_poi_info.md §1.2` (the `full_address` and `street` rows) and `docs/context/mapping_gld_srv_poi_multi_lang.md §1.2` (the `cost_vnd` row) still describe the lineage before this task. `§1.6` and `§2` record the new decision, and SCOPE-005 and AC-005 require updating the files before review. This is not reported as a `CONFLICT` because `§1.6` and `§2` are labelled as the decision for this task.
- DS-003 lists only `USER_STATED`. The table itself is stated by its cited `TABLE_SPECS` and by SRC-003 (`CONTEXT_STATED`), so the source is treated as known.

## 7. Questions for the user

| q_id | blocks | question | resolution_type |
|---|---|---|---|

No open questions. The remaining item is a user decision on a platform violation, not a missing fact. MQ-001 already records the user's acceptance of the `slv_enr_` deviation on SRC-003 and SRC-004 (PC-01). Main must record that acceptance as an accepted platform deviation in `decision.md` before the Architect gate. The alternative is to rename the tables, which SCOPE-006 does not include.

## 8. Handoff notes for Main

Not written. ANALYSIS_STATUS is USER_DECISION.
