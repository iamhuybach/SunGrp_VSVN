package vn.visitvietnam.dataserving.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * Composite Primary Key for {@link SrvPoiMediaGallery}.
 * Maps compound key (media_id, poi_id), the NodeSpec pk of gld_srv_poi_media_gallery.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PoiMediaGalleryId implements Serializable {

    private String mediaId;
    private String poiId;
}
