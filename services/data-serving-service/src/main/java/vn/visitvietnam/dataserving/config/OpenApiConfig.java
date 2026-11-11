package vn.visitvietnam.dataserving.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.media.Content;
import io.swagger.v3.oas.models.media.MediaType;
import io.swagger.v3.oas.models.media.ObjectSchema;
import io.swagger.v3.oas.models.media.Schema;
import io.swagger.v3.oas.models.media.StringSchema;
import io.swagger.v3.oas.models.responses.ApiResponse;
import io.swagger.v3.oas.models.servers.Server;
import org.springdoc.core.customizers.OpenApiCustomizer;
import org.springdoc.core.models.GroupedOpenApi;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

@Configuration(proxyBeanMethods = false)
public class OpenApiConfig {

    @Bean
    public GroupedOpenApi apiGroupedOpenApi() {
        return GroupedOpenApi.builder()
                .group("serving")
                .packagesToScan("vn.visitvietnam.dataserving.api")
                .build();
    }

    @Bean
    public OpenAPI dataServingApiOpenApi(@Value("${OPENAPI_GATEWAY_URL:}") String gatewayUrl) {
        List<Server> servers = new ArrayList<>();
        servers.add(new Server().url("http://localhost:8080").description("Local"));
        if (!gatewayUrl.isBlank()) {
            servers.add(new Server().url(gatewayUrl).description("Gateway"));
        }
        return new OpenAPI()
                .info(new Info()
                        .title("data-serving-service")
                        .version("0.0.1-SNAPSHOT")
                        .description("""
                                High-throughput Serving API over the Visit Vietnam data store (`vv_data_serving`).
                                Exposes read-optimized queries and search APIs for the Visit Vietnam platform.
                                All errors conform to RFC 9457 application/problem+json.""")
                        .license(new License()
                                .name("Proprietary — Sun Group / Visit Vietnam")
                                .identifier("LicenseRef-SunGroup-Proprietary")))
                .servers(servers);
    }

    @Bean
    public OpenApiCustomizer holidayExceptionsSchemaCustomizer() {
        return openApi -> {
            if (openApi.getComponents() == null || openApi.getComponents().getSchemas() == null) {
                return;
            }
            openApi.getComponents().getSchemas().values().forEach(schema -> {
                if (schema.getProperties() == null || !schema.getProperties().containsKey("holiday_exceptions")) {
                    return;
                }
                // Field Java là String vì @JsonRawValue. Springdoc ghi type string. Schema công bố là mảng nullable.
                Schema<?> items = new Schema<>().additionalProperties(Boolean.TRUE);
                Schema<?> holiday = new Schema<>()
                        .types(new LinkedHashSet<>(List.of("array", "null")))
                        .items(items)
                        .description("Mảng JSON nguyên từ apps.srv_poi_info.holiday_exceptions. JSON hỏng thì null. Không đổi khóa bên trong.");
                schema.getProperties().put("holiday_exceptions", holiday);
            });
        };
    }

    @Bean
    public OpenApiCustomizer problemResponsesCustomizer() {
        Content problemJson = new Content().addMediaType(
                "application/problem+json", new MediaType().schema(problemDetailSchema()));

        return openApi -> {
            if (openApi.getPaths() != null) {
                openApi.getPaths().values().forEach(pathItem ->
                        pathItem.readOperations().forEach(op -> {
                            op.getResponses().putIfAbsent("400", new ApiResponse()
                                    .description("Bad Request: Malformed input or parameter")
                                    .content(problemJson));
                            op.getResponses().putIfAbsent("404", new ApiResponse()
                                    .description("Not Found: Resource not found")
                                    .content(problemJson));
                            op.getResponses().forEach((status, response) -> {
                                boolean error = status.startsWith("4") || status.startsWith("5");
                                if (error && (response.getContent() == null || response.getContent().isEmpty())) {
                                    response.setContent(problemJson);
                                }
                            });
                        }));
            }
        };
    }

    private static Schema<?> problemDetailSchema() {
        return new ObjectSchema()
                .name("ProblemDetail")
                .description("RFC 9457 problem document (application/problem+json)")
                .addProperty("type", new StringSchema().example("about:blank"))
                .addProperty("title", new StringSchema().example("Bad Request"))
                .addProperty("status", new Schema<Integer>().type("integer").example(400))
                .addProperty("detail", new StringSchema().example("Invalid request parameter"))
                .addProperty("instance", new StringSchema().example("/api/v1/resource"));
    }
}

