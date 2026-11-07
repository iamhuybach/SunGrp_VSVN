package vn.visitvietnam.dataserving.service.util;

import java.util.Map;

/**
 * Từ điển ánh xạ mã ngành kinh doanh sang tên tiếng Việt chuẩn hóa.
 */
public final class BusinessSectorDictionary {

    private static final Map<String, String> SECTOR_MAP = Map.ofEntries(
            // Legacy / Uppercase
            Map.entry("ATTRACTION", "Điểm tham quan"),
            Map.entry("ACCOMMODATION", "Khách sạn & Lưu trú"),
            Map.entry("RESTAURANT", "Ẩm thực & Nhà hàng"),
            Map.entry("SHOPPING", "Mua sắm"),
            Map.entry("ENTERTAINMENT", "Giải trí & Vui chơi"),
            Map.entry("TRANSPORT", "Phương tiện & Vận chuyển"),
            Map.entry("TOUR", "Tour & Hoạt động"),
            Map.entry("EVENT", "Event & Show diễn"),
            Map.entry("HEALTH_CARE", "Chăm sóc sức khỏe & Spa"),
            Map.entry("SERVICE", "Dịch vụ du lịch"),
            // Database actual keys
            Map.entry("F_N_B", "Ẩm thực"),
            Map.entry("TOUR_N_ACTIVITIES", "Tour & Hoạt động"),
            Map.entry("SHOPPING_N_RETAIL", "Mua sắm"),
            Map.entry("SPA_N_WELLNESS", "Spa & Wellness"),
            Map.entry("TRANSPORT_ON_DEMAND", "Đưa đón"),
            Map.entry("TRANSPORT_ROUTE_BASE", "Vận tải"),
            Map.entry("VEHICLE_RENTAL", "Thuê phương tiện"),
            Map.entry("OTHER", "Khác")
    );

    private BusinessSectorDictionary() {
        // static utility class
    }

    public static String getLabel(String sectorCode) {
        if (sectorCode == null || sectorCode.isBlank()) {
            return "Khác";
        }
        String normalized = sectorCode.trim().toUpperCase();
        return SECTOR_MAP.getOrDefault(normalized, sectorCode);
    }
}
