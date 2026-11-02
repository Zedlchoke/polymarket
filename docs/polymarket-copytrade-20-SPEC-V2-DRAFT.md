# SPEC v2 NHÁP — POOL TỪ THỊ TRƯỜNG ĐOẠN 1, RỒI VỀ TRƯỚC SAU (CHỈ SAU KHI BACKTEST V2 QUA)

---

# ⛔ CHƯA ĐÓNG BĂNG — CHƯA CÓ HASH ĐÓNG BĂNG — CHƯA CHẠY TÍNH ĐIỂM ⛔

Spec v2 là spec MỚI hoàn toàn về NGUỒN POOL; mọi luật khác giữ nguyên từ spec v1 đóng băng
(`polymarket-copytrade-20-SPEC-V1-FROZEN.md`, hash toàn file `e98691e2c555a326c59a92633a22864e04152109c9e48b8cc8457f9b7a5cb61f`).
Đóng băng v2 chỉ xảy ra sau khi coordinator kiểm toán bản nháp này và chủ nhân duyệt; chạy hồ sơ/backtest/về trước
chỉ xảy ra sau lệnh GO riêng cho từng bước. Lựa chọn "làm cả hai" của chủ nhân KHÔNG phải lệnh GO.

## 0. Vì sao phải có v2 (phân tích từ lần chạy v1, không dùng kết quả tính điểm nào — v1 không có)

Spec v1 dừng ở bước pool vì nguồn pool bắt buộc là 4 bảng leaderboard tháng 09–12/2025, còn endpoint
`/v2/leaderboard` chỉ có `time_period ∈ {day, week, month, all}` tính từ hiện tại, không có tham số tháng quá khứ
(bằng chứng: 2 request mẫu + contract, báo cáo `polymarket-copytrade-20-VIEC-B-C-REPORT-V1.md`). v1 không tính tín hiệu nào,
không chọn k*, không có verdict → không có kết quả v1 nào bị "dùng lại" cho v2.

**Cấm của v2 (kéo dài từ lệnh chủ nhân):** không dùng lại pool leaderboard tháng quá khứ; không dùng bảng `all` hôm nay
làm pool chính (chứa thành tích tương lai — chỉ được làm bảng PHỤ MÔ TẢ, không tính điểm); không đổi sang kỷ nguyên quá khứ
khác mà vẫn dùng leaderboard tháng; không sàng lọc thị trường hay ví theo lãi/PnL/kết quả backtest.

## 1. GIỮ NGUYÊN TỪ V1 — không viết lại khác đi (danh mục kiểm tra khi đóng băng v2)

Tất cả các mục dưới đây NGUYÊN VĂN như spec v1 đóng băng (xem file đó để tra từng luật đầy đủ):

1. **Q1** thể thao trận đơn trước trận; luật tag `'Sports'` + `include_tag=true` + `sportsMarketType`/`gameStartTime`;
   mùa vụ loại khỏi v1, đếm riêng; đường dự phòng tags rỗng + đếm tỷ lệ dùng.
2. **Q2** cửa sổ chọn 90 ngày = đoạn 1; còn chơi ≥3 lệnh/14 ngày cuối; báo cáo hao hụt hoạt động.
3. **Q3** 10 cửa lọc: khối lượng thể thao ≥50.000 USD; ≥80 lệnh (D5); ≥20 mã thị trường; lãi giữ-tới-chốt trên mỗi đồng đặt >0
   VÀ lãi đã chốt thật >0; còn chơi; một thị trường ≤50% lãi giữ-tới-chốt; both-sides >30% loại (chuỗi TRADE loại
   SPLIT/MERGE/REWARD/MAKER_REBATE); bot >2.000 lệnh và lãi/khối lượng <1% loại; xếp hạng theo lãi giữ-tới-chốt/đồng đặt
   (hòa: thị trường → lệnh → chữ cái); gộp nhóm trùng/min ≥50% + ≥20 lệnh + ≤60 phút, k tính theo nhóm, bù đủ 20 nhóm.
4. **Q4** overlap: cùng conditionId + token; cửa sổ trượt 24h; mỗi nhóm ≥100 USD ròng (D3), tổng ≥500 USD; khối lượng tại
   kích hoạt ≥10.000 USD (cộng dồn tới thời điểm); chặn giá 0,10 (D4); dải 0,10–0,90; mỗi thị trường/sự kiện một lần; phe trước thắng.
