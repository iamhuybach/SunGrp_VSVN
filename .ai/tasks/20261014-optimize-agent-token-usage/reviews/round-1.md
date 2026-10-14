## Model and reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium` — confirmed.
- Reviewer: `state-correctness-reviewer` — completed independently.
- Risk gate: not required; not run.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `STATE-001` — P1 — `scripts/vv.py:492`: An arbitrary non-empty `models.author.actual` value passes validation, allowing an unauthorized model substitution through later gates. Fix: require the value to match `claude-opus-5-5` or a valid Author override, with rejection and approved-override tests.
- `STATE-002` — P1 — `scripts/vv.py:1200`: `materialize --write` can modify implementation bytes after gates pass while retaining `ready_to_merge`, and a partial-write crash leaves falsely valid state. Fix: require `implementing` before the first durable write, or atomically invalidate affected gates and transition state before writing.

## Lower-severity findings

P2: 0; P3: 0.

Probe: not required; the reviewer reproduced `STATE-001` by validating `models.author.actual = unapproved-model`, which returned no errors.
