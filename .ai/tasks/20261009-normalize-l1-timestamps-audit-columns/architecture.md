RESULT: PASS

# Architecture — Normalize silver L1 timestamps and audit columns

Task: `20261009-normalize-l1-timestamps-audit-columns`
Architect: Claude Opus 5.5 (Cursor subagent, per `model_policy_exception` approved 2026-10-09).
Evidence gate: `pass`. Locked user decisions in `decision.md` (2026-10-10) and the nine locked decisions in the architect prompt are treated as fixed inputs. Nothing in this document reopens them.

## Context and scope

Silver L1 currently stores partner business instants as raw JSON `bigint` epochs (seconds or millis, depending on the table) or as Spark `TIMESTAMP` (ISO columns, `last_verify_at`), and 3P business instants as Spark `TIMESTAMP`. The only L1 write clock is `_ingested_at` (last MERGE write). This change:

1. Stores every L1 business instant and both L1 audit columns as a UTC string in exactly `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'` (acceptance example `2026-10-09T16:20:01.123Z`).
2. Renames partner business `created_at` / `updated_at` to `src_created_at` / `src_updated_at` (`json_path` unchanged).
3. Adds L1 audit `created_at` (first INSERT) and `updated_at` (every INSERT/UPDATE) to all partner (23) and 3P L1 tables, and removes `_ingested_at`.
4. Backfills existing L1 rows in place, without DROP.

In-scope code: `NB_LIB_EXTRACT_RAWDATA`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_CREATE_DDL` (registry seed only), one new manual notebook `NB_SETUP_L1_TS_AUDIT`, and the context files listed in the implementation plan.

## Non-goals

- No change to MERGE keys, table grain, partner event order (`_cdc_ts_ms`, `_cdc_lsn`, `_raw_ingested_at`, `_is_delete`), the partner stale filter on `ctrl_cdc_state`, or the 3P `(_crawled_at, _event_id)` MERGE guard.
- No change to `ctrl_*` table schemas, watermark semantics, lock semantics, or `ctrl_cdc_state` / `ctrl_cdc_reject` content. `raw_ingested_at` / `_raw_ingested_at` (event-order cursor) are not `_ingested_at` and are untouched.
- No change to L2/gold `created_at`, `updated_at`, `deleted_at`, or `row_hash` semantics.
- No new bronze keys (E4 extras such as `business_services.deleted_at`, `facility_type`, `partners.edit_consent`, `product_posts.category` … stay unmapped).
- No change to `slv_3p_poi_review.time` or `review_id`.
- No new epoch unit. `EPOCH_US_TS` stays available but unused. The new rule `ISO_UTC_TS` is a format rule for strings that are already instants, not an epoch unit.
- 3P technical clocks `_crawled_at`, `_first_seen_at`, `_last_seen_at` keep type `TIMESTAMP` (see Alternatives A6). They are neither business nor audit timestamps.
- Partner MERGE update-storm (context M5, unconditional matched update) is not fixed here.

## Invariants

- **I1 Format.** Every non-NULL value of an L1 business-instant column or an audit column fully matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$` and denotes a UTC instant.
- **I2 Instant preservation.** For each converted value, `unix_millis(CAST(new AS TIMESTAMP))` equals `old_seconds * 1000` (`EPOCH_S_TS`), `old_millis` (`EPOCH_MS_TS`), or `floor(old_instant_micros / 1000)` (ISO / existing `TIMESTAMP`). Sub-millisecond digits are truncated, never rounded, so the displayed second never changes.
- **I3 Session-timezone independence.** Output strings do not depend on `spark.sql.session.timeZone`. Enforced by expression construction and a fail-closed self-check (see Selected design D3).
- **I4 Zero sentinel.** A numeric epoch raw value `0` becomes NULL and is not counted as a cast-null. An ISO string `1970-01-01T00:00:00Z` is a real instant and becomes `1970-01-01T00:00:00.000Z`.
- **I5 Dates stay dates.** `DATE_DAYS` targets stay `date`. 3P bronze `ingested_date` is not an L1 column and is not touched. No time of day is ever synthesized; a date-only string under `ISO_UTC_TS` becomes NULL and is flagged as cast-null.
- **I6 Audit semantics.** `created_at` is written only by the INSERT branch (and once by the backfill); no UPDATE branch references it. `updated_at` is written by every INSERT and every executed UPDATE branch (including the partner soft-delete branch) with the MERGE clock of that statement. Both are non-NULL on every L1 row after backfill. `created_at <= updated_at` lexicographically (equal on insert).
- **I7 Audit independence.** Audit values come only from the MERGE clock (or, for backfill only, from the old `_ingested_at`). Never from a source business timestamp. 3P `created_at` is never derived from `_first_seen_at`.
- **I8 Unchanged ordering/state.** MERGE match keys, the partner stale filter, the 3P guard predicate, `ctrl_cdc_state` rows, and watermark values are byte-for-byte the same logic as today. Watermarks never move backward. Each flow writes only its own `src_tbl` registry rows (`replaceWhere`) and its own L1 tables.
- **I9 Key stability.** No business key or derived key changes value. `review_id` keeps hashing the raw `time` string.
- **I10 No L1 `_ingested_at`.** After cut-over no L1 table, registry row, MERGE statement, or technical-column tuple contains `_ingested_at`.
- **I11 Hash isolation.** L1 audit columns are never inputs of an L2/gold `row_hash`. Future L2 nodes must select L1 business columns explicitly and, if they need an L1 audit value, alias it (for example `l1_updated_at`) so it cannot collide with L2 technical `created_at` / `updated_at`.

