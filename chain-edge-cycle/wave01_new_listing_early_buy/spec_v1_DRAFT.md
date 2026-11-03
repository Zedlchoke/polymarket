# SPEC W1 — NHÁP (DRAFT, KHÔNG ĐÓNG BĂNG, KHÔNG HASH, CHƯA ĐƯỢC PHEP BACKTEST THẬT)

- Cơ chế M1: mua sớm token mới niêm yết DEX (Base), bán sau thời lượng cố định.
- Trạng thái 2026-11-02: vũ trụ 3-factory cổ điển chỉ ~vài chục pool/21 ngày (đếm chính xác ở
  `data/w1_base/universe.csv`) → **chắc chắn thiếu mẫu cho cổng T1 (≥200 tín hiệu/epoch)**.
  Spec này viết ra để (a) froze được ngay khi có nguồn vũ trụ đầy đủ, (b) làm khung kiểm tra logic.
  **Khi đóng băng thật: copy nội dung này sang `spec_v1.md`, bỏ dòng này, tính `shasum -a 256`,
  ghi hash vào file + wave_log TRƯỚC khi chạy backtest.**

## 1. Vũ trụ (trỏ tới step0 đã đóng băng)

Theo `wave01_new_listing_early_buy/step0_universe.md`: pool thuộc epoch đã đóng băng, quote ∈
{USDC, USDbC, WETH} theo địa chỉ, dedupe theo base token, KHÔNG lọc survivor. Biết thiên lệch
nguồn 3-factory (đã ghi trong step0) — vũ trụ đầy đủ cần nguồn khác (GT/đang chờ, hoặc indexer).

## 2. Bar hóa dữ liệu giá

- Nguồn giá: sự kiện Swap của pool (getLogs theo địa chỉ pool), giá = tỷ lệ |amount_quote/amount_base|
  chuẩn hóa decimals. Gom theo GIỜ UTC (dùng block→thời gian nội suy tuyến tính như step0).
- Bar giờ H có: open = giá swap đầu tiên trong giờ, close = giá swap cuối, volume_quote = tổng.
- Giờ H0 = giờ chứa block tạo pool.

## 3. Luật VÀO (đóng băng khi freeze)

- Tín hiệu xuất hiện tại close của giờ H0 (đã thấy toàn bộ giờ đầu).
- Điều kiện lọc thanh khoản tối thiểu (nhìn được TẠI close H0): volume_quote của H0 ≥ V_min.
  V_min cố định = 200 USD (KHÔNG tối ưu — chỉ Y là tham số được tối ưu).
- Giá vào = giá swap ĐẦU TIÊN của giờ H1 (không dùng close H0 — chống nhìn tương lai/biến động trong bar).
- Nếu giờ H1 không có swap nào → tín hiệu rơi vào nhóm "bỏ vì thiếu giá" (đếm vào tỷ lệ bỏ của cổng T1).

## 4. Luật RA (đóng băng khi freeze)

- Exit mặc định: giá swap đầu tiên của giờ H1+Y. Y = tham số chính, grid {1, 2, 4, 6, 12, 24} giờ,
  chỉ chọn trên E2 bằng median lãi ròng (hàm `select_param_insample` đã test).
- Luật chết token (không tối ưu): nếu từ thời điểm entry không còn swap nào trong 6 giờ liên tiếp,
  exit tại giá swap cuối cùng trước khoảng im lặng, thời điểm exit = swap cuối + 1 giờ.
- Token hết dữ liệu trước H1+Y → exit tại swap cuối + cờ truncated (không bỏ tín hiệu).

## 5. Chi phí (bắt buộc lấy THẬT, không trung bình trơn)

- Phí swap: dùng fee tier THẬT của pool (trường fee trong sự kiện PoolCreated, hundredths of bip),
  áp 2 chiều. Pool tier 1% → 100bps/chiều.
- Trượt giá: KHÔNG có dữ liệu reserve lịch sử không-key → giả định khai báo trước 50bps/chiều,
  và cổng T1 có stress +20% mọi chi phí. Ghi nhãn "trượt giá là giả định" trong mọi báo cáo.
- Gas: lấy MẪU gas THẬT: receipt của tối thiểu 10 tx swap thật trong vũ trụ → gasUsed×gasPrice
  (baseFee+priority thật của tx đó) → median mẫu áp cho mọi lệnh. Không lấy đủ 10 mẫu →
  ghi "THIẾU DỮ LIỆU CHI PHÍ", không backtest thật.
- Kích thước lệnh cố định: 100 USD/paper-lệnh.

## 6. Epoch (đã đóng băng ở step0)

E1 [52513088, 52815488) — kiểm tra cấu trúc; E2 [52815488, 53117888) — chọn Y; E3 [53117888,
53420288) — holdout chạy đúng 1 lần sau khi Y đã chọn.

## 7. Cổng giết (theo charter mục 5; bộ máy `tools/bt_core.py` đã PASS 15/15 test giả)

- T1: ≥200 tín hiệu; tổng lãi ròng >0; vẫn >0 khi phí+gas +20%; top-1 token <25%; top-5 <50%;
  tỷ lệ bỏ (thiếu giá/thanh khoản V_min) <30%.
- T2: KTC 95% bootstrap gom theo token hoàn toàn trên 0.
- T3: không một token/chuỗi/ví nào là nguồn lãi duy nhất.
- Stress honeypot (riêng của M1): giả sử x% tín hiệu không bán được (mất 100% lệnh) → tìm x*
  làm tổng lãi ròng E3 = 0; báo cáo x* (mức chịu đựng). Không phải cổng pass/fail, là chỉ số rủi ro.

## 8. Điều kiện để backtest thật được phép chạy

1. Vũ trụ đủ ≥200 pool/epoch TỪ NGUỒN ĐẦY ĐỦ (chưa có trong loop 10h này), và
2. Spec được copy thành `spec_v1.md` + sha256 ghi vào wave_log, và
3. Lệnh GO riêng của chủ nhân sau kiểm toán độc lập cho wave report.
