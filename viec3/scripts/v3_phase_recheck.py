# v3_phase_recheck.py — PHA TRA LẠI THEO MÃ (luật: lặp condition_ids= từng mã + closed=any,
# dạng comma ĐÃ CHỨNG MINH KHÔNG hoạt động). Lấy mẫu thị trường hợp lệ, đối chiếu
# gameStartTime / sportsMarketType / tags với bản liệt kê; kèm 1 request closed=any
# cùng cửa sổ end_date để soi trường hợp closed=true có thể bỏ sót.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, GAMMA_API, T0, T1, jdump

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
SAMPLE_N = int(sys.argv[2]) if len(sys.argv) > 2 else 8
DAY_BOUNDARY = sys.argv[3] if len(sys.argv) > 3 else None
LD = os.path.join(DATA, "listing")
recs = [json.loads(l) for l in open(os.path.join(LD, "listing_slim.jsonl.valid_FULL"), encoding="utf-8")]
recs.sort(key=lambda r: r.get("conditionId") or "")
k = max(1, len(recs) // SAMPLE_N)
sample = [recs[i] for i in range(0, len(recs), k)][:SAMPLE_N]
h = Http(DATA, phase="recheck", max_req=3, day_boundary_ts=DAY_BOUNDARY)

# 1 request chứa lặp condition_ids cho cả mẫu (đã chứng minh hoạt động với 3 mã; thử 8)
q = [("closed", "any")]
for r in sample:
    q.append(("condition_ids", r["conditionId"]))
url = GAMMA_API + "/markets?" + urllib.parse.urlencode(q)
doc, st = h.get(url, "recheck_ids_batch", save_path=os.path.join(DATA, "recheck", "recheck_batch.json"))
rows = doc if isinstance(doc, list) else []
by_cid = {r.get("conditionId"): r for r in rows if isinstance(r, dict)}
print("recheck batch http=%s trả %d/%d mã" % (st, len(by_cid), len(sample)))

diffs = []
def pe(v):
    if v in (None, ""): return None
    s = str(v).strip()
    if s.isdigit(): return int(s)
    try:
        import datetime
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
        return int(d.timestamp())
    except Exception:
        return None

for r in sample:
    f = by_cid.get(r["conditionId"])
    if not f:
        diffs.append({"cid": r["conditionId"], "issue": "KHÔNG TRA RA trong batch recheck"}); continue
    g_new, g_old = pe(f.get("gameStartTime")), r.get("gameStartTime_epoch")
    smt_new, smt_old = f.get("sportsMarketType") or "", r.get("sportsMarketType")
    lab_new = sorted(t.get("label") for t in (f.get("tags") or []) if isinstance(t, dict))
    lab_old = sorted(r.get("tag_labels") or [])
    d = {"cid": r["conditionId"], "question": r.get("question")}
    if g_new != g_old: d["gameStartTime"] = {"listing": g_old, "recheck": g_new}
    if smt_new != smt_old: d["sportsMarketType"] = {"listing": smt_old, "recheck": smt_new}
    if "Sports" not in lab_new: d["tags_missing_Sports_recheck"] = lab_new
    if lab_new != lab_old: d["tags"] = {"listing": lab_old, "recheck": lab_new}
    if d != {"cid": r["conditionId"], "question": r.get("question")}:
        diffs.append(d)
print("Chênh lệch listing ↔ recheck: %d" % len(diffs))

# 1 request closed=any cùng cửa sổ để đếm tổng dòng trang đầu (so với closed=true trang đầu)
q2 = {"closed": "any", "include_tag": "true", "end_date_min": "2025-09-13", "end_date_max": "2025-12-26",
      "order": "id", "ascending": "true", "limit": "100", "offset": "0"}
u2 = GAMMA_API + "/markets?" + urllib.parse.urlencode(q2)
doc2, st2 = h.get(u2, "recheck_closedany_p1", save_path=os.path.join(DATA, "recheck", "closedany_p1.json"))
rows2 = doc2 if isinstance(doc2, list) else []
ids_any = set(r.get("id") for r in rows2 if isinstance(r, dict))
pg0 = os.path.join(LD, "page_0000000.json.gz")
ids_true = set()
if os.path.exists(pg0):
    import gzip
    with gzip.open(pg0, "rt", encoding="utf-8") as f2:
        ids_true = set(r.get("id") for r in json.load(f2) if isinstance(r, dict))
only_any = ids_any - ids_true
extra_note = "closed=any trả %d dòng trang 1; trang 1 closed=true có %d dòng; chỉ-có-trong-any: %d" % (
    len(ids_any), len(ids_true), len(only_any))
print(extra_note)
only_any_rows = [r for r in rows2 if isinstance(r, dict) and r.get("id") in only_any]

jdump(os.path.join(DATA, "recheck", "recheck_result.json"),
      {"sample_n": len(sample), "returned": len(by_cid), "diffs": diffs,
       "closed_any_page1_rows": len(rows2), "closed_true_page1_rows": len(ids_true),
       "only_in_closed_any": [{"id": r.get("id"), "q": r.get("question"), "closed": r.get("closed"),
                               "active": r.get("active"), "gst": r.get("gameStartTime"),
                               "smt": r.get("sportsMarketType")} for r in only_any_rows]})
h.checkpoint(step="recheck_DONE", diffs=len(diffs))
print("requests pha=%d (hôm nay %d)" % (h.count_phase, h.count_today + h.count_phase))
