package vn.visitvietnam.dataserving.service;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
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

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
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

    @InjectMocks
    private PoiService poiService;

    // ── API 1: Compact POIs Tests ────────────────────────────────────────────

    @Test
    @DisplayName("API 1: Lấy danh sách Compact POI thành công kèm media và đa ngôn ngữ")
    void shouldReturnCompactPoisSuccessfully() {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_01")
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
                .isVerified(true)
                .isRecommended(true)
                .isBookable(false)
                .operatingStatus("OPERATIONAL")
                .build();

        when(poiInfoRepository.findAll(any(Specification.class), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(poi)));

        SrvPoiMediaGallery coverMedia = SrvPoiMediaGallery.builder()
                .mediaId("med_01")
                .poiId("poi_01")
                .blobUrl("https://cdn.example.com/cover.webp")
                .widthPx(1920)
                .heightPx(1080)
                .isCover(true)
                .isActive(true)
                .build();

        when(mediaGalleryRepository.findActiveByPoiIdInOrderByDisplayOrderAsc(List.of("poi_01")))
                .thenReturn(List.of(coverMedia));

        SrvPoiMultiLang enLang = SrvPoiMultiLang.builder()
                .poiId("poi_01")
                .lang("en")
                .description("Historical theater")
                .build();

        when(multiLangRepository.findByPoiIdInAndLangIn(eq(List.of("poi_01")), eq(Set.of("en", "vi"))))
                .thenReturn(List.of(enLang));

        PageResponse<CompactPoiResponse> response = poiService.getCompactPois(null, "en", 0, 10, "createdAt,desc");

        assertThat(response.content()).hasSize(1);
        CompactPoiResponse item = response.content().getFirst();
        assertThat(item.id()).isEqualTo("poi_01");
        assertThat(item.name()).isEqualTo("Nhà hát Lớn");
        assertThat(item.description()).isEqualTo("Historical theater");
        assertThat(item.cover().fileKey()).isEqualTo("https://cdn.example.com/cover.webp");
        assertThat(item.cover().mimeType()).isEqualTo("image/webp");
        assertThat(item.businessTags().primaryCategoryLabel()).isEqualTo("Điểm tham quan");
        assertThat(item.businessTags().subcategories()).containsExactly("architecture", "culture");
        assertThat(item.rating().overall()).isEqualTo(4.80);
    }

    @Test
    @DisplayName("API 1: Lấy danh sách Compact POI với lang=vi không bị duplicate element")
    void shouldReturnCompactPoisWithViLang() {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId("poi_vi")
                .poiName("Chùa Một Cột")
                .businessSector("ATTRACTION")
                .build();

        when(poiInfoRepository.findAll(any(Specification.class), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(poi)));
        when(mediaGalleryRepository.findActiveByPoiIdInOrderByDisplayOrderAsc(List.of("poi_vi")))
                .thenReturn(Collections.emptyList());
        when(multiLangRepository.findByPoiIdInAndLangIn(eq(List.of("poi_vi")), eq(Set.of("vi"))))
                .thenReturn(Collections.emptyList());

        PageResponse<CompactPoiResponse> response = poiService.getCompactPois(null, "vi", 0, 10, null);

        assertThat(response.content()).hasSize(1);
        assertThat(response.content().getFirst().name()).isEqualTo("Chùa Một Cột");
    }

    @Test
    @DisplayName("API 1: Trả về trang rỗng an toàn khi không tìm thấy POI")
    void shouldReturnEmptyPageWhenNoPois() {
        when(poiInfoRepository.findAll(any(Specification.class), any(Pageable.class)))
                .thenReturn(new PageImpl<>(Collections.emptyList()));

        PageResponse<CompactPoiResponse> response = poiService.getCompactPois(null, "vi", 0, 10, null);
        assertThat(response.content()).isEmpty();
        assertThat(response.totalElements()).isZero();
    }

    // ── API 3: Gallery Tests ─────────────────────────────────────────────────

    @Test
    @DisplayName("API 3: Lấy thư viện ảnh gallery thành công theo thứ tự sắp xếp và fallback photoApiUri")
    void shouldReturnGallerySuccessfully() {
        when(poiInfoRepository.existsByPoiIdAndDeletedAtIsNull("poi_01")).thenReturn(true);

        SrvPoiMediaGallery m1 = SrvPoiMediaGallery.builder()
                .mediaId("med_01")
                .poiId("poi_01")
                .blobUrl("https://cdn.example.com/img1.webp")
                .widthPx(1920)
                .heightPx(1080)
                .displayOrder(1)
                .isActive(true)
                .build();

        SrvPoiMediaGallery m2 = SrvPoiMediaGallery.builder()
                .mediaId("med_02")
                .poiId("poi_01")
                .photoApiUri("https://photos.example.com/img2.jpg")
                .widthPx(800)
                .heightPx(600)
                .displayOrder(2)
                .isActive(true)
                .build();

        when(mediaGalleryRepository.findActiveByPoiIdOrderByDisplayOrderAsc("poi_01"))
                .thenReturn(List.of(m1, m2));

        List<PoiGalleryItemResponse> gallery = poiService.getGallery("poi_01");
        assertThat(gallery).hasSize(2);

        PoiGalleryItemResponse item1 = gallery.get(0);
        assertThat(item1.id()).isEqualTo("med_01");
        assertThat(item1.mediaId()).isEqualTo("med_01");
        assertThat(item1.fileKey()).isEqualTo("https://cdn.example.com/img1.webp");
        assertThat(item1.width()).isEqualTo(1920);
        assertThat(item1.height()).isEqualTo(1080);
        assertThat(item1.mimeType()).isEqualTo("image/webp");
        assertThat(item1.blurHash()).isNull();
        assertThat(item1.displayOrder()).isEqualTo(1);

        PoiGalleryItemResponse item2 = gallery.get(1);
        assertThat(item2.id()).isEqualTo("med_02");
        assertThat(item2.fileKey()).isEqualTo("https://photos.example.com/img2.jpg");
        assertThat(item2.mimeType()).isEqualTo("image/jpeg");
        assertThat(item2.displayOrder()).isEqualTo(2);
    }

    @Test
    @DisplayName("API 3: Trả về danh sách rỗng khi POI hợp lệ nhưng không có ảnh gallery")
    void shouldReturnEmptyListWhenPoiHasNoGalleryMedia() {
        when(poiInfoRepository.existsByPoiIdAndDeletedAtIsNull("poi_empty")).thenReturn(true);
        when(mediaGalleryRepository.findActiveByPoiIdOrderByDisplayOrderAsc("poi_empty"))
                .thenReturn(Collections.emptyList());

        List<PoiGalleryItemResponse> gallery = poiService.getGallery("poi_empty");
        assertThat(gallery).isNotNull().isEmpty();
    }

    @Test
    @DisplayName("API 3: Ném ResourceNotFoundException khi POI không tồn tại")
    void shouldThrowWhenPoiNotFoundInGallery() {
        when(poiInfoRepository.existsByPoiIdAndDeletedAtIsNull("poi_unknown")).thenReturn(false);

        assertThatThrownBy(() -> poiService.getGallery("poi_unknown"))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("POI not found with id: poi_unknown");
    }

    // ── API 9: Reviews Tests ─────────────────────────────────────────────────

    @Test
    @DisplayName("API 9: Lấy danh sách review có phân trang")
    void shouldReturnReviewsSuccessfully() {
        when(poiInfoRepository.existsByPoiIdAndDeletedAtIsNull("poi_01")).thenReturn(true);

        SrvPoiReview review = SrvPoiReview.builder()
                .reviewId("rev_01")
                .poiId("poi_01")
                .authorName("Nguyễn Văn A")
                .rating(new BigDecimal("4.50"))
                .reviewText("Địa điểm tuyệt vời")
                .reviewDate("2026-04-15")
                .build();

        when(reviewRepository.findByPoiIdAndDeletedAtIsNull(eq("poi_01"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(review)));

        PageResponse<PoiReviewItemResponse> response = poiService.getReviews("poi_01", 0, 10);
        assertThat(response.content()).hasSize(1);
        assertThat(response.content().getFirst().reviewId()).isEqualTo("rev_01");
        assertThat(response.content().getFirst().rating()).isEqualTo(4.5);
    }

    @Test
    @DisplayName("API 9: Ném ResourceNotFoundException khi POI không tồn tại")
    void shouldThrowWhenPoiNotFoundInReviews() {
        when(poiInfoRepository.existsByPoiIdAndDeletedAtIsNull("poi_unknown")).thenReturn(false);

        assertThatThrownBy(() -> poiService.getReviews("poi_unknown", 0, 10))
                .isInstanceOf(ResourceNotFoundException.class);
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
        assertThat(item.amenityLabelEn()).isEqualTo("Outdoor Seating");
        assertThat(item.amenityLabelVi()).isEqualTo("Không gian ngoài trời");
        assertThat(item.serviceFlags()).isEqualTo("Food/service");
        assertThat(item.serviceFlags()).isNotEqualTo(item.amenityLabelVi());
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

