# BÁO CÁO THĂM DÒ DỮ LIỆU POLYMARKET — CHỈ ĐỌC, MẪU NHỎ

Ngày: 2026-11-02. Người chạy: agent ZCode (GLM-5.3), theo lệnh của chủ nhân ngày 2026-11-02.
Phục vụ: Giai đoạn B của dự án copy trade 20 tài khoản Polymarket, đối chiếu SPEC v1 nháp (mục 16 — danh sách THIẾU).

**Bản chất của báo cáo:** chỉ ghi nhận dữ liệu và tên trường. KHÔNG kết luận lãi/lỗ. KHÔNG chọn k. KHÔNG chọn 20 ví cuối cùng. KHÔNG tuyên bố đủ hoặc thiếu dữ liệu ngoài phần đo được.

---

## 0. Trạng thái chung

- Tổng cộng **16 request API** (bảng ở mục 9) + 2 lần tải file contract/tài liệu (openapi). Tất cả GET, công khai, không đăng nhập, không key, chi phí 0 đồng.
- **Không gặp HTTP 429 hay 403.** Không có dấu hiệu throttle: độ trễ 352–2.411 ms, không xu hướng tăng (log đầy đủ trong `probe_out/requests.log`). Luật dừng không bị kích phát bởi sàn.
- Luật dừng đã tự kiểm chứng 1 lần ở hướng ngược: lần chạy đầu bị lỗi mạng SSL (CA của Python không đọc được chứng chỉ macOS) → script **DỪNG TOÀN BỘ đúng luật**, ghi checkpoint `ABORTED` 11:13:17Z, không retry. Sau khi sửa đúng chỗ (trỏ CA bundle hệ thống `/etc/ssl/cert.pem`, vẫn xác thực chứng chỉ đầy đủ) mới chạy lại từ đầu 11:13:40Z.
- 1 request trả **HTTP 400** (bước f, cửa sổ 90 ngày) — là lỗi tham số của chính request mẫu, không phải throttle; message lỗi nguyên văn ở mục 6.
- Script thăm dò: `~/Downloads/Polymarket/probe/probe_polymarket.py` (chỉ đọc, nghỉ 5 giây/request, checkpoint bằng timestamp tại `probe_out/checkpoint.json`, watchdog độ trễ).
- Dữ liệu thô: `~/Downloads/Polymarket/probe/probe_out/` (mỗi bước 1 file JSON nguyên bản + `requests.log`).

## 1. Bước a — Contract v2: tên tham số thật (nguồn: file contract, không đoán)

Contract tải về: `https://data-api.polymarket.com/v2/openapi.json` (OpenAPI 3.1.0, "Polymarket Data API v2", version 0.1.0, 21 endpoint). Lưu tại `probe_out/dataapi_v2_openapi.json`. Gamma contract: `https://docs.polymarket.com/api-spec/gamma-openapi.yaml` → `probe_out/gamma_openapi.yaml`.

### Tên tham số đã chốt từ contract v2 (khác v1)

