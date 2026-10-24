# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-SRV-01 | Phạm vi | Một task. Tạo và ghi hai bảng gold serving theo đúng hai file mapping. Không tách mỗi bảng một task. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-02 | Schema | Lakehouse.schema là `lh_vv_gold.dbo`. Không đặt hai bảng này vào schema `enr`. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-03 | Cột | Cột và phép biến đổi chỉ lấy từ hai file mapping. `is_verified` và `is_bookable` là null. `created_at` và `updated_at` là timestamp hệ thống. | Yêu cầu người dùng; mapping info §1.2 | 2026-10-24 |
| D-SRV-04 | Model cũ | `docs/context/01_DATA_MODEL.md` §7 đang mô tả `gld_srv_poi_multi_lang` kiểu cũ. Hai file mapping thắng §7 khi lệch cột hoặc nguồn. Không tạo `gld_srv_poi_registry` hay `gld_srv_poi_destination_membership`. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-05 | Notebook | Notebook mới theo tên bảng: `NB_GLD_SRV_POI_MULTI_LANG` và `NB_GLD_SRV_POI_INFO`. Một notebook một bảng đích. Không thêm tầng điều phối. Không gắn hai bảng vào `PL_VV_TRANS_SLV_TO_ENR_15P` khi mapping không nói vậy. | Yêu cầu người dùng; `02_NAMING_CONVENTION.md` §2 | 2026-10-24 |
| D-SRV-06 | DDL | DDL ở cả `NB_SETUP_INITIAL_DDL` và `NB_CREATE_DDL`. Setup sửa định nghĩa tại chỗ. Create chỉ thêm markdown `[THÊM dd/mm] <task-id>` và một cell patch tự chứa ở cuối. Không `DROP` bảng. §2.1 mục 7 nói bảng gold qua `ensure_target` không có DDL ở hai notebook; yêu cầu này vẫn bắt có DDL. | Yêu cầu người dùng; `02_NAMING_CONVENTION.md` §2.1 | 2026-10-24 |
| D-SRV-07 | Giờ mở cửa | `operating_hours` làm đúng mục 1.3 và ra đúng JSON của từng case ở 1.4. Kiểu STRING. | Yêu cầu người dùng; mapping info §1.3, §1.4 | 2026-10-24 |
| D-SRV-08 | Cột thiếu | Nguồn thiếu cột so với mapping thì không tự thêm cột silver và không bỏ cột gold. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-09 | Tầng | Gold serving đọc thuộc tính POI đã enrich và địa chỉ enrich, rồi mới biến đổi giờ mở cửa. Hai bảng kia là sản phẩm đưa ra ngoài, không tính lại ở silver. | Yêu cầu người dùng | 2026-10-24 |
| D-SRV-10 | source_name | lấy source_name từ slv_poi_entity_non_enrich theo poi_id | Câu trả lời Q1 | 2026-10-24 |
| D-SRV-11 | Cột destination | thêm các cột này destination_id, country_code, postal_code, lat, lng vào slv_enr_poi_destination | Câu trả lời Q2 | 2026-10-24 |
| D-SRV-12 | poi_id i18n | poi_id của slv_pn_business_service_i18ns cũng tính giống như cách đang xử lý poi_id của slv_pn_business_service_i18ns ở slv_poi_entity_non_enrich. | Câu trả lời Q3 | 2026-10-24 |
| D-SRV-13 | description | Partner thì description lấy bio. Khi bio null, lấy description của slv_enr_poi_info_multi_lang | Câu trả lời Q4 | 2026-10-24 |
| D-SRV-14 | is_recommended | is_recommended là true khi source_name = partner. Nguồn khác là false | Câu trả lời Q5 | 2026-10-24 |
| D-SRV-15 | Nhãn ngày | Tôi đã nhầm. Nguồn 0 là chủ nhật, 1-6 là thứ 2 đến thứ 7. Label đi theo 2 cách là giống nhau. | Câu trả lời Q6 | 2026-10-24 |
| D-SRV-16 | is_closed | Ngược lại là false. | Câu trả lời Q7 | 2026-10-24 |
| D-SRV-17 | close_time | Sửa lại sample, sample của tôi nhầm. Chỉnh lại ý 5: close_time = close_hour và close_minute (sample: nếu "close_time": 7 và "close_minute": 0 -> 07:00). Mapping ghi sample bằng `close_hour` vì cùng câu nói `close_hour` và case 1 dùng `close_hour`. | Câu trả lời 2026-10-24; mapping info §1.3 ý 5 | 2026-10-24 |
| D-SRV-18 | Giờ partner | Rule Google là mục 1.3. Partner theo mục 1.5: object bảy thứ, giờ lấy từ một phần tử `hours`, chuỗi `open_time`/`close_time` giữ nguyên. Không đọc `status`. Nhiều phần tử trong một ngày thì dừng. | Probe partner_hours_shape; mapping info §1.5 | 2026-10-24 |
| D-SRV-19 | Grain multi_lang | Merge theo grain multi_lang (poi_id, lang). | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-20 | Grain info | gld_srv_poi_info có grain là poi_id | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-21 | Destination trùng | destination trùng poi_id ưu tiên bản ghi đến sau (updated_at lớn hơn) | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-22 | pl_name | PL_VV_TRANS_SLV_TO_GLD_30P | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-23 | Khung trước data | 2 bảng slv_enr_poi_destination, slv_enr_poi_info_multi_lang hiện tại chưa có data, tôi đang dựng trước khung, khi nào có tôi sẽ làm task mới để review và test lại sau | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-24 | Write path | Chọn A. MERGE qua `run_node`: cột mapping cộng `row_hash`, `created_at`, `updated_at`, `deleted_at`. Không thêm `is_active`. Dòng không còn trong build thì gán `deleted_at`. Khoá MERGE NOT NULL. | Câu trả lời 2026-10-24; `TECH_COLUMNS` lib | 2026-10-24 |
| D-SRV-25 | Google null | Google opening_hours_text null -> Để operating_hours null | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-26 | Nhiều period | Nếu có nhiều phần tử trở lên cùng một số day_of_week, vẫn xử lý đầy đủ, không gom. Mỗi phần tử thành một object đích, cùng day_of_week và label. | Câu trả lời 2026-10-24; mapping info §1.3 ý 9 | 2026-10-24 |
| D-SRV-27 | Khoá null | `poi_id` hoặc `lang` null thì dừng lần chạy. Không bỏ dòng và không ghi khoá null. | Hệ quả D-SRV-24 | 2026-10-24 |
| D-SRV-28 | Không có entity | Dòng `slv_enr_poi_info_multi_lang` không có entity thì giữ. `source_name` null. `description` lấy bảng enr. | Mapping multi_lang §1.1 | 2026-10-24 |
| D-SRV-29 | Vòng review thêm | Đồng ý duyệt thêm một vòng review | Câu trả lời 2026-10-24 | 2026-10-24 |
| D-SRV-30 | STATE-001 | Accept risk. Tiếp tục xử lý task này đi | Câu trả lời 2026-10-24 | 2026-10-24 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

