# SPEC v1 ỨNG VIÊN (CANDIDATE) — COPY TRADE 20 TÀI KHOẢN POLYMARKET, CHỈ TRÊN GIẤY

Ngày viết: 2026-11-02. Trạng thái: **SPEC ỨNG VIÊN CUỐI, DỰA TRÊN D1–D5 ĐÃ ĐƯỢC CHỦ NHÂN CHỐT**.

---

# ⛔ CHƯA ĐÓNG BĂNG — CHƯA CÓ HASH ĐÓNG BĂNG — CHƯA CHẠY TÍNH ĐIỂM ⛔

File này CHƯA phải spec đóng băng. Đóng băng chỉ xảy ra sau khi: coordinator kiểm toán xong file V2 gốc
+ chủ nhân duyệt chi tiết các mục còn để ngỏ (mục 20) + chủ nhân ra lệnh GO riêng.
Kết quả bất kỳ bước tính điểm nào chạy trước khi đóng băng đều KHÔNG được tính.

---

## Nguồn đã dùng, kèm mã hash để coordinator đối chiếu

| File | sha256 |
|---|---|
| `polymarket-copytrade-20-answers-SYNTHESIS-6-GOC.md` | `cf6f7560c4dc6a1ff4f56bfb7925ba955bcc67b6768072d7cc088868764a4617` |
| `polymarket-copytrade-20-QUYET_DINH_OWNER_2026-11-02.md` (chủ nhân dán qua chat, agent ghi lại nguyên văn) | `6772eec7a4eeda6102b017a8ba241f325d11f9ff0afd40b3ab9a24214a511c7f` |
| `polymarket-copytrade-20-SPEC-V1-DRAFT-V2.md` | `8e108e30612c0997ca3a708468247f890916a92058d79a934e9dc7ba08153406` |
| `polymarket-copytrade-20-PROBE-REPORT-V2.md` | `2782eb5cd6bd3b03264c9fa5717245e541605bab0589fdd54865c1a529b43c32` |

Thứ tự ưu tiên: tổng hợp > quyết định chủ nhân > file V2. Mọi con số của tổng hợp được giữ nguyên; quyết định chủ nhân được áp đúng chữ; các mục quyết định ghi "CHƯA DUYỆT CHI TIẾT" giữ nguyên là đề xuất.

## 0. Ranh giới cứng (không đổi)

- Chỉ nghiên cứu trên giấy. Không lệnh thật, không tiền thật, không nối ví, không tạo tài khoản Polymarket mới, không VPN, không mua dữ liệu trả phí. Chi phí 0 đồng.
- Không ghi mật khẩu, API key, token vào file, log, chat. Toàn bộ dữ liệu từ API công khai không cần đăng nhập.
- Luật dừng thu thập: HTTP 429 / 403 / throttle / response chậm dần bất thường → DỪNG TOÀN BỘ, ghi mã lỗi + Retry-After, không retry ngay, không tăng tốc bù. Không thiết kế collector theo giới hạn burst 10 giây.
- **Ngân sách thu thập đã duyệt (theo quyết định chủ nhân, áp cho hồ sơ + backtest sau này):** tối đa ~200 request/ngày, đi chậm 10 giây/request; sàng lọc rẻ trước (cả hai cửa, khối lượng, lãi giữ-tới-chốt trên mẫu nhỏ), ví qua cửa mới đi sâu; ví nhiều lệnh kiểu UpTheBlues KHÔNG được đi hết lịch sử bằng mọi giá; hạn 14 ngày cho bước hồ sơ; hết hạn mà k≥3 không đủ 100 tín hiệu trong mẫu thì theo luật đã viết (chuyển k đủ mẫu hoặc ghi thiếu mẫu), không hạ ngưỡng, không đổi cửa sổ, không đổi k sau khi thấy ngoài mẫu.
- Không sửa spec sau khi thấy kết quả. Không dùng bản tóm tắt chat thay file gốc để đóng băng. Không tự nâng cờ D1 hay báo động 999 thành cổng giết sau khi đóng băng.
- Không dùng endpoint fee-rate cũ cho phí.

## 1. Thuật ngữ và đơn vị (khóa)

