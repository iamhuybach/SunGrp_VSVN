# Request

## User outcome

Một bảng map ở `lh_vv_gold`, tiền tố `gld_`, grain một dòng cho mỗi `poi_id` của gold model cũ. `poi_id` model mới trên bảng đó được tính lại theo rule model mới từ `source_id` / id nguồn mà notebook luồng cũ đang dùng. Không inner-join với dòng gold mới. Gold cũ có `poi_id` mà gold mới chưa có dòng vẫn phải ra `poi_id` model mới.

Một lần init toàn bộ dữ liệu gold model cũ sang gold model mới. `poi_id` google và partner trên dữ liệu init được tính lại, không chứa lang, không dùng `poi_uid`. Chạy init lần hai không nhân đôi dòng và không đổi `poi_id` google hoặc partner mà pipeline mới đã tính đúng.

## Scope

### In scope

- Bảng map gold, khóa là `poi_id` model cũ.
- Init một lần từ các bảng gold mà `notebooks_lgc/3rd_data_ingested_orches/` và `notebooks_lgc/pl_transform_partner_userprofile_cms/` ghi, sang các bảng gold model mới đã có.
- DDL/registry, lib transform/gold, và một notebook init nếu kiến trúc buộc.
- Ngoại lệ có thời hạn: chỉ notebook init được đọc gold cũ để ghi gold mới. Không phải đường đọc của pipeline định kỳ.

### Out of scope

- Sửa pipeline định kỳ hoặc gắn lịch 15 phút.
- Chạy init trên Fabric trong chat này.
- Serving API khi tập cột và khóa gold không đổi.
- Tạo bảng nghiệp vụ mới để chứa phần dữ liệu POI cũ không có bảng gold mới.
- Đoán lại công thức `poi_id` cũ. `ref_poi_legacy_id` chỉ là bằng chứng thu hoạch, không thay bảng map.

## Acceptance criteria

- Grain map: một dòng mỗi `poi_id` model cũ. Khóa không phải `poi_id` mới.
- Cùng `source_id` google, các `poi_id` cũ khác lang cho một `poi_id` mới: `uuid_format(md5(concat('google', source_id)))` (`HASH_MD5_UUID`).
- Cùng id partner, các `poi_id` cũ khác lang cho một `poi_id` mới: `uuid_format(md5(concat(id, 'partner')))` (`uuid_md5(id, lit('partner'))`). `id` là id nghiệp vụ notebook cũ dùng, đối chiếu `slv_pn_business_services.id`. Không hash cụm `partner_portal`.
- Thiếu `source_id` hoặc id nguồn thì không suy ra `poi_id`. Ghi `MISSING_EVIDENCE`.
- `ingestion_source` model cũ là `source_name` model mới. `partner_portal` thành `partner`. Giá trị khác `google` và `partner_portal` không tự đặt `source_name`.
- Field JSON, array và kiểu gộp của bảng cũ ra đúng kiểu field của bảng mới.
- Cột không có cặp trong notebook cũ hoặc DDL model mới thì không điền.
- Init một lần. Lần hai không nhân đôi dòng và không đổi `poi_id` google/partner mà pipeline mới đã tính đúng.
- Architect ghi rollback, thứ tự ghi, và cách init không ghi đè dòng pipeline mới đang sở hữu hoặc không bị pipeline đó ghi đè ngay sau init. Không tách được hai writer thì dừng `user_decision` trước khi sửa code.

## Constraints

- Người dùng đã chốt bảng map nằm ở gold và init một lần từ gold cũ sang gold mới.
- Danh sách bảng ở mục 2.1 không đủ. Kiểm kê mọi bảng gold hai thư mục notebook ghi.
- Bảng watermark và bảng kỹ thuật không phải dữ liệu POI: liệt kê, không copy.
- Bảng POI cũ không có bảng gold mới tương ứng: liệt kê và dừng `user_decision`. Không tạo bảng nghiệp vụ mới.
- `ref_source` trong tài liệu còn `partner_portal`. Trên dữ liệu init, `source_name` ghi `partner`.
- Không đọc `docs/context/3p-google/*.txt`, manifest pipeline, hay artifact task khác.
- Model cũ nằm ở workspace `sgr_visitvn_prd_batch`. Model mới nằm ở workspace `sgr_visitvn_dev`. Cùng tenant, cả hai có quyền đọc và viết. Script kiểm tra và init dùng tên đủ `workspace.lakehouse.schema.table`. Không dùng tên tắt lakehouse.
- Không fast lane. Không commit trong lượt này.

## Classification rationale

- Complexity: high. Đổi grain và khóa, gộp nhiều `poi_id` cũ vào một `poi_id` mới, init có thứ tự ghi và rollback.
- Risk: high. Ghi gold một lần, idempotency, và khả năng đụng writer của pipeline mới. Sau review bắt buộc risk-gate.
- Architecture: required. Đổi grain/khóa, ngoại lệ gold đọc gold, nhiều cách tách writer.
- Evidence: required. Số lang trên một thực thể, giá trị `ingestion_source`, chỗ `source_id` có dữ liệu, và gold cũ còn dòng hay không không chứng minh được từ repo.
- Runtime proof: required. Init không chạy trên Fabric trong chat này. Khi cần chạy, runbook rồi `waiting_runtime`.
- Reviewer routing: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`. `fabric-pipeline-reviewer` chỉ khi sửa pipeline JSON. Risk high nên có `risk-gate` sau specialist review.
- Signals: `data_model_change`, `idempotency`, `cross_state_impact`, `design_tradeoffs`, `data_evidence_required`, `runtime_proof_required`, `low_probability_high_impact`.
