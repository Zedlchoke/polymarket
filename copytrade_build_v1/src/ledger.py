# -*- coding: utf-8 -*-
"""Copy ledger — Q5/Q6/Q7: VWAP đủ 100 USD trong 60 phút, phạt max(0,02; spread),
cổ phần, phí theo feeSchedule từng thị trường (bảng ngày làm dự phòng), giá chốt
0/0,5/1 từ resolutions.payouts (§19.2), ân hạn 14 ngày, tối đa 10 lệnh mở."""
from . import config


def entry_fee(shares, price, rate):
    """Q5.5: phí = cổ phần × tỷ lệ × giá × (1 − giá)."""
    return shares * rate * price * (1.0 - price)


def fee_rate(market, ts):
    """Lấy rate từ feeSchedule của thị trường (luật chính); thiếu thì bảng theo ngày
    dự phòng. Khoảng 01-07 → 09-07-2026 tổng hợp KHÔNG ghi -> None (THIẾU), không đoán."""
    fs = market.get("feeSchedule") or market.get("fee_schedule")
    if isinstance(fs, dict) and fs.get("rate") is not None:
        return float(fs["rate"]), "feeSchedule"
    for start, end, rate in config.FEE_FALLBACK:
        if ts >= start and (end is None or ts < end):
            return rate, "bảng_ngày_dự_phòng"
    import datetime as dt
    gap_a = int(dt.datetime(2026, 7, 1, tzinfo=dt.timezone.utc).timestamp())
    gap_b = int(dt.datetime(2026, 7, 10, tzinfo=dt.timezone.utc).timestamp())
    if gap_a <= ts < gap_b:
        return None, "THIẾU_khoảng_01_07_đến_09_07"
    raise ValueError("timestamp ngoài bảng phí dự phòng: %r" % ts)


def vwap_fill(fills, cash_needed=config.VWAP_CASH_USD,
              window_s=config.VWAP_WINDOW_S):
    """fills: [{'ts','price','cash'}] sau kích hoạt, tăng dần theo ts. Cộng dồn tới đủ
    cash_needed trong window_s; lệnh cuối cắt một phần. Trả (vwap, n_fills_dùng) hoặc
    (None, lý_do) nếu không đủ trong 60 phút (bỏ vì thiếu độ sâu)."""
    shares = 0.0
    cash = 0.0
    used = 0
    t0 = fills[0]["ts"] if fills else None
    for f in fills:
        if f["ts"] - t0 > window_s:
            break
        need = cash_needed - cash
        if need <= 1e-12:
            break
        take = min(need, f["cash"])
        shares += take / f["price"]
        cash += take
        used += 1
        if cash >= cash_needed - 1e-12:
            break
    if cash < cash_needed - 1e-9:
        return None, "thiếu_độ_sâu_60_phút"
    return cash_needed / shares, used


def late_penalty(spread=None):
    """Q5.2: phạt = max(0,02, spread nếu có); không spread (backtest) -> 0,02."""
    if spread is None:
        return config.PENALTY_BASE
    return max(config.PENALTY_BASE, spread)


def copy_price(base_price, spread=None):
    return base_price + late_penalty(spread)


def shares_for(copy_px):
    return config.STAKE_USD / copy_px


def resolve_price(payouts, outcome_index):
    """§19.2 (đã duyệt): giá chốt = payouts[outcome_index] / 1.000.000.
    Trả (trạng_thái, giá_trị) — cùng thứ tự với resolution_decision.
    outcome_index=999 -> ('thiếu_nhãn_999', None) để loại + đếm riêng (§19.3)."""
    if outcome_index == config.UNLABELED_INDEX:
        return "thiếu_nhãn_999", None
    if not payouts or outcome_index >= len(payouts):
        return "thiếu_payouts", None
    return "ok", payouts[outcome_index] / config.PAYOUTS_PER_USD


def resolution_decision(res_row, gamma_row=None):
    """Trả một trong: ('ok', price) | ('missing', None) | ('mismatch', chi_tiết).
    Nguồn chính resolutions.payouts; Gamma chỉ đối chiếu; lệch -> DỪNG, không tự chọn."""
    if not res_row or res_row.get("payouts") is None:
        return "missing", None
    payouts = res_row["payouts"]
    price0 = payouts[0] / config.PAYOUTS_PER_USD
    if any((p / config.PAYOUTS_PER_USD) not in (0.0, 0.5, 1.0) for p in payouts):
        return "mismatch", {"lý_do": "payouts_không_khớp_dạng_0_0.5_1", "payouts": payouts}
    if gamma_row is not None:
        gamma_prices = gamma_row.get("outcomePrices")
        if gamma_prices:
            try:
                gp = [float(x) for x in gamma_prices]
            except (TypeError, ValueError):
                gp = None
            if gp is not None and len(gp) == len(payouts):
                same = all(
                    abs(gp[i] - payouts[i] / config.PAYOUTS_PER_USD) < 1e-9
                    for i in range(len(gp)))
                if not same:
                    return "mismatch", {"lý_do": "payouts_khác_outcomePrices",
                                        "payouts": payouts, "gamma": gp}
    return "ok", price0  # caller nhân theo outcome_index của cửa đã copy


def signal_pnl(shares, res_price, fee):
    """Thắng/thua/hòa chung một công thức: cổ phần × giá chốt − 100 − phí.
    Hòa 0,5: shares × 0,5 − 100 − phí (KHÔNG trả lại stake). Thua: shares×0 − 100 − phí."""
    return shares * res_price - config.STAKE_USD - fee


def schedule_open_cap(signals, max_open=config.MAX_OPEN):
    """signals: [{'id','trigger_ts','close_ts'}] theo thứ tự thời gian. Khi đã đủ
    max_open lệnh đang mở, tín hiệu mới bị BỎ vì đầy vốn, đếm riêng."""
    accepted, skipped, open_until = [], [], []  # heap tối giản: danh sách close_ts
    for s in signals:
        open_until = [t for t in open_until if t > s["trigger_ts"]]
        if len(open_until) >= max_open:
            skipped.append(s["id"])
        else:
            accepted.append(s["id"])
            open_until.append(s["close_ts"])
    return accepted, skipped


def grace_status(signals, seg_end, grace_days=config.GRACE_DAYS):
    """Ân hạn 14 ngày sau cuối đoạn: chưa chốt sau ân hạn -> 'chưa chốt', không tính
    thắng/thua, không vào mẫu số. Trả (đã_chốt, chưa_chốt_sau_ân_hạn)."""
    deadline = seg_end + grace_days * config.DAY_S
    closed, unresolved = [], []
    for s in signals:
        if s.get("close_ts") is not None and s["close_ts"] <= deadline:
            closed.append(s["id"])
        else:
            unresolved.append(s["id"])
    return closed, unresolved