- Mọi mốc thời gian tính bằng **giây UTC (Unix seconds)**; 1 ngày = 24 giờ = 86.400 giây. Ngày giờ dạng chữ RFC3339 (như `resolved_at`) đổi về epoch giây UTC bằng **làm tròn XUỐNG tới giây** (LUẬT — §19.6 đã duyệt).
- **Tiền mặt của lệnh = `usdc_size` trên `/v2/activity?type=TRADE`** (LUẬT — §19.4 đã duyệt); `price × size` từ `/v2/trades` chỉ dùng đối chiếu (lệch trên 0,01 USD/lệnh thì báo). Hai endpoint đã chứng minh cùng một tập fill.
- Mã thị trường: `condition_id`/`conditionId`. Mã cửa: `token_id` (CLOB), `outcome_index`. **`outcome_index = 999` = không gắn nhãn được cửa** (LUẬT — §19.3 đã duyệt: loại khỏi tín hiệu, đếm riêng "thiếu nhãn cửa", báo động khi trên 5%; chưa phải cổng giết). Cửa phân biệt bằng mã token, không bằng chữ YES/NO.
- Cổ phần: trả 1 USD thắng, 0 USD thua, 0,5 USD hòa. Giá ∈ [0,1].
- Ví = địa chỉ; Nhóm = sau gộp Q3.10. k tính theo NHÓM.
- Sự kiện gồm nhiều thị trường con. VWAP theo tiền. ROI = tổng lãi ròng / tổng tiền đặt; mẫu số tín hiệu copy = 100 × số tín hiệu đã lấy.
- Lãi giữ-tới-chốt = cổ phần × giá chốt (0/0,5/1) − tiền mua − phí theo ngày, tính cho lệnh vào đã chốt.

## 2. Dòng thời gian 3 đoạn 90 ngày

- Đoạn 1 chọn người 90 ngày → đoạn 2 trong mẫu 90 ngày → đoạn 3 ngoài mẫu 90 ngày; liên tiếp, không trùng, không hở, tính bằng giây UTC.
- Dữ liệu đoạn 1 chỉ dùng thông tin biết tới cuối đoạn 1. Tín hiệu gán theo thời điểm kích hoạt.
- Không rút 60 ngày khi thiếu. Thiếu 90+90+90 → ghi thiếu lịch sử/thiếu mẫu.
- Ghi rõ 3 đoạn rơi vào mùa nào. Cách tính ngày khóa trước khi đóng băng.
- **Mốc tuyệt đối T0–T3: ĐỀ XUẤT CHỜ DUYỆT CHI TIẾT (§19.8 chưa duyệt; §20.2).** Đề xuất neo theo ngày viết spec 2026-11-02, trừ ân hạn chốt 14 ngày:
  - **T3 = 2026-10-19T00:00:00Z (1792368000)**; T2 = T3 − 90 ngày = **2026-07-21T00:00:00Z (1784592000)**; T1 = T2 − 90 ngày = **2026-04-22T00:00:00Z (1776816000)**; T0 = T1 − 90 ngày = **2026-01-22T00:00:00Z (1769040000)**.
  - Lý do: mọi thị trường kích hoạt tới T3 có đủ 14 ngày ân hạn chốt tính tới ngày viết spec; dùng ranh giới 00:00:00 UTC cho dễ kiểm lại.
  - **Hậu quả phải ghi trước khi chốt mốc:** (1) World Cup 2026 (≈11-06 → 19-07-2026) nằm gần như trọn trong **đoạn 2 (in-sample)** — k* sẽ được tối ưu trên cửa sổ có giải lớn, còn holdout (đoạn 3, 21-07 → 19-10) không có World Cup → rủi ro k* khớp "mùa World Cup" chứ không khớp holdout; cổng tầng 3 (cờ giải lớn) sẽ soi được phần nào. (2) NBA playoffs (≈04 → 06-2026) vắt qua ranh giới T1. (3) Đoạn 3 chứa đầu mùa NFL 2026 và cuối mùa MLB. (4) Nếu muốn holdout tránh hẳn World Cup thì phải lùi T3 — làm thay đổi toàn bộ mốc, chỉ được quyết TRƯỚC khi đóng băng, không đổi sau khi thấy kết quả.

## 3. Q1 — Chỉ thể thao, chỉ trận đơn, chỉ trước trận

- Chỉ thị trường một trận duy nhất, trước trận, đơn, không combo. Loại v1: vô địch mùa, giải thưởng mùa, nhiều trận gộp, đang đá trực tiếp (trong trận để spec v2 riêng).
- **LUẬT nhận diện thể thao (§19.1 đã duyệt; đủ điều kiện: 23 mẫu thật ở báo cáo V2 + từng bước):**
  1. Gọi Gamma `/markets` với `include_tag=true` (không có cờ này tags luôn rỗng — đã xác nhận V2).
  2. **Thể thao ⇔ có tag label đúng chữ `'Sports'`** trong `tags[].label`.
  3. Thuộc phạm vi v1 ⇔ thể thao VÀ `sportsMarketType` khác rỗng VÀ `gameStartTime` khác rỗng VÀ thời điểm lệnh < `gameStartTime` (trước trận).
  4. Thể thao mà `sportsMarketType` rỗng → mùa vụ/giải dài → loại khỏi v1, đếm riêng.
  5. Không dùng `gameStartTime` một mình (deadline phi thể thao cũng có trường này).
  6. Thị trường 2 tag mâu thuẫn (vừa 'Sports' vừa khác): theo 'Sports', ghi bảng mô tả số lượng.
  - **Đường dự phòng khi tags rỗng (chỉ khi endpoint không trả tag): ĐỀ XUẤT CHỜ DUYỆT — xem §20.1.**
