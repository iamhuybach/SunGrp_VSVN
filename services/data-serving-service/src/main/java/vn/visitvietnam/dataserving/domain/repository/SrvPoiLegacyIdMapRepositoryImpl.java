package vn.visitvietnam.dataserving.domain.repository;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.hibernate.query.NativeQuery;
import org.hibernate.type.StandardBasicTypes;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.EnumMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

public class SrvPoiLegacyIdMapRepositoryImpl implements SrvPoiLegacyIdMapRepositoryCustom {

    /** Quy tắc resolve I1. Đây là định nghĩa SQL duy nhất. */
    public static final String HIT_CTE = """
            hit AS (
              SELECT m.legacy_poi_id, m.poi_id
              FROM apps.srv_poi_legacy_id_map m
              WHERE m.legacy_poi_id = ANY (CAST(:ids AS text[]))
                AND m.poi_id_status = 'OK'
                AND m.poi_id IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM apps.srv_poi_info x WHERE x.poi_id = m.legacy_poi_id)
            )
            """;

    public static final String RESOLVE_SQL = "WITH " + HIT_CTE + "SELECT h.legacy_poi_id, h.poi_id FROM hit h";

    public static final String PRACTICAL_INFO_FROM = """
            FROM apps.srv_poi_info i
            WHERE i.poi_id = ANY (ARRAY(
                    SELECT COALESCE(h.poi_id, u.id)
                    FROM unnest(CAST(:ids AS text[])) AS u(id)
                    LEFT JOIN hit h ON h.legacy_poi_id = u.id))
              AND i.deleted_at IS NULL
              AND (:source = '' OR lower(trim(i.source_name)) = :source)
              AND (:namePattern = '' OR lower(i.poi_name) LIKE lower(:namePattern) ESCAPE '!')
            """;

    public static final String PRACTICAL_INFO_COUNT_SQL = "WITH " + HIT_CTE + "SELECT count(*) " + PRACTICAL_INFO_FROM;

    static final String DEFAULT_ORDER_BY = "i.poi_id ASC";

    static final String DEFAULT_PAGE_SQL = pageSql(DEFAULT_ORDER_BY);

    static final Map<SortColumn, String> ASC_PAGE_SQL;

    static final Map<SortColumn, String> DESC_PAGE_SQL;

    static {
        Map<SortColumn, String> asc = new EnumMap<>(SortColumn.class);
        Map<SortColumn, String> desc = new EnumMap<>(SortColumn.class);
        for (SortColumn column : SortColumn.values()) {
            asc.put(column, pageSql(column.sql() + " ASC NULLS LAST, i.poi_id ASC"));
            desc.put(column, pageSql(column.sql() + " DESC NULLS LAST, i.poi_id ASC"));
        }
        ASC_PAGE_SQL = Collections.unmodifiableMap(asc);
        DESC_PAGE_SQL = Collections.unmodifiableMap(desc);
    }

    @PersistenceContext
    private EntityManager entityManager;

    static String pageSql(String orderBy) {
        return "WITH " + HIT_CTE + "SELECT {i.*}, count(*) OVER () AS total_items " + PRACTICAL_INFO_FROM
                + "ORDER BY " + orderBy + " LIMIT :limit OFFSET :offset";
    }

    @Override
    public List<Resolution> findResolvable(Collection<String> ids) {
        String[] array = distinctNonBlank(ids);
        if (array.length == 0) {
            return List.of();
        }
        NativeQuery<?> query = entityManager.createNativeQuery(RESOLVE_SQL).unwrap(NativeQuery.class);
        query.setParameter("ids", array, String[].class);
        List<?> rows = query.getResultList();
        List<Resolution> out = new ArrayList<>(rows.size());
        for (Object row : rows) {
            Object[] cols = (Object[]) row;
            out.add(new Resolution((String) cols[0], (String) cols[1]));
        }
        return out;
    }

    @Override
    public PracticalInfoSlice findPracticalInfoPage(Collection<String> ids, String source, String poiName,
            SortColumn sort, boolean descending, int limit, long offset) {
        String[] array = distinctNonBlank(ids);
        if (array.length == 0) {
            return new PracticalInfoSlice(List.of(), 0);
        }
        String sourceValue = source == null ? "" : source.trim().toLowerCase(Locale.ROOT);
        String pattern = containsPattern(poiName);
        String sql = sort == null ? DEFAULT_PAGE_SQL : (descending ? DESC_PAGE_SQL : ASC_PAGE_SQL).get(sort);
        NativeQuery<?> page = entityManager.createNativeQuery(sql).unwrap(NativeQuery.class);
        page.addEntity("i", SrvPoiInfo.class);
        page.addScalar("total_items", StandardBasicTypes.LONG);
        bind(page, array, sourceValue, pattern);
        page.setParameter("limit", limit);
        page.setParameter("offset", offset);
        List<?> rows = page.getResultList();
        if (rows.isEmpty()) {
            long total = offset == 0 ? 0 : count(array, sourceValue, pattern);
            return new PracticalInfoSlice(List.of(), total);
        }
        List<SrvPoiInfo> infos = new ArrayList<>(rows.size());
        long total = 0;
        for (Object row : rows) {
            Object[] cols = (Object[]) row;
            infos.add((SrvPoiInfo) cols[0]);
            total = ((Number) cols[1]).longValue();
        }
        return new PracticalInfoSlice(infos, total);
    }

    private long count(String[] ids, String source, String pattern) {
        NativeQuery<?> query = entityManager.createNativeQuery(PRACTICAL_INFO_COUNT_SQL).unwrap(NativeQuery.class);
        bind(query, ids, source, pattern);
        return ((Number) query.getSingleResult()).longValue();
    }

    private static void bind(NativeQuery<?> query, String[] ids, String source, String pattern) {
        query.setParameter("ids", ids, String[].class);
        query.setParameter("source", source);
        query.setParameter("namePattern", pattern);
    }

    private static String[] distinctNonBlank(Collection<String> ids) {
        if (ids == null) {
            return new String[0];
        }
        Set<String> out = new LinkedHashSet<>();
        for (String id : ids) {
            if (id != null && !id.isBlank()) {
                out.add(id);
            }
        }
        return out.toArray(String[]::new);
    }

    static String containsPattern(String raw) {
        if (raw == null || raw.isBlank()) {
            return "";
        }
        StringBuilder escaped = new StringBuilder(raw.length() + 2).append('%');
        for (int k = 0; k < raw.length(); k++) {
            char c = raw.charAt(k);
            if (c == '!' || c == '%' || c == '_') {
                escaped.append('!');
            }
            escaped.append(c);
        }
        return escaped.append('%').toString();
    }
}
