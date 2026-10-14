You are the proposal author for VSVN task `20261014-3p-raw-payload-field-corrections`. This is not an Architect turn. Do not write `architecture.md`. Do not edit, create, or delete any file. Read only the files named below. Return one structured JSON object.

Set `model` to `claude-opus-5-5` and `effort` to `medium`. Do not infer effort from a numeric reasoning budget. Do not return an empty `decision_md` because a budget number looks low. Complete the document.

## Read

- `.ai/tasks/20261013-3p-extract-from-raw-payload/decision.md`
- `.ai/tasks/20261013-3p-extract-from-raw-payload/task-state.yaml` (`user_decisions_2026_10_13` only, for the landed column actions)

The later sections of that `decision.md` override the earlier column tables. The landed action is the last decision for that column, including the dropped-column list. Do not treat the first draft table as the current action when a later section changed it.

## User comments, 2026-10-14

These comments win over the same column in the old decision.

- `slv_3p_poi_contact.phone` reads `nationalPhoneNumber`. It is not in the table now.
- `slv_3p_poi_media.blob_url` is kept. The value stays null. The user will name the source field later. Do not deactivate the column.
- `slv_3p_poi_media.photographer` reads `authorAttribution.displayName`.
- Add `slv_3p_poi_review.is_visible` as a BOOLEAN soft delete for a review, plus a matching hash column only if one is required for that soft delete. The extract must not physically delete a review row. The user has not named a source field and has not named the condition that sets `false`. Do not invent that condition. Ask one clear question.

## decision_md

Write `decision_md` in Vietnamese. Keep commands, identifiers, paths, status tokens, and column names in English.

Start with this text, unchanged, including the heading:

## Ngoại lệ model

Người dùng duyệt ngày 2026-10-14. Người viết đề xuất này là Claude Code, model `claude-opus-5-5`, effort `medium`. Đây không phải lượt Architect. Architect vẫn là `claude-opus-5-5` effort `high` và chỉ viết `architecture.md` qua `run-gate`. `models.architect.effort` giữ `high` vì validator từ chối giá trị khác.

Then:

- Name task `20261013-3p-extract-from-raw-payload` and state that every proposal line not named in these comments stays as last decided.
- Record only the changed rows. For each row give the table, the column, the old action, and the new action.
- Include the matching `ctrl_cfg_schema_registry` rows for those columns only.
- Do not invent a `json_path` when the user has not named a field. `blob_url` has no `json_path`. `is_visible` has no `json_path`.
- For `is_visible`, state that the extract does not physically delete review rows, and ask one clear question about the missing source field and the missing condition for `false`. If a hash column is not required, say so and do not add one. If you cannot tell whether a hash column is required, ask; do not add the column.
- Do not copy sample values, review text, person names, or URLs.
- Do not add commentary that is not part of the proposal. Do not wrap the Markdown in fences inside the JSON string.

Return only the structured JSON object. Do not edit the workspace.
