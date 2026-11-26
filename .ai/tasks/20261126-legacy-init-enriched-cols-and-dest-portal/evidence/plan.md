# Evidence plan

## Decision to resolve

`ai_enriched_poi` column names and gaps G1–G3 are observed in `evidence/results/p_gaps.txt`. `D-INIT-KEY`, `D-INIT-INFO-VI`, and `D-INIT-ENRICH-ONLY` are recorded. `D-DEST-BACKFILL`, `D-LEGACY-DEST`, and G4 remain open user choices.

## Existing evidence

- Gold types in `NB_SETUP_INITIAL_DDL` `TABLE_SPECS`: `old_address` STRING, `price_level` INT, `price_min` DECIMAL(18,2), `price_max` DECIMAL(18,2), `story` STRING, `local_tips` STRING. `gld_srv_poi_multi_lang` grain is `(poi_id, lang)`.
- `docs/context/mapping_gld_srv_poi_info.md` already states the six columns are gold-only.
- `NB_SETUP_LEGACY_GOLD_POI` reads legacy gold from `sgr_visitvn_prd_batch.lh_vv_gold.dbo` (`OLD`). It does not define `ai_enriched_poi`.
- `docs/context/mapping_legacy_ai_product.md` names only `ai_enriched_poi.source_id`.
- Destination payload keys `id` and `strapi_document_id` are a user decision in `request.md`. Current extract schema is `array<struct<id:string,name:string>>`. No destination probe in this phase.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| ai_enriched_poi_schema | Fabric DEV, done | Column names on `ai_enriched_poi` | Result saved | evidence/results/ai_enriched_poi_schema.txt |
| p_gaps | Fabric DEV workspace `sgr_visitvn_dev`, one read-only Python cell | G1 replay counts, G2 legacy-id counts, G3 legacy destination id space. Sections `P-DEST-1`, `P-DEST-2`, `P-AI-1`, `P-AI-2`, `P-LEGDEST-1`, `P-LEGDEST-2` | Six `SECTION` and six `END` lines. A section `ERROR` is a fail for that section | evidence/results/p_gaps.txt |

Architecture `EVIDENCE_REQUIRED`, gaps G1–G3, run as one script. G4 is a scope choice, not a probe. `<ws>` is `sgr_visitvn_dev`. `P-DEST-2` sends one backslash to Spark `RLIKE` so `\s` matches whitespace. The architecture markdown stored two.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise. The table is the legacy catalog the init notebook already reads.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts. Print names, types, and counts only.
