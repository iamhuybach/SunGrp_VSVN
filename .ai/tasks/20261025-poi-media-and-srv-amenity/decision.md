# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-MEDIA-12 | Rule `is_cover` | Boolean. Mỗi `poi_id` có đúng một cover. Nhiều bản ghi: order nhỏ nhất khác null. Hòa, hoặc mọi `display_order` đều null: dòng gặp đầu tiên. | Chat U5, U-TIE, A7, A8, 2026-10-26 | 2026-10-26 |
| D-MEDIA-SHAPE | Shape `media` partner trên Fabric DEV | Phần tử có dữ liệu là JSON array of objects. `url` string, `order` int. Không có object gốc. `preview` có hoặc không. | `evidence/results/partner_media_shape.txt` | 2026-10-26 |
| U1 | `pl_name` | `slv_poi_media_info` và `gld_srv_poi_media_gallery`: `PL_VV_TRANS_SLV_TO_GLD_30P`. `gld_srv_poi_amenity`: `PL_VV_TRANS_SLV_TO_GLD_1H`. | Chat U1 và U1-1H, 2026-10-26 | 2026-10-26 |
| U2 | Khóa MERGE media và gallery | `media_id` | Chat U2, 2026-10-26 | 2026-10-26 |
| U3 | Phần tử `url` null hoặc trắng | Bỏ phần tử. Nguồn url: i18n, hoặc services khi media i18n rỗng. | Chat U3, 2026-10-26 | 2026-10-26 |
| U4 | `[]` và JSON null | Tính là rỗng, lấy `slv_pn_business_services.media`. | Chat U4, 2026-10-26 | 2026-10-26 |
| U6 | Soft delete `is_active` | Chuyển `false`. | Chat U6, 2026-10-26 | 2026-10-26 |
| U7 | Partner `deleted` | Loại khỏi silver media. | Chat U7, 2026-10-26 | 2026-10-26 |
| Q9 | `source_name` | `google` và `partner`. | Chat Q9, 2026-10-26 | 2026-10-26 |
| Q11 | `blob_url` partner | Giữ nguyên chuỗi, không trim. | Chat Q11, 2026-10-26 | 2026-10-26 |
| U-TIE | Hòa `display_order` nhỏ nhất | Dòng nào gặp trước là `is_cover`. Không thêm cột sắp. P1: `poi_with_min_tie = 5`. | Chat U-TIE, 2026-10-26 | 2026-10-26 |
| ARCH-R2 | Architecture | PASS. Chưa sửa notebook. | `architecture.md` Main brief | 2026-10-26 |
| DIRTY-DDL | Notebook DDL | Người dùng đã commit `NB_CREATE_DDL.ipynb` và `NB_SETUP_INITIAL_DDL.ipynb`. Main được sửa hai notebook đó và `tests/test_initial_ddl_contract.py`. | Chat 2026-10-26 | 2026-10-26 |
| A7 | Thứ tự cover | `row_number` theo `display_order ASC NULLS LAST, _pos ASC NULLS LAST, media_id ASC`. Partner "gặp trước" là `_pos`. | Chat A7, 2026-10-26 | 2026-10-26 |
| A8 | Cover khi mọi order null | Vẫn có 1 cover. Lấy dòng gặp đầu tiên khi `display_order` là null. | Chat A8, 2026-10-26 | 2026-10-26 |
| REVIEW-R3 | Thêm một vòng review | Đồng ý thêm một vòng review. `review_plan.extra_round_approved_on` = 2026-10-26. Cap review thành 3. | Chat 2026-10-26 | 2026-10-26 |
| R7-SKIP | `gld_srv_poi_multi_lang` trên `_30P` | Bỏ qua. Node cũ FAILED vì `slv_enr_poi_info_multi_lang` rỗng. Hai node media SUCCESS. Không sửa notebook multi_lang trong task này. | Chat 2026-10-26 | 2026-10-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không thêm cột sắp cho "dòng gặp trước".
- Không đổi `PL_VV_TRANS_SLV_TO_GLD_1H` thành `PL_VV_TRANSFORM_SLV_TO_GLD_1H`.
- A1: `row_hash`, `created_at`, `updated_at`, `deleted_at` thuộc `sql_merge_target`. Build không trả các cột này.
- A2: chỉ khóa MERGE là `NOT NULL`.
- A3: năm cạnh mới `RECOMPUTE`, `priority = 1`, `nb_name = NB_<UPPER(trg_tbl)>`, `write_mode = MERGE`.
- A4: `from_json` chỉ khi chuỗi bắt đầu bằng `[`. Document không parse được thì không có dòng và không fallback.
- A5: fallback join `business_service_id = id`. `poi_id` tính từ id i18n.
- A6: bỏ phần tử `url` null hoặc trắng. `order` null vẫn giữ.
- A7: đã chốt. Hòa thì `row_number` theo `display_order ASC NULLS LAST, _pos ASC NULLS LAST, media_id ASC`. Partner "gặp trước" là vị trí trong array.
- A8: đã chốt, khác kiến trúc. Nhiều dòng và mọi `display_order` đều null vẫn có một cover: dòng gặp đầu tiên theo A7.
- A9: trùng `media_id` thì quality gate chặn, không dedupe.
- A10: gold đọc silver qua `ctx.input`, chỉ dòng `deleted_at` null.
- A11: input bắt buộc là `media_3p` và `i18n` ở silver; gallery bắt buộc `media`; gold amenity bắt buộc `amenity`. `soft_delete_set` của gold amenity là rỗng.
- A12: hai cell DDL, mỗi cell một khóa pipeline, `LEASE_MINUTES = 90`.

