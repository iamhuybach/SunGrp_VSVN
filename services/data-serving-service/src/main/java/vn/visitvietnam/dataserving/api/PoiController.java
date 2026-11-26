package vn.visitvietnam.dataserving.api;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import vn.visitvietnam.dataserving.api.dto.CompactPoiRequest;
import vn.visitvietnam.dataserving.api.dto.CompactPoiResponse;
import vn.visitvietnam.dataserving.api.dto.PoiAmenityGroupResponse;
import vn.visitvietnam.dataserving.api.dto.PoiExperiencesResponse;
import vn.visitvietnam.dataserving.api.dto.PoiFeatureResponse;
import vn.visitvietnam.dataserving.api.dto.PoiGalleryItemResponse;
import vn.visitvietnam.dataserving.api.dto.PracticalInfoListEnvelope;
import vn.visitvietnam.dataserving.api.dto.PracticalInfoSearchRequest;
import vn.visitvietnam.dataserving.api.dto.PoiPracticalInfoResponse;
import vn.visitvietnam.dataserving.api.dto.PoiReviewItemResponse;
import vn.visitvietnam.dataserving.common.dto.ApiResponse;
import vn.visitvietnam.dataserving.common.dto.PageResponse;
import vn.visitvietnam.dataserving.common.dto.PaginationMeta;
import vn.visitvietnam.dataserving.service.PoiService;
import vn.visitvietnam.dataserving.service.PracticalInfoQuery;
import vn.visitvietnam.dataserving.service.util.LanguageResolver;

import java.math.BigDecimal;
import java.util.EnumSet;
import java.util.List;

@Tag(name = "POI API", description = "API đọc dữ liệu địa điểm du lịch (POIs)")
@Validated
@RestController
@RequestMapping("/api/v1/pois")
@RequiredArgsConstructor
public class PoiController {

    private final PoiService poiService;
    private final LanguageResolver languageResolver;

