# Author input — model

No `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md`. Cite ledger row D-01. Do not invent a type, key, or cover predicate.

## User comments (verbatim)

Thêm cover_id và cover_blob_url vào lh_vv_gold.dbo.gld_srv_poi_info và bảng PostgreSQL tương ứng apps.srv_poi_info, trong cùng một task.
- cover_id lấy từ slv_poi_media_info.media_id. cover_blob_url lấy từ slv_poi_media_info.blob_url.
- LEFT JOIN slv_poi_media_info. POI không có cover vẫn giữ một dòng gld_srv_poi_info; hai cột mới để null.
- Chọn đúng dòng cover mà gld_srv_poi_media_gallery đang dùng qua is_cover. Gallery là bản 1-1 của slv_poi_media_info; is_cover đã tính trên silver (with_cover), không tính lại trong gallery. Dùng dòng is_cover đó. Không viết rule cover thứ hai, không đổi rule is_cover, không đổi grain một dòng poi_id.
- Kiểu cột lấy từ media_id và blob_url hiện có, ánh xạ PostgreSQL theo đầu file gld_srv_serve.pg.sql.

## Read

- `.ai/tasks/20261108-gld-srv-poi-info-cover/request.md`
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` — `id:srvinfobuild` (`OUT_COLS`, `SPEC`)
- `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb` — `id:srvgallerybuild`
- `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb` — `def:with_cover` (`with_cover`, `unique_checks`)
- `docs/context/mapping_gld_srv_poi_info.md` — headings `1.1. Xử lý`, `1.2. Field Mapping`
- `docs/context/mapping_poi_media_info.md` — heading `1.2. Field Mapping` (`is_cover`, `media_id`, `blob_url`)
- `notebooks/NB_CREATE_DDL.ipynb` — `id:mediaddlpy` (`MEDIA_COLS`); `id:srvratepy` (additive columns and ctrl edges on `gld_srv_poi_info`)
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` — `grep:gld_srv_poi_info` inside `id:init_tables` and `id:init_seed_ctrl`
- `sql/postgres/gld_srv_serve.pg.sql` — header type map and `CREATE TABLE apps.srv_poi_info`; `media_id` and `blob_url` on `apps.srv_poi_media_gallery`
- `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiInfo.java`
- `docs/context/02_NAMING_CONVENTION.md` only for the `poi_id` formula `AGENTS.md` §7 already states

## Constraints

- Grain stays one row per `poi_id`. `pk` stays `("poi_id",)`. Do not change `is_cover`, gallery, or silver.
- Both new columns are nullable. No cover row means both null. Join the `is_cover` row gallery already projects; do not add `is_active` unless a file above defines the cover that way.
- Column position was not specified. Ask under Conflicts and questions when the files do not show where an added info column sits.
- Record a lineage edge `slv_poi_media_info` → `gld_srv_poi_info` only as the files show ctrl edges. Do not read the pipeline JSON or `docs/poi-serving-api/`.
- No endpoint and no DTO in this model. Gold does not read gold.
