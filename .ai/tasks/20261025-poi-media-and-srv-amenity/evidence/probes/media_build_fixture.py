# Fabric DEV. In-memory only. No table writes. No personal data. Synthetic urls stay in the session and are not printed.
# Cell 1: %run NB_LIB_TRANSFORM_SLV_GLD
# Cell 2: paste only the code cell slvmediabuild from NB_SLV_POI_MEDIA_INFO. Do not run the node.
# Cell 3: paste this file.
# Save stdout to evidence/results/media_build_fixture.txt.
# Pass: every line F1-F11 is PASS and the last line is fixture_fail 0.
# F7 follows decision A8: two null orders still have one cover, the row at _pos 0.

from pyspark.sql import types as T

I18N_SCHEMA = T.StructType([
    T.StructField("business_service_id", T.StringType()),
    T.StructField("locale", T.StringType()),
    T.StructField("media", T.StringType()),
    T.StructField("deleted", T.BooleanType()),
])
SVC_SCHEMA = T.StructType([
    T.StructField("id", T.StringType()),
    T.StructField("media", T.StringType()),
    T.StructField("deleted", T.BooleanType()),
])
fails = []


class _Ctx:
    def __init__(self):
        self.warns = {}
        self.metrics = {}

    def warn(self, name, n):
        self.warns[name] = int(n or 0)


def _i18n(rows):
    return spark.createDataFrame(rows, I18N_SCHEMA)


def _svc(rows):
    return spark.createDataFrame(rows, SVC_SCHEMA)


def _run(i18n_rows, svc_rows):
    ctx = _Ctx()
    out = with_cover(partner_media(_i18n(i18n_rows), _svc(svc_rows), ctx))
    rows = out.select("display_order", "is_cover", "_pos").collect()
    return rows, ctx


def _check(name, ok):
    print(name, "PASS" if ok else "FAIL")
    if not ok:
        fails.append(name)


one = '[{"url":"http://example/a","order":2},{"url":"http://example/b","order":1}]'
rows, ctx = _run([("s1", "vi", one, False)], [])
covers = [r for r in rows if r.is_cover]
_check("F1", len(rows) == 2 and len(covers) == 1 and covers[0].display_order == 1)

svc_one = '[{"url":"http://example/s","order":3}]'
rows, ctx = _run([("s2", "vi", "[]", False)], [("s2", svc_one, False)])
_check("F2", len(rows) == 1 and ctx.metrics.get("partner_fallback_docs") == 1)

rows, ctx = _run([("s3", "vi", "null", False)], [("s3", None, False)])
_check("F3", len(rows) == 0)

rows, ctx = _run(
    [("s4", "vi", None, False), ("s5", "vi", "  ", False)],
    [("s4", svc_one, False), ("s5", svc_one, False)],
)
_check("F4", len(rows) == 2 and ctx.metrics.get("partner_fallback_docs") == 2)

blank_urls = '[{"url":null,"order":1},{"url":"  ","order":2}]'
rows, ctx = _run([("s6", "vi", blank_urls, False)], [])
_check("F5", len(rows) == 0 and ctx.warns.get("partner_url_dropped") == 2)

rows, ctx = _run([("s7", "vi", '[{"url":"http://example/c","order":null}]', False)], [])
_check("F6", len(rows) == 1 and rows[0].is_cover and rows[0].display_order is None)

two_null = '[{"url":"http://example/d","order":null},{"url":"http://example/e","order":null}]'
rows, ctx = _run([("s8", "vi", two_null, False)], [])
cover_pos = [r._pos for r in rows if r.is_cover]
_check("F7", len(rows) == 2 and cover_pos == [0] and all(r.display_order is None for r in rows))

tie = '[{"url":"http://example/f","order":1},{"url":"http://example/g","order":1}]'
rows, ctx = _run([("s9", "vi", tie, False)], [])
cover_pos = [r._pos for r in rows if r.is_cover]
_check("F8", len(rows) == 2 and cover_pos == [0] and all(r.display_order == 1 for r in rows))

kept = '[{"url":"http://example/h","order":4}]'
rows, ctx = _run(
    [("gone", "vi", kept, True), ("empty", "vi", None, False), ("keep", "vi", kept, None)],
    [("empty", kept, True)],
)
_check("F9", len(rows) == 1 and rows[0].display_order == 4 and rows[0].is_cover)

rows, ctx = _run([("s10", "vi", '{"url":"x"}', False)], [("s10", svc_one, False)])
_check("F10", len(rows) == 0 and ctx.warns.get("partner_media_unparsed") == 1 and ctx.metrics.get("partner_fallback_docs") == 0)

tie_schema = T.StructType([
    T.StructField("media_id", T.StringType()),
    T.StructField("poi_id", T.StringType()),
    T.StructField("display_order", T.IntegerType()),
    T.StructField("_pos", T.IntegerType()),
])
base = spark.createDataFrame([("b", "p", 1, None), ("a", "p", 1, None)], tie_schema)


def _keys(df):
    return sorted((r.media_id, bool(r.is_cover)) for r in df.select("media_id", "is_cover").collect())


wide = _keys(with_cover(base.repartition(7)))
narrow = _keys(with_cover(base.coalesce(1)))
_check("F11", wide == narrow == [("a", True), ("b", False)])

print("fixture_fail", len(fails))
if fails:
    raise RuntimeError("fixture FAIL " + ",".join(fails))
