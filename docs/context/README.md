# Repository context

The reviewed control-table contract is [`CTRL_TABLES_CONTEXT.md`](CTRL_TABLES_CONTEXT.md).

Start with [`00_README.md`](00_README.md). The rest of this directory is the Visit Vietnam POI context pack: data model, naming, notebook notes, pain points, and the read-only Fabric script `CHECK_CTRL_SNAPSHOT.py`.

Counts under "Dữ liệu hiện có" come from logs through 05/10/2026. Refresh them by running `CHECK_CTRL_SNAPSHOT.py` in Fabric DEV (default lakehouse `lh_vv_bronze`) and do not paste personal data back into the repository.

Import review notes for 08/10/2026 are in `.ai/tasks/20261008-import-context-pack/decision.md`. Two points to keep in mind before changing code:

- `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` still expires a flow lock with the caller's timeout. The context describes the later `LOCK_EXPIRES_AT` rule.
- `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/` has no Switch and calls `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`. The context describes the later ForEach → Switch design.

A task that changes `ctrl_*` reads, writes, locks, watermarks, logging, or recovery still needs an evidence plan when this contract does not already answer the question.
