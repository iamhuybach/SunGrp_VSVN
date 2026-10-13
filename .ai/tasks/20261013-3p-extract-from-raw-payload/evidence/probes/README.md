# Probes for `20261013-3p-extract-from-raw-payload`

Run in Fabric DEV, read only. Save sanitized stdout under `evidence/results/`. At most 50 sample rows. No payload values, personal data, or secrets. Enum tokens and JSON key names are allowed.

| File | Result |
|---|---|
| `P1_bronze_payload.py` | `evidence/results/P1_bronze_payload.md` |
| `P2_raw_key_types.py` | `evidence/results/P2_raw_key_types.md` |
| `P3_column_equivalence.py` | `evidence/results/P3_column_equivalence.md` |
| `P4_child_keys.py` | `evidence/results/P4_child_keys.md` |
| `P5_enum_periods.py` | `evidence/results/P5_enum_periods.md` |
| `P6_consumers.sql` | `evidence/results/P6_consumers.md` |

`P6` also needs the workspace notebook and schedule list described in `architecture.md` §17.
