package vn.visitvietnam.dataserving.config;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.env.YamlPropertySourceLoader;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;
import vn.visitvietnam.dataserving.api.PoiController;
import vn.visitvietnam.dataserving.api.dto.PoiExperiencesResponse;
import vn.visitvietnam.dataserving.common.dto.PageResponse;
import vn.visitvietnam.dataserving.common.web.GlobalExceptionHandler;
import vn.visitvietnam.dataserving.common.web.RequestContext;
import vn.visitvietnam.dataserving.common.web.RequestIdFilter;
import vn.visitvietnam.dataserving.config.SecurityConfig.Outcome;
import vn.visitvietnam.dataserving.config.SecurityConfig.PoiBearerTokenVerifier;
import vn.visitvietnam.dataserving.service.PoiService;
import vn.visitvietnam.dataserving.service.util.LanguageResolver;

import java.util.List;
import java.util.function.Supplier;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.nullValue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(PoiController.class)
@Import({SecurityConfig.class, GlobalExceptionHandler.class, LanguageResolver.class, RequestIdFilter.class})
class ApiBearerAuthTest {

    @MockitoBean
    private PoiService poiService;

    @Autowired
    private MockMvc mvc;

    @Value("${app.security.poi-api.bearer-token}")
    private String token;

    @BeforeEach
    void stubPoiService() {
        when(poiService.getCompactPois(any(), any())).thenReturn(List.of());
        when(poiService.getFeatures(any(), any(), anyInt(), any(), any(), anyInt(), anyInt()))
                .thenReturn(new PoiService.FeaturePage(List.of(), 0));
        when(poiService.getGallery(any(), anyInt(), anyInt())).thenReturn(PageResponse.of(List.of(), 0, 20, 0));
        when(poiService.getReviews(any(), anyInt(), anyInt()))
                .thenReturn(new PoiService.ReviewsPage(PageResponse.of(List.of(), 0, 10, 0), List.of()));
        when(poiService.getExperiences(any(), any())).thenReturn(new PoiExperiencesResponse(List.of()));
        when(poiService.getPracticalInfo(any(), any())).thenReturn(null);
        when(poiService.getAmenities(any())).thenReturn(List.of());
    }

