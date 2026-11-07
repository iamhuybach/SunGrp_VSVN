package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.PoiMediaGalleryId;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiMediaGallery;

import java.util.Collection;
import java.util.List;

/**
 * Spring Data JPA Repository for {@link SrvPoiMediaGallery}.
 */
@Repository
public interface SrvPoiMediaGalleryRepository extends JpaRepository<SrvPoiMediaGallery, PoiMediaGalleryId> {

    @Query("SELECT m FROM SrvPoiMediaGallery m WHERE m.poiId IN :poiIds AND (m.isActive IS NULL OR m.isActive = true) AND m.deletedAt IS NULL ORDER BY m.displayOrder ASC")
    List<SrvPoiMediaGallery> findActiveByPoiIdInOrderByDisplayOrderAsc(@Param("poiIds") Collection<String> poiIds);

    @Query("SELECT m FROM SrvPoiMediaGallery m WHERE m.poiId = :poiId AND (m.isActive IS NULL OR m.isActive = true) AND m.deletedAt IS NULL ORDER BY m.displayOrder ASC")
    List<SrvPoiMediaGallery> findActiveByPoiIdOrderByDisplayOrderAsc(@Param("poiId") String poiId);
}
