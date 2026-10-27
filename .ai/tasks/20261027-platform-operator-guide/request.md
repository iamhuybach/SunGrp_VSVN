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