| Chức năng | Endpoint v2 | Tên tham số thật | Ghi chú |
|---|---|---|---|
| Giao dịch theo ví | `GET /v2/trades` | `user`, `taker_only`, `start`, `end`, `limit`, `cursor`, `condition`, `event_id`, `side`, `filter_type`, `filter_amount` | **`taker_only`** (v1: `takerOnly`). Mặc định `true`. `start`/`end` là epoch giây, chỉ có tác dụng khi có `user`. |
| Hoạt động theo ví | `GET /v2/activity` | `user`, `type`, `start`, `end`, `limit`, `cursor`, `sort_by`, `sort_direction`, `exclude_deposits_withdrawals` | `type=TRADE` để lấy giao dịch. |
| Vị thế | `GET /v2/positions` | `user`, `status`, `limit`, `cursor`, `sort_by`, `sort_direction`, `filter_type`, `filter_amount`, `include_archived` | `status` ∈ {OPEN, REDEEMABLE, REDEEMABLE_LOST, MERGEABLE, CLOSED}, mặc định OPEN. |
| Bảng xếp hạng | `GET /v2/leaderboard` | `time_period`, `category`, `sort_by`, `limit`, `cursor` | `time_period` ∈ {day, week, month, all} — **KHÔNG có 90 ngày tùy ý** (đúng lo ngại trong tổng hợp Q3). `category` nhận category Gamma, ví dụ `sports`. `sort_by` ∈ {PNL, VOLUME}. |
| Thống kê ví | `GET /v2/user-stats` | `user` | Chỉ có `user`, không có cửa sổ thời gian. |
| Kết quả chốt | `GET /v2/resolutions` | `condition` (hoặc `question_id`, `event_id`), nhận danh sách phẩy, tối đa 20 | Tồn tại thật trên v2. |
| Lịch sử giá | `GET /v2/prices-history` | `token_id`, `start`, `end`, `interval`, `bucket_seconds`, `as_of`, `limit`, `cursor` | `start` đơn lẻ bị giới hạn 15 ngày; `bucket_seconds` 60–86400. |

### Tên trường trong response (từ contract + đối chiếu response thật)

- `Trade` row: `condition_id`, `token_id`, `outcome_index` (**999 = không gắn nhãn được cửa** — cần xử lý đặc biệt khi tính overlap), `price`, `size` (**cổ phần, không phải USD**), `side` (BUY/SELL theo góc nhìn ví), `timestamp` (**epoch giây**), `proxy_wallet`, `transaction_hash`, `slug`, `event_slug`, `title`.
- `Activity` row: như Trade + `usdc_size` (**chỉ Activity có, Trade KHÔNG có** — xem mục 3), `type`.
- `Position` row: `condition_id`, `token_id`, `outcome_index`, `negative_risk`, `status`, `realized_pnl`, `total_pnl`, `avg_price`, `current_size`, `entry_cost_usdc`, `last_event_at`, `event_id`, `opposite_token_id`, `redeemable`, `mergeable`…
- `Resolution` row: `condition_id`, `payouts` (**micro-USDC/cổ phần, mảng [out0, out1]**: 1.000.000 = 1 USD, 500.000 = 0,5), `status`, `resolved_at` (RFC3339), `resolution_source`, `reporter`, `market_type`, `was_disputed`…
- Phân trang: envelope `{data, pagination}`, `pagination.next_cursor` + `has_more`. `limit` chỉ áp cho trang đầu, cursor giữ nguyên kích thước trang.

## 2. Bước b — Leaderboard SPORTS MONTH → ví mẫu, positions CLOSED, user-stats

Ví mẫu: `0xf0318c32136c2db7fec88b84869aee6a1106c80c` (rank 1, tên BreakTheBank, PNL tháng 6.923.532,27 USD, volume 84.781.015,60 USD — số liệu sàn trả, chỉ ghi nhận).

| # | Endpoint + tham số gửi nguyên văn | Kết quả |
|---|---|---|
| b1 | `https://data-api.polymarket.com/v2/leaderboard?time_period=month&category=sports&sort_by=PNL&limit=5` | HTTP 200, 5 dòng. next_cursor: None, has_more: False (đủ trang). Trường mỗi dòng: pnl, volume, rank, user_id, user_name, verified, x_username, profile_image. |
| b2 | `https://data-api.polymarket.com/v2/positions?user=0xf0318c…6c80c&status=CLOSED&limit=10&sort_direction=DESC` | HTTP 200, 10 dòng (đúng limit). next_cursor: None, has_more: False. `last_event_at` sớm nhất 1.784.501.745 (2026-07-19) / muộn nhất trong trang: 1.789.533.xxx (cuối trang). Dòng mẫu: status=CLOSED, negative_risk=True, realized_pnl=1.409.061,71. |
| b3 | `https://data-api.polymarket.com/v2/user-stats?user=0xf0318c…6c80c` | HTTP 200. Trường trong `data`: all_time_pnl, biggest_win, join_date, proxy_wallet, trades, views. **KHÔNG có volume/lãi theo cửa sổ 90 ngày** — khẳng định lại: muốn khối lượng 90 ngày phải tự tính từ trades (đúng phương án tổng hợp Q3.1). |

