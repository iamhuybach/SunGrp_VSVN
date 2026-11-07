package vn.visitvietnam.dataserving.service;

import jakarta.persistence.criteria.Predicate;
import org.springframework.data.jpa.domain.Specification;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;

import java.util.ArrayList;
import java.util.List;

/**
 * Dynamic JPA Specifications for querying {@link SrvPoiInfo}.
 */
public final class PoiSpecifications {

    private PoiSpecifications() {
        // utility class
    }

    public static Specification<SrvPoiInfo> filter(List<String> ids) {
        return (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();

            // 1. Luôn loại trừ các bản ghi đã xóa mềm
            predicates.add(cb.isNull(root.get("deletedAt")));

            // 2. Lọc theo danh sách POI IDs nếu được cung cấp
            if (ids != null && !ids.isEmpty()) {
                predicates.add(root.get("poiId").in(ids));
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }
}
