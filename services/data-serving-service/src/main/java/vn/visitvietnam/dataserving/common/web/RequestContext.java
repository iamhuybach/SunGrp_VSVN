package vn.visitvietnam.dataserving.common.web;

import org.slf4j.MDC;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.UUID;

public final class RequestContext {

    public static final String TRACE_ID_HEADER = "X-Request-Id";
    public static final String TRACE_ID_HEADER_ALT = "X-Request-ID";
    public static final String TRACE_ID_KEY = "trace_id";

    private RequestContext() {}

    public static String getTraceId() {
        RequestAttributes attributes = RequestContextHolder.getRequestAttributes();
        if (attributes instanceof ServletRequestAttributes servletAttributes) {
            Object attr = servletAttributes.getRequest().getAttribute(TRACE_ID_KEY);
            if (attr instanceof String traceId && !traceId.isBlank()) {
                return traceId;
            }
        }
        String mdcTrace = MDC.get(TRACE_ID_KEY);
        if (mdcTrace != null && !mdcTrace.isBlank()) {
            return mdcTrace;
        }
        return UUID.randomUUID().toString();
    }
}

