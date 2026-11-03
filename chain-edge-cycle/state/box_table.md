# Bảng 3 hộp — cập nhật sau mỗi wave (ngày cập nhật gần nhất: 2026-11-02)

## Box 1 — SỐNG có bằng chứng (spec hash + backtest qua cổng giết + kiểm toán CONFIRMED)

| Ngày | Cơ chế | Chuỗi | Spec + hash | Lãi ròng sau chi phí | Kiểm toán |
|---|---|---|---|---|---|
| (trống) | | | | | |

## Box 2 — CHẾT hẳn (đã qua cổng giết, không còn đường hợp lệ trong cùng luật)

| Ngày | Cơ chế | Chuỗi | Chết ở tầng nào | Lý do cụ thể | Kiểm toán |
|---|---|---|---|---|---|
| (trống) | | | | | |

## Box 3 — THIẾU DỮ LIỆU (chỉ vì dữ liệu bị khóa/chặn/lịch sử không đủ — không phải vì kết quả xấu)

| Ngày | Cơ chế | Chuỗi | Dữ liệu thiếu cụ thể | Còn đường hợp lệ nào không |
|---|---|---|---|---|
| 2026-11-02 (loop 10h) | M1 mua sớm token mới listing (W1) — **ĐỀ XUẤT Box 3, chờ kiểm toán CONFIRMED** | Base (3 factory cổ điển) + Solana | Solana: ~38.400 pool/ngày vượt hạn mức lấy vũ trụ không thiên lệch. Base: pool mới thật nằm ở dex/launchpad mới không enumerate được không-key (GT chặn trang sâu; publicnode yêu cầu địa chỉ; mainnet.base.org chặn getLogs); vũ trụ 3-factory = 123 pool, 100% không có swap trong 24h đầu → thiếu giá tuyệt đối, thiếu mẫu (≤83/epoch < 200) | Có — chưa tịt hẳn: chờ đo lại GT (3 call 00:01Z 2026-11-03); nếu GT OHLCV chạy được + new_pools vẫn bị chặn trang thì cần indexer dài hạn qua nhiều ngày, hoặc cơ chế chuyển sang chuỗi khác trong hàng đợi |

