# Wave log — mỗi dòng một wave (hoặc một chuỗi trong wave)

| Wave | Chuỗi | Cơ chế | Bắt đầu | Hạn (14 ngày) | Spec + sha256 | Trạng thái | Verdict | Kiểm toán |
|---|---|---|---|---|---|---|---|---|
| W1 | base (solana dự kiến Box 3) | M1: mua sớm token mới listing DEX, bán theo luật cố định | 2026-11-02 | 2026-11-16 | (spec chỉ ở dạng NHÁP — không hash, không backtest) | Loop 10h 2026-11-02: vũ trụ 123 pool (mọi epoch <200), 0/123 pool có swap trong 24h, 414 ví mô tả được. Trạng thái dữ liệu: CHƯA ĐỦ BẰNG CHỨNG (thiếu mẫu + thiếu giá + thiên lệch nguồn). Đề xuất Box 3 chờ kiểm toán. Chưa backtest, chưa verdict | — | — |
| W2 | base (tập hẹp = vũ trụ W1) | M3: overlap ví độc lập mua cùng token trong 24h | 2026-11-02 (bước 0-1) | — | (chưa có spec — đúng giới hạn chặng 5 loop) | Bước 0 đóng băng 15:47Z; bước 1 mô tả sơ bộ xong (414 ví, 0 trường hợp overlap-mua thật trên tập hẹp). Cần nguồn token-vũ-trụ rộng để tiếp tục | — | — |
