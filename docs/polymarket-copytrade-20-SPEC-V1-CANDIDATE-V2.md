# SPEC v1 ỨNG VIÊN (CANDIDATE) V2 — COPY TRADE 20 TÀI KHOẢN POLYMARKET, CHỈ TRÊN GIẤY

Ngày viết: 2026-11-02. Bản V2 của `polymarket-copytrade-20-SPEC-V1-CANDIDATE.md` (sha256 `0cc46805…79938f`, giữ nguyên không ghi đè), sửa theo 7 mục trong prompt sửa của chủ nhân sau báo cáo kiểm toán coordinator.

---

# ⛔ CHƯA ĐÓNG BĂNG — CHƯA CÓ HASH ĐÓNG BĂNG — CHƯA CHẠY TÍNH ĐIỂM ⛔

File này CHƯA phải spec đóng băng. Đóng băng chỉ sau khi: coordinator xác nhận lại các điều kiện §19 + chủ nhân chọn đề xuất mốc A/B + duyệt các mục còn ngỏ (mục 21) + lệnh GO riêng.
Mọi kết quả tính điểm chạy trước khi đóng băng đều KHÔNG được tính.

## Nguồn đã dùng (đã cập nhật theo Sửa 1)

| File | sha256 |
|---|---|
| `polymarket-copytrade-20-answers-SYNTHESIS-6-GOC.md` | `cf6f7560c4dc6a1ff4f56bfb7925ba955bcc67b6768072d7cc088868764a4617` (khớp coordinator 100%) |
| **`polymarket-copytrade-20-QUYET_DINH_OWNER_2026-11-02.md` — file Coordinator** | `01248d550391824d208a5bf49ca6650054d8f179950e32b4fcc11edce939a3a0` — **đã thay file, hash khớp đúng** |
| `…QUYET_DINH_OWNER_2026-11-02_BAN-DAN-CHAT-DAU.md` (bản tôi ghi từ nội dung chủ nhân dán chat, chỉ còn giá trị bằng chứng) | `6772eec7a4eeda6102b017a8ba241f325d11f9ff0afd40b3ab9a24214a511c7f` |
| `polymarket-copytrade-20-SPEC-V1-DRAFT-V2.md` | `8e108e30612c0997ca3a708468247f890916a92058d79a934e9dc7ba08153406` |
| `polymarket-copytrade-20-PROBE-REPORT-V2.md` | `2782eb5cd6bd3b03264c9fa5717245e541605bab0589fdd54865c1a529b43c32` |
| `polymarket-copytrade-20-SPEC-V1-CANDIDATE.md` (bản V1, giữ nguyên) | `0cc4680515f02d7f585a6f393b87ce662058ac37ce96fe03c75de95be979938f` |
| Code V2 | `~/Downloads/Polymarket/copytrade_build_v2/` (code V1 giữ nguyên tại `copytrade_build_v1/`) |

## BẢNG TRẠNG THÁI §19 (Sửa 2 — theo đúng file quyết định coordinator)

| Mục | Trạng thái | Điều kiện / ghi chú |
|---|---|---|
| 19.1 tag 'Sports' | **DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN** | Điều kiện: file V2 cho thấy đủ 23 mẫu thật + luật viết thành từng bước. Cả hai đã có ở báo cáo V2/spec; **chờ coordinator xác nhận lại khi kiểm toán** thì mới là luật đầy đủ. |
| 19.2 ưu tiên resolutions.payouts, lệch → dừng và báo | **ĐÃ DUYỆT** | Luật. |
| 19.3 cửa 999 loại + đếm riêng + báo động trên 5% | **ĐÃ DUYỆT (làm BÁO ĐỘNG)** | Chưa phải cổng giết; cấm nâng lên sau khi đóng băng. |
| 19.4 usdc_size activity làm tiền chính, trades đối chiếu | **ĐÃ DUYỆT** | Luật. |
| 19.5 pool từ leaderboard tháng + tự tính 90 ngày + đo thiên lệch | **DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN** | Điều kiện: cách đo thiên lệch viết rõ trong spec (đã viết ở mục 5); **tham số 50 ví đối chứng là TỰ CHỌN chờ duyệt** (mục 20.6). |
| 19.6 ngày chốt về giây UTC, làm tròn xuống giây | **ĐÃ DUYỆT** | Luật. |
| 19.7 làm tròn giá/cổ phần/phí | **CHƯA DUYỆT CHI TIẾT** | Toàn bộ mục 20.3 là ĐỀ XUẤT. |
| 19.8 mốc tuyệt đối T0–T3 | **CHƯA DUYỆT CHI TIẾT** | Hai đề xuất A/B ở mục 2 — chờ chủ nhân chọn. |
| 19.9 đo spread cho test về trước | **DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN** | Điều kiện: chu kỳ + công thức viết rõ (đã viết ở mục 12); **số chu kỳ 5 phút là ĐỀ XUẤT chờ duyệt số cụ thể**. |

