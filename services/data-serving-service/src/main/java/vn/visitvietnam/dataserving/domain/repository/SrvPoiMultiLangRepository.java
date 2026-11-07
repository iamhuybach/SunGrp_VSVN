package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.PoiMultiLangId;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiMultiLang;

import java.util.Collection;
import java.util.List;

/**
 * Spring Data JPA Repository for {@link SrvPoiMultiLang}.
 */
@Repository
public interface SrvPoiMultiLangRepository extends JpaRepository<SrvPoiMultiLang, PoiMultiLangId> {

    @Query("SELECT ml FROM SrvPoiMultiLang ml WHERE ml.poiId IN :poiIds AND ml.lang IN :langs AND ml.deletedAt IS NULL")
    List<SrvPoiMultiLang> findByPoiIdInAndLangIn(@Param("poiIds") Collection<String> poiIds, @Param("langs") Collection<String> langs);
}
