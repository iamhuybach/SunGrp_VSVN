# VSVN agent-system token optimization plan

| Field | Value |
|---|---|
| Plan date | 2026-10-14 |
| Plan author | Claude Code, `claude-opus-5-5`, effort `high`. The user designated it Main for this planning task. In repository role terms this document is the task's architecture. |
| Implementer | Codex, `gpt-5.6-sol`, effort `medium`, in a session with a writable workspace. The user approved this on 2026-10-14. |
| Reviewer | Codex review lane through `python scripts/vv.py run-gate <task-id>`. It runs as a separate, read-only process. |
| Goal | Cut Cursor Grok 4.7 Medium token use without reducing the agents' capability, gate discipline, or review quality. |
| Language | English, per `AGENTS.md` §1. Appendix A is Vietnamese because `docs/AGENT_PROMPT_SAMPLES.md` is Vietnamese by user request. |

---

## 0. How Codex uses this document

1. This document is the source of truth. Do not repeat the analysis in §1–§5. Implement §6 phase by phase, in order.
2. Every phase lists files, exact steps, acceptance checks, and rollback. A phase is done only when its acceptance checks pass.
3. Decision points D1–D3 (§5.13) belong to the user. Before Phase 1, ask the user once for D1–D3 and record the answers in `decision.md`. If the user answers "theo khuyến nghị", use the recommendation. Skip the steps marked for a decision that is answered "no".
4. If the repository differs from what this document describes, stop and report it. Examples: a file is missing, a function signature changed, or a test already fails. Do not improvise a different design. Record any deviation in `decision.md` (Vietnamese) before continuing.
5. Do not commit, push, merge, or rewrite history. Do not change model IDs or efforts in `.codex/config.toml`, `.codex/agents/*.toml`, or `.claude/settings.json`.
6. Read budget for Codex: this document, the files a step names, and the tests. Do not read `notebooks_lgc/`, `docs/context/3p-google/*.txt`, or `.ai/tasks/*/evidence/context/`.

Kickoff prompt for the Codex implementer session. Start Codex with a writable sandbox, for example `codex --sandbox workspace-write --ask-for-approval on-request`, or in the IDE extension's Agent mode. The project `.codex/config.toml` stays read-only for the review lane.

```text
Thực hiện kế hoạch tại docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md, bắt đầu từ §0 rồi §6 Phase 0.
Hỏi tôi D1–D3 một lần trước Phase 1. Dừng ở mỗi điểm dừng trong §6 và báo kết quả acceptance của phase.
Không commit, push, merge. Không đổi model/effort trong .codex/ hoặc .claude/.
```

---

## 1. Baseline measured on 2026-10-14

Token figures are rough estimates: about 4 characters per token for English and about 3 for mixed Vietnamese. Phase 0 replaces them with the user's real Cursor usage.

### 1.1 Instructions that load on every Main request

| Item | Size | ≈ tokens | Loaded |
|---|---:|---:|---|
| `AGENTS.md` | 12.8 KB | 3.2k | Cursor loads it automatically as a root rule. `00-main-orchestrator.mdc` step 1 and the `vsvn-task-workflow` skill also say "Read `AGENTS.md`", which can add a second copy. |
| `.cursor/rules/00-main-orchestrator.mdc` (`alwaysApply`) | 5.4 KB | 1.4k | Every request, including explain-only questions. About 45% of it is closeout detail. |
| Skill descriptions (4 skills) | ~1.5 KB | 0.4k | Every request |
| **Fixed preamble per request** | **~20 KB** | **~5k** | It is re-sent on every agent step (tool call) of a turn. |

### 1.2 Task artifacts that Main is told to read

The current rule, step 3, says to read "`task-state.yaml`, `request.md`, decisions, evidence, architecture, and reviews before acting".

| Task | architecture.md | decision.md | evidence (excluding copies) | evidence/context copies |
|---|---:|---:|---:|---:|
| 20261013-3p-extract-from-raw-payload | 61.5 KB | 49.6 KB | ~60 KB | **1.45 MB** (duplicates of `docs/context/3p-google/*`) |
| 20261011-requirements-templates-and-analyst | 114 KB (contains full files) | 5.4 KB | small | — |
| 20261011-notebook-design-skills | 71 KB (contains full files) | 3.4 KB | small | — |
| 20261014-3p-raw-payload-field-corrections | 52.9 KB | 7.0 KB | small | — |
| 20261009-normalize-l1-timestamps-audit-columns | 38.7 KB | 2.8 KB | ~180 KB results | — |

### 1.3 Source that Main reads whole

| Notebook | File | Source only | JSON lines |
|---|---:|---:|---:|
| `NB_LIB_EXTRACT_RAWDATA.ipynb` | 183 KB (≈50k tok) | 139 KB | 2,938 |
| `NB_CREATE_DDL.ipynb` | 130 KB (≈35k) | 87 KB | 2,474 |
| `NB_LIB_TRANSFORM_SLV_GLD.ipynb` | 125 KB (≈33k) | 95 KB | 2,130 |
| `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` | 70 KB (≈19k) | 53 KB | 1,084 |
| `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` | 57 KB (≈15k) | 43 KB | 887 |

Other large items: `notebooks_lgc/` (3.0 MB, legacy), `docs/context/3p-google/ward_mapping_satnhap.txt` (1.19 MB), and `pipelines/*/manifest.json` (75 KB). The repository has no `.cursorignore` or `.cursorindexingignore`.

### 1.4 Work pattern from 14 tasks (2026-10-08 → 2026-10-14)

- 10 of 14 tasks are classified `complexity: high`. Architecture round 2 happened in 3 tasks and review round 2 in 5 tasks.
- 6 tasks are not in a terminal state (`reviewing`, `user_decision` ×2, `implementing`, `waiting_runtime`, `waiting_evidence`). Some are stale: `20261009-normalize-l1-timestamps-audit-columns` is still `implementing`, but its feature commit `5c79224` has landed.
- Two tasks called Claude by hand as a "proposal author" at `medium` effort, using prompts that Grok wrote (`handoffs/proposal-prompt.md`, 6.5 KB and 3.3 KB), plus a free-form `model_policy_exception` block in `task-state.yaml`. One of those invocations failed because Claude reported its own effort wrongly.
- Two tasks carried full files inside `architecture.md`, which Main then had to copy verbatim. One task used a hand-written Python extractor to do it.

---

## 2. Where Main's tokens go

For one Cursor agent turn:

```text
turn_tokens ≈ Σ over steps [ fixed_preamble + conversation_so_far + tool_outputs_so_far ]   (input, mostly cached)
            + Σ over steps [ reasoning + visible output ]                                     (output)
```

Four multipliers drive the bill, in order of impact:

1. **Read set size.** Every file Main reads stays in the conversation and is re-sent on every later step. For a heavy "resume + implement" turn on a task like 20261013, the current instructions point Main at roughly **190k tokens**: preamble ~6k, task artifacts ~52k, notebooks ~104k, and context docs ~31k. That is more than one context window, so Cursor also summarizes, which costs more tokens.
2. **Steps per turn.** A 40-tool-call turn with a 100k-token conversation re-sends about 4M input tokens, cached or not.
3. **Chat length.** The prompt samples ask for the whole chain (triage → evidence → architecture → implement → verify → review → runbook) in one chat, so context only grows.
4. **Output.** Main writes long Vietnamese documents (`decision.md` up to 49.6 KB, runbooks of 7–14 KB), copies file blocks verbatim (up to 100 KB), and drafts prompts for other agents.

The model's price per token is a smaller lever than these four. The target design attacks multipliers 1–4 first and leaves the model choice as a separate decision (D1).

---

## 3. Problem inventory

Each row gives the evidence, the impact, and the fixing solution (§5).

### 3.1 Model

| ID | Problem | Evidence | Impact | Fix |
|---|---|---|---|---|
| M1 | One model and one effort for all Main work. Mechanical steps spend medium reasoning. | Main copies file blocks, writes closeouts, edits state, drafts prompts | Reasoning and output tokens are spent where scripts would do | SOL-04, SOL-07, D1 |
| M2 | Model exceptions are ad hoc. | `model_policy_exception` (~2 KB) in 20261013 state. The validator rejects any non-default effort, so exceptions live in untyped keys. One run failed because Claude misread its own effort ("reasoning_effort=10"). | Extra Main turns, state bloat, and failed runs | SOL-09, SOL-10 |
| M3 | Architect `high` output has no size contract, and Main consumes all of it. | 7 architecture docs of 38–114 KB | 15–30k tokens per read, repeated on every resume | SOL-06 |
| M4 | (Keep.) The review lane is efficient: diff-only, P0/P1-only, reports of 0.7–14 KB. | `.ai/prompts/review.md`, `.codex/agents/*.toml` | None | No change |
| M5 | Long Vietnamese artifacts cost more tokens per character, and Main both writes and re-reads them. | `decision.md` of 49.6 KB with superseded tables | High re-read cost; superseded rows confuse later turns | SOL-08, SOL-10 |

### 3.2 Agents

| ID | Problem | Evidence | Impact | Fix |
|---|---|---|---|---|
| A1 | Main holds six jobs: orchestrator, implementer, document author, verbatim copier, closeout writer, and prompt writer for other agents. | Tasks 20261011-*, 20261013, 20261014 | Grok tokens go to non-coding work | SOL-04, SOL-07, SOL-10 |
| A2 | The Architect → Main handoff has no compact form. | Architect returns one `document` field | Main reads 40–114 KB to find its edit list | SOL-06 |
| A3 | No session-continuity artifact exists, so every new chat rebuilds state from all artifacts. | Rule step 3; sample 10 says "tất cả task artifact" | The full read set is paid on every resume | SOL-05, SOL-08 |
| A4 | Off-gate Claude/Codex calls (proposal author, performance review) need hand-written prompts. | `handoffs/proposal-prompt.md`, `performance-review-prompt.md` | 3–7 KB of Grok output each time, plus prompt errors | SOL-10 |

### 3.3 Skills and rules