## State ownership, grain, and keys

| State | Owner (writer) | Change |
|---|---|---|
| `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` rows `src_tbl = partner_raw_data` | `NB_CREATE_DDL` partner seed cell (`replaceWhere`) | Rename 2 columns per affected table, set `data_type`/`convert_rule` per column class |
| Same table, rows `src_tbl = brz_3rd_crawler_poi_stream` | `NB_CREATE_DDL` 3P seed cell (`replaceWhere`) | `source_created_at`, `published_at` → `string` + `ISO_UTC_TS` |
| `slv_pn_*` (23) | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` (steady state); `NB_SETUP_L1_TS_AUDIT` (one-shot backfill, pipelines paused) | Schema + values |
| `slv_3p_poi_*` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`; `NB_SETUP_L1_TS_AUDIT` | Schema + values |
| `ctrl_mng_watermark`, `ctrl_cdc_state`, `ctrl_log_*` | Existing writers | None |

Grain and keys: unchanged for every table. Registry row count per source unchanged (partner stays 301; renames do not add rows). Technical columns are not registry rows.

## Ordering and transaction boundaries

Steady state, per table attempt (unchanged structure; audit columns ride inside the existing commit):

1. `ensure_target(spec)` — type mismatch → `ConfigError` before any write (fail-closed guard for un-backfilled tables).
2. Build events, stats, cast-null check (`CastNullError` before MERGE under `FAIL`).
3. Compute `merge_clock = utc_ts_text(utc_now())` once for this attempt.
4. One Delta MERGE commit writes business values, `deleted`/`_source_db` or 3P technical columns, and audit columns atomically.
5. `ctrl_cdc_state` rows, then table log (existing order).
6. Watermark advances only after all tables succeed and the run still owns the lock (existing).

