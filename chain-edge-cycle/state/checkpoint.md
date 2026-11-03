# CHECKPOINT — đọc file này đầu tiên khi tiếp tục cycle

Cập nhật lần cuối: **2026-11-02 (phiên khởi động)** — wave đang chạy: **W1, bước 0**.

## 1. Đã làm tới đâu

- [x] Dựng cây thư mục `chain-edge-cycle/` (tách khỏi PaperDesk/Polymarket — không đụng gì vào đó).
- [x] `00_CHARTER.md`: hiến pháp đầy đủ (ranh giới cứng, cổng giết 3 tầng, epoch, freeze/hash,
      kiểm toán độc lập, bảng 3 hộp, ngân sách, hàng đợi wave W1-W7).
- [x] `tools/fetch_common.py` + `budget_config.json`: mọi request đều qua đây — log CSV, nghỉ tối thiểu,
      trần ngày, 429/403 khóa API + ghi `logs/rate_events.log`. `discover_new_pools.py` viết sẵn (resume được).
- [x] Kiểm kê API key trên máy: **KHÔNG có key dữ liệu nào** (không .env, biến môi trường chỉ có của
      ZCode harness, không liên quan). → cycle chạy 100% nguồn công khai không-key.
- [x] Probe nguồn (2026-11-02): DexScreener OK; Solana/Base/Arbitrum/BNB RPC OK;
      `eth.llamarpc.com` CHẾT (connection refused) — khi tới lượt Ethereum phải tìm RPC công khai khác.
- [x] `wave01/step0_universe.md`: **TIÊU CHÍ VŨ TRỤ ĐÃ ĐÓNG BĂNG** (trước khi kéo bất kỳ nến nào):
      pool_created_at trong epoch, quote ∈ {USDC, USDbC, WETH} (base), dedupe theo base token,
      không lọc survivor. Epoch chưa điền (chờ đo sâu dữ liệu — mục 7 của file đó).

## 2. Phát hiện dữ liệu quan trọng hôm nay (chi tiết trong step0 phụ lục)

1. **GT new_pools bị chặn trang sâu**: page 1-10 OK, page ≥ 30 → 401. Chỉ quay lại được vài giờ
   → KHÔNG đủ làm vũ trụ 21-42 ngày bằng GT new_pools.
2. **GT OHLCV có ngưỡng limit ẩn**: `day?limit=10` có nến; `limit≥100` (hour/day) → 200 rỗng.
   `before_timestamp` chưa đo được. **Phải đo lại 2026-11-03.**
3. **Solana**: ~38.400 pool/ngày trên new_pools (đa số pump-fun) → dự kiến **Box 3** cho Solana ở W1.
4. Sự kiện: 429 lúc 13:41 UTC (Retry-After=0) — đã dừng theo luật, giảm tốc GT xuống 10s/call,
   cap 1200/ngày; 401 trang sâu lúc 13:45-13:47; 2 lần 400 lúc 13:41 là **bug đảo tham số của tôi**
   (đã ghi rõ, không đổ cho GT).
5. **GT đã DỪNG HẲN TỚI 2026-11-03** theo cam kết cuối phiên.

## 3. Usage ngày 2026-11-02 (từ logs/request_log.csv)

| API | Gọi | Lỗi |
|---|---|---|
| geckoterminal | 22 | 1× 429, 3× 401, 2× 400 (bug của ta), 4× 200-rỗng |
| dexscreener | 2 | 0 |
| RPC (solana/base/arbitrum/bsc) | 4+1 lần đầu probe | 0 (eth_rpc chết) |

## 4. Chạy tiếp từ đâu (phiên sau, theo thứ tự)

1. **Đo lại GT (chậm, 3 call)**: `day?limit=10` (đối chứng) → `hour?limit=10` → `day?limit=100`.
   - Nếu `hour?limit=10` có nến → thử `hour?limit=10&before_timestamp=<cũ nhất>` 1 call → biết cách
     phân trang. Ghi kết quả vào step0 phụ lục.
   - Nếu đối chứng cũng rỗng → GT đang soft-throttle ta: nghỉ GT 24h, lấy danh sách pool trước.