| ID | Problem | Evidence | Impact | Fix |
|---|---|---|---|---|
| S1 | The always-apply rule is 5.4 KB and about 45% closeout detail. | `.cursor/rules/00-main-orchestrator.mdc` | ~0.7k tokens wasted on every step of every request | SOL-02 |
| S2 | `AGENTS.md` (12.8 KB) is auto-loaded, and the rule and skill also say to read it. Many sections do not concern Main on a given step (routing detail, commands, statuses). | `AGENTS.md` §4–§7, §10 | Fixed preamble about 2× larger than needed | SOL-03 |
| S3 | Workflow facts are duplicated in five places: `AGENTS.md` §6, the rule, the skill, `SETUP.md`, and the prompt samples. | — | Repeated tokens and drift | SOL-02, SOL-03, SOL-11 |
| S4 | The notebook skills (15–19 KB) do not say how to read a notebook, so Main reads the whole `.ipynb`. | `vsvn-extract-notebook`, `vsvn-notebook-library` | 15–50k tokens per notebook touch | SOL-05 |
| S5 | No guard stops instruction or context bloat from coming back. | `vv.py doctor` checks presence only | Regression | SOL-12 |

### 3.4 Flow

| ID | Problem | Evidence | Impact | Fix |
|---|---|---|---|---|
| F1 | One long chat spans several phases. | Samples 1, 4, 8, 19 | Context grows, and every step re-sends it | SOL-01 |
| F2 | Resume reads every artifact. | Rule step 3, sample 10 | ~50k+ tokens before any work | SOL-05 |
| F3 | Documents that carry files: Main retypes file blocks. | 20261011-* tasks | 50–100k output tokens | SOL-07 |
| F4 | Proposal-only turns get full high/high classification. | 20261014: `high/high`, architecture and runtime required for a proposal | Heavier ceremony and more reading | SOL-11 (proposal lane) |
| F5 | Rework rounds re-read everything. | Architecture round 2 ×3, review round 2 ×5 | Each round repeats the full read set | SOL-05, SOL-06, SOL-08 |
| F6 | `verify` prints full tool output to Main, and the log keeps growing. | `verify.log` up to 12 KB | Small but frequent | SOL-04 |
| F7 | Large data and legacy files are indexed, and context files are copied into tasks. | 1.45 MB under `evidence/context/`; 3 MB `notebooks_lgc/` | Semantic search pulls chunks into context | SOL-02 (ignore files), SOL-03 (rule) |
| F8 | Stale non-terminal tasks. | §1.4 | Main may scan them to orient | SOL-05 never lists other tasks; user cleanup is optional |

### 3.5 Prompt samples (`docs/AGENT_PROMPT_SAMPLES.md`, 37.8 KB, 22 cases)

| ID | Problem | Fix |
|---|---|---|
| P1 | Each sample repeats boilerplate that the rules already enforce: follow `AGENTS.md`, record Grok, no commit, stop on fallback. | Appendix A: one shared skeleton; the boilerplate stays in the rule. |
| P2 | No sample has an explicit read list, and several ask for broad reads ("tất cả task artifact", "tất cả project rule, skill có liên quan", "Đối chiếu `notebooks/` và `docs/context/`"). | Every sample has a `Context` block plus a repository context map. |
| P3 | End-to-end samples encourage one long chat. | Samples are organized by phase, with one chat per phase. |
| P4 | One-off exceptions are stored as reusable samples (15, 21, 22) and fight the validator. | Formal `exceptions` field (SOL-09) and author lane (SOL-10). |
| P5 | Domain samples (5, 6, 7) restate rules that attach by glob anyway. | Merged into one triage sample with a domain line. |

---

## 4. Target design

### 4.1 Principles

1. **Deterministic context first.** A script assembles what Main needs (state, resume note, request essentials, decision ledger, architecture brief) in a bounded output. The LLM does not explore to find it.
2. **Read by anchor.** Files over 20 KB are read by heading or notebook cell, never whole by default.
3. **One chat per phase.** Every stop writes `resume.md`, and the next phase starts a new chat.
4. **Scripts do mechanical work.** Copying file blocks, closeout skeletons, compact verification, and state bookkeeping are done by `vv.py`.
5. **Long prose is written outside Cursor when it is not code.** Proposals and runbooks can come from the Claude author lane (D2).
6. **Budgets are linted.** `doctor` warns when instruction files grow past their budgets.
7. **Gates do not change.** Evidence, architecture, review, risk gate, runtime, round caps, and user authority stay exactly as they are.

### 4.2 Roles after the change

| Role | Runtime | Change |
|---|---|---|
| Main | Cursor, Grok 4.7 Medium | Same authority. Reads through `vv.py context` / `toc` / `show`. Does not retype file blocks. Writes `resume.md` at every stop. |
| Architect | Claude Code, Opus 5.5 High | Same authority. Must also return a `main_brief` of at most 14,000 characters, which the runner places at the top of `architecture.md`. Size guidance per risk level. |
| Author (D2) | Claude Code, Opus 5.5 Medium, through `vv.py run-author` | New, narrow lane. Writes `proposal.md` or `runtime-runbook.md` on Main's request. The runner persists the output and records the model and effort from the CLI flags. |
| Review Coordinator and specialists | Codex, GPT-5.6 Sol Medium | No change. |
| Local Verifier | `vv.py verify` | Compact stdout by default; `--full` keeps today's output. |
| Gate runner | `vv.py run-gate` | Composes `architecture.md` with the brief. |

### 4.3 Phase-sliced flow and read budgets

```text
chat 1  TRIAGE      new → classify → (probes → STOP waiting_evidence) | (run-gate architecture → STOP) | fast lane → done
chat 2  EVIDENCE    results → interpret into ledger → run-gate architecture → STOP
chat 3  IMPLEMENT   context pack + Main brief + edit-list cells → code → verify → run-gate review → STOP
chat 4  REMEDIATE   context pack (P0/P1 rows) + cited lines → fix → verify → run-gate round 2 → STOP
chat 5  RUNTIME     runbook (author lane or Main) → vv.py closeout → STOP waiting_runtime
chat 6  CLOSE       user results → runtime gate → closeout → user commits
```

| Phase | Default read set | Budget (≈ tokens) |
|---|---|---:|
| any | Rule, `AGENTS.md` core, skill descriptions | ≤ 3.5k |
| triage | Request text, `WORKFLOW.md` §Classification and §Review routing, named context sections | ≤ 15k |
| evidence | Context pack, probe headers, results | ≤ 15k |
| implement | Context pack (≤ 400 lines), Main brief, edit-list cells/sections | ≤ 35k |
| remediate | Context pack (P0/P1 rows), cited `file:line` ranges | ≤ 20k |
| runtime / close | Context pack, closeout skeleton | ≤ 10k |

Against §2 (~190k), the implement phase target is ~35k, about **−80% on the read set**. Shorter chats and fewer steps compound this. The overall target is in §7.

### 4.4 New and changed task artifacts

| Artifact | Owner | Language | Contract |
|---|---|---|---|
| `resume.md` (new, task root) | Main | English | Overwritten at every stop. At most 40 lines. Sections: `Status`, `Done this session`, `Next action`, `Read next` (path + anchor), `Waiting on`. |
| `architecture.md` → `## Main brief` (new section) | Architect, through the runner | English | At most 14,000 characters, directly after the `RESULT:` line. Uses only `###` sub-headings. Contents: Decision; Invariants Main must preserve; Edit list (`# \| file \| anchor \| change \| done-when`); Order and stop points; Tests and verification; Read only if needed (full-document headings → edit rows). |
| `decision.md` → `## Quyết định hiện hành` (new ledger) | Main | Vietnamese | Directly after `# Quyết định`. Table `ID \| Chủ đề \| Quyết định hiện hành \| Nguồn (mục) \| Ngày`. A superseded row is edited in place; details are appended under `## Lịch sử quyết định`. |
| `task-state.yaml` → `exceptions` (new, optional) | Main | English | Typed list (SOL-09). Replaces free-form `model_policy_exception` blocks for new tasks. |
| `proposal.md` (D2) | Author lane, through the runner | Vietnamese | Proposal for the user. `decision.md` ledger rows point to it. |
| `handoffs/author-input.md` (D2) | Main | English, user comments verbatim | At most 60 lines: user comments verbatim, files and anchors the author may read, constraints. |

Existing tasks are not migrated. `vv.py context` falls back to tables of contents when the ledger or brief is missing.

### 4.5 New `vv.py` commands

| Command | Purpose |
|---|---|
| `vv.py toc <path>` | `.md`: headings with line ranges and sizes. `.ipynb`: cells with index, id, type, JSON line range, source line count, label, and `def` names. |
| `vv.py show <path> <anchor> [--max-lines N]` | Prints one Markdown section or notebook cell(s) as plain source. |
| `vv.py context <task-id> [--phase P] [--max-lines N]` | Bounded context pack for the phase. |
| `vv.py verify … [--full]` | Compact by default. |
| `vv.py materialize <task-id> [--source F] [--write]` | Extracts `FILE:` / `SKILL_FILE:` blocks byte-for-byte to allowed paths. |
| `vv.py closeout <task-id>` | Vietnamese four-section closeout skeleton built from state, probes, and runbook. |
| `vv.py run-author <task-id> --kind proposal\|runbook` (D2) | Claude author lane. |

---

## 5. Solutions: pros, cons, impact, and trade-offs

Saving estimates are rough. §7 states how they are measured.

### SOL-01 One chat per phase

- **What:** Prompt samples and the rule end every phase with `resume.md` and suggest a new chat.
- **Pros:** Removes accumulated-history re-sends (multipliers 2–3). This is the largest single lever for long tasks. Cursor summarizes less often.
- **Cons:** The user starts more chats. Some tacit knowledge from the earlier chat is lost.
- **Impact:** Operator habit changes, and the prompt samples are reorganized.
- **Trade-off and mitigation:** Lost knowledge is covered by `resume.md` plus the deterministic context pack. A phase can continue in the same chat when it is short. Fast lane stays one chat.
- **Estimated saving:** 30–50% of cached input on multi-phase tasks.

### SOL-02 Lean always-apply rule, closeout moved to the skill, ignore files

