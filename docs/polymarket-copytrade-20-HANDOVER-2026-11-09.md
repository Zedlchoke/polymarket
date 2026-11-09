# BÀN GIAO DỰ ÁN — POLYMARKET COPY TRADE 20 TÀI KHOẢN — 2026-11-09

*(Tài liệu giao ban cho agent tiếp quản "mọi thứ" — đọc file này trước, rồi đọc danh mục tài liệu ở mục 8.)*

## 1. MỤC TIÊU (điều quan trọng nhất)

Trả lời MỘT câu hỏi của chủ nhân: **"Nếu bắt chước (copy trade) 20 người giao dịch thể thao giỏi nhất trên sàn Polymarket thì có lời không?"** — và trả lời bằng cách AN TOÀN: **toàn bộ trên giấy, 0 đồng tiền thật, không tài khoản thật, không nối ví, không đụng hệ thống thật nào** (PaperDesk chỉ được ĐỌC ở bước cuối nếu được phép).

Cấu trúc trả lời: chọn 20 "cao thủ" theo tiêu chuẩn chặt đã đóng băng (không dựa vào kết quả tương lai — chống rò rỉ dữ liệu), giả-lập copy giao dịch của họ trong quá khứ (backtest giấy), chấm điểm, và chỉ vượt qua khi qua đủ các "cổng giết" thống kê khắt khe. **Mọi verdict chỉ có hiệu lực sau kiểm toán độc lập + chủ nhân đọc.** Kể cả mọi thứ qua hết: chạy giấy thời gian thực (Việc 5) vẫn cần lệnh GO riêng, và tiền thật là quyết định riêng của chủ nhân ngoài phạm vi mọi spec hiện có.

## 2. NGUYÊN TẮC QUYỀN LỰC (bất di bất dịch)

1. **Chủ nhân quyết mọi thứ** bằng lệnh văn bản (GO). Lời ambiguous ≠ GO ("làm cả hai" KHÔNG phải GO). Mỗi việc lớn cần GO riêng.
2. **Spec v2 đã ĐÓNG BĂNG là LUẬT**: `docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md`, commit `8727bcc`, hash toàn file `ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8`. KHÔNG ĐƯỢC SỬA sau đóng băng — muốn đổi luật thì viết spec MỚI, kiểm toán, duyệt, đóng băng mới. Trước khi chạy việc gì, TỰ TÍNH LẠI hash — khác là DỪNG.
3. **Mỗi việc xong → KIỂM TOÁN ĐỘC LẬP bằng agent KHÁC** (không phải agent đã làm việc đó), file AUDIT_* riêng, kết luận 1 trong 4: CONFIRMED / BUG FOUND / SPEC FLAW / CHƯA ĐỦ BẰNG CHỨNG. BUG FOUND → verdict TREO, sửa + làm lại + kiểm lại từ đầu.
4. **Báo cáo trung thực tuyệt đối**: lỗi của agent phải tự khai (dự án này đã có 2 lần tự khai được đánh giá tốt — vi phạm nhịp chạy trùng, các lỗi nhãn). Không bịa số, không đoán hash, không "đã xong" khi chưa đủ điều kiện luật.
5. Mọi thứ push lên repo GitHub `Zedlchoke/polymarket`, branch `main` — đây là kênh chủ nhân đọc.

## 3. VỊ TRÍ HIỆN TẠI (tới 09/11/2026 — chuỗi đã hoàn tất)

| Việc | Trạng thái | Bằng chứng |
|---|---|---|
| Spec v1 → v2 → đóng băng v2 | ✅ | `8727bcc`, FREEZE_LOG_V2; kiểm toán CONFIRMED `0514c51` |
| **Việc 3: đếm pool thị trường** (gọi Gamma liệt kê toàn bộ thị trường thể thao trận đơn có gameStartTime trong [2025-09-13, 2025-12-12)) | ✅ **XONG + ĐÃ KIỂM TOÁN CONFIRMED** | Báo cáo bản sửa `9c3698f`; kiểm toán toàn bộ CONFIRMED `9b56d8a` |
| Việc 4: hồ sơ + backtest | ⏸ **KHOÁ — chờ quyết định lớn của chủ nhân (mục 4)** | |
| Việc 5: chạy giấy thời gian thực | ⏸ xa hơn nữa (điều kiện ở spec mục 3) | |

**SỐ CHÍNH THỨC (hiệu lực sau kiểm toán `9b56d8a`):** đã quét 71.351 thị trường duy nhất trong cửa sổ tra cứu → **19.230 trận HỢP LỆ** cho pool (T9-2025: 1.346 · T10: 4.128 · T11: 10.555 · T12: 3.201). Tổng 1.305 request thật qua 6 ngày chạy (03→09/11). Danh sách đầy đủ: `viec3/data/listing/listing_slim.jsonl.valid_FULL` (19.230 dòng).

