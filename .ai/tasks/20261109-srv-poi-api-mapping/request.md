# Request

## User outcome

Có một mẫu mapping thống nhất và bốn tài liệu mapping, mỗi tài liệu một API GET đang có dưới prefix `/api/v1/pois`, đúng cột và đúng mã lỗi lấy từ code cùng `sql/postgres/gld_srv_serve.pg.sql`.

## Scope

### In scope

- `docs/context/api-mapping/MAPPING_SAMPLE.md`
- `docs/context/api-mapping/compact.md` cho `GET /api/v1/pois/compact` (`CompactPoiResponse`)
- `docs/context/api-mapping/gallery.md` cho `GET /api/v1/pois/{poi_id}/gallery` (`PoiGalleryItemResponse`)
- `docs/context/api-mapping/reviews.md` cho `GET /api/v1/pois/{poi_id}/reviews` (`PoiReviewItemResponse`)
- `docs/context/api-mapping/amenities.md` cho `GET /api/v1/pois/{poi_id}/amenities` (`PoiAmenityGroupResponse`)

### Out of scope

- Sửa Java, DDL, entity, DTO, hoặc hành vi API.
- `docs/poi-serving-api/`.
- Query PostgreSQL và `docker compose`.
- `run-author` và Architect.

## Acceptance criteria

- Có 1 file mẫu và 4 file API. File mẫu xong trước; 4 file giữ cùng tên mục và cùng cột.
- Mỗi mục là một bảng Markdown. Cuối mỗi file là sample request và sample response.
- Cột, kiểu, JSON name và error code lấy từ code và từ `sql/postgres/gld_srv_serve.pg.sql`. Không bịa field, không bịa mã 401, 403, 429 hay mã số 1, 3, 4 nếu code không có.

## Constraints

- Không đổi hành vi. Không `data_model_change`. Không fast lane vì hơn 2 file. `architecture_required` false, `evidence_required` false, `complexity` low, `risk_level` low. Không commit.
- Viết tiếng Việt. Tên field, path, và mã lỗi giữ tiếng Anh. Sample chỉ dùng UUID và chữ giả, không email, phone, tên người thật.

## Classification rationale

- Complexity: `low`. Việc chỉ thêm tài liệu Markdown cho hợp đồng đã có trong code.
- Risk: `low`. Không đổi hành vi API; thay đổi hẹp và kiểm được bằng đối chiếu repository.
- Architecture: không bắt buộc. Không đổi grain, key, chủ sở hữu state, transaction, CDC, watermark, hay orchestration. Không có nhiều cách làm với trade-off vật chất. Phạm vi là năm file tài liệu.
- Evidence: không bắt buộc. Cột và mã lỗi đã có trong source và `sql/postgres/gld_srv_serve.pg.sql`.
- Runtime proof: không bắt buộc. Không cần Fabric DEV hay `docker compose`.
- Reviewer routing: `required_reviewers` rỗng. `api-contract-reviewer` khi diff chạm `api/`, `dto/`, `domain/entity/`, `OpenApiConfig`, hoặc `sql/postgres/gld_srv_serve.pg.sql`. `app-security-reviewer` và `jpa-performance-reviewer` khi diff chạm các path tương ứng ở WORKFLOW.md §7. Diff tài liệu này không chạm các path đó. Không fast lane vì hơn 2 file. Không có signal `data_model_change`.