## Sai lệch so với kiến trúc

- A8: `with_cover` gán `is_cover` cho `row_number = 1` kể cả khi `display_order` của dòng đó là null. Kiến trúc để trường hợp mọi order null không có cover. Người dùng chốt vẫn có một cover. Fixture F7 kỳ vọng cover ở dòng gặp đầu. Kiểm tra runtime: POI còn dòng mà `sum(is_cover) = 0` là lỗi.
- SPARK-001: `partner_media` đọc metric bằng `DataFrame.first()` trên agg một dòng, không phải `F.first()` không thứ tự. `poi_without_cover` ghi 0, không quét lại.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | accepted-risk | Người dùng chấp nhận phần còn lại: lease không được giữ đến lúc MERGE commit. Hai lần `refresh_flow_lock` vẫn còn. Run theo lịch có timeout node 20 phút và lease 90 phút. Run tay hoặc MERGE dài hơn lease vẫn có thể ghi snapshot cũ. Hết cap review 3. | |
| SPARK-001 | P1 | fixed | Vòng 3 xác nhận block metric nằm trong `try/finally` và luôn `unpersist()`. | |
| SQL-001 | P1 | fixed | Full build trên DEV: `rows 1131`, `dup_media_id 0`. Không dedupe. `evidence/results/media_id_unique.txt`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-26: đã sửa `docs/context/mapping_poi_media_info.md`. Main đối chiếu lại registry. Phần lệch hàng của 8 cột `slv_3p_poi_media` được ghi nhận bên dưới. `is_cover` chưa đủ rule.
- 2026-10-26, trả lời D-MEDIA-12:
  1. Mỗi poi_id chỉ có một media là is_cover. Nếu có nhiều order nhỏ nhất, gặp media nào trước thì đấy là is_cover.
  2. is_active là cột ở bảng đích slv.slv_poi_media_info. Ở slv_3p_poi_media không có. Luôn đánh dấu là "true".
  3. created_at và updated_at vẫn lấy theo rule như các bảng khác.
  4. Đã thêm lại rule gld_srv_poi_media_gallery vào mapping.
  5. Đổi hết `slv_pn_business_service` thành `slv_pn_business_services`.
