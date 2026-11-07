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
 * JPA Entity mapping POI Multi-Language table {@code srv_poi_multi_lang}.
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "srv_poi_multi_lang", schema = "apps")
@IdClass(PoiMultiLangId.class)
public class SrvPoiMultiLang {

    @Id
    @Column(name = "poi_id", nullable = false)
    private String poiId;

    @Id
    @Column(name = "lang", nullable = false)
    private String lang;

    @Column(name = "source_name")
    private String sourceName;

    @Column(name = "time_to_spend")
    private String timeToSpend;

    @Column(name = "best_time")
    private String bestTime;

    @Column(name = "cost_vnd")
    private String costVnd;

    @Column(name = "description")
    private String description;

    @Column(name = "experience")
    private String experience;

    @Column(name = "row_hash")
    private String rowHash;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
}

