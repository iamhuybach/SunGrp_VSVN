# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | Evidence bronze | `experiences` là mảng 360/360, khóa phần tử `description,keyword,title`. `destinations` là mảng 113/113. 271 phần tử, 1 phần tử `id` và `name` null, 1 mảng không có khóa ở phần tử đầu. `translated_at` parse_null=0 trên 360 dòng. | evidence/results/probe_json_shape_rest.txt | 2026-11-16 |
| D-2 | Ngoài phạm vi sửa | Không sửa `gld_enr_poi_info`, cell lịch sử `NB_CREATE_DDL`, `slv_poi_entity_non_enrich.street`, và `(ood).general-information.md`. | request.md ## Constraints | 2026-11-16 |
| D-3 | Khoá silver | `slv_enr_poi_info_multi_lang`: một dòng cho `(poi_id, lang)`, MERGE đúng cặp đó. `slv_enr_poi_destination`: một dòng cho `poi_id`. `version` không nằm trong khoá. Cùng khoá thì giữ `version` lớn hơn; bằng `version` thì giữ `EventProcessedUtcTime` lớn hơn. | docs/context/mapping_gld_srv_poi_multi_lang.md §2; docs/context/mapping_gld_srv_poi_info.md §1.6 | 2026-11-16 |
| D-4 | Extract | `load_mode = DOC`. `src_object = $`. Cột gốc: `_doc.poi_id`, `_doc.source`, `_doc.lang`. Cột trong `data`: path JSON đã nêu. `convert_rule = NONE` cho STRING và `lat`/`lng`. `translated_at` là TIMESTAMP, `ISO_UTC_TS`, `parse_null = 0`. `country_code` và `postal_code` ghi NULL. Watermark `EventProcessedUtcTime`. | evidence/results/probe_json_shape_rest.txt | 2026-11-16 |
| D-5 | full_address | Nối bằng `, ` (phẩy và một dấu cách). Một field null, hoặc `house_number` hay `street` chỉ còn khoảng trắng sau trim, thì bỏ cả nhóm. Ba nhóm chỉ khi có dòng destination; không có thì giữ `full_address` của entity. | docs/context/mapping_gld_srv_poi_info.md §1.6; người dùng U-2 và U-4, 2026-11-17 | 2026-11-17 |
| D-6 | Cột và tên bảng | Cột chữ mới là STRING. `destination` là chuỗi JSON của cả mảng. `data.experiences` ghi vào `experience` STRING. Giữ tên hai bảng `slv_enr_*`. Bỏ Mapping `TRG-005`. `apps.srv_poi_multi_lang.cost_vnd` thành `cost`, giữ `text`. `practical_info.md` nằm trong phạm vi. | docs/context/mapping_gld_srv_poi_multi_lang.md §2 | 2026-11-16 |
| D-7 | PC-01 nguồn slv_enr_ | Người dùng chấp nhận lệch PC-01 trên `SRC-003` và `SRC-004`. Giữ nguyên tên `slv_enr_poi_info_multi_lang` và `slv_enr_poi_destination`. | Người dùng, 2026-11-16; MAPPING.md `MQ-001` | 2026-11-16 |
| D-8 | Quyết định Architect | A-1 đến A-9 giữ nguyên. A-10 bị A-11 và A-12 thay. A-11: silver đổi schema bằng overwrite tại chỗ, không DROP, không column mapping, lỗi thì RESTORE. A-12: gold `cost_vnd` thành `cost` bằng overwrite tại chỗ, chỉ trong runbook B5.1, protocol giữ 1/2. A-13: preflight extract và guard gold trong `build`. A-14: thứ tự B1 đến B5; `ALTER` Postgres ngay sau rewrite gold. A-15: blank trong D-5 là Spark `trim(x) = ''`. | architecture.md §19 | 2026-11-17 |
| D-9 | U-1 U-2 U-3 | U-1: sửa parser để `{text, label}` thành `{label, value=text}`. U-2: ba nhóm `full_address` chỉ khi có dòng destination; không có thì giữ `full_address` của entity. U-3: `destination_id` và `destination_name` là chuỗi JSON mảng, kể cả null. | Người dùng, 2026-11-17 | 2026-11-17 |
| D-10 | Probe P-1 P-3 P-4 | `slv_enr_poi_info_multi_lang` có 3 dòng, không tạo lại bảng. `slv_enr_poi_destination` có 0 dòng. Gold multi_lang 859 dòng sống, 0 dòng `deleted_at`, reader 1, writer 2. Mọi `poi_id` bronze khớp entity. Destination JSON không có chuỗi rỗng. Partner entity có 39 `house_number` rỗng và 39 `street` rỗng. | evidence/results/probe_arch_gaps.txt | 2026-11-17 |
| D-11 | Copy Job | Gold sang `apps.srv_poi_*` bằng Fabric Copy Job, 15 phút một lần, mode ghi `apps.srv_poi_multi_lang` là merge. Job map cột theo tên hiện có trên gold. Job tạm dừng được. B5 dừng job, chạy `enrgldpy`, `ALTER` `cost_vnd` thành `cost`, rồi mở lại job. | Người dùng, 2026-11-17 | 2026-11-17 |
| D-12 | NOT NULL Delta | `ALTER COLUMN SET NOT NULL` bị Delta từ chối. Silver giữ `poi_id` nullable. Gold giữ `poi_id` và `lang` nullable. Không `RESTORE` vì lỗi này. Extract vẫn reject khóa rỗng. | B2 và B5, 2026-11-17 | 2026-11-17 |
| D-13 | ward district city | Có dòng destination: `ward`/`district`/`city` lấy cột mới trên `slv_enr_poi_destination`. Null hoặc `trim` rỗng thì lấy `old_ward`/`old_district`/`old_city`. Cả hai trống thì null. Partner chưa có dòng destination giữ nhánh cũ: `ward` và `city` từ entity, `district` null. | Người dùng, 2026-11-17 | 2026-11-17 |
| D-14 | Sẵn sàng merge | Người dùng chuyển task sang `ready_to_merge` sau khi runtime pass. Findings đã `fixed`, `open_findings` rỗng. `specialist_review` và `risk_gate` chuyển `pass` theo lệnh merge này. Không có vòng Codex mới. | Người dùng, 2026-11-17 | 2026-11-17 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Delta trên silver từ chối `ALTER COLUMN ... SET NOT NULL` (`Cannot change nullable column to non-nullable: poi_id`, B2 2026-11-17). Cell `enrbrzpy` và `enrgldpy` bỏ qua lỗi này, không `RESTORE`. Cột giữ nullable của Delta. Extract vẫn reject khóa rỗng.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P0 | fixed | `_cdc_ts_ms` là `version`. State so `(version, EventProcessedUtcTime, event_id)`. | |
| GATE-002 | P1 | fixed | Bỏ `sources`, `TABLE_SOURCE`, `_crawled_at` trong code chạy. | |
| GATE-003 | P1 | fixed | `_src_version` được giữ qua các `select` tới MERGE. | |
| GATE-004 | P1 | fixed | JSON `destinations` hỏng tăng `_cn__` và FAIL trước MERGE. | |
| GATE-005 | P1 | fixed | `event_id` rỗng bị reject. Cùng bộ thứ tự mà payload khác thì dừng. | |
| GATE-006 | P1 | fixed | `SKIP` sau commit rewrite kiểm lại từ version trước; lệch thì `RESTORE`. | |
| GATE-007 | P1 | fixed | Lease rewrite 780 phút. Gia hạn và xác nhận chủ khoá trước khi ghi hoặc `RESTORE`. | |
| GATE-008 | P1 | fixed | Runbook B5: dừng Copy Job, xác nhận không còn run, `enrgldpy`, `ALTER`, deploy API, NB_00, rồi mới mở job. Lỗi thì không mở job. | |
| GATE-010 | P0 | fixed | Chỉ `RESTORE` khi HEAD vẫn là commit của attempt. Commit sau đó thì dừng, phục hồi thủ công. | |
| GATE-011 | P1 | fixed | `_fence` gia hạn khoá và dừng nếu version Delta đổi trước overwrite, `ALTER`, và `SET TBLPROPERTIES`. | |
| GATE-009 | P1 | fixed | Thêm dấu phẩy giữa tuple watermark trong `NB_CREATE_DDL`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-16: AQ-001 đến AQ-007 và AQ-009 chốt đúng khuyến nghị, với AQ-006 bỏ `TRG-005`. AQ-008 hỏi khoá của `apps.srv_poi_multi_lang`; dòng Mapping bảng đó đã bỏ.
- 2026-11-16: Chấp nhận lệch PC-01 trên `SRC-003` và `SRC-004`. Giữ nguyên tên hai bảng.
- 2026-11-17: U-1 sửa parser `{text, label}` thành `{label, value=text}`. U-2 ba nhóm chỉ khi có dòng destination. U-3 giữ chuỗi JSON mảng. U-4: `house_number` hoặc `street` chỉ còn khoảng trắng thì bỏ cả nhóm `full_address`. Copy Job map cột theo tên hiện có trên gold.
- 2026-11-17: GATE-001 đến GATE-007 và GATE-009 sửa theo review. GATE-008: Copy Job tạm dừng được. B5 dừng job, chạy `enrgldpy`, `ALTER`, rồi mở lại.
- 2026-11-17: Chấp nhận bản sửa sau cap review cho GATE-010, GATE-011 và GATE-008. Không có review vòng 3.

