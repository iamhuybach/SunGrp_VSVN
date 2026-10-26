# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| Q1 | Nguồn `gld_srv_poi_multi_lang.experience` | Dòng partner lấy usps, và khi usps null thì lấy experience của enr. Dòng nguồn khác lấy experience của enr. | Quyết định của người dùng, phương án 4 | 2026-10-26 |
| Q2 | Lần RUN gold khi landing rỗng | Chấp nhận lần RUN này. Gate rỗng là hành vi hiện có. | Quyết định của người dùng, Q2 phương án 1 | 2026-10-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- `slv_enr_poi_info_multi_lang.experience` chỉ thêm schema. Request cấm bịa loader. Q2 trong `model-design.md` không chặn.
- `usps` đã là cột registry `type: string` trên `slv_pn_business_service_i18ns` trong `NB_CREATE_DDL` và `NB_SETUP_INITIAL_DDL`. Không probe.
- Backlog: chưa thêm dòng `experience` vào `docs/context/mapping_gld_srv_poi_multi_lang.md` §1.2. Architect cho phép bỏ qua mapping doc và ghi backlog.

## Sai lệch so với kiến trúc

- Không lệch Q1 hay vị trí cột.
- `test_pl_cadence_patch_cell` đọc `notebooks/NB_00_ORCHES_SLV_TO_ENR.ipynb`. File `NB_00_ORCHES_SLV_TO_ENR_15P.ipynb` không còn sau commit cadence. Architecture yêu cầu test này pass.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | accepted-risk | Người dùng chấp nhận lần RUN `PARTIAL_FAILED`. `slv_enr_poi_info_multi_lang` rỗng và quality gate hiện có không ghi gold. Schema, `mlexppy` chạy lại `+[]`, và `mismatch` 0 trên không dòng đã ghi ở `evidence/results/experience_dev.txt`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-26, người dùng chọn phương án 4: Dòng partner lấy usps, và khi usps null thì lấy experience của enr. Dòng nguồn khác lấy experience của enr.

Q2 đã chốt, phương án 1. Nguyên văn: Chấp nhận lần RUN này. Gate rỗng là hành vi hiện có.

## Lịch sử quyết định

- 2026-10-26: `model-design.md` (`claude-opus-5-5`, effort medium) ghi Q1 mở ở `## Conflicts and questions`. Main không gọi Architect và không sửa notebook.
- 2026-10-26: Người dùng chốt Q1, phương án 4. Nguyên văn: Dòng partner lấy usps, và khi usps null thì lấy experience của enr. Dòng nguồn khác lấy experience của enr.
- 2026-10-26: Architecture PASS. Q1 thành `F.when(partner, F.coalesce(usps, experience)).otherwise(experience)`. Cột đứng sau `description`. `experience` vào `row_hash`, không `hash_exclude`.
- 2026-10-26: Backlog mapping §1.2. Dừng trước khi sửa notebook: `20261026-pl-name-cadence-suffix` còn uncommitted và `plcadpy` phải đã chạy trên DEV. `mlexppy` nối sau `plcadpy`.
- 2026-10-26: Cadence đã commit (`6783eeb`). `def _refresh_lock` trong `mlexppy` đặt sau comment `Dừng trước khi ghi`. Test cadence đọc `NB_00_ORCHES_SLV_TO_ENR.ipynb`.
- 2026-10-26: DEV một phần. R0, P1, R1 lần đầu, R2 đúng vị trí cột. R3 `ConfigError`: `TABLE_SPECS cần 18 fq duy nhất, có 21`. Phân loại `code`. `init_plan` sửa mốc 18 thành 21 cho khớp `TABLE_SPECS`. R4–R6 chưa chạy. Runtime chưa pass.
- 2026-10-26: R1 chạy lại `+[]`. R3 `PLAN`. R4 `PARTIAL_FAILED` vì `slv_enr_poi_info_multi_lang` rỗng. Phân loại `data`. R5 `mismatch` 0 trên không dòng. Không sửa code. Chờ Q2.
- 2026-10-26: Người dùng chốt Q2. Nguyên văn: Chấp nhận lần RUN này. Gate rỗng là hành vi hiện có. SPARK-001 là `accepted-risk`. Không sửa `required_inputs`. Runtime chưa pass.