- **What:** Replace `00-main-orchestrator.mdc` with Appendix B (≤ 3 KB). Move the closeout rules into the `vsvn-task-workflow` skill (Appendix D). Add `.cursorindexingignore` and `.cursorignore` (Phase 3).
- **Pros:** Every step of every request gets cheaper. The index stops surfacing legacy and data files.
- **Cons:** Closeout details load only when the skill is selected, so Main could skip a detail.
- **Impact:** The behavioral contract stays: the four headings are still mandatory in the rule. `vv.py closeout` generates the content.
- **Trade-off and mitigation:** Keep the four-heading contract in the rule and use the generator. `.cursorindexingignore` only removes files from the index; the agent can still open them when a prompt names them. `.cursorignore` is used only for caches.
- **Estimated saving:** ~1k tokens per step.

### SOL-03 Split `AGENTS.md` into a core file and `docs/agent-system/WORKFLOW.md`

- **What:** `AGENTS.md` keeps roles, language, model policy, the new context discipline, severity, evidence, platform invariants, and prohibited actions (Appendix C, ≤ 8 KB). Statuses and transitions, classification, workflow, review routing, and commands move verbatim to `WORKFLOW.md`, which is read at triage or on demand.
- **Pros:** The preamble shrinks for all three tools (Cursor, Codex, and Claude all load `AGENTS.md`). Each fact has one home.
- **Cons:** An agent that needs routing or classification must open `WORKFLOW.md`. Risk of missing a rule.
- **Impact:** Triage reads one extra file section once per task. Reviewers are unaffected: their scope is in their own `.toml`, and severity stays in the core.
- **Trade-off and mitigation:** Keep every invariant and prohibition in the core. The skill points to the exact `WORKFLOW.md` sections. Run `external-smoke` after the change (user step).
- **Decision:** D3.
- **Estimated saving:** ~1.5–3k tokens per step.

### SOL-04 Compact verification output

- **What:** `verify` prints one line per tool, plus the first 40 lines of output only for failing tools. `--full` keeps the old output. The log stays complete.
- **Pros:** Small but frequent saving, and failures stay visible.
- **Cons:** Main may need `--full` to diagnose.
- **Trade-off:** The 40 failing lines are usually enough; Main uses `--full` when they are not.

### SOL-05 Context pack plus anchor reads (`context`, `toc`, `show`)

- **What:** Deterministic, bounded context per phase. Notebooks and large docs are read by cell or section.
- **Pros:** The biggest read-set cut (resume ~50k → ~6k; notebook touch 15–50k → 2–10k). Deterministic: the same pack every time.
- **Cons:** New tooling to maintain. Main may still miss a dependency outside the listed cells.
- **Impact:** The rule makes `context` the first command, and the skills explain `toc`/`show`.
- **Trade-off and mitigation:** Main may read more when the brief's "Read only if needed" map or a failing test points there. Reviewers still read the full diff and architecture, so a missed dependency is caught there. If a notebook's JSON layout changes, the cell-to-line mapping degrades gracefully: no line ranges, but source is still shown.
- **Estimated saving:** 60–85% of the read set.

### SOL-06 Architect `main_brief` and size guidance

- **What:** The architecture output schema gets a required `main_brief` field. The runner composes `RESULT` line + `## Main brief` + the rest. The Architect prompt gets size guidance: low/medium risk ≤ 25 KB excluding file blocks; non-applicable sections become one line, "Not applicable: <reason>".
- **Pros:** Main reads 3–4k tokens instead of 15–30k. Claude also writes less, so runs are faster. Reviewers still get the full document.
- **Cons:** The brief can drop a nuance. One more schema field could fail a run.
- **Impact:** Changes `agent_runner.run_architecture`, the prompt, and tests. The smoke test must be re-run.
- **Trade-off and mitigation:** The brief has a mandatory "Read only if needed" map, and reviewers read the full document. Structured output enforces `maxLength`. The runner demotes stray `## ` headings inside the brief to `### ` and does not fail the run for it.

### SOL-07 `materialize` file blocks

- **What:** A script extracts `FILE:`/`END_FILE` and legacy `SKILL_FILE:`/`END_SKILL_FILE` blocks byte-for-byte. Paths must be listed in `scope.files`. Dry run is the default.
- **Pros:** Removes 50–100k output tokens on file-carrier tasks, and copies are exact.
- **Cons:** A wrong path could overwrite a file.
- **Trade-off and mitigation:** `scope.files` allowlist, dry run by default, and refusal of `..`, absolute paths, `.git/`, and `task-state.yaml`.

### SOL-08 `resume.md` and the decision ledger

- **Pros:** Resume cost is bounded. Superseded decisions stop confusing later turns (the 20261014 prompt needed a paragraph to explain "later sections override earlier tables").
- **Cons:** Main must keep the ledger and history in sync, which costs a little output.
- **Trade-off and mitigation:** The ledger copies decision text verbatim from its source section, with no rewording. `context` prints a warning when `decision.md` has no ledger.

### SOL-09 Typed `exceptions` in `task-state.yaml`

- **What:** Optional list. The validator accepts `models.<role>.actual` equal to the default model or to the model of an approved `model_override` exception for that role. The runner records model and effort from the flags it passed and never asks a model to report its own effort.
- **Pros:** Ends untyped exception blocks and validator workarounds, and makes user approval auditable.
- **Cons:** Could be used to bypass the model policy.
- **Trade-off and mitigation:** Each entry needs `approved_by: user`, a date, and a scope sentence. It is mirrored in `decision.md`, and `context` prints active exceptions.

### SOL-10 Author lane `run-author` (D2)

- **What:** Main writes a ≤ 60-line `author-input.md`. The runner calls Claude Opus 5.5 at medium effort with read-only tools and a fixed prompt template, then persists `proposal.md` or `runtime-runbook.md`.
- **Pros:** Moves 5–15k output tokens per proposal or runbook off Cursor, and replaces hand-written prompts with templates. Same immutability checks as the architecture gate.
- **Cons:** Uses Claude quota, which the Architect also uses. A runbook from the author lane may miss notebook-level parameter values.
- **Impact:** New runner function, CLI command, templates, tests, and `models.author` handling.
- **Trade-off and mitigation:** Limit it to two kinds (proposal, runbook) and measure Claude quota in Phase 6. The runbook template forces "ask, don't guess" for unknown parameters, and Main checks parameter values against the parameter cell through `show`.
- **Decision:** D2.

### SOL-11 Prompt samples rewritten by phase (Appendix A)

- **Pros:** Each prompt is a fraction of the old length, scopes its reads explicitly, has no duplicated rules, and includes a repository context map.
- **Cons:** Operators must learn the new layout, and the old sample numbers change.
- **Trade-off and mitigation:** A table at the top maps situation → sample, and each old case is covered (see the mapping in Phase 5).

### SOL-12 Budget lint in `doctor`

- **What:** Warnings (not failures) when budgets are exceeded: `AGENTS.md` > 8,192 bytes; total size of always-apply rules > 4,096 bytes; any `SKILL.md` > 20,480 bytes; `docs/AGENT_PROMPT_SAMPLES.md` > 25,600 bytes; `.cursorindexingignore` missing.
- **Pros:** Prevents regression. **Cons:** None material.

### 5.13 Decision points for the user

| ID | Question | Recommendation | Why |
|---|---|---|---|
| D1 | Allow Grok 4.7 **Low** for mechanical prompts (explain, resume-status, closeout, runtime result logging)? | **Defer.** Decide after one week of measurements from Phases 1–5. If adopted, it needs the eval run from `SETUP.md` and a validator change. | Scripts already remove most of the mechanical reasoning, and the capability risk is not measured yet. |
| D2 | Adopt the Claude author lane for `proposal` and `runbook`? | **Adopt.** | It formalizes what the user already does by hand, with typed state and templates. |
| D3 | Split `AGENTS.md` into a core file and `WORKFLOW.md`? | **Adopt.** | Saves preamble on every step for all three tools; invariants stay in the core. |

Rejected alternatives:

- Replacing Grok with a cheaper Main model wholesale: unmeasured capability loss.
- Translating `docs/context` to English: large effort, risk of drift, and it is the user's working pack.
- Skipping architecture or review for high-risk tasks: quality loss.
- Cursor subagents for review: they consume Cursor quota, which the setup avoided on purpose.
- Codex as the default implementer: it would weaken review independence. It stays a per-task exception, as in this task.

---

## 6. Implementation phases (Codex)

### Phase 0: task setup and baseline

1. Run `python scripts/vv.py new optimize-agent-token-usage`. The printed ID is `<T>` below.
2. Write `.ai/tasks/<T>/request.md` (English):
   - User outcome: reduce Cursor Grok 4.7 Medium token use without reducing agent capability. Rewrite `docs/AGENT_PROMPT_SAMPLES.md` with explicit context scopes.
   - Scope: the files in step 3. Out of scope: notebooks, pipelines, schemas, `.codex/`, `.claude/`, model IDs and efforts.
   - Acceptance: §7 of this plan.
   - Constraints: §0 of this plan.
3. Edit `task-state.yaml`:
   - `title: Optimize agent-system token usage`
   - `classification`: `complexity: high`, `risk_level: medium`, `architecture_required: true`, `evidence_required: false`, `runtime_required: false`, `signals: [design_tradeoffs, cross_state_impact, deep_reasoning_required]`
   - `scope.systems: [cursor-main, claude-architect, codex-review, vv-runner]`
   - `scope.files`: `scripts/vv.py`, `scripts/agent_runner.py`, `tests/test_vv.py`, `tests/test_vv_context.py`, `tests/fixtures/sample_notebook.ipynb`, `.ai/tasks/_template/decision.md`, `.ai/tasks/_template/resume.md`, `.ai/tasks/_template/task-state.yaml`, `.ai/prompts/architect.md`, `.ai/prompts/author-proposal.md`, `.ai/prompts/author-runbook.md`, `AGENTS.md`, `docs/agent-system/WORKFLOW.md`, `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md`, `.cursor/rules/00-main-orchestrator.mdc`, `.cursor/skills/vsvn-task-workflow/SKILL.md`, `.cursor/skills/vsvn-extract-notebook/SKILL.md`, `.cursor/skills/vsvn-notebook-library/SKILL.md`, `.cursorindexingignore`, `.cursorignore`, `SETUP.md`, `docs/AGENT_PROMPT_SAMPLES.md`, `docs/context/00_README.md`
   - `review_plan.required_reviewers: [state-correctness-reviewer]`. Reason: validator, gate, and runner state transitions change. Risk is `medium`, so no risk gate.