- Phân biệt 2 cửa / nhiều cửa bằng mã token.
- Báo cáo bắt buộc tách theo: môn, loại thị trường (thắng thua / chấp điểm / tổng điểm / kèo cầu thủ), mùa thường / playoff / giải lớn, dải giá, độ lớn thị trường.

## 4. Q2 — Cửa sổ chọn: 90 ngày là đoạn 1

- Giữ 90 ngày đoạn 1. Không rút 60 ngày.
- Còn chơi: **≥ 3 lệnh trong 14 ngày cuối** đoạn chọn.
- Báo cáo hao hụt hoạt động của 20 nhóm ở đoạn 2, đoạn 3; nếu ngoài mẫu chỉ còn một nửa → ghi rõ không còn là cùng một chiến lược.
- Ghi chú mùa giải theo mục 2.

## 5. Q3 — Luật chọn 20 (D5 đã chốt: 80 lệnh)

Tính chỉ trên thể thao trước trận, đoạn chọn 90 ngày, dữ liệu biết tới cuối đoạn chọn. 10 cửa:

1. Khối lượng thể thao ≥ **50.000 USD** (tổng `usdc_size` mua từ activity, sau khi nối Gamma chỉ giữ thể thao; không lấy từ bảng xếp hạng).
2. Số lệnh ≥ **80 lệnh giao dịch** (trade rows) — **D5 ĐÃ CHỐT: 80, không dùng 100**. Còn dưới 20 ví sau lọc → ghi thiếu mẫu, không hạ 50.
3. Số thị trường khác nhau ≥ **20 mã** conditionId.
4. Lãi giữ-tới-chốt trên mỗi đồng đặt > 0 VÀ lãi đã chốt thật > 0 (lãi xếp hạng = lãi giữ-tới-chốt tính lại từ lệnh vào đã chốt: cổ phần × giá chốt − tiền mua − phí theo ngày; lãi đã chốt thật chỉ là cửa phụ; lãi đã chốt cao mà giữ-tới-chốt âm → loại).
5. Còn chơi: ≥ 3 lệnh trong 14 ngày cuối đoạn chọn.
6. Một thị trường không chiếm quá **50%** tổng lãi giữ-tới-chốt.
7. Loại market maker/phòng hộ: "cả hai cửa" = tại bất kỳ thời điểm nào trong đoạn chọn, cùng lúc giữ cổ phần > 0 của cả hai token của cùng mã thị trường, tính lại từ chuỗi TRADE (loại SPLIT, MERGE, REWARD, MAKER_REBATE). Trên **30%** số thị trường là cả hai cửa → loại. Không cộng dồn "từng giữ".
8. Loại bot thanh khoản: trên **2.000 lệnh** và lãi/khối lượng < **1%** → loại.
9. Xếp hạng theo lãi giữ-tới-chốt trên mỗi đồng đặt (tổng lãi giữ-tới-chốt / tổng tiền mua các lệnh đã chốt đó), cao xuống thấp, lấy 20 đầu. Hòa: nhiều thị trường hơn → nhiều lệnh hơn → mã ví theo chữ cái.
10. Gộp nhóm nghi cùng người, TRƯỚC xếp hạng cuối: hai ví gộp nếu số lệnh trùng / số lệnh ít hơn ≥ **50%** VÀ trùng ≥ **20 lệnh** (trùng = cùng conditionId + cùng token, cách ≤ **60 phút**); gộp theo cặp duyệt theo thứ tự lãi giảm dần, giữ ví lãi cao hơn; sau gộp k tính theo nhóm; bù tới đủ 20 nhóm, không đủ → thiếu mẫu; nhóm đóng băng từ đoạn chọn, dùng cho cả đoạn 2 và 3; gộp chỉ là nghi ngờ → ghi giới hạn trong báo cáo.

**Pool ứng viên (§19.5 đã duyệt về hướng, điều kiện: cách đo thiên lệch viết rõ — viết tại đây):**
- Pool khởi đầu = leaderboard `time_period=month&category=sports&sort_by=PNL` lấy ở 4 thời điểm: tháng chứa cuối đoạn 1 và 3 tháng trước đó, mỗi bảng đi hết cursor.
- Mọi chỉ số 90 ngày của từng ví tự tính lại từ trades/activity, không tin số liệu bảng.
- **Đo thiên lệch (bắt buộc in trong báo cáo hồ sơ):** lấy mẫu đối chứng 50 ví từ bảng `all` (PNL cao) KHÔNG nằm trong pool, tự tính 90 ngày, đếm bao nhiêu ví đạt hết các cửa Q3 → tỷ lệ "ví giỏi bị missed" (ước lượng dưới, vì chỉ đo được ví có mặt ở bảng all). Ghi rõ pool thiên về "đang thắng gần đây".

