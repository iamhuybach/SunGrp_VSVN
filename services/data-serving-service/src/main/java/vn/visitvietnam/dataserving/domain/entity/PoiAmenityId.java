package vn.visitvietnam.dataserving.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * Composite Primary Key for {@link SrvPoiAmenity}.
 * Maps compound key (poi_id, business_sector, amenity_group, amenity_raw).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PoiAmenityId implements Serializable {

    private String poiId;
    private String businessSector;
    private String amenityGroup;
    private String amenityRaw;
}

