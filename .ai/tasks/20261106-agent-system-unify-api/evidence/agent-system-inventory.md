# Agent-system inventory (current state, 2026-11-06)

Source: repository inspection only. Context estimate = bytes / 4, rounded (≈ tokens). "Always" means loaded into every session of that runtime without a trigger.

## 1. Instruction and context files

| Component | Runtime | Model / effort | Config file | Trigger | Bytes | ≈ tokens |
|---|---|---|---|---|---:|---:|
| `AGENTS.md` (constitution) | Cursor, Claude Code (via `CLAUDE.md` `@AGENTS.md`), Codex | n/a | `AGENTS.md` | Always | 8,187 | 2,050 |
| `CLAUDE.md` (Claude role table) | Claude Code; also injected in Cursor as an always-applied workspace rule | n/a | `CLAUDE.md` | Always | 1,425 | 360 |
| `docs/agent-system/WORKFLOW.md` | All (read on demand) | n/a | same | Named section per phase | 9,877 | 2,470 |
| `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` | none (historical plan) | n/a | same | Not referenced by rules | 85,023 | 21,250 |
| `docs/AGENT_PROMPT_SAMPLES.md` (A1–A19) | User → any runtime | n/a | same | User copies a template | 16,333 | 4,080 |
| `docs/context/` | All (by section) | n/a | 20 files | Named section | 328 KB | 84,000 total |
| `docs/context/3p-google/*.txt` | Excluded by rule | n/a | 12 files | Only when named | 1,512 KB | — |
| `.cursorindexingignore` | Cursor indexing | n/a | same | Always | present | — |

Nested instruction files: none. Only root `AGENTS.md` and `CLAUDE.md` exist; no `AGENTS.override.md`, no per-directory `CLAUDE.md`.

## 2. Cursor

| Component | Model / effort | Config file | Trigger | Bytes | ≈ tokens |
|---|---|---|---|---:|---:|
| Rule `00-main-orchestrator` | Main policy: Grok 4.7 medium | `.cursor/rules/00-main-orchestrator.mdc` | `alwaysApply: true` | 2,570 | 640 |
| Rule `10-fabric-notebook` | — | `.cursor/rules/10-fabric-notebook.mdc` | globs `**/*.Notebook/**, **/*.ipynb` | 2,772 | 690 |
| Rule `20-data-pipeline` | — | `.cursor/rules/20-data-pipeline.mdc` | globs `**/*.DataPipeline/**` | 1,655 | 410 |
| Rule `30-sql` (Spark SQL and PostgreSQL) | — | `.cursor/rules/30-sql.mdc` | globs `**/*.sql` (would also match Flyway `db/migration/*.sql`) | 1,329 | 330 |
| Skill `fabric-runtime-evidence` | — | `.cursor/skills/fabric-runtime-evidence/SKILL.md` | Description match | 996 (desc 299) | 250 |
| Skill `vsvn-data-model-flow` | — | `.cursor/skills/vsvn-data-model-flow/SKILL.md` | Description match | 5,478 (desc 451) | 1,370 |
| Skill `vsvn-eventhubs-kafka-ui` | — | `.cursor/skills/vsvn-eventhubs-kafka-ui/SKILL.md` | Description match | 1,587 (desc 300) | 400 |
| Skill `vsvn-extract-notebook` | — | `.cursor/skills/vsvn-extract-notebook/SKILL.md` | Description match | 19,332 (desc 467) | 4,830 |
| Skill `vsvn-notebook-library` | — | `.cursor/skills/vsvn-notebook-library/SKILL.md` | Description match | 15,736 (desc 473) | 3,930 |
| Skill `vsvn-operator-docs` | — | `.cursor/skills/vsvn-operator-docs/SKILL.md` | Description match | 10,069 (desc 453) | 2,520 |
| Skill `vsvn-task-workflow` | — | `.cursor/skills/vsvn-task-workflow/SKILL.md` | Description match | 4,925 (desc 386) | 1,230 |
| Subagent `requirements-analyst` (exposed from `.claude/agents/`) | `claude-opus-5-5` medium (frontmatter) | `.claude/agents/requirements-analyst.md` | User names task + MAPPING + BRD | 26,036 (desc 459) | 6,510 |
| Hooks | none | no `.cursor/hooks.json` | — | — | — |
| MCP | none in repo | no `.cursor/mcp.json` | — | — | — |
| Plugins | none in repo | — | — | — | — |

Always-loaded Cursor payload from the repo: `AGENTS.md` + `CLAUDE.md` + rule 00 + 7 skill descriptions + 1 subagent description ≈ 2,050 + 360 + 640 + 710 + 115 ≈ 3,900 tokens.

## 3. Claude Code

| Component | Model / effort | Config file | Trigger | Bytes | ≈ tokens |
|---|---|---|---|---:|---:|
| Project settings | `model: claude-opus-5-5`, `effortLevel: high`; `permissions.defaultMode: dontAsk`; allow: Edit of `.ai/tasks/*/architecture.md`, read-only git, WebSearch, WebFetch for 4 domains; deny: git add/commit/push/reset/restore/checkout/stash, rm/del/Remove-Item | `.claude/settings.json` | Every session in the repo | 900 | — |
| Subagent `requirements-analyst` | `claude-opus-5-5` medium; tools Read, Grep, Glob, Write | `.claude/agents/requirements-analyst.md` | Explicit request (A14) | 26,036 | 6,510 |
| Skills, commands | none | no `.claude/skills/`, `.claude/commands/` | — | — | — |
| Hooks | none | no `hooks` key in settings | — | — | — |
| MCP | none | no `.mcp.json` | — | — | — |

## 4. Codex

