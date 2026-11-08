# Proposal — 20261104-extract-cms-raw-data

## Phạm vi

- Task gốc: `20261104-extract-cms-raw-data` (`task-state.yaml`: `status: triage`, `scope.systems`: `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_ctrl`).
- Đề xuất này chỉ chọn `load_mode` cho extract bronze `lh_vv_bronze.dbo.cms_raw_data` trong ba giá trị đang có (`CDC`, `DOC`, `DOC_ARRAY`), chọn chỗ đặt extract (notebook theo nguồn), và xếp từng khối đã parse của `raw_payload` vào `DOC` hoặc `DOC_ARRAY`. Đề xuất dừng ở đó để người dùng chốt bảng silver đích.
- Ngoài phạm vi: tên và grain bảng silver đích, cột khóa, `json_path`, rule chuyển kiểu, và thiết kế kiến trúc (invariant, sở hữu state, ranh giới commit, thứ tự, idempotency, retry, recovery).
- Ledger `Quyết định hiện hành` trong `decision.md` chưa có dòng nào. Mọi dòng không nêu trong đề xuất này giữ nguyên như đã quyết định trước đó (đã land).

## Căn cứ

Đề xuất trả lời các mục sau của `problem-analysis.md`. Phần nội dung không chép lại ở đây.

- `## Hiện trạng` → `### Miền load_mode trong thư viện` (H1–H3), `### Mode CDC (partner)` (H4–H7), `### Mode DOC / DOC_ARRAY (3rd-party)` (H8–H13), `### Cấu hình ctrl` (H14–H15), `### Quy ước đặt tên` (H16–H17), `### Dòng mẫu cms_raw_data` (H18–H21).
- `## Khoảng trống hoặc nguyên nhân` → K1 (vì sao không chọn `CDC`), K2 (vì sao dùng snapshot nhưng không dùng lại notebook 3P), K3–K9 (các điểm còn trống, chuyển sang `## Câu hỏi`).
- `## Đối tượng bị ảnh hưởng`: danh sách đối tượng dùng cho `## Dòng thay đổi`.
- `## Câu hỏi`: các câu 1–16, giữ lại ở `## Câu hỏi` bên dưới vì constraint chưa đóng câu nào.

## Giải pháp đề xuất

### Các phương án

| # | Phương án | Đánh giá |
|---|---|---|
| A | `CDC`: đọc `cms_raw_data` bằng notebook partner hoặc bằng một notebook theo luật partner | Loại. Dòng mẫu không có cột Debezium nên luật partner xếp nó vào `TOMBSTONE` (K1). Constraint cấm gán `CDC` khi chưa có event Debezium thật. |
| B | `DOC` / `DOC_ARRAY` qua notebook 3P hiện có, chỉ đổi tham số `src_tbl` | Loại. Hằng số nguồn của notebook 3P cố định `normalized_payload`, `source_id`, `language_code`. Luật phân loại số 1 sẽ reject mọi dòng (K2). Một notebook phục vụ một nguồn (H17). |
| C | `DOC` / `DOC_ARRAY` qua một notebook extract mới theo nguồn (`NB_EXTRACT_<NGUỒN>_CDC_BRZ_TO_SLV`). Notebook gọi `load_table_specs` với `SNAPSHOT_MODES` và có hằng số nguồn riêng cho `cms_raw_data` | **Chọn.** |

### Lý do chọn C