## 3. Bước c — Cửa sổ 7 ngày: taker_only true/false, đơn vị timestamp, usdc_size

Cửa sổ: start=1793013231, end=1793618031 (epoch giây UTC; ≈ 2026-10-26 → 2026-11-02).

| # | Request | Kết quả |
|---|---|---|
| c1 | `…/v2/trades?user=0xf0318c…6c80c&taker_only=true&start=1793013231&end=1793618031&limit=100` | HTTP 200, **77 dòng**, next_cursor: None, has_more: False → 77 là TOÀN BỘ lệnh taker của ví trong 7 ngày. timestamp sớm nhất 1.793.054.282 / muộn nhất 1.793.582.404 (epoch giây). BUY=72. |
| c2 | `…/v2/trades?user=0xf0318c…6c80c&taker_only=false&start=1793013231&end=1793618031&limit=100` | HTTP 200, **100 dòng (đầy trang)**, has_more: True, next_cursor: `eyJkYXRhIjp7InR5cGUiOiJ0cmFk…` (còn trang sau) → **taker_only=false tồn tại trên v2 và làm thêm dòng maker**. Trang 1 phủ timestamp 1.793.615.035–1.793.617.954 (~49 phút) → ví này có mật độ fill rất dày khi tính cả maker. |
| c3 | `…/v2/activity?user=0xf0318c…6c80c&type=TRADE&start=1793013231&end=1793618031&limit=100` | HTTP 200, 100 dòng (đầy trang). **`usdc_size` CÓ mặt trên Activity** (mẫu 102,0 USD). |

**Kết luận tên trường cho spec (chỉ về mặt kỹ thuật, không về lãi):**
- Đơn vị thời gian: **epoch giây** ở trades/activity/positions — khớp yêu cầu "tính bằng giây UTC" của tổng hợp.
- `usdc_size` (tiền mặt USD): **KHÔNG có trên `/v2/trades`**, CHỈ có trên `/v2/activity`. Hai đường lấy tiền mặt: (1) dùng `/v2/activity?type=TRADE` có sẵn `usdc_size`; hoặc (2) dùng `/v2/trades` và tự tính `price × size`. Cần chủ nhân/spec chốt 1 trong 2 đường (spec mục 16, dòng 1).
- `taker_only=true` mặc định đúng như tổng hợp lo ngại (giấu phía maker) — phải đặt `false` khi dựng chuỗi vị thế.

## 4. Bước d — 3 mã thị trường trên Gamma (neg-risk, moneyline 2 cửa, đã chốt)

Phát hiện bắt buộc ghi: **Gamma `/markets` mặc định `closed=false` → chỉ trả thị trường đang mở.** Hai lần gọi đầu (d1, d2 dưới) trả `[]` (0 dòng) vì các mã chọn đều đã đóng. Phải gửi `closed=any` khi tra theo identifier. Đây là bẫy dữ liệu lớn nếu không biết: mọi thị trường đã chốt (đoạn 1 của backtest) sẽ "biến mất" nếu quên `closed=any`.

| # | Request | Kết quả |
|---|---|---|
| d1 | `…gamma-api.polymarket.com/markets?condition_ids=0x5116…,0x0256…,0x5116…&limit=10` (join phẩy) | HTTP 200, **0 dòng** — mã đã đóng bị lọc khỏi mặc định. |
| d2 | lặp `condition_ids=` 3 lần (0x0256…, 0x401c…, 0x5116…) | HTTP 200, **0 dòng** — cùng nguyên nhân. |
| d3 | lặp `condition_ids=` 3 lần + **`closed=any`** | HTTP 200, **2 dòng** (2/3 mã tra được; mã 0x401c1614… không trả về — ghi THIẾU, cần tra lại bằng slug/id ở lần thăm dò sau). |

