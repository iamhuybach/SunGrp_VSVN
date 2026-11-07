"""Đo lại hiện trạng gap của model POI mới (apps.srv_poi_*).

Chạy:
    export PGHOST=<host>
    export PGDATABASE=vv_data_serving
    export PGUSER=...  PGPASSWORD=...      # lấy từ secret/info.md — KHÔNG hardcode
    uv run --with psycopg2-binary python docs/poi-serving-api/scripts/check-gaps.py

In ra số liệu tương ứng từng mục trong HANDOFF.md §4, §5, §7.
Chạy lại mỗi lần team Data báo đã nạp thêm, để biết gap nào đã đóng.
"""
import os
import sys

import psycopg2

REQUIRED_ENV = ("PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD")


def connect(dbname=None):
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        sys.exit(f"Thiếu biến môi trường: {', '.join(missing)}. Xem docstring đầu file.")
    return psycopg2.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", "5432"),
        dbname=dbname or os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )


def show(cur, label, sql):
    print(f"\n== {label} ==")
    try:
        cur.execute(sql)
        print(" | ".join(d[0] for d in cur.description))
        for row in cur.fetchall():
            print(" | ".join("NULL" if v is None else str(v)[:140] for v in row))
    except Exception as exc:  # noqa: BLE001 - script chẩn đoán, in lỗi rồi đi tiếp
        cur.connection.rollback()
        print("ERR:", exc)


def main():
    conn = connect()
    cur = conn.cursor()

    show(cur, "§4 Độ phủ apps.srv_poi_*", """
        SELECT 'srv_poi_info' AS t, count(*) AS n FROM apps.srv_poi_info
        UNION ALL SELECT 'srv_poi_multi_lang',   count(*) FROM apps.srv_poi_multi_lang
        UNION ALL SELECT 'srv_poi_media_gallery',count(*) FROM apps.srv_poi_media_gallery
        UNION ALL SELECT 'srv_poi_amenity',      count(*) FROM apps.srv_poi_amenity
        UNION ALL SELECT 'srv_poi_review',       count(*) FROM apps.srv_poi_review;""")

    show(cur, "§4 srv_poi_info — cột nào còn rỗng", """
        SELECT count(*) AS total, count(poi_name) AS name, count(lat) AS lat,
               count(rating_overall) AS rating, count(destination_id) AS destination,
               count(subcategory_tags) AS subcategory, count(operating_hours) AS operating_hours,
               count(holiday_exceptions) AS holiday
        FROM apps.srv_poi_info;""")

    show(cur, "§5 G1/G8 — cột spec yêu cầu, hiện có trong apps?", """
        SELECT table_name, column_name FROM information_schema.columns
        WHERE table_schema='apps' AND column_name IN
          ('blur_hash','mime_type','operating_timezone','is_anchor','anchor_type',
           'amenity_code','short_address','content_language')
        ORDER BY 1,2;""")
    print("   (rỗng = tất cả vẫn thiếu)")

    show(cur, "§5 G2/G3 — bảng ref_* đã tồn tại chưa", """
        SELECT table_schema, table_name FROM information_schema.tables
        WHERE table_name LIKE 'ref_%' AND table_schema NOT IN ('information_schema','pg_catalog')
        ORDER BY 1,2;""")
    print("   (rỗng = ref_business_category / ref_amenity vẫn chưa có)")

    show(cur, "§5 G1 — media đã có blob_url chưa", """
        SELECT count(*) AS total, count(blob_url) AS co_blob_url,
               count(*) FILTER (WHERE is_cover) AS covers, count(thumbnail_url) AS thumbnail
        FROM apps.srv_poi_media_gallery;""")

    show(cur, "§5 G3 — amenity_raw bẩn (chứa biểu thức SQL)", """
        SELECT count(*) AS row_ban FROM apps.srv_poi_amenity WHERE amenity_raw ILIKE '%json_type%';""")

    show(cur, "§5 G6 — holiday_exceptions đã đúng format spec chưa", """
        SELECT count(*) AS co_du_lieu,
               count(*) FILTER (WHERE holiday_exceptions ~ '"date":"[0-9]{2}/[0-9]{2}/[0-9]{4}"') AS date_sai_ddmmyyyy,
               count(*) FILTER (WHERE holiday_exceptions ~ '"date":"[0-9]{4}-[0-9]{2}-[0-9]{2}"') AS date_dung_iso,
               count(*) FILTER (WHERE holiday_exceptions ILIKE '%"hours"%')       AS gio_long_trong_mang,
               count(*) FILTER (WHERE holiday_exceptions ILIKE '%is_closed%')     AS co_is_closed
        FROM apps.srv_poi_info WHERE holiday_exceptions IS NOT NULL AND holiday_exceptions <> '[]';""")
    print("   (spec cần: date ISO, open_time/close_time phẳng, có is_closed + is_open_all_day)")

    show(cur, "§7 G16 — mức độ nhân bản poi_id theo ngôn ngữ (legacy)", """
        SELECT count(*) AS rows, count(DISTINCT poi_id) AS poi_ids,
               count(DISTINCT source_id) AS dia_diem_that,
               round(count(*)::numeric / NULLIF(count(DISTINCT source_id),0), 2) AS ids_moi_dia_diem
        FROM public.poi_master;""")

    show(cur, "§7 G16 — poi_id mới có trùng poi_id cũ không", """
        SELECT count(*) AS trung_khop FROM apps.srv_poi_info a
        WHERE EXISTS (SELECT 1 FROM public.poi_master m WHERE m.poi_id::text = a.poi_id);""")
    print("   (0 = id space khác nhau hoàn toàn → bắt buộc có crosswalk)")

    show(cur, "§4 Legacy public vẫn đang lớn lên?", """
        SELECT 'poi_master' AS t, count(*) AS n FROM public.poi_master
        UNION ALL SELECT 'poi_review', count(*) FROM public.poi_review
        UNION ALL SELECT 'poi_enrichment_display', count(*) FROM public.poi_enrichment_display;""")

    cur.close()
    conn.close()

    # tripplanner nằm cùng server, khác database
    try:
        tp = connect("tripplanner")
        tcur = tp.cursor()
        show(tcur, "§7 Blast radius — tripplanner giữ bao nhiêu poi_id", """
            SELECT 'trip_slot_pois' AS t, count(*) AS n FROM public.trip_slot_pois
            UNION ALL SELECT 'trip_acco_pois', count(*) FROM public.trip_acco_pois
            UNION ALL SELECT 'trip_stops',     count(*) FROM public.trip_stops;""")
        tcur.close()
        tp.close()
    except Exception as exc:  # noqa: BLE001
        print(f"\n== §7 tripplanner ==\nKhông kết nối được: {exc}")


if __name__ == "__main__":
    main()
