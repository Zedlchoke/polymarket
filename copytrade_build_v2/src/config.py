# -*- coding: utf-8 -*-
"""Toàn bộ hằng số của spec ứng viên — KHÔNG đổi số ở đây khi không có lệnh chủ nhân.
Nguồn: polymarket-copytrade-20-SPEC-V1-CANDIDATE.md (từ tổng hợp SYNTHESIS-6-GOC +
quyết định D1–D5 ngày 2026-11-02). Mỗi hằng số ghi rõ nguồn mục spec."""

# --- Dòng thời gian (mục 2) ---
SEGMENT_DAYS = 90
GRACE_DAYS = 14            # ân hạn chốt sau cuối đoạn (Q7)
DAY_S = 86400
WINDOW_S = 86400           # cửa sổ trượt overlap 24h (Q4, D4 đã chốt 24 giờ)

# --- Q3 chọn người ---
VOL_MIN_USD = 50_000.0     # cổng 1
TRADES_MIN = 80            # cổng 2 — D5 đã chốt 80
MARKETS_MIN = 20           # cổng 3
ACTIVE_TRADES = 3          # cổng 5: >=3 lệnh trong 14 ngày cuối
ACTIVE_WINDOW_DAYS = 14
ONE_MARKET_PNL_CAP = 0.50  # cổng 6: một thị trường <=50% lãi giữ-tới-chốt
BOTH_SIDES_RATIO = 0.30    # cổng 7: >30% thị trường giữ 2 cửa -> loại
BOT_TRADES = 2000          # cổng 8
BOT_PNL_VOL_RATIO = 0.01

# --- Q3.10 gộp nhóm ---
GROUP_RATIO = 0.50         # số lệnh trùng / số lệnh ít hơn >= 50%
GROUP_MIN_SHARED = 20      # và >= 20 lệnh trùng
GROUP_MATCH_WINDOW_MIN = 60  # hai lệnh trùng cách nhau <= 60 phút
N_GROUPS_TARGET = 20

# --- Q4 overlap (D3, D4 đã chốt) ---
GROUP_NET_MIN_USD = 100.0  # D3: mỗi nhóm từ 100 USD ròng
GROUPS_TOTAL_MIN_USD = 500.0  # D3: tổng các nhóm đếm từ 500 USD
MARKET_VOL_MIN_USD = 10_000.0  # khối lượng thị trường TẠI kích hoạt
PRICE_RUN_CAP = 0.10       # D4: chặn giá chạy quá 0,10
PRICE_BAND = (0.10, 0.90)  # khoảng giá copy sau phạt
K_VALUES = (1, 2, 3, 4, 5)

# --- Q5 giá copy ---
STAKE_USD = 100.0
VWAP_CASH_USD = 100.0
VWAP_WINDOW_S = 3600       # 60 phút
PENALTY_BASE = 0.02
SENS_PENALTIES = (0.05, 0.10)  # thay thế, không cộng
PAYOUTS_PER_USD = 1_000_000.0  # payouts micro-USDC / cổ phần
UNLABELED_INDEX = 999      # §19.3: loại + đếm riêng + báo động >5%
UNLABELED_ALERT = 0.05

# Bảng phí theo ngày DỰ PHÒNG (chỉ khi feeSchedule thiếu — Q5):
# thể thao 0 năm 2025; 0,03 từ 01-03 đến 30-06-2026; 0,05 từ 10-07-2026.
# 01-07 → 09-07-2026: tổng hợp KHÔNG ghi -> trả None (THIẾU), không đoán.
import datetime as _dt
_UTC = _dt.timezone.utc
FEE_FALLBACK = [
    (0, int(_dt.datetime(2026, 3, 1, tzinfo=_UTC).timestamp()), 0.0),
    (int(_dt.datetime(2026, 3, 1, tzinfo=_UTC).timestamp()),
     int(_dt.datetime(2026, 7, 1, tzinfo=_UTC).timestamp()), 0.03),
    (int(_dt.datetime(2026, 7, 10, tzinfo=_UTC).timestamp()), None, 0.05),
]

# --- Q6 tiền giấy ---
MAX_OPEN = 10              # tối đa 10 lệnh mở (<=1000 USD phơi)
SKIP_RATE_CAP = 0.30       # tỷ lệ bỏ >30% -> cổng không qua

# --- Q7 chốt ---
UNRESOLVED_CAP = 0.10      # tỷ lệ chưa chốt sau ân hạn >10% -> cổng không qua

# --- Q8 chọn k ---
K_MIN_SIGNALS_IN_SAMPLE = 100
K_EDGE_VS_K1 = 0.03        # ROI_k >= ROI_1 + 0,03
K_TIE_EPS = 0.02           # chênh Điểm < 0,02 -> chọn nhiều tín hiệu hơn

# --- Q9 cổng giết ---
GATE_MIN_IN = 100
GATE_MIN_OUT = 100
GATE_MIN_TOTAL = 200
GATE_ROI_MIN = 0.05
TOP5_CAP = 0.50
TOP1_CAP = 0.25
CI_LEVEL = 0.95
BOOTSTRAP_SEED = 42        # seed cố định để kiểm toán lặp lại được

# --- Thu thập (quyết định chủ nhân 2026-11-02) ---
BUDGET_MAX_REQUESTS_PER_DAY = 200
BUDGET_SLEEP_S = 10.0
PROFILE_DEADLINE_DAYS = 14

