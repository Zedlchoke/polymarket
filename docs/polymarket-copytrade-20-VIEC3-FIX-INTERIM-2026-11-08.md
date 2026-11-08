# BÁO CÁO INTERIM SỬA LIỆT KÊ VIỆC 3 — NGÀY 08/11 — CHƯA XONG, DỪNG THEO TRẦN 200

**Bản sửa liệt kê. KHÔNG phải hồ sơ chính, không phải backtest. Chưa chọn ví, chưa tính điểm, chưa tìm k*. LIỆT KÊ CHƯA XONG — mọi số VẪN LÀ CẬN DƯỚI.** Ngày 07/11 trôi qua 0 request (GO "ngày 7 ngày 8" đến sáng 08/11 — trần ngày 07 không dùng được theo luật ngày dương lịch).

## Tuân thủ ngày 08/11
- Preflight ghi đầu log: hash KHỚP ae504a97…; dò-trước 2 điểm ĐẠT; khóa sạch; sổ trước chạy = 0.
- **Đúng 200/200 request thật** (bộ đếm status+latency, ngày dương lịch giờ VN). Watchdog chậm xảy ra 2 lần trong ngày (tối đa 8.235 ms) — xử lý đúng giao thức GO gốc: dừng → cooldown 17 phút → đúng 1 retry 15 giây; sau đó tiếp tới khi chạm trần 200. Không 429/403; 0 khoảng <9 giây; 1 tiến trình/đợt (khóa); checkpoint liên tục; cache không lặp.
- Tích lũy từ đầu Việc 3: 358 + 200 + 200 + 172 + 0 + 200 = **1.130 request thật**.
- Ghi nhận: GO THƯỜ TRỰC của chủ nhân (08/11): "chạy mỗi ngày không cần hỏi" — đã dựng automation 00:10 hằng ngày, tự dừng khi liệt kê xong + báo cáo bản sửa được push.

## Số đếm hiện tại — CẬN DƯỚI
| Bước | Số (cận dưới) |
|---|---|
| Thị trường duy nhất | 65.864 |
| Phi thể thao | 36.767 (+978 anomaly có smt) |
| Mùa vụ | 9.318 |
| Thiếu gameStartTime | 228 |
| gst ngoài đoạn 1 | 768 (159 trước + 609 sau T1) |
| Tag rỗng | 0 |
| **Hợp lệ (T0 ≤ gst < T1)** | **17.805** (T9: 1.346, T10: 4.128, T11: 9.842, T12: 2.489) |

Độ phủ tự nhiên: **71/105 ngày** (37 lát tự nhiên; hôm nay +26 ngày: xong 10-12→13, 10-23→26, và Nov tới 24/11).

## Còn thiếu
34/105 ngày, các khoảng: 2025-11-15→2025-11-16; 2025-11-25→2025-12-26 (vùng Nov cuối–Dec dày ~600–700 thị trường/ngày). Ước còn ~200–300 request ≈ **1–2 ngày chạy nữa** — automation 00:10 ngày 09/11 sẽ tự chạy tiếp.

## Errata (giữ nguyên): (1) 25 dòng ngày 2 = 13 biên phiên + 12 SSL-fallback; (2) request thật 03/11 = 358; (3) smt tennis 27.

## Xác nhận
Chỉ sửa liệt kê + đếm lại theo spec v2 hash ae504a97…; dò-trước chỉ phán CAP; chưa chọn ví, chưa tính điểm, chưa backtest, chưa về trước; chưa sửa spec; chưa áp dụng cơ chế nào vào PaperDesk/Polymarket; không lặp request cũ; không chạy trùng tiến trình; trần 200 ngày 08/11 giữ nguyên vẹn (đúng 200/200).

**DỪNG phần hôm nay — automation chạy tiếp 00:10 ngày 09/11 theo GO thường trực.**
