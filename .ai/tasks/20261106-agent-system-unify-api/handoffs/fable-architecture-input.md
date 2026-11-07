# Fable architecture input: 20261106-agent-system-unify-api (EX-02)

Session: `claude-fable-5-1`, effort high, Claude Code extension. Write only `architecture.md`: the `RESULT:` line, then `## Main brief` (≤ 14,000 chars, `###` sub-headings, per `docs/agent-system/WORKFLOW.md` §Task artifacts), then the full design. Do not run `run-gate` or `run-author`. Do not edit any other file.

## Read

- `decision.md` → `## Quyết định hiện hành`. This is binding: D-01..D-18, EX-03 scope, BA-0311 `out_of_date`.
- `proposal.md` (read by section): "h. Lộ trình", "Ràng buộc cho Architect (EX-02)", and the P-xx sections each child task cites.
- `handoffs/fable-input.md`, `evidence/*.md`. API source `D:\git\SunGrp_VSVN_API` @ `20bca8a` is read-only. Never open `.env.example`.

## Scope

Architecture covers child tasks CT-1..CT-8 of "h. Lộ trình", including the entity, DTO, and test changes for D-08, D-09, and D-10 (CT-4). CT-9 (gold → PostgreSQL load) appears only as a dependency. It needs its own task, with Main `grok-4.7` medium.

## Changes from proposal imposed by decisions

- D-06: drop every Main-model change in P-d1 and P-d2. No §3 Main sentence, no `scope.systems` branch in `vv.py validate`, and no model edit in `00-main-orchestrator.mdc`. Remove P-d2 from CT-2.
- D-07: CT-1 makes the runner read approved `exceptions` (architect, author, author_proposal, review) only after `external-smoke` proves the CLI accepts `claude-fable-5-1`. If that check fails, keep the hard-coded models and use manual exception sessions. Design both branches.
- D-08: remove Flyway (`pom.xml:32,43-44`, `db/migration/V1__init_srv_poi_tables.sql`, `spring.flyway` in both `application.yml`). Testcontainers loads `sql/postgres/gld_srv_serve.pg.sql`. That file creates no schema, so the test must create `apps` first.
- D-09: `SrvPoiMediaGallery` gets `@IdClass(media_id, poi_id)` with a new id class. `SrvPoiMediaGalleryRepository` changes from `JpaRepository<…, String>`.
- D-10: drop `source_name` from `SrvPoiReview`. API 9 is `GET /api/v1/pois/{poi_id}/reviews` (`PoiController.getReviews`). Also drop `source`/`lang` from `PoiReviewItemResponse` and its mapping at `PoiService.java:165`. Test builders with `.sourceName(…)`: `PoiServiceTest.java:70,243` and `PoiRepositoryIntegrationTest.java:68`. Decide which of them build a review; `PoiControllerIntegrationTest` has no `source` reference. List every endpoint, DTO, and test you change. Other entities' `source_name` is out of D-10 scope.
- D-10 docs to update when copied in CT-3/CT-4 (they describe API 9 returning `source`, `lang`): `docs/poi-serving-api/DESIGN-AND-PLAN.md` (lines 241 and 404, §G item 4) and `docs/poi-serving-api/API-GAPS.md` (line 150 G14, line 159 S4). No `docs/context/mapping_*.md` says this. Related but not API 9: `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio:397` shows `lang` on `gld_srv_poi_review`.
- D-16: delete `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md`. D-17: merge A1–A19 per P-c1 and add A20.

## D-05: every place that forbids agent commit (edit them together)

| File:line | Current text (short) |
|---|---|
| `AGENTS.md:22` (§2 User row) | "commits and merges" |
| `AGENTS.md:74` (§8) | "Agents do not commit, push, merge, or rewrite Git history." |
| `.cursor/rules/00-main-orchestrator.mdc:26` | "Only the user commits, merges, …" |
| `CLAUDE.md:25` | "Do not commit or push." (Claude roles; decide whether D-05 applies) |
| `.cursor/skills/vsvn-task-workflow/SKILL.md:48-49,57` | `commit` request type; "Main never commits." |
| `.claude/settings.json:23-24` | deny `git add *`, `git commit *` |
| `docs/AGENT_PROMPT_SAMPLES.md:7,270` | "không commit"; "Dừng trước commit." |
| `scripts/vv.py:790,1544-1548` | `ready_to_merge`: "user commit/merge only"; closeout `commit:` wait |
| `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` | deleted by D-16 |

The new hook blocks `git push`, `reset`, `rebase`, `commit --amend`, and recursive delete. A commit is allowed only when the user's current turn asks for one. Push and merge stay with the user.

## Required output shape

1. An Edit list per child task (`# | file | anchor | change | done-when`), in the order of D-18: CT-1 ∥ CT-2 → CT-3 → {CT-4, CT-5, CT-7, CT-8}; CT-6 after D-05.
2. A `FILE:` block (full content, for `vv.py materialize`) for every new or rewritten rule, skill, hook, agent toml, config (`.cursor/hooks.json`, `.cursor/mcp.json`, `.codex/config.toml`, `.claude/settings.json`), and nested `AGENTS.md`/`CLAUDE.md`.
3. For each child task: classification, `architecture_required`, verify commands, the `doctor` check, rollback, acceptance criteria, and the `exceptions` entry for role `main` (`claude-opus-5-5` medium, scope "Main of CT-n under EX-03 of 20261106-agent-system-unify-api", approved_by user, 2026-11-06).
4. A byte budget: root `AGENTS.md` ≤ 8,192 B after D-05 edits (5 B headroom today); `doctor` with no WARN after every task.
5. Reviewers: `risk-gate`, one round, for CT-2 and CT-3 (D-15). Three Codex API reviewers in CT-5 (D-13), `gpt-5.6-sol` medium.
6. Runtime gates: user-run local compose + smoke for the first 2 API tasks (D-12). JDK 26 + wrapper (D-11). MCP PostgreSQL local, read-only, after CT-3 (D-14).

## Still MISSING_EVIDENCE

ME-06 (how the eval suite runs), ME-07, and ME-08 are unanswered. Proposal items 1–5 and 9 are checked inside child tasks. Do not assume answers; give each one a probe or a check step.
