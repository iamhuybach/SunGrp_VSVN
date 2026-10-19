RESULT: PASS

## Main brief

### Decision
Split by invocation, one effort per run. Business analysis = `requirements-analyst` at `medium`. Problem analysis = new `run-author --kind analysis` → `problem-analysis.md`. Solution proposal = `--kind proposal` at `high` (unchanged lane `models.author_proposal`). Model design = new `--kind model` → `model-design.md`. Both new kinds run on the existing `models.author` lane at `medium`. The Architect stays `high`, reads `model-design.md`, and never writes it. New signal `data_model_change` makes `run-gate` refuse to call the Architect while `model-design.md` is missing. `.claude/settings.json`, the task template, and `author-runbook.md` are unchanged.

### Invariants Main must preserve
- `agent_runner.ARCHITECT_EFFORT == "high"`; `.claude/settings.json` `effortLevel` stays `high` and the file is untouched.
- `agent_runner.AUTHOR_EFFORTS == {"analysis":"medium","model":"medium","proposal":"high","runbook":"medium"}`, derived from `AUTHOR_LANE_EFFORTS == {"author":"medium","author_proposal":"high"}`.
- `--kind proposal` records only `models.author_proposal.actual`; `analysis`/`model`/`runbook` record only `models.author.actual`.
- Output files: analysis→`problem-analysis.md`, model→`model-design.md`, proposal→`proposal.md`, runbook→`runtime-runbook.md`. An existing non-template file is preserved and output goes to `.new.md`.
- `run-gate` in `waiting_architecture` with signal `data_model_change` and a missing or blank `model-design.md` exits non-zero before any Claude call, with `task-state.yaml` byte-identical.
- The validator reports each lane's wrong effort once; the template validates with zero errors and is unchanged.
- `requirements-analyst.md` has `effort: medium` and keeps "Never write `architecture.md`" and "never replaces the Architect".
- `architect.md` keeps effort `high` and drops "You own model design". `author-proposal.md` keeps effort `high` and has no `## Phân tích bài toán`.
- Every kind has `.ai/prompts/author-<kind>.md`.
- doctor shows no budget WARN; `AGENTS.md` < 8192 bytes.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | `.ai/tasks/20261019-agent-system-claude-opus-design/task-state.yaml` | `scope.files`; `exceptions[0].effort` | Add `.ai/prompts/author-analysis.md` and `.ai/prompts/author-model.md` to `scope.files`. Set the exception `effort: medium` (the role `author` lane now carries the medium products; the scope text already records the revision). | `vv.py validate` PASS |
| 2 | `.ai/prompts/architect.md` | whole file | Save the FILE block with `materialize --write` | materialize shows `identical` on re-run |
| 3 | `.ai/prompts/author-proposal.md` | whole file | Save the FILE block with `materialize --write` | same as #2 |
| 4 | `.ai/prompts/author-analysis.md` | new file | Create it verbatim from §New prompt: author-analysis.md | `test_author_kind_lanes_and_prompts` passes |
| 5 | `.ai/prompts/author-model.md` | new file | Create it verbatim from §New prompt: author-model.md | same as #4 |
| 6 | `scripts/agent_runner.py` | constants after `AUTHOR_MODEL` | Replace the `AUTHOR_EFFORTS` literal with `AUTHOR_LANE_EFFORTS`, `AUTHOR_KIND_LANES`, and derived `AUTHOR_EFFORTS` (§Runner and validator code). `run_author` is unchanged. | `test_run_author_effort_follows_kind[analysis/model]` pass |
| 7 | `scripts/vv.py` | `AUTHOR_LANES` constant; `SIGNALS` | `AUTHOR_LANES = agent_runner.AUTHOR_KIND_LANES`; add `AUTHOR_OUTPUTS`; add `"data_model_change"` to `SIGNALS` | `test_data_model_change_signal_is_valid` passes |
| 8 | `scripts/vv.py` | `validate_state_data` author loop | Iterate `agent_runner.AUTHOR_LANE_EFFORTS.items()` as `(key, effort)`; drop the per-kind effort lookup | `test_author_lane_effort_error_reported_once` passes |
| 9 | `scripts/vv.py` | `_author_output_path` | `name = AUTHOR_OUTPUTS[kind]` | `test_run_author_records_lane_by_kind[*]` pass |
| 10 | `scripts/vv.py` | `cmd_run_author` | Key from `AUTHOR_LANES[args.kind]`; add `print(f"Lane: models.{key}")` after the `Model:` line | same as #9 |
| 11 | `scripts/vv.py` | `cmd_run_gate` `waiting_architecture` branch, after the round-cap block | Add the model-design precondition (§Runner and validator code) | both new `test_run_gate_*model_design*` pass |
| 12 | `scripts/vv.py` | `build_parser` `run-author --kind` | `choices=tuple(AUTHOR_LANES)` | `run-author --help` lists 4 kinds |
| 13 | `.claude/agents/requirements-analyst.md` | frontmatter `effort`; `## Identity` table and bullets L23–24; `## Output file` metadata `effort` row | `high`→`medium`; approval date → 2026-10-20 (§requirements-analyst.md edits) | `test_requirements_analyst_effort_medium` passes |
| 14 | `AGENTS.md` | §1 Vietnamese line; §2 Architect, Author, Requirements Analyst rows; §3 bullets 1–2 | Replace with the exact text in §AGENTS.md text | doctor has no WARN; `test_roles_documented` passes |
| 15 | `docs/agent-system/WORKFLOW.md` | `### Complexity signals`; commands block `run-author`; `## Task artifacts` `proposal.md` row and `author-input.md` row | Per §WORKFLOW.md edits | text present |
| 16 | `docs/AGENT_PROMPT_SAMPLES.md` | triage sample "Cần architecture" line; A13; A14; A15 bullet; A16 bullet | Per §AGENT_PROMPT_SAMPLES.md edits | doctor has no WARN |
| 17 | `tests/test_vv.py` | `prepare_author_task`; `test_run_author_records_lane_by_kind`; `test_run_author_effort_follows_kind`; `test_requirements_analyst_effort_high`; new tests | Per §Tests | pytest green |
| 18 | `tests/test_vv_context.py` | new tests next to `test_optional_author_proposal_model_validation` | Add `test_data_model_change_signal_is_valid` and `test_author_lane_effort_error_reported_once` using the file's existing base-state builder | pytest green |

