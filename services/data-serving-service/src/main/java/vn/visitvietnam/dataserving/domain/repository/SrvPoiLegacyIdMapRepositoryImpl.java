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

    /** Tập poi_id từ ids: id cũ resolve qua hit, còn lại giữ nguyên. Cần HIT_CTE và :ids. */
    static final String ID_SET = """
            SELECT COALESCE(h.poi_id, u.id)
                    FROM unnest(CAST(:ids AS text[])) AS u(id)
                    LEFT JOIN hit h ON h.legacy_poi_id = u.id""";

    /** Tập poi_id khớp tên. :namePattern lấy từ containsPattern. */
    static final String NAME_SET = """
            SELECT n.poi_id
                    FROM apps.srv_poi_info n
                    WHERE lower(n.poi_name) LIKE lower(:namePattern) ESCAPE '!'""";

    /** Cách chọn POI. Chỉ ids, chỉ tên, hoặc hợp cả hai. */
    enum Selection { IDS, NAME, IDS_OR_NAME }

    static final String DEFAULT_ORDER_BY = "i.poi_id ASC";

    static final Map<Selection, String> COUNT_SQL;
    static final Map<Selection, String> DEFAULT_PAGE_SQL;
    static final Map<Selection, Map<SortColumn, String>> ASC_PAGE_SQL;
    static final Map<Selection, Map<SortColumn, String>> DESC_PAGE_SQL;

    static {
        Map<Selection, String> count = new EnumMap<>(Selection.class);
        Map<Selection, String> def = new EnumMap<>(Selection.class);
        Map<Selection, Map<SortColumn, String>> ascAll = new EnumMap<>(Selection.class);
        Map<Selection, Map<SortColumn, String>> descAll = new EnumMap<>(Selection.class);
        for (Selection selection : Selection.values()) {
            count.put(selection, withClause(selection) + "SELECT count(*) " + fromClause(selection));
            def.put(selection, pageSql(selection, DEFAULT_ORDER_BY));
            Map<SortColumn, String> asc = new EnumMap<>(SortColumn.class);
            Map<SortColumn, String> desc = new EnumMap<>(SortColumn.class);
            for (SortColumn column : SortColumn.values()) {
                asc.put(column, pageSql(selection, column.sql() + " ASC NULLS LAST, i.poi_id ASC"));
                desc.put(column, pageSql(selection, column.sql() + " DESC NULLS LAST, i.poi_id ASC"));
            }
            ascAll.put(selection, Collections.unmodifiableMap(asc));
            descAll.put(selection, Collections.unmodifiableMap(desc));
        }
        COUNT_SQL = Collections.unmodifiableMap(count);
        DEFAULT_PAGE_SQL = Collections.unmodifiableMap(def);
        ASC_PAGE_SQL = Collections.unmodifiableMap(ascAll);
        DESC_PAGE_SQL = Collections.unmodifiableMap(descAll);
    }

    @PersistenceContext
    private EntityManager entityManager;

    static String withClause(Selection selection) {
        return selection == Selection.NAME ? "" : "WITH " + HIT_CTE;
    }

    static String fromClause(Selection selection) {
        String selector = switch (selection) {
            case IDS -> "i.poi_id = ANY (ARRAY(\n        " + ID_SET + "))";
            case NAME -> "lower(i.poi_name) LIKE lower(:namePattern) ESCAPE '!'";
            case IDS_OR_NAME -> "i.poi_id IN (\n        " + ID_SET + "\n        UNION\n        " + NAME_SET + ")";
        };
        return "FROM apps.srv_poi_info i\nWHERE " + selector + "\n"
                + "  AND i.deleted_at IS NULL\n"
                + "  AND (:source = '' OR lower(trim(i.source_name)) = :source)\n";
    }

    static String pageSql(Selection selection, String orderBy) {
        return withClause(selection) + "SELECT {i.*}, count(*) OVER () AS total_items " + fromClause(selection)
                + "ORDER BY " + orderBy + " LIMIT :limit OFFSET :offset";
    }

    /** null khi không có selector nào. */
    static Selection selection(String[] ids, String pattern) {
        boolean byId = ids.length > 0;
        boolean byName = !pattern.isEmpty();
        if (byId && byName) {
            return Selection.IDS_OR_NAME;
        }
        if (byId) {
            return Selection.IDS;
        }
        return byName ? Selection.NAME : null;
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
        String pattern = containsPattern(poiName);
        Selection selection = selection(array, pattern);
        if (selection == null) {
            return new PracticalInfoSlice(List.of(), 0);
        }
        String sourceValue = source == null ? "" : source.trim().toLowerCase(Locale.ROOT);
        String sql = sort == null
                ? DEFAULT_PAGE_SQL.get(selection)
                : (descending ? DESC_PAGE_SQL : ASC_PAGE_SQL).get(selection).get(sort);
        NativeQuery<?> page = entityManager.createNativeQuery(sql).unwrap(NativeQuery.class);
        page.addEntity("i", SrvPoiInfo.class);
        page.addScalar("total_items", StandardBasicTypes.LONG);
        bind(page, selection, array, sourceValue, pattern);
        page.setParameter("limit", limit);
        page.setParameter("offset", offset);
        List<?> rows = page.getResultList();
        if (rows.isEmpty()) {
            long total = offset == 0 ? 0 : count(selection, array, sourceValue, pattern);
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

    private long count(Selection selection, String[] ids, String source, String pattern) {
        NativeQuery<?> query = entityManager.createNativeQuery(COUNT_SQL.get(selection)).unwrap(NativeQuery.class);
        bind(query, selection, ids, source, pattern);
        return ((Number) query.getSingleResult()).longValue();
    }

    /** Chỉ bind tham số có trong SQL của selection; Hibernate từ chối tên tham số lạ. */
    private static void bind(NativeQuery<?> query, Selection selection, String[] ids, String source, String pattern) {
        if (selection != Selection.NAME) {
            query.setParameter("ids", ids, String[].class);
        }
        if (selection != Selection.IDS) {
            query.setParameter("namePattern", pattern);
        }
        query.setParameter("source", source);
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
