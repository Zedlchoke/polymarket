# -*- coding: utf-8 -*-
"""K optimizer — Q8: k=1..5, Điểm = ROI − sai số, đủ 100 tín hiệu trong mẫu,
phải hơn k=1 ít nhất 3 điểm %; chênh Điểm <0,02 -> chọn k nhiều tín hiệu hơn."""
import math

from . import config


def k_metrics(signals_pnl):
    """signals_pnl: danh sách lãi ròng từng tín hiệu (USD)."""
    n = len(signals_pnl)
    if n == 0:
        return None
    mean = sum(signals_pnl) / n
    roi = mean / config.STAKE_USD
    if n > 1:
        var = sum((x - mean) ** 2 for x in signals_pnl) / (n - 1)
        std = math.sqrt(var)
    else:
        std = 0.0
    se = std / config.STAKE_USD / math.sqrt(n)
    return {"n": n, "roi": roi, "std": std, "se": se, "diem": roi - se}


def select_k(per_k):
    """per_k: {k: signals_pnl}. Trả (k*, lý_do) hoặc (None, lý_do).
    Chỉ k đủ >= K_MIN_SIGNALS_IN_SAMPLE được xét."""
    m = {k: k_metrics(v) for k, v in per_k.items()}
    m = {k: v for k, v in m.items() if v and v["n"] >= config.K_MIN_SIGNALS_IN_SAMPLE}
    if 1 not in m:
        return None, "thiếu_k1_đủ_mẫu"
    roi1 = m[1]["roi"]
    eligible = {k: v for k, v in m.items()
                if v["diem"] > 0 and v["roi"] > 0
                and v["roi"] >= roi1 + config.K_EDGE_VS_K1}
    if not eligible:
        return None, "không_k_nào_thỏa_cả_ba_điều_kiện"
    best = sorted(eligible.items(), key=lambda kv: (-kv[1]["diem"], -kv[1]["n"]))
    if len(best) >= 2 and (best[0][1]["diem"] - best[1][1]["diem"]) < config.K_TIE_EPS:
        k_star = best[0][0] if best[0][1]["n"] >= best[1][1]["n"] else best[1][0]
        return k_star, "hòa_điểm_dưới_0.02_chọn_k_nhiều_tín_hiệu_hơn"
    return best[0][0], "điểm_cao_nhất"
