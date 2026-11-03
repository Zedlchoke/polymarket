# BÁO CÁO INTERIM SỬA LIỆT KÊ VIỆC 3 — NGÀY 04/11/2026 — CHƯA XONG, DỪNG THEO TRẦN NGÀY

**Đây là bản sửa liệt kê (sau kiểm toán BUG FOUND d8f2bb9), KHÔNG phải hồ sơ chính, không phải backtest. Chưa chọn ví, chưa tính điểm, chưa tìm k*. LIỆT KÊ CHƯA XONG — mọi số đếm dưới đây VẪN LÀ CẬN DƯỚI.**

## Cửa pháp lý & tuân thủ
- GO sửa liệt kê ngày 04/11 của chủ nhân (2026-11-03 18:53 ICT). Hash spec v2 tự tính lại trước khi chạy: `ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8` — KHỚP.
- Bước 0 (in danh sách lát thiếu offline, 0 request) đã xong tối 03/11, commit `b0527d8`: bản đồ 41 node/19 leaf, đối chiếu đủ 24 nhánh CAP + queue-6 + lát dở + 28 dò-only + 2 tự nhiên; giải thích queue-9≠queue-6; bộ đếm trần sửa thành status+latency (=358 ngày 03/11).
- Chạy 00:05–00:44 ngày 04/11 giờ VN: **đúng 200 request thật** (194×HTTP200 + 6×422 offset-cap), nhịp ≥10 giây giữ trọn (**0 khoảng cách <9 giây** — không lặp lỗi chạy trùng), 1 tiến trình duy nhất (khóa viec3.lock), không watchdog (max latency 2.167 ms), không 429/403. Tích lũy từ đầu Việc 3: 358 + 200 = **558 request thật**.
- Dừng vì TRẦN 200/NGÀY DƯƠNG LỊCH (giờ VN) — đúng luật, không phải lỗi.

## Kết quả đêm 04/11 (6 lát kết thúc tự nhiên)
10-01→10-03 (xác nhận lại), 10-07→10-09 (xác nhận lại), **10-14→10-16 (lát dở đi tiếp từ offset 400 — xong tự nhiên)**, 10-17→10-19, 10-20→10-22, 10-27→10-29. Độ phủ tự nhiên: 18/105 ngày cửa sổ.

## Số đếm hiện tại — CẬN DƯỚI (liệt kê chưa xong)
| Bước | Số (cận dưới) |
|---|---|
| Tổng dòng trang đã lưu | 48.212 |
| Thị trường duy nhất (dedupe id) | 33.453 |
| Phi thể thao (không tag Sports) | 17.453 (+717 anomaly có smt) |
| Mùa vụ (smt rỗng) | 6.521 |
| Thiếu gameStartTime | 189 |
| gst ngoài đoạn 1 (159 trước + 146 sau) | 305 |
| Tag rỗng | 0 |
| **Hợp lệ (T0 ≤ gst < T1)** | **8.268** (tháng: 9=845, 10=3.299, 11=3.874, 12=250) |

So với báo cáo cũ (16.748/2.743 — cũng là cận dưới): pool thật lớn hơn nhiều đúng như kiểm toán dự báo; **kết luận "hồ sơ VƯỢT 14 ngày" càng vững** (riêng trade danh sách đã ≥8.268 request ≈ 41 ngày @200/ngày, chưa kể resolutions/phí/ví).

## Còn thiếu (không ghi "đã xong")
87/105 ngày cửa sổ chưa có phủ tự nhiên, theo khoảng: 2025-09-13→2025-09-30; 2025-10-04→2025-10-06; 2025-10-10→2025-10-13; 2025-10-23→2025-10-26; 2025-10-30→2025-12-26.
Ước lượng phần còn lại: ~350–500 request ≈ **2–3 ngày dương lịch nữa @200/ngày** (ước tính, số thật biết khi chạy). Cần lệnh GO của chủ nhân cho ngày 05/11 (và có thể 06/11) để chạy tiếp từ cache — script/list3 đã sẵn, không lặp request cũ.

## Errata (3 lỗi khai báo của báo cáo Việc 3 cũ ở commit 85f8732 — ghi lại cho rõ)
1. Thành phần 25 dòng ngày 2: đúng là **13 dòng biên phiên + 12 dòng SSL-fallback**, không phải "10 + … + 2 dòng 400-SSL" như báo cáo cũ ghi. Nguyên nhân: tôi mô tả theo trí nhớ thay vì đếm lại từ sổ.
2. Request thật chạm server = **358**, không phải 359: 1 dòng ghi tay `E_market_body` có status 400 nhưng không tới server (lỗi SSL cục bộ, latency=None). Bộ đếm trần đã sửa để loại đúng dòng này.
3. Số loại thị trường tennis trong mô tả smt = **27**, không phải 37 (lỗi gõ nhầm).

File báo cáo cũ commit 85f8732 giữ nguyên không sửa tại chỗ; các Errata này sẽ đưa vào đầy đủ trong báo cáo bản sửa cuối cùng khi liệt kê xong.

## Xác nhận
Chỉ sửa liệt kê + đếm lại theo spec v2 hash ae504a97…; chưa chọn ví, chưa tính điểm, chưa backtest, chưa về trước; chưa sửa spec; chưa áp dụng cơ chế nào vào PaperDesk/Polymarket; không lặp request cũ (cache dùng lại 0 request); không chạy trùng tiến trình; trần 200/ngày dương lịch giờ VN được giữ nguyên vẹn (đúng 200/200 hôm nay).

**DỪNG — chờ lệnh GO của chủ nhân cho ngày 05/11.**
