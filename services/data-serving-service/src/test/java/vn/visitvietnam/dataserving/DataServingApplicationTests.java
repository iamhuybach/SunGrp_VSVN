package vn.visitvietnam.dataserving;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Import(TestcontainersConfiguration.class)
@SpringBootTest
@AutoConfigureMockMvc
class DataServingApplicationTests {

	@Autowired
	private MockMvc mvc;

	@Autowired
	private JdbcTemplate jdbcTemplate;

	@Autowired
	private ApplicationContext context;

	@Value("${app.security.poi-api.bearer-token}")
	private String bearerToken;

	@Test
	void contextLoads() {
	}

	@Test
	void healthEndpointReturnsUp() throws Exception {
		mvc.perform(get("/actuator/health"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.status").value("UP"));
	}

	@Test
	void openApiDocsDescribeHolidayExceptionsAsNullableArray() throws Exception {
		String body = mvc.perform(get("/v3/api-docs"))
				.andExpect(status().isOk())
				.andReturn()
				.getResponse()
				.getContentAsString();
		JsonNode schemas = new ObjectMapper().readTree(body).path("components").path("schemas");
		JsonNode field = null;
		var properties = schemas.fields();
		while (properties.hasNext()) {
			JsonNode candidate = properties.next().getValue().path("properties").path("holiday_exceptions");
			if (!candidate.isMissingNode()) {
				field = candidate;
				break;
			}
		}
		assertThat(field).as("holiday_exceptions schema").isNotNull();
		JsonNode type = field.path("type");
		assertThat(type.isArray()).as(field.toString()).isTrue();
		assertThat(type).extracting(JsonNode::asText).containsExactly("array", "null");
		JsonNode items = field.path("items");
		assertThat(items.isObject()).isTrue();
		assertThat(items.has("properties")).isFalse();
		assertThat(items.path("additionalProperties").asBoolean()).isTrue();
	}

	@Test
	void initScriptCreatesAllServingTables() {
		List<String> expectedTables = List.of(
				"srv_poi_info",
				"srv_poi_multi_lang",
				"srv_poi_amenity",
				"srv_poi_media_gallery",
				"srv_poi_review"
		);

		for (String table : expectedTables) {
			Integer count = jdbcTemplate.queryForObject(
					"SELECT count(*) FROM information_schema.tables WHERE table_schema = 'apps' AND table_name = ?",
					Integer.class,
					table
			);
			assertThat(count).as("Table apps." + table + " should exist").isEqualTo(1);
		}
	}

	@Test
	void poiEndpointWithoutTokenReturns401Envelope() throws Exception {
		mvc.perform(get("/api/v1/pois/no-such-poi/amenities"))
				.andExpect(status().isUnauthorized())
				.andExpect(jsonPath("$.meta.error_code").value("ERR_UNAUTHORIZED"));
	}

	@Test
	void poiEndpointWithTokenReturns200() throws Exception {
		mvc.perform(get("/api/v1/pois/no-such-poi/amenities")
						.header(HttpHeaders.AUTHORIZATION, "Bearer " + bearerToken))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data").isEmpty());
	}

	@Test
	void openApiDocsDeclareBearerAuthAndStayOpen() throws Exception {
		mvc.perform(get("/v3/api-docs"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.components.securitySchemes.bearerAuth.scheme").value("bearer"))
				.andExpect(jsonPath("$.paths['/api/v1/pois/{poi_id}/amenities'].get.responses['401'].content['application/json']").exists())
				.andExpect(jsonPath("$.paths['/api/v1/pois/{poi_id}/amenities'].get.responses['401'].content['application/problem+json']").doesNotExist())
				.andExpect(jsonPath("$.paths['/api/v1/pois/{poi_id}/amenities'].get.responses['401'].headers['WWW-Authenticate']").exists());
	}

	@Test
	void noDefaultUserDetailsServiceIsCreated() {
		assertThat(context.getBeanNamesForType(UserDetailsService.class)).isEmpty();
	}
}
