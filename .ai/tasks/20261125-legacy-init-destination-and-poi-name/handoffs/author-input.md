# Author input

## User comments

Sửa dữ liệu Dev và init Prod do người dùng chạy. Runbook có tham số workspace đích, thứ tự sửa dòng LEGACY_INIT đang có, và cách kiểm destination_id là chuỗi JSON mảng cùng poi_name theo lang. Không chạy notebook trên Fabric trong chat này.

Notebook init nhận workspace đích bằng tham số. Không gắn cứng sgr_visitvn_dev. Không đoán tên workspace Prod. Nguồn gold cũ giữ workspace đang có trong notebook.

## Files and anchors

- .ai/tasks/20261125-legacy-init-destination-and-poi-name/architecture.md — Main brief, Rollout, Rollback and forward recovery, Verification
- notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb — id:lgpparams, id:lgpconst
- notebooks/NB_CREATE_DDL.ipynb — id:lgpnamepy, id:legacyidpy
- sql/postgres/gld_srv_serve.pg.sql — comment ALTER poi_name
- decision.md — D-02, D-03, D-04, D-05, D-07

## Constraints

Dev target workspace is sgr_visitvn_dev (D-03). Prod workspace is `<CẦN NGƯỜI DÙNG CUNG CẤP>`. Do not guess it. p_mode is PLAN then RUN. p_pin_json comes from the prior init summary or log; if absent, say the user supplies it. Do not invent a pin. Old gold workspace stays sgr_visitvn_prd_batch. Order on Dev: PostgreSQL ALTER, lgpnamepy, service deploy, PLAN, then RUN that updates existing LEGACY_INIT rows, then checks (a) through (e) in Verification. A second RUN must insert 0 rows and must not change poi_id. If destination.decision is USER_DECISION, stop and report shape, stop_n, conflict_n, and the samples. No personal data. At most 50 rows.
