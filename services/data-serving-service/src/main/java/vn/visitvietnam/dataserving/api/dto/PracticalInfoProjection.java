package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonRawValue;
import com.fasterxml.jackson.annotation.JsonValue;
import vn.visitvietnam.dataserving.service.PracticalInfoQuery;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

public final class PracticalInfoProjection {

    private PracticalInfoProjection() {
    }

    public static Map<String, Object> select(PoiPracticalInfoResponse dto, Set<PracticalInfoQuery.Field> fields) {
        Map<String, Object> out = new LinkedHashMap<>();
        for (PracticalInfoQuery.Field field : PracticalInfoQuery.Field.values()) {
            if (fields.contains(field)) {
                out.put(field.key(), value(dto, field));
            }
        }
        return out;
    }

    private static Object value(PoiPracticalInfoResponse dto, PracticalInfoQuery.Field field) {
        return switch (field) {
            case ID -> dto.id();
            case NAME -> dto.name();
            case DESCRIPTION -> dto.description();
            case TIME_TO_SPEND -> dto.timeToSpend();
            case COST -> dto.cost();
            case BEST_TIME -> dto.bestTime();
            case COVER -> dto.cover();
            case RATINGS -> dto.ratings();
            case BUSINESS_TAGS -> dto.businessTags();
            case STATUS -> dto.status();
            case OPERATING_HOURS -> dto.operatingHours();
            case HOLIDAY_EXCEPTIONS -> dto.holidayExceptions() == null ? null : new RawJson(dto.holidayExceptions());
            case ADDRESS -> dto.address();
            case GEO_LOCATION -> dto.geoLocation();
            case PHONE -> dto.phone();
            case EMAIL -> dto.email();
            case WEBSITE_URL -> dto.websiteUrl();
            case DESTINATIONS -> dto.destinations();
        };
    }

    public record RawJson(@JsonValue @JsonRawValue String json) {}
}
