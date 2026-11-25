# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | `operating_hours` partner | Lấy `poi_opening_hours_json.periods_json` và chạy `google_hours` của `NB_GLD_SRV_POI_INFO` (mapping §1.3). `periods_json` null hoặc `[]` thì `operating_hours` null. Object `policies.operating_hours` không còn trong gold cũ nên không chạy mapping §1.5 và không dựng lại object đó. Khoảng giờ thứ hai mỗi ngày đã mất lúc ghi gold cũ thì không phục hồi. | Người dùng, 2026-11-24. Probe `hours-shape.txt`: 63 dòng partner có khóa `close_hour`, `close_minute`, `day_of_week`, `open_hour`, `open_minute`; 93 dòng là mảng rỗng | 2026-11-24 |
| D-02 | `operating_hours` Google | Lấy `poi_opening_hours_json.periods_json` và chạy cùng `google_hours`. `$.periods` null trên toàn bộ 45521 dòng Google. 36521 dòng có khóa phần tử `close_day`, `close_hour`, `close_minute`, `day_of_week`, `open_hour`, `open_minute`. `close_day` không đọc. `periods_json` null hoặc `[]` thì `operating_hours` null. | Probe `evidence/results/hours-shape.txt`, 2026-11-24 | 2026-11-24 |
| D-03 | `holiday_exceptions` | Google ghi null. Partner copy nguyên chuỗi `poi_opening_hours_json.holiday_exceptions_json`, không parse. Thiếu khóa trong notebook cũ đã thành `[]` thì giữ chuỗi `[]`. Không đọc `$.policies.holiday_exceptions` vì khóa đó không còn trong gold cũ. | Người dùng, 2026-11-24. Entity Google là `lit(None)`. Partner entity giữ chuỗi JSON | 2026-11-24 |
| D-04 | Ba cột lệch đã có rule | `rating_count`: chỉ Google, từ `poi_rating.total_reviews`, null khi nguồn null, không coalesce 0. `review_count`: chỉ Google, `COUNT(*)` dòng `poi_review`, không có dòng thì null. `is_recommended`: true khi `source_name` là partner, còn lại false. | Mapping `gld_srv_poi_info` và `NB_GLD_SRV_POI_INFO` | 2026-11-24 |
| D-05 | Dòng giờ không đúng shape | Dòng `google_hours` trả mã lỗi thì `operating_hours` null, trừ dòng `is_24_7` true thì theo D-07. Init vẫn ghi các dòng khác. Summary đếm từng mã lỗi. Cả lần init không dừng vì một dòng. | Người dùng, 2026-11-24, sửa 2026-11-25 theo D-07 | 2026-11-25 |
| D-07 | `is_24_7` true | Mọi dòng có `poi_opening_hours_json.$.is_24_7` sau `lower(trim)` bằng `true` thì `operating_hours` là output case 2 của mapping: bảy ngày 1–7, `is_open_all_day` true, `is_closed` false, không có `open_time`, `close_time`, `value`. Không đọc `periods_json` ở những dòng này. Áp cho google và partner. | Người dùng, 2026-11-25. Model mới không có nhánh `is_24_7`. Case 2 là dạng mở cả ngày duy nhất của `google_hours` | 2026-11-25 |
| D-06 | `vi_key` khi trùng `poi_id` mới | Chọn dòng vào sau: `poi_master.created_at` lớn nhất trong các dòng `lang = vi` cùng `poi_id` mới. `created_at` null xếp sau dòng có giờ. Cùng `created_at` thì lấy `legacy_poi_id` lớn hơn theo thứ tự chữ. Áp cho mọi nhóm trùng, không dừng notebook. | Người dùng, 2026-11-25: SQL-001 chọn dòng vào sau. Cột `created_at` có trong `NB_40_GOLD_POI_SERVING` trên `poi_master` | 2026-11-25 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Giá trị giờ có `child_kind` `other` được coi là số của `google_hours`. Số thực làm `GOOGLE_BAD_TIME` và cột của dòng đó null theo D-05. Probe không trả kiểu số.
- 6450 dòng Google có phần tử đầu của `periods_json` với `close_hour`, `close_minute`, `close_day` null. Cả mảng vẫn đưa vào `google_hours`. Probe không mở các phần tử sau phần tử đầu.
- Cờ `is_24_7` không được `google_hours` đọc. Partner mở cả ngày đã ghi thành nhiều phần tử giờ sẽ ra `00:00 - 00:00`, `is_open_all_day` false. Hàm `partner_hours` của model mới cũng không đặt `is_open_all_day` true.

## Sai lệch so với kiến trúc

- D-06 thay `dropDuplicates(["_new"])` không thứ tự trong `vi_key`. Kiến trúc vòng 1 chưa có rule chọn dòng vì review mới nêu SQL-001.
- D-07 đổi nhánh `is_24_7` true khỏi D-05. Cần kiến trúc vòng 2 trước khi sửa code.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-002 | P1 | rejected-false-positive | `total_reviews` đã là `bigint`. `rating_not_exact_bigint_n` = 0 trên probe `review-round1-guards.txt`. Cast sang `bigint` không cắt giá trị. | |
| SQL-001 | P1 | fixed | D-06: `rank1_source_conflict_n` = 0. Vòng 4: `eligible_n` 6462 và `IS_24_7` 6442. Probe `is-24-7-gap20.txt`: 6442 `in_info`, 20 `cmp_conflict`, `cmp_conflict_groups` 200 trùng PLAN. Người dùng chấp nhận giải thích ngày 2026-11-25. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-24: đưa ra quyết định để transform toàn bộ data cũ theo model và bảng mới. Có thể gửi sample nếu cần.