    @Operation(summary = "Truy vấn danh sách POI rút gọn")
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Truy vấn thành công"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Body JSON hỏng hoặc thiếu", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "422", description = "ids không hợp lệ", content = @Content(schema = @Schema(implementation = ApiResponse.class)))
    })
    @PostMapping(value = "/compact", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ApiResponse<List<CompactPoiResponse>>> getCompactPois(
            @Valid @RequestBody CompactPoiRequest request,
            @RequestHeader(name = "Accept-Language", required = false) String acceptLanguage
    ) {
        String resolvedLang = languageResolver.resolveLanguage(request.lang(), acceptLanguage);
        List<CompactPoiResponse> items = poiService.getCompactPois(request.ids(), resolvedLang);
        return ResponseEntity.ok(ApiResponse.success(items, "Compact POIs retrieved successfully"));
    }

    @Operation(summary = "Danh sách POI nổi bật")
    @GetMapping("/features")
    public ResponseEntity<ApiResponse<List<PoiFeatureResponse>>> getFeatures(
            @RequestParam(name = "lang", required = false) String lang,
            @RequestHeader(name = "Accept-Language", required = false) String acceptLanguage,
            @RequestParam(name = "page", defaultValue = "0") @Min(0) int page,
            @RequestParam(name = "size", defaultValue = "10") @Min(1) @Max(100) int size,
            @RequestParam(name = "business_sector_priority", required = false) @Size(max = 20) List<String> businessSectorPriority,
            @RequestParam(name = "fallback_min_rating", defaultValue = "4.5") @DecimalMin("0") @DecimalMax("5") BigDecimal fallbackMinRating,
            @RequestParam(name = "fallback_min_review_count", defaultValue = "100") @Min(0) int fallbackMinReviewCount,
            @RequestParam(name = "rating_source", required = false) @Size(max = 64) String ratingSource
    ) {
        String resolvedLang = languageResolver.resolveLanguage(lang, acceptLanguage);
        PoiService.FeaturePage pageResult = poiService.getFeatures(
                businessSectorPriority, fallbackMinRating, fallbackMinReviewCount, ratingSource, resolvedLang, page, size);
        PaginationMeta pagination = PaginationMeta.offset(page, size, pageResult.total());
        return ResponseEntity.ok(ApiResponse.successList(pageResult.items(), pagination, "Featured POIs retrieved successfully"));
    }

    @Operation(summary = "Lấy thư viện ảnh của POI")
    @GetMapping("/{poi_id}/gallery")
    public ResponseEntity<ApiResponse<List<PoiGalleryItemResponse>>> getGallery(
            @PathVariable("poi_id") String poiId,
            @RequestParam(name = "page", defaultValue = "0") @Min(0) int page,
            @RequestParam(name = "size", defaultValue = "20") @Min(1) @Max(100) int size
    ) {
        PageResponse<PoiGalleryItemResponse> response = poiService.getGallery(poiId, page, size);
        PaginationMeta pagination = PaginationMeta.offset(response.page(), response.size(), response.totalElements());
        return ResponseEntity.ok(ApiResponse.successList(response.content(), pagination, "POI gallery retrieved successfully"));
    }

    @Operation(summary = "Truy vấn đánh giá của POI")
    @GetMapping("/{poi_id}/reviews")
    public ResponseEntity<PoiReviewItemResponse.ReviewsResponse> getReviews(
            @PathVariable("poi_id") String poiId,
            @RequestParam(name = "page", defaultValue = "0") @Min(0) int page,
            @RequestParam(name = "size", defaultValue = "10") @Min(1) @Max(100) int size
    ) {
        PoiService.ReviewsPage response = poiService.getReviews(poiId, page, size);
        PaginationMeta pagination = PaginationMeta.offset(response.page().page(), response.page().size(), response.page().totalElements());
        ApiResponse<List<PoiReviewItemResponse>> base = ApiResponse.successList(
                response.page().content(), pagination, "POI reviews retrieved successfully");
        return ResponseEntity.ok(PoiReviewItemResponse.ReviewsResponse.of(base, response.ratingSummary()));
    }

    @Operation(summary = "Trải nghiệm của POI")
    @GetMapping("/{poi_id}/experiences")
    public ResponseEntity<ApiResponse<PoiExperiencesResponse>> getExperiences(
            @PathVariable("poi_id") String poiId,
            @RequestParam(name = "lang", required = false) String lang,
            @RequestHeader(name = "Accept-Language", required = false) String acceptLanguage
    ) {
        String resolvedLang = languageResolver.resolveLanguage(lang, acceptLanguage);
        return ResponseEntity.ok(ApiResponse.success(poiService.getExperiences(poiId, resolvedLang), "POI experiences retrieved successfully"));
    }

    @Operation(summary = "Thông tin thực tế của POI")
    @GetMapping("/{poi_id}/practical_info")
    public ResponseEntity<ApiResponse<PoiPracticalInfoResponse>> getPracticalInfo(
            @PathVariable("poi_id") String poiId,
            @RequestParam(name = "lang", required = false) String lang,
            @RequestHeader(name = "Accept-Language", required = false) String acceptLanguage
    ) {
        String resolvedLang = languageResolver.resolveLanguage(lang, acceptLanguage);
        return ResponseEntity.ok(ApiResponse.success(poiService.getPracticalInfo(poiId, resolvedLang), "POI practical info retrieved successfully"));
    }

    @Operation(summary = "Danh sách thông tin thực tế của nhiều POI")
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Danh sách practical info. required_fields vắng thì mỗi phần tử đủ field; có chọn thì chỉ các khóa đó, giữ null.", content = @Content(schema = @Schema(implementation = PracticalInfoListEnvelope.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Body không đọc được (kể cả poi_name không phải chuỗi JSON), quá lớn, hoặc page/size không phải số.", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "401", description = "Thiếu hoặc sai bearer token.", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "415", description = "Content-Type khác application/json.", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "422", description = "ids, required_fields, source, poi_name, page, size, sort_field hoặc sort_order ngoài hợp đồng, hoặc thiếu cả ids và poi_name.", content = @Content(schema = @Schema(implementation = ApiResponse.class))),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Lỗi không phân loại.", content = @Content(schema = @Schema(implementation = ApiResponse.class)))
    })
    @PostMapping(value = "/practical_info", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ApiResponse<List<Object>>> searchPracticalInfo(
            @Valid @RequestBody PracticalInfoSearchRequest body,
            @RequestParam(name = "required_fields", required = false) @Size(max = 18) List<@Pattern(regexp = PracticalInfoQuery.FIELD_REGEX) String> requiredFields,
            @RequestParam(name = "source", required = false) @Pattern(regexp = "^(partner|google)?$") String source,
            @RequestParam(name = "lang", required = false) String lang,
            @RequestHeader(name = "Accept-Language", required = false) String acceptLanguage,
            @RequestParam(name = "page", defaultValue = "0") @Min(0) int page,
            @RequestParam(name = "size", defaultValue = "10") @Min(1) @Max(100) int size,
            @RequestParam(name = "sort_field", required = false) @Pattern(regexp = PracticalInfoQuery.SORT_REGEX) String sortField,
            @RequestParam(name = "sort_order", defaultValue = "asc") @Pattern(regexp = "^(asc|desc)$") String sortOrder
    ) {
        String resolvedLang = languageResolver.resolveLanguage(lang, acceptLanguage);
        EnumSet<PracticalInfoQuery.Field> fields = EnumSet.noneOf(PracticalInfoQuery.Field.class);
        if (requiredFields != null) {
            for (String key : requiredFields) {
                fields.add(PracticalInfoQuery.Field.byKey(key));
            }
        }
        PracticalInfoQuery.SortField sort = sortField == null || sortField.isBlank()
                ? null
                : PracticalInfoQuery.SortField.byKey(sortField);
        org.springframework.data.domain.Sort.Direction direction = "desc".equals(sortOrder)
                ? org.springframework.data.domain.Sort.Direction.DESC
                : org.springframework.data.domain.Sort.Direction.ASC;
        PracticalInfoQuery query = new PracticalInfoQuery(
                body.ids() == null ? List.of() : body.ids(),
                fields,
                source == null || source.isBlank() ? null : source,
                body.poiName() == null || body.poiName().isBlank() ? null : body.poiName(),
                resolvedLang,
                page,
                size,
                sort,
                direction);
        PoiService.PracticalInfoPage result = poiService.searchPracticalInfo(query);
        return ResponseEntity.ok(ApiResponse.successList(
                result.items(),
                PaginationMeta.offset(page, size, result.total()),
                "POI practical info list retrieved successfully"));
    }

    @Operation(summary = "Truy vấn danh sách tiện ích của POI theo nhóm")
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