| Component | Model / effort | Config file | Trigger | Bytes |
|---|---|---|---|---:|
| Project config | `gpt-5.6-sol`, `medium`, `sandbox_mode = read-only`, `approval_policy = never`; `[agents] enabled`, subagent default `gpt-5.6-sol` medium, `max_concurrent_threads_per_session = 4` | `.codex/config.toml` | Every Codex run (`run-gate` review) | 257 |
| `state-correctness-reviewer` | `gpt-5.6-sol` medium, read-only | `.codex/agents/state-correctness-reviewer.toml` | Review manifest | 1,816 |
| `spark-runtime-reviewer` | same | `.codex/agents/spark-runtime-reviewer.toml` | Review manifest | 1,374 |
| `sql-data-reviewer` | same | `.codex/agents/sql-data-reviewer.toml` | Review manifest | 1,778 |
| `fabric-pipeline-reviewer` | same | `.codex/agents/fabric-pipeline-reviewer.toml` | Review manifest | 1,471 |
| `risk-gate` | same | `.codex/agents/risk-gate.toml` | `risk_level` high or critical | 1,457 |
| `requirements-reviewer` | same | `.codex/agents/requirements-reviewer.toml` | Templates/analyst review only | 7,223 |
| Profiles, prompts, MCP | none | no `[profiles]`, no `.codex/prompts/`, no `[mcp_servers]` | — | — |

No reviewer covers Java, Spring, JPA, Flyway, HTTP contracts, or application security.

## 5. `scripts/vv.py` (87,482 B) and `scripts/agent_runner.py` (19,461 B)

| Command | Role | External CLI |
|---|---|---|
| `new` | Create task from `.ai/tasks/_template`; seeds `models.*.expected` | — |
| `validate`, `transition` | State schema, `TRANSITIONS`, owner by status | — |
| `context`, `toc`, `show`, `materialize`, `closeout` | Context pack, section reads, FILE-block save, closeout skeleton | — |
| `verify [--full] [--all]` | ruff (`*.py`); sqlfluff sparksql (`*.sql` not `*.pg.sql`); sqlfluff postgres (`*.pg.sql`); JSON + pipeline activity graph; TOML; pytest `tests/`. No Java/Maven lane; a Flyway `V*__*.sql` would be linted as sparksql | — |
| `doctor` | Model pins, verification modules, budgets: `AGENTS.md` ≤ 8,192 B, always-apply rules ≤ 4,096 B, each skill ≤ 20,480 B, `AGENT_PROMPT_SAMPLES.md` ≤ 25,600 B, `.cursorindexingignore` present, `CTRL_TABLES_CONTEXT.md` present. Current result: `DOCTOR PASS`, no WARN | — |
| `prompt`, `run-gate` | Architect at `waiting_architecture`; review (+ risk-gate) at `reviewing`; round caps | Claude Code; Codex |
| `run-author --kind analysis\|proposal\|model\|runbook` | Author artifacts | Claude Code |
| `external-doctor`, `external-smoke` | CLI discovery and end-to-end smoke | Claude Code; Codex |

CLI discovery (`agent_runner.discover_executable`): env `VSVN_CLAUDE_EXE` / `VSVN_CODEX_EXE`, then `PATH`, then the newest Cursor/VS Code extension binary (`anthropic.claude-code-*`, `openai.chatgpt-*`).

### Hard-coded model locations

| File:line | Value | Effect |
|---|---|---|
| `scripts/agent_runner.py:16-17` | `ARCHITECT_MODEL = "claude-opus-5-5"`, `ARCHITECT_EFFORT = "high"` | Passed as `--model/--effort` at `:249-250`; `run-gate` cannot run Fable |
| `scripts/agent_runner.py:18-23` | `AUTHOR_MODEL = "claude-opus-5-5"`, efforts `author: medium`, `author_proposal: high` | Passed at `:303-304` for every `run-author` kind |
| `scripts/agent_runner.py:24-25` | `REVIEW_MODEL = "gpt-5.6-sol"`, `REVIEW_EFFORT = "medium"` | Passed at `:415-416` to Codex |
| `scripts/vv.py:453-455` | expected `main: grok-4.7`, `architect: claude-opus-5-5`, `review: gpt-5.6-sol` | `validate` fails if `models.*.expected` differ |
| `scripts/vv.py:521-523` | effort `high` for architect, `medium` otherwise | `validate` |
| `scripts/vv.py:1355` | author lanes seeded from `agent_runner.AUTHOR_MODEL` | `new` / `run-author` |
| `scripts/vv.py:1760-1762` | `.codex/config.toml` must be `gpt-5.6-sol` + `medium` | `doctor` |
| `scripts/vv.py:1775-1776` | `.claude/settings.json` model must be `claude-opus-5-5` | `doctor` |
| `scripts/vv.py:1795-1796` | every `.codex/agents/*.toml` must be `gpt-5.6-sol` + `medium` | `doctor` |
| `.claude/agents/requirements-analyst.md` frontmatter | `claude-opus-5-5` medium | Analyst lane |

`exceptions` entries are validated (`scripts/vv.py:457-513`) and listed by `context`, but no runner reads them; an approved override can only be honored by bypassing `run-gate`/`run-author`.

## 6. Budget headroom

| Budget | Limit | Current | Headroom |
|---|---:|---:|---:|
| `AGENTS.md` | 8,192 B | 8,187 B | 5 B |
| Always-apply rules | 4,096 B | 2,570 B | 1,526 B |
| Largest skill (`vsvn-extract-notebook`) | 20,480 B | 19,332 B | 1,148 B |
| `AGENT_PROMPT_SAMPLES.md` | 25,600 B | 16,333 B | 9,267 B |
