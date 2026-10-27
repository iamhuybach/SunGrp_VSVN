
# Table: `gld_srv_poi_review`

## 1. Xử lý

- Thêm cột `lang`, `title` vào `slv_enr_poi_review_multi_lang`.
- `slv_enr_poi_review_multi_lang` INNER JOIN `slv_3p_poi_review` on `review_id`.
- `slv_enr_poi_review_multi_lang` LEFT JOIN `slv_3p_poi_rating` on `poi_id`.

## 2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_enr_poi_review_multi_lang.review_id | string | transform 1-1 | review_id |
| slv_enr_poi_review_multi_lang.poi_id | string | transform 1-1 | poi_id |
| slv_enr_poi_review_multi_lang.lang | string | transform 1-1 | lang |
| slv_3p_poi_rating.rating_overall | decimal(4,2) | transform 1-1 | rating_overall |
| slv_3p_poi_rating.rating_count | integer | transform 1-1 | rating_count |
| slv_enr_poi_review_multi_lang.title | string | transform 1-1 | title |
| slv_enr_poi_review_multi_lang.review_text | string | transform 1-1 | review_text |
| slv_3p_poi_review.rating | string | transform 1-1 | rating |
| slv_3p_poi_review.time | string | transform 1-1 | review_date |
| slv_3p_poi_review.author_name | string | transform 1-1 | author_name |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |
