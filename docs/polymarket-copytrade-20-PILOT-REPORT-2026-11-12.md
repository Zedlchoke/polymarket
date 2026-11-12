# BÁO CÁO PILOT 100 THỊ TRƯỜNG — 2026-11-12 — KẾT QUẢ: PHƯƠNG PHÁP LẤY THEO THỊ TRƯỜNG KHÔNG KHẢ THI

**Đây là pilot đo chi phí (luật sửa 2026-11-12), KHÔNG phải hồ sơ chính, không phải backtest, chưa chọn ví, chưa tính điểm.** Pilot KHÔNG hoàn tất 100/100 — nhưng trả lời được câu hỏi quan trọng hơn: **chi phí thật của phương pháp hiện tại**.

## Diễn biến (tuân thủ)
- Luật sửa đã push trước khi chạy: ngưỡng 100k + hạn 45 ngày (`db0dd81`).
- Lần 1: watchdog chậm 7.290 ms ở request 11 → dừng đúng luật.
- Retry (sau cooldown 17 phút, nhịp 15 giây): dùng nốt 189 request — **toàn bộ bị thị trường #1 tiêu thụ mà chưa xong** → 0/100 thị trường hoàn tất; hôm nay 200/200, dừng đúng trần. Tích lũy từ đầu dự án: 1.505 request thật.

## Phát hiện chính (bằng chứng)
1. **Thị trường #1 theo id trong tập ≥100k = "Browns vs. Ravens" (NFL, volumeNum mô tả 623.847 USD): một mình cần >189 request** (≈ >47.000 fill trong đoạn 1) → trung bình ~13 USD/đơn lệnh:这类 thị trường lớn là nơi giao dịch lẻ siêu nhỏ của hàng vạn người — số LỆNH khổng lồ chứ không phải số trận.
2. **Ước tính lại (offline, từ volumeNum mô tả + avg-bet đo được 13–800 USD/fill):** ngưỡng 100k → **46–308 ngày**; 250k → 42–285; 500k → 38–257; 1M → vẫn rất lớn. **Nâng ngưỡng KHÔNG giải quyết được** vì tiền tập trung đúng vào các thị trường nhiều lệnh nhất. Kế hoạch 100k + 45 ngày sáng nay **không khả thi theo dữ liệu đo thật** — hạn 45 ngày đã bị vượt ở cận dưới của mọi ngưỡng.

## Khai lỗi của tôi (agent) trong pilot
1. Script pilot KHÔNG có trần request/thị trường → một thị trường khổng lồ nuốt cả ngân sách ngày.
2. Response theo cửa sổ KHÔNG được ghi đĩa từng bước (chỉ ghi khi xong thị trường) → 189 request của thị trường #1 mất dữ liệu (chỉ còn ledger). Cả 2 lỗi đã ghi nhận để sửa nếu chạy pilot lại.

## Kết luận + lựa chọn cho chủ nhân (không tự quyết)
**Lấy trade theo TỪNG THỊ TRƯỜNG là ngõ cụt về chi phí ở mọi ngưỡng.** Còn 2 hướng thật:
- **(A) Thiết kế lại (spec v3) — lấy dữ liệu theo TỪNG VÍ thay vì theo thị trường.** Bằng chứng quan trọng từ probe 03/11: query theo VÍ (`/v2/trades?user=…`) CÓ phân trang cursor hiệu quả (17.248 fill chỉ tốn 35 request, không cần chia cửa sổ). Nếu dựng được danh sách ví ứng viên rẻ (ví dụ: ví xuất hiện lặp lại trong mẫu fill của các thị trường lớn), chi phí có thể giảm ~10–50 lần vì bỏ qua hàng triệu lệnh lẻ của người mua nhỏ. Cần: viết spec v3 đầy đủ → kiểm toán → duyệt → đóng băng (quy trình chuẩn).
- **(B) Chấp nhận thời gian thật** (ít nhất ~1,5–10 tháng chỉ lấy dữ liệu) — khả thi về kỹ thuật, đắt về thời gian; hạn 45 ngày phải sửa lại lần nữa thành vài tháng.
- (C) Dừng dự án ở kết luận "không thể đánh giá trong thời gian hợp lý" — cũng là một câu trả lời thành thật.

**DỪNG — hết trần 200/200 ngày 12/11. Chờ chủ nhân chọn hướng (A)/(B)/(C).**
