# Đề xuất: gom API vào `SunGrp_VSVN` và thiết kế lại agent-system cho Fabric và API

Task: `20261106-agent-system-unify-api`. Viết bởi phiên ngoại lệ EX-01 (`claude-fable-5-1`, effort high, Claude Code extension), không qua `run-author`. Ngày: 2026-11-06.

## Phạm vi

- Trả lời câu a–h trong `handoffs/fable-input.md`. Mỗi đề xuất có mã `P-<câu><số>` để bảng quyết định cuối file tham chiếu.
- Mọi dòng cấu hình, rule, skill, script không được nêu trong file này giữ nguyên như đã quyết định.
- File này không thiết kế invariant, ownership, commit boundary hay recovery; phần đó thuộc `architecture.md` (EX-02).
- Dữ kiện không có trong repo, trong 3 inventory, hoặc trong nguồn đọc `D:\git\SunGrp_VSVN_API` được ghi `MISSING_EVIDENCE`. Khả năng của công cụ (Cursor, Claude Code, Codex) mà repo không chứng minh được ghi `[VERIFY]` và trở thành tiêu chí nghiệm thu của task con.

## Căn cứ

`problem-analysis.md`: Không áp dụng. Căn cứ là:

- `evidence/agent-system-inventory.md` (§1–§6), `evidence/api-source-inventory.md` (§1–§4), `evidence/user-action-inventory.md` (§1–§6).
- `AGENTS.md`, `CLAUDE.md`, `docs/agent-system/WORKFLOW.md`, `.cursor/rules/*.mdc`, frontmatter `.cursor/skills/*/SKILL.md`, `.claude/settings.json`, `.claude/agents/requirements-analyst.md` (frontmatter), `.codex/config.toml`, `.codex/agents/*.toml`, `scripts/vv.py`, `scripts/agent_runner.py`, `.ai/prompts/author-proposal.md`, `.ai/tasks/_template/task-state.yaml`, `.ai/evals/cases.yaml`, `.ai/evals/rubric.md`, `tests/test_vv.py` (các dòng pin model), `sql/postgres/gld_srv_serve.pg.sql`, `docs/context/00_README.md`, `docs/context/mapping_gld_srv_poi_review.md`, `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`, `notebooks/NB_GLD_SRV_POI_{MEDIA_GALLERY,REVIEW}.ipynb` (NodeSpec `pk`).
- Nguồn đọc `D:\git\SunGrp_VSVN_API`: `pom.xml`, `Dockerfile`, `docker-compose.yml` (che giá trị credential), `.gitignore`, `.dockerignore`, `src/main/resources/application.yml`, `src/test/resources/application.yml`, `db/migration/V1__init_srv_poi_tables.sql`, entity `SrvPoiMediaGallery.java`, `SrvPoiReview.java`, `docs/poi-serving-api/DESIGN-AND-PLAN.md` §C.1, §C.4, §G, `HANDOFF.md` §6, §7, §10, §11, `API-GAPS.md` §5, §7, cấu trúc `scripts/check-gaps.py` (không trích host). Không mở `.env.example`.
- Kiểm tra cục bộ ngày 2026-11-06: `java -version` trả về OpenJDK 21; `mvn` không có trên PATH (API dùng wrapper `mvnw`); Docker 29.7 có sẵn; remote repo này là GitHub, remote API là Azure DevOps project `Sun-Visit-VN`, repo `data-serving-service`, HEAD `20bca8a`, 3 commit, working tree sạch.

## Tóm tắt khuyến nghị

1. Một repo, API nằm ở `services/data-serving-service/` (trùng `artifactId` và tên repo ADO), docs giữ `docs/poi-serving-api/`. Chép thường từ commit `20bca8a`, ghi nguồn vào `decision.md`; không `git subtree`.
2. Một nguồn sự thật cho hợp đồng serving: DDL gold trong `NB_SETUP_INITIAL_DDL` cell `init_tables` cộng NodeSpec `pk`. `sql/postgres/gld_srv_serve.pg.sql`, Flyway và entity đều là bản dẫn xuất và được pytest so khớp tự động.
3. Instruction lồng theo thư mục: `services/data-serving-service/AGENTS.md` (≤ 4 KB) là nguồn duy nhất cho quy tắc API; Codex đọc trực tiếp, Claude Code qua `CLAUDE.md` lồng chứa `@AGENTS.md`, Cursor qua rule glob `40-java-api.mdc` tham chiếu file đó. Root `AGENTS.md` giảm ~940 B bằng cách bỏ nội dung trùng với rule 10 và 20.
4. Runner đọc `exceptions` đã duyệt để chọn model thay vì gán cứng; `doctor` và mặc định không đổi.
5. Main cho lane API là `claude-opus-5-5` medium theo phê duyệt thường trực ghi vào `AGENTS.md` §3, thay vì EX từng task.
6. Thêm 3 reviewer Codex cho API, 1 skill Cursor `vsvn-api-service`, lane `maven` trong `verify`, gate runtime local bằng `docker compose` do user chạy.
7. Hook Cursor chặn `git push`, reset, rebase, xóa đệ quy; tự `validate` sau khi sửa `task-state.yaml`. Chính sách commit ở §8 cần user chốt vì dữ liệu cho thấy user chủ động yêu cầu commit 105 lần.
8. MCP: chỉ một MCP PostgreSQL chỉ đọc cho Cursor Main, trỏ PostgreSQL local của compose, credential qua biến môi trường. Không MCP cho Claude Code và Codex. Không plugin.
9. Lộ trình 8 task con agent-system theo thứ tự, cộng 1 task dữ liệu ngoài agent-system (loader gold → PostgreSQL, hiện chưa tồn tại).

## a. Bố cục một repo

### P-a1. Thư mục đích cho code API

- **Hiện trạng**: API là repo riêng, 62 file, gốc package `src/main/java/vn/visitvietnam/dataserving/` (`api-source-inventory.md` §1). `pom.xml:12` `artifactId` là `data-serving-service`; `docker-compose.yml:21,26` dùng tên `data-serving-service`; tài liệu gọi là `data-serving-api` (`DESIGN-AND-PLAN.md` §C.1, `API-GAPS.md` §5). Repo này có các thư mục cấp 1: `docs/ local/ notebooks/ notebooks_lgc/ pipelines/ scripts/ sql/ tests/`.
- **Thay đổi**: tạo `services/data-serving-service/` chứa nguyên cây Maven: `pom.xml`, `mvnw`, `mvnw.cmd`, `.mvn/`, `src/`, `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.gitignore` riêng (xem P-a4). Không đặt `src/` ở gốc repo.
- **Lý do**: tên trùng `artifactId` và tên repo ADO nên `pom.xml`, `Dockerfile`, compose không phải sửa dòng nào. Tránh tên `apps/` vì trùng schema PostgreSQL `apps` và làm nhiễu `grep apps.srv_poi`. Tiền tố `services/` chừa chỗ cho service đọc khác về sau mà không đổi rule glob.
- **Chi phí**: 0 B context thường trực; glob rule mới chỉ nạp khi mở file trong thư mục đó.
- **Rủi ro**: đường dẫn dài trên Windows khi Maven sinh `target/` (giới hạn 260 ký tự); hiện chưa đo. `MISSING_EVIDENCE`: độ dài đường dẫn sâu nhất sau khi chép. Nghiệm thu task con: `mvnw.cmd -q test` chạy được từ thư mục mới.
- **Rollback**: xóa thư mục, revert commit; nguồn `D:\git\SunGrp_VSVN_API` vẫn nguyên.

### P-a2. Thư mục docs

