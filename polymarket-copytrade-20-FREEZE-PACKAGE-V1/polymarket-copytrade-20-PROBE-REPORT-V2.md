# BÁO CÁO THĂM DÒ BỔ SUNG V2 — LÀM RÕ 8 LỖ HỔNG CỦA V1

Ngày: 2026-11-02. Người chạy: agent ZCode (GLM-5.3), theo prompt bổ sung của chủ nhân sau báo cáo Giai đoạn C.
File V1 (`polymarket-copytrade-20-PROBE-REPORT-V1.md`) **giữ nguyên, không ghi đè**. Dữ liệu thô V2: `~/Downloads/Polymarket/probe/probe_out_v2/`, log từng request: `probe_out_v2/requests.log`, checkpoint: `probe_out_v2/checkpoint.json`.

**Bản chất:** chỉ làm rõ lỗ hổng, chỉ đọc. KHÔNG tính lãi, KHÔNG chọn k, KHÔNG chọn 20 ví, KHÔNG kết luận sống/chết/thiếu mẫu. Mọi luật/ngưỡng mới trong báo cáo này đều là **ĐỀ XUẤT, chờ chủ nhân duyệt**, không tự áp vào spec chính. Con số 0,02 (phạt trễ dự phòng) và mọi con số trong file tổng hợp **không đổi**.

---

## 0. Nhật ký vận hành V2 — đầy đủ, kể cả lỗi của agent

- **Tổng 205 request API** (204× HTTP 200, 1× HTTP 404), ngoài ra 2 lần tải file contract (không phải API). Độ trễ trung vị 766 ms, mean 897 ms.
- **Sự kiện dừng theo luật (1 lần):** 11:48:09Z, request `v2_trades_upthe_p27` trả HTTP 200 nhưng chậm **7.363 ms so với trung vị 0,7 s** → watchdog "response chậm dần bất thường" kích hoạt → **DỪNG TOÀN BỘ**, không retry ngay. Không có 429/403/Retry-After. Xử lý: **cooldown 17 phút** (11:48→12:05), sau đó chạy lại **chậm hơn** (10 giây/request thay vì 6), watchdog giữ nguyên. Phiên 2 chạy hết phần còn lại không sự cố.
- **Lỗi của agent phải khai báo (V1):** ở V1, request d3 gửi chuỗi mã `0x401c161493cecfca…` là **bản chép tay sai phần đuôi** của mã thật `0x401c1614a93ddc09…aa58e28d7` (mã đúng vẫn nằm nguyên trong file dữ liệu gốc). V1 kết luận "1/3 mã không tra được" một phần do lỗi này. Việc 1 dưới đây đã làm rõ bằng mã đúng.
- **Request lặp không cần thiết (V2):** khi chạy lại chế độ `all`, hàm Việc 1 không có chốt bỏ-qua nên gửi lại 3 request Gamma trùng lặp (comma/slug). Không ảnh hưởng kết quả, ghi ra đây để minh bạch.
- **Trần an toàn phân trang:** mỗi stream tối đa 40 trang (20.000 dòng). Hai stream của ví UpTheBlues **chạm trần** (chi tiết ở Việc 2).

## 1. Việc 1 — Gamma tra không ra 1/3 mã: KẾT LUẬN (a) LỖI DẠNG GỬI, ĐÃ SỬA ĐƯỢC

Các mã dùng (lấy từ file dữ liệu gốc, không chép tay): `0x0256ef63427ed0d9…c44182074` (Ghana), `0x401c1614a93ddc09…aa58e28d7` (Grizzlies vs. Jazz, NBA), `0x51166276fa646ca5…44182074` (Spain vs. Argentina).

| Thử | Tham số gửi nguyên văn | HTTP | Kết quả |
|---|---|---|---|
| comma phẳng, KHÔNG closed | `gamma-api.polymarket.com/markets?condition_ids=<3 mã nối bằng %2C>&limit=10` | 200 | **0 dòng** (rỗng) |
| comma phẳng, CÓ `closed=any` | `…?condition_ids=<3 mã %2C>&closed=any&limit=10` | 200 | **0 dòng** (rỗng) — dạng comma KHÔNG hoạt động dù đã có closed=any |
| lặp param, CÓ `closed=any` | `…?condition_ids=<mã1>&condition_ids=<mã2>&condition_ids=<mã3>&closed=any&limit=10` | 200 | **3/3 mã tra ra** (Ghana, Grizzlies vs. Jazz, Spain) |
| theo slug | `…?slug=nba-mem-uta-2026-10-26&closed=any&limit=5` | 200 | 1 dòng, đúng mã Grizzlies |

