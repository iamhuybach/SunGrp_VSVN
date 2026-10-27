# Architect handoff: 20261027-platform-operator-guide

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author 20261027-platform-operator-guide --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/20261027-platform-operator-guide/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

The first non-blank line is `RESULT: PASS` or `RESULT: EVIDENCE_REQUIRED`. Cover: scope, non-goals, invariants, state ownership, grain and keys, ordering, transaction and commit boundaries, idempotency, concurrency, retry and recovery, partial failure, observability, security, rollout, rollback and forward recovery, implementation plan, and verification. Compare material alternatives and explain the selected trade-off. Write a section that does not apply as one line: `Not applicable: <reason>`.

Size: for `low` or `medium` risk, keep the document under 25 KB, excluding `FILE:` blocks. For `high` or `critical` risk, use the space the failure analysis needs, without repeating the request or the evidence.

Files that Main must save verbatim go in blocks: a line `FILE: <repo-relative path>`, the exact content, then a line `END_FILE`. Every path must be in `scope.files`.

## Main brief contract

Return a separate Main brief, at most 14,000 characters, in English. It is the only part Main reads by default. Use `###` headings only, in this order:

1. `Decision`: at most 5 lines.
2. `Invariants Main must preserve`: at most 10 testable bullets.
3. `Edit list`: table `# | file | anchor (cell id, function, or heading) | change | done-when`, one row per anchor.
4. `Order and stop points`: numbered; mark each stop for evidence or a user decision.
5. `Tests and verification`: exact test names and commands.
6. `Read only if needed`: full-document headings mapped to the edit rows they justify.

Do not restate the request or the evidence in the brief. Code longer than 15 lines goes in the full document under a heading the edit list references.

If evidence is missing, list exact probes and the decisions each one blocks. Do not implement code, update task state, or fill gaps with assumptions.

## Generated context pack

`vv.py` generated this block. Do not re-read the task state, request, decision ledger, or task file list it covers.

# Context 20261027-platform-operator-guide | phase=triage

## STATE

id: 20261027-platform-operator-guide
title: Platform operator guide and data-model skills
status/owner: waiting_architecture/architect
complexity/risk: medium/low
required: architecture_required=True, evidence_required=False, runtime_required=False
signals: design_tradeoffs
gates: evidence=not_required, architecture=pending, local_verification=pending, specialist_review=pending, risk_gate=not_required, runtime=not_required
rounds: verification=0, review=0, architecture=0, runtime_failure=0
reviewers: sql-data-reviewer, spark-runtime-reviewer
open findings: none
exceptions: none
scope.files:
- docs/context/03_OPERATOR_GUIDE.md
- .cursor/skills/vsvn-operator-docs/SKILL.md
- .cursor/skills/vsvn-data-model-flow/SKILL.md
- docs/AGENT_PROMPT_SAMPLES.md
- docs/context/CTRL_TABLES_CONTEXT.md
- docs/context/02_NAMING_CONVENTION.md
- docs/context/01_DATA_MODEL.md
- docs/context/00_README.md
- docs/context/NB_00_ORCHES_SLV_TO_GLD.md
- docs/context/NB_LIB_TRANSFORM_SLV_GLD.md
- docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md
- .cursor/skills/vsvn-notebook-library/SKILL.md
- AGENTS.md
- notebooks/NB_00_ORCHES_SLV_TO_ENR.ipynb
- notebooks/NB_SETUP_INITIAL_DDL.ipynb
- notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb

## VALIDATION

PASS

## RESUME

# Resume

Status: user_decision. Architecture has not run. Skills are not written. Runtime is not pass.

Done this session: classified `20261027-platform-operator-guide` as an agent-system change (`design_tradeoffs` only, no `data_model_change`). Wrote `docs/context/03_OPERATOR_GUIDE.md` with five sections. Recorded skill procedures and three public skill sources in `decision.md`. Did not edit notebooks, DDL, pipelines, tests, rules, `AGENTS.md`, or `vv.py`.

Next action: after the user answers the four CONFLICT questions, update the marked rows in the guide, write `handoffs/author-input.md`, transition to `waiting_architecture`, and run `python scripts/vv.py run-gate 20261027-platform-operator-guide`.

