# Fabric DEV. Chỉ chạy 3 node. R1 và 5 cạnh đã có trên DEV (2026-11-27).
# Notebook tạm có lakehouse mặc định khác node, nên phải truyền useRootDefaultLakehouse.
# Cell này không %run lib. Timeout 14400 giây.

NOTEBOOK_TIMEOUT_SEC = 14400
NODES = ("NB_SLV_PN_PRODUCT_SALE", "NB_SLV_PN_HOTEL_ROOM_OFFER", "NB_SLV_PN_HOTEL_RATE_OFFER")
TARGETS = ("slv_pn_product_sale", "slv_pn_hotel_room_offer", "slv_pn_hotel_rate_offer")


def run_nb(nb, args):
    payload = dict(args)
    payload["useRootDefaultLakehouse"] = True
    try:
        print(nb, notebookutils.notebook.run(nb, NOTEBOOK_TIMEOUT_SEC, payload))
    except Exception as exc:
        print(nb, "FAIL", type(exc).__name__, str(exc)[:2000])


base = {
    "p_exec_id": "", "p_run_id": "", "p_pl_name": "", "p_trg_fq": "",
    "p_pinned_json": "", "p_history_limit": "1000",
}
print("== DRY_RUN")
dry = dict(base)
dry["p_mode"] = "DRY_RUN"
dry["p_force"] = "false"
for nb in NODES:
    run_nb(nb, dry)

print("== RUN")
run = dict(base)
run["p_mode"] = "RUN"
run["p_force"] = "false"
for nb in NODES:
    run_nb(nb, run)

print("== exists")
for name in TARGETS:
    print(name, spark.catalog.tableExists("lh_vv_silver.dbo." + name))

spark.sql("""
SELECT trg_tbl, status, started_at, inserted_rows, updated_rows, deactivated_rows, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
ORDER BY started_at DESC
LIMIT 20
""").show(20, truncate=False)