- **Hiện trạng**: `docs/poi-serving-api/` có 4 file Vietnamese (85 KB) và 2 script (`api-source-inventory.md` §1). `check-gaps.py` ghi tên host DEV trong docstring; `list-repos.sh` đọc PAT từ env.
- **Thay đổi**: chép sang `docs/poi-serving-api/` của repo này, giữ nguyên tên file để liên kết nội bộ không gãy. Bỏ tên host khỏi docstring `check-gaps.py` (script đã đọc `PGHOST` từ env tại dòng 25). Thêm một dòng vào bảng `docs/context/00_README.md` trỏ sang `docs/poi-serving-api/HANDOFF.md`. Thêm `docs/poi-serving-api/` vào mục "chỉ đọc khi được nêu" của rule 00 giống `notebooks_lgc/` (4 file ≈ 21k token).
- **Lý do**: yêu cầu của user nêu đúng tên này; 4 file là context lớn, không được nạp mặc định.
- **Chi phí**: 1 dòng rule 00 (≈ 60 B, còn trong budget 4,096 B always-apply: hiện 2,570 B).
- **Rủi ro**: số liệu trong các file đó đã cũ (HANDOFF §11 tự ghi); agent có thể trích số cũ. Giảm bằng nhãn ở đầu mỗi file "số liệu ngày đo, không phải hiện trạng".
- **Rollback**: xóa thư mục, revert.

### P-a3. Instruction lồng: `AGENTS.md` theo thư mục cộng `CLAUDE.md` theo thư mục

- **Hiện trạng**: chỉ có root `AGENTS.md` (8,187 B, dư 5 B) và `CLAUDE.md` (1,425 B, chứa `@AGENTS.md`); không có file lồng (`agent-system-inventory.md` §1). `AGENTS.md:67` (622 B) lặp lại nội dung `10-fabric-notebook.mdc:9`; `AGENTS.md:68` (302 B) lặp `20-data-pipeline.mdc:10`; `AGENTS.md:66` (263 B) liệt kê 3 notebook dùng công thức partner `poi_id`.
- **Thay đổi**:
  1. Tạo `services/data-serving-service/AGENTS.md` (English, ≤ 4,096 B): stack và lệnh thật (`mvnw.cmd -q test`, `mvnw.cmd package`, `docker compose up`), nguyên tắc read-only trên `apps.srv_poi_*`, không `ddl-auto`, không đọc chéo schema (`DESIGN-AND-PLAN.md` §C.4), DTO không lộ cột không có trong gold, không log dữ liệu cá nhân (`email`, `phone`, `author_name`), biến môi trường theo `application.yml` (tên biến, không giá trị), vị trí Flyway và quy tắc đặt tên `V<n>__<slug>.sql`.
  2. Tạo `services/data-serving-service/CLAUDE.md` chỉ chứa `@AGENTS.md` (giống root).
  3. Root `AGENTS.md`: gộp dòng 67 và 68 thành một dòng trỏ sang rule 10, rule 20 và `02_NAMING_CONVENTION.md` §2–§3 (≈ 130 B, tiết kiệm ≈ 790 B); rút dòng 66 còn công thức và tên bảng nguồn (≈ 110 B, tiết kiệm ≈ 150 B); thêm vào §7 hai dòng (≈ 250 B): "Serving API ở `services/data-serving-service/`, chỉ đọc `apps.srv_poi_*`; quy tắc trong `AGENTS.md` của thư mục đó" và "`*.sql` dưới `db/migration/` là PostgreSQL". Kết quả ước tính ≈ 7,500 B, dư ≈ 690 B cho §3 và §8 (P-d2, P-f1).
  4. Thêm vào `doctor`: mọi `services/*/AGENTS.md` ≤ 4,096 B.
- **Lý do**: Codex nạp `AGENTS.md` theo cây thư mục từ gốc tới cwd; Claude Code nạp `CLAUDE.md` của thư mục con khi làm việc trong đó `[VERIFY phiên bản đang dùng]`. Một nguồn cho ba runtime; Cursor dùng rule glob tham chiếu cùng file (P-c3). Phần trùng lặp trong root `AGENTS.md` hiện tốn 2 lần token ở Cursor khi rule 10 hoặc 20 được kích hoạt.
- **Chi phí**: Fabric session không tăng; session mở file Java tăng ≈ 1,000 token (file lồng).
- **Rủi ro**: Cursor có đọc `AGENTS.md` lồng hay không chưa chứng minh được từ repo `[VERIFY]`; vì vậy Cursor không dựa vào file lồng mà dựa vào rule glob P-c3. Nội dung `AGENTS.md:67–68` bị rút gọn có thể làm agent Claude (Architect) thiếu quy tắc notebook; Architect đọc rule 10 và 20 theo đường dẫn nêu trong dòng gộp.
- **Rollback**: revert `AGENTS.md`; xóa 2 file lồng; `doctor` không đổi kết quả.

### P-a4. `.gitignore`, `.cursorindexingignore`, `.dockerignore`

- **Hiện trạng**: `.gitignore` của API (dòng cuối) ignore `.claude`, `.agent`, `.agents`, `openspec`, `graphify-out`; gộp vào gốc sẽ ignore `.claude/settings.json` của repo này. `.cursorindexingignore` hiện có 7 dòng, không có `target/`.
- **Thay đổi**: `services/data-serving-service/.gitignore` chỉ giữ `target/`, `.mvn/wrapper/maven-wrapper.jar`, `.env`, `.env.local`, `.env.*.local`, `!.env.example`, `.idea/`, `*.iml`, `.vscode/`; bỏ các dòng `.claude`, `.agent*`, `openspec*`, `graphify-out`. Thêm `services/*/target/` vào `.cursorindexingignore`. `.dockerignore` giữ trong thư mục service (build context là thư mục service).
- **Lý do**: tránh ignore nhầm cấu hình agent; `target/` chứa class và báo cáo surefire, làm nhiễu index.
- **Chi phí**: không.
- **Rủi ro**: quên `.env` khi user chạy compose local; đã ignore.
- **Rollback**: revert.

### P-a5. `vv.py context`, `verify`, `doctor` cho task API

- **Hiện trạng**: `verify` (`scripts/vv.py:1676–1733`) phân lane theo đuôi file: `*.sql` không phải `*.pg.sql` → sparksql; không có lane Java; `changed_files` bỏ qua `.ai/`. `context` (`vv.py:796–855`) không nhìn `scope.systems`. `doctor` (`vv.py:1735–1843`) chỉ kiểm file agent-system Fabric. Flyway bắt buộc tên `V<n>__<slug>.sql`, không đổi được sang `.pg.sql`.
- **Thay đổi**:
  1. `verify`: file `.sql` có đường dẫn chứa `/db/migration/` vào lane `sqlfluff[postgres]`; thêm lane `maven` chạy `mvnw.cmd -q -B test` trong `services/data-serving-service/` khi có file thay đổi dưới thư mục đó; trước khi chạy kiểm `docker info`; nếu Docker vắng thì lane trả `FAIL` kèm thông báo, trừ khi gọi `--allow-no-docker` (ghi rõ vào `verify.log`, gate `local_verification` không được `pass` cho task có `scope.systems` chứa `poi-serving-api`). Kiểm `java -version` ≥ 26 trước khi gọi wrapper; thiếu thì `FAIL` với hướng dẫn.
  2. `context`: khi `scope.systems` chứa `poi-serving-api`, thêm block `## API` gồm 4 dòng: đường dẫn service, lệnh test, đường dẫn `AGENTS.md` lồng, trạng thái Docker/JDK.
  3. `doctor`: thêm kiểm `services/*/AGENTS.md` ≤ 4,096 B; `services/*/.gitignore` không chứa `.claude`; `.cursor/rules/40-java-api.mdc` tồn tại và không `alwaysApply`; không có chuỗi literal `password=`, `PASSWORD:` kèm giá trị trong `.cursor/mcp.json`, `.mcp.json`, `docker-compose.yml` ngoài dạng `${...}`; JDK và Docker in dòng `INFO`, không `WARN`, để `doctor` giữ không WARN như ràng buộc.
  4. `tests/test_vv.py`: thêm test cho phân lane đường dẫn và block `## API`.
