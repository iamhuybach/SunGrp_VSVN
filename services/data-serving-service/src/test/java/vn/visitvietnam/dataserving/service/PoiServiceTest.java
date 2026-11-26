package vn.visitvietnam.dataserving.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import vn.visitvietnam.dataserving.api.dto.CompactPoiResponse;
import vn.visitvietnam.dataserving.api.dto.PoiAmenityGroupResponse;
import vn.visitvietnam.dataserving.api.dto.PoiExperiencesResponse;
import vn.visitvietnam.dataserving.api.dto.PoiPracticalInfoResponse;
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
import vn.visitvietnam.dataserving.domain.repository.SrvPoiLegacyIdMapRepository;
import vn.visitvietnam.dataserving.domain.repository.SrvPoiLegacyIdMapRepositoryCustom;

import java.math.BigDecimal;
import java.util.Collection;
import java.util.Collections;
import java.util.EnumSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.lenient;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class PoiServiceTest {

    @Mock
    private SrvPoiInfoRepository poiInfoRepository;

    @Mock
    private SrvPoiMediaGalleryRepository mediaGalleryRepository;

    @Mock
    private SrvPoiMultiLangRepository multiLangRepository;

    @Mock
    private SrvPoiReviewRepository reviewRepository;

    @Mock
    private SrvPoiAmenityRepository amenityRepository;

    @Mock
    private PoiIdResolver poiIdResolver;

    @Mock
    private SrvPoiLegacyIdMapRepository legacyIdMapRepository;

    @InjectMocks
    private PoiService poiService;

    @BeforeEach
    void identityResolver() {
        lenient().when(poiIdResolver.resolve(any())).thenAnswer(invocation -> invocation.getArgument(0));
        lenient().when(poiIdResolver.resolveAll(any())).thenAnswer(invocation -> {
            Map<String, String> out = new LinkedHashMap<>();
            Collection<?> ids = invocation.getArgument(0);
            if (ids != null) {
                for (Object id : ids) {
                    if (id instanceof String value && !value.isBlank()) {
                        out.put(value, value);
                    }
                }
            }
            return out;
        });
    }

    @Test
    @DisplayName("searchPracticalInfo không đọc multi_lang và cover khi không chọn field đó")
    void searchPracticalInfoSkipsMultiLangAndCoverWhenNotSelected() {
        SrvPoiInfo poi = SrvPoiInfo.builder().poiId("poi_01").poiName("A").build();
        when(legacyIdMapRepository.findPracticalInfoPage(any(), any(), any(), any(), anyBoolean(), anyInt(), anyLong()))
                .thenReturn(new SrvPoiLegacyIdMapRepositoryCustom.PracticalInfoSlice(List.of(poi), 1));
        PracticalInfoQuery query = new PracticalInfoQuery(
                List.of("poi_01"),
                EnumSet.of(PracticalInfoQuery.Field.ID),
                null,
                null,
                "vi",
                0,
                10,
                null,
                Sort.Direction.ASC);
        PoiService.PracticalInfoPage page = poiService.searchPracticalInfo(query);
        assertThat(page.total()).isEqualTo(1);
        verifyNoInteractions(multiLangRepository, mediaGalleryRepository);
    }

    // ── API 1: Compact POIs Tests ────────────────────────────────────────────

    @Test
    @DisplayName("API 1: Lấy danh sách Compact POI thành công kèm media và đa ngôn ngữ")
    void shouldReturnCompactPoisSuccessfully() {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_01")
                .destinationId("[\"dest_01\"]")
                .destinationName("[\"Ha Noi\"]")
                .poiName("Nhà hát Lớn")
                .sourceName("google_places")
                .businessSector("ATTRACTION")
                .businessCategory("THEATER")
                .subcategoryTags("[\"architecture\", \"culture\"]")
                .fullAddress("1 Tràng Tiền, Hoàn Kiếm, Hà Nội")
                .lat(21.025)
                .lng(105.857)
                .ratingOverall(new BigDecimal("4.80"))
                .ratingCount(1500)
                .reviewCount(450)
                .coverId("med_01")
                .coverBlobUrl("https://cdn.example.com/cover.webp")
                .isVerified(true)
                .isRecommended(true)
                .isBookable(false)
                .operatingStatus("OPERATIONAL")
                .build();

        when(poiInfoRepository.findAll(any(Specification.class), any(Sort.class)))
                .thenReturn(List.of(poi));

        SrvPoiMultiLang enLang = SrvPoiMultiLang.builder()
                .poiId("poi_01")
                .lang("en")
                .description("Historical theater")
                .build();

        when(multiLangRepository.findByPoiIdInAndLangIn(eq(List.of("poi_01")), eq(Set.of("en", "vi"))))
                .thenReturn(List.of(enLang));

        List<CompactPoiResponse> response = poiService.getCompactPois(List.of("poi_01"), "en");

        assertThat(response).hasSize(1);
        CompactPoiResponse item = response.getFirst();
        assertThat(item.id()).isEqualTo("poi_01");
        assertThat(item.name()).isEqualTo("Nhà hát Lớn");
        assertThat(item.description()).isEqualTo("Historical theater");
        assertThat(item.cover().id()).isEqualTo("med_01");
        assertThat(item.cover().fileKey()).isEqualTo("https://cdn.example.com/cover.webp");
        assertThat(item.businessTags().businessSector()).isEqualTo("ATTRACTION");
        assertThat(item.businessTags().subcategories()).containsExactly("architecture", "culture");
        assertThat(item.rating().overall()).isEqualTo(4.80);
        assertThat(item.destinations().id()).containsExactly("dest_01");
        assertThat(item.destinations().name()).containsExactly("Ha Noi");
    }

    @Test
    @DisplayName("API 1: destinations luôn là object khi destination_id và destination_name null")
    void shouldReturnCompactDestinationsObjectWhenColumnsNull() throws Exception {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_null")
                .poiName("X")
                .build();
        when(poiInfoRepository.findAll(any(Specification.class), any(Sort.class)))
                .thenReturn(List.of(poi));
        when(multiLangRepository.findByPoiIdInAndLangIn(eq(List.of("poi_null")), eq(Set.of("vi"))))
                .thenReturn(Collections.emptyList());

        CompactPoiResponse item = poiService.getCompactPois(List.of("poi_null"), "vi").getFirst();
        assertThat(item.destinations()).isNotNull();
        assertThat(item.destinations().id()).isNull();
        assertThat(item.destinations().name()).isNull();
        assertThat(new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(item))
                .contains("\"destinations\":{\"id\":null,\"name\":null}");
    }

    @Test
    @DisplayName("API 1: Lấy danh sách Compact POI với lang=vi không bị duplicate element")
    void shouldReturnCompactPoisWithViLang() {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_vi")
                .poiName("Chùa Một Cột")
                .businessSector("ATTRACTION")
                .build();

        when(poiInfoRepository.findAll(any(Specification.class), any(Sort.class)))
                .thenReturn(List.of(poi));
        when(multiLangRepository.findByPoiIdInAndLangIn(eq(List.of("poi_vi")), eq(Set.of("vi"))))
                .thenReturn(Collections.emptyList());

        List<CompactPoiResponse> response = poiService.getCompactPois(List.of("poi_vi"), "vi");

        assertThat(response).hasSize(1);
        assertThat(response.getFirst().name()).isEqualTo("Chùa Một Cột");
    }

    @Test
    @DisplayName("API 1: Trả về trang rỗng an toàn khi không tìm thấy POI")
    void shouldReturnEmptyPageWhenNoPois() {
        when(poiInfoRepository.findAll(any(Specification.class), any(Sort.class)))
                .thenReturn(Collections.emptyList());

        List<CompactPoiResponse> response = poiService.getCompactPois(List.of("missing"), "vi");
        assertThat(response).isEmpty();
    }

    // ── API 3: Gallery Tests ─────────────────────────────────────────────────

    @Test
    @DisplayName("API 3: Lấy thư viện ảnh gallery thành công theo thứ tự sắp xếp và fallback photoApiUri")
    void shouldReturnGallerySuccessfully() {
        SrvPoiMediaGallery m1 = SrvPoiMediaGallery.builder()
                .mediaId("med_01")
                .poiId("poi_01")
                .blobUrl("https://cdn.example.com/img1.webp")
                .displayOrder(1)
                .isActive(true)
                .build();

        SrvPoiMediaGallery m2 = SrvPoiMediaGallery.builder()
                .mediaId("med_02")
                .poiId("poi_01")
                .blobUrl(null)
                .displayOrder(2)
                .isActive(true)
                .build();

        when(mediaGalleryRepository.findActivePageByPoiId(eq("poi_01"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(m1, m2)));

        PageResponse<PoiGalleryItemResponse> gallery = poiService.getGallery("poi_01", 0, 20);
        assertThat(gallery.content()).hasSize(2);
        assertThat(gallery.content().get(0).id()).isEqualTo("med_01");
        assertThat(gallery.content().get(0).fileKey()).isEqualTo("https://cdn.example.com/img1.webp");
        assertThat(gallery.content().get(0).displayOrder()).isEqualTo(1);
        assertThat(gallery.content().get(1).fileKey()).isNull();
    }

    @Test
    @DisplayName("API 3: Trả về danh sách rỗng khi POI hợp lệ nhưng không có ảnh gallery")
    void shouldReturnEmptyListWhenPoiHasNoGalleryMedia() {
        when(mediaGalleryRepository.findActivePageByPoiId(eq("poi_empty"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(Collections.emptyList()));

        PageResponse<PoiGalleryItemResponse> gallery = poiService.getGallery("poi_empty", 0, 20);
        assertThat(gallery.content()).isNotNull().isEmpty();
    }

    @Test
    @DisplayName("API 3: Ném ResourceNotFoundException khi POI không tồn tại")
    void shouldNotCheckPoiExistenceForGallery() {
        when(mediaGalleryRepository.findActivePageByPoiId(eq("poi_unknown"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(Collections.emptyList()));

        PageResponse<PoiGalleryItemResponse> gallery = poiService.getGallery("poi_unknown", 0, 20);
        assertThat(gallery.content()).isEmpty();
        assertThat(gallery.totalElements()).isZero();
    }

    // ── API 9: Reviews Tests ─────────────────────────────────────────────────

    @Test
    @DisplayName("API 9: Lấy danh sách review có phân trang")
    void shouldReturnReviewsSuccessfully() {
        SrvPoiReview review = SrvPoiReview.builder()
                .reviewId("rev_01")
                .poiId("poi_01")
                .authorName("Nguyễn Văn A")
                .rating(new BigDecimal("4.50"))
                .ratingCount(3L)
                .ratingOverall(new BigDecimal("4.20"))
                .reviewText("Địa điểm tuyệt vời")
                .reviewDate("2026-04-15")
                .sourceName("google")
                .build();

        when(reviewRepository.findByPoiIdAndDeletedAtIsNull(eq("poi_01"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(review)));

        PoiService.ReviewsPage response = poiService.getReviews("poi_01", 0, 10);
        assertThat(response.page().content()).hasSize(1);
        assertThat(response.page().content().getFirst().reviewId()).isEqualTo("rev_01");
        assertThat(response.ratingSummary()).hasSize(1);
        assertThat(response.ratingSummary().getFirst().ratingCount()).isEqualTo(3L);
        assertThat(response.ratingSummary().getFirst().ratingAvgScore()).isEqualTo(4.2);
        assertThat(response.page().content().getFirst().sourceName()).isEqualTo("google");
    }

    @Test
    @DisplayName("API 9: Ném ResourceNotFoundException khi POI không tồn tại")
    void shouldReturnEmptyRatingSummaryWhenNoReviews() {
        when(reviewRepository.findByPoiIdAndDeletedAtIsNull(eq("poi_unknown"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(Collections.emptyList()));

        PoiService.ReviewsPage response = poiService.getReviews("poi_unknown", 0, 10);
        assertThat(response.page().content()).isEmpty();
        assertThat(response.ratingSummary()).isEmpty();
    }

    // ── API 10: Amenities Tests ──────────────────────────────────────────────

    @Test
    @DisplayName("API 10: map cột amenity sang cây D-01, service_flags khác amenity_vi")
    void shouldMapAmenityColumnsToD01Fields() {
        SrvPoiAmenity row = SrvPoiAmenity.builder()
                .poiId("poi_01")
                .businessSector("accommodation")
                .amenityGroup("facilities_and_services")
                .amenityRaw("outdoorSeating")
                .amenity("outdoor_seating")
                .amenityEn("Outdoor Seating")
                .amenityVi("Không gian ngoài trời")
                .serviceFlags("Food/service")
                .build();

        when(amenityRepository.findByPoiIdAndDeletedAtIsNull("poi_01")).thenReturn(List.of(row));

        List<PoiAmenityGroupResponse> amenities = poiService.getAmenities("poi_01");
        assertThat(amenities).hasSize(1);
        assertThat(amenities.getFirst().amenityGroup()).isEqualTo("facilities_and_services");
        PoiAmenityGroupResponse.Item item = amenities.getFirst().items().getFirst();
        assertThat(item.amenityCode()).isEqualTo("outdoor_seating");
        assertThat(item.serviceFlags()).isEqualTo("Food/service");
    }

    @Test
    @DisplayName("API 10: sắp amenity_group rồi amenity_code rồi amenity_raw")
    void shouldOrderAmenityGroupsAndItemsDeterministically() {
        SrvPoiAmenity laterGroup = amenity("facilities_and_services", "wifi", "free_wi_fi");
        SrvPoiAmenity second = amenity("accessibility", "ramp_b", "wheelchair_ramp");
        SrvPoiAmenity first = amenity("accessibility", "ramp_a", "step_free");

        when(amenityRepository.findByPoiIdAndDeletedAtIsNull("poi_01"))
                .thenReturn(List.of(laterGroup, second, first));

        List<PoiAmenityGroupResponse> amenities = poiService.getAmenities("poi_01");
        assertThat(amenities).extracting(PoiAmenityGroupResponse::amenityGroup)
                .containsExactly("accessibility", "facilities_and_services");
        assertThat(amenities.getFirst().items()).extracting(PoiAmenityGroupResponse.Item::amenityCode)
                .containsExactly("step_free", "wheelchair_ramp");
    }

    @Test
    @DisplayName("API 10: bỏ dòng amenity_raw chứa json_type")
    void shouldFilterJsonTypeAmenityRows() {
        SrvPoiAmenity kept = amenity("accessibility", "ramp", "step_free");
        SrvPoiAmenity dirty = SrvPoiAmenity.builder()
                .poiId("poi_01")
                .businessSector("accommodation")
                .amenityGroup("accessibility")
                .amenityRaw("json_type in ('bar','pub')")
                .amenity("bar")
                .amenityEn("Bar")
                .amenityVi("Quán bar")
                .build();

        when(amenityRepository.findByPoiIdAndDeletedAtIsNull("poi_01")).thenReturn(List.of(kept, dirty));

        List<PoiAmenityGroupResponse> amenities = poiService.getAmenities("poi_01");
        assertThat(amenities.getFirst().items()).hasSize(1);
        assertThat(amenities.getFirst().items().getFirst().amenityCode()).isEqualTo("step_free");
    }

    @Test
    @DisplayName("API 10: Trả về danh sách rỗng khi không có tiện ích")
    void shouldReturnEmptyListWhenPoiHasNoAmenities() {
        when(amenityRepository.findByPoiIdAndDeletedAtIsNull("poi_empty")).thenReturn(Collections.emptyList());

        List<PoiAmenityGroupResponse> amenities = poiService.getAmenities("poi_empty");
        assertThat(amenities).isNotNull().isEmpty();
    }

    @Test
    @DisplayName("API 10: trả amenity khi không có dòng srv_poi_info")
    void shouldReturnAmenitiesWhenInfoRowIsAbsent() {
        when(amenityRepository.findByPoiIdAndDeletedAtIsNull("poi_amenity_only"))
                .thenReturn(List.of(amenity("accessibility", "ramp", "step_free")));

        List<PoiAmenityGroupResponse> amenities = poiService.getAmenities("poi_amenity_only");

        assertThat(amenities).hasSize(1);
        assertThat(amenities.getFirst().items().getFirst().amenityCode()).isEqualTo("step_free");
        verifyNoInteractions(poiInfoRepository);
    }

    @Test
    @DisplayName("normalizeSectors bỏ trống, khử trùng, và từ chối giá trị ngoài regex")
    void shouldNormalizeSectorPriority() {
        assertThat(poiService.normalizeSectors(null)).containsExactly("attraction", "f_n_b", "event", "tour_n_activities");
        assertThat(poiService.normalizeSectors(List.of(" Event ", "event", "f_n_b")))
                .containsExactly("event", "f_n_b");
        assertThatThrownBy(() -> poiService.normalizeSectors(List.of("Bad-Sector")))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("business_sector_priority contains an invalid value");
    }

    @Test
    @DisplayName("experiences lấy hàng vi khi en rỗng và gắn source_name")
    void shouldFallBackExperiencesToViWhenTargetEmpty() {
        SrvPoiMultiLang en = SrvPoiMultiLang.builder().poiId("poi_01").lang("en").sourceName("en-src").experience("[]").build();
        SrvPoiMultiLang vi = SrvPoiMultiLang.builder().poiId("poi_01").lang("vi").sourceName("partner")
                .experience("[{\"title\":\"A\",\"description\":\"B\",\"keyword\":\"walk\"},{\"title\":\" \",\"description\":\"\"},{\"title\":\"C\",\"description\":\"D\"},{\"title\":\"E\",\"description\":\"F\",\"keyword\":1}]")
                .build();
        when(multiLangRepository.findByPoiIdInAndLangIn(eq(List.of("poi_01")), eq(Set.of("en", "vi"))))
                .thenReturn(List.of(en, vi));

        PoiExperiencesResponse response = poiService.getExperiences("poi_01", "en");
        assertThat(response.items()).hasSize(3);
        assertThat(response.items()).allMatch(item -> "partner".equals(item.source()));
        assertThat(response.items().getFirst().title()).isEqualTo("A");
        assertThat(response.items()).extracting(PoiExperiencesResponse.Item::iconKey)
                .containsExactly("walk", null, null);
    }

    @Test
    @DisplayName("practical_info không có business_sector ngoài business_tags và có destinations.name")
    void shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector() throws Exception {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_01")
                .poiName("A")
                .businessSector("attraction")
                .destinationId("[\"dest_01\"]")
                .destinationName("[\"Ha Noi\"]")
                .build();
        when(legacyIdMapRepository.findPracticalInfoPage(eq(List.of("poi_01")), any(), any(), any(), anyBoolean(), anyInt(), anyLong()))
                .thenReturn(new SrvPoiLegacyIdMapRepositoryCustom.PracticalInfoSlice(List.of(poi), 1));
        when(multiLangRepository.findByPoiIdInAndLangIn(any(), any())).thenReturn(List.of());
        when(mediaGalleryRepository.findActiveCoversByPoiIdIn(any())).thenReturn(List.of());

        PoiPracticalInfoResponse info = poiService.getPracticalInfo("poi_01", "vi");
        com.fasterxml.jackson.databind.JsonNode node = new com.fasterxml.jackson.databind.ObjectMapper()
                .readTree(new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(info));
        assertThat(node.has("business_sector")).isFalse();
        assertThat(node.path("business_tags").path("business_sector").asText()).isEqualTo("attraction");
        assertThat(node.path("destinations").path("id").isArray()).isTrue();
        assertThat(node.path("destinations").path("name").get(0).asText()).isEqualTo("Ha Noi");
    }

    @Test
    @DisplayName("practical_info 404 khi không có info, và holiday_exceptions là nguyên text cột")
    void shouldThrowWhenPracticalInfoPoiMissing() throws Exception {
        when(legacyIdMapRepository.findPracticalInfoPage(eq(List.of("missing")), any(), any(), any(), anyBoolean(), anyInt(), anyLong()))
                .thenReturn(new SrvPoiLegacyIdMapRepositoryCustom.PracticalInfoSlice(List.of(), 0));
        assertThatThrownBy(() -> poiService.getPracticalInfo("missing", "vi"))
                .isInstanceOf(ResourceNotFoundException.class);

        SrvPoiInfo poi = SrvPoiInfo.builder().poiId("poi_01").poiName("A").sourceName("partner")
                .operatingHours("not-json").holidayExceptions("[ {\"date\" : \"02/09/2026\"} ]").build();
        when(legacyIdMapRepository.findPracticalInfoPage(eq(List.of("poi_01")), any(), any(), any(), anyBoolean(), anyInt(), anyLong()))
                .thenReturn(new SrvPoiLegacyIdMapRepositoryCustom.PracticalInfoSlice(List.of(poi), 1));
        when(multiLangRepository.findByPoiIdInAndLangIn(any(), any())).thenReturn(List.of(
                SrvPoiMultiLang.builder().poiId("poi_01").lang("vi").timeToSpend("{\"Thoi gian\":\"1 gio\"}").build()));
        when(mediaGalleryRepository.findActiveCoversByPoiIdIn(any())).thenReturn(List.of());

        PoiPracticalInfoResponse info = poiService.getPracticalInfo("poi_01", "vi");
        assertThat(info.holidayExceptions()).isEqualTo("[ {\"date\" : \"02/09/2026\"} ]");
        assertThat(new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(info))
                .contains("\"holiday_exceptions\":[ {\"date\" : \"02/09/2026\"} ]");
        assertThat(vn.visitvietnam.dataserving.service.util.StoredJsonParser.singleJsonValueOrNull("poi_01", "{"))
                .isNull();
        assertThat(vn.visitvietnam.dataserving.service.util.StoredJsonParser.singleJsonValueOrNull("poi_01", "{\"a\":1},\"x\""))
                .isNull();
        assertThat(info.timeToSpend().label()).isEqualTo("Thoi gian");
        assertThat(info.operatingHours()).isNull();
    }

    @Test
    @DisplayName("StoredJsonParser suy biến JSON hỏng và đọc giờ mở cửa")
    void shouldDegradeMalformedStoredJsonToNull() {
        assertThat(vn.visitvietnam.dataserving.service.util.StoredJsonParser.labelValue("p", "cost", "{")).isNull();
        assertThat(vn.visitvietnam.dataserving.service.util.StoredJsonParser.operatingHours("p", "[{}]")).isEmpty();
        var hours = vn.visitvietnam.dataserving.service.util.StoredJsonParser.operatingHours("p",
                "[{\"day_of_week\":1,\"open_time\":\"09:00\",\"close_time\":\"18:00\",\"is_open_all_day\":false,\"is_closed\":false}]");
        assertThat(hours).hasSize(1);
        assertThat(hours.getFirst().dayOfWeek()).isEqualTo(1);
    }

    @Test
    @DisplayName("labelValue đọc {text,label} thành {label,value} và bỏ shape khác")
    void labelValueReadsTextAndLabel() {
        var parsed = vn.visitvietnam.dataserving.service.util.StoredJsonParser.labelValue(
                "p", "cost", "{\"text\":\"Miễn phí\",\"label\":\"Chi phí\"}");
        assertThat(parsed.label()).isEqualTo("Chi phí");
        assertThat(parsed.value()).isEqualTo("Miễn phí");
        assertThat(vn.visitvietnam.dataserving.service.util.StoredJsonParser.labelValue(
                "p", "cost", "{\"text\":1,\"label\":\"Chi phí\"}")).isNull();
        assertThat(vn.visitvietnam.dataserving.service.util.StoredJsonParser.labelValue(
                "p", "cost", "{\"text\":\"a\",\"label\":\"b\",\"extra\":\"c\"}")).isNull();
    }

    @Test
    @DisplayName("destinationArray giữ thứ tự và chuỗi rỗng")
    void destinationArrayParsesStringArrayInOrder() {
        assertThat(PoiService.destinationArray("poi_01", "destination_id", "[\"a\",\"b\"]"))
                .containsExactly("a", "b");
        assertThat(PoiService.destinationArray("poi_01", "destination_id", "[\" a \",\"\",\"a\"]"))
                .containsExactly(" a ", "", "a");
        assertThat(PoiService.destinationArray("poi_01", "destination_id", "[]")).isEmpty();
    }

    @Test
    @DisplayName("destinationArray giữ dấu gạch chéo ngược")
    void destinationArrayKeepsBackslash() throws Exception {
        assertThat(PoiService.destinationArray("poi_01", "destination_id", "[\"a\\\\b\"]"))
                .containsExactly("a\\b");
        String json = new com.fasterxml.jackson.databind.ObjectMapper().writeValueAsString(
                new CompactPoiResponse.Destinations(List.of("a\\b"), null));
        assertThat(json).contains("[\"a\\\\b\"]");
    }

    @ParameterizedTest
    @NullSource
    @ValueSource(strings = {
            "", "   ", "null", "dest_01", "\"[\\\"a\\\"]\"", "{\"a\":1}", "1", "[\"a\"", "[\"a\"] x"
    })
    @DisplayName("destinationArray trả null khi rỗng hoặc không phải mảng")
    void destinationArrayReturnsNullForBlankOrNonArray(String raw) {
        assertThat(PoiService.destinationArray("poi_01", "destination_id", raw)).isNull();
    }

    @ParameterizedTest
    @ValueSource(strings = {"[\"a\",1]", "[\"a\",null]", "[true]", "[[\"a\"]]", "[{\"id\":\"a\"}]"})
    @DisplayName("destinationArray trả null khi phần tử không phải chuỗi")
    void destinationArrayReturnsNullWhenElementNotString(String raw) {
        assertThat(PoiService.destinationArray("poi_01", "destination_id", raw)).isNull();
    }

    @Test
    @DisplayName("một cột destination hỏng không làm mất cột còn lại")
    void compactKeepsOtherFieldWhenOneDestinationInvalid() {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_01")
                .poiName("A")
                .destinationId("not-json")
                .destinationName("[\"Ha Noi\"]")
                .build();
        when(poiInfoRepository.findAll(any(Specification.class), any(Sort.class))).thenReturn(List.of(poi));
        when(multiLangRepository.findByPoiIdInAndLangIn(any(), any())).thenReturn(List.of());
        CompactPoiResponse item = poiService.getCompactPois(List.of("poi_01"), "vi").getFirst();
        assertThat(item.destinations().id()).isNull();
        assertThat(item.destinations().name()).containsExactly("Ha Noi");
    }

    @Test
    @DisplayName("compact và practical info cùng hình destinations")
    void compactAndPracticalInfoShareDestinationsShape() throws Exception {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_01")
                .poiName("A")
                .destinationId("[\"dest_01\"]")
                .destinationName("[\"Ha Noi\"]")
                .build();
        when(poiInfoRepository.findAll(any(Specification.class), any(Sort.class))).thenReturn(List.of(poi));
        when(multiLangRepository.findByPoiIdInAndLangIn(any(), any())).thenReturn(List.of());
        when(legacyIdMapRepository.findPracticalInfoPage(any(), any(), any(), any(), anyBoolean(), anyInt(), anyLong()))
                .thenReturn(new SrvPoiLegacyIdMapRepositoryCustom.PracticalInfoSlice(List.of(poi), 1));
        when(mediaGalleryRepository.findActiveCoversByPoiIdIn(any())).thenReturn(List.of());
        com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
        com.fasterxml.jackson.databind.JsonNode compact = mapper.valueToTree(
                poiService.getCompactPois(List.of("poi_01"), "vi").getFirst()).path("destinations");
        com.fasterxml.jackson.databind.JsonNode detail = mapper.valueToTree(
                poiService.getPracticalInfo("poi_01", "vi")).path("destinations");
        assertThat(detail).isEqualTo(compact);
    }

    @Test
    @DisplayName("projection practical info giữ destinations là mảng")
    void searchPracticalInfoProjectionKeepsDestinationsArray() throws Exception {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_01")
                .poiName("A")
                .destinationId("[\"dest_01\"]")
                .destinationName("[\"Ha Noi\"]")
                .build();
        when(legacyIdMapRepository.findPracticalInfoPage(any(), any(), any(), any(), anyBoolean(), anyInt(), anyLong()))
                .thenReturn(new SrvPoiLegacyIdMapRepositoryCustom.PracticalInfoSlice(List.of(poi), 1));
        PracticalInfoQuery query = new PracticalInfoQuery(
                List.of("poi_01"),
                EnumSet.of(PracticalInfoQuery.Field.DESTINATIONS),
                null, null, "vi", 0, 10, null, Sort.Direction.ASC);
        Object item = poiService.searchPracticalInfo(query).items().getFirst();
        com.fasterxml.jackson.databind.JsonNode node = new com.fasterxml.jackson.databind.ObjectMapper().valueToTree(item);
        assertThat(node.path("destinations").path("id").isArray()).isTrue();
        assertThat(node.path("destinations").path("id").get(0).asText()).isEqualTo("dest_01");
    }

    private static SrvPoiAmenity amenity(String group, String raw, String code) {
        return SrvPoiAmenity.builder()
                .poiId("poi_01")
                .businessSector("accommodation")
                .amenityGroup(group)
                .amenityRaw(raw)
                .amenity(code)
                .amenityEn(code)
                .amenityVi(code)
                .serviceFlags("Suitability")
                .build();
    }
}

