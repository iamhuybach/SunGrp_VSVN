package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

/**
 * DTO dữ liệu rút gọn của POI phục vụ danh sách / feed theo đúng chuẩn Confluence spec (API 1).
 * Giữ nguyên đầy đủ schema contract các trường và hiển thị giá trị null khi không có dữ liệu.
 */
@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Thông tin tóm tắt rút gọn của POI phục vụ danh sách / feed")
public record CompactPoiResponse(
        @Schema(description = "Mã định danh duy nhất của POI", example = "poi_01jk9a7b8c")
        String id,

        @Schema(description = "Tên địa điểm", example = "Nhà hát Lớn Hà Nội")
        String name,

        @Schema(description = "Mô tả tóm tắt địa điểm", example = "Công trình kiến trúc lịch sử nổi bật tại trung tâm thủ đô.")
        String description,

        @Schema(description = "Ảnh đại diện")
        Cover cover,

        @Schema(description = "Điểm xếp hạng tổng thể")
        Rating rating,

        @JsonProperty("business_tags")
        @Schema(description = "Thông tin phân loại ngành nghề")
        BusinessTags businessTags,

        @Schema(description = "Địa chỉ hành chính")
        Address address,

        @JsonProperty("geo_location")
        @Schema(description = "Tọa độ địa lý")
        GeoLocation geoLocation
) {

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Ảnh đại diện (Cover) của POI")
    public record Cover(
            @JsonProperty("id")
            @Schema(description = "Mã định danh media ảnh cover", example = "med_01jk9a7b")
            String mediaId,

            @JsonProperty("file_key")
            @Schema(description = "URL / key ảnh CDN", example = "https://cdn.visitvietnam.gov.vn/media/pois/cover_01.jpg")
            String fileKey,

            @Schema(description = "Chiều rộng pixel", example = "1920")
            Integer width,

            @Schema(description = "Chiều cao pixel", example = "1080")
            Integer height,

            @JsonProperty("mime_type")
            @Schema(description = "Mime type", example = "image/jpeg")
            String mimeType,

            @JsonProperty("blur_hash")
            @Schema(description = "BlurHash đại diện ảnh mờ khi tải", example = "LEHV6nWB2yk8pyo0adR*.7kCMdnj")
            String blurHash
    ) {
        public Cover(String mediaId, String fileKey, Integer width, Integer height, String mimeType) {
            this(mediaId, fileKey, width, height, mimeType, null);
        }
    }

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Tổng hợp xếp hạng đánh giá của POI")
    public record Rating(
            @JsonProperty("ratings_avg_score")
            @Schema(description = "Điểm đánh giá trung bình", example = "4.8")
            Double ratingsAvgScore,

            @JsonProperty("ratings_count")
            @Schema(description = "Tổng số lượt đánh giá", example = "1250")
            Integer ratingsCount
    ) {
        public Double overall() { return ratingsAvgScore; }
        public Integer ratingCount() { return ratingsCount; }
    }

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Thẻ ngành nghề kinh doanh và phân loại POI")
    public record BusinessTags(
            @JsonProperty("business_sector")
            @Schema(description = "Mã ngành chính / sector", example = "tour_n_activities")
            String businessSector,

            @JsonProperty("business_sector_label")
            @Schema(description = "Nhãn hiển thị tiếng Việt của ngành chính", example = "Tour & Hoạt động")
            String businessSectorLabel,

            @JsonProperty("business_category")
            @Schema(description = "Mã phân loại chi tiết", example = "attraction")
            String businessCategory,

            @JsonProperty("subcategory_tags")
            @Schema(description = "Danh sách thẻ phân loại chi tiết")
            List<String> subcategoryTags
    ) {
        public String primaryCategory() { return businessCategory != null ? businessCategory : businessSector; }
        public String primaryCategoryLabel() { return businessSectorLabel; }
        public List<String> subcategories() { return subcategoryTags; }
    }

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Thông tin địa chỉ chi tiết của POI")
    public record Address(
            @JsonProperty("full_address")
            @Schema(description = "Địa chỉ đầy đủ", example = "Tràng Tiền, Quận Hoàn Kiếm, Hà Nội")
            String fullAddress,

            @Schema(description = "Tên đường phố", example = "Tràng Tiền")
            String street,

            @Schema(description = "Phường / Xã", example = "Phường Tràng Tiền")
            String ward,

            @Schema(description = "Quận / Huyện", example = "Quận Hoàn Kiếm")
            String district,

            @Schema(description = "Tỉnh / Thành phố", example = "Hà Nội")
            String city,

            @JsonProperty("country_code")
            @Schema(description = "Mã quốc gia ISO", example = "VN")
            String countryCode
    ) {}

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Tọa độ địa lý WGS-84")
    public record GeoLocation(
            @Schema(description = "Vĩ độ (Latitude)", example = "21.028511")
            Double latitude,

            @Schema(description = "Kinh độ (Longitude)", example = "105.854444")
            Double longitude
    ) {
        public Double lat() { return latitude; }
        public Double lng() { return longitude; }
    }
}
