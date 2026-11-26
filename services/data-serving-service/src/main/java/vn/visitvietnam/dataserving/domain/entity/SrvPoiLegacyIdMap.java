package vn.visitvietnam.dataserving.domain.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.Immutable;

import java.time.LocalDateTime;

/**
 * Bản đọc của {@code lh_vv_gold.dbo.gld_poi_legacy_id_map}. Khóa chính là MERGE key {@code lgpmain}.
 */
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Immutable
@Entity
@Table(name = "srv_poi_legacy_id_map", schema = "apps")
public class SrvPoiLegacyIdMap {

    @Id
    @Column(name = "legacy_poi_id", nullable = false)
    private String legacyPoiId;

    @Column(name = "poi_id")
    private String poiId;

    @Column(name = "poi_id_status", nullable = false)
    private String poiIdStatus;

    @Column(name = "ingestion_ts")
    private LocalDateTime ingestionTs;
}
