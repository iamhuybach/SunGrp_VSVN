package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiLegacyIdMap;

@Repository
public interface SrvPoiLegacyIdMapRepository extends JpaRepository<SrvPoiLegacyIdMap, String>, SrvPoiLegacyIdMapRepositoryCustom {
}
