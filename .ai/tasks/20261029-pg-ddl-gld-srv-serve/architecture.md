RESULT: PASS

## Main brief

### Decision
- PASS. Create one PostgreSQL file with five `CREATE TABLE apps.srv_poi_*` statements inside a single `BEGIN; ... COMMIT;`. Columns, order, and types follow `model-design.md` `## Columns`. Keys are table-level `PRIMARY KEY (...)` in `NodeSpec.pk` order, left unnamed so PostgreSQL uses `<table>_pkey`.
- The file uses plain `CREATE TABLE`, not `IF NOT EXISTS`. A rerun errors with `42P07` and rolls back, so an existing table whose shape has drifted is never silently kept.
- The file has no `CREATE SCHEMA`, index, view, FK, GRANT, or COMMENT. Schema `apps` must already exist.
- Conflict to resolve first: `.sqlfluff` and `vv.py` lint `*.sql` as sparksql and `*.pg.sql` as postgres. The scoped name `gld_srv_serve.sql` is expected to fail sparksql parsing. Recommendation: rename to `sql/postgres/gld_srv_serve.pg.sql` (user decision). File content is the same under either name.

### Invariants Main must preserve
- Exactly 5 `CREATE TABLE apps.srv_poi_{info,multi_lang,amenity,media_gallery,review}`. Nothing in `public`, nothing unqualified.
- Column counts 32 / 12 / 11 / 16 / 13 in gold order. `apps.srv_poi_review` has no `lang`. `apps.srv_poi_multi_lang` keeps `lang`.
- PK order: info (poi_id); multi_lang (poi_id, lang); amenity (poi_id, business_sector, amenity_group, amenity_raw); media_gallery (media_id); review (review_id).
- `NOT NULL` appears on exactly 9 columns, all of them PK columns. `poi_id` stays nullable in media_gallery and review.
- Allowed types only: text, boolean, integer, int8 (review.rating_count only), double precision, numeric(4, 2), timestamp without time zone.
- The header comment lists the full D-TYPE mapping, including `BIGINT -> int8` and `Kiểu khác -> MISSING`, and notes D-LANG.
- One transaction: all five tables are created or none are.
- No changes under `notebooks/`, `pipelines/`, or `scripts/`. `NodeSpec.pk` is untouched.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | `sql/postgres/gld_srv_serve.sql` (or `sql/postgres/gld_srv_serve.pg.sql` if the user picks option A at Stop 1) | whole file; content in architecture `## FILE content` | Create the file with the FILE block bytes verbatim | All checks under Tests and verification pass. The bytes equal the FILE block. |
| 2 | `.ai/tasks/20261029-pg-ddl-gld-srv-serve/task-state.yaml` + `request.md` + `decision.md` (only if option A) | `scope.files`; Scope/Acceptance file name; new ledger row D-FILE | Replace the path with `sql/postgres/gld_srv_serve.pg.sql`. Record D-FILE with reason `.sqlfluff` L2 dialect routing. | `python scripts/vv.py verify 20261029-pg-ddl-gld-srv-serve` shows `task-state: PASS` |

### Order and stop points
1. **STOP (user decision)**: ask exactly one question. Option A: rename to `sql/postgres/gld_srv_serve.pg.sql` (recommended; `vv.py verify` then lints it with the postgres dialect). Option B: keep `gld_srv_serve.sql` and accept a sparksql lint FAIL as a recorded finding.
2. If A, apply edit row 2 first. Then save the file from edit row 1.
3. Run the local checks below. **STOP (evidence)** if any check fails. Under option B, if `sqlfluff[sparksql]` FAILs, record the finding in `decision.md` `## Xử lý findings` as `accepted-risk` with the manual postgres lint output, then continue.
4. Route the change to `sql-data-reviewer`.
5. Do not apply the file to any shared PostgreSQL. That is an operator action outside this task, and the runtime gate stays `not_required`.