Chi tiết 2 thị trường trả về (d3):

| Trường | Thị trường 1 | Thị trường 2 |
|---|---|---|
| conditionId | 0x0256ef63427ed0d9…c44182074 | 0x51166276fa646ca5…44182074 |
| Câu hỏi | "Will Ghana win on 2026-06-17?" | "Will Spain vs. Argentina end in a draw?" |
| Sự kiện (`events[0].title`) | Ghana vs. Panama | Spain vs. Argentina |
| negRisk | True | True |
| outcomes | ["Yes","No"] | ["Yes","No"] |
| clobTokenIds | có (chuỗi JSON mã hóa) | có |
| volumeNum | 12.677.277,82 | 9.115.515,02 |
| **feeSchedule** | `{exponent: 1, rate: 0.03, takerOnly: true, rebateRate: 0.25}` | `{exponent: 1, rate: 0.05, takerOnly: true, rebateRate: 0.15}` |
| sportsMarketType | moneyline | moneyline |
| gameStartTime | 2026-06-17 23:00:00+00 | 2026-07-19 19:00:00+00 |
| closed / umaResolutionStatus | True / "resolved" | True / "resolved" |
| outcomePrices (đã chốt) | ["1","0"] (chuỗi) | ["1","0"] (chuỗi) |
| tags | **[] rỗng** | **[] rỗng** |

**Xác nhận quan trọng cho Q5 (phí theo ngày):** trường `feeSchedule` tồn tại, cấu trúc `{exponent, rate, takerOnly, rebateRate}`. Hai mẫu đo được: rate **0,03** cho trận 17-06-2026 và **0,05** cho trận 19-07-2026 — **khớp đúng bảng lịch sử phí trong tổng hợp** (0,03 tới tháng 6/2026; 0,05 từ 10-07-2026). Công thức phí của Q5 (số cổ phần × rate × giá × (1−giá), exponent=1) nhất quán với cấu trúc này. **Kết luận kỹ thuật: có thể lấy phí theo từng thị trường đúng luật Q5.5; không cần hardcode.**

**Tên trường thể thao xác nhận được:** `sportsMarketType` (moneyline…), `gameStartTime` (giờ UTC), `events` (gom thị trường con theo sự kiện — phục vụ luật "mỗi sự kiện một lần" của Q4), `negRisk`, `negRiskMarketID`. **THIẾU: `tags` trả rỗng ở 2 thị trường đã đóng này** — chưa xác nhận được bộ giá trị tag thể thao cho thị trường đang mở (cần 1–2 request mẫu ở giai đoạn sau với thị trường còn mở); tạm dùng `sportsMarketType`/`gameStartTime` làm tín hiệu thể thao chính. **THIẾU: không có trường tên `resolutionStatus` như tổng hợp đã viết — trường thật là `umaResolutionStatus`** (giá trị "resolved"); cần sửa tên trường này trong spec trước khi đóng băng.

## 5. Bước e — Resolutions + đối chiếu Gamma + hòa 0,5

| Request | Kết quả |
|---|---|
| `https://data-api.polymarket.com/v2/resolutions?condition=0x51166276fa646ca50165f7d030c297138ed1d62dc41f6ffde21e962c44182074` | HTTP 200, 1 dòng. `payouts=[1000000, 0]` (micro-USDC/cổ phần → cửa 0 trả 1 USD, cửa 1 trả 0). `status=resolved`, `resolved_at=2026-07-19T22:53:46Z` (RFC3339), `resolution_source=reported`. |

- **Đối chiếu Gamma:** cùng mã, Gamma `umaResolutionStatus="resolved"`, `outcomePrices=["1","0"]` → **hai nguồn khớp nhau** ở mẫu này (cửa 0 thắng).
- **Trường hợp hòa 0,5: KHÔNG có trong mẫu** (không có payouts = 500.000). Ghi THIẾU: cần bắt gặp thị trường chốt 0,5 trong mẫu rộng hơn trước khi đóng băng. Cấu trúc `payouts` micro-USDC đã xác nhận là nơi đọc giá chốt đúng nhất (hỗ trợ công thức hòa của Q7: lãi = cổ phần × 0,5 − 100 − phí).
- Ghi chú kỹ thuật: `resolved_at` ở resolutions là RFC3339, KHÔNG phải epoch giây như trades — hai đơn vị thời gian khác nhau trong cùng API, phải quy đổi về giây UTC khi ghép dòng thời gian.

