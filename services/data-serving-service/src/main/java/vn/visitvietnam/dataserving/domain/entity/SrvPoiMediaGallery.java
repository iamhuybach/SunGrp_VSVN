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
 * JPA Entity mapping POI Media Gallery table {@code srv_poi_media_gallery}.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "srv_poi_media_gallery", schema = "apps")
@IdClass(PoiMediaGalleryId.class)
public class SrvPoiMediaGallery {

    @Id
    @Column(name = "media_id", nullable = false)
    private String mediaId;

    @Id
    @Column(name = "poi_id", nullable = false)
    private String poiId;

    @Column(name = "source_name")
    private String sourceName;

    @Column(name = "photo_api_uri")
    private String photoApiUri;

    @Column(name = "display_order")
    private Integer displayOrder;

    @Column(name = "width_px")
    private Integer widthPx;

    @Column(name = "height_px")
    private Integer heightPx;

    @Column(name = "photographer")
    private String photographer;

    @Column(name = "blob_url")
    private String blobUrl;

    @Column(name = "thumbnail_url")
    private String thumbnailUrl;

    @Column(name = "is_cover")
    private Boolean isCover;

    @Column(name = "is_active")
    private Boolean isActive;

    @Column(name = "row_hash")
    private String rowHash;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
}

