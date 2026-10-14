# Request

## User outcome

Update the 3rd-party extract for four column comments from 2026-10-14. The source is now the corrected `normalized_payload`, which has the raw shape plus `photos[].blob_url`.

## Scope

### In scope

- `.ai/tasks/20261014-3p-raw-payload-field-corrections/decision.md`
- The columns named by the user: `slv_3p_poi_contact.phone`, `slv_3p_poi_media.blob_url`, `slv_3p_poi_media.photographer`, and `slv_3p_poi_review.is_visible`
- The matching `ctrl_cfg_schema_registry` rows, described in the proposal only

### Out of scope

- Every other `slv_3p_*` table and column
- Partner extract
- `gld_enr_*`
- Changing `20261013-3p-extract-from-raw-payload` status (`ready_to_merge` has no outbound transition)

## Acceptance criteria

- `slv_3p_poi_contact.phone` is present and reads `nationalPhoneNumber`.
- `blob_url` stays, `is_active = true`, and reads `photos[].blob_url`.
- `photographer` uses a user-approved path after P7 showed that the originally named singular path is absent in DEV.
- `slv_3p_poi_review.is_visible` is a new BOOLEAN soft-delete column. The extract does not physically delete review rows. The source field and the condition for `false` are not chosen in this proposal.

## Constraints

- Comments from 2026-10-14 override the same column rows in `20261013-3p-extract-from-raw-payload`.
- Do not invent a `photographer` selection rule or path before the user resolves P7.
- Do not copy sample values, review text, person names, or URLs into the repository.
- Proposal author is Claude Code CLI, `claude-opus-5-5`, effort `medium`. This is not an Architect turn.
- During the proposal-only turn, do not call `python scripts/vv.py run-gate`, Codex, Architect, or `requirements-analyst`. The user later approved architecture; round 2 passed. Implementation follows the passed architecture and then uses the required reviewers.
- Do not change `.claude/settings.json`.
- Do not commit, push, or merge.

## Classification rationale

- Complexity: `high`. Four column corrections, plus stateful `is_visible` on the latest `reviews[]` for each `poi_id`.
- Risk: `high`. A review that leaves the latest `reviews[]` stays in the table with `is_visible = false`. DEV showed that array is a five-review window.
- Architecture: required later, because `is_visible` changes review visibility state and the live silver tables already exist. Not called this turn. Gate stays `pending`.
- Evidence: not required to record the proposal. `nationalPhoneNumber` and the photographer path were named by the user. `blob_url` and `is_visible` have no source field by instruction.
- Runtime proof: required before a later implementation can merge, because the columns land in Fabric silver. Not run this turn. Gate stays `pending`.
- Reviewer routing: none this turn. Review stays closed until implementation after the open question is answered.
