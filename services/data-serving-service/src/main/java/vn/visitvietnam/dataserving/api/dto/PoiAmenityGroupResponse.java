package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Nhóm tiện ích của POI")
public record PoiAmenityGroupResponse(
        @JsonProperty("amenity_group")
        @Schema(description = "Mã nhóm tiện ích", example = "facilities_and_services")
        String amenityGroup,

        @JsonProperty("items")
        @Schema(description = "Danh sách các tiện ích trong nhóm")
        List<Item> items
) {

    @JsonInclude(JsonInclude.Include.ALWAYS)
    @Schema(description = "Mục tiện ích chi tiết của POI")
    public record Item(
            @JsonProperty("amenity_code")
            @Schema(description = "Mã tiện ích snake_case", example = "free_street_parking")
            String amenityCode,

            @JsonProperty("service_flags")
            @Schema(description = "Nhóm cờ dịch vụ", example = "Parking")
            String serviceFlags
    ) {}
}
