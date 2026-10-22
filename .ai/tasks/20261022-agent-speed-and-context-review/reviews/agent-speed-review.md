# Agent speed and context review

Task: `20261022-agent-speed-and-context-review`. Phiên khảo sát: Claude Code, model `claude-fable-5-1`, effort `medium` (EXC-01). Chỉ đọc. Không chạy `python scripts/vv.py`, không commit. Ngày: 2026-10-22.

Phạm vi đọc: `request.md`, ledger `decision.md`, `AGENTS.md`, `CLAUDE.md`, `SETUP.md`, `docs/agent-system/WORKFLOW.md` (§Classification, §Review routing, Phases and context budgets), `docs/AGENT_PROMPT_SAMPLES.md`, `.ai/prompts/*.md`, `.cursor/rules/*.mdc`, phần kích hoạt và phần bắt đọc của `.cursor/skills/*/SKILL.md`, `.claude/agents/requirements-analyst.md` (frontmatter và Identity), `.codex/config.toml`, `.codex/agents/*.toml` (model, effort, vai), hằng số của `scripts/agent_runner.py`, phần dựng prompt và `run-gate` của `scripts/vv.py`, `docs/context/00_README.md` và các mục liên quan của `01_DATA_MODEL.md`, `02_NAMING_CONVENTION.md`, `CTRL_TABLES_CONTEXT.md`, `99_PAIN_POINTS.md` §0, `NB_*.md`. Việc hàng ngày: `request.md` (phần yêu cầu) và `task-state.yaml` của 13 task từ `20261016` đến `20261022`, cùng header `reviews/round-N.md` và `round-N.json`. Notebook đối chiếu bằng table of contents cell và grep, không đọc cả file.

Giới hạn: repository không ghi thời gian chạy của bất kỳ lượt model nào (`agent_runner.py` chỉ có `timeout_seconds`, `round-N.json` chỉ có verdict, findings, SHA-256). Mọi nhận định về tốc độ dưới đây đo bằng số process model và độ dài đầu vào, không phải giây. `NB_ENR_POI_COORDINATE.ipynb` không còn trong `HEAD` và không có trong working tree, nên không đối chiếu được; context nhắc tới nó được coi là lệch.

## 1. Kết luận

1. Việc hàng ngày từ 16/10 là 13 task, 11 task đi đủ ba lane Main, Architect, Codex review. Lane Author chỉ dùng `--kind model` (5 task) và `--kind runbook` (7 task). `--kind analysis`, `--kind proposal` và Requirements Analyst không chạy lần nào.
2. Chi phí nằm ở Codex review: 26 vòng review cho 11 task, mỗi vòng 5 đến 6 process (coordinator, 3 đến 4 specialist, risk-gate). 7 vòng trong số đó trả 0 finding nhưng vẫn chạy đủ manifest. 5 trong 11 task cần vòng 3 qua `extra_round_approved_on`, nên cap 2 vòng không còn là cap.
3. Lượt dài nhất là Architect: Opus `high`, tối đa 80 turn, đọc notebook 50 đến 200 KB qua TOC, trả `architecture.md` 35 đến 69 KB. 3 task chạy Architect 2 vòng, và vòng 2 không nhận bản vòng 1 trong context pack.
4. Timeout 1800 giây là trần chung cho Architect, Author và Codex. Không có số đo nên không biết lượt nào chạm trần; đề xuất ghi `elapsed_seconds`.
5. `docs/context` lệch notebook ở phần gold và luồng 15 phút: tài liệu vẫn mô tả `gld_srv_*` tại `lh_vv_gold.dbo` và `NB_00_ORCHES_SLV_TO_GLD`, trong khi repo chạy `gld_enr_*` tại `lh_vv_gold.enr` qua `NB_00_ORCHES_SLV_TO_ENR_15P`. Số bảng 3P, tham số extract, danh sách caller của lib, và mode `APPEND` cũng lệch.
6. Không đề xuất đổi model ID hay effort. Đề xuất 15 mục sửa, 13 mục là tài liệu và skill, 2 mục là `AGENTS.md`/`CLAUDE.md` và `scripts/vv.py`.

## 2. Việc hàng ngày đang đi những lane nào

Nguồn: `task-state.yaml` và `reviews/` của 13 task từ `20261016` đến `20261022`; commit log từ 16/10 (14 commit, 1 đến 5 commit/ngày).