## 6. Bước f — prices-history 7 ngày và 90 ngày, hạt thời gian thực tế

Token dùng: `103502227257868648930155562667494664756217753218326084089472320347435597174870` (lấy từ trades của ví mẫu).

| # | Request | Kết quả |
|---|---|---|
| f1 (7 ngày) | `…/v2/prices-history?token_id=10350…174870&start=1793013244&end=1793618044` | HTTP 200, **1.940 điểm**. Mỗi điểm: `{timestamp, price, resolution_seconds}`. **Hạt thời gian thực tế = 300 giây (5 phút)/điểm** (trường `resolution_seconds` tự khai báo). next_cursor None, has_more False (đủ 7 ngày trong 1 trang, dưới mức trần 10.000 điểm). |
| f2 (90 ngày) | `…/v2/prices-history?token_id=10350…174870&start=1785842044&end=1793618044` | **HTTP 400**, body nguyên văn: `{"error": "'start' to 'end' must span at most 15 days", "code": "invalid_request", "retryable": false}`. |
| f3 (`interval=max`) | `…/v2/prices-history?token_id=80727…1503113&interval=max` (token khác, lấy từ trang trades_maker) | HTTP 200, 13 điểm, span 7,0 ngày, `resolution_seconds` = 43.200 giây (12 giờ/điểm). Token này chỉ có ~7 ngày lịch sử giá. |

**Hệ quả kỹ thuật bắt buộc ghi cho backtest:** cửa sổ prices-history v2 **tối đa 15 ngày/request**. Lịch sử giá 90 ngày (đoạn 1 của timeline) phải gộp từ ≥ 6 request 15 ngày nối nhau (dùng cursor hoặc start/end liền kề), hạt 300 giây nếu trong 15 ngày. Với token đã lâu thì lịch sử đầy đủ; với token mới sinh thì chỉ có từ lúc sinh (f3). **Điều này KHÔNG cản trở việc dựng giá copy theo Q5** vì Q5 dùng giá giao dịch thật (trades), prices-history chỉ dùng kiểm tra/chốt giá — nhưng phải ghi vào spec như ràng buộc thu thập.

## 7. Bước g — ĐẾM MÔ TẢ tốc độ tín hiệu (k=2, k=3), KHÔNG tính lãi

3 ví từ leaderboard sports/month/PNL (rank 1–3), cửa sổ 7 ngày (1793013257 → 1793618057), mỗi ví đúng 1 trang request, `taker_only=false`, `limit=500`, chỉ đếm lệnh BUY:

| Ví | Tên | Dòng trả về | BUY | Số mã thị trường khác nhau | has_more |
|---|---|---|---|---|---|
| 0xf0318c32136c2db7…6c80c | BreakTheBank | 500 (đầy trang) | 462 | 23 | True |
| 0xcdcccd0f2d86e450…cc7935a | joseph00677 | **0** | 0 | 0 | False |
| 0x2a69660046d7acc4…76cd2f7 | UpTheBlues | 500 (đầy trang) | 500 | 117 | True |

