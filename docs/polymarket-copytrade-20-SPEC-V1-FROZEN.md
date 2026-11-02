# SPEC v1 ĐÓNG BĂNG (FROZEN) — COPY TRADE 20 TÀI KHOẢN POLYMARKET, CHỈ TRÊN GIẤY

# ✅ ĐÃ ĐÓNG BĂNG — 2026-11-02 ✅

SHA256 (tính trên TOÀN BỘ nội dung từ dòng "# SPEC v1 ĐÓNG BĂNG" xuống hết file, không gồm chính dòng hash này): d7b4c39b7dda6a43f4ff3d4717bf5e63fed734e305496bc1813e952c3be6a9f7

Ngày đóng băng: 2026-11-02. Đóng băng theo lệnh của chủ nhân (prompt đóng băng/backtest/overlap ngày 2026-11-02), sau khi chủ nhân chọn mốc B và duyệt hết theo khuyến nghị, coordinator chọn B theo ủy quyền.
Từ sau thời điểm đóng băng: KHÔNG ĐƯỢC SỬA file này. Muốn đổi thì viết spec mới, đặt tên mới, đóng băng mới. Hash đầy đủ của file (kể cả dòng hash) ghi tại `polymarket-copytrade-20-FREEZE-LOG-V1.md`.

## Danh sách quyết định đã chốt (nguồn + hash, đúng thứ tự ưu tiên)

| Quyết định | Nguồn | sha256 |
|---|---|---|
| Q1–Q10 + 3 tầng cổng giết + timeline 3×90 ngày | `polymarket-copytrade-20-answers-SYNTHESIS-6-GOC.md` | `cf6f7560c4dc6a1ff4f56bfb7925ba955bcc67b6768072d7cc088868764a4617` |
| D1 cờ / D2 nhóm mới / D3 100-500 USD / D4 24h+0,10 / D5 80 lệnh; §19.2–19.4, 19.6 duyệt; 19.1/19.5/19.9 duyệt hướng kèm điều kiện | `polymarket-copytrade-20-QUYET_DINH_OWNER_2026-11-02.md` (bản coordinator) | `01248d550391824d208a5bf49ca6650054d8f179950e32b4fcc11edce939a3a0` |
| Mốc B + 7 mục duyệt chi tiết (phí thiếu, giải lớn, 50 ví, spread, làm tròn, tags dự phòng) | Prompt chủ nhân ngày 2026-11-02 "đóng băng, backtest, overlap" | (văn bản lệnh trong chat; các giá trị liệt kê nguyên văn tại mục 15 dưới đây) |
| Spec ứng viên V2 (đối chiếu, không lệch) | `polymarket-copytrade-20-SPEC-V1-CANDIDATE-V2.md` | `2f69fdc103dafebabe5a2be8e67167c432b7ee9d97879ed203c3faa3c8dac276` |
| Báo cáo thăm dò V1/V2 (tên trường, phí, resolutions) | `polymarket-copytrade-20-PROBE-REPORT-V1.md` / `-V2.md` | `2782eb5cd6bd3b03264c9fa5717245e541605bab0589fdd54865c1a529b43c32` (V2) |

## 0. Ranh giới cứng

Chỉ trên giấy, 0 đồng, không lệnh thật, không tiền thật, không nối ví, không tạo tài khoản Polymarket mới, không VPN, không mua dữ liệu trả phí. Không ghi mật khẩu/API key/token vào file/log/chat. Luật dừng thu thập: HTTP 429/403/throttle/response chậm dần bất thường → DỪNG TOÀN BỘ bước đang chạy, ghi mã lỗi + Retry-After, không retry ngay, không tăng tốc bù; không thiết kế collector burst 10 giây. Ngân sách đã duyệt: sàng lọc rẻ trước; tối đa ~200 request/ngày; đi chậm 10 giây/request; hạn 14 ngày cho bước hồ sơ; ví nhiều lệnh kiểu UpTheBlues KHÔNG đi hết lịch sử bằng mọi giá — chạm trần trang thì ghi CẬN DƯỚI; hết hạn k≥3 thiếu 100 tín hiệu trong mẫu → theo luật (chuyển k đủ mẫu hoặc ghi thiếu mẫu), không hạ ngưỡng, không đổi cửa sổ, không đổi k sau khi thấy ngoài mẫu. Không dùng endpoint fee-rate cũ. Không sửa code/dữ liệu PaperDesk; chỉ ĐỌC sổ PaperDesk ở mục 17.

