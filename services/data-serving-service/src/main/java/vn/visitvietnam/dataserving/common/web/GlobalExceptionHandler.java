package vn.visitvietnam.dataserving.common.web;

import jakarta.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import vn.visitvietnam.dataserving.common.dto.ApiErrorDetail;
import vn.visitvietnam.dataserving.common.dto.ApiResponse;
import vn.visitvietnam.dataserving.common.exception.ResourceNotFoundException;

import java.util.List;

@Order(1)
@RestControllerAdvice(basePackages = "vn.visitvietnam.dataserving")
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handleNotFound(ResourceNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error(HttpStatus.NOT_FOUND, e.getMessage(), "POI_NOT_FOUND", null));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation(MethodArgumentNotValidException e) {
        List<ApiErrorDetail> errors = e.getBindingResult().getFieldErrors().stream()
                .map(f -> new ApiErrorDetail(
                        f.getField(),
                        f.getCode() != null ? f.getCode().toUpperCase() : "INVALID",
                        f.getDefaultMessage() != null ? f.getDefaultMessage() : "Invalid value"
                ))
                .toList();
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                .body(ApiResponse.error(HttpStatus.UNPROCESSABLE_ENTITY, "Validation failed", "ERR_VALIDATION_FAILED", errors));
    }

    @ExceptionHandler(BindException.class)
    public ResponseEntity<ApiResponse<Void>> handleBindException(BindException e) {
        List<ApiErrorDetail> errors = e.getBindingResult().getFieldErrors().stream()
                .map(f -> new ApiErrorDetail(
                        f.getField(),
                        f.getCode() != null ? f.getCode().toUpperCase() : "INVALID",
                        f.getDefaultMessage() != null ? f.getDefaultMessage() : "Invalid value"
                ))
                .toList();
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                .body(ApiResponse.error(HttpStatus.UNPROCESSABLE_ENTITY, "Validation failed", "ERR_VALIDATION_FAILED", errors));
    }

    @ExceptionHandler(HandlerMethodValidationException.class)
    public ResponseEntity<ApiResponse<Void>> handleMethodValidation(HandlerMethodValidationException e) {
        List<ApiErrorDetail> errors = e.getValueResults().stream()
                .flatMap(r -> r.getResolvableErrors().stream().map(err -> {
                    String field = r.getMethodParameter().getParameterName();
                    String code = "INVALID";
                    if (err.getCodes() != null && err.getCodes().length > 0) {
                        code = err.getCodes()[err.getCodes().length - 1].toUpperCase();
                    }
                    String message = err.getDefaultMessage() != null ? err.getDefaultMessage() : "Invalid value";
                    return new ApiErrorDetail(field != null ? field : "parameter", code, message);
                }))
                .toList();
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                .body(ApiResponse.error(HttpStatus.UNPROCESSABLE_ENTITY, "Validation failed", "ERR_VALIDATION_FAILED", errors));
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ApiResponse<Void>> handleConstraintViolation(ConstraintViolationException e) {
        List<ApiErrorDetail> errors = e.getConstraintViolations().stream()
                .map(cv -> {
                    String path = cv.getPropertyPath() != null ? cv.getPropertyPath().toString() : "field";
                    int lastDot = path.lastIndexOf('.');
                    String field = lastDot >= 0 ? path.substring(lastDot + 1) : path;
                    String code = cv.getConstraintDescriptor() != null && cv.getConstraintDescriptor().getAnnotation() != null
                            ? cv.getConstraintDescriptor().getAnnotation().annotationType().getSimpleName().toUpperCase()
                            : "INVALID";
                    return new ApiErrorDetail(field, code, cv.getMessage());
                })
                .toList();
        return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY)
                .body(ApiResponse.error(HttpStatus.UNPROCESSABLE_ENTITY, "Validation failed", "ERR_VALIDATION_FAILED", errors));
    }

    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ApiResponse<Void>> handleTypeMismatch(MethodArgumentTypeMismatchException e) {
        String required = e.getRequiredType() == null ? "the expected type" : e.getRequiredType().getSimpleName();
        String message = String.format("'%s' is not a valid %s for parameter '%s'.", e.getValue(), required, e.getName());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(HttpStatus.BAD_REQUEST, message, "ERR_BAD_REQUEST", null));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiResponse<Void>> handleBadRequest(IllegalArgumentException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(HttpStatus.BAD_REQUEST, e.getMessage(), "ERR_BAD_REQUEST", null));
    }

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<ApiResponse<Void>> handleConflict(IllegalStateException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(ApiResponse.error(HttpStatus.CONFLICT, e.getMessage(), "STATE_CONFLICT", null));
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiResponse<Void>> handleNotReadable(HttpMessageNotReadableException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.error(HttpStatus.BAD_REQUEST, "Malformed or missing request body.", "ERR_BAD_REQUEST", null));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleUnexpected(Exception e) {
        log.error("Unhandled exception in data-serving-service", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error(
                        HttpStatus.INTERNAL_SERVER_ERROR,
                        "An unexpected error occurred. Please contact support with the trace ID.",
                        "INTERNAL_SERVER_ERROR",
                        null
                ));
    }
}
