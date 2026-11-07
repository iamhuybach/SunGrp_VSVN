package vn.visitvietnam.dataserving.common.dto;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class ApiResponseTest {

    @Test
    @DisplayName("Tạo ApiResponse.success cho đối tượng đơn lẻ")
    void shouldCreateSuccessResponse() {
        ApiResponse<String> response = ApiResponse.success("sample_data", "Thành công");

        assertThat(response.success()).isTrue();
        assertThat(response.code()).isEqualTo(200);
        assertThat(response.message()).isEqualTo("Thành công");
        assertThat(response.data()).isEqualTo("sample_data");
        assertThat(response.errors()).isNull();
        assertThat(response.meta()).isNotNull();
        assertThat(response.meta().timestamp()).endsWith("Z");
        assertThat(response.meta().traceId()).isNotBlank();
        assertThat(response.meta().pagination()).isNull();
    }

    @Test
    @DisplayName("Tạo ApiResponse.successList cho danh sách kèm phân trang")
    void shouldCreateSuccessListResponse() {
        List<String> list = List.of("item1", "item2");
        PaginationMeta pagination = PaginationMeta.offset(0, 10, 2);

        ApiResponse<List<String>> response = ApiResponse.successList(list, pagination, "Lấy danh sách thành công");

        assertThat(response.success()).isTrue();
        assertThat(response.code()).isEqualTo(200);
        assertThat(response.data()).containsExactly("item1", "item2");
        assertThat(response.meta().pagination()).isNotNull();
        assertThat(response.meta().pagination().type()).isEqualTo("offset");
        assertThat(response.meta().pagination().totalItems()).isEqualTo(2);
        assertThat(response.meta().pagination().totalPages()).isEqualTo(1);
        assertThat(response.meta().pagination().hasNext()).isFalse();
        assertThat(response.meta().pagination().hasPrev()).isFalse();
    }

    @Test
    @DisplayName("Tạo ApiResponse.successList khi data là null thì trả về mảng rỗng []")
    void shouldReturnEmptyListWhenDataIsNull() {
        PaginationMeta pagination = PaginationMeta.offset(0, 10, 0);

        ApiResponse<List<String>> response = ApiResponse.successList(null, pagination, "Rỗng");

        assertThat(response.data()).isNotNull().isEmpty();
    }

    @Test
    @DisplayName("Tạo ApiResponse.error với thông tin lỗi chuẩn")
    void shouldCreateErrorResponse() {
        ApiErrorDetail detail = new ApiErrorDetail("field1", "REQUIRED", "Trường bắt buộc");
        ApiResponse<Void> response = ApiResponse.error(HttpStatus.UNPROCESSABLE_ENTITY, "Validation failed", "ERR_VALIDATION_FAILED", List.of(detail));

        assertThat(response.success()).isFalse();
        assertThat(response.code()).isEqualTo(422);
        assertThat(response.message()).isEqualTo("Validation failed");
        assertThat(response.data()).isNull();
        assertThat(response.meta().errorCode()).isEqualTo("ERR_VALIDATION_FAILED");
        assertThat(response.errors()).hasSize(1);
        assertThat(response.errors().getFirst().field()).isEqualTo("field1");
    }
}