## 6. Q4 — Overlap (D3, D4 đã chốt)

Tính bằng giây UTC. Tín hiệu khi đủ hết:
1. Cùng conditionId + cùng token_id (không phải cùng chữ YES/NO).
2. Mỗi sự kiện một lần đầu tiên mỗi đoạn; thị trường con khác cùng sự kiện bỏ ở bảng chính, ghi bảng phụ (bảng 16).
3. Mỗi thị trường một lần đầu tiên mỗi đoạn; phe kích hoạt trước thắng.
4. Cửa sổ trượt: tại mỗi lệnh mua ròng, nhìn lại các nhóm đã tăng vị thế ròng cùng cửa; nếu t nhóm thứ k − t nhóm đầu tiên ≤ **24 giờ (86.400 giây)** → kích hoạt ngay tại lệnh thứ k. **D4 ĐÃ CHỐT: 24 giờ + chặn giá chạy quá 0,10; cửa sổ 6 giờ chỉ là báo cáo phụ, không dùng chọn k\*.**
5. Đếm vị thế ròng tăng: mỗi nhóm được đếm khi vị thế ròng cho cửa đó tăng ≥ **100 USD tiền mặt** trong cửa sổ, sau khi trừ bán cùng cửa cùng cửa sổ; mua rồi bán hết không đếm; nhóm nào mua cửa ngược cùng thị trường trong cửa sổ thì không đếm. **D3 ĐÃ CHỐT: mỗi nhóm từ 100 USD ròng (không dùng 200), tổng các nhóm đếm ≥ 500 USD.** Báo cáo phụ 50/200 USD chỉ mô tả.
6. Khối lượng thị trường tại kích hoạt ≥ **10.000 USD**, tính tới thời điểm kích hoạt (cộng dồn từ giao dịch, không dùng volumeNum cuối từ Gamma).
7. Chặn giá chạy: giá copy thô hơn **0,10** so với giá nhóm đầu tiên → bỏ tín hiệu.
8. Khoảng giá: giá copy sau phạt ∈ **0,10–0,90**; ngoài → bỏ, đếm riêng; bị loại vì giá > 20% tổng kích hoạt → bảng chính mất đại diện, phải ghi rõ.

## 7. Q5 — Giá copy: VWAP 100 USD → phạt → cổ phần → phí theo ngày

Thứ tự khóa, không đổi:
1. **Giá gốc** = VWAP theo tiền của các giao dịch sau kích hoạt, cộng dồn tới đủ **100 USD tiền mặt**, trong tối đa **60 phút**; không đủ → bỏ tín hiệu (thiếu độ sâu). Không dùng giá một lệnh nhỏ đầu tiên.
2. **Phạt trễ** = max(**0,02**, spread tại kích hoạt nếu lấy được). **Với backtest: KHÔNG có spread lịch sử (đã xác nhận V2) → phạt = 0,02 cố định.** Với test về trước: đo spread theo luật mục 11 (§19.9). Nhạy cảm bắt buộc: thay phạt bằng 0,05 và 0,10 (THAY THẾ, không cộng).
3. **Giá copy** = giá gốc + phạt. **Số cổ phần** = 100 / giá copy.
4. **Phí taker** = cổ phần × tỷ lệ × giá copy × (1 − giá copy). Tỷ lệ từ `feeSchedule` của từng thị trường tại thời điểm tín hiệu (cấu trúc `{exponent, rate, takerOnly, rebateRate}` đã xác nhận); feeSchedule thiếu → bảng theo ngày dự phòng (phải ghi rõ là dự phòng): thể thao 0 năm 2025; 0,03 tháng 3–6/2026; **0,05 từ 10-07-2026** (khớp 2 mẫu đo thật ở V1/V2). Không hardcode 0,05 cho cả 9 tháng. Không dùng endpoint fee-rate cũ.
5. Thắng: lãi = cổ phần × giá chốt − 100 − phí. Thua: lãi = −100 − phí. Giá chốt từ nguồn chốt chính thức.
- **Làm tròn: ĐỀ XUẤT CHỜ DUYỆT CHI TIẾT (§19.7 chưa duyệt; §20.3).**
- Lấy lịch sử đặt `taker_only=false` (đã xác nhận v2). Lịch sử giá kiểm tra: prices-history cửa sổ ≤ 15 ngày/request, hạt 300 giây (7 ngày); 90 ngày ghép ≥ 6 request.

## 8. Q6 — Tiền giấy