Kết luận **(a)**: lỗi dạng gửi + lỗi chép tay của agent, đã sửa. Quy tắc lấy dữ liệu Gamma theo mã: **lặp tham số `condition_ids=` cho từng mã + `closed=any`**; slug là đường dự phòng hoạt động tốt. Không có mã nào "thật sự không tra được"; không mã nào bị bỏ khỏi mẫu.

## 2. Việc 2 — Phân trang đi hết, giải thích ví 0 dòng, đếm lại

### 2.1. Kết quả phân trang (cửa sổ 7 ngày 1793013231→1793618031, `taker_only=false`, `limit=500`)

| Ví | Endpoint | Trang | Dòng | next_cursor cuối | has_more | ts sớm → muộn | Trạng thái |
|---|---|---|---|---|---|---|---|
| BreakTheBank | /v2/trades | 35 | **17.248** | null | False | 1793013261 → 1793617954 | **ĐI HẾT** |
| BreakTheBank | /v2/activity?type=TRADE | 35 | **17.248** | null | False | 1793013261 → 1793617954 | **ĐI HẾT** |
| joseph00677 | /v2/trades | 1 | 0 | null | False | — | ĐI HẾT (rỗng) |
| joseph00677 | /v2/activity?type=TRADE | 1 | 0 | null | False | — | ĐI HẾT (rỗng) |
| UpTheBlues | /v2/trades | 40 | 20.000 | còn cursor | True | 1793546851 → 1793618022 | **CHẠM TRẦN 40 trang** — chỉ phủ ~20,3 giờ cuối của cửa sổ |
| UpTheBlues | /v2/activity?type=TRADE | 40 | 20.000 | còn cursor | True | 1793546851 → 1793618022 | **CHẠM TRẦN 40 trang** |

Phát hiện kèm: **`/v2/activity?type=TRADE` và `/v2/trades?taker_only=false` trả đúng cùng số dòng (17.248 = 17.248) và cùng khoảng ts cho BreakTheBank** — hai endpoint này là hai cửa vào của cùng một tập fill. UpTheBlues có 20.000/20.000 dòng toàn BUY, 3.138 mã thị trường khác nhau chỉ trong ~20 giờ (ví quét mua rát cực rộng); BreakTheBank 15.906 BUY / 181 mã thị trường trong 7 ngày.

Đi hết UpTheBlues ước cần thêm vài trăm trang (≈1000 dòng/giờ × 7 ngày) — đã vượt phạm vi thăm dò nhỏ; **CÒN MỞ**: nếu cần đi hết ví này phải có ngân sách request riêng do chủ nhân duyệt trước (đúng tinh thần "ngân sách request phải ghi trước" của tổng hợp Q10).

### 2.2. Chẩn đoán ví joseph00677 trả 0 dòng — kiểm tra từng khả năng, không đoán một khả năng

| Khả năng | Bằng chứng | Kết luận |
|---|---|---|
| Địa chỉ sai loại (không phải proxy wallet)? | `/v2/user-stats?user=0xcdcc…7935a` HTTP 200, `proxy_wallet` đúng địa chỉ, `trade_count=725`, PNL realized mọi thời đại 5.325.561 USD, volume 47.146.017 USD, join_date 1791224554 | **Loại** — địa chỉ đúng, là proxy wallet có lịch sử |
| Cửa sổ thời gian? | `/v2/trades?taker_only=false` cửa sổ 30 NGÀY (limit 100): 100 dòng, ts 1792182977 → **1792857432** — lệnh cuối lúc ~09:57 ngày 25-10-2026, **trước khi cửa sổ 7 ngày bắt đầu (1793013231 ≈ 26-10 09:13) khoảng 17 giờ** | **Đúng nguyên nhân chính: ví nghỉ chơi trước cửa sổ** |
| taker/maker làm mất dòng? | `taker_only=true` 7 ngày: 0 dòng; `taker_only=false`: 0 dòng — như nhau | **Loại** |
| activity khác trades? | activity 7 ngày: 0 dòng = trades 0 dòng | **Loại** |
| Ví chỉ chơi ngoài thể thao? | `/v2/positions?user=…&limit=20` (mặc định OPEN): 4 vị thế REDEEMABLE — CS2 fnatic vs Liquid (BO3), Games Total O/U 2.5, Chelsea win 2026-10-24, CS2 Map 1 Winner | **Loại** — ví vẫn chơi thể thao (kể cả esports CS2), chỉ là không giao dịch trong cửa sổ |
| Đứng hạng leaderboard? | `/v2/leaderboard?user=0xcdcc…` (mặc định time_period=day) trả `data: None` — không đứng hạng NGÀY; nhưng có rank 2 bảng THÁNG (V1 bước b) | Ghi chú field: lookup 1 ví phụ thuộc `time_period`, không suy lẫn |