4. Write `.ai/tasks/<T>/architecture.md`:
   ```text
   RESULT: PASS

   # Architecture

   The architecture for this task is `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md`, written on 2026-10-14 by Claude Code (`claude-opus-5-5`, effort `high`) in an interactive session the user requested. Reviewers read that file as this task's architecture.
   ```
   Set `gates.architecture: pass`, `models.architect.actual: claude-opus-5-5`, and `rounds.architecture: 1`.
5. Write `decision.md` (Vietnamese). Under `## Quyết định của người dùng`, record: (a) the 2026-10-14 role assignment: Claude Code wrote the plan, Codex implements in place of Grok Main, and Codex reviews through `run-gate`; (b) the D1–D3 answers once asked.
6. **Baseline (user step, stop here once).** Ask the user to open Cursor dashboard → Usage and report the aggregate for the last 7 days: total tokens, number of requests, and the share for Grok 4.7. They paste only aggregate numbers into `.ai/tasks/<T>/evidence/results/cursor-usage-baseline.md`; this path is git-ignored. Also ask the user to confirm in Cursor that `AGENTS.md` shows as an active rule in a new chat. Record the answer: it decides whether Appendix B keeps "do not re-read AGENTS.md".
7. Ask D1–D3 and record the answers.

**Acceptance:** `python scripts/vv.py validate <T>` passes, and the task stays at `triage` until Phase 1 step 1 lands.

### Phase 1: `vv.py` tooling, no behavior change for agents

All new code goes in `scripts/vv.py`, uses only the standard library plus PyYAML (already used), and follows the existing style.

1. **`exceptions` validation (SOL-09).** In `validate_state_data`:
   - `exceptions` is optional. If present, it must be a list of mappings with the keys `id` (unique), `kind` (`model_override`), `role` (`main|architect|review|author`), `model`, `effort` (`low|medium|high`), `runtime`, `approved_by` (must be `user`), `approved_on` (ISO date), and `scope` (non-empty string).
   - In the `required_actual_models` check, accept `actual == expected_models[role]` **or** `actual` equal to the `model` of a `model_override` for that role. Leave the `expected` and `effort` checks unchanged.
   - Do not validate or reject legacy untyped keys such as `model_policy_exception`.
   - Then record this task's exception and move it to `implementing`:
     ```yaml
     exceptions:
     - id: EXC-01
       kind: model_override
       role: main
       model: gpt-5.6-sol
       effort: medium
       runtime: codex-cli
       approved_by: user
       approved_on: '2026-10-14'
       scope: Codex implements docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md in place of Cursor Main.
     ```
     Set `models.main.actual: gpt-5.6-sol`, run `vv.py transition <T> implementing`, then run `validate`.
2. **`toc` and `show`.** Helper functions, so they can be tested:
   - `markdown_toc(text) -> list[Heading]` with `level`, `title`, `start`, `end` (1-based, inclusive). Ignore lines inside fenced code (```` ``` ```` or `~~~`). A section ends before the next heading of the same or higher level.
   - `notebook_cells(path) -> list[Cell]` with `index`, `id`, `cell_type`, `source`, `json_start`, `json_end`. Map JSON lines by matching `^   "cell_type": ` in the raw file (Fabric exports a one-space indent and cells start at three spaces). The cell starts one line earlier and ends one line before the next cell's start, or before the closing `]` of `cells`. If the match count differs from `len(cells)`, set the line fields to `None`.
   - `toc` output for `.ipynb`, one line per cell: `[<i>] <type> id=<id> json=<a>-<b> lines=<n> | <label> | defs: <names>`. The label is the first markdown heading, or the first non-blank, non-comment code line, truncated to 80 characters. `defs` are the names matched by `^\s*def (\w+)` and `^\s*class (\w+)`.
   - `show` anchors:
     - `.md`: a heading-text prefix, case-insensitive, matched after stripping `#` (for example `4.` or `Main brief`), or `L<a>-L<b>`. If more than one heading matches, fail and list the candidates.
     - `.ipynb`: `cell:<i>`, `cell:<i>-<j>`, `id:<cell id>`, `def:<name>` (cell containing `def <name>(`), or `grep:<regex>`. `grep` lists `cell <i> line <k>: <text>` with one line of context and does not print whole cells.
     - Every printed cell starts with `# --- cell <i> id=<id> type=<t> json=<a>-<b> ---`.
     - `--max-lines` defaults to 400. On truncation, print `… truncated: N more lines; use --max-lines or a narrower anchor`.
3. **`context`.** `build_context(task_id, phase, max_lines) -> str`. When `--phase auto` (the default), map from status:

   | Status | Phase |
   |---|---|
   | `triage`, `waiting_architecture` | `triage` |
   | `waiting_evidence` | `evidence` |
   | `implementing`, `verifying` | `remediate` when `rounds.review > 0` and `open_findings` has a P0/P1, else `implement` |
   | `reviewing` | `review` |
   | `waiting_runtime` | `runtime` |
   | `user_decision`, `ready_to_merge`, `blocked` | `closeout` |

   Blocks, in order, each with a `## ` header:
   1. `STATE`: id, title, status/owner, complexity/risk, the three required flags, signals, gates on one line, rounds, reviewers, open findings (`id severity`), exceptions (`id role model effort approved_on`), and `scope.files` (first 30, then `+N more`).
   2. `VALIDATION`: `PASS`, or the validator errors.
   3. `RESUME`: `resume.md` if present and not the template placeholder (first 60 lines).
   4. `REQUEST`: for phase `triage`, the full `request.md`. Otherwise only the sections `User outcome`, `Acceptance criteria`, and `Constraints`.
   5. `DECISIONS`: the `Quyết định hiện hành` section plus the `Xử lý findings` table. If there is no ledger, print `no ledger` and `decision.md`'s TOC with line ranges.
   6. `ARCHITECTURE`: for phases `implement`, `remediate`, `review`, and `runtime`, the `Main brief` section. If it is missing, print `no Main brief` and the TOC with line ranges. For the other phases, print only the `RESULT:` line and the size.
   7. Phase extras:
      - `evidence`: probes under `evidence/probes/` (excluding `README.md`), stems paired across `.sql`/`.py`, each marked `result: <path>` or `NO RESULT`.
      - `remediate`: from the highest `reviews/round-N.md`, the table header and lines matching `^\|.*\bP[01]\b`.
      - `runtime`/`closeout`: `runtime-runbook.md` TOC and its `Kết quả người dùng ghi nhận` section.
   8. `FILES`: task files with sizes. Mark files identical to the template after placeholder substitution as `placeholder`, and files over 20 KB as `large: use toc/show`.
   9. `NEXT`: the command(s) allowed for the status, for example `python scripts/vv.py run-gate <T>`.

   Never read other tasks. Total output is limited to `--max-lines` (default 400), with a truncation notice.
4. **Compact `verify` (SOL-04).** Add `--full`. By default, print the header line, `Files: <count>` plus the first 10 paths, one `name: STATUS` line per tool, and for FAIL tools the first 40 output lines. The `verify.log` content stays complete and unchanged in format.
5. **`materialize` (SOL-07).** `parse_file_blocks(data: bytes) -> list[tuple[str, bytes]]`:
   - A start line is `FILE: <path>` or `SKILL_FILE: <path>`. The matching end line is `END_FILE` or `END_SKILL_FILE`.
   - Body bytes are kept exactly, including line endings. Lines outside blocks are ignored, so outer Markdown fences are harmless.
   - Fail on an unclosed block, a nested start, or a duplicate path.
   - Allowed paths: relative, no `..`, not under `.git/`, not `task-state.yaml`, and listed in `scope.files`.
   - `--source` defaults to `architecture.md`; `proposal.md` is allowed.
   - Dry run prints `path | bytes | sha256[:12] | new|changed|identical`. `--write` writes the files.
6. **`closeout`.** `build_closeout(task_id) -> str`, printing exactly the four headings `Đã làm`, `Bạn cần chạy`, `Agent đang chờ`, `Kết thúc`:
   - `Đã làm`: `status=<s>; gates: <k=v,…>`, changed files from `git status --porcelain` that fall under `scope.files` or the task directory, and the line `<Main: tóm tắt 1–3 dòng>`.
   - `Bạn cần chạy`:
     - At `waiting_evidence`: one block per probe without a result, with path, type, the probe's leading comment block (up to 15 lines), `Dán kết quả vào: .ai/tasks/<T>/evidence/results/<stem>.txt`, and `Tối đa 50 dòng, không dữ liệu cá nhân, không secret.`
     - At `waiting_runtime`: the runbook sections mapped as in the skill table (Appendix D), each up to 80 lines.
     - Otherwise: `Không có.`
   - `Agent đang chờ`: `probe` lines, `runtime-result`, one `decision`/`accept-risk` line per open P0/P1 finding at `user_decision`, plus `commit` (with the file list) when scoped changes exist. Otherwise `Không có.`
   - `Kết thúc`: `Lượt này đã xong trong repository.` when nothing is pending, or only `commit`. Otherwise `Trạng thái tiếp theo: <status>. Trả lời: <what Main needs>`.
7. **`doctor` budget lint (SOL-12):** add the WARN checks listed in SOL-12.
8. **Tests:** add `tests/test_vv_context.py` plus a small fixture `tests/fixtures/sample_notebook.ipynb` (3 cells, Fabric-style indentation, one `def`). Cover:
   - `markdown_toc` ignores headings in fences; section ranges.
   - `notebook_cells` line mapping, plus the degraded mapping when the layout differs.
   - `show` with `cell:`, `def:`, `grep:`, an ambiguous heading, and truncation.
   - `build_context` on a temporary task: phase mapping, ledger and brief present or missing, `max_lines`.
   - `parse_file_blocks`: both marker styles, CRLF preserved, unclosed block, duplicate path, and path rejection.
   - `build_closeout` for `waiting_evidence` and for nothing pending.
   - `exceptions` validation: valid override; missing `approved_by`; wrong role; override that does not match `actual`.
   - Compact verify formatting.

   Use `tmp_path` and `monkeypatch.chdir`, because the helpers use relative `TASKS_ROOT`.

