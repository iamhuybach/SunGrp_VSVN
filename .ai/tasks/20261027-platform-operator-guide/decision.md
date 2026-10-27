# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Phân loại | Thay đổi agent-system vì có skill. `complexity=medium`, `risk_level=low`, `architecture_required=true`, không evidence, không runtime. Signal chỉ `design_tradeoffs`. Không `data_model_change`. Không `model_override`. Main `grok-4.7` / `medium`. | `request.md` Classification rationale | 2026-10-27 |
| D2 | Required ctrl | Required = cột `NOT NULL` trong `NB_SETUP_INITIAL_DDL` cell 3 cộng `ConfigError` trong lib. Cell 3 không có `NOT NULL` trên cột ctrl. Không dùng mục "Dữ liệu hiện có". | `03_OPERATOR_GUIDE.md` §1 | 2026-10-27 |
| D3 | Lineage hiện hành | Bảng gold hiện hành là `fq` trong `TABLE_SPECS` của `NB_SETUP_INITIAL_DDL` cell 3. Kiểu cạnh lấy từ `join` / `union` trong cell `build`. `gld_enr_poi_coordinate` không có trong `TABLE_SPECS` và không có notebook node, nên không vẽ cạnh. | `03_OPERATOR_GUIDE.md` §2 | 2026-10-27 |
| D4 | Tên enrich | Notebook là `NB_00_ORCHES_SLV_TO_ENR`. Pipeline là `PL_VV_TRANS_SLV_TO_ENR_15M`. Không có `PL_VV_TRANS_SLV_TO_ENR_30P`. Activity JSON vẫn tên `NB_00_ORCHES_SLV_TO_ENR_15P`. | Người dùng 2026-10-27; `03_OPERATOR_GUIDE.md` §5.3 | 2026-10-27 |
| D5 | Hash và payload | Hash partner đang chạy là `sha2(concat_ws U+0001, coalesce(_source,_op,_before,_after), 256)` ở cell 6 `reject_rows`. `after_payload` 3rd-party lấy `normalized_payload`. | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` cell 6; `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` hằng `RAW_PAYLOAD` | 2026-10-27 |
| D6 | Hai skill | Hai `SKILL.md` ghi từ FILE block của architecture PASS bằng `materialize --write`. | architecture.md Skill files | 2026-10-27 |
| D7 | Sửa tài liệu sau review | Người dùng yêu cầu ghi giá trị đóng của cột ctrl, đổi mục 2 thành `Data lineage`, hình từng bảng với `enr` trước, bỏ cột nguồn code, và mỗi step mục 3–4 có code. Không mở review vòng 3 vì đã hết round cap. | Người dùng 2026-10-27 | 2026-10-27 |
| D8 | SQL trực tiếp, không mode ngôn ngữ | Bỏ `LANG` và `LANG_ARRAY` khỏi guide và context. Kiểu join nằm dưới hình, không ghi trên mũi tên. Mục 3 và 4 là câu SQL chạy thẳng, không trỏ người đọc tới `NB_SETUP_INITIAL_DDL` hay `NB_CREATE_DDL`. | Người dùng 2026-10-27 | 2026-10-27 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
| REV-001 | P1 | fixed | `03_OPERATOR_GUIDE.md` §4.4 và `vsvn-operator-docs` mục thêm bảng: raw đã có `last_src_version` thì `table_filter` + `full_reload = True`; raw chưa có con trỏ thì `allow_full_scan = True`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-27: Giữ tên `NB_00_ORCHES_SLV_TO_ENR`. Pipeline enrich là `PL_VV_TRANS_SLV_TO_ENR_15M`. Hash lấy biểu thức đang chạy. `after_payload` 3rd-party là `normalized_payload`.

## Lịch sử quyết định

- 2026-10-27: Người dùng bỏ `LANG` / `LANG_ARRAY` khỏi guide và context. Kiểu join ghi dưới hình mục 2. Mục 3 và 4 là SQL chạy thẳng, không dẫn tới hai notebook DDL.
- 2026-10-27: Người dùng góp ý sau review PASS. Guide thêm bảng giá trị đóng, mục 2 đổi thành `Data lineage` với một hình mỗi bảng và `enr` trước, mục 3 và 4 đánh số Step và kèm code. Skill `vsvn-operator-docs` chỉ thêm quy trình, không chép bảng giá trị.
- 2026-10-27: REV-001 fixed. Guide §4.4 và skill `vsvn-operator-docs` phân biệt lần chạy đầu khi thêm bảng: chưa có con trỏ thì `allow_full_scan = True`; đã có con trỏ thì `table_filter` cộng `full_reload = True`.
- 2026-10-27: Hai `SKILL.md` ghi từ FILE block của architecture PASS bằng `python scripts/vv.py materialize 20261027-platform-operator-guide --write`. Một dòng Bản đồ context thêm vào `docs/AGENT_PROMPT_SAMPLES.md`. Comment `event_hash` và `after_payload` trong `NB_CREATE_DDL` được sửa cùng `NB_SETUP_INITIAL_DDL` vì `test_columns_match_sources` bắt hai bên khớp.
- 2026-10-27: Người dùng chốt tên notebook `NB_00_ORCHES_SLV_TO_ENR`, pipeline `PL_VV_TRANS_SLV_TO_ENR_15M`, hash theo biểu thức `reject_rows`, và `normalized_payload`. Main sửa context còn tên cũ, comment DDL của `event_hash` và `after_payload`, tiêu đề notebook enrich, và docstring `reject_rows`. Không đổi activity `NB_00_ORCHES_SLV_TO_ENR_15P` trong JSON pipeline. Không có `PL_VV_TRANS_SLV_TO_ENR_30P`.
- 2026-10-27: Bốn quy trình sẽ đưa vào skill sau khi architecture PASS. Skill chỉ giữ các bước và đường dẫn, không chép bảng cột, sơ đồ lineage, hay danh sách tham số.
  1. Ctrl: đọc `TABLE_SPECS` của `NB_SETUP_INITIAL_DDL` cell 3 và `ConfigError` của `build_table_specs`, `build_dag`, `check_config`, `require_ctrl_columns`. Bỏ "Dữ liệu hiện có".
  2. Lineage gold: danh sách bảng từ `TABLE_SPECS` schema `lh_vv_gold.dbo` và `lh_vv_gold.enr`. Quan hệ từ `join` / `union` trong cell `build`. Không có file node thì ghi không có node. `write_mode` ghi riêng.
  3. Thêm field hoặc bảng bronze sang silver: sửa seed ở cả `NB_SETUP_INITIAL_DDL` và `NB_CREATE_DDL` (`02_NAMING_CONVENTION.md` §2.1). Init là `p_apply` của notebook setup. Không init là cell patch cuối `NB_CREATE_DDL`. `ALTER` cột đích do `ensure_target`. Watermark là theo raw, không theo bảng đích.
  4. Tham số: cell tham số cộng hàm kiểm tra (`build_context`, `check_config`, `_validate_orch_params`). Khung sub-notebook trỏ `NB_LIB_TRANSFORM_SLV_GLD.md` §5. Hai nguồn lệch thì ghi CONFLICT và dừng, không chọn.
- 2026-10-27: Skill công khai đã xem, không chép nguyên văn vào repo. Sự thật VSVN chỉ lấy từ file Context của task.
  - `skill-creator`, nguồn https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md và https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices. Thủ thuật: description nói việc skill làm và lúc dùng (WHAT và WHEN). `SKILL.md` là quy trình ngắn. Chi tiết để file riêng. Ở task này file riêng là `docs/context/03_OPERATOR_GUIDE.md`.
  - `datahub-lineage`, nguồn https://github.com/datahub-project/datahub-skills/blob/main/skills/datahub-lineage/SKILL.md. Thủ thuật: tách hướng truy vết (nguồn vào đích) và bắt mỗi cạnh có nguồn. Không dùng catalog bên ngoài. Cạnh VSVN lấy từ cell `build`.
  - `creating-mermaid-dbt-dag`, nguồn https://github.com/dbt-labs/dbt-agent-skills/blob/main/skills/dbt-extras/skills/creating-mermaid-dbt-dag/SKILL.md. Thủ thuật: các bước vẽ sơ đồ nằm trong skill, quy tắc hình nằm ở tài liệu dẫn chiếu, sơ đồ sinh từ code hiện tại. Skill data model của VSVN trỏ mục lineage trong guide, không nhúng sơ đồ.
