RESULT: PASS

# Architecture: 20261011-requirements-templates-and-analyst (round 2)

## Context and scope

This is architecture round 2. Round 1 produced four files, which Main copied verbatim. The read-only `requirements-reviewer` Codex turn then returned `VERDICT: FIX_REQUIRED` with seven P1 findings (REQ-001 to REQ-007) and one P2 finding (REQ-008), stored in `reviews/requirements-review.md`. Under the user-approved exception dated 2026-10-11, recorded in `task-state.yaml` and `decision.md`, Claude Code rewrites the full content of all four files in this document. Main replaces each file with the new block body verbatim and does not edit the wording.

| # | Path | Purpose | Language of body |
|---|---|---|---|
| 1 | `docs/templates/MAPPING_TEMPLATE.md` | Source-to-target Mapping template (`template_id` `VSVN-MAPPING-v1`) | Vietnamese prose, English identifiers |
| 2 | `docs/templates/BRD_TEMPLATE.md` | Business Requirements Document template (`template_id` `VSVN-BRD-v1`) | Vietnamese prose, English identifiers |
| 3 | `.claude/agents/requirements-analyst.md` | Claude Code subagent `requirements-analyst`, model `claude-opus-5-5`, effort `medium` | English |
| 4 | `.codex/agents/requirements-reviewer.toml` | Codex read-only reviewer `requirements-reviewer`, `gpt-5.6-sol`, effort `medium` | English, ASCII only |

Context read for this round:

- `AGENTS.md` sections 1 to 11, and `CLAUDE.md`.
- Task artifacts: `task-state.yaml`, `request.md`, `decision.md`, `evidence/plan.md`, `reviews/requirements-review.md`, `verification/verify.log`, and the round-1 `architecture.md`.
- `docs/context/00_README.md`, `01_DATA_MODEL.md`, `02_NAMING_CONVENTION.md`, `CTRL_TABLES_CONTEXT.md` (sections 1 to 5, 10, and 11), `99_PAIN_POINTS.md` section 2 (D12), and `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`.
- `notebooks/NB_CREATE_DDL.ipynb`: cell `TABLE_CONFIGS_3P`, variable `POI_ID`, and function `flatten_table_configs`.
- `.codex/agents/risk-gate.toml` for field shape, `.claude/settings.json`, and `scripts/agent_runner.py` (`run_architecture`, `run_review`, `_validate_jsonl`).

Repository facts that shape the design:

- `run_architecture` launches Claude with `--tools Read,Glob,Grep`, `--permission-mode dontAsk`, and `--setting-sources user`, and persists `document.rstrip() + "\n"`. The Architect path is unchanged, and the analyst cannot run inside it.
- `.claude/settings.json` uses `defaultMode: dontAsk` and allows only `Edit(/.ai/tasks/*/architecture.md)` among file edits. A subagent write elsewhere is denied in that mode. A write to `architecture.md` would be allowed, so the analyst definition forbids it explicitly.
- `cmd_verify` lints TOML but not Markdown. The new TOML must parse with `tomllib`. The round-1 `verify.log` shows `toml: PASS` for the round-1 reviewer file.
- `decision.md` records that the round-1 `spawn` prompt did not start the custom agent under `codex exec --ephemeral` (`no rollout found`). The stored report came from a direct read-only turn whose prompt was the TOML `developer_instructions`. This round makes that direct-turn procedure the designed procedure, so it is no longer a deviation.
- `notebooks/NB_CREATE_DDL.ipynb` declares `POI_ID = {"path": "_doc.source_name,_doc.source_id", "type": "string", "rule": "HASH_MD5_UUID"}`, sets `"key": "poi_id"` for `slv_3p_poi` with `source_table` `$`, and `flatten_table_configs` sets `key_order = keys.index(col_name) + 1`. This removes the inference that REQ-002 flagged.
- No notebook and no `docs/context/` file defines the columns or data types of `slv_poi_localization` or `gld_srv_poi_multi_lang`, or the table that holds `has_required_langs` (repository search). The examples mark these as `MISSING_EVIDENCE`.
- `AGENTS.md` section 9 states the third-party prefix as `slv_3p_`. `docs/context/02_NAMING_CONVENTION.md` section 1 states the naming pattern `slv_3p_poi_<khối>`, and the root table `slv_3p_poi` does not match `slv_3p_poi_`. The canonical layer prefix is therefore `slv_3p_`, with the pattern recorded alongside it (REQ-007).

## Resolution of round-1 findings

| Finding | Severity | Change in this round |
|---|---|---|
| REQ-001 | P1 | `data_type` is now a required cell at every layer. `COL-EX-01`, `COL-EX-02`, and `COL-EX-03` are `MISSING_EVIDENCE`, name the empty cell in `note`, and are blocked by gap `MGAP-EX-01`. The `[NEEDS-SCHEMA]` convention is removed from all files. |
| REQ-002 | P1 | `COL-EX-04` cites `notebooks/NB_CREATE_DDL.ipynb` `POI_ID`, `TABLE_CONFIGS_3P`, and `flatten_table_configs`, plus `CTRL_TABLES_CONTEXT.md §5`. Each value (`$`, path, `string`, `HASH_MD5_UUID`, `is_key`, `key_order` 1) is stated by the notebook. The "khoá suy ra" wording is removed. |
| REQ-003 | P1 | The BRD acceptance-criteria table gains `evidence_status` and `context_ref`. `AC-EX-01` cites `01_DATA_MODEL.md §7` and `AGENTS.md §8`. |
| REQ-004 | P1 | Both templates now end with the same three sections: missing evidence, repository conflicts, and open questions (Mapping 6, 7, 8; BRD 11, 12, 13). The BRD gains section 6 "Nguồn dữ liệu" (`DS-`) for each requirement's source tables. The reviewer's T2 lists the designed fill locations for each template. |
| REQ-005 | P1 | No body contains the word "ví dụ". Inline format illustrations are replaced by patterns (`<path> §<mục>`), and every example row or paragraph starts with `[EXAMPLE]`. |
| REQ-006 | P1 | Agent input validation requires a non-blank `task_id` equal to the input, non-blank `mapping_id` exactly `MAP-<task_id>`, and non-blank `brd_id` exactly `BRD-<task_id>`, in both files. This makes the cross-document IDs equal. |
| REQ-007 | P1 | One table-prefix table (`slv_pn_`, `slv_3p_`, `slv_pm_` `[PROPOSED]`, `slv_poi_`, `ref_`, `gld_`, `ctrl_*`) appears identically in both templates and is restated in the agent. The agent runs it as platform check PC-01. Reviewer T8 lists the same prefixes. |
| REQ-008 | P2 | Both templates contain a byte-identical section "Quy ước dùng chung" holding all value sets, the prefix tables, document IDs, row-ID prefixes, cross-document links, and platform guardrails. The agent restates it and stops if they differ. Reviewer T7 checks identity. |

Additional design changes made while fixing these findings:

- Added `evidence_status` `USER_STATED`. Round 1 had no valid status for a value the user decides or answers, so an answered question could never close a gap. `USER_STATED` is allowed only for requirements and decisions. Facts about `EXISTING` objects still need `CONTEXT_STATED` or `TASK_EVIDENCE` (`AGENTS.md` sections 5 and 8).
- Renamed the column-mapping row prefix from `MAP-` to `COL-`, so it cannot be confused with `mapping_id` `MAP-<task_id>`. Renamed the consumer prefix from `CON-` to `CSM-`, so it is not confused with conflict IDs. Gap, conflict, and question prefixes are `MGAP-`, `MCONF-`, `MQ-` in the Mapping and `BGAP-`, `BCONF-`, `BQ-` in the BRD.
- `key_order` is required only at silver L1, where `ctrl_cfg_schema_registry.key_order` exists. At silver L2 and gold, the composite key order is not stated by context, and requiring it would invite inference.
- A bronze source has no stated key. Context states only the event grain (`01_DATA_MODEL.md §4`), and the extract reads raw by version. Bronze sources therefore leave `key_columns` and `key_evidence` blank by rule. Every other source table requires grain and key.
- A requirement whose target is a legacy table without a layer prefix gets a user question. The agent does not judge it.

## Non-goals

