# Model design: 20261104-gld-srv-multi-lang-i18n-without-enr

## Scope

- Base task: `20261104-gld-srv-multi-lang-i18n-without-enr`. In `task-state.yaml` the status is `waiting_architecture` and `architecture` is `pending`. `scope.files` lists `NB_GLD_SRV_POI_MULTI_LANG.ipynb`, `mapping_gld_srv_poi_multi_lang.md`, `test_gld_srv_poi_contract.py`, `NB_ENR_POI_INFO.ipynb`, `NB_CREATE_DDL.ipynb`, `NB_SETUP_INITIAL_DDL.ipynb`, `gld_enr_poi_info_review.md`, `test_enr_poi_contract.py` and `test_initial_ddl_contract.py`.
- `proposal.md`: Not applicable. The task folder has no `proposal.md`, and the handoff says so ("No `proposal.md`"). This design cannot cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry` (Conflicts item 1).
- Ledger rows this design implements, from `decision.md` `## Quyết định hiện hành`:
  - D-I18N-ROW, D-I18N-COLS, D-I18N-KEY, D-KEEP and D-REF.
  - UD-SRC, UD-MEASURES, UD-LOCALE, UD-DELETED, UD-INPUT and UD-BLANK.
  - D-ML-SRC, only for "Tạo thêm 1 cột source_name ở bảng slv_enr_poi_info_multi_lang" and "Dòng chỉ có i18n vẫn lấy mọi locale và source_name là partner". D-ML-NOMATCH overrides its sentence "Bảng gld_enr_poi_info lấy source_name từ đây".
  - D-ML-WRITER: the change is DDL only, with no notebook writer. The external enrich job is out of scope.
  - D-ML-NOMATCH: `gld_enr_poi_info` still takes `slv_poi_entity_non_enrich.source_name`. This row is later than D-ML-SRC and D-ML-GATE and wins over both.
  - D-ML-PICK: recorded. It does not drive any rule here, because `NB_ENR_POI_INFO` does not read the new column.
  - D-ML-GATE ("Dùng source_name mới"): D-ML-NOMATCH and the handoff constraint override it. The `google` predicate stays on the entity value (Conflicts item 2).
- D-REF: this design does not change D-SRV-LANG, D-SRV-TEXT or D-REINIT of task `20261104-poi-review-src-and-partner-i18n`.
- Model changes:
  1. `gld_srv_poi_multi_lang` gets a second row population, P2: partner rows that have only i18n. Grain, gold columns, the P1 transform and the non-partner branch stay the same (D-KEEP; `request.md` out of scope; handoff "P1 of that gold table stays on the current transform").
  2. `slv_enr_poi_info_multi_lang` gets a new DDL column, `source_name`. No writer is added (D-ML-SRC, D-ML-WRITER).
  3. `gld_enr_poi_info` does not change. `source_name`, the `google` predicate and the `google_cols_not_google` block check all stay on `slv_poi_entity_non_enrich.source_name` (D-ML-NOMATCH).
- No new gold column (D-I18N-COLS; `request.md` out of scope).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | gold (serving) | `(poi_id, lang)`, unchanged (mapping §1.1; cell `id:srvmlbuild` `pk=("poi_id", "lang")`) | `NB_GLD_SRV_POI_MULTI_LANG` |
| `slv_enr_poi_info_multi_lang` | silver enrich (landing) | `(poi_id, lang)`, unchanged (mapping §1.1 MERGE grain; D-ML-PICK "1 poi_id có thể nhiều lang") | No repo writer. The external enrich job loads it, and that job is out of scope (D-ML-WRITER). This task changes only DDL: `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL` |
| `lh_vv_gold.enr.gld_enr_poi_info` | gold (enrich) | `poi_id` (`pk=("poi_id",)`), unchanged | `NB_ENR_POI_INFO`. No change to the model in this task (D-ML-NOMATCH) |
| `slv_poi_entity_non_enrich` (read only) | silver L2 | `poi_id` | not changed |
| `slv_pn_business_service_i18ns` (read only) | silver L1 partner | `(business_service_id, locale)`, as `request.md` cites from `CTRL_TABLES_CONTEXT.md` §5 | not changed |

Row populations of `gld_srv_poi_multi_lang`:

- P1, matched rows and non-partner rows. `slv_enr_poi_info_multi_lang` drives them and the current transform stays, including the `bio` / `usps` fallback (D-KEEP).
- P2, i18n-only partner rows. P2 has one row for each `slv_pn_business_service_i18ns` row whose derived `(poi_id, lang)` has no row in `slv_enr_poi_info_multi_lang` (D-I18N-ROW, UD-INPUT). Every `locale` produces a row, with no allow-list (UD-LOCALE; D-ML-SRC "Dòng chỉ có i18n vẫn lấy mọi locale").

## Keys

`gld_srv_poi_multi_lang`