- 2026-10-26, U1–U7 và Q9–Q11, nguyên văn:
  - U1: `slv_poi_media_info` và `gld_srv_poi_media_gallery` theo `PL_VV_TRANS_SLV_TO_GLD_30P`. `gld_srv_poi_amenity` là `PL_VV_TRANS_SLV_TO_GLD_1H`.
  - U2: khóa MERGE của media silver và gallery là `media_id`.
  - U3: url i18n, hoặc nếu media i18n null/rỗng thì url services; url services null hoặc trắng thì bỏ phần tử.
  - U4: `[]` và JSON null tính là rỗng để lấy `slv_pn_business_services.media`.
  - U5: `is_cover` là boolean. Một bản ghi url: `display_order` null vẫn cover. Nhiều hơn một bản ghi: order nhỏ nhất khác null.
  - U6: soft delete thì `is_active` chuyển false.
  - U7: dòng partner `deleted` bị loại.
  - Q9: `source_name` là `google` và `partner`.
  - Q10: `is_cover` là boolean.
  - Q11: `blob_url` giữ nguyên chuỗi.
- 2026-10-26, DIRTY-DDL, A7, A8:
  - DIRTY-DDL: đã commit `NB_CREATE_DDL.ipynb` và `NB_SETUP_INITIAL_DDL.ipynb`.
  - A7: Đồng ý. Main giữ thứ tự đó.
  - A8: Vẫn phải có 1 cover. Lấy dòng gặp đầu tiên khi display_order là null.
- 2026-10-26: Đồng ý thêm một vòng review. Vòng 3 chạy xong, verdict `FIX_REQUIRED`, còn `STATE-001`.
- 2026-10-26: accept-risk `STATE-001`, tiếp tục workflow. `specialist_review` giữ `fix_required`.
- 2026-10-26: hai lần RUN `_30P` lỗi vì `slv_enr_poi_info_multi_lang` không có data, có thể bỏ qua.
- 2026-10-26: R4 0 dòng, R5 0 dòng, R6 version `slv_poi_amenity` vẫn là 1 ngày 2026-10-20, R8 `partner_url_dropped 1` và `poi_without_cover 0`. Runtime `pass`. `specialist_review` vẫn `fix_required`, nên task không vào `ready_to_merge`.
- 2026-10-26, probe `media_id_unique`: `rows 1131`, `dup_media_id 0`, `partner_media_unparsed 0`, `partner_url_dropped 1`, `poi_without_cover 0`, `partner_fallback_docs 0`. Bảng duplicate rỗng.

## Lịch sử quyết định

### 2026-10-25 — D-MEDIA-12 CONFLICT

Registry `slv_3p_poi_media` trong `TABLE_CONFIGS_3P` có khóa `media_dedup_key` và đúng 8 cột nghiệp vụ, theo thứ tự:

| Cột registry | Kiểu | Rule |
|---|---|---|
| `media_dedup_key` | string | `HASH_SHA256_PIPE` trên `_doc.source_name,_doc.source_id,name` |
| `poi_id` | string | `HASH_MD5_UUID` |
| `photo_api_uri` | string | path `name` |
| `display_order` | int | `POS_1BASED` |
| `width_px` | int | `widthPx` |
| `height_px` | int | `heightPx` |
| `blob_url` | string | `blob_url` |
| `photographer` | string | `ARRAY_AT` `authorAttributions` index 0 `displayName` |

`docs/context/01_DATA_MODEL.md` §5.2 ghi cột kỹ thuật L1 3P: `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`, `created_at`, `updated_at`. Registry không có `media_id`, `source_name`, `thumbnail_url`, `is_cover`, `is_active`.

§1.2 viết 14 dòng. Nguồn 3P, nguồn partner, kiểu và target của cùng một dòng không mô tả một field:

| Dòng | Source 3P | Source partner | Kiểu trên dòng | Target |
|---|---|---|---|---|
| 1 | trống | trống | string | `media_id` |
| 2 | `media_dedup_key` | trống | string | `poi_id` |
| 3 | `poi_id` | trống | string | `source_name` |
| 4 | trống | `null` | string | `photo_api_uri` |
| 5 | `photo_api_uri` | `media.order` | integer | `display_order` |
| 6 | `display_order` | `null` | integer | `width_px` |
| 7 | `width_px` | `null` | integer | `height_px` |
| 8 | `height_px` | `null` | string | `photographer` |
| 9 | `photographer` | `media.url` | string | `blob_url` |
| 10 | `blob_url` | `null` | string | `thumbnail_url` |
| 11 | `null` | trống | string | `is_cover` |
| 12 | trống | trống | boolean | `is_active` |
| 13 | `is_active` | trống | timestamp | `created_at` |
| 14 | trống | trống | timestamp | `updated_at` |

