package vn.visitvietnam.dataserving.api;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import vn.visitvietnam.dataserving.api.dto.CompactPoiResponse;
import vn.visitvietnam.dataserving.api.dto.PoiAmenityGroupResponse;
import vn.visitvietnam.dataserving.api.dto.PoiGalleryItemResponse;
import vn.visitvietnam.dataserving.api.dto.PoiReviewItemResponse;
import vn.visitvietnam.dataserving.common.dto.ApiResponse;
import vn.visitvietnam.dataserving.common.dto.PageResponse;
import vn.visitvietnam.dataserving.common.dto.PaginationMeta;
import vn.visitvietnam.dataserving.service.PoiService;
import vn.visitvietnam.dataserving.service.util.LanguageResolver;

import java.util.List;

@Tag(name = "POI API", description = "API đọc dữ liệu địa điểm du lịch (POIs) - Compact, Gallery, Reviews và Amenities")
@Validated
@RestController
@RequestMapping("/api/v1/pois")
@RequiredArgsConstructor
public class PoiController {

    private final PoiService poiService;
    private final LanguageResolver languageResolver;

    // ── API 1: Compact POIs (GET) ────────────────────────────────────────────

    @Operation(summary = "Truy vấn danh sách POI rút gọn (Compact POIs)", description = "Hỗ trợ phân trang, lọc theo danh sách ID, sắp xếp và đa ngôn ngữ")
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Truy vấn thành công"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Tham số truy vấn không hợp lệ", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "422", description = "Dữ liệu đầu vào vi phạm validation", content = @Content(schema = @Schema(implementation = ApiResponse.class)))
    })
    @GetMapping("/compact")
    public ResponseEntity<ApiResponse<List<CompactPoiResponse>>> getCompactPois(
            @Parameter(description = "Danh sách POI ID cần lọc (tối đa 100 ID)")
            @RequestParam(name = "ids", required = false) List<String> ids,

            @Parameter(description = "Mã ngôn ngữ yêu cầu (vd: vi, en, ko, ja)")
            @RequestParam(name = "lang", required = false) String lang,

            @Parameter(description = "Header ngôn ngữ ưu tiên của trình duyệt/ứng dụng (vd: en-US,en;q=0.9,vi;q=0.8)")
            @RequestHeader(name = "Accept-Language", required = false) String acceptLanguage,

            @Parameter(description = "Số thứ tự trang (bắt đầu từ 0)")
            @RequestParam(name = "page", defaultValue = "0") @Min(0) int page,

            @Parameter(description = "Số lượng phần tử trên mỗi trang (tối đa 100)")
            @RequestParam(name = "size", defaultValue = "20") @Min(1) @Max(100) int size,

            @Parameter(description = "Tiêu chí sắp xếp (vd: createdAt,desc)")
            @RequestParam(name = "sort", required = false) String sort
    ) {
        String resolvedLang = languageResolver.resolveLanguage(lang, acceptLanguage);
        PageResponse<CompactPoiResponse> response = poiService.getCompactPois(ids, resolvedLang, page, size, sort);
        PaginationMeta pagination = PaginationMeta.offset(response.page(), response.size(), response.totalElements());
        return ResponseEntity.ok(ApiResponse.successList(response.content(), pagination, "Compact POIs retrieved successfully"));
    }

    // ── API 3: POI Gallery ───────────────────────────────────────────────────

    @Operation(summary = "Lấy thư viện ảnh (Media Gallery) của POI", description = "Trả về danh sách hình ảnh theo thứ tự display_order tăng dần")
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Truy vấn thành công"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Không tìm thấy POI", content = @Content(schema = @Schema(implementation = ApiResponse.class)))
    })
    @GetMapping("/{poi_id}/gallery")
    public ResponseEntity<ApiResponse<List<PoiGalleryItemResponse>>> getGallery(
            @Parameter(description = "Mã định danh của POI", example = "poi_01jk9a7b")
            @PathVariable("poi_id") String poiId
    ) {
        List<PoiGalleryItemResponse> gallery = poiService.getGallery(poiId);
        return ResponseEntity.ok(ApiResponse.success(gallery, "POI gallery retrieved successfully"));
    }

    // ── API 9: POI Reviews ───────────────────────────────────────────────────

    @Operation(summary = "Truy vấn danh sách đánh giá của POI", description = "Hỗ trợ phân trang và lọc theo ngôn ngữ bài viết")
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Truy vấn thành công"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Tham số truy vấn không hợp lệ", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "422", description = "Dữ liệu đầu vào vi phạm validation", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Không tìm thấy POI", content = @Content(schema = @Schema(implementation = ApiResponse.class)))
    })
    @GetMapping("/{poi_id}/reviews")
    public ResponseEntity<ApiResponse<List<PoiReviewItemResponse>>> getReviews(
            @Parameter(description = "Mã định danh của POI", example = "poi_01jk9a7b")
            @PathVariable("poi_id") String poiId,

            @Parameter(description = "Số thứ tự trang (bắt đầu từ 0)")
            @RequestParam(name = "page", defaultValue = "0") @Min(0) int page,

            @Parameter(description = "Số lượng phần tử trên mỗi trang (tối đa 100)")
            @RequestParam(name = "size", defaultValue = "10") @Min(1) @Max(100) int size
    ) {
        PageResponse<PoiReviewItemResponse> response = poiService.getReviews(poiId, page, size);
        PaginationMeta pagination = PaginationMeta.offset(response.page(), response.size(), response.totalElements());
        return ResponseEntity.ok(ApiResponse.successList(response.content(), pagination, "POI reviews retrieved successfully"));
    }

    // ── API 10: POI Amenities ────────────────────────────────────────────────

    @Operation(summary = "Truy vấn danh sách tiện ích của POI theo nhóm", description = "Trả về danh sách nhóm tiện ích (amenity_group) kèm các tiện nghi chi tiết")
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Truy vấn thành công. Data rỗng khi không có dòng amenity còn hiệu lực.")
    })
    @GetMapping("/{poi_id}/amenities")
    public ResponseEntity<ApiResponse<List<PoiAmenityGroupResponse>>> getAmenities(
            @Parameter(description = "Mã định danh của POI", example = "poi_01jk9a7b")
            @PathVariable("poi_id") String poiId
    ) {
        List<PoiAmenityGroupResponse> amenities = poiService.getAmenities(poiId);
        return ResponseEntity.ok(ApiResponse.success(amenities, "POI amenities retrieved successfully"));
    }
}
