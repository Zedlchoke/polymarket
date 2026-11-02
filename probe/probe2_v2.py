#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thăm dò bổ sung V2 — CHỈ ĐỌC. 8 việc làm rõ lỗ hổng của báo cáo thăm dò V1.
- Đi chậm (nghỉ SLEEP giây), checkpoint bằng timestamp, bỏ qua stream đã xong.
- DỪNG TOÀN BỘ khi HTTP 429/403/5xx/lỗi mạng/độ trễ tăng bất thường.
- Không retry ngay, không tăng tốc. KHÔNG tính lãi, KHÔNG chọn k, KHÔNG chọn 20 ví.
Chỉ thư viện chuẩn. Không key. Chi phí 0 đồng.
"""
import json
import os
import ssl
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "probe_out_v2")
os.makedirs(OUT, exist_ok=True)

DATA = "https://data-api.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

SLEEP = float(os.environ.get("PROBE_SLEEP", "6.0"))  # phiên 2 sau watchdog: đặt 10.0
MAX_PAGES = 40          # trần an toàn mỗi stream phân trang (ghi rõ nếu chạm trần)
REQUEST_TIMEOUT = 30

state = {"stop": False, "reason": None}
latencies = []

SSL_CTX = None
for _ca in ("/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"):
    if os.path.exists(_ca):
        SSL_CTX = ssl.create_default_context(cafile=_ca)
        break


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_req(**kw):
    kw["ts"] = utcnow()
    with open(os.path.join(OUT, "requests.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(kw, ensure_ascii=False) + "\n")


def get(url, tag):
    if state["stop"]:
        raise RuntimeError("đã dừng: %s" % state["reason"])
    t0 = time.time()
    status, body, headers = None, "", {}
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "poly-probe-readonly/1.0 (paper research)",
                          "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT, context=SSL_CTX) as r:
            status, headers = r.status, dict(r.headers)
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, headers = e.code, dict(e.headers or {})
        body = e.read().decode("utf-8", "replace")[:2000]
    except Exception as e:
        log_req(tag=tag, url=url, error=repr(e))
        raise RuntimeError("lỗi mạng: %r" % e)
    dt = time.time() - t0
    latencies.append(dt)
    log_req(tag=tag, url=url, status=status, latency_ms=int(dt * 1000),
            retry_after=headers.get("Retry-After"))
    if status in (429, 403):
        raise RuntimeError("HTTP %d — Retry-After=%s" % (status, headers.get("Retry-After")))
    if status is None or status >= 500:
        raise RuntimeError("HTTP %s (lỗi máy chủ)" % status)
    if len(latencies) >= 6:
        med = statistics.median(latencies[:-1])
        if dt > max(3.0 * med, med + 3.0):
            raise RuntimeError("độ trễ tăng bất thường: %.1fs vs trung vị %.1fs — nghi throttle" % (dt, med))
    if status == 404:
        return None, status
    try:
        return json.loads(body), status
    except Exception:
        return {"_raw": body[:2000]}, status


def ck():
    p = os.path.join(OUT, "checkpoint.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def ck_set(step, status, summary=None):
    c = ck()
    c[step] = {"status": status, "ts": utcnow(), "summary": summary or state["reason"]}
    json.dump(c, open(os.path.join(OUT, "checkpoint.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def dump(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def page(doc):
    if not isinstance(doc, dict):
        return [], None, False
    return doc.get("data") or [], (doc.get("pagination") or {}).get("next_cursor"), \
        (doc.get("pagination") or {}).get("has_more")


# ---------------------------------------------------------------- Việc 1
V1_CODES = {
    "ghana_neg_risk": "0x0256ef63427ed0d9eefa1422eee948165a2a215b0741a339025fb08b2cf6e15d",
    "grizzlies_true": "0x401c1614a93ddc098c97338b5452d887f4ca1617a4445c2a1a966b6aa58e28d7",
    "spain_resolved": "0x51166276fa646ca50165f7d030c297138ed1d62dc41f6ffde21e962c44182074",
}
V1_SLUG = "nba-mem-uta-2026-10-26"


def viec1():
    """Gamma: comma phẳng (đúng dạng) có/không closed=any; slug nếu còn thiếu."""
    out = []
    codes_flat = ",".join(V1_CODES.values())
    for label, extra in (("comma_KHONG_closed", {}),
                         ("comma_CO_closed_any", {"closed": "any"})):
        q = [("condition_ids", codes_flat), ("limit", "10")] + list(extra.items())
        url = GAMMA + "/markets?" + urllib.parse.urlencode(q)
        doc, st = get(url, "v1_gamma_%s" % label)
        rows = doc if isinstance(doc, list) else []
        dump("v1_gamma_%s.json" % label, doc)
        got = [m.get("conditionId") for m in rows]
        out.append({"url": url, "http": st, "rows": len(rows), "tra_ra": got})
        print("V1 %s -> HTTP %s, %d rows: %s" % (label, st, len(rows), got), flush=True)
        time.sleep(SLEEP)
    missing = set(V1_CODES.values()) - {c for r in out for c in r["tra_ra"]}
    if missing:
        q = [("slug", V1_SLUG), ("closed", "any"), ("limit", "5")]
        url = GAMMA + "/markets?" + urllib.parse.urlencode(q)
        doc, st = get(url, "v1_gamma_slug")
        rows = doc if isinstance(doc, list) else []
        dump("v1_gamma_slug.json", doc)
        got = [m.get("conditionId") for m in rows]
        out.append({"url": url, "http": st, "rows": len(rows), "tra_ra": got})
        print("V1 slug %s -> HTTP %s, %s" % (V1_SLUG, st, got), flush=True)
    dump("v1_summary.json", {"requests": out, "missing": sorted(missing)})
    ck_set("v1", "OK", "missing=%s" % sorted(missing)[:1])


# ---------------------------------------------------------------- Việc 2
WALLETS = {
    "bb": "0xf0318c32136c2db7fec88b84869aee6a1106c80c",
    "joseph": "0xcdcccd0f2d86e450d973da415ad2430e5cc7935a",
    "upthe": "0x2a69660046d7acc4ab204d7cc5ba78b0776cd2f7",
}
W_START = 1793013231  # khớp cửa sổ 7 ngày của V1
W_END = 1793618031


def paginate(step, base_url_first):
    """Đi hết trang tới next_cursor null. Trần MAX_PAGES trang, ghi rõ nếu chạm trần."""
    st = ck().get(step, {})
    if st.get("status") == "OK":
        print("(%s đã xong)" % step, flush=True)
        return json.load(open(os.path.join(OUT, step + ".json"), encoding="utf-8"))
    all_rows, cursor, npages, capped = [], None, 0, False
    url = base_url_first
    while True:
        doc, http = get(url, "%s_p%d" % (step, npages + 1))
        rows, nc, hm = page(doc)
        all_rows.extend(rows)
        npages += 1
        if nc is None or not hm:
            break
        if npages >= MAX_PAGES:
            capped = True
            break
        cursor = nc
        sep = "&" if "?" in base_url_first else "?"
        url = base_url_first + sep + "cursor=" + urllib.parse.quote(nc, safe="")
        time.sleep(SLEEP)
    lo_hi = None
    tss = [int(r["timestamp"]) for r in all_rows if r.get("timestamp") is not None]
    if tss:
        lo_hi = [min(tss), max(tss)]
    res = {"pages": npages, "rows": len(all_rows), "last_next_cursor": cursor,
           "hit_page_cap": capped, "ts_min_max": lo_hi}
    dump(step + ".json", res)
    dump(step + "_rows.json", all_rows)
    ck_set(step, "OK" if not capped else "CAP",
           "%d pages %d rows capped=%s" % (npages, len(all_rows), capped))
    print("%s: %d trang, %d dòng, cursor=%s, cap=%s, ts=%s" %
          (step, npages, len(all_rows), str(cursor)[:20], capped, lo_hi), flush=True)
    return res


def viec2():
    """Đi hết trades + activity TRADE cho 3 ví; chẩn đoán ví 0 dòng; (đếm lại ở offline)."""
    for key in ("bb", "joseph", "upthe"):
        w = WALLETS[key]
        u_tr = DATA + "/v2/trades?" + urllib.parse.urlencode(
            {"user": w, "taker_only": "false", "start": W_START, "end": W_END, "limit": "500"})
        paginate("v2_trades_%s" % key, u_tr)
        u_ac = DATA + "/v2/activity?" + urllib.parse.urlencode(
            {"user": w, "type": "TRADE", "start": W_START, "end": W_END, "limit": "500"})
        paginate("v2_activity_%s" % key, u_ac)


def viec2_joseph():
    """Chẩn đoán từng khả năng cho ví joseph00677 trả 0 dòng."""
    w = WALLETS["joseph"]
    out = {}
    # 1) leaderboard lookup 1 ví — user_id có đứng hạng không
    url = DATA + "/v2/leaderboard?" + urllib.parse.urlencode({"user": w})
    doc, st = get(url, "vj_leaderboard_user")
    dump("vj_leaderboard_user.json", doc)
    out["leaderboard_user"] = {"url": url, "http": st, "body": doc if not isinstance(doc, dict) else {k: doc.get(k) for k in ('data',)}}
    time.sleep(SLEEP)
    # 2) user-stats — địa chỉ có phải proxy wallet hoạt động không
    url = DATA + "/v2/user-stats?" + urllib.parse.urlencode({"user": w})
    doc, st = get(url, "vj_user_stats")
    dump("vj_user_stats.json", doc)
    out["user_stats"] = {"url": url, "http": st,
                         "data": doc.get("data") if isinstance(doc, dict) else doc}
    time.sleep(SLEEP)
    # 3) trades 7 ngày taker_only=TRUE (đối chiếu với false đã = 0)
    url = DATA + "/v2/trades?" + urllib.parse.urlencode(
        {"user": w, "taker_only": "true", "start": W_START, "end": W_END, "limit": "100"})
    doc, st = get(url, "vj_trades_true_7d")
    rows, nc, hm = page(doc)
    dump("vj_trades_true_7d.json", doc)
    out["trades_true_7d"] = {"url": url, "http": st, "rows": len(rows)}
    time.sleep(SLEEP)
    # 4) trades 30 ngày taker_only=false, limit nhỏ — ví có hoạt động gần đây không
    url = DATA + "/v2/trades?" + urllib.parse.urlencode(
        {"user": w, "taker_only": "false", "start": W_END - 30 * 86400, "end": W_END, "limit": "100"})
    doc, st = get(url, "vj_trades_30d")
    rows, nc, hm = page(doc)
    dump("vj_trades_30d.json", doc)
    tss = [int(r["timestamp"]) for r in rows if r.get("timestamp")]
    out["trades_30d"] = {"url": url, "http": st, "rows": len(rows),
                         "ts_min_max": [min(tss), max(tss)] if tss else None}
    time.sleep(SLEEP)
    # 5) positions mọi trạng thái — ví chơi thị trường gì
    url = DATA + "/v2/positions?" + urllib.parse.urlencode(
        {"user": w, "limit": "20", "sort_direction": "DESC"})
    doc, st = get(url, "vj_positions_all")
    rows, nc, hm = page(doc)
    dump("vj_positions_all.json", doc)
    out["positions_all"] = {
        "url": url, "http": st, "rows": len(rows),
        "titles": [r.get("title") for r in rows[:10]],
        "statuses": sorted({r.get("status") for r in rows}),
        "event_slugs": [r.get("event_slug") for r in rows[:10]]}
    dump("vj_summary.json", out)
    ck_set("vjoseph", "OK")
    for k, v in out.items():
        print("VJ %s: %s" % (k, {x: y for x, y in v.items() if x not in ('url',)}), flush=True)


# ---------------------------------------------------------------- Việc 3
def viec3():
    """Mẫu: thể thao đã đóng, không-thể-thao đã đóng, thể thao đang mở, không-thể-thao đang mở."""
    out = {}
    qs = {
        "sports_closed": [("sports_market_types", "moneyline"), ("closed", "true"),
                          ("limit", "8"), ("order", "volumeNum"), ("ascending", "false")],
        "nonsports_closed": [("closed", "true"), ("limit", "12"),
                             ("order", "volumeNum"), ("ascending", "false")],
        "sports_open": [("sports_market_types", "moneyline"), ("closed", "false"),
                        ("limit", "5"), ("order", "volumeNum"), ("ascending", "false")],
        "nonsports_open": [("closed", "false"), ("limit", "5"),
                           ("order", "volumeNum"), ("ascending", "false")],
    }
    for label, q in qs.items():
        url = GAMMA + "/markets?" + urllib.parse.urlencode(q)
        doc, st = get(url, "v3_%s" % label)
        rows = doc if isinstance(doc, list) else []
        dump("v3_%s.json" % label, doc)
        slim = []
        for m in rows:
            slim.append({
                "conditionId": m.get("conditionId"),
                "q": (m.get("question") or "")[:70],
                "slug": m.get("slug"),
                "tags": [t.get("label") if isinstance(t, dict) else t for t in (m.get("tags") or [])][:8],
                "sportsMarketType": m.get("sportsMarketType"),
                "gameStartTime": m.get("gameStartTime"),
                "event_title": (m.get("events") or [{}])[0].get("title") if m.get("events") else None,
                "negRisk": m.get("negRisk"),
                "outcomes": m.get("outcomes"),
            })
        out[label] = {"url": url, "http": st, "rows": len(rows), "markets": slim}
        print("V3 %s: HTTP %s, %d rows" % (label, st, len(rows)), flush=True)
        time.sleep(SLEEP)
    dump("v3_summary.json", out)
    ck_set("v3", "OK")


# ---------------------------------------------------------------- Việc 4
def viec4():
    """Kiểm tra nguồn spread: sổ lệnh hiện tại, tokens, prices-history (đã biết)."""
    out = {}
    tok = "103502227257868648930155562667494664756217753218326084089472320347435597174870"
    url = CLOB + "/book?" + urllib.parse.urlencode({"token_id": tok})
    doc, st = get(url, "v4_clob_book")
    dump("v4_clob_book.json", doc)
    out["clob_book_now"] = {"url": url, "http": st,
                            "keys": sorted(doc.keys()) if isinstance(doc, dict) else "list",
                            "n_bids_levels": len(doc.get("bids") or []) if isinstance(doc, dict) else None,
                            "n_asks_levels": len(doc.get("asks") or []) if isinstance(doc, dict) else None}
    time.sleep(SLEEP)
    # /v2/tokens xem có midpoint/spread không (contract v2 có endpoint /v2/tokens)
    url = DATA + "/v2/tokens?" + urllib.parse.urlencode({"token_id": tok})
    doc, st = get(url, "v4_tokens")
    dump("v4_tokens.json", doc)
    rows, nc, hm = page(doc)
    out["tokens"] = {"url": url, "http": st, "rows": len(rows),
                     "row_keys": sorted(rows[0].keys()) if rows else []}
    dump("v4_summary.json", out)
    ck_set("v4", "OK")
    print("V4:", json.dumps(out, ensure_ascii=False)[:400], flush=True)


# ---------------------------------------------------------------- Việc 5
def viec5():
    """Cùng 1 mã đã chốt trên Gamma + resolutions + positions."""
    out = []
    for label, cond in (("spain", V1_CODES["spain_resolved"]),
                        ("ghana", V1_CODES["ghana_neg_risk"])):
        url = DATA + "/v2/resolutions?" + urllib.parse.urlencode({"condition": cond})
        doc, st = get(url, "v5_res_%s" % label)
        rows, _, _ = page(doc)
        dump("v5_res_%s.json" % label, doc)
        out.append({"label": label, "condition": cond, "url": url, "http": st,
                    "resolutions_rows": [{
                        "status": r.get("status"), "payouts": r.get("payouts"),
                        "resolved_at": r.get("resolved_at"),
                        "resolution_source": r.get("resolution_source"),
                        "reporter": r.get("reporter"),
                        "was_disputed": r.get("was_disputed")} for r in rows]})
        time.sleep(SLEEP)
    # positions của ví bb cho 2 mã đã chốt
    for label, cond in (("spain", V1_CODES["spain_resolved"]),
                        ("ghana", V1_CODES["ghana_neg_risk"])):
        url = DATA + "/v2/positions?" + urllib.parse.urlencode(
            {"user": WALLETS["bb"], "condition": cond, "limit": "10"})
        doc, st = get(url, "v5_pos_%s" % label)
        rows, _, _ = page(doc)
        dump("v5_pos_%s.json" % label, doc)
        out.append({"label": "pos_" + label, "condition": cond, "url": url, "http": st,
                    "position_rows": [{
                        "status": r.get("status"), "redeemable": r.get("redeemable"),
                        "realized_pnl": r.get("realized_pnl"),
                        "current_size": r.get("current_size"),
                        "outcome": r.get("outcome"),
                        "avg_price": r.get("avg_price")} for r in rows]})
        time.sleep(SLEEP)
    dump("v5_summary.json", out)
    ck_set("v5", "OK")
    for r in out:
        print("V5", r["label"], r["http"], str(r.get("resolutions_rows") or r.get("position_rows"))[:140], flush=True)


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    print("=== PROBE V2 (%s) — %s ===" % (what, utcnow()), flush=True)
    try:
        if what in ("v1", "all"):
            viec1()
        if what in ("v2", "all"):
            viec2()
        if what in ("vj", "all"):
            viec2_joseph()
        if what in ("v3", "all"):
            viec3()
        if what in ("v4", "all"):
            viec4()
        if what in ("v5", "all"):
            viec5()
    except RuntimeError as e:
        state["stop"], state["reason"] = True, str(e)
        ck_set("ABORTED", str(e))
        print("!! DỪNG TOÀN BỘ:", e, flush=True)
        sys.exit(2)
    print("=== XONG (%s) ===" % what, flush=True)


if __name__ == "__main__":
    main()