## 4. QUYẾT ĐỊNH ĐANG TREO — GẶP CHỦ NHÂN ĐẦU TIÊN

Phép tính bất biến (kiểm toán xác nhận): mỗi thị trường hợp lệ cần ≥1 request để lấy trade (endpoint không phân trang theo thị trường) → chỉ riêng trade đã ≥19.230 request ≈ **96 ngày** @200/ngày, trong khi luật hạn hồ sơ 14 ngày (≈2.800 request). **→ KHÔNG còn đường nào lọt 14 ngày theo cách hiện tại.** Ba hướng (chủ nhân chọn; agent tính toán cụ thể từng hướng khi được yêu cầu, KHÔNG tự quyết):
- **(a) Thu hẹp pool theo luật KHÔNG dựa trên kết quả** (vd nâng ngưỡng khối lượng 10.000 USD lên cao hơn, giới hạn môn/ngày) — cần chủ nhân duyệt như luật mới trước khi chạy;
- **(b) Chấp nhận thời gian dài** (~3-4+ tháng chỉ tính trade);
- **(c) Đổi thiết kế** (spec v3 — ví dụ kỹ thuật lấy dữ liệu khác) — quy trình đầy đủ: viết → kiểm toán → duyệt → đóng băng.

## 5. LUẬT VẬN HÀNH API (đã được chủ nhân ban hành qua từng lệnh)

- **Trần 200 request/ngày DƯƠNG LỊCH theo giờ Việt Nam (Asia/Saigon), cộng dồn MỌI tiến trình trong ngày** — không lách bằng nhiều phiên. Bộ đếm chuẩn: đếm dòng `viec3/data/ledger.jsonl` có `status` VÀ `latency_ms` (đã sửa sau sự cố "359").
- **Nhịp ≥10 giây/request**; sau watchdog chậm → cooldown 17 phút + 1 retry chậm hơn (15-20s); **429/403/throttle → DỪNG toàn bộ**, ghi lỗi + Retry-After, không tăng tốc bù, không đổi endpoint lách.
- **Khóa tiến trình** `viec3/data/viec3.lock` (pid + xác minh chết + dead.log) — TUYỆT ĐỐI không 2 tiến trình chạy song song (lỗi từng bị 03/11: 33 request <9 giây).
- **Checkpoint + ledger liên tục**, dữ liệu ghi ngay từng trang (cache .gz từng trang — resume miễn phí).
- Watchdog "chậm bất thường" >5.000 ms → dừng theo luật.

## 6. KIẾN THỨC KỸ THUẬT ĐÃ ĐO (cứng, có bằng chứng trong repo)

1. Gamma `/markets`: **offset ≥ 2100 → HTTP 422** (mỗi query tối đa ~2.100 dòng) → kỹ thuật chuẩn: **chia lát cửa sổ `end_date_min/max` (ISO ngày) + bisection + dò-trước offset 2000 (1 request biết cụt)**; `limit` bị kẹp 100; `start_date_min/max` KHÔNG tác dụng; `include_tag=true` bắt buộc (không thì tags luôn rỗng); `sports_market_types` hoạt động nhưng không dùng (sợ sót enum).
2. Luật nhận diện: thể thao ⇔ tag 'Sports'; trận đơn ⇔ sportsMarketType ≠ rỗng VÀ gameStartTime ≠ rỗng; mùa vụ = Sports + smt rỗng (đếm riêng).
3. Tra theo mã: **lặp `condition_ids=` từng mã + `closed=any`** (dạng comma KHÔNG hoạt động).
4. Data-API `/v2/trades`: tham số `market=` BỊ TỪ CHỐI (400, API hướng dẫn dùng `condition`); **`condition_id=<cid>` + `taker_only=false` + `start/end` (epoch) + `limit=500` hoạt động**; KHÔNG cursor, KHÔNG offset → thị trường >500 fill phải **chia nhỏ cửa sổ thời gian** đệ quy. Lược đồ snake_case (`proxy_wallet`, `token_id`…).
5. Mật độ thị trường: Sep-Oct ~450-550/ngày; **Nov-Dec ~600-700/ngày** (lát 3 ngày thường cụt).
6. Máy này thiếu chuỗi CA → GET chỉ-đọc dùng SSL context không xác minh (tiền lệ probe; ghi SSL_FALLBACK trong ledger).
7. **Luật hoàn tất liệt kê** (sau BUG FOUND): tự nhiên = trang ngắn <100 hoặc rỗng @offset<2100; **rỗng @≥2100 = CỤT phải chia tiếp**; dò-trước CHỈ phán CAP, không bao giờ phán "xong".

