package vn.visitvietnam.dataserving.service;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import vn.visitvietnam.dataserving.api.dto.CompactPoiResponse;
import vn.visitvietnam.dataserving.api.dto.PoiAmenityGroupResponse;
import vn.visitvietnam.dataserving.api.dto.PoiExperiencesResponse;
import vn.visitvietnam.dataserving.api.dto.PoiFeatureResponse;
import vn.visitvietnam.dataserving.api.dto.PoiGalleryItemResponse;
import vn.visitvietnam.dataserving.api.dto.PoiPracticalInfoResponse;
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
import vn.visitvietnam.dataserving.service.util.LanguageResolver;
import vn.visitvietnam.dataserving.service.util.StoredJsonParser;
import vn.visitvietnam.dataserving.service.util.SubcategoryTagsParser;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Service hợp nhất quản lý toàn bộ logic nghiệp vụ đọc dữ liệu POI.
 */
@Service
@RequiredArgsConstructor
public class PoiService {

    private static final Pattern SECTOR = Pattern.compile("^[a-z0-9_]{1,64}$");
    private static final List<String> DEFAULT_SECTORS = List.of("attraction", "f_n_b", "event", "tour_n_activities");

    private final SrvPoiInfoRepository poiInfoRepository;
    private final SrvPoiMediaGalleryRepository mediaGalleryRepository;
    private final SrvPoiMultiLangRepository multiLangRepository;
    private final SrvPoiReviewRepository reviewRepository;
    private final SrvPoiAmenityRepository amenityRepository;

    public record ReviewsPage(PageResponse<PoiReviewItemResponse> page, List<PoiReviewItemResponse.RatingSummary> ratingSummary) {}

    public record FeaturePage(List<PoiFeatureResponse> items, long total) {}

    @Transactional(readOnly = true)
    public List<CompactPoiResponse> getCompactPois(List<String> ids, String targetLang) {
        String lang = blankToDefault(targetLang);
        List<SrvPoiInfo> pois = poiInfoRepository.findAll(
                PoiSpecifications.filter(ids),
                Sort.by(Sort.Order.desc("createdAt"), Sort.Order.asc("poiId")));
        if (pois.isEmpty()) {
            return List.of();
        }
        Map<String, Map<String, SrvPoiMultiLang>> multiLangByPoi = loadLangs(pois.stream().map(SrvPoiInfo::getPoiId).toList(), lang);
        return pois.stream()
                .map(poi -> mapToCompactResponse(poi, lang, multiLangByPoi.get(poi.getPoiId())))
                .toList();
    }

    @Transactional(readOnly = true)
    public PageResponse<PoiGalleryItemResponse> getGallery(String poiId, int page, int size) {
        Page<SrvPoiMediaGallery> mediaPage = mediaGalleryRepository.findActivePageByPoiId(poiId, PageRequest.of(page, size));
        List<PoiGalleryItemResponse> items = mediaPage.getContent().stream()
                .map(m -> new PoiGalleryItemResponse(m.getMediaId(), m.getBlobUrl(), m.getDisplayOrder()))
                .toList();
        return PageResponse.of(items, page, size, mediaPage.getTotalElements());
    }

    @Transactional(readOnly = true)
    public ReviewsPage getReviews(String poiId, int page, int size) {
        Sort sort = Sort.by(Sort.Order.desc("reviewDate"), Sort.Order.asc("reviewId"));
        Page<SrvPoiReview> reviewPage = reviewRepository.findByPoiIdAndDeletedAtIsNull(poiId, PageRequest.of(page, size, sort));
        List<PoiReviewItemResponse> items = reviewPage.getContent().stream().map(this::mapReview).toList();
        SrvPoiReview summarySource = null;
        if (!reviewPage.getContent().isEmpty()) {
            summarySource = reviewPage.getContent().getFirst();
        } else if (reviewPage.getTotalElements() > 0) {
            Page<SrvPoiReview> first = reviewRepository.findByPoiIdAndDeletedAtIsNull(
                    poiId, PageRequest.of(0, 1, Sort.by("reviewId")));
            if (!first.getContent().isEmpty()) {
                summarySource = first.getContent().getFirst();
            }
        }
        List<PoiReviewItemResponse.RatingSummary> summary = summarySource == null
                ? List.of()
                : List.of(new PoiReviewItemResponse.RatingSummary(
                        summarySource.getRatingCount(),
                        summarySource.getRatingOverall() == null ? null : summarySource.getRatingOverall().doubleValue()));
        return new ReviewsPage(PageResponse.of(items, page, size, reviewPage.getTotalElements()), summary);
    }