### Còn mở

- D-SRV-21 không nói `updated_at` bằng nhau hoặc null. Không tự thêm khoá sắp xếp thứ hai.
- Repo không có pipeline tên `PL_VV_TRANS_SLV_TO_GLD_30P`. Giữ đúng tên này. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15P`.
- `NB_SLV_POI_ENTITY_NON_ENRICH` cell 4 có `pk=("poi_id",)`. Registry `slv_pn_business_service_i18ns` có khoá `business_service_id`, `locale`.
- D-SRV-11 chỉ thêm cột. Không có notebook ghi `destination_id`, `country_code`, `postal_code`, `lat`, `lng`. Gold lấy 1-1, nên null khi landing null.
- Mapping không lọc `deleted_at`. Không thêm lọc đó.
- Probe `gld_srv_input_shape`: entity 24 partner và 41 google, không `deleted`, không trùng `poi_id`. Google có 1 null, 8 `multi_period_day`, 3 `all_day_exact`, 2 `close_day_differs`. Partner có 13 null, 10 một phần tử `hours`, 1 thiếu `hours`, không có mảng dài hơn 1. `slv_enr_poi_destination` và `slv_enr_poi_info_multi_lang` 0 dòng theo D-SRV-23.
- `updated_at` bằng nhau hoặc null: không có khoá sắp xếp thứ hai, lần chạy dừng. Không chọn dòng.
- D-SRV-30: người dùng `accepted-risk` cho `STATE-001` và yêu cầu tiếp tục. `_refresh_lock` giữ nguyên trong cell.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- SQL-001: `srvpoipy` đối chiếu đủ `pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`, `is_active`, `priority`, `load_mode`, `nb_name` và `n = 1` trước khi ghi và sau khi ghi. Kiến trúc chỉ đối chiếu `(src, trg)`, `is_active` và `n`.
- STATE-001: `srvpoipy` gọi `_refresh_lock()` ngay trước `ALTER`, trước mỗi `CREATE`, và trước `INSERT`. Hết hạn lease thì dừng, không ghi. Kiến trúc chỉ lấy khoá một lần ở đầu cell.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | fixed | `srvpoipy` đối chiếu đủ payload của cạnh trước khi ghi và sau khi ghi. | |
| STATE-001 | P1 | accepted-risk | Accept risk. Cell đã có `_refresh_lock` trước mỗi lần ghi. Không còn vòng review để xác nhận lại. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-24, nguyên văn Q1–Q10, ghi ở D-SRV-10 đến D-SRV-19.

## Lịch sử quyết định

- 2026-10-24 triage. Đối chiếu mapping với `NB_SETUP_INITIAL_DDL` (`init_tables`, registry `slv_pn_business_service_i18ns`) và `NB_SLV_POI_ENTITY_NON_ENRICH` cell 4. Chưa gọi `run-author`.
- 2026-10-24. Ghi nguyên văn Q1–Q10. D-SRV-11 là ngoại lệ đã được người dùng chốt của D-SRV-08, chỉ năm cột destination. Công thức `poi_id` mà D-SRV-12 chỉ tới nằm ở `NB_SLV_POI_ENTITY_NON_ENRICH` cell 4: `uuid_md5(id, lit('partner'))`, `id` là `business_service_id`. Dòng không phải partner vẫn lấy `description` của `slv_enr_poi_info_multi_lang` theo mục 1.1; Q4 không sửa câu đó.
- 2026-10-24. Probe: 362 dòng, 36 không null, locale ko 14 / en 11 / vi 11, 36 object, 0 JSON lỗi, 33 object đủ `hours`, 3 object chỉ `status`. Sửa hai file mapping.
- 2026-10-24. Ghi D-SRV-20, D-SRV-21, D-SRV-22. `updated_at` hoà hoặc null chưa được chọn. Tên pipeline không có file trong repo.
- 2026-10-24. Ghi probe `gld_srv_input_shape` và D-SRV-23. B5 không xuất hiện. B2 và B3 có trong 41 dòng Google. B1 chưa trả lời.
- 2026-10-24. D-SRV-24 chọn A. D-SRV-25: Google null thì `operating_hours` null. `multi_period_day` đang được giải thích, chưa có rule.
- 2026-10-24. D-SRV-26: nhiều phần tử cùng `day_of_week` thì mỗi phần tử một object, không gom. Partner vẫn dừng khi một ngày có nhiều phần tử `hours`, vì câu này nói số `day_of_week`.
- 2026-10-24. D-SRV-24 không thêm `is_active`. D-SRV-27 dừng khi khoá null. D-SRV-28 giữ dòng multi_lang không có entity. Model mới thay `model-design.md`.
- 2026-10-24. Review round 1: SQL-001 P1 fixed. Kiểm tra cạnh gold gồm đủ payload, không chỉ `(src, trg)`.
- 2026-10-24. Probe `gld_srv_edge_payload` pass. Lần một: `destination +5`, tạo hai bảng gold, 6 cạnh. Lần hai: `destination +0`, `gold tạo []`, cùng 6 cạnh. Probe: `edge_n 6`, `payload_match True`, ba `cols match True`. Gate evidence chuyển `pass`. Review chưa có verdict PASS vì cap 2.
- 2026-10-24. D-SRV-29: "Đồng ý duyệt thêm một vòng review". Cap review thành 3.
- 2026-10-24. Review round 3: STATE-001 P1. `srvpoipy` gia hạn lease trước mỗi `ALTER`, `CREATE`, `INSERT`, cùng kiểu `_refresh_lock` của `ohpasspy`.
- 2026-10-24. D-SRV-30: "Accept risk. Tiếp tục xử lý task này đi". Disposition `accepted-risk`. Sang runtime runbook. Không review vòng 4.
- 2026-10-25. Runtime bước 0 pass: `destination +0`, `gold tạo []`, 6 cạnh. Bước 1 pass: 18 `EXISTS_OK`, `to_insert=0`, `status=PLAN`. Bước 2–5 chưa có paste.
- 2026-10-25. Info DRY_RUN SUCCESS, diff 24/0/0, không commit. Info RUN SUCCESS, inserted 24, `trg_version = 1`. Multi_lang FAILED đúng vì đầu vào rỗng. NB_00 PLAN fail vì tên `PL_VV_TRANSFORM_SLV_TO_GLD_30P`; config đang có `PL_VV_TRANS_SLV_TO_GLD_30P`.
- 2026-10-25. PLAN đúng tên: 2 node, 6 cạnh, `status=PLAN`. RUN info lần 2: 0/0/0, `trg_version` vẫn 1. K1: 24, 24, 24, 13, 11, 0, 0, 0. Bước 5 Counter chưa chạy.
- 2026-10-25. Bước 5: `Counter({None: 65})`. Kết luận runtime PASS. `gates.runtime=pass`. Chưa chuyển `ready_to_merge`.
- 2026-10-25. Người dùng yêu cầu commit và push `main`. Trạng thái chuyển `ready_to_merge`.
