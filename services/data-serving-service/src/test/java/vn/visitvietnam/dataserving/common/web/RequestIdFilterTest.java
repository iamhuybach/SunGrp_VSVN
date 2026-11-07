package vn.visitvietnam.dataserving.common.web;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import java.io.IOException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class RequestIdFilterTest {

    private final RequestIdFilter filter = new RequestIdFilter();

    @Test
    @DisplayName("Sử dụng X-Request-Id từ client khi có header")
    void shouldUseProvidedRequestId() throws ServletException, IOException {
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("X-Request-Id", "test-req-12345");
        MockHttpServletResponse response = new MockHttpServletResponse();
        MockFilterChain filterChain = new MockFilterChain() {
            @Override
            public void doFilter(ServletRequest req, ServletResponse res) {
                assertThat(req.getAttribute(RequestContext.TRACE_ID_KEY)).isEqualTo("test-req-12345");
                assertThat(MDC.get(RequestContext.TRACE_ID_KEY)).isEqualTo("test-req-12345");
            }
        };

        filter.doFilter(request, response, filterChain);

        assertThat(response.getHeader("X-Request-Id")).isEqualTo("test-req-12345");
        assertThat(MDC.get(RequestContext.TRACE_ID_KEY)).isNull();
    }

    @Test
    @DisplayName("Sử dụng X-Request-ID (case alt) từ client khi có header")
    void shouldUseProvidedRequestIdAlt() throws ServletException, IOException {
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("X-Request-ID", "alt-req-99999");
        MockHttpServletResponse response = new MockHttpServletResponse();
        MockFilterChain filterChain = new MockFilterChain() {
            @Override
            public void doFilter(ServletRequest req, ServletResponse res) {
                assertThat(req.getAttribute(RequestContext.TRACE_ID_KEY)).isEqualTo("alt-req-99999");
                assertThat(MDC.get(RequestContext.TRACE_ID_KEY)).isEqualTo("alt-req-99999");
            }
        };

        filter.doFilter(request, response, filterChain);

        assertThat(response.getHeader("X-Request-Id")).isEqualTo("alt-req-99999");
        assertThat(MDC.get(RequestContext.TRACE_ID_KEY)).isNull();
    }

    @Test
    @DisplayName("Tự sinh UUID khi client không truyền header X-Request-Id")
    void shouldGenerateUuidWhenHeaderMissing() throws ServletException, IOException {
        MockHttpServletRequest request = new MockHttpServletRequest();
        MockHttpServletResponse response = new MockHttpServletResponse();
        MockFilterChain filterChain = new MockFilterChain() {
            @Override
            public void doFilter(ServletRequest req, ServletResponse res) {
                Object traceId = req.getAttribute(RequestContext.TRACE_ID_KEY);
                assertThat(traceId).isNotNull();
                assertThat(traceId.toString()).isNotBlank();
                assertThat(MDC.get(RequestContext.TRACE_ID_KEY)).isEqualTo(traceId.toString());
            }
        };

        filter.doFilter(request, response, filterChain);

        String generatedId = response.getHeader("X-Request-Id");
        assertThat(generatedId).isNotBlank();
        assertThat(MDC.get(RequestContext.TRACE_ID_KEY)).isNull();
    }

    @Test
    @DisplayName("Xóa MDC ngay cả khi filterChain ném exception")
    void shouldCleanMdcOnException() {
        MockHttpServletRequest request = new MockHttpServletRequest();
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain throwingChain = (req, res) -> {
            throw new RuntimeException("Simulated error");
        };

        assertThatThrownBy(() -> filter.doFilter(request, response, throwingChain))
                .isInstanceOf(RuntimeException.class)
                .hasMessage("Simulated error");

        assertThat(MDC.get(RequestContext.TRACE_ID_KEY)).isNull();
    }
}

