RESULT: PASS

## Main brief

### Decision

One task, eight Main sessions CT-1..CT-8 under EX-03; all `FILE:` blocks live here and every path below goes into `scope.files` before `materialize`. API lands at `services/data-serving-service/`, docs at `docs/poi-serving-api/`, copied from `D:\git\SunGrp_VSVN_API` commit `20bca8a` (D-01..D-04). Gold DDL (`NB_SETUP_INITIAL_DDL` cell `init_tables`) plus NodeSpec `pk` is the serving contract; Flyway is removed and tests load `sql/postgres/gld_srv_serve.pg.sql` (D-08..D-10). Runner honors approved `exceptions` behind a flag switched on only after `external-smoke` passes with `claude-fable-5-1` (D-07). D-05 commit policy everywhere; hooks block push, reset, rebase, amend, recursive delete. Main model and `doctor` defaults unchanged (D-06).

### Invariants Main must preserve

- Root `AGENTS.md` ≤ 8,192 B after every CT; `python scripts/vv.py doctor` prints no `WARN` after every CT.
- No credential value, DEV host name, or `.env.example` enters the repo; compose and MCP read secrets from environment only.
- `D:\git\SunGrp_VSVN_API` is never written; copies are byte-identical except the edits listed for CT-3/CT-4.
- Default models in `agent_runner.py:16-25`, `vv.py` expected models, and `doctor` pins stay unchanged; an override is applied only from an `exceptions` entry with `approved_by: user` and only when `HONOR_EXCEPTIONS` is true.
- Entity, DTO, and test columns are a subset of the gold table columns; `tests/test_srv_poi_serving_contract.py` is the proof and must pass before CT-4 ends.
- `verify` never reports `PASS` for the `maven` lane without Docker unless `--allow-no-docker` is printed in the log; `local_verification` is not `pass` on such a run.
- Hooks deny `git push`, `git reset`, `git rebase`, `git commit --amend`, `git clean`, `git filter-branch`, and recursive deletes in Cursor and Claude Code; `git commit` is allowed.
- `.cursor/rules` always-apply total ≤ 4,096 B; each `SKILL.md` ≤ 20,480 B; `docs/AGENT_PROMPT_SAMPLES.md` ≤ 25,600 B; `services/*/AGENTS.md` ≤ 4,096 B.
- `vv.py` `REVIEWERS` and `.codex/agents/*.toml` change in the same CT-5 edit, or `doctor` fails.
- Every repository write of this task happens while `task.status` is `implementing`; review rounds use `reviewing` only.

### Edit list

| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1.1 | `scripts/agent_runner.py` | after `REVIEW_EFFORT` | add `HONOR_EXCEPTIONS = False`, `LANE_DEFAULTS`, `resolve_lane()` (§Code A) | `python -c "import scripts.agent_runner"` ok |
| 1.2 | `scripts/agent_runner.py` | `run_architecture`, `run_author`, `run_review`, `_review_schema` | add `model`/`effort` params defaulting to constants; schema enum and mismatch check use them | tests 1.7 |
| 1.3 | `scripts/vv.py` | `architecture_state_after`, `review_state_after`, `cmd_run_gate`, `cmd_run_author` | pass resolved lane; record `actual` = resolved model; print `MODEL OVERRIDE <id>` | tests 1.7 |
| 1.4 | `scripts/vv.py` | `main()` `external-smoke` | add `--architect-model`, `--architect-effort`; `cmd_external_smoke` forwards them | `external-smoke --help` shows flags |
| 1.5 | `scripts/vv.py` | `main()` `run-gate`, `run-author` | `--timeout` default 2700 | help shows 2700 |
| 1.6 | `scripts/agent_runner.py` | `_assert_repo_unchanged` | ignore paths under `.ai/.tmp/` in both snapshots | test 1.7 |
| 1.7 | `tests/test_vv.py` | end of file | add 5 tests named in §Tests | `pytest tests/test_vv.py -q` green |
| 1.8 | `.cursor/rules/00-main-orchestrator.mdc` | whole file | `FILE:` block (D-05 line, transition note, `docs/poi-serving-api/` exclusion) | `doctor` no WARN |
| 2.1 | `AGENTS.md` | lines 22, 66-69, 74, new §7 line | replacements in §Code B | `wc -c` ≤ 7,800 |
| 2.2 | `CLAUDE.md` | line 25 | `Do not push. Commit only when the user's current turn asks for it.` | grep |
| 2.3 | `.cursor/rules/20-data-pipeline.mdc` | line 10 | notebook name `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` (matches pipeline JSON) | grep `_BK` |
| 2.4 | `.cursor/rules/30-sql.mdc` | line 7 | append `A `.sql` file under a `db/migration/` path is PostgreSQL.` | grep |
| 2.5 | `.cursor/rules/40-java-api.mdc` | new | `FILE:` block | rule listed by Cursor |
| 2.6 | `services/data-serving-service/AGENTS.md`, `CLAUDE.md`, `.gitignore` | new | `FILE:` blocks | sizes per invariants |
| 2.7 | `scripts/vv.py` | `cmd_verify` | postgres lane for `/db/migration/`; `maven` lane (§Code C); `--allow-no-docker` | tests 2.12 |
| 2.8 | `scripts/vv.py` | `build_context` | `## API` block when `scope.systems` has `poi-serving-api` (§Code D) | test |
| 2.9 | `scripts/vv.py` | `cmd_doctor` | nested AGENTS budget, nested `.gitignore` check, rule 40 check, literal-secret scan, INFO lines (§Code E) | `doctor` PASS |
| 2.10 | `.cursorindexingignore` | end | add `services/*/target/` | file |
| 2.11 | `docs/agent-system/WORKFLOW.md` | §10 Commands; §6 rule 10; §Task artifacts | add `verify … --allow-no-docker`, `external-smoke --architect-model`; D-05 wording; API runtime note | grep |
| 2.12 | `tests/test_vv.py`, `tests/test_vv_context.py` | end | tests in §Tests | green |
| 2.13 | `docs/context/00_README.md` | file table | row for `docs/poi-serving-api/HANDOFF.md` | grep |
| 3.1 | `services/data-serving-service/**` | copy | 55 tracked files (all but `.env.example`, `docs/`); `.gitignore` from 2.6 wins | `git status` lists them |
| 3.2 | `docs/poi-serving-api/*` | copy | 6 files; add `[OUT_OF_DATE 2026-11-06, D-10]` notes at `DESIGN-AND-PLAN.md:241,404`, `API-GAPS.md:150,159`; `check-gaps.py:4` host → `<host>` | grep shows no `azure.com` |
| 3.3 | `services/data-serving-service/docker-compose.yml` | `environment` | `${POSTGRES_USER:?}`, `${POSTGRES_PASSWORD:?}`, URL built from them (§Code F) | `doctor` secret scan PASS |
| 3.4 | `services/data-serving-service/src/main/resources/application.yml` | `spring.datasource` | defaults removed; env vars required (§Code F) | no literal credential |
| 4.1 | `pom.xml` | dependencies, build | remove 2 Flyway deps; add `testResources` (§Code G) | `mvnw.cmd -q test` |
| 4.2 | `src/main/resources/application.yml`, `src/test/resources/application.yml` | `spring.flyway` | delete block | grep none |
| 4.3 | `db/migration/V1__init_srv_poi_tables.sql` | file | delete | gone |
| 4.4 | `src/test/resources/db/00_create_schema_apps.sql` | new | `FILE:` block | exists |
| 4.5 | `test/.../TestcontainersConfiguration.java` | bean | init files via `withCopyFileToContainer` (§Code G) | IT green |
| 4.6 | `test/.../DataServingApplicationTests.java` | `flywayMigrationCreatesAllServingTables` | rename `initScriptCreatesAllServingTables` | green |
| 4.7 | `domain/entity/PoiMediaGalleryId.java` | new | `FILE:` block | compiles |
| 4.8 | `domain/entity/SrvPoiMediaGallery.java` | class | `@IdClass(PoiMediaGalleryId.class)`, `@Id` on `poi_id`, `nullable = false` | contract test |
| 4.9 | `domain/repository/SrvPoiMediaGalleryRepository.java` | interface | `JpaRepository<SrvPoiMediaGallery, PoiMediaGalleryId>` | compiles |
| 4.10 | `domain/entity/SrvPoiReview.java` | field `sourceName` | delete field | contract test |
| 4.11 | `api/dto/PoiReviewItemResponse.java` | record | drop `sourceName` component | compiles |
| 4.12 | `service/PoiService.java` | `getReviews` map | drop `r.getSourceName()` | compiles |
| 4.13 | `test/.../PoiServiceTest.java` | line 243 | drop `.sourceName(...)` on review builder (line 70 is `SrvPoiInfo`: keep) | green |
| 4.14 | `test/.../PoiControllerIntegrationTest.java` | line 210 | 5-arg `PoiReviewItemResponse` | green |
| 4.15 | `test/.../PoiRepositoryIntegrationTest.java` | line 203 | `findById(new PoiMediaGalleryId("MED_002", TEST_POI_ID))`; line 68 keep | green |
| 4.16 | `tests/test_srv_poi_serving_contract.py` | new | `FILE:` block | `pytest -q tests/test_srv_poi_serving_contract.py` |
| 4.17 | `handoffs/author-input.md` → `runtime-runbook.md` | runbook | `run-author --kind runbook` for local compose smoke (§Runtime) | user records result |
| 5.1 | `.codex/agents/api-contract-reviewer.toml`, `app-security-reviewer.toml`, `jpa-performance-reviewer.toml`, `risk-gate.toml` | new / whole | `FILE:` blocks | `doctor` PASS |
| 5.2 | `scripts/vv.py` | `REVIEWERS` | add the three names (same edit as 5.1) | `doctor` PASS |
| 5.3 | `docs/agent-system/WORKFLOW.md` | §7 Review routing | three routing lines (§Code H) | grep |
| 5.4 | `.ai/evals/cases.yaml` | whole | `FILE:` block (8 + 4 cases) | `doctor` PASS |
| 6.1 | `.cursor/hooks.json`, `scripts/hooks/git_guard.py`, `scripts/hooks/task_state_guard.py` | new | `FILE:` blocks | manual deny test |
| 6.2 | `.claude/settings.json` | whole | `FILE:` block (deny list minus add/commit; hooks; WebFetch domains) | `doctor` PASS |
| 6.3 | `.cursor/skills/vsvn-task-workflow/SKILL.md` | line 57 | `Main commits only when the user's current turn asks for it; otherwise list a `commit` request.` | grep |
| 6.4 | `scripts/vv.py` | `_next_context` `ready_to_merge`; `build_closeout` `commit:` | `user push/merge; commit on request`; wait text `commit (on your request): …` | tests |
| 6.5 | `tests/test_vv_context.py` | `test_build_closeout_*` | adjust strings; add `test_git_guard_*` | green |
| 7.1 | `.cursor/skills/vsvn-api-service/SKILL.md` | new | `FILE:` block | `doctor` PASS |
| 7.2 | `docs/AGENT_PROMPT_SAMPLES.md` | whole | `FILE:` block (D-17) | ≤ 25,600 B |
| 7.3 | `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` | file | delete (D-16) | gone |
| 8.1 | `.cursor/mcp.json` | new | `FILE:` block | `doctor` secret scan PASS |
| 8.2 | `services/data-serving-service/AGENTS.md` | §Local database | already names `VV_SERVING_PG_URL` | no edit |

### Order and stop points

1. Main: set gate `architecture: pass`, `transition implementing`, add every path above to `scope.files`, record CT plan in ledger. CT-1 and CT-2 may run in two parallel chats (D-18); both touch `scripts/vv.py` and `tests/test_vv.py` in disjoint functions, so finish one before `verify` of the other.
2. CT-1 rows 1.1-1.8; `verify`; STOP (user): `python scripts/vv.py external-smoke --architect-model claude-fable-5-1 --architect-effort high --timeout 900`. PASS → Main sets `HONOR_EXCEPTIONS = True` (row 1.1) and re-runs tests. FAIL → leave `False`, ledger row "D-07 branch B: manual exception sessions", keep code.
3. CT-2 rows 2.1-2.13; `verify`, `doctor`; STOP (user, VERIFY-1..3): open a `.java` file in Cursor and confirm rule 40 attaches and expands `@services/data-serving-service/AGENTS.md`; run one `codex exec --sandbox read-only --cd services/data-serving-service "print the first heading of each AGENTS.md you loaded"` and confirm the nested file is listed. Failure → fallback in §Alternatives A3.
4. STOP (user) before CT-3: install JDK 26 (D-11); `java -version` shows 26; Docker running.
5. CT-3 rows 3.1-3.4; `verify` (maven lane runs `mvnw.cmd -q -B test`; Flyway still present, so IT green); `doctor`; set `risk_level: high` with ledger rationale (D-15); `transition verifying` → `reviewing`; STOP: `run-gate` review round 1 (`required_reviewers: []`, risk-gate). If the runner rejects an empty manifest, set `required_reviewers: [sql-data-reviewer]` and rerun. PASS → `user_decision` → `transition implementing`.
6. CT-4 rows 4.1-4.17; `verify`; STOP (evidence): if `tests/test_srv_poi_serving_contract.py` reports a gold column absent from `gld_srv_serve.pg.sql`, stop and open a data task (do not edit the DDL here). Then STOP (user, D-12): run `runtime-runbook.md` (compose + smoke), record result; `gates.runtime`.
7. CT-5 rows 5.1-5.4 (5.1 and 5.2 in one edit); `doctor`; STOP (user): `external-smoke` once to confirm Codex loads the new agents (optional, same command as today).
8. CT-6 rows 6.1-6.5; STOP (user, VERIFY-4): in Cursor run `git push --dry-run` and `git status`; expect deny then allow; in Claude Code the same. If Cursor hook event names differ, fix names only (§Alternatives A6).
9. CT-7 rows 7.1-7.3; `doctor`. 10. CT-8 rows 8.1-8.2; STOP (user): set `VV_SERVING_PG_URL` in the OS environment, restart Cursor, run `SELECT 1` through the MCP tool.
11. Closeout: user commits per D-05 after each CT or at the end; `transition ready_to_merge` only after rows 1-8 and gates.