**Kết luận:** ví hợp lệ, đang giữ vị thế thể thao/esports REDEEMABLE, **đã ngừng giao dịch trước cửa sổ 7 ngày ~17 giờ** → 0 dòng là đúng dữ liệu, không phải lỗi API/địa chỉ. Đây chính là lý do tổng hợp yêu cầu điều kiện "còn chơi ≥3 lệnh/14 ngày cuối" (Q2/Q3) — ví này sẽ bị loại ở cổng đó.

### 2.3. Đếm lại bước đếm mô tả (bb đầy đủ + upthe một phần + joseph 0)

- **Cặp thị trường + cửa (condition_id + token_id) có ≥ 2 ví cùng BUY trong cửa sổ trượt 24h: 22.** (V1 đếm 0 vì mỗi ví chỉ lấy 1 trang.)
- **Cặp có ≥ 3 ví: 0.**
- Giới hạn bắt buộc ghi kèm: (1) upthe chỉ có ~20h cuối (chạm trần), thiếu ~6 ngày → **22 là CẬN DƯỚI**; (2) mẫu chỉ 3 ví từ top PNL tháng, chưa gộp nhóm, chưa áp bất kỳ lọc Q4 nào (100 USD ròng, khối lượng ≥10.000 USD, dải giá 0,10–0,90, mỗi sự kiện một lần); (3) joseph đóng góp 0. **Con số này vẫn chỉ là đếm mô tả, KHÔNG dùng kết luận 90+90+90 ngày đủ hay thiếu, KHÔNG dùng chọn k.**

## 3. Việc 3 — Nhận diện thể thao: tag 'Sports' với `include_tag=true` là tín hiệu chính xác

### 3.1. Vì sao V1 thấy tags rỗng

Contract Gamma ghi rõ: *"Tags included only when `include_tag=true`"* — V1 và V2-round-1 đều không gửi cờ này nên **tags luôn trả [] ở mọi thị trường, kể cả đang mở**. Kết luận "tags rỗng vì thị trường đã đóng" trong báo cáo V1 là **sai**; đã sửa ở đây.

### 3.2. Mẫu kiểm tra (đã lấy, URL nguyên văn trong requests.log: `v3_*`, `v3b_*`, `v3c_*`)

| Nhóm | Số | Đặc điểm quan sát được |
|---|---|---|
| Thể thao đã đóng (trận đơn) | 8 + Ghana + Spain + Grizzlies = 11 | `sportsMarketType='moneyline'`, `gameStartTime` có, **tag 'Sports' có (11/11)** khi `include_tag=true` |
| Thể thao đã đóng (mùa vụ: Kings win 2025 NBA Finals) | 1 | `sportsMarketType=None`, `gameStartTime=None`, NHƯNG **tag 'Sports' + NBA + Basketball có** |
| Phi thể thao đã đóng | 12 (Trump/Harris, Fed, Iran, MicroStrategy, Zelenskyy…) | `sportsMarketType=None`; 2 thị trường CÓ `gameStartTime` (deadline 2026-06-01, 2025-07-01) → **gameStartTime đơn lẻ KHÔNG đủ** để nhận diện; **không cái nào có tag 'Sports'** |
| Thể thao đang mở | 5 (CS2, tennis, EPL) | `sportsMarketType='moneyline'`, `gameStartTime` ngày trận |
| Phi thể thao đang mở | 5 (Iran 2027, bầu cử 2028…) | `sportsMarketType=None`, không 'Sports' |

### 3.3. LUẬT NHẬN DIỆN THỂ THAO — ĐỀ XUẤT (chờ duyệt, chưa áp vào spec)

1. Gọi Gamma `/markets` kèm `include_tag=true` (bắt buộc, nếu không tags luôn rỗng).
2. **Thể thao ⇔ có tag label đúng chữ `'Sports'`** trong `tags[].label` của thị trường.
3. Trong thể thao, **thuộc phạm vi v1 (trận đơn, trước trận) ⇔ `sportsMarketType` khác rỗng VÀ `gameStartTime` khác rỗng**; chỉ tính lệnh có thời điểm < `gameStartTime`.
4. Thể thao mà `sportsMarketType` rỗng → thị trường mùa vụ/giải dài → **loại khỏi v1, đếm riêng** (đúng luật Q1 loại "vô địch cả mùa").
5. Không dùng `gameStartTime` một mình (deadline của thị trường phi thể thao cũng lọt vào trường này).
6. Thị trường "2 tag" mâu thuẫn (ví vừa 'Sports' vừa 'Politics'): nếu có 'Sports' thì theo 'Sports', ghi vào bảng mô tả số lượng; khoanh mẫu v2 kiểm tra lại.