## 1. Thuật ngữ và đơn vị

Mọi mốc tính bằng giây UTC (Unix seconds); 1 ngày = 24 giờ = 86.400 giây. RFC3339 → epoch giây bằng làm tròn XUỐNG tới giây (§19.6 ĐÃ DUYỆT). Tiền mặt lệnh = `usdc_size` trên `/v2/activity?type=TRADE` (§19.4 ĐÃ DUYỆT); `price×size` từ `/v2/trades` chỉ để đối chiếu (lệch >0,01 USD/lệnh thì báo). Mã thị trường `condition_id`; mã cửa `token_id` + `outcome_index`; `outcome_index=999` = thiếu nhãn → loại + đếm riêng + báo động >5% (§19.3 ĐÃ DUYỆT, KHÔNG phải cổng giết; cấm nâng thành cổng sau đóng băng). Cửa phân biệt bằng mã token, không bằng chữ YES/NO. Cổ phần trả 1/0/0,5 USD. Ví/nhóm: k tính theo NHÓM sau gộp. VWAP theo tiền. ROI = lãi ròng / tổng tiền đặt; mẫu số copy = 100 × số tín hiệu đã lấy. Lãi giữ-tới-chốt = cp × giá chốt − tiền mua − phí theo ngày.

## 2. Dòng thời gian — MỐC B (ĐÃ CHỐT, LUẬT)

| Mốc | Ngày UTC | Epoch giây |
|---|---|---|
| T0 (đầu đoạn 1 — chọn người) | 2025-09-13T00:00:00Z | 1757721600 |
| T1 (đầu đoạn 2 — trong mẫu) | 2025-12-12T00:00:00Z | 1765497600 |
| T2 (đầu đoạn 3 — ngoài mẫu) | 2026-03-12T00:00:00Z | 1773273600 |
| T3 (cuối đoạn 3) | 2026-06-10T00:00:00Z | 1781049600 |

Ba đoạn đúng 90,0 ngày mỗi đoạn, liền nhau, không trùng không hở, tránh World Cup 2026 (bắt đầu 11-06-2026, sau T3). Mùa giải từng đoạn (ghi trong báo cáo): đoạn 1 (13-09→12-12-2025): NFL 2025 mùa thường, MLB playoffs 2025, NBA/NHL khai màn; đoạn 2 (12-12-2025→12-03-2026): NFL playoffs + Super Bowl 02-02-2026, NBA/NHL mùa thường; đoạn 3 (12-03→10-06-2026): MLB khai màn, NBA/NHL playoffs, Champions League knockout, Pháp Open. Dữ liệu đoạn 1 chỉ dùng thông tin biết tới cuối đoạn 1. Tín hiệu gán theo thời điểm kích hoạt. Không rút 60 ngày; thiếu 90+90+90 → ghi thiếu mẫu. **Không có code chọn mốc tự động, không tối ưu mốc theo kết quả.**

## 3. Q1 — Chỉ thể thao, chỉ trận đơn, chỉ trước trận

Chỉ thị trường một trận duy nhất, trước trận, đơn, không combo; loại: vô địch mùa, giải thưởng mùa, nhiều trận gộp, đang đá trực tiếp. LUẬT nhận diện (§19.1, điều kiện đã thỏa: 23 mẫu thật + luật từng bước; coordinator xác nhận theo ủy quyền 2026-11-02): (1) Gamma `/markets` kèm `include_tag=true` (lặp `condition_ids` từng mã + `closed=any`); (2) thể thao ⇔ có tag label đúng chữ `'Sports'`; (3) phạm vi v1 ⇔ thể thao VÀ `sportsMarketType` khác rỗng VÀ `gameStartTime` khác rỗng VÀ thời điểm lệnh < giờ bóng; (4) thể thao thiếu 2 trường = mùa vụ → loại khỏi v1, đếm riêng; (5) không dùng `gameStartTime` một mình; (6) 2 tag mâu thuẫn → theo 'Sports', ghi bảng mô tả. Đường dự phòng khi tags vẫn rỗng sau `include_tag=true` (ĐÃ DUYỆT): smt khác rỗng → coi thể thao trận đơn; smt rỗng + chỉ gameStartTime → KHÔNG coi thể thao, đưa danh sách tra lại; đếm riêng tỷ lệ dùng dự phòng. Báo cáo tách theo môn / loại thị trường (thắng thua, chấp điểm, tổng điểm, kèo cầu thủ) / mùa / dải giá / độ lớn.

