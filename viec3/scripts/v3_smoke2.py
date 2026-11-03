# v3_smoke2.py — nhóm 2: định dạng ngày ISO cho start_date_min/max; order; limit clamp; sports_market_types.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, GAMMA_API, T0, T1

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
h = Http(DATA, phase="smoke2", max_req=6)

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

def tf(ep):
    import datetime
    return datetime.datetime.fromtimestamp(ep, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")

def gamma(tag, extra):
    q = {"closed": "true", "include_tag": "true", "limit": "100", "offset": "0"}
    q.update(extra)
    u = GAMMA_API + "/markets?" + urllib.parse.urlencode(q)
    doc, st = h.get(u, tag, save_path=os.path.join(DATA, "smoke", tag + ".json"))
    if not isinstance(doc, list):
        print("%s http=%s NOT-LIST %s" % (tag, st, str(doc)[:150])); return None
    print("%s http=%s rows=%d" % (tag, st, len(doc)))
    return doc

def stats(rs, name):
    if not rs: return
    ed = [parse_epoch(r.get("endDate")) for r in rs]
    ed_nn = sorted(x for x in ed if x is not None)
    sd = [x for x in (parse_epoch(r.get("startDate")) for r in rs) if x is not None]
    gs_in = [x for x in (parse_epoch(r.get("gameStartTime")) for r in rs) if x is not None and T0 <= x < T1]
    sport = [r for r in rs if any(t.get("label") == "Sports" for t in (r.get("tags") or []))]
    print("  %s: endDate nn=%d [%s..%s] | startDate nn=%d | gst-in-D1=%d | Sports=%d" %
          (name, len(ed_nn), tf(ed_nn[0]) if ed_nn else "-", tf(ed_nn[-1]) if ed_nn else "-",
           len(sd), len(gs_in), len(sport)))

# D: ngày ISO cho start_date
rowsD = gamma("smokeD_iso_startdate", {"start_date_min": "2025-07-14", "start_date_max": "2025-12-12"})
stats(rowsD, "D")
# E: D + order id asc
rowsE = gamma("smokeE_order", {"start_date_min": "2025-07-14", "start_date_max": "2025-12-12",
                               "order": "id", "ascending": "true"})
stats(rowsE, "E")
# F: limit clamp — không include_tag, limit 500
rowsF = gamma("smokeF_limit500", {"include_tag": "false", "limit": "500"})
if rowsF: print("  F rows=%d (clamp?)" % len(rowsF))
# G: end_date ISO (hẹp: chỉ đoạn 1 + 2 ngày)
rowsG = gamma("smokeG_enddate", {"end_date_min": "2025-09-13", "end_date_max": "2025-12-14"})
stats(rowsG, "G")
# H: sports_market_types (nếu được hỗ trợ trên /markets)
rowsH = gamma("smokeH_smt", {"end_date_min": "2025-09-13", "end_date_max": "2025-12-14",
                             "sports_market_types": "moneyline"})
stats(rowsH, "H")
print("requests used:", h.count_phase, "| today:", h.count_today + h.count_phase)