### Tests and verification

- Every CT: `python scripts/vv.py verify 20261106-agent-system-unify-api`; `python scripts/vv.py doctor` (no WARN); `wc -c AGENTS.md`.
- CT-1: `pytest -q tests/test_vv.py -k "resolve_lane or review_schema_uses_resolved or smoke_flags or repo_snapshot_ignores_tmp or timeout_default"`; new tests: `test_resolve_lane_defaults_when_flag_off`, `test_resolve_lane_prefers_user_approved_exception`, `test_review_schema_uses_resolved_model`, `test_repo_snapshot_ignores_ai_tmp`, `test_run_gate_timeout_default_2700`.
- CT-2: `test_verify_routes_migration_sql_to_postgres_lane`, `test_verify_maven_lane_requires_docker`, `test_verify_maven_lane_allow_no_docker_marks_log`, `test_context_api_block_for_poi_serving_api`, `test_doctor_nested_agents_budget`, `test_doctor_rejects_literal_secret`.
- CT-3/4: `cd services/data-serving-service && mvnw.cmd -q -B test` (Docker on); `pytest -q tests/test_srv_poi_serving_contract.py`.
- CT-5: `python -c "import tomllib,glob;[tomllib.load(open(p,'rb')) for p in glob.glob('.codex/agents/*.toml')]"`; `doctor`.
- CT-6: `pytest -q tests/test_vv_context.py -k "git_guard or closeout"`; manual deny/allow check (step 8).
- CT-7: `doctor` budgets; `wc -c docs/AGENT_PROMPT_SAMPLES.md .cursor/skills/vsvn-api-service/SKILL.md`.
- CT-8: `python -c "import json;json.load(open('.cursor/mcp.json'))"`; `doctor`.

### Read only if needed

- §Code A-H → rows 1.1-1.3, 2.1, 2.7-2.9, 3.3-3.4, 4.1-4.5, 5.3.
- §Selected design → rows 1.x (runner), 2.7 (verify), 6.1 (hooks).
- §Alternatives and trade-offs → fallbacks at stop points 3, 5, 8.
- §Rollout, rollback, and forward recovery → per-CT rollback.
- §Security and data handling → rows 3.2-3.4, 8.1.
- §Verification strategy → acceptance table per CT and the `exceptions` entry template if a CT is split out.

# Architecture

Written by exception session EX-02 (`claude-fable-5-1`, effort high, Claude Code extension) on 2026-11-06. Inputs: `decision.md` ledger D-01..D-18, EX-03, BA-0311; `proposal.md` sections "h. Lộ trình", "Ràng buộc cho Architect (EX-02)", P-a1..P-g7; the three inventories; `handoffs/fable-architecture-input.md`. The document exceeds the 25 KB medium-risk guide because it carries eight child-task edit lists and the task is reclassified `high` at CT-3 (D-15, `cross_system`).

## Context and scope