- **Lý do**: `handoffs/fable-input.md` nêu rõ Flyway sẽ bị lint sai dialect; lane Java là điều kiện để gate `local_verification` có nghĩa với API; Testcontainers cần Docker (`DataServingApplicationTests`, `PoiRepositoryIntegrationTest`).
- **Chi phí**: ≈ 120 dòng Python, 1 lần. `verify` chậm hơn khi có file Java (Maven lần đầu tải dependency; chưa đo, `MISSING_EVIDENCE` thời gian chạy `mvnw test` trên máy này).
- **Rủi ro**: `docker-compose.yml:8–9,34–36` của API chứa credential local inline; kiểm `doctor` sẽ FAIL cho tới khi chuyển sang `${POSTGRES_USER}`-style đọc từ `.env`. Đây là thay đổi mong muốn nhưng cần Main sửa compose khi chép (P-h, CT-3).
- **Rollback**: revert `vv.py` và test; lane Java biến mất, các lane cũ không đổi.

## b. Hợp đồng gold → serving

### P-b1. Nguồn sự thật

- **Hiện trạng**: có 5 định nghĩa cho cùng 5 bảng: gold DDL trong `NB_SETUP_INITIAL_DDL` cell `init_tables` và `NB_CREATE_DDL`; NodeSpec `pk` trong `NB_GLD_SRV_POI_*` (`pk=("media_id", "poi_id")` ở media gallery, `pk=("review_id",)` ở review); `docs/context/mapping_*.md`; `sql/postgres/gld_srv_serve.pg.sql`; Flyway `V1__init_srv_poi_tables.sql` và 5 entity JPA. `docs/context/00_README.md` đã quy định "Notebook trong repo > tài liệu thiết kế > bộ context". Drift đo được (`api-source-inventory.md` §4): PK `srv_poi_media_gallery` (`media_id` ở Flyway và entity `SrvPoiMediaGallery.java:27–28` so với `(media_id, poi_id)` ở gold và PG DDL dòng 104); `srv_poi_review.source_name` có ở Flyway dòng 103 và entity `SrvPoiReview.java:35`, không có ở gold (`init_tables`, mục `gld_srv_poi_review`), PG DDL và mapping. Không có thành phần nào nạp gold vào `apps.srv_poi_*`; runtime `flyway.enabled: false` (`application.yml:39`), test `flyway.enabled: true` (`src/test/resources/application.yml:9`).
- **Thay đổi**: tuyên bố trong `AGENTS.md` lồng và `WORKFLOW.md`: nguồn sự thật cột và kiểu là gold DDL (`init_tables`), nguồn sự thật khoá là NodeSpec `pk`; `mapping_*.md` là tài liệu; `gld_srv_serve.pg.sql`, Flyway, entity là bản dẫn xuất phải khớp. Mọi thay đổi cột hoặc khoá đi qua `data_model_change` → `run-author --kind model` → Architect (quy trình hiện có, `WORKFLOW.md` §5).
- **Lý do**: trùng với quy tắc đã có của repo; gold là nơi pipeline sinh dữ liệu nên API không thể có cột mà gold không có.
- **Chi phí**: 3 dòng tài liệu.
- **Rủi ro**: `API-GAPS.md` §7 và `HANDOFF.md` §10 cho thấy phía API muốn thêm cột (`blur_hash`, `mime_type`, `source` và `lang` cho review theo quyết định 03/11 ở `DESIGN-AND-PLAN.md` §G.4). Những yêu cầu đó phải vào task dữ liệu, không vào API trước.
- **Rollback**: không có thay đổi mã; bỏ câu tuyên bố.

### P-b2. Check tự động phát hiện lệch

- **Hiện trạng**: `tests/test_gld_srv_poi_contract.py`, `test_initial_ddl_contract.py`, `test_poi_media_amenity_contract.py` kiểm notebook và mapping, không đọc Flyway hay entity (`api-source-inventory.md` §4). `evidence/probes/api_schema_diff.py` đã so Flyway với PG DDL.
- **Thay đổi**: thêm `tests/test_srv_poi_serving_contract.py` (pytest, không Spark, không JDK): đọc `init_tables` và NodeSpec `pk` của 5 notebook; đọc `sql/postgres/gld_srv_serve.pg.sql`; đọc mọi `V*__*.sql` trong `services/data-serving-service/src/main/resources/db/migration/`; đọc `@Table`, `@Id`, `@IdClass`, `@Column` của 5 entity bằng regex. Khẳng định: tập cột bằng nhau theo tên; kiểu ánh xạ theo bảng ở đầu `gld_srv_serve.pg.sql` dòng 4–12; PK bằng NodeSpec `pk`; `@IdClass` tồn tại khi PK nhiều cột. Test chạy trong lane pytest hiện có nên mọi `verify` đều kiểm. Chuyển logic từ `api_schema_diff.py` sang test rồi giữ probe làm tài liệu.
- **Lý do**: lệch được phát hiện tại local trước review; không cần Docker hay Fabric.
- **Chi phí**: ≈ 150 dòng test, thời gian chạy < 1 s.
- **Rủi ro**: regex entity dễ vỡ khi dùng Lombok hoặc annotation nhiều dòng; giới hạn bằng quy ước trong `AGENTS.md` lồng: mỗi `@Column` một dòng, `name=` bắt buộc. Test sẽ FAIL ngay sau khi chép code vì 2 drift hiện có; thứ tự xử lý ở P-h (CT-4 trước khi bật test, hoặc `xfail` có lý do ghi trong `decision.md`).
- **Rollback**: xóa test.

### P-b3. Vai trò của Flyway và DDL PostgreSQL

- **Hiện trạng**: Flyway tạo schema và 10 index nhưng chỉ chạy trong test; `API-GAPS.md` §5 ghi "Read-only: không Flyway. DDL của `apps` do pipeline Fabric sở hữu"; `gld_srv_serve.pg.sql` không tạo schema, không tạo index (dòng 15).
- **Thay đổi**: hai phương án, cần user chốt (D-08).
  - Phương án 1 (khuyến nghị): một DDL PostgreSQL duy nhất là `sql/postgres/gld_srv_serve.pg.sql` (bổ sung `CREATE SCHEMA IF NOT EXISTS apps` và index, đưa qua `sql-data-reviewer`); test của API nạp file này qua Testcontainers `withInitScript`; bỏ dependency Flyway và thư mục `db/migration`. Rule `30-sql.mdc` không cần ngoại lệ Flyway; lane postgres giữ nguyên.
  - Phương án 2: giữ Flyway cho test, `V1` được sinh từ `gld_srv_serve.pg.sql` và test P-b2 so khớp; `flyway.enabled: false` giữ ở runtime.
