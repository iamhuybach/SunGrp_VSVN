## 1. Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp yêu cầu.
- Specialists: `api-contract-reviewer`, `app-security-reviewer`, `jpa-performance-reviewer`.
- `risk-gate`: đã hoàn tất.
- Carry-over: `API-001`, `SEC-001`, `JPA-001` đã được xác nhận resolved.

## 2. Gate verdict

`FIX_REQUIRED`

## 3. P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| JPA-002 | P1 | `PoiSpecifications.java:45`; `SrvPoiLegacyIdMapRepositoryImpl.java:33` | `arrayContains(idsArray, scalarColumn)` sinh dạng `? @> ARRAY[column]`, không tạo access path trực tiếp qua B-tree PK và có nguy cơ quét cả hai bảng khi tải đồng thời tăng. | Đổi cả hai predicate sang `scalar_column = ANY(:ids)` với một PostgreSQL array parameter; giữ tối đa 5 statement và không tạo `IN` quá 100 phần tử. |

`GATE-001` được gộp vào `JPA-002` vì cùng một nguyên nhân và cách khắc phục.

## 4. P2/P3

P2: 0; P3: 0.

## 5. Probe

Sau khi sửa, chạy `EXPLAIN (ANALYZE, BUFFERS)` cho lookup trên `apps.srv_poi_legacy_id_map.legacy_poi_id` và `apps.srv_poi_info.poi_id` với input đại diện; đạt khi cả hai dùng PK index lookup và không có `Seq Scan`.
