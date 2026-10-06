@AGENTS.md

## Claude Code trong VSVN
- Vai trò mặc định: **Architect** — đọc code, chỉ ghi `.ai/**`. `.claude/settings.json` đặt `defaultMode: dontAsk` + chỉ allow `Edit(/.ai/**)`, nên mọi sửa file ngoài `.ai/` bị từ chối tự động.
- Nhiệm vụ cụ thể của mỗi phiên nằm trong `.ai/task/<id>/handoff-claude-r<N>.md` do Main sinh ra. Đọc file đó trước tiên.
- Skill nên dùng: `visitvn-fabric-platform-architect` cho spec/ADR/LLD; `fabric-pyspark-notebook-reviewer` khi cần soi code hiện có.
- Khi `triage.md` ghi `writer: claude`: USER tự chuyển mode sang Edit automatically (acceptEdits) cho phiên đó; dùng skill `fabric-pyspark-notebook-writer`. Cursor không sửa code trong thời gian này.
- Không commit/push.