## 7. LỖI ĐÃ HỌC (đừng lặp)

- 03/11: 2 tiến trình trùng (tôi chẩn đoán nhầm job chết) → 33 request <9s. Bài học: khóa tiến trình + kiểm tra ps trước khi chạy.
- "Liệt kê xong 105/105 ngày" tuyên bố SAI (BUG FOUND d8f2bb9): phủ theo NGÀY ≠ đủ theo DÒNG; bài học: đối chiếu file trạng thái của chính mình trước khi tuyên bố xong; điều kiện "xong" phải là MỌI LÁ tự nhiên + hàng đợi rỗng.
- Công thức tổng kết `complete` đòi mọi node NATURAL (kể cả lá cha đã chia) — sai thiết kế; đã khai và xác minh chỉ là lỗi nhãn.
- Mô tả theo trí nhớ thay vì đếm từ sổ → 3 lỗi Errata. Bài học: mọi con số trong báo cáo phải đếm lại được.

## 8. DANH MỤC TÀI LIỆU CHÍNH (đọc theo thứ tự này)

1. `docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md` @8727bcc — LUẬT (Q1-Q10, D1-D5, mốc B T0=2025-09-13/T1=2025-12-12, ngưỡng 10.000 USD LUẬT ĐÃ DUYỆT, cổng giết 3 tầng, 18 bảng…).
2. `docs/polymarket-copytrade-20-VIEC3-FIX-FINAL-2026-11-09.md` @9c3698f — kết quả đếm cuối + Errata + mọi số.
3. `docs/AUDIT_POLYMARKET_VIEC3_FIX_FULL_2026-11-09.md` @9b56d8a — kiểm toán CONFIRMED toàn bộ.
4. `docs/AUDIT_POLYMARKET_VIEC3_COUNT_2026-11-03.md` @d8f2bb9 — BUG FOUND (bài học).
5. `docs/AUDIT_POLYMARKET_VIEC2_FREEZE_SPECV2_2026-11-03.md` @0514c51 — CONFIRMED đóng băng.
6. `docs/polymarket-copytrade-20-FREEZE-LOG-V2.md` — hash + lịch sử GO.
7. `docs/polymarket-copytrade-20-VIEC3-COUNT-REPORT.md` @85f8732 — báo cáo gốc (một phần bị thay bởi bản sửa; giữ nguyên làm lịch sử) + các interim 04-08/11.
8. `viec3/data/` — toàn bộ dữ liệu thô (1.246 trang .gz), sổ ledger.jsonl, checkpoint; `viec3/scripts/` — code đã kiểm chứng (list3, coverage_check, recount, lib có khóa + bộ đếm trần + watchdog).
9. `docs/polymarket-copytrade-20-PROBE-REPORT-V1/V2.md` — bằng chứng endpoint gốc.

## 9. LỘ TRÌNH PHÍA TRƯỚC (khung, mọi bước cần GO riêng)

Chủ nhân chọn hướng ở mục 4 → (nếu đổi luật) quy trình spec mới đầy đủ → **Việc 4: hồ sơ 20 nhóm + backtest** theo đúng spec (kèm mẫu ngưỡng 10k đo từ trade, ví trước lọc, cổng Q8/Q9…) → kiểm toán độc lập → **Việc 5: chạy giấy về trước** (chỉ sau backtest qua tầng 1+2 + CONFIRMED + bộ ánh xạ PaperDesk theo spec riêng) → báo cáo cuối cho chủ nhân. **Tuyệt đối: không tiền thật, không pilot/Việc 4/5 khi chưa có GO, không sửa spec đóng băng.**

## 10. CÁC BÊN

- **Chủ nhân**: ra mọi quyết định (tiếng Việt, qua chat; lựa chọn bấm cũng là văn bản).
- **Agent Việc 3 (tôi, GLM via ZCode)**: đã làm spec v2 đóng băng, Việc 3 + bản sửa. Về sau: không tự kiểm toán việc mình làm.
- **Agent kiểm toán độc lập**: mỗi lần xong việc, giao agent khác, file AUDIT_* mới.
- **Agent tiếp quản (bạn)**: phụ trách mọi thứ từ đây — giữ nguyên các nguyên tắc mục 2 và luật mục 5; khi cần số liệu tính toán cho quyết định mục 4, lấy trực tiếp từ `viec3/data/` (đã kiểm toán) hoặc chạy đo mới theo đúng luật ngân sách.
