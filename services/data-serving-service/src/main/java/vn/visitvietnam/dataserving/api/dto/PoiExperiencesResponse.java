package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Tối đa 3 trải nghiệm của một POI")
public record PoiExperiencesResponse(List<Item> items) {
    @JsonInclude(JsonInclude.Include.ALWAYS)
    public record Item(String title, String description, String source) {}
}