- Primary key and MERGE key: `(poi_id, lang)`, unchanged. `quality_gate` in `NB_LIB_TRANSFORM_SLV_GLD` stops the run on a null key (mapping §1.1).
- P1 key: `poi_id` and `lang` are copied 1-1 from `slv_enr_poi_info_multi_lang` (mapping §1.2; D-KEEP).
- P2 key: `poi_id = uuid_md5(business_service_id, 'partner')`, `lang = locale` (D-I18N-KEY).
  - Formula source: `AGENTS.md` §7, partner `poi_id = uuid_format(md5(concat(id, 'partner')))` 8-4-4-4-12, where `id` is `slv_pn_business_service_i18ns.business_service_id`. The same formula appears in `docs/context/01_DATA_MODEL.md` §8, as `request.md` `## Current behavior` cites.
  - Cell `id:srvmlbuild` already computes this as `uuid_md5(F.col("business_service_id"), F.lit(PARTNER))` aliased `_pid`, with `locale` aliased `_loc`. `NB_ENR_POI_INFO` `_vi_i18n` uses the same function and the same argument order.
- P2 rows are unique among themselves: the source key `(business_service_id, locale)` is unique and the formula is deterministic.
- P1 and P2 do not overlap. P2 is an anti-match on `(poi_id, lang)` against `slv_enr_poi_info_multi_lang` (D-I18N-ROW "khớp theo poi_id partner và lang = locale"). P2 does not test the entity partner predicate (Conflicts item 4).
- Null or blank P2 keys: UD-BLANK says "Chốt theo kiến trúc", so the Architect decides. This design sets no rule (Conflicts item 5).
- Business key: the same as the primary key. There is no surrogate key.
- Logical foreign keys (not enforced):
  - `poi_id` → `slv_poi_entity_non_enrich.poi_id`. P1 uses a LEFT join, as today. P2 needs no entity row (UD-SRC, UD-INPUT).
  - For P2, `(poi_id, lang)` traces back to `slv_pn_business_service_i18ns(business_service_id, locale)` through the formula above.

`slv_enr_poi_info_multi_lang`

- `(poi_id, lang)`, unchanged. `source_name` is not a key column. D-ML-PICK says every `lang` row of one `poi_id` belongs to one source. No reader in this task depends on that.

`gld_enr_poi_info`

- `poi_id`, unchanged. The spine stays `slv_poi_entity_non_enrich` (`required_inputs=("entity",)`).

## Columns

