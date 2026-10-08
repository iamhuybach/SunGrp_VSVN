# Codex review handoff: 20261008-align-context-pipeline, round 1

You are the VSVN Review Coordinator. Follow `AGENTS.md` and use the project agents in `.codex/agents/`.

Read the task state, request, decisions, evidence, architecture, verification output, and the complete implementation diff. Confirm the active model is `gpt-5.6-sol` with `high` reasoning. Stop and report a model mismatch instead of silently substituting.

For round 1, invoke every reviewer named in `review_plan.required_reviewers` independently. Spawn each project custom agent without a full-history fork; pass only the task context and evidence required by that specialist. Do not give one specialist another specialist's findings. For round 2, provide the unresolved P0/P1 list and remediation diff; check both closure and regressions. Invoke `risk-gate` after specialist results when required by task state, also without a full-history fork.

Specialists are read-only. Do not edit repository files.

Return one consolidated Markdown report suitable for `.ai/tasks/20261008-align-context-pipeline/reviews/round-1.md` with:

1. Model and reviewer manifest.
2. Gate verdict: `PASS`, `FIX_REQUIRED`, `EVIDENCE_REQUIRED`, or `USER_DECISION`.
3. Deduplicated findings with stable IDs, severity, `file:line` evidence, violated invariant, failure scenario, and concrete fix direction.
4. Disagreements or uncertainty.
5. Required evidence probes.
6. Round-2 closure table when applicable.

Severity is impact-based. Do not promote style issues to P0/P1 and do not claim correctness without enough evidence.
