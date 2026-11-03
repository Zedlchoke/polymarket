# WAVE 1 — BƯỚC 0: VŨ TRỤ (phần vũ trụ đóng băng TRƯỚC khi xem dữ liệu giá)

- Cơ chế W1: **Mua sớm token mới niêm yết trên DEX, bán sau thời lượng cố định theo luật.**
- File này đóng băng **phần vũ trụ** (cách chọn pool). Spec vào/ra/chi phí/epoch đóng băng riêng ở
  bước 2 (sau khi có mô tả bước 1), hash trước khi backtest.
- **Thời điểm đóng băng vũ trụ: 2026-11-02, TRƯỚC khi kéo bất kỳ cây nến OHLCV nào hoặc tính bất kỳ
  số lãi/lỗ nào.** File này không chứa và không được hiệu chỉnh theo bất kỳ kết quả giá nào.
  Dữ liệu đã nhìn tới thời điểm đóng băng: CHỈ metadata cấu trúc từ trang 1 `new_pools`
  (số pool/trang, danh sách trường, mật độ pool/ngày, tên cặp) — không có tính toán lãi/lỗ.

## 1. Chuỗi của wave này

Xử lý **độc lập, hai báo cáo chuỗi riêng**, không trộn PnL:

| Chuỗi | Điều kiện tham gia (đo bằng DỮ LIỆU, không bằng hiệu suất) | Kết quả đo 2026-11-02 |
|---|---|---|
| base | new_pools phân trang được ≥ 21 ngày liên tục trong ngân sách; dự kiến ≥ 200 pool thỏa tiêu chí trong đoạn chọn | Mật độ ~493 pool/ngày → khả thi, chờ đo độ sâu `page=` |
| solana | như trên | Mật độ ~38.400 pool/ngày (đa số pump-fun) → vượt hạn mức lấy vũ trụ không thiên lệch → **dự kiến Box 3** (ghi rõ: hạn mức API công khai, không phải kết quả xấu). Xác nhận lại sau đo `page=` |

Không chuỗi nào đạt → W1 dừng với verdict CHƯA ĐỦ BẰNG CHỨNG (thiếu mẫu), không hạ ngưỡng.

## 2. Nguồn phát hiện vũ trụ

GeckoTerminal public API (không key): `GET /networks/{base}/new_pools?page=N`, N tăng dần từ 1.

- Dừng khi: `pool_created_at` cũ nhất của trang < đầu epoch E1, HOẶC hết dữ liệu/trang lặp,
  HOẶC chạm trần request phiên (script tự dừng theo luật ngân sách).
- Lưu raw JSON mỗi trang vào `data/gt/new_pools/base/page_XXXXX.json` (giữ nguyên toàn bộ, để tái hiện).
- Extract CSV **chỉ gồm trường cấu trúc**: `pool_address, quote_symbol, base_token_address,
  pool_created_at_utc, page, discovered_at_utc, dex_id`. **KHÔNG trích price/volume/reserve** vào file
  vũ trụ (chống thiên lệch khi chọn). Các trường giá trong raw page CHỈ được dùng ở bước 1+ (mô tả),
  không được dùng để quyết định pool nào thuộc vũ trụ.

## 3. Tiêu chí pool thuộc vũ trụ (đóng băng)

