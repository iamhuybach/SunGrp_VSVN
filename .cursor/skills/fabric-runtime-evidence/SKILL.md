---
name: fabric-runtime-evidence
description: Design or interpret VSVN Fabric DEV probes and runtime evidence when correctness depends on schemas, data shape, ordering, uniqueness, nulls, distribution, performance, or actual control-table behavior. Do not use when repository inspection and deterministic local tests are sufficient.
---

# Fabric runtime evidence

1. State the decision the evidence must resolve and the pass/fail criterion.
2. Create the smallest read-only probe under `.ai/tasks/<task-id>/evidence/probes/`.
3. Include the target environment, prerequisites, expected schema, limits, and instructions for saving results.
4. Aggregate where possible. Limit samples to 50 rows and exclude personal data, secrets, and production extracts.
5. The user runs probes in Fabric DEV and stores sanitized output under `evidence/results/`.
6. Interpret only observed results. Record residual assumptions in `decision.md`.

Never convert missing runtime evidence into a guessed invariant.