2. **Đo Base RPC getLogs**: 1 call `eth_getLogs` sự kiện `PoolCreated` (Uniswap V3 factory
   `0x1F98431c8aD98523631AE4a59f267346ea31F984`) range 50k block gần nhất → biết giới hạn range
   và mức độ phát sinh pool. Nếu OK: đo tiếp Aerodrome factory `0x420DD381b31b62cF37E8F6CC62c9a7757CE5A312`
   và PancakeSwap V3 factory (Base) — xác định factory nào nuôi nhiều pool mới nhất.
3. Quyết định nguồn discovery (GT nếu magically sâu, hoặc RPC logs) → **điền epoch vào step0 mục 7**
   (vẫn trước khi kéo nến) → chạy discovery → bước 1 mô tả.
4. Nếu mọi đường đều tịt: W1 ghi **CHƯA ĐỦ BẰNG CHỨNG (thiếu dữ liệu)**, solana+base Box 3, sang W2
   (overlap ví độc lập) — KHÔNG hạ ngưỡng, không đổi spec theo kết quả.

## 5. File cần nhớ

- Hiến pháp: `00_CHARTER.md` (đọc lại trước khi làm bất cứ gì).
- Vũ trụ W1 đã đóng băng: `wave01_new_listing_early_buy/step0_universe.md` (+ phụ lục đo dữ liệu).
- Luật request: `tools/fetch_common.py` — MỌI call phải qua đây, không curl tay.
- Bảng 3 hộp: `state/box_table.md` (cả 3 hộp đang trống — đúng, vì chưa wave nào xong hết).

## LOOP 10 TIẾNG — bắt đầu 2026-11-02T14:22:30Z (kết thúc muộn nhất 2026-11-03T00:22:30Z)

- T0=2026-11-02T14:22:30Z. Chặng 1 bắt đầu ngay. GT còn trong thời gian dừng tới 2026-11-03T00:00Z (nửa đêm rơi vào giờ thứ 9.6 của loop → 3 call đo lại GT sẽ chạy ở chặng 5).

## 6. Phiên ĐÊM 2026-11-02 (bắt đầu 14:20:42Z, giới hạn 10 tiếng tới 00:20:42Z 2026-11-03)

- Sự kiện: **base_rpc dính 429 lúc 14:23:44Z** (Retry-After=None) từ 4 call liên tiếp KHÔNG phải do agent đêm
  (tiến trình ngoài — log `logs/request_log.csv`; chỉ có ops_service của PaperDesk đang chạy, không liên quan).
  Theo luật §1.7: nguồn base_rpc NGHỈ, không retry ngay. Counter sửa lại base_rpc=5/150 theo log thực tế.
- Polymarket v2 đêm nay DỪNG ở Việc 1 (đã push GitHub commit d62dc6f + tự kiểm toán không lệch) —
  thiếu (a) lệnh GO có điều kiện bằng văn bản, (b) văn bản kiểm toán coordinator. Không đóng băng v2.
- Kế hoạch blockchain đêm (chỉ mô tả + discovery, KHÔNG backtest):
  1. 18:05Z — cron chạy `tools/w1_night_rpc.py` (sau ~3,5h giải lao base_rpc): probe eth_blockNumber →
     UniV3 getLogs range 50k→10k→2k → Aerodrome no-topic 2k (đo chữ ký sự kiện thực nghiệm, không đoán) →
     tính D theo ngân sách → nếu D≥21: điền epoch §7 step0 (đúng luật đóng băng) → discovery getLogs
     (tối đa 60 call đêm) ghi raw `data/rpc/base/univ3_poolcreated_*.jsonl` + state/night_w1_rpc.json.
     429 lần nữa → DỪNG nguồn cả đêm, ghi Box 3 dự kiến, không hạ ngưỡng.
  2. 00:05Z 2026-11-03 — cron chạy `tools/gt_recheck.py` (GT hết lệnh dừng): đúng 4 call §4.1
     (day?limit=10 → hour?limit=10 → hour?limit=10&before_timestamp → day?limit=100), nghỉ ≥10s,
     kết quả vào `state/gt_recheck_20261103.json` + night_log.
  3. 00:20:42Z — hết 10 tiếng: báo cáo sáng, không tự gia hạn.
- Script mới: `tools/w1_night_rpc.py`, `tools/gt_recheck.py` (đều test khô --dry-run xong, mọi call qua fetch_common).
- KHÔNG kéo nến OHLCV nào trong đêm (GT còn dừng; giá chờ kết quả đo lại 00:05Z) — đúng luật "điền epoch
  trước khi kéo nến".