### Order and stop points
1. Row 1 (Main edits task state). The status is already `implementing` after this PASS.
2. `python scripts/vv.py materialize 20261019-agent-system-claude-opus-design --write` (rows 2–3).
3. Rows 4–5, then the code in rows 6–12.
4. Rows 17–18, then run pytest. Stop if anything fails; fix only within the edit list.
5. Rows 13–16.
6. Run doctor. **Stop (evidence):** if it reports `AGENTS.md` ≥ 8192, apply the fallback trim in §AGENTS.md text and re-run. If it still exceeds the limit, stop for a user decision on which line to shorten.
7. `verify` PASS → `transition … reviewing` → `run-gate` (review round 2, the last allowed).
8. **Stop (user decision):** the user commits. Do not commit.

### Tests and verification
- `python -m pytest tests/test_vv.py tests/test_vv_context.py "tests/test_initial_ddl_contract.py::test_roles_documented" -q`
- New or renamed tests: `test_author_kind_lanes_and_prompts`, `test_architect_effort_stays_high`, `test_prompts_split_analysis_proposal_and_model_design`, `test_run_gate_requires_model_design_for_data_model_change`, `test_run_gate_runs_architect_when_model_design_exists`, `test_requirements_analyst_effort_medium`, `test_data_model_change_signal_is_valid`, `test_author_lane_effort_error_reported_once`; parametrized `test_run_author_records_lane_by_kind[analysis|model|proposal|runbook]` and `test_run_author_effort_follows_kind` with analysis/model.
- `python scripts/vv.py doctor`: no `budget exceeded` line.
- `python scripts/vv.py run-author --help`: `--kind` shows analysis, model, proposal, runbook.
- `git diff --quiet -- .claude/settings.json .ai/tasks/_template/task-state.yaml .ai/prompts/author-runbook.md`: exit 0.
- `python scripts/vv.py verify 20261019-agent-system-claude-opus-design`: PASS.

### Read only if needed
- `Decisions and alternatives` (D-A to D-D) → rows 4–12, 14
- `Invariants` → all rows
- `Ordering`; `Retry and recovery` → row 11
- `Implementation plan / Runner and validator code` → rows 6–12
- `Implementation plan / AGENTS.md text` → row 14
- `Implementation plan / requirements-analyst.md edits` → row 13
- `Implementation plan / WORKFLOW.md edits` → row 15
- `Implementation plan / AGENT_PROMPT_SAMPLES.md edits` → row 16
- `Implementation plan / New prompt: author-analysis.md`, `New prompt: author-model.md` → rows 4–5
- `Implementation plan / Tests` → rows 17–18
- `Rollback and forward recovery` → row 7 (`data_model_change` after a revert)

# Architecture: split Claude effort for analysis, proposal, model design, and architecture

## Scope

This design implements the 2026-10-20 revision (ledger rows EX-20261019-CLAUDE-DESIGN-HIGH, D2, D3; D1 kept). It splits five Claude Code products into separate invocations, each with one effort:

| Product | Artifact | Lane (existing) | Invocation | Effort |
|---|---|---|---|---|
| Business analysis | `requirements-analysis.md` | `requirements-analyst` subagent | user-triggered subagent | `medium` |
| Problem analysis | `problem-analysis.md` (new) | `models.author` | `run-author --kind analysis` (new kind) | `medium` |
| Solution proposal | `proposal.md` | `models.author_proposal` | `run-author --kind proposal` | `high` |
| Model design | `model-design.md` (new) | `models.author` | `run-author --kind model` (new kind) | `medium` |
| Architecture | `architecture.md` | `models.architect` | `run-gate` (waiting_architecture) | `high` |
| Runbook (unchanged) | `runtime-runbook.md` | `models.author` | `run-author --kind runbook` | `medium` |

Pipeline order for a data-model task: business analysis (optional) → problem analysis → solution proposal → model design → architecture → Main implements.