Only affected columns are listed. `gld_srv_poi_multi_lang` types come from mapping §1.2.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_enr_poi_info_multi_lang` | `source_name` | MISSING (Conflicts item 3) | MISSING (Conflicts item 3) | No repo writer. The external enrich job will fill it. Rows that exist when the column is added have no value shown | D-ML-SRC "Tạo thêm 1 cột source_name ở bảng slv_enr_poi_info_multi_lang"; D-ML-WRITER "Chỉ cần thêm cột DDL" |
| `gld_srv_poi_multi_lang` | `poi_id` | string | NOT NULL (key; `quality_gate`) | P1: `slv_enr_poi_info_multi_lang.poi_id`. P2: `uuid_md5(slv_pn_business_service_i18ns.business_service_id, 'partner')` | P1: D-KEEP. P2: D-I18N-KEY; `AGENTS.md` §7 |
| `gld_srv_poi_multi_lang` | `lang` | string | NOT NULL (mapping §1.1) | P1: `slv_enr_poi_info_multi_lang.lang`. P2: `slv_pn_business_service_i18ns.locale` | P1: D-KEEP. P2: D-I18N-KEY, UD-LOCALE, D-ML-SRC "mọi locale" |
| `gld_srv_poi_multi_lang` | `source_name` | string | P1 not shown; P2 always `'partner'` | P1: `slv_poi_entity_non_enrich.source_name` by `poi_id`, unchanged. P2: literal `'partner'` | P1: D-KEEP and the handoff ("P1 … stays on the current transform"). P1 does not read the new silver column. P2: UD-SRC, D-ML-SRC "source_name là partner" |
| `gld_srv_poi_multi_lang` | `description` | string | not shown | P1: partner rows use `bio`, then enrich `description`; other rows use enrich `description`. P2: `bio` | P1: D-KEEP, mapping §1.2. P2: D-I18N-COLS, UD-INPUT, with no enrich fallback |
| `gld_srv_poi_multi_lang` | `experience` | string | not shown | P1: partner rows use `usps`, then enrich `experience`; other rows use enrich `experience`. P2: `usps` | P1: D-KEEP, mapping §1.2. P2: D-I18N-COLS, UD-INPUT, with no enrich fallback |
| `gld_srv_poi_multi_lang` | `time_to_spend` | string | P2 always null | P1: `slv_enr_poi_info_multi_lang.time_to_spend`. P2: null | P1: D-KEEP. P2: UD-MEASURES, UD-INPUT |
| `gld_srv_poi_multi_lang` | `best_time` | string | P2 always null | P1: `slv_enr_poi_info_multi_lang.best_time`. P2: null | P1: D-KEEP. P2: UD-MEASURES, UD-INPUT |
| `gld_srv_poi_multi_lang` | `cost_vnd` | string | P2 always null | P1: `slv_enr_poi_info_multi_lang.cost_vnd`. P2: null | P1: D-KEEP. P2: UD-MEASURES, UD-INPUT |

The following are not changed, and the table above omits them:

- `gld_enr_poi_info.source_name` stays `F.col("e.source_name")` from `slv_poi_entity_non_enrich` (D-ML-NOMATCH).
- `source = lower(trim(e.source_name))`, the `google` gating of `rating`, `user_rating_count`, `price_level` and `review_json`, and the `google_cols_not_google` block check all stay on that same entity value (handoff constraint).
- `REQUIRED_COLS["multi_lang"]` stays `("poi_id",)`, and `_present` still reads only `poi_id`.
- `ML_COLS` in `id:srvmlbuild` does not add `source_name`.
- `created_at` and `updated_at` are system fields and do not change.

## Lineage

`gld_srv_poi_multi_lang`

- Bronze: none.
- Silver: all three inputs are already in `SPEC.inputs`, and their three ctrl edges already exist on `PL_VV_TRANS_SLV_TO_GLD_30M` (mapping §1.1).
  - `slv_enr_poi_info_multi_lang` (`multi_lang`): drives P1 and is the anti-match set for P2. It stays in `required_inputs`. Its `source_name` is not read.
  - `slv_poi_entity_non_enrich` (`entity`): gives P1 its `source_name` and the partner predicate, as today. P2 reads nothing from it. It stays in `required_inputs`.
  - `slv_pn_business_service_i18ns` (`i18n`): gives P1 partner rows `bio` and `usps`, and drives P2. It stays optional.
  - All three keep `live_only=False`. No `deleted` filter is added (UD-DELETED "Giữ như hiện tại").
- Gold: none.

`slv_enr_poi_info_multi_lang`

- DDL column only. The external enrich job writes it, and that job is out of scope (D-ML-WRITER). This task adds no bronze, silver or gold read for it.

`gld_enr_poi_info`

- No change. Silver reads stay as `SPEC.inputs`, and `slv_enr_poi_info_multi_lang` is still read only for `poi_id` to compute `is_enriched_multi_lang`. That matches `gld_enr_poi_info_review.md` "chỉ đọc `poi_id` để tính cờ. Không chép nội dung enrich sang gold". Gold reads: none.

Gold never reads gold.

## Conflicts and questions

1. There is no `proposal.md`, so no `## Dòng thay đổi` or `## ctrl_cfg_schema_registry` can be cited. This design proposes no `ctrl_cfg_schema_registry` row. Should the new `slv_enr_poi_info_multi_lang.source_name` column have a registry entry? The files I read show none.
2. D-ML-GATE ("Dùng source_name mới") is still in the ledger, but D-ML-NOMATCH (later) and the handoff override it. Both keep the `google` predicate on `slv_poi_entity_non_enrich.source_name`. The first sentence of D-ML-SRC ("Bảng gld_enr_poi_info lấy source_name từ đây") is also overridden. Please edit those ledger rows in place so they agree with D-ML-NOMATCH (`decision.md` "Sửa dòng tại chỗ khi quyết định đổi").
3. The type and nullability of the new `slv_enr_poi_info_multi_lang.source_name` are not in any file I read. Comparable columns are `string` (`slv_poi_entity_non_enrich.source_name`, mapping §1.2) and `STRING` (`gld_enr_poi_info.source_name`, review doc). Please confirm `STRING`, nullable, before the column goes into `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL`. Also confirm whether the patch in `NB_CREATE_DDL` leaves existing rows null.
4. Please confirm the P2 anti-match. D-I18N-ROW matches on partner `poi_id` and `lang = locale`. UD-INPUT says "không có poi_id khớp" and does not mention `lang`. This design anti-matches on `(poi_id, lang)` and skips the entity partner predicate, so a P2 key can never collide with a P1 key.
5. Null or blank P2 keys are still open. UD-BLANK says "Chốt theo kiến trúc", and no rule is recorded for a null or blank `business_service_id` or `locale`. A null key would make `quality_gate` stop the run.
6. Should P2 require `bio` or `usps` to be non-null? UD-INPUT says "có data (của bio và usps)". D-I18N-ROW sets no condition, and this design sets none.
7. UD-MEASURES is not grammatical as written. This design reads it, together with UD-INPUT, as "P2 `time_to_spend`, `best_time` and `cost_vnd` are null". Please confirm.
8. The files I read do not show source types or nullability for `slv_pn_business_service_i18ns.business_service_id`, `locale`, `bio` or `usps`. This design assumes none.
9. Some docs will be stale:
   - Mapping §1.1 says "`slv_enr_poi_info_multi_lang` không có `source_name`". That becomes false once the DDL column exists. The gold node still does not read the column. The mapping file is in scope, so this line can be corrected there.
   - `docs/context/03_OPERATOR_GUIDE.md` §2.3 and markdown cell `id:srvmlmd` describe only P1. `03_OPERATOR_GUIDE.md` is out of scope (`request.md`).
10. The `gld_enr_poi_info_review.md` source list includes `slv_3p_poi_opening_hours`, but `NB_ENR_POI_INFO` `SPEC.inputs` does not. This task does not touch that difference. It is reported only.