- No notebook, pipeline, schema, DDL, SQL, ctrl-table, or source-code change.
- No change to `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, `.codex/config.toml`, `scripts/vv.py` (including `REVIEWERS`), or `scripts/agent_runner.py`.
- No change to the existing Codex review cycle or its five reviewers.
- No Fabric DEV probe and no runtime proof.
- No filled Mapping or BRD for a real task. `docs/requirements/` is only recommended, not created.
- No validator script for the templates.
- No commit, push, or merge.

## Invariants

- INV-1: Implementation creates or replaces exactly the four paths above, plus one Main-owned archive of the round-1 review (`reviews/requirements-review-round-1.md`). It modifies no other repository file outside Main's task artifacts.
- INV-2: Each file's bytes equal the UTF-8 encoding, without BOM and with LF line endings, of the matching block body as defined in "Block format".
- INV-3: The Architect stays on `claude-opus-5-5` at effort `high` and writes only `architecture.md` through `python scripts/vv.py run-gate`. The analyst never runs inside `run-gate`.
- INV-4: The analyst writes at most one path, `.ai/tasks/<task_id>/requirements-analysis.md`. It never writes `architecture.md`, `task-state.yaml`, other task artifacts, inputs, or templates, and it has no shell tool.
- INV-5: Every example value that states a table, column, key, grain, data type, enum value, formula, or rule either cites a `context_ref` that states it, or is blank with `MISSING_EVIDENCE` and a gap row in the same template. See "Example fact provenance".
- INV-6: The section "Quy ước dùng chung" is byte-identical in both templates. The agent restates its content and stops with `INPUT_INVALID` if the template content differs from its restatement.
- INV-7: When evidence is missing, the analyst stops after sections 1 to 7. It never proposes a new notebook while any target grain or key, or any non-bronze source grain or key, is not known.
- INV-8: `ANALYSIS_STATUS` is an input to Main, not a workflow gate. Only Main changes `task-state.yaml`.
- INV-9: `review_plan.required_reviewers` stays empty. `gates.specialist_review` and `gates.risk_gate` stay `not_required`. The requirements review is one manual read-only Codex turn, not `run-gate`.
- INV-10: No personal data, secrets, tokens, or production extracts appear in templates, inputs, analysis, or review.
- INV-11: The reviewer TOML is ASCII-only, contains no backslash, and contains no triple quote inside `developer_instructions`.

## State ownership, grain, and keys

There is no Lakehouse state. The durable state is repository files.

| Artifact | Content owner | Persisted by | Changed by |
|---|---|---|---|
| This `architecture.md` | Architect (Claude Code, `claude-opus-5-5`, `high`) | `vv.py run-gate` | A new architecture round only |
| The four files | Architect, under the 2026-10-11 exception | Main, by verbatim copy | A new architecture round only. Main never edits the wording |
| `docs/requirements/<task_id>/MAPPING.md` and `BRD.md` (future) | User or requirements owner | User | User |
| `.ai/tasks/<task_id>/requirements-analysis.md` (future) | `requirements-analyst` | The agent, or the user or Main verbatim on write failure | A rerun of the agent only |
| `reviews/requirements-review.md` and `reviews/requirements-review-round-1.md` | `requirements-reviewer` (Codex) | Main | A rerun of the reviewer only |
| `task-state.yaml`, `decision.md` | Main | Main | Main |

Document grain and keys:

- One Mapping and one BRD per task. Document keys are `mapping_id = MAP-<task_id>` and `brd_id = BRD-<task_id>`, where `task_id` is the `.ai/tasks/` directory name (`YYYYMMDD-slug`, `AGENTS.md` section 4). Each document carries `task_id` and both IDs. `version` is an integer that starts at 1 and increases by 1 on each edit.
- Row IDs are unique within a file, and no prefix is shared between files. Mapping: `FLOW-`, `SRC-`, `TRG-`, `COL-`, `MGAP-`, `MCONF-`, `MQ-`. BRD: `SCOPE-`, `CSM-`, `BR-`, `DS-`, `RULE-`, `ID-`, `NFR-`, `AC-`, `BGAP-`, `BCONF-`, `BQ-`. Filled rows use the prefix plus three digits. Example rows use the prefix plus `EX-` and two digits.
- Cross-document links:
  - Mapping `COL-*.req_ids` points to `BR-*`, and Mapping `COL-*.rule_ids` points to `RULE-*`.
  - BRD `trg_tbl`, `grain`, and `key_columns` equal the Mapping `TRG-*` row with the same `trg_tbl`.
  - For each requirement, the set of `src_tbl` in BRD `DS-*` rows equals the set of `src_tbl` in the Mapping `SRC-*` rows used by its `COL-*` rows.
- One analysis file per task. It is overwritten in full on each run and records input IDs and versions in its section 1.

## Ordering and transaction boundaries

Each step below is a separate, re-runnable boundary. No step commits to git.

1. `run-gate` persists this document. Main records the architecture gate as `pass` and `rounds.architecture` as 2.
2. Main transitions to `implementing`.
3. Main copies the current `reviews/requirements-review.md` byte for byte to `reviews/requirements-review-round-1.md`, so the round-1 report is kept.
4. Main runs the extraction procedure in `write` mode. It validates the block set before any write, then overwrites the four files.
5. Main runs the extraction procedure in `check` mode, then the content checks in "Verification strategy".
6. Main runs `python scripts/vv.py verify 20261011-requirements-templates-and-analyst`.
7. Main records disposition `fixed` for REQ-001 to REQ-008 in `decision.md`, because the new bodies were copied verbatim.
8. Main transitions to `reviewing` without calling `run-gate`. Main runs one direct read-only Codex turn (implementation plan step 7) and stores the report at `reviews/requirements-review.md`.
9. If the report has no P0 or P1 finding, the user may mark the task `ready_to_merge`. If a P0 or P1 finding remains, the task goes to `user_decision`. Two architecture rounds and two review rounds are now used, so the caps are reached (`AGENTS.md` section 6, rule 8). Main does not patch the documents.

Operational order when the analyst is used later:

1. Main creates the task with `vv.py new`.
2. The user fills the Mapping and BRD under `docs/requirements/<task_id>/` and sets `doc_status = READY_FOR_ANALYSIS`.
3. The user runs `requirements-analyst`, which writes the analysis.
4. Main reads the analysis for triage, evidence planning, and classification. The analysis never moves task status.

## Idempotency, concurrency, retry, and recovery

- Copy idempotency: `write` mode writes the same bytes on every run, and `check` mode is read-only.
- Analyst idempotency: a rerun replaces the whole analysis file. On identical inputs and context, the validation rules, coverage codes, and status are deterministic. Wording may differ, so the status and codes are the contract, not the prose.
- Reviewer idempotency: the reviewer is read-only. A rerun replaces `requirements-review.md`, and the round-1 archive is never overwritten.
- Concurrency: Main is the only writer. Two analyst runs on the same task are not locked, so the last write wins. Operators run one analyst session per task at a time.
- Retry: a failed copy is retried by rerunning `write` mode. A failed Codex turn is retried once as the same command. A model or effort mismatch is never retried on another model.
- Recovery: a content defect is fixed only by a new architecture round. With caps reached, that requires a user decision.

## Partial failures

| Failure | Detection | Behavior |
|---|---|---|
| Copy writes some files, then crashes | `check` mode prints `DIFF` | Rerun `write` mode |
| Block set differs from the four expected paths | Script exits before writing | Stop and report to the user. This is an architecture defect |
| Content check fails (shared section `DIFF`, example-label count not 0, "ví dụ" count not 0, TOML not ASCII) | Verification commands | Do not edit. Report to the user, because the round cap is reached |
| New TOML does not parse | `vv.py verify` reports toml FAIL | Same as above |
| Claude Code rejects or ignores the `effort` frontmatter key | Post-merge user smoke check | Stop and report. Do not substitute (`AGENTS.md` section 3) |
| Analyst write denied, for example under project `dontAsk` | The agent sees the denied write | The agent returns the content between `ANALYSIS_FILE:` and `END_ANALYSIS_FILE` lines. The user or Main stores it verbatim |
| Analyst inputs invalid, or templates differ from the agent restatement | Agent validation | `INPUT_INVALID` analysis with sections 1 and 2 only. No write if the task directory is missing |
| Codex turn fails, emits JSONL `error` or `turn.failed`, changes the working tree, or reports a model or effort other than `gpt-5.6-sol` and `medium` | JSONL check, `git status` comparison, report header | Do not store the report. Stop and report. Do not substitute a model |
| Review returns P0 or P1 | Report findings | `user_decision` (caps reached) |

## Alternatives and trade-offs

1. Template format.
   - (a) Markdown with fixed headings and fixed table columns.
   - (b) YAML or JSON.
   - Selected: (a). Business owners can fill Vietnamese prose, and fixed column names keep the documents machine-readable. (b) needs a validator, which is out of scope. Cost: structure is enforced by the analyst's `INPUT_INVALID` checks, not by a parser.
2. Shared conventions.
   - (a) A byte-identical shared section in each template.
   - (b) A third shared file.
   - (c) Scattered definitions.
   - Selected: (a). It satisfies REQ-008, keeps each template self-contained, and stays within the four-file scope. Cost: duplication. This is mitigated by an exact-equality check at copy time and by the agent's mismatch stop rule.
3. Business-rule fill location in the Mapping.
   - (a) `rule_ids` per column, pointing to BRD section 7.
   - (b) A duplicated rule table in the Mapping.
   - Selected: (a). Each rule is defined once, so the two documents cannot disagree on a rule's text. The Mapping still records which rules produce each column. The reviewer's T2 states this fill location explicitly.
4. Source fill location in the BRD.
   - (a) A table-level section 6 `DS-`, with column-level detail in the Mapping.
   - (b) Column-level detail in both documents.
   - Selected: (a). It satisfies REQ-004 without duplicating column mappings. The agent checks set equality between `DS-` and the Mapping sources.
5. User-decided values.
   - (a) Add `USER_STATED` with a restricted scope.
   - (b) Keep only repository-backed statuses.
   - Selected: (a). Under (b), an answered question could never close a gap, which makes the analysis status unreachable for new designs. The restriction keeps `AGENTS.md` section 5 intact: data characteristics of existing objects still need repository or probe evidence.
6. Evidence granularity: separate `grain_evidence` and `key_evidence` for tables, and one row status for column mappings, as in round 1. Grain and key gate both `MAPPED` and the notebook prohibition.
7. Analyst persistence: Write tool restricted by instruction to one path, with a verbatim-reply fallback, as in round 1. Widening `.claude/settings.json` is out of scope.
8. Analyst form: a Claude Code subagent file, as in round 1, because only that form carries `model` and `effort` without touching `.claude/settings.json`.
9. Review invocation.
   - (a) A direct `codex exec` turn whose prompt is the TOML `developer_instructions`.
   - (b) A parent turn that spawns the custom agent.
   - Selected: (a). (b) failed under `--ephemeral` in round 1 (`decision.md`). (a) keeps the same model, effort, sandbox, and approval flags as `run_review`. Cost: the TOML `sandbox_mode` is enforced by command flags rather than by agent loading, so the command repeats them.
10. Analysis status set: `COMPLETE`, `EVIDENCE_REQUIRED`, `USER_DECISION`, `INPUT_INVALID`, as in round 1. A platform violation is not missing evidence, and malformed input must stop first.

## Selected design

- Templates: an unnumbered "Cách điền" section, the byte-identical "Quy ước dùng chung" section, then numbered sections with fixed English column names.
  - Mapping sections: 1 document, 2 flow, 3 sources, 4 targets, 5 column mapping, 6 missing evidence, 7 conflicts, 8 questions.
  - BRD sections: 1 document, 2 context, 3 scope, 4 consumers, 5 requirements, 6 data sources, 7 rules, 8 identifiers, 9 NFR, 10 acceptance, 11 missing evidence, 12 conflicts, 13 questions.
  - Every `MISSING_EVIDENCE` cell needs a gap row in the same file. Every `USER_ANSWER` or `EXTERNAL` gap, and every conflict, needs a question row.
  - Example rows use only cited context, and unknown example values stay blank.
- Analyst: tools `Read, Grep, Glob, Write`, with no shell. The procedure is:
  1. Validate inputs, including exact ID formats, sections, columns, row prefixes, value sets, references, and template identity.
  2. Verify every citation.
  3. Assign coverage codes per requirement.
  4. Run platform checks PC-01 to PC-09.
  5. Collect gaps.
  6. Pick the status by first-match precedence.
  7. Write a fixed-structure English analysis whose first line is `ANALYSIS_STATUS: <status>`.
- Reviewer: a Codex TOML with the existing field shape. It reads exactly three files and runs checks T1 to T9 and A1 to A8 with designed fill locations, canonical prefixes, and identity checks.

## Observability

- `check` mode prints one `MATCH` or `DIFF` per path and sets the exit code. The content checks print `SAME`, counts, `ASCII`, or `OK`.
- `vv.py verify` appends to `verification/verify.log`.
- The analysis records task, paths, IDs, versions, model, effort, date, and skipped example rows. Its first line `ANALYSIS_STATUS` can be found with grep.
- The review report header records model, effort, and files read. The JSONL checker prints `JSONL_OK` or `JSONL_BAD`.
- `decision.md` (Main) records dispositions and the archive of the round-1 report.

## Security and data handling

- No secrets, tokens, or personal data in any body. Templates require `owner_role`, not personal names. The analyst returns `INPUT_INVALID` on personal data and cites only row IDs.
- The analyst has no Bash tool. Project `deny` rules stay in force.
- Write scope:
  - The instruction allows one path only.
  - Under `dontAsk`, every write except `architecture.md` is denied, and the instruction forbids `architecture.md`. The reviewer treats any weakening of that rule as P0.
  - Under `--permission-mode default`, the user approves the single path.
- The Codex turn runs with `--sandbox read-only` and `approval_policy="never"`. Main compares `git status --porcelain -uall` before and after the turn.
- Filled documents under `docs/requirements/` are committed, so both templates restate the no-personal-data rule.

## Rollout, rollback, and forward recovery

- Rollout: the files do nothing until invoked. There is no Lakehouse, pipeline, or ctrl-table effect. Optional user smoke check after copy: confirm that Claude Code `/agents` lists `requirements-analyst` with model `claude-opus-5-5` and that a run shows effort `medium`. If effort is not honored, stop and report.
- Rollback: delete the four paths or revert the commit. No data rollback is needed, and no existing gate references these files.
- Forward recovery: a copy defect is fixed by rerunning `write` mode. A content defect needs a user decision, because the architecture cap is reached.

## Implementation plan

1. Confirm the verdict is `PASS`. Confirm with `git status --porcelain -uall` that the only paths outside `.ai/` that are new or changed are the four files from round 1. If any other path appears, stop for the user.
2. Copy `reviews/requirements-review.md` byte for byte to `reviews/requirements-review-round-1.md`.
3. Run the extraction script below from the repository root in `write` mode, then in `check` mode. Do not type or reformat bodies by hand. The script is ASCII-only.

PowerShell:

```powershell
@'
import pathlib
import sys

ARCH = pathlib.Path(".ai/tasks/20261011-requirements-templates-and-analyst/architecture.md")
EXPECTED = [
    "docs/templates/MAPPING_TEMPLATE.md",
    "docs/templates/BRD_TEMPLATE.md",
    ".claude/agents/requirements-analyst.md",
    ".codex/agents/requirements-reviewer.toml",
]
MARK_OPEN = "FILE: "
MARK_CLOSE = "END_FILE"

mode = sys.argv[1] if len(sys.argv) > 1 else "check"
lines = ARCH.read_text(encoding="utf-8").split("\n")
blocks = []
path = None
body = []
for line in lines:
    if path is None:
        if line.startswith(MARK_OPEN):
            path = line[len(MARK_OPEN):]
            body = []
    elif line == MARK_CLOSE:
        blocks.append((path, "\n".join(body) + "\n"))
        path = None
    else:
        body.append(line)
if path is not None:
    sys.exit("unterminated block: " + path)
if [p for p, _ in blocks] != EXPECTED:
    sys.exit("unexpected block paths: " + repr([p for p, _ in blocks]))
failed = False
for p, content in blocks:
    target = pathlib.Path(p)
    data = content.encode("utf-8")
    if mode == "write":
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print("WROTE", p, len(data))
    else:
        ok = target.is_file() and target.read_bytes() == data
        failed = failed or not ok
        print("MATCH" if ok else "DIFF", p)