**Acceptance:** `python scripts/vv.py verify <T>` PASS, `python scripts/vv.py doctor` passes (WARN lines are allowed in this phase), and `python scripts/vv.py context 20261013-3p-extract-from-raw-payload` prints at most 400 lines without error.
**Rollback:** revert `scripts/vv.py` and the new tests.

### Phase 2: artifact contracts

1. **Templates:**
   - `.ai/tasks/_template/decision.md`: insert, after `# Quyết định`:
     ```text
     ## Quyết định hiện hành

     | ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
     |---|---|---|---|---|

     Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.
     ```
     Append `## Lịch sử quyết định` with `- Chưa có.` at the end.
   - Add `.ai/tasks/_template/resume.md`:
     ```text
     # Resume

     ## Status
     ## Done this session
     ## Next action
     ## Read next
     ## Waiting on
     ```
   - If D2 is adopted: add `author: {expected: claude-opus-5-5, effort: medium, actual: ""}` under `models` in `_template/task-state.yaml`. The validator treats `models.author` as optional, so old tasks stay valid, and when present it must be a mapping with exactly those expected values.
2. **Architect brief (SOL-06) in `scripts/agent_runner.py`:**
   - Add `main_brief` to `_architecture_schema()` as `{"type": "string", "minLength": 200, "maxLength": 14000}` and to `required`.
   - Add `compose_architecture(document: str, brief: str) -> str`. Keep the first non-blank `RESULT:` line, then a blank line, `## Main brief`, a blank line, the brief with any line starting `## ` rewritten to `### `, a blank line, and then the rest of the document with the `RESULT:` line removed. If the document already has a `## Main brief` heading, keep both and append a warning to `ArchitectureResult` (add a `warnings: tuple[str, ...] = ()` field). `vv.py run-gate` prints the warnings.
   - Add `"main_brief"` to the automation contract text: "`main_brief` follows the Main brief contract in the prompt; do not repeat it inside `document`."
   - Tests: composition, heading demotion, duplicate warning, and schema keys.
3. **Architect prompt:** replace `.ai/prompts/architect.md` with Appendix E.

**Acceptance:** tests pass. A user-run `python scripts/vv.py external-smoke --timeout 600` passes (a user step, because nested CLIs may not run inside the Codex sandbox). Record the result in `decision.md`.
**Rollback:** revert `agent_runner.py`, the prompt, and the templates. Existing `architecture.md` files are unaffected.

### Phase 3: instruction layer

1. **D3 adopted:** create `docs/agent-system/WORKFLOW.md`. Move these sections of the current `AGENTS.md` **verbatim**, keeping their headings:
   - §4 Canonical task state (statuses and gate results)
   - §5 Classification (all subsections)
   - §6 Workflow
   - §7 Review routing (severity is also in the core)
   - §10 Commands, plus the new commands from §4.5 of this plan

   Then add:
   - `## Phases and context budgets`: the table in §4.3 of this plan.
   - `## Task artifacts`: the table in §4.4 of this plan.

   Replace `AGENTS.md` with Appendix C. **D3 rejected:** keep `AGENTS.md` and only add Appendix C's `## 4. Context discipline` section after its §3.
2. Replace `.cursor/rules/00-main-orchestrator.mdc` with Appendix B. If Phase 0 step 6 found that Cursor does **not** load `AGENTS.md` automatically, change the first line of Appendix B to "Read `AGENTS.md` once per chat."
3. Replace `.cursor/skills/vsvn-task-workflow/SKILL.md` with Appendix D.
4. In both `.cursor/skills/vsvn-extract-notebook/SKILL.md` and `.cursor/skills/vsvn-notebook-library/SKILL.md`, insert at the end of the `## Before editing` section, before the next `##`:
   ```text
   ### Read budget

   - List cells with `python scripts/vv.py toc notebooks/<name>.ipynb`. Read only the cells in the architecture `Main brief` edit list and the cells they call, with `python scripts/vv.py show notebooks/<name>.ipynb cell:<i>` or `def:<function>`.
   - Read the matching `docs/context/<name>.md` by section with `toc` and `show`, not whole.
   - Search a notebook with `python scripts/vv.py show notebooks/<name>.ipynb grep:<regex>` before opening cells.
   ```
   Do not change any other text in those skills; the user approved only this insertion.
5. Create `.cursorindexingignore`:
   ```text
   notebooks_lgc/
   docs/context/3p-google/*.txt
   .ai/tasks/*/evidence/context/
   .ai/tasks/*/evidence/results/
   .ai/tasks/*/verification/
   .ai/tasks/*/handoffs/
   pipelines/*/manifest.json
   ```
   Create `.cursorignore`:
   ```text
   **/__pycache__/
   .pytest_cache/
   .ruff_cache/
   .ai/.tmp/
   debug.log
   ```
6. `docs/context/00_README.md`:
   - In the file table, change the `01_DATA_MODEL.md` "Khi nào đọc" cell from `Luôn đọc đầu tiên` to `Đọc mục cần cho task (bản đồ context trong docs/AGENT_PROMPT_SAMPLES.md)`.
   - Replace the `## Thứ tự đọc` list with: `Agent: đọc "Tóm tắt 10 dòng" dưới đây, rồi chỉ đọc mục được prompt nêu (python scripts/vv.py toc / show). Người mới: 01 → 02 → 99 §0 → file của phần đang làm.`
   - Change nothing else.
7. `SETUP.md`:
   - In "Cursor Main", add step 7: "Start a new chat per phase. Begin each with `python scripts/vv.py context <task-id>`."
   - Add the new commands to the "Task workflow" command block.
   - Add one line pointing to `docs/agent-system/WORKFLOW.md`.

**Acceptance:** `doctor` shows no budget WARN for `AGENTS.md`, the rules, or `.cursorindexingignore`. `rg -n "Read \`AGENTS.md\`" .cursor` returns nothing (unless the step 2 exception applies). Every heading moved from `AGENTS.md` exists in `WORKFLOW.md`, and every §9 platform invariant line is still in `AGENTS.md` byte-for-byte.
**Rollback:** revert these files. `vv.py` keeps working, because commands are additive.

### Phase 4: author lane (only if D2 is adopted)

1. In `agent_runner.py`, add `AUTHOR_MODEL = "claude-opus-5-5"`, `AUTHOR_EFFORT = "medium"`, and `run_author(repo, prompt, timeout_seconds=1800) -> AuthorResult(document, executable)`:
   - Same command flags as `run_architecture`, except `--effort AUTHOR_EFFORT` and `--max-turns 40`.
   - Schema `{document: string, minLength 200}`.
   - Same `_assert_repo_unchanged` check.
   - Never ask the model to report its own model or effort.
2. In `vv.py`, add `run-author <task-id> --kind proposal|runbook [--timeout]`:
   - Requires `handoffs/author-input.md` (≤ 60 lines, else fail).
   - Prompt = `.ai/prompts/author-<kind>.md` with `{{TASK_ID}}` replaced, plus the author input.
   - Output: `proposal` → `.ai/tasks/<T>/proposal.md`; `runbook` → `.ai/tasks/<T>/runtime-runbook.md`. If the target exists and is not the template placeholder, write `<name>.new.md` instead and print a notice; Main merges it.
   - Set `models.author.actual = AUTHOR_MODEL`, adding the `models.author` mapping if absent. Do not change status or gates.
3. Add the prompt templates from Appendix F.
4. Update `AGENTS.md`: add `proposal.md` to the Vietnamese list and the Author row to the roles table (Appendix C marks both).
5. Tests: input missing or too long, output path selection, `.new.md` collision, and state update. Mock the CLI by monkeypatching `agent_runner.run_author`.

**Acceptance:** tests pass. A user-run dry trial on a scratch task (`vv.py new author-lane-trial`) produces `proposal.md`, and the user deletes the trial task afterwards.
**Rollback:** remove the command, templates, and `models.author`.

### Phase 5: prompt samples

Replace `docs/AGENT_PROMPT_SAMPLES.md` with Appendix A. If D2 is rejected, delete the lines marked `(D2)` and keep the fallback lines marked `(không D2)`.

Coverage map (old → new): 1, 4, 5, 6, 7, 8 → A1 + A4; 2 → A2; 3 → A1 + A3; 9 → A9; 10 → A10; 11 → A6; 12 → A12; 13 → A19; 14, 15 → A18; 16 → A11; 17 → A13; 18 → A14; 19 → A1 (domain DDL/notebook) + A4; 20 → A17; 21 → A15; 22 → A16.

**Acceptance:** file ≤ 25,600 bytes, every old case is covered, and every command named in it exists (`python scripts/vv.py --help`).

### Phase 6: verify, review, measure

1. Run `python scripts/vv.py verify <T>`. On PASS, run `vv.py transition <T> verifying`, set `gates.local_verification: pass`, then transition to `reviewing`.
2. **User step:** run `python scripts/vv.py run-gate <T>` from a normal terminal. Codex remediates `FIX_REQUIRED` findings, re-runs verify, and the user runs round 2. Caps are as in `AGENTS.md`.
3. Write `resume.md` and a closeout with `vv.py closeout <T>`. Stop for the user to commit.
4. **Measurement (after merge, tracked as a backlog row in `decision.md`):** after 7 working days, the user pastes the same aggregate as Phase 0 into `evidence/results/cursor-usage-after.md`, plus the number of task phases completed in each window (count of stops recorded in `resume.md`, or of gate runs). Codex or Main compares:
   - tokens per completed phase, before vs after;
   - review FIX_REQUIRED rate and number of rounds;
   - any missed P0/P1 reported later;
   - Claude quota use, if D2 is adopted.

---

## 7. Acceptance for the whole change

