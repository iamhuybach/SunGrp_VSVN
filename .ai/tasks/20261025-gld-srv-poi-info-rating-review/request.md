# Request

## User outcome

Bổ sung nghiệp vụ `gld_srv_poi_info`:

Nếu có poi_id thỏa mãn điều kiện slv_poi_entity_non_enrich.source_name = 'google' chỉ lấy khi poi_id có cả trong cả 2 bảng slv_enr_poi_destination và slv_enr_poi_info_multi_lang, left join với 2 bảng slv_3p_poi_rating và slv_3p_poi_review với logic sau:

- slv_3p_poi_rating.rating_overall, decimal(4,2), transform 1-1 → rating_overall
- slv_3p_poi_rating.rating_count, integer, transform 1-1 → rating_count
- slv_3p_poi_review, integer, count số lượng review theo poi_id → review_count

Khóa join của hai bảng mới là poi_id. Grain đích vẫn một dòng poi_id. MERGE vẫn theo poi_id.

Đã có trong repository, phải giữ, không viết lại:

- docs/context/mapping_gld_srv_poi_info.md §1.1 đã có rule Google giao hai bảng enriched và rule partner lấy full.
- notebooks/NB_GLD_SRV_POI_INFO.ipynb def:build đã lọc ~is_google | _both.

Việc mới là ba cột và hai nguồn left join. Partner và mọi dòng không khớp rating hoặc review để NULL. Không coalesce review_count thành 0. Không đổi rule operating_hours, is_recommended, hay các cột §1.2 hiện có.

## Scope

### In scope

- Three gold columns and two left joins: `rating_overall`, `rating_count`, `review_count`.
- `docs/context/mapping_gld_srv_poi_info.md` §1.2.
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` `OUT_COLS`, `SPEC.inputs`, and the build select.
- `notebooks/NB_CREATE_DDL.ipynb` and `notebooks/NB_SETUP_INITIAL_DDL.ipynb`: target DDL and the node input registry.
- `tests/test_gld_srv_poi_contract.py` for `gld_srv_poi_info`.

### Out of scope

- Rewriting the Google intersection rule or the partner-full rule in §1.1 or `build`.
- Changing `operating_hours`, `is_recommended`, or any current §1.2 column.
- Coalescing a missing `review_count` to 0.
- Choosing a `slv_3p_poi_rating` row when one `poi_id` has more than one row.
- A separate analysis task or a separate mapping task.

## Acceptance criteria

- source_name google, sau lower/trim như notebook hiện tại, chỉ còn khi poi_id có trong cả slv_enr_poi_destination và slv_enr_poi_info_multi_lang.
- Dòng partner vẫn lấy full.
- rating_overall và rating_count là transform 1-1 từ slv_3p_poi_rating; kiểu decimal(4,2) và integer.
- review_count là count review theo poi_id từ slv_3p_poi_review, kiểu integer; không có review thì NULL.
- Không match rating hoặc review không loại poi_id.
- slv_3p_poi_rating lệch grain 1 dòng / poi_id thì không tự chọn dòng; dừng để probe hoặc quyết định.
- DDL bảng đích, OUT_COLS, mapping §1.2, contract test và registry input của node cùng một bộ cột.
- File mapping (`docs/context/mapping_gld_srv_poi_info.md`), NB_CREATE_DDL và NB_SETUP_INITIAL_DDL cùng được cập nhật.

## Constraints

- One task: TRIAGE → EVIDENCE if required → model-design → ARCHITECTURE → IMPLEMENT → LOCAL VERIFY → REVIEW.
- Do not edit the notebook before architecture PASS.
- `data_model_change` is set because gold columns are added. Before the architecture `run-gate`, write `handoffs/author-input.md` and run `python scripts/vv.py run-author <task-id> --kind model`.
- Evidence is required when the repository does not prove that `slv_3p_poi_rating` has one row per `poi_id`.
- Architecture is required. No fast lane.
- A deviation from the Main brief is recorded in `decision.md` before code changes.
- Save `FILE:` blocks with `python scripts/vv.py materialize <task-id> --write`.
- Task `20261024-gld-srv-poi-from-mapping` is `ready_to_merge` and is not still editing `NB_GLD_SRV_POI_INFO`, so this work is a new task.

## Classification rationale

- Complexity: `medium`. Signals: `data_model_change`, `data_evidence_required`, `runtime_proof_required`. The target grain and MERGE key stay `poi_id`. The change adds columns, two left joins, a review count, DDL, registry inputs, mapping §1.2, and the contract test. That is a behavior change across more than two files, so it is not `low` and not a fast lane.
- Risk: `medium`. The behavior change is bounded to three additive columns and left joins. Rollback is reverting the notebook and dropping those columns. No new lock, watermark, or retry design.
- Architecture: required. The user forbids the fast lane. A rating grain other than one row per `poi_id` would multiply the MERGE source. `data_model_change` also requires `model-design.md` before `run-gate`.
- Evidence: required. `docs/context/01_DATA_MODEL.md` §5.2 and the 3rd-party registry in both DDL notebooks declare `slv_3p_poi_rating` as `DOC` with key `poi_id`, `rating_overall` `decimal(4,2)`, and `rating_count` `bigint`. `slv_3p_poi_review` is `DOC_ARRAY` with key `review_id`, so many reviews per `poi_id` is the declared shape. Neither DDL notebook creates a UNIQUE constraint, and the repository has no measured row count. Declared key is not proof of current cardinality.
- Runtime proof: required after implementation. Local tests can align columns; the live left joins need a Fabric DEV run of the gold node.
- Reviewer routing: `sql-data-reviewer` (join, count, types, MERGE-source grain), `spark-runtime-reviewer` (notebook contract and Delta DDL), `fabric-pipeline-reviewer` (new `ctrl_mng_pipeline_config` inputs change what triggers `NB_GLD_SRV_POI_INFO`). No `state-correctness-reviewer`: lock, watermark, and retry stay on the existing `run_node` path. No `risk-gate`: risk is `medium`.
