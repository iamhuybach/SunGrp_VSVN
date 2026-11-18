# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`.

## Phạm vi và môi trường

Fabric DEV. Lakehouse `lh_vv_silver` và `lh_vv_gold`. Notebook `NB_SLV_POI_AMENITY`, cell `amenpnpy` của `NB_CREATE_DDL`. Pipeline `PL_VV_TRANS_SLV_TO_ENR_15M` và `PL_VV_TRANS_SLV_TO_GLD_1H`.

## Điều kiện tiên quyết

- Code của task này đã ở workspace DEV, gồm `NB_SLV_POI_AMENITY`.
- Trigger `PL_VV_TRANS_SLV_TO_ENR_15M` có thể tạm dừng.
- `amenpnpy`: `MODE = "ON"` khi thêm cạnh. Rollback dùng `MODE = "OFF"`.
- Chạy P5 trước. Chỉ đi tiếp khi `pois_sector_null = 0` và `labels_multi_match = 0`.

## Baseline trước khi chạy

Số `poi_id` amenity Google đang sống là 15995. Số `poi_id` amenity có trên `gld_srv_poi_info` là 0.

## Các bước thực hiện

1. Chạy SQL P5 bên dưới trên Fabric DEV. Chỉ đọc. Dán vào `evidence/results/partner-amenity-precheck.txt`. Nếu `labels_multi_match > 0`, dán thêm tối đa 50 giá trị `label`. Không dữ liệu cá nhân, không secret.
2. Nếu `pois_sector_null > 0` hoặc `labels_multi_match > 0`, dừng và báo Main. Không chạy notebook ghi.
3. Tạm dừng trigger `PL_VV_TRANS_SLV_TO_ENR_15M`.
4. Chạy cell `amenpnpy` với `MODE = "ON"`.
5. Chạy `NB_SLV_POI_AMENITY` một lần, hoặc bật lại trigger để pipeline chạy một vòng.
6. Để `PL_VV_TRANS_SLV_TO_GLD_1H` copy `gld_srv_poi_amenity`.

```sql
WITH vi AS (
  SELECT business_service_id AS id, amentities AS am
  FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns
  WHERE coalesce(deleted, false) = false AND locale = 'vi'),
svc AS (
  SELECT id, amentities AS am, business_sector
  FROM lh_vv_silver.dbo.slv_pn_business_services
  WHERE coalesce(deleted, false) = false),
tags AS (
  SELECT vi.id, svc.business_sector,
         coalesce(from_json(vi.am, 'struct<facilities:struct<specialty_tags:array<string>>>').facilities.specialty_tags,
                  from_json(svc.am, 'struct<facilities:struct<specialty_tags:array<string>>>').facilities.specialty_tags) AS t
  FROM vi LEFT JOIN svc ON vi.id = svc.id),
labels AS (
  SELECT DISTINCT id, business_sector, trim(l) AS label
  FROM tags LATERAL VIEW explode(t) e AS l
  WHERE l IS NOT NULL AND trim(l) <> ''),
dict AS (
  SELECT trim(amenity_raw) AS amenity_raw, count(*) AS n
  FROM lh_vv_silver.dbo.ref_dictionary_amenities
  WHERE is_active = true AND lower(trim(source_name)) = 'partner'
  GROUP BY trim(amenity_raw))
SELECT count(DISTINCT l.id) AS pois,
       count(*) AS rows,
       count(DISTINCT CASE WHEN l.business_sector IS NULL THEN l.id END) AS pois_sector_null,
       count(DISTINCT CASE WHEN trim(l.business_sector) = '' THEN l.id END) AS pois_sector_blank,
       count(DISTINCT CASE WHEN d.n > 1 THEN l.label END) AS labels_multi_match,
       count(DISTINCT CASE WHEN d.n = 1 THEN l.label END) AS labels_matched,
       count(DISTINCT CASE WHEN d.n IS NULL THEN l.label END) AS labels_unmatched
FROM labels l LEFT JOIN dict d ON l.label = d.amenity_raw;
```

## Kiểm tra kết quả

Chạy lại `evidence/probes/amenity-poi-id-side.sql` và `evidence/probes/amenity-poi-id-overlap.sql`. Đạt khi số `poi_id` Google vẫn là 15995, số `poi_id` partner lớn hơn 0 và không lớn hơn `pois` của P5, và `in_gld_srv_poi_info` của nhóm partner bằng số `poi_id` partner. `gld_enr_poi_info.service_flag` của dòng partner vẫn là `[]`.

## Chạy lại để kiểm tra idempotency