**Độ chính xác trên mẫu 23 thị trường đã lấy:** nhận diện thể thao/phi thể thao đúng **23/23** (11/11 thể thao có 'Sports' gồm cả mùa vụ; 12/12 phi thể thao không có). Nhận sai 0. Giới hạn: mẫu 23 thị trường, chưa dày các môn; luật đang là ĐỀ XUẤT.

## 4. Việc 4 — Spread lịch sử: XÁC NHẬN KHÔNG CÓ ENDPOINT

| Nguồn đã kiểm | Bằng chứng (URL + kết quả trong requests.log) | Vì sao không cho spread tại thời điểm kích hoạt trong quá khứ |
|---|---|---|
| Sổ lệnh CLOB `/book?token_id=` | Token thị trường đã chốt → **HTTP 404** (sổ đã biến mất). Token thị trường đang mở → HTTP 200: 51 mức bid / 29 mức ask, `tick_size`, `last_trade_price`, `timestamp` | Chỉ trả **ảnh chụp HIỆN TẠI**; không có tham số thời điểm quá khứ; sổ của thị trường đã chốt bị xóa hẳn (404) |
| `/v2/tokens?token_id=` | HTTP 200, 1 dòng; các trường liên quan giá chỉ có `final_price` (=1.0, giá chốt) | Metadata + giá chốt, không có bid/ask/spread |
| `/v2/prices-history` | V1 + V2: chuỗi giá đơn 5 phút/điểm; có `as_of` = "giá quan sát gần nhất tại/trước thời điểm" | Là chuỗi **giá đơn** (last/observation), không phải bid và ask riêng → không dựng được spread = ask − bid |
| Gamma market `outcomePrices` | Chỉ là giá hiện tại/cuối | Không phải sổ lệnh |

**Xác nhận lại luật tổng hợp (không đổi):** nếu không lấy được spread thì **phạt trễ = 0,02** (Q5.2 của file tổng hợp). Không có lệnh chủ nhân thì không đổi số này thành số khác.

**ĐỀ XUẤT — cách đo spread cho test giấy về trước (chờ duyệt):**
1. Chỉ đo ở test về trước (forward), không đo được cho backtest quá khứ — backtest dùng phạt 0,02 cố định theo đúng tổng hợp.
2. Trong chu kỳ thăm dò forward (ví dụ 5 phút/lần theo Q10), khi phát hiện kích hoạt k: gọi ngay `/book` của token đó 1 lần, ghi `best_bid`, `best_ask`, `timestamp` sổ.
3. spread = best_ask − best_bid; nếu spread < 0,02 thì phạt vẫn lấy 0,02 (đúng công thức max(0,02; spread)); sổ rỗng/404/timeout → phạt = 0,02, ghi riêng số lần rơi vào dự phòng.
4. Ngân sách: tối đa +1 request mỗi tín hiệu; tổng ghi trước khi GO; gặp 429/throttle → dừng theo luật chung.
5. Ghi thêm độ sâu 2 mức giá tốt nhất (size) để đối chiếu với giả định VWAP đủ 100 USD ở Q5.1 — chỉ mô tả, không đổi luật.

## 5. Việc 5 — Tên trường chốt: đối chiếu cùng mã trên 3 nguồn

Mẫu: Spain vs. Argentina draw (`0x51166276…`) và Ghana (`0x0256ef63…`), cả hai đã chốt.

| Nguồn | Tên trường thật | Giá trị Spain | Giá trị Ghana | Ghi chú |
|---|---|---|---|---|
| Gamma market | **`umaResolutionStatus`** (KHÔNG có trường `resolutionStatus` trong response) | `"resolved"` | `"resolved"` | Kèm `resolvedBy`, `automaticallyResolved`, `resolutionSource` (fifa.com), `outcomePrices=["1","0"]` (chuỗi) |
| Data API `/v2/resolutions?condition=` | `status`, **`payouts`**, `resolved_at`, `resolution_source` | `resolved`, **[1000000, 0]**, `2026-07-19T22:53:46Z` | `resolved`, **[1000000, 0]**, `2026-06-18T01:35:55Z` | payouts = micro-USDC/cổ phần; `resolved_at` RFC3339 (khác epoch giây của trades) |
| Data API `/v2/positions?user=&condition=` | `status`, `redeemable`, `realized_pnl` | `CLOSED`, `False`, 1.409.061,71 | `CLOSED`, `False`, 1.291.590,01 | **`status` của positions là vòng đời VỊ THẾ của ví, không phải kết quả chốt của thị trường** — không được dùng làm nguồn chốt |