- In scope: child tasks CT-1..CT-8 of the proposal roadmap, executed inside this task as eight Main sessions (the materializer reads only this task's `architecture.md` and only paths in its `scope.files`). CT-1 runner exceptions (D-07); CT-2 repository layout, nested instructions, `verify`/`context`/`doctor` lanes; CT-3 import of the API source and docs (D-01..D-04); CT-4 Flyway removal, `@IdClass`, `source_name` removal, serving contract test (D-08..D-10); CT-5 three Codex API reviewers and eval cases (D-13); CT-6 hooks and commit policy (D-05); CT-7 skill, prompt samples, plan deletion (D-16, D-17); CT-8 Cursor MCP PostgreSQL local (D-14).
- Out of scope: CT-9 (gold → PostgreSQL load). Opening condition: CT-4 done (contract test green) and a Fabric DEV probe plan; its own task with Main `grok-4.7` medium, `cross_system` + `idempotency`, Architect required. Also out: any Main-model lane (D-06), gold or `sql/postgres/gld_srv_serve.pg.sql` column changes (a `data_model_change` task), index DDL for PostgreSQL (needs query evidence), API features beyond the four existing endpoints.

## Non-goals

- No change to default models, `doctor` pins, or `.codex/config.toml` (D-06, D-07 branch B).
- No `git subtree`, no second repository, no write to `D:\git\SunGrp_VSVN_API`.
- No Claude Code skills or commands; Claude roles in this repo are read-only authors.
- No plugin, no Fabric MCP, no Codex MCP.
- No rewrite of `docs/poi-serving-api/*` content beyond `OUT_OF_DATE` markers and the host placeholder.

## Invariants

1. Serving contract: columns and types come from `NB_SETUP_INITIAL_DDL` cell `init_tables` for `lh_vv_gold.dbo.gld_srv_poi_*`; primary keys come from NodeSpec `pk` in `NB_GLD_SRV_POI_*` build cells (`srvinfobuild`, `srvmlbuild`, `srvamenitybuild`, `srvgallerybuild`, `srvrvbuild`). `sql/postgres/gld_srv_serve.pg.sql`, the JPA entities, and the DTOs are derived views; `tests/test_srv_poi_serving_contract.py` enforces column-set equality, type mapping, and PK equality.
2. The API reads schema `apps` only (`DESIGN-AND-PLAN.md` §C.4), never writes, never creates DDL at runtime (`ddl-auto: none`, no Flyway).
3. Instruction single source: `services/data-serving-service/AGENTS.md` is the only place API rules are written; root `AGENTS.md` §7 points to it; `CLAUDE.md` in that directory is `@AGENTS.md`; Cursor rule 40 references the same file. Root `AGENTS.md` wins on conflict.
4. Model policy: `agent_runner.py` constants remain the defaults; an override is applied only from a validated `exceptions` entry (`kind: model_override`, `approved_by: user`, matching `role`) and only while `HONOR_EXCEPTIONS` is `True`; the resolved model is printed and recorded in `models.<role>.actual`; `doctor` keeps today's pins.
5. Budgets: root `AGENTS.md` ≤ 8,192 B; always-apply rules ≤ 4,096 B; skill ≤ 20,480 B; prompt samples ≤ 25,600 B; nested `AGENTS.md` ≤ 4,096 B; `doctor` no WARN.
6. Secrets: no credential value, token, DEV host, or `.env` content in the repository; compose, `application.yml`, and MCP resolve them from environment variables; `doctor` scans for literals.
7. Git authority: agents never push, merge, rebase, amend, reset, clean, or delete recursively; an agent commits only when the user's current turn asks (D-05). Hooks enforce the deny list in Cursor and Claude Code; Codex runs read-only.
8. Verification truth: `verify` reports the `maven` lane `FAIL` when JDK 26 or Docker is missing unless `--allow-no-docker` is passed, which is printed in `verify.log`; `local_verification` is never `pass` from such a run for a task whose `scope.systems` contains `poi-serving-api`.
9. Repository writes occur only in `implementing`; `materialize --write` enforces it.

## State ownership, grain, and keys

Not a data-pipeline change; the state is repository files and task state.

| State | Owner | Grain | Key |
|---|---|---|---|
| `task-state.yaml`, `decision.md`, `resume.md` | Main | one task | task id |
| `architecture.md` | Architect (this session) | one task | task id |
| Root `AGENTS.md`, `CLAUDE.md`, rules, skills, hooks, MCP, Codex agents, `vv.py`, `agent_runner.py` | Main, per edit list | file | path |
| `services/data-serving-service/**`, `docs/poi-serving-api/**` | Main (copied from `20bca8a`) | file | path |
| Gold DDL and NodeSpec `pk` | data tasks (not this task) | table | `fq` name |
| `sql/postgres/gld_srv_serve.pg.sql` | data tasks; read-only here | table | table name |
| PostgreSQL `apps.srv_poi_*` rows | future loader (CT-9) | row | `poi_id`; `(poi_id, lang)`; `(poi_id, business_sector, amenity_group, amenity_raw)`; `(media_id, poi_id)`; `review_id` |

`model-design.md` is absent and not required: no table, column, grain, or key changes in gold or PostgreSQL. The API entity change (D-09) aligns the entity to the existing gold key; the column removal (D-10) aligns the entity to the existing gold column set.

## Ordering and transaction boundaries

- CT order (D-18): CT-1 ∥ CT-2 → CT-3 → {CT-4, CT-5, CT-7, CT-8} → CT-6 any time after D-05 (already decided, so CT-6 may follow CT-3). Both CT-1 and CT-2 edit `scripts/vv.py` and `tests/test_vv.py` in disjoint functions; run `verify` only after the other chat has saved, and never edit the same function in both.
- Within CT-5, `REVIEWERS` in `vv.py` and the three `.toml` files change in one edit before `doctor` runs, because `doctor` derives required files from `REVIEWERS`.
- Within CT-4, the order is: pom and test resources (4.1-4.5) → entity/DTO/service (4.7-4.12) → tests (4.13-4.15) → `mvnw.cmd -q test` → contract test (4.16) → runbook (4.17).
- The single review round (D-15) runs after CT-3 with `task.status = reviewing`; the task returns to `implementing` before CT-4.
- Git commits are the user's transaction boundary (one per CT recommended); the materializer writes files atomically per block but not per CT, so an interrupted CT is recovered by re-running `materialize --write` (idempotent on identical content) and the remaining anchor edits.

## Idempotency, concurrency, and recovery

- `materialize --write` skips identical files and overwrites changed ones; rerunning is safe.
- Anchor edits are specified as replacements of known text; a second application is a no-op when the text already matches. Main checks with `grep` before editing.
- `verify` and `doctor` are read-only and repeatable.
- Copy step (CT-3): copying again from `20bca8a` is idempotent for untouched files; the four CT-3 edits (compose, application.yml, docs markers, host placeholder) are re-applied by Main after any re-copy. `decision.md` records the source commit so a re-copy is checkable with `git -C D:\git\SunGrp_VSVN_API rev-parse HEAD`.
- Two parallel chats (CT-1, CT-2) are the only concurrency; the disjoint-function rule above plus "save before the other runs verify" prevents lost edits. If both edited `tests/test_vv.py`, the later chat appends; test names are unique per CT.
- Hooks are stateless scripts; a failed hook script denies nothing in Cursor if the JSON cannot be parsed (VERIFY-4 checks the actual behavior), so the guard must always print valid JSON.

## Partial failures

| Failure | Effect | Recovery |
|---|---|---|
| `external-smoke` with `claude-fable-5-1` fails (CT-1 stop 2) | Override code present but `HONOR_EXCEPTIONS = False` | Ledger "D-07 branch B"; manual exception sessions continue as today; code is dormant and tested with the flag forced in unit tests |
| Cursor does not expand `@file` in rule 40 (VERIFY-1) | Rule body lacks API rules | Alternative A3: Main pastes the nested `AGENTS.md` body into rule 40 and `doctor` compares the two by SHA-256 |
| Codex does not load nested `AGENTS.md` (VERIFY-2) | Codex reviewers miss API rules | Reviewer tomls (CT-5) already carry the rules they need; add one line in `.ai/prompts/review.md` telling the coordinator to read `services/data-serving-service/AGENTS.md` when the diff touches `services/` |
| JDK 26 missing at CT-3 | `maven` lane FAIL | Stop; user installs; no `--allow-no-docker` bypass for JDK |
| Docker missing | `maven` lane FAIL | User starts Docker; `--allow-no-docker` only for a diagnostic run, never for the gate |
| Review runner rejects empty reviewer manifest (stop 5) | round 1 fails before Codex runs | Set `required_reviewers: [sql-data-reviewer]`, rerun; round counter unaffected if the runner failed before writing state |
| Contract test finds a gold column missing in `gld_srv_serve.pg.sql` | CT-4 blocked | Stop with `EVIDENCE_REQUIRED`-style ledger row; open a data task; do not edit the DDL here |
| Cursor hook event names differ (VERIFY-4) | Hooks never fire | Fix names only in `.cursor/hooks.json` from the Cursor docs; scripts unchanged |
| `postgres-mcp` package or flag differs (CT-8) | MCP fails to start | Replace `command`/`args` only; keep env-variable credential rule |

## Alternatives and trade-offs

- A1 Single task vs eight child tasks. Selected: single task (input default). `materialize` reads only this task's `architecture.md`, and `scope.files` must list every path, which one task provides once. Cost: a long `scope.files` and one shared review budget (two review rounds). Mitigation: one review round after CT-3 (D-15), round 2 reserved for fixes. Split is allowed; §Verification strategy gives the `exceptions` entry and the transfer rule (copy the CT's `FILE:` blocks verbatim into the child `architecture.md`, list paths in the child `scope.files`).
- A2 Runner reads exceptions always vs behind a flag. Selected: flag, default `False`, switched after smoke (D-07). Trade-off: one extra edit, but no untested model id reaches a real gate.
- A3 Cursor nested `AGENTS.md` vs rule glob with `@file`. Selected: rule 40 with `@services/data-serving-service/AGENTS.md`; fallback is a verbatim copy guarded by a `doctor` hash check. Nested `AGENTS.md` loading by Cursor is unverified.
- A4 Flyway kept for tests vs removed. Selected: removed (D-08). Testcontainers copies two scripts into `/docker-entrypoint-initdb.d/` (schema, then repo DDL) via `withCopyFileToContainer`, keeping one DDL owner. Cost: the 10 Flyway indexes disappear from tests; they were never applied at runtime (`flyway.enabled: false`) and need query evidence before a DDL task adds them.
- A5 Review: one round covering CT-2 + CT-3 vs two rounds. Selected: one round after CT-3; two rounds would consume the cap before any fix round.
- A6 Hooks: Cursor-only vs Cursor + Claude Code. Selected: both, same `git_guard.py`; Claude Code `permissions.deny` keeps reset/restore/checkout/stash denies and drops only `git add`/`git commit`. Codex: no hook mechanism is known in `config.toml`; sandbox `read-only` already prevents git writes (VERIFY-5 in CT-6: confirm no `hooks` key exists in the installed Codex version's config schema; if one exists, mirror the same deny list).
- A7 MCP server choice: `postgres-mcp` restricted mode vs the archived reference server. Selected: `postgres-mcp` with `--access-mode=restricted` (VERIFY-6 at CT-8); credential via `${env:VV_SERVING_PG_URL}`.

## Selected design

### Runner lane resolution (CT-1)

`agent_runner.resolve_lane(exceptions, role, default_model, default_effort) -> Lane(model, effort, source)`. `source` is `"default"` or the exception id. Rules: `HONOR_EXCEPTIONS` false → defaults; else the first entry with `kind == "model_override"`, `role == role`, `approved_by == "user"`, non-empty `model`, `effort in {low, medium, high}`; otherwise defaults. `vv.py` passes `state.get("exceptions", [])`. `run_architecture`, `run_author`, `run_review` take `model`/`effort` keyword arguments defaulting to the constants; `_review_schema(reviewers, model, effort)` pins the resolved values; the Codex mismatch check compares against them. `architecture_state_after(state, verdict, model=agent_runner.ARCHITECT_MODEL)` and `review_state_after(state, result, round_number, model=agent_runner.REVIEW_MODEL)` record the resolved model; `cmd_run_author` records the resolved author model. `validate` already accepts an `actual` equal to an approved override for that role. `external-smoke --architect-model/--architect-effort` passes the values straight to `run_architecture` so the user can prove `claude-fable-5-1` before the flag is turned on. `--timeout` default 2700 for `run-gate` and `run-author`. `_git_snapshot` filters out entries whose path starts with `.ai/.tmp/`.

### Verification lanes (CT-2)

`cmd_verify`: `postgres_sql` includes `.pg.sql` and any `.sql` whose posix path contains `/db/migration/`; `spark_sql` excludes both. New lane `maven`: targets are changed files under `services/data-serving-service/`; preconditions `java -version` reports major ≥ 26 and `docker info` exits 0; command `mvnw.cmd -q -B test` (POSIX: `./mvnw -q -B test`) with `cwd` the service directory and a 1,800 s timeout; result `PASS`/`FAIL` with the last 40 lines. `--allow-no-docker` runs `-Dtest=!*IntegrationTest,!DataServingApplicationTests -Dsurefire.failIfNoSpecifiedTests=false` and labels the lane `PASS (docker tests skipped: --allow-no-docker)`; the label is what WORKFLOW §6 rule 10b forbids for a gate pass. `build_context` adds an `## API` block (service path, test command, nested `AGENTS.md` path, JDK and Docker presence) when `scope.systems` contains `poi-serving-api`. `cmd_doctor` adds: `services/*/AGENTS.md` ≤ 4,096 B (WARN like other budgets); `services/*/.gitignore` must not contain a line equal to `.claude` (FAIL); `.cursor/rules/40-java-api.mdc` exists and has `alwaysApply: false` (FAIL when `services/` exists); literal-secret scan over `.cursor/mcp.json`, `.mcp.json`, `services/*/docker-compose.yml`, `services/*/src/main/resources/application*.yml` with pattern `(?i)\b(password|passwd|secret|token|pwd)\b\s*[:=]\s*["']?(?!\$\{)[A-Za-z0-9_./+@-]{4,}` (FAIL); `INFO: java …`, `INFO: docker …` lines (never WARN).

### Serving contract test (CT-4)

`tests/test_srv_poi_serving_contract.py` builds three views per table: gold (`init_tables` `TABLE_SPECS` filtered to `lh_vv_gold.dbo.gld_srv_poi_*`, PK from NodeSpec via `ast`), PostgreSQL (`CREATE TABLE apps.<name> (...)` blocks parsed by regex, PK from `PRIMARY KEY (...)`), entity (`@Table(name=…)`, `@Column(name=…)`, `@Id`, Java field type). Assertions: column name sets equal across the three; gold type → PostgreSQL type by the map in `gld_srv_serve.pg.sql:4-12`; gold type → Java type (`STRING→String`, `BOOLEAN→Boolean`, `INT→Integer`, `BIGINT→Long`, `DOUBLE→Double`, `DECIMAL(p,s)→BigDecimal`, `TIMESTAMP→LocalDateTime`); PK tuple equal (order-insensitive for the entity). The test skips with a message when `services/data-serving-service` is absent, so it is safe before CT-3.

### Hooks (CT-6)

`scripts/hooks/git_guard.py --runtime cursor|claude` reads one JSON object from stdin, takes `command` (Cursor) or `tool_input.command` (Claude Code), splits on `&&`, `||`, `;`, `|`, newlines, and denies when any segment matches a deny regex. Cursor output: `{"permission": "deny", "userMessage": …, "agentMessage": …}` or `{"permission": "allow"}`; Claude Code: exit 2 with the reason on stderr, else exit 0. `scripts/hooks/task_state_guard.py` runs after a file edit; when the edited path matches `.ai/tasks/<id>/task-state.yaml` it runs `python scripts/vv.py validate <id>` and returns the first errors as `agentMessage`. Event names in `.cursor/hooks.json` (`beforeShellExecution`, `afterFileEdit`) are VERIFY-4.

## Observability

- `verify` log per CT in `verification/verify.log` (appended), with the `maven` lane label and the JDK/Docker precondition lines.
- `doctor` output pasted into `resume.md` "Done this session" for every CT (one line: `DOCTOR PASS`, `INFO` lines allowed).
- Runner prints `MODEL OVERRIDE <id>: <model> <effort>` or `MODEL default: <model> <effort>` before invoking a CLI; `task-state.yaml` `models.<role>.actual` holds the resolved model.
- Hook denials appear as `userMessage` in Cursor and as a Claude Code tool error; the guard also appends one line per denial to `.ai/.tmp/hooks.log` (ignored by git).
- Review round artifacts: `reviews/round-1.md` and `.json` from the single risk-gate round.

## Security and data handling

- `.env.example` is not copied (D-04); the variable names live in the nested `AGENTS.md` only.
- `docker-compose.yml` loses inline credentials; `${POSTGRES_USER:?set POSTGRES_USER in .env}` style makes `docker compose` fail loudly when unset. `application.yml` datasource keys lose inline defaults for username and password (URL default stays composable from host/port/dbname which carry no secret).
- `check-gaps.py:4` DEV host becomes `<host>`; `list-repos.sh` already reads the PAT from the environment and prints none.
- Fixtures and tests use synthetic names only; existing test strings are kept but no production extract is added. Runtime smoke uses the user's local compose database.
- MCP credential `VV_SERVING_PG_URL` is an OS environment variable; the repo file holds `${env:VV_SERVING_PG_URL}` only; `doctor` scans for literals.
- `.cursorindexingignore` excludes `services/*/target/`; nested `.gitignore` excludes `target/`, `.env*` (except `.env.example`, which does not exist in the repo).

## Rollout, rollback, and forward recovery

| CT | Rollback | Forward recovery |
|---|---|---|
| 1 | `git checkout -- scripts/agent_runner.py scripts/vv.py tests/test_vv.py .cursor/rules/00-main-orchestrator.mdc` (user) | re-run `materialize --write` and the anchor edits |
| 2 | revert the listed files; delete rule 40 and the three nested files | same |
| 3 | `git rm -r services/data-serving-service docs/poi-serving-api` (user); source repo untouched | re-copy from `20bca8a`, re-apply 3.2-3.4 |
| 4 | revert Java/test/pom edits; `V1__init_srv_poi_tables.sql` returns from the source repo if needed | re-apply 4.x in order |
| 5 | delete three tomls, restore `risk-gate.toml`, `REVIEWERS`, `cases.yaml`, WORKFLOW §7 | re-materialize |
| 6 | delete `.cursor/hooks.json`, `scripts/hooks/*`, restore `.claude/settings.json`, skill line, `vv.py` strings | re-materialize |
| 7 | restore `TOKEN_OPTIMIZATION_PLAN.md` from git, revert samples, delete the skill | re-materialize |
| 8 | delete `.cursor/mcp.json` | re-materialize |

All rollbacks are git operations by the user (push/merge/reset remain the user's). Fabric and PostgreSQL state are untouched by this task; `runtime-runbook.md` for CT-4 ends with `docker compose down -v`.

## Implementation plan

Per-CT classification for the ledger (the task itself stays one `task-state.yaml`; these drive `required_reviewers`, `risk_level`, and runtime flags at each phase):

| CT | Signals to keep set | `architecture_required` | `risk_level` while in CT | Reviewer | Runtime |
|---|---|---|---|---|---|
| 1 | `design_tradeoffs`, `cross_system` | true (this doc) | medium | none; user smoke | no |
| 2 | same | true | medium → `high` set at end of CT-3 | risk-gate (with CT-3) | no |
| 3 | same | true | high | risk-gate, round 1 | no |
| 4 | same | true | high | none (round 2 reserved for fixes) | yes: local compose (D-12), `runtime_required: true`, `gates.runtime: pending` until the user records PASS |
| 5 | same | true | high | none | no |
| 6 | same | true | high | none | no |
| 7 | same | true | high | none | no |
| 8 | same | true | high | none | no |

`scope.files` to add (Main writes; every `FILE:` path and every edited path):

```text
scripts/agent_runner.py
scripts/vv.py
tests/test_vv.py
tests/test_vv_context.py
tests/test_srv_poi_serving_contract.py
AGENTS.md
CLAUDE.md
.cursor/rules/00-main-orchestrator.mdc
.cursor/rules/20-data-pipeline.mdc
.cursor/rules/30-sql.mdc
.cursor/rules/40-java-api.mdc
.cursor/skills/vsvn-task-workflow/SKILL.md
.cursor/skills/vsvn-api-service/SKILL.md
.cursor/hooks.json
.cursor/mcp.json
.cursorindexingignore
.claude/settings.json
.codex/agents/api-contract-reviewer.toml
.codex/agents/app-security-reviewer.toml
.codex/agents/jpa-performance-reviewer.toml
.codex/agents/risk-gate.toml
.ai/evals/cases.yaml
scripts/hooks/git_guard.py
scripts/hooks/task_state_guard.py
docs/agent-system/WORKFLOW.md
docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md
docs/AGENT_PROMPT_SAMPLES.md
docs/context/00_README.md
docs/poi-serving-api/API-GAPS.md
docs/poi-serving-api/DESIGN-AND-PLAN.md
docs/poi-serving-api/FEED-SERVICE-GROUND-TRUTH.md
docs/poi-serving-api/HANDOFF.md
docs/poi-serving-api/scripts/check-gaps.py
docs/poi-serving-api/scripts/list-repos.sh
services/data-serving-service/AGENTS.md
services/data-serving-service/CLAUDE.md
services/data-serving-service/.gitignore
services/data-serving-service/src/test/resources/db/00_create_schema_apps.sql
services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/PoiMediaGalleryId.java
services/data-serving-service/<each of the 55 tracked source files, prefixed>  # generate: git -C D:\git\SunGrp_VSVN_API ls-files | grep -v '^docs/' | grep -v '^.env.example$'
```

`exceptions` entry template, used only if a CT is split into its own task (inside this task EX-03 already covers Main):

```yaml
- id: EX-03-CT<n>
  kind: model_override
  role: main
  model: claude-opus-5-5
  effort: medium
  runtime: cursor
  approved_by: user
  approved_on: '2026-11-06'
  scope: Main of CT-<n> under EX-03 of 20261106-agent-system-unify-api
```

Transfer rule on split: copy that CT's rows and `FILE:` blocks verbatim into the child `architecture.md` (keep the `RESULT:` line and a `## Main brief` with only that CT), list its paths in the child `scope.files`, and reference this document by path in the child `decision.md`.

### Code A: `agent_runner.py` lane resolution

```python
HONOR_EXCEPTIONS = False  # D-07: set True only after external-smoke passes with the override model


@dataclass(frozen=True)
class Lane:
    model: str
    effort: str
    source: str  # "default" or the exception id


LANE_DEFAULTS = {
    "architect": (ARCHITECT_MODEL, ARCHITECT_EFFORT),
    "review": (REVIEW_MODEL, REVIEW_EFFORT),
    "author": (AUTHOR_MODEL, AUTHOR_LANE_EFFORTS["author"]),
    "author_proposal": (AUTHOR_MODEL, AUTHOR_LANE_EFFORTS["author_proposal"]),
}


def resolve_lane(exceptions: Any, role: str, honor: bool | None = None) -> Lane:
    model, effort = LANE_DEFAULTS[role]
    if not (HONOR_EXCEPTIONS if honor is None else honor) or not isinstance(exceptions, list):
        return Lane(model, effort, "default")
    for item in exceptions:
        if not isinstance(item, dict) or item.get("kind") != "model_override":
            continue
        if item.get("role") != role or item.get("approved_by") != "user":
            continue
        candidate = item.get("model")
        candidate_effort = item.get("effort")
        if isinstance(candidate, str) and candidate.strip() and candidate_effort in {"low", "medium", "high"}:
            return Lane(candidate.strip(), candidate_effort, str(item.get("id", "exception")))
    return Lane(model, effort, "default")
```

`run_architecture(repo, prompt, timeout_seconds=1800, *, model=ARCHITECT_MODEL, effort=ARCHITECT_EFFORT)`; `run_author(repo, prompt, kind, timeout_seconds=1800, *, model=AUTHOR_MODEL, effort=None)` with `effort = effort or AUTHOR_EFFORTS[kind]`; `run_review(repo, prompt, required_reviewers, risk_gate_required, timeout_seconds=1800, *, model=REVIEW_MODEL, effort=REVIEW_EFFORT)`; `_review_schema(reviewers, model=REVIEW_MODEL, effort=REVIEW_EFFORT)`; the mismatch check at the end of `run_review` compares `payload["model"]`/`["reasoning_effort"]` with the arguments. In `vv.py`, `cmd_run_gate` computes `lane = agent_runner.resolve_lane(state.get("exceptions", []), "architect")` (or `"review"`), prints `MODEL {lane.source}: {lane.model} {lane.effort}`, passes `model=lane.model, effort=lane.effort`, and `architecture_state_after(state, verdict, model=lane.model)` / `review_state_after(state, result, round_number, model=lane.model)` set `actual`. `cmd_run_author` uses `key` (`author` or `author_proposal`) as the role. `_git_snapshot` returns `b"\0".join(e for e in raw.split(b"\0") if e and not e[3:].startswith(b".ai/.tmp/"))`.

### Code B: root `AGENTS.md` replacements

Line 22: `| User | Fabric DEV and Git | Runs probes and runbooks, accepts risk, pushes and merges; asks for a commit when one is wanted. |`

Line 66: `- Partner `poi_id = uuid_format(md5(concat(id, 'partner')))` 8-4-4-4-12 from `slv_pn_business_services.id` or `slv_pn_business_service_i18ns.business_service_id` (`uuid_md5(id, lit('partner'))`).`

Lines 67-69 become one line: `- Notebook roles and the `NB_SETUP_INITIAL_DDL` / `NB_CREATE_DDL` rule: `docs/context/02_NAMING_CONVENTION.md` §2–§2.1 and `.cursor/rules/10-fabric-notebook.mdc`. Pipeline FL_00 and pre-check contract: `.cursor/rules/20-data-pipeline.mdc` and §3 of the same convention.`

New line after the `CTRL_TABLES_CONTEXT.md` line: `- Serving API `services/data-serving-service/` reads only PostgreSQL `apps.srv_poi_*`, derived from `lh_vv_gold.dbo.gld_srv_poi_*`; gold DDL and NodeSpec `pk` are the contract. Its rules are in that directory's `AGENTS.md`. The repo DDL is `sql/postgres/gld_srv_serve.pg.sql`; the API ships no Flyway.`

Line 74: `- Agents never push, merge, rebase, amend, reset, or rewrite Git history. An agent commits only when the user's current turn asks for that commit.`

Measured candidate: 7,717 B (headroom 475 B). Rule 20 line 10 must be corrected to `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` in the same CT because the pipeline JSON uses that name and the root line that carried it is removed.

### Code C: `verify` maven lane

```python
SERVICE_DIR = Path("services/data-serving-service")


def _java_major() -> int | None:
    code, output = run(["java", "-version"])
    match = re.search(r'version "(\d+)', output)
    return int(match.group(1)) if code == 0 and match else None


def _docker_available() -> bool:
    return run(["docker", "info"])[0] == 0


def maven_lane(targets: list[str], allow_no_docker: bool) -> tuple[str, str, str]:
    if not targets:
        return ("maven", "SKIP", "no relevant files")
    major = _java_major()
    if major is None or major < 26:
        return ("maven", "FAIL", f"JDK 26 required for {SERVICE_DIR.as_posix()}; found {major or 'none'} (D-11)")
    wrapper = "mvnw.cmd" if os.name == "nt" else "./mvnw"
    command = [wrapper, "-q", "-B", "test"]
    label = "PASS"
    if not _docker_available():
        if not allow_no_docker:
            return ("maven", "FAIL", "Docker is not running; Testcontainers tests need it. Start Docker or pass --allow-no-docker for a diagnostic run.")
        command += ["-Dtest=!*IntegrationTest,!DataServingApplicationTests", "-Dsurefire.failIfNoSpecifiedTests=false"]
        label = "PASS (docker tests skipped: --allow-no-docker)"
    result = subprocess.run(command, cwd=SERVICE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    output = (result.stdout + result.stderr).strip().splitlines()
    return ("maven", label if result.returncode == 0 else "FAIL", "\n".join(output[-40:]))
```

In `cmd_verify`: `postgres_sql = [p for p in files if p.endswith(".pg.sql") or "/db/migration/" in p]`; `spark_sql = [p for p in files if p.endswith(".sql") and p not in postgres_sql]`; `java_targets = [p for p in files if p.startswith(SERVICE_DIR.as_posix() + "/")]`; `results.append(maven_lane(java_targets, args.allow_no_docker))` after the pytest lane; parser gains `--allow-no-docker`. `format_compact_verification` prints labels unchanged.

### Code D: `build_context` API block

```python
if "poi-serving-api" in state["scope"].get("systems", []):
    blocks.append(("API", "\n".join([
        f"service: {SERVICE_DIR.as_posix()} (rules: {SERVICE_DIR.as_posix()}/AGENTS.md)",
        "test: cd services/data-serving-service && mvnw.cmd -q -B test  (JDK 26, Docker)",
        f"jdk: {_java_major() or 'missing'} | docker: {'up' if _docker_available() else 'down'}",
        "runtime: user-run docker compose per runtime-runbook.md (D-12)",
    ])))
```

Insert before the `FILES` block.

### Code E: `doctor` additions

```python
for nested in Path("services").glob("*/AGENTS.md") if Path("services").is_dir() else []:
    if nested.stat().st_size > 4096:
        warnings.append(f"instruction budget exceeded: {nested.as_posix()} is {nested.stat().st_size} bytes (limit 4096)")
for ignore in Path("services").glob("*/.gitignore") if Path("services").is_dir() else []:
    if any(line.strip() == ".claude" for line in ignore.read_text(encoding="utf-8").splitlines()):
        errors.append(f"{ignore.as_posix()} must not ignore .claude")
if Path("services").is_dir():
    rule = Path(".cursor/rules/40-java-api.mdc")
    if not rule.is_file():
        errors.append("missing required file: .cursor/rules/40-java-api.mdc")
    elif re.search(r"(?m)^alwaysApply:\s*true\s*$", rule.read_text(encoding="utf-8")):
        errors.append(".cursor/rules/40-java-api.mdc must not be alwaysApply")
SECRET_RE = re.compile(r"(?i)\b(password|passwd|secret|token|pwd)\b\s*[:=]\s*[\"']?(?!\$\{)[A-Za-z0-9_./+@-]{4,}")
for candidate in [Path(".cursor/mcp.json"), Path(".mcp.json"), *Path("services").glob("*/docker-compose.yml"), *Path("services").glob("*/src/main/resources/application*.yml")]:
    if candidate.is_file():
        for number, line in enumerate(candidate.read_text(encoding="utf-8").splitlines(), start=1):
            if SECRET_RE.search(line):
                errors.append(f"literal secret in {candidate.as_posix()}:{number}")
print(f"INFO: java {_java_major() or 'missing'}; docker {'up' if _docker_available() else 'down'}")
```

### Code F: compose and `application.yml` credential handling (CT-3)

`docker-compose.yml` `postgres.environment`: `POSTGRES_USER: ${POSTGRES_USER:?set POSTGRES_USER in .env}`, `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}`; healthcheck `pg_isready -U ${POSTGRES_USER} -d vv_data_serving`. `data-serving-service.environment`: `POSTGRES__DP_POI__URL: jdbc:postgresql://postgres:5432/vv_data_serving?currentSchema=apps`, `POSTGRES__DP_POI__USERNAME: ${POSTGRES_USER:?}`, `POSTGRES__DP_POI__PASSWORD: ${POSTGRES_PASSWORD:?}`. `application.yml`: `username: ${POSTGRES__DP_POI__USERNAME}`, `password: ${POSTGRES__DP_POI__PASSWORD}` (no inline default); `url` keeps its env-first form with a non-secret default built from `POSTGRES__DP_POI__HOST/PORT/DBNAME`. Main reads the current lines in the copy and edits only the three credential keys and the healthcheck.

### Code G: Maven test resources and Testcontainers init (CT-4)

`pom.xml` `<build>` gains, before `<plugins>`:

```xml
<testResources>
    <testResource>
        <directory>src/test/resources</directory>
    </testResource>
    <testResource>
        <directory>${project.basedir}/../../sql/postgres</directory>
        <includes>
            <include>gld_srv_serve.pg.sql</include>
        </includes>
    </testResource>
</testResources>
```

Remove the `spring-boot-starter-flyway` and `flyway-database-postgresql` dependencies. `TestcontainersConfiguration.postgresContainer()`:

```java
return new PostgreSQLContainer(DockerImageName.parse("postgres:18-alpine").asCompatibleSubstituteFor("postgres"))
        .withCopyFileToContainer(MountableFile.forClasspathResource("db/00_create_schema_apps.sql"),
                "/docker-entrypoint-initdb.d/00_create_schema_apps.sql")
        .withCopyFileToContainer(MountableFile.forClasspathResource("gld_srv_serve.pg.sql"),
                "/docker-entrypoint-initdb.d/10_gld_srv_serve.sql");
```

Import `org.testcontainers.utility.MountableFile`. The PostgreSQL image runs `/docker-entrypoint-initdb.d/*.sql` in name order on first start, so the schema exists before the DDL's `BEGIN; CREATE TABLE apps.…`. Both `application.yml` files drop the `spring.flyway` block; `src/test/resources/application.yml` keeps `spring.jpa.hibernate.ddl-auto: none` and `default_schema: apps`.

### Code H: WORKFLOW §7 routing lines (CT-5)

- `api-contract-reviewer`: HTTP contract of `services/data-serving-service` (paths, DTO fields and JSON names, error envelope, paging, `lang` resolution, OpenAPI annotations) against the entities and the gold contract (`tests/test_srv_poi_serving_contract.py`). Route when the diff touches `api/`, `dto/`, `domain/entity/`, `OpenApiConfig`, or `sql/postgres/gld_srv_serve.pg.sql`.
- `app-security-reviewer`: input validation, dynamic JPQL/Specification construction, actuator exposure, request-id handling, personal data in logs or responses, configuration and dependency secrets. Route when the diff touches `common/web/`, `config/`, `application*.yml`, `pom.xml`, `Dockerfile`, or `docker-compose.yml`.
- `jpa-performance-reviewer`: N+1 and fetch plans, mandatory pagination, index coverage of Specifications, read-only transactions, Hikari pool settings, batch settings. Route when the diff touches `domain/repository/`, `service/`, entities, or DDL indexes.
- `risk-gate` scope sentence gains "and the PostgreSQL serving API (`services/data-serving-service`)".

## Verification strategy

Acceptance per CT (all require `verify` PASS, `doctor` no WARN, `AGENTS.md` ≤ 8,192 B):

| CT | Acceptance |
|---|---|
| 1 | new tests green; `external-smoke --architect-model claude-fable-5-1` result recorded in ledger as D-07 branch A or B; `HONOR_EXCEPTIONS` matches the branch |
| 2 | rule 40 attaches on a `.java` file and shows the nested rules (VERIFY-1); Codex `exec` lists the nested `AGENTS.md` (VERIFY-2) or fallback applied; `verify` routes a `db/migration/x.sql` fixture to postgres (unit test) |
| 3 | 55 + 6 files present; `grep -r "azure.com" docs/poi-serving-api services/` empty; `mvnw.cmd -q -B test` green with Docker; risk-gate round 1 PASS or findings dispositioned |
| 4 | `pytest tests/test_srv_poi_serving_contract.py` green; `mvnw.cmd -q -B test` green; no `flyway` string in `pom.xml` or `application*.yml`; `V1__init_srv_poi_tables.sql` absent; user runbook result recorded (`gates.runtime: pass`) |
| 5 | three tomls parse and are pinned; `REVIEWERS` has 7 names; WORKFLOW §7 has the three lines; `cases.yaml` has 12 cases |
| 6 | Cursor denies `git push --dry-run`, allows `git status`; Claude Code `PreToolUse` denies the same; `.claude/settings.json` has no `git add`/`git commit` deny; all D-05 locations edited (`grep -rn "never commits\|Only the user commits\|do not commit\|Dừng trước commit" AGENTS.md CLAUDE.md .cursor docs scripts` empty) |
| 7 | `TOKEN_OPTIMIZATION_PLAN.md` absent; samples ≤ 25,600 B with A20 present; skill ≤ 20,480 B |
| 8 | `.cursor/mcp.json` parses, contains `${env:VV_SERVING_PG_URL}` and no literal; `SELECT 1` works through the tool (user) |

Unit tests to add (names are binding): CT-1 `test_resolve_lane_defaults_when_flag_off`, `test_resolve_lane_prefers_user_approved_exception`, `test_review_schema_uses_resolved_model`, `test_repo_snapshot_ignores_ai_tmp`, `test_run_gate_timeout_default_2700`; CT-2 `test_verify_routes_migration_sql_to_postgres_lane`, `test_verify_maven_lane_requires_docker`, `test_verify_maven_lane_allow_no_docker_marks_log`, `test_context_api_block_for_poi_serving_api`, `test_doctor_nested_agents_budget`, `test_doctor_rejects_literal_secret`; CT-6 `test_git_guard_denies_push_reset_rebase_amend_recursive_delete`, `test_git_guard_allows_commit_and_status`, `test_closeout_commit_request_wording`. Existing tests that must change: `test_review_schema_uses_supported_reviewer_array_keywords` (call with default model), `test_build_closeout_*` (new commit wording), `test_architecture_pass_advances_to_implementation` (default model path unchanged).

Runtime proof (CT-4, D-12): `runtime-runbook.md` written by `run-author --kind runbook` from a ≤ 60-line `handoffs/author-input.md` that names: `docker compose up -d postgres` with `.env` holding `POSTGRES_USER`/`POSTGRES_PASSWORD`; `psql -v ON_ERROR_STOP=1 -c "CREATE SCHEMA IF NOT EXISTS apps"` then `-f sql/postgres/gld_srv_serve.pg.sql`; optional synthetic rows (≤ 50 per table, no personal data) inserted by the user from the runbook; `docker compose up -d data-serving-service`; `curl http://localhost:8080/actuator/health`, `curl "http://localhost:8080/api/v1/pois/compact?size=5"`, one call each to `/gallery`, `/reviews`, `/amenities` for a seeded `poi_id`; log check for `email`/`phone`/`author_name`; `docker compose down -v`. Expected: health `UP`; 200 with empty or seeded data; 404 for an unknown `poi_id`.

## Evidence needed

None blocking. Pre-check run by this session (read-only, 2026-11-06): the `tests/test_srv_poi_serving_contract.py` logic executed against the repo notebooks and `sql/postgres/gld_srv_serve.pg.sql` passes `test_gold_and_pg_columns_and_types_match` today (5 tables; 32/12/11/16/13 columns; PKs equal), and against the read-only source entities it reports exactly two differences: `srv_poi_media_gallery` entity PK `(media_id,)` vs gold `(media_id, poi_id)` (D-09) and `srv_poi_review` extra column `source_name` (D-10). No other column, type, or key drift exists, so CT-4 rows 4.7-4.12 are sufficient for the entity test to pass. Checks inside child tasks (no assumption is made before them): VERIFY-1 Cursor `@file` in rules; VERIFY-2 Codex nested `AGENTS.md`; VERIFY-3 Claude Code nested `CLAUDE.md` loading (interactive sessions only; runner uses `--setting-sources user` and reads the prompt); VERIFY-4 Cursor hook event names and JSON shape; VERIFY-5 Codex hook support; VERIFY-6 `postgres-mcp` package and `--access-mode=restricted`; ME-01 Claude CLI accepts `--model claude-fable-5-1` (CT-1 smoke); ME-04 `mvnw.cmd test` duration (CT-3). ME-06 (how the evaluation suite is run) stays open and does not block: no model changes in this task. ME-07 moot under D-04. ME-08 does not affect any file here.

## File blocks

Save with `python scripts/vv.py materialize 20261106-agent-system-unify-api --write` after every path below is in `scope.files`. Blocks are grouped by child task; a block is materialized in the CT that lists it.

### CT-1 and CT-2 blocks

FILE: .cursor/rules/00-main-orchestrator.mdc
---
description: Operating protocol for the VSVN Main agent
alwaysApply: true
---

You are Main: the sole source-code writer and the owner of task state. `AGENTS.md` is already in context; do not re-read it.

## Context budget

- The first command of every task turn is `python scripts/vv.py context <task-id>`. Read nothing else before it.
- Then read only what the prompt or the context pack names. For files over 20 KB, use `python scripts/vv.py toc <file>` and `python scripts/vv.py show <file> <anchor>`.
- Read the full `architecture.md` only at an anchor its `Main brief` points to, or when the brief is missing.
- Read `decision.md` through `Quyết định hiện hành`. Open its history only for a named decision.
- Do not open other tasks, `notebooks_lgc/`, `evidence/context/`, `docs/context/3p-google/*.txt`, `pipelines/*/manifest.json`, or `docs/poi-serving-api/` unless the prompt names them. Never copy context files into a task.
- Save file blocks with `python scripts/vv.py materialize <task-id> --write`; never retype them.
- `python scripts/vv.py verify <task-id>` output is compact. Open `verification/verify.log` or `--full` only for a FAIL.
- Work under `services/` follows that directory's `AGENTS.md` (loaded by rule `40-java-api`).

## Workflow

- New task: `python scripts/vv.py new <slug>`. Classify with `docs/agent-system/WORKFLOW.md` (§Classification, §Review routing).
- Record the actual Main model. Stop if it is not Grok 4.7 Medium, unless an approved `exceptions` entry covers it.
- At `waiting_architecture` or `reviewing`, run `python scripts/vv.py run-gate <task-id>`. The review lane is Codex only.
- `python scripts/vv.py transition` validates before and after the change; call `validate` only to diagnose an edit you made by hand.
- Implement only after the required evidence and architecture gates pass. Record any deviation in `decision.md` before coding.
- Never invent data properties. Write the smallest probe.
- Verify before review and after each P0/P1 fix. Never mark a gate `pass` while evidence is missing or a P0/P1 is open.
- Only the user pushes, merges, accepts risk, and confirms runtime results. Commit only when the user's current turn asks for it; otherwise list the changed files as a `commit` request.

## Stop

Stop for: a Fabric DEV probe or runbook; a local `docker compose` runtime step; a gate, CLI, or model failure or fallback; a round cap; or a choice that changes scope. Before stopping, overwrite `.ai/tasks/<task-id>/resume.md` (≤ 40 lines) and tell the user to open a new chat for the next phase.

## Turn closeout

End every task turn with four Vietnamese sections, in this order, with these exact headings: `Đã làm`, `Bạn cần chạy`, `Agent đang chờ`, `Kết thúc`. Generate the skeleton with `python scripts/vv.py closeout <task-id>` and edit only the summary lines. Full rules: skill `vsvn-task-workflow`, section `Build the closeout`. Never claim that a Fabric DEV step or a `docker compose` step ran.
END_FILE

FILE: .cursor/rules/40-java-api.mdc
---
description: VSVN POI serving API (Spring Boot, JPA, PostgreSQL apps schema) implementation rules
globs: services/**/*.java, services/**/pom.xml, services/**/application*.yml, services/**/Dockerfile, services/**/docker-compose.yml, services/**/db/migration/*.sql, services/**/src/test/resources/**
alwaysApply: false
---

Read the service constitution first; it is the single source for these rules and is shared with Codex and Claude Code:

@services/data-serving-service/AGENTS.md

Then:

- Change a column, key, or table only through a data task (`data_model_change`, `run-author --kind model`); the API follows gold, never the reverse.
- Run `cd services/data-serving-service && mvnw.cmd -q -B test` (Docker running) before `python scripts/vv.py verify <task-id>`; `verify` repeats it in the `maven` lane.
- Keep `tests/test_srv_poi_serving_contract.py` green; it compares gold DDL, `sql/postgres/gld_srv_serve.pg.sql`, and the entities.
- Route review by path: `api/`, `dto/`, entities → `api-contract-reviewer`; `common/web/`, `config/`, `application*.yml`, `pom.xml`, Docker files → `app-security-reviewer`; `domain/repository/`, `service/` → `jpa-performance-reviewer`.
END_FILE

FILE: services/data-serving-service/AGENTS.md
# data-serving-service

Spring Boot read-only API over PostgreSQL schema `apps` (`srv_poi_info`, `srv_poi_multi_lang`, `srv_poi_amenity`, `srv_poi_media_gallery`, `srv_poi_review`). Root `AGENTS.md` applies first; this file adds the API rules. Stack: Java 26, Spring Boot 4.1.x (`pom.xml`), Spring Data JPA, springdoc, Testcontainers. Imported from ADO repo `data-serving-service` commit `20bca8a` on 2026-11-06.

## Contract

- Columns and types come from gold `lh_vv_gold.dbo.gld_srv_poi_*` (`notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`); primary keys come from NodeSpec `pk` in `notebooks/NB_GLD_SRV_POI_*.ipynb`. `sql/postgres/gld_srv_serve.pg.sql` is the PostgreSQL DDL derived from them. Entities and DTOs expose only columns that exist there. `tests/test_srv_poi_serving_contract.py` enforces this.
- Keys: `srv_poi_info(poi_id)`, `srv_poi_multi_lang(poi_id, lang)`, `srv_poi_amenity(poi_id, business_sector, amenity_group, amenity_raw)`, `srv_poi_media_gallery(media_id, poi_id)`, `srv_poi_review(review_id)`. Composite keys use `@IdClass`.
- `poi_id` never includes language. `srv_poi_review` has no `source_name`, `source`, or `lang` (D-10 of task `20261106-agent-system-unify-api`).
- Read-only: no writes, `spring.jpa.hibernate.ddl-auto: none`, no Flyway, no DDL at runtime. The schema and tables are created by the data side with the repo DDL.
- Query schema `apps` only. Never join to `public`, `poi_mgmt`, `destination_mgmt`, or `admin_ref`.
- Every list endpoint is paginated (`size` ≤ 100). Filters go through `PoiSpecifications`; never concatenate request values into JPQL.
- Responses use `ApiResponse` / `PageResponse`; errors go through `GlobalExceptionHandler`; `lang` resolves through `LanguageResolver`.
- Do not log or return `email`, `phone`, or `author_name` beyond the fields a DTO already exposes. Test fixtures are synthetic.

## Layout

`src/main/java/vn/visitvietnam/dataserving/`: `api/` + `api/dto/`; `service/` + `service/util/`; `domain/entity/` + `domain/repository/`; `common/` envelope, exceptions, filters; `config/`. Tests mirror the tree. `@WebMvcTest` needs no Docker; `@SpringBootTest` uses `TestcontainersConfiguration` (`postgres:18-alpine`, init scripts `db/00_create_schema_apps.sql` then `gld_srv_serve.pg.sql` from `../../sql/postgres` via Maven test resources).

## Commands

- Tests: `mvnw.cmd -q -B test` (POSIX `./mvnw -q -B test`). Needs JDK 26 and a running Docker daemon.
- Package: `mvnw.cmd -q -B package`. Image: `docker build -t data-serving-service .`
- Local run: create `.env` next to `docker-compose.yml` with `POSTGRES_USER` and `POSTGRES_PASSWORD` (never commit it), then `docker compose up -d`. Service on `8080`, PostgreSQL on `${POSTGRES_PORT:-55432}`. Apply the DDL once: `psql -c "CREATE SCHEMA IF NOT EXISTS apps"` then `psql -v ON_ERROR_STOP=1 -f ../../sql/postgres/gld_srv_serve.pg.sql`.
- Health: `GET /actuator/health`. OpenAPI: `/v3/api-docs`, `/swagger-ui.html`.

## Environment variables

`POSTGRES__DP_POI__URL`, `POSTGRES__DP_POI__HOST`, `POSTGRES__DP_POI__PORT`, `POSTGRES__DP_POI__DBNAME`, `POSTGRES__DP_POI__SSLMODE`, `POSTGRES__DP_POI__USERNAME`, `POSTGRES__DP_POI__PASSWORD`, `HIKARI_MAX_POOL_SIZE`, `HIKARI_MIN_IDLE`, `SERVER_PORT`, `LOG_LEVEL`. Compose: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`. Values live only in the environment or an ignored `.env`; never in the repository, never in a prompt or task artifact.

## Local database for agents

The Cursor MCP server `vv-serving-postgres-local` (`.cursor/mcp.json`) is read-only and reads `VV_SERVING_PG_URL` from the OS environment. Point it at the compose database only. A DEV or production database needs the user's explicit approval for that run, as for Fabric probes.

## Review and verification

`vv.py verify` runs the `maven` lane for changes here and fails without JDK 26 or Docker. Reviewers: `api-contract-reviewer`, `app-security-reviewer`, `jpa-performance-reviewer` (WORKFLOW §7). Runtime proof: user-run `docker compose` smoke in `runtime-runbook.md`.
END_FILE

FILE: services/data-serving-service/CLAUDE.md
@AGENTS.md
END_FILE

FILE: services/data-serving-service/.gitignore
# Maven
target/
.mvn/wrapper/maven-wrapper.jar

# Local environment files: never commit credentials
.env
.env.local
.env.*.local

# IDE
.idea/
*.iml
.vscode/
.settings/
.project
.classpath
END_FILE

### CT-4 blocks

FILE: services/data-serving-service/src/test/resources/db/00_create_schema_apps.sql
-- Chạy trước gld_srv_serve.pg.sql trong container test (docker-entrypoint-initdb.d, thứ tự theo tên file).
-- Schema apps do phía dữ liệu sở hữu; file DDL của repo không tạo schema nên test tạo ở đây.
CREATE SCHEMA IF NOT EXISTS apps;
END_FILE

FILE: services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/PoiMediaGalleryId.java
package vn.visitvietnam.dataserving.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * Composite Primary Key for {@link SrvPoiMediaGallery}.
 * Maps compound key (media_id, poi_id), the NodeSpec pk of gld_srv_poi_media_gallery.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PoiMediaGalleryId implements Serializable {

    private String mediaId;
    private String poiId;
}
END_FILE

FILE: tests/test_srv_poi_serving_contract.py
"""Serving contract: gold DDL + NodeSpec pk == PostgreSQL DDL == JPA entities. No Spark, no JDK, no Docker."""
import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "services" / "data-serving-service"
ENTITY_DIR = SERVICE / "src" / "main" / "java" / "vn" / "visitvietnam" / "dataserving" / "domain" / "entity"
PG_DDL = ROOT / "sql" / "postgres" / "gld_srv_serve.pg.sql"
GOLD_PREFIX = "lh_vv_gold.dbo.gld_"
BUILD_CELLS = {
    "srv_poi_info": ("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"),
    "srv_poi_multi_lang": ("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"),
    "srv_poi_amenity": ("NB_GLD_SRV_POI_AMENITY.ipynb", "srvamenitybuild"),
    "srv_poi_media_gallery": ("NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb", "srvgallerybuild"),
    "srv_poi_review": ("NB_GLD_SRV_POI_REVIEW.ipynb", "srvrvbuild"),
}
# Ánh xạ kiểu Fabric -> PostgreSQL theo đầu file gld_srv_serve.pg.sql (decision D-TYPE, D-BIGINT).
GOLD_TO_PG = {
    "STRING": "text", "BOOLEAN": "boolean", "INT": "integer", "BIGINT": "int8",
    "DOUBLE": "double precision", "TIMESTAMP": "timestamp without time zone",
}
GOLD_TO_JAVA = {
    "STRING": "String", "BOOLEAN": "Boolean", "INT": "Integer", "BIGINT": "Long",
    "DOUBLE": "Double", "TIMESTAMP": "LocalDateTime",
}


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell_source(name: str, cell_id: str) -> str:
    found = [cell for cell in _notebook(name)["cells"] if cell.get("id") == cell_id]
    assert len(found) == 1, f"{name}: cell {cell_id}"
    return "".join(found[0]["source"])


def _normalize_gold_type(value: str) -> str:
    base = value.upper().replace(" NOT NULL", "").strip()
    return base


def gold_tables() -> dict[str, dict]:
    namespace: dict = {}
    exec(_cell_source("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), namespace)  # noqa: S102 - pure table spec cell
    tables: dict[str, dict] = {}
    for spec in namespace["TABLE_SPECS"]:
        fq = spec["fq"]
        if not fq.startswith(GOLD_PREFIX + "srv_poi_"):
            continue
        name = fq[len(GOLD_PREFIX):]
        cols = {col[0]: _normalize_gold_type(col[1]) for col in spec["cols"]}
        notebook, cell_id = BUILD_CELLS[name]
        tree = ast.parse(_cell_source(notebook, cell_id))
        spec_call = next(
            node.value for node in ast.walk(tree)
            if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SPEC" for t in node.targets)
        )
        kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in spec_call.keywords if kw.arg != "build"}
        tables[name] = {"cols": cols, "pk": tuple(kwargs["pk"])}
    assert set(tables) == set(BUILD_CELLS)
    return tables


def pg_tables() -> dict[str, dict]:
    text = PG_DDL.read_text(encoding="utf-8")
    tables: dict[str, dict] = {}
    for match in re.finditer(r"CREATE TABLE apps\.(\w+) \((.*?)\n\);", text, re.S):
        name, body = match.group(1), match.group(2)
        cols: dict[str, str] = {}
        pk: tuple[str, ...] = ()
        for raw in body.split("\n"):
            line = raw.strip().rstrip(",")
            if not line:
                continue
            if line.upper().startswith("PRIMARY KEY"):
                pk = tuple(item.strip() for item in line[line.index("(") + 1:line.rindex(")")].split(","))
                continue
            col, rest = line.split(" ", 1)
            cols[col] = rest.replace(" NOT NULL", "").strip()
        tables[name] = {"cols": cols, "pk": pk}
    return tables


def entity_tables() -> dict[str, dict]:
    tables: dict[str, dict] = {}
    for path in sorted(ENTITY_DIR.glob("Srv*.java")):
        text = path.read_text(encoding="utf-8")
        table = re.search(r'@Table\(name = "(\w+)", schema = "apps"\)', text)
        assert table, f"{path.name}: @Table(name=..., schema=\"apps\") required"
        cols: dict[str, str] = {}
        pk: list[str] = []
        pending_id = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "@Id":
                pending_id = True
                continue
            column = re.match(r'@Column\(name = "(\w+)"', stripped)
            if column:
                current = column.group(1)
                cols[current] = ""
                if pending_id:
                    pk.append(current)
                    pending_id = False
                continue
            field = re.match(r"private (\w+) (\w+);", stripped)
            if field and cols and not cols[current]:
                cols[current] = field.group(1)
        tables[table.group(1)] = {"cols": cols, "pk": tuple(pk), "id_class": "@IdClass(" in text}
    return tables


def _require_service() -> None:
    if not SERVICE.is_dir():
        pytest.skip("services/data-serving-service not imported yet (CT-3)")


def test_gold_and_pg_columns_and_types_match():
    gold, pg = gold_tables(), pg_tables()
    assert set(gold) == set(pg)
    for name, spec in gold.items():
        assert set(spec["cols"]) == set(pg[name]["cols"]), name
        for col, gold_type in spec["cols"].items():
            expected = GOLD_TO_PG.get(gold_type)
            if expected is None:
                decimal = re.fullmatch(r"DECIMAL\((\d+),(\d+)\)", gold_type)
                assert decimal, f"{name}.{col}: unmapped gold type {gold_type}"
                expected = f"numeric({decimal.group(1)}, {decimal.group(2)})"
            assert pg[name]["cols"][col] == expected, f"{name}.{col}: {pg[name]['cols'][col]} != {expected}"
        assert pg[name]["pk"] == spec["pk"], f"{name}: pk {pg[name]['pk']} != NodeSpec {spec['pk']}"


def test_entities_match_gold_columns_types_and_keys():
    _require_service()
    gold, entities = gold_tables(), entity_tables()
    assert set(gold) == set(entities)
    for name, spec in gold.items():
        entity = entities[name]
        assert set(entity["cols"]) == set(spec["cols"]), f"{name}: entity columns differ from gold"
        for col, gold_type in spec["cols"].items():
            expected = GOLD_TO_JAVA.get(gold_type, "BigDecimal" if gold_type.startswith("DECIMAL(") else None)
            assert entity["cols"][col] == expected, f"{name}.{col}: {entity['cols'][col]} != {expected}"
        assert set(entity["pk"]) == set(spec["pk"]), f"{name}: @Id columns {entity['pk']} != {spec['pk']}"
        assert entity["id_class"] == (len(spec["pk"]) > 1), f"{name}: @IdClass must match composite pk"


def test_review_entity_has_no_source_or_lang():
    _require_service()
    text = (ENTITY_DIR / "SrvPoiReview.java").read_text(encoding="utf-8")
    assert "source_name" not in text and '"lang"' not in text and '"source"' not in text


def test_no_flyway_in_service():
    _require_service()
    assert not list(SERVICE.rglob("db/migration"))
    assert "flyway" not in (SERVICE / "pom.xml").read_text(encoding="utf-8").lower()
    for yml in SERVICE.rglob("application*.yml"):
        assert "flyway" not in yml.read_text(encoding="utf-8").lower(), yml
END_FILE

### CT-5 blocks

FILE: .codex/agents/api-contract-reviewer.toml
name = "api-contract-reviewer"
description = "Reviews the HTTP contract of services/data-serving-service: endpoints, DTO fields and JSON names, error envelope, paging, language resolution, OpenAPI, and DTO-to-entity-to-gold column alignment."
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
approval_policy = "never"
developer_instructions = """
You are a read-only VSVN specialist for the POI serving API. Never edit files or run builds. Review only the diff and the contract invariants it touches. Return P0/P1 rows only. Count P2/P3; do not write them up.

Read services/data-serving-service/AGENTS.md first. The contract is gold: columns come from notebooks/NB_SETUP_INITIAL_DDL.ipynb cell init_tables, keys from NodeSpec pk; sql/postgres/gld_srv_serve.pg.sql is the PostgreSQL DDL. Check that every entity field, DTO field, and JSON property maps to an existing gold column or is a documented derived value; that srv_poi_review exposes no source_name, source, or lang; that composite keys use @IdClass matching the pk; that list endpoints are paginated with size <= 100; that error responses use the shared envelope; that lang resolves through LanguageResolver; that OpenAPI annotations match the actual parameters and codes; and that a response shape change is backward compatible or explicitly versioned.

Do not infer data distribution or coverage. When correctness depends on real data, return EVIDENCE_REQUIRED with a minimal read-only SQL probe against the local compose database and a pass/fail criterion.

Return `VERDICT: PASS | FIX_REQUIRED | EVIDENCE_REQUIRED | USER_DECISION`, followed by a findings table with IDs API-001..., impact-based severity P0-P3, file:line evidence, violated contract rule, concrete request and response example, and fix direction. Report only actionable findings.
"""
END_FILE

FILE: .codex/agents/app-security-reviewer.toml
name = "app-security-reviewer"
description = "Reviews application security of services/data-serving-service: input validation, dynamic JPQL and Specifications, actuator exposure, request-id handling, personal data in logs and responses, configuration and dependency secrets, container hardening."
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
approval_policy = "never"
developer_instructions = """
You are a read-only VSVN security specialist for the POI serving API. Never edit files, never run the service, never fetch dependencies. Review only the diff and the security invariants it touches. Return P0/P1 rows only. Count P2/P3; do not write them up.

Read services/data-serving-service/AGENTS.md first. Check: request parameters validated and bounded; no request value concatenated into JPQL, SQL, or Specification strings; actuator endpoints exposed only as configured and health details not leaking datasource facts; request-id and correlation handling cannot inject log lines; email, phone, author_name, and other personal data never logged and only returned by the DTOs that already expose them; no credential, token, host, or production extract in application*.yml, docker-compose.yml, Dockerfile, test resources, or documentation; environment variables read without insecure defaults; the image runs as non-root; dependency additions are justified.

Do not assume deployment topology or authentication that the repository does not show. When a conclusion depends on it, return USER_DECISION with the exact question.

Return `VERDICT: PASS | FIX_REQUIRED | EVIDENCE_REQUIRED | USER_DECISION`, followed by a findings table with IDs SEC-001..., impact-based severity P0-P3, file:line evidence, attack or leak scenario, and fix direction. Report only actionable findings.
"""
END_FILE

FILE: .codex/agents/jpa-performance-reviewer.toml
name = "jpa-performance-reviewer"
description = "Reviews JPA and PostgreSQL access patterns of services/data-serving-service: N+1, fetch plans, mandatory pagination, index coverage of Specifications, read-only transactions, Hikari pool and batch settings."
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
approval_policy = "never"
developer_instructions = """
You are a read-only VSVN performance specialist for the POI serving API. Never edit files or run queries. Review only the diff and the access-path invariants it touches. Return P0/P1 rows only. Count P2/P3; do not write them up.

Read services/data-serving-service/AGENTS.md first. Check: every repository call that serves a list is paginated or bounded by an IN list of at most 100 ids; child tables (multi_lang, media_gallery, amenity, review) are fetched in batch per request, not per POI; Specifications filter on columns that the PostgreSQL DDL or a documented index can serve; transactions are read-only; open-in-view stays false; Hikari pool, batch size, and ordering settings are not loosened without a stated reason; sorting is whitelisted; no unbounded findAll.

Do not infer table sizes or selectivity. When a conclusion depends on them, return EVIDENCE_REQUIRED with a minimal read-only EXPLAIN or COUNT probe against the local compose database and a pass/fail criterion.

Return `VERDICT: PASS | FIX_REQUIRED | EVIDENCE_REQUIRED | USER_DECISION`, followed by a findings table with IDs JPA-001..., impact-based severity P0-P3, file:line evidence, query shape or cost scenario, and fix direction. Report only actionable findings.
"""
END_FILE

FILE: .codex/agents/risk-gate.toml
name = "risk-gate"
description = "Final independent gate for high-impact stateful, orchestration, or cross-system changes after specialist review."
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
approval_policy = "never"
developer_instructions = """
You are the read-only final risk gate. Never edit files. Read the specialist P0/P1 findings and the implementation diff. Do not re-read the repository. Verify a claim in source only when a finding depends on it.

Focus on end-to-end invariants across Event Hub, Eventstream, Lakehouses, Spark notebooks, Fabric pipelines, control tables, PostgreSQL sync, and the PostgreSQL serving API (services/data-serving-service). Test transaction boundaries, commit order, replay, duplicate delivery, concurrent execution, retries, partial failure, rollback, forward recovery, observability, and low-probability high-impact scenarios. For agent-system changes, test that model policy, gate ordering, repository immutability, secret handling, and commit authority still hold. Identify disagreements between architecture, code, evidence, and specialist findings.

Do not re-list low-value style issues. Do not approve missing evidence. Route unresolved architectural ambiguity, accepted P0/P1 risk, exceeded round caps, or non-local correctness uncertainty to USER_DECISION.

Return `VERDICT: PASS | FIX_REQUIRED | EVIDENCE_REQUIRED | USER_DECISION`, followed by a findings table with IDs GATE-001..., impact-based severity P0-P3, evidence, end-to-end failure timeline, affected systems, and required resolution. End with residual risks and the exact conditions required to pass.
"""
END_FILE

FILE: .ai/evals/cases.yaml
schema_version: 1
cases:
  - id: merge-watermark-crash-window
    summary: Business MERGE succeeds, process crashes before watermark update, and the pipeline retries.
    expected_reviewers: [state-correctness-reviewer, sql-data-reviewer]
    expected_risk_gate: true
    required_topics: [idempotency, transaction_boundaries, retry_recovery, watermark]
  - id: concurrent-control-state-writers
    summary: Two table workers MERGE into a shared control table without an ownership key in the predicate.
    expected_reviewers: [state-correctness-reviewer, spark-runtime-reviewer]
    expected_risk_gate: true
    required_topics: [concurrency, cross_state_impact, partial_failure]
  - id: nondeterministic-dedup
    summary: A row_number dedup window orders only by a timestamp that can tie.
    expected_reviewers: [state-correctness-reviewer, sql-data-reviewer]
    expected_risk_gate: true
    required_topics: [event_ordering, idempotency]
  - id: foreach-partial-failure
    summary: A Fabric ForEach runs four notebooks concurrently and reports success when one child fails.
    expected_reviewers: [fabric-pipeline-reviewer, state-correctness-reviewer]
    expected_risk_gate: true
    required_topics: [partial_failure, failure_propagation, concurrency]
  - id: malformed-notebook-exit
    summary: Pipeline expressions assume every notebook returns valid JSON with a status field.
    expected_reviewers: [fabric-pipeline-reviewer, spark-runtime-reviewer]
    expected_risk_gate: false
    required_topics: [notebook_contract, retry_recovery]
  - id: join-cardinality-unknown
    summary: A new enrichment join assumes one row per entity, but no uniqueness evidence exists.
    expected_reviewers: [sql-data-reviewer]
    expected_risk_gate: false
    expected_verdict: EVIDENCE_REQUIRED
    required_topics: [grain, data_evidence_required]
  - id: unbounded-driver-collection
    summary: A notebook calls collect on an input with unknown production volume.
    expected_reviewers: [spark-runtime-reviewer]
    expected_risk_gate: false
    required_topics: [driver_memory, runtime_proof_required]
  - id: comment-only-fast-lane
    summary: A Vietnamese explanatory comment is corrected in one notebook without changing behavior.
    expected_reviewers: []
    expected_risk_gate: false
    required_topics: [fast_lane]
  - id: api-dto-exposes-missing-gold-column
    summary: A review DTO adds a source field that no gold or PostgreSQL column provides.
    expected_reviewers: [api-contract-reviewer]
    expected_risk_gate: false
    expected_verdict: FIX_REQUIRED
    required_topics: [contract, gold_alignment]
  - id: api-specification-string-concat
    summary: A sort parameter is concatenated into a JPQL order clause and the list endpoint has no page size cap.
    expected_reviewers: [app-security-reviewer, api-contract-reviewer]
    expected_risk_gate: false
    expected_verdict: FIX_REQUIRED
    required_topics: [injection, pagination]
  - id: api-gallery-n-plus-one
    summary: Compact POI listing loads media per POI inside a loop instead of one batched query.
    expected_reviewers: [jpa-performance-reviewer]
    expected_risk_gate: false
    expected_verdict: FIX_REQUIRED
    required_topics: [n_plus_one, batch_fetch]
  - id: api-key-change-without-runbook
    summary: An entity switches to a composite @IdClass while the PostgreSQL DDL and runbook keep the old key.
    expected_reviewers: [api-contract-reviewer, sql-data-reviewer]
    expected_risk_gate: true
    expected_verdict: FIX_REQUIRED
    required_topics: [key_change, rollback, contract]
END_FILE

### CT-6 blocks

Event names `beforeShellExecution` and `afterFileEdit`, and the stdin/stdout JSON shape, are VERIFY-4; if the installed Cursor version names them differently, change only `.cursor/hooks.json`.

FILE: .cursor/hooks.json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      {
        "command": "python scripts/hooks/git_guard.py --runtime cursor"
      }
    ],
    "afterFileEdit": [
      {
        "command": "python scripts/hooks/task_state_guard.py --runtime cursor"
      }
    ]
  }
}
END_FILE

FILE: scripts/hooks/git_guard.py
"""Deny destructive Git and delete commands from agent shells (AGENTS.md §8, D-05 of 20261106-agent-system-unify-api).

Usage: python scripts/hooks/git_guard.py --runtime cursor|claude  (reads one JSON object from stdin)
Cursor: prints {"permission": "allow"|"deny", ...}. Claude Code: exit 2 with the reason on stderr to deny.
`git commit` is allowed; the user's turn decides whether it is wanted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

DENY = [
    (re.compile(r"^git\s+(-\S+\s+)*push\b"), "git push is reserved for the user"),
    (re.compile(r"^git\s+(-\S+\s+)*reset\b"), "git reset is prohibited for agents"),
    (re.compile(r"^git\s+(-\S+\s+)*rebase\b"), "git rebase is prohibited for agents"),
    (re.compile(r"^git\s+(-\S+\s+)*commit\b.*--amend"), "git commit --amend rewrites history"),
    (re.compile(r"^git\s+(-\S+\s+)*filter-branch\b"), "history rewrite is prohibited"),
    (re.compile(r"^git\s+(-\S+\s+)*clean\b"), "git clean deletes untracked files recursively"),
    (re.compile(r"^rm\s+(-\S*[rR]\S*|--recursive)\b"), "recursive delete is prohibited"),
    (re.compile(r"^(rmdir|rd)\b.*(\s/s\b|\s-r)", re.IGNORECASE), "recursive delete is prohibited"),
    (re.compile(r"^remove-item\b.*-recurse", re.IGNORECASE), "recursive delete is prohibited"),
    (re.compile(r"^del\b.*\s/s\b", re.IGNORECASE), "recursive delete is prohibited"),
]
SPLIT = re.compile(r"&&|\|\||;|\||\n")
LOG = Path(".ai/.tmp/hooks.log")


def extract_command(payload: dict, runtime: str) -> str:
    if runtime == "claude":
        tool_input = payload.get("tool_input") or {}
        return str(tool_input.get("command", ""))
    return str(payload.get("command", ""))


def find_violation(command: str) -> str | None:
    for segment in SPLIT.split(command):
        text = segment.strip().lstrip("(").strip()
        for pattern, reason in DENY:
            if pattern.search(text):
                return f"{reason}: `{text[:120]}`"
    return None


def _log(message: str) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {message}\n")
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("cursor", "claude"), required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    command = extract_command(payload if isinstance(payload, dict) else {}, args.runtime)
    violation = find_violation(command)
    if args.runtime == "cursor":
        if violation:
            _log(f"deny cursor {violation}")
            print(json.dumps({
                "permission": "deny",
                "userMessage": f"Blocked by scripts/hooks/git_guard.py: {violation}",
                "agentMessage": f"Command denied ({violation}). Push, reset, rebase, amend, and recursive delete belong to the user; ask instead.",
            }))
        else:
            print(json.dumps({"permission": "allow"}))
        return 0
    if violation:
        _log(f"deny claude {violation}")
        print(f"Blocked by scripts/hooks/git_guard.py: {violation}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
END_FILE

FILE: scripts/hooks/task_state_guard.py
"""After an edit of .ai/tasks/<id>/task-state.yaml, run `vv.py validate <id>` and report errors to the agent.

Usage: python scripts/hooks/task_state_guard.py --runtime cursor|claude  (reads one JSON object from stdin)
Never blocks; it only returns the validator output so Main does not need a separate `validate` call.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

TASK_STATE = re.compile(r"\.ai[\\/]tasks[\\/](\d{8}-[a-z0-9-]+)[\\/]task-state\.yaml$")


def edited_path(payload: dict, runtime: str) -> str:
    if runtime == "claude":
        tool_input = payload.get("tool_input") or {}
        return str(tool_input.get("file_path", ""))
    return str(payload.get("file_path") or payload.get("filePath") or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("cursor", "claude"), required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    match = TASK_STATE.search(edited_path(payload if isinstance(payload, dict) else {}, args.runtime))
    if not match:
        if args.runtime == "cursor":
            print(json.dumps({}))
        return 0
    task_id = match.group(1)
    result = subprocess.run(
        [sys.executable, "scripts/vv.py", "validate", task_id],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    output = (result.stdout + result.stderr).strip()
    message = f"vv.py validate {task_id}: {'PASS' if result.returncode == 0 else 'FAIL'}\n{output}".strip()
    if args.runtime == "cursor":
        print(json.dumps({"agentMessage": message[:2000]}))
    else:
        print(message[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
END_FILE

FILE: .claude/settings.json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-opus-5-5",
  "effortLevel": "high",
  "permissions": {
    "defaultMode": "dontAsk",
    "allow": [
      "Edit(/.ai/tasks/*/architecture.md)",
      "Bash(git status)",
      "Bash(git status *)",
      "Bash(git diff)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git show *)",
      "Bash(git ls-files *)",
      "WebSearch",
      "WebFetch(domain:learn.microsoft.com)",
      "WebFetch(domain:docs.delta.io)",
      "WebFetch(domain:spark.apache.org)",
      "WebFetch(domain:debezium.io)",
      "WebFetch(domain:docs.spring.io)",
      "WebFetch(domain:docs.oracle.com)",
      "WebFetch(domain:java.testcontainers.org)",
      "WebFetch(domain:hibernate.org)",
      "WebFetch(domain:www.postgresql.org)"
    ],
    "deny": [
      "Bash(git push *)",
      "Bash(git reset *)",
      "Bash(git rebase *)",
      "Bash(git restore *)",
      "Bash(git checkout *)",
      "Bash(git stash *)",
      "Bash(git clean *)",
      "Bash(rm *)",
      "Bash(del *)",
      "Bash(Remove-Item *)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python scripts/hooks/git_guard.py --runtime claude"
          }
        ]
      }
    ]
  }
}
END_FILE