5. **Q5** giá copy: VWAP đủ 100 USD/60 phút; phạt max(0,02; spread) — backtest 0,02 cố định; cổ phần = 100/giá; phí
   feeSchedule từng thị trường, bảng ngày dự phòng, **FEE_MISSING bỏ + đếm riêng + báo động >5% (không phải cổng)**;
   làm tròn giá 4 chữ số / cổ phần số lẻ / phí tới xu / so ngưỡng trước; nhạy cảm 0,05/0,10 thay thế.
6. **Q6** 100 USD cố định; mẫu số 100×n; trần 10 lệnh mở; mọi lý do bỏ đếm riêng; tỷ lệ bỏ >30% → cổng không qua.
7. **Q7** giữ tới chốt từ resolutions.payouts (đơn vị micro-USDC); Gamma umaResolutionStatus đối chiếu; lệch → dừng và báo;
   hòa 0,5 = cp×0,5−100−phí; ân hạn 14 ngày; >10% chưa chốt sau ân hạn → cổng không qua.
8. **Q8** k=1–5 theo nhóm; ≥100 tín hiệu trong mẫu; Điểm = ROI − std/100/√n; Điểm>0, ROI>0, ROI ≥ ROI₁+0,03;
   chênh Điểm <0,02 → nhiều tín hiệu; khóa k*, test đúng 1 lần.
9. **Q9** cổng giết 3 tầng đủ 8 cổng tầng 1, tầng 2 CI 95% bootstrap gom sự kiện, tầng 3 chỉ cờ (D1); verdict
   SỐNG / CHẾT / CHƯA ĐỦ BẰNG CHỨNG.
10. **Q10** về trước chỉ sau backtest qua tầng 1+2 + kiểm toán CONFIRMED; cohort mới tại GO (D2); thăm dò 5 phút;
    spread /book 1 lần, sổ rỗng → 0,02; ≥500 đã chốt + ≥90 ngày, tối đa 12 tháng, +30 ngày; bắt đầu đầu mùa thường.
11. **D1–D5** như đã chốt; **mốc B**: T0 2025-09-13 (1757721600), T1 2025-12-12 (1765497600), T2 2026-03-12 (1773273600),
    T3 2026-06-10 (1781049600), 90 ngày/đoạn, tránh World Cup.
12. Giải lớn chỉ mô tả (khối lượng cộng dồn tới cuối đoạn, ≥8 thị trường con, top 5%); 50 ví đối chứng chỉ đo thiên lệch;
    18 bảng báo cáo với nhãn tính điểm/mô tả; ngân sách ~200 request/ngày, 10 giây/request, hạn 14 ngày hồ sơ;
    luật dừng 429/403/throttle; trần trang → cận dưới; ranh giới cứng (giấy, 0 đồng, không lệnh thật, không VPN, không bí mật).

## 2. THAY ĐỔI 1 — POOL: TỪ LEADERBOARD THÁNG SANG QUÉT THỊ TRƯỜNG ĐOẠN 1 (thay toàn bộ mục pool của v1)

### 2.1. Liệt kê thị trường đoạn 1 (từng bước)

1. Gọi Gamma `/markets` với `include_tag=true`. Ưu tiên lọc theo ngày nếu endpoint cho phép (contract có
   `start_date_min`/`start_date_max`, `sports_market_types`, `closed`): lấy danh sách thị trường thể thao đã đóng
   có ngày bắt đầu rơi quanh đoạn 1, rồi **xác minh từng thị trường bằng `gameStartTime`** (T0 ≤ gameStartTime < T1) —
   vì `start_date` của thị trường có thể khác giờ đá (điều này sẽ được đo ở bước đếm mô tả, Việc 3).
   Cần tra lại theo mã: lặp `condition_ids=` từng mã + `closed=any` (dạng comma không hoạt động — đã chứng minh).
2. Thị trường HỢP LỆ cho pool: có tag label đúng chữ `'Sports'`; `sportsMarketType` khác rỗng; `gameStartTime` khác rỗng
   và T0 ≤ gameStartTime < T1; trận đơn; trước trận; KHÔNG phải mùa vụ.
3. Thị trường thể thao thiếu `sportsMarketType`/`gameStartTime` (mùa vụ, futures): loại khỏi v1, **đếm riêng** như v1.
4. Thị trường 2 tag mâu thuẫn: theo 'Sports', ghi bảng mô tả. Tags rỗng sau `include_tag=true`: theo đường dự phòng v1 + đếm tỷ lệ.