sys.exit(1 if failed else 0)
'@ | python - write
```

   Run the same here-string with `| python - check` afterwards. In Bash, use `python - write <<'EOF'` with the same body.

4. Run the content checks in "Verification strategy".
5. Run `python scripts/vv.py verify 20261011-requirements-templates-and-analyst`.
6. Record `fixed` for REQ-001 to REQ-008 in `decision.md`. Also record there that `requirements-analyst` owns `.ai/tasks/<task_id>/requirements-analysis.md`, and that the direct-turn review procedure is now the architecture. `AGENTS.md` stays unchanged.
7. Transition to `reviewing`. Do not call `run-gate`. Capture `git status --porcelain -uall`, then run:

```powershell
python -c "import pathlib;pathlib.Path('.ai/.tmp').mkdir(parents=True,exist_ok=True)"
python -c "import tomllib,sys;sys.stdout.write(tomllib.load(open('.codex/agents/requirements-reviewer.toml','rb'))['developer_instructions'])" | codex exec --strict-config --ephemeral --json --model gpt-5.6-sol -c 'model_reasoning_effort="medium"' -c 'approval_policy="never"' --sandbox read-only --cd . --output-last-message .ai/.tmp/requirements-review.md - | python -c "import json,sys;bad=[l for l in sys.stdin if l.strip() and json.loads(l).get('type') in ('error','turn.failed')];print('JSONL_BAD' if bad else 'JSONL_OK');sys.exit(1 if bad else 0)"
```

   Accept the run only if all of the following hold:
   - The checker prints `JSONL_OK` and exits 0.
   - `git status --porcelain -uall` is unchanged.
   - `.ai/.tmp/requirements-review.md` exists, and its first line starts with `VERDICT:`.
   - The report header states `gpt-5.6-sol` and `medium` and lists exactly the three files.

   In Bash, run the same pipeline with `set -o pipefail`. Then copy `.ai/.tmp/requirements-review.md` to `.ai/tasks/20261011-requirements-templates-and-analyst/reviews/requirements-review.md`.
8. If no P0 or P1 finding remains, hand over to the user for `ready_to_merge`. Otherwise transition to `user_decision` with the findings.

## Verification strategy

| Check | Command or method | Pass criterion |
|---|---|---|
| Byte equality to blocks | Extraction script, `check` mode | Four `MATCH` lines, exit 0 |
| No extra paths | `git status --porcelain -uall` | Outside `.ai/`, the only new paths are the four files |
| Shared section identical | `python -c "import pathlib as P;g=lambda p:(lambda L:(lambda i:L[i[1]:i[2]])([n for n,l in enumerate(L) if l.startswith('## ')]))(P.Path(p).read_text(encoding='utf-8').split(chr(10)));print('SAME' if g('docs/templates/MAPPING_TEMPLATE.md')==g('docs/templates/BRD_TEMPLATE.md') else 'DIFF')"` | Prints `SAME` |
| No unlabeled "ví dụ" | `python -c "import pathlib as P;print(sum(P.Path(p).read_text(encoding='utf-8').lower().count('ví dụ') for p in ['docs/templates/MAPPING_TEMPLATE.md','docs/templates/BRD_TEMPLATE.md']))"` | Prints `0` |
| Example rows labeled | `python -c "import pathlib as P;print(len([l for p in ['docs/templates/MAPPING_TEMPLATE.md','docs/templates/BRD_TEMPLATE.md'] for l in P.Path(p).read_text(encoding='utf-8').split(chr(10)) if l.startswith('| ') and '-EX-' in l.split('|')[1] and not l.split('|')[1].strip().startswith(chr(96)+'[EXAMPLE]')]))"` | Prints `0` |
| TOML ASCII | `python -c "import pathlib;b=pathlib.Path('.codex/agents/requirements-reviewer.toml').read_bytes();print('ASCII' if all(c<128 for c in b) else 'NON_ASCII')"` | Prints `ASCII` |
| TOML fields | `python -c "import tomllib;d=tomllib.load(open('.codex/agents/requirements-reviewer.toml','rb'));assert (d['name'],d['model'],d['model_reasoning_effort'],d['sandbox_mode'],d['approval_policy'])==('requirements-reviewer','gpt-5.6-sol','medium','read-only','never');print('OK')"` | Prints `OK` |
| TOML validity and task state | `python scripts/vv.py verify <task-id>` | Overall PASS |
| Existing gates unchanged | `python scripts/vv.py doctor` | Same result as before the change |
| Unchanged config | `git diff --stat -- .claude/settings.json .codex/config.toml scripts AGENTS.md` | Empty |
| Content review | `requirements-reviewer` direct Codex turn | `reviews/requirements-review.md` exists with no open P0 or P1 |
| Task state | `review_plan.required_reviewers == []`, and `gates.specialist_review` and `gates.risk_gate` are `not_required` | `vv.py validate` PASS |

### Block format

- Each block starts with a line that is exactly `FILE: <path>` at column 0 and ends with a line that is exactly `END_FILE`. Both delimiter lines are excluded from the body.
- Canonical body: the lines between the delimiters after universal-newline decoding of this file, joined with LF, plus one final LF. No body contains trailing spaces, tabs, or a blank last line.
- Files are written as UTF-8 without BOM, with LF line endings. The script does exactly this, so any CRLF that `run-gate` writes on Windows does not leak into the files.
- No line outside the four blocks starts with the opening delimiter. No line inside a block is exactly the closing delimiter.

### Example fact provenance

| Example ID | Fact | Source |
|---|---|---|
| Shared prefix table | `slv_pn_`, `slv_3p_`, `gld_`; `slv_3p_poi_<khối>`, `slv_poi_`, `ref_`, `gld_srv_`, `ctrl_*`, `slv_pm_` `[PROPOSED]`; two raw names; legacy tables kept until cutover | `AGENTS.md` §9; `01_DATA_MODEL.md` §1, §2; `02_NAMING_CONVENTION.md` §1 |
| Shared guardrails | Bronze append only; L1 no rules; rules in L2 or ref; gold expose, sync, filter by silver flag, never reads gold; `poi_id` no language; technical column names; notebook and pipeline naming | `01_DATA_MODEL.md` §1, §2; `AGENTS.md` §9; `02_NAMING_CONVENTION.md` §2, §3, §5.2 |
| FLOW-EX-01 | `NB_00_ORCHES_SLV_TO_GLD` writes the gold tables; selected by `p_pl_name` | `01_DATA_MODEL.md` §3; `02_NAMING_CONVENTION.md` §2 |
| FLOW-EX-02 | `RECOMPUTE` edges run by `NB_00_ORCHES_SLV_TO_GLD`; targets are silver L2 or gold nodes; gold edges not seeded | `CTRL_TABLES_CONTEXT.md` §2, §3, §10 |
| FLOW-EX-03, MGAP-EX-04, MQ-EX-02 | `_1H` is `[PROPOSED]`; cadence suffix mandatory for recompute (`CADENCE_RE`); no pipeline name stated | `02_NAMING_CONVENTION.md` §3 |
| FLOW-EX-04, NFR-EX-02 | Silver to gold POI runs hourly | `AGENTS.md` §9 |
| SRC-EX-01, DS-EX-01 | `slv_poi_localization` in `lh_vv_silver.dbo`, PK (`poi_id`, `lang`), node N4, node notebook not in the repository | `01_DATA_MODEL.md` §2, §6 |
| SRC-EX-02, DS-EX-02 | 1 event = 1 full document at crawl; columns `source_name`, `source_id`; `event_id` duplicates, not a key (D12) | `01_DATA_MODEL.md` §4; `99_PAIN_POINTS.md` §2; `CTRL_TABLES_CONTEXT.md` §5 |
| TRG-EX-01, BR-EX-01, SCOPE-EX-01, AC-EX-01 | `gld_srv_poi_multi_lang`, PK (`poi_id`, `lang`), column `poi_name`, 1:1 from N4, keeps only POIs with vi, en, ko | `01_DATA_MODEL.md` §7 |
| TRG-EX-02, BR-EX-02 | `slv_3p_poi`, key `poi_id`, `DOC`, `$`, 1 row per place | `01_DATA_MODEL.md` §5.2; `NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` |
| TRG-EX-03, MGAP-EX-02, MQ-EX-01 | `slv_pn_order_item_hotels`, latest Postgres row; key `order_id` unconfirmed (K1); confirmation pending with the source team | `01_DATA_MODEL.md` §5.1; `CTRL_TABLES_CONTEXT.md` §11 |
| COL-EX-01, COL-EX-02, COL-EX-03, MGAP-EX-01, MGAP-EX-03 | Key columns at N4 and gold; gold `poi_name`; N4 columns and data types not stated | `01_DATA_MODEL.md` §6, §7 |
| COL-EX-04 | `$`, `_doc.source_name,_doc.source_id`, `string`, `HASH_MD5_UUID`, key `poi_id`, `key_order` from key position | `CTRL_TABLES_CONTEXT.md` §5; `NB_CREATE_DDL.ipynb` `POI_ID`, `TABLE_CONFIGS_3P`, `flatten_table_configs` |
| MCONF-EX-01, MQ-EX-03 | Activity name `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` versus `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`; JSON path in `pipelines/` | `AGENTS.md` §9; `CTRL_TABLES_CONTEXT.md` §2 |
| BRD section 2 paragraph | PostgreSQL sync by `updated_at` | `01_DATA_MODEL.md` §1, §3, §7 |
| SCOPE-EX-02 | Old `poi_*` tables and old NB_00 chain run in parallel until cutover | `01_DATA_MODEL.md` §1, §9 |
| CSM-EX-01 | PostgreSQL backend reads gold; `updated_at` changes only when `row_hash` changes | `01_DATA_MODEL.md` §1, §3, §7, §10 |
| BR-EX-03, DS-EX-03, BGAP-EX-02, BQ-EX-01 | Gold `short_description` exists; 3P description NULL; partner description source not stated | `01_DATA_MODEL.md` §6, §7 |
| RULE-EX-01, BGAP-EX-01 | L2 holds the language-completeness flag; gold filters by `has_required_langs`; the holding table is not stated; `ref_lang_policy.is_required` | `01_DATA_MODEL.md` §2, §6.1, §7; `02_NAMING_CONVENTION.md` §5.1 |
| RULE-EX-02 | en missing: unaccented vi name; ko missing: copy vi name; applied in L2; descriptions not copied | `01_DATA_MODEL.md` §6, §6.1 |
| ID-EX-01 | 3P `poi_id` formula; applies to every 3P registry table | `AGENTS.md` §9; `01_DATA_MODEL.md` §8; `CTRL_TABLES_CONTEXT.md` §5 |
| ID-EX-02 | Partner `poi_id` formula; no current notebook applies it | `AGENTS.md` §9; `01_DATA_MODEL.md` §8 |
| NFR-EX-01 | Source-to-serving SLA 30 to 60 minutes | `AGENTS.md` §9; `01_DATA_MODEL.md` §1 |

### Residual risks

- R1: The reviewer cannot verify citations against the sources. This is mitigated by T4 and by the provenance table above.
- R2: Claude Code may not honor the `effort` frontmatter key. The user smoke check detects this, and the policy is to stop, not substitute.
- R3: `AGENTS.md` section 2 does not list the analyst. Its write authority rests on this task's request and on Main's `decision.md` entry.
- R4: Under project `dontAsk`, the instruction is the only guard against an analyst write to `architecture.md`. This is accepted because the analyst is user-invoked.
- R5: The round caps are reached. Any new P0 or P1 from the round-2 review routes to `user_decision`.

## Evidence needed

None. No template decision depends on a Fabric DEV fact. Unknown schema and rules stay blank and are marked `MISSING_EVIDENCE` in the examples.

## File blocks

FILE: docs/templates/MAPPING_TEMPLATE.md
# Mẫu Mapping nguồn → đích (VSVN)

> `template_id`: `VSVN-MAPPING-v1`. Mẫu này đi cùng `docs/templates/BRD_TEMPLATE.md` (`VSVN-BRD-v1`). Agent `requirements-analyst` (`.claude/agents/requirements-analyst.md`) đọc file đã điền theo đúng tên mục, tên cột và giá trị cho phép của mẫu này.
> Phần mô tả viết bằng tiếng Việt. Tên trường, tên bảng, tên cột, giá trị trạng thái và định danh giữ bằng tiếng Anh.
> Dòng có nhãn `[EXAMPLE]` chỉ minh hoạ cách điền. Đó không phải dữ liệu production và không phải yêu cầu thật. Mọi giá trị trong dòng `[EXAMPLE]` có nguồn ở `context_ref`, hoặc để trống và đặt `MISSING_EVIDENCE`.
> Không ghi dữ liệu cá nhân, secret, token hoặc trích xuất dữ liệu production vào file này.

## Cách điền

1. Sao chép mẫu thành `docs/requirements/<task_id>/MAPPING.md`. Mỗi task có đúng 1 file Mapping và 1 file Business Requirements Document (BRD). Không lưu bản đã điền trong `.ai/tasks/`, vì task artifact ở đó phải viết bằng tiếng Anh (`AGENTS.md §1`).
2. Giữ nguyên mục "Quy ước dùng chung", tên mục, tên cột và thứ tự cột. Không xoá cột. Ô không dùng thì để trống.
3. Xoá mọi dòng `[EXAMPLE]` trước khi đặt `doc_status` là `READY_FOR_ANALYSIS`. Agent bỏ qua dòng `[EXAMPLE]` còn sót và báo lại.
4. Chỉ ghi một giá trị khi có nguồn hợp lệ theo `evidence_status` ở mục "Quy ước dùng chung". Ghi nguồn vào `context_ref`.
5. Khi chưa có nguồn: để trống ô, đặt `MISSING_EVIDENCE` và thêm 1 dòng ở mục 6 có `blocks` chứa ID của dòng đó. Nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận: được ghi giá trị đó, đặt `MISSING_EVIDENCE` và nêu lý do ở `note`. Không đoán tên bảng, tên cột, kiểu dữ liệu, khoá, grain, giá trị enum, công thức hoặc rule.
6. Dòng ở mục 6 có `resolution_type` là `USER_ANSWER` hoặc `EXTERNAL` cần ít nhất 1 câu hỏi ở mục 8 có `blocks` chứa `gap_id` đó.
7. Hai nguồn trong repository nói khác nhau: không tự chọn. Đặt `CONFLICT`, thêm 1 dòng ở mục 7 và 1 câu hỏi ở mục 8 có `blocks` chứa `conflict_id` đó (`docs/context/00_README.md`, mục "Quy tắc khi làm việc với bộ này").
8. Tên mới chưa có trong repository: đặt `name_status` là `PROPOSED` và ghi nhãn `[PROPOSED]` ở `note`. Tên bảng mới phải đúng tiền tố của tầng ở mục "Quy ước dùng chung".
9. Không ghi tên notebook mới ở mục 2 khi `grain_evidence` hoặc `key_evidence` của bảng đích liên quan ở mục 4 là `MISSING_EVIDENCE` hoặc `CONFLICT`.
10. Khi có câu trả lời: ghi `answer` và `answered_on` ở mục 8, sửa ô liên quan theo luật của `evidence_status`, rồi tăng `version`.

## Quy ước dùng chung

> Mục này giống hệt nhau ở `docs/templates/MAPPING_TEMPLATE.md` và `docs/templates/BRD_TEMPLATE.md`. Không sửa mục này khi điền tài liệu.

### Giá trị cho phép

| field | value | Ý nghĩa |
|---|---|---|
| `doc_status` | `DRAFT` | Đang soạn. Agent `requirements-analyst` không phân tích |
| `doc_status` | `READY_FOR_ANALYSIS` | Đã xoá dòng và đoạn `[EXAMPLE]`. Sẵn sàng cho agent `requirements-analyst` |
| `evidence_status`, `*_evidence` | `CONTEXT_STATED` | Một file trong repository nêu đúng giá trị: `AGENTS.md`, file trong `docs/context/`, notebook trong `notebooks/` hoặc pipeline trong `pipelines/`. `context_ref` ghi đường dẫn và mục, hoặc đường dẫn và tên cell, biến hay hàm trong notebook |
| `evidence_status`, `*_evidence` | `TASK_EVIDENCE` | Kết quả probe đã làm sạch ở `.ai/tasks/<task_id>/evidence/results/` nêu đúng giá trị. `context_ref` ghi đường dẫn file kết quả |
| `evidence_status`, `*_evidence` | `USER_STATED` | Người dùng hoặc chủ nghiệp vụ đặt ra giá trị. `context_ref` ghi `USER_INPUT` khi giá trị nêu ngay trong tài liệu, hoặc ghi `q_id` của câu hỏi đã có `answer` và `answered_on`. Chỉ dùng cho yêu cầu và quyết định: câu yêu cầu, phạm vi, mức ưu tiên, rule mới, giá trị phi chức năng, tên `PROPOSED`, grain và khoá của bảng `PROPOSED`, nơi đặt rule mới. Không dùng cho sự kiện về đối tượng `EXISTING`: cột, grain, khoá, kiểu dữ liệu, độ duy nhất, tỉ lệ NULL, định dạng, giá trị enum, rule hoặc công thức đã có. Các sự kiện đó cần `CONTEXT_STATED` hoặc `TASK_EVIDENCE` (`AGENTS.md §5`, `§8`) |
| `evidence_status`, `*_evidence` | `MISSING_EVIDENCE` | Chưa có nguồn hợp lệ, hoặc nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận. Cần 1 dòng ở mục thiếu evidence của cùng file, có `blocks` chứa ID của dòng |
| `evidence_status`, `*_evidence` | `CONFLICT` | Hai nguồn trong repository nói khác nhau. Cần 1 dòng ở mục mâu thuẫn và 1 câu hỏi ở mục câu hỏi mở của cùng file |
| `evidence_status`, `*_evidence` | Nhiều giá trị | Được ghi nhiều giá trị trong `CONTEXT_STATED`, `TASK_EVIDENCE`, `USER_STATED`, cách nhau bằng dấu phẩy, khi giá trị dựa trên nhiều loại nguồn. `MISSING_EVIDENCE` và `CONFLICT` luôn đứng một mình |
| `name_status`, `trg_name_status` | `EXISTING` | Tên đã có trong repository. `context_ref` chỉ nơi nêu tên |
| `name_status`, `trg_name_status` | `PROPOSED` | Tên mới chưa có trong repository. Ghi nhãn `[PROPOSED]` ở `note` (`docs/context/02_NAMING_CONVENTION.md`, phần đầu file) |
| `layer` | `bronze`, `silver_l1`, `silver_l2`, `ref`, `gold`, `ctrl` | Tầng theo `docs/context/01_DATA_MODEL.md §2` |
| `resolution_type` | `REPO_READ` | Đọc thêm file trong repository |
| `resolution_type` | `PROBE` | Probe chỉ đọc trên Fabric DEV. Main viết probe, người dùng chạy (`AGENTS.md §8`). Ghi tiêu chí đạt và không đạt bằng lời, không viết code |
| `resolution_type` | `USER_ANSWER` | Người dùng hoặc chủ nghiệp vụ trả lời. Cần 1 câu hỏi có `blocks` chứa `gap_id` |
| `resolution_type` | `EXTERNAL` | Chờ team nguồn hoặc hệ thống bên ngoài. Cần 1 câu hỏi có `blocks` chứa `gap_id` |
| `priority` | `MUST`, `SHOULD`, `COULD` | Mức ưu tiên của yêu cầu ở BRD mục 5 |
| `scope` | `IN`, `OUT` | Trong hoặc ngoài phạm vi ở BRD mục 3 |
| `is_key` | `true`, `false` | Cột thuộc khoá của bảng đích ở Mapping mục 5 |
| `key_order` | Số nguyên từ 1 | Thứ tự trong khoá ghép của bảng silver L1 (`ctrl_cfg_schema_registry.key_order`, `docs/context/CTRL_TABLES_CONTEXT.md §5`). Để trống ở tầng khác và khi `is_key` là `false` |
| `field` | `pl_name`, `load_mode`, `orchestrator`, `nb_name`, `cadence` | Cột `field` ở Mapping mục 2 |
| `load_mode`, `convert_rule` | Giá trị ở `docs/context/02_NAMING_CONVENTION.md §6` | Mẫu không chép lại danh sách |
| `context_ref` | `<path> §<mục>`, `<path> <cell, biến hoặc hàm>`, `<file kết quả>`, `<q_id>`, `USER_INPUT` | Nguồn của giá trị. Nhiều nguồn cách nhau bằng dấu phẩy |

### Tiền tố bảng theo tầng

| layer | lakehouse_schema | Tiền tố bảng | context_ref |
|---|---|---|---|
| `bronze` | `lh_vv_bronze.dbo` | Không có tiền tố chung. Hai bảng raw đang dùng là `partner_raw_data` và `brz_3rd_crawler_poi_stream`. Không suy ra quy tắc đặt tên raw | `docs/context/02_NAMING_CONVENTION.md §1` |
| `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_` cho partner (`slv_pn_<bảng Postgres>`). `slv_3p_` cho 3rd-party (`slv_3p_poi` và `slv_3p_poi_<khối>`). `slv_pm_` `[PROPOSED]` cho POI management | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ref` | `lh_vv_silver.dbo` | `ref_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `gold` | `lh_vv_gold.dbo` | `gld_`. Bảng phục vụ đặt tên `gld_srv_<chủ đề>_<grain>` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ctrl` | `lh_vv_ctrl.dbo` | `ctrl_mng_`, `ctrl_cfg_`, `ctrl_log_`, `ctrl_cdc_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |

Bảng cũ không theo tiền tố trên, như `poi_master`, `destination_ward_mapping`, bảng `poi_*` cũ ở silver và `lh_vv_bronze.partner.*`, giữ nguyên tới cutover (`docs/context/01_DATA_MODEL.md §1`, `docs/context/02_NAMING_CONVENTION.md §1`). Yêu cầu có bảng đích là bảng cũ cần 1 câu hỏi cho người dùng.

### Định danh

| ID | Dạng | Ghi ở |
|---|---|---|
| `task_id` | Tên thư mục `.ai/tasks/<task_id>/`, dạng `YYYYMMDD-slug` (`AGENTS.md §4`) | Mục 1 của cả hai file |
| `mapping_id` | `MAP-<task_id>` | Mục 1 của cả hai file |
| `brd_id` | `BRD-<task_id>` | Mục 1 của cả hai file |
| `version` | Số nguyên từ 1, tăng 1 mỗi lần sửa file | Mục 1 của từng file |
| `updated_on` | `YYYY-MM-DD` | Mục 1 của từng file |

| Tiền tố dòng | File | Mục |
|---|---|---|
| `FLOW-` | Mapping | 2. Luồng xử lý |
| `SRC-` | Mapping | 3. Bảng nguồn |
| `TRG-` | Mapping | 4. Bảng đích |
| `COL-` | Mapping | 5. Mapping cột |
| `MGAP-` | Mapping | 6. Mục thiếu evidence |
| `MCONF-` | Mapping | 7. Mâu thuẫn trong repository |
| `MQ-` | Mapping | 8. Câu hỏi mở |
| `SCOPE-` | BRD | 3. Phạm vi |
| `CSM-` | BRD | 4. Bên sử dụng dữ liệu |
| `BR-` | BRD | 5. Yêu cầu nghiệp vụ |
| `DS-` | BRD | 6. Nguồn dữ liệu |
| `RULE-` | BRD | 7. Rule nghiệp vụ |
| `ID-` | BRD | 8. Định danh |
| `NFR-` | BRD | 9. Yêu cầu phi chức năng |
| `AC-` | BRD | 10. Tiêu chí nghiệm thu |
| `BGAP-` | BRD | 11. Mục thiếu evidence |
| `BCONF-` | BRD | 12. Mâu thuẫn trong repository |
| `BQ-` | BRD | 13. Câu hỏi mở |

- Dòng thật: tiền tố cộng 3 chữ số, bắt đầu từ `001`, không trùng trong file.
- Dòng minh hoạ: tiền tố cộng `EX-` và 2 chữ số. Ô đầu của dòng bắt đầu bằng `[EXAMPLE]`.
- Cột trỏ sang dòng khác (`trg_ids`, `src_id`, `trg_id`, `req_ids`, `rule_ids`, `id_rule_ids`, `consumer_id`, `blocks`) chỉ ghi ID của dòng có thật ở một trong hai file. Nhiều ID cách nhau bằng dấu phẩy.

### Liên kết giữa hai file

- Mapping mục 5: `req_ids` trỏ tới BRD mục 5, `rule_ids` trỏ tới BRD mục 7.
- BRD mục 5: `trg_tbl`, `grain` và `key_columns` khớp dòng có cùng `trg_tbl` ở Mapping mục 4.
- BRD mục 6: tập `src_tbl` của một yêu cầu khớp tập `src_tbl` ở Mapping mục 3 của các dòng Mapping mục 5 có `req_ids` chứa yêu cầu đó.
- Hai file lệch nhau thì sửa cho khớp trước khi đặt `READY_FOR_ANALYSIS`. Agent `requirements-analyst` báo mọi chỗ lệch là `CONFLICT`.

### Ràng buộc nền tảng

- Chỉ Eventstream ghi bronze, bằng append. Bronze không sửa, không xoá (`docs/context/01_DATA_MODEL.md §1`, `§2`). Yêu cầu không có bảng đích ở bronze.
- Silver L1 chỉ đưa payload về đúng cấu trúc nguồn và chuyển kiểu theo cấu hình. Silver L1 không có rule nghiệp vụ (`docs/context/01_DATA_MODEL.md §2`).
- Rule nghiệp vụ chỉ nằm ở silver L2 (`slv_poi_*`) hoặc bảng `ref_*`. 1 dòng của bảng `ref_*` là 1 rule (`docs/context/01_DATA_MODEL.md §2`, `AGENTS.md §9`).
- Gold chỉ đồng bộ và phơi dữ liệu: join theo khoá, gom, tính `row_hash`, lọc theo cờ silver. Gold không xử lý nghiệp vụ và không đọc gold khác (`docs/context/01_DATA_MODEL.md §2`).
- Tiền tố bảng khớp tầng theo bảng "Tiền tố bảng theo tầng".
- `poi_id` không bao giờ chứa ngôn ngữ. Không dùng `poi_uid` (`AGENTS.md §9`).
- Tên cột nghiệp vụ không trùng cột kỹ thuật của tầng (`docs/context/02_NAMING_CONVENTION.md §5.2`).
- Tên notebook theo `docs/context/02_NAMING_CONVENTION.md §2`. Tên pipeline theo `docs/context/02_NAMING_CONVENTION.md §3`.

## 1. Thông tin tài liệu

| field | value |
|---|---|
| `template_id` | `VSVN-MAPPING-v1` |
| `mapping_id` | `MAP-<task_id>` |
| `task_id` | `<task_id>` |
| `brd_id` | `BRD-<task_id>` |
| `version` | `<số nguyên từ 1>` |
| `doc_status` | `DRAFT` hoặc `READY_FOR_ANALYSIS` |
| `owner_role` | `<vai trò hoặc nhóm phụ trách; không ghi tên người, email, số điện thoại>` |
| `updated_on` | `<YYYY-MM-DD>` |

## 2. Luồng xử lý

> 1 dòng = 1 thuộc tính của luồng ghi các bảng đích ở `trg_ids` (mục 4). `field` chỉ nhận giá trị ở "Giá trị cho phép".
> `load_mode` theo `docs/context/02_NAMING_CONVENTION.md §6`. Tên notebook theo `§2`, tên pipeline theo `§3` của file đó.

| flow_id | trg_ids | field | value | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|
| `[EXAMPLE] FLOW-EX-01` | `TRG-EX-01` | `orchestrator` | `NB_00_ORCHES_SLV_TO_GLD` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §3`, `docs/context/02_NAMING_CONVENTION.md §2` | Chọn luồng bằng tham số `p_pl_name` |
| `[EXAMPLE] FLOW-EX-02` | `TRG-EX-01` | `load_mode` | `RECOMPUTE` | | `CONTEXT_STATED` | `docs/context/CTRL_TABLES_CONTEXT.md §2`, `§3` | Cạnh của luồng tính lại do `NB_00_ORCHES_SLV_TO_GLD` chạy. Cạnh gold chưa được seed (`docs/context/CTRL_TABLES_CONTEXT.md §10`, dòng 08/10) |
| `[EXAMPLE] FLOW-EX-03` | `TRG-EX-01` | `pl_name` | | | `MISSING_EVIDENCE` | `docs/context/02_NAMING_CONVENTION.md §3` | Context chỉ nêu hậu tố nhịp `_1H` là `[PROPOSED]`, chưa nêu tên pipeline. Xem `MGAP-EX-04` |
| `[EXAMPLE] FLOW-EX-04` | `TRG-EX-01` | `cadence` | Hằng giờ | | `CONTEXT_STATED` | `AGENTS.md §9` | Luồng silver → gold POI |
| `FLOW-001` | | | | | | | |

