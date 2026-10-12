ANALYSIS_STATUS: USER_DECISION

# Requirements analysis: 20261012-map-gld-enr-poi-tables

## 1. Inputs

| field | value |
|---|---|
| task_id | 20261012-map-gld-enr-poi-tables |
| mapping_path | docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md |
| mapping_id | MAP-20261012-map-gld-enr-poi-tables |
| mapping_version | 13 |
| brd_path | docs/requirements/20261012-map-gld-enr-poi-tables/BRD.md |
| brd_id | BRD-20261012-map-gld-enr-poi-tables |
| brd_version | 11 |
| analyst | requirements-analyst |
| model | claude-opus-5-5 |
| effort | medium |
| analyzed_on | 2026-10-12 |
| skipped_example_rows | none |

## 2. Input problems

None.

Input validation rules 1 to 14 pass:

- The "Quy ước dùng chung" section is the same in both filled files and in `docs/templates/MAPPING_TEMPLATE.md` and `docs/templates/BRD_TEMPLATE.md`. It agrees with this agent's restatement, so there is no `TEMPLATE_MISMATCH`.
- All IDs, versions, dates, and `doc_status` values are valid. Every numbered section and every column is present, and the columns are in template order.
- Row IDs are unique within each file. Every reference cell names a filled row. No cell refers to `MQ-055` or `ID-005`, which were removed. No `[EXAMPLE]` rows remain.
- No sanitized results exist under `.ai/tasks/20261012-map-gld-enr-poi-tables/evidence/results/`, so no value can use `TASK_EVIDENCE`.

Changes since the previous run (Mapping v12, BRD v10):

- `AG-010` is closed. `COL-027` now has `CONTEXT_STATED, USER_STATED`, and its `context_ref` cites the answered `MQ-057`, which sets the `PROPOSED` target name `review_text` and the source `slv_3p_poi_review.text`. `BQ-025` records the same answer.
- `AG-011` is closed. `RULE-003`, `RULE-004`, `RULE-005`, and `RULE-006` now cite `MQ-054` ("Không có bảng rule riêng") in `context_ref`. The no-rule-table exception now holds for all five rule rows.
- `AG-012` is closed. `ID-005` was removed from BRD section 8.
- `MQ-058` and `BQ-026` state that partner and 3rd-party rows are appended, not joined, and that `src_id` is not required. `COL-022` and `COL-024` have a blank `src_id`, and that is not `MISSING_SOURCE`.
- `MQ-059` and `BQ-024` state that `notebooks_lgc` is a field-business comparison source, not a design model. "Out-of-scope legacy physical facts" applies to `SRC-006`, `SRC-008`, `DS-004`, `DS-008`, the JSON paths in `COL-003` to `COL-007`, the partner `address` keys in `COL-013` to `COL-016`, the `locale` value (`SRC-005`, `DS-003`, `COL-012`), and `reviewId` (`COL-022`, `COL-024`, `ID-001`, `ID-002`). The `USER_STATED` grain and key on `SRC-006` and `SRC-008` count as known for coverage. The blank `layer` on `SRC-006` and `DS-004` is part of the closed `poi_enrichment` schema fact. `AG-001` to `AG-012` are not reopened, and their IDs are not reused.
- "Template exceptions" applies. The six write-time rows `COL-009`, `COL-010`, `COL-020`, `COL-021`, `COL-033`, and `COL-034` meet the write-time technical-column exception (`MQ-052`, `MQ-058`).

Later answers replace some earlier ones, and the rows follow the later answers: `MQ-001` and `BQ-002` are replaced by `MQ-031`, `MQ-039`, and `BQ-018`. `MQ-002` and `BQ-005` are replaced by `MQ-044`. `MQ-018`, `MQ-032`, `MQ-043`, and `BQ-019` are replaced by `MQ-034`, `MQ-050`, and `BQ-020`. `MQ-013` is replaced by `MQ-030` and `MQ-052`. `MQ-038` and `MQ-042` are replaced by `MQ-053`. None of these is a gap.

## 3. Requirement coverage

These notes apply to all three requirements:

- The target grain and key are known and are the same in the BRD and the Mapping. They are `USER_STATED` through `MQ-039`, which is allowed for the `PROPOSED` tables `TRG-001` to `TRG-003` and `BR-001` to `BR-003`.
- For each requirement, the BRD section 6 source-table set equals the Mapping section 3 set:
  - `BR-001` uses 9 tables: `slv_3p_poi`, `slv_pn_business_services`, `poi_enrichment`, `slv_3p_poi_address`, `slv_3p_poi_review`, `slv_3p_poi_contact`, `slv_3p_poi_rating`, `slv_3p_poi_price`, and `slv_3p_poi_opening_hours`.
  - `BR-002` uses 5 tables: `slv_3p_poi`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`, `slv_3p_poi_address`, and `poi_address_enrichment_staging`.
  - `BR-003` uses 2 tables: `slv_3p_poi` and `slv_3p_poi_review`.
- Every non-bronze source has a known grain and key. For `SRC-001` to `SRC-005` and `SRC-009` to `SRC-012`, the sources are `docs/context/01_DATA_MODEL.md §5.1` and `§5.2`, and `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS` and `TABLE_CONFIGS_3P`. For `SRC-006` and `SRC-008`, the grain and key are closed facts (section 2).
- Every mapping row has its required cells filled and known, after counting template exceptions and closed facts. `src_id` is not required.
- The Mapping has 23 info rows, 11 coordinate rows, and 9 review rows, which matches `AC-001`.
- Every `rule_ids` entry has a known statement and a known home: `TEMPLATE_EXCEPTION_NO_RULE_TABLE` through `MQ-054`. Every `id_rule_ids` entry has a known formula.
- The only remaining code is `PLATFORM_VIOLATION`. No requirement is `MAPPED`, because the definition of `MAPPED` requires that no other code applies.

| req_id | priority | coverage | trg_tbl | grain | key | ds_ids | col_ids | rule_ids | basis |
|---|---|---|---|---|---|---|---|---|---|
| BR-001 | MUST | PLATFORM_VIOLATION | gld_enr_poi_info | 1 append history row / (`poi_id`, `updated_at`) (known) | `poi_id`, `updated_at` (known) | DS-001, DS-002, DS-004, DS-005, DS-007, DS-009, DS-010, DS-011, DS-012 | COL-001, COL-003 to COL-010, COL-035 to COL-048 | RULE-003, RULE-004, RULE-006 | All facts are known or closed. `ID-003` and `ID-004` are known. Violations: PC-01 (schema `enr`), PC-03, PC-05 (business logic and partner `poi_id` in gold), PC-08, and PC-09. The flow-level PC-07 violation also applies |
| BR-002 | MUST | PLATFORM_VIOLATION | gld_enr_poi_coordinate | 1 append history row / (`poi_id`, `updated_at`) (known) | `poi_id`, `updated_at` (known) | DS-001, DS-002, DS-003, DS-005, DS-008 | COL-011 to COL-021 | RULE-005 | All facts are known or closed. Violations: PC-01 (schema `enr`), PC-03, PC-05 (gold source `SRC-008`, business logic in gold, and partner `poi_id` in gold), PC-08, and PC-09. The flow-level PC-07 violation also applies |
| BR-003 | MUST | PLATFORM_VIOLATION | gld_enr_poi_review | 1 append history row / (`review_id`, `updated_at`) (known) | `review_id`, `updated_at` (known) | DS-001, DS-007 | COL-022 to COL-025, COL-027, COL-031 to COL-034 | none | `COL-027` is known (`MQ-057`). `COL-022` and `COL-024` have a blank `src_id`, which is allowed (`MQ-058`), and their `reviewId` input is closed. `COL-025` `decimal(3,1)` is user-stated (`MQ-051`). `ID-001` and `ID-002` are known. Violations: PC-01 (schema `enr`), PC-05 (the `review_id` hash in gold), PC-08, and PC-09. The flow-level PC-07 violation also applies |

Mapped: 0 of 3. All three are blocked only by platform violations.

## 4. Rules and identifiers

| item_id | layer | rule_home_or_formula | status | basis |
|---|---|---|---|---|
| RULE-001 | silver_l2 | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | PLATFORM_VIOLATION | The statement matches `docs/context/01_DATA_MODEL.md §2`. The home is known through `MQ-054`. The row fails PC-03. No requirement lists it |
| RULE-003 | silver_l2 | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | PLATFORM_VIOLATION | The new rule is user-stated (`MQ-041`). The home is known through `MQ-054`. The row fails PC-03 |
| RULE-004 | silver_l2 | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | PLATFORM_VIOLATION | The rule is user-stated (`MQ-012`). The home is known through `MQ-054`. The row fails PC-03 |
| RULE-005 | silver_l2 | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | PLATFORM_VIOLATION | The rule is user-stated (`MQ-019`). The home is known through `MQ-054`. The row fails PC-03 |
| RULE-006 | silver_l2 | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` | PLATFORM_VIOLATION | The rule is user-stated (`MQ-053`). The home is known through `MQ-054`. The row fails PC-03 |
| ID-001 | gold (applies_to) | `HASH_SHA256(source_name, reviewId)` | PLATFORM_VIOLATION | A new identifier for a `PROPOSED` table (`MQ-020`, `BQ-009`). The `reviewId` input is closed. The hash is computed on a gold target, which fails PC-05 |
| ID-002 | gold (applies_to) | raw `reviewId` | KNOWN | User-stated (`MQ-021`, `BQ-010`). The `reviewId` input is closed |
| ID-003 | gold (applies_to) | `uuid_format(md5(concat(source_name, source_id)))` | KNOWN | Stated in `AGENTS.md §9` and `docs/context/01_DATA_MODEL.md §8`. It contains no language. Silver L1 `slv_3p_poi` already stores it (`TABLE_CONFIGS_3P`) |
| ID-004 | gold (applies_to) | `uuid_format(md5('partner_portal' ‖ business_service_id))` | PLATFORM_VIOLATION | Stated in `AGENTS.md §9` and `docs/context/01_DATA_MODEL.md §8`. It contains no language. Identity belongs to silver L2 N1 (`docs/context/01_DATA_MODEL.md §2`, `§6`), but `COL-001` and `COL-011` compute it on gold targets, which fails PC-05 |