Files touched: `scripts/agent_runner.py`, `scripts/vv.py`, `.ai/prompts/architect.md`, `.ai/prompts/author-proposal.md`, two new prompts `.ai/prompts/author-analysis.md` and `.ai/prompts/author-model.md` (Main must add both to `scope.files` first), `.claude/agents/requirements-analyst.md`, `AGENTS.md`, `docs/agent-system/WORKFLOW.md`, `docs/AGENT_PROMPT_SAMPLES.md`, `tests/test_vv.py`, `tests/test_vv_context.py`, and this task's `task-state.yaml` (Main-owned record fixes).

Explicitly unchanged: `.claude/settings.json` (stays `effortLevel` `high` for the Architect), `.ai/tasks/_template/task-state.yaml` (already `author` medium and `author_proposal` high), `.ai/prompts/author-runbook.md`, `.cursor/rules/00-main-orchestrator.mdc`, and `.cursor/skills/vsvn-task-workflow/SKILL.md` (neither mentions author effort).

## Non-goals

- No new `models.*` key, no new `EXCEPTION_ROLES` entry, no new subagent, no new role that writes `architecture.md`.
- No change to Main, Review, risk-gate, round caps, evidence or runtime gates, `materialize` sources, or Fabric objects.
- No migration of historical `proposal.md` files that contain `## Phân tích bài toán`; they remain valid inputs.
- `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` is not edited.

## Decisions and alternatives

### D-A. Where problem analysis runs

| Option | Assessment |
|---|---|
| **A1. New kind `analysis` on `models.author` (selected)** | Reuses the existing medium lane, the runner's read-only/immutability contract, author-input, and `.new` collision handling. Zero schema change. Runs before the proposal, so it cannot share the high run. |
| A2. Fold into `requirements-analyst` | Rejected. That agent is user-triggered and bound to Mapping + BRD inputs; adding a second product changes its contract and its single-file boundary. Many proposal tasks have no Mapping/BRD. |
| A3. New `models.author_analysis` key | Rejected. Adds schema, validator, template, and exception-role churn; acceptance asks for an existing lane. |
| A4. Keep it inside `proposal.md`, second pass at medium | Rejected. Two runs writing one file needs merge logic; the high run would still regenerate or paraphrase the analysis. |

### D-B. Where model design runs

| Option | Assessment |
|---|---|
| **B1. New kind `model` on `models.author`; Architect consumes `model-design.md` (selected)** | Satisfies "not produced by the high Architect invocation" with one deterministic boundary (a separate file and a separate process). Runs after the accepted proposal and before `run-gate`. |
| B2. Two-phase `run-gate`: Architect at medium, then high | Rejected. Redefines the Architect lane as dual-effort, doubles consumption of the 2-round architecture cap, and complicates the state machine. |
| B3. `requirements-analyst` writes model design | Rejected. Its role boundary forbids design and it is not on the task's critical path. |
| B4. Main writes it | Prohibited by the request. |

### D-C. Enforcing that the Architect does not produce model design

| Option | Assessment |
|---|---|
| C1. Prompt only | Weak. When `model-design.md` is absent, a high-effort Architect tends to fill the gap, and an `EVIDENCE_REQUIRED` return burns an architecture round. |
| **C2. Prompt + new signal `data_model_change` + deterministic `run-gate` precondition (selected)** | `run-gate` refuses to call Claude when the signal is set and `model-design.md` is missing or blank: no round consumed, no state change. The prompt covers unsignalled tasks and conflicts. |

The signal is additive to `SIGNALS`, so existing tasks stay valid.

### D-D. Representing effort

The current code keys effort by kind (`AUTHOR_EFFORTS`) and iterates kinds in the validator. With four kinds over two lanes, that iteration would emit duplicate `models.author` errors. **Selected:** effort is keyed by lane (`AUTHOR_LANE_EFFORTS`), kinds map to lanes (`AUTHOR_KIND_LANES`), and `AUTHOR_EFFORTS` is derived for the runner and tests. The validator iterates lanes. This keeps D1: `models.author` is the medium (runbook) lane, `models.author_proposal` is the high solution-proposal lane.

## Invariants

1. I1: The Architect command built by `run_architecture` contains `--effort high` and `--model claude-opus-5-5`; `.claude/settings.json` is byte-identical before and after.
2. I2: `run_author(kind="proposal")` passes `--effort high` and records `models.author_proposal.actual`; kinds `analysis`, `model`, `runbook` pass `--effort medium` and record only `models.author.actual`.
3. I3: `agent_runner.AUTHOR_EFFORTS == {"analysis": "medium", "model": "medium", "proposal": "high", "runbook": "medium"}`, derived from `AUTHOR_LANE_EFFORTS == {"author": "medium", "author_proposal": "high"}`.
4. I4: Each kind writes only its artifact: `analysis`→`problem-analysis.md`, `model`→`model-design.md`, `proposal`→`proposal.md`, `runbook`→`runtime-runbook.md`; an existing non-template target is preserved and output goes to `<stem>.new.md`.
5. I5: `run-gate` in `waiting_architecture` with `data_model_change` in signals and a missing or whitespace-only `model-design.md` exits non-zero before `render_prompt`/`run_architecture`, and `task-state.yaml` is unchanged.
6. I6: The validator reports a wrong lane effort exactly once per lane; the template validates with zero errors and is unchanged.
7. I7: `requirements-analyst.md` frontmatter has `effort: medium`, keeps `model: claude-opus-5-5`, and still says it never writes `architecture.md` and never replaces the Architect.
8. I8: `architect.md` keeps effort `high`, no longer claims model design, and names `model-design.md` / `--kind model` as the model-design input. `author-proposal.md` keeps effort `high` and no longer contains `## Phân tích bài toán`.
9. I9: `python scripts/vv.py doctor` emits no budget WARN; `AGENTS.md` < 8192 bytes.
10. I10: Every `run-author` kind has a prompt file `.ai/prompts/author-<kind>.md`.