## 3. Bảng nguồn

> 1 dòng = 1 bảng nguồn. `layer` và `lakehouse_schema` theo bảng "Tiền tố bảng theo tầng".
> Grain trả lời câu "1 dòng của bảng ứng với cái gì". Khoá là các cột làm cho mỗi dòng là duy nhất.
> Bảng nguồn ở `bronze`: ghi grain theo `docs/context/01_DATA_MODEL.md §4`, để trống `key_columns` và `key_evidence`. Khoá của bảng đích silver L1 ghi ở mục 5 theo `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` (`docs/context/CTRL_TABLES_CONTEXT.md §5`).
> Bảng nguồn ở tầng khác: grain và khoá là bắt buộc. Chưa có nguồn thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 6.

| src_id | layer | lakehouse_schema | src_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] SRC-EX-01` | `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_localization` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §2`, `§6` | Node N4. Notebook node chưa có trong repository |
| `[EXAMPLE] SRC-EX-02` | `bronze` | `lh_vv_bronze.dbo` | `brz_3rd_crawler_poi_stream` | 1 event = 1 tài liệu đầy đủ lúc crawl | `CONTEXT_STATED` | | | `EXISTING` | `docs/context/01_DATA_MODEL.md §4` | Bảng raw. `event_id` có giá trị trùng và không dùng làm khoá (`docs/context/99_PAIN_POINTS.md §2`, D12) |
| `SRC-001` | | | | | | | | | | |

## 4. Bảng đích

> 1 dòng = 1 bảng đích. Tầng và tiền tố theo bảng "Tiền tố bảng theo tầng". Bảng đích tuân theo "Ràng buộc nền tảng".
> Grain và khoá của bảng đích là bắt buộc. Thiếu một trong hai thì yêu cầu liên quan chưa được coi là đã map, và không được ghi tên notebook mới cho bảng đó.

| trg_id | layer | lakehouse_schema | trg_tbl | grain | grain_evidence | key_columns | key_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] TRG-EX-01` | `gold` | `lh_vv_gold.dbo` | `gld_srv_poi_multi_lang` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §7` | Chiếu 1–1 từ N4 |
| `[EXAMPLE] TRG-EX-02` | `silver_l1` | `lh_vv_silver.dbo` | `slv_3p_poi` | 1 dòng / địa điểm (`poi_id`) | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.2`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | `load_mode` là `DOC`, `src_object` là `$` |
| `[EXAMPLE] TRG-EX-03` | `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_order_item_hotels` | 1 dòng / 1 dòng của bảng Postgres nguồn, bản mới nhất | `CONTEXT_STATED` | `order_id` | `MISSING_EVIDENCE` | `EXISTING` | `docs/context/01_DATA_MODEL.md §5.1`, `docs/context/CTRL_TABLES_CONTEXT.md §11` | Context ghi khoá `order_id` kèm "chưa xác nhận PK" (K1). Xem `MGAP-EX-02` |
| `TRG-001` | | | | | | | | | | |

## 5. Mapping cột

> 1 dòng = 1 cột đích. `req_ids` trỏ tới BRD mục 5. `rule_ids` trỏ tới BRD mục 7. `data_type` là kiểu Spark của cột đích (`docs/context/CTRL_TABLES_CONTEXT.md §5`, cột `data_type`).
> Ô bắt buộc ở mọi tầng: `req_ids`, `src_id`, `src_column_or_json_path`, `trg_id`, `trg_column`, `data_type`, `is_key`.
> Silver L1: bắt buộc thêm `src_object`, `convert_rule`, và `key_order` khi `is_key` là `true`. 1 dòng ứng với 1 dòng của `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` và theo luật cấu hình ở `docs/context/CTRL_TABLES_CONTEXT.md §5`. `rule_ids` để trống vì silver L1 không có rule nghiệp vụ.
> Silver L2: `src_object`, `convert_rule`, `key_order` để trống. Rule nghiệp vụ tạo ra giá trị của cột ghi ở `rule_ids`.
> Gold: `src_object`, `convert_rule`, `key_order`, `rule_ids` để trống, theo "Ràng buộc nền tảng".
> `evidence_status` của dòng: khi mọi ô bắt buộc đã có nguồn, ghi giá trị theo nguồn và ghi đủ nguồn ở `context_ref`. Còn ô bắt buộc chưa có nguồn: để trống ô đó, đặt `MISSING_EVIDENCE`, ghi tên ô ở `note` và thêm dòng ở mục 6.

| col_id | req_ids | src_id | src_object | src_column_or_json_path | trg_id | trg_column | data_type | convert_rule | is_key | key_order | rule_ids | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] COL-EX-01` | `BR-EX-01` | `SRC-EX-01` | | `poi_id` | `TRG-EX-01` | `poi_id` | | | `true` | | | `MISSING_EVIDENCE` | `docs/context/01_DATA_MODEL.md §6`, `§7` | `data_type` trống: context không nêu kiểu của cột. Xem `MGAP-EX-01` |
| `[EXAMPLE] COL-EX-02` | `BR-EX-01` | `SRC-EX-01` | | `lang` | `TRG-EX-01` | `lang` | | | `true` | | | `MISSING_EVIDENCE` | `docs/context/01_DATA_MODEL.md §6`, `§7` | `data_type` trống: context không nêu kiểu của cột. Xem `MGAP-EX-01` |
| `[EXAMPLE] COL-EX-03` | `BR-EX-01` | `SRC-EX-01` | | | `TRG-EX-01` | `poi_name` | | | `false` | | | `MISSING_EVIDENCE` | `docs/context/01_DATA_MODEL.md §6`, `§7` | `src_column_or_json_path` và `data_type` trống. Context liệt kê `poi_name` ở gold nhưng không liệt kê cột của `slv_poi_localization`. Xem `MGAP-EX-01`, `MGAP-EX-03` |
| `[EXAMPLE] COL-EX-04` | `BR-EX-02` | `SRC-EX-02` | `$` | `_doc.source_name,_doc.source_id` | `TRG-EX-02` | `poi_id` | `string` | `HASH_MD5_UUID` | `true` | `1` | | `CONTEXT_STATED` | `docs/context/CTRL_TABLES_CONTEXT.md §5`, `notebooks/NB_CREATE_DDL.ipynb` `POI_ID`, `TABLE_CONFIGS_3P`, `flatten_table_configs` | Notebook khai báo `POI_ID` với `path` `_doc.source_name,_doc.source_id`, `type` `string`, `rule` `HASH_MD5_UUID`, và `key` của `slv_3p_poi` là `poi_id`. `flatten_table_configs` đặt `key_order` theo vị trí trong `key`, bắt đầu từ 1 |
| `COL-001` | | | | | | | | | | | | | | |

## 6. Mục thiếu evidence

> 1 dòng = 1 sự kiện còn thiếu trong file này. `blocks` ghi ID bị chặn. `PROBE` ghi tiêu chí đạt và không đạt bằng lời, không viết code probe.

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] MGAP-EX-01` | `COL-EX-01`, `COL-EX-02`, `COL-EX-03` | Kiểu dữ liệu của `poi_id`, `lang`, `poi_name` ở `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | Context nêu grain, khoá và tên cột của bảng nhưng không nêu kiểu dữ liệu (`docs/context/01_DATA_MODEL.md §7`) | `PROBE` | Đạt: schema thật của bảng trên Fabric DEV có đủ 3 cột và cho biết kiểu của từng cột. Không đạt: thiếu bảng hoặc thiếu cột | |
| `[EXAMPLE] MGAP-EX-02` | `TRG-EX-03` | Khoá chính của `slv_pn_order_item_hotels` | Context ghi khoá `order_id` kèm "chưa xác nhận PK" (K1). Việc chốt khoá còn chờ team nguồn (`docs/context/CTRL_TABLES_CONTEXT.md §11`) | `EXTERNAL` | Đạt: xác nhận của team nguồn được ghi vào một file trong repository, rồi `key_evidence` đổi sang `CONTEXT_STATED`. Không đạt: chưa có xác nhận | |
| `[EXAMPLE] MGAP-EX-03` | `COL-EX-03` | Cột của `slv_poi_localization` chứa tên POI | Context không liệt kê cột của N4. Notebook node N4 chưa có trong repository (`docs/context/01_DATA_MODEL.md §6`) | `PROBE` | Đạt: schema thật của `lh_vv_silver.dbo.slv_poi_localization` có đúng 1 cột tên POI. Không đạt: không có cột nào, hoặc có hơn 1 cột ứng viên | |
| `[EXAMPLE] MGAP-EX-04` | `FLOW-EX-03` | Tên pipeline của luồng tính lại hằng giờ ghi `gld_srv_poi_multi_lang` | Context chỉ nêu hậu tố nhịp `_1H` là `[PROPOSED]` (`docs/context/02_NAMING_CONVENTION.md §3`) | `USER_ANSWER` | Đạt: tên pipeline đã có được ghi trong một file của repository, hoặc người dùng chốt tên mới `[PROPOSED]` có hậu tố nhịp khớp `CADENCE_RE` (`docs/context/02_NAMING_CONVENTION.md §3`). Không đạt: chưa có tên | |
| `MGAP-001` | | | | | | |