Code V2 khớp bảng này qua `config.S19_STATUS` (config.py dòng 91–100); các hằng của mục điều kiện ghi chú "TỰ CHỌN/điều kiện, chờ kiểm toán V2" trong `config.SELF_CHOSEN` (dòng 125–134).

## 0. Ranh giới cứng (giữ nguyên V1)

Chỉ trên giấy, 0 đồng, không lệnh thật, không tiền thật, không nối ví, không tạo tài khoản mới, không VPN. Không ghi bí mật vào file/log/chat. Luật dừng thu thập: 429/403/throttle/chậm bất thường → DỪNG TOÀN BỘ, không retry ngay, không tăng tốc bù; không collector burst 10 giây. Ngân sách đã duyệt: ~200 request/ngày, 10 giây/request, sàng lọc rẻ trước, ví kiểu UpTheBlues không đi hết lịch sử bằng mọi giá, hạn 14 ngày hồ sơ; hết hạn k≥3 thiếu 100 tín hiệu trong mẫu → theo luật (đổi k đủ mẫu hoặc ghi thiếu mẫu), không hạ ngưỡng, không đổi cửa sổ/k sau khi thấy ngoài mẫu. Không sửa spec sau khi thấy kết quả. Không dùng tóm tắt chat thay file gốc. Không nâng cờ D1/999 thành cổng sau khi đóng băng. Không dùng endpoint fee-rate cũ.

## 1. Thuật ngữ và đơn vị (giữ nguyên V1)

Giây UTC; 1 ngày = 86.400 giây; RFC3339 → epoch giây làm tròn XUỐNG (19.6 ĐÃ DUYỆT). Tiền lệnh = `usdc_size` trên `/v2/activity?type=TRADE` (19.4 ĐÃ DUYỆT), `price×size` trades chỉ đối chiếu. `condition_id`/`token_id`/`outcome_index`; 999 = thiếu nhãn (19.3). Cổ phần 1/0/0,5 USD. Ví/nhóm; k tính theo nhóm. VWAP theo tiền. ROI = lãi ròng / tổng tiền đặt; mẫu số copy = 100 × số tín hiệu đã lấy. Lãi giữ-tới-chốt = cp × giá chốt − tiền mua − phí theo ngày.

## 2. Dòng thời gian 3 đoạn 90 ngày — HAI ĐỀ XUẤT (Sửa 4, KHÔNG tự đổi mốc)

Cấu trúc bất biến: 3 đoạn 90 ngày liên tiếp không trống không chồng, giây UTC; dữ liệu đoạn 1 chỉ dùng thông tin tới cuối đoạn 1; tín hiệu gán theo thời điểm kích hoạt; không rút 60 ngày; thiếu → ghi thiếu mẫu.

### ĐỀ XUẤT A (giữ nguyên mốc V1 — CHỜ CHỦ NHÂN CHỌN)

T3 = 2026-10-19T00:00:00Z (1792368000); T2 = 2026-07-21 (1784592000); T1 = 2026-04-22 (1776816000); T0 = 2026-01-22 (1769040000).

| Đoạn | Khoảng | Mùa giải rơi vào |
|---|---|---|
| 1 chọn người | 22-01 → 22-04-2026 | NBA mùa thường; **Super Bowl (02-02) nằm trong đoạn**; NHL/英超 mùa thường; MLB khởi động cuối đoạn; NFL nghỉ |
| 2 trong mẫu | 22-04 → 21-07-2026 | **FIFA World Cup 11-06 → 19-07 gần như trọn đoạn**; NBA playoffs + chung kết; NHL playoffs; MLB mùa thường; Pháp Open; Wimbledon |
| 3 ngoài mẫu | 21-07 → 19-10-2026 | Sau World Cup; NFL mùa trước + đầu mùa thường; MLB chặng cuối; US Open tennis; NBA/NHL khởi động tháng 10 |

Ưu điểm: dữ liệu mới nhất (chỉ lùi ~2 tuần tới giờ). Nhược điểm: **k* được tối ưu trên mẫu có World Cup** — điều tổng hợp lo ngị nhất (lợi nhuận có thể thuộc "mùa World Cup"), holdout không có World Cup để đối chiếu.