### Chặng 1 (14:22:30Z → 14:39Z) — KẾT THÚC SỚM sau 17 phút (hạn của chặng: 15:22Z). SỬA 2026-11-02: bản trước ghi sai 'kết thúc 16:05Z, cắt chặng vì quá giờ' — sai đồng hồ ghi chép của agent, không có việc cắt chặng; chặng 1 xong sớm.

**3 câu của coordinator — đáp án:**
1. *Nguồn con số Solana ~38.400 pool/ngày?* Đo từ GT `new_pools?page=1` (solana) lúc 13:40Z ngày 2026-11-02: 20 pool trải trên 45 giây (13:37:01Z→13:37:46Z) → 20/(45/3600)≈1.600/giờ ≈ 38.400/ngày. Giới hạn: mẫu 1 trang, cửa sổ 45 giây, đa số dex id 'pump-fun' (bonding curve, chưa hẳn pool DEX) → là ước lượng cấp độ lớn, không phải điều tra dân số.
2. *Tham số OHLCV nào chạy?* Chạy được: `day?limit=10` (có nến, đo 13:41Z). Trả 200-rỗng: `hour|day` với `limit>=100`. `aggregate`/`currency` CHƯA kết luận được (2 lần 400 hôm đó là bug đảo tham số của script test, đã ghi). `before_timestamp` chưa đo được (GT tạm dừng tới 2026-11-03T00:00Z; sẽ đo 3 call chậm ở chặng 5).
3. *Kết quả test getLogs Base?* publicnode (base-rpc.publicnode.com): getLogs OK, range tối đa 50.000 block, BẮT BUỘC có địa chỉ (topics-only bị từ chối); UA python-urllib bị 403, UA curl chuẩn đi được. meowrpc: không hỗ trợ getLogs. mainnet.base.org: 429 cả 2 lần thử getLogs (metadata OK) → bỏ không dùng getLogs (2/3 lỗi). llamarpc: chết phía nhà cung cấp (525).

**Quyết định nguồn discovery W1 (chặng 1):** publicnode getLogs `PoolCreated` trên 3 factory cổ điển (univ3, aerodrome, pancakev3), epoch 21 ngày đã đóng băng trong step0 mục 7 TRƯỚC khi lấy pool. Biết trước vũ trụ sẽ rất nhỏ (pancakev3 ≈2 pool/ngày, 2 factory kia ≈0) → chạy để CÓ SỐ LƯỢNG + dựng pipeline, W1 tối đa được verdict "CHƯA ĐỦ BẰNG CHỨNG (thiếu mẫu)". GT (trang sâu bị chặn + tạm dừng) và DS (không duyệt lịch sử) tịt cho vũ trụ 21 ngày không thiên lệch; các dex mới (bankr, hydrex, treble…) không enumerate được không-key trong loop này. V4 PoolManager (0x000…4444c) trên Base: 0 log/2000 block — im lặng.

**Request đã dùng (đến 14:39Z, theo request_log.csv):** publicnode 26, base_rpc(mainnet) 7 (trong đó 2 getLogs 429), DexScreener 7, GT 0. Chi tiết: logs/request_log.csv.

### Checkpoint chặng 2 (14:43Z)
- Discovery đang chạy nền: univ3 XONG 19/19 chunk (0 pool mới — khớp đo chặng 1), aerodrome + pancakev3 đang chạy (~19 chunk mỗi cái, 15s/call). Tổng dự kiến ~57 call publicnode.
- Bộ máy backtest đã test dữ liệu giả: **15/15 PASS** (data/w1_base/synth_test_report.md).
- spec W1 NHÁP đã viết: wave01_new_listing_early_buy/spec_v1_DRAFT.md (không hash, không backtest thật — chờ vũ trụ đầy đủ).
- Chặng 3 (giá/ví) sẽ chạy SAU khi discovery xong (luật: không 2 đợt API cùng lúc trên một nguồn).
- Chưa chạm dữ liệu thật nào để tính lãi/lỗ — đúng luật (spec chưa đóng băng).

