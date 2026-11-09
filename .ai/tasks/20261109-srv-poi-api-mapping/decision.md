# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Phạm vi | Không đổi hành vi. Không `data_model_change`. Không fast lane vì hơn 2 file. `architecture_required` false, `evidence_required` false, `complexity` low, `risk_level` low. Không commit. | request.md ## Constraints | 2026-11-09 |
| D-02 | Review | `required_reviewers` rỗng. `api-contract-reviewer` khi diff chạm `api/`, `dto/`, `domain/entity/`, `OpenApiConfig`, hoặc `sql/postgres/gld_srv_serve.pg.sql`. `app-security-reviewer` và `jpa-performance-reviewer` khi diff chạm các path tương ứng ở WORKFLOW.md §7. Diff tài liệu này không chạm các path đó. Không fast lane vì hơn 2 file. Không có signal `data_model_change`. | request.md ## Classification rationale | 2026-11-09 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-09: commit và push lên `main`.

## Lịch sử quyết định

- 2026-11-09 D-01: ghi phạm vi tài liệu, không đổi hành vi, không architecture, không evidence.
- 2026-11-09 D-02: không route specialist review vì diff không chạm contract Java hay SQL.
