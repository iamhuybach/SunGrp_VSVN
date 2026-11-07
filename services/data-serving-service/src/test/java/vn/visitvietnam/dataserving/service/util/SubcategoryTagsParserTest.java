package vn.visitvietnam.dataserving.service.util;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class SubcategoryTagsParserTest {

    @Test
    @DisplayName("Parse định dạng JSON array hợp lệ")
    void shouldParseValidJsonArray() {
        String input = "[\"museum\", \"historical_site\", \"culture\"]";
        List<String> tags = SubcategoryTagsParser.parse(input);
        assertThat(tags).containsExactly("museum", "historical_site", "culture");
    }

    @Test
    @DisplayName("Parse định dạng CSV")
    void shouldParseCsvString() {
        String input = "beach, resort, luxury ";
        List<String> tags = SubcategoryTagsParser.parse(input);
        assertThat(tags).containsExactly("beach", "resort", "luxury");
    }

    @Test
    @DisplayName("Parse mảng JSON lỗi hoặc dùng dấu nháy đơn")
    void shouldHandleMalformedJsonArrayGracefully() {
        String input = "['coffee', 'bakery']";
        List<String> tags = SubcategoryTagsParser.parse(input);
        assertThat(tags).containsExactly("coffee", "bakery");
    }

    @Test
    @DisplayName("Trả về danh sách rỗng khi input null hoặc rỗng")
    void shouldReturnEmptyListForNullOrBlank() {
        assertThat(SubcategoryTagsParser.parse(null)).isEmpty();
        assertThat(SubcategoryTagsParser.parse("")).isEmpty();
        assertThat(SubcategoryTagsParser.parse("   ")).isEmpty();
    }
}

