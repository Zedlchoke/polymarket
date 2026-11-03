# DANH SÁCH LÁT THIẾU TRƯỚC KHI CHẠY SỬA 00:05 NGÀY 04/11 — IN OFFLINE, 0 REQUEST API

- Ngày lập: 2026-11-03 tối (lệnh chủ nhân). Script: `viec3/scripts/v3_missing_slices_prerun.py` (chỉ đọc cache trang trên đĩa).
- Luật hoàn tất (ĐÃ SỬA theo kiểm toán d8f2bb9): NATURAL = trang ngắn <100 hoặc rỗng ở offset <2100; **rỗng ở offset ≥2100 = CỤT phải chia tiếp**; probe-only (page_2000=100 dòng, không page_0) = CAP.

## Bản đồ hiện trạng: 41 node cây, 19 leaf việc-cần-làm

| # | Cửa sổ | Lát cha | Trạng thái | Bằng chứng |
|---|---|---|---|---|
| 1 | 2025-10-17→2025-10-22 | 2025-10-10→2025-10-22 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 2 | 2025-10-23→2025-10-29 | 2025-10-23→2025-11-04 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 3 | 2025-10-30→2025-11-04 | 2025-10-23→2025-11-04 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 4 | 2025-11-05→2025-11-11 | 2025-11-05→2025-11-17 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 5 | 2025-11-12→2025-11-17 | 2025-11-05→2025-11-17 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 6 | 2025-11-18→2025-11-24 | 2025-11-18→2025-11-30 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 7 | 2025-11-25→2025-11-30 | 2025-11-18→2025-11-30 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 8 | 2025-12-01→2025-12-07 | 2025-12-01→2025-12-13 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 9 | 2025-12-08→2025-12-13 | 2025-12-01→2025-12-13 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 10 | 2025-12-14→2025-12-20 | 2025-12-14→2025-12-26 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 11 | 2025-12-21→2025-12-26 | 2025-12-14→2025-12-26 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 12 | 2025-09-13→2025-09-16 | 2025-09-13→2025-09-19 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 13 | 2025-09-17→2025-09-19 | 2025-09-13→2025-09-19 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 14 | 2025-09-20→2025-09-23 | 2025-09-20→2025-09-26 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 15 | 2025-09-24→2025-09-26 | 2025-09-20→2025-09-26 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 16 | 2025-09-27→2025-09-30 | 2025-09-27→2025-10-03 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 17 | 2025-10-04→2025-10-06 | 2025-10-04→2025-10-09 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 18 | 2025-10-10→2025-10-13 | 2025-10-10→2025-10-16 | CAP | dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật |
| 19 | 2025-10-14→2025-10-16 | 2025-10-10→2025-10-16 | PARTIAL | chuỗi dừng ở offset 400, chưa có trang chốt |

Thống kê đĩa (khớp kiểm toán): probe-only tổng 28 (không dir con 18 + có dir con 10) = "28 lát dò-only"; NATURAL 2 = "2 lát tự nhiên thật".

## Bảng đối chiếu với kiểm toán (từng dòng)

| Mục kiểm toán | Cửa sổ | Trạng thái của tôi | Là leaf việc-cần-làm? | Dir con trên đĩa |
|---|---|---|---|---|
| queue-6 | 2025-10-10→2025-10-22 | PARTIAL | không (việc tiếp tục ở dir con) | 2025-10-10→2025-10-16, 2025-10-17→2025-10-22 |
| queue-6 | 2025-10-23→2025-11-04 | CAP | không (việc tiếp tục ở dir con) | 2025-10-23→2025-10-29, 2025-10-30→2025-11-04 |
| queue-6 | 2025-11-05→2025-11-17 | CAP | không (việc tiếp tục ở dir con) | 2025-11-05→2025-11-11, 2025-11-12→2025-11-17 |
| queue-6 | 2025-11-18→2025-11-30 | CAP | không (việc tiếp tục ở dir con) | 2025-11-18→2025-11-24, 2025-11-25→2025-11-30 |
| queue-6 | 2025-12-01→2025-12-13 | CAP | không (việc tiếp tục ở dir con) | 2025-12-01→2025-12-07, 2025-12-08→2025-12-13 |
| queue-6 | 2025-12-14→2025-12-26 | CAP | không (việc tiếp tục ở dir con) | 2025-12-14→2025-12-20, 2025-12-21→2025-12-26 |
| lát dở | 2025-10-14→2025-10-16 | PARTIAL | CÓ | — |

**24 nhánh CAP của kiểm toán = cấu thành theo đĩa:** 18 lát probe-only KHÔNG dir con (danh sách leaf 1–18 ở trên) + 5 lát queue-6 probe-only CÓ dir con nhưng dir con chưa hoàn thành (10-23→11-04, 11-05→11-17, 11-18→11-30, 12-01→12-13, 12-14→12-26) + 1 lát queue PARTIAL 10-10→10-22 (18 trang chưa chốt) = **24**. Không gộp  nào không ghi rõ; không nhánh nào bị bỏ.

**28 lát dò-only =** 18 (không dir con) + 10 (có dir con: 5 queue trên + 09-13→09-19, 09-20→09-26, 09-27→10-03, 10-04→10-09, 10-10→10-16) = **28** ✓.

**2 lát tự nhiên thật =** 10-01→10-03 (17 trang, trang cuối ngắn) và 10-07→10-09 (14 trang) — đã xong THẬT, không cần đi lại (trang cache giữ nguyên dùng cho đếm).

## Giải thích queue-9 khác queue-6
Queue-6 (kiểm toán, từ slices_progress.json run cuối ngày 2) và queue-9 (dry-run a74a382, slices3_progress.json) là HAI ẢNH CHỤP BFS ở hai thời điểm khác nhau của cùng cây việc. Queue-9 gồm: 5/6 lát queue của kiểm toán (10-23→11-04, 11-05→11-17, 11-18→11-30, 12-01→12-13, 12-14→12-26 — bị pop rồi phán quyết CAP từ cache probe rồi re-enqueue con) + 4 lát con MỚI sinh do dry-run chia tiếp 2 nhánh [09-13→09-26] và [09-27→10-09] mà run cũ chưa từng tới (09-13→09-19, 09-20→09-26, 09-27→10-03, 10-04→10-09). Lát thứ 6 của kiểm toán (10-10→10-22) là lát ĐANG XỬ LÝ lúc dry-run dừng nên không xuất hiện trong file queue — vô hại vì cây dựng lại từ đĩa luôn nhận ra nó là PARTIAL (18 trang, chưa có trang chốt). Không nhánh nào bị mất.

## Bộ đếm trần
Bộ đếm trần (viec3_lib._count_today, đã sửa tối 03/11): đếm dòng sổ CÓ status VÀ CÓ latency_ms (= request thật chạm server). Ngày 03/11: 358 (loại đúng 1 dòng ghi tay E_market_body có status 400 nhưng latency=None, không tới server). Trước sửa chỉ đếm status → 359; đã sửa tại _count_today, thêm điều kiện latency_ms is None → bỏ qua.
