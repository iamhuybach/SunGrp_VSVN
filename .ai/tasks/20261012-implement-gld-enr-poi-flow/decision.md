# Quyết định

## Giả định còn lại

- `e1` ngày 2026-10-13: 30 dòng active, 30 dòng parse được JSON. Khoá không rỗng: `full_address` 30, `address_line1` 23, `city` 23, `street` 23, `ward` 23, `country` 12. Không có khoá không rỗng tên `district`, `province`, `province_name`, hoặc `state_province`.
- `slv_pn_poi.short_address` lấy `address.full_address`. `e1` xác nhận khoá này không rỗng trên 30/30 dòng. Không đổi công thức `MQ-025`.
- `slv_pn_poi.ward` lấy `address.ward`. Đây là khoá ward duy nhất trong `e1`.
- `slv_pn_poi.name` lấy `slv_pn_business_service_i18ns.name` với `locale = 'vi'`. `e2` có đúng một mã tiếng Việt: `vi` 121 dòng, cùng `ko` 123 và `en` 118. Không có dòng `vi` thì `name` là NULL.
- Người dùng chốt ngày 2026-10-13: bốn cột địa chỉ của `slv_pn_poi` lấy khoá JSON của `slv_pn_business_services.address`. `district` lấy `district`. `province_name` lấy `city`. `ward` lấy `ward`. `short_address` lấy `full_address`. Mẫu người dùng đưa có đủ các khoá `full_address`, `address_line1`, `address_line2`, `street`, `ward`, `district`, `city`, `state`, `zip`, `country`. Khoá `district` có mặt cả khi giá trị là chuỗi rỗng. Không lưu nguyên văn địa chỉ mẫu vào artifact.
- `COL-004`, `COL-005`, `COL-006`, `COL-007` không có cột nguồn trong Mapping mục 5. Ba cột `best_time_*` và `cost` để NULL cho đến khi có nguồn mới. Không lấy `costVnd` và không đọc bảng enrichment đã gỡ.
- Phút của `time_to_spend` không có cột nguồn trong Mapping. Công thức hiển thị trong ghi chú `COL-003` xử lý trường hợp NULL hoặc nhỏ hơn hoặc bằng 0 thành `Không cố định`. Không bịa cột phút.

## Sai lệch so với kiến trúc

Architecture verdict `PASS` ngày 2026-10-13. Các mục dưới đây ghi trước khi sửa code, theo mục 11.5 của `architecture.md`.

