# Codex review handoff: 20261019-poi-entity-non-enrich, round 2

You are the VSVN Review Coordinator. Use the project agents in `.codex/agents/`.

Confirm the active model is `gpt-5.6-sol` with `medium` reasoning. Stop and report a model mismatch instead of silently substituting.

Read `architecture.md` when it exists, the open items in `decision.md`, and the implementation diff. Do not read the rest of the repository, past reviews, or evidence files unless one finding depends on a named path.

For round 1, invoke every reviewer named in `review_plan.required_reviewers` independently. Spawn each project custom agent without a full-history fork and without another specialist's findings. For round 2, use the generated round-1 carry-over at the end of this prompt: pass each specialist only the round-1 P0/P1 findings it owns, their dispositions, and the diff of the files listed as changed since round 1 (`git diff -- <path>`, or the file itself when untracked). Invoke `risk-gate` after the specialist results when task state requires it. Risk-gate reads those findings and the diff, not the whole repository.

Specialists are read-only. Do not edit repository files.

Return one short consolidated Markdown report:

1. Model and reviewer manifest.
2. Gate verdict: `PASS`, `FIX_REQUIRED`, `EVIDENCE_REQUIRED`, or `USER_DECISION`.
3. Deduplicated P0/P1 findings: ID, severity, `file:line`, one-sentence failure, one-sentence fix.
4. P2/P3 as a count.
5. One probe line when evidence is missing.

Do not promote style issues to P0/P1. Do not write a repository tour.

## Round 1 carry-over

`vv.py` generated this block. Use it instead of opening past review files. Re-check each round-1 P0/P1 against its disposition, then review only the changed files below for regressions caused by the fixes.

### Round 1 P0/P1 findings

- `GATE-001` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:852,861`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:785,794`: Releasing the flow lock between the entity and amenity switches lets `NB_00` observe mixed edge generations and advance partial state. Fix: hold one durable cutover lease across both switches or commit both edge sets atomically.
- `GATE-002` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:770,824`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:706,757`: The edge MERGE commits before conflicting/stale-state validation, so a failed post-check leaves partially switched durable control state. Fix: perform complete ownership and stale-state validation under the lock before MERGE.
- `GATE-003` — P1 — `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb:134`: Deeply nested `amentities` can raise `RecursionError`, causing deterministic Spark retries and node failure. Fix: use iterative document-order traversal and classify parser/depth failures as `JSON_INVALID`.
- `GATE-004` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:782`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:715`: MERGE keys omit `src_schema` and `trg_schema`, allowing same-named foreign-schema edges to be rewritten or retired. Fix: include both schemas in the MERGE source, match key, and all related validation predicates.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | A9. Một MERGE commit cạnh entity và amenity. | |
| GATE-002 | P1 | fixed | A10. Kiểm tra dưới flow lock, trước MERGE. | |
| GATE-003 | P1 | fixed | A11. Duyệt lặp, sâu tối đa 64, lỗi parse thành `JSON_INVALID`. | |
| GATE-004 | P1 | fixed | A12. Khoá MERGE và predicate gồm `src_schema`, `trg_schema`. | |

### Files changed since round 1

- notebooks/NB_CREATE_DDL.ipynb | modified
- notebooks/NB_SETUP_INITIAL_DDL.ipynb | modified
- notebooks/NB_SETUP_POI_AMENITY.ipynb | modified
- notebooks/NB_SETUP_POI_ENTITY.ipynb | modified
- notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb | modified
- tests/test_poi_amenity_contract.py | modified
- tests/test_poi_entity_contract.py | modified