### Tests and verification
- `python -m sqlfluff lint --dialect postgres --nocolor <path>` → no PRS or other violations.
- `python scripts/vv.py verify 20261029-pg-ddl-gld-srv-serve`
  - Option A: `sqlfluff[postgres]: PASS`, `pytest: PASS`, `task-state: PASS`.
  - Option B: record the `sqlfluff[sparksql]` status as it comes out.
- `rg -c "^CREATE TABLE apps\.srv_poi_" <path>` → `5`.
- `rg -n "NOT NULL" <path>` → 9 lines, all PK columns.
- `rg -n -i "varchar|timestamptz|bigint|serial|CREATE (INDEX|VIEW|SCHEMA)|GRANT|public\.|IF NOT EXISTS|DROP " <path>` → only the header comment line `BIGINT -> int8`.
- Inside the `apps.srv_poi_review` block, no line `    lang text`.
- `git status --porcelain` → no paths under `notebooks/`, `pipelines/`, or `scripts/`.
- Optional, not a gate: on a disposable PostgreSQL with schema `apps`, run `psql -v ON_ERROR_STOP=1 -f <path>` twice. The first run commits. The second exits non-zero with `42P07` and changes nothing. The `information_schema.columns` query in `## Verification` returns 84 rows.

### Read only if needed
- `## File name and lint dialect` → rows 1, 2 and Stop 1.
- `## FILE content` → row 1.
- `## Idempotency`, `## Transaction and commit boundaries`, `## Concurrency` → row 1 (BEGIN/COMMIT, no IF NOT EXISTS).
- `## Grain and keys`, `## Alternatives considered` → row 1 (unnamed PK, no FK, no CREATE SCHEMA, `int8` spelling).
- `## Verification` → Tests and verification, including the catalog query.
- `## Rollback and forward recovery`, `## Security`, `## Risks carried to the future sync (not designed here)` → reviewer questions; no edits.

# Architecture: 20261029-pg-ddl-gld-srv-serve

## Scope

One new PostgreSQL DDL file, `sql/postgres/gld_srv_serve.sql`. It creates five tables in the existing schema `apps`: `srv_poi_info`, `srv_poi_multi_lang`, `srv_poi_amenity`, `srv_poi_media_gallery`, `srv_poi_review`. Entities, grain, keys, columns, and lineage come from `model-design.md` (`## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`). This architecture does not add to that model. It decides only how the file runs: transaction shape, rerun behaviour, preconditions, verification, and how the operator applies it.

Sources checked in this run:
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables` (raw file lines 362–481). The five gold specs match the `model-design.md` `## Columns` table row for row: 32 + 12 + 11 + 16 + 14 columns.
- The latest `notebooks/NB_CREATE_DDL.ipynb` cells agree with `init_tables`. Review is at L4503–4510 (`rating_count BIGINT`, `lang STRING`). Media `MEDIA_COLS` is at L3650. Amenity `AMENITY_COLS` is at L3860. Info gains `rating_overall`/`rating_count`/`review_count` at L3434. Multi-lang gains `experience` at L4303.
- `NodeSpec.pk`: `NB_GLD_SRV_POI_INFO.ipynb` L301 `("poi_id",)`; `NB_GLD_SRV_POI_MULTI_LANG.ipynb` L99 `("poi_id", "lang")`; `NB_GLD_SRV_POI_AMENITY.ipynb` L72 `("poi_id", "business_sector", "amenity_group", "amenity_raw")`; `NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb` L81 `("media_id",)`; `NB_GLD_SRV_POI_REVIEW.ipynb` L117 `("review_id",)`.
- `.sqlfluff` line 2 and `scripts/vv.py` `cmd_verify` L1679–1680: `*.pg.sql` is linted as postgres, and any other `*.sql` is linted as sparksql. See `## File name and lint dialect`.

## Non-goals