`is_cover` chỉ có transform "Chọn theo order bé nhất". Dòng đó ghi kiểu string. Dòng không ghi grain, giá trị của dòng được chọn, giá trị của dòng còn lại, cách xử lý nhiều dòng cùng `order` nhỏ nhất, hay `order` là `display_order` hay `media.order`.

Tên bảng partner trong §1.1 và §1.2 là `slv_pn_business_service` (không có `s`). Registry partner là `slv_pn_business_services` và `slv_pn_business_service_i18ns`. Cả hai cột `media` đều `type: string`. Shape bên trong chuỗi không có trong repo. Chưa viết probe vì CONFLICT đứng trước evidence.

Không gọi `run-author`. Không sửa notebook. Không sửa `mapping_gld_srv_poi_amenity.md`.

### 2026-10-26 — D-MEDIA-12, bản sửa mapping

Người dùng sửa `docs/context/mapping_poi_media_info.md`. Các dòng sau cùng mô tả một field và khớp cột registry `slv_3p_poi_media`:

| Source 3P | Target | Kiểu | Ghi nhận |
|---|---|---|---|
| `media_dedup_key` | `media_id` | string | 3rd 1-1. Partner: `sha2(concat_ws('\|', 'partner', poi_id, trim(media.url)), 256)` |
| `poi_id` | `poi_id` | string | 3rd 1-1. Partner: `uuid_md5(business_service_id, 'partner')` |
| `photo_api_uri` | `photo_api_uri` | string | 3rd 1-1. Partner `null` |
| `display_order` | `display_order` | integer | 3rd 1-1. Partner `media.order` |
| `width_px` | `width_px` | integer | 3rd 1-1. Partner `null` |
| `height_px` | `height_px` | integer | 3rd 1-1. Partner `null` |
| `photographer` | `photographer` | string | 3rd 1-1. Partner `null` |
| `blob_url` | `blob_url` | string | 3rd 1-1. Partner `media.url` |

`source_name` không có cột nguồn. Transform ghi nhãn `google` cho nhánh 3P và `partner` cho nhánh partner. `thumbnail_url` nguồn `null`, transform `null`.

Còn mở:

- `is_cover`: transform vẫn là "Chọn theo order bé nhất". Kiểu trên dòng là string. Chưa có grain, giá trị dòng được chọn, giá trị dòng còn lại, xử lý hòa order, hay order lấy từ cột nào.
- `is_active`: ô source 3P ghi `is_active`. Registry `slv_3p_poi_media` không có cột này. Transform ghi `true`.
- `created_at` và `updated_at`: transform để trống.
- File không còn mục `gld_srv_poi_media_gallery`.
- Mapping vẫn ghi `slv_pn_business_service`. Registry và request ghi `slv_pn_business_services`. Hai cột `media` vẫn là `string`. Chưa viết probe.

Không gọi `run-author`. Không sửa notebook.

### 2026-10-26 — D-MEDIA-12 đã chốt

Người dùng trả lời năm điểm. Mapping được sửa theo đúng câu đó:

- `is_cover`: mỗi `poi_id` một media. Nhiều order nhỏ nhất thì media gặp trước. Kiểu ô mapping vẫn `string`.
- `is_active`: cột đích, không có trên `slv_3p_poi_media`, luôn `true`. Ô source 3P để trống.
- `created_at`, `updated_at`: rule `sql_merge_target` trong `NB_LIB_TRANSFORM_SLV_GLD`. INSERT ghi cả hai bằng `current_timestamp()`. UPDATE khi `row_hash` đổi chỉ ghi `updated_at`. `created_at` không nằm trong SET. Gold gallery và gold amenity cũng dùng cột kỹ thuật của lần MERGE đích, không copy timestamp từ silver.
- §2 `gld_srv_poi_media_gallery` đã có lại: transform 1-1 từ `slv_poi_media_info`, chỉ khác `created_at` và `updated_at`.
- Mọi chỗ `slv_pn_business_service` không kèm `_i18ns` đổi thành `slv_pn_business_services`. `slv_pn_business_service_i18ns` giữ nguyên.