**Các trường hợp lệch tên/giá trị đã ghi nhận:** (1) tổng hợp viết `Gamma resolutionStatus = resolved` → trường thật là `umaResolutionStatus`; (2) `status` trùng tên nhưng khác nghĩa ở resolutions (trạng thái chốt thị trường) và positions (vòng đời vị thế); (3) đơn vị thời gian khác nhau: `resolved_at` RFC3339 vs `timestamp` epoch giây; (4) giá chốt biểu diễn khác nhau: `outcomePrices` (chuỗi "1"/"0") vs `payouts` (micro-USDC 1000000/0). **Không có lệch GIÁ TRỊ chốt** trên 2 mã mẫu: hai nguồn cùng nói cửa 0 thắng toàn phần.

**ĐỀ XUẤT — luật ưu tiên nguồn chốt (chờ duyệt, từng bước):**
1. Nguồn chính: **Data API `/v2/resolutions` → `payouts`** (micro-USDC, chừng mực chính xác nhất, chứa được cả hòa 0,5 = 500.000).
2. Nguồn đối chiếu: Gamma `umaResolutionStatus='resolved'` + `outcomePrices`.
3. Positions KHÔNG bao giờ là nguồn chốt.
4. Quy trình mỗi tín hiệu: đọc resolutions; nếu `payouts` đủ 2 phần tử → giá chốt = payouts/1.000.000 theo outcome_index của token. Nếu resolutions KHÔNG trả dòng cho mã đó → dùng Gamma `outcomePrices` (chuỗi → số) và **đánh cờ "nguồn phụ"**. Nếu cả hai không có → tín hiệu vào diện ân hạn 14 ngày của Q7.
5. **Điều kiện dừng và báo lệch thay vì tự chọn:** nếu resolutions và Gamma khác nhau về cửa thắng (payouts chỉ đúng 1 phía nhưng outcomePrices ngược) HOẶC payouts không khớp bất kỳ dạng chốt hợp lệ nào (0/0,5/1 mỗi cổ phần) → KHÔNG tính lãi tín hiệu đó, ghi vào bảng lệch, đưa vào diện ân hạn; nếu sau ân hạn vẫn lệch thì tín hiệu giữ trạng thái "chưa chốt chắc", không tính thắng không tính thua, và số này nhập vào tỷ lệ chưa chốt của cổng giết Q9 tầng 1 (cổng 8). Không bao giờ tự chọn nguồn theo cảm tính khi hai nguồn mâu thuẫn.

## 6. Việc 6 — outcome_index=999: KHÔNG GẶP trong 34.783 dòng đã quét

- Đã quét toàn bộ dòng có trường `outcome_index` trong mọi file dữ liệu V1 + V2 (bao gồm corpus phân trang 34.496 dòng của 2 ví): **tổng 34.783 dòng, 0 dòng = 999**. Phân bố thực đo: `{0: 24.832, 1: 9.951}` — không gặp cả index ≥2 (toàn bộ mẫu là thị trường 2 cửa).
- Kết luận: chưa tìm được ví dụ nào (đã tìm trong 34.783 dòng); giá trị 999 chỉ được chứng thực bởi mô tả contract v2 ("999 means the outcome could not be labeled"), chưa thấy ngoài đời. **THIẾU mẫu thị trường nhiều cửa** (neg-risk có nhiều outcome) để biết hành vi index ≥2 của dữ liệu — thuộc bước hồ sơ sau này.

**ĐỀ XUẤT — cách xử lý (chờ duyệt):**
1. Khi dựng tín hiệu: dòng có `outcome_index=999` → **loại khỏi tín hiệu, đếm riêng mục "thiếu nhãn cửa"** trong bảng tỷ lệ bỏ của Q6 (bỏ vì lý do dữ liệu), không đoán nhãn từ chuỗi `outcome`.
2. **Ngưỡng báo động ĐỀ XUẤT: trên 5%** tổng lệnh quan sát của một nhóm (hoặc của toàn bộ) thiếu nhãn → báo cáo phải nêu đích danh, xem lại chất lượng dữ liệu trước khi tiếp tục; ngưỡng này chỉ báo động, chưa phải cổng giết — nếu chủ nhân muốn nâng thành cổng thì quyết trước khi đóng băng.
3. Với thị trường nhiều cửa (index ≥2): bắt buộc đối chiếu `outcome_index` ↔ `clobTokenIds[outcome_index]` ↔ chuỗi `outcomes` tại bước hồ sơ; chưa xác nhận xong thì chưa đóng băng (đúng mục 16 dòng 1 của spec).

