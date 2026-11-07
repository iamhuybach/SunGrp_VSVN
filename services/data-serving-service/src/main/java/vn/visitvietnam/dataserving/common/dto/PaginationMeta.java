package vn.visitvietnam.dataserving.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "Thông tin phân trang danh sách")
public record PaginationMeta(
        @Schema(description = "Loại phân trang (offset hoặc keyset)", example = "offset")
        String type,

        @Schema(description = "Số thứ tự trang hiện tại", example = "0")
        Integer page,

        @JsonProperty("per_page")
        @Schema(description = "Số phần tử trên mỗi trang", example = "20")
        Integer perPage,

        @JsonProperty("total_items")
        @Schema(description = "Tổng số phần tử thỏa mãn điều kiện", example = "145")
        Long totalItems,

        @JsonProperty("total_pages")
        @Schema(description = "Tổng số trang", example = "8")
        Integer totalPages,

        @JsonProperty("has_next")
        @Schema(description = "Có trang kế tiếp hay không", example = "true")
        Boolean hasNext,

        @JsonProperty("has_prev")
        @Schema(description = "Có trang phía trước hay không", example = "false")
        Boolean hasPrev
) {
    public static PaginationMeta offset(int page, int perPage, long totalItems) {
        int totalPages = perPage > 0 ? (int) Math.ceil((double) totalItems / perPage) : 0;
        boolean hasNext = totalItems > 0 && page < totalPages - 1;
        boolean hasPrev = page > 0;
        return new PaginationMeta("offset", page, perPage, totalItems, totalPages, hasNext, hasPrev);
    }
}