## 4. Q2 — Cửa sổ chọn = đoạn 1 của mốc B

90 ngày: 2025-09-13 → 2025-12-12. Còn chơi: ≥3 lệnh trong 14 ngày cuối đoạn. Báo cáo hao hụt hoạt động 20 nhóm ở đoạn 2, 3.

## 5. Q3 — Luật chọn 20 nhóm (D5 = 80 lệnh)

Tính chỉ trên thể thao trước trận, đoạn 1, dữ liệu biết tới cuối đoạn 1. 10 cửa: (1) khối lượng thể thao ≥50.000 USD (tổng `usdc_size` mua, tự tính, không lấy từ bảng xếp hạng); (2) ≥80 lệnh trade rows; (3) ≥20 mã thị trường; (4) lãi giữ-tới-chốt trên mỗi đồng đặt >0 VÀ lãi đã chốt thật >0; (5) ≥3 lệnh/14 ngày cuối; (6) một thị trường ≤50% tổng lãi giữ-tới-chốt; (7) both-sides (đồng thời giữ cp>0 cả hai token cùng thị trường, từ chuỗi TRADE loại SPLIT/MERGE/REWARD/MAKER_REBATE) >30% số thị trường → loại; (8) >2.000 lệnh và lãi/khối lượng <1% → loại; (9) xếp theo lãi giữ-tới-chốt/đồng đặt giảm dần, hòa: nhiều thị trường → nhiều lệnh → mã ví chữ cái; (10) gộp trước xếp hạng cuối: trùng/min ≥50% VÀ trùng ≥20 lệnh, trùng = cùng conditionId + cùng token, ≤60 phút; gộp theo thứ tự lãi giảm dần; k tính theo nhóm; bù tới 20 nhóm, không đủ → thiếu mẫu; nhóm đóng băng từ đoạn 1, dùng cho cả đoạn 2+3.

Pool ứng viên (§19.5 ĐÃ DUYỆT kèm điều kiện đã viết rõ): hợp 4 bảng leaderboard `time_period=month&category=sports&sort_by=PNL` (tháng chứa cuối đoạn 1 + 3 tháng trước), đi hết cursor, tự tính mọi chỉ số 90 ngày. Đo thiên lệch (ĐÃ DUYỆT, chỉ phương pháp đo + báo động): 50 ví đối chứng (TỰ CHỌN đã duyệt) từ bảng `all` PNL giảm dần, bỏ ví đã ở pool, lấy đủ 50; tự tính các cửa Q3; tỷ lệ "ví giỏi bị missed" in trong báo cáo hồ sơ; vượt 20% (đã duyệt) → báo động "pool thiên lệch mạnh", KHÔNG tự mở rộng pool.

## 6. Q4 — Overlap (D3, D4)

Cùng conditionId + cùng token_id. Mỗi sự kiện một lần đầu mỗi đoạn (thị trường con khác cùng sự kiện → bảng phụ 16). Mỗi thị trường một lần đầu mỗi đoạn, phe trước thắng. Cửa sổ trượt 24h (86.400 giây) theo giây UTC: tại mỗi lệnh mua ròng, nhóm thứ k − nhóm đầu tiên ≤24h → kích hoạt ngay tại lệnh thứ k. Đếm vị thế ròng tăng: mỗi nhóm ≥100 USD ròng trong cửa sổ (trừ bán cùng cửa), mua-then-bán không đếm, nhóm mua cửa ngược cùng thị trường trong cửa sổ không đếm; tổng các nhóm đếm ≥500 USD. Khối lượng thị trường tại kích hoạt ≥10.000 USD tính tới thời điểm kích hoạt (cộng dồn, không dùng volumeNum cuối). Chặn giá: giá copy thô hơn nhóm đầu >0,10 → bỏ. Dải giá sau phạt 0,10–0,90, ngoài → bỏ + đếm riêng; bị loại vì giá >20% tổng kích hoạt → bảng chính mất đại diện, phải ghi. 6h và 50/200 USD chỉ báo cáo phụ.

