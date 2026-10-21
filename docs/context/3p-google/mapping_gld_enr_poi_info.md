
# 1. Mapping Transform

| Source Field | Rule | Target Field | Data Sample |
|---|---|---|---|
| avg_range_min | Transform 1:1 | time_to_spend_minutes | |
| avg_range_min | Value dạng Json:<br>- Key lấy theo mục 2.<br>- Value xử lý theo mục 1.1. | time_to_spend | `{"Thời gian dùng bữa":"1 tiếng 30 phút"}` |
| canonical_candidate | Transform 1:1 | best_time_type | best_time_type |
| canonical_candidate | Value dạng Json:<br>- Key lấy theo mục 2.<br>- Value xử lý theo mục 1.2. | best_time | `{"Thời điểm nên ghé":"Quanh năm"}`<br>`{"Thời điểm nên ghé":"Tháng 3 - Tháng 8"}` |
| Cost (Từ 2 cột price_min và price_max khi join với slv_3p_poi_price -> tính cost theo mục 1.9.3 trong D:\git\SunGrp_VSVN\docs\context\3p-google\mapping_place_type.md) | Value dạng Json:<br>- Key lấy theo mục 2.<br>- Value xử lý theo mục 1.3. | cost_vnd | `{"Mức giá tham khảo":"Từ 350,000đ"}`<br>cost = null => Serialized JSON null, không phải `{key: null}` |

## 1.1. Time_to_spend formatter

- avg_range_min < 60 phút: hiển thị phút;
- avg_range_min > 60 phút: tách giờ và phút.
- null hoặc ≤ 0: Không cố định
- business_sector = accommodation: ceil(avg_range_min / 1,440) rồi hiển thị theo số ngày.
- business_sector = tour_n_activities: avg_range_min > 420 phút: Cả ngày.Best-time formatter:

## 1.2. Best-time formatter

- Chỉ canonical_candidate có đủ month 1–12 mới hiển thị range. From-To của Best-time lấy đúng theo thứ tự trong String. Ví dụ ‘Month 11-3’ = > `{"Thời điểm nên ghé":"Tháng 11 - Tháng 3"}`
- Các trường hợp còn lại hiển thị Quanh năm.

## 1.3. Cost formatter round về 1,000 VND.

# 2. Mapping business_sector với text tương ứng

| business_sector | VI: time_to_spend / best time / cost_vnd |
|---|---|
| accommodation | Thời gian lưu trú lý tưởng / Mùa lưu trú đẹp nhất / Giá phòng tham khảo |
| f_n_b | Thời gian dùng bữa / Thời điểm nên ghé / Mức giá tham khảo |
| attraction | Thời gian tham quan / Mùa đẹp nhất / Chi phí tham quan |
| tour_n_activities | Thời lượng hoạt động / Thời điểm phù hợp / Chi phí tham khảo |
| shopping_n_retail | Thời gian mua sắm / Thời điểm nên ghé / Chi tiêu tham khảo |
| transport_route_base | Thời gian đưa đón / Thời điểm phù hợp / Chi phí đưa đón |
| transport_on_demand | Thời gian thuê phổ biến / Thời điểm nên thuê / Giá thuê tham khảo |
| vehicle_rental | Thời gian thuê phổ biến / Thời điểm nên thuê / Giá thuê tham khảo |
| spa_n_wellness | Thời lượng liệu trình / Thời điểm phù hợp / Giá dịch vụ tham khảo |
| event | Thời lượng chương trình / Thời điểm nên xem / Giá vé tham khảo |
| other | Thời lượng trải nghiệm / Thời điểm phù hợp / Chi phí tham khảo |
