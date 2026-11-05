# BÁO CÁO INTERIM SỬA LIỆT KÊ VIỆC 3 — NGÀY 05/11/2025-thực-lịch-2026 — CHƯA XONG, DỪNG THEO TRẦN NGÀY

*(ngày chạy: 2026-11-05, giờ VN)*

**Bản sửa liệt kê (tiếp theo kiểm toán BUG FOUND d8f2bb9 và interim 04/11). KHÔNG phải hồ sơ chính, không phải backtest. Chưa chọn ví, chưa tính điểm, chưa tìm k*. LIỆT KÊ CHƯA XONG — mọi số dưới đây VẪN LÀ CẬN DƯỚI.**

## Tuân thủ ngày 05/11
- Hash spec v2 tự tính lại trước khi chạy: `ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8` — KHỚP.
- Ghi nhận sự cố vận hành: job lên lịch 00:05 chết âm thầm (chưa chạy request nào, 0 thiệt hại); chạy lại 07:51 theo GO ngày 05/11 (GO phủ cả ngày dương lịch).
- **Đúng 200/200 request thật** (bộ đếm status+latency, ngày dương lịch giờ VN); **0 khoảng cách <9 giây**; 1 tiến trình duy nhất (khóa); không watchdog (max latency 2.889 ms); không 429/403; dừng vì hết trần — đúng luật.
- Tích lũy từ đầu Việc 3: 358 (03/11) + 200 (04/11) + 200 (05/11) = **758 request thật**.

## Kết quả ngày 05/11
- 200 trang mới trong 10 lát con (vùng 11-12→12-13); **9 lát 3-ngày đều CỤT đầy 2.100 dòng** (tân phát hiện: mật độ Nov–Dec ~600–700 thị trường/ngày — cao hơn Oct ~450–550) — dữ liệu 2.100 dòng/lát vẫn vào sổ/đĩa (không mất), nhưng các lát con sẽ phải lấy lại vùng này.
- Không lát nào kết thúc TỰ NHIÊN trong ngày (độ phủ tự nhiên giữ 18/105 ngày; +16.295 id mới nằm trong lát chưa hoàn tất).

## Số đếm hiện tại — CẬN DƯỚI
| Bước | Số (cận dưới) |
|---|---|
| Thị trường duy nhất (dedupe id) | 49.748 |
| Phi thể thao | 25.134 (+726 anomaly có smt) |
| Mùa vụ | 8.125 |
| Thiếu gameStartTime | 206 |
| gst ngoài đoạn 1 | 544 (159 trước + 385 sau T1) |
| Tag rỗng | 0 |
| **Hợp lệ (T0 ≤ gst < T1)** | **15.013** (T9: 845, T10: 3.299, T11: 8.385, T12: 2.484) |

Kết luận "hồ sơ VƯỢT 14 ngày" càng vững (trade danh sách ≥15.013 request ≈ 75 ngày @200/ngày).

## Còn thiếu + kế hoạch hiệu quả cho ngày kế (mô tả, chưa chạy)
Còn 87/105 ngày chưa phủ tự nhiên (hàng đợi 46 lát): các khoảng 2025-09-13→2025-09-30; 2025-10-04→2025-10-06; 2025-10-10→2025-10-13; 2025-10-23→2025-10-26; 2025-10-30→2025-12-26.
**Bài học hiệu quả phải khai:** script list3 thiếu bước dò-trước offset-2000 (list2 đã có, bị bỏ sót khi viết lại) → mỗi lát cụt tốn 22 request thay vì 1. Sẽ khôi phục dò-trước cho lần chạy sau (cùng kỹ thuật đã kiểm toán, không đổi luật, không đổi spec) — ước còn ~500–600 request ≈ **3 ngày dương lịch nữa @200/ngày** (không có dò-trước thì đắt gần gấp đôi).

## Errata (giữ nguyên từ interim 04/11)
(1) 25 dòng ngày 2 = 13 biên phiên + 12 SSL-fallback; (2) request thật 03/11 = 358 không phải 359; (3) smt tennis 27 không phải 37. Sẽ đưa đủ vào báo cáo bản sửa cuối.

## Xác nhận
Chỉ sửa liệt kê + đếm lại theo spec v2 hash ae504a97…; chưa chọn ví, chưa tính điểm, chưa backtest, chưa về trước; chưa sửa spec; chưa áp dụng cơ chế nào vào PaperDesk/Polymarket; không lặp request cũ; không chạy trùng tiến trình; trần 200 ngày 05/11 giữ nguyên vẹn (đúng 200/200).

**DỪNG — hết trần ngày 05/11, chưa xong liệt kê. Chờ lệnh GO của chủ nhân cho ngày 06/11. Không tự lăn sang ngày mới.**
