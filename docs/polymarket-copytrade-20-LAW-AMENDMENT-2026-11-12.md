# VĂN BẢN SỬA LUẬT (LAW AMENDMENT) — 2026-11-12

## Quyết định của chủ nhân

Chủ nhân duyệt ngày **2026-11-12** bằng văn bản trong chat: **"okay vậy đi"** — chấp nhận toàn bộ phương án tôi (agent Việc 3) trình cùng ngày (bảng phân bổ khối lượng + khuyến nghị), gồm 2 thay đổi luật và 1 bước đo:

1. **Ngưỡng sàng lọc thị trường cho hồ sơ (Việc 4) nâng từ 10.000 USD lên 100.000 USD** — tổng giao dịch trong đoạn 1 (13/09→12/12/2025), giữ nguyên cách đo: **đo từ dữ liệu trade trong đoạn 1, KHÔNG dùng volumeNum cuối**; vẫn phải báo tổng/số giữ/số bỏ; vẫn cấm sàng lọc theo lãi/PnL/kết quả backtest.
2. **Hạn bước hồ sơ (Việc 4) kéo dài từ 14 ngày lên tối đa 45 ngày dương lịch** (trần vẫn 200 request/ngày giờ VN). Sửa này áp dụng cho hạn thời gian; mọi luật khác (nhịp, watchdog, khóa, kiểm toán, GO riêng từng bước) không đổi.
3. **Chạy pilot 100 thị trường đầu tiên theo thứ tự id TRONG tập ≥100.000 USD** (lưu ý minh bạch: việc CHỌN 100 thị trường pilot dùng volumeNum CHỈ để lấy mẫu đo chi phí — bản thân pipeline hồ sơ khi chạy thật vẫn đo ngưỡng từ trade như mục 1) — để đo số request thật/trận rồi chốt kế hoạch Việc 4. Pilot KHÔNG phải Việc 4, không phải hồ sơ chính, không backtest, chưa chọn ví.

## Căn cứ

- Spec v2 đóng băng §4.3 (commit `8727bcc`, hash `ae504a97…bee55d8`) dự liệu trước đúng trường hợp này: *"vượt 14 ngày thì báo vượt bao nhiêu + đề xuất giữ/thu hẹp theo luật KHÔNG dựa trên lãi — chủ nhân quyết"*.
- Số liệu đã kiểm toán (CONFIRMED `9b56d8a`): 19.230 thị trường hợp lệ; ở ngưỡng 100.000 USD giữ lại 2.321 trận = **92% tổng tiền**, ước cận dưới ~12 ngày lấy trade @200/ngày.
- File spec đóng băng **KHÔNG bị sửa** (hash bất biến); văn bản này là luật hoạt động mới của chủ nhân, ghi kèm như tiền lệ FREEZE_LOG_V2 ghi quyết định ngưỡng 10.000 USD ngày 2026-11-03.

## Hiệu lực

- Có hiệu lực từ duyệt; áp dụng cho pilot (hôm nay 12/11, trần 200 request) và cho Việc 4 khi có **lệnh GO riêng** của chủ nhân sau khi đọc báo cáo pilot.
- Số đếm Việc 3 (19.230 hợp lệ) KHÔNG đổi — ngưỡng mới áp ở bước sàng lọc hồ sơ.
- Mọi ranh giới cứng giữ nguyên: trên giấy, 0 đồng, không lệnh thật, không sửa spec đóng băng, không đụng PaperDesk/Polymarket thật, kiểm toán độc lập sau mỗi việc.
