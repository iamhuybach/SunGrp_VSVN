## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`
- Risk gate: không yêu cầu

## Gate verdict: `EVIDENCE_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| SQL-001 | P1 | `docs/context/mapping_gld_srv_product_offer.md:31`, `:93`, `:147` | Mapping yêu cầu mỗi `variant_id` chỉ tạo một phần tử JSON nhưng chưa bảo vệ tính duy nhất của holiday `(product_id, id)` và hotel `(business_service_id, rate_plan_id)`; dữ liệu trùng có thể tạo phần tử lặp và kết quả không xác định. | Chạy probe dưới đây; nếu có kết quả, bổ sung guard fail-fast trước aggregation, nếu không thì lưu bằng chứng zero-row cho giả định source grain. |

P2/P3: 0.

Probe — PASS khi trả về 0 dòng: `WITH anomalies AS (SELECT 'holiday' AS branch, CAST(product_id AS STRING) AS owner_id, CAST(id AS STRING) AS variant_id, COUNT(*) AS row_count FROM lh_vv_silver.dbo.slv_pn_product_variants WHERE deleted = false AND product_id IS NOT NULL GROUP BY product_id, id HAVING id IS NULL OR COUNT(*) > 1 UNION ALL SELECT 'hotel' AS branch, CAST(business_service_id AS STRING) AS owner_id, CAST(rate_plan_id AS STRING) AS variant_id, COUNT(*) AS row_count FROM lh_vv_silver.dbo.slv_pn_hotel_rate_offer WHERE deleted_at IS NULL AND business_service_id IS NOT NULL GROUP BY business_service_id, rate_plan_id HAVING rate_plan_id IS NULL OR COUNT(*) > 1) SELECT * FROM anomalies ORDER BY branch, owner_id, variant_id LIMIT 50;`
