# Repository context

The reviewed control-table contract is [`CTRL_TABLES_CONTEXT.md`](CTRL_TABLES_CONTEXT.md).

Start with [`00_README.md`](00_README.md). The rest of this directory is the Visit Vietnam POI context pack: data model, naming, notebook notes, pain points, and the read-only Fabric script `CHECK_CTRL_SNAPSHOT.py`.

Counts under "Dữ liệu hiện có" come from logs through 05/10/2026. Refresh them by running `CHECK_CTRL_SNAPSHOT.py` in Fabric DEV (default lakehouse `lh_vv_bronze`) and do not paste personal data back into the repository.

The pack matches `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` and `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/` as aligned on 08/10/2026. The flow lock expires from `lock_at` plus the caller's timeout. FL_00 calls only `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` with `partner_raw_data` fixed in the activity parameters.

A task that changes `ctrl_*` reads, writes, locks, watermarks, logging, or recovery still needs an evidence plan when this contract does not already answer the question.
