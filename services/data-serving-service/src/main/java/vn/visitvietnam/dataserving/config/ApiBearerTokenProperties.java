package vn.visitvietnam.dataserving.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/** Shared secret for /api/v1/pois. Bound from POI_API_BEARER_TOKEN via application.yml. */
@ConfigurationProperties(prefix = "app.security.poi-api")
public record ApiBearerTokenProperties(String bearerToken) {

    @Override
    public String toString() {
        boolean set = bearerToken != null && !bearerToken.isBlank();
        return "ApiBearerTokenProperties[bearerToken=" + (set ? "<set>" : "<blank>") + "]";
    }
}