Read next: `docs/context/03_OPERATOR_GUIDE.md` §1.7 and §5.3; `decision.md` D4 and D5.

Waiting on: user choice for the enrich notebook name, enrich `p_pl_name`, partner `event_hash` formula, and 3rd-party `after_payload` wording.

## REQUEST

# Request

## User outcome

Dựa vào context và model hiện tại, cho một tài liệu đầy đủ các thông tin sau (bỏ qua phần model cũ, cụ thể ở notebooks_lgc):

1. Thông tin, ý nghĩa của các bảng ctrl và các fields trong bảng; các fields nào là required. Thiết kế dạng bảng để dễ nhìn.
2. Hình vẽ data lineage (cấp độ table) cho các bảng ở gld (cả schema dbo và enr). Không cần chi tiết field, nhưng mô tả được quan hệ (inner join/left join/append/...) giữa các bảng nguồn để ra bảng đích.
3. Step by step khi cần thêm một field mới ở bronze → silver (cấu hình, cấu hình bắt buộc, chạy khi cần init lại, chạy khi không cần init, câu lệnh đi kèm, lưu ý).
4. Step by step khi cần thêm một bảng mới ở bronze → silver (cùng các mục như phần 3).
5. Thông tin, ý nghĩa tham số (tham số nào bắt buộc) của các NB sau; cấu hình cần thiết và bắt buộc; cách reuse; sub-notebook cần gì để chạy với Notebook Orches (kèm một khung sub-notebook sample):
   - NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV
   - NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV
   - NB_00_ORCHES_SLV_TO_ENR
   - NB_00_ORCHES_SLV_TO_GLD

Build skill cho việc doc những tài liệu này và skill cho việc gen data model, data flow. Trong quá trình xử lý task này, bổ sung thêm thông tin và kỹ năng cho skill để sau tận dụng được. Skill mới có thể tham khảo những skill liên quan được đánh giá cao trên nguồn công khai.

Lý do nghiệp vụ: một tài liệu vận hành, cộng hai skill để lần sau viết lại loại tài liệu này và sinh data model cùng data flow từ hiện trạng, không phải từ model cũ.

## Scope

### In scope

- `docs/context/03_OPERATOR_GUIDE.md` with the five sections above, in that order.
- `.cursor/skills/vsvn-operator-docs/SKILL.md`
- `.cursor/skills/vsvn-data-model-flow/SKILL.md`
- One new row in the context map of `docs/AGENT_PROMPT_SAMPLES.md` pointing at the two skills and `03_OPERATOR_GUIDE.md`.
- Task ledger, `handoffs/author-input.md`, and architecture for the skills.

### Out of scope

- Edits to notebooks, DDL, pipelines, tests, rules, `AGENTS.md`, or `scripts/vv.py`.
- `notebooks_lgc/` and `docs/context/01_DATA_MODEL.md` §9.
- Fabric DEV probes and runtime proof.
- Signal `data_model_change` and `run-author --kind model`.
- `model_override` or any `exceptions` entry.
- Commit.

## Acceptance criteria

- `docs/context/03_OPERATOR_GUIDE.md` has all five sections, in order. Prose is Vietnamese. Table names, columns, parameters, and commands stay English.
- Two project skills use the same frontmatter style as the four skills in `.cursor/skills/`:
  - `.cursor/skills/vsvn-operator-docs/SKILL.md` — write and update this kind of operator document (ctrl, gold lineage, adding a bronze-to-silver field or table, notebook parameter contracts).
  - `.cursor/skills/vsvn-data-model-flow/SKILL.md` — generate a table-level data model and data flow from current DDL and notebooks.
- A skill contains only reusable procedure and paths to sections in the guide or context. It does not copy ctrl tables, lineage diagrams, or column lists into `SKILL.md`.
- Every required row, lineage edge, command, and required parameter in the guide cites a file and a section or cell. If it is not found, write `MISSING`. If two sources disagree, write `CONFLICT`, record the question, and stop at `user_decision`.
- `python scripts/vv.py doctor` has no budget `WARN`.
- Skill descriptions are short enough for that budget. Each description states what the skill does, when to use it, and when not to use it. `vsvn-operator-docs` is not for editing notebooks or DDL. `vsvn-data-model-flow` is not for `notebooks_lgc/` and is not for changing grain, keys, or columns.
- Do not mark the runtime gate pass.

