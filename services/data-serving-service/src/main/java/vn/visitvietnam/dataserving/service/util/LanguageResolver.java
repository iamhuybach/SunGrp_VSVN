package vn.visitvietnam.dataserving.service.util;

import org.springframework.stereotype.Component;

import java.util.Locale;

/**
 * Utility phân giải mã ngôn ngữ theo thứ tự ưu tiên:
 * 1. Query parameter `lang`
 * 2. Request header `Accept-Language` (chuẩn HTTP)
 * 3. Fallback mặc định: `vi` (Tiếng Việt)
 */
@Component
public class LanguageResolver {

    public static final String DEFAULT_LANG = "vi";

    public String resolveLanguage(String queryLang, String acceptLanguageHeader) {
        if (queryLang != null && !queryLang.isBlank()) {
            return extractLanguageCode(queryLang.trim());
        }

        if (acceptLanguageHeader != null && !acceptLanguageHeader.isBlank()) {
            // Lấy ngôn ngữ ưu tiên đầu tiên từ header (vd: "en-US,en;q=0.9,vi;q=0.8" -> "en")
            String primaryTag = acceptLanguageHeader.split(",")[0].trim();
            if (!primaryTag.isEmpty()) {
                return extractLanguageCode(primaryTag);
            }
        }

        return DEFAULT_LANG;
    }

    private String extractLanguageCode(String raw) {
        if (raw == null || raw.isBlank()) {
            return DEFAULT_LANG;
        }
        // Tách subtag nếu có (vd: "en-US" -> "en", "zh-CN" -> "zh")
        String tag = raw.split("[-_;]")[0].trim().toLowerCase(Locale.ROOT);
        return tag.isEmpty() ? DEFAULT_LANG : tag;
    }
}