## Lịch sử quyết định

- 2026-11-16 D-1 lúc triage: chưa điền Mapping. Probe là việc tiếp theo.
- 2026-11-16 D-1 sau probe: `event_id` 473/473. `LANG` 360, duy nhất theo `(poi_id, lang)` và theo `(poi_id, lang, version)`. `DESTINATION` 113, duy nhất theo `poi_id` và theo `(poi_id, version)`. `produced_at`, `EventProcessedUtcTime`, `EventEnqueuedUtcTime` đều `nulls=0`. `$.address.new.district.name` và `name_with_type` nonempty 0/113. Các path LANG đã nêu nonempty 360/360. Không suy ra khoá vĩnh viễn từ snapshot một khoảng 07:05–07:07.
- 2026-11-16: requirements-analysis `EVIDENCE_REQUIRED`. Chưa sang model-design.
- 2026-11-16 D-3 đến D-6: người dùng chốt khoá, extract, dấu nối `, `, kiểu cột, `experience`, bỏ `TRG-005`, giữ tên `slv_enr_*`, `practical_info.md` trong phạm vi.
- 2026-11-16 D-1 sau probe mảng: `translated_at` parse 360/360. `experiences` 360 mảng. `destinations` 113 mảng, 271 phần tử, 1 phần tử id và name null.
- 2026-11-17: architecture `EVIDENCE_REQUIRED`. A-1 đến A-10 ghi ở D-8. Chưa implement.
- 2026-11-17 D-9 đến D-11: U-1 đến U-3 và Copy Job đã ghi. P-1 chặn tạo lại `slv_enr_poi_info_multi_lang` vì còn 3 dòng. Gold writer version 2. U-4 còn mở vì partner có `house_number` và `street` rỗng.
- 2026-11-17 U-4: `house_number` hoặc `street` chỉ còn khoảng trắng sau trim thì bỏ cả nhóm `full_address`.
- 2026-11-17 D-11: Copy Job map cột theo tên hiện có trên gold.
- 2026-11-17: architecture vòng 2 PASS. A-11 đến A-15 ghi đè A-10. Không gọi gate lần 3 vì cap architecture là 2.
- 2026-11-17 D-11: Copy Job tạm dừng được. B5 dừng job, `enrgldpy`, `ALTER`, mở lại.
- 2026-11-17: review vòng 2 `FIX_REQUIRED`. GATE-010 và GATE-011 sửa sau cap review: không `RESTORE` khi đã có commit sau attempt; `_fence` trước mỗi ghi. B5 không mở Copy Job khi một bước lỗi. Không gọi review vòng 3.
- 2026-11-17: Người dùng chấp nhận bản sửa sau cap cho GATE-010, GATE-011 và GATE-008. Ba finding giữ `fixed`. Chuyển `waiting_runtime`, dừng ở R-0.
- 2026-11-17 R-0: Copy Job 15 phút một lần, mode merge. `slv_enr_poi_info_multi_lang` 3, `slv_enr_poi_destination` 0, gold và PostgreSQL 859. `COUNT(cost_vnd)` gold 3, PostgreSQL 3.
- 2026-11-17 B2: cell `enrbrzpy` lỗi `wm_transform_brz_enrichment_result đang bị giữ`. SELECT trả 0 dòng, nên chưa có khoá thật.
- 2026-11-17 B3: cell `enrbrzcfgpy` lỗi `NameError: name 'seed_registry' is not defined`. Hàm nằm ở cell `# Seed ctrl_cfg_schema_registry (v2) từ TABLE_CONFIGS`, sau cell `TABLE_CONFIGS = [`.
- 2026-11-17: cell seed partner PASS. `show_registry` trả 23 bảng `slv_pn_*`, tất cả `CDC`, `so_cot_tat=0`, `bang_active=1`.
- 2026-11-17 B3 lần 2 PASS: `Seed 31 cột / 2 bảng`, `enrbrzcfgpy 2 wm_transform_brz_enrichment_result`.
- 2026-11-17 B2: overwrite rồi `RESTORED` vì `Cannot change nullable column to non-nullable: poi_id`. D-12: bỏ qua lỗi này, không restore. Bảng đã về version trước rewrite.
- 2026-11-17: user gửi lại output `Seed 31 cột / 2 bảng` và `enrbrzcfgpy 2 ...`. Đó là cell B3 chạy lại, chưa phải `enrbrzpy`.
- 2026-11-17 B2 PASS: `NOT NULL giữ nullable` cho `poi_id`. `REWRITTEN slv_enr_poi_info_multi_lang v0 8 rows 3`. `REWRITTEN slv_enr_poi_destination v0 4 rows 0`.
- 2026-11-17 B4 dry run PASS, exec `457a8180-099e-470a-a9cb-e115bbf52ffd`. `SUCCESS`, 473/473 hợp lệ, `cast_null` 0, rejected 0, ignored 0. LANG 360, DESTINATION 113. `mapped_heads_missing` là đầu JSON của event_type kia, không chặn.
- 2026-11-17 B4 lần thật PASS, exec `00fde3e6-4aab-4fa5-a7e0-c56948d2d232`. INCREMENTAL SUCCESS, inserted 473, updated 0, cast_null 0. destination 113, multi_lang 360. src_version 3.
- 2026-11-17 B5 gold PASS. `REWRITTEN` `gld_srv_poi_multi_lang` v0 3, rows 859. `NOT NULL giữ nullable` cho `poi_id` và `lang`.
- 2026-11-17 B5 ALTER PASS. Người dùng xác nhận `apps.srv_poi_multi_lang.cost_vnd` đã thành `cost`. API chưa deploy. Copy Job vẫn dừng.
- 2026-11-17 API commit local `025e785` trên `D:\git\SunGrp_VSVN_API` nhánh `develop`. Chưa push. Entity giữ nguyên, không mang `ingestion_ts` từ repo data.
- 2026-11-17 API PASS. Người dùng xác nhận đã push và deploy. NB_00 chưa chạy. Copy Job vẫn dừng.
- 2026-11-17 D-13. Có dòng destination thì `ward`, `district`, `city` lấy cột mới, null hoặc trim rỗng thì lấy `old_*`. Partner chưa có dòng destination giữ nhánh entity. NB_00 chưa chạy.
- 2026-11-17 NB_00 PASS, exec `7d25219d-b6e7-453f-92a6-d12e2aa98b29`. `gld_srv_poi_multi_lang` SUCCESS ins 13 upd 350 version 5. `gld_srv_poi_info` SUCCESS ins 0 upd 113 version 13. Copy Job chưa mở lại.
- 2026-11-17 Gold count PASS. `gld_srv_poi_multi_lang` n=872, cost_n=363. PostgreSQL `25P02` current transaction is aborted. Chưa có count.
- 2026-11-17 PostgreSQL count PASS. `apps.srv_poi_multi_lang` n=872, cost_n=363. Khớp gold. `gates.runtime` = pass. `specialist_review` và `risk_gate` vẫn `fix_required`.
- 2026-11-17 D-14. Người dùng yêu cầu `ready_to_merge`. Hai gate review chuyển `pass` theo lệnh này. Không chạy Codex lại.