## 7. Q5 — Giá copy: VWAP → phạt → cổ phần → phí

(1) VWAP theo tiền của giao dịch sau kích hoạt, cộng dồn đủ 100 USD trong tối đa 60 phút; không đủ → bỏ (thiếu độ sâu); (2) phạt = max(0,02; spread nếu có) — backtest không spread lịch sử → 0,02; (3) giá copy = gốc + phạt; (4) cổ phần = 100/giá copy; (5) phí = cp × rate × giá × (1−giá); (6) thắng: cp × giá chốt − 100 − phí; thua: −100 − phí. Nhạy cảm 0,05/0,10 THAY THẾ (bắt buộc).

**Phí (ĐÃ DUYỆT):** thứ tự nguồn: (a) feeSchedule từng thị trường tại thời điểm tín hiệu; (b) bảng ngày dự phòng khi thiếu feeSchedule (ghi rõ dự phòng): 0 cả 2025; 0,03 từ 01-03 đến 30-06-2026; 0,05 từ 10-07-2026 (ngày này là SUY LUẬN từ câu "Lịch sử đã biết" của tổng hợp — chỉ đo trực tiếp 17-06-2026=0,03 và 19-07-2026=0,05); (c) cả hai thiếu → mã **FEE_MISSING** (tín hiệu rơi 01-07→09-07-2026 trên thị trường không feeSchedule): **bỏ tín hiệu + đếm riêng "thiếu phí" + báo động khi tỷ lệ >5% — KHÔNG phải cổng giết; không bao giờ tính lãi với phí 0.**

**Làm tròn (ĐÃ DUYỆT):** giá copy 4 chữ số thập phân (gần nhất); cổ phần giữ số lẻ trên giấy; phí làm tròn tới xu (gần nhất); so ngưỡng TRƯỚC khi làm tròn.

Lấy lịch sử `taker_only=false`. prices-history ≤15 ngày/request, hạt 300 giây.

## 8. Q6 — Tiền giấy

100 USD cố định mỗi tín hiệu, phí ngoài 100 USD, không gấp thếp. Mẫu số duy nhất: lãi/(100×n). Tối đa 10 lệnh mở (≤1.000 USD); đủ 10 → bỏ theo thứ tự thời gian + đếm riêng "đầy vốn". Lý do bỏ đếm riêng: thiếu độ sâu / không giao dịch 60 phút / đầy vốn / ngoài dải / chặn giá / thiếu nhãn 999 / thiếu phí. Tỷ lệ bỏ >30% → cổng không qua + phạm vi áp dụng hẹp. Báo cáo tách dải 0,10–0,30/0,30–0,70/0,70–0,90 + môn + sự kiện; lãi chỉ nhờ một dải/sự kiện → ghi mong manh.

## 9. Q7 — Copy lệnh vào, giữ tới chốt

Giữ tới chốt chính thức, một luật thoát duy nhất. NGUỒN CHỐT (§19.2 ĐÃ DUYỆT): chính = `/v2/resolutions` `payouts` (micro-USDC; giá chốt = payouts[outcome_index]/1.000.000); đối chiếu = Gamma `umaResolutionStatus='resolved'` + `outcomePrices`; positions KHÔNG bao giờ là nguồn; hai nguồn lệch → DỪNG tính lãi tín hiệu đó, báo lệch, đưa vào ân hạn; sau ân hạn vẫn lệch = "chưa chốt chắc", không thắng không thua, nhập tỷ lệ chưa chốt cổng 8. Hòa 0,5: cp×0,5−100−phí (không trả lại stake); hủy lấy giá chốt thật. Ân hạn 14 ngày sau cuối đoạn; tỷ lệ chưa chốt sau ân hạn >10% → cổng không qua. Thời gian chờ chốt báo cáo riêng.