## 7. Việc 7 — 15 bảng báo cáo của spec V1: đối chiếu với tổng hợp

| # | Bảng (spec V1 §14) | Định nghĩa ngắn | Nguồn dữ liệu | Lọc áp dụng | Tính điểm hay mô tả | Có trong tổng hợp? |
|---|---|---|---|---|---|---|
| 1 | Theo môn | Lãi ròng+tín hiệu theo môn | tín hiệu × Gamma (tags/smt) | Q1–Q7 | Mô tả (cấp dữ liệu cho cờ tầng 3 "môn duy nhất") | Có (Q1) |
| 2 | Theo loại thị trường | thắng thua / chấp điểm / tổng điểm / kèo cầu thủ | tín hiệu × Gamma sportsMarketType | Q1 | Mô tả | Có (Q1) |
| 3 | Mùa thường / playoff / giải lớn + World Cup | tách mùa; phụ: bỏ World Cup | tín hiệu × Gamma + lịch mùa | Q1, Q9 tầng 3 | Mô tả + cờ tầng 3 (D1 quyết có thành cổng) | Có (Q1, Q9) |
| 4 | Theo dải giá | 0,10–0,30 / 0,30–0,70 / 0,70–0,90 | sổ tín hiệu copy | Q6 | Mô tả + cờ "mong manh" | Có (Q6) |
| 5 | Theo độ lớn thị trường | khối lượng tại kích hoạt | tín hiệu + khối lượng cộng dồn | Q4.7 | Mô tả | Có (Q1) |
| 6 | Top 3 sự kiện % lãi ngoài mẫu | đóng góp sự kiện | lãi từng tín hiệu × sự kiện | Q9 tầng 3 | Mô tả (tầng 3) | Có (Q9) |
| 7 | Hao hụt hoạt động | còn hoạt động đoạn 2/3 bao nhiêu nhóm | trades theo nhóm | Q2 | Mô tả (bắt buộc ghi rõ) | Có (Q2) |
| 8 | Tỷ lệ bỏ + lý do bỏ | bỏ vì thiếu độ sâu/60'/đầy vốn/giá | sổ tín hiệu | Q6 | **CỔNG** (Q9 tầng 1, cổng 8: ≤30%) | Có (Q6, Q9) |
| 9 | Tỷ lệ chưa chốt + thời gian chờ | sau ân hạn 14 ngày | sổ tín hiệu × resolutions | Q7 | **CỔNG** (≤10%) + thời gian chờ mô tả | Có (Q7, Q9) |
| 10 | Bảng k=1 đối chứng | cùng công thức, cùng mẫu số | pipeline ở k=1 | Q8 | **CỔNG** (Q9 cổng 5, 6) | Có (Q8, Q9) |
| 11 | Phụ: đếm theo tiền / 50-200 USD / 6h-24h | biến thể mô tả | pipeline biến thể | Q4, Q8, D3, D4 | Mô tả — **cấm cứu verdict** | Có (Q4, Q8, D4) |
| 12 | Nhạy cảm phạt 0,05 / 0,10 | thay phạt, tính lại từ đầu | pipeline Q5 | Q5 | **CỔNG với 0,05** (Q9 cổng 3); 0,10 mô tả | Có (Q5, Q9) |
| 13 | Bỏ vì chặn giá 0,10 / ngoài 0,10–0,90 + cờ 20% | số bị loại theo giá | sổ tín hiệu | Q4.8–9 | Mô tả + cờ (Q4 "phải ghi rõ") | Có (Q4) |
| 14 | Độ trễ forward từng tín hiệu | thời điểm giao dịch vs phát hiện | sổ giấy forward | Q10 | Mô tả (không được che) | Có (Q10) |
| 15 | Ghi chú giới hạn | gộp nhóm = nghi ngờ; phạm vi khi bỏ >30% | — | Q3.10, Q6 | Mô tả | Có (Q3, Q6) |

