package vn.visitvietnam.dataserving.domain.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiReview;

/**
 * Spring Data JPA Repository for {@link SrvPoiReview}.
 */
@Repository
public interface SrvPoiReviewRepository extends JpaRepository<SrvPoiReview, String> {

    Page<SrvPoiReview> findByPoiIdAndDeletedAtIsNull(String poiId, Pageable pageable);
}