- **Số cặp thị trường + cửa có ≥ 2 ví cùng mua trong cửa sổ 24 giờ: 0. Số cặp có ≥ 3 ví: 0.** (Đếm theo cặp `condition_id + token_id` từ lệnh BUY, trượt 24h = 86.400 giây, đúng khung Q4.)
- Giới hạn của phép đo này (phải ghi kèm): (1) chỉ 3 ví, lấy từ top PNL tháng — không phải mẫu ngẫu nhiên của 20 nhóm sau gộp; (2) mỗi ví chỉ 1 trang (has_more=True ở 2 ví → số thật lớn hơn, đây là **cận dưới**); (3) ví rank 2 trả 0 dòng trong 7 ngày — chưa rõ nguyên nhân (có thể `user_id` leaderboard không phải proxy wallet giao dịch của ví đó, hoặc ví nghỉ 7 ngày) — ghi THIẾU, cần đối chiếu `proxy_wallet` khi làm hồ sơ; (4) chưa áp các lọc Q4 (100 USD ròng/nhóm, khối lượng thị trường ≥ 10.000 USD, dải giá 0,10–0,90) nên con số này chỉ là đếm thô.
- **Ước tốc độ tín hiệu (chỉ mô tả):** với mẫu cạn dưới này, tần suất tín hiệu k=2 quan sát được là **0 sự kiện/7 ngày** giữa 2 ví đang hoạt động (23 và 117 mã thị trường). Không ngoại suy được ra 20 nhóm (190 cặp) vì mẫu 3 ví quá nhỏ và 0 sự kiện không có sai số ước lượng. **Theo checklist: chưa đủ dữ kiện để khẳng định 90+90+90 ngày đủ hay thiếu cho 20 nhóm** — cần bước hồ sơ 20 nhóm (Bước 2 của bản nháp gốc, sau khi chủ nhân GO) đo tốc độ tín hiệu thật trên pool rộng hơn, đi chậm theo luật 429.

## 8. Bảng tổng hợp: v1 so với v2, và danh sách THIẾU cập nhật

### Khác biệt tên trường/tham số v1 → v2 đã xác nhận

| v1 / tài liệu cũ | v2 thật (đã chạy) |
|---|---|
| `takerOnly` | `taker_only` (mặc định true) |
| Pagination `/positions?user=&limit=` | envelope `{data, pagination{next_cursor, has_more}}` |
| Gamma `resolutionStatus = resolved` | **`umaResolutionStatus`** (giá trị "resolved"); đồng thời có Data API `/v2/resolutions` với `payouts` micro-USDC |
| Giả định prices-history lấy cả 90 ngày 1 lần | **cửa sổ tối đa 15 ngày/request**, phải ghép ≥ 6 lần |
| Gamma `/markets?condition_ids=` tự hiểu mọi trạng thái | mặc định `closed=false`; phải gửi `closed=any` khi tra mã đã đóng |
| `usdcSize` trên mọi endpoint | `usdc_size` chỉ có trên `/v2/activity`; `/v2/trades` phải tự tính price × size |

### Đối chiếu mục 16 của SPEC v1 nháp — đã xác nhận / còn thiếu