- **Lý do**: một DDL, một chủ sở hữu (phía dữ liệu), khớp tuyên bố của chính tài liệu API; giảm một nguồn lệch.
- **Chi phí**: phương án 1 sửa `pom.xml`, 2 file test config, 1 test class; phương án 2 chỉ thêm test.
- **Rủi ro**: phương án 1 làm API không tự dựng được DB khi deploy môi trường mới; đó là chủ đích (DDL do Data chạy theo `runtime-runbook.md`). Index của Flyway (10 index) chưa có trong DDL repo; `MISSING_EVIDENCE` về index nào thực sự cần (chưa có số liệu truy vấn).
- **Rollback**: phương án 1 khôi phục Flyway từ nguồn đọc; phương án 2 xóa test.

### P-b4. Hai drift hiện có

- `srv_poi_media_gallery` PK: gold và PG DDL dùng `(media_id, poi_id)` theo commit `e309c0e`; API dùng `media_id`. Cần bằng chứng: `media_id` có duy nhất toàn bảng gold không. `MISSING_EVIDENCE`; probe Fabric DEV (user chạy): `SELECT COUNT(*) AS rows, COUNT(DISTINCT media_id) AS media_ids FROM lh_vv_gold.dbo.gld_srv_poi_media_gallery`. Nếu bằng nhau: API có thể giữ `@Id media_id` nhưng Flyway/DDL vẫn theo gold, hoặc gold đổi khoá (task dữ liệu). Nếu khác: entity bắt buộc `@IdClass(media_id, poi_id)`. Quyết định D-09.
- `srv_poi_review.source_name` (và `lang`, `source` theo `DESIGN-AND-PLAN.md` §G.4): gold không có; API có. Hai hướng: bỏ khỏi entity và Flyway (API theo gold, nhanh) hoặc thêm vào gold qua `run-author --kind model` (BA đã chốt API 9 trả `source` và `lang` ngày 03/11 nhưng mapping review `D-SRV-LANG` lại bỏ `lang`). Mâu thuẫn này do user và BA chốt, D-10.

## c. Phân vai theo thế mạnh

Nguyên tắc: Cursor là nơi viết code (rule glob, skill, hook, MCP); Claude Code là nơi đọc và viết tài liệu quyết định (Architect, Author, Analyst; subagent, không cần skill thi công); Codex là nơi review chỉ đọc (AGENTS.md lồng, agent toml, sandbox read-only). Không runtime nào nhận thêm vai mới.

### P-c1. Bảng thành phần hiện có

| Thành phần | Hành động | Lý do | Chi phí token (ước, mỗi session) |
|---|---|---|---|
| `AGENTS.md` | giữ, rút gọn §7 (P-a3), thêm §3 và §8 (P-d2, P-f1) | duy nhất được nạp ở cả 3 runtime | 2,050 → ≈ 1,900 |
| `CLAUDE.md` root | giữ | bảng vai Claude; không đổi | 360 |
| `docs/agent-system/WORKFLOW.md` | giữ, thêm §7 reviewer API, §10 lane `maven`, §Task artifacts dòng "API runtime runbook" | đọc theo mục | +≈ 150 khi đọc mục |
| `docs/agent-system/TOKEN_OPTIMIZATION_PLAN.md` (85 KB) | bỏ (chuyển `docs/agent-system/archive/` hoặc xóa, git giữ lịch sử) | không rule nào tham chiếu | 0, giảm nhiễu index |
| `docs/AGENT_PROMPT_SAMPLES.md` A1–A19 | gộp: giữ A1, A4, A9, A10, A13–A16, A18, A19 (có dùng); gộp A2/A3/A5/A6/A7/A8/A11/A12/A17 vào một mục "câu ngắn thường dùng"; thêm A20 "Task API" | 654/708 lượt không dùng mẫu; 9 mẫu có 0–1 lượt | 4,080 → ≈ 2,500 khi user mở |
| `docs/context/*` | giữ; thêm 1 dòng trỏ `docs/poi-serving-api/` | — | 0 |
| Rule `00-main-orchestrator` | giữ; thêm 1 dòng cấm đọc `docs/poi-serving-api/` khi không nêu; sửa câu "Record the actual Main model" theo P-d2; thêm "`transition` đã validate, không gọi `validate` trước đó" | 438 `transition` kèm 409 `validate` thừa (`vv.py:908,917`) | 640 → ≈ 700 |
| Rule `10-fabric-notebook`, `20-data-pipeline` | giữ | đúng glob | 0 (theo glob) |
| Rule `30-sql` | giữ, sửa dòng 7: thêm "`*.sql` dưới `db/migration/` là PostgreSQL (Flyway)"; nếu chọn P-b3 phương án 1 thì không cần | glob `**/*.sql` bắt Flyway | +20 |
| Rule mới `40-java-api` | thêm (P-c3) | — | ≈ 1,000 chỉ khi mở file Java |
| Skill `fabric-runtime-evidence`, `vsvn-extract-notebook`, `vsvn-notebook-library`, `vsvn-operator-docs`, `vsvn-data-model-flow`, `vsvn-eventhubs-kafka-ui` | giữ | đúng việc cũ | 710 (mô tả) |
| Skill `vsvn-task-workflow` | giữ, thêm mục "Task API: lane maven, runtime local" (≤ 1 KB) | tránh skill mới cho quy trình | +0 mô tả |
| Skill mới `vsvn-api-service` | thêm (P-e2) | — | +≈ 110 mô tả |
| Subagent `requirements-analyst` (26 KB) | giữ | không liên quan API trong phase này | 115 (mô tả) |
| `.claude/settings.json` | giữ; thêm domain WebFetch (P-g3); thêm `hooks` không cần (P-f3) | — | 0 |
| `.claude/skills/`, `.claude/commands/` | không thêm | vai Claude trong repo là chỉ đọc; skill thi công không có ích | 0 |
| `.codex/config.toml` | giữ | — | 0 |
| `.codex/agents/*` 6 file | giữ | — | chỉ khi được gọi |
| Reviewer Codex mới ×3 | thêm (P-e3) | không reviewer nào phủ Java (`agent-system-inventory.md` §4) | chỉ khi được gọi |
| `[profiles]` Codex, `.codex/prompts/` | không thêm | runner truyền model qua CLI (`agent_runner.py:415–416`) | 0 |
| Hook Cursor | thêm (P-f1, P-f2) | — | 0 token, 1 process |
| MCP Cursor | thêm 1 (P-g1) | — | ≈ 300 mô tả tool |
| MCP Claude Code, Codex | không | — | 0 |
| Plugin | không | — | 0 |

### P-c2. Luồng vai cho task API

- Main (Cursor) viết Java, SQL migration, test, compose; chạy `verify` (có lane maven). Không đổi chủ sở hữu.
- Author (Claude Code, `run-author`) viết `problem-analysis.md`, `proposal.md`, `model-design.md` khi task API đổi cột hoặc khoá; `runtime-runbook.md` cho runtime local.
- Architect (Claude Code, `run-gate`) viết `architecture.md` khi task API chạm hợp đồng HTTP, entity, Flyway, hoặc > 8 file (`WORKFLOW.md` §5 đã đủ, không thêm tiêu chí).
- Review (Codex, `run-gate`) gọi reviewer API theo đường dẫn diff (P-e3).
- User chạy `docker compose up` và smoke test, ghi kết quả vào `runtime-runbook.md` giống Fabric DEV (P-e5); commit.

### P-c3. Cursor rule `40-java-api.mdc`

