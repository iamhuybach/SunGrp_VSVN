package vn.visitvietnam.dataserving.api.dto;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import vn.visitvietnam.dataserving.api.PoiController;
import vn.visitvietnam.dataserving.common.web.GlobalExceptionHandler;
import vn.visitvietnam.dataserving.common.web.RequestIdFilter;
import vn.visitvietnam.dataserving.config.SecurityConfig;
import vn.visitvietnam.dataserving.service.PoiService;
import vn.visitvietnam.dataserving.service.PracticalInfoQuery;
import vn.visitvietnam.dataserving.service.util.LanguageResolver;

import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(PoiController.class)
@Import({SecurityConfig.class, GlobalExceptionHandler.class, LanguageResolver.class, RequestIdFilter.class})
class PracticalInfoProjectionTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private PoiService poiService;

    @Value("${app.security.poi-api.bearer-token}")
    private String bearerToken;

    @Test
    @DisplayName("holiday_exceptions giữ nguyên mảng JSON")
    void holidayExceptionsStaysRawArray() throws Exception {
        PoiPracticalInfoResponse dto = sample("[{\"a\":1}]");
        Map<String, Object> item = PracticalInfoProjection.select(
                dto, EnumSet.of(PracticalInfoQuery.Field.HOLIDAY_EXCEPTIONS));
        when(poiService.searchPracticalInfo(any())).thenReturn(new PoiService.PracticalInfoPage(List.of(item), 1));
        mockMvc.perform(post("/api/v1/pois/practical_info")
                        .header(HttpHeaders.AUTHORIZATION, "Bearer " + bearerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ids\":[\"p\"]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data[0].holiday_exceptions[0].a").value(1));
    }

    @Test
    @DisplayName("field được chọn mà null vẫn có trong JSON")
    void selectedNullIsEmitted() throws Exception {
        Map<String, Object> item = PracticalInfoProjection.select(
                sample(null), EnumSet.of(PracticalInfoQuery.Field.ID, PracticalInfoQuery.Field.PHONE));
        when(poiService.searchPracticalInfo(any())).thenReturn(new PoiService.PracticalInfoPage(List.of(item), 1));
        mockMvc.perform(post("/api/v1/pois/practical_info")
                        .header(HttpHeaders.AUTHORIZATION, "Bearer " + bearerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ids\":[\"p\"]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data[0].id").value("p"))
                .andExpect(jsonPath("$.data[0].phone").value(org.hamcrest.Matchers.nullValue()));
    }

    @Test
    @DisplayName("FIELD_REGEX khớp đúng khóa enum")
    void fieldRegexMatchesEnumKeys() {
        assertThat(alternatives(PracticalInfoQuery.FIELD_REGEX))
                .containsExactly(java.util.Arrays.stream(PracticalInfoQuery.Field.values()).map(PracticalInfoQuery.Field::key).toArray(String[]::new));
    }

    @Test
    @DisplayName("SORT_REGEX khớp đúng khóa enum")
    void sortRegexMatchesEnumKeys() {
        assertThat(alternatives(PracticalInfoQuery.SORT_REGEX))
                .containsExactly(java.util.Arrays.stream(PracticalInfoQuery.SortField.values()).map(PracticalInfoQuery.SortField::key).toArray(String[]::new));
    }

    private static List<String> alternatives(String regex) {
        Matcher matcher = Pattern.compile("\\((.+)\\)\\??\\$").matcher(regex);
        assertThat(matcher.find()).isTrue();
        return List.of(matcher.group(1).split("\\|"));
    }

    private static PoiPracticalInfoResponse sample(String holiday) {
        return new PoiPracticalInfoResponse(
                "p", "n", null, null, null, null, null, null, null, null, null,
                holiday, null, null, null, null, null, null);
    }
}