## Constraints

- Required ctrl columns are the `NOT NULL` columns in DDL plus `ConfigError` conditions in the library.
- Lineage covers gold tables in schemas `dbo` and `enr` only. Relationship type comes from the join or union in the build cell. A gold table that has DDL but no node notebook is recorded as having no node.
- Re-init means `NB_SETUP_INITIAL_DDL` for an empty environment. No re-init means `NB_CREATE_DDL` patching an existing environment. A command that is not in the repository is `MISSING`.
- The sub-notebook frame lives in the guide and follows `NB_LIB_TRANSFORM_SLV_GLD` §5. Do not add an `.ipynb` file.
- The data-model skill describes the current state only. It does not design a new model and does not call `run-author --kind model` for that.
- Public skill references: public sources only. Record in `decision.md` the skill name, the source, and the structural technique used (a description with WHAT and WHEN, a short procedure, detail in a separate file). Do not copy an external `SKILL.md` verbatim into the repo. VSVN facts come only from the Context files.
- Main stays Grok 4.7 Medium. No `model_override`.
- Do not write the two `SKILL.md` files before architecture `PASS`. Save architecture `FILE` or `SKILL_FILE` blocks with `python scripts/vv.py materialize <task-id> --write`.
- New facts found while editing the guide, if the skill still lacks that procedure, go in `decision.md` and then into the skill as procedure only.
- Stop before commit. Stop on `CONFLICT` that needs a decision, a gate or model failure or fallback, or a round cap. Overwrite `resume.md` before stopping.

## Classification rationale

- Complexity: medium. The change adds an operator guide, two skills, and one context-map row across ctrl, both extracts, both libraries, gold and enr nodes, and DDL. That is more than a two-file fast lane.
- Risk: low. No notebook, DDL, pipeline, or test behavior changes.
- Architecture: required. This is an agent-system change because it adds skills (sample A18). The boundary between reusable procedure and copied tables is a design trade-off (`design_tradeoffs`). Skills are written only after architecture `PASS`.
- Evidence: not required. Correctness comes from repository inspection. No Fabric probe.
- Runtime proof: not required.
- Reviewer routing: `sql-data-reviewer` for table-level join and union claims; `spark-runtime-reviewer` for notebook parameter and orchestration contracts. No `fabric-pipeline-reviewer` because pipeline JSON is out of scope. No `data_model_change` signal.