Shape `media` vẫn chỉ là `string` trong registry. Probe `evidence/probes/partner_media_shape.py`. Chưa gọi Author. Chưa ghi hiện trạng `slv_poi_amenity`.

### 2026-10-26 — D-MEDIA-SHAPE

Stdout Fabric DEV ghi ở `evidence/results/partner_media_shape.txt`. Đủ cả bảng: i18n 362, `locale = vi` 121, services 30.

`media` có phần tử là JSON array of objects. Không có dòng object gốc. `url` là `str`, `order` là `int` khi có giá trị. Key `description` và `is_cover` có trên object; kiểu giá trị của hai key này không đo. `preview` có ở 39 dòng `vi` và 3 dòng services, không có ở 34 dòng `vi`. Trong một document, `url` string không trùng (`dup_url_docs = 0`). Tối đa 8 phần tử.

`vi`: array 74, `[]` 26, SQL null 18, JSON null 3 (`NoneType` vì `json.loads` ra `None`). Một array trộn `url` null và string, `order` null và int.

Services: JSON null 27, array 3.

Fallback của probe chỉ là SQL null hoặc `trim` rỗng: 18 dòng `vi`, 0 dòng có `slv_pn_business_services.media`. `[]` và JSON null không nằm trong join đó.

Hiện trạng `slv_poi_amenity` đã ghi vào `docs/context/mapping_gld_srv_poi_amenity.md` từ notebook, DDL và test. Rule gold vẫn là 1-1.

### 2026-10-26 — architecture round 1 EVIDENCE_REQUIRED

`run-author --kind model` ghi `model-design.md` bằng Claude Opus 5.5, effort medium. `run-gate` trả `EVIDENCE_REQUIRED`. Không sửa notebook. Gate architecture không được đánh PASS.

Cần câu trả lời U1–U7 trong `architecture.md` mục Open user decisions, và stdout P1–P5 từ `evidence/probes/media_key_grain.py`. Sau đó chạy lại `run-author --kind model` rồi architecture.

### 2026-10-26 — U1–U7, P1–P3, P4 lỗi

Người dùng chốt U1–U7, Q9, Q10, Q11. Mapping §1.2 đổi `is_cover` sang boolean và ghi rule U5. `blob_url` partner giữ nguyên chuỗi. Soft delete đặt `is_active` false. `[]` và JSON null là rỗng. Phần tử url null hoặc trắng bị bỏ. Dòng partner `deleted` bị loại. Khóa MERGE là `media_id`.

P1: `n = 940`, `n_key = 940`, `null_key = 0`, `null_poi = 0`, `null_order = 0`, `poi_with_min_tie = 5`.
P2: `vi` 121 dòng, 121 id, `vi_deleted = 0`. Services 30 dòng, 30 id, `deleted = 0`.
P3: `vi_empty_any = 47`, `fallback_hits = 0`.
P4 dừng với `NameError: uuid_md5 is not defined`. P5 chưa chạy.

`PL_VV_TRANS_SLV_TO_GLD_30P` có trong `NB_CREATE_DDL`. `PL_VV_TRANS_SLV_TO_GLD_1H` không có. Parameter cell `NB_00_ORCHES_SLV_TO_GLD` là `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. Main không đổi tên. Chưa chạy lại Author.

### 2026-10-26 — U-TIE, U1-1H, P4 và P5

U-TIE: dòng nào gặp trước là `is_cover`. Không thêm cột sắp. U1-1H: giữ `PL_VV_TRANS_SLV_TO_GLD_1H`.

P4: `overlap_vi = 0`, `overlap_services = 0`. P5: `null_url = 1`, `null_order = 1`, `elems = 192`. P1 vẫn `poi_with_min_tie = 5`.




