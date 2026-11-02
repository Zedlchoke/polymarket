# -*- coding: utf-8 -*-
"""Selection — 10 cửa Q3, lãi giữ-tới-chốt trên mỗi đồng đặt, gộp nhóm, xếp hạng, luật hòa.
D5 đã chốt: 80 lệnh. Tiền mặt: usdc_size trên activity (§19.4)."""
from . import config
from .ledger import entry_fee


def trade_shares(trade):
    """Cổ phần của lệnh vào = tiền mặt / giá thực hiện."""
    return trade["usdc_size"] / trade["price"]


def hold_pnl(trade, res_price, fee_rate):
    """Q3.4: lãi giữ-tới-chốt của MỘT lệnh vào đã chốt =
    cổ phần × giá chốt (0/0,5/1) − tiền mua − phí theo ngày."""
    sh = trade_shares(trade)
    fee = entry_fee(sh, trade["price"], fee_rate)
    return sh * res_price - trade["usdc_size"] - fee


def wallet_stats(trades, resolutions, fee_rates, seg_end):
    """trades: activity TRADE rows (usdc_size, price, condition_id, token_id, timestamp,
    side='BUY'); resolutions: {condition_id: giá_chốt}; fee_rates: {condition_id: rate}.
    Chỉ tính lệnh vào (BUY) đã chốt trước cuối đoạn."""
    closed = [t for t in trades
              if t.get("side") == "BUY"
              and t.get("condition_id") in resolutions
              and int(t["timestamp"]) <= seg_end]
    pnl = 0.0
    cash = 0.0
    per_market = {}
    for t in closed:
        p = hold_pnl(t, resolutions[t["condition_id"]], fee_rates[t["condition_id"]])
        pnl += p
        cash += t["usdc_size"]
        per_market[t["condition_id"]] = per_market.get(t["condition_id"], 0.0) + p
    hold_roi = (pnl / cash) if cash > 0 else None
    max_share = (max(per_market.values()) / pnl) if pnl > 0 and per_market else None
    return {"n_trades": len(trades), "n_buy_closed": len(closed),
            "hold_pnl": pnl, "hold_cash": cash, "hold_roi": hold_roi,
            "max_market_pnl_share": max_share,
            "n_markets": len({t["condition_id"] for t in trades}),
            "cash_volume": sum(t["usdc_size"] for t in trades
                               if t.get("side") == "BUY"),
            "per_market_pnl": per_market}


def both_sides_ratio(trades):
    """Q3.7: tỷ lệ thị trường mà ví TỪNG cùng lúc giữ cổ phần >0 của cả hai token
    (tính lại từ chuỗi TRADE, loại SPLIT/MERGE/REWARD/MAKER_REBATE)."""
    from collections import defaultdict
    net = defaultdict(lambda: defaultdict(float))  # cond -> token -> shares
    holding_both = set()
    seen = set()
    EXCLUDED = {"SPLIT", "MERGE", "REWARD", "MAKER_REBATE"}
    for t in trades:
        if t.get("type") in EXCLUDED:
            continue
        cond, tok = t["condition_id"], str(t["token_id"])
        delta = t["usdc_size"] / t["price"] * (1 if t.get("side") == "BUY" else -1)
        net[cond][tok] += delta
        toks = [k for k, v in net[cond].items() if v > 1e-9]
        if len(toks) >= 2:
            holding_both.add(cond)
        seen.add(cond)
    return (len(holding_both) / len(seen)) if seen else 0.0


def passes_gates(stats, both_ratio, active_trades_14d, realized_pnl_positive):
    """10 cửa Q3 — trả (bool, cổng_trượt). D5: >=80 lệnh."""
    g = []
    g.append(("vol", stats["cash_volume"] >= config.VOL_MIN_USD))
    g.append(("trades", stats["n_trades"] >= config.TRADES_MIN))
    g.append(("markets", stats["n_markets"] >= config.MARKETS_MIN))
    g.append(("hold_roi", stats["hold_roi"] is not None and stats["hold_roi"] > 0))
    g.append(("realized", realized_pnl_positive))
    g.append(("active", active_trades_14d >= config.ACTIVE_TRADES))
    g.append(("concentration",
              stats["max_market_pnl_share"] is not None
              and stats["max_market_pnl_share"] <= config.ONE_MARKET_PNL_CAP))
    g.append(("both_sides", both_ratio <= config.BOTH_SIDES_RATIO))
    fails = [name for name, ok in g if not ok]
    # cổng 8 bot: trên 2000 lệnh và lãi/khối lượng <1% -> loại
    pnl_vol = (stats["hold_pnl"] / stats["cash_volume"]) if stats["cash_volume"] > 0 else 0
    bot = stats["n_trades"] > config.BOT_TRADES and pnl_vol < config.BOT_PNL_VOL_RATIO
    if bot:
        fails.append("bot")
    return (len(fails) == 0), fails


def rank_key(w):
    """Q3.9: xếp theo lãi giữ-tới-chốt trên mỗi đồng đặt giảm dần; hòa: nhiều thị trường
    hơn, rồi nhiều lệnh hơn, rồi mã ví theo chữ cái."""
    return (-w["stats"]["hold_roi"], -w["stats"]["n_markets"],
            -w["stats"]["n_trades"], w["address"])


def pair_overlap(trades_a, trades_b):
    """Q3.10: trùng = cùng condition + cùng token, cách nhau <=60 phút.
    Trả (số_trùng, tỉ_lệ = trùng/số_lệnh_ít_hơn)."""
    def keys(ts):
        return [(t["condition_id"], str(t["token_id"]), int(t["timestamp"]))
                for t in ts if t.get("side") == "BUY"]
    ka, kb = keys(trades_a), keys(trades_b)
    if not ka or not kb:
        return 0, 0.0
    shared = 0
    used = set()
    for c, tok, tsa in ka:
        for j, (c2, tok2, tsb) in enumerate(kb):
            if j in used:
                continue
            if c2 == c and tok2 == tok and abs(tsa - tsb) <= config.GROUP_MATCH_WINDOW_MIN * 60:
                shared += 1
                used.add(j)
                break
    ratio = shared / min(len(ka), len(kb))
    return shared, ratio


def should_merge(trades_a, trades_b):
    shared, ratio = pair_overlap(trades_a, trades_b)
    return shared >= config.GROUP_MIN_SHARED and ratio >= config.GROUP_RATIO


def merge_groups(candidates):
    """candidates: [{address, stats, trades}] đã xếp hạng (giảm dần theo rank_key).
    Duyệt theo thứ tự lãi giảm dần: ví sau trùng với bất kỳ thành viên nhóm nào đã giữ
    thì nhập nhóm đó; ngược lại lập nhóm mới. Trả danh sách nhóm."""
    groups = []  # mỗi nhóm: {'members': [...], 'best': candidate}
    for cand in candidates:
        placed = False
        for grp in groups:
            if any(should_merge(m["trades"], cand["trades"]) for m in grp["members"]):
                grp["members"].append(cand)
                placed = True
                break
        if not placed:
            groups.append({"members": [cand], "best": cand})
    return groups


def select_groups(candidates, n_target=config.N_GROUPS_TARGET):
    """Gộp trước (Q3.10), xếp hạng sau (Q3.9 đã sắp candidates), đủ n_target nhóm;
    không đủ -> trả kèm cờ thiếu mẫu."""
    ranked = sorted(candidates, key=rank_key)
    groups = merge_groups(ranked)
    groups.sort(key=lambda g: rank_key(g["best"]))
    chosen = groups[:n_target]
    return chosen, {"n_groups_total": len(groups), "enough": len(groups) >= n_target}