### ĐỀ XUẤT B (tránh World Cup hoàn toàn — CHỜ CHỦ NHÂN CHỌN)

T3 = 2026-06-10T00:00:00Z; T2 = 2026-03-12; T1 = 2025-12-12; T0 = 2025-09-13. (Đủ 90 ngày mỗi đoạn: 13-09→12-12-2025, 12-12→12-03, 12-03→10-06.)

| Đoạn | Khoảng | Mùa giải rơi vào |
|---|---|---|
| 1 chọn người | 13-09-2025 → 12-12-2025 | NFL 2025 mùa thường; MLB playoffs 2025; NBA/NHL khai màn 10-2025 |
| 2 trong mẫu | 12-12-2025 → 12-03-2026 | NFL playoffs + **Super Bowl (02-02-2026)**; NBA/NHL mùa thường; bóng đá châu Âu mùa đông |
| 3 ngoài mẫu | 12-03 → 10-06-2026 | MLB khai màn; NBA/NHL playoffs (04→06); chung kết NBA chạm mép T3; Champions League knockout + chung kết; Pháp Open. **World Cup bắt đầu 11-06 = sau T3 → loại hẳn** |

Ưu điểm: cả 3 đoạn không chứa World Cup → không bị một giải lớn chi phối mẫu. Nhược điểm: dữ liệu cũ hơn ~4 tháng so với A; đoạn 2 chứa Super Bowl + NFL playoffs (vẫn có giải lớn, chỉ nhỏ hơn); lệch mùa (NFL 2025 ≠ NFL 2026); đến ngày GO dữ liệu đoạn 3 đã 5+ tháng tuổi — thị trường/phí đã đổi giữa chừng (phí 0,03 → 0,05 nằm đúng đoạn 2/3 của B, may là bảng theo ngày xử lý được).

**Cả A và B đều là ĐỀ XUẤT CHỜ CHỦ NHÂN CHỌN, không phải luật. KHÔNG có code chọn mốc tự động, KHÔNG có code tối ưu mốc theo kết quả** (chỉ có hằng vô hiệu — xem nhật ký Sửa 4).

## 3. Q1 — Chỉ thể thao, trận đơn, trước trận

Như V1, với phân định trạng thái đúng (Sửa 2): luật nhận diện tag 'Sports' là **DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN** — điều kiện "đủ 23 mẫu thật + luật từng bước" đã được thỏa ở báo cáo V2 (23/23 mẫu) và luật đã viết từng bước, **chờ coordinator xác nhận lại** trong đợt kiểm toán này; đến lúc đó mới thành luật đầy đủ. Từng bước: (1) Gamma `include_tag=true`; (2) thể thao ⇔ tag label 'Sports'; (3) phạm vi v1 ⇔ thể thao + sportsMarketType + gameStartTime + lệnh trước giờ bóng; (4) thể thao thiếu 2 trường = mùa vụ → loại khỏi v1, đếm riêng; (5) không dùng gameStartTime một mình; (6) 2 tag mâu thuẫn → theo 'Sports' + ghi bảng mô tả. Đường dự phòng tags rỗng: mục 20.1 (ĐỀ XUẤT). Báo cáo tách theo môn / loại thị trường / mùa / dải giá / độ lớn.

## 4. Q2 — Cửa sổ chọn 90 ngày đoạn 1 (giữ nguyên V1)

≥3 lệnh trong 14 ngày cuối; báo cáo hao hụt hoạt động; ghi mùa theo mục 2.

## 5. Q3 — Luật chọn 20 (D5 = 80 lệnh; pool có điều kiện)

10 cửa như V1 (50.000 USD; **80 lệnh**; 20 mã; lãi giữ-tới-chốt/d visit >0 + lãi đã chốt >0; 3 lệnh/14 ngày; 1 thị trường ≤50% lãi; both-sides >30% loại; bot >2.000 lệnh & <1% loại; xếp hạng hold-ROI, hòa: thị trường→lệnh→chữ cái; gộp trùng/min ≥50% & ≥20 lệnh & ≤60 phút, k theo nhóm, bù đủ 20).