- `D-01`: phát hiện thay đổi bằng diff từng dòng đầu vào giữa hai version Delta, so mọi cột, kể cả cột kỹ thuật của silver.
- `D-02`: `slv_pn_poi` dùng RECOMPUTE MERGE của lib, có `row_hash`. Loại `row_hash` của `PC-09` chỉ áp vào ba bảng `gld_enr_*`.
- `D-03`: không lọc `deleted` trên đầu vào partner, theo `MQ-046`. Dịch vụ đã xóa mềm vẫn còn dòng.
- `D-04`: `slv_pn_poi` là bảng L2 nhưng giữ tiền tố `slv_pn_` theo `MQ-063`. Hậu tố `_15P` không khớp `CADENCE_RE`, nên kiểm tra nhịp của lib bỏ qua và ghi WARN.
- `D-05`: DDL gold và seed cạnh nằm trong `NB_CREATE_DDL`, không tạo `NB_SETUP_*`. Lib và hai file context được thêm vào scope.
- `D-06`: không có pre-check không cần Spark. Mỗi 15 phút vẫn mở session Spark trên F16 dùng chung. Để backlog.
- `D-07`: `review_json` của POI 3rd-party không có review là chuỗi `'[]'`. Chỉ dòng partner là NULL.
- `D-08`: `gld_enr_poi_info` chỉ có nguồn 3rd-party. Bỏ nhánh partner và bỏ cạnh `slv_pn_poi` → `gld_enr_poi_info`. Còn 13 cạnh. Info không còn là con của `slv_pn_poi`, nên `slv_pn_poi` lỗi không làm `SKIPPED` notebook info. Coordinate vẫn đọc `slv_pn_poi`.
- `U-01` đã chốt ngày 2026-10-13: chỗ NULL trong `destination_context` thành chuỗi rỗng, câu vẫn được ghép bằng `concat` và `coalesce`.
- `GATE-002` vòng 2 vẫn mở vì guard cũ tách cột kỹ thuật trước khi so thứ tự. Bản sửa sau vòng 2 so từng cột đích đúng vị trí: tên, kiểu và nullability, gồm `created_at` và `updated_at`. Review đã hết 2 vòng nên không gọi vòng 3.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| `PC-01` | P2 | `accepted-risk` | Giữ schema `lh_vv_gold.enr` và tiền tố `gld_enr_`. Người dùng chốt 2026-10-12. Nguồn: `MQ-024`, `BQ-007`. | |
| `PC-03` | P2 | `accepted-risk` | Không tạo bảng `ref_` mới. Không chuyển rule sang `slv_poi_*`. `rule_home` giữ `TEMPLATE_EXCEPTION_NO_RULE_TABLE`. Nguồn: `MQ-054`. | |
| `PC-05` | P2 | `accepted-risk` | Rule nghiệp vụ nằm ở luồng ghi gold này. Gold info và coordinate copy `poi_id` từ silver. `review_id` copy `slv_3p_poi_review.review_id`, không hash lại trên gold. Nguồn: `MQ-062`, `MQ-063`, `docs/context/01_DATA_MODEL.md` mục 2 đã sửa 2026-10-12. | |
| `PC-07` | P2 | `accepted-risk` | Giữ `PL_VV_TRANS_SLV_TO_ENR_15P` và `NB_00_ORCHES_SLV_TO_ENR_15P` dù lệch pattern pipeline và orchestrator. Nguồn: `MQ-028`, `MQ-044`. | |
| `PC-08` | P2 | `accepted-risk` | Giữ `load_mode` `APPEND` dù `docs/context/02_NAMING_CONVENTION.md` mục 6 chưa có giá trị này. Partner và 3rd-party append thành dòng riêng, không join. Nguồn: `MQ-027`, `MQ-058`. | |
| `PC-09` | P2 | `accepted-risk` | `created_at` và `updated_at` đổi mỗi lần ghi. Không dùng `row_hash`. `updated_at` thuộc khoá lịch sử. Nguồn: `MQ-030`, `MQ-039`, `MQ-052`. | |
| `GATE-001` | P1 | `fixed` | APPEND kiểm tra `required_inputs` trước khi build. Input rỗng thành `FAILED`, không append và không tiến watermark. | |
| `GATE-002` | P1 | `fixed` | Vòng 2 vẫn bắt guard tách cột kỹ thuật. Bản sau vòng 2 so toàn bộ schema đích theo vị trí, gồm tên, kiểu và nullability của mọi cột. Hết 2 vòng review nên chưa có verdict mới. | |
| `GATE-003` | P1 | `fixed` | Diff version được `persist` và `count()` trong khối bắt lỗi time travel. Lỗi thì unpersist rồi đọc snapshot hiện tại với `FULL_VERSION_UNAVAILABLE`. | |
| `GATE-004` | P1 | `fixed` | Pipeline không gắn id workspace hay notebook. Tham số `nb_orches_id` và `workspace_id` do môi trường truyền. Activity fail khi giá trị rỗng hoặc chứa `PENDING`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-12: giữ schema `lh_vv_gold.enr` và tiền tố `gld_enr_`.
- 2026-10-12: giữ `APPEND` dù quy ước mục 6 chưa có giá trị này.
- 2026-10-12: giữ `PL_VV_TRANS_SLV_TO_ENR_15P` và `NB_00_ORCHES_SLV_TO_ENR_15P`.
- 2026-10-12: rule nghiệp vụ nằm ở luồng ghi gold này. Không tạo bảng `ref_` mới. Không chuyển rule về `slv_poi_*`.
- 2026-10-12: `created_at` và `updated_at` đổi mỗi lần ghi. Không dùng `row_hash`.
- 2026-10-12: không đọc `destination_ward_mapping`, không đọc bảng `ref`, không đọc `poi_address_enrichment_staging`.
- 2026-10-12: không sửa `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` và không sửa notebook extract partner hoặc 3rd-party.
- 2026-10-12: không commit, push, merge.
- 2026-10-12: không mở lại task `20261012-map-gld-enr-poi-tables`. Không đưa `SRC-006`, `SRC-008`, `DS-004`, `DS-008` vào code.
- 2026-10-13: `slv_pn_poi.district` lấy `address.district`. `slv_pn_poi.province_name` lấy `address.city`. `slv_pn_poi.ward` lấy `address.ward`. `slv_pn_poi.short_address` lấy `address.full_address`. Nguồn là JSON `slv_pn_business_services.address`.
- 2026-10-13: `gld_enr_poi_info` chỉ có nguồn 3rd-party, không có nguồn partner.
- 2026-10-13: `destination_context` khi `short_address`, `district`, `city` hoặc `destination_name` là NULL thì chỗ đó là chuỗi rỗng và câu vẫn được ghép.
- 2026-10-13: chấp nhận bản sửa `GATE-002` sau khi hết hai vòng review. Finding đóng là `fixed`. Không chạy vòng review thứ ba.
- 2026-10-13: `D-09`. `runMultiple` truyền `useRootDefaultLakehouse` vì Fabric từ chối notebook con có default lakehouse khác notebook cha. Các node dùng lakehouse của `NB_00`.
- 2026-10-13: cho qua bước tạo và trigger pipeline `PL_VV_TRANS_SLV_TO_ENR_15P` trên Fabric DEV trong lượt đánh giá này. Không yêu cầu người vận hành chạy pipeline. Không truyền `nb_orches_id` hay `workspace_id`. Bước đó vẫn giữ trong `runtime-runbook.md`. `gates.runtime` vẫn `pending`. Task không chuyển `ready_to_merge`.
- 2026-10-13: không sửa notebook theo `SPARK-001` và `SQL-001` trong `reviews/performance-review.md`. Giữ `changed()` một chiều và giữ `iso_utc_ts`.
- 2026-10-13: người dùng xác nhận task done. Lần `RUN` đầu, `NO_DATA`, ba lần force và `DESCRIBE HISTORY` là đủ. Cho qua bước commit silver mới để kiểm tra append theo khóa đổi. Cho qua trigger pipeline. `gates.runtime` chuyển `pass`. Task sang `ready_to_merge`.