**Kết luận đối chiếu:** cả 15 bảng đều có gốc trong file tổng hợp — **spec V1 không tự thêm bảng mới nào**. Ngược lại, tổng hợp có **3 yêu cầu báo cáo mà §14 của spec V1 còn thiếu** (chỉ liệt kê trong luật chứ chưa thành bảng):
- (A) **Bảng phụ các thị trường con khác của cùng sự kiện bị bỏ** (Q4: "ghi vào bảng phụ") — mô tả.
- (B) **Bảng kết quả cổng tầng 1 (8 cổng) + tầng 2 (khoảng tin cậy 95%) in rõ từng giá trị** (Q9) — kết quả cổng để kiểm toán, không phải bảng dữ liệu mới; in đầy đủ để kiểm tra, không lật thêm verdict nào ngoài cổng đã định.
- (C) **Bảng ngày thiếu dữ liệu forward + ngân sách request thực dùng** (Q10: thiếu >10% số ngày → test vô hiệu) — mô tả nhưng quyết định hiệu lực của test forward.
Cả 3 đều **chỉ mô tả/in kết quả cổng, không được dùng để cứu verdict khi bảng chính thua**. Ba bảng này được bổ sung vào SPEC-V1-DRAFT-V2 §14 (mục 16–18) — xem nhật ký sửa.

## 8. Việc 8 — Bốn đề xuất thành văn bản (ĐỀ XUẤT, chờ duyệt)

### 8.1. Nguồn tiền mặt chính

So sánh thực đo trên **100 cặp giao dịch ghép 1-1** (khóa ghép `transaction_hash + token_id + timestamp + side + size`; BreakTheBank, trang gần nhất): `usdc_size` (activity) vs `price × size` (trades) — **chênh lệch tối đa 0,000000 USD, trung vị 0,000000, 100/100 khớp tới nửa xu**. Không có lệch do làm tròn hay tick; khác biệt duy nhất là biểu diễn: `price` trên trades có nhiễu float (0,0909999999) — nghĩa là giá được tính ngược từ usdc/size ở đâu đó trong chuỗi dữ liệu.
**ĐỀ XUẤT:** nguồn tiền chính = **`usdc_size` trên `/v2/activity?type=TRADE`** (sẵn số USD, không phải nhân hai số float); `price × size` từ `/v2/trades` dùng làm kiểm tra chéo (không khớp quá 0,01 USD/lệnh thì báo). Hai endpoint đã chứng minh cùng một tập fill (17.248 = 17.248 dòng).

### 8.2. Pool ứng viên

Thực tế dữ liệu: leaderboard chỉ có `time_period` = day/week/month/all; không có 90 ngày. user-stats không có cửa sổ.
**ĐỀ XUẤT — cách dựng pool và đo thiên lệch:**
1. Pool = hợp của leaderboard `time_period=month&category=sports&sort_by=PNL` lấy ở 4 thời điểm: tháng chứa cuối đoạn 1, và 3 tháng trước đó (đủ phủ 90 ngày đoạn chọn), mỗi bảng lấy đủ trang (cursor), ghi số ví mỗi bảng.
2. Với mỗi ví trong pool, tự tính đủ các chỉ số 90 ngày từ trades/activity theo luật Q3 (không tin số liệu bảng).
3. **Đo thiên lệch bắt buộc:** lấy mẫu đối chứng K ví (ĐỀ XUẤT K=50) từ bảng `all` PNL cao mà KHÔNG nằm trong pool, tự tính chỉ số 90 ngày của họ, đếm bao nhiêu ví lẽ ra đạt hết các cửa Q3 → số đó là "ví giỏi bị missed"; tỷ lệ missed phải in trong báo cáo hồ sơ. Đây là ước lượng dưới của thiên lệch (chỉ đo được trong những ví có mặt ở bảng all).
4. Ghi rõ trong spec trước khi chạy: pool này thiên về ví đang thắng gần đây — đúng như tổng hợp đã cảnh báo, không được giả vờ là ngẫu nhiên.

### 8.3. Quy đổi ngày giờ

**ĐỀ XUẤT:** mọi mốc đổi về **epoch giây UTC**; `resolved_at` RFC3339 → epoch giây bằng cách **làm tròn XUỐNG tới giây** (floor, không làm tròn gần nhất) để không bao giờ coi thị trường là chốt sớm hơn thực tế lệch nửa giây; mọi so sánh thời gian thực hiện trên số nguyên giây UTC. Không dùng múi giờ địa phương ở bất cứ bước nào.

### 8.4. Làm tròn

