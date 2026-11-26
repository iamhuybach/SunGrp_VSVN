package vn.visitvietnam.dataserving.api.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.validation.constraints.AssertTrue;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonParser;
import tools.jackson.core.JsonToken;
import tools.jackson.databind.DeserializationContext;
import tools.jackson.databind.ValueDeserializer;
import tools.jackson.databind.annotation.JsonDeserialize;

import java.util.List;

/**
 * Body POST practical_info. ids hoặc poi_name là selector; có cả hai thì hợp.
 */
public record PracticalInfoSearchRequest(
        @Size(max = 500) List<@NotBlank @Size(max = 128) String> ids,
        @JsonProperty("poi_name")
        @JsonDeserialize(using = PracticalInfoNameDeserializer.class)
        @Size(max = 128) String poiName
) {
    /** ids không rỗng hoặc poi_name có chữ. Thiếu cả hai trả 422. */
    @JsonIgnore
    @AssertTrue(message = "ids hoặc poi_name phải có giá trị")
    public boolean isSelectorPresent() {
        return (ids != null && !ids.isEmpty()) || (poiName != null && !poiName.isBlank());
    }
}

/**
 * Chỉ nhận chuỗi JSON cho poi_name. Số, boolean, mảng và object không bị ép thành chuỗi.
 */
final class PracticalInfoNameDeserializer extends ValueDeserializer<String> {

    @Override
    public String deserialize(JsonParser parser, DeserializationContext context) throws JacksonException {
        if (parser.currentToken() != JsonToken.VALUE_STRING) {
            throw context.wrongTokenException(
                    parser, String.class, JsonToken.VALUE_STRING, "poi_name phải là chuỗi JSON");
        }
        return parser.getText();
    }
}