- Dòng mẫu có dạng "một event = một tài liệu", là loại dữ liệu `DOC` / `DOC_ARRAY` phục vụ (K2). Cả hai mode đã có trong `LOAD_MODES` và `SNAPSHOT_MODES`, nên không cần thêm giá trị mới.
- `load_table_specs(ctx, allowed_modes)` đã nhận `SNAPSHOT_MODES` từ phía 3P, nên không phải sửa chữ ký mode trong `NB_LIB_EXTRACT_RAWDATA`.
- Notebook mới chỉ là notebook theo nguồn, đúng mẫu tên `NB_EXTRACT_<NGUỒN>_CDC_BRZ_TO_SLV`. Chữ `CDC` trong tên là mẫu đặt tên, không phải `load_mode`.
- Chỉ những điểm sau khác 3P: cột payload, định danh tài liệu, cột ngôn ngữ (nếu có), và luật phân loại phụ thuộc định danh. Các điểm này để trống, chờ trả lời ở `## Câu hỏi`. Notebook 3P và notebook partner giữ nguyên.
- Notebook mới không gắn vào activity của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` (constraint). Chưa rõ notebook sẽ chạy theo pipeline hay lịch nào (Câu hỏi 11).

### Phân loại khối của `raw_payload` (theo dòng mẫu, không phải hợp đồng schema)

| Khối (`src_object`) | Dạng JSON trên dòng mẫu | `load_mode` đề xuất | Ghi chú |
|---|---|---|---|
| `$` (các trường vô hướng cấp gốc) | object | `DOC` | Một dòng / tài liệu. `$` không dùng với `*_ARRAY` (H15). |
| `cover_gallery` | array of object | `DOC_ARRAY` | Trong mỗi phần tử có object lồng `formats.*` và `provider_metadata`. Đây là trường của phần tử, không phải khối riêng. Khóa con của `formats.*` chưa có bằng chứng (Câu hỏi 14). |
| `SEO` | array of object | `DOC_ARRAY` | |
| `FAQ` | array of object | `DOC_ARRAY` | |
| `experiences` | array of object | `DOC_ARRAY` | |
| `highlight` | array of object | `DOC_ARRAY` | |
| `pois` | array, phần tử `MISSING_EVIDENCE` | Không xếp | Không thiết kế bảng từ khối này (K7, constraint). |

- Cấp gốc không có khối object nào ngoài các mảng (H20). Vì vậy ngoài `$`, không có khối `DOC` nào khác.
- Bảng trên chỉ gợi ý khối nào có thể thành bảng đích. Người dùng chốt bảng nào được tạo, tên, grain, khóa và cột cần giữ (Câu hỏi 1–2). Đề xuất dừng tại đây.

## Dòng thay đổi

| Bảng | Cột | Hành động cũ (đã land) | Hành động mới |
|---|---|---|---|
| `NB_LIB_EXTRACT_RAWDATA` (§1 constants) | `LOAD_MODES` / `SNAPSHOT_MODES` | `CDC, DOC, DOC_ARRAY` / `DOC, DOC_ARRAY` | Giữ nguyên. |
| `NB_LIB_EXTRACT_RAWDATA` | chữ ký `load_table_specs(ctx, allowed_modes)` | Partner dùng mặc định `("CDC",)`, 3P truyền `SNAPSHOT_MODES` | Giữ nguyên. Notebook mới truyền `SNAPSHOT_MODES`. |
| `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` | toàn bộ | Đọc `partner_raw_data`, chỉ `CDC` | Giữ nguyên. |
| `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | hằng số nguồn, luật phân loại | Cho `brz_3rd_crawler_poi_stream` | Giữ nguyên. |
| `NB_EXTRACT_<NGUỒN>_CDC_BRZ_TO_SLV` (mới) | hằng số nguồn (`RAW_PAYLOAD`, `RAW_EVENT_ID`, `RAW_DOC_ID`, `RAW_LANG`, `ARRAY_MODES`) | Không có | Tạo notebook theo nguồn, chỉ nhận `DOC` / `DOC_ARRAY`. Giá trị hằng số chờ Câu hỏi 3, 6, 9. `ARRAY_MODES` = `DOC_ARRAY`. Tên `<NGUỒN>` chờ Câu hỏi 11. |
| `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` | `src_tbl`, `trg_schema`, `trg_tbl`, `load_mode`, `is_active` | Không có dòng cho `cms_raw_data` | Thêm một dòng / bảng đích được chốt, `src_tbl = cms_raw_data`, `load_mode` theo bảng phân loại khối. `trg_tbl` chờ Câu hỏi 1. |
| `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` | `pl_name` | Không có dòng cho `cms_raw_data` | Chờ Câu hỏi 11. |
| `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` | `align_path` | Không có dòng cho `cms_raw_data` | Không đề xuất. Chưa có yêu cầu ghép mảng theo vị trí. |
| `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` | toàn bộ | Không có dòng cho `cms_raw_data` | Chờ bảng đích, khóa và cột (Câu hỏi 1–3). Xem `## ctrl_cfg_schema_registry`. |
| `lh_vv_ctrl.dbo.ctrl_mng_watermark` | dòng cấp nguồn, `watermark_column` | Không có dòng cho `cms_raw_data` | Thêm một dòng cấp nguồn. Id và `watermark_column` chờ Câu hỏi 10, 12. |
| `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` | Chỉ chạy `partner_raw_data` | Giữ nguyên. Không gắn `cms_raw_data`. |
| `NB_CREATE_DDL` / `NB_SETUP_INITIAL_DDL` | seed ctrl cho `cms_raw_data` | Không có | Thêm seed sau khi người dùng chốt bảng đích. Nội dung seed chờ Câu hỏi 1–3, 10–12. |