## 10. Q8 — Chọn k*

k=1–5 theo nhóm; k=1 đối chứng định nghĩa giống hệt. Chỉ tối ưu trên đoạn 2 (T1→T2). Mỗi k ≥100 tín hiệu trong mẫu mới được xét. Điểm_k = ROI_k − std/100/√n_k. Điều kiện cả ba: Điểm>0, ROI>0, ROI ≥ ROI₁+0,03. Không k nào thỏa → dừng sàng lọc, không chọn k*. Hai k chênh Điểm <0,02 → chọn nhiều tín hiệu hơn. Khóa k*, test đúng 1 lần đoạn 3 (T2→T3); không quay lại. Phụ đếm theo tiền chỉ mô tả. Không tối ưu biến khác trên đoạn 2.

## 11. Q9 — Cổng giết 3 tầng (D1: tầng 3 chỉ cờ)

Ngưỡng "lớn hơn hẳn", không làm tròn lên. **Tầng 1 (phải qua hết):** (1) trong mẫu ≥100, ngoài mẫu ≥100, tổng ≥200 (đếm theo kích hoạt); (2) ngoài mẫu lãi ròng >0; (3) vẫn >0 khi thay phạt 0,05 (tính lại toàn bộ); (4) ROI ngoài mẫu >5%; (5) ROI ngoài mẫu > k=1 cùng công thức; (6) trong mẫu dương và > k=1; (7) top-5 <50% tổng lãi ngoài mẫu, top-1 <25%, bỏ top-10 vẫn >0; (8) tỷ lệ bỏ ≤30% VÀ tỷ lệ chưa chốt sau ân hạn ≤10%. **Tầng 2:** CI 95% bootstrap GOM THEO SỰ KIỆN của ROI ngoài mẫu nằm hoàn toàn trên 0 VÀ ROI >5%; khoảng chứa 0 → "chưa đủ bằng chứng". **Tầng 3 (CHỈ CỜ, D1):** giải >50% lãi; môn duy nhất là nguồn lãi trong khi môn khác lỗ nặng; lãi bỏ World Cup >0; top-3 sự kiện % lãi. **Verdict:** thiếu tầng 1 → CHẾT; qua T1 thiếu T2 → CHƯA ĐỦ BẰNG CHỨNG; qua cả hai → SỐNG (backtest; vẫn phải qua test về trước mới bàn tiếp).

**Giải lớn (ĐÃ DUYỆT, chỉ mô tả):** sự kiện ≥8 thị trường con VÀ khối lượng cộng dồn TỚI CUỐI ĐOẠN đang xét thuộc top 5% sự kiện thể thao của đoạn đó; KHÔNG dùng volumeNum cuối (chỉ dùng mô tả sau chốt nếu không dựng được); KHÔNG dùng chọn người, KHÔNG dùng chọn k*, KHÔNG quyết D1.

## 12. Q10 — Test giấy về trước (D2: cohort mới tại GO; CHƯA CHẠY ở lần này)

Chỉ sau tầng 1+2 và kiểm toán độc lập CONFIRMED. Tại ngày GO chọn lại 20 nhóm bằng Q3 từ 90 ngày trước GO. Chu kỳ thăm dò 5 PHÚT (số đã duyệt); khi kích hoạt gọi `/book` đúng 1 LẦN: spread = best_ask − best_bid; phạt = max(0,02; spread); sổ rỗng/404 → 0,02 + đếm riêng (ĐÃ DUYỆT). Ngân sách +1 request/tín hiệu, ghi trước; 429 → dừng, chờ Retry-After; thiếu >10% ngày hoặc đúng cao điểm → test vô hiệu. Giữa kỳ 200 đã chốt (chỉ kiểm số lượng/chất lượng). Cuối: ≥500 đã chốt + ≥90 ngày, mốc nào sau, tối đa 12 tháng; +30 ngày chờ chốt sau thu thập; bắt đầu đầu mùa thường.

