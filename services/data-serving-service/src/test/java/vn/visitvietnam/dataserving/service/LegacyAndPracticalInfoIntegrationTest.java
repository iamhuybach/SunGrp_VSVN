package vn.visitvietnam.dataserving.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;
import vn.visitvietnam.dataserving.TestcontainersConfiguration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Import(TestcontainersConfiguration.class)
@SpringBootTest(properties = "spring.jpa.properties.hibernate.session_factory.statement_inspector=vn.visitvietnam.dataserving.service.CountingStatementInspector")
@AutoConfigureMockMvc
@Transactional
class LegacyAndPracticalInfoIntegrationTest {

    private static final String NEW_ID = "new-poi-1";
    private static final String OLD_ID = "legacy-poi-1";

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbc;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${app.security.poi-api.bearer-token}")
    private String token;

    @BeforeEach
    void seed() {
        jdbc.update("DELETE FROM apps.srv_poi_legacy_id_map");
        jdbc.update("DELETE FROM apps.srv_poi_review");
        jdbc.update("DELETE FROM apps.srv_poi_media_gallery");
        jdbc.update("DELETE FROM apps.srv_poi_amenity");
        jdbc.update("DELETE FROM apps.srv_poi_multi_lang");
        jdbc.update("DELETE FROM apps.srv_poi_info");
        insertInfo(NEW_ID, "Sample Cafe", "partner", "[{\"a\":1}]");
        insertMap(OLD_ID, NEW_ID, "OK");
        jdbc.update(
                "INSERT INTO apps.srv_poi_multi_lang (poi_id, lang, description, experience) VALUES (?,?,?,?)",
                NEW_ID, "vi", "Mo ta", "[{\"title\":\"Walk\",\"description\":\"Path\",\"keyword\":\"walk\"}]");
        jdbc.update(
                "INSERT INTO apps.srv_poi_media_gallery (media_id, poi_id, is_cover, is_active, blob_url) VALUES (?,?,?,?,?)",
                "media-1", NEW_ID, true, true, "pois/media-1.jpg");
        jdbc.update(
                "INSERT INTO apps.srv_poi_review (review_id, poi_id, review_text, source_name, rating) VALUES (?,?,?,?,?)",
                "review-1", NEW_ID, "Tot", "google", new java.math.BigDecimal("4.00"));
        jdbc.update(
                "INSERT INTO apps.srv_poi_amenity (poi_id, business_sector, amenity_group, amenity_raw, amenity) VALUES (?,?,?,?,?)",
                NEW_ID, "attraction", "access", "parking", "parking");
    }

    @Test
    @DisplayName("mọi endpoint trả cùng data cho poi_id cũ và mới")
    void everyPoiEndpointReturnsSameDataForLegacyAndNewId() throws Exception {
        assertThat(okData("GET", "/api/v1/pois/" + OLD_ID + "/gallery", null))
                .isEqualTo(okData("GET", "/api/v1/pois/" + NEW_ID + "/gallery", null));
        assertSame("GET", "/api/v1/pois/" + OLD_ID + "/reviews", "/api/v1/pois/" + NEW_ID + "/reviews", null, "data", "rating_summary");
        assertThat(okData("GET", "/api/v1/pois/" + OLD_ID + "/experiences", null))
                .isEqualTo(okData("GET", "/api/v1/pois/" + NEW_ID + "/experiences", null));
        assertThat(okData("GET", "/api/v1/pois/" + OLD_ID + "/practical_info", null))
                .isEqualTo(okData("GET", "/api/v1/pois/" + NEW_ID + "/practical_info", null));
        assertThat(okData("GET", "/api/v1/pois/" + OLD_ID + "/amenities", null))
                .isEqualTo(okData("GET", "/api/v1/pois/" + NEW_ID + "/amenities", null));
        assertThat(okData("POST", "/api/v1/pois/compact", "{\"ids\":[\"" + OLD_ID + "\"]}"))
                .isEqualTo(okData("POST", "/api/v1/pois/compact", "{\"ids\":[\"" + NEW_ID + "\"]}"));
        assertThat(okData("POST", "/api/v1/pois/practical_info", "{\"ids\":[\"" + OLD_ID + "\"]}"))
                .isEqualTo(okData("POST", "/api/v1/pois/practical_info", "{\"ids\":[\"" + NEW_ID + "\"]}"));
        assertThat(okData("GET", "/api/v1/pois/" + OLD_ID + "/practical_info", null).get("id").asText()).isEqualTo(NEW_ID);
    }

