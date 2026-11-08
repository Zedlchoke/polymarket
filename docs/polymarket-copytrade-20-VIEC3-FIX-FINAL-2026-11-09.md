# BÁO CÁO BẢN SỬA LIỆT KÊ VIỆC 3 — HOÀN TẤT — 2026-11-09

**ĐÂY LÀ BẢN SỬA LIỆT KÊ VÀ ĐẾM LẠI (sau kiểm toán BUG FOUND `d8f2bb9`), KHÔNG PHẢI HỒ SƠ CHÍNH, KHÔNG PHẢI BACKTEST. Chưa chọn ví, chưa tính điểm, chưa tìm k\*, chưa chọn 20 nhóm, chưa tính lời lỗ.**

File này THAY THẾ phần liệt kê/đếm của báo cáo Việc 3 cũ (commit `85f8732`) và các interim (f2cd581, 7634d8b, 040802a, 02d8f3f, c1a7cd4 — giữ nguyên, không sửa tại chỗ). Các phần CÒN GIỮ NGUYÊN của báo cáo cũ: kỹ thuật endpoint đã đo (offset-cap 2100, condition_id, không cursor/offset), kết quả tra-lại-theo-mã 8/8 không lệch, mẫu ngưỡng 10k (9 thị trường, 6/9 đạt — MÔ TẢ, không thay đổi), phát hiện về hồ sơ VƯỢT 14 ngày (nay củng cố bằng số đầy đủ dưới đây).

## 1. Hash spec tự tính lại

`shasum -a 256 docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md` = `ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8` — KHỚP luật; kiểm lại trước MỖI đợt chạy (ghi đầu mỗi log `list3_run_day*.log`).

## 2. LIỆT KÊ XONG — xác minh theo đúng 2 điều kiện luật

Luật hoàn tất (đã sửa sau BUG FOUND): tự nhiên = trang ngắn <100 hoặc rỗng ở offset <2100; rỗng ở offset ≥2100 = CỤT phải chia nhỏ tiếp; dò-trước CHỈ phán CAP (2 điểm kiểm tra bắt buộc đạt, ghi đầu log mỗi ngày).

- **Điều kiện A — mọi cửa sổ kết thúc tự nhiên:** 63/63 LÁ tự nhiên; 0 lá CỤT/PARTIAL; phủ tự nhiên **105/105 ngày** cửa sổ end_date [2025-09-13 → 2025-12-26]; 0 unresolved-giờ. (Bằng chứng: `viec3/data/final_completion_verification.json`.)
- **Điều kiện B — hàng đợi rỗng:** đợt 09/11 kết thúc bằng dòng "KẾT THÚC" bình thường, 0 lần "DỪNG THEO LUẬT" trong log, hàng đợi 0.
- **Khai lỗi công thức (không ảnh hưởng dữ liệu):** trường `complete` trong `slices3_status.json`/`coverage_fixed.json` in `false` do công thức tổng kết đòi mọi NODE cây (kể cả lát CHA đã chia đôi — vốn không thể NATURAL theo thiết kế) phải NATURAL. Công thức sai ở chỗ đó; điều kiện luật (mọi LÁ tự nhiên + hàng đợi rỗng) ĐỦ và ĐÃ ĐẠT — xác minh độc lập ở trên.

## 3. Lát đã lấy thêm qua các ngày sửa (tóm tắt; chi tiết trong interim từng ngày + cây `slices3_status.json` ghi cha-con)

Ngày 04/11: 6 lát tự nhiên (10-01→03, 10-07→09, lát dở 10-14→16, 10-17→19, 10-20→22, 10-27→29). Ngày 05/11: 10 lát 3-ngày Nov–Dec (đều CỤT đầy 2.100 — mật độ 600–700/ngày). Ngày 06/11: hết tháng 9 + 10-04→06 + 10-10→11. Ngày 08/11: 10-12→13, 10-23→26, Nov tới 24/11. Ngày 09/11: các lát cuối 11-15→16, 11-25→12-26 (tới 12-26). Tổng cây: 129 node, 63 lá tự nhiên.

## 4. Request tách theo từng ngày dương lịch (giờ VN; bộ đếm status+latency)

| Ngày | Request thật | Ghi chú |
|---|---|---|
| 03/11 | 358 | gồm ngày-chạy 1 (184) + ngày-chạy 2 (174) theo lệnh cũ |
| 04/11 | 200 | |
| 05/11 | 200 | |
| 06/11 | 172 | 28 bỏ theo lệnh watchdog chặt |
| 07/11 | 0 | ngày trôi qua không chạy |
| 08/11 | 200 | GO thường trực bắt đầu |
| 09/11 | 175 | hàng đợi rỗng — không cần hết trần |
| **Tổng** | **1.305** | |

