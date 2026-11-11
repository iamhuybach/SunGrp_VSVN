package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "POI nổi bật")
public record PoiFeatureResponse(
        String id,
        String name,
        String description,
        Cover cover,
        List<Rating> ratings,
        @JsonProperty("business_tags") BusinessTags businessTags,
        Status status,
        @JsonProperty("operating_hours") List<OperatingHour> operatingHours,
        CompactPoiResponse.Address address,
        @JsonProperty("geo_location") CompactPoiResponse.GeoLocation geoLocation
) {
    public record Cover(
            @JsonProperty("id") String id,
            @JsonProperty("file_key") String fileKey
    ) {}

    public record Rating(
            String source,
            @JsonProperty("ratings_count") Integer ratingsCount,
            @JsonProperty("ratings_avg_score") Double ratingsAvgScore
    ) {}

    public record BusinessTags(
            @JsonProperty("business_sector") String businessSector,
            @JsonProperty("business_category") String businessCategory,
            @JsonProperty("subcategory_tags") List<String> subcategoryTags
    ) {}

    public record Status(
            @JsonProperty("operating_status") String operatingStatus,
            @JsonProperty("is_verified") Boolean isVerified,
            @JsonProperty("is_recommended") Boolean isRecommended,
            @JsonProperty("is_bookable") Boolean isBookable
    ) {}

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record OperatingHour(
            @JsonProperty("day_of_week") Integer dayOfWeek,
            @JsonProperty("open_time") String openTime,
            @JsonProperty("close_time") String closeTime,
            @JsonProperty("is_open_all_day") Boolean isOpenAllDay,
            @JsonProperty("is_closed") Boolean isClosed
    ) {}
}
