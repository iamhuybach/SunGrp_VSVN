package vn.visitvietnam.dataserving.service.util;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.assertj.core.api.Assertions.assertThat;

class BusinessSectorDictionaryTest {

    @ParameterizedTest(name = "Mã sector {0} phải ánh xạ thành {1}")
    @CsvSource({
            "ATTRACTION, Điểm tham quan",
            "ACCOMMODATION, Khách sạn & Lưu trú",
            "RESTAURANT, Ẩm thực & Nhà hàng",
            "SHOPPING, Mua sắm",
            "ENTERTAINMENT, Giải trí & Vui chơi",
            "TRANSPORT, Phương tiện & Vận chuyển",
            "f_n_b, Ẩm thực",
            "tour_n_activities, Tour & Hoạt động"
    })
    void shouldMapKnownSectors(String code, String expectedLabel) {
        assertThat(BusinessSectorDictionary.getLabel(code)).isEqualTo(expectedLabel);
    }

    @Test
    @DisplayName("Trả về mã gốc nếu là sector chưa định nghĩa trong từ điển")
    void shouldReturnOriginalCodeWhenUnknown() {
        assertThat(BusinessSectorDictionary.getLabel("CUSTOM_SECTOR")).isEqualTo("CUSTOM_SECTOR");
    }

    @Test
    @DisplayName("Trả về 'Khác' nếu mã null hoặc rỗng")
    void shouldReturnDefaultWhenNullOrBlank() {
        assertThat(BusinessSectorDictionary.getLabel(null)).isEqualTo("Khác");
        assertThat(BusinessSectorDictionary.getLabel("")).isEqualTo("Khác");
        assertThat(BusinessSectorDictionary.getLabel("   ")).isEqualTo("Khác");
    }
}