- **100 USD giấy cố định** mỗi tín hiệu; phí ngoài 100 USD. Không gấp thếp, không dồn lãi.
- Mẫu số lãi duy nhất: tổng lãi ròng / (100 × số tín hiệu đã lấy). Không dùng vốn danh nghĩa 10.000 USD.
- **Tối đa 10 lệnh mở cùng lúc** (≤ 1.000 USD phơi); tín hiệu mới khi đủ 10 → bỏ theo thứ tự thời gian, đếm riêng "bỏ vì đầy vốn".
- Mọi lý do bỏ (thiếu độ sâu, không giao dịch trong 60 phút, đầy vốn, ngoài khoảng giá, thiếu nhãn 999) đếm riêng. Tỷ lệ bỏ = bỏ/(lấy+bỏ); trên **30%** → kết quả chỉ áp dụng thị trường thanh khoản + vốn trống, và là cổng không qua ở Q9.
- Báo cáo tách dải giá 0,10–0,30 / 0,30–0,70 / 0,70–0,90, theo môn, theo sự kiện; lãi chỉ nhờ một dải/sự kiện → ghi mong manh.

## 9. Q7 — Copy lệnh vào, giữ tới chốt

- Tên bắt buộc trong báo cáo: **"copy lệnh vào, giữ tới chốt"** (ví gốc có thể bán sớm — không nói "copy trade thắng").
- Giữ tới chốt chính thức. Một luật thoát duy nhất. Không chốt lãi/cắt lỗ/bán sớm.
- **LUẬT nguồn chốt (§19.2 đã duyệt):**
  1. Nguồn chính: Data API `/v2/resolutions` → `payouts` (micro-USDC/cổ phần; 1.000.000 = 1; 500.000 = 0,5). Giá chốt = payouts[outcome_index]/1.000.000.
  2. Nguồn đối chiếu: Gamma `umaResolutionStatus='resolved'` + `outcomePrices`. (Lưu ý: KHÔNG có trường `resolutionStatus` trên Gamma — tên thật `umaResolutionStatus`; positions KHÔNG bao giờ là nguồn chốt.)
  3. **Hai nguồn lệch nhau (cửa thắng ngược nhau, hoặc payouts không khớp dạng 0/0,5/1) → DỪNG tính lãi tín hiệu đó, báo lệch, đưa vào ân hạn; sau ân hạn vẫn lệch → "chưa chốt chắc", không thắng không thua, nhập tỷ lệ chưa chốt của cổng Q9. Không tự chọn nguồn.**
- Giá chốt: thắng 1, thua 0, hòa 0,5 — công thức hòa: lãi = cổ phần × 0,5 − 100 − phí (KHÔNG phải trả lại stake). Thị trường hủy lấy giá chốt thực tế từ nguồn chốt.
- Chưa chốt tới cuối đoạn: ân hạn **14 ngày**; sau ân hạn chưa chốt → ghi riêng, không vào mẫu số lãi; tỷ lệ chưa chốt sau ân hạn > **10%** → cổng không qua.
- Thời gian chờ chốt thực tế báo cáo riêng (tranh chấp có thể 4–6 ngày; vốn kẹt trong giới hạn 10 lệnh mở).

## 10. Q8 — Chọn k* (công thức giữ nguyên)

- Thử **k = 1, 2, 3, 4, 5** trên số nhóm sau gộp. k = 1 đối chứng, định nghĩa giống hệt các k khác.
- Chỉ tối ưu trên đoạn 2. Mỗi k phải có **≥ 100 tín hiệu trong mẫu**.
- **Điểm_k = ROI_k − sai số_k**; sai số_k = (độ lệch chuẩn lãi mỗi tín hiệu của k) / 100 / √(n_k).
- Chọn k có Điểm cao nhất, phải thỏa cả ba: Điểm_k > 0, ROI_k > 0, **ROI_k ≥ ROI_1 + 0,03**. Không k nào thỏa → dừng ở sàng lọc, không chọn k*.
- Hai k tốt nhất chênh Điểm < **0,02** → chọn k nhiều tín hiệu hơn.
- Khóa k*, test đúng một lần ở đoạn 3; không quay lại thử k khác trên cùng đoạn. Báo cáo phụ đếm theo tiền chỉ mô tả. Không tối ưu thêm biến nào khác trên đoạn 2.

## 11. Q9 — Cổng giết 3 tầng (D1 đã chốt: tầng 3 chỉ là cờ)

Ngưỡng "lớn hơn hẳn", không làm tròn lên (99 tín hiệu = trượt; 4,9% không thành 5%).

