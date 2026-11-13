package vn.visitvietnam.dataserving.service.util;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import vn.visitvietnam.dataserving.api.dto.PoiFeatureResponse;

import java.util.ArrayList;
import java.util.List;

/**
 * Đọc JSON đang lưu trong cột text. Lỗi cú pháp chỉ làm rỗng đúng field đó.
 */
public final class StoredJsonParser {

    private static final Logger log = LoggerFactory.getLogger(StoredJsonParser.class);
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private StoredJsonParser() {
    }

    public record LabelValue(String label, String value) {}

    public record ExperienceDraft(String title, String description, String keyword) {}

    public static List<PoiFeatureResponse.OperatingHour> operatingHours(String poiId, String raw) {
        if (raw == null) {
            return null;
        }
        JsonNode node = read(poiId, "operating_hours", raw);
        if (node == null || node.isNull()) {
            return null;
        }
        if (!node.isArray()) {
            warn(poiId, "operating_hours", "NOT_ARRAY");
            return null;
        }
        List<PoiFeatureResponse.OperatingHour> hours = new ArrayList<>();
        for (JsonNode element : node) {
            if (!element.isObject() || !element.hasNonNull("day_of_week")
                    || !element.has("is_open_all_day") || !element.get("is_open_all_day").isBoolean()
                    || !element.has("is_closed") || !element.get("is_closed").isBoolean()) {
                warn(poiId, "operating_hours", "BAD_ELEMENT");
                continue;
            }
            hours.add(new PoiFeatureResponse.OperatingHour(
                    element.get("day_of_week").asInt(),
                    textOrNull(element.get("open_time")),
                    textOrNull(element.get("close_time")),
                    element.get("is_open_all_day").asBoolean(),
                    element.get("is_closed").asBoolean()
            ));
        }
        return hours;
    }

    public static LabelValue labelValue(String poiId, String field, String raw) {
        if (raw == null) {
            return null;
        }
        JsonNode node = read(poiId, field, raw);
        if (node == null || node.isNull()) {
            return null;
        }
        if (!node.isObject() || node.size() != 1) {
            warn(poiId, field, "NOT_OBJECT");
            return null;
        }
        var entry = node.fields().next();
        if (!entry.getValue().isTextual()) {
            warn(poiId, field, "BAD_ELEMENT");
            return null;
        }
        return new LabelValue(entry.getKey(), entry.getValue().asText());
    }

    public static List<ExperienceDraft> experiences(String poiId, String raw) {
        if (raw == null) {
            return List.of();
        }
        JsonNode node = read(poiId, "experience", raw);
        if (node == null || node.isNull()) {
            return List.of();
        }
        if (!node.isArray()) {
            warn(poiId, "experience", "NOT_ARRAY");
            return List.of();
        }
        List<ExperienceDraft> items = new ArrayList<>();
        for (JsonNode element : node) {
            if (items.size() == 3) {
                break;
            }
            if (!element.isObject()) {
                continue;
            }
            String title = textOrNull(element.get("title"));
            String description = textOrNull(element.get("description"));
            if ((title == null || title.isBlank()) && (description == null || description.isBlank())) {
                continue;
            }
            items.add(new ExperienceDraft(title, description, textOrNull(element.get("keyword"))));
        }
        return items;
    }

    /**
     * Giữ nguyên text khi chuỗi là đúng một giá trị JSON. Token thừa hoặc JSON hỏng thì null.
     */
    public static String singleJsonValueOrNull(String poiId, String raw) {
        if (raw == null) {
            return null;
        }
        try (JsonParser parser = OBJECT_MAPPER.getFactory().createParser(raw)) {
            if (parser.nextToken() == null) {
                warn(poiId, "holiday_exceptions", "INVALID_JSON");
                return null;
            }
            parser.skipChildren();
            if (parser.nextToken() != null) {
                warn(poiId, "holiday_exceptions", "INVALID_JSON");
                return null;
            }
            return raw;
        } catch (Exception ex) {
            warn(poiId, "holiday_exceptions", "INVALID_JSON");
            return null;
        }
    }

    private static JsonNode read(String poiId, String field, String raw) {
        try {
            return OBJECT_MAPPER.readTree(raw);
        } catch (Exception ex) {
            warn(poiId, field, "INVALID_JSON");
            return null;
        }
    }

    private static String textOrNull(JsonNode node) {
        if (node == null || node.isNull()) {
            return null;
        }
        if (!node.isTextual()) {
            return null;
        }
        return node.asText();
    }

    private static void warn(String poiId, String field, String reason) {
        log.warn("stored_json_parse_failed poi_id={} field={} reason={}", poiId, field, reason);
    }
}
