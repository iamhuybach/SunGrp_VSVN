package vn.visitvietnam.dataserving.domain.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * JPA Entity mapping POI Master Serving Info table {@code srv_poi_info}.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "srv_poi_info", schema = "apps")
public class SrvPoiInfo {

    @Id
    @Column(name = "poi_id", nullable = false)
    private String poiId;

    @Column(name = "poi_name")
    private String poiName;

    @Column(name = "source_name")
    private String sourceName;

    @Column(name = "business_sector")
    private String businessSector;

    @Column(name = "business_category")
    private String businessCategory;

    @Column(name = "subcategory_tags")
    private String subcategoryTags;

    @Column(name = "destination_id")
    private String destinationId;

    @Column(name = "destination_name")
    private String destinationName;

    @Column(name = "full_address")
    private String fullAddress;

    @Column(name = "street")
    private String street;

    @Column(name = "ward")
    private String ward;

    @Column(name = "district")
    private String district;

    @Column(name = "city")
    private String city;

    @Column(name = "country_code")
    private String countryCode;

    @Column(name = "postal_code")
    private String postalCode;

    @Column(name = "lat")
    private Double lat;

    @Column(name = "lng")
    private Double lng;

    @Column(name = "phone")
    private String phone;

    @Column(name = "email")
    private String email;

    @Column(name = "website_url")
    private String websiteUrl;

    @Column(name = "operating_status")
    private String operatingStatus;

    @Column(name = "is_verified")
    private Boolean isVerified;

    @Column(name = "is_recommended")
    private Boolean isRecommended;

    @Column(name = "is_bookable")
    private Boolean isBookable;

    @Column(name = "operating_hours")
    private String operatingHours;

    @Column(name = "holiday_exceptions")
    private String holidayExceptions;

    @Column(name = "rating_overall", precision = 4, scale = 2)
    private BigDecimal ratingOverall;

    @Column(name = "rating_count")
    private Integer ratingCount;

    @Column(name = "review_count")
    private Integer reviewCount;

    @Column(name = "cover_id")
    private String coverId;

    @Column(name = "cover_blob_url")
    private String coverBlobUrl;

    @Column(name = "row_hash")
    private String rowHash;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
}

