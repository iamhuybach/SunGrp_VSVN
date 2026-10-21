# Evidence plan

## Decision to resolve

- SQL-001: `slv_poi_entity_non_enrich` có đúng một dòng cho mỗi `poi_id` khác null.
- SQL-002: `slv_pn_business_service_i18ns` có đúng một dòng `locale = vi` chưa deleted cho mỗi `business_service_id`.

## Existing evidence

- Grain `slv_poi_amenity` và khóa DOC `slv_3p_poi_price`: `docs/context/01_DATA_MODEL.md` §5.2 và §6.
- Cột entity và hợp đồng gold enr: `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`.
- Cạnh `PL_VV_TRANS_SLV_TO_ENR_15P`: cell `init_seed_ctrl` và `notebooks/NB_CREATE_DDL.ipynb` cell `enrddlpy`.
- Mục 1.3 không có công thức: `docs/context/3p-google/mapping_gld_enr_poi_info.md`.
- Review round 2: `reviews/round-2.md`.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| sql-001-sql-002 | Fabric DEV | `poi_id` entity và i18n `vi` còn sống có trùng hoặc null không | Mỗi câu trả 0 dòng. User báo 0 dòng ngày 2026-10-21. | evidence/results/sql-001-sql-002.txt |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
