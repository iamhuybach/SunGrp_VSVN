package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonRawValue;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

@JsonInclude(JsonInclude.Include.ALWAYS)
@Schema(description = "Thông tin thực tế của một POI")
public record PoiPracticalInfoResponse(
        String id,
        String name,
        String description,
        @JsonProperty("business_sector") String businessSector,
        @JsonProperty("time_to_spend") LabelValue timeToSpend,
        LabelValue cost,
        @JsonProperty("best_time") LabelValue bestTime,
        Cover cover,
        Ratings ratings,
        @JsonProperty("business_tags") BusinessTags businessTags,
        Status status,
        @JsonProperty("operating_hours") OperatingHours operatingHours,
        @JsonRawValue
        @JsonProperty("holiday_exceptions")
        @Schema(
                types = {"array", "null"},
                description = "Mảng JSON nguyên từ apps.srv_poi_info.holiday_exceptions. JSON hỏng thì null. Không đổi khóa bên trong."
        )
        String holidayExceptions,
        CompactPoiResponse.Address address,
        @JsonProperty("geo_location") CompactPoiResponse.GeoLocation geoLocation,
        String phone,
        String email,
        @JsonProperty("website_url") String websiteUrl,
        Destinations destinations
) {
    public record LabelValue(String label, String value) {}

    public record Cover(
            @JsonProperty("id") String id,
            @JsonProperty("file_key") String fileKey
    ) {}

    public record Ratings(
            String source,
            @JsonProperty("ratings_count") Integer ratingsCount,
            @JsonProperty("ratings_avg_score") Double ratingsAvgScore
    ) {}

    public record BusinessTags(
            @JsonProperty("business_sector") String businessSector,
            @JsonProperty("business_category") String businessCategory
    ) {}

    public record Status(
            @JsonProperty("operating_status") String operatingStatus,
            @JsonProperty("is_verified") Boolean isVerified,
            @JsonProperty("is_recommended") Boolean isRecommended,
            @JsonProperty("is_bookable") Boolean isBookable
    ) {}

    public record OperatingHours(List<PoiFeatureResponse.OperatingHour> value) {}

    public record Destinations(String id) {}
}
