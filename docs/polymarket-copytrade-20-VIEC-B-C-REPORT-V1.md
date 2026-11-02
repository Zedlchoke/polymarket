# BÁO CÁO VIỆC B + VIỆC C — LẦN CHẠY ĐẦU DƯỚI SPEC ĐÓNG BĂNG — 2026-11-02

Chạy theo lệnh GO văn bản của chủ nhân "hash đúng, chạy tiếp" (đã ghi FREEZE_LOG), sau khi coordinator kiểm toán gói
`polymarket-copytrade-20-FREEZE-PACKAGE-V1` (repo github.com/Zedlchoke/polymarket). Hash spec đóng băng xác minh lại
nguyên vẹn trước khi chạy: `e98691e2c555a326c59a92633a22864e04152109c9e48b8cc8457f9b7a5cb61f`.

**KẾT QUẢ TÓM TẮT: Việc B DỪNG Ở BƯỚC POOL vì SPEC FLAW có bằng chứng (leaderboard không có bảng tháng quá khứ).
Không hồ sơ, không backtest, không k*, KHÔNG CÓ VERDICT. Việc C: 0 lệnh PaperDesk trong kỷ nguyên B → THIẾU MẪU
theo đúng luật C4 đã chốt trước. Không phá luật nào của spec đóng băng; không sửa spec.**

## Việc B — Hồ sơ 20 nhóm + Backtest: DỪNG Ở POOL (SPEC FLAW)

### Bằng chứng (2 request mẫu, nghỉ 10 giây, log tại probe/probe_out_v2/requests.log tag B1_*)

1. `GET /v2/leaderboard?time_period=month&category=sports&sort_by=PNL&limit=3` → HTTP 200, trả **bảng tháng HIỆN TẠI**
   (tháng 11/2026; rank 1 BreakTheBank PNL 6.923.532 — trùng thăm dò hôm nay).
2. `GET /v2/leaderboard?...&end=1765584000` (13-12-2025) → HTTP 200, **tham số bị bỏ qua hoàn toàn**, kết quả không đổi.
3. Contract v2 (đã lưu `probe_out/dataapi_v2_openapi.json`): tham số leaderboard chỉ có
   `time_period ∈ {day, week, month, all}` (tính từ hiện tại), `category`, `sort_by`, `user`, `limit`, `cursor` —
   **không có tham số ngày/tháng quá khứ nào**.

### Hệ quả

- Spec đóng băng mục 5 bắt buộc: pool = hợp **4 bảng leaderboard tháng 09/10/11/12-2025** (tháng chứa cuối đoạn 1 +
  3 tháng trước). **4 bảng này KHÔNG THỂ LẤY** — endpoint không phục vụ bảng tháng quá khứ, đã chứng minh bằng request.
- Cách thay thế khả dĩ (bảng `all` hoặc tháng hiện tại lấy hôm nay) đều **phản ánh thành tích tới 2026-11-02**, tức
  chứa toàn bộ đoạn 2 + đoạn 3 của mốc B → dùng để chọn pool là **rò rỉ tương lai** vào chọn mẫu, vi phạm luật
  "dữ liệu đoạn 1 chỉ dùng thông tin biết tới cuối đoạn 1".
- Theo đúng luật spec đóng băng §18 ("Không sửa spec sau khi thấy kết quả. Muốn đổi thì viết spec mới") và từ vựng
  kiểm toán của bản nháp gốc Bước 5: đây là **SPEC FLAW** — không phải CHẾT (không có kết quả tính điểm nào),
  không phải thiếu nỗ law. Hồ sơ 20 nhóm KHÔNG chạy; backtest KHÔNG chạy; k* KHÔNG chọn; **KHÔNG CÓ VERDICT**.
- Ngân sách đã dùng cho Việc B: **2 request** (thăm dò khả năng pool). Không request thu thập nào khác.

### Các hướng cho spec v2 (CHỈ LIỆT KÊ ĐỀ XUẤT, chờ chủ nhân quyết — không tự chọn)

