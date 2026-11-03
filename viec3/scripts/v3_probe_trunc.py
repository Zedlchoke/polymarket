# v3_probe_trunc.py — 2 request chẩn đoán cụt: (1) order=id DESC cùng cửa sổ;
# (2) slice tháng 11 order asc. Xem createdAt/id để quyết định chiến lắc chia nhỏ.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, GAMMA_API

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
h = Http(DATA, phase="trunc_probe", max_req=2)

def gamma(tag, extra):
    q = {"closed": "true", "include_tag": "true", "end_date_min": "2025-09-13",
         "end_date_max": "2025-12-26", "limit": "100", "offset": "0"}
    q.update(extra)
    cached = os.path.join(DATA, "smoke", tag + ".json")
    if os.path.exists(cached):
        rows = json.load(open(cached, encoding="utf-8"))
        rows = rows if isinstance(rows, list) else []
        print("%s (CACHED) rows=%d" % (tag, len(rows)))
    else:
        u = GAMMA_API + "/markets?" + urllib.parse.urlencode(q)
        doc, st = h.get(u, tag, save_path=cached)
        rows = doc if isinstance(doc, list) else []
        print("%s http=%s rows=%d" % (tag, st, len(rows)))
    if rows:
        cr = [str(r.get("createdAt"))[:7] for r in rows]
        ids = [int(r.get("id")) for r in rows if r.get("id") is not None]
        en = [str(r.get("endDate"))[:10] for r in rows]
        print("   createdAt các tháng:", dict(sorted(__import__("collections").Counter(cr).items())))
        print("   id: %s..%s | endDate: %s..%s" % (min(ids), max(ids), min(en), max(en)))
        sp = sum(1 for r in rows if any(t.get("label") == "Sports" for t in (r.get("tags") or [])))
        gst = sum(1 for r in rows if r.get("gameStartTime"))
        print("   Sports=%d gst-nonnull=%d" % (sp, gst))
    return rows

# 1) DESC từ đầu mới
gamma("trunc_desc", {"order": "id", "ascending": "false"})
# 2) slice tháng 11 (narrow) order asc
gamma("trunc_nov", {"order": "id", "ascending": "true",
                    "end_date_min": "2025-11-01", "end_date_max": "2025-11-30"})
print("requests:", h.count_phase, "| today:", h.count_today + h.count_phase)