### Chặng 2 HOÀN THÀNH (14:55Z) — discovery W1
- RAW PoolCreated trong epoch 21 ngày (3 factory): 150. Bỏ quote ngoài bộ: 26; trùng base token: 1.
- UNIVERSE = 123 pool, toàn bộ pancakev3 (univ3/aerodrome ≈ 0 pool mới — khớp đo chặng 1).
  Theo epoch: E1=83, E2=27, E3=13. Theo quote: USDC 117, WETH 6.
- **Mọi epoch < 200 → thiếu mẫu cho cổng T1: ĐÃ CÓ SỐ CHỨNG MINH** (không phải khẳng định suông).
- File: data/w1_base/universe.csv, universe_raw.csv; raw chunk ở data/rpc/pool_created/.
- Chặng 3 pha GIÁ đang chạy nền (123 pool, Swap logs 24h đầu + decimals + ≤12 receipt gas mẫu).
- publicnode đã dùng ~83/400. Sau pha giá sẽ chạy pha VÍ (60 pool đầu để nằm trong trần).
- [giá 2026-11-02T14:55:15+00:00] pool 10/123; publicnode đã dùng 0/400 hôm nay
- [giá 2026-11-02T14:57:46+00:00] pool 20/123; publicnode đã dùng 0/400 hôm nay
- [giá 2026-11-02T15:00:17+00:00] pool 30/123; publicnode đã dùng 0/400 hôm nay
- [giá 2026-11-02T15:02:45+00:00] pool 40/123; publicnode đã dùng 0/400 hôm nay
- [giá 2026-11-02T15:05:17+00:00] pool 50/123; publicnode đã dùng 0/400 hôm nay
- [giá 2026-11-02T15:07:50+00:00] pool 10/123; publicnode đã dùng 135/400 hôm nay
- [giá 2026-11-02T15:07:50+00:00] pool 20/123; publicnode đã dùng 135/400 hôm nay
- [giá 2026-11-02T15:07:50+00:00] pool 30/123; publicnode đã dùng 135/400 hôm nay
- [giá 2026-11-02T15:07:50+00:00] pool 40/123; publicnode đã dùng 135/400 hôm nay
- [giá 2026-11-02T15:07:50+00:00] pool 50/123; publicnode đã dùng 135/400 hôm nay

### Checkpoint 15:12Z — sửa bug ngân sách (quan trọng cho kiểm toán)
- Phát hiện bug fetch_common: `_save_daily` mất khóa ngày → bộ đếm ngày tự reset ~1, guard trần CHẾT trong khi chạy. Thực tế đã dùng theo request_log.csv (nguồn sự thật, mọi call đều log): publicnode 135/400 lúc 15:12Z — CHƯA vượt trần; pacing 15s/call vẫn đúng nên không có việc gọi dồn.
- Đã: dừng task giá, sửa `_load_daily`/`_save_daily` (giữ cấu trúc {"ngày": {api: n}}), đồng bộ lại bộ đếm từ request_log.csv, chạy lại pha giá (resume từ file cache — không lấy lại pool đã có).
- Bài học ghi vào charter: đối chiếu daily_counts với request_log định kỳ.
- [giá 2026-11-02T15:08:09+00:00] pool 60/123; publicnode đã dùng 137/400 hôm nay
- [giá 2026-11-02T15:10:39+00:00] pool 70/123; publicnode đã dùng 147/400 hôm nay
- [giá 2026-11-02T15:13:07+00:00] pool 80/123; publicnode đã dùng 157/400 hôm nay
- [giá 2026-11-02T15:15:39+00:00] pool 90/123; publicnode đã dùng 167/400 hôm nay
- [giá 2026-11-02T15:18:12+00:00] pool 100/123; publicnode đã dùng 177/400 hôm nay
- [giá 2026-11-02T15:20:38+00:00] pool 110/123; publicnode đã dùng 187/400 hôm nay
- [giá 2026-11-02T15:23:10+00:00] pool 120/123; publicnode đã dùng 197/400 hôm nay

