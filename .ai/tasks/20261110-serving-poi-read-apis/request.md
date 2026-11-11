# Request

## User outcome

The six POI serving read APIs return the JSON contract below, and the six mapping files describe that same contract.

1. `POST /api/v1/pois/compact` accepts a JSON body `lang` (string) and `ids` (array of `poi_id` strings). `ids` has 1 to 20 items (user decision D-4, 2026-11-11). A missing or empty `ids`, or more than 20 items, is HTTP 422 `ERR_VALIDATION_FAILED`. Rows are ordered `created_at DESC, poi_id ASC`. `data[].cover.id` comes from `apps.srv_poi_info.cover_id`. `data[].cover.file_key` comes from `apps.srv_poi_info.cover_blob_url` (user decision D-1, 2026-11-10). The response and the mapping omit `data[].cover.blur_hash`, `data[].cover.width`, `data[].cover.height`, `data[].cover.mime_type`, `data[].business_tags.business_sector_label`, and `meta.pagination`. A malformed JSON body is HTTP 400 `ERR_BAD_REQUEST` (user decision D-6, 2026-11-11).
2. `GET /api/v1/pois/{poi_id}/gallery` does not call `validatePoiExists`. Query `page` and `size` are added. Rows are ordered by `display_order` ascending. `data[]` contains only `id`, `file_key`, and `display_order`. `file_key` comes only from `apps.srv_poi_media_gallery.blob_url`. `meta.pagination` uses the reviews envelope shape: `type`, `page`, `per_page`, `total_items`, `total_pages`, `has_next`, `has_prev`.
3. `GET /api/v1/pois/{poi_id}/reviews` does not call `validatePoiExists`. `rating_summary` is a sibling of `data`: one element `{rating_count, rating_avg_score}` (user decision D-5, 2026-11-11). `rating_count` comes from `apps.srv_poi_review.rating_count`. `rating_avg_score` comes from `apps.srv_poi_review.rating_overall`.
4. `GET /api/v1/pois/features` follows `docs/context/api-mapping/features.md` (overview, request header, request param, response, status code, sample request, sample response), after that file is updated so `data[].cover.id` comes from `apps.srv_poi_info.cover_id` and `data[].cover.file_key` comes from `apps.srv_poi_info.cover_blob_url` (user decision D-1, 2026-11-10). Selection follows user decision D-2, 2026-11-11.
5. `GET /api/v1/pois/{poi_id}/experiences` follows `docs/context/api-mapping/experiences.md`, same sections, after that file is updated so `data.items.source` comes from `apps.srv_poi_multi_lang.source_name` (user decision D-1, 2026-11-10).
6. `GET /api/v1/pois/{poi_id}/practical_info` follows `docs/context/api-mapping/practical_info.md`, same sections.

Required-field rule for all six APIs and all six mapping files: the only request field with Required = có is path `poi_id`, except compact body `ids`, which is required with 1 to 20 items (user decision D-4, 2026-11-11). Every other request header and request param stays, keeps its current default, and has Required = không. Missing `lang` and `Accept-Language` resolve to `vi`, as the mapping already states. Compact has no path `poi_id`. Body `lang` has Required = không.

All six success responses use `ApiResponse`, and the six mapping files are updated to that envelope (user decision D-3, 2026-11-11). Features includes full `meta.pagination`.

## Scope

### In scope

- `services/data-serving-service` read endpoints, DTOs, service mapping, and repository queries needed for the six contracts.
- `docs/context/api-mapping/compact.md`, `gallery.md`, `reviews.md`, `features.md`, `experiences.md`, `practical_info.md` (overview, params, response, samples), after lowering Required as above.
- Java tests for the changed endpoints and `tests/test_srv_poi_serving_contract.py` on the maven lane.
- `runtime-runbook.md` for a user-run `docker compose` smoke. Main does not run `docker compose`.

### Out of scope

- Splitting this into one task per API.
- `docs/context/api-mapping/MAPPING_SAMPLE.md`, `amenities.md`, `(ood).summary.md`, `(ood).must-know.md`, `(ood).general-information.md`.
- `docs/poi-serving-api/`.
- Task `20261110-split-api-mapping`.
- New columns, tables, keys, or `ALTER` in this task.
- Credentials or database hosts in the repository.

## Acceptance criteria

- Behavior and JSON match items 1–3 and the three mapping files in items 4–6, after the Required rule above.
- Every named source column exists in `sql/postgres/gld_srv_serve.pg.sql` and the matching entity.
- Changed-endpoint Java tests and `tests/test_srv_poi_serving_contract.py` pass on the maven lane. `gates.local_verification` is `pass` only when `python scripts/vv.py verify` runs with Docker.
- Reviewers: `api-contract-reviewer`. Add `jpa-performance-reviewer` when the diff touches a repository or a query. Add no other reviewer unless routing requires it.

## Constraints

- The API reads gold only through PostgreSQL `apps.srv_poi_*`.
- A missing source column stops the task: record it in `decision.md`, do not invent the column, do not open `ALTER` here.
- Main model is Grok 4.7 Medium. No approved `exceptions` entry.
- Commit only when the user asks in the current turn.

## Classification rationale

- Complexity: medium. Six read-contract changes in one service, with prescribed JSON for compact, gallery, and reviews. Features rotation and fallback are not fully specified in `features.md`.
- Risk: medium. Bounded read-behavior change. Rollback is reverting the API and the six mapping files. Local proof is the maven lane once the column contract is real.
- Architecture: required. The change spans one service and more than eight source files (controller, service, compact/gallery/review DTOs, three new response types, gallery or info repository queries, and the endpoint tests). Features rotation versus fallback is a material design tradeoff (`design_tradeoffs`). No grain, key, or CDC change, so `data_model_change` is not set.
- Evidence: not required to prove the missing columns. `sql/postgres/gld_srv_serve.pg.sql` and the entities already show `apps.srv_poi_media_gallery` has no `cover_id` or `cover_blob_url`, and `apps.srv_poi_multi_lang` has no `source`. Those names exist only as `apps.srv_poi_info.cover_id`, `apps.srv_poi_info.cover_blob_url`, and `apps.srv_poi_multi_lang.source_name`.
- Runtime proof: required after implementation. The user runs `docker compose` from `runtime-runbook.md`. `runtime_proof_required` is set. This session stops before that runbook because the column contract is absent.
- Reviewer routing: `api-contract-reviewer` because the diff touches `api/` and `dto/`. `jpa-performance-reviewer` because the diff touches `service/` and repository queries (gallery page and order, features selection). `app-security-reviewer` stays off the plan: the planned diff does not touch `common/web/`, `config/`, `application*.yml`, `pom.xml`, or Docker files. `risk_level` is medium, so `risk-gate` is not required.
