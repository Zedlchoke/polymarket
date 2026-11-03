# BÁO CÁO VIỆC 3 — ĐẾM MÔ TẢ POOL THỊ TRƯỜNG V2 — NGÀY 1 + NGÀY 2 (2026-11-03)

**ĐÂY LÀ ĐẾM MÔ TẢ, KHÔNG PHẢI HỒ SƠ CHÍNH, KHÔNG PHẢI BACKTEST.** Không chọn 20 nhóm, không xếp hạng ví, không tính lời lỗ ví nào, không tìm k*, không chạy đoạn 2/3, không chạy backtest, không chạy về trước, không áp dụng cơ chế nào vào PaperDesk hay Polymarket.

## 1. Cửa pháp lý đã khớp trước khi chạy

- **GO Việc 3 (ngày 1):** chủ nhân xác nhận qua cổng hỏi ngày 2026-11-03: *"Hash đúng — GO Việc 3"* — bao gồm: đã đọc file kiểm toán Việc 2 (CONFIRMED, commit `0514c51`), đã tự tính lại hash spec v2 = đúng, lệnh GO riêng cho Việc 3.
- **GO ngày 2:** chủ nhân xác nhận trong chat 2026-11-03 11:31 ICT: *"Tôi đã xác nhận hash đúng và GO Việc 3, tiếp tục ngày 2"* (trích theo prompt ngày 2).
- **Hash spec v2 tự tính lại trước khi chạy (cả 2 ngày):** `shasum -a 256 docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md` = `ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8` — **KHỚP** hash trong lệnh.

## 2. Kỹ thuật liệt kê (báo theo §5.3 spec — kèm mọi phát hiện endpoint)

Kỹ thuật đã dùng, đúng luật: Gamma `/markets?closed=true&include_tag=true` + cửa sổ `end_date_min/max` (ISO) **[2025-09-13 → 2025-12-26 = T1 + 14 ngày đệm chốt trễ]** + `order=id&ascending=true` + `limit=100` (server kẹp limit tại 100) + **xác minh TỪNG thị trường bằng gameStartTime client-side trong [T0, T1)**. Cửa sổ end_date CHỈ là kỹ thuật liệt kê + đệm, KHÔNG phải tiêu chí chọn (đúng lệnh ngày 2).

Phát hiện endpoint (đều có URL trong `viec3/data/ledger.jsonl`):
1. `start_date_min/max` KHÔNG tác dụng trên /markets (ngày 1 chứng minh; bỏ theo lệnh).
2. `sports_market_types` hoạt động nhưng KHÔNG dùng (sợ sót giá trị enum — đúng lệnh; giá trị smt quan sát được ở thị trường hợp lệ: moneyline 1.784, totals 449, spreads 381, both_teams_to_score 83, các loại tennis 37, nrfi 6, team_totals 4, child_moneyline 9).
3. **Offset-cap:** Gamma /markets từ chối `offset ≥ 2100` bằng HTTP 422 → mỗi query tối đa ~2.100 dòng. Khắc phục: **chia lát cửa sổ end_date (bisection)** tới khi mỗi lát phân trang hết tự nhiên; dò-trước offset 2000 (1 request) cho lát mới để tiết kiệm. 11 lát hoàn chỉnh ghép phủ kín 105/105 ngày cửa sổ.
4. **Data-API /v2/trades theo thị trường:** tham số `market=` BỊ TỪ CHỐI (HTTP 400, thông báo API hướng dẫn dùng `condition`); phải dùng **`condition_id=<cid>`** + `taker_only=false` + `start/end` (epoch) + `limit=500`. **KHÔNG có cursor, KHÔNG có offset** (400) → thị trường >500 fill trong đoạn 1 phải **chia nhỏ cửa sổ thời gian** đệ quy (kỹ thuật đã viết sẵn `v3_phase_trades2.py`, hoạt động).
5. Lược đồ dòng theo thị trường: snake_case (`proxy_wallet`, `token_id`, `condition_id`, `transaction_hash`, `outcome_index`…).

## 3. ĐẾM TỪNG BƯỚC LỌC (chính xác, từ union id trên đĩa — 28.992 dòng trang, khử trùng còn 16.748 id duy nhất)

