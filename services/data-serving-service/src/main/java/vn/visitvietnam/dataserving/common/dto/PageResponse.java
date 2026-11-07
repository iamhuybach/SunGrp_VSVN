package vn.visitvietnam.dataserving.common.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

@Schema(description = "Đối tượng phân trang dữ liệu chuẩn")
public record PageResponse<T>(
        @Schema(description = "Danh sách phần tử của trang hiện tại")
        List<T> content,

        @Schema(description = "Số thứ tự trang (bắt đầu từ 0)", example = "0")
        int page,

        @Schema(description = "Kích thước mỗi trang", example = "10")
        int size,

        @Schema(description = "Tổng số phần tử trên toàn bộ các trang", example = "42")
        long totalElements,

        @Schema(description = "Tổng số trang", example = "5")
        int totalPages,

        @Schema(description = "Đã là trang cuối cùng hay chưa", example = "false")
        boolean last
) {
    public static <T> PageResponse<T> of(List<T> content, int page, int size, long totalElements) {
        int totalPages = size > 0 ? (int) Math.ceil((double) totalElements / size) : 0;
        boolean last = page >= totalPages - 1 || totalElements == 0;
        return new PageResponse<>(content, page, size, totalElements, totalPages, last);
    }
}

