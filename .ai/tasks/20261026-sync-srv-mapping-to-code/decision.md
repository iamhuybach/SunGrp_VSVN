# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Nguồn mapping | Code là nguồn đúng. Chỉ sửa lệch trong bảng dưới. Chỗ notebook và DDL không ghi thì để MISSING. Không thêm rule, coalesce, hay nhánh mới. | request.md Acceptance criteria | 2026-10-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có. `architecture_required` = false. Diff toàn markdown, không đổi grain, khóa, owner, hay orchestration.

## Bảng lệch mapping

Khớp thì giữ. Dòng dưới là lệch sẽ ghi.

| File | Mục | Dòng code | Hiện tại | Sẽ ghi |
|---|---|---|---|---|
| `mapping_gld_srv_poi_amenity.md` | §0 pipeline | `NB_SETUP_POI_AMENITY` cell `c1setupedges`: `PL = "PL_VV_TRANS_SLV_TO_ENR_15M"`, `load_mode = 'RECOMPUTE'` | `PL_VV_TRANS_SLV_TO_ENR_15P` | `PL_VV_TRANS_SLV_TO_ENR_15M` |
| `mapping_gld_srv_poi_amenity.md` | §1 `gld_srv_poi_amenity` | `NB_GLD_SRV_POI_AMENITY` cell `srvamenitybuild`: `select(*OUT_COLS)`; `NB_CREATE_DDL` cell `amenddlpy`: `PL_VV_TRANS_SLV_TO_GLD_1H`; `sql_merge_target` | Chỉ đổi `created_at` và `updated_at`. Không ghi pipeline | Build chọn `OUT_COLS`. Timestamp do `sql_merge_target`. Pipeline `PL_VV_TRANS_SLV_TO_GLD_1H`, `load_mode = RECOMPUTE` |
| `mapping_gld_srv_poi_info.md` | §1.1 lọc nguồn | `srvinfobuild`: `where(~is_google \| _both)`, `is_google = lower(trim(source_name))` | Partner lấy full; google so `source_name = 'google'` | Mọi dòng không phải google được giữ. Google chỉ khi `poi_id` có ở cả destination và multi_lang |
| `mapping_gld_srv_poi_info.md` | §1.1 trùng destination | `_destination`: dừng khi `updated_at` null hoặc nhiều dòng cùng max | Ưu tiên bản ghi `updated_at` lớn hơn | Giữ max khi max duy nhất và không null. Ngược lại dừng, không chọn dòng |
| `mapping_gld_srv_poi_info.md` | §1.1 pipeline | `plcadpy` đổi `30P` → `30M`; `mlexppy` dùng `PL_VV_TRANS_SLV_TO_GLD_30M` | `PL_VV_TRANS_SLV_TO_GLD_30P`. Không gắn `15P` | `PL_VV_TRANS_SLV_TO_GLD_30M`, `load_mode = RECOMPUTE`. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15M` |
| `mapping_gld_srv_poi_info.md` | §1.1 input | `SPEC.required_inputs=("entity",)`; ba input `live_only=False` | Không ghi `required_inputs` hay `live_only` | Đúng `SPEC.inputs`, `required_inputs`, và chỗ notebook truyền `live_only` |
| `mapping_gld_srv_poi_info.md` | §1.2 `is_recommended` | `F.coalesce(SRC == "partner", F.lit(False))` | `source_name = 'partner'` | `lower(trim(source_name))`; null thành false |
| `mapping_gld_srv_poi_info.md` | §1.2 miền INT | `INT_MIN, INT_MAX = -2147483648, 2147483647` | "ngoài miền INT" | Thêm đúng hai biên |
| `mapping_gld_srv_poi_info.md` | §1.3 giờ Google | `google_hours`: không đọc `close_day`; dừng `GOOGLE_*` | Không ghi mã dừng | Ghi mã dừng có trong hàm. Không sửa JSON case 1 và case 2 |
| `mapping_gld_srv_poi_info.md` | §1.5 giờ partner | `partner_hours`, `operating_hours` | Không ghi mã dừng partner và nguồn khác | Ghi `PARTNER_*` và `SOURCE_NOT_GOOGLE_PARTNER` |
| `mapping_gld_srv_poi_multi_lang.md` | §1.1–§1.2 | `srvmlbuild`: `experience = when(partner, coalesce(usps, experience))` | Không có `experience` | Thêm cột và rule `usps` / `experience` đúng `OUT_COLS` |
| `mapping_gld_srv_poi_multi_lang.md` | §1.1 pipeline và input | `SPEC.required_inputs=("multi_lang", "entity")`; `plcadpy` | `30P`; không ghi input bắt buộc | `30M`; `i18n` không thuộc `required_inputs` |
| `mapping_poi_media_info.md` | §1.2 `is_cover` | `with_cover`: `orderBy(display_order asc nulls last, _pos asc nulls last, media_id asc)` | Hòa thì dòng gặp đầu tiên | Đúng thứ tự `orderBy` |
| `mapping_poi_media_info.md` | §1.1 pipeline | `mediaddlpy` literal `30P`; `plcadpy` đổi thành `30M`; `required_inputs=("media_3p", "i18n")` | Không ghi pipeline, `load_mode`, `required_inputs` | `PL_VV_TRANS_SLV_TO_GLD_30M`, `RECOMPUTE`; `services` không bắt buộc |
| `mapping_poi_media_info.md` | §2 gallery | `srvgallerybuild`: `select(*OUT_COLS)`; cạnh gallery trong `mediaddlpy` | Chỉ đổi `created_at` và `updated_at` | Build chọn `OUT_COLS`. Pipeline `30M`, `load_mode = RECOMPUTE` |
| Bốn file mapping | Dòng đầu | Yêu cầu nghiệm thu | Chưa có câu nghĩa vụ | Câu: cùng task cập nhật file trước review sau mỗi đổi nghiệp vụ của bảng trong file |
| `docs/AGENT_PROMPT_SAMPLES.md` | Bản đồ context | Yêu cầu nghiệm thu | Chưa có dòng bốn file | Một dòng, kèm cùng câu nghĩa vụ |

Đã đối chiếu và giữ, vì khớp code:

- Amenity: grain và khóa `(poi_id, business_sector, amenity_group, amenity_raw)`, `OUT_COLS`, DDL `slv_poi_amenity`, ba cạnh active, cạnh `slv_poi_entity` `RETIRE`, `SPEC.inputs`, markdown đầu `NB_SLV_POI_AMENITY`.
- `gld_srv_poi_info`: thứ tự target của §1.2 bằng `OUT_COLS` rồi `created_at`, `updated_at`; rule rating, review, JSON case 1 và case 2.
- `gld_srv_poi_multi_lang`: grain `(poi_id, lang)`, `uuid_md5`, `description` = `bio` rồi fallback `description`.
- Media: thứ tự target §1.2 bằng `OUT_COLS` rồi hai timestamp; `sha2` `media_id`; `blob_url` không trim; `locale = vi`; bỏ `deleted`; `thumbnail_url` null; `is_active` true và soft-delete false.

`NODE_EDGES` trong `NB_CREATE_DDL` vẫn liệt kê ba cạnh amenity và kiểm tra `load_mode = RECOMPUTE`. Cell đó còn literal `PL_VV_TRANS_SLV_TO_ENR_15P`. Tên pipeline hiện hành là tên `NB_SETUP_POI_AMENITY` ghi: `PL_VV_TRANS_SLV_TO_ENR_15M`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | fixed | `lang` nguồn đổi về `string`. Target `STRING NOT NULL` và `quality_gate` chặn khóa NULL ghi riêng ở §1.1. | |
| SQL-002 | P1 | fixed | Cột `media_dedup_key` ghi `string`. Nullability nguồn là `MISSING`. Target `media_id` `STRING NOT NULL` và `quality_gate` ghi riêng. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-26: Người dùng yêu cầu xử lý tiếp cho đến khi task xong. Không còn lựa chọn mở. Chuyển `ready_to_merge`.

## Lịch sử quyết định

- 2026-10-26 D1: Code là nguồn đúng. Chỉ sửa lệch trong `## Bảng lệch mapping`. Chỗ notebook và DDL không ghi thì để MISSING.
- 2026-10-26 SQL-001 fixed: `lang` nguồn là `STRING` không `NOT NULL`. Target và `quality_gate` ghi riêng.
- 2026-10-26 SQL-002 fixed: nullability `media_dedup_key` là `MISSING`. Target `media_id` `STRING NOT NULL`.
- 2026-10-26: `gld_srv_poi_info.poi_id` nguồn trả về `string`. DDL entity là `STRING`, không `NOT NULL`. Target `STRING NOT NULL`. `quality_gate` chặn khóa NULL.
- 2026-10-26: Người dùng yêu cầu xử lý tiếp cho đến khi task xong. Review round 2 đã PASS. Chuyển `ready_to_merge`.