## State ownership

- `task-state.yaml`: Main, plus the runner on Main's behalf (`run-author` sets `models.<lane>.actual`; `run-gate` sets architect fields and status). Unchanged.
- `problem-analysis.md`, `model-design.md`: written only by `run-author` (Claude, read-only run; vv.py persists). Main may merge `.new.md` versions.
- `architecture.md`: Architect through `run-gate`. It reads `model-design.md` and never writes it.
- `requirements-analysis.md`: `requirements-analyst` only.
- `handoffs/author-input.md`: Main. A single file reused per run; Main overwrites it before each `run-author` kind.

## Grain and keys

Not applicable: no data model changes. Logical key of an author run = `(task_id, kind)` → one artifact path.

## Ordering

- Inside `cmd_run_author`: validate state → render prompt → Claude run → validate candidate state → write artifact → write state (existing order kept).
- Inside `cmd_run_gate`/`waiting_architecture`: architecture-required check → round cap → **new model-design precondition** → render prompt → Claude run. The precondition runs after the cap, so cap routing still works when the round limit is reached; it runs before any external call.
- Workflow order: `analysis` before `proposal` (the proposal cites it); `model` after the accepted proposal; `run-gate` after `model` when signalled.

## Transaction and commit boundaries

- Artifact write then state write in `cmd_run_author`: a crash between them leaves the artifact without `actual` recorded. This is pre-existing behavior and harmless, because re-running rewrites or `.new`-suffixes the artifact.
- Precondition failure writes nothing.
- Git commit: the user, once, after review.

## Idempotency

- Re-running a kind never overwrites a non-template artifact (`.new.md`), so repeated runs are safe.
- The precondition is pure: it reads only state and file existence.
- `materialize --write` of the two FILE blocks is idempotent (`identical` is skipped).

## Concurrency

Not applicable: Main runs `run-author` and `run-gate` sequentially per task. Concurrent runs on one task were already unsupported (single `task-state.yaml` writer).

## Retry and recovery

- A `run-author` failure (`AUTHOR FAIL`) leaves no artifact or state change. Fix the input and re-run.
- A precondition failure tells Main the exact command (`run-author <task> --kind model`). After it succeeds, re-run `run-gate`. No round was consumed.
- If the Architect returns `EVIDENCE_REQUIRED` because `model-design.md` conflicts with the ledger: Main re-runs `--kind model` with the conflict in author input, merges `model-design.new.md`, and transitions `waiting_evidence → waiting_architecture`.

## Partial failure

- Half-applied edit set (code updated, prompts not): `test_author_kind_lanes_and_prompts` fails on the missing prompt files, so `verify` blocks.
- AGENTS.md over budget after the edit: doctor WARN plus `tests/test_initial_ddl_contract.py::test_roles_documented` failure. Apply the fallback trim in §AGENTS.md text.

## Observability

- `cmd_run_author` prints `Model: claude-opus-5-5 effort <e>` (existing) and adds `Lane: models.<key>`.
- The precondition message names the signal, the missing file, and the command to run.
- `task-state.yaml` `models.author.actual` / `models.author_proposal.actual` record which lane ran.

## Security

No new tools, permissions, or network paths. New kinds inherit `--tools Read,Glob,Grep`, `--permission-mode dontAsk`, `--safe-mode`, and the git-snapshot immutability check. The new prompts forbid copying sample values, person names, or URLs.

## Rollout

Single change set on `main`, committed by the user after `verify`, doctor, and review round 2. Existing tasks need no migration: the template is unchanged, `data_model_change` is opt-in, and old `proposal.md` files with an analysis section remain readable inputs.

## Rollback and forward recovery

- Rollback: `git revert` of the commit. Any task that adopted `data_model_change` after rollout will then fail `validate` (unknown signal). Forward recovery: Main removes that signal from those tasks' `task-state.yaml`. `problem-analysis.md` / `model-design.md` files stay as plain inputs.
- No Fabric or data state is involved.

## Implementation plan

### Runner and validator code

`scripts/agent_runner.py`, module constants (replace the `AUTHOR_EFFORTS` line):

```python
AUTHOR_MODEL = "claude-opus-5-5"
AUTHOR_LANE_EFFORTS = {"author": "medium", "author_proposal": "high"}
AUTHOR_KIND_LANES = {
    "analysis": "author", "model": "author", "proposal": "author_proposal", "runbook": "author",
}
AUTHOR_EFFORTS = {kind: AUTHOR_LANE_EFFORTS[lane] for kind, lane in AUTHOR_KIND_LANES.items()}
```

`run_author` is unchanged; it already validates `kind in AUTHOR_EFFORTS` and passes `AUTHOR_EFFORTS[kind]`.