- **Hiện trạng**: không rule nào khớp `*.java`, `pom.xml`, `db/migration/*.sql`.
- **Thay đổi**: `.cursor/rules/40-java-api.mdc`, `alwaysApply: false`, `globs: services/**/*.java, services/**/pom.xml, services/**/db/migration/*.sql, services/**/application*.yml, services/**/Dockerfile, services/**/docker-compose.yml`. Thân rule: một dòng "Read `services/data-serving-service/AGENTS.md` first" cộng tham chiếu `@services/data-serving-service/AGENTS.md` `[VERIFY cú pháp @file trong rule của phiên bản Cursor đang dùng]`; nếu không hỗ trợ, thân rule chép nội dung và `doctor` kiểm hai file khớp nhau theo hash.
- **Lý do**: Cursor kích hoạt theo glob nên Fabric session không tốn; một nguồn với Codex và Claude.
- **Chi phí**: ≈ 1,000 token khi mở file Java.
- **Rủi ro**: tham chiếu file không hoạt động → nội dung trùng ở 2 nơi; `doctor` giữ chúng đồng bộ.
- **Rollback**: xóa rule.

## d. Model cho từng lane

### P-d1. Bảng lane

| Lane | Hiện tại (`AGENTS.md` §3, `vv.py:453–455,521–523`, `agent_runner.py:16–25`) | Đề xuất | Cần gì theo §3 |
|---|---|---|---|
| Main, việc Fabric | `grok-4.7` medium | giữ | không |
| Main, việc API (Java) | `grok-4.7` medium; EX-03 đặt `claude-opus-5-5` medium cho roadmap này | `claude-opus-5-5` medium theo phê duyệt thường trực ghi vào §3; `vv.py` tính `models.main.expected` theo `scope.systems` (`poi-serving-api` → `claude-opus-5-5`) | user-approved exception ghi §3 (như dòng 2026-10-09); không cần eval vì eval suite không có case Java; hoặc chạy eval sau khi thêm case Java (P-d4) |
| Author `analysis`, `model`, `runbook` | `claude-opus-5-5` medium | giữ cho cả API | không |
| Author `proposal` | `claude-opus-5-5` high | giữ; Fable qua exception khi user chọn (P-d3) | exception từng task |
| Architect | `claude-opus-5-5` high | giữ; Fable qua exception khi user chọn | exception từng task |
| Review Fabric | `gpt-5.6-sol` medium | giữ | không |
| Review API (3 reviewer mới) | — | `gpt-5.6-sol` medium (cùng pin của `doctor` `vv.py:1795–1796`) | không đổi model; thêm case Java vào `.ai/evals/cases.yaml` để có cơ sở đo (P-d4) |
| Requirements Analyst | `claude-opus-5-5` medium | giữ | không |

### P-d2. Ghi phê duyệt thường trực cho Main lane API

- **Hiện trạng**: 50 lượt user phải đặt hoặc đổi exception (`user-action-inventory.md` §6); `00-main-orchestrator.mdc:21` bắt Main dừng nếu không phải Grok trừ khi có exception.
- **Thay đổi**: thêm vào `AGENTS.md` §3 một câu (≈ 120 B): "Main for `scope.systems: poi-serving-api`: `claude-opus-5-5`, `medium` (user approved <ngày>)". `vv.py` `validate` chọn expected theo lane; `_template/task-state.yaml` không đổi (Main ghi `scope.systems` ở triage rồi `validate` tự đổi kỳ vọng).
- **Lý do**: giảm lặp thủ công; vẫn tuân §3 vì có phê duyệt ghi rõ.
- **Chi phí**: 120 B `AGENTS.md`; ≈ 15 dòng `vv.py`; test.
- **Rủi ro**: task hỗn hợp (Fabric và API trong một task) → quy ước: có `poi-serving-api` trong `scope.systems` là lane API; khuyến nghị tách task.
- **Rollback**: bỏ câu và nhánh `vv.py`; EX từng task như hiện nay.

### P-d3. Runner đọc model từ `exceptions`

- **Hiện trạng**: `agent_runner.py:16–25` gán cứng; `run-gate` truyền tại `:249–250`, `run-author` tại `:303–304`, Codex tại `:415–416`; schema review pin `enum: [REVIEW_MODEL]` tại `:330–331`; `validate` đã thu `valid_overrides` (`vv.py:457–513`) nhưng không ai dùng ở runner (`agent-system-inventory.md` §5). Hệ quả: EX-01, EX-02 của task này phải chạy tay ngoài runner.
- **Thay đổi**: hàm `resolve_lane(state, role) -> (model, effort, source)` trong `agent_runner.py`: nếu `exceptions` có entry `kind: model_override`, `role` trùng (`architect`, `author`, `author_proposal`, `review`), `approved_by: user`, thì dùng `model` và `effort` của entry, in `MODEL OVERRIDE <id>: <model> <effort>` và ghi `models.<role>.actual` bằng model đó; không thì dùng hằng số. Schema review dùng model đã resolve. `run-gate` và `run-author` nhận `--timeout` mặc định 2700 (8 chat đã phải truyền tay). `validate` chấp nhận `actual` bằng model override (đã có cơ chế). `doctor` không đổi.
- **Lý do**: trả lời đúng câu d; cơ chế exception đã được validate và mirror trong `decision.md`, chỉ thiếu bước đọc.
- **Chi phí**: ≈ 60 dòng Python, 4 test.
- **Rủi ro**: CLI `claude -p --model claude-fable-5-1` có được chấp nhận không là `MISSING_EVIDENCE`; `external-smoke` phải có bước thử với model override trước khi dùng cho gate thật. Codex với model khác `gpt-5.6-sol` không nằm trong đề xuất (không có exception nào như vậy ngoài 1 tiền lệ `review → claude-opus-5-5` không chạy được qua Codex).
- **Rollback**: revert; hằng số lại có hiệu lực.

### P-d4. Eval suite cho Java

- **Hiện trạng**: `.ai/evals/cases.yaml` có 8 case, toàn Fabric; `rubric.md` chấm 6 chiều; không có lệnh `vv.py eval`, suite chạy thủ công (`MISSING_EVIDENCE` cách user đã chạy suite trước đây).
- **Thay đổi**: thêm 4 case: (1) DTO lộ cột không có trong gold; (2) Specification ghép chuỗi từ tham số request (injection) và thiếu phân trang; (3) N+1 khi tải gallery theo danh sách POI; (4) Flyway đổi PK không có bước rollback trong runbook. Mỗi case có `expected_reviewers` trong 3 reviewer mới và `required_topics`.
- **Lý do**: điều kiện để thay model lane API về sau có cơ sở; cũng là spec cho prompt reviewer.
- **Chi phí**: ≈ 40 dòng YAML.
- **Rủi ro**: không.
- **Rollback**: xóa case.

## e. Thành phần mới cho API

### P-e1. Rule glob

Đã nêu ở P-c3 (`40-java-api.mdc`) và sửa `30-sql.mdc:7` (P-c1).

### P-e2. Skill `vsvn-api-service` (Cursor)

- **Hiện trạng**: không skill API; skill lớn nhất 19,332 B gần trần 20,480 B.
- **Thay đổi**: một skill `.cursor/skills/vsvn-api-service/SKILL.md` ≤ 12 KB, mô tả ≤ 300 ký tự, ba mục: (1) endpoint Spring: controller → service → repository, envelope `ApiResponse`/`PageResponse`, `GlobalExceptionHandler`, `LanguageResolver`, không logic trong controller, OpenAPI annotation; (2) migration và entity: quy trình P-b1 (gold trước), `V<n>__`, `@IdClass` khi PK nhiều cột, test P-b2 phải xanh; (3) test: `@WebMvcTest` cho contract, `@SpringBootTest` + Testcontainers cho repository, fixture tổng hợp ≤ 50 dòng không dữ liệu cá nhân, `mvnw.cmd -q test`. Không tách 3 skill vì mỗi mô tả thêm ≈ 110 token vào mọi session Cursor.
- **Lý do**: đúng kiểu skill đang dùng (mô tả kích hoạt theo việc); tránh phình always-loaded.
- **Chi phí**: +110 token mỗi session; thân skill chỉ khi kích hoạt.
- **Rủi ro**: mô tả quá rộng kích hoạt nhầm trong task Fabric; viết "Do not use for notebooks, pipelines, DDL Fabric, ctrl tables" như các skill hiện có.
- **Rollback**: xóa thư mục skill.

