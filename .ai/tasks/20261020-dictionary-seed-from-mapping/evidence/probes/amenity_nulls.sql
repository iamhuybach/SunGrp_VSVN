-- Fabric DEV, read-only. Task 20261020-dictionary-seed-from-mapping.
-- Quyết định: bốn cột khóa slv_poi_amenity có dòng NULL hay không, và từ điển amenities còn bao nhiêu dòng sau R6.
-- Pass ALTER chỉ khi cả bốn số NULL = 0. Có NULL thì không ALTER SET NOT NULL.
-- Giới hạn: một dòng tổng, không mẫu, không dữ liệu cá nhân.

SELECT count(*) AS amenity_dictionary_rows
FROM lh_vv_silver.dbo.ref_dictionary_amenities;

SELECT
    count(*) AS amenity_rows,
    sum(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) AS poi_id_null,
    sum(CASE WHEN business_sector IS NULL THEN 1 ELSE 0 END) AS business_sector_null,
    sum(CASE WHEN amenity_group IS NULL THEN 1 ELSE 0 END) AS amenity_group_null,
    sum(CASE WHEN amenity_raw IS NULL THEN 1 ELSE 0 END) AS amenity_raw_null
FROM lh_vv_silver.dbo.slv_poi_amenity;
