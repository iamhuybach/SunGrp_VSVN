# Request

## User outcome

`POST /api/v1/pois/practical_info` accepts `poi_name` in the JSON body next to `ids`, applies both filters together, and no longer filters on the `poi_name` query parameter. `GET /api/v1/pois/{poi_id}/practical_info` stays unchanged.

## Scope

### In scope

- `POST /api/v1/pois/practical_info`: move `poi_name` from the query string into the JSON body, beside `ids`.
- Validation, body-size ceiling, mapping doc `docs/context/api-mapping/practical_info_list.md`, and tests for that contract.
- `scope.systems`: `poi-serving-api`.

### Out of scope

- `GET /api/v1/pois/{poi_id}/practical_info`.
- Query parameters `required_fields`, `source`, `lang`, `page`, `size`, `sort_field`, `sort_order`.
- Gold schema, new columns, tables, or keys.
- `docs/poi-serving-api/`.
- Fast lane. An HTTP contract change is in scope.

## Yêu cầu nguyên văn

POST /api/v1/pois/practical_info thay đổi:
- Đưa poi_name vào Body Request giống ids. Để có thể query theo cả body và poi_name.

Diễn giải đã chốt cho hợp đồng hiện tại:
- Body JSON hiện chỉ có ids. poi_name đang là query, chuỗi, không bắt buộc, tối đa 128, rỗng thì không lọc, khớp không phân biệt hoa thường trên apps.srv_poi_info.poi_name, escape %, _ và \.
- Chuyển poi_name vào body, cùng cấp với ids. Vẫn một chuỗi, không thành mảng. Bỏ query poi_name.
- ids giữ nguyên: bắt buộc, 1 đến 500 chuỗi, mỗi chuỗi không rỗng, dài tối đa 128.
- Một request lọc bằng cả ids và poi_name. poi_name rỗng hoặc vắng thì chỉ lọc theo ids, đúng hành vi hiện tại.
- GET /api/v1/pois/{poi_id}/practical_info không đổi. required_fields, source, lang, page, size, sort_field, sort_order giữ là query.

Tiêu chí nghiệm thu:
- POST nhận {"ids":[...], "poi_name":"..."} và áp cả hai điều kiện.
- Query poi_name không còn tác dụng lọc.
- Trần và cách khớp poi_name giữ như docs/context/api-mapping/practical_info_list.md.
- ids vẫn 422 khi rỗng hoặc quá 500. poi_name dài hơn 128 thì 422.
- PracticalInfoBodyLimitFilter vẫn chặn body quá lớn trước khi gọi service, và vẫn đủ chỗ cho 500 id cộng poi_name tối đa.
- docs/context/api-mapping/practical_info_list.md cập nhật trước review: poi_name sang mục Request body, sample request đổi theo.
- Verify PASS trước review. P0/P1 được xử lý trong cap 2 vòng.

## Acceptance criteria

- `POST` accepts `{"ids":[...], "poi_name":"..."}` and applies both conditions.
- A `poi_name` query parameter no longer filters.
- The `poi_name` length ceiling and match rules stay as in `docs/context/api-mapping/practical_info_list.md`.
- `ids` still returns 422 when empty or longer than 500. `poi_name` longer than 128 returns 422.
- `PracticalInfoBodyLimitFilter` still rejects an oversized body before the service runs, and the ceiling still fits 500 ids plus a maximum-length `poi_name`.
- `docs/context/api-mapping/practical_info_list.md` is updated before review: `poi_name` moves to the Request body section and the sample request matches.
- Local verification PASS before review. P0/P1 findings are handled within two review rounds.

## Constraints

- The API follows gold. Do not add columns, tables, or keys.
- Do not read `docs/poi-serving-api/`.
- Do not copy credentials or hosts into the repository or task artifacts.
- Do not commit. Do not run `docker compose`. The user runs runtime steps from `runtime-runbook.md`.
- Fast lane does not apply: the HTTP contract changes.

## Classification rationale

- Complexity: medium. The change moves one filter across the controller, request DTO, query object, body-limit filter, tests, and the mapping doc. No concurrency, CDC, watermark, or grain change.
- Risk: medium. Bounded HTTP behavior change. Rollback is reverting the endpoint. Local tests can prove the contract. `WORKFLOW.md` §5 low is a change with no behavior change or a narrower local proof; this changes which request part filters `poi_name`.
- Architecture: required. `docs/AGENT_PROMPT_SAMPLES.md` A20 requires architecture when the HTTP contract changes. Evidence does not block architecture: the match rule is already in the mapping doc and the repository.
- Evidence: not required. Correctness of the existing `poi_name` match (case-insensitive, escape `%`, `_`, and `\`) is already written in `docs/context/api-mapping/practical_info_list.md` and the repository. Local tests can prove the new binding.
- Runtime proof: required. The user runs `docker compose` from `runtime-runbook.md`. Signal: `runtime_proof_required`.
- Reviewer routing (`WORKFLOW.md` §7): `api-contract-reviewer` because the diff touches `api/` and `dto/`. `app-security-reviewer` because the acceptance criterion names `PracticalInfoBodyLimitFilter` under `common/web/`. `jpa-performance-reviewer` is added before review only if the diff touches `domain/repository/` or SQL. Risk is medium, so `risk-gate` is not required.
