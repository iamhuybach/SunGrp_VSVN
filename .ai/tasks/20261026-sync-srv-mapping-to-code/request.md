# Request

## User outcome

The four serving mapping files describe the current notebooks, and the same task updates each file before review whenever that table's business logic changes.

Verbatim request:

Kiểm tra các file mapping đã khớp với code chưa. Nếu chưa hãy cập nhật lại. Ngoài ra sau mỗi lần xử lý nghiệp vụ của các bảng tương ứng, phải update lại các file này để có context phục vụ cho sau này:

- docs/context/mapping_gld_srv_poi_amenity.md
- docs/context/mapping_gld_srv_poi_info.md
- docs/context/mapping_gld_srv_poi_multi_lang.md
- docs/context/mapping_poi_media_info.md

Lý do nghiệp vụ: bốn file này là context cho lần sửa sau. Chúng phải mô tả đúng code hiện tại, và cùng task phải sửa lại chúng mỗi khi nghiệp vụ của bảng tương ứng đổi.

## Scope

### In scope

- docs/context/mapping_gld_srv_poi_amenity.md
- docs/context/mapping_gld_srv_poi_info.md
- docs/context/mapping_gld_srv_poi_multi_lang.md
- docs/context/mapping_poi_media_info.md
- docs/AGENT_PROMPT_SAMPLES.md, bảng Bản đồ context, one row for these four files

Read-only comparison sources:

- notebooks/NB_SLV_POI_AMENITY.ipynb
- notebooks/NB_GLD_SRV_POI_AMENITY.ipynb
- notebooks/NB_SETUP_POI_AMENITY.ipynb
- notebooks/NB_GLD_SRV_POI_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb
- notebooks/NB_SLV_POI_MEDIA_INFO.ipynb
- notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb
- tests/test_poi_amenity_contract.py
- tests/test_gld_srv_poi_contract.py
- DDL and registry, read only

### Out of scope

- Editing notebooks, DDL, pipelines, or tests to match an older mapping file.
- AGENTS.md, rules, skills, and vv.py.
- Other tasks, notebooks_lgc/, and pipeline manifests.
- docs/templates/MAPPING_TEMPLATE.md conversion.
- data_model_change, Fabric probes, and a runtime runbook.

## Acceptance criteria

- Each mapping file matches its source notebook on grain, MERGE key, inputs, joins, filters, OUT_COLS, types, pipeline, and load_mode. Code is the source of truth.
- Where the notebook does not state a fact, write MISSING. Do not add a rule, coalesce, or branch that the notebook does not have.
- Keep each file's existing section names. Do not convert them to docs/templates/MAPPING_TEMPLATE.md.
- The first line of each mapping file states that the same task updates this file before review after every business-logic change to the table in the file.
- docs/AGENT_PROMPT_SAMPLES.md, bảng Bản đồ context, has one row for these four files and the same obligation sentence.

## Constraints

- Do not signal data_model_change. Do not probe Fabric.
- Run architecture only when §Classification requires it. The diff is markdown only.
- Do not mark runtime pass.

## Classification rationale

- Complexity: low. No complexity signal applies. The task does not change a table, column, grain, or key, so `data_model_change` is not set.
- Risk: low. No runtime behavior change. The edit is a narrow documentation alignment that local inspection can prove.
- Architecture: not required. Grain, keys, state ownership, commit order, layer placement, CDC, watermark, locking, retry, and orchestration stay as the notebooks already implement them. There is one implementation, the current code. The change is five markdown files, not three services and not eight source files.
- Evidence: not required. Correctness is repository inspection of the named notebooks and the named contract tests.
- Runtime proof: not required. No Fabric execution.
- Reviewer routing: not the fast lane. Fast lane needs low complexity, low risk, no behavior change, and at most two changed files. This task changes five files. `sql-data-reviewer` because the files state grain, MERGE keys, joins, filters, and column types of the gold SQL. `spark-runtime-reviewer` because the files state notebook `OUT_COLS` and `load_mode` contracts. No `state-correctness-reviewer`: no CDC, watermark, lock, or retry change. No `fabric-pipeline-reviewer`: pipeline JSON is unread and out of scope. No risk gate: risk is low.
