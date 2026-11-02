# -*- coding: utf-8 -*-
"""Kill gate checker — Q9, 3 tầng. Tầng 1: 8 cổng sàng lọc. Tầng 2: khoảng tin cậy 95%
bootstrap GOM THEO SỰ KIỆN. Tầng 3: cờ mô tả (D1 đã chốt: chỉ cờ, không lật verdict)."""
import random

from . import config


def contribution_gates(pnls):
    """Cổng 7: top-5 < 50%, top-1 < 25%, bỏ top-10 mà tổng vẫn > 0 (lãi ròng từng tín hiệu)."""
    total = sum(pnls)
    if total <= 0:
        return {"top1_share": None, "top5_share": None, "ex10_positive": False}
    s = sorted(pnls, reverse=True)
    return {"top1_share": s[0] / total,
            "top5_share": sum(s[:5]) / total,
            "ex10_positive": (total - sum(s[:10])) > 0}


def tier1(m):
    """m: dict gồm in_n, out_n, out_pnl, out_pnl_sens005, out_roi, k1_out_roi,
    in_pnl (k*), in_roi, k1_in_roi, pnls_out (danh sách), skip_rate, unresolved_rate.
    Ngưỡng 'lớn hơn hẳn', không làm tròn lên."""
    g = {}
    g["1_số_tín_hiệu"] = (m["in_n"] >= config.GATE_MIN_IN
                          and m["out_n"] >= config.GATE_MIN_OUT
                          and (m["in_n"] + m["out_n"]) >= config.GATE_MIN_TOTAL)
    g["2_ngoài_mẫu_dương"] = m["out_pnl"] > 0
    g["3_nhạy_cảm_0.05"] = m["out_pnl_sens005"] > 0
    g["4_roi>5%"] = m["out_roi"] > config.GATE_ROI_MIN
    g["5_hơn_k=1"] = m["out_roi"] > m["k1_out_roi"]
    g["6_trong_mẫu_dương_hơn_k1"] = m["in_pnl"] > 0 and m["in_roi"] > m["k1_in_roi"]
    c = contribution_gates(m["pnls_out"])
    g["7_tập_trung"] = (c["top1_share"] is not None
                        and c["top1_share"] < config.TOP1_CAP
                        and c["top5_share"] < config.TOP5_CAP
                        and c["ex10_positive"])
    g["8_bỏ_và_chưa_chốt"] = (m["skip_rate"] <= config.SKIP_RATE_CAP
                              and m["unresolved_rate"] <= config.UNRESOLVED_CAP)
    fails = [k for k, v in g.items() if not v]
    return {"gates": g, "pass": len(fails) == 0, "fails": fails, "contrib": c}


def tier2_bootstrap(signals, n_boot=2000, seed=config.BOOTSTRAP_SEED):
    """signals: [{'event_id','pnl'}]. Bootstrap gom theo sự kiện: lấy mẫu lại CÁC SỰ KIỆN
    (có hoàn lại), ROI = tổng pnl / (100 × tổng số tín hiệu) của mẫu lại.
    Trả (pass, ci_low, ci_high, roi_point) — pass khi CI nằm hoàn toàn trên 0 VÀ roi > 5%."""
    events = {}
    for s in signals:
        events.setdefault(s["event_id"], []).append(s["pnl"])
    keys = sorted(events.keys())
    total_pnl = sum(s["pnl"] for s in signals)
    total_n = len(signals)
    roi_point = total_pnl / (config.STAKE_USD * total_n) if total_n else 0.0
    rng = random.Random(seed)
    rois = []
    for _ in range(n_boot):
        pnl_sum = 0.0
        n_sum = 0
        for _ in range(len(keys)):
            k = rng.choice(keys)
            pnl_sum += sum(events[k])
            n_sum += len(events[k])
        if n_sum:
            rois.append(pnl_sum / (config.STAKE_USD * n_sum))
    rois.sort()
    lo_idx = int(0.025 * (len(rois) - 1))
    hi_idx = int(0.975 * (len(rois) - 1))
    ci_low, ci_high = rois[lo_idx], rois[hi_idx]
    passed = ci_low > 0 and roi_point > config.GATE_ROI_MIN
    return passed, ci_low, ci_high, roi_point


def tier3_flags(pnls_by_tournament, pnls_by_sport, pnl_ex_worldcup,
                sport_pnls_positive_rule):
    """D1 (đã chốt): CHỈ CỜ — bật cờ không lật verdict. Trả dict cờ + mô tả."""
    total = sum(v for v in pnls_by_tournament.values())
    flags = {}
    if total > 0:
        max_t = max(pnls_by_tournament.values()) / total
        flags["cờ_giải_lớn_trên_50%"] = max_t > 0.50
    else:
        flags["cờ_giải_lớn_trên_50%"] = False
    flags["cờ môn_lãnh_lãi_riêng"] = sport_pnls_positive_rule
    flags["cờ bỏ World Cup âm"] = pnl_ex_worldcup <= 0
    return flags


def verdict(t1_pass, t2_pass):
    if not t1_pass:
        return "CHẾT", "thiếu_cổng_tầng_1"
    if not t2_pass:
        return "CHƯA ĐỦ BẰNG CHỨNG", "khoảng_tin_cậy_chứa_0_hoặc_roi<=5%"
    return "SỐNG_ở_backtest", "qua_cả_hai_tầng"