## 7. Mâu thuẫn trong repository

> Ghi cả hai nguồn và nội dung từng nguồn. Không tự chọn bên nào. Mỗi dòng cần 1 câu hỏi ở mục 8.

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|
| `[EXAMPLE] MCONF-EX-01` | | Tên activity notebook trong `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` | `AGENTS.md §9`: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` | `docs/context/CTRL_TABLES_CONTEXT.md §2`: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` | Không tự chọn. Xem `MQ-EX-03` |
| `MCONF-001` | | | | | |

## 8. Câu hỏi mở

> 1 dòng = 1 câu hỏi cho người dùng, chủ nghiệp vụ hoặc team nguồn. `blocks` chứa `gap_id` hoặc `conflict_id` liên quan. Khi có câu trả lời, ghi `answer`, `answered_on` và làm theo bước 10 của "Cách điền".

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
| `[EXAMPLE] MQ-EX-01` | `MGAP-EX-02` | Team nguồn đã xác nhận khoá chính của bảng Postgres nguồn của `slv_pn_order_item_hotels` chưa? | `EXTERNAL` | | |
| `[EXAMPLE] MQ-EX-02` | `MGAP-EX-04` | Luồng tính lại hằng giờ ghi `gld_srv_poi_multi_lang` đã có pipeline chưa, và `pl_name` là gì? | `USER_ANSWER` | | |
| `[EXAMPLE] MQ-EX-03` | `MCONF-EX-01` | Tên activity nào khớp JSON trong `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/`, và tài liệu nào cần sửa? | `USER_ANSWER` | | |
| `MQ-001` | | | | | |
END_FILE
FILE: docs/templates/BRD_TEMPLATE.md
# Mẫu Business Requirements Document (BRD) — VSVN

> `template_id`: `VSVN-BRD-v1`. Mẫu này đi cùng `docs/templates/MAPPING_TEMPLATE.md` (`VSVN-MAPPING-v1`). Agent `requirements-analyst` (`.claude/agents/requirements-analyst.md`) đọc file đã điền theo đúng tên mục, tên cột và giá trị cho phép của mẫu này.
> Phần mô tả viết bằng tiếng Việt. Tên trường, tên bảng, tên cột, giá trị trạng thái và định danh giữ bằng tiếng Anh.
> Dòng và đoạn có nhãn `[EXAMPLE]` chỉ minh hoạ cách điền. Đó không phải dữ liệu production và không phải yêu cầu thật. Mọi giá trị trong phần `[EXAMPLE]` có nguồn ở `context_ref`, hoặc để trống và đặt `MISSING_EVIDENCE`.
> Không ghi dữ liệu cá nhân, secret, token hoặc trích xuất dữ liệu production vào file này.

## Cách điền

1. Sao chép mẫu thành `docs/requirements/<task_id>/BRD.md`. Mỗi task có đúng 1 file BRD và 1 file Mapping. Không lưu bản đã điền trong `.ai/tasks/`, vì task artifact ở đó phải viết bằng tiếng Anh (`AGENTS.md §1`).
2. Giữ nguyên mục "Quy ước dùng chung", tên mục, tên cột và thứ tự cột. Không xoá cột. Ô không dùng thì để trống.
3. Xoá mọi dòng và đoạn `[EXAMPLE]` trước khi đặt `doc_status` là `READY_FOR_ANALYSIS`. Agent bỏ qua phần `[EXAMPLE]` còn sót và báo lại.
4. Mỗi yêu cầu là 1 dòng ở mục 5. `statement` là yêu cầu của người dùng, viết sao cho kiểm chứng được. Sự kiện về hệ thống đã có được nêu trong yêu cầu cần `context_ref`.
5. Mỗi yêu cầu có bảng đích, grain và khoá ở mục 5, và có ít nhất 1 dòng nguồn ở mục 6. Cột nguồn chi tiết ghi ở Mapping mục 5.
6. Rule nghiệp vụ ghi ở mục 7. Rule repository đã nêu: đặt `CONTEXT_STATED` và ghi `context_ref`. Rule mới do người dùng đặt ra: ghi nguyên văn, đặt `USER_STATED` và ghi `context_ref` là `USER_INPUT`. Không tự đặt rule. Rule chỉ nằm ở tầng cho phép trong "Ràng buộc nền tảng".
7. Chỉ ghi một giá trị khi có nguồn hợp lệ theo `evidence_status` ở mục "Quy ước dùng chung". Ghi nguồn vào `context_ref`.
8. Khi chưa có nguồn: để trống ô, đặt `MISSING_EVIDENCE` và thêm 1 dòng ở mục 11 có `blocks` chứa ID của dòng đó. Nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận: được ghi giá trị đó, đặt `MISSING_EVIDENCE` và nêu lý do ở `note`. Không đoán bảng, cột, kiểu dữ liệu, khoá, grain, giá trị enum, công thức hoặc rule.
9. Dòng ở mục 11 có `resolution_type` là `USER_ANSWER` hoặc `EXTERNAL` cần ít nhất 1 câu hỏi ở mục 13 có `blocks` chứa `gap_id` đó.
10. Hai nguồn trong repository nói khác nhau: không tự chọn. Đặt `CONFLICT`, thêm 1 dòng ở mục 12 và 1 câu hỏi ở mục 13 có `blocks` chứa `conflict_id` đó (`docs/context/00_README.md`, mục "Quy tắc khi làm việc với bộ này").
11. Tên mới chưa có trong repository: đặt `name_status` hoặc `trg_name_status` là `PROPOSED` và ghi nhãn `[PROPOSED]` ở `note`. Tên bảng mới phải đúng tiền tố của tầng ở mục "Quy ước dùng chung".
12. Khi có câu trả lời: ghi `answer` và `answered_on` ở mục 13, sửa ô liên quan theo luật của `evidence_status`, rồi tăng `version`.

## Quy ước dùng chung

> Mục này giống hệt nhau ở `docs/templates/MAPPING_TEMPLATE.md` và `docs/templates/BRD_TEMPLATE.md`. Không sửa mục này khi điền tài liệu.

### Giá trị cho phép

| field | value | Ý nghĩa |
|---|---|---|
| `doc_status` | `DRAFT` | Đang soạn. Agent `requirements-analyst` không phân tích |
| `doc_status` | `READY_FOR_ANALYSIS` | Đã xoá dòng và đoạn `[EXAMPLE]`. Sẵn sàng cho agent `requirements-analyst` |
| `evidence_status`, `*_evidence` | `CONTEXT_STATED` | Một file trong repository nêu đúng giá trị: `AGENTS.md`, file trong `docs/context/`, notebook trong `notebooks/` hoặc pipeline trong `pipelines/`. `context_ref` ghi đường dẫn và mục, hoặc đường dẫn và tên cell, biến hay hàm trong notebook |
| `evidence_status`, `*_evidence` | `TASK_EVIDENCE` | Kết quả probe đã làm sạch ở `.ai/tasks/<task_id>/evidence/results/` nêu đúng giá trị. `context_ref` ghi đường dẫn file kết quả |
| `evidence_status`, `*_evidence` | `USER_STATED` | Người dùng hoặc chủ nghiệp vụ đặt ra giá trị. `context_ref` ghi `USER_INPUT` khi giá trị nêu ngay trong tài liệu, hoặc ghi `q_id` của câu hỏi đã có `answer` và `answered_on`. Chỉ dùng cho yêu cầu và quyết định: câu yêu cầu, phạm vi, mức ưu tiên, rule mới, giá trị phi chức năng, tên `PROPOSED`, grain và khoá của bảng `PROPOSED`, nơi đặt rule mới. Không dùng cho sự kiện về đối tượng `EXISTING`: cột, grain, khoá, kiểu dữ liệu, độ duy nhất, tỉ lệ NULL, định dạng, giá trị enum, rule hoặc công thức đã có. Các sự kiện đó cần `CONTEXT_STATED` hoặc `TASK_EVIDENCE` (`AGENTS.md §5`, `§8`) |
| `evidence_status`, `*_evidence` | `MISSING_EVIDENCE` | Chưa có nguồn hợp lệ, hoặc nguồn có ghi giá trị nhưng nói rõ là chưa xác nhận. Cần 1 dòng ở mục thiếu evidence của cùng file, có `blocks` chứa ID của dòng |
| `evidence_status`, `*_evidence` | `CONFLICT` | Hai nguồn trong repository nói khác nhau. Cần 1 dòng ở mục mâu thuẫn và 1 câu hỏi ở mục câu hỏi mở của cùng file |
| `evidence_status`, `*_evidence` | Nhiều giá trị | Được ghi nhiều giá trị trong `CONTEXT_STATED`, `TASK_EVIDENCE`, `USER_STATED`, cách nhau bằng dấu phẩy, khi giá trị dựa trên nhiều loại nguồn. `MISSING_EVIDENCE` và `CONFLICT` luôn đứng một mình |
| `name_status`, `trg_name_status` | `EXISTING` | Tên đã có trong repository. `context_ref` chỉ nơi nêu tên |
| `name_status`, `trg_name_status` | `PROPOSED` | Tên mới chưa có trong repository. Ghi nhãn `[PROPOSED]` ở `note` (`docs/context/02_NAMING_CONVENTION.md`, phần đầu file) |
| `layer` | `bronze`, `silver_l1`, `silver_l2`, `ref`, `gold`, `ctrl` | Tầng theo `docs/context/01_DATA_MODEL.md §2` |
| `resolution_type` | `REPO_READ` | Đọc thêm file trong repository |
| `resolution_type` | `PROBE` | Probe chỉ đọc trên Fabric DEV. Main viết probe, người dùng chạy (`AGENTS.md §8`). Ghi tiêu chí đạt và không đạt bằng lời, không viết code |
| `resolution_type` | `USER_ANSWER` | Người dùng hoặc chủ nghiệp vụ trả lời. Cần 1 câu hỏi có `blocks` chứa `gap_id` |
| `resolution_type` | `EXTERNAL` | Chờ team nguồn hoặc hệ thống bên ngoài. Cần 1 câu hỏi có `blocks` chứa `gap_id` |
| `priority` | `MUST`, `SHOULD`, `COULD` | Mức ưu tiên của yêu cầu ở BRD mục 5 |
| `scope` | `IN`, `OUT` | Trong hoặc ngoài phạm vi ở BRD mục 3 |
| `is_key` | `true`, `false` | Cột thuộc khoá của bảng đích ở Mapping mục 5 |
| `key_order` | Số nguyên từ 1 | Thứ tự trong khoá ghép của bảng silver L1 (`ctrl_cfg_schema_registry.key_order`, `docs/context/CTRL_TABLES_CONTEXT.md §5`). Để trống ở tầng khác và khi `is_key` là `false` |
| `field` | `pl_name`, `load_mode`, `orchestrator`, `nb_name`, `cadence` | Cột `field` ở Mapping mục 2 |
| `load_mode`, `convert_rule` | Giá trị ở `docs/context/02_NAMING_CONVENTION.md §6` | Mẫu không chép lại danh sách |
| `context_ref` | `<path> §<mục>`, `<path> <cell, biến hoặc hàm>`, `<file kết quả>`, `<q_id>`, `USER_INPUT` | Nguồn của giá trị. Nhiều nguồn cách nhau bằng dấu phẩy |

### Tiền tố bảng theo tầng

| layer | lakehouse_schema | Tiền tố bảng | context_ref |
|---|---|---|---|
| `bronze` | `lh_vv_bronze.dbo` | Không có tiền tố chung. Hai bảng raw đang dùng là `partner_raw_data` và `brz_3rd_crawler_poi_stream`. Không suy ra quy tắc đặt tên raw | `docs/context/02_NAMING_CONVENTION.md §1` |
| `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_` cho partner (`slv_pn_<bảng Postgres>`). `slv_3p_` cho 3rd-party (`slv_3p_poi` và `slv_3p_poi_<khối>`). `slv_pm_` `[PROPOSED]` cho POI management | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ref` | `lh_vv_silver.dbo` | `ref_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `gold` | `lh_vv_gold.dbo` | `gld_`. Bảng phục vụ đặt tên `gld_srv_<chủ đề>_<grain>` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |
| `ctrl` | `lh_vv_ctrl.dbo` | `ctrl_mng_`, `ctrl_cfg_`, `ctrl_log_`, `ctrl_cdc_` | `docs/context/01_DATA_MODEL.md §2`, `docs/context/02_NAMING_CONVENTION.md §1` |

Bảng cũ không theo tiền tố trên, như `poi_master`, `destination_ward_mapping`, bảng `poi_*` cũ ở silver và `lh_vv_bronze.partner.*`, giữ nguyên tới cutover (`docs/context/01_DATA_MODEL.md §1`, `docs/context/02_NAMING_CONVENTION.md §1`). Yêu cầu có bảng đích là bảng cũ cần 1 câu hỏi cho người dùng.

### Định danh

| ID | Dạng | Ghi ở |
|---|---|---|
| `task_id` | Tên thư mục `.ai/tasks/<task_id>/`, dạng `YYYYMMDD-slug` (`AGENTS.md §4`) | Mục 1 của cả hai file |
| `mapping_id` | `MAP-<task_id>` | Mục 1 của cả hai file |
| `brd_id` | `BRD-<task_id>` | Mục 1 của cả hai file |
| `version` | Số nguyên từ 1, tăng 1 mỗi lần sửa file | Mục 1 của từng file |
| `updated_on` | `YYYY-MM-DD` | Mục 1 của từng file |

| Tiền tố dòng | File | Mục |
|---|---|---|
| `FLOW-` | Mapping | 2. Luồng xử lý |
| `SRC-` | Mapping | 3. Bảng nguồn |
| `TRG-` | Mapping | 4. Bảng đích |
| `COL-` | Mapping | 5. Mapping cột |
| `MGAP-` | Mapping | 6. Mục thiếu evidence |
| `MCONF-` | Mapping | 7. Mâu thuẫn trong repository |
| `MQ-` | Mapping | 8. Câu hỏi mở |
| `SCOPE-` | BRD | 3. Phạm vi |
| `CSM-` | BRD | 4. Bên sử dụng dữ liệu |
| `BR-` | BRD | 5. Yêu cầu nghiệp vụ |
| `DS-` | BRD | 6. Nguồn dữ liệu |
| `RULE-` | BRD | 7. Rule nghiệp vụ |
| `ID-` | BRD | 8. Định danh |
| `NFR-` | BRD | 9. Yêu cầu phi chức năng |
| `AC-` | BRD | 10. Tiêu chí nghiệm thu |
| `BGAP-` | BRD | 11. Mục thiếu evidence |
| `BCONF-` | BRD | 12. Mâu thuẫn trong repository |
| `BQ-` | BRD | 13. Câu hỏi mở |