### P-e3. Reviewer Codex cho API

- **Hiện trạng**: 4 reviewer Fabric + `risk-gate` + `requirements-reviewer`; `REVIEWERS` ở `vv.py:60–63`; `doctor` pin model từng toml; `WORKFLOW.md` §7 định tuyến.
- **Thay đổi**: thêm 3 toml, mỗi file ≤ 2 KB, cùng khung "read-only, P0/P1 rows only, VERDICT" như `spark-runtime-reviewer.toml`:
  - `api-contract-reviewer` (ID `API-001…`): hợp đồng HTTP so với DTO, DTO so với entity, entity so với gold (đọc `init_tables`), envelope lỗi, phân trang, i18n qua `lang`, OpenAPI, tương thích ngược của response. Định tuyến khi diff chạm `api/`, `dto/`, `domain/entity`, `db/migration`, `OpenApiConfig`.
  - `app-security-reviewer` (ID `SEC-001…`): validate đầu vào, Specification/JPQL động, lộ actuator (`application.yml:55` mở `metrics,prometheus`), header request-id, dữ liệu cá nhân trong log và response, secret trong cấu hình, dependency. Định tuyến khi diff chạm `common/web`, `config/`, filter, `application*.yml`, `pom.xml`, `Dockerfile`, compose.
  - `jpa-performance-reviewer` (ID `JPA-001…`): N+1, fetch plan, phân trang bắt buộc, chỉ mục so với Specification, transaction read-only, pool Hikari, `open-in-view: false` giữ nguyên, batch size. Định tuyến khi diff chạm `domain/repository`, `service/`, entity, index trong migration.
  - `risk-gate`: thêm vào `developer_instructions` một mệnh đề "and the PostgreSQL serving API" để phủ cross-system gold → PostgreSQL → API.
  - `vv.py:60` thêm 3 tên; `doctor` kiểm 3 toml cùng pin; `WORKFLOW.md` §7 thêm 3 dòng; `.ai/evals/cases.yaml` P-d4.
- **Lý do**: câu e yêu cầu; 3 miền có tiêu chí khác nhau, prompt hẹp cho kết quả ổn định hơn một reviewer gộp; Coordinator chỉ gọi reviewer liên quan nên chi phí theo diff. Phương án gộp `app-security` và `jpa-performance` thành `java-service-reviewer` là lựa chọn D-13 nếu user muốn ít thread Codex (`max_concurrent_threads_per_session = 4`).
- **Chi phí**: 3 file ≈ 5 KB; mỗi round review API gọi 1–3 reviewer.
- **Rủi ro**: reviewer Codex không chạy được Maven (sandbox read-only, không Docker) nên chỉ review tĩnh; test chạy ở lane `verify` trước review (đúng thứ tự `WORKFLOW.md` §6 mục 5).
- **Rollback**: xóa toml, hoàn `vv.py:60`, `WORKFLOW.md`.

### P-e4. Lane verify `maven`

Đã nêu ở P-a5. Điều kiện môi trường: JDK 26 (máy hiện có JDK 21, `pom.xml:17` yêu cầu 26) và Docker. Hai lựa chọn D-11: cài JDK 26 cục bộ (khuyến nghị; wrapper tự tải Maven 3.9.16 theo `.mvn/wrapper/maven-wrapper.properties`) hoặc chạy test trong image `maven:3.9-eclipse-temurin-26` (Dockerfile stage 1) nhưng Testcontainers trong container cần Docker socket, phức tạp hơn và chưa thử.

### P-e5. Gate runtime local thay Fabric DEV

- **Hiện trạng**: gate `runtime` và `runtime-runbook.md` dành cho Fabric DEV do user chạy; `docker-compose.yml` của API dựng `postgres:18-alpine` và service; không có dữ liệu mồi; không loader gold → PostgreSQL.
- **Thay đổi**: cho task API có `runtime_required: true`, `runtime-runbook.md` (Author `--kind runbook`, Vietnamese) mô tả: `docker compose up -d postgres`; nạp `sql/postgres/gld_srv_serve.pg.sql`; nạp fixture tổng hợp `services/data-serving-service/src/test/resources/fixtures/*.sql` (≤ 50 dòng mỗi bảng, không dữ liệu cá nhân); `docker compose up data-serving-service`; smoke: `GET /actuator/health`, `GET /api/v1/pois/compact`, 1 request mỗi endpoint còn lại; kiểm log không in `email`, `phone`, `author_name`; `docker compose down -v`. User chạy và ghi `PASS`/`FAIL` như hiện nay. Có thể cho Main chạy trực tiếp vì local không ảnh hưởng dữ liệu thật, cần user chốt D-12.
- **Lý do**: gate runtime có nghĩa với API mà không cần DEV; dữ liệu thật trong `apps` DEV mới có 24 POI (`API-GAPS.md` §7 mục 1, số liệu 29/10) và chưa có loader.
- **Chi phí**: 1 runbook mẫu, fixture 5 file.
- **Rủi ro**: fixture không đại diện phân bố thật; gate này chứng minh hợp đồng và khởi động, không chứng minh hiệu năng. Hiệu năng cần DEV sau khi có loader (CT-9).
- **Rollback**: không có thay đổi hệ thống.

## f. Hook và skill rút từ user-action inventory

Dữ kiện: hook áp dụng cho phiên tương tác. Runner gọi Claude với `--setting-sources user` (`agent_runner.py:255`), nên hook và permission trong `.claude/settings.json` của repo không tác động tới `run-gate`/`run-author`; Codex chạy sandbox read-only, không cần hook. Vì vậy hook chủ yếu đặt ở Cursor (Main). Tên sự kiện hook Cursor dưới đây là `[VERIFY theo tài liệu Cursor của phiên bản đang cài]`.