### CT-7 blocks

FILE: .cursor/skills/vsvn-api-service/SKILL.md
---
name: vsvn-api-service
description: Add or change an endpoint, DTO, entity, repository, Specification, or test in the POI serving API under services/data-serving-service (Spring Boot, JPA, PostgreSQL schema apps). Use for API tasks, the maven verify lane, and the local docker compose runtime check. Do not use for notebooks, pipelines, Fabric DDL, ctrl tables, gold column or key changes, or the gold to PostgreSQL loader.
---

# VSVN API service

Read `services/data-serving-service/AGENTS.md` first (rule `40-java-api` loads it). This skill adds the working order.

## 1. Endpoint

1. Controller in `api/` only parses and validates parameters (`@Min`, `@Max`, `size` ≤ 100), resolves `lang` with `LanguageResolver`, and delegates to `service/`.
2. Service method is `@Transactional(readOnly = true)`, calls `validatePoiExists` for `/{poi_id}/...` routes, batches child reads (one repository call per table per request), and maps entities to records in `api/dto/`.
3. DTO is a Java `record` with `@JsonProperty` snake_case names and `@Schema` descriptions. Every field maps to a gold column or a derived value named in the record's Javadoc.
4. Errors: throw `ResourceNotFoundException` for an unknown or soft-deleted `poi_id`; `GlobalExceptionHandler` renders the envelope. Do not add a new handler for a new endpoint.
5. Filters: extend `PoiSpecifications`; never build JPQL from request strings. Sorting is whitelisted in `parseSort`.
6. Tests: `@WebMvcTest(PoiController.class)` with `@MockitoBean PoiService` for the contract (status, envelope, JSON names, 404 and 422 paths); a Mockito unit test for the service mapping; a repository test only when a query or key changes.

