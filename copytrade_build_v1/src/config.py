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
