# Evidence plan

## Decision to resolve

Tập dòng `ctrl_mng_pipeline_config` và `ctrl_mng_watermark` đang sống trên Fabric DEV cho hai node cần chuyển và các đối tượng cần xóa. Seed trong repo không liệt kê mọi cạnh đã retire trên DEV. Architecture không được xóa hoặc chuyển một dòng chưa có trong kết quả probe.

## Existing evidence

- Seed `init_seed_ctrl` trong `notebooks/NB_SETUP_INITIAL_DDL.ipynb`: 6 cạnh `slv_poi_entity_non_enrich` và 3 cạnh `slv_poi_amenity` thuộc `PL_VV_TRANS_SLV_TO_SLV_1H`; 2 cạnh `slv_pn_poi` và 3 cạnh `gld_enr_poi_coordinate` thuộc `PL_VV_TRANS_SLV_TO_ENR_15P`; 3 cạnh info cũ từ `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` có `is_active = 0`.
- `docs/context/CTRL_TABLES_CONTEXT.md` §3–§4: một node chỉ thuộc một pipeline active; watermark cạnh là `wm_e__<trg_tbl>__<src_tbl>`; khoá luồng là `wm_flow__<pl_name>`.
- `evidence/results/ctrl-inventory.txt` (user paste 2026-10-21): đủ điều kiện pass của probe. Diễn giải nằm ở `decision.md` D-01 đến D-04.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `evidence/probes/ctrl-inventory.sql` | Fabric DEV, đọc `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold` | Cạnh, watermark, khoá, và số dòng của các bảng trong phạm vi | INV-1 bằng số dòng INV-2. INV-3 bằng số dòng INV-4. INV-2 và INV-4 không chạm 50 dòng. INV-5 đến INV-8 trả một số đếm, hoặc dán lỗi nếu bảng không có rồi chạy câu sau | `evidence/results/ctrl-inventory.txt` |
| `evidence/probes/slv-1h-quiesce.sql` | Fabric DEV, đọc `lh_vv_ctrl`; Monitor pipeline là thao tác người dùng | PIPE-001: `PL_VV_TRANS_SLV_TO_SLV_1H` có run notebook `RUNNING` hoặc khoá luồng đang giữ không, ngay trước cleanup | Q1: 0 hoặc 1 dòng, `lock_exec_id` null. Q2: không có `RUNNING` hoặc `n = 0`. Q3: không `RUNNING` và không chạm 20 dòng. Monitor: item vắng hoặc schedule tắt, In progress = 0, Queued = 0 | `evidence/results/slv-1h-quiesce.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