| ID | Hành vi lặp | Tần suất (inventory) | Tự động hoá | Lợi ích ước lượng | Rủi ro |
|---|---|---|---|---|---|
| P-f1 | Agent chạy `git push` 122, `git commit` 102 segment dù §8 cấm; user mở 28 lượt "commit và", 105 lượt nhắc commit | §2, §6 | `.cursor/hooks.json` sự kiện trước khi chạy shell: từ chối `git push`, `git reset --hard`, `git rebase`, `git commit --amend`, `git checkout -- .`, `rm -rf`, `Remove-Item -Recurse`. `git commit` tùy D-05: (1) cấm như §8 hiện nay; (2) cho phép khi lượt hiện tại của user yêu cầu, §8 sửa thành "Agents never push, merge, or rewrite history; commit only when the user's current turn asks" | loại bỏ 122 push từ agent; giảm 105 lượt nhắc nếu chọn (2) | (2) làm agent commit sai phạm vi; giảm bằng hook chỉ cho `git commit` với `-m` và không `-a` khi có file ngoài `scope.files` (kiểm bằng script nhỏ) |
| P-f2 | `vv.py validate` 409 lần, phần lớn ngay trước `transition` vốn đã validate 2 lần (`vv.py:908,917`) | §2 | Hook sau khi sửa file khớp `.ai/tasks/*/task-state.yaml`: chạy `python scripts/vv.py validate <id>` và trả lỗi vào chat; rule 00 ghi "transition tự validate" | bớt ≈ 400 lệnh shell trên 50 task; lỗi state phát hiện ngay khi sửa | hook chạy trên mỗi lần sửa file (≈ 0.3 s) |
| P-f3 | `resume.md` phải ghi trước khi dừng; 45 lần thay đổi trên 50 task | §6 | Hook khi agent dừng: nếu `task.status` thuộc trạng thái dừng và `resume.md` không đổi trong phiên → nhắc trong chat | nhỏ; tỉ lệ đã cao | cảnh báo giả khi phiên chỉ đọc |
| P-f4 | `vv.py context` 382 lần đầu lượt | §2 | không hook; rule 00 đã bắt buộc; hook trước khi gửi prompt không biết task id | — | — |
| P-f5 | Gate chạy lâu (8 chat, `--timeout 2700`), OAuth hết hạn (1), token cạn (6 chat) | §4 | Không hook; runner: mặc định timeout 2700, gọi `external-doctor` trước gate (kiểm executable và đăng nhập `[VERIFY lệnh kiểm trạng thái đăng nhập của Claude CLI]`), in thời gian đã chạy mỗi 5 phút | gate fail sớm thay vì sau 45 phút | không |
| P-f6 | "Repository changed during read-only run" 5 chat | §4 | Runner in danh sách đường dẫn đổi (nếu chưa) và loại `.ai/.tmp/` khỏi snapshot | chẩn đoán nhanh; nguyên nhân gốc `MISSING_EVIDENCE` | không |
| P-f7 | `materialize` 12 lần, user chép dán 23 lượt | §2, §6 | giữ; không thêm | — | — |
| P-f8 | Mẫu prompt dùng 7.6% | §1 | gộp mẫu (P-c1); không hook | giảm 1,600 token khi user mở file | — |

Claude Code hook: không đề xuất. `permissions.deny` tại `.claude/settings.json:22–32` đã chặn git ghi và xóa cho phiên tương tác; runner không nạp project settings.

## g. MCP và plugin

| ID | Công cụ | Ứng viên | Mục đích | Quyền | Credential | Chọn hay loại |
|---|---|---|---|---|---|---|
| P-g1 | Cursor | MCP PostgreSQL chỉ đọc (ví dụ server có chế độ restricted/read-only `[VERIFY tên gói và chế độ]`) | Main xem schema, `EXPLAIN`, đếm dòng trên PostgreSQL local của compose khi viết Specification và index | chỉ đọc; chỉ DB local mặc định | `.cursor/mcp.json` tham chiếu `${env:VV_SERVING_PG_URL}`; giá trị trong biến môi trường user hoặc `.env` đã ignore; `doctor` kiểm không có literal | chọn, sau CT-3; dùng với DEV chỉ khi user cho phép từng lần như probe Fabric (§6) |
| P-g2 | Cursor, Claude Code | MCP Microsoft Fabric | đọc metadata lakehouse | — | cần SPN; `00_README.md` ghi "Không SPN" | loại |
| P-g3 | Claude Code | không MCP; thêm `WebFetch(domain:docs.spring.io)`, `docs.oracle.com`, `flywaydb.org`, `java.testcontainers.org`, `hibernate.org`, `www.postgresql.org` vào `allow` | Architect/Author tra tài liệu Spring Boot 4.1, Java 26 | đọc web | không | chọn (6 dòng JSON) |
| P-g4 | Codex | `[mcp_servers]` | — | — | — | loại; reviewer chỉ đọc repo |
| P-g5 | Cursor, Claude Code | MCP GitHub hoặc Azure DevOps | PR, work item | ghi | PAT | loại; user commit và push; agent không cần |
| P-g6 | Cursor, Claude Code | Plugin (marketplace) đóng gói skill và hook | phân phối cho nhiều máy | — | — | loại trong phase này; repo-local skill đủ; `MISSING_EVIDENCE` số người dùng repo |
| P-g7 | Cursor | MCP Docker | điều khiển compose | ghi local | socket | loại; lệnh `docker compose` trong runbook đủ và có log |

Chi phí P-g1: ≈ 300 token mô tả tool mỗi session Cursor; có thể tắt theo workspace khi làm Fabric. Rủi ro: agent truy vấn DEV nếu biến môi trường trỏ DEV; giảm bằng tên biến riêng cho local và quy tắc trong `AGENTS.md` lồng. Rollback: xóa `.cursor/mcp.json`.

## h. Lộ trình

Mỗi task con là một task `vv.py new`, Main `claude-opus-5-5` medium theo EX-03 (hoặc P-d2 khi đã có), một phase, dừng ở `ready_to_merge` để user commit. Điều kiện chung sau mỗi task: `python scripts/vv.py verify <id>` PASS, `python scripts/vv.py doctor` không WARN, `AGENTS.md` ≤ 8,192 B. Reviewer cho task agent-system: không reviewer Fabric nào phù hợp; đề xuất `risk-gate` một vòng cho CT-2 và CT-3, còn lại dựa `tests/test_vv.py` và user duyệt (D-15).

| # | Task con | Phụ thuộc | Việc | Nghiệm thu | Rollback |
|---|---|---|---|---|---|
| CT-1 | `runner-model-exceptions` | — | P-d3, P-f5, P-f6, rule 00 câu "transition tự validate" (P-f2 phần rule) | `external-smoke` chạy với một exception thử (model mặc định) và với `claude-fable-5-1` (kết quả quyết định D-07); test mới xanh | revert 2 file Python |
| CT-2 | `repo-layout-and-instructions` | — | P-a3, P-a4 (`.cursorindexingignore`), P-a5 (verify dialect theo đường dẫn, doctor budget lồng, block `## API`), P-c3, sửa `30-sql.mdc`, `WORKFLOW.md` §10, P-d2 (câu §3 và nhánh validate), P-g3 | `doctor` không WARN; `AGENTS.md` ≤ 8,192 B; rule 40 kích hoạt khi mở file `.java` thử `[VERIFY]`; Codex đọc `AGENTS.md` lồng trong một lần `exec` thử | revert |
| CT-3 | `import-data-serving-service` | CT-2; JDK 26 (D-11) | Main chép 62 file từ `D:\git\SunGrp_VSVN_API` commit `20bca8a` vào `services/data-serving-service/` và `docs/poi-serving-api/` (D-03); `.gitignore` lồng (P-a4); compose đọc credential từ `.env` thay vì inline; bỏ host khỏi docstring `check-gaps.py`; `.env.example` theo D-04; nhãn ngày đo trên 4 docs; ghi commit nguồn vào `decision.md` | `mvnw.cmd -q test` xanh với Docker; `verify` PASS kể cả lane maven và postgres; `doctor` không WARN; `grep` không thấy host DEV, không `.env` | xóa thư mục; nguồn đọc còn nguyên |
| CT-4 | `serving-contract-test` | CT-3; D-08, D-09, D-10 | P-b2 test; P-b3 theo phương án đã chốt; sửa entity/Flyway theo D-09, D-10 (nếu gold đổi thì tách task dữ liệu với `data_model_change`, `run-author --kind model`) | test contract xanh; `sql-data-reviewer` PASS nếu DDL đổi | revert test và entity |
| CT-5 | `codex-api-reviewers` | CT-3 | P-e3, P-d4, `WORKFLOW.md` §7 | `doctor` kiểm 3 toml; `external-smoke` gọi được 1 reviewer mới; 4 case eval có trong `cases.yaml` | xóa toml, hoàn `vv.py:60` |
| CT-6 | `cursor-hooks-and-commit-policy` | D-05 | P-f1, P-f2, P-f3; sửa §8 nếu chọn (2) | thử `git push` trong Cursor bị chặn; sửa `task-state.yaml` sai → lỗi hiện trong chat | xóa `.cursor/hooks.json`, hoàn §8 |
| CT-7 | `skills-and-prompt-samples` | CT-3 | P-e2, P-c1 (gộp mẫu A, mục API trong `vsvn-task-workflow`), P-a2 dòng README, bỏ `TOKEN_OPTIMIZATION_PLAN.md` (D-16) | `doctor` không WARN budget skill và samples | revert |
| CT-8 | `cursor-mcp-postgres-local` | CT-3; D-14 | P-g1 | `doctor` không thấy literal secret; truy vấn `SELECT 1` qua MCP tới PostgreSQL compose | xóa `mcp.json` |
| CT-9 (ngoài agent-system) | `gold-to-postgres-serving-load` | CT-4 | thiết kế và dựng thành phần nạp `gld_srv_poi_*` → `apps.srv_poi_*` (hiện không tồn tại, `api-source-inventory.md` §4); `cross_system`, `idempotency`, evidence Fabric DEV, Architect bắt buộc; runbook DDL `gld_srv_serve.pg.sql` trên DEV | ngoài phạm vi file này; chỉ ghi để lộ trình API có runtime thật | — |