`scripts/vv.py`:

```python
AUTHOR_LANES = agent_runner.AUTHOR_KIND_LANES
AUTHOR_OUTPUTS = {
    "analysis": "problem-analysis.md", "model": "model-design.md",
    "proposal": "proposal.md", "runbook": "runtime-runbook.md",
}
```

Add `"data_model_change"` to `SIGNALS`.

`validate_state_data`, author loop: replace `for kind, key in AUTHOR_LANES.items():` with `for key, effort in agent_runner.AUTHOR_LANE_EFFORTS.items():` and delete the line `effort = agent_runner.AUTHOR_EFFORTS[kind]`. The rest of the body is unchanged.

`_author_output_path`: `name = AUTHOR_OUTPUTS[kind]`.

`cmd_run_author`: `effort = agent_runner.AUTHOR_EFFORTS[args.kind]` stays. After the `Model:` print, add `print(f"Lane: models.{key}")`.

Argparse `run-author`: `choices=tuple(AUTHOR_LANES)`.

`cmd_run_gate`, `waiting_architecture` branch, directly after the round-cap block and before `render_prompt`:

```python
            if "data_model_change" in state["classification"].get("signals", []):
                design = directory / "model-design.md"
                if not design.is_file() or not design.read_text(encoding="utf-8").strip():
                    fail(
                        "Signal data_model_change requires model-design.md before the Architect runs. "
                        f"Run: python scripts/vv.py run-author {args.task} --kind model"
                    )
```

### AGENTS.md text

Replace exactly these lines and leave every other line unchanged.

§1 line beginning `- Vietnamese:`:

```text
- Vietnamese: prose in `decision.md`, `runtime-runbook.md`, `problem-analysis.md`, and `proposal.md`; explanatory comments in source, notebooks, and SQL; conversation with the user.
```

§2 rows Architect, Author, Requirements Analyst:

```text
| Architect | Claude Code, Claude Opus 5.5 High | Writes only the current task's `architecture.md`, including the `Main brief`, through the runner. Reads `model-design.md`; never writes model design. Never implements. |
| Author | Claude Code, Claude Opus 5.5 (effort in §3) | Through `vv.py run-author --kind` only, on Main's request: writes `problem-analysis.md`, `proposal.md`, `model-design.md`, or `runtime-runbook.md`. Never implements. |
| Requirements Analyst | Claude Code, Claude Opus 5.5 Medium | Business analysis on the user's request: writes only the task's `requirements-analysis.md`. Never writes `architecture.md` or replaces the Architect. |
```

§3 first two bullets:

```text
- Main: Grok 4.7, `medium` (user approved 2026-10-09). Architect: Claude Opus 5.5, `high`. Review: `gpt-5.6-sol`, `medium` (user approved 2026-10-08). Author: Claude Opus 5.5, `high` for `--kind proposal` (`models.author_proposal`), `medium` for `--kind analysis`, `model`, and `runbook` (`models.author`). Requirements Analyst: Claude Opus 5.5, `medium`.
- Lanes (user approved 2026-10-20): business analysis is the Requirements Analyst, problem analysis is `--kind analysis`, solution proposal is `--kind proposal`, model design is `--kind model`, and architecture is the Architect. Main does not author them.
```

The estimated net change is about +100 bytes on 7909, which stays under the limit. Fallback if doctor reports ≥ 8192: in line 3, delete ` (statuses, classification, workflow, review routing, commands)`.

### requirements-analyst.md edits

- Line 6 frontmatter: `effort: medium`.
- Identity table: `| effort | \`medium\` |`.
- Line 23: `- Model and effort are set in this file's frontmatter (effort \`medium\`, user approved 2026-10-20). \`.claude/settings.json\` keeps \`claude-opus-5-5\` at effort \`high\` for the Architect and is not changed for this agent.`
- Line 24: replace `effort is not \`high\`` with `effort is not \`medium\``.
- Output-file metadata table: `| effort | medium |`.

### WORKFLOW.md edits

- `### Complexity signals` block: add the line `data_model_change` after `data_evidence_required`. After the closing fence, add: ``"`data_model_change`: the task changes a table, column, grain, or key. `run-gate` then requires a non-empty `model-design.md` (`run-author --kind model`) before it calls the Architect."``
- Commands block: `python scripts/vv.py run-author <task-id> --kind analysis|proposal|model|runbook`.
- Task artifacts table: replace the `proposal.md` row with these three rows:

```text
| `problem-analysis.md` | Author lane `models.author` (`claude-opus-5-5`, effort `medium`), `run-author --kind analysis` | Vietnamese | Problem analysis: problem, cited current state, gap or cause, affected objects, questions. Input to the proposal. |
| `proposal.md` | Proposal author lane `models.author_proposal` (`claude-opus-5-5`, effort `high`), `run-author --kind proposal` | Vietnamese | Solution proposal for the user; cites `problem-analysis.md`. `decision.md` ledger rows point to it. |
| `model-design.md` | Author lane `models.author` (`claude-opus-5-5`, effort `medium`), `run-author --kind model` | English | Model design: entities, grain, keys, columns, lineage. Input to the Architect, who never writes it. Required before `run-gate` when signal `data_model_change` is set. |
```