    @Test
    @DisplayName("id cũ không resolve thì xử lý như id mới không tồn tại")
    void unresolvedLegacyIdBehavesAsUnknownId() throws Exception {
        insertMap("missing-evidence", NEW_ID, "MISSING_EVIDENCE");
        mockMvc.perform(auth(get("/api/v1/pois/missing-evidence/practical_info"))).andExpect(status().isNotFound());
        mockMvc.perform(auth(get("/api/v1/pois/absent-id/practical_info"))).andExpect(status().isNotFound());
        assertThat(okData("GET", "/api/v1/pois/missing-evidence/gallery", null)).isEmpty();
        assertThat(okData("GET", "/api/v1/pois/absent-id/gallery", null)).isEmpty();
        assertThat(okData("POST", "/api/v1/pois/practical_info", "{\"ids\":[\"missing-evidence\"]}")).isEmpty();
        assertThat(okData("POST", "/api/v1/pois/practical_info", "{\"ids\":[\"absent-id\"]}")).isEmpty();
    }

    @Test
    @DisplayName("id đã là poi_id mới thì không đổi theo dòng map")
    void newIdWinsWhenLegacyRowEqualsExistingPoiId() throws Exception {
        insertInfo("shared", "Keep", "google", null);
        insertInfo("other", "Other", "partner", null);
        insertMap("shared", "other", "OK");
        JsonNode data = okData("GET", "/api/v1/pois/shared/practical_info", null);
        assertThat(data.get("id").asText()).isEqualTo("shared");
        assertThat(data.get("name").asText()).isEqualTo("Keep");
    }

    @Test
    @DisplayName("POST gộp id cũ và id mới của cùng một POI")
    void postDedupesLegacyAndNewIdsOfSamePoi() throws Exception {
        JsonNode body = okBody("POST", "/api/v1/pois/practical_info",
                "{\"ids\":[\"" + OLD_ID + "\",\"" + NEW_ID + "\"]}");
        assertThat(body.get("data")).hasSize(1);
        assertThat(body.get("data").get(0).get("id").asText()).isEqualTo(NEW_ID);
        assertThat(body.get("meta").get("pagination").get("total_items").asInt()).isEqualTo(1);
    }

    @Test
    @DisplayName("POST không required_fields thì mỗi phần tử khớp GET data")
    void postWithoutRequiredFieldsEqualsGetDataPerItem() throws Exception {
        JsonNode getData = okData("GET", "/api/v1/pois/" + NEW_ID + "/practical_info", null);
        JsonNode postData = okData("POST", "/api/v1/pois/practical_info", "{\"ids\":[\"" + NEW_ID + "\"]}");
        assertThat(postData).hasSize(1);
        assertThat(postData.get(0)).isEqualTo(getData);
    }

    @Test
    @DisplayName("required_fields chỉ trả khóa đã chọn theo thứ tự detail")
    void postRequiredFieldsReturnsOnlySelectedKeysInCanonicalOrder() throws Exception {
        JsonNode item = okData("POST", "/api/v1/pois/practical_info?required_fields=phone,id",
                "{\"ids\":[\"" + NEW_ID + "\"]}").get(0);
        assertThat(item.fieldNames()).toIterable().containsExactly("id", "phone");
        assertThat(item.get("phone").isNull()).isTrue();
    }

