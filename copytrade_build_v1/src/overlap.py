# -*- coding: utf-8 -*-
"""Overlap detector — Q4 với D3/D4 đã chốt: cửa sổ 24h, đếm vị thế ròng tăng,
mỗi nhóm >=100 USD ròng, tổng >=500 USD, mỗi thị trường/sự kiện một lần, phe trước thắng."""
from . import config


def detect_side(events, window_s=config.WINDOW_S,
                group_net_min=config.GROUP_NET_MIN_USD,
                total_net_min=config.GROUPS_TOTAL_MIN_USD,
                k_values=config.K_VALUES,
                opposite_buyers=frozenset()):
    """events: [{'group','ts','cash','price'}] theo thứ tự thời gian; cash>0 = mua,
    cash<0 = bán cùng cửa. Trả {k: trigger}. Quy tắc: tại mỗi lệnh MUA ròng, nhìn lại
    window_s; nhóm được đếm nếu vị thế ròng tích lũy trong cửa sổ >= group_net_min
    (đã trừ bán); nếu số nhóm đạt k và tổng ròng các nhóm đếm >= total_net_min thì
    kích hoạt mức k NGAY tại lệnh đó (không chờ hết 24h, không dùng ngày lịch)."""
    triggers = {}
    for i, ev in enumerate(events):
        if ev["cash"] <= 0:
            continue  # chỉ lệnh mua ròng mới là điểm xét
        t = ev["ts"]
        win = [e for e in events[:i + 1]
               if t - e["ts"] <= window_s and e["ts"] <= t]
        net, first_ts, first_price = {}, {}, {}
        for e in win:
            net[e["group"]] = net.get(e["group"], 0.0) + e["cash"]
            if e["cash"] > 0 and e["group"] not in first_ts:
                first_ts[e["group"]] = e["ts"]
                first_price[e["group"]] = e.get("price")
        qualified = {g: v for g, v in net.items()
                     if v >= group_net_min - 1e-9 and g not in opposite_buyers}
        if not qualified:
            continue
        total_net = sum(qualified.values())
        if total_net < total_net_min - 1e-9:
            continue
        k = len(qualified)
        t_first = min(first_ts[g] for g in qualified)
        if t - t_first > window_s:
            continue  # nhóm đầu đã rời cửa sổ trượt
        for kk in k_values:
            if kk <= k and kk not in triggers:
                triggers[kk] = {
                    "k": kk, "ts": t, "group_first": min(qualified, key=lambda g: first_ts[g]),
                    "first_price": first_price[min(qualified, key=lambda g: first_ts[g])],
                    "groups": sorted(qualified), "total_net": total_net,
                }
    return triggers


def price_run_blocked(raw_copy_price, first_group_price, cap=config.PRICE_RUN_CAP):
    """D4: giá copy thô chạy quá 0,10 so với giá nhóm đầu tiên -> bỏ."""
    return (raw_copy_price - first_group_price) > cap + 1e-12


def band_ok(price_after_penalty, band=config.PRICE_BAND):
    lo, hi = band
    return (lo - 1e-12) <= price_after_penalty <= (hi + 1e-12)


def volume_ok(volume_at_trigger, min_usd=config.MARKET_VOL_MIN_USD):
    """Khối lượng thị trường TÍNH TỚI thời điểm kích hoạt (không dùng volumeNum cuối)."""
    return volume_at_trigger >= min_usd - 1e-9


class SegmentState:
    """Mỗi thị trường một lần / mỗi sự kiện một lần / phe trước thắng, mỗi đoạn."""
    def __init__(self):
        self.copied_markets = set()      # condition_id đã copy
        self.copied_events = set()       # event_id đã copy (bảng chính)
        self.suppressed_same_event = []  # bảng 16: thị trường con cùng sự kiện bị bỏ

    def admit(self, condition_id, event_id):
        """Trả ('copy', None) nếu được nhận; ngược lại ('bỏ', lý_do)."""
        if condition_id in self.copied_markets:
            return "bỏ", "thị_trường_đã_copy"
        if event_id in self.copied_events:
            self.suppressed_same_event.append(
                {"condition_id": condition_id, "event_id": event_id})
            return "bỏ", "cùng_sự_kiện_đã_copy"
        return "copy", None

    def mark(self, condition_id, event_id):
        self.copied_markets.add(condition_id)
        self.copied_events.add(event_id)
