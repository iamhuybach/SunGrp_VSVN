package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

/**
 * Spring Data JPA Repository for {@link SrvPoiInfo}.
 */
@Repository
public interface SrvPoiInfoRepository extends JpaRepository<SrvPoiInfo, String>, JpaSpecificationExecutor<SrvPoiInfo> {

    String FEATURE_WHERE = " i.deleted_at IS NULL"
            + " AND lower(trim(i.business_sector)) = ANY (string_to_array(:sectorsCsv, ','))"
            + " AND ( i.is_recommended IS TRUE"
            + " OR ( i.rating_overall >= :minRating"
            + " AND i.rating_count >= :minReviewCount"
            + " AND (:ratingSource = '' OR lower(trim(i.source_name)) = :ratingSource) ) )";

    boolean existsByPoiIdAndDeletedAtIsNull(String poiId);

    Optional<SrvPoiInfo> findByPoiIdAndDeletedAtIsNull(String poiId);

    @Query(nativeQuery = true, value = """
            SELECT c.poi_id FROM (
              SELECT i.poi_id,
                     array_position(string_to_array(:sectorsCsv, ','), lower(trim(i.business_sector))) AS sector_rank,
                     row_number() OVER (PARTITION BY lower(trim(i.business_sector))
                         ORDER BY CASE WHEN i.is_recommended IS TRUE THEN 0 ELSE 1 END,
                                  i.rating_overall DESC NULLS LAST, i.rating_count DESC NULLS LAST, i.poi_id) AS sector_seq
              FROM apps.srv_poi_info i WHERE""" + FEATURE_WHERE + """
            ) c ORDER BY c.sector_seq, c.sector_rank, c.poi_id
            LIMIT :limit OFFSET :offset
            """)
    List<String> findFeatureIds(@Param("sectorsCsv") String sectorsCsv, @Param("minRating") BigDecimal minRating,
            @Param("minReviewCount") int minReviewCount, @Param("ratingSource") String ratingSource,
            @Param("limit") int limit, @Param("offset") long offset);

    @Query(nativeQuery = true, value = "SELECT count(*) FROM apps.srv_poi_info i WHERE " + FEATURE_WHERE)
    long countFeatures(@Param("sectorsCsv") String sectorsCsv, @Param("minRating") BigDecimal minRating,
            @Param("minReviewCount") int minReviewCount, @Param("ratingSource") String ratingSource);
}