## 2. Entity, key, or column

- The API never adds a column, table, or key. Confirm it exists in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables` and in `sql/postgres/gld_srv_serve.pg.sql`. Missing → stop, open a data task (`data_model_change`, `run-author --kind model`).
- One `@Column(name = "...")` per line, `name` always set; composite keys use `@IdClass` with every key column marked `@Id`. `tests/test_srv_poi_serving_contract.py` parses this layout.
- Repository generic id type matches the entity key (`String` or the `@IdClass` type).
- After the edit: `pytest -q tests/test_srv_poi_serving_contract.py`, then `mvnw.cmd -q -B test`.

## 3. Tests and verification

- `cd services/data-serving-service && mvnw.cmd -q -B test` with JDK 26 and Docker running. `@SpringBootTest` classes import `TestcontainersConfiguration`, which starts `postgres:18-alpine` and runs `db/00_create_schema_apps.sql` then `gld_srv_serve.pg.sql`.
- `python scripts/vv.py verify <task-id>` repeats the Maven run in the `maven` lane and fails without JDK 26 or Docker. `--allow-no-docker` is diagnostic only and never backs a `local_verification: pass`.
- Fixtures are synthetic: no real names, emails, phones, review texts, or URLs from production.

## 4. Runtime check (D-12)

The user runs it; Main writes `handoffs/author-input.md` and calls `python scripts/vv.py run-author <task-id> --kind runbook`. The runbook: `.env` with `POSTGRES_USER`/`POSTGRES_PASSWORD`; `docker compose up -d postgres`; `psql -c "CREATE SCHEMA IF NOT EXISTS apps"`; `psql -v ON_ERROR_STOP=1 -f ../../sql/postgres/gld_srv_serve.pg.sql`; optional synthetic rows (≤ 50 per table); `docker compose up -d data-serving-service`; `curl /actuator/health` and one request per endpoint; check logs for personal data; `docker compose down -v`. The user pastes sanitized results into `runtime-runbook.md` → `Kết quả người dùng ghi nhận`.

## 5. Review routing

`api/`, `dto/`, entities → `api-contract-reviewer`. `common/web/`, `config/`, `application*.yml`, `pom.xml`, Docker files → `app-security-reviewer`. `domain/repository/`, `service/`, entities → `jpa-performance-reviewer`. Cross-system or key changes add `risk-gate` (`risk_level: high`).

## 6. Stop points

Missing gold column; JDK or Docker absent; a credential or host appears in any file; a contract test failure that points at `sql/postgres/gld_srv_serve.pg.sql` rather than the API.
END_FILE

### CT-8 block

Package and flag are VERIFY-6; change only `command`/`args` if they differ. The credential stays in the OS environment variable `VV_SERVING_PG_URL` (for the compose database: `postgresql://<user>:<password>@localhost:55432/vv_data_serving`), never in this file.

