package vn.visitvietnam.dataserving.config;

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
}
