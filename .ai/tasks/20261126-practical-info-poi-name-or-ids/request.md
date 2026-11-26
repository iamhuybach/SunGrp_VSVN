# Request

## User outcome

`POST /api/v1/pois/practical_info` accepts `poi_name` or `ids` in the JSON body as alternative selectors. A name does not filter the id set. `GET /api/v1/pois/{poi_id}/practical_info` stays unchanged.

## Scope

### In scope

- `POST /api/v1/pois/practical_info` body contract, validation, SQL selection, tests, and `docs/context/api-mapping/practical_info_list.md`.
- `scope.systems`: `poi-serving-api`.
- Replace the AND behavior shipped by task `20261126-practical-info-poi-name-body`.

### Out of scope

- `GET /api/v1/pois/{poi_id}/practical_info`.
- Query parameters `required_fields`, `source`, `lang`, `page`, `size`, `sort_field`, `sort_order`.
- Gold schema, new columns, tables, or keys.
- `docs/poi-serving-api/`.
- Fast lane. The HTTP contract changes.
- The deploy repo `D:\git\SunGrp_VSVN_API` until this task's contract is implemented here.

## Yêu cầu nguyên văn

poi_name bạn đã làm sai yêu cầu. Tôi muốn nó được query tương đương với ids chứ không phải được filter từ ids. Ở body request có thể nhập poi_name hoặc ids.

## Acceptance criteria

- A body with only `ids` selects those POIs and does not apply a name predicate.
- A body with only `poi_name` selects by name and does not require `ids`.
- A body with both selectors returns the union of the two selections. It does not return the intersection.
- A body with neither selector returns 422.
- `poi_name` stays one string, maximum 128. Longer than 128 returns 422. A non-string JSON value returns 400.
- The name match stays the documented rule: contains, case-insensitive, on `apps.srv_poi_info.poi_name`, with `%`, `_`, and `\` escaped.
- When `ids` is present it keeps the current rules: 1 to 500 strings, each non-empty and at most 128 characters. An empty `ids` array is "no id selector", not a 422, when `poi_name` is present.
- The `poi_name` query parameter still does not filter.
- `source`, paging, and sort still apply to the selected rows.
- `docs/context/api-mapping/practical_info_list.md` matches this contract before review.
- Local verification PASS before review. P0/P1 findings are handled within two review rounds.

## Constraints

- The API follows gold. Do not add columns, tables, or keys.
- Do not read `docs/poi-serving-api/`.
- Do not copy credentials or hosts into the repository or task artifacts.
- Do not commit. Do not run `docker compose` unless the user asks in the current turn.
- `SrvPoiLegacyIdMapRepositoryImpl.findPracticalInfoPage` currently returns an empty page when `ids` is empty before the name predicate is applied. That is the behavior to replace.

## Classification rationale

- Complexity: medium. The selector moves from "ids required, name filters those ids" to "ids or name, union when both are present". The repository SQL changes. No CDC, watermark, or grain change.
- Risk: medium. Bounded HTTP and query behavior change. Rollback is reverting the endpoint. Local tests can prove the selectors.
- Architecture: required. `docs/AGENT_PROMPT_SAMPLES.md` A20 requires architecture when the HTTP contract changes. The previous architecture of `20261126-practical-info-poi-name-body` specified AND and is withdrawn.
- Evidence: not required. The name match rule is already in `docs/context/api-mapping/practical_info_list.md` and `containsPattern`. This change is which predicate is applied, not an unknown data distribution.
- Runtime proof: required. Signal `runtime_proof_required`. The user runs `docker compose` from `runtime-runbook.md` unless a later turn says otherwise.
- Reviewer routing (`WORKFLOW.md` §7): `api-contract-reviewer` because `api/` and `dto/` change. `jpa-performance-reviewer` because the repository SQL changes. `app-security-reviewer` is added before review only if the diff touches `common/web/`. Risk is medium, so `risk-gate` is not required.
