package vn.visitvietnam.dataserving.service.util;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Tiện ích bóc tách danh sách subcategory tags từ định dạng JSON array hoặc chuỗi CSV.
 */
public final class SubcategoryTagsParser {

    private static final Logger log = LoggerFactory.getLogger(SubcategoryTagsParser.class);
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private SubcategoryTagsParser() {
        // static utility class
    }

    public static List<String> parse(String rawTags) {
        if (rawTags == null || rawTags.isBlank()) {
            return Collections.emptyList();
        }

        String trimmed = rawTags.trim();

        // Trường hợp chuỗi mảng JSON: ["tag1", "tag2"]
        if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
            try {
                List<String> list = OBJECT_MAPPER.readValue(trimmed, new TypeReference<List<String>>() {});
                return list.stream()
                        .filter(s -> s != null && !s.isBlank())
                        .map(String::trim)
                        .toList();
            } catch (Exception e) {
                log.debug("Failed to parse tags as JSON array, falling back to regex: {}", trimmed);
                // Fallback: Loại bỏ ngoặc vuông và dấu quote
                String cleaned = trimmed.substring(1, trimmed.length() - 1)
                        .replace("\"", "")
                        .replace("'", "");
                return parseCsv(cleaned);
            }
        }

        // Trường hợp chuỗi phân tách bởi dấu phẩy (CSV)
        return parseCsv(trimmed);
    }

    private static List<String> parseCsv(String input) {
        if (input == null || input.isBlank()) {
            return Collections.emptyList();
        }
        return Arrays.stream(input.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
    }
}