- Dòng thật: tiền tố cộng 3 chữ số, bắt đầu từ `001`, không trùng trong file.
- Dòng minh hoạ: tiền tố cộng `EX-` và 2 chữ số. Ô đầu của dòng bắt đầu bằng `[EXAMPLE]`.
- Cột trỏ sang dòng khác (`trg_ids`, `src_id`, `trg_id`, `req_ids`, `rule_ids`, `id_rule_ids`, `consumer_id`, `blocks`) chỉ ghi ID của dòng có thật ở một trong hai file. Nhiều ID cách nhau bằng dấu phẩy.

### Liên kết giữa hai file

- Mapping mục 5: `req_ids` trỏ tới BRD mục 5, `rule_ids` trỏ tới BRD mục 7.
- BRD mục 5: `trg_tbl`, `grain` và `key_columns` khớp dòng có cùng `trg_tbl` ở Mapping mục 4.
- BRD mục 6: tập `src_tbl` của một yêu cầu khớp tập `src_tbl` ở Mapping mục 3 của các dòng Mapping mục 5 có `req_ids` chứa yêu cầu đó.
- Hai file lệch nhau thì sửa cho khớp trước khi đặt `READY_FOR_ANALYSIS`. Agent `requirements-analyst` báo mọi chỗ lệch là `CONFLICT`.

### Ràng buộc nền tảng

- Chỉ Eventstream ghi bronze, bằng append. Bronze không sửa, không xoá (`docs/context/01_DATA_MODEL.md §1`, `§2`). Yêu cầu không có bảng đích ở bronze.
- Silver L1 chỉ đưa payload về đúng cấu trúc nguồn và chuyển kiểu theo cấu hình. Silver L1 không có rule nghiệp vụ (`docs/context/01_DATA_MODEL.md §2`).
- Rule nghiệp vụ chỉ nằm ở silver L2 (`slv_poi_*`) hoặc bảng `ref_*`. 1 dòng của bảng `ref_*` là 1 rule (`docs/context/01_DATA_MODEL.md §2`, `AGENTS.md §9`).
- Gold chỉ đồng bộ và phơi dữ liệu: join theo khoá, gom, tính `row_hash`, lọc theo cờ silver. Gold không xử lý nghiệp vụ và không đọc gold khác (`docs/context/01_DATA_MODEL.md §2`).
- Tiền tố bảng khớp tầng theo bảng "Tiền tố bảng theo tầng".
- `poi_id` không bao giờ chứa ngôn ngữ. Không dùng `poi_uid` (`AGENTS.md §9`).
- Tên cột nghiệp vụ không trùng cột kỹ thuật của tầng (`docs/context/02_NAMING_CONVENTION.md §5.2`).
- Tên notebook theo `docs/context/02_NAMING_CONVENTION.md §2`. Tên pipeline theo `docs/context/02_NAMING_CONVENTION.md §3`.

## 1. Thông tin tài liệu

| field | value |
|---|---|
| `template_id` | `VSVN-BRD-v1` |
| `brd_id` | `BRD-<task_id>` |
| `task_id` | `<task_id>` |
| `mapping_id` | `MAP-<task_id>` |
| `version` | `<số nguyên từ 1>` |
| `doc_status` | `DRAFT` hoặc `READY_FOR_ANALYSIS` |
| `owner_role` | `<vai trò hoặc nhóm phụ trách; không ghi tên người, email, số điện thoại>` |
| `updated_on` | `<YYYY-MM-DD>` |

## 2. Bối cảnh và mục tiêu

> Viết ngắn: vấn đề nghiệp vụ, ai cần dữ liệu, dùng dữ liệu để làm gì. Không mô tả thiết kế kỹ thuật.

`[EXAMPLE]` Backend PostgreSQL nhận dữ liệu POI từ gold qua đồng bộ theo `updated_at` (`docs/context/01_DATA_MODEL.md §1`, `§3`). Phần minh hoạ của mẫu này dùng một yêu cầu giả định: cần tên POI theo từng ngôn ngữ vi, en, ko trên `gld_srv_poi_multi_lang` (`docs/context/01_DATA_MODEL.md §7`).

`<Mô tả bối cảnh và mục tiêu>`

## 3. Phạm vi

> `scope` là quyết định của người dùng. `evidence_status` và `context_ref` chỉ nguồn của bảng, luồng hoặc ràng buộc có thật được nêu trong `description`.

| scope_id | scope | description | evidence_status | context_ref |
|---|---|---|---|---|
| `[EXAMPLE] SCOPE-EX-01` | `IN` | Tên POI theo ngôn ngữ trên `gld_srv_poi_multi_lang` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §7` |
| `[EXAMPLE] SCOPE-EX-02` | `OUT` | Bảng `poi_*` cũ và chuỗi NB_00 cũ. Hai phần này giữ nguyên và chạy song song tới cutover | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §1`, `§9` |
| `SCOPE-001` | | | | |

## 4. Bên sử dụng dữ liệu

| consumer_id | consumer | reads_from | sync_rule | evidence_status | context_ref |
|---|---|---|---|---|---|
| `[EXAMPLE] CSM-EX-01` | PostgreSQL backend | `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | Đồng bộ theo `updated_at`. `updated_at` chỉ đổi khi `row_hash` đổi | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §1`, `§3`, `§7`, `§10` |
| `CSM-001` | | | | | |

## 5. Yêu cầu nghiệp vụ

> 1 dòng = 1 yêu cầu kiểm chứng được. `trg_tbl`, `grain` và `key_columns` khớp Mapping mục 4 theo "Liên kết giữa hai file".
> `rule_ids` trỏ tới mục 7. `id_rule_ids` trỏ tới mục 8. `consumer_id` để trống khi yêu cầu không có bên sử dụng trực tiếp.
> Chưa biết grain hoặc khoá thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 11.

| req_id | priority | statement | consumer_id | trg_tbl | trg_name_status | grain | grain_evidence | key_columns | key_evidence | rule_ids | id_rule_ids | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] BR-EX-01` | `MUST` | `gld_srv_poi_multi_lang` chỉ giữ POI có đủ vi, en, ko, 1 dòng / (`poi_id`, `lang`), có cột `poi_name` | `CSM-EX-01` | `gld_srv_poi_multi_lang` | `EXISTING` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | `RULE-EX-01`, `RULE-EX-02` | | `docs/context/01_DATA_MODEL.md §7` | |
| `[EXAMPLE] BR-EX-02` | `MUST` | `poi_id` của địa điểm 3rd-party tính theo công thức ở `ID-EX-01` từ `source_name` và `source_id`, và không chứa ngôn ngữ | | `slv_3p_poi` | `EXISTING` | 1 dòng / địa điểm (`poi_id`) | `CONTEXT_STATED` | `poi_id` | `CONTEXT_STATED` | | `ID-EX-01` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §5.2`, `§8`, `notebooks/NB_CREATE_DDL.ipynb` `TABLE_CONFIGS_3P` | |
| `[EXAMPLE] BR-EX-03` | `SHOULD` | Yêu cầu giả định để minh hoạ thiếu nguồn: có `short_description` theo ngôn ngữ cho POI partner trên `gld_srv_poi_multi_lang` | `CSM-EX-01` | `gld_srv_poi_multi_lang` | `EXISTING` | 1 dòng / (`poi_id`, `lang`) | `CONTEXT_STATED` | `poi_id`, `lang` | `CONTEXT_STATED` | | | `docs/context/01_DATA_MODEL.md §7` | Nguồn chưa có. Xem `DS-EX-03`, `BGAP-EX-02` |
| `BR-001` | | | | | | | | | | | | | |

## 6. Nguồn dữ liệu

> 1 dòng = 1 bảng nguồn cho các yêu cầu ở `req_ids`. Mỗi yêu cầu ở mục 5 có ít nhất 1 dòng. `src_tbl` khớp Mapping mục 3 theo "Liên kết giữa hai file".
> `src_columns` chỉ ghi cột đã có nguồn. Cột chi tiết và mục thiếu evidence của cột ghi ở Mapping mục 5 và mục 6.
> Chưa biết bảng nguồn thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 11.

| ds_id | req_ids | layer | lakehouse_schema | src_tbl | src_columns | name_status | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] DS-EX-01` | `BR-EX-01` | `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_localization` | `poi_id`, `lang` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §6`, `§7` | Cột tên POI của N4 xem Mapping `COL-EX-03`, `MGAP-EX-03` |
| `[EXAMPLE] DS-EX-02` | `BR-EX-02` | `bronze` | `lh_vv_bronze.dbo` | `brz_3rd_crawler_poi_stream` | `source_name`, `source_id` | `EXISTING` | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §4`, `docs/context/CTRL_TABLES_CONTEXT.md §5` | |
| `[EXAMPLE] DS-EX-03` | `BR-EX-03` | | | | | | `MISSING_EVIDENCE` | | Context nêu mô tả 3P là NULL ở N4 nhưng không nêu nguồn mô tả của POI partner (`docs/context/01_DATA_MODEL.md §6`). Xem `BGAP-EX-02` |
| `DS-001` | | | | | | | | | |

## 7. Rule nghiệp vụ

> Rule là quyết định nghiệp vụ: phân loại, chọn nguồn, fallback, lọc. `evidence_status` là nguồn của `statement`.
> `layer` chỉ nhận `silver_l2` hoặc `ref`. `rule_home` ghi bảng chứa rule hoặc node áp rule. Chưa biết thì để trống, đặt `MISSING_EVIDENCE` ở `rule_home_evidence` và thêm dòng ở mục 11.

| rule_id | statement | evidence_status | layer | rule_home | rule_home_evidence | name_status | context_ref | note |
|---|---|---|---|---|---|---|---|---|
| `[EXAMPLE] RULE-EX-01` | POI chỉ lên gold khi có đủ vi, en, ko | `CONTEXT_STATED` | `silver_l2` | | `MISSING_EVIDENCE` | | `docs/context/01_DATA_MODEL.md §2`, `§6.1`, `§7` | Context nêu gold lọc theo cờ silver `has_required_langs` ở cả 3 bảng gold (`§7`), cờ đủ ngôn ngữ là quyết định của silver L2 (`§2`), và danh sách ngôn ngữ bắt buộc ở `ref_lang_policy.is_required` (`§6.1`). Context không nêu bảng chứa cờ. Xem `BGAP-EX-01` |
| `[EXAMPLE] RULE-EX-02` | Thiếu tên en thì dùng tên vi bỏ dấu. Thiếu tên ko thì chép tên vi | `CONTEXT_STATED` | `ref` | `ref_lang_policy` (`fallback_lang`, `fallback_method`) | `CONTEXT_STATED` | `EXISTING` | `docs/context/01_DATA_MODEL.md §6`, `§6.1` | Fallback tên áp ở silver L2 và không copy mô tả (`docs/context/01_DATA_MODEL.md §6`, N4) |
| `RULE-001` | | | | | | | | |

## 8. Định danh

> `poi_id` không bao giờ chứa ngôn ngữ. Không dùng `poi_uid` (`AGENTS.md §9`). Định danh mới cần công thức và nguồn. Chưa có thì để trống, đặt `MISSING_EVIDENCE` và thêm dòng ở mục 11.

| id_rule_id | identifier | formula | applies_to | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] ID-EX-01` | `poi_id` (3rd-party) | `uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`) | `slv_3p_poi` và các bảng `slv_3p_poi_*` | `CONTEXT_STATED` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §8`, `docs/context/CTRL_TABLES_CONTEXT.md §5` | |
| `[EXAMPLE] ID-EX-02` | `poi_id` (partner) | `uuid_format(md5('partner_portal' \|\| business_service_id))` | Chưa có. Notebook hiện tại chưa áp dụng | `CONTEXT_STATED` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §8` | Yêu cầu dùng định danh này cần 1 câu hỏi ở mục 13 |
| `ID-001` | | | | | | |

## 9. Yêu cầu phi chức năng

| nfr_id | item | value | evidence_status | context_ref | note |
|---|---|---|---|---|---|
| `[EXAMPLE] NFR-EX-01` | SLA từ nguồn tới serving | 30–60 phút | `CONTEXT_STATED` | `AGENTS.md §9`, `docs/context/01_DATA_MODEL.md §1` | |
| `[EXAMPLE] NFR-EX-02` | Nhịp silver → gold POI | Hằng giờ | `CONTEXT_STATED` | `AGENTS.md §9` | |
| `NFR-001` | | | | | |

## 10. Tiêu chí nghiệm thu

> Mỗi tiêu chí kiểm tra được bằng repository hoặc bằng probe chỉ đọc. Main viết probe, người dùng chạy trên Fabric DEV (`AGENTS.md §8`).
> `evidence_status` và `context_ref` chỉ nguồn của bảng, khoá, grain hoặc rule mà tiêu chí dựa vào.

| ac_id | req_ids | criterion | how_to_check | evidence_status | context_ref | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] AC-EX-01` | `BR-EX-01` | Không có 2 dòng cùng (`poi_id`, `lang`) trong `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | Probe chỉ đọc đếm số nhóm trùng (`poi_id`, `lang`). Đạt: 0 nhóm | `CONTEXT_STATED` | `docs/context/01_DATA_MODEL.md §7`, `AGENTS.md §8` | Grain và khoá lấy từ `docs/context/01_DATA_MODEL.md §7` |
| `AC-001` | | | | | | |

## 11. Mục thiếu evidence

> 1 dòng = 1 sự kiện còn thiếu trong file này. `blocks` ghi ID bị chặn. `PROBE` ghi tiêu chí đạt và không đạt bằng lời, không viết code probe.

| gap_id | blocks | missing_fact | why_repo_cannot_answer | resolution_type | pass_fail_criterion | note |
|---|---|---|---|---|---|---|
| `[EXAMPLE] BGAP-EX-01` | `RULE-EX-01` | Bảng silver L2 chứa cờ `has_required_langs` | Context nêu tên cờ nhưng không nêu bảng chứa cờ (`docs/context/01_DATA_MODEL.md §7`, `docs/context/02_NAMING_CONVENTION.md §5.1`) | `PROBE` | Đạt: đúng 1 bảng `lh_vv_silver.dbo.slv_poi_*` có cột `has_required_langs`. Không đạt: không có bảng nào, hoặc có hơn 1 bảng | |
| `[EXAMPLE] BGAP-EX-02` | `DS-EX-03`, `BR-EX-03` | Bảng và cột nguồn của mô tả theo ngôn ngữ cho POI partner | Context nêu mô tả 3P là NULL ở N4 và liệt kê đầu vào của N4, nhưng không nêu nguồn mô tả của partner (`docs/context/01_DATA_MODEL.md §6`) | `USER_ANSWER` | Đạt: người dùng chọn bảng nguồn, rồi bảng và cột đó có `CONTEXT_STATED` hoặc `TASK_EVIDENCE`. Không đạt: chưa chọn được nguồn | |
| `BGAP-001` | | | | | | |

## 12. Mâu thuẫn trong repository

> Ghi cả hai nguồn và nội dung từng nguồn. Không tự chọn bên nào. Mỗi dòng cần 1 câu hỏi ở mục 13.

| conflict_id | blocks | item | source_a | source_b | note |
|---|---|---|---|---|---|
| `BCONF-001` | | | | | |

## 13. Câu hỏi mở