1. **Pool từ thị trường thay vì bảng xếp hạng:** lấy danh sách ví hoạt động từ các thị trường thể thao lớn trong đoạn 1
   (tự dựng từ lịch sử giao dịch thị trường — dữ liệu past vẫn lấy được qua trades theo condition), rồi áp đủ 10 cửa Q3.
   Ưu: không rò rỉ tương lai. Nhược: tốn request hơn nhiều (cần ngân sách riêng, có thể vượt hạn 14 ngày).
2. **Chấp nhận bảng `all` lấy hôm nay + ghi rõ thiên lệch rò rỉ tương lai** — nhanh nhưng vi phạm tinh thần "không dùng
   tương lai để chọn mẫu"; chỉ hợp lệ nếu chủ nhân đổi luật một cách minh bạch trong spec v2.
3. **Đổi kỷ nguyên test** sang các đoạn gần hơn (dữ liệu leaderboard tháng hiện tại còn sống) — tương đương chọn lại
   mốc A hoặc mốc mới; là quyết định của chủ nhân, không phải của agent.
4. **Bỏ qua backtest quá khứ, đi thẳng test giấy về trước** từ bây giờ (forward-only) — đổi lớn nhất, cần spec riêng.

## Việc C — Overlap PaperDesk (chỉ mô tả): THIẾU MẪU theo luật C4

### C1A. Census sổ PaperDesk (CHỈ ĐỌC, không ghi/xóa/sửa/chaạy lại gì)

- **Sổ đã đọc:** `/Users/hoangminhlong/.my-quantitative-data/sports-papertrade-exec-v1/ledger/paper_ledger.jsonl`
  (975.273 byte, cập nhật lần cuối 2026-11-02 11:51 theo mtime). Đọc tổng 404 dòng JSONL.
- Phân bố loại dòng: GENESIS 1 · FORECAST 134 · MARKET_QUOTE 105 · **DECISION 134 (trong đó status=BET_PAPER: 32)** · SETTLEMENT 30.
  Lưu ý schema: `BET_PAPER` là giá trị `status` trên dòng DECISION (không phải type riêng).
- **Khoảng phủ thật của 32 lệnh BET_PAPER: 2026-10-07T11:16:45Z → 2026-10-31T00:38:40Z.**
- **Số lệnh BET_PAPER trong kỷ nguyên B (13-09-2025 → 10-06-2026): 0** (32/32 nằm ngoài).
- Trường ánh xạ Polymarket trên dòng BET_PAPER: **KHÔNG CÓ** conditionId/token_id/pm_event_id nào; chỉ có
  `match_id`, `home/away`, `league`, `kickoff_utc`, `quote_meta.bookmaker='POLYMARKET_CLOB'`, `chosen_leg` (HOME/AWAY) —
  là khóa trận/cửa bằng chữ, không phải mã thị trường. Nếu sau này có lệnh trong kỷ nguyên thì bắt buõi qua bảng
  không-ánh-xạ-được theo luật C2.

### C-kết luận (đúng luật C4 đã chốt trước, không thêm kết luận mới)

- Số lệnh overlap chính trong kỷ nguyên B = **0 < 30** → **THIẾU MẪU cho kiểm tra overlap**: không tăng/giảm sự tự tin,
  không nói "hai hệ thống khác nhau", không suy ra ngoài khoảng phủ. Hàng overlapping chi tiết không tính vì vô nghĩa.
- Việc C cũng phụ thuộc 20 nhóm của Việc B (bị chặn), nhưng kể cả không chặn, kỷ nguyên B không có lệnh PaperDesk nào.

## Xác nhận

- Không đổi luật PaperDesk; chỉ ĐỌC sổ; không chạy lại PaperDesk.
- Không sửa spec đóng băng (hash xác minh lại sau GO, trước và sau khi chạy: `e98691e2…` nguyên vẹn).
- Không áp bộ lọc overlap vào hệ thống nào.
- Mọi bước chạy đều dưới spec đóng băng đã có hash mà chủ nhân đã kiểm tra (GO văn bản "hash đúng, chạy tiếp").
- Không chạy test giấy về trước, không kích hoạt PaperDesk.
- Tổng request API lần chạy này: **2** (cả hai log đầy đủ).