### 2.2. Sàng lọc rẻ trước (VIẾT TRƯỚC, KHÔNG DỰA TRÊN LÃI — ngưỡng là ĐỀ XUẤT CHỜ DUYỆT)

- Nếu số thị trường đoạn 1 quá lớn: chỉ đưa vào bước lấy giao dịch chi tiết những thị trường có **tổng tiền giao dịch
  cộng dồn TRONG ĐOẠN 1 ≥ 10.000 USD** (đo từ dữ liệu giao dịch đoạn 1; KHÔNG dùng `volumeNum` cuối cùng — đó là tương lai).
- **Ngưỡng 10.000 USD là ĐỀ XUẤT CHỜ DUYỆT, chưa phải luật đã chốt.** Phải báo: tổng thị trường đoạn 1, số giữ lại,
  **số bị sàng lọc bỏ là bao nhiêu**.
- Cấm: sàng lọc thị trường hay ví theo lãi, theo PnL, hay theo kết quả backtest.

### 2.3. Lấy giao dịch đoạn 1 (từng bước)

1. Với mỗi thị trường hợp lệ (sau sàng lọc): lấy `trades`/`activity` với `taker_only=false`, phân trang cursor tới null,
   trần trang ghi cận dưới.
2. CHỈ giữ giao dịch có timestamp trong đoạn 1 (T0 ≤ ts < T1). Không lấy giao dịch ngoài đoạn 1 để tính pool;
   không lấy giao dịch sau đoạn 1 để chọn ví.
3. Checkpoint bằng timestamp + conditionId sau mỗi thị trường; ngân sách ~200 request/ngày, 10 giây/request;
   429/403/throttle/chậm bất thường → dừng toàn bộ, ghi lỗi + Retry-After, không tăng tốc bù.

### 2.4. Tổng hợp ví và áp Q3 (từng bước)

1. Từ tất cả giao dịch đoạn 1: gom theo ví. Tiền mặt = `usdc_size` trên activity (trades đối chiếu).
2. Tính cho mỗi ví: tổng usdc_size mua thể thao đoạn 1; số lệnh; số thị trường; **lãi giữ-tới-chốt trên mỗi đồng đặt —
   chỉ các lệnh đã chốt TỚI CUỐI ĐOẠN 1** (giá chốt từ resolutions.payouts của các thị trường đó; thị trường chưa chốt
   tới cuối đoạn 1 không tính lãi lúc chọn người — như v1); lãi đã chốt thật; còn chơi ≥3 lệnh/14 ngày cuối; both-sides;
   bot. Dòng 999: loại + đếm riêng.
3. Áp đúng 10 cửa Q3 + gộp nhóm + xếp hạng như v1 (mục 1). Đủ 20 nhóm; không đủ → thiếu mẫu, không hạ cửa.

### 2.5. Đo thiên lệch pool mới (bắt buộc trong báo cáo hồ sơ, chỉ mô tả)

Báo cáo phải có: (a) số thị trường đoạn 1 hợp lệ; (b) số thị trường sau sàng lọc + số bị bỏ; (c) số ví trước lọc;
(d) số nhóm sau lọc; (e) **tỷ lệ ví Q3-passing mà pool leaderboard cũ sẽ bỏ sót** — lấy bảng `all` HÔM NAY
(chỉ mô tả, không tính điểm, vì chứa tương lai), so ví nào đạt Q3 trong pool thị trường mà không nằm trong top bảng all:
đó là ước lượng "pool quét thị trường bắt được người mà leaderboard không thấy". (f) Đối chiếu 50 ví đối chứng như v1
(chỉ đo thiên lệch, chỉ mô tả). Tỷ lệ (e) KHÔNG phải cổng giết, KHÔNG dùng để mở rộng pool.

## 3. THAY ĐỔI 2 — OVERLAP: KHÔNG ÁP DỤNG CHO KỶ NGUYÊN B; CHUYỂN SANG GIAI ĐOẠN VỀ TRƯỚC

1. **Overlap kỷ nguyên B: KHÔNG ÁP DỤNG / THIẾU MẪU.** Lý do (đã đo, chỉ đọc): sổ PaperDesk chỉ phủ 07–31/10/2026,
   không phủ kỷ nguyên B (kết thúc 10/06/2026) — 0/32 lệnh BET_PAPER trong kỷ nguyên; dòng BET_PAPER không có trường
   ánh xạ conditionId/token. KHÔNG được ghi "0% overlap", KHÔNG được ghi "hai hệ thống khác nhau".
