package vn.visitvietnam.dataserving.service;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiLegacyIdMapRepository;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiLegacyIdMapRepositoryCustom.Resolution;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Đổi {@code poi_id} cũ sang {@code poi_id} mới khi dòng map {@code OK} và id nhập chưa là khóa của {@code srv_poi_info}.
 */
@Component
@RequiredArgsConstructor
public class PoiIdResolver {

    private static final Logger log = LoggerFactory.getLogger(PoiIdResolver.class);

    private final SrvPoiLegacyIdMapRepository repository;

    @Transactional(readOnly = true)
    public Map<String, String> resolveAll(Collection<String> ids) {
        Map<String, String> out = new LinkedHashMap<>();
        if (ids != null) {
            ids.stream().filter(id -> id != null && !id.isBlank()).forEach(id -> out.put(id, id));
        }
        if (out.isEmpty()) {
            return out;
        }
        int changed = 0;
        for (Resolution row : repository.findResolvable(out.keySet())) {
            if (!row.poiId().equals(out.get(row.legacyPoiId()))) {
                changed++;
            }
            out.put(row.legacyPoiId(), row.poiId());
        }
        log.debug("poi_id_resolution requested={} legacy_resolved={}", out.size(), changed);
        return out;
    }

    @Transactional(readOnly = true)
    public String resolve(String id) {
        if (id == null || id.isBlank()) {
            return id;
        }
        return resolveAll(List.of(id)).get(id);
    }
}
