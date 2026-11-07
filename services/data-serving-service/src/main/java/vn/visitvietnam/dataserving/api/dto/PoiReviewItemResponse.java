package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Bản ghi đánh giá thô của POI")
public record PoiReviewItemResponse(
        @JsonProperty("review_id")
        @Schema(description = "Mã định danh đánh giá", example = "rev_01jk9a7b")
        String reviewId,

        @JsonProperty("author_name")
        @Schema(description = "Tên tác giả đánh giá", example = "Nguyễn Văn A")
        String authorName,

        @Schema(description = "Điểm đánh giá thang 5", example = "4.5")
        Double rating,

        @JsonProperty("review_text")
        @Schema(description = "Nội dung nhận xét đánh giá", example = "Không gian tuyệt đẹp, kiến trúc cổ kính tráng lệ.")
        String reviewText,

        @JsonProperty("review_date")
        @Schema(description = "Thời gian đánh giá (chuỗi ngày hoặc timestamp)", example = "2026-05-15")
        String reviewDate
) {}