Chạy lại `NB_SLV_POI_AMENITY`. Số dòng partner sống không tăng vì cùng khóa MERGE. Chạy lại `amenpnpy` với `MODE = "ON"` không thêm cạnh mới.

## Kiểm tra log và watermark

`amenpnpy` chỉ gia hạn khóa flow `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M` rồi trả khóa. Cell không ghi watermark bảng. Notebook amenity ghi log run theo `NB_LIB_TRANSFORM_SLV_GLD`.

## Rollback và forward recovery

1. Tạm dừng trigger.
2. Đưa `NB_SLV_POI_AMENITY` về bản không có nhánh partner.
3. Chạy `amenpnpy` với `MODE = "OFF"`. Hai cạnh partner thành `is_active = 0`. Cell không xóa dòng cấu hình.
4. Chạy `NB_SLV_POI_AMENITY` với `p_force = "true"`. RECOMPUTE soft-delete dòng partner. Dòng Google không đổi.
5. Để pipeline gold copy lại.
6. Bật lại trigger.

Forward: sửa từ điển hoặc rule rồi chạy lại. Bảng L1 partner vẫn giữ nguồn.

## Kết quả người dùng ghi nhận

- P5, Fabric DEV, 2026-11-18: `pois=48`, `rows=96`, `pois_sector_null=0`, `pois_sector_blank=0`, `labels_multi_match=0`, `labels_matched=8`, `labels_unmatched=13`. Đủ điều kiện chạy tiếp.
- `amenpnpy` với `MODE = "ON"`: năm cạnh active là `ref_dictionary_amenities`, `slv_3p_poi_amenity`, `slv_pn_business_service_i18ns`, `slv_pn_business_services`, `slv_poi_entity_non_enrich`.
- `NB_SLV_POI_AMENITY`, chạy tay, exec `620ce8e5-b1db-4aa1-949d-46aca2eb11ae`: SUCCESS 77s. Hai cạnh partner là `NEW_EDGE`. Cảnh báo `partner_labels_unmatched: 13`. Diff: insert 96, update 0, xoá mềm 0, nguồn 42332 dòng. Exit `inserted=96`, `updated=0`, `deactivated=0`, `trg_version=5`.
- `NB_00_ORCHES_SLV_TO_GLD`, exec `5ebef331-52eb-4ff7-a273-e4183eb520dd`, `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_1H`, `p_force_nodes = gld_srv_poi_amenity`: SUCCESS 77s. Kế hoạch 0 Dirty Edge, 1 node ép chạy. `gld_srv_poi_amenity` SUCCESS, `inserted=0`, `updated=0`, `deactivated=0`, `trg_version=1`. Gold chưa nhận 96 dòng partner vì lát cắt `output_versions_json` của `PL_VV_TRANS_SLV_TO_ENR_15M` chưa có version 5.
- `NB_00_ORCHES_SLV_TO_ENR` PLAN, exec `58ad4cb7-91e1-4fc0-860f-91989d2b2a03`: 3 node, 20 cạnh, 3 Dirty Edge, 2 ứng viên. `slv_poi_amenity` vì hai cạnh partner `NEW_EDGE`. `gld_enr_poi_info` vì `slv_poi_amenity` `DATA_CHANGED` đã đọc 4, đọc 5.
- `NB_00_ORCHES_SLV_TO_ENR` RUN, exec `02ca8f86-211d-4849-a914-9fea5f381d6a`: SUCCESS 195s. `slv_poi_amenity` inserted 0, updated 0, deactivated 0, `trg_version=5`. `gld_enr_poi_info` inserted 0, updated 0, deactivated 0, `trg_version=6`. Tiến 13 cạnh.
- `NB_00_ORCHES_SLV_TO_GLD`, exec `3f968daa-8886-4553-973a-e0ab9b0fa740`: SUCCESS 124s. Dirty Edge `gld_srv_poi_amenity` đã đọc 4, đọc 5. Exit `inserted=96`, `updated=0`, `deactivated=0`, `trg_version=2`.
- Probe sau copy: amenity Google 15995, partner 48. Hai bảng amenity cùng 16043 `poi_id`. `gld_srv_poi_info` sống: Google 2797, partner 295. Giao toàn bộ amenity với info là 2230. `gld_enr_poi_info` không đổi dòng, nên `service_flag` không đổi.
- Query 4, 2026-11-19: Google `amenity_poi_id=15995`, `in_gld_srv_poi_info=2182`. Partner `amenity_poi_id=48`, `in_gld_srv_poi_info=48`. Đạt điều kiện partner.