    @Test
    @DisplayName("source và poi_name lọc không phân biệt hoa thường và escape LIKE")
    void postFiltersBySourceAndPoiNameCaseInsensitiveEscaped() throws Exception {
        insertInfo("pct", "100%_Cafe", "Partner", null);
        insertInfo("wide", "100X Cafe", "google", null);
        MvcResult result = mockMvc.perform(auth(post("/api/v1/pois/practical_info")
                        .contentType(MediaType.APPLICATION_JSON)
                        .param("source", "partner")
                        .param("poi_name", "100%_")
                        .content("{\"ids\":[\"" + NEW_ID + "\",\"pct\",\"wide\"]}")))
                .andExpect(status().isOk())
                .andReturn();
        JsonNode data = objectMapper.readTree(result.getResponse().getContentAsString()).get("data");
        assertThat(data).hasSize(1);
        assertThat(data.get(0).get("id").asText()).isEqualTo("pct");
    }

    @Test
    @DisplayName("sort desc đưa null xuống cuối")
    void sortDescKeepsNullsLast() throws Exception {
        insertInfo("named-b", "Mango", "partner", null);
        insertInfo("named-a", "Alpha", "partner", null);
        insertInfo("named-null", null, "partner", null);
        JsonNode data = okData("POST", "/api/v1/pois/practical_info?sort_field=name&sort_order=desc&size=10",
                "{\"ids\":[\"named-b\",\"named-a\",\"named-null\"]}");
        assertThat(data).hasSize(3);
        assertThat(data.get(0).get("name").asText()).isEqualTo("Mango");
        assertThat(data.get(1).get("name").asText()).isEqualTo("Alpha");
        assertThat(data.get(2).get("name").isNull()).isTrue();
    }

    @Test
    @DisplayName("meta.pagination cùng hình reviews")
    void postPaginationMetaMatchesReviewsShape() throws Exception {
        insertInfo("second", "Second", "partner", null);
        JsonNode page = okBody("POST", "/api/v1/pois/practical_info?page=0&size=1",
                "{\"ids\":[\"" + NEW_ID + "\",\"second\"]}").get("meta").get("pagination");
        assertThat(page.fieldNames()).toIterable().containsExactlyInAnyOrder(
                "type", "page", "per_page", "total_items", "total_pages", "has_next", "has_prev");
        assertThat(page.get("type").asText()).isEqualTo("offset");
        assertThat(page.get("per_page").asInt()).isEqualTo(1);
        assertThat(page.get("total_items").asInt()).isEqualTo(2);
        assertThat(page.get("has_next").asBoolean()).isTrue();
        assertThat(page.get("has_prev").asBoolean()).isFalse();
    }

    @Test
    @DisplayName("POST tối đa 3 câu SQL")
    void postUsesAtMostThreeStatements() throws Exception {
        CountingStatementInspector.reset();
        okData("POST", "/api/v1/pois/practical_info", "{\"ids\":[\"" + OLD_ID + "\"]}");
        assertThat(CountingStatementInspector.COUNT.get()).isBetween(1, 3);
        assertThat(CountingStatementInspector.SQL).allSatisfy(sql -> assertThat(placeholderCount(sql)).isLessThanOrEqualTo(100));
    }

    @Test
    @DisplayName("120 id vẫn tối đa 3 câu SQL và dùng ANY")
    void postOneHundredTwentyIdsStaysWithinStatementAndInLimits() throws Exception {
        StringBuilder ids = new StringBuilder("{\"ids\":[\"" + NEW_ID + "\"");
        for (int i = 0; i < 119; i++) {
            ids.append(",\"missing-").append(i).append('"');
        }
        ids.append("]}");
        CountingStatementInspector.reset();
        JsonNode data = okData("POST", "/api/v1/pois/practical_info", ids.toString());
        assertThat(data).hasSize(1);
        assertThat(CountingStatementInspector.COUNT.get()).isBetween(1, 3);
        assertThat(CountingStatementInspector.SQL).noneMatch(sql -> sql.contains("@>"));
        assertThat(CountingStatementInspector.SQL).anyMatch(sql -> sql.toLowerCase().contains("= any (cast("));
        assertThat(CountingStatementInspector.SQL).allSatisfy(sql -> assertThat(placeholderCount(sql)).isLessThanOrEqualTo(100));
    }

