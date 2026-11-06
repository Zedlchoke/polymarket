# BÁO CÁO INTERIM SỬA LIỆT KÊ VIỆC 3 — NGÀY 06/11 BẢN CẬP NHẬT CUỐI NGÀY — CHƯA XONG, DỪNG THEO LỆNH WATCHDOG CHẶT

**Bản sửa liệt kê. KHÔNG phải hồ sơ chính, không phải backtest. Chưa chọn ví, chưa tính điểm, chưa tìm k*. LIỆT KÊ CHƯA XONG — mọi số VẪN LÀ CẬN DƯỚI.** (Thay thế bản interim sáng 06/11 ở commit 040802a — file đó giữ nguyên không sửa.)

## Tổng hợp cả ngày 06/11 (3 đợt chạy)
| Đợt | Request | Kết thúc |
|---|---|---|
| Đêm 00:05–00:50 (10s) | 111 | watchdog 5.437ms → cooldown 17p → 1 retry 15s đúng GO → watchdog 5.235ms → dừng |
| Sáng 09:33–09:56 (20s, chạy tiếp 89 theo lệnh chủ nhân) | 58 | lỗi DNS (gaierror) → dừng ngay theo luật; DNS hồi sau vài giây (đã kiểm tra bằng phân giải tên, 0 request API) |
| Sáng 09:57–10:00 (20s, tiếp 31 còn lại) | 3 | **watchdog 12.202 ms → DỪNG NGAY theo lệnh chặt, không chạy lại hôm nay dù còn 28 request** |

- **Tổng ngày 06/11: 172/200 request thật** (28 không dùng — bỏ theo lệnh watchdog chặt). Không 429/403; 0 khoảng <9 giây; 1 tiến trình/đợt (khóa); checkpoint liên tục; cache không lặp.
- Tích lũy từ đầu Việc 3: 358 + 200 + 200 + 172 = **930 request thật**.
- API Polymarket/Gamma chậm bất thường 3 lần trong ngày (5.437 / 5.235 / 12.202 ms — trung vị cả ngày ~1,5s) — hiện tượng phía server/mạng, không phải do nhịp của ta.
- **Dò-trước cả ngày: 19 lần dò, 4 lát phán CAP ngay (1 request thay vì 22) → tiết kiệm ~84 request.**

## Số đếm hiện tại — CẬN DƯỚI
| Bước | Số (cận dưới) |
|---|---|
| Thị trường duy nhất | 60.516 |
| Phi thể thao | 33.460 (+905 anomaly có smt) |
| Mùa vụ | 9.289 |
| Thiếu gameStartTime | 228 |
| gst ngoài đoạn 1 | 768 (159 trước + 609 sau T1) |
| Tag rỗng | 0 |
| **Hợp lệ (T0 ≤ gst < T1)** | **15.866** (T9: 1.346, T10: 3.646, T11: 8.385, T12: 2.489) |

Độ phủ tự nhiên: **45/105 ngày** (19 lát tự nhiên; hôm nay +27 ngày: xong hết tháng 9, 10-04→06, 10-10→11).

## Còn thiếu
64/105 ngày, 3 khoảng: `10-12→10-13`, `10-23→10-26`, `10-30→12-26` (chủ yếu là vùng Nov–Dec dày ~600–700 thị trường/ngày). Ước còn ~250–350 request ≈ **2 ngày dương lịch nữa @200/ngày**.

## Errata (giữ nguyên): (1) 25 dòng ngày 2 = 13 biên phiên + 12 SSL-fallback; (2) request thật 03/11 = 358; (3) smt tennis 27.

## Xác nhận
Chỉ chạy tiếp đúng 89 được duyệt (thực dùng 61 trong 2 đợt sáng; đợt cuối dừng ngay khi watchdog 12.202ms theo lệnh — tổng 172/200, không lách); nhịp 20 giây giữ ở cả 2 đợt sáng; chỉ sửa liệt kê + đếm lại theo spec v2 hash ae504a97… (preflight ĐẠT ghi đầu log); dò-trước chỉ phán CAP; chưa chọn ví, chưa tính điểm, chưa backtest, chưa về trước; chưa sửa spec; chưa áp dụng cơ chế nào vào PaperDesk/Polymarket; không lặp request cũ; không chạy trùng tiến trình.

**DỪNG — hết phần được chạy trong ngày 06/11 (lệnh watchdog chặt). Chờ GO ngày 07/11 của chủ nhân.**
