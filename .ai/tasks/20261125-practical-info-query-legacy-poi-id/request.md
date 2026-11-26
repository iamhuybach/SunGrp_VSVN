# Request

## User outcome

Redesign `GET /api/v1/pois/{poi_id}/practical_info`. A new endpoint based on this one is allowed. Choose the option with the best fit and performance. Every `/api/v1/pois/**` endpoint returns the same mapped record for a legacy `poi_id` and for the new-model `poi_id`.

## Requirements (verbatim)

1. Thiết kế lại GET /api/v1/pois/{poi_id}/practical_info. Được tạo endpoint mới dựa trên endpoint này. Chọn phương án tối ưu và hiệu năng tốt.
   - id nhập được với biên dưới 0 và biên trên 500.
   - Thêm query required_fields. Không nhập thì trả toàn bộ field như hiện tại. Có nhập thì chỉ trả các field được chọn. Danh sách được chọn là phần detail của response hiện tại (các field data.* trong docs/context/api-mapping/practical_info.md). Không thêm field ngoài danh sách đó.
   - Thêm query source (partner hoặc google), lang, poi_name. lang đã có trên endpoint này; giữ cách resolve hiện tại.
   - Thêm phân trang page, size. meta của response có pagination tương ứng envelope hiện có (mẫu reviews).
   - Thêm sort_field (đúng một field) và sort_order (asc hoặc desc).
2. Mọi API: poi_id model cũ hoặc model mới đều trả được dữ liệu. Data poi_id model cũ đã được map sang model mới và khớp data model mới. Không bịa công thức poi_id thứ hai.

## Scope

### In scope

- `scope.systems`: `poi-serving-api`
- HTTP contract for practical info: `required_fields`, `source`, `lang`, `poi_name`, `page`, `size`, `sort_field`, `sort_order`, and an `id` input whose lower bound is 0 and upper bound is 500.
- Legacy and new `poi_id` on every `/api/v1/pois/**` endpoint, using the existing map. No second `poi_id` formula.
- API mapping docs updated before review. Tests named by the acceptance criteria.

### Out of scope

- Inventing a second `poi_id` formula.
- Adding a column, table, or key from the API side. If PostgreSQL DDL and the entity lack a legacy `poi_id` key, set `data_model_change` and do not patch the entity to fill the gap.
- Assigning the 0 and 500 bounds to `poi_id` (UUID text) or to `size`.
- Reading `docs/poi-serving-api/`, `notebooks_lgc/`, or pipeline manifests.
- Copying credentials or hosts into the repo or task artifacts.
- Commit. `docker compose`. Fabric DEV probes unless correctness depends on data that is not in the repo.

## Acceptance criteria

- Hợp đồng HTTP, JSON, lỗi, phân trang và lang khớp entity và gold contract (tests/test_srv_poi_serving_contract.py).
- required_fields rỗng hoặc vắng mặt trả đủ field detail như practical_info hiện tại. Có giá trị thì chỉ các field nằm trong whitelist detail.
- source chỉ nhận partner và google. sort_field chỉ một field trong whitelist sort. sort_order chỉ asc hoặc desc.
- page và size đi cùng meta.pagination. Trần size giữ theo AGENTS.md của service (size ≤ 100) trừ khi architecture ghi lệch và decision.md đã nhận.
- Mọi endpoint /api/v1/pois/** nhận poi_id cũ và poi_id mới, cùng một bản ghi đã map.
- Tài liệu mapping API được cập nhật trước review.
- Verify PASS trước review. P0/P1 của review được xử lý trong cap 2 vòng.

## Constraints

- API theo gold. Không thêm cột, bảng, khóa từ phía API. Thiếu khóa poi_id cũ trong DDL postgres và entity thì bật data_model_change, không sửa entity cho đủ.
- Không đọc docs/poi-serving-api/, notebooks_lgc/, manifest pipeline.
- Không chép credential hay host vào repo hay artifact.
- Không commit. Không chạy docker compose. Runtime để người dùng chạy theo runtime-runbook.md.
- Fast lane không áp dụng: có đổi hành vi và hợp đồng HTTP.
- id biên 0 và 500: D-ID-UNIT quyết định đây là số lượng giá trị `poi_id` trong một request, tối thiểu 1 và tối đa 500. Không phải miền số, không phải độ dài chuỗi, không phải `size` phân trang.
- Grain hiện tại của practical_info là một POI, một object, không có meta.pagination. Phân trang, source, poi_name và sort chỉ đứng trên response danh sách. Architect chọn giữ GET một POI và thêm endpoint danh sách, hoặc đổi endpoint hiện tại. Main không chọn trước.
- poi_id cũ: dùng map đã có trong mapping_legacy_gold_to_gld_srv.md. Nếu apps.srv_poi_* và gld_srv_serve.pg.sql chưa có khóa để resolve id cũ, viết handoffs/author-input.md và chạy python scripts/vv.py run-author --kind model (effort medium) trước Architect. Main không viết model-design.md.
- Evidence chỉ khi đúng/sai phụ thuộc dữ liệu chưa có trong repo. Không đoán tỉ lệ null, uniqueness hay dạng id cũ trên DEV.

## Classification rationale

- Complexity: high. Signals `design_tradeoffs` (keep the single-POI GET and add a list endpoint, or change the current endpoint; `poi_name` filter; sort whitelist) and `data_model_change` (serving PostgreSQL has no legacy key).
- Risk: high. Signal `cross_system`: legacy identity is `gld_poi_legacy_id_map` in `docs/context/mapping_legacy_gold_to_gld_srv.md` and `ref_poi_legacy_id` / `legacy_poi_id` in `docs/context/01_DATA_MODEL.md` §6.1 and §8. `sql/postgres/gld_srv_serve.pg.sql` and `apps.srv_poi_*` only key `poi_id`. A key change crosses gold and the serving API. `risk-gate` is required.
- Architecture: required. HTTP contract change and more than one viable implementation. Grain is an Architect choice. Main does not choose it in triage.
- Evidence: not required. The missing key and the published map are in the repository. The unbound unit of `id` is a user decision, not a data probe. Do not infer null rate, uniqueness, or the shape of legacy ids on DEV.
- Runtime proof: required. Behavior and the HTTP contract change. The service rule is a user-run `docker compose` smoke in `runtime-runbook.md`. Signal `runtime_proof_required`. Main does not run compose.
- Reviewer routing: `api-contract-reviewer` (paths, DTO, errors, paging, `lang`). `jpa-performance-reviewer` (the change touches `PoiService`, `PoiSpecifications`, and may touch an entity after the model). `app-security-reviewer` (`required_fields` and `sort_field` are request input that must stay on a whitelist, not dynamic JPQL built from raw strings).
- `id` bounds: `GET /{poi_id}/practical_info` takes only path `poi_id` and query `lang`. Serving DDL numeric columns (`rating_overall`, `rating_count`, `review_count`, `display_order`, `width_px`, `height_px`) have no 0..500 domain. Text columns have no length 500. Controller bounds that do exist are `page` `@Min(0)`, `size` `@Max(100)`, and other `@Size` caps (20, 64, 128). None is the pair 0 and 500. Stop for the unit before `run-gate`.
- Legacy key: confirmed absent from `sql/postgres/gld_srv_serve.pg.sql` and from Java entities. Model author runs after this decision, before the Architect. Main does not write `model-design.md`.
