# Author input — runtime runbook

Notebook: `notebooks/NB_SETUP_INITIAL_DDL.ipynb`. Parameter cell `init_param`: `p_apply = "false"`. Apply only when the operator sets `p_apply = "true"`.

Environment for R1–R5: empty Fabric env the user provides. Lakehouses `lh_vv_bronze`, `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold`, each with schema `dbo`, no tables, no schedules. Do not guess workspace or capacity ids.

R6 is DEV, plan only: `p_apply = "false"`. Never apply on DEV.

Steps are architecture §14 R1–R6 and the count SQL in that section. Rollback is architecture §15. No `ctrl_log_run` row is written (architecture §12). Watermark check is the two source rows in `WATERMARK_ROWS`, not edge watermarks.

Paste sanitized results (≤ 50 rows, no personal data, no secrets) into `Kết quả người dùng ghi nhận`.
