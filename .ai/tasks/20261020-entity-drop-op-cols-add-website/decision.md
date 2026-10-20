# Decision

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Cột op trên entity | Chỉ bỏ `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at` khỏi `lh_vv_silver.dbo.slv_poi_entity_non_enrich`. Giữ nguyên bốn cột trên các bảng `slv_3p_*`. | request.md User outcome | 2026-10-20 |
| D2 | `website_url` | `website_url` là STRING, nullable. Dòng google lấy `slv_3p_poi_contact.website_url` qua `poi_id`. Dòng partner lấy giá trị của key `website_url` trong JSON `slv_pn_business_services.website_urls`. Không có key thì null. Không ghi URL mẫu vào seed hay test. | request.md Constraints | 2026-10-20 |
| D3 | Grain contact | Grain `slv_3p_poi_contact` trong data model và registry là `poi_id`. Nhiều dòng contact cho một `poi_id` thì ghi `USER_DECISION`, không chọn dòng. | request.md Constraints | 2026-10-20 |
| D4 | DEV drop và watermark | Drop và xóa watermark chỉ với `slv_poi_entity_non_enrich` và `slv_poi_amenity` trên DEV để chạy lại như init. Không drop bảng nguồn, `ref_dictionary_place_type`, hay `ref_dictionary_amenities`. Runbook ghi môi trường DEV, bước đếm trước khi xóa, lệnh drop, watermark bị xóa, cách dựng lại và cách quay lại. User chạy Fabric DEV. Agent không đánh `gates.runtime`. | request.md Yêu cầu bổ sung | 2026-10-20 |
| D5 | Watermark được xóa | Xóa dòng watermark có `trg_tbl` là `slv_poi_entity_non_enrich` hoặc `slv_poi_amenity` (`wm_e__<trg_tbl>__<src_tbl>`). Không xóa `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`. | CTRL_TABLES_CONTEXT.md §4; request.md Yêu cầu bổ sung | 2026-10-20 |
| D6 | Nguồn model | Task không có `proposal.md`. `model-design.md` bám D1–D5. Không chạy lane proposal. Không đổi công thức `poi_id` partner và không sửa `AGENTS.md` trong task này. | model-design.md Conflicts 1–2 | 2026-10-20 |
| D7 | Join contact | Google không có dòng `slv_3p_poi_contact`: left join, `website_url` null. Không inner join, vì grain entity vẫn một dòng mỗi `poi_id`. `slv_3p_poi_contact` là input bắt buộc của node (thiếu bảng thì fail). Trùng `poi_id`: fail run, không chọn dòng, không ghi entity. | D2, D3; model-design.md Conflicts 3–4, 7 | 2026-10-20 |
| D8 | JSON partner | Lấy key top-level bằng `top_level_text` (UDF). Không dùng `get_json_object`. Chỉ khi giá trị là chuỗi JSON. Không có key, JSON null, JSON không hợp lệ, hoặc giá trị không phải chuỗi JSON thì null. Chuỗi rỗng giữ nguyên, không trim. Khoá trùng ở tầng gốc: `json.loads` lấy khoá sau. Không tìm key ở độ sâu khác. `website_url` đứng ngay sau `primary_type`. | D2; architecture.md §3 | 2026-10-20 |
| D9 | Cột estimate | `slv_poi_entity_non_enrich` thêm `range_low_min`, `range_high_min`, `avg_range_min`, `candidate_best_time_code`, `canonical_candidate` từ đúng dòng `ref_dictionary_place_type` mà entity đã khớp. Không thêm rule khớp thứ hai. Không seed lại từ điển. Với partner: dòng `ref_dictionary_place_type` partner mà entity đã khớp qua `primary_type`. | request.md Yêu cầu bổ sung; user 2026-10-20 | 2026-10-20 |
| D10 | `service_flags` | `slv_poi_amenity` thêm `service_flags` từ đúng dòng `ref_dictionary_amenities` mà amenity đã khớp. Không thêm rule khớp thứ hai. Không seed lại từ điển. | request.md Yêu cầu bổ sung | 2026-10-20 |
| D11 | Estimate khi không khớp | Không có dòng `ref_dictionary_place_type` đã khớp thì năm cột estimate là NULL. Không đặt giá trị mặc định. Google: cả `_p` và `_m` đều null. Partner: `primary_type` null hoặc không có dòng `dp`. | architecture.md §3 Conflicts 2 | 2026-10-20 |
| D12 | Vị trí cột | `website_url` đứng sau `primary_type`. Năm cột estimate đứng sau `category_group`, đúng thứ tự DDL `a1setupddl`. `service_flags` đứng sau `amenity_vi`. | architecture.md §3 Conflicts 3 | 2026-10-20 |
| D13 | Khoá khi đổi cạnh và khi reset | Cell `entwebpy` tạo dòng `wm_flow__` nếu chưa có, nhận khoá, đọc lại `lock_exec_id`, rồi mới INSERT cạnh, nhả khoá trong `finally`. Runbook R3 tách nhận khoá, đọc lại, DROP/DELETE, rồi nhả. Rollback nhận khoá trước khi đổi code và cạnh. Notebook dựng lại tự nhận khoá nên runbook nhả ngay trước các notebook đó. | reviews/round-1.md STATE-001, STATE-002, STATE-003 | 2026-10-20 |
| D14 | Tag tham số amenity | Cell `d1amenparam` của `NB_SLV_POI_AMENITY` phải có tag Fabric `parameters`. Không có tag thì `runMultiple` không ghi `p_exec_id`, node chạy như chạy tay và từ chối khoá của `NB_00`. | runtime exec `4704e1a4-d6fd-446b-a320-962dc8d0dbb9` | 2026-10-20 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-001 | P1 | fixed | Runbook R3a nhận khoá cả khi chưa có dòng flow, R3b đọc lại `lock_exec_id` trước DROP, R3d nhả sau khi kiểm tra. | |
| STATE-002 | P1 | fixed | `entwebpy` giữ khoá từ trước INSERT đến `finally`. Không còn cửa sổ INSERT khi khoá trống. | |
| STATE-003 | P1 | fixed | Rollback chạy R3a/R3b trước revert và trước UPDATE cạnh. DROP nằm trong lúc còn khoá. Nhả ngay trước notebook cũ vì notebook đó tự nhận khoá. | |
| STATE-004 | P1 | fixed | `finally` ghi `FAILED` khi có exception, `SUCCESS` khi không. Exception được raise lại. | |
| STATE-005 | P1 | accepted-risk | User chấp nhận khoá hiện tại ngày 2026-10-20. Mỗi lần chạy `entwebpy` có một token `uuid`, chỉ nhận khoá khi trống hoặc quá 90 phút, và chỉ nhả đúng token của lần đó. Không thêm fencing generation. Không chạy cell này song song với `NB_00` hoặc với một lần chạy cell khác. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Lịch sử quyết định