**Pool ứng viên (19.5 — DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN):** hướng đã duyệt (leaderboard tháng → tự tính 90 ngày). Điều kiện "cách đo thiên lệch viết rõ" đã viết tại đây: hợp 4 bảng tháng phủ đoạn chọn; tự tính mọi chỉ số; **đo thiên lệch bằng mẫu đối chứng K ví lấy từ leaderboard `time_period=all&category=sports&sort_by=PNL` theo thứ tự giảm dần, bỏ những ví đã ở pool, lấy đủ K=50 (TỰ CHỌN — giải thích đầy đủ mục 20.6)**; đếm bao nhiêu ví đạt hết cửa Q3 = "ví giỏi bị missed"; tỷ lệ missed in trong báo cáo hồ sơ; **nếu tỷ lệ missed vượt 20% (TỰ CHỌN) thì báo động và ghi rõ pool thiên lệch mạnh — mức phản ứng cụ thể chờ chủ nhân duyệt, spec không tự định**.

## 6. Q4 — Overlap (D3, D4 đã chốt — giữ nguyên V1)

24h trượt theo giây; đếm vị thế ròng tăng; mỗi nhóm ≥100 USD ròng, tổng ≥500 USD; khối lượng tại kích hoạt ≥10.000 USD (cộng dồn tới thời điểm, không volumeNum cuối); chặn giá 0,10; dải 0,10–0,90; mỗi thị trường/sự kiện một lần; phe trước thắng; 6h + 50/200 USD chỉ phụ.

## 7. Q5 — Giá copy: VWAP → phạt → cổ phần → phí (Sửa 3 sửa toàn bộ phần phí)

Thứ tự khóa: (1) VWAP đủ 100 USD/60 phút; (2) phạt max(0,02; spread nếu có) — backtest không có spread lịch sử → 0,02; (3) giá copy; (4) cổ phần = 100/giá; (5) phí; (6) lãi = cp × giá chốt − 100 − phí (thua −100−phí). Nhạy cảm 0,05/0,10 thay thế.

**PHÍ — nguồn theo THỨ TỰ (Sửa 3):**
- **(a) feeSchedule của từng thị trường tại thời điểm tín hiệu** (cấu trúc `{exponent, rate, takerOnly, rebateRate}`, đã đo thật 0,03 trận 17-06-2026 và 0,05 trận 19-07-2026).
- **(b) Bảng ngày dự phòng** khi thị trường thiếu feeSchedule (phải ghi rõ là dự phòng): 0 cả năm 2025; 0,03 từ 01-03 đến 30-06-2026; 0,05 từ 10-07-2026. **Ghi rõ suy luận: ngày chuyển 10-07-2026 lấy NGUYÊN VĂN từ câu "Lịch sử đã biết" mục Q5.5 của file tổng hợp — thăm dò KHÔNG đo trực tiếp ngày này** (chỉ đo được 2 điểm 17-06=0,03 và 19-07=0,05 bao lấy nó).
- **(c) Khi cả (a) và (b) đều thiếu (tín hiệu rơi 01-07 → 09-07-2026 trên thị trường không feeSchedule): trả mã `FEE_MISSING` — KHÔNG trả 0, KHÔNG đoán 0,03/0,05.**

**Xử lý FEE_MISSING — ĐỀ XUẤT CHỜ DUYỆT (không phải luật đã chốt):** (i) bỏ tín hiệu đó; (ii) đếm riêng vào bảng tín hiệu bỏ, lý do "thiếu phí" (bảng 8); (iii) báo tỷ lệ thiếu phí = số thiếu / (lấy + bỏ); (iv) **ngưỡng báo động ĐỀ XUẤT: trên 5% (TỰ CHỌN, cùng mức với báo động 999) — vượt ngưỡng phải xem lại dữ liệu phí trước khi tiếp tục; ngưỡng chưa được nâng thành cổng giết.**

Làm tròn: mục 20.3 (CHƯA DUYỆT CHI TIẾT). `taker_only=false`; prices-history ≤15 ngày/request hạt 300 giây.

## 8. Q6 — Tiền giấy (giữ nguyên V1 + lý do bỏ thêm thiếu phí)

100 USD cố định; mẫu số 100×n; tối đa 10 lệnh mở; mọi lý do bỏ đếm riêng — **V2 thêm lý do "thiếu phí" (FEE_MISSING)**; tỷ lệ bỏ >30% → cổng không qua; tách dải giá/môn/sự kiện.

## 9. Q7 — Copy lệnh vào, giữ tới chốt (giữ nguyên V1)

19.2 ĐÃ DUYỆT: nguồn chính resolutions.payouts (micro-USDC), Gamma umaResolutionStatus + outcomePrices đối chiếu, positions không bao giờ là nguồn; lệch → dừng tính lãi, báo lệch, ân hạn, sau ân hạn vẫn lệch = "chưa chốt chắc" nhập tỷ lệ chưa chốt cổng 8. Hòa 0,5 = cp×0,5−100−phí. Ân hạn 14 ngày; >10% chưa chốt → cổng không qua.

