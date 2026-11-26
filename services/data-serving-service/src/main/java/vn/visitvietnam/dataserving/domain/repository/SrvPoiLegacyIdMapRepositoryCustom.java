package vn.visitvietnam.dataserving.domain.repository;

import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;

import java.util.Collection;
import java.util.List;

public interface SrvPoiLegacyIdMapRepositoryCustom {

    /** Một poi_id cũ resolve được và poi_id mới của nó. */
    record Resolution(String legacyPoiId, String poiId) {}

    /** Một trang dòng srv_poi_info theo thứ tự SQL và tổng số dòng khớp. */
    record PracticalInfoSlice(List<SrvPoiInfo> rows, long total) {}

    /** Cột sort cho trang practical info. Text SQL chỉ lấy từ hằng này. */
    enum SortColumn {
        POI_ID("i.poi_id"),
        POI_NAME("i.poi_name"),
        RATING_OVERALL("i.rating_overall"),
        RATING_COUNT("i.rating_count");

        private final String sql;

        SortColumn(String sql) {
            this.sql = sql;
        }

        public String sql() {
            return sql;
        }
    }

    List<Resolution> findResolvable(Collection<String> ids);

    /** ids rỗng và poiName trắng thì trả trang rỗng; có cả hai thì hợp hai tập. */
    PracticalInfoSlice findPracticalInfoPage(Collection<String> ids, String source, String poiName,
            SortColumn sort, boolean descending, int limit, long offset);
}