- No change to the sync job, any loader, Fabric notebooks, pipelines, lakehouse DDL, or `NodeSpec.pk`.
- No `CREATE SCHEMA`, index, view, foreign key, `GRANT`, `COMMENT ON`, trigger, or default.
- No change to `gld_enr_poi_info` or `gld_enr_poi_review`, and no use of `notebooks_lgc/` or the drawio `srv_*` tags.
- The task does not apply the DDL to any shared PostgreSQL instance. The runtime gate stays `not_required`.
- No new pytest file, because `scope.files` holds only the SQL file.

## Invariants

1. The file contains exactly five `CREATE TABLE` statements, all qualified as `apps.<name>` with the names from D-NAME. It never uses `public` or an unqualified name.
2. Each table's columns, column order, and types match `model-design.md` `## Columns`, which is gold DDL order with D-TYPE/D-BIGINT types. `apps.srv_poi_review` has 13 columns and no `lang` (D-LANG). The other tables have 32, 12, 11, and 16 columns.
3. `PRIMARY KEY (...)` column order equals `NodeSpec.pk`, as listed under `## Scope`.
4. `NOT NULL` appears only on primary-key columns. These are exactly the columns gold marks `STRING NOT NULL`. `poi_id` stays nullable in media_gallery and review.
5. Only these type spellings appear: `text`, `boolean`, `integer`, `int8`, `double precision`, `numeric(4,2)`, and `timestamp without time zone`. The file never uses `varchar`, `timestamptz`, `bigint`, `serial`, or `json`.
6. The header comment lists the full D-TYPE mapping, including `BIGINT -> int8` and `other -> MISSING`. It also notes the D-LANG omission.
7. The file runs as one transaction, so it creates either all five tables or none.
8. Running the file again never changes an existing table. It errors and rolls back.
9. No Fabric file changes. `git diff --name-only` shows only the SQL file, plus task files under `.ai/`.

## State ownership

- Gold `lh_vv_gold.dbo.gld_srv_poi_*` stays the system of record. The `apps.srv_poi_*` tables are serving copies.
- This task owns only the table definitions. Row content will belong to a future sync job, which is out of scope. No process in this task writes rows.
- The `apps` schema, its owner, and grants belong to the PostgreSQL DBA/operator (D-SCHEMA names the schema; nothing records who created it). The new tables are owned by the role that runs the file.

## Grain and keys

See `model-design.md` `## Entities and grain` and `## Keys`. The design uses table-level `PRIMARY KEY (...)` clauses without a constraint name, so PostgreSQL names each one `<table>_pkey`. The table-level clause keeps the column order of composite keys visible, and it reads the same way for single-column keys. Each key creates one unique btree index. That index comes with the key itself and does not count as an "added index".

All key columns are `text`. PostgreSQL databases always use a deterministic default collation, so two values count as equal only when their bytes are equal. That matches Spark's binary string equality on the gold side. Gold rows that are unique on `NodeSpec.pk` therefore stay unique in PostgreSQL. Foreign keys stay logical only (`model-design.md` `## Keys`, `## Conflicts and questions` item 4).

## Ordering

Tables appear in request order: info, multi_lang, amenity, media_gallery, review. There are no foreign keys, so the order does not affect correctness. Columns follow gold DDL order (`model-design.md` `## Columns`, closing note).

## Transaction and commit boundaries

PostgreSQL DDL is transactional, so the file wraps the five statements in `BEGIN; ... COMMIT;`. If any statement fails, for example because `apps` is missing, a table already exists, or the role lacks `CREATE` on `apps`:
- With `psql -v ON_ERROR_STOP=1 -f`, psql exits non-zero before `COMMIT`. When the session closes, the open transaction rolls back.
- Without `ON_ERROR_STOP`, every later statement fails with "current transaction is aborted", and the final `COMMIT` becomes `ROLLBACK`.

Either way the end state is all five tables or none. Do not run the file with `psql -1` or `--single-transaction`, because the file already contains `BEGIN`/`COMMIT`.

## Idempotency

Rerunning the file never changes state, but it does exit with an error. A second run fails on the first `CREATE TABLE` with `42P07 relation "srv_poi_info" already exists` and rolls back.

