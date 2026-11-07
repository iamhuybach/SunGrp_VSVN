package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Nhóm tiện ích của POI")
public record PoiAmenityGroupResponse(
        @JsonProperty("amenity_group")
        @Schema(description = "Mã nhóm tiện ích", example = "FACILITY")
        String amenityGroup,

        @JsonProperty("amenity_vi")
        @Schema(description = "Tên nhóm tiếng Việt", example = "Tiện nghi cơ sở")
        String amenityVi,

        @Schema(description = "Danh sách các tiện ích trong nhóm")
        List<Item> items
) {

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Mục tiện ích chi tiết của POI")
    public record Item(
            @JsonProperty("amenity_code")
            @Schema(description = "Mã tiện ích chuẩn", example = "parking")
            String amenityCode,

            @JsonProperty("amenity_label")
            @Schema(description = "Tên hiển thị tiếng Việt của tiện ích", example = "Bãi đỗ xe")
            String amenityLabel,

            @JsonProperty("service_flags")
            @Schema(description = "Đặc tính dịch vụ (vd: free, paid)", example = "free")
            String serviceFlags
    ) {}
}