| Mục spec | Trạng thái sau thăm dò |
|---|---|
| 1. Tên trường mã thị trường/cửa/giá/tiền/thời gian | **ĐÃ XÁC NHẬN** (condition_id, token_id, outcome_index [999 = không nhãn], price, size = cổ phần, usdc_size [chỉ activity], timestamp = epoch giây) |
| 2. takerOnly trên v2 | **ĐÃ XÁC NHẬN**: `taker_only`, chạy thật true/false khác nhau (77 vs >100 dòng) |
| 3. Trường thể thao của Gamma | **MỘT PHẦN**: `sportsMarketType`, `gameStartTime`, `events` OK; `tags` rỗng ở 2 thị trường đóng — THIẾU với thị trường đang mở |
| 4. feeSchedule + bảng phí theo ngày | **ĐÃ XÁC NHẬN**: cấu trúc `{exponent, rate, takerOnly, rebateRate}`; đo 0,03 (trận 17-06) và 0,05 (trận 19-07) khớp bảng lịch sử trong tổng hợp |
| 5. Đầu mối resolutions + hòa 0,5 | **MỘT PHẦN**: endpoint + payouts micro-USDC xác nhận, khớp Gamma; **chưa bắt gặp trường hợp 0,5 trong mẫu** |
| 6. Hạt prices-history | **ĐÃ XÁC NHẬN**: 300 giây (cửa sổ 7 ngày), tự co tới 43.200 giây theo span; cửa sổ tối đa 15 ngày |
| 7. Nguồn pool + tham số leaderboard | **ĐÃ XÁC NHẬN tham số**: time_period=month, category=sports, sort_by=PNL/VOLUME; **không có 90 ngày tùy ý** — nguồn pool vẫn là quyết định phải ghi trong spec |
| 8. Spread tại thời điểm kích hoạt | **CHƯA XÁC NHẬN** (không có endpoint spread lịch sử trong contract v2; chỉ có order book hiện tại — cần quyết: bỏ spread, phạt = 0,02 cố định theo Q5.2) |
| 9. Khối lượng thị trường TỚI thời điểm kích hoạt | **CHƯA XÁC NHẬN hoàn toàn**: có volumeNum (tổng cuối) trên Gamma; khối lượng tới thời điểm phải tự cộng dồn từ trades theo thời gian — khả thi trên giấy với chi phí request cao, cần thiết kế ở bước hồ sơ |
| 14. Đơn vị timestamp | **ĐÃ XÁC NHẬN**: trades/activity/positions = epoch giây; resolutions.resolved_at = RFC3339 (phải quy đổi) |
| 10–13 (T0, làm tròn, ưu tiên nguồn chốt, giải lớn) | Vẫn chờ chủ nhân (D1–D5 và 2 quyết định spec) |

## 9. Nhật ký 16 request (nguyên văn, latencies — không có 429/403)

| Tag | HTTP | ms | URL (rút gọn ví/token, bản đầy đủ trong requests.log) |
|---|---|---|---|
| b1_leaderboard | 200 | 515 | /v2/leaderboard?time_period=month&category=sports&sort_by=PNL&limit=5 |
| b2_positions_closed | 200 | 668 | /v2/positions?user=0xf0318c…&status=CLOSED&limit=10&sort_direction=DESC |
| b3_user_stats | 200 | 352 | /v2/user-stats?user=0xf0318c… |
| c_trades_true | 200 | 512 | /v2/trades?user=0xf0318c…&taker_only=true&start=…&end=…&limit=100 |
| c_trades_false | 200 | 541 | /v2/trades?user=0xf0318c…&taker_only=false&start=…&end=…&limit=100 |
| c_activity_trade | 200 | 562 | /v2/activity?user=0xf0318c…&type=TRADE&start=…&end=…&limit=100 |
| d_gamma_markets | 200 | 654 | gamma /markets?condition_ids=…,…,…&limit=10 → 0 dòng (closed mặc định) |
| e_resolutions | 200 | 518 | /v2/resolutions?condition=0x5116… |
| f_prices_7d | 200 | 2411 | /v2/prices-history?token_id=10350…&start=…&end=… (7 ngày) |
| f_prices_90d | **400** | 489 | /v2/prices-history?token_id=10350…&start=…&end=… (90 ngày) — "must span at most 15 days" |
| g_trades ×3 | 200 | 738/460/851 | /v2/trades?user=<3 ví>&taker_only=false&start=…&end=…&limit=500 |
| d2_gamma_repeat_params | 200 | 616 | gamma /markets?condition_ids=×3&limit=10 → 0 dòng |
| f3_prices_max | 200 | 582 | /v2/prices-history?token_id=80727…&interval=max |
| d3_gamma_closed_any | 200 | 1039 | gamma /markets?condition_ids=×3&closed=any&limit=10 → 2 dòng |

## 10. Báo cáo này KHÔNG làm

- Không kết luận lãi/lỗ của bất kỳ ví nào. Số PNL/volume dẫn trên là giá trị sàn trả về cho ví mẫu, chỉ để minh họa trường dữ liệu.
- Không chọn k, không chọn 20 ví, không tuyên bố chiến lược sống/chết.
- Không đề xuất chạy backtest. Backtest chỉ chạy sau khi chủ nhân chốt D1–D5, spec đóng băng có hash, và có lệnh GO riêng.
