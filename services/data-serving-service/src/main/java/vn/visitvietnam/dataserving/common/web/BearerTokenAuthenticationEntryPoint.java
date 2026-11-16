package vn.visitvietnam.dataserving.common.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.access.AccessDeniedHandler;
import vn.visitvietnam.dataserving.common.dto.ApiResponse;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

public final class BearerTokenAuthenticationEntryPoint implements AuthenticationEntryPoint, AccessDeniedHandler {

    static final String MESSAGE = "Missing or invalid bearer token.";
    static final String ERROR_CODE = "ERR_UNAUTHORIZED";
    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException)
            throws IOException {
        writeUnauthorized(response);
    }

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response, AccessDeniedException accessDeniedException)
            throws IOException {
        writeUnauthorized(response);
    }

    private void writeUnauthorized(HttpServletResponse response) throws IOException {
        if (response.isCommitted()) {
            return;
        }
        ApiResponse<Void> body = ApiResponse.error(HttpStatus.UNAUTHORIZED, MESSAGE, ERROR_CODE, null);
        response.setStatus(HttpStatus.UNAUTHORIZED.value());
        response.setHeader(HttpHeaders.WWW_AUTHENTICATE, "Bearer");
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.getOutputStream().write(MAPPER.writeValueAsBytes(body));
    }
}