| Option | Behaviour when tables exist | Behaviour when an existing table has a different shape | Choice |
|---|---|---|---|
| Plain `CREATE TABLE` inside one transaction | Errors and rolls back; no change | Errors loudly; the operator sees the conflict | Selected |
| `CREATE TABLE IF NOT EXISTS` | Prints a notice and exits 0 | Skips silently and leaves the drifted shape in place, which breaks invariant 2 without any signal | Rejected |
| `DROP TABLE IF EXISTS` + `CREATE` | Recreates the table | Destroys data a future sync loaded | Rejected: destructive |

The selected option fails closed. A clean exit code on rerun matters less than catching shape drift, because no automated job runs this file.

## Concurrency

Two sessions running the file at the same time: PostgreSQL serializes catalog inserts. The second session either waits and then fails with `42P07`/`23505` on `pg_type`/`pg_class` and rolls back, or it commits first and the other session fails. Exactly one copy of the five tables ends up existing. No application traffic exists yet, so there is no lock contention with readers.

## Retry and recovery

- Failure from a missing schema (`3F000 schema "apps" does not exist`): the operator or DBA creates `apps` (outside this file), then reruns.
- Failure from a missing privilege (`42501`): grant `CREATE` on `apps` to the deploying role, then rerun.
- `42P07` on rerun: compare the existing table with the catalog check under `## Verification`. If it matches, nothing needs doing. If it differs, the fix is out of scope and needs a new task.

## Partial failure

Not applicable: the single transaction makes partial creation impossible (`## Transaction and commit boundaries`).

## Observability

A successful psql run prints `BEGIN`, then `CREATE TABLE` five times, then `COMMIT`. Any other output means failure. After applying, the operator runs the catalog checks in `## Verification` (post-apply). No metrics or logging objects are added.

## Security

- The file holds no credentials, no hostnames, and no `GRANT`/`REVOKE`. The operator supplies connection details at run time (for example in `PGPASSWORD` or `.pgpass`), never in the repository.
- The file never mentions `public`, so it cannot widen access through the default `PUBLIC` privileges on schema `public`.
- Read grants for the API role on the new tables come from the DBA. They are out of scope. New tables give no privileges to other roles until someone grants them.
- PII: `author_name`, `review_text`, `phone`, and `email` will hold copied gold data once a sync runs. This task loads no data.

## Rollout

1. Main writes the file (after Stop 1 on the file name).
2. Local verification and `sql-data-reviewer` review follow.
3. The operator applies the file to PostgreSQL outside this task. This is an outward-facing action that needs operator confirmation, and the task does not gate on it. Recommended sequence: a disposable or dev database first, then the serving database. Use `psql -v ON_ERROR_STOP=1 -f <file>` as a role with `CREATE` on `apps`.

## Rollback and forward recovery

- Before any data exists: `DROP TABLE apps.srv_poi_info, apps.srv_poi_multi_lang, apps.srv_poi_amenity, apps.srv_poi_media_gallery, apps.srv_poi_review;` in one transaction. This is an operator runbook command and is not saved in the repository. Run it only after confirming the tables are empty and no consumer depends on them.
- After a sync has loaded data: never drop a table. Forward-fix through a new task that adds an `ALTER TABLE` file.
- Undoing the repository change is `git revert` of the commit that adds the file. That has no effect on Fabric.

## File name and lint dialect

`scope.files` and `request.md` name `sql/postgres/gld_srv_serve.sql`. The repository's lint routing is in `.sqlfluff` line 2 ("`*.sql = sparksql, *.pg.sql = postgres`") and `scripts/vv.py` L1679–1680. Under that routing, `python scripts/vv.py verify` would lint this file with `--dialect sparksql`. PostgreSQL syntax such as `timestamp without time zone` and `int8` is expected to fail sparksql parsing (`PRS`). That would make the `sqlfluff[sparksql]` step FAIL and block `local_verification`. Main should confirm this by running the command and must not assume the result.

