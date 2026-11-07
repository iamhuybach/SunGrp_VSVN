package vn.visitvietnam.dataserving.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;
import org.springframework.http.HttpStatus;
import vn.visitvietnam.dataserving.common.web.RequestContext;

import java.time.Instant;
import java.util.Collections;
import java.util.List;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Vỏ bọc phản hồi API chuẩn toàn hệ thống")
public record ApiResponse<T>(
        @Schema(description = "Trạng thái thành công của yêu cầu", example = "true")
        boolean success,

        @Schema(description = "Mã HTTP Status Code tương ứng", example = "200")
        int code,

        @Schema(description = "Thông điệp mô tả trạng thái phản hồi", example = "Resource retrieved successfully")
        String message,

        @Schema(description = "Dữ liệu nghiệp vụ chính (luôn null khi lỗi)")
        T data,

        @Schema(description = "Dữ liệu bổ trợ kỹ thuật")
        ApiMeta meta,

        @Schema(description = "Chi tiết các lỗi con (luôn null khi thành công)")
        List<ApiErrorDetail> errors
) {

    public static <T> ApiResponse<T> success(T data, String message) {
        String traceId = RequestContext.getTraceId();
        String timestamp = Instant.now().toString();
        ApiMeta meta = new ApiMeta(timestamp, traceId, null, null);
        return new ApiResponse<>(true, HttpStatus.OK.value(), message, data, meta, null);
    }

    public static <T> ApiResponse<List<T>> successList(List<T> data, PaginationMeta pagination, String message) {
        String traceId = RequestContext.getTraceId();
        String timestamp = Instant.now().toString();
        ApiMeta meta = new ApiMeta(timestamp, traceId, null, pagination);
        List<T> payload = (data != null) ? data : Collections.emptyList();
        return new ApiResponse<>(true, HttpStatus.OK.value(), message, payload, meta, null);
    }

    public static <T> ApiResponse<T> created(T data, String message) {
        String traceId = RequestContext.getTraceId();
        String timestamp = Instant.now().toString();
        ApiMeta meta = new ApiMeta(timestamp, traceId, null, null);
        return new ApiResponse<>(true, HttpStatus.CREATED.value(), message, data, meta, null);
    }

    public static <T> ApiResponse<T> error(HttpStatus status, String message, String errorCode, List<ApiErrorDetail> errors) {
        String traceId = RequestContext.getTraceId();
        String timestamp = Instant.now().toString();
        ApiMeta meta = new ApiMeta(timestamp, traceId, errorCode, null);
        return new ApiResponse<>(false, status.value(), message, null, meta, errors);
    }

    public static <T> ApiResponse<T> error(HttpStatus status, String message, String errorCode) {
        return error(status, message, errorCode, null);
    }
}
