# Context Google 3rd-party dùng chung

Các file này là tài liệu hình payload Google và cho lớp L2 sau này. Extract hiện
đọc `normalized_payload` đã có raw shape và thêm `photos[].blob_url`. Chúng không
phải hợp đồng schema.

| File | Dùng khi |
|---|---|
| `sample_raw_payload.txt` | Đối chiếu hình `raw_payload` |
| `sample_normalized_payload.txt` | Đối chiếu output extract cũ |
| `get_amenity.md` | L2 làm phẳng cờ Google và lọc theo ngành. L1 chỉ lưu JSON gốc |
| `business_sector_rule.md` | L2 map `primaryType` / `types` sang ngành |
| `mapping_sector.md` | L2 map Google place type sang nhóm amenity |
| `ward_mapping_satnhap.txt` | L2 chuẩn hoá địa chỉ hành chính sau sát nhập |
| `amenity-l1-demo.md` | Hình `source_flags_json` mà L1 phải giữ |