| Bước lọc | Số | Ghi chú |
|---|---|---|
| Tổng dòng Gamma trả về trong bước liệt kê (mọi trang mọi lát) | **28.992** | gồm trùng do chia lát; nguyên văn từng trang lưu `viec3/data/listing/` |
| **Thị trường duy nhất** | **16.748** | khử trùng theo id |
| — Phi thể thao (không có tag 'Sports' sau include_tag=true) | 8.557 | loại khỏi pool |
| — Phi thể thao CÓ sportsMarketType (anomaly, mô tả) | 257 | theo luật tag là chuẩn → loại; đếm riêng |
| — Thể thao MÙA VỤ (Sports + sportsMarketType rỗng) | **4.720** | loại, đếm riêng đúng luật |
| — Thể thao THIẾU gameStartTime (smt có, gst rỗng) | **166** | loại, đếm riêng đúng luật (gồm props mùa giải vd HR-leaders) |
| — Thể thao trận đơn nhưng gameStartTime NGOÀI đoạn 1 | 305 | 159 trước T0 + 146 sau T1 |
| — Tag rỗng sau include_tag=true | **0** | không phải dùng fallback v1; tỷ lệ fallback = 0% |
| **Thị trường HỢP LỆ (tag 'Sports' + smt ≠ rỗng + T0 ≤ gameStartTime < T1)** | **2.743** | danh sách đầy đủ: `listing_slim.jsonl.valid_FULL`; phân bố gst: T9-2025: 845, T10: 862, T11: 786, T12 (→12/12): 250 |

## 4. Ngưỡng 10.000 USD (LUẬT ĐÃ DUYỆT 2026-11-03) — đo từ trade đoạn 1, KHÔNG dùng volumeNum

**Đo mẫu hệ thống 9 thị trường** (8 thị trường chọn hệ thống theo thứ tự conditionId — cố định, không dính lãi/khối lượng — + 1 thị trường đo lúc debug endpoint; mỗi thị trường đúng 1 request, fills 26→445, tất cả <500 nên 1 trang đủ):

| Thị trường | fills | USD đoạn 1 | Đạt 10k | Ví |
|---|---|---|---|---|
| nfl-jax-sf-2025-09-28 spread | 107 | 12.378 | ✓ | 57 |
| cfb-usc-ill-2025-09-27 total | 30 | 1.514 | ✗ | 15 |
| cfb-ballst-wmich-2025-10-11 spread | 26 | 9.436 | ✗ | 18 |
| nfl-lac-lv-2025-09-15 total | 61 | 24.319 | ✓ | 35 |
| atp-kecmanovic-vs-mensik-2025-09-25 | 107 | 10.723 | ✓ | 30 |
| atp-sinner-vs-minaur-2025-09-30 | 296 | 39.421 | ✓ | 63 |
| nfl-tb-hou-2025-09-15 total | 108 | 86.698 | ✓ | 55 |
| nba-sas-dal-2025-10-22 total | 49 | 5.955 | ✗ | 23 |
| nfl-chi-was-2025-10-13 total (debug) | 445 | 54.603 | ✓ | 83 |

- **Tỷ lệ đạt ngưỡng trong mẫu: 6/9 (67%)** → ước ~1.829 thị trường giữ / ~914 bỏ (khoảng tin cậy rộng vì n=9; USD đo bằng Σ price×size trên fill duy nhất, khử trùng theo transaction_hash+token_id+timestamp+side+size; timestamp 100% trong đoạn 1 đã kiểm).
- **Số ví trước khi lọc (chưa áp cửa nào theo lời/hiệu suất): đo được trên mẫu = 236 ví hợp nhất qua 8 thị trường mẫu** (Bears debug: 83 ví, không lưu danh sách). Đếm ĐẦY ĐỦ số ví của cả 2.743 thị trường đòi hỏi lấy hết trade — chính là việc vượt 14 ngày ở mục 6, nên theo lệnh "ước tính vượt thì dừng", số đầy đủ CHƯA đo và không bịa.

## 5. Tra lại theo mã (luật: lặp condition_ids + closed=any)

- Request lặp `condition_ids=` × 8 mã + `closed=any` (+ `include_tag=true`): **tra lại được 8/8, không tra lại được 0**; **chênh lệch thật với bản liệt kê: 0** (tag/sportsMarketType/gameStartTime khớp hết). Lần chạy đầu thiếu include_tag → tags rỗng gây 8 "chênh lệch" giả; đã chạy lại đúng và ghi rõ.
- Đối chiếu `closed=any` + cùng cửa sổ end_date: trả **0 dòng** (tổ hợp tham số không cho kết quả — phép kiểm này KHÔNG KẾT LUẬN được, ghi trung thực).
- Dò rò thị trường chốt sau 26/12 (cửa sổ 27/12→31/01, trang 1): **0 thị trường hợp lệ bị lọt** ở mức kiểm tra trang mẫu.

## 6. Ngân sách đã dùng (tách từng ngày-chạy) + giải thích 9 dòng chênh

| | Dòng sổ | Request API thật | HTTP 200 | 4xx | Không phản hồi |
|---|---|---|---|---|---|
| **Ngày 1** (2026-11-03 sáng, tới commit `294a51e`) | 193 | **184** | 174 | 10×422 (đều là trang offset ≥2100 — bằng chứng offset-cap) | 9 |
| **Ngày 2** (phiên tiếp theo cùng ngày lịch, theo lệnh chủ nhân "trần ngày 2 vẫn ~200") | 200 | **175** | 154 | 4×422 + 17×400 (thử tham số trades: market= bị từ chối, offset= bị từ chối) | 25 |

