package vn.visitvietnam.dataserving.common.web;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class RequestIdFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String traceId = resolveTraceId(request);

        request.setAttribute(RequestContext.TRACE_ID_KEY, traceId);
        MDC.put(RequestContext.TRACE_ID_KEY, traceId);
        response.setHeader(RequestContext.TRACE_ID_HEADER, traceId);

        try {
            filterChain.doFilter(request, response);
        } finally {
            MDC.remove(RequestContext.TRACE_ID_KEY);
        }
    }

    private String resolveTraceId(HttpServletRequest request) {
        String header = request.getHeader(RequestContext.TRACE_ID_HEADER);
        if (header != null && !header.isBlank()) {
            return header.trim();
        }
        String headerAlt = request.getHeader(RequestContext.TRACE_ID_HEADER_ALT);
        if (headerAlt != null && !headerAlt.isBlank()) {
            return headerAlt.trim();
        }
        return UUID.randomUUID().toString();
    }
}