- `handoffs/author-input.md` row: append ` Overwritten before each \`run-author\` kind.` to the contract cell.

### AGENT_PROMPT_SAMPLES.md edits

- Triage sample, line `- Cần architecture, đủ evidence: ...` →
  `- Cần architecture, đủ evidence: nếu đổi bảng, cột, grain hoặc khoá thì thêm signal data_model_change, viết handoffs/author-input.md và chạy python scripts/vv.py run-author <task-id> --kind model (effort medium) trước; rồi chạy python scripts/vv.py run-gate <task-id> (Architect effort high), dừng.`
- A13: `... Phân tích nghiệp vụ làm ở A14 (requirements-analyst, claude-opus-5-5, effort medium).`
- A14: replace `effort high, phân tích nghiệp vụ` with `effort medium, phân tích nghiệp vụ`.
- A15 bullet →
  `- Viết handoffs/author-input.md (≤ 60 dòng): yêu cầu nguyên văn, file và mục được đọc, ràng buộc. Chạy python scripts/vv.py run-author <task-id> --kind analysis (claude-opus-5-5, effort medium: phân tích bài toán → problem-analysis.md), rồi viết lại author-input.md và chạy --kind proposal (effort high: đề xuất giải pháp → proposal.md). Main không tự phân tích bài toán hay soạn đề xuất.`
- A16 bullet →
  `- author-input.md gồm góp ý nguyên văn và các mục bị thay. Góp ý về hiện trạng hoặc nguyên nhân: chạy run-author --kind analysis (effort medium) trước. Chạy run-author --kind proposal (effort high); bản mới ghi ra proposal.new.md thì Main gộp đúng các dòng bị góp ý. Đề xuất đã chốt mà đổi bảng, cột, grain hoặc khoá: chạy run-author --kind model (effort medium) → model-design.md trước architecture.`

### New prompt: author-analysis.md

Create `.ai/prompts/author-analysis.md` with exactly:

```text
# Author handoff: problem analysis for {{TASK_ID}}

You are the VSVN problem-analysis author on Claude Code `claude-opus-5-5`, effort `medium`; the runner sets both. You own problem analysis only. Do not propose a solution, do not design a data model, and do not write `proposal.md`, `model-design.md`, or `architecture.md`. Do not edit any file. Read only the files and sections named in the author input below, `.ai/tasks/{{TASK_ID}}/requirements-analysis.md` when it exists, `.ai/tasks/{{TASK_ID}}/task-state.yaml`, and the `Quyết định hiện hành` ledger in that task's `decision.md`.

Write `document` as the complete `problem-analysis.md`, in Vietnamese prose, keeping commands, identifiers, paths, status tokens, and column names in English. Sections:

1. `## Phạm vi`: the base task and the question being analyzed.
2. `## Bài toán`: the problem in the user's words.
3. `## Hiện trạng`: the current state, citing a file and section or cell for every fact.
4. `## Khoảng trống hoặc nguyên nhân`: the gap or cause, each tied to a `## Hiện trạng` fact.
5. `## Đối tượng bị ảnh hưởng`: affected tables, notebooks, configuration, and consumers.
6. `## Câu hỏi`: one numbered question per unknown.

A fact the named files do not show goes to `## Câu hỏi`. Write `Không áp dụng.` under a section that has no content. Never invent a `json_path`, condition, key, or rule the user has not named. Do not copy sample values, review text, person names, or URLs.
```

### New prompt: author-model.md

Create `.ai/prompts/author-model.md` with exactly:

```text
# Author handoff: model design for {{TASK_ID}}

You are the VSVN model-design author on Claude Code `claude-opus-5-5`, effort `medium`; the runner sets both. You own model design only: the data model the accepted proposal needs. This is not an Architect turn: do not write `architecture.md`, and do not design invariants, state ownership, transaction or commit boundaries, ordering, locking, watermarks, idempotency, retry, recovery, or rollout. Do not edit any file. Read only the files and sections named in the author input below, `.ai/tasks/{{TASK_ID}}/proposal.md`, `problem-analysis.md` and `requirements-analysis.md` in that task when they exist, `.ai/tasks/{{TASK_ID}}/task-state.yaml`, and the `Quyết định hiện hành` ledger in that task's `decision.md`. Follow `AGENTS.md` section 7 and `docs/context/02_NAMING_CONVENTION.md`.

Write `document` as the complete `model-design.md`, in English. Sections:

1. `## Scope`: the base task and the proposal sections and ledger rows this design implements.
2. `## Entities and grain`: table `table | layer | grain | node notebook`, one row per affected table.
3. `## Keys`: primary, business, and foreign keys per table, citing the formula source for `poi_id`.
4. `## Columns`: table `table | column | type | nullable | source | rule`, affected columns only; `rule` cites the proposal line or ledger row.
5. `## Lineage`: bronze, silver, and gold reads per affected table; gold never reads gold.
6. `## Conflicts and questions`: one numbered item per conflict with the proposal or ledger, or per unknown.