### 2026-10-20 — Triage, đường bốn cột op và `website_url`

Bốn cột op vào `slv_poi_entity_non_enrich` vì `POI_COLS` trong cell `b1entitybuild` của `NB_SLV_POI_ENTITY_NON_ENRICH` gồm `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`. `_google` select `*POI_COLS`. `_partner` cast null theo schema của nhánh google. `TABLE_SPECS` trong `NB_SETUP_INITIAL_DDL` cell `init_tables` lặp lại bốn cột đó trước `house_number`. Chúng là `SNAPSHOT_TECH_COLUMNS` của L1 3rd-party (`docs/context/02_NAMING_CONVENTION.md` §5.2), không phải cột L2.

`website_url` chưa có trên entity. Registry `slv_3p_poi_contact` (key `poi_id`) có `website_url` từ `websiteUri` trong `NB_SETUP_INITIAL_DDL` / `NB_CREATE_DDL` cell `e9c137c5`. `SPEC.inputs` của entity chưa có contact. `slv_pn_business_services.website_urls` đã là cột STRING (toast) trong registry partner. `NB_SLV_POI_AMENITY` chỉ đọc `poi_id`, `business_sector`, `source_name`, `types_json` của entity.

Cạnh active hiện có của entity (`PL_VV_TRANS_SLV_TO_SLV_1H`): `slv_3p_poi`, `slv_3p_poi_address`, `ref_dictionary_place_type`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`. `NB_SETUP_POI_AMENITY` đếm đúng 5 cạnh đó. Thêm cạnh `slv_3p_poi_contact` làm số này thành 6.

Không có `USER_DECISION` mở: D1–D8 đã chốt. Chưa có probe. Grain contact lấy từ data model và registry, chưa đếm dòng trùng trên DEV.

`model-design.md` Conflicts 1–7 được đóng bằng D6–D8: không proposal, không đổi `poi_id`, left join null, fail khi trùng `poi_id`, JSON top-level, cột đứng sau `primary_type`, contact là input bắt buộc.

### 2026-10-20 — Bổ sung cột estimate và `service_flags`

`ref_dictionary_place_type` trong `NB_SETUP_POI_ENTITY` cell `a1setupddl` đã có `range_low_min`, `range_high_min`, `avg_range_min` kiểu INT nullable và `candidate_best_time_code`, `canonical_candidate` kiểu STRING nullable. Entity cell `b1entitybuild` vẫn chỉ `pick` bốn `CATEGORY_COLS`.

`ref_dictionary_amenities` trong `NB_SETUP_POI_AMENITY` đã có `service_flags` STRING nullable. Cell `d1amenbuild` collect từ điển không lấy cột này; `OUT_COLS` chưa có `service_flags`.

D4–D5 đổi tại chỗ: drop và xóa watermark của cả hai bảng đích. D9–D10 chốt cột mới lấy từ dòng từ điển đã khớp.

### 2026-10-20 — Partner estimate và Architect fallback

User chốt: với partner, năm cột estimate lấy từ dòng `ref_dictionary_place_type` partner mà entity đã khớp qua `primary_type`. D9 sửa tại chỗ. Không thêm rule khớp thứ hai. `model-design.md` Conflicts 1 được ledger đóng; file model không viết lại trong lượt này.

User cho phép tạm dùng Opus 5.5 effort medium trên Cursor cho chat này vì Claude Architect hết session limit. Cursor không có model đó. Không thay bằng Opus 5.5 low. Không ghi `exceptions`. Không chạy architecture.

User nhắc lại: chọn (a) nhưng effort medium. Task tool chỉ nhận model slug, không có tham số effort riêng. Slug Opus 5.5 trên Cursor là effort low. Không gọi subagent. Không ghi `exceptions`.

Ảnh picker và một lần gọi thử sau đó cho thấy Cursor có Claude Opus 5.5 Medium. Slug subagent `claude-opus-5-5-medium` được nhận. Exception `cursor-architect-opus-medium` đã ghi rồi bị gỡ: user rút fallback, Architect chạy lại bằng Claude CLI Opus 5.5 effort high. Subagent Cursor viết architecture bị hủy, `architecture.md` vẫn là placeholder.

### 2026-10-20 — Architecture PASS

`run-gate` trả `ARCHITECTURE PASS`. D8 đổi cơ chế sang `top_level_text` vì `get_json_object` trả text cho giá trị không phải chuỗi. D11 và D12 ghi NULL khi không khớp và vị trí cột. Không có `USER_DECISION` mở.

### 2026-10-20 — Vòng review thứ 3

User phê duyệt thêm một vòng review sau khi vòng 2 trả `FIX_REQUIRED` cho STATE-004 và STATE-005. Hai finding đã sửa trước khi phê duyệt. `review_plan.extra_round_approved_on` = 2026-10-20. `rounds.verification` giữ 2 vì cap verification là 2; lần verify thứ ba vẫn PASS nhưng không tăng counter.

### 2026-10-20 — Chấp nhận khoá hiện tại

Vòng 3 giữ STATE-005 mở vì không có fencing generation. User chấp nhận khoá hiện tại và không sửa thêm. STATE-005 chuyển thành `accepted-risk`. Implement đã xong trước đó: notebook, test, docs và runbook DEV. Bước còn lại là user chạy runbook trên Fabric DEV.

### 2026-10-20 — Amenity thiếu tag `parameters`

Lần `NB_00` exec `4704e1a4-d6fd-446b-a320-962dc8d0dbb9`: entity `SUCCESS`, `inserted = 65`, tiến 6 cạnh. Amenity `ConfigError` vì `p_exec_id` rỗng trong lúc chính exec đó giữ khoá. Cell `d1amenparam` không có tag `parameters`; cell `b1entityparam` có. D14 gắn lại tag. Không DROP entity.

### 2026-10-20 — User xác nhận runtime

User xác nhận `gates.runtime = pass` sau R5 và lần `NB_00` idempotent exec `86a52eee-474c-45ec-9d3b-2483cab3b0aa` (`NO_DATA`, 0 Dirty Edge). `specialist_review` và `risk_gate` giữ `fix_required` vì vòng 3 không trả `PASS`. STATE-005 vẫn `accepted-risk`. Task chưa sang `ready_to_merge`.
