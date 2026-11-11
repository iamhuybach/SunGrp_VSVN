package vn.visitvietnam.dataserving.domain.repository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.transaction.annotation.Transactional;
import vn.visitvietnam.dataserving.TestcontainersConfiguration;
import vn.visitvietnam.dataserving.domain.entity.PoiAmenityId;
import vn.visitvietnam.dataserving.domain.entity.PoiMediaGalleryId;
import vn.visitvietnam.dataserving.domain.entity.PoiMultiLangId;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiAmenity;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiInfo;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiMediaGallery;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiMultiLang;
import vn.visitvietnam.dataserving.domain.entity.SrvPoiReview;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@Import(TestcontainersConfiguration.class)
@SpringBootTest
@Transactional
class PoiRepositoryIntegrationTest {

    @Autowired
    private SrvPoiInfoRepository poiInfoRepository;

    @Autowired
    private SrvPoiMultiLangRepository poiMultiLangRepository;

    @Autowired
    private SrvPoiAmenityRepository poiAmenityRepository;

    @Autowired
    private SrvPoiMediaGalleryRepository poiMediaGalleryRepository;

    @Autowired
    private SrvPoiReviewRepository poiReviewRepository;

    private static final String TEST_POI_ID = "POI_VN_HAN_001";
    private static final String DESTINATION_ID = "DEST_HANOI";
    private static final String BUSINESS_CATEGORY = "ATTRACTION";

    @BeforeEach
    void setUp() {
        poiReviewRepository.deleteAll();
        poiMediaGalleryRepository.deleteAll();
        poiAmenityRepository.deleteAll();
        poiMultiLangRepository.deleteAll();
        poiInfoRepository.deleteAll();
    }

    @Test
    @DisplayName("SrvPoiInfoRepository: Lưu và truy vấn POI chính theo ID và Specification")
    void testSrvPoiInfoRepository() {
        SrvPoiInfo poi = SrvPoiInfo.builder()
                .poiId(TEST_POI_ID)
                .poiName("Hồ Hoàn Kiếm")
                .sourceName("DATA_POI_PIPELINE")
                .businessSector("TOURISM")
                .businessCategory(BUSINESS_CATEGORY)
                .destinationId(DESTINATION_ID)
                .lat(21.0285)
                .lng(105.8542)
                .operatingStatus("OPERATING")
                .isVerified(true)
                .isRecommended(true)
                .isBookable(false)
                .ratingOverall(new BigDecimal("4.85"))
                .ratingCount(1250)
                .reviewCount(350)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        poiInfoRepository.save(poi);

        Optional<SrvPoiInfo> foundById = poiInfoRepository.findById(TEST_POI_ID);
        assertThat(foundById).isPresent();
        assertThat(foundById.get().getPoiName()).isEqualTo("Hồ Hoàn Kiếm");
        assertThat(foundById.get().getLat()).isEqualTo(21.0285);
        assertThat(foundById.get().getRatingOverall()).isEqualByComparingTo("4.85");

        Specification<SrvPoiInfo> spec = (root, query, cb) ->
                cb.and(
                        cb.equal(root.get("destinationId"), DESTINATION_ID),
                        cb.isTrue(root.get("isRecommended"))
                );
        List<SrvPoiInfo> specResults = poiInfoRepository.findAll(spec);
        assertThat(specResults).hasSize(1);
    }

    @Test
    @DisplayName("SrvPoiMultiLangRepository: Lưu và truy vấn nội dung đa ngôn ngữ với Composite Key (poiId, lang)")
    void testSrvPoiMultiLangRepository() {
        SrvPoiMultiLang viLang = SrvPoiMultiLang.builder()
                .poiId(TEST_POI_ID)
                .lang("vi")
                .description("Trái tim của thủ đô Hà Nội")
                .experience("Đi dạo quanh hồ vào sáng sớm")
                .timeToSpend("1-2 hours")
                .costVnd("Miễn phí")
                .createdAt(LocalDateTime.now())
                .build();

        SrvPoiMultiLang enLang = SrvPoiMultiLang.builder()
                .poiId(TEST_POI_ID)
                .lang("en")
                .description("The heart of Hanoi capital")
                .experience("Morning walk around the lake")
                .timeToSpend("1-2 hours")
                .costVnd("Free")
                .createdAt(LocalDateTime.now())
                .build();

        poiMultiLangRepository.saveAll(List.of(viLang, enLang));

        Optional<SrvPoiMultiLang> foundVi = poiMultiLangRepository.findById(
                new PoiMultiLangId(TEST_POI_ID, "vi")
        );
        assertThat(foundVi).isPresent();
        assertThat(foundVi.get().getDescription()).isEqualTo("Trái tim của thủ đô Hà Nội");

        Optional<SrvPoiMultiLang> foundEn = poiMultiLangRepository.findById(
                new PoiMultiLangId(TEST_POI_ID, "en")
        );
        assertThat(foundEn).isPresent();
        assertThat(foundEn.get().getDescription()).isEqualTo("The heart of Hanoi capital");

        List<SrvPoiMultiLang> all = poiMultiLangRepository.findAll();
        assertThat(all).hasSize(2);
    }

