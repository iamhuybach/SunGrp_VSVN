package vn.visitvietnam.dataserving.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import vn.visitvietnam.dataserving.common.dto.ApiErrorDetail;
import vn.visitvietnam.dataserving.common.dto.ApiMeta;

import java.util.List;

@Schema(name = "PracticalInfoListResponse", description = "Envelope danh sách practical info. Phần tử data là PoiPracticalInfoResponse hoặc tập con khóa khi có required_fields.")
public record PracticalInfoListEnvelope(
        boolean success,
        int code,
        String message,
        List<PoiPracticalInfoResponse> data,
        ApiMeta meta,
        List<ApiErrorDetail> errors
) {}