**ĐỀ XUẤT (khóa trước khi đóng băng, chờ duyệt):**
- Giá copy: giữ đúng kết quả VWAP + phạt, **làm tròn tới 4 chữ số thập phân** (0,0001), làm tròn gần nhất.
- Số cổ phần = 100 / giá copy: **giữ nguyên số lẻ, không làm tròn** (tính trên giấy); chỉ khi in báo cáo mới làm tròn hiển thị 4 chữ số.
- Phí = cổ phần × tỷ lệ × giá × (1−giá): **làm tròn tới xu (0,01 USD), làm tròn gần nhất**; tổng lãi mỗi tín hiệu cộng phí đã làm tròn.
- usdc_size/usdc: theo nguyên bản sàn (đã thấy số lẻ tới 2 chữ số).
- Mọi phép so ngưỡng (ví dụ 0,10–0,90) thực hiện TRƯỚC khi làm tròn, tránh tín hiệu lọt nhờ làm tròn.

### 8.5. Mốc tuyệt đối T0/T1/T2/T3

Dữ liệu đã xác nhận: lịch sử giá từng token có thể lấy theo cửa sổ ≤15 ngày (phải ghép ≥6 lần cho 90 ngày); trades theo ví lấy theo start/end tùy ý; thị trường đã chốt phải đợi resolutions.
**ĐỀ XUẤT (cách chọn, KHÔNG chốt mốc):** lấy **ngày GO làm mốc neo** (không lấy ngày thăm dò, vì còn khoảng thời gian chủ nhân duyệt): T3 = ngày GO trừ ân hạn chốt 14 ngày; T2 = T3 − 90 ngày; T1 = T2 − 90 ngày; T0 = T1 − 90 ngày (tổng 270 + 14 ngày lùi từ GO). Sau khi tính, kiểm tra 3 điều kiện rồi mới trình chủ nhân chốt: (1) 3 đoạn rơi vào mùa nào, (2) dữ liệu resolutions đã có cho mọi thị trường chốt tới T3 + 14, (3) không段 nào rơi vào khoảng API thiếu dữ liệu đã biết. Mốc cuối cùng do chủ nhân duyệt sau khi xem V2.

## 9. Bảng tổng kết 8 lỗ hổng

| Việc | Lỗ hổng V1 | Trạng thái | Bằng chứng ngắn |
|---|---|---|---|
| 1 | 1/3 mã Gamma không tra ra | **ĐÃ ĐÓNG** (loại a) | lặp `condition_ids` + `closed=any` → 3/3 mã; comma không hoạt động; slug hoạt động |
| 2 | Phân trang chưa đi hết; ví 0 dòng chưa giải thích | **ĐÃ ĐÓNG một phần — CÒN MỞ với UpTheBlues** | bb 17.248 dòng đi hết; joseph = nghỉ chơi trước cửa sổ 17h (đã loại 4 khả năng khác); upthe chạm trần 40 trang, cần ngân sách riêng |
| 3 | Tags thể thao rỗng | **ĐÃ ĐÓNG** | cần `include_tag=true`; luật ĐỀ XUẤT tag 'Sports' đúng 23/23 mẫu |
| 4 | Spread lịch sử chưa xác nhận | **ĐÃ ĐÓNG** (không có endpoint) | book chỉ hiện tại (404 với token đã chốt); tokens chỉ final_price; prices-history chỉ giá đơn; phạt 0,02 giữ nguyên; đề xuất đo forward |
| 5 | Tên trường chốt mâu thuẫn | **ĐÃ ĐÓNG** | 3 nguồn, giá trị khớp trên 2 mã; luật ưu tiên resolutions.payouts là ĐỀ XUẤT chờ duyệt |
| 6 | outcome_index=999 chưa rõ | **CÒN MỞ (thiếu mẫu)** | 0/34.783 dòng gặp 999; chưa có mẫu thị trường nhiều cửa; cách xử lý + ngưỡng 5% là ĐỀ XUẤT |
| 7 | 15 bảng đối chiếu | **ĐÃ ĐÓNG** | 15/15 có gốc trong tổng hợp; tổng hợp đòi thêm 3 bảng (A,B,C) → đã bổ sung vào spec V2 |
| 8 | Tiền mặt/pool/ngày/làm tròn/T0 | **ĐỀ XUẤT XONG, chờ chủ nhân quyết** | 100/100 cặp usdc_size ≡ price×size; 4 văn bản đề xuất 8.1–8.5 |

## 10. Báo cáo này KHÔNG làm

Không tính lãi, không chọn k, không chọn 20 ví, không kết luận đủ/thiếu mẫu cho 90+90+90 ngày từ con số đếm mô tả, không đóng băng, không ghi hash. Mọi ĐỀ XUẤT trong file chỉ có hiệu lực sau khi chủ nhân duyệt bằng văn bản.
