package vn.visitvietnam.dataserving.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.Operation;
import io.swagger.v3.oas.models.PathItem;
import io.swagger.v3.oas.models.Paths;
import io.swagger.v3.oas.models.responses.ApiResponses;
import io.swagger.v3.oas.models.servers.Server;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class OpenApiConfigTest {

    private final OpenApiConfig config = new OpenApiConfig();

    @Test
    @DisplayName("Chỉ có server Local khi OPENAPI_GATEWAY_URL rỗng")
    void shouldListOnlyLocalServerWhenGatewayUrlBlank() {
        assertThat(config.dataServingApiOpenApi("").getServers())
                .extracting(Server::getUrl)
                .containsExactly("http://localhost:8080");
    }

    @Test
    @DisplayName("Thêm server Gateway từ OPENAPI_GATEWAY_URL")
    void shouldAddGatewayServerFromEnvironment() {
        assertThat(config.dataServingApiOpenApi("https://gateway.example.test").getServers())
                .extracting(Server::getUrl)
                .containsExactly("http://localhost:8080", "https://gateway.example.test");
    }

    @Test
    @DisplayName("401 của /api/v1/pois là application/json, không phải problem+json")
    void unauthorizedResponseIsApiJsonWithWwwAuthenticate() {
        OpenAPI openApi = new OpenAPI();
        Operation operation = new Operation().responses(new ApiResponses());
        PathItem pathItem = new PathItem().get(operation);
        openApi.setPaths(new Paths().addPathItem("/api/v1/pois/{poi_id}/amenities", pathItem));

        config.problemResponsesCustomizer().customise(openApi);

        var response = operation.getResponses().get("401");
        assertThat(response.getContent()).containsKey("application/json");
        assertThat(response.getContent()).doesNotContainKey("application/problem+json");
        assertThat(response.getHeaders()).containsKey("WWW-Authenticate");
        assertThat(response.getContent().get("application/json").getSchema().getProperties())
                .containsKeys("success", "code", "message", "data", "meta", "errors");
    }
}