## DECISIONS

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Phân loại | Thay đổi agent-system vì có skill. `complexity=medium`, `risk_level=low`, `architecture_required=true`, không evidence, không runtime. Signal chỉ `design_tradeoffs`. Không `data_model_change`. Không `model_override`. Main `grok-4.7` / `medium`. | `request.md` Classification rationale | 2026-10-27 |
| D2 | Required ctrl | Required = cột `NOT NULL` trong `NB_SETUP_INITIAL_DDL` cell 3 cộng `ConfigError` trong lib. Cell 3 không có `NOT NULL` trên cột ctrl. Không dùng mục "Dữ liệu hiện có". | `03_OPERATOR_GUIDE.md` §1 | 2026-10-27 |
| D3 | Lineage hiện hành | Bảng gold hiện hành là `fq` trong `TABLE_SPECS` của `NB_SETUP_INITIAL_DDL` cell 3. Kiểu cạnh lấy từ `join` / `union` trong cell `build`. `gld_enr_poi_coordinate` không có trong `TABLE_SPECS` và không có notebook node, nên không vẽ cạnh. | `03_OPERATOR_GUIDE.md` §2 | 2026-10-27 |
| D4 | Tên enrich | Notebook là `NB_00_ORCHES_SLV_TO_ENR`. Pipeline là `PL_VV_TRANS_SLV_TO_ENR_15M`. Không có `PL_VV_TRANS_SLV_TO_ENR_30P`. Activity JSON vẫn tên `NB_00_ORCHES_SLV_TO_ENR_15P`. | Người dùng 2026-10-27; `03_OPERATOR_GUIDE.md` §5.3 | 2026-10-27 |
| D5 | Hash và payload | Hash partner đang chạy là `sha2(concat_ws U+0001, coalesce(_source,_op,_before,_after), 256)` ở cell 6 `reject_rows`. `after_payload` 3rd-party lấy `normalized_payload`. | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` cell 6; `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` hằng `RAW_PAYLOAD` | 2026-10-27 |
| D6 | Skill sau architecture | Chưa viết hai `SKILL.md`. Quy trình sẽ đưa vào skill nằm ở lịch sử, không chép bảng ctrl hay sơ đồ. | mục Lịch sử quyết định | 2026-10-27 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## ARCHITECTURE

RESULT: missing
size: 483 bytes

## FILES

- architecture.md | 483 bytes | placeholder
- decision.md | 5504 bytes
- evidence/plan.md | 383 bytes | placeholder
- evidence/probes/README.md | 175 bytes | placeholder
- handoffs/author-input.md | 2903 bytes
- request.md | 6569 bytes
- resume.md | 957 bytes
- reviews/README.md | 157 bytes | placeholder
- runtime-runbook.md | 456 bytes | placeholder
- task-state.yaml | 2009 bytes

## NEXT

python scripts/vv.py run-gate 20261027-platform-operator-guide

## Large scope files

Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a notebook function name or cell id.

### docs/context/03_OPERATOR_GUIDE.md (42682 bytes)

# Hướng dẫn vận hành nền tảng | L1-L509
## 1. Bảng ctrl | L5-L171
### 1.1 `ctrl_mng_pipeline_config` | L9-L31
### 1.2 `ctrl_mng_watermark` | L32-L55
### 1.3 `ctrl_cfg_schema_registry` | L56-L78
### 1.4 `ctrl_log_run` | L79-L106
### 1.5 `ctrl_log_table_run` | L107-L131
### 1.6 `ctrl_cdc_state` | L132-L148
### 1.7 `ctrl_cdc_reject` | L149-L171
## 2. Data lineage gold | L172-L299
### 2.1 `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | L228-L237
### 2.2 `lh_vv_gold.dbo.gld_srv_poi_info` | L238-L251
### 2.3 `lh_vv_gold.dbo.gld_srv_poi_media_gallery` | L252-L255
### 2.4 `lh_vv_gold.dbo.gld_srv_poi_amenity` | L256-L259
### 2.5 `lh_vv_gold.dbo.gld_srv_poi_review` | L260-L271
### 2.6 `lh_vv_gold.enr.gld_enr_poi_info` | L272-L290
### 2.7 `lh_vv_gold.enr.gld_enr_poi_review` | L291-L299
## 3. Thêm một field bronze sang silver | L300-L351
### 3.1 Cấu hình | L304-L309
### 3.2 Cấu hình bắt buộc | L310-L323
### 3.3 Chạy khi cần init lại | L324-L334
### 3.4 Chạy khi không cần init | L335-L344
### 3.5 Lưu ý | L345-L351
## 4. Thêm một bảng bronze sang silver | L352-L392
### 4.1 Cấu hình | L356-L364
### 4.2 Cấu hình bắt buộc | L365-L375
### 4.3 Chạy khi cần init lại | L376-L379
### 4.4 Chạy khi không cần init | L380-L385
### 4.5 Lưu ý | L386-L392
## 5. Tham số notebook | L393-L509
### 5.1 `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | L397-L421
### 5.2 `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` | L422-L444
### 5.3 `NB_00_ORCHES_SLV_TO_ENR` | L445-L452
### 5.4 `NB_00_ORCHES_SLV_TO_GLD` | L453-L509

### docs/context/CTRL_TABLES_CONTEXT.md (46957 bytes)