## 5. Platform checks

| check | item_ids | result | basis |
|---|---|---|---|
| PC-01 | TRG-001, TRG-002, TRG-003, SRC-001 to SRC-005, SRC-009 to SRC-012 | PASS | Target names start with `gld_`. Silver L1 sources start with `slv_3p_` or `slv_pn_` (`docs/context/02_NAMING_CONVENTION.md §1`). The `gld_srv_` rename is out of scope (`SCOPE-004`, `BQ-007`) |
| PC-01 | SRC-006, SRC-008 | PASS | Legacy sources without a layer prefix stay unchanged until cutover (`docs/context/02_NAMING_CONVENTION.md §1`) |
| PC-01 | TRG-001, TRG-002, TRG-003 | PLATFORM_VIOLATION | `lakehouse_schema` is `lh_vv_gold.enr`, but `gold` maps to `lh_vv_gold.dbo`. The convention says not to create a new schema when the prefix already separates the tables (`docs/context/02_NAMING_CONVENTION.md §1`, OD-G11). The user kept `enr` (`MQ-024`, `BQ-007`) |
| PC-02 | TRG-001, TRG-002, TRG-003 | PASS | No target has `layer` `bronze` |
| PC-03 | RULE-001, RULE-003, RULE-004, RULE-005, RULE-006 | PLATFORM_VIOLATION | `TEMPLATE_EXCEPTION_NO_RULE_TABLE` does not start with `slv_poi_` or `ref_` (`docs/context/01_DATA_MODEL.md §2`, `docs/templates/BRD_TEMPLATE.md` section 7) |
| PC-04 | none | PASS | There is no silver L1 target and no silver L1 mapping row |
| PC-05 | all COL rows | PASS | `rule_ids`, `src_object`, `convert_rule`, and `key_order` are blank on every gold mapping row |
| PC-05 | COL-014, COL-016, SRC-008, DS-008 | PLATFORM_VIOLATION | The gold target `gld_enr_poi_coordinate` reads the gold source `lh_vv_gold.dbo.poi_address_enrichment_staging`. The rule is "gold không đọc gold khác" (`docs/context/01_DATA_MODEL.md §2`). Closing the physical facts does not clear this check |
| PC-05 | COL-003, COL-008, COL-012 to COL-019, COL-042, COL-043, COL-048, RULE-003, RULE-004, RULE-005, RULE-006 | PLATFORM_VIOLATION | The flow that writes gold applies business logic in these rows: source selection, the `coalesce` fallbacks, sector labels, the duration text, the templated `destination_context`, and the sort, limit, and truncation of `review_json`. The rule is gold "không xử lý nghiệp vụ" (`docs/context/01_DATA_MODEL.md §2`). Appending sources instead of joining them (`MQ-058`) does not change this |
| PC-05 | COL-001, COL-011, COL-022, ID-001, ID-004 | PLATFORM_VIOLATION | The partner `poi_id` and the new `review_id` hash are computed on gold targets. Identity belongs to silver L2 N1 (`docs/context/01_DATA_MODEL.md §2`, `§6`). `COL-023` is excluded because silver L1 already stores the 3rd-party `poi_id` |
| PC-06 | ID-001 to ID-004, COL-001, COL-011, COL-023 | PASS | No formula or key contains a language. No row uses `poi_uid`. `ID-005` was removed |
| PC-07 | FLOW-001 | PLATFORM_VIOLATION | `PL_VV_TRANS_SLV_TO_ENR_15P` does not follow `PL_VV_TRANSFORM_<FROM>_TO_<TO>_<SUFFIX>`, and `_15P` does not match `CADENCE_RE = _(\d+)([MHD])$` (`docs/context/02_NAMING_CONVENTION.md §3`). The row has `PROPOSED` and `[PROPOSED]` |
| PC-07 | FLOW-003 | PLATFORM_VIOLATION | `NB_00_ORCHES_<FROM>_TO_<TO>` is one shared orchestrator, and `p_pl_name` selects the flow (`docs/context/02_NAMING_CONVENTION.md §2`, `AGENTS.md §9`). `NB_00_ORCHES_SLV_TO_ENR_15P` is a flow-specific clone (`MQ-044`), and its suffix is outside the pattern. The row has `PROPOSED` and `[PROPOSED]` |
| PC-07 | FLOW-004, FLOW-005, FLOW-006 | PASS | The optional `nb_name` column of `pipeline_config` allows a node name other than `NB_<UPPER(trg_tbl)>` (`docs/context/02_NAMING_CONVENTION.md §2`). Each row has `PROPOSED` and `[PROPOSED]` |
| PC-08 | FLOW-002 | PLATFORM_VIOLATION | `APPEND` is not one of `CDC`, `DOC`, `DOC_ARRAY`, `LANG`, `LANG_ARRAY`, or `RECOMPUTE` (`docs/context/02_NAMING_CONVENTION.md §6`). The user kept it (`MQ-027`, `BQ-015`, `MQ-058`) |
| PC-09 | COL-009, COL-010, COL-020, COL-021, COL-033, COL-034 | PLATFORM_VIOLATION | In silver L2 and gold, `created_at` and `updated_at` are technical columns, and `updated_at` changes only when `row_hash` changes (`docs/context/02_NAMING_CONVENTION.md §5.2`). These rows give the names another meaning: both are set on every write (`MQ-030`, `MQ-052`), and `updated_at` is part of the history key (`MQ-039`). The write-time exception does not clear this check |
| PC-09 | other COL rows | PASS | No other business column reuses `row_hash`, `created_at`, `updated_at`, or `deleted_at` |