    @Test
    @DisplayName("SrvPoiAmenityRepository: Lưu và truy vấn tiện ích với Composite Key 4 trường")
    void testSrvPoiAmenityRepository() {
        SrvPoiAmenity amenity1 = SrvPoiAmenity.builder()
                .poiId(TEST_POI_ID)
                .businessSector("TOURISM")
                .amenityGroup("GENERAL")
                .amenityRaw("WIFI_FREE")
                .amenity("Free Wi-Fi")
                .amenityVi("Wi-Fi miễn phí")
                .createdAt(LocalDateTime.now())
                .build();

        SrvPoiAmenity amenity2 = SrvPoiAmenity.builder()
                .poiId(TEST_POI_ID)
                .businessSector("TOURISM")
                .amenityGroup("PARKING")
                .amenityRaw("MOTORBIKE_PARKING")
                .amenity("Motorbike Parking")
                .amenityVi("Bãi đỗ xe máy")
                .createdAt(LocalDateTime.now())
                .build();

        poiAmenityRepository.saveAll(List.of(amenity1, amenity2));

        Optional<SrvPoiAmenity> found = poiAmenityRepository.findById(
                new PoiAmenityId(TEST_POI_ID, "TOURISM", "GENERAL", "WIFI_FREE")
        );
        assertThat(found).isPresent();
        assertThat(found.get().getAmenityVi()).isEqualTo("Wi-Fi miễn phí");

        List<SrvPoiAmenity> all = poiAmenityRepository.findAll();
        assertThat(all).hasSize(2);
    }

    @Test
    @DisplayName("SrvPoiMediaGalleryRepository: Lưu và truy vấn media")
    void testSrvPoiMediaGalleryRepository() {
        SrvPoiMediaGallery media1 = SrvPoiMediaGallery.builder()
                .mediaId("MED_001")
                .poiId(TEST_POI_ID)
                .displayOrder(2)
                .blobUrl("https://cdn.example.com/lake_day.jpg")
                .isActive(true)
                .isCover(false)
                .createdAt(LocalDateTime.now())
                .build();

        SrvPoiMediaGallery media2 = SrvPoiMediaGallery.builder()
                .mediaId("MED_002")
                .poiId(TEST_POI_ID)
                .displayOrder(1)
                .blobUrl("https://cdn.example.com/lake_cover.jpg")
                .isActive(true)
                .isCover(true)
                .createdAt(LocalDateTime.now())
                .build();

        poiMediaGalleryRepository.saveAll(List.of(media1, media2));

        Optional<SrvPoiMediaGallery> found = poiMediaGalleryRepository.findById(new PoiMediaGalleryId("MED_002", TEST_POI_ID));
        assertThat(found).isPresent();
        assertThat(found.get().getBlobUrl()).isEqualTo("https://cdn.example.com/lake_cover.jpg");

        List<SrvPoiMediaGallery> all = poiMediaGalleryRepository.findAll();
        assertThat(all).hasSize(2);
    }

    @Test
    @DisplayName("SrvPoiReviewRepository: Lưu và phân trang truy vấn đánh giá")
    void testSrvPoiReviewRepository() {
        SrvPoiReview review1 = SrvPoiReview.builder()
                .reviewId("REV_001")
                .poiId(TEST_POI_ID)
                .authorName("Nguyen Van A")
                .rating(new BigDecimal("5.00"))
                .ratingCount(100L)
                .title("Tuyệt vời")
                .reviewText("Cảnh quan rất đẹp vào buổi tối.")
                .createdAt(LocalDateTime.now())
                .build();

        SrvPoiReview review2 = SrvPoiReview.builder()
                .reviewId("REV_002")
                .poiId(TEST_POI_ID)
                .authorName("John Doe")
                .rating(new BigDecimal("4.50"))
                .ratingCount(50L)
                .title("Must visit")
                .reviewText("Historical place in the center of Hanoi.")
                .createdAt(LocalDateTime.now())
                .build();

        poiReviewRepository.saveAll(List.of(review1, review2));

        Page<SrvPoiReview> reviewPage = poiReviewRepository.findAll(PageRequest.of(0, 10));

        assertThat(reviewPage.getTotalElements()).isEqualTo(2);
        assertThat(reviewPage.getContent()).extracting(SrvPoiReview::getAuthorName)
                .containsExactlyInAnyOrder("Nguyen Van A", "John Doe");
    }

    @Test
    @DisplayName("Gallery page sorts display_order then media_id, and cover is the first active cover")
    void shouldPageGalleryByDisplayOrderThenMediaId() {
        poiMediaGalleryRepository.saveAll(List.of(
                gallery("media-z", 2, false),
                gallery("media-a", null, false),
                gallery("media-m", 1, true),
                gallery("media-c", 0, true)
        ));
        poiMediaGalleryRepository.flush();

        Page<SrvPoiMediaGallery> page = poiMediaGalleryRepository.findActivePageByPoiId(TEST_POI_ID, PageRequest.of(0, 10));
        assertThat(page.getContent()).extracting(SrvPoiMediaGallery::getMediaId)
                .containsExactly("media-c", "media-m", "media-z", "media-a");

        List<SrvPoiMediaGallery> covers = poiMediaGalleryRepository.findActiveCoverByPoiId(TEST_POI_ID, PageRequest.of(0, 1));
        assertThat(covers).extracting(SrvPoiMediaGallery::getMediaId).containsExactly("media-c");
    }

    @Test
    @DisplayName("Features round-robin prefers recommended rows, then rating fallback, and honors rating_source")
    void shouldRoundRobinFeaturesBySectorPriority() {
        poiInfoRepository.saveAll(List.of(
                feature("a-1", "attraction", true, null, null, "partner"),
                feature("a-2", "attraction", false, "4.80", 200, "partner"),
                feature("b-1", "f_n_b", true, null, null, "partner"),
                feature("e-1", "event", false, "4.90", 150, "other"),
                feature("e-low", "event", false, "4.00", 10, "partner"),
                feature("acc-1", "accommodation", true, null, null, "partner"),
                feature("blank-1", "  ", true, null, null, "partner")
        ));
        poiInfoRepository.flush();

        List<String> ids = poiInfoRepository.findFeatureIds(
                "attraction,f_n_b,event", new BigDecimal("4.5"), 100, "", 10, 0);
        assertThat(ids).containsExactly("a-1", "b-1", "e-1", "a-2");
        assertThat(poiInfoRepository.countFeatures("attraction,f_n_b,event", new BigDecimal("4.5"), 100, "")).isEqualTo(4);

        List<String> partnerOnly = poiInfoRepository.findFeatureIds(
                "attraction,f_n_b,event", new BigDecimal("4.5"), 100, "partner", 10, 0);
        assertThat(partnerOnly).containsExactly("a-1", "b-1", "a-2");
    }

    private SrvPoiMediaGallery gallery(String mediaId, Integer displayOrder, boolean cover) {
        return SrvPoiMediaGallery.builder()
                .mediaId(mediaId)
                .poiId(TEST_POI_ID)
                .displayOrder(displayOrder)
                .blobUrl("pois/" + mediaId + ".jpg")
                .isActive(true)
                .isCover(cover)
                .build();
    }

    private SrvPoiInfo feature(String poiId, String sector, boolean recommended, String rating, Integer count, String source) {
        return SrvPoiInfo.builder()
                .poiId(poiId)
                .poiName(poiId)
                .sourceName(source)
                .businessSector(sector)
                .isRecommended(recommended)
                .ratingOverall(rating == null ? null : new BigDecimal(rating))
                .ratingCount(count)
                .createdAt(LocalDateTime.now())
                .build();
    }
}
