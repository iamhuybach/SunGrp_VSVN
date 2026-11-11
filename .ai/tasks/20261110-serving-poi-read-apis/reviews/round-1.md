## Model and reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium` — confirmed.
- Reviewers: `api-contract-reviewer`, `jpa-performance-reviewer`, `app-security-reviewer` — completed independently.
- Risk gate: not required and not run.

## Gate verdict

`USER_DECISION`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| API-002 | P1 | `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java:193` | `holiday_exceptions` is always returned as `null` because decision D-7 remains open, leaving the practical-info contract incomplete. | Choose D-7 option A or B, then implement and document the selected mapping. |

## Lower-severity findings

P2: 4; P3: 5.

Probe: not required; the blocker is an explicit user decision, not missing runtime evidence.
