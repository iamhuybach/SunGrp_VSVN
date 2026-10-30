# Kafka UI cho Event Hubs DEV

Xem topic của namespace `dev-visitvn-evhns-sg-01` bằng Kafka UI trên Docker. Compose nằm ở `local/eventhubs-kafka-ui/`. Skill đi kèm là `vsvn-eventhubs-kafka-ui`.

Yêu cầu «Mở Kafka UI cho dự án VSVN môi trường Dev» đi theo mục Bật nhanh. Không tạo task, không chạy `python scripts/vv.py`, không đọc notebook, pipeline, hay DDL.

## Bật nhanh

`.env` đã có connection string thì một lệnh:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File local/eventhubs-kafka-ui/up.ps1
```

UI: http://127.0.0.1:8080. Cluster: `dev-visitvn-evhns-sg-01`, rồi **Topics**.

Tắt, và giữ `.env` cho lần sau:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File local/eventhubs-kafka-ui/down.ps1
```

`up.ps1` dừng khi Docker chưa chạy, hoặc khi `EVENTHUB_CONNECTION_STRING` trong `.env` còn trống. Lần đó chỉ điền `.env`, rồi chạy lại `up.ps1`. Không ghi key vào `.env.example`.

## File

| File | Vai trò |
|---|---|
| `local/eventhubs-kafka-ui/compose.yaml` | Được commit. Không có connection string. |
| `local/eventhubs-kafka-ui/.env.example` | Mẫu. `SharedAccessKey` chỉ là `REPLACE_ME`. |
| `local/eventhubs-kafka-ui/.env` | Git bỏ qua. Chỉ file này chứa connection string. |
| `local/eventhubs-kafka-ui/.gitignore` | Bỏ qua `.env`. |

Không thêm Dockerfile. Image là `ghcr.io/kafbat/kafka-ui:latest`.

## Kết nối

- Bootstrap: `dev-visitvn-evhns-sg-01.servicebus.windows.net:9093`
- `security.protocol=SASL_SSL`, `sasl.mechanism=PLAIN`
- Username Kafka là `$ConnectionString`. Trong `compose.yaml` phải viết `$$ConnectionString` để Compose giữ lại dấu `$`.
- Password là nguyên connection string cấp namespace, gồm `SharedAccessKey`. Không có `EntityPath`.
- UI: http://127.0.0.1:8080, cổng gắn `127.0.0.1`. Cluster `dev-visitvn-evhns-sg-01` ở chế độ read-only.
- `metadata.max.age.ms` và `connections.max.idle.ms` là `180000`.

Kafka protocol có trên tier Standard, Premium hoặc Dedicated. Tier Basic không có cổng 9093 dùng được. Policy **Listen** trên namespace đủ để xem topic. **Send** không đủ. **Manage** chỉ cần khi tạo hoặc xóa event hub. `RootManageSharedAccessKey` chỉ dùng khi chưa có policy Listen riêng.

## Secret

- Đọc connection string từ `.env` hoặc biến `EVENTHUB_CONNECTION_STRING`.
- Không ghi key vào `.env.example`, `compose.yaml`, image, chat, hoặc log.
- Không chạy `docker compose config` hoặc `docker inspect` khi output sẽ được chia sẻ. Hai lệnh đó in password.
- Nếu log có `password="Endpoint=` hoặc `SharedAccessKey=`, xóa đoạn đó trước khi gửi.

`.env` để trống thì Compose dừng với `required variable EVENTHUB_CONNECTION_STRING is missing a value` và không tạo container.

## Lần đầu

Chỉ làm mục này khi chưa có `.env` hoặc Kafka chưa bật. Lần sau dùng mục Bật nhanh.

1. `docker info`. Docker không chạy thì dừng.
2. Kiểm tra tier và Kafka trên namespace. Khi có Azure CLI:

```powershell
az eventhubs namespace show --name dev-visitvn-evhns-sg-01 --resource-group <resource-group> --query "{sku:sku.name, kafkaEnabled:kafkaEnabled}" -o json
```

`kafkaEnabled=false` trên tier Standard trở lên thì `az eventhubs namespace update ... --enable-kafka true`. Tier Basic thì dừng.

3. Tạo policy `kafka-ui-listen` với quyền Listen. Copy primary connection string vào `.env`, một dòng, không dấu nháy:

```text
EVENTHUB_CONNECTION_STRING=Endpoint=sb://dev-visitvn-evhns-sg-01.servicebus.windows.net/;SharedAccessKeyName=kafka-ui-listen;SharedAccessKey=<key>
```

4. Bật và tắt bằng `up.ps1` và `down.ps1` ở mục Bật nhanh. `down.ps1` không xóa `.env`. Log khi cần:

```powershell
cd local/eventhubs-kafka-ui
docker compose logs -f kafka-ui
```

Trên UI: cluster `dev-visitvn-evhns-sg-01`, rồi **Topics**.

## Khi lỗi

| Hiện tượng | Việc làm |
|---|---|
| `SaslAuthenticationException` hoặc `connection string is not of the expected format` | Username phải là `$ConnectionString` (`$$` trong compose). Password phải bắt đầu bằng `Endpoint=sb://...`, gồm `SharedAccessKeyName` và `SharedAccessKey`, không có `EntityPath`, không bọc thêm nháy. Chuỗi chỉ bắt đầu bằng `sb://` thì `up.ps1` thêm `Endpoint=`. Sửa `.env` rồi `docker compose up -d --force-recreate`. |
| Kafka protocol không bật, hoặc broker đóng sau handshake | Xem tier và `kafkaEnabled`. Basic thì dừng. |
| `TimeoutException` trên 9093 | `Test-NetConnection dev-visitvn-evhns-sg-01.servicebus.windows.net -Port 9093`. `TcpTestSucceeded=False` là firewall hoặc DNS. Cổng Kafka là 9093. |
| UI trống, cluster offline | Mở đúng http://127.0.0.1:8080. Xem log đã xóa secret. Cluster online mà không có topic nghĩa là namespace chưa có event hub. |
| `'Listen' claim(s) are required` | Policy thiếu Listen. Đổi `.env` sang policy Listen rồi `--force-recreate`. |

## Đã thấy trên DEV

Ngày 2026-10-30, từ máy này: DNS phân giải được, `Test-NetConnection` cổng 9093 trả về `TcpTestSucceeded=True`. UI lên cluster **ONLINE**, 1 broker, 10 topic, 18 partition: `cms-data-events`, `email-delivery-request`, `otp-delivery-request`, `vv-commerce-cdc`, `vv-gold-kb-events-live`, `vv-partner-cdc`, `vv-poi-changes`, `vv-posthog-event`, `vv-raw-events`, `vv-userprofile-cdc`. Đây là kết quả một lần xem, không phải hợp đồng schema. Sau lần xem đó container đã `docker compose down` và `.env` được tạo lại, chưa có connection string.
