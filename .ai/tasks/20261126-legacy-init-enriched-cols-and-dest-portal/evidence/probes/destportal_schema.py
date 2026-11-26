# Môi trường: Fabric DEV, một cell Python, chỉ đọc. Không tham số.
# Bảng: lh_vv_silver.dbo.slv_enr_poi_destination
# Đạt: mỗi cột một dòng name, simpleString, nullable.
# Dán: .ai/tasks/20261126-legacy-init-enriched-cols-and-dest-portal/evidence/results/destportal-schema.txt
# Chỉ tên cột, kiểu, nullable. Không dữ liệu dòng. Tối đa 50 dòng.

fq = "lh_vv_silver.dbo.slv_enr_poi_destination"
fields = spark.table(fq).schema.fields
print(f"COLUMN_COUNT\t{len(fields)}")
for field in fields:
    print(f"{field.name}\t{field.dataType.simpleString()}\t{field.nullable}")
