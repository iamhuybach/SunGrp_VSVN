package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.PoiMediaGalleryId;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiMediaGallery;

import java.util.List;

/**
 * Spring Data JPA Repository for {@link SrvPoiMediaGallery}.
 */
@Repository
public interface SrvPoiMediaGalleryRepository extends JpaRepository<SrvPoiMediaGallery, PoiMediaGalleryId> {

    String ACTIVE = "m.poiId = :poiId AND (m.isActive IS NULL OR m.isActive = true) AND m.deletedAt IS NULL";

    @Query(value = "SELECT m FROM SrvPoiMediaGallery m WHERE " + ACTIVE
            + " ORDER BY m.displayOrder ASC NULLS LAST, m.mediaId ASC",
            countQuery = "SELECT count(m) FROM SrvPoiMediaGallery m WHERE " + ACTIVE)
    Page<SrvPoiMediaGallery> findActivePageByPoiId(@Param("poiId") String poiId, Pageable pageable);

    @Query("SELECT m FROM SrvPoiMediaGallery m WHERE " + ACTIVE + " AND m.isCover = true"
            + " ORDER BY m.displayOrder ASC NULLS LAST, m.mediaId ASC")
    List<SrvPoiMediaGallery> findActiveCoverByPoiId(@Param("poiId") String poiId, Pageable pageable);
}
