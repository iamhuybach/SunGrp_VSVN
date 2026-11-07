package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.PoiAmenityId;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiAmenity;

import java.util.Collection;
import java.util.List;

/**
 * Spring Data JPA Repository for {@link SrvPoiAmenity}.
 */
@Repository
public interface SrvPoiAmenityRepository extends JpaRepository<SrvPoiAmenity, PoiAmenityId> {

    List<SrvPoiAmenity> findByPoiIdAndDeletedAtIsNull(String poiId);

    List<SrvPoiAmenity> findByPoiIdInAndDeletedAtIsNull(Collection<String> poiIds);
}