# =====================================================================
# V2 — các bổ sung theo prompt sửa ngày 2026-11-02 (coordinator audit)

# --- Sửa 2: bảng trạng thái §19 theo file quyết định CHỦ NHÂN
# (hash 01248d550391824d208a5bf49ca6650054d8f179950e32b4fcc11edce939a3a0) ---
S19_STATUS = {
    "19.1": "DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN — điều kiện: file V2 đủ 23 mẫu thật + luật từng bước (đã thỏa ở V2, chờ coordinator xác nhận lại)",
    "19.2": "ĐÃ DUYỆT",
    "19.3": "ĐÃ DUYỆT (làm BÁO ĐỘNG trên 5%, chưa phải cổng giết)",
    "19.4": "ĐÃ DUYỆT",
    "19.5": "DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN — điều kiện: cách đo thiên lệch phải viết rõ trong spec (đã viết; tham số 50 ví là TỰ CHỌN chờ duyệt)",
    "19.6": "ĐÃ DUYỆT",
    "19.7": "CHƯA DUYỆT CHI TIẾT — mọi quy tắc làm tròn còn là ĐỀ XUẤT",
    "19.8": "CHƯA DUYỆT CHI TIẾT — mốc T0–T3 còn là ĐỀ XUẤT A/B chờ chủ nhân chọn",
    "19.9": "DUYỆT VỀ HƯỚNG KÈM ĐIỀU KIỆN — điều kiện: chu kỳ + công thức viết rõ (đã viết; số chu kỳ 5 phút là TỰ CHỌN chờ duyệt)",
}

# --- Sửa 3: xử lý thiếu phí (FEE_MISSING) — toàn bộ dưới đây là ĐỀ XUẤT CHỜ DUYỆT ---
FEE_MISSING = "FEE_MISSING"   # mã trả về khi cả feeSchedule lẫn bảng ngày đều thiếu
FEE_MISSING_ALERT = 0.05      # TỰ CHỌN — đề xuất ngưỡng báo động tỷ lệ tín hiệu thiếu phí
# Ghi chú nguồn ngày chuyển phí 10-07-2026: KHÔNG được đo trực tiếp trong thăm dò.
# Thăm dò chỉ đo: trận 17-06-2026 rate 0,03; trận 19-07-2026 rate 0,05.
# Ngày 10-07 lấy NGUYÊN VĂN từ câu "Lịch sử đã biết" trong file tổng hợp SYNTHESIS-6-GOC
# (mục Q5.5) — là suy luận từ văn bản tổng hợp, chưa phải đo trực tiếp. Khoảng
# 01-07 → 09-07-2026 tổng hợp không ghi -> FEE_MISSING, không đoán.

# --- Sửa 5: định nghĩa giải lớn (ĐỀ XUẤT CHỜ DUYỆT) — khối lượng phải là cộng dồn TỚI CUỐI ĐOẠN ---
MAJOR_MIN_MARKETS = 8         # TỰ CHỌN — ngưỡng số thị trường con, chưa kiểm tra độ nhạy
MAJOR_TOP_SHARE = 0.05        # TỰ CHỌN — top 5% khối lượng sự kiện của đoạn, chưa kiểm tra độ nhạy

# --- Sửa 6: các hằng TỰ CHỌN khác (không có trong tổng hợp/quyết định) ---
K_CONTROL = 50                # TỰ CHỌN — số ví đối chứng đo thiên lệch pool
N_BOOT = 2000                 # TỰ CHỌN — số lần bootstrap mặc định (seed cố định để lặp lại)
BOOTSTRAP_SEED_NOTE = "42 — TỰ CHỌN để kiểm toán lặp lại được"
MAX_PAGES_NOTE = "40 — TỰ CHỌN trần an toàn mỗi stream phân trang"
WATCHDOG_NOTE = "độ trễ > max(3× trung vị, +3s) sau ≥6 mẫu — TỰ CHỌN, đã kích hoạt đúng 1 lần thật ở V2"
MAX_PAGES = 40               # TỰ CHỌN — trần an toàn mỗi stream phân trang (data_loader dùng)

# Registry mọi hằng TỰ CHỌN — dùng cho test kiểm toán Sửa 6 (không hằng nào được thiếu chú thích)
SELF_CHOSEN = {
    "FEE_MISSING_ALERT": (FEE_MISSING_ALERT, "ngưỡng báo động thiếu phí — ĐỀ XUẤT"),
    "MAJOR_MIN_MARKETS": (MAJOR_MIN_MARKETS, "giải lớn: số thị trường con — ĐỀ XUẤT"),
    "MAJOR_TOP_SHARE": (MAJOR_TOP_SHARE, "giải lớn: top % khối lượng — ĐỀ XUẤT"),
    "K_CONTROL": (K_CONTROL, "số ví đối chứng đo thiên lệch pool — ĐỀ XUẤT"),
    "N_BOOT": (N_BOOT, "số lần bootstrap — kỹ thuật, TỰ CHỌN"),
    "BOOTSTRAP_SEED": (BOOTSTRAP_SEED, "seed cố định để kiểm toán lặp lại — kỹ thuật, TỰ CHỌN"),
    "MAX_PAGES": (MAX_PAGES, "trần phân trang mỗi stream — an toàn, TỰ CHỌN"),
}