1. `pool_created_at` nằm trong [đầu E1, cuối E3].
2. Quote token thuộc: **base: {USDC, USDbC, WETH}** (lọc theo tên cặp `XXX / QUOTE`).
3. Mỗi base token: chỉ tính **pool ĐẦU TIÊN** theo `pool_created_at` (dedupe theo base token).
4. KHÔNG có tiêu chí nào dựa trên giá/khối lượng/kết quả sau listing. Token chết, rug, honeypot
   **ở lại trong vũ trụ**; việc không thể thoát được mô hình hóa ở spec (phân loại "bỏ vì thiếu giá/
   thanh khoản" và stress-test honeypot), không lọc survivor.

## 4. Loại cấu trúc (tương đương "ví rác" ở cơ chế theo ví) — nhìn được TẠI THỜI ĐIỂM listing

| Loại | Quy tắc | Ghi nhận |
|---|---|---|
| Pool trùng base token | giữ pool đầu theo `pool_created_at` | đếm số bị bỏ |
| Quote ngoài bộ cho phép | bỏ | đếm số bị bỏ |
| Không nến giờ nào sau creation | KHÔNG bỏ khỏi vũ trụ → phân loại "bỏ vì thiếu giá" (vào tử số tỷ lệ bỏ của cổng T1) | đếm |

## 5. Gộp cụm (tương đương "gộp ví cùng người")

Không có dữ liệu deployer/creator không-key → **không gộp được theo người tạo token**. Ghi là thiếu
dữ liệu. Hệ quả: đơn vị gom của cổng T2 là **token** (đúng luật "gom theo token hoặc sự kiện").

## 6. Cỡ mẫu tối thiểu (không hạ ngưỡng)

- E1 (đoạn chọn/kiểm tra cấu trúc): ≥ 200 pool thỏa tiêu chí.
- E2 (đoạn trong mẫu): ≥ 200 tín hiệu thực thi được.
- E3 (holdout): ≥ 200 tín hiệu.
- Không đạt ở chuỗi nào → chuỗi đó verdict **CHƯA ĐỦ BẰNG CHỨNG (thiếu mẫu)**; không kéo dài wave quá hạn.

## 7. Epoch (điền NGAY SAU khi đo xong độ sâu phân trang — vẫn TRƯỚC khi kéo nến)

- E1 = [____-__-__T00:00:00Z, ____-__-__T00:00:00Z) — chọn cấu trúc vũ trụ
- E2 = [____-__-__T00:00:00Z, ____-__-__T00:00:00Z) — trong mẫu, tối ưu đúng 1 tham số chính
- E3 = [____-__-__T00:00:00Z, ____-__-__T00:00:00Z) — holdout, chạy đúng 1 lần
- Quy tắc chia (đóng băng): gọi D = số ngày liên tục quay lại được bằng phân trang.
  - D ≥ 42: 3 đoạn 14 ngày, E3 kết thúc tại thời điểm chạy discovery.
  - 21 ≤ D < 42: 3 đoạn bằng nhau `floor(D/3)` ngày, tối thiểu 7 ngày/đoạn, E3 kết thúc tại discovery.
  - D < 21: chuỗi không đủ điều kiện (Box 3).
- Cả 3 đoạn liền nhau, không chồng lấn, biên tính bằng giây UTC.

### ĐIỀN EPOCH 2026-11-02 (loop 10h, chặng 2) — TRƯỚC khi lấy bất kỳ pool nào

- Nguồn dữ liệu quyết định D: hạn mức thực tế (publicnode getLogs 50k block/range × 3 factory cổ điển
  trong trần 400 call/ngày) → chốt **D = 21 ngày** (nhánh 21 ≤ D < 42: 3 đoạn 7 ngày).
- Mốc neo: block 53420288 = 2026-11-02T14:32:03Z (đo trên publicnode; slope 2.000 s/block đo từ
  2 block cách 43200). Thời gian của block cũ là nội suy tuyến tính — sai số tích lũy có thể tới
  vài phút ở 21 ngày; ghi nhận là ước tính.
- **E1 = block [52513088, 52815488) ≈ [2026-10-12T14:32:03Z, 2026-10-19T14:32:03Z)**
- **E2 = block [52815488, 53117888) ≈ [2026-10-19T14:32:03Z, 2026-10-26T14:32:03Z)**
- **E3 = block [53117888, 53420288) ≈ [2026-10-26T14:32:03Z, 2026-11-02T14:32:03Z)**
- Không đổi epoch sau khi thấy pool. Nếu số pool thỏa tiêu chí < 200/epoch → verdict thiếu mẫu,
  không hạ ngưỡng, không nới epoch.

### Ánh xạ tiêu chí quote từ tên → địa chỉ (bổ sung implementation, tiêu chí không đổi)

- USDC = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 (6 decimals)
- USDbC = 0xd9aAEc86B65D86f6A7B5B1b0c42FFA5337d0d3Fa (6 decimals)
- WETH = 0x4200000000000000000000000000000000000006 (18 decimals)
- Pool thuộc vũ trụ nếu một trong token0/token1 thuộc bộ trên; token còn lại là base.
  (Tiêu chí gốc "quote ∈ {USDC, USDbC, WETH} theo tên cặp" — ánh xạ địa chỉ là cách kiểm tra
  chặt hơn của cùng một tiêu chí, áp cho nguồn RPC.)

### Phạm vi nguồn discovery (ghi thẳng thắn — quan trọng cho kiểm toán)

- **Chỉ 3 factory cổ điển**: UniswapV3 (0x1F98431c8aD98523631AE4a59f267346ea31F984),
  Aerodrome (0x420DD381b31b62cF37E8F6CC62c9a7757CE5A312), PancakeSwapV3
  (0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865) qua publicnode.
- Đo chặng 1: pancakev3 ≈ 2 pool/ngày, univ3 = 0/27h, aerodrome = 0/27h → vũ trụ này sẽ RẤT NHỎ
  (dự kiến vài chục pool/21 ngày, chủ yếu pancakev3) → gần như chắc chắn thiếu mẫu cho cổng T1.
- Lý do vẫn chạy: (1) đưa ra SỐ LƯỢNG chứng minh thay vì khẳng định suông; (2) dựng pipeline
  giá/ví tái dùng được khi có nguồn dữ liệu đầy đủ; (3) dữ liệu ví này dùng lại cho W2 bước 1
  (mô tả) mà không rò rỉ vũ trụ.
- **Thiên lệch cấu trúc đã biết và ghi nhận**: pool mới trên Base thời 2026-11 phân mảnh ở nhiều
  dex/launchpad mới (GT hôm qua cho thấy dex 'bankr', DS search thấy 'hydrex', 'treble', 'sushiswap',
  'aerodrome', 'uniswap'…) — không có cách nào không-key enumerate toàn bộ chúng trong 10 tiếng
  (GT bị chặn trang sâu + đang tạm dừng tới 2026-11-03; publicnode yêu cầu địa chỉ cho getLogs;
  mainnet.base.org từ chối getLogs; DS không duyệt listing lịch sử). Vũ trụ 3-factory là một
  THƯỚC ĐO THAM KHẢO, không phải vũ trụ đầy đủ của cơ chế. Verdict W1 trong loop này tối đa là
  "CHƯA ĐỦ BẰNG CHỨNG (thiếu mẫu + thiên lệch nguồn đã ghi)", không được cao hơn.

## 8. Hạn wave

Bắt đầu 2026-11-02 → hạn **2026-11-16** (hồ sơ + backtest). Hết hạn chưa đủ mẫu → ghi thiếu mẫu, sang wave khác.

## 9. Câu hỏi dữ liệu đang mở (phải trả lời xong trước khi điền mục 7)

1. `new_pools?page=N` có quay lại quá khứ sâu không? (đang kiểm chứng chậm, sau lỗi 429)
2. OHLCV giờ: `?limit=1000` + `before_timestamp` có phân trang về quá khứ đủ sâu cho pool mới không?
3. Pool mới tạo có nến giờ/phút từ gần thời điểm creation không? (probe đầu bị lỗi param, chưa trả lời được)

---

## PHỤ LỤC 2026-11-02 (cuối phiên khởi động) — kết quả đo dữ liệu, tiêu chí vũ trụ KHÔNG đổi

**Quan trọng:** mục 1-8 ở trên (tiêu chí pool thuộc vũ trụ) giữ nguyên như đã đóng băng.
Phụ lục này chỉ ghi thêm kết quả đo nguồn dữ liệu và đường dự phòng cho **cách lấy danh sách pool**
(đổi bộ fetcher, không đổi tiêu chí — pool thuộc vũ trụ vẫn phải thỏa đúng mục 3).

Kết quả đo (log đầy đủ: `logs/request_log.csv`, `logs/rate_events.log`):

| Câu hỏi | Kết quả |
|---|---|
| Q1: `new_pools?page=` sâu bao nhiêu? | page 1-10 OK; **page 30 và 50 → 401 Unauthorized** → ngưỡng trang ẩn ở (10, 30]; với ~27 phút/trang ⇒ chỉ quay lại được ~3-13 giờ. **Không đủ cho vũ trụ 21-42 ngày.** |
| Q2: OHLCV giờ sâu bao nhiêu? | `day?limit=10` CÓ nến (đo 13:41 UTC); `hour?limit=1000`, `hour?limit=100`, `day?limit=1000` → **200 + payload rỗng** ⇒ nghi ngưỡng `limit` ẩn cho anonymous. `before_timestamp` chưa đo được (dính lỗi gọi nhầm ở lần đầu). Kiểm tra lại 2026-11-03: `day?limit=10` (đối chứng), `hour?limit=10`, `day?limit=100`. |
| Q3: pool mới có nến giờ không? | chưa đo được |
| Solana | `new_pools` trang 1 mật độ ~38.400 pool/ngày (đa số pump-fun bonding curve) ⇒ vũ trụ không thiên lệch không lấy được trong hạn mức ⇒ **duy trì dự kiến Box 3 cho Solana** ở W1 (không phải vì kết quả xấu) |
| Sự kiện lỗi cần nhớ | 429 lúc 13:41 (Retry-After=0); 401 trang sâu lúc 13:45-13:47; 2 lần 400 lúc 13:41 là **bug đảo tham số của script test** (nhãn/query hoán vị làm URL mất `?`) — không phải lỗi của GT |

**Đường dự phòng discovery (không cần key, dự kiến kiểm chứng 2026-11-03):**
danh sách pool mới trên Base lấy bằng `eth_getLogs` sự kiện `PoolCreated` của các factory DEX
(Uniswap V3, Aerodrome, PancakeSwap V3 — địa chỉ factory sẽ ghi vào spec khi đóng băng) qua
Base RPC công khai; block range chia nhỏ theo giới hạn của RPC. Tiêu chí thuộc vũ trụ (mục 3)
áp dụng y hệt lên danh sách này. Nếu RPC cũng không lấy được → W1 ghi thiếu dữ liệu, không hạ ngưỡng.

**Giá cho backtest:** chờ kết quả đo lại OHLCV 2026-11-03. Nếu hour-candle không dùng được:
(i) thử `before_timestamp` với limit nhỏ, (ii) nếu vẫn không được — dựng giá từ chính Swap logs
của từng pool (getLogs theo địa chỉ pool) — đắt hơn nhưng không cần key; quyết định ghi vào spec.

- 2026-11-03T00:05Z (agent đêm, phép đo độc lập với 00:01Z): GT `day?limit=10` (đối chứng) → 200 + 0 nến; `hour?limit=10` → 0 nến; `day?limit=100` → 0 nến → soft-throttle xác nhận lần 2 → GT nghỉ 24h tới 2026-11-04 theo luật đã ghi trước. (base_rpc mainnet.base.org: 429 lần 2 lúc 18:07:04Z 02-11 — nguồn dừng hẳn đêm.)
