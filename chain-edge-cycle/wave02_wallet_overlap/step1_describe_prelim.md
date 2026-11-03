# W2 — Bước 1 (MÔ TẢ SƠ BỘ, không tính điểm) — 2026-11-02T15:50Z

> Dữ liệu: Transfer logs 24h đầu của 123 base token vũ trụ W1 (đóng băng 15:47Z).
> ĐÂY LÀ MÔ TẢ TIÊN PHONG trên tập hẹp — không đại diện vũ trụ W2 đầy đủ (xem step0 mục 2).
> Chỉ mô tả cấu trúc; KHÔNG lãi ròng, KHÔNG chọn ví tốt nhất.

## Số liệu thô

- Tổng ví duy nhất (sau loại địa chỉ pool + zero-addr): **414**; tổng cặp (pool, ví): 629.
- 121/123 pool có ít nhất 1 ví đụng token (dù 0/123 pool có swap → hoạt động là CHUYỂN TRỰC TIẾP
  token, không phải giao dịch qua pool — nhất quán với giả thuyết spam/airdrop, không phải giao dịch thật).
- Lệnh mua/ví (đếm hướng pool→ví): median **1**, mean 10.9, max **1.631** (rõ ràng là bot).
- Ví mua ≥ 2 pool: **63**. Chỉ mua không bán: 204. Chỉ bán: 11. Cả hai chiều: 199.
- Cờ tần suất >200 lệnh/24h (nghi bot/MM, CỜ chứ không loại — theo tiêu chí đóng băng): **4 ví**.

## Đọc cấu trúc (không phải kết luận edge)

- Phân phối cực lệch: nửa ví chỉ 1 lệnh; vài ví hàng nghìn lệnh → dân số = người thả rác + bot,
  gần như không có "trader" theo nghĩa cơ chế overlap.
- Với cơ chế overlap-ví-độc-lập: trên tập dữ liệu hẹp này, "nhiều ví độc lập cùng MUA QUA POOL
  một token trong 24h" = 0 trường hợp (vì không pool nào có swap). Overlap có thể có ở tầng
  Transfer (ví cùng nhận token) — nhưng nhận token không phải mua; không được đếm là tín hiệu mua.

## Hạn chế ghi cho kiểm toán

- 1/123 token bị lỗi "query exceeds max results 20000" (token spam cực lớn) → thiếu dữ liệu 1 pool.
- Volume quy ước 18 decimals cho mọi token (ghi wallets_NOTE.txt) — chỉ dùng ĐẾM LỆNH trong báo cáo.
- Không phân biệt được EOA/hợp đồng (không gọi eth_getCode) → có thể có ví-hợp đồng trộn lẫn.
- Ghép cụm theo tiêu chí đóng băng (cùng mua trong 5 phút ở ≥3 token) CHƯA chạy — mô tả này đếm ví rời.
