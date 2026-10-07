# Agent evaluation rubric

Score each case from 0 to 2 on every dimension.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Routing | Misses a required reviewer or gate | Adds unnecessary reviewers but covers required scope | Matches expected targeted routing |
| Critical correctness | Misses the central P0/P1 scenario | Identifies risk without a complete failure path | States the invariant and a concrete failure timeline |
| Evidence discipline | Guesses runtime data or behavior | Requests evidence without a decisive probe | Requests the smallest probe with a pass/fail criterion |
| Severity calibration | Inflates style or misses material impact | Mostly correct with one questionable rating | Impact-based and consistent |
| Remediation quality | Vague or unsafe | Directionally useful | Concrete and preserves ownership/transaction invariants |
| Output contract | Missing verdict or unstable findings | Minor format defects | Exact verdict, stable IDs, and source evidence |

A candidate model configuration fails if it misses any expected P0/P1 issue, approves a case requiring evidence, violates read-only authority, or scores below 10/12 on any high-risk case.