| # | Criterion | How it is checked |
|---|---|---|
| 1 | The problem analysis covers model, agents, skills and rules, flow, and prompts. | §3 of this plan |
| 2 | Each solution has pros, cons, impact, and a trade-off with mitigation. | §5 |
| 3 | All phases pass their acceptance checks. | Phase logs in `decision.md` |
| 4 | Gates and authority are unchanged: same statuses, gate results, round caps, reviewer set, and user-only commit and risk acceptance. | Diff of `WORKFLOW.md` against the old `AGENTS.md` sections; `test_vv.py` passes unchanged |
| 5 | Fixed preamble ≤ 12 KB, down from ~20 KB. | Budget lint plus file sizes |
| 6 | The `context` pack for each existing task is ≤ 400 lines. | Run `vv.py context` on all tasks |
| 7 | Target: Cursor tokens per completed phase drop **≥ 40%**, with no increase in review rounds and no missed P0/P1. | Phase 6 step 4. If the drop is below 20%, report to the user before D1 is considered. |

---

## 8. Rollback

Every change is agent-system configuration or additive tooling; no data or Fabric state is touched. Rollback is `git revert` of the user's commit, or one commit per phase, done by the user. Partial rollback by phase:

| Phase | Effect when reverted |
|---|---|
| 3 (instruction layer) | Restores old agent behavior while keeping the tools available. |
| 2 (runner) | Removes the brief. |
| 4 (author lane) | Removes `run-author`. |

Old tasks need no migration in either direction.

## 9. Risk register

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R1 | Grok ignores the context pack and reads files whole | Medium | First instruction in the rule; every prompt sample names `context`; measurement in Phase 6 |
| R2 | The brief omits a needed detail | Medium | "Read only if needed" map; reviewers read the full architecture |
| R3 | The `AGENTS.md` split hides a rule | Low | Invariants and prohibitions stay in the core; moved text is verbatim; `external-smoke` |
| R4 | The ledger drifts from history | Medium | Verbatim copy rule; `context` warns |
| R5 | Fabric notebook export layout changes | Low | Degraded mapping; tests |
| R6 | The author lane strains Claude quota | Medium | Two kinds only; measured |
| R7 | `materialize` writes the wrong path | Low | `scope.files` allowlist; dry run by default |
| R8 | Phase-sliced chats lose tacit context | Medium | `resume.md` plus the context pack |
| R9 | Exceptions used to bypass policy | Low | `approved_by: user`, date, scope; mirrored in `decision.md`; printed by `context` |

---

## Appendix A: `docs/AGENT_PROMPT_SAMPLES.md` (full new content, Vietnamese)

````markdown
# Các prompt mẫu cho VSVN agent

Cách dùng:

1. **Mỗi phase một chat mới** trong Cursor. Chọn **Grok 4.7 Medium**.
2. Thay mọi `<placeholder>`. Xoá dòng không dùng.
3. Không cần nhắc lại AGENTS.md, "không commit", "ghi model" hay "dừng khi fallback". Rule always-apply đã áp.
4. Agent chỉ đọc output của `python scripts/vv.py context <task-id>` và những gì ghi trong mục `Context`. File lớn đọc theo mục hoặc cell bằng `python scripts/vv.py toc <file>` và `python scripts/vv.py show <file> <anchor>`.
5. Khi agent dừng, xem `Kết thúc`, rồi mở chat mới với mẫu của phase kế tiếp.

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
| Pipeline | `pipelines/<PL>/<PL>.json` | đọc cả file (nhỏ). Không đọc `manifest.json` |
| Bài học cũ | `docs/context/99_PAIN_POINTS.md` | §0 |
| Quy trình | `docs/agent-system/WORKFLOW.md` | §Classification, §Review routing khi triage |

Không đọc nếu prompt không nêu: `notebooks_lgc/`, `docs/context/3p-google/*.txt`, `.ai/tasks/*/evidence/context/`, `pipelines/*/manifest.json`, và artifact của task khác.

## Chọn mẫu

| Tình huống | Mẫu |
|---|---|
| Việc mới bất kỳ (SQL, notebook, pipeline, stateful, cross-system, viết code từ Mapping/BRD) | A1, rồi A3/A4 |
| Sửa nhỏ, tối đa 2 file, không đổi hành vi | A2 |
| Đã dán kết quả probe | A3 |
| Architecture đã PASS, cần viết code | A4 |
| Review trả FIX_REQUIRED | A5 |
| Chạy gate đang chờ | A6 |
| Cần hướng dẫn chạy Fabric DEV | A7 |
| Đã chạy runbook, dán kết quả | A8 |
| Lỗi runtime | A9 |
| Không nhớ task đang ở đâu | A10 |
| Hỏi giải thích | A11 |
| Review diff có sẵn, không sửa | A12 |
| Lập Mapping và BRD | A13 |
| Phân tích Mapping và BRD | A14 |
| Đề xuất hoặc rà tác động, chưa sửa code | A15 |
| Góp ý vào đề xuất | A16 |
| Codex đánh giá hiệu năng | A17 |
| Thay đổi agent-system | A18 |
| Smoke test tích hợp | A19 |

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
Miền (giữ dòng đúng): partner extract | 3P extract | lib extract | lib transform/gold | DDL/registry | ctrl | pipeline | agent-system
Nguồn yêu cầu đã chốt (nếu có): docs/requirements/<task_id>/MAPPING.md, BRD.md; .ai/tasks/<task_id>/decision.md (ledger); requirements-analysis.md
Context:
- <path — mục/cell theo Bản đồ context>
Việc: tạo task, ghi request.md, phân loại theo WORKFLOW.md §Classification và §Review routing.
- Cần evidence: viết probe nhỏ nhất, dừng ở waiting_evidence.
- Cần architecture, đủ evidence: chạy python scripts/vv.py run-gate <task-id>, dừng.
- Đủ điều kiện fast lane: làm theo A2 trong chat này.
```

## A2. Sửa nhỏ (fast lane)

```text
Task mới: <slug>
Phase: triage + implement
Thay đổi: <…>
File: <tối đa 2 path>
Tiêu chí nghiệm thu:
- <…>
Context: chỉ 2 file trên (file lớn thì theo cell hoặc mục).
Việc: tạo task. Chỉ dùng fast lane khi đủ tiêu chí dẫn xuất trong WORKFLOW.md, nếu không thì dừng ở triage như A1. Sửa, chạy python scripts/vv.py verify <task-id>, closeout.
```

## A3. Nạp kết quả evidence

```text
Task: <task-id>
Phase: evidence
Kết quả đã dán: .ai/tasks/<task-id>/evidence/results/<file>
Context: output context --phase evidence; header của probe tương ứng; file kết quả trên.
Việc: so từng kết quả với tiêu chí pass/fail của probe. Ghi kết luận vào ledger trong decision.md. Đủ evidence thì chuyển waiting_architecture và chạy run-gate. Thiếu thì viết probe bổ sung và dừng.
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

## A5. Sửa finding review

```text
Task: <task-id>
Phase: remediate
Context: context --phase remediate (P0/P1 của round mới nhất); các dòng file:line mà finding trích dẫn; Main brief.
Việc: sửa từng P0/P1, ghi disposition trong decision.md, chạy verify. Còn round thì chạy run-gate round kế. Dừng.
```

## A6. Chạy gate đang chờ

```text
Task: <task-id>
Chạy python scripts/vv.py context <task-id>. Chỉ khi status là waiting_architecture hoặc reviewing, chạy python scripts/vv.py run-gate <task-id>. Không sửa source.
Báo: verdict, reviewer trong manifest, risk-gate, artifact đã lưu, status sau khi chạy, lỗi nguyên văn nếu có.
```

## A7. Hướng dẫn chạy Fabric DEV

```text
Task: <task-id>
Phase: runtime
Context: context --phase runtime; Main brief mục Rollout; parameter cell của notebook cần chạy (vv.py show … cell:0).
Việc:
- (D2) Nếu chưa có runtime-runbook.md: viết handoffs/author-input.md (≤ 60 dòng), chạy python scripts/vv.py run-author <task-id> --kind runbook, rồi đối chiếu tham số với parameter cell.
- (không D2) Viết runtime-runbook.md theo skill vsvn-task-workflow.
Sau đó chạy python scripts/vv.py closeout <task-id> và trả lời đúng 4 mục. Dừng ở waiting_runtime.
```

## A8. Ghi nhận kết quả runtime

```text
Task: <task-id>
Phase: closeout
Kết quả: <dán ở runtime-runbook.md mục "Kết quả người dùng ghi nhận" | evidence/results/<file>>
Context: context --phase closeout; chỉ các mục "Kiểm tra kết quả" và "Kiểm tra log và watermark" của runbook.
Việc: so kết quả với tiêu chí. Đạt thì đặt gates.runtime pass và chuẩn bị ready_to_merge. Không đạt thì phân loại code | data | architecture | unclear theo WORKFLOW.md và chuyển status tương ứng. Closeout.
```

## A9. Điều tra lỗi runtime

```text
Task: <task-id | mới: <slug>>
Phase: evidence
Lỗi (đã làm sạch): <…>
Thời điểm, môi trường: <…>
Notebook, pipeline, bảng: <…>
Lần chạy tốt gần nhất: <… | Chưa biết>
Context: cell liên quan (vv.py show … grep:<từ khoá lỗi>); bảng ctrl liên quan (CTRL_TABLES_CONTEXT.md đúng mục).
Việc: chỉ chẩn đoán. Phân loại code | data | architecture | unclear, có bằng chứng. Thiếu evidence thì viết probe nhỏ nhất, dừng ở waiting_evidence. Không sửa code.
```

## A10. Tiếp tục task

```text
Task: <task-id>
Chạy python scripts/vv.py context <task-id>. Chỉ dựa vào output đó và resume.md: nêu phase hiện tại, gate còn mở, việc kế tiếp. Nếu phase là evidence, implement hay remediate, làm tiếp theo mẫu A3, A4 hay A5 trong chat này.
```

## A11. Giải thích (chỉ đọc)

```text
Giải thích cho người vận hành. Không sửa file, không tạo task, không chạy gate.
Phần cần hiểu: <task-id | file + mục/cell | câu trả lời trước>
Context: chỉ phần được nêu (vv.py show), ledger của task nếu cần.
Trả lời theo thứ tự:
1. Nghĩa một câu.
2. Vì sao, có file và dòng; không có thì ghi "không thấy trong repository".
3. Ví dụ đầu vào và đầu ra lấy từ task, không bịa.
4. Việc cần làm tiếp, hoặc "Không cần làm thêm".
```