| Lane | Task dùng / 13 | Lượt (process model) | Ghi chú |
|---|---|---|---|
| Main (Cursor, Grok 4.7 medium) | 13 | mọi phase | 1 chat/phase; triage, probe, implement, remediate, runtime, closeout |
| Architect (`run-gate` ở `waiting_architecture`) | 11 | 14 lượt | 3 task 2 vòng: `20261016-setup-initial-ddl-and-patch-ddl`, `20261019-agent-system-claude-opus-design`, `20261021-refresh-gld-enr-poi-info` |
| Author `--kind model` | 5 | 5 lượt | các task có signal `data_model_change` |
| Author `--kind runbook` | 7 | 7 lượt | `runtime-runbook.md` không phải template |
| Author `--kind analysis` / `--kind proposal` | 0 | 0 | `models.author_proposal.actual` rỗng ở mọi task |
| Requirements Analyst | 0 | 0 | không có `requirements-analysis.md` nào từ 16/10 |
| Codex review (`run-gate` ở `reviewing`) | 11 | 26 vòng, ước 130 đến 150 process | mỗi vòng = coordinator + specialist (2 đến 4) + risk-gate khi risk `high` |
| Codex `requirements-reviewer` | 0 | 0 | không nằm trong `run-gate` |

Vòng review theo task: 2, 2, 2, 2, 3, 2, 3, 3, 0, 3, 3, 0, 1. Vòng trả 0 finding với đủ manifest: `20261016-ref-amenities-poi-amenity` r2, `20261016-setup-initial-ddl-and-patch-ddl` r2, `20261019-agent-system-claude-opus-design` r1 và r2, `20261019-amenity-raw-key-only` r3, `20261020-dictionary-seed-from-mapping` r3, `20261021-move-poi-nodes-enr-15p-cleanup` r3, `20261021-refresh-gld-enr-poi-info` r3.

Loại việc hàng ngày theo `request.md`: thêm hoặc đổi bảng silver L2 và ref (`slv_poi_*`, `ref_dictionary_*`), seed từ `docs/context/3p-google/mapping_*.md`, đổi cột và nguồn của `gld_enr_poi_info`, chuyển cạnh `ctrl_mng_pipeline_config` giữa pipeline, dọn bảng và notebook cũ, hai task agent-system, một task ghi chú tài liệu. 10/13 task có `runtime_required: true` và kết thúc bằng runbook Fabric DEV do người dùng chạy.

## 3. Từng lane

| Lane | Model, effort | Việc đang gánh | Giữ hay bỏ khỏi đường hàng ngày |
|---|---|---|---|
| Main | Grok 4.7, `medium` (`.cursor/rules/00-main-orchestrator.mdc`) | Triage, phân loại, probe, `handoffs/author-input.md`, implement theo Main brief, remediate, runbook handoff, closeout | Giữ. Là lane duy nhất ghi code. |
| Architect | `claude-opus-5-5`, `high` (`agent_runner.ARCHITECT_MODEL/EFFORT`, `.claude/settings.json`) | `architecture.md` + Main brief cho 11/13 task, kể cả 2 task agent-system | Giữ cho task đổi grain, khoá, cạnh, ctrl, DDL. Bỏ khỏi đường hàng ngày cho task agent-system chỉ sửa tài liệu và rule (dùng review diff như EXC-02 của task này). |
| Author `--kind model` | `claude-opus-5-5`, `medium` | `model-design.md` trước Architect khi có `data_model_change` | Giữ. Đầu vào có cấu trúc cho Architect, 10 đến 14 KB. |
| Author `--kind runbook` | `claude-opus-5-5`, `medium` | `runtime-runbook.md` 7 đến 31 KB | Giữ. Thay thế Main viết runbook. |
| Author `--kind analysis` | `claude-opus-5-5`, `medium` | Không dùng từ 16/10 | Giữ cấu hình, nằm ngoài đường hàng ngày. Chỉ gọi theo mẫu A15/A16. |
| Author `--kind proposal` | `claude-opus-5-5`, `high` | Không dùng từ 16/10 | Như trên. |
| Requirements Analyst | `claude-opus-5-5`, `medium` (frontmatter `.claude/agents/requirements-analyst.md`) | Không dùng từ 16/10 | Giữ cấu hình, nằm ngoài đường hàng ngày. Chỉ gọi theo A14. |
| Codex Review Coordinator | `gpt-5.6-sol`, `medium` (`.codex/config.toml`) | 26 vòng, đọc `architecture.md` + diff, spawn specialist, gom report | Giữ, nhưng vòng 2 và 3 nên thu manifest (xem A2). |
| `state-correctness-reviewer` | `gpt-5.6-sol`, `medium` | 9/11 task | Giữ cho task có `stateful_logic`, `idempotency`, ctrl. |
| `sql-data-reviewer` | `gpt-5.6-sol`, `medium` | 11/11 task | Giữ. |
| `spark-runtime-reviewer` | `gpt-5.6-sol`, `medium` | 11/11 task | Giữ. |
| `fabric-pipeline-reviewer` | `gpt-5.6-sol`, `medium` | 1 task (`20261021-move-poi-nodes-enr-15p-cleanup`), không có file `pipelines/` trong `scope.files` | Giữ, nhưng chỉ route khi `scope.files` có `pipelines/` (xem A5). |
| `risk-gate` | `gpt-5.6-sol`, `medium` | mọi vòng của task `risk_level: high` (8 task) | Giữ. |
| `requirements-reviewer` | `gpt-5.6-sol`, `medium` | Không dùng | Ngoài đường hàng ngày. |

