# BÁO CÁO INTERIM SỬA LIỆT KÊ VIỆC 3 — NGÀY 06/11 — CHƯA XONG, DỪNG THEO LUẬT WATCHDOG (1 RETRY ĐÃ DÙNG)

**Bản sửa liệt kê (tiếp theo kiểm toán BUG FOUND d8f2bb9 và interim 04/11, 05/11). KHÔNG phải hồ sơ chính, không phải backtest. Chưa chọn ví, chưa tính điểm, chưa tìm k*. LIỆT KÊ CHƯA XONG — mọi số dưới đây VẪN LÀ CẬN DƯỚI.**

## Preflight (ghi ở đầu log chạy, đúng lệnh)
- Hash spec: `ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8` — KHỚP.
- Kiểm tra dò-trước 2 điểm bắt buộc: **ĐẠT/ĐẠT** (dò = 1 request @offset 2000, đủ 100 dòng → chỉ phán CAP rồi chia tiếp, không lấy 21 trang; KHÔNG có nhánh nào dùng dò để kết luận xong; luật hoàn tất nguyên bản).
- Khóa sạch; sổ ngày 06/11 trước chạy = 0.

## Diễn biến & tuân thủ
- Chạy 00:05–00:50 giờ VN. **Watchdog "chậm bất thường" kích hoạt 2 LẦN**: 5.437 ms (nhịp 10s) → cooldown 17 phút → **đúng 1 lần retry 15 giây theo GO** → watchdog lần 2 (5.235 ms) → DỪNG HẲN. Không 429/403; 0 khoảng cách <9 giây; 1 tiến trình (khóa); checkpoint liên tục.
- **Request ngày 06/11: 111/200** (còn 89 chưa dùng — dừng vì hết lượt retry watchdog, không phải hết trần). Tích lũy từ đầu Việc 3: 358 + 200 + 200 + 111 = **869 request thật**.
- **Dò-trước hoạt động:** 14 lần dò @offset 2000; 4 lát bị phán CAP ngay (1 request thay vì 22) → **tiết kiệm ~84 request** so với cách cũ. Tháng 9 bắt đầu xong tự nhiên theo lát 1-2 ngày.

## Số đếm hiện tại — CẬN DƯỚI
| Bước | Số (cận dưới) |
|---|---|
| Thị trường duy nhất | 57.055 |
| Phi thể thao | 31.360 (+726 anomaly có smt) |
| Mùa vụ | 8.562 |
| Thiếu gameStartTime | 211 |
| gst ngoài đoạn 1 | 768 (159 trước + 609 sau T1) |
| Tag rỗng | 0 |
| **Hợp lệ (T0 ≤ gst < T1)** | **15.428** (T9: 1.255, T10: 3.299, T11: 8.385, T12: 2.489) |

Độ phủ tự nhiên: 32/105 ngày (14 lát tự nhiên; tăng từ 18). Kết luận "hồ sơ VƯỢT 14 ngày" càng vững (trade danh sách ≥15.428 request ≈ 77 ngày @200/ngày).

## Còn thiếu + đề xuất (mô tả, chưa chạy)
73/105 ngày chưa phủ tự nhiên, các khoảng: `09-27→09-30`, `10-04→10-06`, `10-10→10-13`, `10-23→10-26`, `10-30→12-26`.
**Còn 89/200 request chưa dùng trong ngày 06/11.** Nếu chủ nhân duyệt bằng văn bản, tôi chạy tiếp trong CÙNG ngày 06/11 với nhịp chậm hơn (20 giây/request) sau cooldown — API chỉ chậm 2 lần nội kích (~20 phút), nhiều khả năng đã hồi. Không có lệnh thì tôi dừng tới ngày 07/11 theo quy trình cũ. Ước còn ~300–400 request nữa mới xong hết.

## Errata (giữ nguyên): (1) 25 dòng ngày 2 = 13 biên phiên + 12 SSL-fallback; (2) request thật 03/11 = 358; (3) smt tennis 27.

## Xác nhận
Chỉ sửa liệt kê + đếm lại theo spec v2 hash ae504a97…; dò-trước chỉ phán CAP rồi chia tiếp, không phán xong; chưa chọn ví, chưa tính điểm, chưa backtest, chưa về trước; chưa sửa spec; chưa áp dụng cơ chế nào vào PaperDesk/Polymarket; không lặp request cũ; không chạy trùng tiến trình; trần 200 ngày 06/11 giữ (111/200 — dừng vì watchdog hết lượt retry, không phải lách trần).

**DỪNG — chờ lệnh mới của chủ nhân (hoặc lệnh chạy tiếp 89 request còn lại trong ngày 06/11, hoặc GO ngày 07/11).**
