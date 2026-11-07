package vn.visitvietnam.dataserving.common.web;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.core.MethodParameter;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import vn.visitvietnam.dataserving.common.dto.ApiResponse;
import vn.visitvietnam.dataserving.common.exception.ResourceNotFoundException;

import java.lang.reflect.Method;

import static org.assertj.core.api.Assertions.assertThat;

class GlobalExceptionHandlerTest {

    private final GlobalExceptionHandler handler = new GlobalExceptionHandler();

    @Test
    @DisplayName("handleNotFound trả về 404 với error_code POI_NOT_FOUND")
    void shouldHandleNotFound() {
        ResourceNotFoundException ex = new ResourceNotFoundException("Poi", "poi_999");

        ResponseEntity<ApiResponse<Void>> response = handler.handleNotFound(ex);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().success()).isFalse();
        assertThat(response.getBody().code()).isEqualTo(404);
        assertThat(response.getBody().message()).contains("poi_999");
        assertThat(response.getBody().data()).isNull();
        assertThat(response.getBody().meta().errorCode()).isEqualTo("POI_NOT_FOUND");
        assertThat(response.getBody().meta().traceId()).isNotBlank();
        assertThat(response.getBody().meta().timestamp()).endsWith("Z");
        assertThat(response.getBody().errors()).isNull();
    }

    @Test
    @DisplayName("handleValidation trả về 422 với error_code ERR_VALIDATION_FAILED và errors chi tiết")
    void shouldHandleValidation() throws Exception {
        Method method = this.getClass().getDeclaredMethod("dummyMethod", String.class);
        MethodParameter parameter = new MethodParameter(method, 0);
        BeanPropertyBindingResult bindingResult = new BeanPropertyBindingResult(new Object(), "testObject");
        bindingResult.addError(new FieldError("testObject", "email", "invalid_email", false, new String[]{"Email"}, null, "Email không hợp lệ"));

        MethodArgumentNotValidException ex = new MethodArgumentNotValidException(parameter, bindingResult);

        ResponseEntity<ApiResponse<Void>> response = handler.handleValidation(ex);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNPROCESSABLE_ENTITY);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().success()).isFalse();
        assertThat(response.getBody().code()).isEqualTo(422);
        assertThat(response.getBody().message()).isEqualTo("Validation failed");
        assertThat(response.getBody().meta().errorCode()).isEqualTo("ERR_VALIDATION_FAILED");
        assertThat(response.getBody().errors()).hasSize(1);
        assertThat(response.getBody().errors().getFirst().field()).isEqualTo("email");
        assertThat(response.getBody().errors().getFirst().message()).isEqualTo("Email không hợp lệ");
    }

    @Test
    @DisplayName("handleTypeMismatch trả về 400 với error_code ERR_BAD_REQUEST")
    void shouldHandleTypeMismatch() {
        MethodArgumentTypeMismatchException ex = new MethodArgumentTypeMismatchException(
                "abc", Integer.class, "size", null, null);

        ResponseEntity<ApiResponse<Void>> response = handler.handleTypeMismatch(ex);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().success()).isFalse();
        assertThat(response.getBody().code()).isEqualTo(400);
        assertThat(response.getBody().meta().errorCode()).isEqualTo("ERR_BAD_REQUEST");
    }

    @Test
    @DisplayName("handleBadRequest trả về 400 với error_code ERR_BAD_REQUEST")
    void shouldHandleBadRequest() {
        IllegalArgumentException ex = new IllegalArgumentException("Tham số không hợp lệ");

        ResponseEntity<ApiResponse<Void>> response = handler.handleBadRequest(ex);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().success()).isFalse();
        assertThat(response.getBody().code()).isEqualTo(400);
        assertThat(response.getBody().message()).isEqualTo("Tham số không hợp lệ");
        assertThat(response.getBody().meta().errorCode()).isEqualTo("ERR_BAD_REQUEST");
    }

    @Test
    @DisplayName("handleUnexpected trả về 500 với error_code INTERNAL_SERVER_ERROR")
    void shouldHandleUnexpected() {
        RuntimeException ex = new RuntimeException("Lỗi hệ thống bất ngờ");

        ResponseEntity<ApiResponse<Void>> response = handler.handleUnexpected(ex);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.INTERNAL_SERVER_ERROR);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().success()).isFalse();
        assertThat(response.getBody().code()).isEqualTo(500);
        assertThat(response.getBody().meta().errorCode()).isEqualTo("INTERNAL_SERVER_ERROR");
        assertThat(response.getBody().data()).isNull();
        assertThat(response.getBody().errors()).isNull();
    }

    @SuppressWarnings("unused")
    private void dummyMethod(String param) {}
}

