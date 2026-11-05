## Model và reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Reviewers: `sql-data-reviewer`, `state-correctness-reviewer`, `spark-runtime-reviewer`.
- `risk-gate`: completed.

## Gate verdict

`USER_DECISION`

## P0/P1 findings

- **GATE-001 — P1 — `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:176`; `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb:81`**: Fabric dùng khóa `(media_id, poi_id)` nhưng PostgreSQL vẫn dùng `PRIMARY KEY (media_id)`, nên hai POI dùng chung media có thể gây lỗi hoặc divergence khi đồng bộ. **Fix:** đổi PostgreSQL PK/conflict target sang `(media_id, poi_id)`, hoặc chặn global duplicate `media_id`; nếu hoãn, user phải ghi nhận `accepted-risk` rõ ràng thay vì `backlog`.
- **GATE-003 — P1 — `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:97,101-102`**: logic mới cast ba nguồn `updated_at` sang timestamp để chọn survivor nhưng chưa có bằng chứng cast luôn thành công và có cùng timezone semantics, nên có thể giữ nhầm bản ghi cũ. **Fix:** chứng minh kiểu dữ liệu, zero failed casts và timezone tương thích, hoặc chuẩn hóa/validate timestamp và chặn giá trị lỗi trước cửa sổ dedupe.

P2/P3: **0**.

Probe: `SELECT 'slv_3p_poi_media' src, typeof(updated_at) data_type, count_if(updated_at IS NOT NULL) non_null, count_if(updated_at IS NOT NULL AND try_cast(updated_at AS timestamp) IS NULL) failed_cast FROM slv_3p_poi_media GROUP BY typeof(updated_at) UNION ALL SELECT 'slv_pn_business_service_i18ns', typeof(updated_at), count_if(updated_at IS NOT NULL), count_if(updated_at IS NOT NULL AND try_cast(updated_at AS timestamp) IS NULL) FROM slv_pn_business_service_i18ns GROUP BY typeof(updated_at) UNION ALL SELECT 'slv_pn_business_services', typeof(updated_at), count_if(updated_at IS NOT NULL), count_if(updated_at IS NOT NULL AND try_cast(updated_at AS timestamp) IS NULL) FROM slv_pn_business_services GROUP BY typeof(updated_at);`