2. Overlap chỉ chạy ở giai đoạn về trước (Việc 5), SAU khi: (a) backtest v2 qua tầng 1+2; (b) kiểm toán CONFIRMED;
   (c) xây xong bộ ánh xạ PaperDesk↔Polymarket bằng spec RIÊNG + kiểm tra độ chính xác.
3. **Yêu cầu cho bộ ánh xạ (chỉ ghi yêu cầu ở đây, KHÔNG xây trong bước này):** ánh xạ từ `match_id` + đội nhà/khách
   (`home`/`away`) + giờ đá (`kickoff_utc`) sang conditionId/token; phải đo và báo: tỷ lệ dòng BET_PAPER ánh xạ được,
   tỷ lệ không ánh xạ được; **tỷ lệ không ánh xạ >20% → THIẾU DỮ LIỆU ÁNH XẠ, dừng, không kết luận overlap thấp**;
   không đoán mã thị trường.
4. Quy tắc overlap khi chạy (như v1, không đổi): chỉ mô tả; nhãn CẤM cứu verdict; không chọn k*; không lật verdict copytrade
   hay verdict D2 PaperDesk; cửa sổ chính 24 giờ TRƯỚC lệnh PaperDesk; hai cửa sổ phụ chỉ mô tả; <30 lệnh overlap →
   THIẾU MẪU; các kết luận bám đúng 4 luật đọc đã chốt ở v1, không thêm kết luận mới.

## 4. Trình tự 5 việc với điểm dừng bắt buộc (tóm tắt để kiểm toán)

1. Việc 1: viết spec v2 nháp (file này) → DỪNG chờ kiểm toán + duyệt.
2. Việc 2: đóng băng v2 + hash toàn file (mã chuẩn sha256sum) + FREEZE_LOG_V2 → DỪNG chờ "hash v2 đúng, chạy tiếp".
3. Việc 3: bước đếm mô tả pool (số thị trường/sau sàng lọc/số ví; ước request; ước ngày với trần 200/ngày) → DỪNG báo
   ngân sách; vượt 14 ngày thì báo vượt bao nhiêu + đề xuất giữ/thu hẹp theo luật KHÔNG dựa trên lãi — chủ nhân quyết.
4. Việc 4: hồ sơ + backtest v2 (chỉ sau GO riêng) → DỪNG chờ kiểm toán; BUG FOUND → sửa + chạy lại sạch; SPEC FLAW → viết
   thiết kế v3 công bằng, không chạy v3 ngay.
5. Việc 5: về trước (chỉ sau backtest qua tầng 1+2 + CONFIRMED + GO riêng): cohort mới tại GO; dựng bộ ánh xạ trước;
   thăm dò 5 phút; spread /book 1 lần; ≥500 đã chốt + ≥90 ngày; overlap về trước theo luật C4 → DỪNG báo cáo.

## 5. Những chỗ còn là ĐỀ XUẤT CHỜ DUYỆT trong bản nháp này

1. **Ngưỡng sàng lọc thị trường ≥10.000 USD giao dịch trong đoạn 1** (mục 2.2) — ĐỀ XUẤT, chưa luật.
2. Ngưỡng báo động tỷ lệ bỏ vì thiếu phí 5%; ngưỡng missed 20%; K=50 ví đối chứng; giải lớn ≥8 thị trường + top 5%;
   chu kỳ 5 phút — các ngưỡng này v1 đã duyệt, giữ nguyên; không ngưỡng mới nào khác được thêm trong v2 ngoài mục 2.2.
3. Việc dùng `start_date_min/max` của Gamma để thu hẹp danh sách ban đầu (mục 2.1 bước 1) là kỹ thuật liệt kê, phải xác minh
   bằng gameStartTime từng thị trường; nếu endpoint không lọc được theo ngày thì quét phân trang toàn bộ thị trường thể thao
   đã đóng và lọc bằng gameStartTime phía client — cách nào cũng phải báo số request dùng ở Việc 3.

## 6. KHÔNG làm

Không đóng băng trong file này; không chạy hồ sơ/backtest/về trước; không dùng kết quả backtest v2 để đổi luật về trước
và ngược lại; không sửa spec v2 sau khi đóng băng và sau khi thấy kết quả; không sửa code/dữ liệu PaperDesk (chỉ đọc khi tới Việc 5);
giữ mọi ranh giới cứng của v1 (giấy, 0 đồng, không lệnh thật, không ví, không VPN, không bí mật trong file/log/chat).
