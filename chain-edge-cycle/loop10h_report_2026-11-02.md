# BÁO CÁO CUỐI LOOP 10 TIẾNG — edge blockchain W1/W2 (chỉ giấy)

- Giờ bắt đầu: **2026-11-02T14:22:30Z** (T0). Hạn cứng: 2026-11-03T00:22:30Z.
- Giờ kết thúc: **2026-11-03T00:05Z** — Lý do dừng: **xong sớm mọi việc đã định** (công việc chính
  xong từ 15:57Z ngày 2026-11-02; phần còn lại là 3 call GT đo lại đúng sau nửa đêm UTC theo đúng
  thời gian biểu — không kéo dài cho đủ 10 tiếng).
- Loop chạy song song, không đụng code/dữ liệu Polymarket & PaperDesk.

## 1. Đã làm được gì, từng chặng

- **Chặng 1 (14:22–14:39Z, xong sớm):** đo nguồn. publicnode = getLogs OK (range tối đa 50k block,
  bắt buộc có địa chỉ, UA python bị 403 → dùng UA curl chuẩn). mainnet.base.org: 429 cả 2 lần getLogs
  → loại khỏi getLogs. meowrpc không hỗ trợ getLogs. V4 PoolManager (địa chỉ canonical) im lặng.
  Trả lời 3 câu coordinator (ghi trong checkpoint 14:39Z). Chốt: discovery W1 = publicnode getLogs
  PoolCreated trên 3 factory cổ điển + epoch 21 ngày đóng băng TRƯỚC khi lấy pool (step0 mục 7).
- **Chặng 2 (14:39–14:55Z, xong sớm):** discovery 57 chunk getLogs. RAW 150 PoolCreated →
  vũ trụ 123 pool (toàn pancakev3; E1=83, E2=27, E3=13 — mọi epoch < 200 tín hiệu).
- **Chặng 3 (15:12–15:44Z):** giá (Swap logs 24h đầu/pool): **0/123 pool có lấy một swap nào**
  (mỗi pool chỉ 2-3 sự kiện Initialize/Mint → pool chết ngay khi sinh). Mẫu gas thật: 0 (không pool
  nào có swap để lấy receipt — thiếu dữ liệu chi phí gas, đúng luật phải ghi thế). Đối chiếu nội suy
  block→thời gian bằng block thật ở E1: sai số 0 giây. Pha ví (Transfer logs 123/123, 1 lỗi đơn lẻ
  "query exceeds max results" bỏ sót 1 token spam): **414 ví duy nhất**, 629 cặp (pool, ví).
  Sự cố giữa chặng: bug `_save_daily` làm mất guard trần ngày (đã sửa + đồng bộ lại từ request_log,
  ghi checkpoint 15:12Z; thực tế không vượt trần nhờ pacing 15s).
- **Chặng 4 (xong sớm):** spec W1 NHÁP viết xong (chưa hash, chưa backtest): `wave01_new_listing_early_buy/spec_v1_DRAFT.md`.
  Bộ máy backtest (phí/anti-lookahead/bootstrap gom theo token/cổng 3 tầng/chọn 1 tham số) test trên
  dữ liệu giả có đáp án biết trước: **15/15 PASS** (`data/w1_base/synth_test_report.md`).
  W1 trạng thái dữ liệu: **CHƯA ĐỦ BẲNG CHỨNG (thiếu dữ liệu)** — 3 chân bằng chứng: (a) 123 pool
  < 200/epoch; (b) 100% pool không có giá (tỷ lệ bỏ >30% của cổng T1); (c) thiên lệch nguồn 3-factory
  đã ghi (pool mới Base thật đang ở các dex/launchpad mới không enumerate được không-key).
- **Chặng 5 (15:47Z đóng băng W2 + mô tả; 00:01-00:05Z GT đo lại):** đóng băng vũ trụ W2 TRƯỚC khi
  đọc bảng tổng hợp ví; mô tả W2 sơ bộ từ dữ liệu ví đã thu. GT đo lại đúng 3 call sau nửa đêm UTC:
  **cả 3 trả 200-rỗng, kể cả câu đối chứng `day?limit=10` từng có nến hôm 2026-11-02 13:41Z** →
  GT đang chặn mềm máy/IP này; GT OHLCV không dùng được cho các phiên sau (không tạo key, không VPN —
  đúng ranh giới). Chi tiết: `data/gt_retest_2026-11-03.json` + checkpoint 00:02Z.

## 2. Số request đã dùng từng nguồn + lỗi (từ logs/request_log.csv, ngày UTC 2026-11-02)

