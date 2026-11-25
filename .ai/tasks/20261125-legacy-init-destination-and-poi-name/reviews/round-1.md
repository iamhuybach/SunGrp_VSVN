## Review round 1

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: completed
- Verdict: `EVIDENCE_REQUIRED`

### P0/P1

- `GATE-001` — P1 — `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb:123`, `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1094`: `poi_name=NULL` có thể làm đổi toàn bộ `row_hash` nếu Fabric không bỏ trường null khi `to_json`, gây mass rewrite và chuyển ownership các dòng khớp `LEGACY_INIT`. Fix: chứng minh JSON/hash không đổi trên Fabric DEV, hoặc loại `poi_name` khỏi hash hay cố định null serialization.

P2: 1. P3: 0.

Probe: `p=spark.range(1).select(F.lit("p").alias("poi_id"),F.lit("vi").alias("lang"),F.lit("partner").alias("source_name")); r=p.select(F.to_json(F.struct("poi_id","lang","source_name")).alias("old_json"),F.to_json(F.struct("poi_id","lang",F.lit(None).cast("string").alias("poi_name"),"source_name")).alias("new_json"),F.sha2(F.to_json(F.struct("poi_id","lang","source_name")),256).alias("old_hash"),F.sha2(F.to_json(F.struct("poi_id","lang",F.lit(None).cast("string").alias("poi_name"),"source_name")),256).alias("new_hash")).first(); print("spark.sql.jsonGenerator.ignoreNullFields=",spark.conf.get("spark.sql.jsonGenerator.ignoreNullFields","<unset>"),r.asDict()); assert r.old_json==r.new_json and r.old_hash==r.new_hash`