- **Giải thích 9 dòng chênh ngày 1 (193 sổ − 184 API):** 1 dòng lỗi SSL xác thực chứng chỉ (request không tới được server) + 8 dòng nhật ký `SSL_FALLBACK_UNVERIFIED` (ghi lại việc hạ sang SSL context không xác minh cho GET chỉ-đọc — máy này không có chuỗi CA; tiền lệ `probe2_v2.py`). Các dòng này KHÔNG phải request API.
- Ngày 2 có 25 dòng không phản hồi: 10 dòng `DAY_BOUNDARY`/biên giới phiên + nhật ký SSL fallback + 2 dòng ghi nhãn 400 nhưng thực tế lỗi SSL cục bộ (khai rõ: dòng `E_market_body`, `F_condition_id`).
- Nhịp: 10 giây/request (luật); sau 1 lần watchdog "chậm bất thường" 40.053 ms (đúng luật dừng toàn bộ) → cooldown >17 phút + giảm còn 15 giây/request. **Lỗi của agent phải khai:** trong ~11 phút có 2 tiến trình liệt kê chạy trùng (tôi chẩn đoán nhầm job cũ đã chết rồi khởi động lại) → 33 khoảng cách giữa 2 request liên tiếp < 9 giây (nhỏ nhất 3,0 giây) — vi phạm kỷ luật nhịp, đã dừng cả 2 ngay khi phát hiện, không xảy ra 429/403. Hai tiến trình trùng cũng là lý do liệt kê vô tình hoàn tất sớm.
- Toàn bộ log từng request: `viec3/data/ledger.jsonl`; checkpoint: `viec3/data/checkpoint.json`; dữ liệu thô từng trang: `viec3/data/listing/`.

## 7. ƯỚc tính ngân sách cho HỒ SƠ CHÍNH (Việc 4) và kết luận 14 ngày

Ngân sách luật: ~200 request/ngày, 10 giây/request, hạn 14 ngày cho bước hồ sơ (= 2.800 request).

| Thành phần hồ sơ | Ước request | Ghi chú |
|---|---|---|
| Lấy trade đoạn 1 cho 2.743 thị trường hợp lệ | **≥ 2.743** | cận dưới: mọi thị trường mẫu chỉ cần đúng 1 request; thị trường >500 fill phải chia cửa sổ (thêm request, đuôi lớn CHƯA đo được — mẫu n=9 chưa bắt thị trường nghìn fill) |
| Resolutions + phí từng thị trường giữ (ước ~1.829) | ≥ 1.829 | ≥1 request/thị trường |
| Query từng VÍ cho Q2/Q3 (còn chơi ≥3 lệnh/14 ngày cuối, lãi giữ-tới-chốt từng ví-từng thị trường) | hàng nghìn | ví hợp nhất chỉ 8 thị trường mẫu đã 236; toàn pool chắc chắn nhiều nghìn ví |
| **Tổng thận trọng** | **~5.000–12.000+** | **≈ 25–60 ngày @200/ngày** |

**KẾT LUẬN: VƯỢT 14 NGÀY.** Chỉ riêng việc lấy trade danh sách (cận dưới 2.743 request ≈ 13,7 ngày) đã gần cạn toàn bộ hạn 14 ngày mà chưa tính resolutions, phí, và query ví (thành phần bắt buộc của hồ sơ). Vượt ít nhất ~11 ngày (kịch bản chỉ còn resolutions ~28 ngày) và có thể vượt ~46+ ngày theo khối lượng ví. **Tôi DỪNG đúng chỗ theo lệnh: không tự thu hẹp pool theo lãi, không tự đổi ngưỡng 10.000 USD, không tự bỏ thị trường theo lời.** Việc giữ nguyên hay thu hẹp theo luật KHÔNG dựa trên lãi (ví dụ nâng ngưỡng khối lượng, giới hạn môn/ngày — nếu chủ nhân duyệt như luật mới) là quyết định của chủ nhân.

## 8. Xác nhận cuối Việc 3, bằng chữ

Tôi xác nhận: chỉ đếm mô tả theo spec v2 đã đóng băng có hash `ae504a97…bee55d8` (tự tính lại khớp trước khi chạy cả 2 ngày); chưa chọn ví, chưa tính điểm, chưa backtest, chưa về trước; chưa sửa spec sau khi đóng băng; chưa áp dụng cơ chế nào vào PaperDesk hay Polymarket; không lặp request ngày 1 (cache trang dùng lại 0 request; mọi request ngày 2 là cho phần chưa liệt kê xong + tra lại + đo mẫu). Giới hạn đã khai đầy đủ: mẫu ngưỡng/ví n=9 hệ thống (số đầy đủ của toàn pool chưa đo vì chính là việc vượt 14 ngày); phép đối chiếu closed=any không kết luận được; đuôi thị trường >500 fill chưa đo.

**DỪNG. Chờ chủ nhân đọc báo cáo Việc 3, rồi mới có lệnh mới cho Việc 4.**