## 10. Q8 — Chọn k* (giữ nguyên V1)

k=1–5 theo nhóm; ≥100 tín hiệu trong mẫu; Điểm = ROI − std/100/√n; ba điều kiện (Điểm>0, ROI>0, ROI ≥ ROI₁+0,03); hòa Điểm <0,02 chọn nhiều tín hiệu; khóa k*, test một lần.

## 11. Q9 — Cổng giết 3 tầng (D1 đã chốt: tầng 3 chỉ cờ — giữ nguyên V1)

Tầng 1: 8 cổng (100/100/200; dương; nhạy cảm 0,05; ROI>5%; hơn k=1; trong mẫu dương hơn k=1; top1<25% & top5<50% & bỏ top-10 dương; bỏ ≤30% & chưa chốt ≤10%). Tầng 2: CI 95% bootstrap gom sự kiện hoàn toàn trên 0 và ROI>5%. Tầng 3: cờ (giải >50%; môn duy nhất; bỏ World Cup dương; top-3 sự kiện). Verdict CHẾT / CHƯA ĐỦ BẰNG CHỨNG / SỐNG.

## 12. Q10 — Test giấy về trước (D2 đã chốt: cohort mới; 19.9 có điều kiện)

Chọn lại 20 nhóm bằng Q3 từ 90 ngày trước GO. Ghi sổ giấy. Ví dụ chu kỳ thăm dò 5 phút. **Đo spread (19.9 — DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN): hướng đã duyệt; công thức đã viết: khi phát hiện kích hoạt gọi /book đúng 1 lần, spread = best_ask − best_bid, phạt = max(0,02; spread), sổ rỗng/404 → 0,02 + đếm riêng. SỐ CHU KỲ 5 PHÚT LÀ ĐỀ XUẤT chờ chủ nhân duyệt số cụ thể** (5 phút lấy từ ví dụ của chính tổng hợp Q10, không phải số đo được). Ngân sách +1 request/tín hiệu; thiếu >10% ngày → test vô hiệu. Giữa kỳ 200 đã chốt; cuối ≥500 đã chốt + ≥90 ngày, tối đa 12 tháng; +30 ngày chốt xong sau thu thập; bắt đầu đầu mùa thường.

## 13. 18 bảng báo cáo (giữ nguyên V1; bảng 8 thêm lý do thiếu phí)

Như V1 — bảng 8 (tỷ lệ bỏ + lý do) nay gồm cả "thiếu phí"; các bảng chạm verdict: 8, 9, 10, 12; bảng 11 cấm cứu verdict.

## 14. D1–D5 đã chốt (giữ nguyên V1, trích file quyết định coordinator hash 01248d55…)

D1 cờ không cổng; D2 nhóm mới tại GO; D3 100/500 USD; D4 24h + 0,10 (6h phụ); D5 80 lệnh.

## 15. Trạng thái §19

Đã đưa lên đầu file (bảng sau nguồn) — đúng 3 nhóm: ĐÃ DUYỆT (19.2/19.3/19.4/19.6); DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN (19.1/19.5/19.9); CHƯA DUYỆT CHI TIẾT (19.7/19.8).

## 16. Code V2 đi kèm

`~/Downloads/Polymarket/copytrade_build_v2/` — code V1 giữ nguyên ở `copytrade_build_v1/`. Code V2 chứa: `config.S19_STATUS` (bảng trạng thái §19), mã `FEE_MISSING` + `fee_for_signal`/`split_signals_by_fee` (bỏ + đếm riêng tín hiệu thiếu phí), `classify_major_tournament` nhận khối lượng TỚI CUỐI ĐOẠN, registry `SELF_CHOSEN` mọi hằng tự chọn. 0 request API thật.

## 17. Điều kiện thành spec đóng băng (cập nhật V2)

1. Coordinator xác nhận lại 2 điều kiện còn treo: 19.1 (23 mẫu + luật từng bước) và nội dung file quyết định khớp (đã khớp hash — còn chờ xác nhận chính thức).
2. Chủ nhân CHỌN đề xuất mốc A hoặc B (mục 2) và duyệt: luật xử lý thiếu phí; định nghĩa giải lớn sau sửa volume; 50 ví đối chứng + ngưỡng missed 20%; số chu kỳ spread; quy tắc làm tròn; đường dự phòng tags rỗng.
3. Viết spec đóng băng + sha256 → chủ nhân kiểm tra → lệnh GO riêng.

