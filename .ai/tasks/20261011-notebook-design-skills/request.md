# Request

## User outcome

Cursor skills exist for repeated Microsoft Fabric notebook-design rules. Claude Code authors every skill. Codex reviews that content. Main coordinates the task, records state, runs verification, and stores each skill file as the exact text Claude returned.

## Scope

### In scope

- Notebook roles in `docs/context/02_NAMING_CONVENTION.md`: `NB_LIB_*`, `NB_EXTRACT_*_CDC_BRZ_TO_SLV`, `NB_00_ORCHES_*`, `NB_<UPPER(trg_tbl)>`, `NB_SETUP_*`, and `NB_CREATE_DDL`.
- Comparison against `notebooks/` and `docs/context/`.
- Skill files at `.cursor/skills/<name>/SKILL.md`, authored by Claude Code and copied verbatim by Main after an architecture verdict of `PASS`.

Notebooks present in the repository at task creation:

- `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`
- `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`
- `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`
- `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`
- `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb`
- `notebooks/NB_SETUP_L1_TS_AUDIT.ipynb`
- `notebooks/NB_CREATE_DDL.ipynb`

No `NB_<UPPER(trg_tbl)>` notebook is present. Do not invent a skill for a role that has no repeated implementation.

### Out of scope

- Pipeline skills, partner business-rule skills, and gold-sync skills unless the same rule already repeats in at least two notebooks or two extract sources.
- Fabric DEV probes. Notebook survey uses the repository only.
- Work owned by the Architect role or by Codex reviewers `spark-runtime-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`, and `risk-gate`.
- Duplicating `.cursor/skills/vsvn-task-workflow/SKILL.md` or `.cursor/skills/fabric-runtime-evidence/SKILL.md`.
- Restating `.cursor/rules/10-fabric-notebook.mdc` or `.cursor/rules/30-sql.mdc` as a second copy of the same rule.
- Changes to `scripts/agent_runner.py`.
- Commit, push, or merge.

## Acceptance criteria

- `architecture.md` lists each selected skill, why it exists, the notebook files that evidence the repeated rule, and the work the skill does not do.
- Each selected skill has one `SKILL.md` whose bytes match the block Claude wrote.
- `git diff` of the skill files matches those blocks.
- A skill Claude does not place in `architecture.md` is not created.
- `python scripts/vv.py verify <task-id>` passes.
- Review runs through `python scripts/vv.py run-gate <task-id>` at `reviewing`.
- Reviewers are only those whose domain the skill content touches. `risk-gate` always runs because a wrong skill would be reused by Main across many notebooks.

## Constraints

- Skills are for Main, Grok 4.7 Medium.
- A skill exists only for a repeated rule that already appears in at least two notebooks or two extract sources. A rule that belongs to one notebook is out.
- English is mandatory for skill files and for `architecture.md`.
- The user-approved exception dated 2026-10-11 is recorded in `task-state.yaml` and `decision.md` before the architecture gate. Claude Code authors every `.cursor/skills/<name>/SKILL.md`. Main does not draft, reword, shorten, or add skill prose. Codex stays read-only.
- `python scripts/vv.py run-gate` at `waiting_architecture` remains a read-only Claude turn. The runner rejects every file edit and persists only `architecture.md`.
- If Claude or Codex falls back to another model, stop and report it. Do not substitute a model.

## Architecture delivery contract

The architecture document selects which skills are written. It contains the full text of each `SKILL.md` in its own block. Each block starts with a line of this exact form:

```text
SKILL_FILE: .cursor/skills/<name>/SKILL.md
```

The skill body is every following line until, but not including, a line that is exactly `END_SKILL_FILE`. `END_SKILL_FILE` is a delimiter and is not part of the skill file. Main copies the body character for character, including blank lines and trailing spaces, and does not add or remove a final newline beyond the characters inside the block.

After verdict `PASS`, Main creates only those paths and writes only those bodies. On a later architecture round caused by a P0 or P1 skill-content finding, Main replaces skill files with the new verbatim bodies and does not edit them itself.

## Classification rationale

- Complexity: `high`. Choosing skill boundaries across notebook roles is a design trade-off and needs deep reasoning over repeated implementations. This is a user-requested agent-system change, so fast lane does not apply.
- Risk: `high`. A wrong skill is reused by Main on later notebooks. That is why `risk-gate` is required. The task itself does not write Lakehouse data.
- Architecture: required. The skill set, the repeated-rule evidence, and the full skill text are architecture decisions.
- Evidence: not required. Correctness is established from notebooks and context already in the repository. No Fabric DEV probe.
- Runtime proof: not required. No pipeline, notebook, or table behavior changes in this task.
- Reviewer routing: `spark-runtime-reviewer`, `sql-data-reviewer`, and `state-correctness-reviewer`, because notebook-design skills for Spark notebooks, Spark SQL or Delta DDL, and CDC or watermark behavior enter those domains. `fabric-pipeline-reviewer` is added before review only if a selected skill states pipeline activity contracts or notebook exit contracts. `risk-gate` runs because `risk_level` is `high`.
