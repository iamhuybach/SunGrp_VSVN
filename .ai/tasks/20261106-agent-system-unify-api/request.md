# Request

## User outcome

One repository, `SunGrp_VSVN`, holds both the Fabric data platform and the POI serving API now in `D:\git\SunGrp_VSVN_API` (Java 26, Spring Boot 4.1, JPA, Flyway, PostgreSQL, Testcontainers). The agent system (models, agents, sub-agents, skills, rules, context, hooks, MCP, plugins) for Cursor, Claude Code, and Codex is redesigned to serve both the existing work (Fabric notebooks, pipelines, DDL, ctrl tables) and API work.

This task's triage phase produces factual inventories and a handoff for a Fable exception session that writes `proposal.md` and `architecture.md`.

## Verbatim user request

> Thay đổi agent-system: gom code API từ D:\git\SunGrp_VSVN_API (Java 26, Spring Boot 4.1, JPA, Flyway, PostgreSQL, Testcontainers) vào repo SunGrp_VSVN hiện tại; thiết kế lại model, agent, sub-agent, skill, rule, context, hook, MCP, plugin cho Cursor, Claude Code, Codex để phục vụ cả việc cũ (Fabric notebook, pipeline, DDL, ctrl) và việc API. D:\git\SunGrp_VSVN_API chỉ là nguồn đọc; không tạo repo thứ hai, không sửa thư mục đó.

## Scope

### In scope

- Create the task, ledger, and exceptions EX-01, EX-02, EX-03.
- `evidence/agent-system-inventory.md`, `evidence/api-source-inventory.md`, `evidence/user-action-inventory.md`, `evidence/probes/user_actions_scan.py`.
- `handoffs/fable-input.md` with questions a–h.
- `python scripts/vv.py verify <task-id>`; stop at `user_decision`.

### Out of scope

- Any edit to rules, skills, agents, hooks, MCP, `AGENTS.md`, `WORKFLOW.md`, `scripts/vv.py`, `scripts/agent_runner.py`, `.claude/settings.json`.
- Copying API code. Any write to `D:\git\SunGrp_VSVN_API`. A second repository.
- `run-author` or `run-gate` for proposal and architecture of this task.

## Acceptance criteria

- `evidence/agent-system-inventory.md`: current-state matrix (component, runtime, model, effort, config file, trigger, context estimate) for `AGENTS.md`, `CLAUDE.md`, `WORKFLOW.md`, `.cursor/rules`, `.cursor/skills`, `.claude/agents`, `.claude/settings.json`, `.codex/config.toml`, `.codex/agents/*.toml`, `scripts/vv.py` and `scripts/agent_runner.py` commands, with hard-coded model locations.
- `evidence/api-source-inventory.md`: one row per API source file (path, KB, role); real build/test commands from `pom.xml`, `Dockerfile`, `docker-compose.yml`, `application.yml`; tables and columns from `V1__init_srv_poi_tables.sql` and entities; join points with gold (`gld_srv_poi_*`, `docs/context/mapping_*.md`). No copied content; no `.env.example` values.
- `evidence/user-action-inventory.md`: facts with counts (prompt templates A1–A19 usage, repeated commands, frequent stops, gate/CLI failures with sanitized verbatim errors, review rounds, repeated manual steps). Counted by `evidence/probes/user_actions_scan.py` run locally. No names, emails, tokens, or payloads.
- `handoffs/fable-input.md` (≤ 80 lines): verbatim request, the three inventory paths, questions a–h.

## Constraints

- Main model: `claude-opus-5-5` medium in Cursor under EX-03.
- Proposal and architecture: Fable 5.1 high in the Claude Code extension under EX-01 and EX-02. The runner hard-codes `claude-opus-5-5`, so neither `run-author` nor `run-gate` is used for them.
- Allowed sources for the user-action scan: `.ai/tasks/*/task-state.yaml`, `.ai/tasks/*/resume.md`, the `Quyết định hiện hành` section of `.ai/tasks/*/decision.md`, `git log --stat -n 200`, this project's agent transcripts.

## Classification rationale

- Complexity: high. Signals `cross_system` (Fabric + Java API + three agent runtimes), `design_tradeoffs` (layout, role split, models), `deep_reasoning_required`.
- Risk: medium. Agent-system and repository layout changes; no data or Fabric state touched; rollback is a git revert.
- Architecture: required. The change spans more than eight files and three runtimes with material trade-offs.
- Evidence: required. The three inventories are repository and transcript evidence, gathered locally; no Fabric DEV probe.
- Runtime proof: not required in this phase.
- Reviewer routing: none in triage. Later child tasks route per architecture.
