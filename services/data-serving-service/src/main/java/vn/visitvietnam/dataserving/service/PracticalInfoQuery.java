package vn.visitvietnam.dataserving.service;

import org.springframework.data.domain.Sort;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiLegacyIdMapRepositoryCustom.SortColumn;

import java.util.EnumSet;
import java.util.List;

public record PracticalInfoQuery(
        List<String> ids,
        EnumSet<Field> fields,
        String source,
        String poiName,
        String lang,
        int page,
        int size,
        SortField sortField,
        Sort.Direction direction
) {
    public static final String FIELD_REGEX = "^(id|name|description|time_to_spend|cost|best_time|cover|ratings"
            + "|business_tags|status|operating_hours|holiday_exceptions|address|geo_location|phone|email"
            + "|website_url|destinations)$";
    public static final String SORT_REGEX = "^(id|name|ratings_avg_score|ratings_count)?$";

    public enum Field {
        ID("id"),
        NAME("name"),
        DESCRIPTION("description"),
        TIME_TO_SPEND("time_to_spend"),
        COST("cost"),
        BEST_TIME("best_time"),
        COVER("cover"),
        RATINGS("ratings"),
        BUSINESS_TAGS("business_tags"),
        STATUS("status"),
        OPERATING_HOURS("operating_hours"),
        HOLIDAY_EXCEPTIONS("holiday_exceptions"),
        ADDRESS("address"),
        GEO_LOCATION("geo_location"),
        PHONE("phone"),
        EMAIL("email"),
        WEBSITE_URL("website_url"),
        DESTINATIONS("destinations");

        private final String key;

        Field(String key) {
            this.key = key;
        }

        public String key() {
            return key;
        }

        public static Field byKey(String key) {
            for (Field field : values()) {
                if (field.key.equals(key)) {
                    return field;
                }
            }
            throw new IllegalArgumentException(key);
        }
    }

    public enum SortField {
        ID("id", SortColumn.POI_ID),
        NAME("name", SortColumn.POI_NAME),
        RATINGS_AVG_SCORE("ratings_avg_score", SortColumn.RATING_OVERALL),
        RATINGS_COUNT("ratings_count", SortColumn.RATING_COUNT);

        private final String key;
        private final SortColumn column;

        SortField(String key, SortColumn column) {
            this.key = key;
            this.column = column;
        }

        public String key() {
            return key;
        }

        public SortColumn column() {
            return column;
        }

        public static SortField byKey(String key) {
            for (SortField field : values()) {
                if (field.key.equals(key)) {
                    return field;
                }
            }
            throw new IllegalArgumentException(key);
        }
    }
}
