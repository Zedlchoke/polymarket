# v3_smoke.py — thử tham số Gamma từng nhóm để tìm tổ hợp hoạt động (đếm vào ledger).
# Nhóm: A baseline (closed+include_tag+limit) / B=A+start_date_min,max / C=B+order,ascending
# Sau đó thử /v2/trades?market= nếu có ứng viên hợp lệ.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, GAMMA_API, DATA_API, T0, T1, LIST_START_MIN

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
h = Http(DATA, phase="smoke", max_req=8)

def parse_epoch(v):
    if v in (None, ""): return None
    if isinstance(v, (int, float)): return int(v)
    s = str(v).strip()
    if s.isdigit(): return int(s)
    try:
        import datetime
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
        return int(d.timestamp())
    except Exception:
        return None

def gamma(tag, extra):
    q = {"closed": "true", "include_tag": "true", "limit": "500", "offset": "0"}
    q.update(extra)
    u = GAMMA_API + "/markets?" + urllib.parse.urlencode(q)
    doc, st = h.get(u, tag, save_path=os.path.join(DATA, "smoke", tag + ".json"))
    rows = doc if isinstance(doc1 := doc, list) else (doc.get("data") if isinstance(doc, dict) else None)
    n = len(rows) if isinstance(rows, list) else -1
    print("%s http=%s rows=%s %s" % (tag, st, n, "" if isinstance(rows, list) else str(doc)[:200]))
    return rows

rowsA = gamma("smokeA_base", {})
rowsB = gamma("smokeB_dates", {"start_date_min": str(LIST_START_MIN), "start_date_max": str(T1)})
rowsC = gamma("smokeC_order", {"start_date_min": str(LIST_START_MIN), "start_date_max": str(T1),
                               "order": "id", "ascending": "true"})

rows = rowsC if isinstance(rowsC, list) and rowsC else (rowsB if isinstance(rowsB, list) and rowsB else rowsA)
if not isinstance(rows, list) or not rows:
    print("KHÔNG có trang nào đọc được — dừng smoke, xem file smoke/*.json")
    sys.exit(0)

def stats(rs, name):
    sds = [parse_epoch(r.get("startDate")) for r in rs]
    sds_nn = [x for x in sds if x is not None]
    inwin = [x for x in sds_nn if LIST_START_MIN <= x <= T1]
    gsts = [parse_epoch(r.get("gameStartTime")) for r in rs]
    g_in = [x for x in gsts if x is not None and T0 <= x < T1]
    sport = [r for r in rs if any(t.get("label") == "Sports" for t in (r.get("tags") or []))]
    print("%s: rows=%d startDate non-null=%d in-window=%d | gst in [T0,T1)=%d | Sports=%d" %
          (name, len(rs), len(sds_nn), len(inwin), len(g_in), len(sport)))
    if sds_nn:
        print("   startDate min=%s max=%s" % (time_fmt(min(sds_nn)), time_fmt(max(sds_nn))))

def time_fmt(ep):
    import datetime
    return datetime.datetime.fromtimestamp(ep, datetime.timezone.utc).strftime("%Y-%m-%d")

stats(rowsA or [], "A(base)")
if isinstance(rowsB, list) and rowsB: stats(rowsB, "B(dates)")
if isinstance(rowsC, list) and rowsC: stats(rowsC, "C(order)")

print("SMOKE fields:", sorted(rows[0].keys())[:50])
cand = None
for r in rows:
    if any(t.get("label") == "Sports" for t in (r.get("tags") or [])):
        g = parse_epoch(r.get("gameStartTime"))
        if g is not None and T0 <= g < T1 and r.get("sportsMarketType"):
            cand = r; break
if cand is None:
    print("Không có ứng viên hợp lệ trên trang này — bỏ smoke trades")
else:
    cid = cand["conditionId"]
    print("SMOKE-TRADES market: %s | %s" % (cid, cand.get("question")))
    q3 = {"market": cid, "taker_only": "false", "start": str(T0), "end": str(T1), "limit": "500"}
    u3 = DATA_API + "/v2/trades?" + urllib.parse.urlencode(q3)
    doc3, st3 = h.get(u3, "smoke_trades_market", save_path=os.path.join(DATA, "smoke", "smoke_trades.json"))
    d3 = doc3.get("data") if isinstance(doc3, dict) else doc3
    nc = doc3.get("next_cursor") if isinstance(doc3, dict) else None
    print("SMOKE-TRADES http=%s rows=%s next_cursor=%s" % (st3, len(d3) if isinstance(d3, list) else d3, (nc or "")[:50]))
    if isinstance(d3, list) and d3:
        print("row keys:", sorted(d3[0].keys()))
        print("row0:", json.dumps(d3[0], ensure_ascii=False)[:700])
        from collections import Counter
        keys = Counter((r.get("transactionHash"), r.get("tokenId"), r.get("timestamp"), r.get("side"), r.get("size")) for r in d3)
        print("dup fill-keys: %d/%d | wallets: %d" % (sum(1 for v in keys.values() if v > 1), len(keys), len(set(r.get("proxyWallet") for r in d3 if r.get("proxyWallet")))))
print("requests used:", h.count_phase, "| today total:", h.count_today + h.count_phase)
