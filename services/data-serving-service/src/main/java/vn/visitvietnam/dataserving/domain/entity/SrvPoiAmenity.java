package vn.visitvietnam.dataserving.domain.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

/**
 * JPA Entity mapping POI Sector Amenity table {@code srv_poi_amenity}.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "srv_poi_amenity", schema = "apps")
@IdClass(PoiAmenityId.class)
public class SrvPoiAmenity {

    @Id
    @Column(name = "poi_id", nullable = false)
    private String poiId;

    @Id
    @Column(name = "business_sector", nullable = false)
    private String businessSector;

    @Id
    @Column(name = "amenity_group", nullable = false)
    private String amenityGroup;

    @Id
    @Column(name = "amenity_raw", nullable = false)
    private String amenityRaw;

    @Column(name = "amenity")
    private String amenity;

    @Column(name = "amenity_en")
    private String amenityEn;

    @Column(name = "amenity_vi")
    private String amenityVi;

    @Column(name = "service_flags")
    private String serviceFlags;

    @Column(name = "row_hash")
    private String rowHash;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
}