Cite `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` instead of repeating them. Write `Not applicable.` under a section that has no content. Never invent a `json_path`, condition, key, type, or rule the files do not show; ask instead. Do not copy sample values, review text, person names, or URLs.
```

### Tests

`tests/test_vv.py`:

- In `prepare_author_task`, change `for kind in ("proposal", "runbook"):` to `for kind in agent_runner.AUTHOR_KIND_LANES:`.
- `test_run_author_records_lane_by_kind` parametrize: add `("analysis", "author", "medium", "problem-analysis.md")` and `("model", "author", "medium", "model-design.md")`; ids `["analysis", "model", "proposal", "runbook"]`. The existing `other_key` expression already works.
- `test_run_author_effort_follows_kind` parametrize: add `("analysis", "medium")` and `("model", "medium")`.
- Rename `test_requirements_analyst_effort_high` to `test_requirements_analyst_effort_medium` and assert `"effort: medium" in frontmatter`. Keep the other asserts.
- Add:

```python
def test_author_kind_lanes_and_prompts() -> None:
    assert agent_runner.AUTHOR_EFFORTS == {
        "analysis": "medium", "model": "medium", "proposal": "high", "runbook": "medium",
    }
    assert agent_runner.AUTHOR_LANE_EFFORTS == {"author": "medium", "author_proposal": "high"}
    assert set(vv.AUTHOR_OUTPUTS) == set(agent_runner.AUTHOR_KIND_LANES)
    for kind in agent_runner.AUTHOR_KIND_LANES:
        assert Path(f".ai/prompts/author-{kind}.md").is_file()


def test_architect_effort_stays_high() -> None:
    assert agent_runner.ARCHITECT_EFFORT == "high"
    settings = json.loads(Path(".claude/settings.json").read_text(encoding="utf-8"))
    assert settings.get("effortLevel") == "high"


def test_prompts_split_analysis_proposal_and_model_design() -> None:
    architect = Path(".ai/prompts/architect.md").read_text(encoding="utf-8")
    assert "effort `high`" in architect
    assert "model-design.md" in architect and "--kind model" in architect
    assert "You own model design" not in architect
    proposal = Path(".ai/prompts/author-proposal.md").read_text(encoding="utf-8")
    assert "effort `high`" in proposal and "## Phân tích bài toán" not in proposal
    for kind in ("analysis", "model"):
        text = Path(f".ai/prompts/author-{kind}.md").read_text(encoding="utf-8")
        assert "effort `medium`" in text and "architecture.md" in text


