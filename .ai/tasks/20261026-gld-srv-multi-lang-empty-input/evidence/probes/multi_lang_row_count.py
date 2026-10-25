# Environment: Fabric DEV. Spark session that can read lh_vv_silver.dbo.slv_enr_poi_info_multi_lang.
# Item: paste this file into one notebook cell and run it. Read-only. Do not write a table.
# Parameters: table lh_vv_silver.dbo.slv_enr_poi_info_multi_lang; incident Delta version 2.
# Steps: open a notebook that sees lh_vv_silver, paste this cell, run, copy stdout.
# Expected: current_version, row_count, deleted_at_is_null or COLUMN_ABSENT, column names,
# and the same aggregates at version 2, or version_2=UNAVAILABLE.
# Paste to: .ai/tasks/20261026-gld-srv-multi-lang-empty-input/evidence/results/multi_lang_row_count.txt
# Limits: aggregates and column names only, at most 50 lines, no personal data, no secrets.

FQ = "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang"
QUOTED = ".".join("`{0}`".format(part) for part in FQ.split("."))
INCIDENT_VERSION = 2


def emit(label, frame):
    columns = list(frame.columns)
    lower = {name.lower(): name for name in columns}
    print(label + ".columns=" + ",".join(columns))
    print(label + ".has_row_hash=" + ("yes" if "row_hash" in lower else "no"))
    print(label + ".has_deleted_at=" + ("yes" if "deleted_at" in lower else "no"))
    print(label + ".row_count=" + str(frame.count()))
    if "deleted_at" in lower:
        deleted_at = lower["deleted_at"]
        live = frame.filter(frame[deleted_at].isNull()).count()
        print(label + ".deleted_at_is_null=" + str(live))
    else:
        print(label + ".deleted_at_is_null=COLUMN_ABSENT")


if not spark.catalog.tableExists(FQ):
    print("table=ABSENT")
else:
    current_version = spark.sql("DESCRIBE HISTORY {0}".format(QUOTED)).agg({"version": "max"}).collect()[0][0]
    print("current_version={0}".format(current_version))
    current = spark.table(FQ)
    emit("current", current)
    if int(current_version) == INCIDENT_VERSION:
        print("version_2=SAME_AS_CURRENT")
    elif int(current_version) < INCIDENT_VERSION:
        print("version_2=UNAVAILABLE")
    else:
        try:
            pinned = spark.sql("SELECT * FROM {0} VERSION AS OF {1}".format(QUOTED, INCIDENT_VERSION))
            emit("version_2", pinned)
        except Exception as exc:
            print("version_2=UNAVAILABLE {0}".format(type(exc).__name__))