### Checkpoint 15:55Z — chặng 2/3/4/phần đầu chặng 5 HOÀN THÀNH (xong sớm, không chờ đủ giờ)
- Dữ liệu cuối: 123 pool vũ trụ; 0/123 có swap (100% thiếu giá — pool chết ngay); 414 ví từ Transfer logs (1 token spam lỗi >20k kết quả, bỏ sót 1 pool); gas mẫu = 0 (thiếu dữ liệu chi phí gas, ghi đúng luật).
- W2: step0 ĐÓNG BĂNG 15:47Z (trước khi đọc tổng hợp ví; lộ con số 414 in ra màn hình trước đó — đã khai minh bạch trong file); step1 mô tả sơ bộ xong.
- Bảng 3 hộp + wave_log đã cập nhật (W1 = đề xuất Box 3 chờ kiểm toán; W2 = bước 0-1 xong).
- Báo cáo loop gần hoàn thiện: loop10h_report_2026-11-02.md (còn chừa: kết quả 3 call GT + giờ kết thúc).
- CÒN DUY NHẤT: 3 call GT đo lại sau 2026-11-03T00:00Z — đã lập cron một lần (00:01Z = 07:01 giờ máy) chạy tools/gt_retest.py + hoàn thiện báo cáo + DỪNG. Không việc gì khác chạy tự động.
- Nếu đọc checkpoint này mà cron chưa chạy/chạy lỗi: chạy tay `python3 tools/gt_retest.py` (chỉ khi đã qua 00:00Z UTC) rồi tự điền 2 chỗ trống trong loop10h_report và dừng — KHÔNG làm gì hơn.

### Kết quả đợt 18:06Z (cron đêm)
- base_rpc: `eth_blockNumber` OK (head=53.426.727, 18:06:42Z); `eth_getLogs` UniV3 range 50k → **429 thứ 2 trong ngày** (18:07:04Z, Retry-After=None) → nguồn DỪNG HẲN cho đêm theo luật, không retry, không đổi endpoint.
- Range/Aerodrome/D/epoch/discovery: KHÔNG đo được đêm nay. W1 giữ "đang đo nguồn"; nếu nguồn còn chặn tiếp → dự kiến Box 3 cho Base (giới hạn nguồn, không phải kết quả), Solana đã dự kiến Box 3 → W1 có nguy cơ CHƯA ĐỦ BẰNG CHỨNG (thiếu dữ liệu) cả hai chuỗi.
- Sáng kiến nghị: thử RPC Base công khai khác (không đổi tiêu chí, chỉ đổi endpoint nguồn — phải ghi vào nhật ký ngân sách charter mục 8 vì là thay đổi nguồn), hoặc để GT (nếu đo lại 00:05Z qua được) gánh discovery. KHÔNG quyết đêm nay.

- [GT đo lại 2026-11-03T00:02:00+00:00] day_limit10=0; hour_limit10=0; day_limit100=0

### Chặng 5 hoàn tất — GT đo lại 00:01:34Z → 00:02Z (loop kết thúc)
- day?limit=10 (ĐỐI CHỨNG): 200 + 0 nến — cùng query này CÓ nến hôm 2026-11-02 13:41Z.
- hour?limit=10: 200 + 0 nến. day?limit=100: 200 + 0 nến.
- DIỄN GIẢI: vì đối chứng cũng rỗng, không thể kết luận gì về hour hay ngưỡng limit —
  vấn đề là **GT chặn mềm (200-rỗng) theo máy/IP** sau loạt 429/401 hôm 2026-11-02.
  GT OHLCV KHÔNG dùng được cho các phiên sau trừ khi nhà cung cấp bỏ chặn hoặc có nguồn thay thế.
- Hệ quả cho W1: đường "chờ GT" đã ĐÓNG → trường hợp Box 3 của W1 càng vững
  (chỉ còn đường thu thập RPC dài hạn qua nhiều ngày hoặc indexer khác — ngoài loop này).

### Kết quả đợt 00:05Z 03-11 (task nền agent đêm)
- GT rỗng toàn bộ (kể cả đối chứng day?limit=10) — trùng phép đo độc lập 00:01Z của agent loop 10h → GT NGHỈ 24h tới 2026-11-04.
- Agent loop 10h (14:27–15:55Z, nguồn base_pubnode/base_meow riêng) đã: discovery 3 factory → 123 pool, 0/123 swap-24h, 414 ví; W1 ĐỀ XUẤT Box 3 chờ kiểm toán; W2 bước 0 đóng băng + mô tả sơ bộ. Xem wave_log.md + box_table.md.
- Phiên đêm KẾT THÚC 00:10Z 03-11 (xong sớm, trong hạn 10 tiếng). Sáng cần chủ nhân: kiểm toán Box 3 W1, quyết nghỉ GT/đổi hướng W2.