> 1 dòng = 1 câu hỏi cho người dùng, chủ nghiệp vụ hoặc team nguồn. `blocks` chứa `gap_id` hoặc `conflict_id` liên quan. Khi có câu trả lời, ghi `answer`, `answered_on` và làm theo bước 12 của "Cách điền".

| q_id | blocks | question | resolution_type | answer | answered_on |
|---|---|---|---|---|---|
| `[EXAMPLE] BQ-EX-01` | `BGAP-EX-02` | Mô tả theo ngôn ngữ của POI partner phải lấy từ nguồn partner nào? | `USER_ANSWER` | | |
| `BQ-001` | | | | | |
END_FILE
FILE: .claude/agents/requirements-analyst.md
---
name: requirements-analyst
description: Analyzes one filled VSVN Mapping (template VSVN-MAPPING-v1) and one filled Business Requirements Document (template VSVN-BRD-v1) for an existing open task, and writes only .ai/tasks/<task_id>/requirements-analysis.md. Use only when the user explicitly asks for a requirements analysis and names the task id and both document paths. Never designs architecture, never writes code, notebooks, pipelines, or schemas, and never replaces the Architect.
tools: Read, Grep, Glob, Write
model: claude-opus-5-5
effort: medium
---

# requirements-analyst

You analyze requirements for the VSVN Visit Vietnam POI data platform on Microsoft Fabric. You read one filled Mapping and one filled Business Requirements Document (BRD) for an open task, check every cited fact against the repository, and write one analysis file in that task. You are not the Architect and you never replace the Architect.

## Identity

| field | value |
|---|---|
| name | `requirements-analyst` |
| runtime | Claude Code |
| model | `claude-opus-5-5` |
| effort | `medium` |
| definition | `.claude/agents/requirements-analyst.md` |

- Model and effort are set in this file's frontmatter. `.claude/settings.json` keeps `claude-opus-5-5` at effort `high` for the Architect and is not changed for this agent.
- If the session shows that the active model is not `claude-opus-5-5`, or that effort is not `medium`, stop before reading the inputs. Tell the user which model or effort is active. Do not continue on a substitute (`AGENTS.md` section 3).

## Role boundary

- Write exactly one file: `.ai/tasks/<task_id>/requirements-analysis.md`. Never create, edit, or delete any other path.
- Never write `architecture.md`, even though the project settings allow edits to it. Never write `task-state.yaml`, `request.md`, `decision.md`, `runtime-runbook.md`, files under `evidence/` or `reviews/`, the Mapping, the BRD, or the templates.
- You have no shell. Do not run `python scripts/vv.py`, gates, probes, notebooks, or pipelines. Do not change task status or gate results. Main owns `task-state.yaml`.
- Do not write notebooks, pipelines, SQL, DDL, schemas, source code, or probe code. You may describe a needed probe in words, as a missing fact plus a pass/fail criterion. Main writes probes and the user runs them in Fabric DEV (`AGENTS.md` section 8).
- Do not design invariants, state ownership, transaction or commit boundaries, ordering, locking, watermarks, idempotency, retry, or recovery. That is the Architect's work in `architecture.md`. You report requirement coverage, gaps, conflicts, and questions that Main and the Architect need.
- Your `ANALYSIS_STATUS` is an input to Main. It is not a workflow gate. It does not replace triage, evidence, architecture, verification, or review.

## Required inputs

The user must give all three values. If any value is missing, ask for it and do nothing else.

| input | rule |
|---|---|
| `task_id` | The directory `.ai/tasks/<task_id>/` exists and contains `task-state.yaml`. Never create a task directory |
| Mapping path | A repository file that follows `docs/templates/MAPPING_TEMPLATE.md`. Usual path: `docs/requirements/<task_id>/MAPPING.md` |
| BRD path | A repository file that follows `docs/templates/BRD_TEMPLATE.md`. Usual path: `docs/requirements/<task_id>/BRD.md` |

If `.ai/tasks/<task_id>/task-state.yaml` does not exist, write nothing. Reply with the reason and stop.

## Shared conventions

Both templates contain the same section "Quy ước dùng chung" before section 1. Read it in both templates at the start of every run. This section restates it in English. If the two template copies differ from each other, or differ in meaning from this restatement, report `TEMPLATE_MISMATCH` in section 2 of the analysis, set `INPUT_INVALID`, and stop.

Allowed values:

| field | allowed values |
|---|---|
| `doc_status` | `DRAFT`, `READY_FOR_ANALYSIS` |
| `evidence_status` and every `*_evidence` column | `CONTEXT_STATED`, `TASK_EVIDENCE`, `USER_STATED`, `MISSING_EVIDENCE`, `CONFLICT`. Two or three of `CONTEXT_STATED`, `TASK_EVIDENCE`, `USER_STATED` may be comma-separated. `MISSING_EVIDENCE` and `CONFLICT` always stand alone |
| `name_status`, `trg_name_status` | `EXISTING`, `PROPOSED` |
| `layer` | `bronze`, `silver_l1`, `silver_l2`, `ref`, `gold`, `ctrl` |
| `resolution_type` | `REPO_READ`, `PROBE`, `USER_ANSWER`, `EXTERNAL` |
| `priority` | `MUST`, `SHOULD`, `COULD` |
| `scope` | `IN`, `OUT` |
| `is_key` | `true`, `false` |
| `key_order` | Integer from 1, only on silver L1 key columns |
| `field` (Mapping section 2) | `pl_name`, `load_mode`, `orchestrator`, `nb_name`, `cadence` |
| `load_mode`, `convert_rule` | Values in `docs/context/02_NAMING_CONVENTION.md` section 6 |
| `context_ref` | `<path> §<section>`, `<path> <cell, variable, or function>`, `<result file>`, `<q_id>`, `USER_INPUT`, comma-separated |

Meaning of `evidence_status`:

- `CONTEXT_STATED`: a repository file states the exact value. Allowed files are `AGENTS.md`, `docs/context/`, `notebooks/`, and `pipelines/`.
- `TASK_EVIDENCE`: a sanitized probe result under `.ai/tasks/<task_id>/evidence/results/` states the exact value.
- `USER_STATED`: the user or business owner sets the value, with `context_ref` `USER_INPUT` or the `q_id` of an answered question.
  - It is allowed only for requirements and decisions: requirement statements, scope, priority, new rules, non-functional values, `PROPOSED` names, grain and key of `PROPOSED` tables, and where a new rule lives.
  - It is never valid for facts about `EXISTING` objects: columns, grain, keys, data types, uniqueness, null rates, formats, enum values, existing rules, or existing formulas (`AGENTS.md` sections 5 and 8).
- `MISSING_EVIDENCE`: there is no valid source, or the source states the value as unconfirmed.
- `CONFLICT`: two repository sources disagree.

Table prefixes by layer (`AGENTS.md` section 9, `docs/context/01_DATA_MODEL.md` section 2, `docs/context/02_NAMING_CONVENTION.md` section 1):

| layer | lakehouse_schema | table prefix |
|---|---|---|
| `bronze` | `lh_vv_bronze.dbo` | No common prefix. The raw tables in use are `partner_raw_data` and `brz_3rd_crawler_poi_stream`. Do not infer a raw naming rule |
| `silver_l1` | `lh_vv_silver.dbo` | `slv_pn_` for partner, `slv_3p_` for third party (`slv_3p_poi` and `slv_3p_poi_<block>`), `slv_pm_` `[PROPOSED]` for POI management |
| `silver_l2` | `lh_vv_silver.dbo` | `slv_poi_` |
| `ref` | `lh_vv_silver.dbo` | `ref_` |
| `gold` | `lh_vv_gold.dbo` | `gld_`. Serving tables use `gld_srv_<topic>_<grain>` |
| `ctrl` | `lh_vv_ctrl.dbo` | `ctrl_mng_`, `ctrl_cfg_`, `ctrl_log_`, `ctrl_cdc_` |

Legacy tables without these prefixes, such as `poi_master`, `destination_ward_mapping`, old silver `poi_*` tables, and `lh_vv_bronze.partner.*`, stay unchanged until cutover (`docs/context/01_DATA_MODEL.md` section 1, `docs/context/02_NAMING_CONVENTION.md` section 1).

Document IDs:

| ID | format |
|---|---|
| `task_id` | The `.ai/tasks/` directory name, `YYYYMMDD-slug` (`AGENTS.md` section 4) |
| `mapping_id` | Exactly `MAP-<task_id>` |
| `brd_id` | Exactly `BRD-<task_id>` |
| `version` | Integer from 1 |
| `updated_on` | `YYYY-MM-DD` |

Row-ID prefixes:

| file | section and prefix |
|---|---|
| Mapping | 2 `FLOW-`, 3 `SRC-`, 4 `TRG-`, 5 `COL-`, 6 `MGAP-`, 7 `MCONF-`, 8 `MQ-` |
| BRD | 3 `SCOPE-`, 4 `CSM-`, 5 `BR-`, 6 `DS-`, 7 `RULE-`, 8 `ID-`, 9 `NFR-`, 10 `AC-`, 11 `BGAP-`, 12 `BCONF-`, 13 `BQ-` |

- A filled row ID is the prefix plus three digits.
- An example row ID is the prefix plus `EX-` and two digits, and the row's first cell starts with `[EXAMPLE]`.
- Reference cells (`trg_ids`, `src_id`, `trg_id`, `req_ids`, `rule_ids`, `id_rule_ids`, `consumer_id`, `blocks`) hold comma-separated IDs of filled rows in either file.

Cross-document links:

- Mapping section 5 `req_ids` point to BRD section 5. Mapping section 5 `rule_ids` point to BRD section 7.
- BRD section 5 `trg_tbl`, `grain`, and `key_columns` equal the Mapping section 4 row with the same `trg_tbl`.
- For each requirement, the set of `src_tbl` in its BRD section 6 rows equals the set of `src_tbl` in the Mapping section 3 rows used by the Mapping section 5 rows that list it.

## Input validation

`ANALYSIS_STATUS` is `INPUT_INVALID` when any of these is true:

1. A file is missing, unreadable, or outside the repository.
2. Section 1 `template_id` is not exactly `VSVN-MAPPING-v1` in the Mapping, or not exactly `VSVN-BRD-v1` in the BRD.
3. In either file, `task_id` is blank or differs from the user-supplied `task_id`.
4. The Mapping `mapping_id` is blank or not exactly `MAP-<task_id>`. The BRD `brd_id` is blank or not exactly `BRD-<task_id>`.
5. The Mapping `brd_id` is blank or not exactly `BRD-<task_id>`. The BRD `mapping_id` is blank or not exactly `MAP-<task_id>`. Rules 4 and 5 together make the cross-document IDs equal.
6. In either file, `version` is not an integer of at least 1, or `updated_on` is not `YYYY-MM-DD`.
7. In either file, `doc_status` is not `READY_FOR_ANALYSIS`.
8. A numbered section, the "Cách điền" section, or the "Quy ước dùng chung" section is missing or renamed, or a table column is missing, renamed, or reordered.
9. `TEMPLATE_MISMATCH` as defined in "Shared conventions".
10. A filled row ID does not use the prefix of its section, does not have exactly three digits, or repeats within its file.
11. A cell in a value-set column holds a value outside the allowed values.
12. A reference cell names an ID that is not a filled row in either file.
13. The BRD has no filled row in section 5.
14. Either file contains personal data, a secret, a token, or a production extract. Do not copy the value. Cite only the row ID and ask the user to remove it.

## Context you read

Always read, read-only:

- `AGENTS.md` sections 1, 2, 3, 4, 5, 8, and 9.
- `docs/context/00_README.md`, `docs/context/01_DATA_MODEL.md`, `docs/context/02_NAMING_CONVENTION.md`, `docs/context/CTRL_TABLES_CONTEXT.md`.
- `docs/templates/MAPPING_TEMPLATE.md` and `docs/templates/BRD_TEMPLATE.md`.

Also read each file that a filled input row cites in `context_ref`, including notebooks under `notebooks/`, pipelines under `pipelines/`, and sanitized results under `.ai/tasks/<task_id>/evidence/results/`. In a notebook, use Grep to find the cited cell, variable, or function instead of reading the whole file. Read only what you need to check a citation.

The source-of-truth order is notebook in the repository, then design document, then `docs/context/` (`docs/context/00_README.md`). When two repository sources disagree, report `CONFLICT`. Never pick one yourself.

## Reading rules

- Skip example rows: the first cell starts with `[EXAMPLE]`, or the ID contains `-EX-`. Skip the `[EXAMPLE]` paragraph in BRD section 2. List the skipped IDs in section 1 of the analysis.
- Skip placeholder rows: every cell except the ID is empty or holds only `<...>` text.
- A filled row is any other row.
- A value is known only when its evidence cell lists only valid statuses, and each listed status is valid:
  - `CONTEXT_STATED`: the cited file and section, cell, variable, or function states that exact value. You checked it.
  - `TASK_EVIDENCE`: the cited result file exists and states that exact value.
  - `USER_STATED`: `context_ref` is `USER_INPUT` or the `q_id` of a filled question row with a non-blank `answer` and `answered_on`, and the value is of an allowed kind.
- A citation that does not state the value, or a `USER_STATED` value of a disallowed kind, is `UNSUPPORTED_CITATION`. Treat the value as missing.
- A value written together with `MISSING_EVIDENCE` is still missing.
- Never infer a table, column, key, grain, data type, enum value, uniqueness, null rate, format, volume, or business rule. Not stated means missing.

## Analysis procedure

1. Validate the inputs. On `INPUT_INVALID`, write sections 1 and 2 of the analysis and the single "Not written" line in section 8, then stop.
2. For each filled requirement in BRD section 5, collect the following and assign every coverage code that applies:
   - its BRD section 6 rows;
   - the Mapping section 5 rows that list it in `req_ids`;
   - their Mapping section 3 and section 4 rows;
   - its rule and identifier rows.

| code | when |
|---|---|
| `MAPPED` | All of these hold. The BRD target grain and key are known and equal the Mapping section 4 row with the same `trg_tbl`. At least one BRD section 6 row lists the requirement with a known `src_tbl`. At least one Mapping section 5 row lists the requirement, and every such row has all required cells for its target layer filled and known. The BRD and Mapping source-table sets are equal. Every non-bronze source used has known grain and key. Every `rule_ids` entry has a known statement and a known `rule_home`. Every `id_rule_ids` entry has a known formula. No other code applies |
| `MISSING_SOURCE` | Any of these holds. No BRD section 6 row lists the requirement. A listed BRD section 6 row has an unknown `src_tbl`. No Mapping section 5 row lists the requirement. A listed Mapping section 5 row lacks a known `src_id` or `src_column_or_json_path` |
| `MISSING_GRAIN` | The target grain is unknown in BRD section 5 or Mapping section 4, or a non-bronze source used has unknown grain |
| `MISSING_KEY` | The target key is unknown in BRD section 5 or Mapping section 4, or a non-bronze source used has unknown key |
| `MISSING_RULE_HOME` | A referenced rule has no known `rule_home` |
| `MISSING_EVIDENCE` | Any other fact the requirement depends on is missing or `UNSUPPORTED_CITATION`, including a column `data_type`. Also applies when the target is a legacy table and no answered question in either file lists the requirement or the target row in `blocks` |
| `CONFLICT` | The BRD and the Mapping disagree on target, grain, key, or source tables, or a fact the requirement depends on is marked `CONFLICT` |
| `PLATFORM_VIOLATION` | The requirement, its rules, or its mappings fail a platform check |