## 4. Tốc độ

Đo theo số process và độ dài đầu vào. Không có số giây nào trong repository.

- **Main**: chậm ở việc đọc. Mẫu A1 và rule bắt `vv.py context` rồi đọc theo TOC, nhưng skill `vsvn-extract-notebook` bước 1 bắt đọc nguyên notebook extract (53 đến 70 KB). Giảm: đổi bước 1 sang `toc` + `show cell:<i>` (mục 8, #10).
- **Architect**: lượt dài nhất. Opus `high`, `--max-turns 80`, prompt = `architect.md` + context pack phase triage (cả `request.md`) + TOC 150 dòng cho mỗi file scope > 20 KB; tự đọc notebook 50 đến 200 KB bằng Grep; output 35 đến 69 KB. Vòng 2 (sau `EVIDENCE_REQUIRED`) nhận lại context pack ở phase triage, nơi khối ARCHITECTURE chỉ có `RESULT` và size (`vv.py` `_architecture_summary`), nên làm lại từ đầu. Giảm: khi `rounds.architecture = 1`, nhúng Main brief và mục `RESULT: EVIDENCE_REQUIRED` của bản cũ vào appendix để vòng 2 là delta (mục 9, Q2).
- **Author `--kind model` / `--kind runbook`**: ngắn, Opus `medium`, `--max-turns 40`, đọc đúng file trong `author-input.md` (≤ 60 dòng). Timeout 1800 không cản trở vì chỉ là trần. Không cần giảm.
- **Codex coordinator**: `review.md` bắt đọc `architecture.md` khi tồn tại (35 đến 69 KB) ở mọi vòng, cộng diff. Giảm: vòng ≥ 2 chỉ đọc mục `## Main brief` và carry-over do `vv.py` sinh (mục 8, không có vì cần đổi `.ai/prompts/review.md`; ghi ở mục 9, Q1).
- **Specialist**: mỗi vòng spawn đủ `required_reviewers` vì `agent_runner.validate_reviewer_manifest` yêu cầu tập bằng nhau. 7/26 vòng trả 0 finding với đủ 3 đến 4 specialist. Giảm: vòng ≥ 2 manifest = specialist sở hữu finding P0/P1 còn mở + specialist của loại file đổi (mục 9, Q1).
- **risk-gate**: chạy tuần tự sau specialist ở mọi vòng của task `high`. Không giảm được nếu không đổi `WORKFLOW.md` §6.
- **Requirements Analyst, Author analysis/proposal**: không chạy, không ảnh hưởng tốc độ hàng ngày.
- **Timeout 1800**: cùng giá trị cho `run_architecture`, `run_author`, `run_review` (`agent_runner.py` dòng 104, 232, 286, 388). Không phải nguyên nhân chậm vì không chờ hết. Rủi ro là ngược lại: Codex vòng 1 với 4 specialist + risk-gate có thể chạm trần mà không ai biết. Giảm: ghi `elapsed_seconds` (mục 8, #15).

## 5. Context lệch

Thứ tự sự thật: notebook trong `notebooks/` (và `pipelines/*.json` cho pipeline), rồi tài liệu thiết kế, rồi `docs/context/`.

| ID | File, mục | Nội dung tài liệu | Chỗ notebook đối chiếu |
|---|---|---|---|
| C1 | `docs/context/01_DATA_MODEL.md` §3 (sơ đồ, bảng pipeline) và §7 | Gold là `lh_vv_gold.dbo` với `gld_srv_poi_registry`, `gld_srv_poi_multi_lang`, `gld_srv_poi_destination_membership`, ghi bởi `NB_00_ORCHES_SLV_TO_GLD`. Bảng pipeline chỉ có FL_00. | `NB_SETUP_INITIAL_DDL` cell 7 (`_ENR = "PL_VV_TRANS_SLV_TO_ENR_15P"`, `_E = "lh_vv_gold.enr"`), cell 11 `_create_enr_schema`; `NB_CREATE_DDL` cell 23; `NB_ENR_POI_INFO` cell 3 `NodeSpec(trg_tbl="gld_enr_poi_info")`; `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/*.json`. Không có notebook `gld_srv_*` trong repo. `docs/context/gld_enr_poi_info_review.md` dòng 3 tự ghi "01_DATA_MODEL.md không có hai bảng này". |
| C2 | `01_DATA_MODEL.md` §3 (`slv_3p_poi_* (14 bảng, 13 active)`), §5.2 tiêu đề (`10 bảng trong registry, 9 active`); `00_README.md` tóm tắt dòng 4 (`14, 13 active`); `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §1 dòng "Song song" (`13 bảng active`) | Ba con số khác nhau trong cùng bộ context. | `NB_SETUP_INITIAL_DDL` cell 5 `TABLE_CONFIGS_3P`: 9 `trg_tbl`, không dòng nào `is_active = 0`; cell 7 seed 9 dòng `brz_3rd_crawler_poi_stream → slv_3p_*`. |
| C3 | `CTRL_TABLES_CONTEXT.md` §3 "Dữ liệu hiện có" nguồn `brz_3rd_crawler_poi_stream` (id 24–37, 14 dòng gồm `slv_3p_poi_policy`, `_content`, `_enrichment`, `_review_i18n`, `_raw_data`, mode `LANG`, `LANG_ARRAY`); §2 sơ đồ và cột `load_mode` dòng 84 | Vẫn mô tả 5 bảng và 2 mode đã gỡ. | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` cell 4 `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`; seed 9 dòng ở C2. `NB_LIB_EXTRACT_RAWDATA` cell 2 `LOAD_MODES` vẫn giữ `LANG`, `LANG_ARRAY` (lib chấp nhận, notebook không dùng). |
| C4 | `02_NAMING_CONVENTION.md` §2 (ví dụ `NB_00_ORCHES_*` chỉ có `SLV_TO_GLD`; `NB_<UPPER(trg_tbl)>` ví dụ "—"), §3 (hậu tố nhịp `_15M [PROPOSED]`, `_1H [PROPOSED]` "bắt buộc với luồng tính lại") | Luồng đang chạy tên `PL_VV_TRANS_SLV_TO_ENR_15P`: hậu tố `_15P` không khớp `CADENCE_RE`, và tiền tố `TRANS_` khác mẫu `PL_VV_TRANSFORM_`. | `NB_LIB_TRANSFORM_SLV_GLD` cell 1 `CADENCE_RE = re.compile(r"_(\d+)([MHD])$")`, cell 3 `cadence_minutes` trả `None`; `NB_00_ORCHES_SLV_TO_ENR_15P` cell 0 ghi "Lib ghi WARN và bỏ qua kiểm tra nhịp". Node notebook có thật: `NB_SLV_POI_AMENITY`, `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`. |
| C5 | `NB_00_ORCHES_SLV_TO_GLD.md` §1 ("Gọi bởi: chưa có pipeline trong repo", "33 dòng cạnh"), §3 (mặc định 3/20/45/90) | Không có tài liệu cho `NB_00_ORCHES_SLV_TO_ENR_15P`; `00_README.md` không liệt kê notebook này. | `NB_00_ORCHES_SLV_TO_ENR_15P` cell 1: `p_max_parallel 2`, `p_node_timeout_min 15`, `p_dag_timeout_min 25`, `p_lock_timeout_min 35`; pipeline JSON activity `NB_00_ORCHES_SLV_TO_ENR_15P` timeout `0.00:32:00`, retry 0, `p_pl_name = @pipeline().Pipeline`. `NB_00_ORCHES_SLV_TO_GLD` cell 1 mặc định `PL_VV_TRANSFORM_SLV_TO_GLD_1H`, không có cạnh nào seed cho tên này. |
| C6 | `NB_LIB_TRANSFORM_SLV_GLD.md` §1 ("Được gọi bởi `NB_00_ORCHES_SLV_TO_GLD`"), §4 (không có mode `APPEND`) | Thiếu caller và thiếu mode. | `%run NB_LIB_TRANSFORM_SLV_GLD` có trong 9 notebook: `NB_00_ORCHES_SLV_TO_ENR_15P`, `NB_00_ORCHES_SLV_TO_GLD`, `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`, `NB_SETUP_INITIAL_DDL`, `NB_SETUP_POI_AMENITY`, `NB_SETUP_POI_ENTITY`, `NB_SLV_POI_AMENITY`, `NB_SLV_POI_ENTITY_NON_ENRICH`. Cell 1 lib: `APPEND_TECH_COLUMNS`, `APPEND_MARKER_KEY = "vv_append"`, `APPEND_INVALIDATING_OPS` ("[THÊM 13/10] cạnh APPEND không MERGE"). Chỉ `CTRL_TABLES_CONTEXT.md` dòng 84 nhắc `APPEND`. |
| C7 | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` §3 (`allow_full_scan False`, `max_parallel 4`); `NB_LIB_EXTRACT_RAWDATA.md` §6 (partner `False`/`4`, 3P `False`/`8`) | Mặc định sai, đã được skill `vsvn-extract-notebook` ghi là "known difference 2026-10-11" nhưng chưa sửa tài liệu. | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` cell 1: `allow_full_scan = True`, `max_parallel = 12`; `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` cell 1: `allow_full_scan = True`, `max_parallel = 12`. |
| C8 | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §3 dòng 27 (`langs`), §5 dòng 64–67 (`RAW_LANG`, `LANG_MODES`), §7 dòng 105–111 (`uses_langs`, `need_langs`, `LANG*`) | Còn mô tả nhánh ngôn ngữ đã bỏ. | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` cell 4 `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`; cell 1 không có tham số `langs`. |
| C9 | `AGENTS.md` §7 dòng 61 ("silver-to-gold POI runs hourly"), dòng 67 ("`NB_00_ORCHES_*` is the shared orchestrator"), dòng về FL_00 ("notebook activity is `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`"); `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` §1 "Gọi bởi" | Nhịp gold và tên activity lệch. | Pipeline `PL_VV_TRANS_SLV_TO_ENR_15P` là luồng 15 phút duy nhất có cạnh; có 2 notebook orchestrator trong repo. `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json` activity tên `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` (`CTRL_TABLES_CONTEXT.md` §2 ghi đúng `_BK`). |
| C10 | `00_README.md` bảng "Danh sách file" và "Tài liệu gốc trong project (`claude/`)" | Thiếu `gld_enr_poi_info_review.md`; thư mục `claude/` không có trong repo; "Cập nhật 08/10"; tóm tắt dòng 8 còn mở theo trạng thái 08/10. | `ls docs/context`; `ls claude` không tồn tại. |
| C11 | `CTRL_TABLES_CONTEXT.md` §3 "Gold trong cùng pipeline" (`gld_enr_poi_info` ← 7 bảng) | Đang lệch với working tree của task đang mở `20261022-enr-landing-and-gld-flags`. | `NB_ENR_POI_INFO` cell 3 `NodeSpec.inputs` có thêm `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination` (chưa commit). Không sửa trong task này; ghi để task kia cập nhật ở closeout. |
| C12 | `.cursor/skills/vsvn-notebook-library/SKILL.md` "Before editing" bước 2 ("As of 2026-10-11 ... `NB_LIB_TRANSFORM_SLV_GLD` is loaded by `NB_00_ORCHES_SLV_TO_GLD` and, in future, by node notebooks") | Danh sách caller cũ. | Như C6: 9 caller. |

## 6. Agent và workflow lệch

| ID | Chỗ lệch | Bằng chứng | Hệ quả |
|---|---|---|---|
| A1 | `CLAUDE.md` nói Claude Code "is the Architect, not an implementation agent" và chỉ ghi `architecture.md`. `AGENTS.md` §2 giao Claude Code thêm Author (4 kind) và Requirements Analyst; task này giao Claude Code khảo sát và review diff qua `exceptions`. | `CLAUDE.md` dòng 3–11; `AGENTS.md` §2; `task-state.yaml` task này `exceptions` EXC-01, EXC-02. | Phiên Claude mở trong workspace nhận chỉ dẫn hẹp hơn vai thật; `requirements-analyst.md` phải tự ghi đè. |
| A2 | Vòng review ≥ 2 vẫn phải chạy đủ `required_reviewers`. | `agent_runner.validate_reviewer_manifest` yêu cầu `set(value) == set(required_reviewers)`; `.ai/prompts/review.md` đoạn round 2 chỉ "pass each specialist only the round-1 P0/P1 findings it owns" nhưng vẫn spawn tất cả. 7/26 vòng trả 0 finding với đủ manifest. | Mỗi vòng xác nhận tốn 5 đến 6 process như vòng 1. |
| A3 | Cap 2 vòng review (`WORKFLOW.md` §6 luật 8) bị vượt ở 5/11 task bằng `review_plan.extra_round_approved_on`. | `20261019-amenity-raw-key-only`, `20261020-dictionary-seed-from-mapping`, `20261020-entity-drop-op-cols-add-website`, `20261021-move-poi-nodes-enr-15p-cleanup`, `20261021-refresh-gld-enr-poi-info`. 3/5 vòng 3 chỉ xác nhận disposition `fixed` hoặc `rejected-false-positive` đã có evidence. | Vòng 3 là đường thường, không phải ngoại lệ. |
| A4 | `review.md` bắt coordinator "Read `architecture.md` when it exists" ở mọi vòng. | `architecture.md` 35 đến 69 KB ở 10 task; Main brief ≤ 14.000 ký tự nằm ngay sau `RESULT:`. | Coordinator và specialist nạp 3 đến 5 lần lượng cần. |
| A5 | `fabric-pipeline-reviewer` được route khi không có file `pipelines/` trong scope. | `20261021-move-poi-nodes-enr-15p-cleanup`: `request.md` ghi "Không đổi pipeline JSON", `scope.files` không có `pipelines/`; finding `PIPE-001` sau đó `rejected-false-positive` (D-09) và cần vòng 3. `.cursor/rules/20-data-pipeline.mdc` chỉ yêu cầu reviewer này cho "pipeline change". | 1 specialist thừa × 3 vòng + 1 vòng thừa. |
| A6 | Không có số đo thời gian cho lượt model. | `agent_runner._run` chỉ có `timeout_seconds`; `round-N.json` chỉ có `round`, `verdict`, `findings`, `files`; `verify` chỉ ghi timestamp. | Không trả lời được "lượt nào chạm 1800 giây". |
| A7 | Architect vòng 2 không nhận bản vòng 1. | `vv.py` `_architect_appendix` gọi `build_context(phase="triage")`; ở phase triage `_architecture_summary` trả `RESULT` + size. 3 task có `rounds.architecture = 2`. | Vòng 2 là lượt Opus `high` làm lại toàn bộ. |
| A8 | Task agent-system đi đủ Architect 2 vòng + Codex 2 vòng với `required_reviewers: []`. | `20261019-agent-system-claude-opus-design`: `rounds.architecture 2`, `rounds.review 2`, hai vòng review chỉ coordinator, 0 finding. | 2 lượt Opus `high` + 2 lượt Codex cho thay đổi rule và prompt. Task này đã chọn đường khác (EXC-02). |
| A9 | Skill `vsvn-extract-notebook` bước 1 "Read the closer existing notebook in full" trái với "Read budget" của chính skill và với `00-main-orchestrator.mdc` (file > 20 KB đọc qua `toc`/`show`). | `.cursor/skills/vsvn-extract-notebook/SKILL.md` dòng 14 và 21–25. | Main nạp 53 đến 70 KB mỗi lần sửa extract. |
| A10 | Skill mang "known differences 2026-10-11" thay vì tài liệu được sửa. | `vsvn-extract-notebook` bước 3; C7, C8. | Mỗi phiên đọc thêm một đoạn giải thích lệch thay vì đọc số đúng. |
| A11 | `requirements-reviewer.toml` (7 KB) không nằm trong `run-gate` và không được mẫu nào gọi. | `.codex/agents/requirements-reviewer.toml` description tự ghi "Not part of the run-gate specialist review cycle"; không task nào từ 16/10 dùng. | Không tốn process; chỉ là cấu hình chưa có đường dùng. |

## 7. Việc không làm

- Không sửa model ID hay effort trong `.claude/settings.json`, `.codex/config.toml`, `.codex/agents/*.toml`, frontmatter `.claude/agents/requirements-analyst.md`, hằng số `scripts/agent_runner.py`, hay `models.*.expected` trong template (DEC-03).
- Không chạy `python scripts/vv.py` (context, toc, show, verify, run-gate, run-author), không chạy probe Fabric, không commit.
- Không sửa notebook, pipeline JSON, test, hay `docs/context` trong phiên này. Mọi sửa thuộc mục 8 do Grok 4.7 Medium làm sau khi người dùng chốt.
- Không đọc `notebooks_lgc/`, `docs/context/3p-google/*.txt`, `pipelines/*/manifest.json`, evidence của task khác, `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md`.
- Không đọc cả file notebook; không đọc thân `.cursor/skills/*/SKILL.md` ngoài phần kích hoạt và phần bắt đọc; không đọc thân `requirements-analyst.md` ngoài frontmatter và Identity.
- Không đo giây. Không suy đoán mức tiêu thụ token tuyệt đối.
- Không đổi `WORKFLOW.md` §6 cap vòng, không đổi hợp đồng JSON của `run-gate`; hai việc này cần người dùng chốt (mục 9).
- Không xử lý C11 (task `20261022-enr-landing-and-gld-flags` đang mở).

## 8. Mục sửa

Mỗi mục một file. Người thực hiện: Grok 4.7 Medium, chỉ mục được chốt.

| # | File | Thay đổi (một câu) | Cách kiểm tra |
|---|---|---|---|
| 1 | `docs/context/01_DATA_MODEL.md` | Sửa §3 sơ đồ, bảng pipeline và §7 sang gold hiện hành: `lh_vv_gold.enr.gld_enr_poi_info`, `gld_enr_poi_review`, pipeline `PL_VV_TRANS_SLV_TO_ENR_15P` gọi `NB_00_ORCHES_SLV_TO_ENR_15P`, mode `APPEND`; chuyển `gld_srv_*` và `NB_00_ORCHES_SLV_TO_GLD` xuống §11 "Hướng sắp tới" với nhãn `[PROPOSED]`. | `grep -n "gld_srv_\|lh_vv_gold.dbo" docs/context/01_DATA_MODEL.md` chỉ còn khớp trong §11; `grep -c "gld_enr_poi_info" docs/context/01_DATA_MODEL.md` ≥ 2. |
| 2 | `docs/context/01_DATA_MODEL.md` | Thống nhất số bảng 3P ở §3 và tiêu đề §5.2 thành "9 bảng trong registry, 9 active" theo `TABLE_CONFIGS_3P`. | `grep -n "14 bảng\|13 active\|10 bảng" docs/context/01_DATA_MODEL.md` không còn kết quả. |
| 3 | `docs/context/CTRL_TABLES_CONTEXT.md` | Thay bảng 3P ở §3 "Dữ liệu hiện có" bằng 9 dòng `DOC`/`DOC_ARRAY` theo seed `NB_SETUP_INITIAL_DDL` cell 7, bỏ `LANG`/`LANG_ARRAY` khỏi §2 và dòng 84, giữ ghi chú lịch sử ở §10. | Số dòng `slv_3p_` trong bảng §3 = 9; `grep -n "LANG_ARRAY" docs/context/CTRL_TABLES_CONTEXT.md` chỉ còn trong §10. |
| 4 | `docs/context/02_NAMING_CONVENTION.md` | §2 thêm ví dụ `NB_00_ORCHES_SLV_TO_ENR_15P`, `NB_SLV_POI_AMENITY`, `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`; §3 ghi `PL_VV_TRANS_SLV_TO_ENR_15P` là tên đang chạy, hậu tố `_15P` không khớp `CADENCE_RE` nên lib WARN và bỏ kiểm tra nhịp, và quyết định đổi tên (nếu có) là task riêng. | `grep -n "ENR_15P" docs/context/02_NAMING_CONVENTION.md` ≥ 2 kết quả. |
| 5 | `docs/context/NB_00_ORCHES_SLV_TO_GLD.md` | Mở rộng thành tài liệu cho cả hai orchestrator: §1 "Gọi bởi" = `PL_VV_TRANS_SLV_TO_ENR_15P` (activity timeout 32 phút, retry 0, `p_pl_name = @pipeline().Pipeline`), §3 bảng mặc định theo từng notebook (2/15/25/35 và 3/20/45/90), ghi `NB_00_ORCHES_SLV_TO_GLD` chưa có cạnh seed. | Giá trị §3 khớp cell 1 của hai notebook (`python scripts/vv.py show notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb cell:1`). |
| 6 | `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md` | §1 liệt kê 9 notebook `%run` lib; §4 thêm mục mode `APPEND` (`APPEND_TECH_COLUMNS`, `APPEND_MARKER_KEY`, `APPEND_INVALIDATING_OPS`, cạnh không MERGE). | Đếm `%run NB_LIB_TRANSFORM_SLV_GLD` trong cell code của `notebooks/*.ipynb` (không tính markdown) cho đúng 9 notebook trong §1; `grep -c "APPEND" docs/context/NB_LIB_TRANSFORM_SLV_GLD.md` ≥ 3. |
| 7 | `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` | §3 sửa `allow_full_scan` = `True`, `max_parallel` = `12`; §1 "Gọi bởi" ghi tên activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`. | So với `python scripts/vv.py show notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb cell:1` và `grep "_BK" pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/*.json`. |
| 8 | `docs/context/NB_LIB_EXTRACT_RAWDATA.md` | §6 sửa mặc định partner và 3P: `allow_full_scan True/True`, `max_parallel 12/12`. | So với cell 1 của hai notebook extract. |
| 9 | `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` | §1 "Song song" sửa thành 9 bảng; gỡ `langs`, `RAW_LANG`, `LANG_MODES`, `uses_langs`, `need_langs` ở §3, §5, §7 hoặc ghi rõ là mã chết chỉ chạy khi registry có mode `LANG*`. | `grep -n "13 bảng\|langs" docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` chỉ còn dòng có nhãn mã chết. |
| 10 | `.cursor/skills/vsvn-extract-notebook/SKILL.md` | Bước 1 đổi "Read ... in full" thành đọc cell 0, 1 và cell Main/Exit qua `toc`/`show`; xoá khối "Known differences on 2026-10-11" sau khi #7, #8, #9 xong. | `grep -n "in full\|Known differences" .cursor/skills/vsvn-extract-notebook/SKILL.md` không còn; `python scripts/vv.py doctor` không WARN skill budget. |
| 11 | `.cursor/skills/vsvn-notebook-library/SKILL.md` | Bước 2 cập nhật caller "As of 2026-10-22": 9 notebook `%run NB_LIB_TRANSFORM_SLV_GLD` (danh sách ở C6), 3 notebook `%run NB_LIB_EXTRACT_RAWDATA` (`NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_SETUP_L1_TS_AUDIT`); hai lib không `%run` nhau. | Đếm `%run` chỉ trong cell code (`python scripts/vv.py show notebooks/<nb>.ipynb grep:^%run`) khớp danh sách; `doctor` không WARN. |
| 12 | `docs/context/00_README.md` | Thêm `gld_enr_poi_info_review.md` vào danh sách file; sửa tóm tắt dòng 4 (9 bảng 3P) và dòng 8; bỏ hoặc đánh dấu bảng "Tài liệu gốc (`claude/`)" không có trong repo; cập nhật ngày. | Mọi `docs/context/*.md` (trừ `README.md`) xuất hiện trong bảng; `grep -n "claude/" docs/context/00_README.md` không còn. |
| 13 | `AGENTS.md` | §7 sửa "silver-to-gold POI runs hourly" thành nhịp 15 phút của `PL_VV_TRANS_SLV_TO_ENR_15P`, sửa tên activity FL_00 thành `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`, ghi `NB_00_ORCHES_*` là orchestrator dùng chung với hai bản trong repo; cắt chữ chỗ khác để giữ ≤ 8 KB. | `python scripts/vv.py doctor` không WARN "instruction budget exceeded: AGENTS.md"; `wc -c AGENTS.md` ≤ 8192. |
| 14 | `CLAUDE.md` | Sửa vai: Claude Code chạy Architect, Author (`run-author --kind`), Requirements Analyst, và phiên ngoại lệ theo `exceptions`; mỗi vai ghi đúng một artifact; trỏ `AGENTS.md` §2 thay vì tự định nghĩa. | Đọc lại thấy không còn câu "Claude Code is the Architect, not an implementation agent" mâu thuẫn §2; `python scripts/vv.py validate --all` PASS. |
| 15 | `scripts/vv.py` | `cmd_run_gate` và `cmd_run_author` đo thời gian quanh lời gọi `agent_runner.*`, in `Elapsed: <n> s` và ghi `elapsed_seconds` vào `reviews/round-N.json` (và vào stdout cho architect/author). | `tests/test_vv.py` thêm test snapshot có khoá `elapsed_seconds`; `python scripts/vv.py verify <task-id>` PASS. |

## 9. Câu hỏi cần chốt

1. **Thu manifest vòng ≥ 2 (A2, A4)**: có cho `run-gate` vòng 2 và 3 chạy manifest = specialist sở hữu finding P0/P1 còn mở + specialist của loại file đổi, giữ risk-gate, và coordinator chỉ đọc `## Main brief` thay cả `architecture.md`? Việc này đổi `agent_runner.validate_reviewer_manifest`, `vv.py` (truyền manifest rút gọn), `.ai/prompts/review.md`, `WORKFLOW.md` §6, nên vượt "một file một mục" và cần quyết định của người dùng trước khi vào mục 8.
2. **Architect vòng 2 (A7)**: có cho `_architect_appendix` nhúng Main brief và các dòng probe của bản `EVIDENCE_REQUIRED` vòng 1 khi `rounds.architecture = 1`? Đổi `vv.py` và `tests/test_vv_context.py`.
3. **Route `fabric-pipeline-reviewer` (A5)**: chốt luật "chỉ khi `scope.files` có `pipelines/`" ở `WORKFLOW.md` §7, và có để `vv.py validate` cảnh báo khi reviewer này nằm trong `required_reviewers` mà scope không có pipeline?
4. **Task agent-system (A8)**: có chốt đường mặc định cho task agent-system chỉ sửa tài liệu, rule, prompt là review diff bằng Claude Code (như EXC-02) thay cho Architect + Codex, ghi vào `AGENT_PROMPT_SAMPLES.md` A18?
5. **Tên pipeline `_15P` (C4)**: giữ tên `PL_VV_TRANS_SLV_TO_ENR_15P` và ghi là ngoại lệ của `CADENCE_RE`, hay mở task đổi tên pipeline và cạnh ctrl sang hậu tố `_15M`? Mục 8 #4 giả định giữ tên.
