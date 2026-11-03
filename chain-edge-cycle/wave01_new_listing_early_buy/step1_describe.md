# W1 — Bước 1: MÔ TẢ (không tính điểm, không lãi ròng) — 2026-11-02 loop 10h

## Vũ trụ (đã đóng băng ở bước 0)
- Tổng pool: 123. Có ≥1 swap trong 24h đầu: 0. Có ≥2 swap: 0. KHÔNG swap nào (chết ngay / thiếu giá tuyệt đối): 123 (100%).
- E1: 83 pool, 0 pool có swap.
- E2: 27 pool, 0 pool có swap.
- E3: 13 pool, 0 pool có swap.
- Số swap/pool (chỉ pool có swap): median=0, max=0.

## Cờ tập trung
- pool 0x4ee2a2…46ee (E1, quote USDC): 0 swap.
- pool 0x76b7d9…5e84 (E1, quote USDC): 0 swap.
- pool 0x6c8335…6f54 (E1, quote USDC): 0 swap.
- pool 0x895d2d…44b3 (E1, quote USDC): 0 swap.
- pool 0x74c898…4fe1 (E1, quote USDC): 0 swap.

## Ví (từ Transfer logs — mô tả thô)
- Số ví duy nhất xuất hiện: 414. 
- Số lệnh mua/ví: median=1.0, max=1631.
- Ví giao dịch ≥2 pool trong dữ liệu: 63.

## Gas mẫu (nếu có)
- chưa có (gặp lỗi hoặc chưa đủ pool có swap)

## Kết luận mô tả (không phải verdict)
- Vũ trụ 3-factory hầu như là POOL CHẾT NGAY: 123/123 pool không có lấy một swap nào trong 24h đầu → 'tỷ lệ bỏ vì thiếu giá' sẽ vượt xa mức 30% của cổng T1 nếu backtest thật.
- Số liệu này là MÔ TẢ cấu trúc dữ liệu, không phải kết quả backtest, không phải verdict.
