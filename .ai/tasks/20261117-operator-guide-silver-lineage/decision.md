# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Lineage silver | Mục 2 của `docs/context/03_OPERATOR_GUIDE.md` giữ năm heading. Lineage silver nằm trong mục 2, sau lineage gold. Phạm vi silver là bảng L1 từ seed `id:init_cfg_partner`, `id:init_cfg_3p`, `id:init_cfg_cms` và `id:init_cfg_enr`, cộng bảng silver mà node `NodeSpec` ghi khi cạnh `id:init_seed_ctrl` có `load_mode` `RECOMPUTE` hoặc `APPEND`. Không sửa `.cursor/skills/vsvn-operator-docs/SKILL.md`: AGENTS.md §8 cấm sửa cấu hình agent-system khi người dùng không yêu cầu. Skill §2 hiện chỉ nêu scope gold; task này không chọn skill làm nguồn đúng cho phạm vi người dùng đã yêu cầu. | request.md ## Scope | 2026-11-17 |
| D-02 | Nguồn mục 2 | Mục 2 lấy bảng, khoá, cạnh và kiểu join từ `TABLE_SPECS`, seed `init_cfg_*` / `init_seed_ctrl` và `NodeSpec` / `build`. `01_DATA_MODEL.md` §5.2 ghi khối `poi_address`, `poi_review`, `poi_media`; cell `init_cfg_3p` ghi `source_table` `$`, `reviews`, `photos`. Guide dùng cell. §6 liệt kê năm bảng L2 không có trong `TABLE_SPECS`; mục 2 ghi không hiện hành, không vẽ cạnh. §6 không có `slv_poi_media_info`; mục 2 có vì `TABLE_SPECS` và seed có. §7 không liệt kê `gld_srv_*`; mục 2 giữ các bảng đó vì chúng có trong `TABLE_SPECS`. | request.md ## User outcome | 2026-11-17 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Chưa có.

## Lịch sử quyết định

- 2026-11-17: D-01. Người dùng yêu cầu cập nhật operator guide theo model hiện tại và thêm lineage silver. Skill `vsvn-operator-docs` §2 chỉ giao scope `lh_vv_gold.dbo` và `lh_vv_gold.enr`. Skill cũng nói nếu thiếu procedure thì ghi `decision.md` rồi sửa skill. Sửa skill mâu thuẫn AGENTS.md §8. Task ghi lệch ở D-01 và không sửa skill. Layout hình silver theo layout mục 2 hiện có của guide. Nhãn quan hệ lấy từ `vsvn-data-model-flow`.
- 2026-11-17: D-02. Người dùng yêu cầu toàn bộ model hiện tại. Seed `init_cfg_3p` và `01_DATA_MODEL.md` §5.2 không cùng `source_table`. `TABLE_SPECS` không có năm bảng L2 của §6 và có `slv_poi_media_info` cùng `gld_srv_*` mà §6–§7 không liệt kê đủ. Guide theo repository, theo outcome của request.