| Nguồn | Số call ghi trong log | Lỗi | Ghi chú pacing |
|---|---|---|---|
| base_pubnode (publicnode.com) | 324 | 0 | 15 giây/call suốt loop |
| base_rpc (mainnet.base.org) | 7 | 2× 429 (getLogs) | 12-25 giây/call; ngừng dùng getLogs sau 2 lỗi |
| base_meow | 2 | 0 (không hỗ trợ getLogs → loại) | 15 giây/call |
| DexScreener | 7 | 0 | 1.5 giây/call |
| GeckoTerminal | 18 (phiên khởi động, trước loop) + **3 (00:01-00:02Z 2026-11-03, cuối loop)** | 1× 429, 3× 401, 2× 400 (bug script ta), 1× 404 (phiên khởi động); 3 call cuối: 200-rỗng (chặn mềm) | Tạm dừng đúng cam kết tới 2026-11-03T00:00Z; 3 call đo lại đúng lúc 00:01Z, cách ≥10 giây |
| solana/arbitrum/bsc RPC | 1 mỗi nguồn | 0 | probe phiên khởi động |

Không lần nào tăng tốc bù; không đổi endpoint CÙNG NHÀ để lách (việc thêm publicnode/meow là nguồn
MỚI độc lập, ghi minh bạch trong budget_config + checkpoint, sau khi mainnet.base.org từ chối getLogs).

## 3. Dữ liệu đã có

- **Số pool:** 123 (vũ trụ W1, kèm raw 150 PoolCreated; địa chỉ đầy đủ chỉ nằm trong data/ nội bộ).
- **Số nến giá:** 0 nến chuẩn; dữ liệu giá thô = 0 swap/123 pool trong 24h đầu.
- **Số ví:** 414 ví duy nhất (629 cặp pool-ví) — từ Transfer logs 24h đầu của 123 base token.
- **Epoch phủ:** E1/E2/E3 = 7 ngày liền nhau, block [52513088→53420288], ≈ 2026-10-12T14:32Z → 2026-11-02T14:32Z.
- **Đoạn còn thiếu:** toàn bộ pool mới của các dex mới (bankr/hydrex/treble/…) — không nguồn không-key nào
  enumerate được trong loop (GT chặn trang sâu + tạm dừng tới 00:00Z; publicnode yêu cầu địa chỉ).

## 4. Trạng thái W1 / W2

- **W1** = CHƯA ĐỦ BẲNG CHỨNG (thiếu dữ liệu; chưa verdict SỐNG/CHẾT vì chưa từng backtest — đúng luật).
  Spec nháp: `wave01_new_listing_early_buy/spec_v1_DRAFT.md` (không hash — hash chỉ khi đóng băng thật).
  Điều kiện đi tiếp: nguồn vũ trụ đầy đủ — đường GT đã ĐÓNG (chặn mềm, xác nhận 00:01Z 2026-11-03);
  còn: thu thập RPC dài hạn qua nhiều ngày, hoặc indexer công khai khác khi tìm được. Khi có dữ liệu:
  copy spec → đóng băng → hash → backtest theo đúng cổng.
- **W2** = vũ trụ tiêu chí đã đóng băng lúc **15:47Z** (`wave02_wallet_overlap/step0_universe.md`),
  mô tả sơ bộ từ 414 ví (`wave02_wallet_overlap/step1_describe_prelim.md`): phân phối cực lệch
  (median 1 lệnh/ví, max 1.631 — bot), 63 ví ≥2 pool, 4 ví cờ tần suất >200 lệnh/24h; và phát hiện
  cấu trúc quan trọng: 0/123 pool có swap nên KHÔNG tồn tại trường hợp "nhiều ví độc lập cùng MUA
  QUA POOL trong 24h" trên tập dữ liệu hẹp này. Chưa có spec, chưa backtest (đúng giới hạn chặng 5).

## 5. Xác nhận bằng chữ

Tôi xác nhận trong loop 10 tiếng này: **chưa chạy lệnh thật nào; chưa backtest trên dữ liệu thật;
chưa tuyên bố verdict SỐNG/CHẾT cho cơ chế nào; chưa áp dụng cơ chế nào vào PaperDesk hay Polymarket;
không tạo tài khoản, không dùng key mới, không tìm/luu private key; mọi địa chỉ đầy đủ chỉ nằm trong
data/ nội bộ.** Loop dừng tại đây, chờ kiểm toán độc lập cho báo cáo này + lệnh GO riêng của chủ nhân
cho mọi bước tiếp theo.