# CTRL_TABLES_CONTEXT — 7 bảng control `lh_vv_ctrl.dbo` | L1-L582
## 1. Tổng quan | L7-L24
## 2. Quan hệ | L25-L48
## 3. `ctrl_mng_pipeline_config` | L49-L151
### DDL | L54-L73
### Cột | L74-L89
### Dữ liệu hiện có | L90-L141
### Thao tác thường gặp | L142-L151
## 4. `ctrl_mng_watermark` | L152-L244
### DDL | L162-L186
### Cột theo loại dòng | L187-L211
### Ghi chú migration — số đo watermark trước 08/10 tại `lh_vv_bronze.ctrl` (dòng 3P cũ `wm_transform_poi_raw_event`) | L212-L220
### Thao tác thường gặp | L221-L244
## 5. `ctrl_cfg_schema_registry` | L245-L334
### DDL | L250-L274
### Luật cấu hình (lib kiểm tra, sai → `ConfigError` trước khi ghi) | L275-L285
### Dữ liệu hiện có (seed `NB_CREATE_DDL`, cấu hình chốt 04/10 chiều) | L286-L334
## 6. `ctrl_log_run` — 1 dòng / lần chạy notebook (khoá `exec_id`) | L335-L405
### DDL | L339-L379
### Cột khác nghĩa giữa extract và NB_00 | L380-L394
### Ghi chú migration — log đã thấy trước 08/10 tại vị trí control cũ | L395-L405
## 7. `ctrl_log_table_run` — 1 dòng / bảng đích (hoặc node) / lần chạy | L406-L461
### DDL | L408-L461
## 8. `ctrl_cdc_state` — 1 dòng / entity / bảng đích (chỉ extract) | L462-L501
### DDL | L466-L501
## 9. `ctrl_cdc_reject` — 1 dòng / event (hoặc phần tử) lỗi (chỉ extract) | L502-L555
### DDL | L504-L555
## 10. Lịch sử thay đổi (tóm tắt) | L556-L572
## 11. Việc còn lại liên quan ctrl | L573-L582

### docs/context/01_DATA_MODEL.md (35724 bytes)

# 01 — Data Model mới của Visit Vietnam (POI) trên Microsoft Fabric | L1-L404
## 1. Bối cảnh nền tảng | L7-L18
## 2. Nguyên tắc phân tầng (đã chốt) | L19-L35
## 3. Sơ đồ tổng | L36-L75
## 4. Bronze — bảng raw | L76-L253
### Cấu trúc `normalized_payload` | L86-L253
## 5. Silver L1 — extract (đúng cấu trúc nguồn) | L254-L318
### 5.1 Partner `slv_pn_*` (23 bảng, `load_mode = CDC`) | L256-L289
### 5.2 3rd-party `slv_3p_poi_*` (9 bảng trong registry, 9 active, snapshot) | L290-L318
## 6. Silver L2 — tích hợp POI (7 node) | L319-L348
### 6.1 Bảng ref (rule dạng dữ liệu) | L335-L348
## 7. Gold hiện hành (`lh_vv_gold.enr`) | L349-L359
## 8. Định danh | L360-L372
## 9. Model cũ (vẫn chạy song song) và lý do đổi | L373-L382
## 10. Ý nghĩa của model mới | L383-L392
## 11. Hướng sắp tới (chưa làm) | L393-L404

### docs/context/NB_LIB_TRANSFORM_SLV_GLD.md (21491 bytes)

# NB_LIB_TRANSFORM_SLV_GLD — Thư viện luồng tính lại silver → silver L2 → gold | L1-L221
## 1. Mô tả | L6-L21
## 2. Ý nghĩa / mô hình | L22-L36
## 3. Cấu trúc | L37-L49
## 4. Chi tiết hàm | L50-L180
### §1 constants | L52-L71
### §2 common | L72-L86
### §3 delta | L87-L97
### §4 config / DAG | L98-L107
### §5 ctrl | L108-L125
### §6 node | L126-L152
### §7 orchestrator | L153-L165
### §8 build helpers (dùng trong `build` của node) | L166-L180
## 5. Hợp đồng notebook node | L181-L203
## 6. Bảo đảm | L204-L216
## 7. Kiểm thử và việc còn mở | L217-L221