### Tầng 1 — sàng lọc, phải qua hết
1. Số tín hiệu: trong mẫu ≥ 100, ngoài mẫu ≥ 100, tổng ≥ 200 (đếm theo thời điểm kích hoạt).
2. Ngoài mẫu lãi ròng > 0.
3. Ngoài mẫu lãi ròng vẫn > 0 khi thay phạt trễ bằng **0,05** (tính lại toàn bộ: cổ phần mới, phí mới).
4. Ngoài mẫu lãi / tổng tiền đặt > **5%**.
5. Cao hơn **k = 1** cùng đoạn, cùng mẫu số, cùng công thức.
6. Trong mẫu ở k* dương và hơn k = 1.
7. 5 tín hiệu lãi nhất < **50%** tổng lãi ngoài mẫu; tín hiệu lãi nhất < **25%**; bỏ 10 tín hiệu lãi nhất mà lãi ngoài mẫu vẫn > 0. (Tính bằng lãi ròng từng tín hiệu.)
8. Tỷ lệ bỏ ≤ **30%** và tỷ lệ chưa chốt sau ân hạn ≤ **10%**.

### Tầng 2 — xác nhận
- Khoảng tin cậy **95%** của lãi ngoài mẫu trên tổng tiền đặt, bootstrap **gom theo sự kiện** (không gom theo tín hiệu), nằm hoàn toàn trên 0, VÀ lãi/tổng tiền đặt vẫn > 5%. Ở 200 tín hiệu khoảng này thường ±14–21% → lãi 5% quan sát chưa đủ kết luận; khoảng chứa 0 → **"chưa đủ bằng chứng"**, đi tiếp test về trước theo Q10, không đổi k.

### Tầng 3 — cờ mô tả (D1 ĐÃ CHỐT: chỉ cờ, không lật verdict ở v1)
- Không giải nào chiếm trên 50% lãi ngoài mẫu; không môn nào là nguồn lãi duy nhất trong khi các môn khác lỗ nặng; lãi khi **bỏ World Cup** vẫn > 0. Vi phạm → ghi rõ "lãi tập trung" — cờ bật, verdict chính không đổi.
- Top 3 sự kiện % lãi ngoài mẫu báo cáo bắt buộc.

### Verdict
Thiếu cổng tầng 1 nào → **CHẾT** (không sửa k/giá/luật; muốn hướng khác viết spec mới). Qua tầng 1 chưa qua tầng 2 → **CHƯA ĐỦ BẰNG CHỨNG**. Qua cả hai → **SỐNG** ở backtest, vẫn phải qua test về trước Q12.

## 12. Q10 — Test giấy về trước (D2 đã chốt: cohort mới)

- Chỉ làm sau tầng 1 + tầng 2 + kiểm toán độc lập CONFIRMED.
- **D2 ĐÃ CHỐT: tại ngày GO chọn lại 20 nhóm bằng đúng luật Q3 từ 90 ngày trước GO** — test luật, không test 20 ví cũ.
- Ghi sổ giấy, không lệnh thật. Chu kỳ thăm dò, nguồn phát hiện, cách ghi thời điểm phát hiện khóa trước GO. Ví dụ: thăm dò Data API v2 activity/trades **mỗi 5 phút**, trigger khi đủ k, giá forward đúng luật Q5, ghi độ trễ từng tín hiệu; độ trễ lớn hơn backtest → ghi rõ, không lấy backtest che.
- **Đo spread forward (§19.9 đã duyệt về hướng; chu kỳ + công thức viết tại đây):** trong cùng chu kỳ thăm dò 5 phút, khi phát hiện kích hoạt: gọi `/book` của token đúng 1 lần, ghi best_bid, best_ask, timestamp sổ; **spread = best_ask − best_bid; phạt = max(0,02; spread)**; sổ rỗng/404/timeout → phạt 0,02 + đếm riêng; ngân sách +1 request/tín hiệu ghi trước; ghi thêm độ sâu 2 mức giá tốt nhất để đối chiếu VWAP 100 USD (chỉ mô tả).
- Ngân sách request forward ghi trước; checkpoint timestamp; 429 → dừng, chờ Retry-After; thiếu > 10% số ngày hoặc đúng giai đoạn cao điểm → test vô hiệu (bảng 18).
- Giữa kỳ: 200 tín hiệu đã chốt — chỉ kiểm số lượng + chất lượng, không phán lãi.
- Cuối: **≥ 500 tín hiệu đã chốt + ≥ 90 ngày**, mốc nào tới sau, tối đa 12 tháng; chưa đủ → thiếu mẫu. Trước khi chạy, tính trước số tín hiệu cần từ độ lệch chuẩn + lãi backtest; không thể tới 500/12 tháng → không nên bắt đầu với k đó.
- Cổng forward: đúng tầng 1 + tầng 2 nhưng thay số đếm bằng ≥ 500 đã chốt ("đã chốt" = resolved); sau mốc thu thập chờ tối đa 30 ngày cho chốt xong.
- Ngày bắt đầu vào đầu mùa thường, không giữa playoff/giải lớn (trừ khi ghi rõ test riêng); 200 tín hiệu tới giữa giải lớn đang chạy → chờ giải xong + chốt xong rồi mới phán.