Dò-trước: 91 lần dò, 9 lát phán CAP ngay (1 request thay 22) → tiết kiệm ~189 request.

## 5. SỐ ĐẾM LẠI TỪNG BƯỚC LỌC — ĐẦY ĐỦ (liệt kê xong; không còn cận dưới)

Tổng dòng trang đã lưu: 111.672 (gồm trùng do chia lát). Khử trùng theo id:

| Bước lọc | Số |
|---|---|
| **Thị trường duy nhất** | **71.351** |
| Phi thể thao (không tag Sports) | 40.104 |
| — anomaly có sportsMarketType nhưng không tag Sports | 978 |
| Mùa vụ (Sports + smt rỗng) | 9.361 |
| Thiếu gameStartTime | 229 |
| Thể thao trận đơn, gst TRƯỚC T0 | 159 |
| Thể thao trận đơn, gst SAU T1 (13–26/12) | 1.290 |
| Tag rỗng sau include_tag=true | 0 |
| **HỢP LỆ (tag 'Sports' + smt ≠ rỗng + T0 ≤ gameStartTime < T1)** | **19.230** |

Phân bố hợp lệ theo tháng gameStartTime: **T9-2025: 1.346 · T10: 4.128 · T11: 10.555 · T12 (tới 12/12): 3.201.** Danh sách đầy đủ: `viec3/data/listing/listing_slim.jsonl.valid_FULL` (19.230 dòng, tạo lại từ đĩa).

## 6. Errata — 3 lỗi khai báo của báo cáo Việc 3 cũ (commit 85f8732)

1. **Thành phần 25 dòng ngày 2:** đúng là **13 dòng biên phiên (DAY_BOUNDARY) + 12 dòng nhật ký SSL-fallback**; báo cáo cũ ghi "10 + nhật ký SSL + 2 dòng ghi 400 nhưng thật ra lỗi SSL cục bộ" — SAI. Nguyên nhân: mô tả theo trí nhớ thay vì đếm từ sổ. (Dòng `E_market_body` status 400 nằm TRONG nhóm 175 — ghi tay sau lỗi SSL cục bộ, không tới server; dòng `F_condition_id` không tồn tại trong sổ.)
2. **Request thật chạm server ngày 03/11 = 358, không phải 359** — loại đúng 1 dòng ghi tay trên. Bộ đếm trần đã sửa thành "status VÀ latency_ms" (tại `viec3_lib._count_today`).
3. **Số loại thị trường tennis trong mô tả smt = 27, không phải 37** — lỗi đánh máy.

## 7. Cập nhật kết luận "hồ sơ VƯỢT 14 ngày" bằng số ĐẦY ĐỦ

Hạn hồ sơ: ~200 request/ngày × 14 ngày ≈ 2.800 request. Chỉ riêng việc lấy trade đoạn 1 cho **19.230** thị trường hợp lệ đã cần ≥ 19.230 request (endpoint không cursor/offset — đã chứng minh) ≈ **96 ngày @200/ngày**, chưa tính resolutions/phí từng thị trường giữ (mẫu 6/9 đạt → ước ~12.800 thị trường giữ) và query từng ví cho Q2/Q3. **KẾT LUẬN VƯỢT 14 NGÀY: CHẮC CHẮN, vượt ~82+ ngày chỉ tính trade.** Hướng xử lý (thu hẹp theo luật KHÔNG dựa trên lãi / kéo dài / đổi thiết kế) là quyết định của chủ nhân — mô tả đủ trong báo cáo Việc 3 cũ và interim; không tự quyết.

## 8. Tuân thủ toàn bộ đợt sửa (04–09/11)

Trần 200/ngày dương lịch giờ VN giữ trọn (mỗi ngày ≤200, tổng 1.305); khóa tiến trình không chạy trùng (0 khoảng <9 giây từ 04/11 trở đi); nhịp ≥10 giây (15–20 giây sau watchdog/DNS theo lệnh); mọi watchdog/DNS xử lý đúng luật và khai đầy đủ trong interim từng ngày; cache không lặp request; checkpoint liên tục; không 429/403; KHÔNG pilot, KHÔNG Việc 4/5; không sửa spec v2 (hash khớp xuyên suốt)/kiểm toán/báo cáo cũ tại chỗ; không áp dụng cơ chế nào vào PaperDesk hay Polymarket.

**DỪNG. Chờ chủ nhân giao kiểm toán lại Việc 3 từ đầu bằng agent khác (file mới). Không tự chạy bước nào khác.**