### notebooks/NB_SETUP_INITIAL_DDL.ipynb (226470 bytes)

[0] markdown id=init_md json=unknown lines=7 | NB_SETUP_INITIAL_DDL | defs: none
[1] code id=init_param json=unknown lines=1 | p_apply = "false" | defs: none
[2] code id=init_run json=unknown lines=1 | %run NB_LIB_TRANSFORM_SLV_GLD | defs: none
[3] code id=init_tables json=unknown lines=501 | PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCo | defs: _q, create_sql, schema_diff
[4] code id=init_cfg_partner json=unknown lines=535 | TABLE_CONFIGS = [ | defs: none
[5] code id=init_cfg_3p json=unknown lines=184 | _S = "lh_vv_silver.dbo" | defs: _str, _bool, _off
[6] code id=init_registry_pure json=unknown lines=139 | import re | defs: resolve_type, flatten_table_configs, validate_rows
[7] code id=init_seed_ctrl json=unknown lines=90 | _FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_ | defs: none
[8] code id=init_seed_place_type json=unknown lines=455 | import re | defs: validate_seed
[9] code id=init_seed_amenity json=unknown lines=262 | import re | defs: amenity_keys, validate_seed
[10] code id=init_plan json=unknown lines=144 | import json | defs: _missing, _dup_keys, _target_dup_keys
[11] code id=init_ddl json=unknown lines=20 | def _create_enr_schema(): | defs: _create_enr_schema, _create
[12] code id=init_seed_write json=unknown lines=180 | PC_FQ = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" | defs: _merge_pipeline_config, _merge_watermark, _merge_registry, _merge_place_type, _merge_amenities, _apply_seed
[13] code id=init_verify json=unknown lines=30 | verify_errors = [] | defs: none
[14] code id=init_exit json=unknown lines=7 | summary = { | defs: none

### notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb (57033 bytes)

[0] markdown id=df470ac8 json=3-44 lines=35 | NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV | defs: none
[1] code id=f6c1e91a json=45-78 lines=17 | pl_name                 = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"   # @pipeline | defs: none
[2] code id=d65c3085 json=79-93 lines=1 | %run NB_LIB_EXTRACT_RAWDATA | defs: none
[3] markdown id=56ba9f07 json=94-109 lines=9 | Hằng số Debezium | defs: none
[4] code id=309d4772 json=110-149 lines=26 | import uuid                                  # [03/10 → LIB] bỏ import traceback | defs: none
[5] markdown id=a4b868e6 json=150-165 lines=9 | A. Đọc và phân loại raw | defs: none
[6] code id=f68e3e2a json=166-318 lines=139 | def objects_cond(objects) -> Column: | defs: objects_cond, read_raw, classify_events, blank, profile_events, reject_rows, as_col
[7] markdown id=0067281b json=319-337 lines=12 | B. Xử lý 1 bảng: parse → lọc event cũ theo state → gộp TOAST → MERGE | defs: none
[8] code id=c237e0de json=338-581 lines=230 | def build_table_events(spec: TableSpec, valid_df: DataFrame, state_df: Optional[ | defs: build_table_events, raw_value, typed_value, cast_null_flag, unavailable_flag, table_stats, as_int, resolve_latest, build_merge_sql, merge_into_target, _run_table, process_table
[9] markdown id=40f29bf9 json=582-597 lines=9 | C. Chạy theo wave và commit | defs: none
[10] code id=3ad7e33c json=598-657 lines=46 | def run_waves(specs: list, profile: Profile, valid_df: DataFrame, state_df: Opti | defs: run_waves, target_of, commit_rejects, commit
[11] markdown id=412f2266 json=658-669 lines=5 | Main | defs: none
[12] code id=2a32b2a0 json=670-757 lines=71 | def build_context() -> RunContext: | defs: build_context, process_run, run_extract
[13] code id=b01a9ea0 json=758-781 lines=10 | _summary_json = json.dumps(RUN_SUMMARY, ensure_ascii=False, default=str) | defs: none
[14] markdown id=9e922ec6 json=782-838 lines=50 | Vận hành | defs: none
