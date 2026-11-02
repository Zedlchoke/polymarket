# -*- coding: utf-8 -*-
"""Sports filter — luật tag 'Sports' (§19.1 ĐÃ DUYỆT) + đường dự phòng khi tags rỗng (§20.1 ĐỀ XUẤT)."""
from . import config

GENERIC_TAGS = {"Sports", "All", "Games"}


def tag_labels(market):
    tags = market.get("tags") or []
    out = []
    for t in tags:
        out.append(t.get("label") if isinstance(t, dict) else t)
    return out


def is_sports(market, allow_fallback=True):
    """Trả (bool, đường_dùng). Đường chính: tag 'Sports' (luật đã duyệt).
    Đường dự phòng khi tags rỗng (§20.1 — ĐỀ XUẤT CHỜ DUYỆT): sportsMarketType khác rỗng
    -> coi là thể thao; sportsMarketType rỗng nhưng gameStartTime có -> KHÔNG coi là thể thao
    (deadline phi thể thao cũng có trường này), đưa danh sách tra lại."""
    labels = tag_labels(market)
    if labels:
        return ("Sports" in labels), "tag"
    if not allow_fallback:
        return False, "tag_trống_không_dự_phòng"
    smt = market.get("sportsMarketType")
    if smt:
        return True, "dự_phòng_smt"
    return False, "dự_phòng_không_xác_định"  # kể cả khi có gameStartTime (bước 2 §20.1)


def in_v1_scope(market, trade_ts=None):
    """Thể thao VÀ trận đơn VÀ trước trận (Q1). Trả (bool, lý_do)."""
    sports, _ = is_sports(market)
    if not sports:
        return False, "không_phải_thể_thao"
    smt = market.get("sportsMarketType")
    gst = market.get("gameStartTime")
    if not smt or not gst:
        return False, "thể_thao_mùa_vụ_ngoài_v1"  # đếm riêng, không phải lỗi
    if trade_ts is not None and trade_ts >= _epoch(gst):
        return False, "trong_trận_hoặc_sau_giờ_bóng"
    return True, "ok"


def sport_label(market):
    """Tên môn cho bảng tách theo môn: tag cụ thể đầu tiên bỏ tag chung."""
    for lab in tag_labels(market):
        if lab not in GENERIC_TAGS:
            return lab
    return "không_rõ_môn"


def _epoch(v):
    """Chuẩn hóa các dạng Gamma trả về: '2026-06-17 23:00:00+00',
    '2026-06-17T23:00:00+00', '...Z', hoặc số nguyên."""
    from .data_loader import floor_seconds_utc
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip()
    if " " in s:
        s = s.replace(" ", "T", 1)
    if s.endswith("+00"):
        s += ":00"
    return floor_seconds_utc(s)
