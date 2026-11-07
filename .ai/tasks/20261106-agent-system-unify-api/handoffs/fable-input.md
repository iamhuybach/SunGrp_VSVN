# Fable input: 20261106-agent-system-unify-api

Session: Fable 5.1 (`claude-fable-5-1`), effort high, Claude Code extension, under EX-01 (writes `proposal.md`, Vietnamese) and EX-02 (writes `architecture.md`, English, `RESULT:` line then `## Main brief` per `docs/agent-system/WORKFLOW.md` §Task artifacts). Write only those two files. No `run-author`/`run-gate`: the runner hard-codes `claude-opus-5-5`.

## Verbatim user request

> Thay đổi agent-system: gom code API từ D:\git\SunGrp_VSVN_API (Java 26, Spring Boot 4.1, JPA, Flyway, PostgreSQL, Testcontainers) vào repo SunGrp_VSVN hiện tại; thiết kế lại model, agent, sub-agent, skill, rule, context, hook, MCP, plugin cho Cursor, Claude Code, Codex để phục vụ cả việc cũ (Fabric notebook, pipeline, DDL, ctrl) và việc API. D:\git\SunGrp_VSVN_API chỉ là nguồn đọc; không tạo repo thứ hai, không sửa thư mục đó.

## Evidence (read first)

- `.ai/tasks/20261106-agent-system-unify-api/evidence/agent-system-inventory.md` — components, models, triggers, budgets, hard-coded model lines.
- `.ai/tasks/20261106-agent-system-unify-api/evidence/api-source-inventory.md` — 62 API files, build/test commands, tables, gold join points, measured drift.
- `.ai/tasks/20261106-agent-system-unify-api/evidence/user-action-inventory.md` — template use, repeated commands, stops, failures, rounds, manual steps.
- Probes: `evidence/probes/user_actions_scan.py`, `evidence/probes/api_schema_diff.py`.

## May read (by section)

`AGENTS.md`, `CLAUDE.md`, `docs/agent-system/WORKFLOW.md`, `.cursor/rules/*`, `.cursor/skills/*/SKILL.md`, `.claude/settings.json`, `.claude/agents/*`, `.codex/config.toml`, `.codex/agents/*.toml`, `scripts/vv.py` and `scripts/agent_runner.py` (via `vv.py toc/show`), `docs/AGENT_PROMPT_SAMPLES.md`, `sql/postgres/gld_srv_serve.pg.sql`, `docs/context/mapping_*.md`. API source `D:\git\SunGrp_VSVN_API` read-only; never open `.env.example`; do not quote the DEV host in `docs/poi-serving-api/scripts/check-gaps.py`.

## Constraints

- One repository. No writes to `D:\git\SunGrp_VSVN_API`. No secrets in the repo.
- `AGENTS.md` < 8 KB (5 B headroom today); `doctor` must stay without WARN.
- Model changes need the agent evaluation suite or a user-approved exception (`AGENTS.md` §3).
- Child-task Main is `claude-opus-5-5` medium under EX-03.
- Mark each item that needs a user decision.

## Questions

a. Bố cục một repo: thư mục đích cho code API và docs/poi-serving-api; AGENTS.md lồng hay CLAUDE.md theo thư mục; vv.py context/verify/doctor cần đổi gì để nhận task API.
b. Hợp đồng gold → serving: nơi chứa nguồn sự thật cho cột và khoá giữa gld_srv_poi_*, mapping_*.md, Flyway và entity; check tự động phát hiện lệch.
c. Phân vai theo thế mạnh: Cursor (rule theo glob, skill, subagent, hook, MCP, plugin), Claude Code (subagent, skill, hook, .mcp.json, plugin), Codex (AGENTS.md lồng, profile config.toml, agent toml, sandbox). Mỗi thành phần hiện có: giữ | gộp | tách | thêm | bỏ, kèm lý do và chi phí token.
d. Model cho từng lane: cũ và API, Main viết Java, Author, Architect, reviewer. Đánh dấu thay đổi nào cần agent evaluation suite hoặc exception (AGENTS.md §3). Có cho runner đọc model từ exception thay vì gán cứng không.
e. Thành phần mới cho API: rule glob (src/**/*.java, db/migration/*.sql); skill (endpoint Spring, migration Flyway/JPA, contract và integration test); reviewer Codex (api-contract, security, jpa-performance); verify lane (mvn test, Testcontainers cần Docker); gate runtime local/docker thay cho Fabric DEV.
f. Hook và skill rút từ user-action-inventory: mỗi hành vi lặp lại có tần suất, đề xuất tự động hoá (hook nào, runtime nào, sự kiện nào), lợi ích ước lượng, rủi ro.
g. MCP và plugin: liệt kê ứng viên cho từng công cụ, mục đích, quyền (read-only), cách cấp credential không ghi secret vào repo, lý do chọn hoặc loại.
h. Lộ trình: chia task con, mỗi task một phase, có thứ tự, rollback và tiêu chí nghiệm thu; ngân sách AGENTS.md < 8 KB, doctor không WARN; danh sách quyết định user phải chốt.

## Facts the answers must account for

- `30-sql.mdc` globs `**/*.sql`; `verify` lints any non-`.pg.sql` file as sparksql, so a moved Flyway `V*__*.sql` would hit both.
- `exceptions` are validated but no runner reads them.
- Drift today: `srv_poi_media_gallery` PK and `srv_poi_review.source_name`; no repo component loads gold into `apps.srv_poi_*`; runtime `flyway.enabled: false`.
- Agents ran `git commit`/`git push` (102/122 Shell segments) despite `AGENTS.md` §8; 654 of 708 user turns used no template.
