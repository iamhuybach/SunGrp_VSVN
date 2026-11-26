# Request

## User outcome

`destinations.id` and `destinations.name` in the POI serving API are JSON arrays of strings. A stored text value that is already a JSON array is parsed. The response no longer wraps that array in a string.

## Scope

### In scope

- `CompactPoiResponse.Destinations`, used by compact and practical info, including `POST /api/v1/pois/practical_info`.
- The mapping from `apps.srv_poi_info.destination_id` and `destination_name`.
- Tests and `docs/context/api-mapping/compact.md`, `practical_info.md`, and `practical_info_list.md`.
- `scope.systems`: `poi-serving-api`.

### Out of scope

- Gold columns, tables, and keys. The columns stay `text`.
- `docs/poi-serving-api/`.
- Fast lane. The HTTP response shape changes.

## Yêu cầu nguyên văn

Vậy hãy sửa như bạn khuyến nghị.

Khuyến nghị đã chốt: parse `destination_id` và `destination_name` thành mảng JSON. `null` hoặc chuỗi rỗng vẫn là `null`. Không xóa ký tự `\` trong chuỗi. Không bịa mảng khi giá trị không phải mảng JSON.

## Acceptance criteria

- A column value `["a","b"]` is returned as a JSON array `["a","b"]`, not as a string.
- `null` and blank text become JSON `null`.
- A value that is not a JSON array becomes JSON `null`. The list or detail request still returns 200. Do not invent elements.
- An array element that is not a JSON string becomes JSON `null` for that field. Do not coerce numbers or objects into strings.
- Compact and practical info use the same shape.
- The mapping docs show `id` and `name` as arrays before review.

## Constraints

- The API follows gold. Do not add columns, tables, or keys.
- Do not read `docs/poi-serving-api/`.
- Do not copy credentials or hosts into the repository or task artifacts.
- Do not commit. Do not run `docker compose` unless the user asks in the current turn.

## Classification rationale

- Complexity: medium. One shared DTO and the two service mappings change, plus tests and three mapping docs. No SQL or grain change.
- Risk: medium. Clients that read `destinations.id` as a string must read an array. Rollback is reverting the DTO.
- Architecture: required. A20 requires architecture when the HTTP contract changes.
- Evidence: not required. The user sample shows a JSON array stored in the text column, and `gld_srv_serve.pg.sql` types both columns as `text`.
- Runtime proof: required. Signal `runtime_proof_required`.
- Reviewer routing: `api-contract-reviewer` because `api/dto` changes. `jpa-performance-reviewer` because `service/PoiService` changes. `app-security-reviewer` only if the diff touches `common/web/`. Risk is medium, so `risk-gate` is not required.
