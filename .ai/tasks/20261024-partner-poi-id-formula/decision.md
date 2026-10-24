# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Công thức `poi_id` partner | `poi_id = md5(concat(<id>, 'partner'))` rồi chèn gạch 8-4-4-4-12. `<id>` là `slv_pn_business_services.id` hoặc `slv_pn_business_service_i18ns.business_service_id` (cùng một giá trị). `uuid_md5(<id>, lit('partner'))` là lời gọi đúng. Ba notebook đang gọi đã đúng nên không viết lại. `ref_source` = `partner_portal` giữ nguyên vì đó là tên nguồn. Bảng `slv_pn_*` không thêm `poi_id`. | request.md — Acceptance criteria | 2026-10-24 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có. Fast lane, không có `architecture.md`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-24 — Chốt công thức trong request của task này: `md5(concat(<id>, 'partner'))`, gạch 8-4-4-4-12; không đảo `partner` đứng trước; không đổi thân `uuid_md5` khi thân hàm vẫn nối theo thứ tự đối số.

## Lịch sử quyết định

- 2026-10-24 — Câu `poi_id` partner đặt thêm ở `docs/context/01_DATA_MODEL.md` §5.1, ngay dưới hai bảng `slv_pn_business_services` và `slv_pn_business_service_i18ns`, để lần đọc L1 sau dùng luôn. §8 và `AGENTS.md` giữ công thức đã chốt.
- 2026-10-24 — D1. Rà `uuid_md5` và `partner_portal` trong `notebooks/*.ipynb`. Không notebook nào lệch. Fast lane: chỉ sửa câu partner trong `AGENTS.md` và câu §8 còn ghi `partner_portal`. Câu §6 về `slv_poi_entity_non_enrich` đã đúng nên không sửa. Để `AGENTS.md` dưới 8 KB, cụm lặp `docs/context/02_NAMING_CONVENTION.md` ở cuối bullet vai trò notebook rút thành `(§2.1)`; đường dẫn vẫn đứng ở đầu bullet đó.

| File | Dòng | Biểu thức đang chạy | Kết luận |
|---|---|---|---|
| `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` | `def uuid_md5` (cell 15) | `md5(concat(*cols))` rồi `regexp_replace` thành 8-4-4-4-12, đúng thứ tự đối số | Đúng. Không sửa thân hàm |
| `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` | cell 4, `uuid_md5` | `uuid_md5(col("id"), lit(PARTNER))`, `PARTNER = "partner"`, nguồn `slv_pn_business_services` | Đúng. Không viết lại |
| `notebooks/NB_ENR_POI_INFO.ipynb` | cell 3, `_vi_i18n` | `uuid_md5(col("business_service_id"), lit(PARTNER))`, `PARTNER = "partner"`, nguồn `slv_pn_business_service_i18ns` | Đúng. Không viết lại |
| `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` | `uuid_md5` | `uuid_md5(col("business_service_id"), lit(PARTNER))`, `PARTNER = "partner"`, nguồn `slv_pn_business_service_i18ns` | Đúng. Không sửa (task `20261024-gld-srv-poi-from-mapping`) |
| `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` và bảng `slv_pn_*` ở `docs/context/01_DATA_MODEL.md` §5.1 | — | Không có biểu thức `poi_id`. Khóa là khóa nguồn (`id`, hoặc `business_service_id` + `locale`) | Không gán |
| `notebooks/*.ipynb` | — | Không có literal `partner_portal` | Không có chỗ tính theo tên nguồn |
