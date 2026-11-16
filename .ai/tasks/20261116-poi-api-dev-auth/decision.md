# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Cơ chế auth | Spring Security `SecurityFilterChain` + `AuthorizationManager` on `/api/v1/pois/**`, `anyRequest().permitAll()`. | Alternatives 1–3 | 2026-11-16 |
| D-2 | Biến môi trường | Variable `POI_API_BEARER_TOKEN` → `app.security.poi-api.bearer-token`. Blank fails closed and the app still starts. | Decision | 2026-11-16 |
| D-3 | Envelope 401 | 401 = `ApiResponse.error(UNAUTHORIZED, "Missing or invalid bearer token.", "ERR_UNAUTHORIZED")` plus `WWW-Authenticate: Bearer`, the same for every reason. | Decision | 2026-11-16 |
| D-4 | So sánh token | SHA-256 + `MessageDigest.isEqual`, and the configured value is `strip()`ed. | Decision | 2026-11-16 |
| D-5 | Token test | Test token lives in `src/test/resources/application.yml`, and `poi-api-bearer-token.txt` is not created (Alternatives 4). | Alternatives 4 | 2026-11-16 |
| D-6 | ConfigMap | ConfigMap value empty. Recommend Secret injection at deploy (follow-up, not blocking). | Security | 2026-11-16 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- D-7 (2026-11-16): `tests/test_srv_poi_api_mapping_required.py` được sửa vì `test_only_path_poi_id_or_compact_body_ids_is_required` cấm mọi `Required = có` ngoài `Request param` / `poi_id`. Edit list không có file này. Rule mới: `Request header` / `Authorization` được `Required = có` trên sáu file mapping và `amenities.md`. Mọi field Required khác giữ nguyên.
- API-001 (2026-11-16): Khác câu "401 dùng cùng content problem+json" trong mục `Code: OpenApiConfig`. Runtime trả envelope `ApiResponse` (`application/json`). OpenAPI 401 phải khớp body đó.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| API-001 | P1 | fixed | 401 OpenAPI là `application/json` đúng envelope `ApiResponse`, kèm header `WWW-Authenticate: Bearer`. Customizer không ghi đè bằng `application/problem+json`. | |
| API-002 | P1 | accepted-risk | Người dùng chọn `accepted-risk` ngày 2026-11-16. OpenAPI gắn `bearerAuth` ở gốc, nên tài liệu mô tả mọi operation cần token. Runtime vẫn `permitAll` ngoài `/api/v1/pois`. Không sửa code. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-16: `API-002` là `accepted-risk`. Giữ `bearerAuth` toàn cục trên OpenAPI. Không sửa code.

## Lịch sử quyết định

- 2026-11-16: Ghi D-1 đến D-6 từ `architecture.md`, mục `Proposed decision ledger rows (Main records)`. Văn bản quyết định giữ nguyên như kiến trúc.
- 2026-11-16: API-001 fixed. `OpenApiConfig.problemResponsesCustomizer` ghi 401 là `application/json` và `WWW-Authenticate: Bearer`.
- 2026-11-16: Người dùng trả lời `accepted-risk` cho `API-002`. Finding đóng. `specialist_review` chuyển `pass`. Không có vòng review thứ ba.
- 2026-11-16: Người dùng yêu cầu Main tự chạy smoke. Kết quả ghi trong `runtime-runbook.md`, mục `Kết quả người dùng ghi nhận`. `gates.runtime` chuyển `pass`. Không in token.
- 2026-11-16: Người dùng yêu cầu chuyển task sang trạng thái xong và commit. Workflow không có `done`. Trạng thái kết là `ready_to_merge`. `.env` không commit.
