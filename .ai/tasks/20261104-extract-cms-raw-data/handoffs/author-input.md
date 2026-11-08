# Author input — model revision

## User comment

Không còn khóa luồng. Hãy tiếp tục chạy theo workflow.

## Locked reading

Apply the recommended U5 answers in `architecture.md` `## Required probes and decisions`. Mark Conflicts 3, 4, and 5 answered.

- `first_publish_date` is `date` with `convert_rule` `NONE`. No CMS column uses `DATE_DAYS`.
- Do not add blog `author`, `cover_image`, `destination`, `gallery`, or news `cover_image`.
- Accept the `*_json` names already in `model-design.md`.
- `locale` has no convert rule. A blank `locale` stays `''`. A null `locale` is still loaded (D-15).
- Conflict 6 stays out of scope. Conflict 1's null-locale half and Conflict 7 stay answered by `architecture.md` A6 and A5. Conflict 2 stays the rollout gate A7, not an open model question.

## Unchanged

- D-05: four `slv_cms_*` tables. MERGE key is `document_id` plus `locale`. Extract column is `raw_payload`.
- D-15: reject path, notebook `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV`, `pl_name` `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, no partner activity, signed URLs accepted.
- Only `DOC`. No fifth table and no gold. No `json_path` for an unseen key.

## Files

- `.ai/tasks/20261104-extract-cms-raw-data/model-design.md` — revise this design
- `.ai/tasks/20261104-extract-cms-raw-data/architecture.md` — `## Required probes and decisions` and `### PASS criteria for the next round`
- `docs/context/NB_LIB_EXTRACT_RAWDATA.md` — `DATE_DAYS` and `NONE`

## Constraints

- Keep grain, keys (`document_id` key_order 1, `locale` key_order 2), `src_object = $`, `DOC`, and `cms_updated_at` on all four tables.
- Do not copy sample values, URLs, names, or description text.