## 18. KHÔNG làm (giữ nguyên V1)

Không lệnh thật/tiền/wallet/VPN; không chạy tính điểm; không chọn k*; không verdict; không sửa spec sau khi thấy kết quả; không nâng cờ D1/999 sau khi đóng băng.

---

## 20. ĐỀ XUẤT CHỜ DUYỆT CHI TIẾT (không phải luật)

### 20.1 Đường dự phòng khi tags rỗng (giữ nguyên V1)
smt khác rỗng → coi thể thao trận đơn; smt rỗng + chỉ gameStartTime → không coi thể thao (deadline phi thể thao cũng có), đưa danh sách tra lại; đếm và báo cáo.

### 20.2 Mốc T0–T3 (Sửa 4 — thay toàn bộ)
Hai đề xuất A và B kèm bảng mùa giải từng đoạn — xem mục 2. Cả hai CHỜ CHỦ NHÂN CHỌN. Không code tự chọn mốc.

### 20.3 Quy tắc làm tròn (giữ nguyên V1 — 19.7 CHƯA DUYỆT)
Giá copy 4 chữ số thập phân gần nhất; cổ phần giữ số lẻ; phí tới xu gần nhất; so ngưỡng trước khi làm tròn.

### 20.4 Định nghĩa "giải lớn" (Sửa 5 — thay toàn bộ, hết rò rỉ volume cuối)
**Đề xuất:** giải lớn = sự kiện có ≥ **8** thị trường con (TỰ CHỌN, chưa kiểm tra độ nhạy) VÀ khối lượng **cộng dồn TỚI CUỐI ĐOẠN đang xét** nằm trong **top 5%** (TỰ CHỌN, chưa kiểm tra độ nhạy) khối lượng sự kiện thể thao của đoạn đó — khối lượng tính bằng tổng tiền giao dịch tới cuối đoạn, **KHÔNG dùng volumeNum cuối cùng** (chứa giao dịch tương lai). **Nếu nguồn chỉ cho volumeNum cuối:** định nghĩa này chỉ dùng để **báo cáo mô tả SAU KHI đã chốt**, không dùng chọn người, không dùng chọn k*, không dùng quyết D1. Danh sách sự kiện bị coi là giải lớn + bằng chứng 2 điều kiện in kèm.

### 20.5 Chi tiết khác chờ duyệt
Chu kỳ spread 5 phút (số cụ thể); K=50 ví đối chứng; ngưỡng missed 20%; ngưỡng báo động thiếu phí 5%.

### 20.6 Giải thích 50 ví đối chứng (Sửa 6)
- **Lấy từ đâu:** leaderboard `time_period=all&category=sports&sort_by=PNL` (bảng mọi thời đại, thể thao, xếp theo lãi).
- **Chọn bằng luật nào:** đi từ trên xuống theo thứ hạng, **bỏ mọi ví đã có trong pool 4-bảng-tháng**, lấy đúng 50 ví đầu tiên — quy tắc tất định, không ngẫu nhiên, lặp lại được.
- **Đo thiên lệch bằng cách nào:** với 50 ví đó, tự tính lại đủ các chỉ số 90 ngày của đoạn chọn (khối lượng thể thao, số lệnh, lãi giữ-tới-chốt/đồng đặt, các cửa Q3) từ trades/activity; đếm số ví đạt HẾT các cửa Q3 nhưng không nằm trong pool → "ví giỏi bị missed"; tỷ lệ missed = số đó / 50.
- **Kết quả dùng để làm gì:** in trong báo cáo hồ sơ cạnh danh sách pool, để đọc kết quả backtest biết thiên lệch chọn mẫu của pool tháng.
- **Nếu vượt ngưỡng:** vượt 20% (TỰ CHỌN) → báo động, ghi rõ "pool thiên lệch mạnh, kết quả chỉ đại diện cho ví đang thắng gần đây"; mức phản ứng cụ thể (mở rộng pool bằng bảng week/all hay không) là quyết định của chủ nhân, spec không tự định.
- **Nguồn con số 50 và 20%:** KHÔNG có trong tổng hợp hay quyết định — là TỰ CHỌN của tôi, ĐỀ XUẤT chờ duyệt.

### 20.7 Bảng hằng TỰ CHỌN trong code (Sửa 6 — không hằng nào không có ghi chú)

