package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Mục media gallery trong thư viện ảnh của POI")
public record PoiGalleryItemResponse(
        @JsonProperty("id")
        @Schema(description = "apps.srv_poi_media_gallery.media_id", example = "med_01jk9a7b")
        String id,

        @JsonProperty("file_key")
        @Schema(description = "apps.srv_poi_media_gallery.blob_url", example = "pois/mau/1.jpg")
        String fileKey,

        @JsonProperty("display_order")
        @Schema(description = "apps.srv_poi_media_gallery.display_order", example = "1")
        Integer displayOrder
) {}
