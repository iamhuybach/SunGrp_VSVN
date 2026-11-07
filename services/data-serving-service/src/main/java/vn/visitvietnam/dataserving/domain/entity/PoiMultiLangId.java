package vn.visitvietnam.dataserving.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * Composite Primary Key for {@link SrvPoiMultiLang}.
 * Maps compound key (poi_id, lang).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PoiMultiLangId implements Serializable {

    private String poiId;
    private String lang;
}