| Option | Effect | Cost |
|---|---|---|
| A. Rename to `sql/postgres/gld_srv_serve.pg.sql` | `vv.py verify` lints with postgres, as the repository convention intends | Changes `scope.files` and the request's file name, so it needs user approval |
| B. Keep `gld_srv_serve.sql` | Matches the request exactly | `vv.py verify` FAILs on sparksql. Main must run a manual postgres lint and record the sparksql FAIL as an accepted finding in `decision.md` |
| C. Edit `vv.py` or `.sqlfluff` routing (for example, treat `sql/postgres/**` as postgres) | Fixes the routing for every file | Out of scope: it changes shared tooling |

Recommendation: A. The file content is identical under either name. This is a user decision (Stop 1). The FILE block below uses the current scoped path. If the user picks A, Main updates `scope.files`, the request's file name, and the ledger (new row D-FILE) first, then saves the same bytes at the `.pg.sql` path.

## Alternatives considered

- `CREATE SCHEMA IF NOT EXISTS apps` in the file. Rejected. The request allows only five `CREATE TABLE` statements and calls everything else an extra object. Schema ownership belongs to the DBA. If the schema is missing, the run fails closed with `3F000`.
- Named constraints (`CONSTRAINT pk_srv_poi_info PRIMARY KEY`). Rejected. This would invent a naming convention the repository does not have. The default `<table>_pkey` name is already deterministic.
- `bigint` instead of `int8`. These are the same PostgreSQL type, but D-BIGINT records `int8` verbatim, so the file uses `int8`.
- Foreign keys to `apps.srv_poi_info`. Rejected per `model-design.md` `## Keys`. Gold declares none, and a future sync would then depend on load order.
- `IF NOT EXISTS` and drop-and-recreate are compared under `## Idempotency`.

## Risks carried to the future sync (not designed here)

- Spark `TIMESTAMP` is an instant shown in the session time zone. `timestamp without time zone` (D-TYPE) stores a wall-clock time without a zone. The sync must write UTC wall-clock time consistently.
- Spark `STRING` can contain U+0000, which PostgreSQL `text` rejects. The sync must handle that character.
- Gold `DECIMAL(4,2)`, `INT`, and `BIGINT` have the same ranges as `numeric(4,2)`, `integer`, and `int8`, so the copy loses no data.

## Implementation plan

1. Stop 1: the user picks the file name (`## File name and lint dialect`).
2. Main saves the FILE block verbatim at the chosen path.
3. Main runs the checks in `## Verification` (local), records the results, and routes the change to `sql-data-reviewer`.

## Verification

Local (gate):
1. `python -m sqlfluff lint --dialect postgres --nocolor <path>`: no `PRS` violations, and no violations of the configured rules.
2. `python scripts/vv.py verify 20261029-pg-ddl-gld-srv-serve`
   - Option A: `sqlfluff[postgres]` PASS, `sqlfluff[sparksql]` SKIP, `pytest` PASS, `task-state` PASS.
   - Option B: record the `sqlfluff[sparksql]` result as it comes out. If it FAILs, record the accepted finding in `decision.md`.
3. Structural checks with ripgrep on the file:
   - `rg -c "^CREATE TABLE apps\.srv_poi_" <path>` → `5`
   - `rg -n -i "varchar|timestamptz|bigint|serial|CREATE (INDEX|VIEW|SCHEMA)|GRANT|public\.|IF NOT EXISTS|DROP " <path>` → only header-comment hits, and only for the words `BIGINT` and `MISSING`. No statement-level hits.
   - `rg -n "NOT NULL" <path>` → exactly 9 column lines: poi_id (info); poi_id and lang (multi_lang); four amenity key columns; media_id; review_id.
   - Inside the `apps.srv_poi_review` block there is no line starting with `    lang`.
4. `git status --porcelain` shows no changes under `notebooks/`, `pipelines/`, or `scripts/`.

