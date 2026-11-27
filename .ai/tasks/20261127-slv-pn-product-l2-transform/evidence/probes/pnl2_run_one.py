# Fabric DEV. Một node, DRY_RUN. In lỗi đầy đủ nếu notebook không vào được run_node.
# Log ctrl trống nghĩa là notebook chưa chạy tới lib.

args = {
    "p_exec_id": "",
    "p_run_id": "",
    "p_pl_name": "",
    "p_trg_fq": "",
    "p_pinned_json": "",
    "p_mode": "DRY_RUN",
    "p_force": "false",
    "p_history_limit": "1000",
    "useRootDefaultLakehouse": True,
}
try:
    print(notebookutils.notebook.run("NB_SLV_PN_PRODUCT_SALE", 14400, args))
except Exception as exc:
    print(type(exc).__name__)
    print(str(exc)[:2000])
