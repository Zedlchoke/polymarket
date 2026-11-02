# -*- coding: utf-8 -*-
"""Report generator — 18 bảng bắt buộc của spec ứng viên mục 13.
Mỗi bảng gắn nhãn 'tính điểm' (đầu vào của cổng Q9, được dùng phán xét) hoặc
'mô tả' (chỉ mô tả/kiểm toán, CẤM dùng cứu verdict khi bảng chính thua)."""
from . import config

PRICE_BANDS = [(0.10, 0.30), (0.30, 0.70), (0.70, 0.90)]

TABLE_REGISTRY = [
    (1, "Theo môn", "mô tả"),
    (2, "Theo loại thị trường", "mô tả"),
    (3, "Mùa/playoff/giải lớn + World Cup", "mô tả + cờ tầng 3 (D1: chỉ cờ)"),
    (4, "Theo dải giá 0,10–0,30/0,30–0,70/0,70–0,90", "mô tả + cờ mong manh"),
    (5, "Theo độ lớn thị trường", "mô tả"),
    (6, "Top 3 sự kiện % lãi ngoài mẫu", "mô tả (tầng 3)"),
    (7, "Hao hụt hoạt động đoạn 2/3", "mô tả bắt buộc"),
    (8, "Tỷ lệ bỏ + lý do bỏ", "TÍNH ĐIỂM — cổng 8"),
    (9, "Tỷ lệ chưa chốt sau ân hạn + thời gian chờ", "TÍNH ĐIỂM (tỷ lệ) + mô tả (thời gian)"),
    (10, "Bảng k=1 đối chứng", "TÍNH ĐIỂM — cổng 5, 6"),
    (11, "Phụ: đếm theo tiền / 50-200 USD / 6h-24h", "mô tả — CẤM cứu verdict"),
    (12, "Nhạy cảm phạt 0,05 / 0,10", "TÍNH ĐIỂM (0,05 — cổng 3) + mô tả (0,10)"),
    (13, "Bỏ vì chặn giá / ngoài dải giá + cờ 20%", "mô tả bắt buộc"),
    (14, "Độ trễ forward từng tín hiệu", "mô tả, không được che"),
    (15, "Ghi chú giới hạn (gộp = nghi ngờ, bỏ >30% hạn phạm vi)", "mô tả"),
    (16, "Thị trường con cùng sự kiện bị bỏ", "mô tả"),
    (17, "Kết quả cổng tầng 1 (8 cổng) + tầng 2 (hai đầu CI)", "in kết quả cổng"),
    (18, "Ngày thiếu dữ liệu forward + ngân sách thực dùng", "mô tả; quyết định hiệu lực test"),
]


def _agg(rows):
    n = len(rows)
    pnl = sum(r["pnl"] for r in rows)
    return {"n_signals": n, "pnl": pnl,
            "roi": pnl / (config.STAKE_USD * n) if n else None}


def table_by_dim(signals, dim_fn):
    """signals: [{'pnl', ...}] — dim_fn(signal) -> khóa nhóm."""
    out = {}
    for s in signals:
        out.setdefault(dim_fn(s), []).append(s)
    return {k: _agg(v) for k, v in sorted(out.items())}


def band_of(s):
    p = s["copy_price"]
    for lo, hi in PRICE_BANDS:
        if lo <= p < hi:
            return "%.2f–%.2f" % (lo, hi)
    return "ngoài_dải"


def table_price_band(signals):
    return table_by_dim(signals, band_of)


def table_by_sport(signals):
    return table_by_dim(signals, lambda s: s.get("sport", "không_rõ"))


def table_by_event_top(signals, top=3):
    t = table_by_dim(signals, lambda s: s["event_id"])
    total = sum(v["pnl"] for v in t.values())
    rows = sorted(t.items(), key=lambda kv: -kv[1]["pnl"])[:top]
    return {k: {**v, "share_of_pnl": (v["pnl"] / total if total > 0 else None)}
            for k, v in rows}


def table_skip(skip_records):
    """skip_records: [{'lý_do': ...}] — lý_do: thiếu_độ_sâu/thiếu_giao_dịch_60p/
    đầy_vốn/ngoài_dải/chặn_giá/thiếu_nhãn_999/...)
    """
    n_took = skip_records.get("n_took", 0)
    n_skip = sum(v for k, v in skip_records.items() if k.startswith("lý_do_"))
    rate = n_skip / (n_took + n_skip) if (n_took + n_skip) else 0.0
    return {"counts": {k: v for k, v in skip_records.items()
                       if k.startswith("lý_do_")},
            "skip_rate": rate, "gate_pass": rate <= config.SKIP_RATE_CAP}


def table_unlabeled_999(n_total_rows, n_999):
    """§19.3 (đã duyệt làm báo động): trên 5% -> báo động (chưa phải cổng giết)."""
    rate = n_999 / n_total_rows if n_total_rows else 0.0
    return {"n_999": n_999, "n_rows": n_total_rows, "rate": rate,
            "alert": rate > config.UNLABELED_ALERT}


def sensitivity_table(signals_pnl_by_penalty):
    """signals_pnl_by_penalty: {'0,02': [...], '0,05': [...], '0,10': [...]}."""
    out = {}
    for name, pnls in signals_pnl_by_penalty.items():
        out[name] = _agg([{"pnl": p} for p in pnls])
    return out