## ctrl_cfg_schema_registry

Không áp dụng. Chưa có bảng đích, grain, khóa, cột cần giữ hay định danh tài liệu (Câu hỏi 1–3), nên đề xuất không tạo dòng registry nào và không đặt `json_path` nào.

## Ràng buộc cho Architect

1. `load_mode` của mọi dòng `cms_raw_data` chỉ nhận `DOC` hoặc `DOC_ARRAY`. Không dùng `CDC` khi chưa có event Debezium thật. Không thêm giá trị vào `LOAD_MODES`.
2. Không sửa chữ ký mode trong `NB_LIB_EXTRACT_RAWDATA`. Notebook mới gọi `load_table_specs` với `SNAPSHOT_MODES`.
3. Không đổi hành vi hay hằng số của `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` và `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`.
4. Không gắn `cms_raw_data` vào activity của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.
5. Không coi cột `type` là `language_code` hay entity type. Không coi `locale` là `RAW_LANG` / `_langs` khi người dùng chưa chốt (Câu hỏi 7, 9).
6. Không suy ra định danh tài liệu hay `doc_key_column` từ các trường trên dòng mẫu khi người dùng chưa chốt (Câu hỏi 3).
7. Không thiết kế bảng từ `pois[]`. Không đặt `json_path` cho khóa con `cover_gallery[].formats.*` vì chưa có bằng chứng.
8. Không suy ra kiểu Delta của các cột bronze từ một dòng mẫu (Câu hỏi 4). Một dòng không phải hợp đồng schema.
9. Không ghi giá trị mẫu, URL, chữ ký, tên riêng hay nội dung mô tả vào artifact, seed hay registry.
10. Bảng đích và dòng registry chỉ được tạo sau khi người dùng chốt Câu hỏi 1–3.

## Câu hỏi

1. Bảng silver đích của `cms_raw_data` gồm những bảng nào, và dùng tiền tố nguồn nào? Hiện chỉ có `slv_pn_`, `slv_3p_poi_`, `slv_pm_` `[PROPOSED]`. Trong các khối ở bảng phân loại (`$`, `cover_gallery`, `SEO`, `FAQ`, `experiences`, `highlight`), khối nào thành bảng?
2. Mỗi bảng đích có grain gì, cột khóa nào, và giữ những cột nào?
3. Cột hoặc trường nào định danh một tài liệu CMS (tương đương `RAW_DOC_ID` và `doc_key_column` của 3P), khi dòng mẫu không có `source_id`?
4. Kiểu Delta thật của `event_id`, `source_name`, `type`, `crawled_at`, `ingested_date`, `raw_payload` trong `lh_vv_bronze.dbo.cms_raw_data` là gì?
5. Mỗi event của `cms_raw_data` có luôn là một tài liệu đầy đủ (snapshot) không? Nguồn có tín hiệu xóa hay event Debezium (`before`, `after`, `op`, `source`) nào không?
6. Payload cần đọc có phải `raw_payload` không? Bảng có cột payload nào khác không?
7. Cột `type` có nghĩa gì, có những giá trị nào, và có dùng để lọc hay phân bảng không?
8. `source_name` có những giá trị nào? Có cần một tham số lọc nguồn giống `sources` của 3P không?
9. `locale` trong payload có phải ngôn ngữ của tài liệu không? Nó có cần đối ứng với `RAW_LANG` / `_langs` không?
10. Cột thứ tự event là cột nào (dùng làm `watermark_column`), và khi trùng thì xếp theo cột nào?
11. Notebook extract mới tên gì (`<NGUỒN>`)? Pipeline, activity hay lịch nào chạy nó, khi không được gắn vào activity của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`? `pl_name` của các dòng `ctrl_mng_pipeline_config` cho `cms_raw_data` là gì? Notebook 3P hiện được gọi thế nào?
12. Dòng watermark và khóa chống chạy chồng của `cms_raw_data` có id và `watermark_column` gì?
13. Phần tử của `pois[]` có hình dạng gì? Khi nào có mẫu có phần tử?
14. Khóa con của `cover_gallery[].formats.{large,small,medium,thumbnail}` có những gì, và có cần giữ không? `provider_metadata` của phần tử có cần giữ không?
15. Notebook cũ `2.2 nb_cms_transform` có đọc `cms_raw_data` không? Nó có liên quan tới cutover của extract mới không?
16. `cms_raw_data` có được Eventstream ghi append-only giống hai bảng raw hiện có không? Bảng có cho phép đọc theo version Delta không?
