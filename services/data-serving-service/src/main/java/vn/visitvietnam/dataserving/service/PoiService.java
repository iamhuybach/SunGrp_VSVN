package vn.visitvietnam.dataserving.service;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import vn.visitvietnam.dataserving.api.dto.CompactPoiResponse;
import vn.visitvietnam.dataserving.api.dto.PoiAmenityGroupResponse;
import vn.visitvietnam.dataserving.api.dto.PoiGalleryItemResponse;
import vn.visitvietnam.dataserving.api.dto.PoiReviewItemResponse;
import vn.visitvietnam.dataserving.common.dto.PageResponse;
import vn.visitvietnam.dataserving.common.exception.ResourceNotFoundException;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiAmenity;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiMediaGallery;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiMultiLang;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiReview;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiAmenityRepository;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiInfoRepository;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiMediaGalleryRepository;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiMultiLangRepository;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiReviewRepository;
import vn.visitvietnam.dataserving.service.util.BusinessSectorDictionary;
import vn.visitvietnam.dataserving.service.util.LanguageResolver;
import vn.visitvietnam.dataserving.service.util.SubcategoryTagsParser;

import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Service hợp nhất quản lý toàn bộ logic nghiệp vụ đọc dữ liệu POI.
 */
@Service
@RequiredArgsConstructor
public class PoiService {

    private final SrvPoiInfoRepository poiInfoRepository;
    private final SrvPoiMediaGalleryRepository mediaGalleryRepository;
    private final SrvPoiMultiLangRepository multiLangRepository;
    private final SrvPoiReviewRepository reviewRepository;
    private final SrvPoiAmenityRepository amenityRepository;

    // ── API 1: Compact POIs ──────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public PageResponse<CompactPoiResponse> getCompactPois(List<String> ids, String targetLang, int page, int size, String sortParam) {
        String lang = targetLang != null && !targetLang.isBlank() ? targetLang : LanguageResolver.DEFAULT_LANG;

        Sort sort = parseSort(sortParam);
        Pageable pageable = PageRequest.of(page, size, sort);

        Page<SrvPoiInfo> poiPage = poiInfoRepository.findAll(PoiSpecifications.filter(ids), pageable);
        if (poiPage.isEmpty()) {
            return PageResponse.of(Collections.emptyList(), page, size, poiPage.getTotalElements());
        }

        List<SrvPoiInfo> pois = poiPage.getContent();
        List<String> poiIds = pois.stream().map(SrvPoiInfo::getPoiId).toList();

        // Batch query media & multilang (tránh N+1)
        List<SrvPoiMediaGallery> mediaList = mediaGalleryRepository.findActiveByPoiIdInOrderByDisplayOrderAsc(poiIds);
        Map<String, List<SrvPoiMediaGallery>> mediaByPoi = mediaList.stream()
                .collect(Collectors.groupingBy(SrvPoiMediaGallery::getPoiId));

        Set<String> langsToFetch = lang.equalsIgnoreCase(LanguageResolver.DEFAULT_LANG)
                ? Set.of(LanguageResolver.DEFAULT_LANG)
                : Set.of(lang, LanguageResolver.DEFAULT_LANG);
        List<SrvPoiMultiLang> multiLangList = multiLangRepository.findByPoiIdInAndLangIn(poiIds, langsToFetch);
        Map<String, Map<String, SrvPoiMultiLang>> multiLangByPoi = new HashMap<>();
        for (SrvPoiMultiLang ml : multiLangList) {
            multiLangByPoi.computeIfAbsent(ml.getPoiId(), k -> new HashMap<>()).put(ml.getLang(), ml);
        }

        List<CompactPoiResponse> items = pois.stream()
                .map(poi -> mapToCompactResponse(poi, lang, mediaByPoi.get(poi.getPoiId()), multiLangByPoi.get(poi.getPoiId())))
                .toList();

