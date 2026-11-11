package vn.visitvietnam.dataserving.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;

import java.util.List;

/**
 * Body của POST /api/v1/pois/compact. ids từ 1 đến 20 phần tử (D-4).
 */
public record CompactPoiRequest(
        String lang,
        @NotEmpty @Size(max = 20) List<@NotBlank @Size(max = 128) String> ids
) {}