FILE: .cursor/mcp.json
{
  "mcpServers": {
    "vv-serving-postgres-local": {
      "command": "uvx",
      "args": ["postgres-mcp", "--access-mode=restricted"],
      "env": {
        "DATABASE_URI": "${env:VV_SERVING_PG_URL}"
      }
    }
  }
}
END_FILE

FILE: docs/AGENT_PROMPT_SAMPLES.md
# Các prompt mẫu cho VSVN agent

Cách dùng:

1. **Mỗi phase một chat mới** trong Cursor. Chọn **Grok 4.7 Medium** (ngoại lệ model ghi trong `exceptions` của task).
2. Thay mọi `<placeholder>`. Xoá dòng không dùng.
3. Không cần nhắc lại AGENTS.md, "ghi model" hay "dừng khi fallback". Rule always-apply đã áp. Muốn agent commit thì nói rõ trong lượt đó ("commit với message …"); agent không push, không merge.
4. Agent chỉ đọc output của `python scripts/vv.py context <task-id>` và những gì ghi trong mục `Context`. File lớn đọc theo mục hoặc cell bằng `python scripts/vv.py toc <file>` và `python scripts/vv.py show <file> <anchor>`.
5. Khi agent dừng, xem `Kết thúc`, rồi mở chat mới với mẫu của phase kế tiếp.
6. Hầu hết lượt không cần mẫu: một câu nêu task-id, việc cần làm và tiêu chí đủ. Mẫu dưới đây dành cho lượt mở task hoặc lượt đổi phase.