| Hằng | Giá trị | Nguồn |
|---|---|---|
| `FEE_MISSING_ALERT` | 5% | TỰ CHỌN (ĐỀ XUẤT) — không có trong tổng hợp/quyết định |
| `MAJOR_MIN_MARKETS` | 8 | TỰ CHỌN (ĐỀ XUẤT) — chưa kiểm tra độ nhạy |
| `MAJOR_TOP_SHARE` | 5% | TỰ CHỌN (ĐỀ XUẤT) — chưa kiểm tra độ nhạy |
| `K_CONTROL` | 50 | TỰ CHỌN (ĐỀ XUẤT) — xem 20.6 |
| `N_BOOT` | 2.000 | TỰ CHỌN (kỹ thuật) — số lần bootstrap |
| `BOOTSTRAP_SEED` | 42 | TỰ CHỌN (kỹ thuật) — để kiểm toán lặp lại được |
| `MAX_PAGES` | 40 | TỰ CHỌN (an toàn) — trần phân trang mỗi stream |
| Watchdog độ trễ | >max(3× trung vị, +3s), ≥6 mẫu | TỰ CHỌN (an toàn) — đã kích hoạt đúng 1 lần thật ở V2 |
| User-Agent | `copytrade-paper/1.0` | TỰ CHỌN (kỹ thuật) |

Mọi hằng khác đều truy được về: tổng hợp SYNTHESIS-6-GOC (90/14/86.400; 50.000/80/20/3-14/50%/30%/2.000-1%; 50%-20-60 phút; 100-500/10.000/0,10/0,10–0,90; 100/60 phút/0,02/0,05-0,10; 10 lệnh mở/30%; 14 ngày/10%; k1–5/100/0,03/0,02; 100-100-200/5%/25%/50%/CI95), quyết định D1–D5 + §19 (80 lệnh; 999-5%; ~200 request/ngày/10 giây/14 ngày), hoặc quyết định coordinator hash 01248d55…

---

## 21. DANH SÁCH CẦN COORDINATOR KIỂM TOÁN + CHỦ NHÂN DUYỆT (trước khi đóng băng)

1. Coordinator: xác nhận chính thức 2 điều kiện §19.1 và §19.5/19.9 đã viết rõ; xác nhận hash file quyết định 01248d55… là bản chuẩn (đã khớp).
2. Chủ nhân: chọn mốc A hay B (mục 2); duyệt luật xử lý FEE_MISSING + ngưỡng 5%; duyệt định nghĩa giải lớn (đã sửa volume cuối đoạn) + 2 ngưỡng 8/5%; duyệt 50 ví + ngưỡng 20%; duyệt số chu kỳ spread (5 phút?); duyệt làm tròn (20.3); duyệt đường dự phòng tags rỗng (20.1).
3. Sau đó: viết spec đóng băng + sha256 → chủ nhân kiểm tra → lệnh GO riêng.

---

# NHẬT KÝ SỬA SO VỚI SPEC ỨNG VIÊN V1 (7 mục, kèm file/dòng/trước–sau)

**Sửa 1 — lệch hash file quyết định.** Sửa ở: `~/workspace/your_files/` (thay file quyết định) + spec này (bảng nguồn). Trước: nguồn ghi file quyết định hash `6772eec7…511c7f` (bản tôi ghi từ nội dung chat). Sau: file chuẩn là bản coordinator hash `01248d550391824d208a5bf49ca6650054d8f179950e32b4fcc11edce939a3a0` — **đã thay, hash khớp đúng 100%**; bản chat cũ giữ làm bằng chứng với hậu tố `_BAN-DAN-CHAT-DAU.md`. Diff toàn văn: khác 31→35 dòng, **toàn bộ là định dạng markdown** (thêm `#`/`##`, gạch đầu dòng, số thứ tự 1–4, dòng trống, thụt đầu dòng mục con) — **không khác nào về nội dung** D1–D5, §19.1–19.9, kế hoạch, danh mục cấm; spec V2 theo nội dung coordinator (khác biệt chỉ định dạng nên không chỗ nào trong thân spec phải đổi chữ). Xuất nguyên văn hai file kèm hash ở phụ lục báo cáo cuối.

**Sửa 2 — trả §19 đúng trạng thái duyệt.** Sửa ở: spec này (bảng trạng thái sau mục nguồn; các mục 3, 5, 12 đổi cách ghi) + code `copytrade_build_v2/src/config.py` dòng 91–100 (`S19_STATUS`) và 125–134 (`SELF_CHOSEN`). Trước: V1 chuyển 19.1–19.6, 19.9 thành luật tuyệt đối trong thân. Sau: bảng 3 trạng thái đúng theo file quyết định; thân spec ghi rõ "DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN — điều kiện: …" (19.1 chờ coordinator xác nhận lại; 19.5 ghi rõ 50 ví là TỰ CHỌN; 19.9 ghi rõ 5 phút là ĐỀ XUẤT chờ duyệt số cụ thể); code annotate "TỰ CHỌN/điều kiện, chờ kiểm toán V2".

