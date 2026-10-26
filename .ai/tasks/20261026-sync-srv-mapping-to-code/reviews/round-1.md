## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium` — khớp yêu cầu.
- Reviewers chạy độc lập: `spark-runtime-reviewer`, `sql-data-reviewer`.
- Risk gate: không yêu cầu, không chạy.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | Vị trí | Failure | Fix |
|---|---|---|---|---|
| SQL-001 | P1 | `docs/context/mapping_gld_srv_poi_multi_lang.md:23` | Mapping ghi `lang` nguồn là `string NOT NULL`, nhưng DDL cho phép null, che khuất lỗi với grain/MERGE key `(poi_id, lang)`. | Đổi kiểu nguồn thành `string`; mô tả riêng target/key yêu cầu non-null và quality gate chặn null. |
| SQL-002 | P1 | `docs/context/mapping_poi_media_info.md:21` | Mapping suy diễn `media_dedup_key` nguồn là `string NOT NULL`, trong khi notebook chỉ truyền thẳng sang target và không chứng minh nullability. | Ghi `MISSING` cho nullability, hoặc chỉ `string`; chỉ giữ `NOT NULL` khi có bằng chứng schema/runtime. |

P2: 0. P3: 0.

Probe nếu muốn chứng minh SQL-002 thay vì sửa mapping: đọc `spark.table("lh_vv_silver.dbo.slv_3p_poi_media").schema["media_dedup_key"].nullable` và đếm dòng `media_dedup_key IS NULL`; PASS khi `nullable = false` và count = 0.