    @Transactional(readOnly = true)
    public FeaturePage getFeatures(List<String> sectors, BigDecimal minRating, int minReviewCount, String ratingSource,
            String targetLang, int page, int size) {
        List<String> normalized = normalizeSectors(sectors);
        String source = ratingSource == null || ratingSource.isBlank() ? "" : ratingSource.trim().toLowerCase();
        String csv = String.join(",", normalized);
        long total = poiInfoRepository.countFeatures(csv, minRating, minReviewCount, source);
        List<String> ids = poiInfoRepository.findFeatureIds(csv, minRating, minReviewCount, source, size, (long) page * size);
        if (ids.isEmpty()) {
            return new FeaturePage(List.of(), total);
        }
        Map<String, SrvPoiInfo> byId = poiInfoRepository.findAllById(ids).stream()
                .filter(poi -> poi.getDeletedAt() == null)
                .collect(Collectors.toMap(SrvPoiInfo::getPoiId, poi -> poi));
        String lang = blankToDefault(targetLang);
        Map<String, Map<String, SrvPoiMultiLang>> langs = loadLangs(ids, lang);
        List<PoiFeatureResponse> items = new ArrayList<>();
        for (String id : ids) {
            SrvPoiInfo poi = byId.get(id);
            if (poi != null) {
                items.add(mapFeature(poi, lang, langs.get(id)));
            }
        }
        return new FeaturePage(items, total);
    }

    @Transactional(readOnly = true)
    public PoiExperiencesResponse getExperiences(String poiId, String targetLang) {
        String lang = blankToDefault(targetLang);
        Map<String, SrvPoiMultiLang> rows = loadLangs(List.of(poiId), lang).getOrDefault(poiId, Map.of());
        List<SrvPoiMultiLang> candidates = new ArrayList<>();
        if (rows.get(lang) != null) {
            candidates.add(rows.get(lang));
        }
        if (!lang.equals(LanguageResolver.DEFAULT_LANG) && rows.get(LanguageResolver.DEFAULT_LANG) != null) {
            candidates.add(rows.get(LanguageResolver.DEFAULT_LANG));
        }
        for (SrvPoiMultiLang row : candidates) {
            List<StoredJsonParser.ExperienceDraft> drafts = StoredJsonParser.experiences(poiId, row.getExperience());
            if (!drafts.isEmpty()) {
                String source = row.getSourceName();
                return new PoiExperiencesResponse(drafts.stream()
                        .map(item -> new PoiExperiencesResponse.Item(item.title(), item.description(), source))
                        .toList());
            }
        }
        return new PoiExperiencesResponse(List.of());
    }

