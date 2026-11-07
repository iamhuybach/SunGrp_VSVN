package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Mục media gallery trong thư viện ảnh của POI")
public record PoiGalleryItemResponse(
        @JsonProperty("id")
        @Schema(description = "Mã định danh ảnh", example = "med_01jk9a7b")
        String mediaId,

        @JsonProperty("file_key")
        @Schema(description = "URL CDN ảnh", example = "https://cdn.visitvietnam.gov.vn/media/pois/img_1.jpg")
        String fileKey,

        @Schema(description = "Chiều rộng pixel", example = "1920")
        Integer width,

        @Schema(description = "Chiều cao pixel", example = "1080")
        Integer height,

        @JsonProperty("mime_type")
        @Schema(description = "Định dạng file media", example = "image/jpeg")
        String mimeType,

        @JsonProperty("blur_hash")
        @Schema(description = "BlurHash đại diện ảnh mờ khi tải", example = "LEHV6nWB2yk8pyo0adR*.7kCMdnj")
        String blurHash,

        @JsonProperty("display_order")
        @Schema(description = "Thứ tự hiển thị", example = "1")
        Integer displayOrder
) {
    public PoiGalleryItemResponse(String mediaId, String fileKey, Integer width, Integer height, String mimeType, Integer displayOrder) {
        this(mediaId, fileKey, width, height, mimeType, null, displayOrder);
    }

    public String id() {
        return mediaId;
    }
}