Thứ tự: CT-1 và CT-2 song song (file không giao nhau trừ rule 00: CT-1 chỉ thêm một câu); CT-3 sau CT-2; CT-4, CT-5, CT-7, CT-8 sau CT-3 và độc lập nhau; CT-6 bất kỳ lúc nào sau D-05. Đầu mỗi task Main chạy `python scripts/vv.py context <id>`; `architecture_required: true` cho CT-2 và CT-3 (quá 8 file, 3 runtime), còn lại theo phân loại của Main.

## Ràng buộc cho Architect (EX-02)

1. Không đặt bất kỳ dòng nào trong `AGENTS.md` lồng mâu thuẫn với root; root thắng.
2. `services/data-serving-service/` không chứa file `.claude/`, `.cursor/`, `.codex/` riêng; mọi cấu hình agent ở gốc.
3. `verify` phải FAIL rõ ràng khi thiếu JDK hoặc Docker cho task API, không SKIP im lặng.
4. Runner chỉ đọc exception có `approved_by: user`; không bao giờ hạ model so với mặc định mà không in ra.
5. Không chép giá trị credential từ `docker-compose.yml` hay `application.yml` của nguồn đọc vào bất kỳ file nào của repo.
6. Test contract P-b2 không được phụ thuộc Spark, JDK, Docker.

## MISSING_EVIDENCE và câu hỏi

1. CLI Claude chấp nhận `--model claude-fable-5-1` trong chế độ `-p` không. Kiểm trong CT-1 bằng `external-smoke`.
2. `media_id` có duy nhất trong `gld_srv_poi_media_gallery` không. Probe ở P-b4, user chạy trên Fabric DEV.
3. Cursor phiên bản đang dùng có đọc `AGENTS.md` lồng, có hỗ trợ `@file` trong rule, và tên sự kiện hook. Kiểm trong CT-2 và CT-6.
4. Thời gian `mvnw.cmd test` và kích thước tải dependency lần đầu trên máy này. Đo trong CT-3.
5. Nguyên nhân 5 chat "repository changed during read-only run". Không có trong transcript (tool result không lưu).
6. Cách user đã chạy agent evaluation suite trước đây (không có lệnh trong `vv.py`).
7. `.env.example` của nguồn đọc chứa placeholder hay giá trị thật. Chỉ user xác nhận.
8. Số người dùng repo (quyết định plugin P-g6).
9. Index nào trong 10 index Flyway thực sự cần (chưa có số liệu truy vấn).

## Quyết định cần user chốt

| ID | Chủ đề | Lựa chọn | Khuyến nghị |
|---|---|---|---|
| D-01 | Thư mục code API | (a) `services/data-serving-service/`; (b) `services/data-serving-api/`; (c) `api/` | (a): trùng `artifactId` và tên repo ADO, không sửa pom, Dockerfile, compose |
| D-02 | Thư mục docs API | (a) `docs/poi-serving-api/`; (b) `docs/data-serving-service/` | (a): đúng tên trong yêu cầu, liên kết nội bộ không gãy |
| D-03 | Cách chép | (a) chép thường từ commit `20bca8a`, ghi nguồn vào `decision.md`; (b) `git subtree add` giữ lịch sử (user chạy) | (a): nguồn chỉ có 3 commit, subtree thêm merge commit và thao tác user |
| D-04 | `.env.example` | (a) user xem rồi chép nếu chỉ placeholder; (b) không chép, biến môi trường ghi trong `AGENTS.md` lồng | (b): tránh rủi ro, `application.yml` đã nêu đủ tên biến |
| D-05 | Chính sách commit §8 và hook | (1) giữ cấm tuyệt đối, hook chặn commit và push; (2) cho commit khi lượt hiện tại của user yêu cầu, hook chỉ chặn push, reset, rebase, amend, xóa đệ quy | (2): khớp 105 lượt user tự yêu cầu; push vẫn là của user |
| D-06 | Main lane API | (a) phê duyệt thường trực `claude-opus-5-5` medium ghi §3, `validate` theo `scope.systems`; (b) EX từng task như EX-03 | (a) |
| D-07 | Runner đọc `exceptions` | (a) có, cho architect, author, author_proposal, review; (b) không | (a), có điều kiện `external-smoke` xác nhận model Fable chạy được qua CLI |
| D-08 | Flyway | (1) bỏ Flyway, test nạp `sql/postgres/gld_srv_serve.pg.sql`; (2) giữ Flyway cho test, sinh từ DDL repo, test so khớp | (1) |
| D-09 | PK `srv_poi_media_gallery` | chờ probe P-b4; (a) entity `@IdClass(media_id, poi_id)` theo gold; (b) gold đổi khoá sang `media_id` (task dữ liệu) | chạy probe trước; nếu `media_id` không duy nhất thì (a) bắt buộc |
| D-10 | `srv_poi_review.source_name` (và `lang`, `source`) | (a) API bỏ cột, theo gold; (b) gold thêm cột qua `run-author --kind model`, BA xác nhận lại quyết định 03/11 | hỏi BA trước; (a) nếu không có yêu cầu ghi rõ |
| D-11 | Toolchain Java | (a) cài JDK 26 cục bộ, dùng wrapper; (b) chạy test trong image `maven:3.9-eclipse-temurin-26` | (a) |
| D-12 | Ai chạy gate runtime local | (a) user chạy compose và smoke, ghi kết quả; (b) Main chạy, user xác nhận log | (a) trong 2 task đầu, chuyển (b) khi runbook ổn định |
| D-13 | Số reviewer Codex API | (a) 3 reviewer tách; (b) 2 reviewer (`api-contract`, `java-service`) | (a) |
| D-14 | MCP PostgreSQL local cho Cursor | (a) thêm sau CT-3; (b) không | (a) |
| D-15 | Review cho task agent-system | (a) `risk-gate` một vòng cho CT-2, CT-3; (b) không reviewer, dựa test và user | (a) |
| D-16 | `TOKEN_OPTIMIZATION_PLAN.md` | (a) chuyển `docs/agent-system/archive/`; (b) xóa; (c) giữ | (b): git giữ lịch sử |
| D-17 | Gộp mẫu prompt A1–A19 | (a) gộp theo P-c1 và thêm A20; (b) giữ nguyên, chỉ thêm A20 | (a) |
| D-18 | Thứ tự CT-1 và CT-2 | (a) song song; (b) tuần tự CT-2 trước | (a) |
