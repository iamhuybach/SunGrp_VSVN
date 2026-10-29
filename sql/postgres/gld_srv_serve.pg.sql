-- PostgreSQL DDL cho 5 bảng gold serving, schema apps. Task 20261029-pg-ddl-gld-srv-serve.
-- Nguồn cột: lh_vv_gold.dbo.gld_srv_poi_* (NB_SETUP_INITIAL_DDL cell init_tables, NB_CREATE_DDL).
-- Khóa chính theo NodeSpec.pk của notebook NB_GLD_SRV_POI_* tương ứng.
-- Ánh xạ kiểu Fabric -> PostgreSQL (decision.md D-TYPE, D-BIGINT):
--   STRING       -> text
--   BOOLEAN      -> boolean
--   INT          -> integer
--   BIGINT       -> int8
--   DOUBLE       -> double precision
--   DECIMAL(p,s) -> numeric(p,s)
--   TIMESTAMP    -> timestamp without time zone
--   Kiểu khác    -> MISSING
-- NOT NULL chỉ ở cột gold NOT NULL; đó đều là cột khóa chính.
-- apps.srv_poi_review không có cột lang (decision.md D-LANG). Gold gld_srv_poi_review vẫn giữ lang.
-- Schema apps phải có sẵn. File không tạo schema, index, view hay quyền.
-- Chạy: psql -v ON_ERROR_STOP=1 -f <file>. Chạy lại sẽ lỗi "already exists" và rollback, không đổi gì.

BEGIN;

CREATE TABLE apps.srv_poi_info (
    poi_id text NOT NULL,
    poi_name text,
    source_name text,
    business_sector text,
    business_category text,
    subcategory_tags text,
    destination_id text,
    full_address text,
    street text,
    ward text,
    district text,
    city text,
    country_code text,
    postal_code text,
    lat double precision,
    lng double precision,
    phone text,
    email text,
    website_url text,
    operating_status text,
    is_verified boolean,
    is_recommended boolean,
    is_bookable boolean,
    operating_hours text,
    holiday_exceptions text,
    rating_overall numeric(4, 2),
    rating_count integer,
    review_count integer,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (poi_id)
);

CREATE TABLE apps.srv_poi_multi_lang (
    poi_id text NOT NULL,
    lang text NOT NULL,
    source_name text,
    time_to_spend text,
    best_time text,
    cost_vnd text,
    description text,
    experience text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (poi_id, lang)
);

CREATE TABLE apps.srv_poi_amenity (
    poi_id text NOT NULL,
    business_sector text NOT NULL,
    amenity_group text NOT NULL,
    amenity_raw text NOT NULL,
    amenity text,
    amenity_vi text,
    service_flags text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (poi_id, business_sector, amenity_group, amenity_raw)
);

CREATE TABLE apps.srv_poi_media_gallery (
    media_id text NOT NULL,
    poi_id text,
    source_name text,
    photo_api_uri text,
    display_order integer,
    width_px integer,
    height_px integer,
    photographer text,
    blob_url text,
    thumbnail_url text,
    is_cover boolean,
    is_active boolean,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (media_id)
);

CREATE TABLE apps.srv_poi_review (
    review_id text NOT NULL,
    poi_id text,
    rating_overall numeric(4, 2),
    rating_count int8,
    title text,
    review_text text,
    rating numeric(4, 2),
    review_date text,
    author_name text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (review_id)
);

COMMIT;
