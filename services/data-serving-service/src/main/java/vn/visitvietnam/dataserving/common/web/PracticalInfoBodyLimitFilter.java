package vn.visitvietnam.dataserving.common.web;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ReadListener;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletInputStream;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import vn.visitvietnam.dataserving.common.dto.ApiResponse;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

/**
 * Chặn body POST practical_info trước khi Jackson đọc. Trần đủ cho 500 id dài 128 ký tự.
 */
@Component
@Order(Ordered.LOWEST_PRECEDENCE)
public class PracticalInfoBodyLimitFilter extends OncePerRequestFilter {

    public static final int MAX_BYTES = 96 * 1024;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !"POST".equalsIgnoreCase(request.getMethod())
                || !"/api/v1/pois/practical_info".equals(request.getRequestURI());
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        long declared = request.getContentLengthLong();
        if (declared > MAX_BYTES) {
            writeTooLarge(response);
            return;
        }
        byte[] body = readAtMost(request, MAX_BYTES);
        if (body == null) {
            writeTooLarge(response);
            return;
        }
        filterChain.doFilter(new CachedBodyRequest(request, body), response);
    }

    private static byte[] readAtMost(HttpServletRequest request, int maxBytes) throws IOException {
        byte[] buffer = new byte[maxBytes + 1];
        int offset = 0;
        try (ServletInputStream input = request.getInputStream()) {
            while (offset <= maxBytes) {
                int read = input.read(buffer, offset, maxBytes + 1 - offset);
                if (read < 0) {
                    break;
                }
                offset += read;
            }
        }
        if (offset > maxBytes) {
            return null;
        }
        byte[] exact = new byte[offset];
        System.arraycopy(buffer, 0, exact, 0, offset);
        return exact;
    }

    private void writeTooLarge(HttpServletResponse response) throws IOException {
        response.setStatus(HttpStatus.BAD_REQUEST.value());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        objectMapper.writeValue(response.getWriter(), ApiResponse.error(
                HttpStatus.BAD_REQUEST, "Request body is too large.", "ERR_BODY_TOO_LARGE"));
    }

    private static final class CachedBodyRequest extends HttpServletRequestWrapper {
        private final byte[] body;

        private CachedBodyRequest(HttpServletRequest request, byte[] body) {
            super(request);
            this.body = body;
        }

        @Override
        public ServletInputStream getInputStream() {
            ByteArrayInputStream input = new ByteArrayInputStream(body);
            return new ServletInputStream() {
                @Override
                public boolean isFinished() {
                    return input.available() == 0;
                }

                @Override
                public boolean isReady() {
                    return true;
                }

                @Override
                public void setReadListener(ReadListener readListener) {
                    // MockMvc và servlet container đọc đồng bộ.
                }

                @Override
                public int read() {
                    return input.read();
                }
            };
        }

        @Override
        public BufferedReader getReader() {
            return new BufferedReader(new InputStreamReader(getInputStream(), StandardCharsets.UTF_8));
        }

        @Override
        public int getContentLength() {
            return body.length;
        }

        @Override
        public long getContentLengthLong() {
            return body.length;
        }
    }
}