    static Stream<Arguments> poiEndpoints() {
        return Stream.of(
                Arguments.of("compact", (Supplier<MockHttpServletRequestBuilder>) () ->
                        post("/api/v1/pois/compact")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("{\"ids\":[\"poi_01\"]}")),
                Arguments.of("features", (Supplier<MockHttpServletRequestBuilder>) () -> get("/api/v1/pois/features")),
                Arguments.of("gallery", (Supplier<MockHttpServletRequestBuilder>) () -> get("/api/v1/pois/poi_01/gallery")),
                Arguments.of("reviews", (Supplier<MockHttpServletRequestBuilder>) () -> get("/api/v1/pois/poi_01/reviews")),
                Arguments.of("experiences", (Supplier<MockHttpServletRequestBuilder>) () -> get("/api/v1/pois/poi_01/experiences")),
                Arguments.of("practical_info", (Supplier<MockHttpServletRequestBuilder>) () -> get("/api/v1/pois/poi_01/practical_info")),
                Arguments.of("amenities", (Supplier<MockHttpServletRequestBuilder>) () -> get("/api/v1/pois/poi_01/amenities"))
        );
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("poiEndpoints")
    void missingAuthorizationReturns401Envelope(String name, Supplier<MockHttpServletRequestBuilder> request) throws Exception {
        expect401(mvc.perform(request.get()));
        verifyNoInteractions(poiService);
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("poiEndpoints")
    void wrongTokenReturns401(String name, Supplier<MockHttpServletRequestBuilder> request) throws Exception {
        expect401(mvc.perform(request.get().header(HttpHeaders.AUTHORIZATION, "Bearer " + token + "-wrong")));
        verifyNoInteractions(poiService);
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("poiEndpoints")
    void nonBearerSchemeReturns401(String name, Supplier<MockHttpServletRequestBuilder> request) throws Exception {
        for (String value : List.of("Basic " + token, "Token " + token, token)) {
            expect401(mvc.perform(request.get().header(HttpHeaders.AUTHORIZATION, value)));
        }
        verifyNoInteractions(poiService);
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("poiEndpoints")
    void correctTokenReachesController(String name, Supplier<MockHttpServletRequestBuilder> request) throws Exception {
        mvc.perform(request.get().header(HttpHeaders.AUTHORIZATION, "Bearer " + token))
                .andExpect(status().isOk());
    }

    @Test
    void bearerSchemeIsCaseInsensitive() throws Exception {
        mvc.perform(get("/api/v1/pois/features").header(HttpHeaders.AUTHORIZATION, "bearer " + token))
                .andExpect(status().isOk());
    }

    @Test
    void emptyBearerTokenReturns401() throws Exception {
        expect401(mvc.perform(get("/api/v1/pois/features").header(HttpHeaders.AUTHORIZATION, "Bearer ")));
        expect401(mvc.perform(get("/api/v1/pois/features").header(HttpHeaders.AUTHORIZATION, "Bearer    ")));
    }

    @Test
    void duplicateAuthorizationHeadersReturn401() throws Exception {
        expect401(mvc.perform(get("/api/v1/pois/features")
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + token, "Bearer " + token)));
    }

    @Test
    void unauthorizedBodyCarriesTraceIdAndNeverEchoesToken() throws Exception {
        String body = mvc.perform(get("/api/v1/pois/features")
                        .header(RequestContext.TRACE_ID_HEADER, "auth-trace-1")
                        .header(HttpHeaders.AUTHORIZATION, "Bearer " + token + "x"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.meta.trace_id").value("auth-trace-1"))
                .andReturn()
                .getResponse()
                .getContentAsString();
        assertThat(body).doesNotContain(token);
    }

    @Test
    void authPrecedesRoutingForWrongMethodAndUnknownPath() throws Exception {
        expect401(mvc.perform(get("/api/v1/pois/compact")));
        expect401(mvc.perform(get("/api/v1/pois/poi_01/unknown")));
        expect401(mvc.perform(post("/api/v1/pois/compact").contentType(MediaType.TEXT_PLAIN).content("{\"ids\":[\"poi_01\"]}")));
    }

    @Test
    void pathsOutsidePoiApiStayAnonymous() throws Exception {
        mvc.perform(get("/actuator/health")).andExpect(status().isNotFound());
        mvc.perform(get("/api/v1/other")).andExpect(status().isNotFound());
    }

    @Nested
    @TestPropertySource(properties = "app.security.poi-api.bearer-token=")
    class BlankTokenConfiguration {

        @Autowired
        private MockMvc blankMvc;

        @ParameterizedTest(name = "{0}")
        @MethodSource("vn.visitvietnam.dataserving.config.ApiBearerAuthTest#poiEndpoints")
        void blankConfigurationRejectsEveryPoiRequest(String name, Supplier<MockHttpServletRequestBuilder> request) throws Exception {
            expect401(blankMvc.perform(request.get().header(HttpHeaders.AUTHORIZATION, "Bearer ")));
            expect401(blankMvc.perform(request.get().header(HttpHeaders.AUTHORIZATION, "Bearer anything")));
        }

        @Test
        void blankConfigurationKeepsNonPoiPathsOpen() throws Exception {
            blankMvc.perform(get("/actuator/health")).andExpect(status().isNotFound());
        }
    }

    @Test
    void verifierTreatsNullBlankAndWhitespaceConfigAsNotConfigured() {
        for (String configured : new String[] {null, "", "  \r\n"}) {
            PoiBearerTokenVerifier verifier = new PoiBearerTokenVerifier(configured);
            assertThat(verifier.configured()).isFalse();
            assertThat(verifier.verify(new MockHttpServletRequest())).isEqualTo(Outcome.NOT_CONFIGURED);
        }
    }

    @Test
    void verifierStripsConfiguredWhitespace() {
        PoiBearerTokenVerifier verifier = new PoiBearerTokenVerifier("abc\r\n");
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader(HttpHeaders.AUTHORIZATION, "Bearer abc");
        assertThat(verifier.verify(request)).isEqualTo(Outcome.ACCEPTED);
    }

    @Test
    void verifierOutcomes() {
        PoiBearerTokenVerifier verifier = new PoiBearerTokenVerifier("abc");
        assertThat(verifier.verify(requestWith())).isEqualTo(Outcome.MISSING_HEADER);
        assertThat(verifier.verify(requestWith("Bearer abc", "Bearer abc"))).isEqualTo(Outcome.MULTIPLE_HEADERS);
        assertThat(verifier.verify(requestWith("Basic abc"))).isEqualTo(Outcome.NOT_BEARER);
        assertThat(verifier.verify(requestWith("Bearer "))).isEqualTo(Outcome.EMPTY_TOKEN);
        assertThat(verifier.verify(requestWith("Bearer other"))).isEqualTo(Outcome.TOKEN_MISMATCH);
        assertThat(verifier.verify(requestWith("Bearer abc"))).isEqualTo(Outcome.ACCEPTED);
        assertThat(new PoiBearerTokenVerifier("").verify(requestWith("Bearer abc"))).isEqualTo(Outcome.NOT_CONFIGURED);
    }

    @Test
    void propertiesToStringNeverContainsToken() {
        String secret = "super-secret-value";
        assertThat(new ApiBearerTokenProperties(secret).toString())
                .doesNotContain(secret)
                .contains("<set>");
        assertThat(new ApiBearerTokenProperties("  ").toString()).contains("<blank>").doesNotContain("secret");
        assertThat(new ApiBearerTokenProperties(null).toString()).contains("<blank>");
    }

    @Test
    void mainApplicationYmlBindsBearerTokenFromPoiApiBearerTokenEnv() throws Exception {
        var loaded = new YamlPropertySourceLoader().load(
                "main", new FileSystemResource("src/main/resources/application.yml"));
        assertThat(loaded).isNotEmpty();
        assertThat(loaded.getFirst().getProperty("app.security.poi-api.bearer-token"))
                .isEqualTo("${POI_API_BEARER_TOKEN:}");
    }

    private static MockHttpServletRequest requestWith(String... authorizationValues) {
        MockHttpServletRequest request = new MockHttpServletRequest();
        for (String value : authorizationValues) {
            request.addHeader(HttpHeaders.AUTHORIZATION, value);
        }
        return request;
    }

    private static void expect401(ResultActions result) throws Exception {
        result.andExpect(status().isUnauthorized())
                .andExpect(header().string(HttpHeaders.WWW_AUTHENTICATE, "Bearer"))
                .andExpect(header().exists(RequestContext.TRACE_ID_HEADER))
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value(401))
                .andExpect(jsonPath("$.message").value("Missing or invalid bearer token."))
                .andExpect(jsonPath("$.data").value(nullValue()))
                .andExpect(jsonPath("$.errors").value(nullValue()))
                .andExpect(jsonPath("$.meta.error_code").value("ERR_UNAUTHORIZED"))
                .andExpect(jsonPath("$.meta.trace_id").isNotEmpty());
    }
}
