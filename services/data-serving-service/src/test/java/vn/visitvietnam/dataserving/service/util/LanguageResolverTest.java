package vn.visitvietnam.dataserving.service.util;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class LanguageResolverTest {

    private final LanguageResolver resolver = new LanguageResolver();

    @Test
    @DisplayName("Ưu tiên param lang khi được cung cấp")
    void shouldPrioritizeQueryLang() {
        String lang = resolver.resolveLanguage("en", "vi-VN,vi;q=0.9");
        assertThat(lang).isEqualTo("en");
    }

    @Test
    @DisplayName("Ưu tiên param lang cao hơn Accept-Language")
    void shouldPrioritizeQueryLangOverAcceptLanguage() {
        String lang = resolver.resolveLanguage("ja", "vi-VN,vi;q=0.9");
        assertThat(lang).isEqualTo("ja");
    }

    @Test
    @DisplayName("Trích xuất mã ngôn ngữ chính từ chuỗi có subtag")
    void shouldExtractPrimaryLanguageCode() {
        String lang = resolver.resolveLanguage("en-US", null);
        assertThat(lang).isEqualTo("en");
    }

    @Test
    @DisplayName("Sử dụng header Accept-Language khi không có param lang")
    void shouldUseAcceptLanguageHeaderWhenNoQueryLang() {
        String lang = resolver.resolveLanguage(null, "fr-FR,fr;q=0.8");
        assertThat(lang).isEqualTo("fr");
    }

    @Test
    @DisplayName("Fallback về vi khi tất cả đều rỗng hoặc null")
    void shouldFallbackToVi() {
        assertThat(resolver.resolveLanguage(null, null)).isEqualTo("vi");
        assertThat(resolver.resolveLanguage("", "")).isEqualTo("vi");
        assertThat(resolver.resolveLanguage("   ", "   ")).isEqualTo("vi");
    }
}