## Bản đồ context

| Phạm vi | File | Đọc thế nào |
|---|---|---|
| Partner extract | `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`, `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, skill `vsvn-extract-notebook` | `toc` rồi `show … cell:<i>` hoặc mục |
| 3P extract | `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`, `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `docs/context/3p-google/README.md`, skill `vsvn-extract-notebook` | như trên. File `.txt` mẫu chỉ đọc khi prompt nêu |
| Lib extract | `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` (183 KB), `docs/context/NB_LIB_EXTRACT_RAWDATA.md`, skill `vsvn-notebook-library` | luôn theo `cell:` hoặc `def:` |
| Lib transform, gold enr | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`, `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md`, `notebooks/NB_ENR_*.ipynb`, `notebooks/NB_00_ORCHES_*.ipynb` | theo `def:` và mục 4–5 |
| DDL, registry | `notebooks/NB_CREATE_DDL.ipynb` (130 KB) | `show … grep:<tên bảng>` trước, rồi `cell:` |
| Bảng ctrl | `docs/context/CTRL_TABLES_CONTEXT.md` | mục của bảng: §3 config, §4 watermark, §5 registry, §6–§7 log, §8 state, §9 reject |
| Đặt tên | `docs/context/02_NAMING_CONVENTION.md` | mục 1–8 theo việc |
| Data model | `docs/context/01_DATA_MODEL.md` | §4 bronze, §5 L1, §6 L2, §7 gold, §8 định danh |
| Vận hành, data model và flow | `docs/context/03_OPERATOR_GUIDE.md` (42 KB), skill `vsvn-operator-docs`, skill `vsvn-data-model-flow` | `toc` rồi `show … "<tiền tố tiêu đề>"`. Không đọc cả file |
| Event Hubs Kafka UI | `local/eventhubs-kafka-ui/up.ps1`, `docs/context/EVENTHUBS_KAFKA_UI.md`, skill `vsvn-eventhubs-kafka-ui` | Yêu cầu mở UI Dev thì chạy `up.ps1`. Không đọc `.env`, không tạo task. |
| Pipeline | `pipelines/<PL>/<PL>.json` | đọc cả file (nhỏ). Không đọc `manifest.json` |
| Serving POI mapping | `docs/context/mapping_gld_srv_poi_amenity.md`, `docs/context/mapping_gld_srv_poi_info.md`, `docs/context/mapping_gld_srv_poi_multi_lang.md`, `docs/context/mapping_poi_media_info.md`, `docs/context/mapping_gld_srv_poi_review.md` | Đọc cả file. Sau mỗi thay đổi nghiệp vụ của bảng trong file, cùng task cập nhật file này trước review. |
| Serving API (Java) | `services/data-serving-service/AGENTS.md`, skill `vsvn-api-service`, `sql/postgres/gld_srv_serve.pg.sql`, `tests/test_srv_poi_serving_contract.py` | Đọc `AGENTS.md` lồng cả file; code theo package được nêu. `docs/poi-serving-api/` chỉ khi prompt nêu (số liệu cũ) |
| Bài học cũ | `docs/context/99_PAIN_POINTS.md` | §0 |
| Quy trình | `docs/agent-system/WORKFLOW.md` | §Classification, §Review routing khi triage |

Không đọc nếu prompt không nêu: `notebooks_lgc/`, `docs/context/3p-google/*.txt`, `.ai/tasks/*/evidence/context/`, `pipelines/*/manifest.json`, `docs/poi-serving-api/`, và artifact của task khác.

## Chọn mẫu

| Tình huống | Mẫu |
|---|---|
| Việc mới bất kỳ (SQL, notebook, pipeline, stateful, cross-system, viết code từ Mapping/BRD) | A1, rồi A4 |
| Việc mới trên API Java (`services/`) | A20 |
| Architecture đã PASS, cần viết code | A4 |
| Lỗi runtime | A9 |
| Không nhớ task đang ở đâu | A10 |
| Lập Mapping và BRD | A13 |
| Phân tích Mapping và BRD | A14 |
| Đề xuất hoặc rà tác động, chưa sửa code | A15 |
| Góp ý vào đề xuất | A16 |
| Thay đổi agent-system | A18 |
| Smoke test tích hợp | A19 |
| Sửa nhỏ, nạp evidence, sửa finding, chạy gate, hướng dẫn Fabric DEV, ghi kết quả runtime, giải thích, review diff, Codex đánh giá hiệu năng | Câu ngắn ở mục "Câu ngắn thường dùng" |

## Khung chung

```text
Task: <task-id> | mới: <slug>
Phase: <triage|evidence|implement|remediate|runtime|closeout|explain|proposal>
Mục tiêu: <1–3 dòng>
Tiêu chí nghiệm thu:
- <…>
Context (sau `python scripts/vv.py context <task-id>`):
- <path> — <mục | cell:<i> | def:<tên>>
Ràng buộc riêng: <hoặc "Không có">
Dừng sau phase này, ghi resume.md.
```

## A1. Việc mới: triage

```text
Task mới: <slug>
Phase: triage
Yêu cầu: <hành vi cần có>
Lý do nghiệp vụ: <…>
Tiêu chí nghiệm thu:
- <…>
Miền (giữ dòng đúng): partner extract | 3P extract | lib extract | lib transform/gold | DDL/registry | ctrl | pipeline | agent-system | serving API
Nguồn yêu cầu đã chốt (nếu có): docs/requirements/<task_id>/MAPPING.md, BRD.md; .ai/tasks/<task_id>/decision.md (ledger); requirements-analysis.md
Context:
- <path — mục/cell theo Bản đồ context>
Việc: tạo task, ghi request.md, phân loại theo WORKFLOW.md §Classification và §Review routing.
- Cần evidence: viết probe nhỏ nhất, dừng ở waiting_evidence.
- Cần architecture, đủ evidence: nếu đổi bảng, cột, grain hoặc khoá thì thêm signal data_model_change, viết handoffs/author-input.md và chạy python scripts/vv.py run-author <task-id> --kind model (effort medium) trước; rồi chạy python scripts/vv.py run-gate <task-id> (Architect effort high), dừng.
- Đủ điều kiện fast lane (WORKFLOW.md: complexity low, risk low, không đổi hành vi, ≤ 2 file): sửa, chạy python scripts/vv.py verify <task-id>, closeout trong chat này.
```

## A4. Triển khai theo architecture

```text
Task: <task-id>
Phase: implement
Context:
- python scripts/vv.py context <task-id> --phase implement (state, resume, ledger, Main brief)
- Chỉ các anchor trong Edit list của Main brief, đọc bằng vv.py show.
- Mục architecture đầy đủ: chỉ khi Main brief trỏ tới.
Việc: sửa theo thứ tự Edit list. Lệch kiến trúc thì ghi decision.md trước khi sửa. Lưu khối FILE bằng python scripts/vv.py materialize <task-id> --write, không gõ lại. Viết test theo brief. Chạy verify; PASS thì chuyển reviewing và chạy run-gate. Dừng.
```

## A9. Điều tra lỗi runtime

```text
Task: <task-id | mới: <slug>>
Phase: evidence
Lỗi (đã làm sạch): <…>
Thời điểm, môi trường: <…>
Notebook, pipeline, bảng, hoặc endpoint: <…>
Lần chạy tốt gần nhất: <… | Chưa biết>
Context: cell hoặc class liên quan (vv.py show … grep:<từ khoá lỗi>); bảng ctrl liên quan (CTRL_TABLES_CONTEXT.md đúng mục).
Việc: chỉ chẩn đoán. Phân loại code | data | architecture | unclear, có bằng chứng. Thiếu evidence thì viết probe nhỏ nhất, dừng ở waiting_evidence. Không sửa code.
```

## A10. Tiếp tục task

```text
Task: <task-id>
Chạy python scripts/vv.py context <task-id>. Chỉ dựa vào output đó và resume.md: nêu phase hiện tại, gate còn mở, việc kế tiếp. Nếu phase là evidence, implement hay remediate, làm tiếp trong chat này theo đúng phase.
```

## A13. Lập Mapping và BRD

```text
Task mới: <slug>
Phase: triage
Bảng đích: <schema, tên, cột, kiểu, khoá, ghi chú>
Nguồn logic: <notebook hoặc mục context>
Context: docs/templates/MAPPING_TEMPLATE.md, docs/templates/BRD_TEMPLATE.md; nguồn logic theo cell hoặc mục.
Việc: chép mẫu sang docs/requirements/<task_id>/MAPPING.md và BRD.md, giữ tên mục và tên cột của mẫu, xoá dòng [EXAMPLE]. Công thức chỉ ghi khi có trong nguồn; thiếu thì MISSING_EVIDENCE; mâu thuẫn thì CONFLICT kèm câu hỏi. doc_status = DRAFT. Không gọi analyst, Architect hay Codex. Phân tích nghiệp vụ làm ở A14 (requirements-analyst, claude-opus-5-5, effort medium).
```

## A14. Phân tích Mapping và BRD

```text
Task: <task_id>
Phase: proposal
File: docs/requirements/<task_id>/MAPPING.md, BRD.md; ledger trong decision.md.
Việc: được xoá dòng [EXAMPLE] còn sót, đặt doc_status = READY_FOR_ANALYSIS và tăng version; không thêm rule, cột hay khoá. Gọi agent requirements-analyst (.claude/agents/requirements-analyst.md, claude-opus-5-5, effort medium, phân tích nghiệp vụ); agent đó tự viết requirements-analysis.md.
- INPUT_INVALID: sửa đúng lỗi, gọi lại một lần.
- EVIDENCE_REQUIRED hoặc USER_DECISION: dừng, liệt kê từng mục.
- COMPLETE: báo xong. Không mở implementation.
```

## A15. Đề xuất hoặc rà tác động (chưa sửa code)

```text
Task mới: <slug>
Phase: proposal
Thay đổi: <source cũ → mới, phạm vi luồng>
Sample (chỉ khoá và kiểu JSON, không giá trị): <…>
Đối tượng: <bảng silver, config, notebook, consumer, endpoint>
Context: <mục và cell theo Bản đồ context>
Việc: tạo task. Phân loại theo deliverable: chỉ đề xuất, không đổi hành vi, nên không architecture và không review.
- Viết handoffs/author-input.md (≤ 60 dòng): yêu cầu nguyên văn, file và mục được đọc, ràng buộc. Chạy python scripts/vv.py run-author <task-id> --kind analysis (claude-opus-5-5, effort medium: phân tích bài toán → problem-analysis.md), rồi viết lại author-input.md và chạy --kind proposal (effort high: đề xuất giải pháp → proposal.md). Main không tự phân tích bài toán hay soạn đề xuất.
Cây khoá ghi ở evidence/payload-shape.md, không ghi giá trị. Cột không có trong sample ghi MISSING_EVIDENCE. Cập nhật ledger. Dừng ở user_decision.
```

## A16. Góp ý vào đề xuất

```text
Task: <task-id> (nếu task đã ready_to_merge: tạo task mới và dẫn chiếu)
Phase: proposal
Góp ý: <bảng, cột, giá trị người dùng vừa chốt>
Context: ledger trong decision.md; proposal.md đúng mục bị góp ý.
Việc:
- author-input.md gồm góp ý nguyên văn và các mục bị thay. Góp ý về hiện trạng hoặc nguyên nhân: chạy run-author --kind analysis (effort medium) trước. Chạy run-author --kind proposal (effort high); bản mới ghi ra proposal.new.md thì Main gộp đúng các dòng bị góp ý. Đề xuất đã chốt mà đổi bảng, cột, grain hoặc khoá: chạy run-author --kind model (effort medium) → model-design.md trước architecture.
Góp ý mới thắng dòng cũ cùng cột. Không tự đặt json_path khi người dùng chưa nêu field. Cập nhật ledger. Dừng.
```

## A18. Thay đổi agent-system (rule, skill, prompt, hook, MCP, vv.py)

```text
Thay đổi agent-system: <mô tả>
Người thiết kế: Claude Code claude-opus-5-5 high qua run-gate (architecture.md), hoặc phiên exception do user chỉ định.
Người thực hiện: <Main Grok | model khác, ghi exceptions model_override role main>.
Review: Codex qua run-gate (risk-gate khi risk_level high).
Context: chỉ file agent-system bị đổi; WORKFLOW.md đúng mục.
Việc: tạo task, ghi exception đã duyệt vào task-state.yaml và decision.md. File nội dung nằm trong khối FILE của architecture thì lưu bằng python scripts/vv.py materialize <task-id> --write, không chép tay. Chạy verify và doctor; doctor không được có WARN; AGENTS.md ≤ 8 KB. Dừng; commit chỉ khi tôi yêu cầu.
```

## A19. Smoke test tích hợp

```text
Chạy python scripts/vv.py external-smoke --timeout 600. Không sửa file.
Thử model override (chỉ khi được yêu cầu): thêm --architect-model <model-id> --architect-effort <low|medium|high>.
Báo: git status --short trước và sau; version CLI, model và effort của Claude và Codex; verdict; reviewer trong manifest; risk-gate; lỗi nguyên văn.
EVIDENCE_REQUIRED cho kịch bản giả lập vẫn hợp lệ.
```

## A20. Việc mới trên serving API (Java)

```text
Task mới: <slug>
Phase: triage
Yêu cầu: <endpoint | DTO | filter | test | cấu hình>
Tiêu chí nghiệm thu:
- <…>
scope.systems: poi-serving-api
Context: services/data-serving-service/AGENTS.md; skill vsvn-api-service; <package hoặc class liên quan>; sql/postgres/gld_srv_serve.pg.sql khi chạm entity.
Ràng buộc: API theo gold; không thêm cột, bảng, khoá (thiếu thì dừng, mở task dữ liệu). Không chép credential hay host vào repo.
Việc: tạo task, phân loại (architecture khi đổi hợp đồng HTTP, entity, hoặc > 8 file). Reviewer theo đường dẫn: api-contract-reviewer | app-security-reviewer | jpa-performance-reviewer. Verify gồm lane maven (JDK 26, Docker). Runtime: tôi chạy docker compose theo runtime-runbook.md. Dừng sau triage.
```

## Câu ngắn thường dùng

Một câu, không cần mẫu. Agent tự chạy `context` trước.

- Sửa nhỏ (fast lane): `Task mới <slug>: sửa <file> <việc>; không đổi hành vi; chỉ fast lane nếu đủ tiêu chí WORKFLOW.md, không thì dừng ở triage.`
- Nạp kết quả evidence: `Task <id>: đã dán evidence/results/<file>; so với tiêu chí probe, ghi ledger, đủ thì chuyển waiting_architecture và chạy run-gate.`
- Sửa finding review: `Task <id>: sửa P0/P1 của round mới nhất theo context --phase remediate, ghi disposition, verify, chạy round kế nếu còn.`
- Chạy gate đang chờ: `Task <id>: chỉ khi status là waiting_architecture hoặc reviewing, chạy run-gate; không sửa source; báo verdict, manifest, status.`
- Hướng dẫn Fabric DEV: `Task <id>: chưa có runbook thì viết author-input.md và chạy run-author --kind runbook; closeout 4 mục; dừng ở waiting_runtime.`
- Ghi kết quả runtime: `Task <id>: kết quả ở <runbook mục "Kết quả người dùng ghi nhận" | evidence/results/<file>>; so tiêu chí; đạt thì gates.runtime pass, không thì phân loại code | data | architecture | unclear.`
- Giải thích (chỉ đọc): `Giải thích <task-id | file + mục/cell>: nghĩa một câu; vì sao có file:dòng; ví dụ từ task; việc cần làm tiếp. Không sửa file.`
- Review diff có sẵn: `Task <id | mới>: review diff chưa commit, không sửa code; chưa có task thì tạo; verify PASS thì reviewing và run-gate.`
- Codex đánh giá hiệu năng: `Task <id>: ghi waiver vào decision.md; chạy Codex read-only (gpt-5.6-sol, medium) với spark-runtime-reviewer và sql-data-reviewer; lưu reviews/performance-review.md; không sửa code.`
- Commit: `Commit các file đã đổi của task <id> với message "<…>".` (agent không push; push và merge do tôi làm.)

## Điểm phải dừng

Cần Fabric DEV hoặc `docker compose` do tôi chạy, model hoặc CLI không khả dụng hay fallback, structured output hoặc immutability fail, cần quyết định hay accept-risk, hoặc vượt round cap. Đây là kết quả hợp lệ của workflow, không phải quyền bỏ qua gate.
END_FILE