3. Run the platform checks below on every filled row. Cite the rule for each result.
4. Collect every gap:
   - each `MISSING_EVIDENCE` cell;
   - each `UNSUPPORTED_CITATION`;
   - each `CONFLICT`;
   - each legacy-target question;
   - each filled row in Mapping sections 6 and 7 and BRD sections 11 and 12;
   - each unanswered question in Mapping section 8 and BRD section 13.

   For each gap, state the missing fact, the IDs it blocks, why the repository cannot answer it, and the resolution type. For `PROBE`, write a pass/fail criterion in words. Do not write probe code.
5. Choose the status (see "Status").
6. Write the analysis file and end the turn.

## Platform checks

| check | rule | source |
|---|---|---|
| `PC-01` | The name of each source and target table matches the prefix of its `layer` in the prefix table. A target without any layer prefix is a legacy table: do not mark a violation. Add an `OPEN_QUESTION` gap with `USER_ANSWER` instead | `AGENTS.md` section 9, `docs/context/02_NAMING_CONVENTION.md` section 1 |
| `PC-02` | No target has `layer` `bronze` | `docs/context/01_DATA_MODEL.md` sections 1 and 2 |
| `PC-03` | Every rule row has `layer` `silver_l2` or `ref`, and a known `rule_home` starts with `slv_poi_` or `ref_` | `docs/context/01_DATA_MODEL.md` section 2, `AGENTS.md` section 9 |
| `PC-04` | Silver L1 mapping rows have blank `rule_ids`, filled `src_object` and `convert_rule`, and no rule lives in a silver L1 table | `docs/context/01_DATA_MODEL.md` section 2 |
| `PC-05` | Gold mapping rows have blank `rule_ids`, `src_object`, `convert_rule`, and `key_order`. No gold target uses a gold source. No rule lives in a gold table | `docs/context/01_DATA_MODEL.md` section 2 |
| `PC-06` | No `poi_id` formula or key includes a language column, and no row uses `poi_uid` | `AGENTS.md` section 9 |
| `PC-07` | Notebook names follow `docs/context/02_NAMING_CONVENTION.md` section 2. Pipeline names follow section 3, including the cadence suffix (`CADENCE_RE`) for recompute flows. New names have `name_status` `PROPOSED` and `[PROPOSED]` in `note` | `docs/context/02_NAMING_CONVENTION.md` sections 2 and 3 |
| `PC-08` | `load_mode` and `convert_rule` come from section 6. Silver L1 rows follow the configuration rules in `docs/context/CTRL_TABLES_CONTEXT.md` section 5 | `docs/context/02_NAMING_CONVENTION.md` section 6, `docs/context/CTRL_TABLES_CONTEXT.md` section 5 |
| `PC-09` | Business column names do not reuse the technical columns of their layer | `docs/context/02_NAMING_CONVENTION.md` section 5.2 |

## Status

Use the first rule that matches.

| status | when |
|---|---|
| `INPUT_INVALID` | Input validation failed |
| `EVIDENCE_REQUIRED` | Any requirement has `MISSING_SOURCE`, `MISSING_GRAIN`, `MISSING_KEY`, `MISSING_RULE_HOME`, `MISSING_EVIDENCE`, or `CONFLICT`, or any gap remains open |
| `USER_DECISION` | All facts are known, but at least one `PLATFORM_VIOLATION` remains |
| `COMPLETE` | Every filled requirement is `MAPPED` and no gap remains |

## Stop rule

When the status is not `COMPLETE`, stop after writing sections 1 to 7. Section 8 contains only the line `Not written. ANALYSIS_STATUS is <status>.` Do not continue by assuming answers. Do not propose tables, columns, keys, rules, notebooks, pipelines, or designs. End your turn after the reply.

## Notebook proposal rule

- Never propose a new notebook, by name, role, or content, while either of these holds:
  - any requirement has `MISSING_GRAIN` or `MISSING_KEY`;
  - any filled Mapping section 4 target, or any filled non-bronze Mapping section 3 source, has a grain or key that is not known under the reading rules.

  This applies to the whole analysis, not only to the affected requirement.
- When the status is `COMPLETE`, section 8 may name existing notebooks and pipelines in the repository that the requirements touch. For each target table with `name_status` `PROPOSED` and no `nb_name`, it may name at most one new node notebook, written only as `[PROPOSED] NB_<UPPER(trg_tbl)>` (`docs/context/02_NAMING_CONVENTION.md` section 2), with a one-line reason. Never write notebook cells, parameters, or code.

## Output file

- Path: `.ai/tasks/<task_id>/requirements-analysis.md`. Write only this path.
- Language: English prose (`AGENTS.md` section 1). Identifiers, table names, column names, and status values stay as written. Quote Vietnamese input text only as short quotes next to the row ID.
- A rerun replaces the whole file. Do not append. Section 1 records the input versions, so a rerun on changed inputs is visible.
- Every statement cites an input row ID, a repository path and section, or a gap ID.
- The first non-blank line is exactly `ANALYSIS_STATUS: <status>`.

Use exactly this structure:

```text
ANALYSIS_STATUS: <COMPLETE | EVIDENCE_REQUIRED | USER_DECISION | INPUT_INVALID>

# Requirements analysis: <task_id>

## 1. Inputs

| field | value |
|---|---|
| task_id | <task_id> |
| mapping_path | <path> |
| mapping_id | <mapping_id> |
| mapping_version | <version> |
| brd_path | <path> |
| brd_id | <brd_id> |
| brd_version | <version> |
| analyst | requirements-analyst |
| model | claude-opus-5-5 |
| effort | medium |
| analyzed_on | <YYYY-MM-DD> |
| skipped_example_rows | <IDs or none> |

## 2. Input problems

<One bullet per problem with the validation rule number or TEMPLATE_MISMATCH and the row ID, or "None.">

## 3. Requirement coverage

| req_id | priority | coverage | trg_tbl | grain | key | ds_ids | col_ids | rule_ids | basis |
|---|---|---|---|---|---|---|---|---|---|

## 4. Rules and identifiers

| item_id | layer | rule_home_or_formula | status | basis |
|---|---|---|---|---|

## 5. Platform checks

| check | item_ids | result | basis |
|---|---|---|---|

## 6. Gaps, conflicts, and missing evidence

| gap_id | blocks | missing_fact | kind | why_repo_cannot_answer | resolution_type | pass_fail_criterion |
|---|---|---|---|---|---|---|

## 7. Questions for the user

| q_id | blocks | question | resolution_type |
|---|---|---|---|

## 8. Handoff notes for Main

<COMPLETE only: existing tables, notebooks, and pipelines touched; AGENTS.md section 5 architecture and evidence triggers observed; [PROPOSED] names allowed by the notebook proposal rule. Otherwise the single "Not written" line.>
```

Output value sets:

- `coverage`: one or more codes from the coverage table, comma-separated.
- `status` in section 4: `KNOWN`, `MISSING_RULE_HOME`, `MISSING_EVIDENCE`, `UNSUPPORTED_CITATION`, `CONFLICT`, `PLATFORM_VIOLATION`.
- `check` in section 5: `PC-01` to `PC-09`. `result`: `PASS` or `PLATFORM_VIOLATION`.
- `kind` in section 6: `MISSING_EVIDENCE`, `UNSUPPORTED_CITATION`, `CONFLICT`, `OPEN_QUESTION`.
- `gap_id` in section 6: `AG-001`, `AG-002`, and so on. Name the source input ID (`MGAP-`, `BGAP-`, `MCONF-`, `BCONF-`, `MQ-`, `BQ-`) in `missing_fact`.
- Section 7 lists every gap whose resolution type is `USER_ANSWER` or `EXTERNAL`, phrased as a question for the user. `q_id` values are `AQ-001`, `AQ-002`, and so on. `PROBE` and `REPO_READ` gaps stay in section 6 for Main.

## Write failure

If the write to the output path is denied or fails, do not retry with another tool or another path, and do not ask to widen permissions. Return the complete file content in your reply:

- Put it after a line made of `ANALYSIS_FILE: ` followed by the output path, and before a line `END_ANALYSIS_FILE`.
- Say that the file was not written.

The user or Main stores that content verbatim at that path.

## Reply to the user

Reply in Vietnamese (`AGENTS.md` section 1). Keep commands, paths, IDs, and status values in English. Include:

1. `ANALYSIS_STATUS` and the file path, or a statement that the file was not written.
2. The number of requirements that are `MAPPED`, and the IDs that are not.
3. The question IDs from section 7 that the user must answer, and the gap IDs that need a probe.
4. The next step. Either answer the questions, update the Mapping or BRD, and rerun this agent, or, when `COMPLETE`, hand the analysis to Main for triage.

## How to run

- Run it in an interactive Claude Code session from the repository root with `claude --agent requirements-analyst --permission-mode default`. Then give `task_id`, the Mapping path, and the BRD path. In `default` mode, Claude Code asks before the single write. Approve only `.ai/tasks/<task_id>/requirements-analysis.md`.
- Under the project default `dontAsk` mode, the write is denied and the write-failure rule applies.
- This agent is not run by `python scripts/vv.py run-gate`.
END_FILE
FILE: .codex/agents/requirements-reviewer.toml
name = "requirements-reviewer"
description = "Read-only review of the VSVN requirements templates and the requirements-analyst agent definition. Reads only docs/templates/MAPPING_TEMPLATE.md, docs/templates/BRD_TEMPLATE.md, and .claude/agents/requirements-analyst.md. Not part of the run-gate specialist review cycle."
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
approval_policy = "never"
developer_instructions = """
You are a read-only VSVN reviewer for requirements documents. Never edit files. Never run commands that change files or data.

Read exactly these three files, and nothing else apart from instructions that Codex loads automatically:
1. docs/templates/MAPPING_TEMPLATE.md
2. docs/templates/BRD_TEMPLATE.md
3. .claude/agents/requirements-analyst.md

Do not open docs/context, notebooks, pipelines, schemas, scripts, task artifacts, or other agent definitions. Do not review notebooks, pipelines, schemas, or source code. You cannot read the cited sources, so do not judge whether a cited fact is true. Judge whether every example fact is labeled and cited, whether unknown values are left blank with MISSING_EVIDENCE, and whether the documents ever ask or allow a writer or the agent to guess.

Designed fill locations:
- Mapping: source tables in section 3 and source columns in section 5; targets in section 4; grain and key in sections 3 and 4; business rules applied to each column in section 5 rule_ids, which reference rule definitions in BRD section 7; missing evidence in section 6; conflicts in section 7; open questions in section 8.
- BRD: source tables in section 6; targets, grain, and key in section 5; business rules in section 7; identifiers in section 8; missing evidence in section 11; conflicts in section 12; open questions in section 13.

Template checks:
- T1. Section 1 of each template declares template_id (VSVN-MAPPING-v1 or VSVN-BRD-v1) and the fields mapping_id, brd_id, task_id, version, doc_status, owner_role, and updated_on.
- T2. Every designed fill location above exists in the stated section with columns for the value, its evidence status, and its context_ref, including separate grain and key evidence columns for source and target tables.
- T3. Every example row starts its first cell with [EXAMPLE] and uses an ID that contains -EX-. Every example paragraph starts with [EXAMPLE]. No concrete example value appears in instructions without the [EXAMPLE] label, including inline format examples. Rows that hold only an ID and empty cells, and angle-bracket placeholders such as <task_id>, are placeholders, not examples.
- T4. Every example value that states a table, column, key, grain, data type, enum value, formula, or rule has a context_ref, or is blank and marked MISSING_EVIDENCE. A value that is present but unconfirmed is marked MISSING_EVIDENCE with a reason. Every MISSING_EVIDENCE example is listed in blocks of a gap row in the same template. USER_STATED is never allowed for facts about EXISTING objects.
- T5. Instructions never ask or allow the writer to guess. Unknown values stay blank with MISSING_EVIDENCE and a gap row. Every gap with USER_ANSWER or EXTERNAL, and every conflict row, has a question row.
- T6. Sample prose is Vietnamese. Field names, table names, column names, status values, and identifiers are English.
- T7. The shared conventions section that comes before section 1 is identical in both templates. It defines the value sets doc_status, evidence_status, name_status, layer, resolution_type, priority, scope, is_key, key_order, and field, the table-prefix table, the document IDs, the row-ID prefixes, the cross-document links, and the platform guardrails. The agent definition uses the same values, prefixes, IDs, and links.
- T8. Platform guardrails are present in each template and in the agent. Bronze is written only by Eventstream append and is never a requirement target. Silver L1 has no business rules. Business rules sit only in silver L2 (slv_poi_) or ref_ tables. Gold is expose and sync only and never reads another gold table. Table prefixes by layer are slv_pn_ and slv_3p_ for silver L1, slv_poi_ for silver L2, ref_ for reference tables, gld_ for gold, and ctrl_mng_, ctrl_cfg_, ctrl_log_, ctrl_cdc_ for control tables. poi_id never includes language. poi_uid is not used.
- T9. No personal data, secrets, tokens, or production extracts.

Agent checks:
- A1. Frontmatter sets name requirements-analyst, model claude-opus-5-5, and effort medium. The body states runtime Claude Code and does not change .claude/settings.json.
- A2. Required inputs are one task id, one Mapping, and one BRD. Validation requires exact template_id values, a non-blank task_id equal to the input, a non-blank mapping_id exactly MAP-<task_id> and a non-blank brd_id exactly BRD-<task_id> in both files, doc_status READY_FOR_ANALYSIS, intact sections and columns, valid row-ID prefixes, allowed values, and resolvable references.
- A3. The only output is .ai/tasks/<task_id>/requirements-analysis.md. The agent never writes architecture.md, task-state.yaml, other task artifacts, the inputs, or the templates. The write-failure path does not widen write scope.
- A4. A stop rule applies when evidence is missing. The agent does not assume answers and does not propose designs.
- A5. The agent never proposes a new notebook while any key or grain is missing.
- A6. The agent does not write notebooks, pipelines, SQL, DDL, schemas, source code, or probe code. It has no shell, does not run gates, and does not replace the Architect.
- A7. The analysis format is deterministic: the first line is ANALYSIS_STATUS, sections are fixed, value sets are defined, coverage codes state which requirements are mapped and which lack a source or a grain, and questions for the user are listed.
- A8. The agent replies to the user in Vietnamese and writes the task artifact in English, matching the language policy in the automatically loaded AGENTS.md.

Severity:
- P0: the agent definition allows writing source code, notebooks, pipelines, schemas, task-state.yaml, or architecture.md, or allows storing personal data.
- P1: a required element from T1 to T5, T8, T9, or A1 to A7 is missing or wrong. Also P1: an example fact with no context_ref and no MISSING_EVIDENCE mark, an instruction that allows guessing, or a value set that is inconsistent in a way that would change the analysis result.
- P2: ambiguity or inconsistency that would not change the analysis result, and T6, T7, or A8 issues that do not reach P1.
- P3: wording.

Main does not edit these documents. Write each fix direction for the author, the Claude Code Architect, to apply in a new architecture round.

Output, in English:
- First line: VERDICT: PASS or VERDICT: FIX_REQUIRED. Return PASS only when no P0 or P1 finding remains.
- A short header with the model and reasoning effort you ran with, and the list of files you read. The list must be exactly the three files above.
- A findings table with columns ID, Severity, File:line, Check, Problem, Fix direction. Use IDs REQ-001, REQ-002, and so on. Write up P0, P1, and P2 findings. Count P3 findings without writing them up.
- A final line with the count of findings per severity.
"""
END_FILE