## Lịch sử quyết định

- 2026-11-24: D-01 đến D-05. Init đang đọc `$.hours_weekday_text` và `$.holiday_exceptions`. Google ghi `hours_weekday_text` bằng NULL. Partner không có khóa đó; giờ nằm ở `periods_json`. Partner `holiday_exceptions` nằm ở `holiday_exceptions_json`. Mapping §1.5 và path `$.policies.holiday_exceptions` không còn dữ liệu để chạy. `google_hours` là hàm model mới sẵn có và nhận đúng các khóa `periods_json`. Google `$.periods` chưa có khóa trong trong repo, nên D-02 chờ một sample trước khi sửa code.
- 2026-11-24: Sample D-02 là probe `evidence/probes/hours_shape.py`. Kết quả chỉ có tên khóa và số dòng.
- 2026-11-24: Kết quả `evidence/results/hours-shape.txt`. `$.periods` và `$.holiday_exceptions` null toàn bộ. Khóa giờ là `$.periods_json`. Partner `holiday_exceptions_json` là `[]` trên cả 156 dòng. D-02 sửa đường từ `$.periods` sang `$.periods_json`. Dòng `LEGACY_INIT`: Google 25917 và partner 4 đều null cả hai cột giờ.
- 2026-11-25: Probe `review-round1-guards.txt`: `vi_key_collision_n` = 1, `rating_not_exact_bigint_n` = 0, kiểu `total_reviews` là `bigint`. SQL-002 đóng `rejected-false-positive`. SQL-001 còn mở: một `poi_id` mới có hơn một `legacy_poi_id` với `lang = vi` và `poi_id_status = OK`. Chưa chọn dòng thắng.
- 2026-11-25: Hai `legacy_poi_id` `173ce6f5-67cc-ee6e-d827-695b05fa60ae` và `5c574275-faa0-47c4-48cd-4e415e098158` cùng `source_id` `32895ee7-d6e9-4a95-b40a-f7f3d1385065`, cùng `poi_id` mới `f1468622-7ee3-74c1-7410-f87219148e5c`. Hash `poi_opening_hours_json`, `poi_address_json`, `poi_contact_json` giống nhau (`evidence/results/vi-key-detail-hash.txt`). Chưa so media, content, amenity, destination.
- 2026-11-25: Người dùng chọn SQL-001 lấy dòng vào sau. D-06 dùng `poi_master.created_at`.
- 2026-11-25: Probe `vi-key-rank1-source.txt` trả `rank1_source_conflict_n` = 0. SQL-001 giữ `fixed`. Review đã hết cap 2 vòng, nên chưa có vòng review xác nhận disposition này.
- 2026-11-25: Người dùng duyệt một vòng review thêm. `review_plan.extra_round_approved_on` = 2026-11-25.
- 2026-11-25: PLAN `lgp-200ee509c66b41c2af9ac0b1f30a54b5`. Pin `poi_master` 8065, `poi_enrichment_display` 6489, `poi_detail` 6912, `poi_review` 69, `poi_rating` 63. `map.drift_n` = 0, `rating_cast_fail_n` = 0, `rating_conflict_n` = 0, `review_count_dup_n` = 0, `detail_conflict_n` = 0, `vi_key_collision_n` = 1. `hours_reason`: `OK` 29988, `NO_PERIODS` 9058, `GOOGLE_BAD_TIME` 6430. `info.to_insert` = 0, `present_live` = 45476. Chưa RUN.
- 2026-11-25: Probe `google-bad-time-cause.txt`: 6450 dòng Google, tất cả `cause = close_null` và `is_24_7 = true`. Không có `open_null` hay số không nguyên. `google_hours` không đọc `is_24_7`, nên các dòng này thành `GOOGLE_BAD_TIME`. PLAN info chỉ có 6430 dòng mã đó.
- 2026-11-25: Người dùng yêu cầu mọi dòng `is_24_7 = true` ra dạng mở cả ngày của model mới, và duyệt thêm kiến trúc cùng review. D-07 ghi output đúng case 2. Việc này nằm trong task hiện tại.
- 2026-11-25: Người dùng chấp nhận D-07 và duyệt review vòng 4. `second_extra_round_approved_on` = 2026-11-25. PLAN `lgp-3ac94c58324840ccbe123a6fc63b31f2` với `p_pin_json` rỗng in pin `poi_master` 8074, `poi_enrichment_display` 6495, `poi_detail` 6920, `poi_review` 69, `poi_rating` 63. `hours_reason`: `IS_24_7` 6442, `OK` 29978, `NO_PERIODS` 9056. Không có `GOOGLE_BAD_TIME`. Tổng bằng `candidates` 45476. `hours_24_7_partner_n` = 0.
- 2026-11-25: PLAN khóa pin `lgp-acfe492d29374536abd9e56f0fcc8838` trùng các số giờ của PLAN pin trống. Đếm `is_24_7` trên mọi dòng Google `lang = vi`: `eligible_n` 6462, `bad_n` 0, `unexpected_n` 0. Lệch 20 so với `IS_24_7` 6442 vì probe không đi qua bộ lọc ứng viên info.
- 2026-11-25: Probe `evidence/results/is-24-7-gap20.txt`. `flagged_legacy_n` 6462, `in_info_new_id_n` 6442, `cmp_conflict_groups` 200. `by_reason`: `cmp_conflict` 20, `in_info` 6442. 20 dòng Google `is_24_7` true không vào info vì `new_id` thuộc nhóm `size(_cmp) > 1`, cùng số nhóm `cmp_conflict_n` 200 của PLAN. Không có `no_map`, `not_kept`, hay `chosen_legacy_not_flagged`.
- 2026-11-25: Người dùng chấp nhận giải thích 20 dòng `cmp_conflict`. SQL-001 giữ `fixed`. RUN `lgp-0141b690fb824d51a542a63c11d8ce47`, pin `poi_master` 8074, `poi_enrichment_display` 6495, `poi_detail` 6920, `poi_review` 69, `poi_rating` 63. `info.commit` COMMITTED, `info.inserted` 0 bằng `to_insert` 0, `v_pre` 21, `v_post` 22. `hours_reason` trùng PLAN: `NO_PERIODS` 9056, `IS_24_7` 6442, `OK` 29978. `media.inserted` 209, `media.commit` COMMITTED. Pin trong `runtime-runbook.md` sửa từ bộ 8065/6489/6912 sang bộ pin của RUN này.
- 2026-11-25: K1 `dup_poi_id_n` 0. K2 cả hai chiều 0. K3 Google `oh_null` 6847, `all_day_n` 4953, `all_day_bad_n` 0, `he_nonnull` 0. Partner `he_nonnull` 4, `all_day_n` 0. K4 partner `rc_nonnull` 0, `rvc_nonnull` 0, `rec_true` 4. Google `rec_true` 0. Khoá `SUCCESS`, `lock_exec_id` null. History info version 22 là `MERGE` `LEGACY_INIT:lgp-0141b690fb824d51a542a63c11d8ce47`. Không có version lớn hơn 22. Đối chiếu không chặn: `all_day_n` 4953 so với `IS_24_7` 6442, partner holiday 4 so với 125, Google `rvc_nonnull` 25676 so với `review_matched_n` 40197.
- 2026-11-25: PLAN lần 2 `lgp-d31c5e89aa0541f1906e856aa2f38bd9` cùng pin. `to_insert` 0. `hours_reason`, `candidates`, `review_matched_n`, `holiday_partner_nonnull_n`, `review_count_dup_n`, `rating_conflict_n`, `hours_24_7_partner_n` giống PLAN `lgp-acfe492d29374536abd9e56f0fcc8838`. `drift_n` 0, `detail_conflict_n` 0, `rating_cast_fail_n` 0. RUN lần 2 chưa chạy.
- 2026-11-25: Lần chạy `lgp-5664cec5fc404dd7950f7b9027c62ec8` có `mode` `PLAN`, `v_pre` và `v_post` null. Các số giờ giống PLAN lần 2. Không có commit. B4 trước đó `SUCCESS`, `lock_exec_id` null, `last_run_id` vẫn `lgp-0141b690fb824d51a542a63c11d8ce47`. RUN lần 2 vẫn chưa chạy.
- 2026-11-25: RUN lần 2 `lgp-ecaceebb45fc480a97d480f834427086`, `mode` `RUN`, cùng pin. `info.commit` `COMMITTED`, `info.inserted` 0, `v_pre` 22, `v_post` 23. `hours_reason` giống lần đầu. `media.inserted` 0. K1, K2 và so `row_hash` version 22 với 23 chưa có kết quả.
- 2026-11-25: Năm số idempotency đều 0: `dup_poi_id_n`, hai chiều `load_origin IS NULL`, hai chiều `row_hash` của `LEGACY_INIT` giữa version 22 và 23. Khoá `SUCCESS`, `lock_exec_id` null, `last_run_id` `lgp-ecaceebb45fc480a97d480f834427086`. History version 23 là `MERGE`, `userMetadata` `LEGACY_INIT:lgp-ecaceebb45fc480a97d480f834427086`, `numTargetRowsInserted` 0, `numTargetRowsUpdated` 25921. Không có version lớn hơn 23. B5 chưa dán.
- 2026-11-25: Người dùng đóng ba gate `evidence`, `specialist_review` và `risk_gate` bằng bằng chứng đã có. Review vòng 4 giữ verdict `EVIDENCE_REQUIRED` trong file review. Không mở vòng 5. SQL-001 vẫn `fixed`. Bằng chứng là `is-24-7-gap20.txt`, PLAN và RUN đã khớp, K1–K4, và idempotency version 22 với 23.
