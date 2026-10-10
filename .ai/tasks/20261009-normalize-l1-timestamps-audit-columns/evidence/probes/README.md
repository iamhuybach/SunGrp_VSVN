# Probes

Read-only Fabric DEV probes. Save sanitized output under `evidence/results/`.

| File | Decision |
|---|---|
| `e1_partner_timestamp_shapes.sql` | Epoch unit or ISO/date class for each partner timestamp candidate |
| `e2_3p_timestamp_shapes.sql` | Population format class for 3P `crawled_at`, payload `created_at`, review `time`, and `ingested_date` |
| `e3_partner_registry_vs_silver.py` | Deployed partner registry versus silver column types and time-column ranges |
| `e4_partner_raw_registry_map.sql` | Three fullest bronze payloads per partner table versus registry `json_path` |

Pass and fail rules are in `../plan.md`. Do not paste phones, review text, media URLs, or `raw_payload` into the result files.