## 13. 18 bảng báo cáo bắt buộc (mô tả / tính điểm ghi rõ từng bảng)

1. Theo môn (mô tả; cấp dữ liệu cờ tầng 3). 2. Theo loại thị trường (mô tả). 3. Mùa thường/playoff/giải lớn + World Cup riêng + lãi bỏ World Cup (mô tả + cờ tầng 3). 4. Theo dải giá (mô tả + cờ mong manh). 5. Theo độ lớn thị trường (mô tả). 6. Top 3 sự kiện % lãi ngoài mẫu (mô tả, tầng 3). 7. Hao hụt hoạt động đoạn 2/3 (mô tả bắt buộc). 8. Tỷ lệ bỏ + lý do (TÍNH ĐIỂM — cổng 8). 9. Tỷ lệ chưa chốt sau ân hạn (TÍNH ĐIỂM — cổng 8) + thời gian chờ chốt (mô tả). 10. Bảng k=1 đối chứng (TÍNH ĐIỂM — cổng 5, 6). 11. Phụ: đếm theo tiền / 50-200 USD / 6h-24h (mô tả, cấm cứu verdict). 12. Nhạy cảm phạt 0,05 (TÍNH ĐIỂM — cổng 3) / 0,10 (mô tả). 13. Bỏ vì chặn giá 0,10 / ngoài 0,10–0,90 + cờ 20% (mô tả bắt buộc). 14. Độ trễ forward (mô tả, không được che). 15. Ghi chú giới hạn: gộp = nghi ngờ; bỏ >30% hạn phạm vi (mô tả). 16. Bảng phụ thị trường con cùng sự kiện bị bỏ (mô tả). 17. Bảng kết quả cổng tầng 1 (8 cổng, đúng từng giá trị đo) + tầng 2 (hai đầu khoảng tin cậy) (in kết quả cổng). 18. Bảng ngày thiếu dữ liệu forward + ngân sách thực dùng (mô tả; quyết định hiệu lực test forward).

## 14. D1–D5 — ĐÃ ĐƯỢC CHỦ NHÂN CHỐT (trích quyết định 2026-11-02)

| # | Quyết định (nguyên văn tinh thần file quyết định) |
|---|---|
| D1 | Giải lớn chiếm trên 50% lãi ngoài mẫu chỉ là **CỜ CẢNH BÁO**, không phải cổng giết ở v1. Báo cáo ghi rõ khi cờ bật; cờ không tự lật verdict chính. |
| D2 | Test giấy về trước dùng **NHÓM MỚI**, chọn lại bằng đúng luật Q3 từ 90 ngày trước ngày GO. Test luật, không test 20 ví cũ. |
| D3 | Mỗi nhóm đếm từ **100 USD ròng** trở lên, tổng tiền ròng các nhóm đếm từ **500 USD** trở lên. Không dùng 200 USD. |
| D4 | Cửa sổ overlap **24 giờ** + chặn giá chạy quá **0,10**. Không dùng 6 giờ ở v1; 6 giờ chỉ báo cáo phụ. |
| D5 | Ngưỡng chọn người **80 lệnh** giao dịch trong 90 ngày chọn. Không dùng 100 lệnh. |

## 15. Trạng thái các đề xuất §19 (theo quyết định chủ nhân)

| Mục | Trạng thái | Trong spec này |
|---|---|---|
| 19.1 tag 'Sports' | DUYỆT (đủ 23 mẫu + từng bước) | Mục 3 — LUẬT |
| 19.2 resolutions.payouts ưu tiên, lệch → dừng và báo | DUYỆT | Mục 9 — LUẬT |
| 19.3 999 loại + đếm riêng + báo động >5% | DUYỆT LÀM BÁO ĐỘNG (chưa cổng) | Mục 1 — LUẬT (báo động) |
| 19.4 usdc_size activity là tiền chính, trades đối chiếu | DUYỆT | Mục 1 — LUẬT |
| 19.5 pool từ leaderboard tháng + tự tính 90 ngày + đo thiên lệch | DUYỆT VỀ HƯỚNG (điều kiện: đo thiên lệch viết rõ) | Mục 5 — LUẬT kèm cách đo |
| 19.6 RFC3339 → giây UTC, làm tròn xuống | DUYỆT | Mục 1 — LUẬT |
| 19.7 Làm tròn giá/cổ phần/phí | **CHƯA DUYỆT CHI TIẾT** | §20.3 — ĐỀ XUẤT |
| 19.8 Mốc T0–T3 | **CHƯA DUYỆT CHI TIẾT** | §20.2 — ĐỀ XUẤT |
| 19.9 Đo spread forward | DUYỆT VỀ HƯỚNG (điều kiện: chu kỳ + công thức viết rõ) | Mục 12 — LUẬT kèm chu kỳ 5 phút + công thức |

