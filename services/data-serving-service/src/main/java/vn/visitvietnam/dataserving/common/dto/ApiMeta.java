package vn.visitvietnam.dataserving.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "Metadata kỹ thuật bổ trợ cho phản hồi")
public record ApiMeta(
        @Schema(description = "Thời gian phản hồi định dạng ISO 8601 UTC", example = "2026-11-05T06:30:00Z")
        String timestamp,

        @JsonProperty("trace_id")
        @Schema(description = "Mã định danh truy vết phân tán (từ X-Request-Id)", example = "req_8a12bc4e")
        String traceId,

        @JsonProperty("error_code")
        @Schema(description = "Mã lỗi nghiệp vụ / kỹ thuật chuẩn hóa", example = "POI_NOT_FOUND")
        String errorCode,

        @Schema(description = "Thông tin phân trang danh sách (nếu có)")
        PaginationMeta pagination
) {}