    @Test
    @DisplayName("GET practical info tối đa 3 câu SQL, id lạ đúng 1 câu và 404")
    void getPracticalInfoUsesAtMostThreeStatements() throws Exception {
        CountingStatementInspector.reset();
        okData("GET", "/api/v1/pois/" + OLD_ID + "/practical_info", null);
        assertThat(CountingStatementInspector.COUNT.get()).isBetween(1, 3);
        CountingStatementInspector.reset();
        mockMvc.perform(auth(get("/api/v1/pois/absent-id/practical_info"))).andExpect(status().isNotFound());
        assertThat(CountingStatementInspector.COUNT.get()).isEqualTo(1);
    }

    @Test
    @DisplayName("required_fields không cần lang hay cover thì đúng 1 câu SQL")
    void postFieldsWithoutLangOrCoverUseOneStatement() throws Exception {
        CountingStatementInspector.reset();
        okData("POST", "/api/v1/pois/practical_info?required_fields=id,name", "{\"ids\":[\"" + NEW_ID + "\"]}");
        assertThat(CountingStatementInspector.COUNT.get()).isEqualTo(1);
    }

    @Test
    @DisplayName("trang quá cuối vẫn giữ total_items")
    void postPastLastPageKeepsTotalItems() throws Exception {
        insertInfo("second", "Second", "partner", null);
        JsonNode body = okBody("POST", "/api/v1/pois/practical_info?page=5&size=1",
                "{\"ids\":[\"" + NEW_ID + "\",\"second\"]}");
        assertThat(body.get("data")).isEmpty();
        assertThat(body.get("meta").get("pagination").get("total_items").asInt()).isEqualTo(2);
    }

    private static int placeholderCount(String sql) {
        int count = 0;
        for (int i = 0; i < sql.length(); i++) {
            if (sql.charAt(i) == '?') {
                count++;
            }
        }
        return count;
    }

    private void insertInfo(String id, String name, String source, String holiday) {
        jdbc.update(
                "INSERT INTO apps.srv_poi_info (poi_id, poi_name, source_name, holiday_exceptions) VALUES (?,?,?,?)",
                id, name, source, holiday);
    }

    private void insertMap(String legacy, String poiId, String status) {
        jdbc.update(
                "INSERT INTO apps.srv_poi_legacy_id_map (legacy_poi_id, poi_id, poi_id_status) VALUES (?,?,?)",
                legacy, poiId, status);
    }

    private org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder auth(
            org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder builder) {
        return builder.header(HttpHeaders.AUTHORIZATION, "Bearer " + token);
    }

    private JsonNode okData(String method, String path, String json) throws Exception {
        return okBody(method, path, json).get("data");
    }

    private JsonNode okBody(String method, String path, String json) throws Exception {
        var builder = "POST".equals(method)
                ? post(path).contentType(MediaType.APPLICATION_JSON).content(json)
                : get(path);
        MvcResult result = mockMvc.perform(auth(builder)).andExpect(status().isOk()).andReturn();
        return objectMapper.readTree(result.getResponse().getContentAsString());
    }

    private void assertSame(String method, String left, String right, String json, String... fields) throws Exception {
        JsonNode a = okBody(method, left, json);
        JsonNode b = okBody(method, right, json);
        for (String field : fields) {
            assertThat(a.get(field)).isEqualTo(b.get(field));
        }
    }
}
