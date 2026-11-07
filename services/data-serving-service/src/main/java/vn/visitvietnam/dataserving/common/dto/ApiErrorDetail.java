package vn.visitvietnam.dataserving.common.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Chi tiết lỗi kiểm tra dữ liệu đầu vào")
public record ApiErrorDetail(
        @Schema(description = "Tên trường vi phạm", example = "email")
        String field,

        @Schema(description = "Mã lỗi chuẩn hóa", example = "INVALID_FORMAT")
        String code,

        @Schema(description = "Mô tả thông báo lỗi", example = "The email must be a valid email address.")
        String message
) {}

