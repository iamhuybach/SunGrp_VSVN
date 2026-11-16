package vn.visitvietnam.dataserving.config;

import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.ProviderNotFoundException;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.authorization.AuthorizationDecision;
import org.springframework.security.authorization.AuthorizationManager;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.access.intercept.RequestAuthorizationContext;
import vn.visitvietnam.dataserving.common.web.BearerTokenAuthenticationEntryPoint;
import vn.visitvietnam.dataserving.common.web.RequestContext;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;

@Configuration(proxyBeanMethods = false)
@EnableWebSecurity
@EnableConfigurationProperties(ApiBearerTokenProperties.class)
public class SecurityConfig {

    static final String[] POI_API_PATHS = {"/api/v1/pois", "/api/v1/pois/**"};
    private static final Logger log = LoggerFactory.getLogger(SecurityConfig.class);

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http, ApiBearerTokenProperties properties) throws Exception {
        PoiBearerTokenVerifier verifier = new PoiBearerTokenVerifier(properties.bearerToken());
        if (!verifier.configured()) {
            log.warn("poi_api_auth token_configured=false; every /api/v1/pois request returns 401 until POI_API_BEARER_TOKEN is set");
        }
        BearerTokenAuthenticationEntryPoint unauthorized = new BearerTokenAuthenticationEntryPoint();
        AuthorizationManager<RequestAuthorizationContext> poiAccess = (authentication, context) -> {
            HttpServletRequest request = context.getRequest();
            Outcome outcome = verifier.verify(request);
            if (outcome != Outcome.ACCEPTED) {
                log.info("poi_api_auth_rejected reason={} method={} trace_id={}",
                        outcome, request.getMethod(), request.getAttribute(RequestContext.TRACE_ID_KEY));
            }
            return new AuthorizationDecision(outcome == Outcome.ACCEPTED);
        };
        http
                .csrf(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)
                .formLogin(AbstractHttpConfigurer::disable)
                .logout(AbstractHttpConfigurer::disable)
                .requestCache(AbstractHttpConfigurer::disable)
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .exceptionHandling(e -> e.authenticationEntryPoint(unauthorized).accessDeniedHandler(unauthorized))
                .authorizeHttpRequests(a -> a
                        .requestMatchers(POI_API_PATHS).access(poiAccess)
                        .anyRequest().permitAll());
        return http.build();
    }

    /** No login mechanism exists. This bean stops Boot from creating a default user and logging its password. */
    @Bean
    public AuthenticationManager noLoginAuthenticationManager() {
        return authentication -> {
            throw new ProviderNotFoundException("No login mechanism is configured");
        };
    }

    enum Outcome { ACCEPTED, NOT_CONFIGURED, MISSING_HEADER, MULTIPLE_HEADERS, NOT_BEARER, EMPTY_TOKEN, TOKEN_MISMATCH }

    static final class PoiBearerTokenVerifier {
        private final byte[] expectedDigest;

        PoiBearerTokenVerifier(String configuredToken) {
            String token = configuredToken == null ? "" : configuredToken.strip();
            this.expectedDigest = token.isEmpty() ? null : sha256(token);
        }

        boolean configured() {
            return expectedDigest != null;
        }

        Outcome verify(HttpServletRequest request) {
            if (expectedDigest == null) {
                return Outcome.NOT_CONFIGURED;
            }
            Enumeration<String> headers = request.getHeaders(HttpHeaders.AUTHORIZATION);
            List<String> values = headers == null ? List.of() : Collections.list(headers);
            if (values.isEmpty()) {
                return Outcome.MISSING_HEADER;
            }
            if (values.size() > 1) {
                return Outcome.MULTIPLE_HEADERS;
            }
            String value = values.getFirst();
            int space = value.indexOf(' ');
            if (space < 0 || !"Bearer".equalsIgnoreCase(value.substring(0, space))) {
                return Outcome.NOT_BEARER;
            }
            String presented = value.substring(space + 1).strip();
            if (presented.isEmpty()) {
                return Outcome.EMPTY_TOKEN;
            }
            return MessageDigest.isEqual(sha256(presented), expectedDigest) ? Outcome.ACCEPTED : Outcome.TOKEN_MISMATCH;
        }

        private static byte[] sha256(String value) {
            try {
                return MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
            } catch (NoSuchAlgorithmException e) {
                throw new IllegalStateException("SHA-256 is unavailable", e);
            }
        }
    }
}