## A12. Review diff có sẵn

```text
Task: <task-id | mới: <slug>>
Review implementation chưa commit. Không sửa code.
Context: git diff --stat; context của task.
Việc: chưa có task thì tạo task mô tả diff, phân loại, chọn reviewer. Chạy verify; PASS thì chuyển reviewing và chạy run-gate. Báo finding theo severity. Không remediation.
```

## A13. Lập Mapping và BRD

```text
Task mới: <slug>
Phase: triage
Bảng đích: <schema, tên, cột, kiểu, khoá, ghi chú>
Nguồn logic: <notebook hoặc mục context>
Context: docs/templates/MAPPING_TEMPLATE.md, docs/templates/BRD_TEMPLATE.md; nguồn logic theo cell hoặc mục.
Việc: chép mẫu sang docs/requirements/<task_id>/MAPPING.md và BRD.md, giữ tên mục và tên cột của mẫu, xoá dòng [EXAMPLE]. Công thức chỉ ghi khi có trong nguồn; thiếu thì MISSING_EVIDENCE; mâu thuẫn thì CONFLICT kèm câu hỏi. doc_status = DRAFT. Không gọi analyst, Architect hay Codex.
```

## A14. Phân tích Mapping và BRD

```text
Task: <task_id>
Phase: proposal
File: docs/requirements/<task_id>/MAPPING.md, BRD.md; ledger trong decision.md.
Việc: được xoá dòng [EXAMPLE] còn sót, đặt doc_status = READY_FOR_ANALYSIS và tăng version; không thêm rule, cột hay khoá. Gọi agent requirements-analyst (.claude/agents/requirements-analyst.md); agent đó tự viết requirements-analysis.md.
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
Đối tượng: <bảng silver, config, notebook, consumer>
Context: <mục và cell theo Bản đồ context>
Việc: tạo task. Phân loại theo deliverable: chỉ đề xuất, không đổi hành vi, nên không architecture và không review.
- (D2) Viết handoffs/author-input.md (≤ 60 dòng): yêu cầu nguyên văn, file và mục được đọc, ràng buộc. Chạy python scripts/vv.py run-author <task-id> --kind proposal. Main không tự soạn đề xuất.
- (không D2) Main soạn đề xuất trong decision.md.
Cây khoá ghi ở evidence/payload-shape.md, không ghi giá trị. Cột không có trong sample ghi MISSING_EVIDENCE. Cập nhật ledger. Dừng ở user_decision.
```

## A16. Góp ý vào đề xuất

```text
Task: <task-id> (nếu task đã ready_to_merge: tạo task mới và dẫn chiếu)
Phase: proposal
Góp ý: <bảng, cột, giá trị người dùng vừa chốt>
Context: ledger trong decision.md; proposal.md đúng mục bị góp ý.
Việc:
- (D2) author-input.md gồm góp ý nguyên văn và các mục bị thay. Chạy run-author --kind proposal; bản mới ghi ra proposal.new.md thì Main gộp đúng các dòng bị góp ý.
- (không D2) Main sửa đúng các dòng đó.
Góp ý mới thắng dòng cũ cùng cột. Không tự đặt json_path khi người dùng chưa nêu field. Cập nhật ledger. Dừng.
```

## A17. Codex đánh giá xử lý và tốc độ

```text
Task: <task_id>
Bước runtime được bỏ qua: <…>
Context: context của task; các notebook trong scope theo def hoặc cell.
Việc: ghi waiver vào decision.md. Chạy Codex read-only (--model gpt-5.6-sol, model_reasoning_effort=medium) với spark-runtime-reviewer và sql-data-reviewer. Lưu báo cáo tại reviews/performance-review.md. Mỗi đề xuất có file, cell, chi phí hiện tại và cách đổi; không đổi grain, khoá hay rule đã chốt. Không gọi run-gate khi rounds.review = 2. Không sửa code.
```

## A18. Thay đổi agent-system (rule, skill, prompt, vv.py)

```text
Thay đổi agent-system: <mô tả>
Người thiết kế: Claude Code claude-opus-5-5 high (architecture.md, hoặc tài liệu kế hoạch người dùng chỉ định).
Người thực hiện: <Main Grok | Codex, ghi exceptions model_override role main>.
Review: Codex qua run-gate.
Context: chỉ file agent-system bị đổi; WORKFLOW.md đúng mục.
Việc: tạo task, ghi exception đã duyệt vào task-state.yaml và decision.md. Nếu file nội dung nằm trong khối FILE của architecture, lưu bằng python scripts/vv.py materialize <task-id> --write, không chép tay. Chạy verify và doctor; doctor không được có WARN về budget. Dừng trước commit.
```

## A19. Smoke test tích hợp

```text
Chạy python scripts/vv.py external-smoke --timeout 600. Không sửa file.
Báo: git status --short trước và sau; version CLI, model và effort của Claude và Codex; verdict; reviewer trong manifest; risk-gate; lỗi nguyên văn.
EVIDENCE_REQUIRED cho kịch bản giả lập vẫn hợp lệ.
```

## Điểm phải dừng

Cần Fabric DEV, model hoặc CLI không khả dụng hay fallback, structured output hoặc immutability fail, cần quyết định hay accept-risk, hoặc vượt round cap. Đây là kết quả hợp lệ của workflow, không phải quyền bỏ qua gate.
````

---

## Appendix B: `.cursor/rules/00-main-orchestrator.mdc` (full new content)

````markdown
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
- Do not open other tasks, `notebooks_lgc/`, `evidence/context/`, `docs/context/3p-google/*.txt`, or `pipelines/*/manifest.json` unless the prompt names them. Never copy context files into a task.
- Save file blocks with `python scripts/vv.py materialize <task-id> --write`; never retype them.
- `python scripts/vv.py verify <task-id>` output is compact. Open `verification/verify.log` or `--full` only for a FAIL.

## Workflow

- New task: `python scripts/vv.py new <slug>`. Classify with `docs/agent-system/WORKFLOW.md` (§Classification, §Review routing).
- Record the actual Main model. Stop if it is not Grok 4.7 Medium, unless an approved `exceptions` entry covers it.
- At `waiting_architecture` or `reviewing`, run `python scripts/vv.py run-gate <task-id>`. The review lane is Codex only.
- Implement only after the required evidence and architecture gates pass. Record any deviation in `decision.md` before coding.
- Never invent data properties. Write the smallest probe.
- Verify before review and after each P0/P1 fix. Never mark a gate `pass` while evidence is missing or a P0/P1 is open.
- Only the user commits, merges, accepts risk, and confirms runtime results.

## Stop

Stop for: a Fabric DEV probe or runbook; a gate, CLI, or model failure or fallback; a round cap; or a choice that changes scope. Before stopping, overwrite `.ai/tasks/<task-id>/resume.md` (≤ 40 lines) and tell the user to open a new chat for the next phase.

## Turn closeout

End every task turn with four Vietnamese sections, in this order, with these exact headings: `Đã làm`, `Bạn cần chạy`, `Agent đang chờ`, `Kết thúc`. Generate the skeleton with `python scripts/vv.py closeout <task-id>` and edit only the summary lines. Full rules: skill `vsvn-task-workflow`, section `Build the closeout`. Never claim that a Fabric DEV step ran.
````

---

## Appendix C: `AGENTS.md` (full new content, D3 adopted)

Lines marked `(D2)` are included only if D2 is adopted; remove the `(D2)` marker itself. Section 9 must be copied **byte-for-byte** from the current `AGENTS.md` §9.

````markdown
# VSVN Agent Constitution

Shared source of truth for Cursor, Claude Code, Codex, and human operators. Keep this file under 8 KB. Procedures live in `docs/agent-system/WORKFLOW.md` (statuses, classification, workflow, review routing, commands), rules, skills, and agent files. Read them only when the current step needs them.

## 1. Language policy

- English: agent definitions, rules, skills, prompts, configuration, and setup documentation; machine-readable files, keys, enums, statuses, finding IDs, logs, and error codes; task artifacts except the Vietnamese ones below; code identifiers and database metadata.
- Vietnamese: prose in `decision.md`, `runtime-runbook.md`, and `proposal.md` (D2); explanatory comments in source, notebooks, and SQL; conversation with the user.
- Commands, identifiers, paths, status tokens, and finding IDs stay in English inside Vietnamese files.

## 2. Roles and authority

| Role | Runtime | Authority |
|---|---|---|
| Main | Cursor, Grok 4.7 Medium | Sole source-code writer. Owns task state, implementation, remediation, decisions, `resume.md`, and runtime runbooks. |
| Architect | Claude Code, Claude Opus 5.5 High | Writes only the current task's `architecture.md`, including the `Main brief`, through the runner. Never implements. |
| Author (D2) | Claude Code, Claude Opus 5.5 Medium | Through `vv.py run-author` only: writes `proposal.md` or `runtime-runbook.md` on Main's request. Never implements. |
| Review Coordinator and specialists | Codex, GPT-5.6 Sol Medium | Read-only review; the consolidated result goes under `reviews/`. Never fixes code. |
| Local Verifier | `python scripts/vv.py verify` | Deterministic validation. |
| External Gate Runner | `python scripts/vv.py run-gate` / `run-author` | Calls the configured CLI non-interactively, validates structured output and repository immutability, persists the owned artifact, and updates state on behalf of Main. |
| User | Fabric DEV and Git | Runs probes and runbooks, accepts risk, commits and merges. |

- Single code writer plus explicit artifact ownership. Only Main edits source, notebooks, pipelines, schemas, deployment configuration, and `task-state.yaml`.
- There is no `writer: claude` mode. A per-task role or model exception exists only as a user-approved `exceptions` entry in `task-state.yaml`, mirrored in `decision.md`.

## 3. Model policy

- Main: Grok 4.7, `medium` (user approved 2026-10-09). Architect: Claude Opus 5.5, `high`. Review: `gpt-5.6-sol`, `medium` (user approved 2026-10-08). Author (D2): Claude Opus 5.5, `medium`.
- Record actual models in `task-state.yaml`. Do not silently substitute. On fallback or unavailability, stop the gate and report it.
- Change models only after the agent evaluation suite or a recorded user-approved exception.