## 13. 18 bảng báo cáo (nhãn bắt buộc)

1 môn (mô tả) · 2 loại thị trường (mô tả) · 3 mùa/playoff/giải lớn + World Cup + lãi bỏ WC (mô tả + cờ) · 4 dải giá (mô tả + cờ) · 5 độ lớn (mô tả) · 6 top-3 sự kiện (mô tả) · 7 hao hụt hoạt động (mô tả) · 8 tỷ lệ bỏ + lý do, gồm thiếu phí (TÍNH ĐIỂM) · 9 chưa chốt sau ân hạn (TÍNH ĐIỂM) + thời gian chờ (mô tả) · 10 k=1 đối chứng (TÍNH ĐIỂM) · 11 phụ tiền/50-200/6h-24h (mô tả, CẤM cứu verdict) · 12 nhạy cảm 0,05 (TÍNH ĐIỂM) / 0,10 (mô tả) · 13 bỏ vì giá (mô tả) · 14 độ trễ forward (mô tả) · 15 ghi chú giới hạn (mô tả) · 16 thị trường con cùng sự kiện bị bỏ (mô tả) · 17 kết quả cổng T1+T2 (in cổng) · 18 ngày thiếu dữ liệu + ngân sách (mô tả).

## 14. D1–D5 (đã chốt, giữ nguyên)

D1 cờ không cổng · D2 nhóm mới tại GO · D3 mỗi nhóm ≥100 USD ròng, tổng ≥500 · D4 24h + chặn giá 0,10 (6h phụ) · D5 80 lệnh.

## 15. Bảy mục đã duyệt ngày 2026-11-02 (nguyên văn giá trị, nay là LUẬT)

1. **Mốc B:** T0 2025-09-13 / T1 2025-12-12 / T2 2026-03-12 / T3 2026-06-10 (90 ngày/đoạn, tránh World Cup).
2. **Phí thiếu:** FEE_MISSING, bỏ + đếm riêng + báo động >5%, không phải cổng giết.
3. **Giải lớn:** khối lượng cộng dồn tới cuối đoạn, ≥8 thị trường con, top 5%, chỉ mô tả, không chọn người/k*.
4. **50 ví đối chứng + missed 20%:** chỉ phương pháp đo thiên lệch, 20% chỉ báo động.
5. **Spread về trước:** chu kỳ 5 phút, /book đúng 1 lần khi kích hoạt, spread = best_ask − best_bid, sổ rỗng/404 → 0,02 + đếm riêng.
6. **Làm tròn:** giá 4 chữ số, cổ phần giữ số lẻ trên giấy, phí tới xu, so ngưỡng trước khi làm tròn.
7. **Tags dự phòng:** chỉ khi tags vẫn rỗng sau include_tag=true, đếm riêng tỷ lệ dùng.

## 16. Code đi kèm

`~/Downloads/Polymarket/copytrade_build_v2/` (khớp spec này; test 120/120 pass trên dữ liệu giả; không thay đổi sau đóng băng trừ lỗi cú pháp không chạm luật — mọi thay đổi phải ghi FREEZE_LOG).

## 17. MỤC KIỂM TRA OVERLAP VỚI PAPERDESK — CHỈ MÔ TẢ (viết vào spec đóng băng TRƯỚC khi chạy backtest, không phải sửa sau khi thấy kết quả)

> **NHÃN: CHỈ MÔ TẢ — CẤM CỨU VERDICT.** Mục này KHÔNG dùng chọn k*, KHÔNG lật verdict chính của copytrade (Việc B), KHÔNG lật verdict D2 của PaperDesk, KHÔNG tạo cổng giết mới. Mục đích duy nhất: xem lệnh giấy PaperDesk có trùng giao dịch của 20 nhóm Polymarket hay không — biết hai hệ thống có đang nhìn cùng một kèo không.

**C1. Nguồn, chỉ đọc:** (A) Sổ PaperDesk trên máy, chỉ các dòng BET_PAPER; KHÔNG sửa sổ, KHÔNG chạy lại PaperDesk, KHÔNG đổi luật PaperDesk; ghi đường dẫn, số dòng, khoảng ngày. (B) 20 nhóm từ Việc B đoạn 1 mốc B + giao dịch của chúng trong đoạn 2, 3 mốc B; không dùng nhóm chọn lại từ dữ liệu sau, không dùng nhóm thăm dò nhỏ trước.