**Sửa 3 — phí thiếu đầu tháng 7.** Sửa ở: spec mục 7 (nguồn phí a→b→c + FEE_MISSING + xử lý ĐỀ XUẤT + ghi rõ 10-07 là suy luận từ tổng hợp, chưa đo trực tiếp), mục 8 (lý do bỏ "thiếu phí"); code `ledger.py` dòng 13–54 (`fee_rate` trả mã `FEE_MISSING`, mới: `fee_for_signal`, `split_signals_by_fee`), `config.py` dòng 104–112, `report.py` dòng 72. Trước: `fee_rate` trả `(None, 'THIẾU_khoảng…')` và spec không nói tín hiệu xử lý ra sao. Sau: mã `FEE_MISSING` rõ ràng; tín hiệu thiếu phí bị BỎ + đếm riêng lý_do_thiếu_phí; không bao giờ tính lãi với phí 0 im lặng; test T13 chứng minh (ts 05-07-2026 không feeSchedule → FEE_MISSING, tín hiệu bị bỏ).

**Sửa 4 — mốc T0–T3.** Sửa ở: spec mục 2 (hai đề xuất A/B + 2 bảng mùa giải + ưu/nhược). Trước: một đề xuất duy nhất (A) ghi như "đề xuất". Sau: A giữ nguyên + B (tránh World Cup hoàn toàn), cả hai là ĐỀ XUẤT chờ chọn; **không viết code chọn mốc tự động** (code V2 không có hàm nào chọn mốc — kiểm chứng bằng không tồn tại symbol chọn mốc trong `src/`).

**Sửa 5 — giải lớn rò rỉ volume cuối.** Sửa ở: spec mục 20.4; code `report.py` dòng 81–108 (`classify_major_tournament(event, seg_end_cum_volume, universe_seg_end_volumes)`). Trước: định nghĩa dùng `volumeNum` cuối cùng (chứa tương lai). Sau: khối lượng **cộng dồn tới cuối đoạn đang xét**; nếu chỉ có volumeNum cuối → trả "chỉ_mô_tả_sau_chốt", không dùng chọn người/k*/D1; ngưỡng 8 & 5% ghi TỰ CHỌN chưa kiểm tra độ nhạy; test T14: sự kiện volume cuối 1.000.000 nhưng cuối đoạn 4.000 → KHÔNG phải giải lớn.

**Sửa 6 — giải thích 50 ví + bảng hằng tự chọn.** Sửa ở: spec mục 20.6 (giải thích đầy đủ 50: nguồn bảng all, luật chọn tất định, cách đo, công dụng, hành động vượt ngưỡng 20% — cả hai con số ghi TỰ CHỌN) + mục 20.7 (bảng 9 hằng tự chọn, không hằng nào thiếu ghi chú); code `config.py` dòng 117–134. Trước: 50 xuất hiện không giải thích; các hằng kỹ thuật không ghi nguồn. Sau: đủ giải thích + registry `SELF_CHOSEN` + test T15 kiểm tra registry đầy đủ.

**Sửa 7 — test kiểm toán được.** Sửa ở: `copytrade_build_v2/tests/test_synthetic.py` (toàn bộ V1 + dòng 645–675 `V1_FIX_AUDIT` ghi 1 lỗi code thật + 6 lỗi soạn thảo, mỗi lỗi có trước–sau và dòng luật chứng minh; T13/T14/T15 mới; output `test_report_v2.json` kèm mục `v1_fix_audit`). Trước: báo cáo test chỉ nói số liệu. Sau: từng test có tên/dữ liệu vào/đáp án mong đợi/kết quả thật/pass-fail; 7 lỗi bản V1 liệt kê trước–sau kèm luật; thêm test cho Sửa 2/3/5. Trong V2 có 2 chỉnh test: (1) kỳ vọng sentinel phí đổi `THIẾU_khoảng…` → `FEE_MISSING` theo LỆNH Sửa 3 (chứng minh: prompt sửa mục Sửa 3); (2) sửa lỗi cắt chuỗi bảng trạng thái của chính tôi (soạn thảo). Kết quả: **69 test / 120 record, 120 pass / 0 fail** (bảng đầy đủ trong `tests/test_report_v2.json`).