    @Transactional(readOnly = true)
    public PoiPracticalInfoResponse getPracticalInfo(String poiId, String targetLang) {
        SrvPoiInfo poi = poiInfoRepository.findByPoiIdAndDeletedAtIsNull(poiId)
                .orElseThrow(() -> new ResourceNotFoundException("POI not found with id: " + poiId));
        String lang = blankToDefault(targetLang);
        Map<String, SrvPoiMultiLang> rows = loadLangs(List.of(poiId), lang).getOrDefault(poiId, Map.of());
        SrvPoiMultiLang target = rows.get(lang);
        SrvPoiMultiLang fallback = rows.get(LanguageResolver.DEFAULT_LANG);
        List<SrvPoiMediaGallery> covers = mediaGalleryRepository.findActiveCoverByPoiId(poiId, PageRequest.of(0, 1));
        PoiPracticalInfoResponse.Cover cover = covers.isEmpty()
                ? null
                : new PoiPracticalInfoResponse.Cover(covers.getFirst().getMediaId(), covers.getFirst().getBlobUrl());
        List<PoiFeatureResponse.OperatingHour> hours = StoredJsonParser.operatingHours(poiId, poi.getOperatingHours());
        return new PoiPracticalInfoResponse(
                poi.getPoiId(),
                poi.getPoiName(),
                firstNonBlank(text(target, SrvPoiMultiLang::getDescription), text(fallback, SrvPoiMultiLang::getDescription)),
                poi.getBusinessSector(),
                toLabel(StoredJsonParser.labelValue(poiId, "time_to_spend", text(target, SrvPoiMultiLang::getTimeToSpend)),
                        StoredJsonParser.labelValue(poiId, "time_to_spend", text(fallback, SrvPoiMultiLang::getTimeToSpend))),
                toLabel(StoredJsonParser.labelValue(poiId, "cost_vnd", text(target, SrvPoiMultiLang::getCostVnd)),
                        StoredJsonParser.labelValue(poiId, "cost_vnd", text(fallback, SrvPoiMultiLang::getCostVnd))),
                toLabel(StoredJsonParser.labelValue(poiId, "best_time", text(target, SrvPoiMultiLang::getBestTime)),
                        StoredJsonParser.labelValue(poiId, "best_time", text(fallback, SrvPoiMultiLang::getBestTime))),
                cover,
                new PoiPracticalInfoResponse.Ratings(
                        poi.getSourceName(),
                        poi.getRatingCount(),
                        poi.getRatingOverall() == null ? null : poi.getRatingOverall().doubleValue()),
                new PoiPracticalInfoResponse.BusinessTags(poi.getBusinessSector(), poi.getBusinessCategory()),
                new PoiPracticalInfoResponse.Status(poi.getOperatingStatus(), poi.getIsVerified(), poi.getIsRecommended(), poi.getIsBookable()),
                hours == null ? null : new PoiPracticalInfoResponse.OperatingHours(hours),
                StoredJsonParser.singleJsonValueOrNull(poiId, poi.getHolidayExceptions()),
                addressOf(poi),
                geoOf(poi),
                poi.getPhone(),
                poi.getEmail(),
                poi.getWebsiteUrl(),
                new PoiPracticalInfoResponse.Destinations(poi.getDestinationId())
        );
    }

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
                .collect(Collectors.groupingBy(SrvPoiAmenity::getAmenityGroup, LinkedHashMap::new, Collectors.toList()));
        return grouped.entrySet().stream()
                .map(entry -> new PoiAmenityGroupResponse(
                        entry.getKey(),
                        entry.getValue().stream()
                                .map(a -> new PoiAmenityGroupResponse.Item(
                                        a.getAmenity(), a.getAmenityEn(), a.getAmenityVi(), a.getServiceFlags()))
                                .toList()))
                .toList();
    }

    List<String> normalizeSectors(List<String> raw) {
        if (raw == null || raw.isEmpty()) {
            return DEFAULT_SECTORS;
        }
        LinkedHashSet<String> seen = new LinkedHashSet<>();
        for (String value : raw) {
            if (value == null) {
                continue;
            }
            String cleaned = value.trim().toLowerCase();
            if (cleaned.isEmpty()) {
                continue;
            }
            if (!SECTOR.matcher(cleaned).matches()) {
                throw new IllegalArgumentException("business_sector_priority contains an invalid value");
            }
            seen.add(cleaned);
        }
        return seen.isEmpty() ? DEFAULT_SECTORS : List.copyOf(seen);
    }

    private CompactPoiResponse mapToCompactResponse(SrvPoiInfo poi, String targetLang, Map<String, SrvPoiMultiLang> multiLangs) {
        CompactPoiResponse.Cover cover = null;
        if (poi.getCoverId() != null || poi.getCoverBlobUrl() != null) {
            cover = new CompactPoiResponse.Cover(poi.getCoverId(), poi.getCoverBlobUrl());
        }
        CompactPoiResponse.Rating rating = null;
        if (poi.getRatingOverall() != null || poi.getRatingCount() != null) {
            rating = new CompactPoiResponse.Rating(
                    poi.getRatingOverall() == null ? null : poi.getRatingOverall().doubleValue(),
                    poi.getRatingCount());
        }
        CompactPoiResponse.BusinessTags businessTags = null;
        if (poi.getBusinessSector() != null || poi.getBusinessCategory() != null) {
            List<String> subcategories = SubcategoryTagsParser.parse(poi.getSubcategoryTags());
            businessTags = new CompactPoiResponse.BusinessTags(
                    poi.getBusinessSector(),
                    poi.getBusinessCategory(),
                    subcategories.isEmpty() ? null : subcategories);
        }
        return new CompactPoiResponse(
                poi.getPoiId(),
                poi.getPoiName(),
                descriptionOf(targetLang, multiLangs),
                cover,
                rating,
                businessTags,
                addressOf(poi),
                geoOf(poi));
    }

    private PoiFeatureResponse mapFeature(SrvPoiInfo poi, String lang, Map<String, SrvPoiMultiLang> multiLangs) {
        List<PoiFeatureResponse.Rating> ratings = List.of();
        if (poi.getRatingOverall() != null || poi.getRatingCount() != null) {
            ratings = List.of(new PoiFeatureResponse.Rating(
                    poi.getSourceName(),
                    poi.getRatingCount(),
                    poi.getRatingOverall() == null ? null : poi.getRatingOverall().doubleValue()));
        }
        List<String> tags = SubcategoryTagsParser.parse(poi.getSubcategoryTags());
        return new PoiFeatureResponse(
                poi.getPoiId(),
                poi.getPoiName(),
                descriptionOf(lang, multiLangs),
                new PoiFeatureResponse.Cover(poi.getCoverId(), poi.getCoverBlobUrl()),
                ratings,
                new PoiFeatureResponse.BusinessTags(poi.getBusinessSector(), poi.getBusinessCategory(), tags.isEmpty() ? null : tags),
                new PoiFeatureResponse.Status(poi.getOperatingStatus(), poi.getIsVerified(), poi.getIsRecommended(), poi.getIsBookable()),
                StoredJsonParser.operatingHours(poi.getPoiId(), poi.getOperatingHours()),
                addressOf(poi),
                geoOf(poi));
    }

    private PoiReviewItemResponse mapReview(SrvPoiReview review) {
        Double rating = review.getRating() != null ? review.getRating().doubleValue()
                : (review.getRatingOverall() != null ? review.getRatingOverall().doubleValue() : null);
        return new PoiReviewItemResponse(review.getReviewId(), review.getAuthorName(), rating, review.getReviewText(), review.getReviewDate());
    }

    private Map<String, Map<String, SrvPoiMultiLang>> loadLangs(List<String> poiIds, String lang) {
        Set<String> langs = lang.equalsIgnoreCase(LanguageResolver.DEFAULT_LANG)
                ? Set.of(LanguageResolver.DEFAULT_LANG)
                : Set.of(lang, LanguageResolver.DEFAULT_LANG);
        Map<String, Map<String, SrvPoiMultiLang>> byPoi = new HashMap<>();
        for (SrvPoiMultiLang row : multiLangRepository.findByPoiIdInAndLangIn(poiIds, langs)) {
            byPoi.computeIfAbsent(row.getPoiId(), key -> new HashMap<>()).put(row.getLang(), row);
        }
        return byPoi;
    }

    private String descriptionOf(String lang, Map<String, SrvPoiMultiLang> multiLangs) {
        if (multiLangs == null) {
            return null;
        }
        return firstNonBlank(text(multiLangs.get(lang), SrvPoiMultiLang::getDescription),
                text(multiLangs.get(LanguageResolver.DEFAULT_LANG), SrvPoiMultiLang::getDescription));
    }

    private CompactPoiResponse.Address addressOf(SrvPoiInfo poi) {
        if (poi.getFullAddress() == null && poi.getCity() == null && poi.getDistrict() == null) {
            return null;
        }
        return new CompactPoiResponse.Address(
                poi.getFullAddress(), poi.getStreet(), poi.getWard(), poi.getDistrict(), poi.getCity(), poi.getCountryCode());
    }

    private CompactPoiResponse.GeoLocation geoOf(SrvPoiInfo poi) {
        if (poi.getLat() == null || poi.getLng() == null) {
            return null;
        }
        return new CompactPoiResponse.GeoLocation(poi.getLat(), poi.getLng());
    }

    private static PoiPracticalInfoResponse.LabelValue toLabel(StoredJsonParser.LabelValue target, StoredJsonParser.LabelValue fallback) {
        StoredJsonParser.LabelValue chosen = target != null ? target : fallback;
        if (chosen == null) {
            return null;
        }
        return new PoiPracticalInfoResponse.LabelValue(chosen.label(), chosen.value());
    }

    private static String text(SrvPoiMultiLang row, java.util.function.Function<SrvPoiMultiLang, String> getter) {
        return row == null ? null : getter.apply(row);
    }

    private static String firstNonBlank(String target, String fallback) {
        if (target != null && !target.isBlank()) {
            return target;
        }
        if (fallback != null && !fallback.isBlank()) {
            return fallback;
        }
        return null;
    }

    private static String blankToDefault(String lang) {
        return lang != null && !lang.isBlank() ? lang : LanguageResolver.DEFAULT_LANG;
    }
}
