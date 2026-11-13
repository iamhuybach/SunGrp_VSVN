package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import io.swagger.v3.oas.annotations.media.Schema;
import vn.visitvietnam.dataserving.common.dto.ApiErrorDetail;
import vn.visitvietnam.dataserving.common.dto.ApiMeta;
import vn.visitvietnam.dataserving.common.dto.ApiResponse;

import java.util.List;

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
        @Schema(description = "Nội dung nhận xét đánh giá", example = "Nhan xet mau")
        String reviewText,

        @JsonProperty("review_date")
        @Schema(description = "Thời gian đánh giá", example = "2026-05-15")
        String reviewDate,

        @JsonProperty("source_name")
        @Schema(description = "Nguồn đánh giá", example = "google")
        String sourceName
) {
    @JsonInclude(JsonInclude.Include.ALWAYS)
    public record RatingSummary(
            @JsonProperty("rating_count") Long ratingCount,
            @JsonProperty("rating_avg_score") Double ratingAvgScore) {}

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @JsonPropertyOrder({"success", "code", "message", "data", "rating_summary", "meta", "errors"})
    public record ReviewsResponse(boolean success, int code, String message,
            List<PoiReviewItemResponse> data,
            @JsonProperty("rating_summary") List<RatingSummary> ratingSummary,
            ApiMeta meta, List<ApiErrorDetail> errors) {
        public static ReviewsResponse of(ApiResponse<List<PoiReviewItemResponse>> base, List<RatingSummary> summary) {
            return new ReviewsResponse(base.success(), base.code(), base.message(), base.data(),
                    summary == null ? List.of() : summary, base.meta(), base.errors());
        }
    }
}