**C2. Định nghĩa overlap — viết trước, không đổi sau:** khóa trùng = cùng conditionId VÀ cùng token/outcome (token id hoặc outcome index; KHÔNG dùng chữ YES/NO hay tên đội làm khóa duy nhất). Mỗi dòng PaperDesk phải có trường ánh xạ (pm_event_id / market_id / leg identity); không ánh xạ được → đếm riêng bảng không-ánh-xạ, không đoán mã; tỷ lệ không ánh xạ >20% số dòng PaperDesk trong kỷ nguyên B → kiểm tra overlap là THIẾU DỮ LIỆU ÁNH XẠ, dừng và báo, không kết luận overlap thấp. Cửa sổ CHÍNH duy nhất: giao dịch nhóm trong 24 giờ TRƯỚC lệnh PaperDesk. Hai cửa sổ phụ chỉ mô tả: nhóm trong 24h SAU; cùng ngày lịch. Không chọn cửa sổ theo kết quả đẹp. Phạm vi: chỉ lệnh PaperDesk trong kỷ nguyên B (13-09-2025 → 10-06-2026); sổ không phủ hết → ghi khoảng phủ thật + số lệnh trong phủ, không suy ra ngoài.

**C3. Bảng bắt buộc (không bỏ bảng nào):** (1) tổng lệnh PaperDesk trong khoảng phủ / ánh xạ được / không được + tỷ lệ; (2) tỷ lệ overlap chính = lệnh có ≥1 nhóm cùng mã+cửa trong 24h trước / số lệnh ánh xạ được; (3) overlap theo k: ≥1, ≥2, ≥3 NHÓM (không đếm ví); (4) lãi mỗi lệnh PaperDesk tách overlap / không-overlap: số lệnh, lãi trung bình/lệnh, sai số, khoảng tin cậy đơn giản — KHÔNG dùng để tuyên bố PaperDesk thắng/thua (PaperDesk có verdict riêng); (5) overlap theo môn / dải giá / sự kiện lớn (mô tả); (6) sự kiện overlap cao nhất và thấp nhất (mô tả, không dùng chọn sự kiện lần sau).

**C4. Cách đọc kết quả — chốt trước, không đổi sau:** overlap chính <30 lệnh → THIẾU MẪU cho kiểm tra overlap, không tăng/giảm sự tự tin, không nói "overlap thấp nên hai hệ thống khác nhau". Tỷ lệ overlap chính <20% VÀ ≥30 lệnh → hai hệ thống khác nhau là chính; hành động: giữ hai hệ thống tách riêng, không bắt hệ thống này theo hệ thống kia, không đổi luật — đây là bằng chứng hai hệ thống khác nhau, không phải thất bại. Lệnh overlap lãi/lệnh CAO hơn không-overlap VÀ khoảng tin cậy không chứa 0 → GIẢ THUYẾT cho spec v2 (viết spec v2 mới, đóng băng mới, test kỷ nguyên mới); KHÔNG thêm bộ lọc "chỉ đánh khi overlap" vào PaperDesk hay copytrade trong spec v1 này. Lệnh overlap ≤ không-overlap → không có sự tự tin thêm; ghi rõ overlap không giúp PaperDesk trong kỷ nguyên B. **Mọi trường hợp: kết quả overlap KHÔNG đổi verdict Việc B, KHÔNG đổi verdict D2 PaperDesk, KHÔNG cứu verdict đã trượt cổng giết.**

## 18. Cấm sau khi đóng băng

Không sửa spec sau khi thấy kết quả hồ sơ/backtest. Không nâng cờ D1 hay báo động 999/5% thiếu phí thành cổng giết. Không dùng kết quả overlap để đổi spec copytrade, đổi luật PaperDesk, đổi k*, hay cứu verdict. Không chuyển sang test giấy về trước, không kích hoạt PaperDesk, không áp bộ lọc overlap khi chưa có lệnh GO riêng của chủ nhân.