Cut-over ordering (runbook detail is Main's Vietnamese `runtime-runbook.md`):

1. Pause `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` and the 3P runner. Confirm both source watermark rows are not `RUNNING` and the last `ctrl_log_run` of each source is terminal.
2. Record pre-change Delta versions of `ctrl_cfg_schema_registry` and every existing L1 table (`DESCRIBE HISTORY … LIMIT 1`).
3. Deploy `NB_LIB_EXTRACT_RAWDATA` first, then `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, `NB_CREATE_DDL`, `NB_SETUP_L1_TS_AUDIT`.
4. Run only the two registry seed cells of `NB_CREATE_DDL` (partner, then 3P). Do not run DDL/pipeline-config/watermark seed cells. One commit per source.
5. Run `NB_SETUP_L1_TS_AUDIT` with `p_apply = false` (plan + parity only). Stop on any parity failure.
6. Run `NB_SETUP_L1_TS_AUDIT` with `p_apply = true`. One overwrite commit per table, sequential. Post-checks run for every table.
7. Run each extract notebook once with `dry_run = True`, then once for real (incremental). Run the audit-stability check (second MERGE does not change `created_at`).
8. Resume schedules. The next hourly `NB_00_ORCHES_SLV_TO_GLD` sees the L1 overwrite commits as data changes and recomputes.

Rationale for step 4 before 6: the backfill derives target types/rules from the new registry, and the new library rejects the old partner registry (business `created_at` collides with the new technical name), so new code cannot run against the old registry anyway.

## Idempotency, concurrency, and recovery

- **MERGE rerun.** Partner: re-read events already in `ctrl_cdc_state` are stale and never reach MERGE. If a crash happened after the MERGE commit but before state was written, the same events re-apply: business values are identical, `updated_at` moves to the new clock, `created_at` is untouched by construction. 3P: the guard re-applies equal `(_crawled_at, _event_id)` (`>=`), with the same effect. `FULL_RELOAD` re-applies everything: `updated_at` moves for all matched rows, `created_at` never moves. This matches the decided meaning of `updated_at` (time of the last MERGE write).
- **MERGE clock.** One Python literal per MERGE statement, so all rows of a statement share one value and the value does not depend on session time zone or on `current_timestamp()` evaluation. A retry (`process_with_retry`) computes a new clock; only the committed attempt's clock persists.
- **Backfill rerun.** Per table the backfill is a single atomic overwrite commit. Before building SQL it inspects the current schema; if the table already has the exact target schema (all target columns with target types, no `_ingested_at`) it is `SKIPPED` and only the post-check runs. Every column expression is idempotent on its own: a target time column that already exists as `string` is passed through; audit columns use `coalesce(existing_string_audit, fmt(_ingested_at), backfill_clock)`. The write is not wrapped in `with_retry`; a failed write is recovered by rerunning the notebook, which re-evaluates the schema first.
- **Concurrency.** Backfill requires paused extract pipelines (single writer per L1 table, same rule as `run_merge`). Concurrent L2 readers are snapshot-isolated. Tables are processed sequentially; L1 tables are small on F16 (largest E3 silver counts are hundreds of rows; bronze event counts do not apply because backfill reads silver only).
- **Wrong-order safety.** New code against an un-backfilled table whose timestamp column types differ fails in `ensure_target` with `ConfigError`, and the watermark does not advance. Old code against a backfilled table fails on the missing `_ingested_at` column. Both are fail-closed. A table whose only change is the audit columns (for example `slv_pn_product_attribute_value_translations`, `slv_3p_poi_address`) would be auto-extended by `ensure_target` (`ADD COLUMNS created_at, updated_at`) if new code ran before the backfill; the backfill `coalesce` handles that state correctly, but the runbook still requires the pause.

## Partial failures

| Failure point | State | Recovery |
|---|---|---|
| Registry seed fails for one source | Other source untouched (`replaceWhere`) | Rerun the cell; it is a full replace of that source |
| Backfill fails on table N | Tables < N converted (atomic each), N and later unchanged | Rerun `p_apply = true`; converted tables are `SKIPPED` + re-checked |
| Backfill commit succeeded, post-check fails | Table converted but suspect; pipelines still paused | Stop. Inspect; `RESTORE TABLE … TO VERSION AS OF <backfill_version - 1>`; fix; rerun |
| Extract run after cut-over fails on a table | Existing semantics: table `FAILED`, watermark held | Existing retry/rerun |
| Self-check fails at notebook start | Nothing written | `ConfigError`; fix session/runtime; rerun |

## Alternatives and trade-offs

**A1. Storage type of business and audit instants (material).**

| | Spark `TIMESTAMP` | UTC string `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'` (selected) |
|---|---|---|
| Acceptance form `2026-10-09T16:20:01.123Z` | Not stored; rendering depends on session time zone and client (SQL endpoint `datetime2`, PG sync, notebooks render differently, no `Z`) | Stored literally; identical in every reader |
| Precision | Microseconds kept | Milliseconds; sub-ms truncated irreversibly (old micros recoverable only by `RESTORE`) |
| Comparison / ordering | Native | Lexicographic order equals chronological order for this fixed-width UTC format (years 0000–9999) |
| Arithmetic | Native | Needs `CAST(x AS TIMESTAMP)` (the `Z` suffix makes the cast session-independent) |
| Invalid values | Impossible | Possible in principle; prevented by construction, self-check, and post-check regex |
| Storage | 8 bytes | 24 bytes per value; negligible at L1 volume |

Selected: string, because the acceptance criterion is the literal string form, consumers must not depend on session or client time zone, and L1 is extract-only (no arithmetic needed there).

**A2. Backfill mechanism.** (a) `ALTER COLUMN` type change + rename: Delta cannot change `bigint`/`timestamp` to `string` in place, and rename/drop needs column mapping mode `name` (protocol upgrade, irreversible for older readers) — rejected. (b) `FULL_RELOAD` from bronze: full bronze scan on F16, depends on bronze completeness, and would set `created_at` to the reload time for every row — rejected. (c) In-place overwrite of each L1 table from its own current snapshot with `overwriteSchema`, one atomic commit, same table id, `RESTORE`-able, deterministic from stored values — **selected**. Equivalence to a fresh load holds because stored `bigint` values are the raw JSON integers and stored `TIMESTAMP` values carry the same micro truncation the cast applied.

**A3. MERGE clock.** `current_timestamp()` inside SQL plus formatting depends on the session time-zone rendering path; a Python `utc_now()` literal is session-independent, single-valued per statement, and unit-testable — **selected**.

**A4. `created_at` for existing rows.** (a) Delta history scan for the first version containing each key: unreliable after VACUUM and expensive. (b) NULL: violates I6. (c) The old `_ingested_at` (last silver write; never earlier than the true first insert), fallback to the backfill clock when NULL — **selected**. This is an approximation for pre-existing rows only; Main records it as an assumption in `decision.md`.

**A5. Zero sentinel.** Locked: numeric `0` → NULL before epoch conversion.

**A6. 3P technical clocks.** Converting `_crawled_at` / `_first_seen_at` / `_last_seen_at` to ms strings would collapse distinct nanosecond `crawled_at` values into ties and move the tie-break to `_event_id`, which changes the MERGE order that decision 6 keeps. They also feed `MIN_TS` coalesce and `unix_millis`. Kept as `TIMESTAMP`. 3P `crawled_at` has no L1 business column; the "format only" rule applies to `source_created_at` and `published_at`, the 3P business instants that exist.

## Selected design

### D1. Convert rules and target types

| Column class | `data_type` | `convert_rule` | Expression (raw string column `r`) |
|---|---|---|---|
| Epoch seconds instant | `string` | `EPOCH_S_TS` | `CASE WHEN CAST(r AS BIGINT) = 0 THEN NULL ELSE fmt(timestamp_seconds(CAST(r AS BIGINT))) END` |
| Epoch millis instant | `string` | `EPOCH_MS_TS` | same with `timestamp_millis` |
| Epoch micros instant (unused) | `string` | `EPOCH_US_TS` | same with `timestamp_micros` |
| ISO instant (already an instant) | `string` | `ISO_UTC_TS` (new) | `CASE WHEN r RLIKE ISO_INSTANT_RE THEN fmt(CAST(r AS TIMESTAMP)) END` |
| Day count | `date` | `DATE_DAYS` | unchanged |
| Source `deleted_at`, `review.time` | `string` | `NONE` | unchanged |

`CAST` is `CAST_FN` (`CAST` / `TRY_CAST` by ANSI mode), as today.

`fmt(ts)` is the library function `utc_ts_sql(ts)`:

```sql
concat(date_format(to_utc_timestamp(<ts>, current_timezone()), 'yyyy-MM-dd'), 'T',
       date_format(to_utc_timestamp(<ts>, current_timezone()), 'HH:mm:ss.SSS'), 'Z')
```

The literal letters `T` and `Z` are concatenated rather than quoted inside the pattern, so the SQL needs no nested quote escaping and is safe under any `doubleQuotedIdentifiers` setting. `to_utc_timestamp(ts, current_timezone())` moves the rendered wall clock to UTC for any fixed-offset session time zone; I3 is enforced by the self-check (D3), not assumed. `SSS` formatting truncates.

`ISO_INSTANT_RE` (SQL regex, written without backslashes and without braces so it survives Python `.format` and SQL literal parsing):

```text
^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]([.][0-9]+)?(Z|[+-][0-9][0-9]:[0-9][0-9])$
```

The pattern requires a `T` time part and an explicit zone, so date-only and zoneless strings become NULL (flagged cast-null) instead of being interpreted in the session time zone. A string `CAST` with a `Z` or offset is session-independent; 9 fractional digits truncate to micros (proven by the 04/10 3P cast note in the `TABLE_CONFIGS_3P` header and E2).

Library validation in `build_table_specs`: `EPOCH_*` and `ISO_UTC_TS` require `data_type = string`; `DATE_DAYS` requires `date`. Any other combination → `ConfigError` before any write. This retires the old `EPOCH_S_TS → timestamp` form (only `last_verify_at` used it).

### D2. Zero sentinel and cast-null accounting

Library function `unset_raw_sql(c: ColumnSpec) -> str` returns `coalesce(CAST(`<raw>` AS BIGINT) = 0, false)` for `EPOCH_*` rules and `false` otherwise. Both extract notebooks AND `NOT unset_raw_sql(c)` into their `_cn__<col>` flag, so sentinel-to-NULL is not a cast-null and does not trigger `CastNullError`. Both notebooks also aggregate `_unset__<col>` counts in the existing single stats job and `log(...)` them at INFO when non-zero (no `ctrl_*` schema change).

### D3. Format self-check (fail-closed, I1–I5)

Library constant `UTC_SELF_CHECK` and function `assert_utc_format()`. The function runs one literal-only `spark.sql` SELECT (no table I/O) using `convert_sql` and raises `ConfigError` on any mismatch, logging `current_timezone()` on success. Each extract notebook and `NB_SETUP_L1_TS_AUDIT` call it after parameter validation and before reading any table. The library does not call it at `%run` time (library convention: no I/O at `%run`). Cases:

| Input | Rule | Expected |
|---|---|---|
| `1791562801123` | `EPOCH_MS_TS` | `2026-10-09T16:20:01.123Z` |
| `1791562801` | `EPOCH_S_TS` | `2026-10-09T16:20:01.000Z` |
| `0` | `EPOCH_S_TS` | NULL |
| `2026-10-08T08:25:03.999999999Z` | `ISO_UTC_TS` | `2026-10-08T08:25:03.999Z` |
| `2026-10-08T08:25:03.721627Z` | `ISO_UTC_TS` | `2026-10-08T08:25:03.721Z` |
| `2026-10-09T23:20:01.123+07:00` | `ISO_UTC_TS` | `2026-10-09T16:20:01.123Z` |
| `1970-01-01T00:00:00Z` | `ISO_UTC_TS` | `1970-01-01T00:00:00.000Z` |
| `2026-10-08` | `ISO_UTC_TS` | NULL |

The Python twin `utc_ts_text(datetime(2026, 10, 9, 16, 20, 1, 123999))` must return `2026-10-09T16:20:01.123Z` (truncation); this is a pure-Python check Main can add to local verification.

### D4. Technical column tuples (library §1)

```python
UTC_TS_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"            # tài liệu; SQL dựng bằng utc_ts_sql
UTC_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")
AUDIT_COLUMNS = (("created_at", "string"), ("updated_at", "string"))
TECH_COLUMNS = (("deleted", "boolean"), ("_source_db", "string")) + AUDIT_COLUMNS
SNAPSHOT_TECH_COLUMNS = (("_crawled_at", "timestamp"), ("_event_id", "string"),
                         ("_first_seen_at", "timestamp"), ("_last_seen_at", "timestamp")) + AUDIT_COLUMNS
TIME_RULES = ("EPOCH_S_TS", "EPOCH_MS_TS", "EPOCH_US_TS", "ISO_UTC_TS")
```

`CONVERT_RULES` keeps keys `EPOCH_S_TS`, `EPOCH_MS_TS`, `EPOCH_US_TS` and adds `ISO_UTC_TS`, all with value `None` (built by `time_rule_sql(col, rule)`, same pattern as `DECIMAL_BASE64`). `convert_sql` dispatches `TIME_RULES` to `time_rule_sql`. The existing technical-name collision check in `build_table_specs` now rejects any business column named `created_at` / `updated_at`, which is why the partner rename is mandatory.

`utc_ts_text(dt) -> str` (library §2): `dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"`; the caller asserts `UTC_TS_RE.fullmatch` before embedding it as a SQL literal.

### D5. Partner MERGE (`build_merge_sql(spec, target, view, merge_clock)`)

`merge_into_target` computes `merge_clock = utc_ts_text(utc_now())`, validates it, and passes it in. `c = '<merge_clock>'` below.

```sql
MERGE INTO <target> AS t
USING <view> AS s
ON <key equality, unchanged>
WHEN MATCHED AND s.`_cdc_op` = 'd' THEN UPDATE SET
        t.`deleted` = true,
        t.`updated_at` = c
WHEN MATCHED THEN UPDATE SET
        <business non-key columns, TOAST CASE unchanged>,
        t.`deleted` = false,
        t.`_source_db` = s.`_src_db`,
        t.`updated_at` = c
WHEN NOT MATCHED AND s.`_cdc_op` <> 'd' THEN INSERT
        (<business columns>, `deleted`, `_source_db`, `created_at`, `updated_at`)
        VALUES (<s.business>, false, s.`_src_db`, c, c)
```

Technical INSERT columns/values are built from a name → expression dict iterated in `TECH_COLUMNS` order, with an assertion that the dict keys equal the tuple names (removes the current positional coupling). No branch sets `created_at` except INSERT.

### D6. 3P MERGE (`build_merge_sql(spec, target, view, merge_clock)`)

Guard predicate unchanged byte-for-byte. UPDATE SET: business columns, `_crawled_at`, `_event_id`, `_first_seen_at = least(...)`, `_last_seen_at = greatest(...)`, `t.updated_at = c` (replaces `_ingested_at`). INSERT: business columns, `s._crawled_at`, `s._event_id`, `s._first_seen_at`, `s._last_seen_at`, `c`, `c`, built from a dict over `SNAPSHOT_TECH_COLUMNS` as in D5. When the guard is false, no column (including `updated_at`) changes.

### D7. Registry seed (`NB_CREATE_DDL`)

Helpers in the partner config cell: `_epoch_s(path)` → `{"path": path, "type": "string", "rule": "EPOCH_S_TS"}`, `_epoch_ms(path)`, `_iso_ts(path)` → `ISO_UTC_TS`. `PSEUDO_TYPES["epoch_seconds_timestamp"]` becomes `("string", "EPOCH_S_TS")` (or `last_verify_at` uses `_epoch_s`; the pseudo type then has no user). `KNOWN_RULES` adds `ISO_UTC_TS`. `validate_rows` adds: time rules require `string`; no partner column named `created_at` / `updated_at` / `_ingested_at`. The registry `convert_rule` column comment lists `ISO_UTC_TS` (affects new creates only; no ALTER needed).

Partner column classes (renamed keys keep their dict position, so `column_order` is unchanged; `json_path` stays `created_at` / `updated_at`):

| Target table | `EPOCH_MS_TS` | `EPOCH_S_TS` | `ISO_UTC_TS` | Unchanged |
|---|---|---|---|---|
| `slv_pn_products` | | `src_created_at`, `src_updated_at` | | `deleted_at` string |
| `slv_pn_product_translations` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_product_attributes` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_product_attribute_translations` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_product_attribute_values` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_product_attribute_value_translations` | | | | no business instant; audit only |
| `slv_pn_product_variants` | | `src_created_at`, `src_updated_at` | | `deleted_at` string |
| `slv_pn_product_variant_translations` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_product_business_service_relation` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_product_posts` | | `validity_from`, `validity_to`, `src_created_at`, `src_updated_at` | | `deleted_at` string |
| `slv_pn_product_post_translations` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_partners` | | `src_created_at`, `last_updated_at` | | |
| `slv_pn_business_services` | | `src_created_at`, `last_updated_at`, `last_in_activated_at`, `last_verify_at` | | |
| `slv_pn_business_locations` | | `src_created_at`, `last_updated_at` | | |
| `slv_pn_hotel_room_types` | | `src_created_at`, `src_updated_at` | | `deleted_at` string |
| `slv_pn_hotel_rate_plans` | | `valid_from`, `valid_to`, `src_created_at`, `src_updated_at` | | `deleted_at` string |
| `slv_pn_business_service_i18ns` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_business_service_poi_link` | | `src_created_at`, `src_updated_at` | | |
| `slv_pn_orders` | `expire_at`, `src_created_at`, `src_updated_at` | | | |
| `slv_pn_order_refs` | `src_created_at`, `src_updated_at` | | | |
| `slv_pn_order_item_tickets` | `src_created_at`, `src_updated_at` | | `usage_date`, `valid_from`, `valid_to` | |
| `slv_pn_order_item_hotels` | `src_created_at`, `src_updated_at` | | `check_in_date`, `checkout_date` | |
| `slv_pn_order_item_flights` | `src_created_at`, `src_updated_at` | | `departure_time`, `arrival_time` | |

All cells under the three rule columns have `data_type = string`. 3P (`TABLE_CONFIGS_3P`): `slv_3p_poi.source_created_at` → `{"path": "created_at", "type": "string", "rule": "ISO_UTC_TS"}`; `slv_3p_poi_review.published_at` → `{"path": "time", "type": "string", "rule": "ISO_UTC_TS"}`; `time` stays `string`/`NONE`; `review_id` unchanged. No other 3P registry column is an instant (`rating_count`, `file_size_bytes` are counts).

### D8. Backfill notebook `NB_SETUP_L1_TS_AUDIT`

Parameters: `p_apply` (default `"false"`), `p_sources` (default both source tables), `p_tables` (CSV, empty = all). Calls `assert_utc_format()` first. Computes one `backfill_clock = utc_ts_text(utc_now())`.

Specs: reads `ctrl_mng_pipeline_config` **without** the `is_active` filter (so disabled-but-existing tables such as `slv_3p_poi_policy` are still migrated) plus the new registry, and builds specs with `build_table_specs(..., allowed_modes=None)`. Tables that do not exist (`slv_pn_business_locations`, `slv_pn_product_post_translations`) → `MISSING`; the extract notebook will create them with the new DDL.

Per table, from the current schema `old` (name → type):

1. If `old` already equals the target (every spec column and every tech column present with target type, and `_ingested_at` absent) → `SKIPPED`, go to post-check.
2. Build the SELECT list in target order (spec columns by `column_order`, then the tech tuple), then any extra old columns not in the target, not `_ingested_at`, and not consumed by the rename, carried through unchanged at the end:
   - Time-rule column `n`: source column `o = n` if `n` in `old`; else for partner `src_created_at` → `created_at`, `src_updated_at` → `updated_at` when the old one is not `string`; else none.
     - `old[o] = string` → `` `o` `` (already converted).
     - `old[o] in (bigint, int)` and rule `EPOCH_*` → `CASE WHEN o = 0 THEN NULL ELSE fmt(<fn>(o)) END`.
     - `old[o] = timestamp` → `fmt(o)`.
     - Column absent → `CAST(NULL AS STRING)`.
     - Anything else (for example `bigint` under `ISO_UTC_TS`) → `ConfigError`, table not written.
   - Non-time spec column: pass-through; type must already equal target, else `ConfigError`.
   - `created_at` / `updated_at` audit: `coalesce(<old audit col if old type is string>, fmt(_ingested_at) if _ingested_at exists, '<backfill_clock>')`. A partner `created_at` of type `bigint` is never read as audit.
   - Other tech columns (`deleted`, `_source_db`, `_crawled_at`, `_event_id`, `_first_seen_at`, `_last_seen_at`): pass-through.
3. Parity pre-check on the SELECT (one aggregation): for each time column, `count(old non-NULL and old <> 0)` must equal `count(new non-NULL)`; report `count(old = 0)`; row count; key uniqueness. Any mismatch → `FAILED`, no write.
4. If `p_apply`: `df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").option("userMetadata", "L1_TS_AUDIT_BACKFILL").saveAsTable(fq)`. No `with_retry`.
5. Post-check (always, including `SKIPPED`): find the commit with `userMetadata = 'L1_TS_AUDIT_BACKFILL'` (`v_b`) and compare `VERSION AS OF v_b` against `VERSION AS OF v_b - 1` joined on keys: equal row counts and key sets; I1 regex on every time and audit column; I2 instant equality (`unix_millis(CAST(new AS TIMESTAMP))` versus old seconds × 1000, old millis, or `unix_millis(old_ts)`) on 100% of non-zero/non-NULL rows; `created_at` / `updated_at` non-NULL count equals row count; `_ingested_at` absent; table properties `optimizeWrite` / `autoCompact` still set.
6. Exit with `notebookutils.notebook.exit(json.dumps({...}))`: `status`, `apply`, `backfill_clock`, and `tables: [{trg_tbl, action: CONVERTED|SKIPPED|MISSING|FAILED, v_before, v_after, rows, zero_sentinels, checks, error}]`.

Comments and docstrings in this notebook are Vietnamese (repository language policy).

## Observability

- Start of every extract run and of the backfill: self-check PASS with `current_timezone()` in the log; FAIL is a `ConfigError` before reads.
- Per table: existing `cast_null_detail`; new INFO log of `_unset__<col>` sentinel counts.
- Backfill: printed plan per table (old → new type per column), parity counts, `v_before` / `v_after`, post-check results, stable JSON exit payload.
- Runbook queries Main writes in Vietnamese: regex conformance per column, NULL audit count, `created_at` stability via time travel (`VERSION AS OF` the backfill commit versus after two extract runs, join on keys, `created_at` differences = 0), `updated_at >= created_at`, and `DESCRIBE HISTORY` showing exactly one backfill commit per table.
- L2 impact signal: the first `NB_00_ORCHES_SLV_TO_GLD` run reports `DATA_CHANGED` on L1 edges; gold `updated_at` may change once on rows whose business timestamps changed format, producing a one-time PostgreSQL sync burst. Expected, not a regression.

## Security and data handling

No secrets, tokens, or personal data in code or artifacts. The sanitized 3P sample in context contains only keys, JSON types, shapes, and the non-personal instants already in `evidence/3p-sample-shapes.md`. Backfill outputs counts and min/max only.

## Rollout, rollback, and forward recovery

Rollout: see "Ordering and transaction boundaries".

Rollback without DROP (Delta files must still exist: do not `VACUUM` L1 tables or the registry until the user accepts the runtime result):

- **Before schedules resume** (after backfill, before step 8): pause holds. For each converted table `RESTORE TABLE <fq> TO VERSION AS OF <v_b - 1>`; restore the registry (`RESTORE TABLE … TO VERSION AS OF <pre-seed version>`, or reseed one source from the previous git version of its cell, which touches only that `src_tbl`); redeploy previous notebooks (library first). No data loss because no new MERGE happened.
- **After schedules resumed:** `RESTORE` alone would discard MERGEs applied after cut-over while `ctrl_cdc_state` and watermarks already moved past them, leaving silver behind with state claiming the events were applied. Watermarks must not be rewound. Therefore: pause → `RESTORE` tables and registry → redeploy previous code → run each affected extract once in `FULL_RELOAD` (`allow_full_scan = True`), which ignores state and re-applies the latest events (partner order and the 3P guard keep it monotonic) → resume. Under old code, `_ingested_at` is set by that reload.
- **Forward recovery (preferred for conversion bugs):** fix code, `RESTORE` only the affected table to `v_b - 1`, rerun the backfill for that table (`p_tables`). Millisecond truncation of ISO values is irreversible except through `RESTORE`.

## Implementation plan

Order matters: library, then notebooks, then registry seed, then backfill notebook, then context.

1. `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`
   - §1: `UTC_TS_FORMAT`, `UTC_TS_RE`, `AUDIT_COLUMNS`, new `TECH_COLUMNS`, new `SNAPSHOT_TECH_COLUMNS`, `TIME_RULES` (D4). Update the table-of-contents and change-log markdown.
   - §2: `utc_ts_text(dt)`.
   - §6: `ISO_INSTANT_RE`, `EPOCH_FN = {"EPOCH_S_TS": "timestamp_seconds", "EPOCH_MS_TS": "timestamp_millis", "EPOCH_US_TS": "timestamp_micros"}`, `utc_ts_sql(ts_sql)`, `time_rule_sql(col, rule)`, `convert_sql` dispatch, `unset_raw_sql(c)`, `UTC_SELF_CHECK`, `assert_utc_format()`. Update the docstring examples (`last_verify_at` now yields a string).
   - §8: `ColumnSpec.is_time` (`convert_rule in TIME_RULES`). `can_cast_null` stays as is (string + time rule → `True`).
   - §9: `build_table_specs` type/rule validation (D1).
   - §10: `target_ddl` docstring example uses the new tech columns; no logic change (`spec.tech_columns`).
2. `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`: call `assert_utc_format()` after parameter validation; `cast_null_flag` adds `& ~F.expr(unset_raw_sql(c))`; `table_stats` adds `_unset__<col>` for `c.is_time and c.convert_rule != "ISO_UTC_TS"`; log non-zero counts; `build_merge_sql(spec, target, view, merge_clock)` per D5; `merge_into_target` computes and validates `merge_clock`. Update the change-log and section B markdown.
3. `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`: same self-check, cast-null flag, unset counts; `build_merge_sql(spec, target, view, merge_clock)` per D6; `merge_into_target` computes the clock. Guard text unchanged.
4. `notebooks/NB_CREATE_DDL.ipynb`: D7 (partner renames and rules, 3P two columns, `PSEUDO_TYPES`, `KNOWN_RULES`, `validate_rows`, registry comment, header comments `[SỬA 10/10]`). `show_registry` already lists non-`NONE` rules; expected partner list after seed is the D7 table.
5. `notebooks/NB_SETUP_L1_TS_AUDIT.ipynb` (new, Main adds it to `scope.files` in `task-state.yaml`): D8. First cell is the parameter cell; `%run NB_LIB_EXTRACT_RAWDATA`.
6. Context (Vietnamese prose per each file's existing language; identifiers in English):
   - `docs/context/02_NAMING_CONVENTION.md` first. §5.1: `*_at` in `ctrl_*` stays `TIMESTAMP`; silver L1 business instants and audit columns are `STRING` UTC `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'`; partner source `created_at` / `updated_at` → `src_created_at` / `src_updated_at`. §5.2: new L1 partner and 3P technical tuples, `created_at` / `updated_at` meaning, 3P technical clocks stay `TIMESTAMP`, no `_ingested_at`. §5.3: add `_unset__<col>`. §6: add `ISO_UTC_TS` to the `convert_rule` enum and the string-type requirement of the time rules.
   - `docs/context/01_DATA_MODEL.md`: L1 partner and 3P technical-column paragraphs (lines describing `_ingested_at`); add the sanitized 3P bronze sample (from `evidence/3p-sample-shapes.md`) next to the 3P bronze schema table.
   - `docs/context/CTRL_TABLES_CONTEXT.md`: registry `data_type` / `convert_rule` semantics for time rules and the zero sentinel. Do not touch `raw_ingested_at`.
   - `docs/context/NB_LIB_EXTRACT_RAWDATA.md`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`: tech tuples, rules, MERGE text, self-check.
   - `docs/context/CHECK_CTRL_SNAPSHOT.py`: no change (its matches are `raw_ingested_at` in `ctrl_cdc_*`).
7. Before coding, Main re-greps the repository for readers of L1 `_ingested_at`, partner business `created_at` / `updated_at`, `source_created_at`, and `published_at`. At architecture time no repository notebook outside the two extract notebooks reads them (`NB_LIB_TRANSFORM_SLV_GLD` and `NB_00_ORCHES_SLV_TO_GLD` only reference L1 tables generically through edges).

## Verification strategy

Local (`python scripts/vv.py verify`): notebook JSON validity; pure-Python checks Main can add without Spark: `utc_ts_text` truncation case; static parse of `NB_CREATE_DDL` confirming that no partner registry column is named `created_at` / `updated_at`, that every column in the D7 rule columns has `type: string` and the listed rule, that `review_id` / `time` are unchanged, and that no `_ingested_at` remains in the four notebooks except `_raw_ingested_at` / `raw_ingested_at`.

Review routing (unchanged): `sql-data-reviewer` (MERGE clauses, backfill SELECT, rule SQL), `spark-runtime-reviewer` (overwrite/`overwriteSchema`, self-check, F16 cost), `state-correctness-reviewer` (cut-over order, rerun, rollback after resume), then `risk-gate`.

Runtime (Fabric DEV, Vietnamese runbook by Main): self-check output; backfill dry run then apply; post-check JSON; two consecutive extract runs per flow with the `created_at` stability check; one `FULL_RELOAD` on one partner table proving `created_at` stays and `updated_at` moves; the first L2 run after cut-over; rollback rehearsal of one table with `RESTORE` before resume.

## Evidence used

- `evidence/column-inventory.md`: registry seed inventory, collision of partner business names with audit names, 3P `review_id` dependency on `time`.
- `evidence/e1-interpretation.md` + `results/e1_partner_timestamp_shapes.txt`: seconds versus millis per column, zero sentinels, ISO classes (6 fractional digits, `1970-01-01T00:00:00Z` values), unobserved columns.
- `evidence/e1-interpretation.md` (E2) + `results/e2_3p_timestamp_shapes.txt`: 3P ISO UTC with 3/6/9 fractional digits and `Z`; `ingested_date` is a date.
- `evidence/e3-e4-interpretation.md` + results: deployed registry equals the git seed (301 rows; only `last_verify_at` uses `EPOCH_S_TS`); silver technical columns `deleted`, `_ingested_at`, `_source_db`; two partner targets have no silver table; current `hotel_*` rows are zero sentinels; `orders` millis confirmed on silver.
- `evidence/3p-sample-shapes.md`: sanitized 3P bronze shapes for context.
- `decision.md` 2026-10-10 user decisions: rename, 3P format-only, option 3 unit assignment (including unmeasured order columns as `EPOCH_MS_TS` and `product_posts.validity_*`, `business_locations`, `product_post_translations` as `EPOCH_S_TS`), source `deleted_at` stays string, `0` is a sentinel.
- Repository: `NB_LIB_EXTRACT_RAWDATA` (`CONVERT_RULES`, `TECH_COLUMNS`, `SNAPSHOT_TECH_COLUMNS`, `build_table_specs` collision check, `ensure_target` mismatch `ConfigError`, `run_merge`), both extract `build_merge_sql` implementations, `NB_CREATE_DDL` `TABLE_CONFIGS` / `TABLE_CONFIGS_3P` / `resolve_type` / `seed_registry` (`replaceWhere`), `NB_LIB_TRANSFORM_SLV_GLD` edge classification (overwrite and `RESTORE` count as data changes), `02_NAMING_CONVENTION.md` §5 and §8 (library must not `spark.conf.set`).

## Evidence needed

None. The remaining backfill approximation (A4: `created_at` of pre-existing rows = old `_ingested_at`) and the unmeasured-unit columns covered by the user's option 3 are decisions, not open evidence. Main records both in `decision.md`.