Optional, not a gate (runtime `not_required`): apply to a disposable PostgreSQL that has `CREATE SCHEMA apps` (never the shared serving database). Run `psql -v ON_ERROR_STOP=1 -f <path>` twice. The first run commits five tables. The second exits non-zero with `42P07`, and the table set is unchanged. Then run this catalog check:

```sql
SELECT table_name, ordinal_position, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'apps' AND table_name LIKE 'srv_poi_%'
ORDER BY table_name, ordinal_position;
```

Expected: 84 rows (32 + 12 + 11 + 16 + 13). `rating_count` in `srv_poi_review` reports `bigint`, and `rating_count` in `srv_poi_info` reports `integer`.

## FILE content

FILE: sql/postgres/gld_srv_serve.pg.sql
-- PostgreSQL DDL cho 5 bảng gold serving, schema apps. Task 20261029-pg-ddl-gld-srv-serve.
-- Nguồn cột: lh_vv_gold.dbo.gld_srv_poi_* (NB_SETUP_INITIAL_DDL cell init_tables, NB_CREATE_DDL).
-- Khóa chính theo NodeSpec.pk của notebook NB_GLD_SRV_POI_* tương ứng.
-- Ánh xạ kiểu Fabric -> PostgreSQL (decision.md D-TYPE, D-BIGINT):
--   STRING       -> text
--   BOOLEAN      -> boolean
--   INT          -> integer
--   BIGINT       -> int8
--   DOUBLE       -> double precision
--   DECIMAL(p,s) -> numeric(p,s)
--   TIMESTAMP    -> timestamp without time zone
--   Kiểu khác    -> MISSING
-- NOT NULL chỉ ở cột gold NOT NULL; đó đều là cột khóa chính.
-- apps.srv_poi_review không có cột lang (decision.md D-LANG). Gold gld_srv_poi_review vẫn giữ lang.
-- Schema apps phải có sẵn. File không tạo schema, index, view hay quyền.
-- Chạy: psql -v ON_ERROR_STOP=1 -f <file>. Chạy lại sẽ lỗi "already exists" và rollback, không đổi gì.

BEGIN;

CREATE TABLE apps.srv_poi_info (
    poi_id text NOT NULL,
    poi_name text,
    source_name text,
    business_sector text,
    business_category text,
    subcategory_tags text,
    destination_id text,
    full_address text,
    street text,
    ward text,
    district text,
    city text,
    country_code text,
    postal_code text,
    lat double precision,
    lng double precision,
    phone text,
    email text,
    website_url text,
    operating_status text,
    is_verified boolean,
    is_recommended boolean,
    is_bookable boolean,
    operating_hours text,
    holiday_exceptions text,
    rating_overall numeric(4, 2),
    rating_count integer,
    review_count integer,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (poi_id)
);

CREATE TABLE apps.srv_poi_multi_lang (
    poi_id text NOT NULL,
    lang text NOT NULL,
    source_name text,
    time_to_spend text,
    best_time text,
    cost_vnd text,
    description text,
    experience text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (poi_id, lang)
);

CREATE TABLE apps.srv_poi_amenity (
    poi_id text NOT NULL,
    business_sector text NOT NULL,
    amenity_group text NOT NULL,
    amenity_raw text NOT NULL,
    amenity text,
    amenity_vi text,
    service_flags text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (poi_id, business_sector, amenity_group, amenity_raw)
);

CREATE TABLE apps.srv_poi_media_gallery (
    media_id text NOT NULL,
    poi_id text,
    source_name text,
    photo_api_uri text,
    display_order integer,
    width_px integer,
    height_px integer,
    photographer text,
    blob_url text,
    thumbnail_url text,
    is_cover boolean,
    is_active boolean,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (media_id)
);

CREATE TABLE apps.srv_poi_review (
    review_id text NOT NULL,
    poi_id text,
    rating_overall numeric(4, 2),
    rating_count int8,
    title text,
    review_text text,
    rating numeric(4, 2),
    review_date text,
    author_name text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    PRIMARY KEY (review_id)
);

COMMIT;
END_FILE