## 6. Gaps, conflicts, and missing evidence

None.

- Mapping sections 6 and 7 and BRD sections 11 and 12 have no filled rows.
- Every question in Mapping section 8 and BRD section 13 has an `answer` and an `answered_on` date.
- `AG-001` to `AG-012` are closed (section 2), and their IDs are not reused.
- No `MISSING_EVIDENCE`, `UNSUPPORTED_CITATION`, `CONFLICT`, or legacy-target question remains. No target is a legacy table.

| gap_id | blocks | missing_fact | kind | why_repo_cannot_answer | resolution_type | pass_fail_criterion |
|---|---|---|---|---|---|---|

## 7. Questions for the user

None. No gap needs `USER_ANSWER` or `EXTERNAL`, and no gap needs `PROBE` or `REPO_READ`.

| q_id | blocks | question | resolution_type |
|---|---|---|---|

The status is `USER_DECISION` because of the platform violations in section 5:

- PC-01: schema `enr`.
- PC-03: the rules have no `slv_poi_` or `ref_` home.
- PC-05: gold reads gold, business logic runs in gold, and identity hashes are computed in gold.
- PC-07: `FLOW-001` and `FLOW-003`.
- PC-08: `APPEND`.
- PC-09: the meaning of `created_at` and `updated_at`.

Only the user can accept these or change the requirements (`AGENTS.md §6` rule 10).

## 8. Handoff notes for Main

Not written. ANALYSIS_STATUS is USER_DECISION.
