# Evidence plan

## Decision to resolve

`SPARK-001` (P1, review round 1): whether one `NB_GLD_SRV_POI_INFO` build scans `slv_poi_media_info` more than once because `_cover` counts covers before the same media plan is used for the join and `cover_matched`.

## Existing evidence

Local verification passed (`verification/verify.log`, 2026-11-09). No Fabric DEV run of the cover build exists.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `evidence/probes/spark-001-media-scan.md` | Fabric DEV | How many Spark jobs in one forced `DRY_RUN` read `slv_poi_media_info`, and what are scan bytes, shuffle, spill, peak memory, wall time, and node time? | Not reproduced: exactly one input scan of `slv_poi_media_info` and spill 0 on the jobs that read it. Reproduced: two or more scans of that table, or spill bytes greater than 0 on a job that reads it. | `evidence/results/spark-001-media-scan.md` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
