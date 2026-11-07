package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;

import java.util.Optional;

/**
 * Spring Data JPA Repository for {@link SrvPoiInfo}.
 */
@Repository
public interface SrvPoiInfoRepository extends JpaRepository<SrvPoiInfo, String>, JpaSpecificationExecutor<SrvPoiInfo> {

    boolean existsByPoiIdAndDeletedAtIsNull(String poiId);

    Optional<SrvPoiInfo> findByPoiIdAndDeletedAtIsNull(String poiId);
}
