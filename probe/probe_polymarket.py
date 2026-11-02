#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thăm dò dữ liệu Polymarket — CHỈ ĐỌC, theo checklist b–g của Giai đoạn B.
- Mỗi bước tối đa 3 request mẫu, nghỉ SLEEP giây giữa các request.
- Checkpoint bằng timestamp sau mỗi bước (bỏ qua bước đã xong khi chạy lại).
- DỪNG TOÀN BỘ khi: HTTP 429 / 403 / 5xx / lỗi mạng / độ trễ tăng bất thường.
- Không retry ngay, không tăng tốc. Ghi đúng mã lỗi và Retry-After nếu có.
- KHÔNG tính lãi, KHÔNG chọn k, KHÔNG chọn 20 ví.
Chỉ dùng thư viện chuẩn Python, không dependency, không ghi key nào.
"""
import json
import os
import statistics
import sys
import time
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# macOS: Python không tự dùng keychain hệ thống; trỏ CA bundle của hệ thống.
# Vẫn XÁC THỰC CHỨNG CHỈ đầy đủ — không hủy bỏ SSL.
_CA_CANDIDATES = ["/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"]
SSL_CTX = None
for _ca in _CA_CANDIDATES:
    if os.path.exists(_ca):
        try:
            SSL_CTX = ssl.create_default_context(cafile=_ca)
            break
        except Exception:
            pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "probe_out")
os.makedirs(OUT, exist_ok=True)

DATA = "https://data-api.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"

SLEEP = 5.0            # giây giữa các request — đi chậm có chủ đích
REQUEST_TIMEOUT = 30   # giây

state = {"stop": False, "reason": None}
latencies = []


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_req(**kw):
    kw["ts"] = utcnow()
    with open(os.path.join(OUT, "requests.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(kw, ensure_ascii=False) + "\n")


def fail(reason):
    state["stop"] = True
    state["reason"] = reason
    save_ckpt("ABORTED", reason)
    print("!! DỪNG TOÀN BỘ THĂM DÒ:", reason, flush=True)


def get(url, tag):
    """GET một URL, trả (json, status, headers). Theo dõi độ trễ và luật dừng."""
    if state["stop"]:
        raise RuntimeError("đã dừng: %s" % state["reason"])
    t0 = time.time()
    status, body, headers = None, "", {}
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "poly-probe-readonly/1.0 (paper research)",
                     "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT, context=SSL_CTX) as r:
            status = r.status
            headers = dict(r.headers)
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status = e.code
        headers = dict(e.headers or {})
        body = e.read().decode("utf-8", "replace")[:2000]
    except Exception as e:  # lỗi mạng / timeout -> dừng toàn bộ, bảo thủ
        log_req(tag=tag, url=url, error=repr(e))
        raise RuntimeError("lỗi mạng: %r" % e)
    dt = time.time() - t0
    latencies.append(dt)
    log_req(tag=tag, url=url, status=status,
            latency_ms=int(dt * 1000),
            retry_after=headers.get("Retry-After"))
    if status in (429, 403):
        raise RuntimeError("HTTP %d — Retry-After=%s" % (status, headers.get("Retry-After")))
    if status is None or status >= 500:
        raise RuntimeError("HTTP %s (lỗi máy chủ)" % status)
    # Watchdog: response chậm dần bất thường -> nghi throttle -> dừng
    if len(latencies) >= 6:
        med = statistics.median(latencies[:-1])
        if dt > max(3.0 * med, med + 3.0):
            raise RuntimeError(
                "độ trễ tăng bất thường: %.1fs vs trung vị %.1fs — nghi throttle" % (dt, med))
    if status == 404:
        return None, status, headers
    try:
        return json.loads(body), status, headers
    except Exception:
        return {"_raw_truncated": body[:2000]}, status, headers


def save_ckpt(step, status, summary=None):
    ck_path = os.path.join(OUT, "checkpoint.json")
    ck = {}
    if os.path.exists(ck_path):
        try:
            ck = json.load(open(ck_path, encoding="utf-8"))
        except Exception:
            ck = {}
    ck[step] = {"status": status, "ts": utcnow(),
                "summary": summary if summary else state["reason"]}
    json.dump(ck, open(ck_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def done(step):
    ck_path = os.path.join(OUT, "checkpoint.json")
    if os.path.exists(ck_path):
        try:
            return json.load(open(ck_path, encoding="utf-8")).get(step, {}).get("status") == "OK"
        except Exception:
            return False
    return False


def dump(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def page_info(doc):
    """Trả (rows, next_cursor, has_more) từ envelope {data, pagination}."""
    if not isinstance(doc, dict):
        return None, None, None
    rows = doc.get("data")
    pag = doc.get("pagination") or {}
    return rows, pag.get("next_cursor"), pag.get("has_more")


def ts_range(rows, field="timestamp"):
    vals = [r.get(field) for r in rows if isinstance(r, dict) and r.get(field) is not None]
    nums = []
    for v in vals:
        try:
            nums.append(int(v))
        except (TypeError, ValueError):
            pass
    return (min(nums), max(nums), len(nums)) if nums else (None, None, 0)


results = {}


def step_b():
    """b. Leaderboard SPORTS MONTH -> 1 ví mẫu; positions CLOSED limit nhỏ + user-stats."""
    url_lb = DATA + "/v2/leaderboard?" + urllib.parse.urlencode(
        {"time_period": "month", "category": "sports", "sort_by": "PNL", "limit": 5})
    doc, st, _ = get(url_lb, "b1_leaderboard")
    rows, nc, hm = page_info(doc)
    dump("step_b1_leaderboard.json", doc)
    wallets = [r.get("user_id") for r in (rows or []) if isinstance(r, dict)]
    top = wallets[0] if wallets else None
    results["b"] = {"url_leaderboard": url_lb, "status": st, "rows": len(rows or []),
                    "next_cursor": nc, "has_more": hm, "top_wallets": wallets[:5],
                    "row_keys": sorted((rows or [{}])[0].keys()) if rows else []}
    print("b1 leaderboard: %d rows, top=%s" % (len(rows or []), str(top)[:20]), flush=True)
    if not top:
        raise RuntimeError("leaderboard không trả ví nào — không làm tiếp được bước b")
    time.sleep(SLEEP)

    url_pos = DATA + "/v2/positions?" + urllib.parse.urlencode(
        {"user": top, "status": "CLOSED", "limit": 10, "sort_direction": "DESC"})
    doc2, st2, _ = get(url_pos, "b2_positions_closed")
    rows2, nc2, hm2 = page_info(doc2)
    dump("step_b2_positions_closed.json", doc2)
    lo, hi, n = ts_range(rows2, "last_event_at")
    results["b"].update({
        "url_positions": url_pos, "status_positions": st2, "positions_rows": len(rows2 or []),
        "positions_next_cursor": nc2, "positions_has_more": hm2,
        "positions_last_event_at_min_max": [lo, hi],
        "position_row_keys": sorted((rows2 or [{}])[0].keys()) if rows2 else []})
    print("b2 positions CLOSED: %d rows" % len(rows2 or []), flush=True)
    time.sleep(SLEEP)

    url_us = DATA + "/v2/user-stats?" + urllib.parse.urlencode({"user": top})
    doc3, st3, _ = get(url_us, "b3_user_stats")
    dump("step_b3_user_stats.json", doc3)
    results["b"].update({"url_user_stats": url_us, "status_user_stats": st3,
                         "user_stats_keys": sorted(doc3.keys()) if isinstance(doc3, dict) else str(type(doc3))})
    print("b3 user-stats: %s" % st3, flush=True)
    results["b"]["wallet"] = top
    save_ckpt("b", "OK", "wallet=%s" % top)


def step_c(wallet):
    """c. Cửa sổ 7 ngày cho ví đó: trades taker_only true/false (+activity để tìm usdc_size)."""
    end = int(time.time())
    start = end - 7 * 86400
    out = {"window_start": start, "window_end": end}
    for label, tok in (("taker_only=true", "true"), ("taker_only=false", "false")):
        url = DATA + "/v2/trades?" + urllib.parse.urlencode(
            {"user": wallet, "taker_only": tok, "start": start, "end": end, "limit": 100})
        doc, st, _ = get(url, "c_trades_%s" % tok)
        rows, nc, hm = page_info(doc)
        dump("step_c_trades_%s.json" % tok, doc)
        lo, hi, n = ts_range(rows)
        buys = [r for r in (rows or []) if r.get("side") == "BUY"]
        rec = {"url": url, "status": st, "rows": len(rows or []),
               "next_cursor": nc, "has_more": hm,
               "ts_min_max_count": [lo, hi, n],
               "n_buy": len(buys),
               "row_keys": sorted((rows or [{}])[0].keys()) if rows else [],
               "has_usdc_size_field": any("usdc_size" in r for r in (rows or []) if isinstance(r, dict))}
        out[label] = rec
        print("c %s: %d rows (BUY=%d), cursor=%s" % (label, len(rows or []), len(buys), str(nc)[:24]), flush=True)
        time.sleep(SLEEP)

    url_act = DATA + "/v2/activity?" + urllib.parse.urlencode(
        {"user": wallet, "type": "TRADE", "start": start, "end": end, "limit": 100})
    doc, st, _ = get(url_act, "c_activity_trade")
    rows, nc, hm = page_info(doc)
    dump("step_c_activity_trade.json", doc)
    lo, hi, n = ts_range(rows)
    out["activity_TRADE"] = {
        "url": url_act, "status": st, "rows": len(rows or []), "next_cursor": nc,
        "ts_min_max_count": [lo, hi, n],
        "row_keys": sorted((rows or [{}])[0].keys()) if rows else [],
        "has_usdc_size_field": any("usdc_size" in r for r in (rows or []) if isinstance(r, dict))}
    print("c activity TRADE: %d rows" % len(rows or []), flush=True)
    results["c"] = out
    save_ckpt("c", "OK", "trades true/false + activity")


def pick_step_d_conditions(wallet):
    """Chọn 3 mã thị trường từ dữ liệu ví: 1 neg-risk, 1 moneyline 2 cửa, 1 đã chốt."""
    pos = []
    for fn in ("step_b2_positions_closed.json", "step_c_trades_false.json"):
        p = os.path.join(OUT, fn)
        if os.path.exists(p):
            try:
                doc = json.load(open(p, encoding="utf-8"))
                pos.extend(doc.get("data") or [])
            except Exception:
                pass
    seen, uniq = set(), []
    for r in pos:
        c = r.get("condition_id")
        if c and c not in seen:
            seen.add(c)
            uniq.append(r)
    resolved = next((r for r in uniq if r.get("status") in ("REDEEMABLE", "CLOSED")), None)
    negrisk = next((r for r in uniq if r.get("negative_risk") is True), None)
    two = next((r for r in uniq if r is not negrisk and r is not resolved), None)
    if negrisk is None:
        negrisk = next((r for r in uniq if r.get("outcome_index", 0) not in (0, 1)), None)
    return {
        "neg_risk": negrisk.get("condition_id") if negrisk else None,
        "moneyline_2": two.get("condition_id") if two else None,
        "resolved": resolved.get("condition_id") if resolved else None,
    }


def step_d(wallet):
    """d. Gamma: 3 mã thị trường — ghi outcomes, clobTokenIds, negRisk, tags, volumeNum,
    feeSchedule, closed, resolutionStatus, outcomePrices."""
    picks = pick_step_d_conditions(wallet)
    conds = [c for c in (picks["neg_risk"], picks["moneyline_2"], picks["resolved"]) if c]
    if not conds:
        raise RuntimeError("không chọn được mã thị trường nào từ dữ liệu ví")
    url = GAMMA + "/markets?" + urllib.parse.urlencode({"condition_ids": ",".join(conds), "limit": 10})
    doc, st, _ = get(url, "d_gamma_markets")
    dump("step_d_gamma_markets.json", doc)
    rows = doc if isinstance(doc, list) else doc.get("data") or []
    want = ["outcomes", "clobTokenIds", "negRisk", "tags", "volumeNum", "feeSchedule",
            "closed", "resolutionStatus", "outcomePrices", "conditionId", "events",
            "sportsMarketType", "gameStartTime", "startDate", "endDate"]
    per_market = []
    for m in rows:
        per_market.append({
            "conditionId": m.get("conditionId"),
            "title": (m.get("question") or "")[:90],
            "present_fields": {k: (m.get(k) is not None) for k in want},
            "outcomes": m.get("outcomes"),
            "negRisk": m.get("negRisk"),
            "volumeNum": m.get("volumeNum"),
            "closed": m.get("closed"),
            "resolutionStatus": m.get("resolutionStatus"),
            "outcomePrices": m.get("outcomePrices"),
            "feeSchedule_raw": m.get("feeSchedule"),
            "tags": [t.get("label") if isinstance(t, dict) else t
                     for t in (m.get("tags") or [])][:8],
        })
    results["d"] = {"url": url, "status": st, "rows": len(rows), "picks": picks,
                    "markets": per_market,
                    "all_row_keys": sorted(rows[0].keys()) if rows else []}
    print("d gamma: %d markets (picks=%s)" % (len(rows), picks), flush=True)
    save_ckpt("d", "OK", "gamma %d markets" % len(rows))


def step_e():
    """e. Resolutions cho 1 thị trường đã chốt; đối chiếu payout với Gamma; kiếm hòa 0,5."""
    cond = (results.get("d", {}).get("picks", {}) or {}).get("resolved")
    if not cond:
        d_doc = {}
        p = os.path.join(OUT, "step_d_gamma_markets.json")
        if os.path.exists(p):
            raw = json.load(open(p, encoding="utf-8"))
            rows = raw if isinstance(raw, list) else raw.get("data") or []
            for m in rows:
                if m.get("resolutionStatus") == "resolved":
                    cond = m.get("conditionId")
                    break
    if not cond:
        results["e"] = {"error": "THIẾU: không có thị trường đã chốt trong mẫu để lấy resolutions"}
        save_ckpt("e", "OK", "không có thị trường đã chốt — ghi THIẾU")
        return
    url = DATA + "/v2/resolutions?" + urllib.parse.urlencode({"condition": cond})
    doc, st, _ = get(url, "e_resolutions")
    dump("step_e_resolutions.json", doc)
    rows = doc.get("data") if isinstance(doc, dict) else doc
    rows = rows or []
    # payouts là micro-USDC/cổ phần: 1_000_000 = 1 USD, 500_000 = 0,5 (hòa)
    payouts = []
    for r in rows:
        if isinstance(r, dict) and r.get("payouts") is not None:
            payouts.append(r.get("payouts"))
    has_half = any(any(isinstance(x, (int, float)) and abs(float(x) - 500000.0) < 1 for x in p)
                   for p in payouts if isinstance(p, list))
    # Đối chiếu Gamma
    gamma_payout = None
    p = os.path.join(OUT, "step_d_gamma_markets.json")
    if os.path.exists(p):
        raw = json.load(open(p, encoding="utf-8"))
        grows = raw if isinstance(raw, list) else raw.get("data") or []
        for m in grows:
            if m.get("conditionId") == cond:
                gamma_payout = {"outcomePrices": m.get("outcomePrices"),
                                "resolutionStatus": m.get("resolutionStatus")}
    results["e"] = {"url": url, "status": st, "condition": cond, "rows": len(rows),
                    "payouts_micro_usdc": payouts, "co_hoa_0_5": has_half,
                    "gamma_doi_chieu": gamma_payout,
                    "resolution_row_keys": sorted(rows[0].keys()) if rows else []}
    print("e resolutions: %d rows, hòa0.5=%s" % (len(rows), has_half), flush=True)
    save_ckpt("e", "OK", "resolutions %d rows" % len(rows))


def step_f():
    """f. prices-history 7 ngày và 90 ngày cho 1 token; ghi hạt thời gian thực tế."""
    token = None
    p = os.path.join(OUT, "step_d_gamma_markets.json")
    if os.path.exists(p):
        raw = json.load(open(p, encoding="utf-8"))
        rows = raw if isinstance(raw, list) else raw.get("data") or []
        for m in rows:
            ct = m.get("clobTokenIds")
            if ct:
                if isinstance(ct, str):
                    try:
                        ct = json.loads(ct)
                    except Exception:
                        ct = [ct]
                if isinstance(ct, list) and ct:
                    token = str(ct[0])
                    break
    if not token:
        # dự phòng: lấy token từ trades
        p2 = os.path.join(OUT, "step_c_trades_true.json")
        if os.path.exists(p2):
            rows = (json.load(open(p2, encoding="utf-8")).get("data") or [])
            if rows:
                token = rows[0].get("token_id")
    if not token:
        results["f"] = {"error": "THIẾU: không có token_id nào trong mẫu"}
        save_ckpt("f", "OK", "không có token")
        return
    end = int(time.time())
    windows = {"7d": (end - 7 * 86400, end), "90d": (end - 90 * 86400, end)}
    out = {"token_id": token}
    for name, (s, e) in windows.items():
        url = DATA + "/v2/prices-history?" + urllib.parse.urlencode(
            {"token_id": token, "start": s, "end": e})
        doc, st, _ = get(url, "f_prices_%s" % name)
        dump("step_f_prices_%s.json" % name, doc)
        rows, nc, hm = page_info(doc)
        pts = rows or []
        times = sorted(int(r["t"]) for r in pts if isinstance(r, dict) and r.get("t") is not None)
        gaps = [b - a for a, b in zip(times, times[1:])]
        gran = {"min_gap": min(gaps), "max_gap": max(gaps),
                "median_gap": statistics.median(gaps)} if gaps else None
        out[name] = {"url": url, "status": st, "points": len(pts),
                     "next_cursor": nc, "t_min": times[0] if times else None,
                     "t_max": times[-1] if times else None,
                     "gap_seconds": gran,
                     "row_keys": sorted(pts[0].keys()) if pts else []}
        print("f %s: %d điểm, gap median=%s" % (
            name, len(pts), gran["median_gap"] if gran else "?"), flush=True)
        time.sleep(SLEEP)
    results["f"] = out
    save_ckpt("f", "OK", "prices-history 7d+90d")


def step_g():
    """g. ĐẾM MÔ TẢ, không tính lãi: 2–3 ví leaderboard, đếm thị trường + cửa trùng
    trong 24 giờ, ước tốc độ tín hiệu cho k = 2, 3."""
    lb_path = os.path.join(OUT, "step_b1_leaderboard.json")
    if not os.path.exists(lb_path):
        results["g"] = {"error": "THIẾU: không có leaderboard"}
        save_ckpt("g", "OK", "thiếu leaderboard")
        return
    wallets = [r.get("user_id") for r in
               (json.load(open(lb_path, encoding="utf-8")).get("data") or [])
               if isinstance(r, dict) and r.get("user_id")][:3]
    end = int(time.time())
    start = end - 7 * 86400
    per_wallet = {}
    all_buys = []
    for w in wallets:
        url = DATA + "/v2/trades?" + urllib.parse.urlencode(
            {"user": w, "taker_only": "false", "start": start, "end": end, "limit": 500})
        doc, st, _ = get(url, "g_trades_%s" % w[:10])
        rows, nc, hm = page_info(doc)
        buys = [r for r in (rows or []) if r.get("side") == "BUY"]
        conds = {r.get("condition_id") for r in buys if r.get("condition_id")}
        per_wallet[w] = {"url": url, "rows": len(rows or []), "n_buy": len(buys),
                         "n_distinct_condition": len(conds),
                         "next_cursor": nc, "has_more": hm}
        for r in buys:
            all_buys.append({"wallet": w, "condition_id": r.get("condition_id"),
                             "token_id": r.get("token_id"), "ts": r.get("timestamp")})
        print("g %s...: %d rows, BUY=%d, cond=%d" % (w[:10], len(rows or []), len(buys), len(conds)), flush=True)
        time.sleep(SLEEP)
    # Cửa trùng: cùng condition_id + token_id, các ví khác nhau, trong cửa sổ 24h
    by_key = {}
    for b in all_buys:
        if b["condition_id"] and b["token_id"] and b["ts"] is not None:
            by_key.setdefault((b["condition_id"], b["token_id"]), []).append(b)
    k2_events = k3_events = 0
    detail = []
    for key, items in by_key.items():
        items.sort(key=lambda x: int(x["ts"]))
        # quét cửa sổ trượt 24h đếm số ví khác nhau
        used_k2 = used_k3 = set()
        for i, it in enumerate(items):
            window = [x for x in items[i:]
                      if int(x["ts"]) - int(it["ts"]) <= 86400]
            wallets_in = {x["wallet"] for x in window}
            sig_id = (key, it["ts"])
            if len(wallets_in) >= 2 and sig_id not in used_k2:
                used_k2.add(sig_id)
            if len(wallets_in) >= 3 and sig_id not in used_k3:
                used_k3.add(sig_id)
        # đếm "sự kiện cửa" từng xuất hiện >=2 / >=3 ví khác nhau trong bất kỳ cửa sổ 24h nào
        best = 0
        for i, it in enumerate(items):
            window = {x["wallet"] for x in items[i:]
                      if int(x["ts"]) - int(it["ts"]) <= 86400}
            best = max(best, len(window))
        if best >= 2:
            k2_events += 1
        if best >= 3:
            k3_events += 1
        if best >= 2:
            detail.append({"condition_id": key[0], "token_id": key[1][:16] + "…",
                           "max_wallets_in_24h": best})
    total_buy = len(all_buys)
    results["g"] = {
        "note": "ĐẾM MÔ TẢ TRONG 7 NGÀY, KHÔNG TÍNH LÃI, KHÔNG CHỌN k",
        "wallets": per_wallet, "n_wallets": len(wallets),
        "window_days": 7,
        "total_buy_rows_7d_1page": total_buy,
        "canh_trung_24h_toi_thieu_2_vi": k2_events,
        "canh_trung_24h_toi_thieu_3_vi": k3_events,
        "detail_top": sorted(detail, key=lambda x: -x["max_wallets_in_24h"])[:10],
        "uoc_linh_tinh": {
            "k2_signals_per_7d_per_3wallets": k2_events,
            "k3_signals_per_7d_per_3wallets": k3_events,
            "canh_bao": "chỉ 1 trang request mỗi ví, has_more có thể còn trang sau; đây là CẠN DƯỚI của tốc độ tín hiệu",
        },
    }
    print("g: k2=%d, k3=%d (cửa trùng 24h trong 7 ngày)" % (k2_events, k3_events), flush=True)
    save_ckpt("g", "OK", "k2=%d k3=%d" % (k2_events, k3_events))


def main():
    print("=== THĂM DÒ CHỈ ĐỌC POLYMARKET — %s ===" % utcnow(), flush=True)
    try:
        if done("b"):
            print("(b đã xong, bỏ qua)", flush=True)
        else:
            step_b()
        wallet = results.get("b", {}).get("wallet")
        if not wallet and os.path.exists(os.path.join(OUT, "checkpoint.json")):
            wallet = json.load(open(os.path.join(OUT, "checkpoint.json"))) \
                .get("b", {}).get("summary", "").replace("wallet=", "").strip()
        if done("c"):
            print("(c đã xong, bỏ qua)", flush=True)
        elif wallet:
            step_c(wallet)
        if done("d"):
            print("(d đã xong, bỏ qua)", flush=True)
        elif wallet:
            step_d(wallet)
        if done("e"):
            print("(e đã xong, bỏ qua)", flush=True)
        else:
            step_e()
        if done("f"):
            print("(f đã xong, bỏ qua)", flush=True)
        else:
            step_f()
        if done("g"):
            print("(g đã xong, bỏ qua)", flush=True)
        else:
            step_g()
    except RuntimeError as e:
        fail(str(e))
    dump("results_summary.json", results)
    save_ckpt("end", "DONE" if not state["stop"] else "ABORTED")
    print("=== KẾT THÚC: %s ===" % ("DỪNG SỚM: " + str(state["reason"]) if state["stop"] else "đủ bước"), flush=True)


if __name__ == "__main__":
    main()