        return PageResponse.of(items, page, size, poiPage.getTotalElements());
    }

    // ── API 3: POI Gallery ───────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public List<PoiGalleryItemResponse> getGallery(String poiId) {
        validatePoiExists(poiId);

        List<SrvPoiMediaGallery> mediaList = mediaGalleryRepository.findActiveByPoiIdOrderByDisplayOrderAsc(poiId);
        return mediaList.stream()
                .map(m -> {
                    String fileKey = m.getBlobUrl() != null && !m.getBlobUrl().isBlank() ? m.getBlobUrl() : m.getPhotoApiUri();
                    return new PoiGalleryItemResponse(
                            m.getMediaId(),
                            fileKey,
                            m.getWidthPx(),
                            m.getHeightPx(),
                            resolveMimeType(fileKey),
                            null,
                            m.getDisplayOrder()
                    );
                })
                .toList();
    }

    // ── API 9: POI Reviews ───────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public PageResponse<PoiReviewItemResponse> getReviews(String poiId, int page, int size) {
        validatePoiExists(poiId);

        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "reviewDate"));
        Page<SrvPoiReview> reviewPage = reviewRepository.findByPoiIdAndDeletedAtIsNull(poiId, pageable);

        if (reviewPage.isEmpty()) {
            return PageResponse.of(Collections.emptyList(), page, size, reviewPage.getTotalElements());
        }

        List<PoiReviewItemResponse> items = reviewPage.getContent().stream()
                .map(r -> {
                    Double rating = r.getRating() != null ? r.getRating().doubleValue()
                            : (r.getRatingOverall() != null ? r.getRatingOverall().doubleValue() : null);
                    return new PoiReviewItemResponse(
                            r.getReviewId(),
                            r.getAuthorName(),
                            rating,
                            r.getReviewText(),
                            r.getReviewDate()
                    );
                })
                .toList();

        return PageResponse.of(items, page, size, reviewPage.getTotalElements());
    }

    // ── API 10: POI Amenities ────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public List<PoiAmenityGroupResponse> getAmenities(String poiId) {
        List<SrvPoiAmenity> amenities = amenityRepository.findByPoiIdAndDeletedAtIsNull(poiId);
        if (amenities.isEmpty()) {
            return Collections.emptyList();
        }

        List<SrvPoiAmenity> validAmenities = amenities.stream()
                .filter(a -> a.getAmenityRaw() == null || !a.getAmenityRaw().toLowerCase().contains("json_type"))
                .sorted(Comparator.comparing(SrvPoiAmenity::getAmenityGroup)
                        .thenComparing(SrvPoiAmenity::getAmenity, Comparator.nullsLast(Comparator.naturalOrder()))
                        .thenComparing(SrvPoiAmenity::getAmenityRaw))
                .toList();

        if (validAmenities.isEmpty()) {
            return Collections.emptyList();
        }

        Map<String, List<SrvPoiAmenity>> grouped = validAmenities.stream()
                .collect(Collectors.groupingBy(
                        SrvPoiAmenity::getAmenityGroup,
                        LinkedHashMap::new,
                        Collectors.toList()
                ));

        return grouped.entrySet().stream()
                .map(entry -> new PoiAmenityGroupResponse(
                        entry.getKey(),
                        entry.getValue().stream()
                                .map(a -> new PoiAmenityGroupResponse.Item(
                                        a.getAmenity(),
                                        a.getAmenityEn(),
                                        a.getAmenityVi(),
                                        a.getServiceFlags()))
                                .toList()))
                .toList();
    }

    // ── Shared Helpers ───────────────────────────────────────────────────────

    private void validatePoiExists(String poiId) {
        if (!poiInfoRepository.existsByPoiIdAndDeletedAtIsNull(poiId)) {
            throw new ResourceNotFoundException("POI not found with id: " + poiId);
        }
    }

    private CompactPoiResponse mapToCompactResponse(
            SrvPoiInfo poi,
            String targetLang,
            List<SrvPoiMediaGallery> mediaList,
            Map<String, SrvPoiMultiLang> multiLangs) {

        String name = poi.getPoiName();
        String description = null;

        if (multiLangs != null) {
            SrvPoiMultiLang ml = multiLangs.get(targetLang);
            if (ml == null) {
                ml = multiLangs.get(LanguageResolver.DEFAULT_LANG);
            }
            if (ml != null && ml.getDescription() != null && !ml.getDescription().isBlank()) {
                description = ml.getDescription();
            }
        }

        CompactPoiResponse.Cover cover = null;
        if (mediaList != null && !mediaList.isEmpty()) {
            SrvPoiMediaGallery coverMedia = mediaList.stream()
                    .filter(m -> Boolean.TRUE.equals(m.getIsCover()))
                    .findFirst()
                    .orElse(mediaList.getFirst());

            String fileKey = coverMedia.getBlobUrl() != null && !coverMedia.getBlobUrl().isBlank()
                    ? coverMedia.getBlobUrl()
                    : coverMedia.getPhotoApiUri();

            cover = new CompactPoiResponse.Cover(
                    coverMedia.getMediaId(),
                    fileKey,
                    coverMedia.getWidthPx(),
                    coverMedia.getHeightPx(),
                    resolveMimeType(fileKey),
                    null
            );
        }

        CompactPoiResponse.Rating rating = null;
        if (poi.getRatingOverall() != null || poi.getRatingCount() != null) {
            Double score = poi.getRatingOverall() != null ? poi.getRatingOverall().doubleValue() : null;
            rating = new CompactPoiResponse.Rating(score, poi.getRatingCount());
        }

        CompactPoiResponse.BusinessTags businessTags = null;
        if (poi.getBusinessSector() != null || poi.getBusinessCategory() != null) {
            String businessSector = poi.getBusinessSector();
            String businessSectorLabel = BusinessSectorDictionary.getLabel(businessSector);
            String businessCategory = poi.getBusinessCategory();
            List<String> subcategories = SubcategoryTagsParser.parse(poi.getSubcategoryTags());
            businessTags = new CompactPoiResponse.BusinessTags(
                    businessSector,
                    businessSectorLabel,
                    businessCategory,
                    subcategories.isEmpty() ? null : subcategories
            );
        }

        CompactPoiResponse.Address address = null;
        if (poi.getFullAddress() != null || poi.getCity() != null || poi.getDistrict() != null) {
            address = new CompactPoiResponse.Address(
                    poi.getFullAddress(),
                    poi.getStreet(),
                    poi.getWard(),
                    poi.getDistrict(),
                    poi.getCity(),
                    poi.getCountryCode()
            );
        }

        CompactPoiResponse.GeoLocation geoLocation = null;
        if (poi.getLat() != null && poi.getLng() != null) {
            geoLocation = new CompactPoiResponse.GeoLocation(poi.getLat(), poi.getLng());
        }

        return new CompactPoiResponse(
                poi.getPoiId(),
                name,
                description,
                cover,
                rating,
                businessTags,
                address,
                geoLocation
        );
    }

    private Sort parseSort(String sortParam) {
        if (sortParam == null || sortParam.isBlank()) {
            return Sort.by(Sort.Direction.DESC, "createdAt");
        }
        String[] parts = sortParam.split(",");
        String property = parts[0].trim();
        Sort.Direction direction = parts.length > 1 && "asc".equalsIgnoreCase(parts[1].trim())
                ? Sort.Direction.ASC
                : Sort.Direction.DESC;
        return Sort.by(direction, property);
    }

    private static String resolveMimeType(String fileKey) {
        if (fileKey == null) {
            return "image/jpeg";
        }
        String lower = fileKey.toLowerCase();
        if (lower.endsWith(".png")) {
            return "image/png";
        }
        if (lower.endsWith(".webp")) {
            return "image/webp";
        }
        if (lower.endsWith(".gif")) {
            return "image/gif";
        }
        return "image/jpeg";
    }
}

