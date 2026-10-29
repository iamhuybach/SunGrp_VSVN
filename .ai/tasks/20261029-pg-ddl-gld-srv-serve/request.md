# Request

## User outcome

PostgreSQL that serves the API has five gold serving tables, with the same columns and the same keys as current Fabric gold.

Verbatim request:

Tạo DDL cho 5 bảng Gold ở db PostgreSQL phục vụ serve API. Key sẽ tương ứng với grain của các bảng.

Lý do nghiệp vụ: PostgreSQL phục vụ API cần năm bảng gold serving, cùng cột và cùng khóa với gold Fabric hiện tại.

Năm bảng, schema Fabric `lh_vv_gold.dbo`:

- `gld_srv_poi_info`
- `gld_srv_poi_multi_lang`
- `gld_srv_poi_amenity`
- `gld_srv_poi_media_gallery`
- `gld_srv_poi_review`

Không gồm `gld_enr_poi_info` và `gld_enr_poi_review`.

## Scope

### In scope

- One file `sql/postgres/gld_srv_serve.pg.sql` with five `CREATE TABLE` statements.
- Primary key column order from each table notebook's `NodeSpec.pk`.
- Columns and Fabric types from current gold DDL (`NB_SETUP_INITIAL_DDL` cell `init_tables`, confirmed by the latest `NB_CREATE_DDL` cell for that table).
- Type mapping recorded at the top of the SQL file and in `decision.md`.

### Out of scope

- `gld_enr_poi_info` and `gld_enr_poi_review`.
- Extra columns, indexes, views, or an API.
- A sync notebook or sync job.
- Edits to Fabric notebooks, pipelines, or lakehouse DDL.
- `notebooks_lgc/` and `srv_*` tags in `docs/diagram/VSVN_DATA_MODEL.drawio`.

## Acceptance criteria

- `sql/postgres/gld_srv_serve.pg.sql` contains five `CREATE TABLE` statements.
- `PRIMARY KEY` column order matches `NodeSpec.pk` for that table's notebook.
- Columns and types come from current gold DDL. No added column, index, view, or API. No sync notebook.
- `NOT NULL` only where gold DDL writes `NOT NULL`, plus columns that belong to the primary key.
- Type mapping, written at the top of the file and in `decision.md`: `STRING` → `text`, `BOOLEAN` → `boolean`, `INT` → `integer`, `DOUBLE` → `double precision`, `DECIMAL(p,s)` → `numeric(p,s)`, `TIMESTAMP` → `timestamp without time zone`. Any other Fabric type is `MISSING`. Do not invent `varchar(n)` or `timestamptz`.
- If the repository has no PostgreSQL schema name, stop at `user_decision` and ask one question: the schema name. Do not use `public` and do not use a `srv_*` name from the old diagram.
- Do not edit Fabric notebooks, pipelines, or lakehouse DDL.

## Constraints

- `NodeSpec.pk` is the grain. Do not call `run-author --kind model` to change keys.
- Attach `data_model_change` only when a PostgreSQL column or key differs from gold. A full-column copy does not attach it.
- Run architecture when §Classification requires it because this is PostgreSQL DDL. Do not expand scope to a sync job.
- Do not read `notebooks_lgc/` and do not read `srv_*` tags in `docs/diagram/VSVN_DATA_MODEL.drawio`.
- No Fabric DEV probe for this DDL.

## Classification rationale

- Complexity: `medium`. Signal `cross_system`: the SQL file is a PostgreSQL serving contract taken from Fabric gold grain and columns. Signal `data_model_change`: the user removed column `lang` from the PostgreSQL review table (`decision.md` D-LANG). Keys stay `NodeSpec.pk`. The unmapped `BIGINT` still blocks writing.
- Risk: `low`. The change is one new SQL file. Fabric notebooks, pipelines, and lakehouse DDL stay unchanged. Once the schema name and the `BIGINT` mapping are known, local verification can check the file. No deployed behavior changes in this task.
- Architecture: required. `docs/agent-system/WORKFLOW.md` §Classification: logic moving between bronze, silver, gold, orchestration, or PostgreSQL sync. This task adds the PostgreSQL DDL for the five gold serving tables. The sync job stays out of scope. The gate is not run in this session: the schema name and the `BIGINT` mapping are missing, so the task stops at `user_decision` before architecture.
- Evidence: not required. Keys and column types are in the repository notebooks named by the request. No Fabric probe.
- Runtime proof: not required. The deliverable is a SQL file. Runtime gate stays `not_required` and is not marked pass.
- Reviewer routing: `sql-data-reviewer`. `docs/agent-system/WORKFLOW.md` §Review routing: that reviewer owns PostgreSQL SQL. No Spark notebook, pipeline JSON, CDC, or MERGE is in scope, so `spark-runtime-reviewer`, `fabric-pipeline-reviewer`, and `state-correctness-reviewer` are not routed. Risk is `low`, so `risk-gate` is not required.
