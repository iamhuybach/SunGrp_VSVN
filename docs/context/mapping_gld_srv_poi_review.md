
# Table: `gld_srv_poi_review`

## 1. Xử lý

- [SỬA 04/11] Bảng gốc là `slv_3p_poi_review`, một dòng một `review_id`. Không đọc `slv_enr_poi_review_multi_lang`.
- `slv_3p_poi_review` LEFT JOIN `slv_3p_poi_rating` on `poi_id`. `poi_id` trùng trên `slv_3p_poi_rating` thì dừng, không chọn dòng.
- Không có cột `lang` (D-SRV-LANG). `title` luôn NULL: `slv_3p_poi_review` không có cột `title` và không thêm (D-SRV-TEXT). `review_text` lấy từ `slv_3p_poi_review.text`.

## 2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_3p_poi_review.review_id | string | transform 1-1 | review_id |
| slv_3p_poi_review.poi_id | string | transform 1-1 | poi_id |
| slv_3p_poi_rating.rating_overall | decimal(4,2) | transform 1-1 | rating_overall |
| slv_3p_poi_rating.rating_count | bigint | transform 1-1 | rating_count |
| | string | NULL | title |
| slv_3p_poi_review.text | string | transform 1-1 | review_text |
| slv_3p_poi_review.rating | decimal(4,2) | transform 1-1 | rating |
| slv_3p_poi_review.time | string | transform 1-1 | review_date |
| slv_3p_poi_review.author_name | string | transform 1-1 | author_name |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |
