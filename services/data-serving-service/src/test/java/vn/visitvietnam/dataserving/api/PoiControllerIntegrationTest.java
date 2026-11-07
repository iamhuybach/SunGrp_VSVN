package vn.visitvietnam.dataserving.api;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import vn.visitvietnam.dataserving.api.dto.CompactPoiResponse;
import vn.visitvietnam.dataserving.api.dto.PoiAmenityGroupResponse;
import vn.visitvietnam.dataserving.api.dto.PoiGalleryItemResponse;
import vn.visitvietnam.dataserving.api.dto.PoiReviewItemResponse;
import vn.visitvietnam.dataserving.common.dto.PageResponse;
import vn.visitvietnam.dataserving.common.exception.ResourceNotFoundException;
import vn.visitvietnam.dataserving.common.web.GlobalExceptionHandler;
import vn.visitvietnam.dataserving.common.web.RequestIdFilter;
import vn.visitvietnam.dataserving.service.PoiService;
import vn.visitvietnam.dataserving.service.util.LanguageResolver;

import java.util.Collections;
import java.util.List;

import static org.hamcrest.Matchers.nullValue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(PoiController.class)
@Import({GlobalExceptionHandler.class, LanguageResolver.class, RequestIdFilter.class})
class PoiControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private PoiService poiService;

    // ── API 1: Compact POIs Endpoint Tests ───────────────────────────────────

    @Test
    @DisplayName("GET /api/v1/pois/compact trả về 200 OK với cấu trúc envelope chuẩn")
    void shouldReturnCompactPois() throws Exception {
        CompactPoiResponse item = new CompactPoiResponse(
                "poi_01",
                "Hồ Hoàn Kiếm",
                "Trái tim thủ đô",
                new CompactPoiResponse.Cover("med_01", "https://cdn.example.com/cover.jpg", 1920, 1080, "image/jpeg"),
                new CompactPoiResponse.Rating(4.9, 5000),
                new CompactPoiResponse.BusinessTags("ATTRACTION", "Điểm tham quan", "landmark", List.of("heritage")),
                new CompactPoiResponse.Address("Hoàn Kiếm, Hà Nội", "Đinh Tiên Hoàng", null, "Hoàn Kiếm", "Hà Nội", "VN"),
                new CompactPoiResponse.GeoLocation(21.0285, 105.8542)
        );

        when(poiService.getCompactPois(any(), any(), anyInt(), anyInt(), any()))
                .thenReturn(PageResponse.of(List.of(item), 0, 20, 1));

        mockMvc.perform(get("/api/v1/pois/compact")
                        .param("page", "0")
                        .param("size", "20")
                        .header("Accept-Language", "vi-VN,vi;q=0.9"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("Compact POIs retrieved successfully"))
                .andExpect(jsonPath("$.data[0].id").value("poi_01"))
                .andExpect(jsonPath("$.data[0].name").value("Hồ Hoàn Kiếm"))
                .andExpect(jsonPath("$.data[0].cover.id").value("med_01"))
                .andExpect(jsonPath("$.data[0].cover.file_key").value("https://cdn.example.com/cover.jpg"))
                .andExpect(jsonPath("$.data[0].geo_location.latitude").value(21.0285))
                .andExpect(jsonPath("$.data[0].geo_location.longitude").value(105.8542))
                .andExpect(jsonPath("$.meta.pagination.type").value("offset"))
                .andExpect(jsonPath("$.meta.pagination.total_items").value(1))
                .andExpect(jsonPath("$.meta.trace_id").isNotEmpty())
                .andExpect(jsonPath("$.meta.timestamp").isNotEmpty())
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }

    @Test
    @DisplayName("GET /api/v1/pois/compact với trace_id header lan truyền đúng vào meta.trace_id")
    void shouldPropagateTraceIdHeader() throws Exception {
        when(poiService.getCompactPois(any(), any(), anyInt(), anyInt(), any()))
                .thenReturn(PageResponse.of(Collections.emptyList(), 0, 20, 0));

        mockMvc.perform(get("/api/v1/pois/compact")
                        .header("X-Request-Id", "custom-req-trace-42"))
                .andExpect(status().isOk())
                .andExpect(header().string("X-Request-Id", "custom-req-trace-42"))
                .andExpect(jsonPath("$.meta.trace_id").value("custom-req-trace-42"))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data").isEmpty());
    }

    @Test
    @DisplayName("GET /api/v1/pois/compact với size > 100 trả về 422 Unprocessable Entity với meta.error_code ERR_VALIDATION_FAILED")
    void shouldReturn422WhenCompactSizeExceedsMax() throws Exception {
        mockMvc.perform(get("/api/v1/pois/compact")
                        .param("size", "150"))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value(422))
                .andExpect(jsonPath("$.meta.error_code").value("ERR_VALIDATION_FAILED"))
                .andExpect(jsonPath("$.data").value(nullValue()))
                .andExpect(jsonPath("$.errors[0].field").value("size"));
    }

    @Test
    @DisplayName("GET /api/v1/pois/compact với query param ids và Accept-Language trả về danh sách lọc")
    void shouldSupportGetCompactPoisWithIdsAndAcceptLanguage() throws Exception {
        CompactPoiResponse item = new CompactPoiResponse(
                "poi_02",
                "Chùa Một Cột",
                "Di tích lịch sử",
                null,
                new CompactPoiResponse.Rating(4.8, 1200),
                new CompactPoiResponse.BusinessTags("ATTRACTION", "Điểm tham quan", "pagoda", List.of("pagoda")),
                null,
                null
        );

        when(poiService.getCompactPois(eq(List.of("poi_02")), eq("en"), eq(0), eq(20), any()))
                .thenReturn(PageResponse.of(List.of(item), 0, 20, 1));

        mockMvc.perform(get("/api/v1/pois/compact")
                        .param("ids", "poi_02")
                        .header("Accept-Language", "en-US,en;q=0.9"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data[0].id").value("poi_02"))
                .andExpect(jsonPath("$.data[0].name").value("Chùa Một Cột"))
                .andExpect(jsonPath("$.meta.pagination.total_items").value(1));
    }

    // ── API 3: Gallery Endpoint Tests ────────────────────────────────────────

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/gallery trả về 200 OK với đầy đủ trường metadata và blur_hash null")
    void shouldReturnGallerySuccessfully() throws Exception {
        PoiGalleryItemResponse item = new PoiGalleryItemResponse(
                "med_01",
                "https://cdn.example.com/img1.webp",
                1920,
                1080,
                "image/webp",
                null,
                1
        );

        when(poiService.getGallery("poi_01")).thenReturn(List.of(item));

        mockMvc.perform(get("/api/v1/pois/poi_01/gallery"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("POI gallery retrieved successfully"))
                .andExpect(jsonPath("$.data.length()").value(1))
                .andExpect(jsonPath("$.data[0].id").value("med_01"))
                .andExpect(jsonPath("$.data[0].file_key").value("https://cdn.example.com/img1.webp"))
                .andExpect(jsonPath("$.data[0].width").value(1920))
                .andExpect(jsonPath("$.data[0].height").value(1080))
                .andExpect(jsonPath("$.data[0].mime_type").value("image/webp"))
                .andExpect(jsonPath("$.data[0].blur_hash").value(nullValue()))
                .andExpect(jsonPath("$.data[0].display_order").value(1))
                .andExpect(jsonPath("$.meta.trace_id").isNotEmpty())
                .andExpect(jsonPath("$.meta.timestamp").isNotEmpty())
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/gallery trả về 200 OK với data rỗng khi POI không có ảnh")
    void shouldReturnEmptyGalleryWhenPoiHasNoMedia() throws Exception {
        when(poiService.getGallery("poi_empty")).thenReturn(Collections.emptyList());

        mockMvc.perform(get("/api/v1/pois/poi_empty/gallery"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data").isEmpty())
                .andExpect(jsonPath("$.meta.trace_id").isNotEmpty())
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/gallery trả về 404 Not Found khi POI không tồn tại hoặc đã bị xóa mềm")
    void shouldReturn404WhenGalleryPoiNotFound() throws Exception {
        when(poiService.getGallery("poi_unknown"))
                .thenThrow(new ResourceNotFoundException("POI not found with id: poi_unknown"));

        mockMvc.perform(get("/api/v1/pois/poi_unknown/gallery"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value(404))
                .andExpect(jsonPath("$.meta.error_code").value("POI_NOT_FOUND"))
                .andExpect(jsonPath("$.data").value(nullValue()))
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }

    // ── API 9: Reviews Endpoint Tests ────────────────────────────────────────

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/reviews trả về 200 OK với danh sách reviews")
    void shouldReturnReviewsSuccessfully() throws Exception {
        PoiReviewItemResponse review = new PoiReviewItemResponse(
                "rev_01",
                "Nguyễn Văn A",
                4.5,
                "Rất tuyệt vời",
                "2026-04-10"
        );

        when(poiService.getReviews(eq("poi_01"), anyInt(), anyInt()))
                .thenReturn(PageResponse.of(List.of(review), 0, 10, 1));

        mockMvc.perform(get("/api/v1/pois/poi_01/reviews")
                        .param("page", "0")
                        .param("size", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data[0].review_id").value("rev_01"))
                .andExpect(jsonPath("$.meta.pagination.total_items").value(1))
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/reviews với size > 100 trả về 422 Unprocessable Entity")
    void shouldReturn422WhenReviewsSizeExceedsMax() throws Exception {
        mockMvc.perform(get("/api/v1/pois/poi_01/reviews")
                        .param("size", "120"))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value(422))
                .andExpect(jsonPath("$.meta.error_code").value("ERR_VALIDATION_FAILED"))
                .andExpect(jsonPath("$.errors[0].field").value("size"));
    }

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/reviews trả về 404 Not Found khi POI không tồn tại")
    void shouldReturn404WhenReviewsPoiNotFound() throws Exception {
        when(poiService.getReviews(eq("poi_unknown"), anyInt(), anyInt()))
                .thenThrow(new ResourceNotFoundException("POI not found with id: poi_unknown"));

        mockMvc.perform(get("/api/v1/pois/poi_unknown/reviews"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value(404))
                .andExpect(jsonPath("$.meta.error_code").value("POI_NOT_FOUND"))
                .andExpect(jsonPath("$.data").value(nullValue()));
    }

    // ── API 10: Amenities Endpoint Tests ─────────────────────────────────────

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/amenities trả về 200 OK với nhóm tiện ích và hiển thị null tường minh")
    void shouldReturnAmenitiesSuccessfully() throws Exception {
        PoiAmenityGroupResponse group = new PoiAmenityGroupResponse(
                "FACILITY",
                "Tiện nghi cơ sở",
                List.of(new PoiAmenityGroupResponse.Item("parking", "Bãi đỗ xe", null))
        );

        when(poiService.getAmenities("poi_01", "vi")).thenReturn(List.of(group));

        mockMvc.perform(get("/api/v1/pois/poi_01/amenities"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("POI amenities retrieved successfully"))
                .andExpect(jsonPath("$.data.length()").value(1))
                .andExpect(jsonPath("$.data[0].amenity_group").value("FACILITY"))
                .andExpect(jsonPath("$.data[0].amenity_vi").value("Tiện nghi cơ sở"))
                .andExpect(jsonPath("$.data[0].items[0].amenity_code").value("parking"))
                .andExpect(jsonPath("$.data[0].items[0].amenity_label").value("Bãi đỗ xe"))
                .andExpect(jsonPath("$.data[0].items[0].service_flags").value(nullValue()))
                .andExpect(jsonPath("$.meta.trace_id").isNotEmpty())
                .andExpect(jsonPath("$.meta.timestamp").isNotEmpty())
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/amenities hỗ trợ đa ngôn ngữ qua query param lang và Accept-Language")
    void shouldSupportAmenitiesMultiLanguage() throws Exception {
        PoiAmenityGroupResponse group = new PoiAmenityGroupResponse(
                "FACILITY",
                "Facilities",
                List.of(new PoiAmenityGroupResponse.Item("parking", "Parking Lot", "free"))
        );

        when(poiService.getAmenities("poi_01", "en")).thenReturn(List.of(group));

        mockMvc.perform(get("/api/v1/pois/poi_01/amenities")
                        .header("Accept-Language", "en-US,en;q=0.9"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data[0].amenity_vi").value("Facilities"))
                .andExpect(jsonPath("$.data[0].items[0].amenity_label").value("Parking Lot"));
    }

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/amenities trả về 200 OK với data rỗng khi POI không có tiện ích")
    void shouldReturnEmptyListWhenPoiHasNoAmenities() throws Exception {
        when(poiService.getAmenities("poi_empty", "vi")).thenReturn(Collections.emptyList());

        mockMvc.perform(get("/api/v1/pois/poi_empty/amenities"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data").isEmpty())
                .andExpect(jsonPath("$.meta.trace_id").isNotEmpty())
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }

    @Test
    @DisplayName("GET /api/v1/pois/{poi_id}/amenities trả về 404 Not Found khi POI không tồn tại hoặc đã bị xóa mềm")
    void shouldReturn404WhenAmenitiesPoiNotFound() throws Exception {
        when(poiService.getAmenities("poi_unknown", "vi"))
                .thenThrow(new ResourceNotFoundException("POI not found with id: poi_unknown"));

        mockMvc.perform(get("/api/v1/pois/poi_unknown/amenities"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.code").value(404))
                .andExpect(jsonPath("$.meta.error_code").value("POI_NOT_FOUND"))
                .andExpect(jsonPath("$.data").value(nullValue()))
                .andExpect(jsonPath("$.errors").value(nullValue()));
    }
}
