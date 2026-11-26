package vn.visitvietnam.dataserving.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;

import java.util.List;

public record PracticalInfoSearchRequest(
        @NotEmpty @Size(max = 500) List<@NotBlank @Size(max = 128) String> ids
) {}