def _architecture_task(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, Path]:
    task_id, directory, data = prepare_author_task(tmp_path, monkeypatch, author_input=None)
    data["task"].update(status="waiting_architecture", owner="architect")
    data["classification"]["architecture_required"] = True
    data["classification"]["signals"] = ["data_model_change"]
    data["gates"]["architecture"] = "pending"
    data["models"]["main"]["actual"] = "grok-4.7"
    (directory / "task-state.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return task_id, directory


def test_run_gate_requires_model_design_for_data_model_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id, directory = _architecture_task(tmp_path, monkeypatch)
    before = (directory / "task-state.yaml").read_bytes()

    def unreachable(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Architect must not run")

    monkeypatch.setattr(agent_runner, "run_architecture", unreachable)
    with pytest.raises(SystemExit, match="model-design.md"):
        vv.cmd_run_gate(Namespace(task=task_id, round=None, timeout=30))
    assert (directory / "task-state.yaml").read_bytes() == before


def test_run_gate_runs_architect_when_model_design_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id, directory = _architecture_task(tmp_path, monkeypatch)
    (directory / "model-design.md").write_text("# Model design\n\n## Scope\n", encoding="utf-8")
    monkeypatch.setattr(vv, "render_prompt", lambda *_args: (Path("handoff.md"), "prompt"))
    monkeypatch.setattr(agent_runner, "run_architecture", lambda *_args, **_kwargs: agent_runner.ArchitectureResult(
        verdict="PASS", document="RESULT: PASS\n\n## Main brief\n", executable=Path("claude.exe"),
    ))
    assert vv.cmd_run_gate(Namespace(task=task_id, round=None, timeout=30)) == 0
    updated = yaml.safe_load((directory / "task-state.yaml").read_text(encoding="utf-8"))
    assert updated["task"]["status"] == "implementing"
    assert updated["rounds"]["architecture"] == 1
```

`tests/test_vv_context.py` (use that file's existing state-builder; shown here as `data`):

```python
def test_data_model_change_signal_is_valid() -> None:
    data = <existing base-state builder>
    data["classification"]["signals"] = ["data_model_change"]
    assert vv.validate_state_data(data, data["task"]["id"]) == []


def test_author_lane_effort_error_reported_once() -> None:
    data = <existing base-state builder>
    data["models"]["author"] = {"expected": "claude-opus-5-5", "effort": "high", "actual": ""}
    errors = vv.validate_state_data(data, data["task"]["id"])
    assert sum("models.author.effort" in item for item in errors) == 1
```

The existing `test_optional_author_proposal_model_validation` and the author-override tests stay unchanged and must still pass.

## Verification

1. `python -m pytest tests/test_vv.py tests/test_vv_context.py tests/test_initial_ddl_contract.py::test_roles_documented -q`: all pass.
2. `python scripts/vv.py doctor`: no line containing `budget exceeded`.
3. `python scripts/vv.py run-author --help`: `--kind` lists `analysis, model, proposal, runbook`.
4. `git diff --quiet -- .claude/settings.json .ai/tasks/_template/task-state.yaml .ai/prompts/author-runbook.md`: exit 0.
5. `python scripts/vv.py verify 20261019-agent-system-claude-opus-design`: PASS.
6. Then `transition … reviewing` and `run-gate` (review round 2, the last allowed). Stop before commit.

FILE: .ai/prompts/architect.md
# Architect handoff: {{TASK_ID}}

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

You own architecture on Claude Code `claude-opus-5-5`, effort `high`. You do not own model design. Inputs when they exist: `requirements-analysis.md` (business analysis), `problem-analysis.md` (problem analysis), `proposal.md` (solution proposal), and `model-design.md` (model design: entities, grain, keys, columns, lineage; written by `run-author --kind model` at effort `medium`). They never replace this design, and this design never writes or extends model design: cite `model-design.md` headings for grain and keys. If the task changes a table, column, grain, or key and `model-design.md` is missing, or if it conflicts with the ledger or cannot satisfy an invariant, return `RESULT: EVIDENCE_REQUIRED`, state the gap or conflict, and name `python scripts/vv.py run-author {{TASK_ID}} --kind model` as the blocking step.

The generated context pack at the end of this prompt already holds the task state, the request, the `decision.md` ledger, and the task file list; do not re-read them. Open the whole `decision.md` only for a decision the ledger points to. Then read the evidence and the source and context files the design needs. For files over 20 KB, use the generated table of contents: read a Markdown line range, or `Grep` a notebook function name or cell id with context, instead of reading the whole file. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

Produce only `.ai/tasks/{{TASK_ID}}/architecture.md`. In an interactive handoff, write that file directly. When an automated contract requests structured output, do not edit the repository; return the content through that contract.

The first non-blank line is `RESULT: PASS` or `RESULT: EVIDENCE_REQUIRED`. Cover: scope, non-goals, invariants, state ownership, grain and keys, ordering, transaction and commit boundaries, idempotency, concurrency, retry and recovery, partial failure, observability, security, rollout, rollback and forward recovery, implementation plan, and verification. Compare material alternatives and explain the selected trade-off. Write a section that does not apply as one line: `Not applicable: <reason>`.

Size: for `low` or `medium` risk, keep the document under 25 KB, excluding `FILE:` blocks. For `high` or `critical` risk, use the space the failure analysis needs, without repeating the request or the evidence.

Files that Main must save verbatim go in blocks: a line `FILE: <repo-relative path>`, the exact content, then a line `END_FILE`. Every path must be in `scope.files`.

## Main brief contract

Return a separate Main brief, at most 14,000 characters, in English. It is the only part Main reads by default. Use `###` headings only, in this order:

1. `Decision`: at most 5 lines.
2. `Invariants Main must preserve`: at most 10 testable bullets.
3. `Edit list`: table `# | file | anchor (cell id, function, or heading) | change | done-when`, one row per anchor.
4. `Order and stop points`: numbered; mark each stop for evidence or a user decision.
5. `Tests and verification`: exact test names and commands.
6. `Read only if needed`: full-document headings mapped to the edit rows they justify.

Do not restate the request or the evidence in the brief. Code longer than 15 lines goes in the full document under a heading the edit list references.

If evidence is missing, list exact probes and the decisions each one blocks. Do not implement code, update task state, or fill gaps with assumptions.
END_FILE

FILE: .ai/prompts/author-proposal.md
# Author handoff: proposal for {{TASK_ID}}

You are the VSVN proposal author on Claude Code `claude-opus-5-5`, effort `high`; the runner sets both. You own the solution proposal only. Problem analysis is `problem-analysis.md` (`run-author --kind analysis`, effort `medium`) and model design is `model-design.md` (`run-author --kind model`, effort `medium`); do not write either here. This is not an Architect turn: do not write `architecture.md`, and do not design invariants, state ownership, commit boundaries, ordering, idempotency, retry, or recovery. Do not edit any file. Read only the files and sections named in the author input below, `.ai/tasks/{{TASK_ID}}/problem-analysis.md` when it exists, `.ai/tasks/{{TASK_ID}}/task-state.yaml`, and the `Quyết định hiện hành` ledger in that task's `decision.md`.

Write `document` as the complete `proposal.md`, in Vietnamese prose, keeping commands, identifiers, paths, status tokens, and column names in English. Sections:

1. `## Phạm vi`: the base task, and the statement that every line not named in the input stays as last decided.
2. `## Căn cứ`: the `problem-analysis.md` headings this proposal answers, cited by heading; do not restate or extend the analysis. Without `problem-analysis.md`, write `Không áp dụng.` and put every fact the proposal needs but the named files do not show under `## Câu hỏi`.
3. `## Giải pháp đề xuất`: the viable options, the selected one, and why.
4. `## Dòng thay đổi`: table `Bảng | Cột | Hành động cũ (đã land) | Hành động mới`.
5. `## ctrl_cfg_schema_registry`: only the affected rows.
6. `## Ràng buộc cho Architect`
7. `## Câu hỏi`: one numbered question per unknown.

Write `Không áp dụng.` under a section that has no content. Never invent a `json_path`, condition, key, or rule the user has not named; ask instead. Do not copy sample values, review text, person names, or URLs.
END_FILE