## 4. Context discipline

1. Start every task step with `python scripts/vv.py context <task-id>`.
2. Read files over 20 KB by section or cell (`vv.py toc`, `vv.py show`). Read a file whole only when it is small or the step edits most of it.
3. Do not read `notebooks_lgc/`, `docs/context/3p-google/*.txt`, `.ai/tasks/*/evidence/context/`, `pipelines/*/manifest.json`, or other tasks' artifacts unless the request names them.
4. Reference context by path and section. Never copy context files into a task.
5. One chat per phase. End each phase by overwriting `resume.md`.

## 5. Gates and severity

- Statuses, gate results, transitions, and round caps are defined in `docs/agent-system/WORKFLOW.md` and enforced by `vv.py`.
- `PASS` is never valid while required evidence is missing or a P0/P1 finding is unresolved.
- P0: data loss or corruption, irreversible state divergence, or non-idempotent behavior with material impact. P1: runtime failure, broken recovery, locking, or watermark behavior, serious performance risk, or an architecture-rule violation. P2: maintainability, testability, observability, or convention. P3: minor clarity.
- Finding dispositions in `decision.md`: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## 6. Data and runtime evidence

- Never infer unknown runtime data characteristics.
- Main writes probes under `.ai/tasks/<task-id>/evidence/probes/`, and the user runs them in Fabric DEV.
- Results go under `evidence/results/` without personal data. Samples are limited to 50 rows.
- Reviewers may return `EVIDENCE_REQUIRED` with an exact probe instead of guessing.

## 7. VSVN platform invariants

<copy the current AGENTS.md §9 bullet list here, byte-for-byte>

## 8. Prohibited actions

- Agents do not commit, push, merge, or rewrite Git history.
- Do not delete or rename Fabric tables without rollback and forward-recovery steps in `runtime-runbook.md`.
- Do not place secrets, tokens, personal data, or production extracts in task artifacts.
- Do not bypass required evidence, architecture, review, or runtime gates.
- Do not modify agent-system configuration unless the user explicitly requests an agent-system change.
````

Note for Codex: `CLAUDE.md` imports `AGENTS.md` and needs no change. After this step, grep for `AGENTS.md §` and `AGENTS.md` section-number references across `.cursor/`, `.codex/`, `.ai/prompts/`, `SETUP.md`, and `docs/`, and update any reference that now points to the wrong section number.

---

## Appendix D: `.cursor/skills/vsvn-task-workflow/SKILL.md` (full new content)

````markdown
---
name: vsvn-task-workflow
description: Start, resume, route, validate, or close a VSVN engineering task through task-state.yaml and its evidence, architecture, review, verification, and runtime gates. Use for task work, when asked which gate comes next, or when the operator asks how to run an existing task's probes or runtime runbook. Do not use for a read-only repository question that is unrelated to a task.
---

# VSVN task workflow

## Phases

One chat per phase. Every phase starts with `python scripts/vv.py context <task-id>` (a new task runs `python scripts/vv.py new <slug>` first).

| Status | Phase | Read after the context pack | Ends with |
|---|---|---|---|
| `triage` | triage | `docs/agent-system/WORKFLOW.md` §Classification and §Review routing; context-map sections the prompt names | probes, `run-gate` architecture, or a fast-lane edit |
| `waiting_evidence` | evidence | probe headers and new results | ledger interpretation; `run-gate` or another probe |
| `implementing`, `verifying` | implement | Main brief; edit-list anchors through `vv.py show` | verify PASS; `run-gate` review |
| `implementing` after FIX_REQUIRED | remediate | P0/P1 rows; cited `file:line` | verify PASS; next review round |
| `waiting_runtime` | runtime | runbook sections | closeout |
| `user_decision` | closeout | ledger; open findings | closeout |

## Steps

1. Use `python scripts/vv.py transition` for status changes and `validate` after editing state.
2. At `waiting_architecture` or `reviewing`, run `python scripts/vv.py run-gate <task-id>`. Use `prompt` only for diagnosis or a user-approved manual fallback. Never use Cursor subagents for review. Never stage files as a handoff.
3. Save `FILE:` or `SKILL_FILE:` blocks with `python scripts/vv.py materialize <task-id>` (dry run), then `--write`.
4. Keep `task-state.yaml` factual. Do not mark a gate passed based on intent, a generated prompt, or an unexecuted runbook. Record role or model exceptions only in `exceptions`, with the user's approval date, and mirror them in `decision.md`.
5. In `decision.md`, edit the `Quyết định hiện hành` row in place, copying the decision text verbatim from its source section. Append details under `Lịch sử quyết định`.
6. Before stopping, overwrite `resume.md` (≤ 40 lines, English): `Status`, `Done this session`, `Next action`, `Read next` (path + anchor), `Waiting on`.

## Runtime runbook

When runtime proof is required, `runtime-runbook.md` is Vietnamese and has these sections: `Phạm vi và môi trường`, `Điều kiện tiên quyết`, `Baseline trước khi chạy`, `Các bước thực hiện`, `Kiểm tra kết quả`, `Chạy lại để kiểm tra idempotency`, `Kiểm tra log và watermark`, `Rollback và forward recovery`, `Kết quả người dùng ghi nhận`. Take parameter values from the notebook parameter cell or the pipeline JSON. If a value is unknown, ask for it; do not guess.

## Build the closeout

Run `python scripts/vv.py closeout <task-id>`, then edit only the summary lines. The four sections, in Vietnamese, in this order, with these exact headings:

1. `Đã làm`: what changed, the current `status` and gates in one line, and the files the operator must open, as paths.
2. `Bạn cần chạy`: one block per operator-run step:
   - Environment and the exact item to run.
   - Parameters with exact values.
   - Numbered steps in run order.
   - Expected result as a pass/fail criterion.
   - Where to paste sanitized output: an exact path under `evidence/results/`, or the runbook's `Kết quả người dùng ghi nhận`. Restate the limits: at most 50 rows, no personal data, no secrets.
   - When the runbook has them: the rerun/idempotency check, the control-log and watermark check, rollback, and forward recovery.

   Write `Không có.` when there is nothing to run.
3. `Agent đang chờ`: one request per line, typed `probe`, `decision`, `accept-risk`, `runtime-result`, or `commit`. A decision lists the options and what Main does for each. A commit request lists the changed files. Write `Không có.` when nothing is pending.
4. `Kết thúc`: when sections 2 and 3 are `Không có.`, or the only open item is `commit`, write `Lượt này đã xong trong repository.` Otherwise name the next `status` and the reply that lets Main resume.

Rules:

- At `waiting_evidence` or `waiting_runtime`, a file path is not an instruction. Write the ordered steps and the paste-back data inline.
- Probe files and `runtime-runbook.md` are the full source; the answer is the condensed list. If they disagree, fix the file first.
- Map the runbook sections in the order above. Skip an empty section; do not fill it in from memory.
- At `user_decision`, write each pending choice as one `decision` or `accept-risk` request with its options.
- Uncommitted changes add one `commit` request. Main never commits.
- Never claim that a Fabric DEV step ran.
````

---

## Appendix E: `.ai/prompts/architect.md` (full new content)

````markdown
# Architect handoff: {{TASK_ID}}

You are the VSVN Architect. Follow `AGENTS.md` and `CLAUDE.md`.

Start with `.ai/tasks/{{TASK_ID}}/task-state.yaml`, `request.md`, and the `Quyết định hiện hành` ledger in `decision.md` (or the whole file if it has no ledger). Then read the evidence and the source and context files the design needs. For files over 20 KB, read by section or cell. Do not read `.ai/tasks/*/evidence/context/` copies, `notebooks_lgc/`, or other tasks unless the request names them.

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
````

---

## Appendix F: author-lane prompt templates (D2)

`.ai/prompts/author-proposal.md`:

````markdown
# Author handoff: proposal for {{TASK_ID}}

You are the VSVN proposal author. This is not an Architect turn. Do not write `architecture.md`. Do not edit any file. Read only the files and sections named in the author input below, plus `.ai/tasks/{{TASK_ID}}/task-state.yaml` and the `Quyết định hiện hành` ledger in that task's `decision.md`.

Write `document` as the complete `proposal.md`, in Vietnamese prose, keeping commands, identifiers, paths, status tokens, and column names in English. Sections:

1. `## Phạm vi`: the base task, and the statement that every line not named in the input stays as last decided.
2. `## Dòng thay đổi`: table `Bảng | Cột | Hành động cũ (đã land) | Hành động mới`.
3. `## ctrl_cfg_schema_registry`: only the affected rows.
4. `## Ràng buộc cho Architect`
5. `## Câu hỏi`: one numbered question per unknown.

Never invent a `json_path`, condition, key, or rule the user has not named; ask instead. Do not copy sample values, review text, person names, or URLs.
````

`.ai/prompts/author-runbook.md`:

````markdown
# Author handoff: runtime runbook for {{TASK_ID}}

You are the VSVN runbook author. Do not edit any file. Read the `Main brief` and `Rollout, rollback, and forward recovery` sections of `.ai/tasks/{{TASK_ID}}/architecture.md`, the parameter cell of each notebook named in the author input (`python scripts/vv.py show`-equivalent: read only that cell), the pipeline JSON if named, and `docs/context/CTRL_TABLES_CONTEXT.md` sections for the ctrl tables involved.

Write `document` as the complete `runtime-runbook.md`, in Vietnamese prose, with exactly these sections: `Phạm vi và môi trường`, `Điều kiện tiên quyết`, `Baseline trước khi chạy`, `Các bước thực hiện`, `Kiểm tra kết quả`, `Chạy lại để kiểm tra idempotency`, `Kiểm tra log và watermark`, `Rollback và forward recovery`, `Kết quả người dùng ghi nhận`.

Every step has exact parameter values taken from the files. When a value is not in the files, write `<CẦN NGƯỜI DÙNG CUNG CẤP: …>`; never guess. Queries are read-only unless the step is the run itself. Limit result samples to 50 rows, with no personal data.
````