## 16. Code ứng viên đi kèm

Code xây đúng spec này, chỉ test dữ liệu giả: `~/Downloads/Polymarket/copytrade_build_v1/` (config, data_loader, sports_filter, selection, overlap, ledger, kopt, killgate, report + bộ test). Không module nào được gọi API thật trong bước xây này.

## 17. Điều kiện để file này thành spec đóng băng

1. Coordinator mở file gốc V2 (hash ở đầu file này) và kiểm toán từng dòng, từng bảng, từng đề xuất §19. Bản tóm tắt chat không thay được file gốc.
2. Chủ nhân duyệt chi tiết các mục §20 (đặc biệt 20.2 mốc T0–T3 và 20.3 làm tròn).
3. Chủ nhân kiểm tra spec đóng băng + sha256, rồi ra lệnh GO riêng.
4. Chưa có GO: không chạy hồ sơ 20 nhóm, không backtest, không test giấy về trước.

## 18. KHÔNG làm

Không lệnh thật/tiền thật/nối ví/tài khoản mới/VPN. Không chạy tính điểm. Không chọn k*. Không verdict. Không sửa spec sau khi thấy kết quả. Không nâng cờ D1 hay báo động 999 thành cổng giết sau khi đóng băng.

---

## 20. ĐỀ XUẤT CHỜ DUYỆT CHI TIẾT (KHÔNG PHẠM LUẬT — chờ coordinator kiểm toán V2 + chủ nhân duyệt)

### 20.1 Đường dự phòng khi tags rỗng
Gamma thường trả tags khi có `include_tag=true`; nếu một thị trường vẫn trả tags rỗng: (bước 1) dùng `sportsMarketType` khác rỗng → coi là thể thao trận đơn; (bước 2) `sportsMarketType` rỗng nhưng `gameStartTime` khác rỗng → KHÔNG coi là thể thao (vì deadline phi thể thao cũng có trường này), đưa vào danh sách cần tra lại bằng slug/sự kiện ở bước hồ sơ; (bước 3) đếm số thị trường rơi vào bước 2, báo cáo. Đường này chỉ là ĐỀ XUẤT.

### 20.2 Mốc tuyệt đối T0–T3
Đề xuất: T3 = 2026-10-19T00:00:00Z (1792368000); T2 = 2026-07-21T00:00:00Z (1784592000); T1 = 2026-04-22T00:00:00Z (1776816000); T0 = 2026-01-22T00:00:00Z (1769040000). Lý do + hậu quả (World Cup nằm trọn trong đoạn 2; NBA playoffs vắt T1; đoạn 3 có đầu mùa NFL) đã ghi ở mục 2. Chưa duyệt — không dùng để chạy gì.

### 20.3 Quy tắc làm tròn
Đề xuất: giá copy làm tròn 4 chữ số thập phân (gần nhất); cổ phần giữ số lẻ không làm tròn; phí làm tròn tới xu (gần nhất); tổng lãi mỗi tín hiệu cộng phí đã làm tròn; so ngưỡng (0,10–0,90; 0,10 chặn giá) TRƯỚC khi làm tròn. Chưa duyệt — trước khi duyệt, mọi số tính trung gian giữ đủ độ chính xác.

### 20.4 Định nghĩa "giải lớn" bằng trường dữ liệu
Đề xuất (không dùng danh sách viết tay sau khi thấy kết quả): **giải lớn = sự kiện có ≥ 8 thị trường con VÀ volumeNum của sự kiện nằm trong nhóm 5% sự kiện có khối lượng cao nhất tính trên toàn bộ sự kiện thể thao của đoạn 1** (tính trước khi chọn người, không dùng kết quả backtest; bộ sự kiện và ngưỡng lấy theo trường dữ liệu Gamma tại thời điểm tính, không sửa sau). World Cup 2026, Super Bowl, Olympics sẽ rơi vào định nghĩa này tự nhiên qua 2 điều kiện trường dữ liệu. Báo cáo kèm danh sách sự kiện bị coi là giải lớn + bằng chứng 2 điều kiện. Chưa duyệt.

### 20.5 Chi tiết còn chờ kiểm toán/duyệt khác
- Tham số mẫu đo thiên lệch pool: 50 ví đối chứng từ bảng `all` (con số 50 là ĐỀ XUẤT trong điều kiện đã duyệt về hướng).
- Ngưỡng báo động thiếu nhãn 999: 5% đã duyệt làm báo động; nếu chủ nhân muốn nâng thành cổng giết phải quyết TRƯỚC khi đóng băng (quyết định chủ nhân cấm nâng sau).
- Trần ngân sách thu thập hồ sơ: ~200 request/ngày, 10 giây/request, hạn 14 ngày — đã duyệt ở file quyết định; coordinator xác nhận lại khi kiểm toán.
