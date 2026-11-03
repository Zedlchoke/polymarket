# v3_recount.py — ĐẾM LẠI TỪNG BƯỚC LỌC trên đĩa (offline, không API) theo đúng luật spec v2
# đóng băng: tag 'Sports' + sportsMarketType != rỗng + T0 <= gameStartTime < T1.
# Ghi rõ: số đếm là ĐẦY ĐỦ hay CẬN DƯỚI (đối chiếu coverage_fixed.json: complete true/false).
import sys, os, json, gzip, glob, datetime
from collections import Counter

T0, T1 = 1757721600, 1765497600
LD = os.path.join("viec3", "data", "listing")

def parse_epoch(v):
    if v in (None, ""): return None
    if isinstance(v, (int, float)): return int(v)
    s = str(v).strip()
    if s.isdigit(): return int(s)
    try:
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
        return int(d.timestamp())
    except Exception:
        return None

ids, rows_total = {}, 0
for p in (glob.glob(os.path.join(LD, "slices3", "*", "page_*.json.gz")) +
          glob.glob(os.path.join(LD, "slices", "*", "page_*.json.gz")) +
          glob.glob(os.path.join(LD, "page_*.json.gz"))):
    with gzip.open(p, "rt", encoding="utf-8") as f:
        rows = json.load(f)
        rows_total += len(rows)
        for r in rows:
            ids[r.get("id")] = r

cnt = Counter()
valid = []
for r in ids.values():
    labels = [t.get("label") for t in (r.get("tags") or []) if isinstance(t, dict)]
    smt = r.get("sportsMarketType") or ""
    g = parse_epoch(r.get("gameStartTime"))
    if not labels: cnt["tag_rong"] += 1
    elif "Sports" not in labels: cnt["phi_theo_thao" + ("_anomaly_co_smt" if smt else "")] += 1
    elif not smt: cnt["mua_vu"] += 1
    elif g is None: cnt["thieu_gst"] += 1
    elif T0 <= g < T1:
        cnt["HOP_LE"] += 1
        valid.append({"id": r.get("id"), "conditionId": r.get("conditionId"),
                      "question": r.get("question"), "slug": r.get("slug"),
                      "sportsMarketType": smt, "gameStartTime": r.get("gameStartTime"),
                      "gameStartTime_epoch": g, "endDate": r.get("endDate"),
                      "volumeNum_chi_mo_ta_khong_dung_loc": r.get("volumeNum")})
    else: cnt["gst_truoc_D1" if g < T0 else "gst_sau_D1"] += 1

valid.sort(key=lambda x: x["conditionId"] or "")
with open(os.path.join(LD, "listing_slim.jsonl.valid_FULL"), "w", encoding="utf-8") as f:
    for v in valid:
        f.write(json.dumps(v, ensure_ascii=False) + "\n")

cov = {}
cf = os.path.join(LD, "coverage_fixed.json")
if os.path.exists(cf):
    cov = json.load(open(cf))
mon = Counter(datetime.datetime.fromtimestamp(v["gameStartTime_epoch"], datetime.timezone.utc).strftime("%Y-%m")
              for v in valid)
out = {"complete": cov.get("complete", None),
       "rows_total_pages": rows_total, "unique_ids": len(ids), "counts": dict(cnt),
       "valid_theo_thang": dict(sorted(mon.items())), "n_valid": len(valid),
       "ghi_chu": ("SỐ ĐẦY ĐỦ (mọi lát kết thúc tự nhiên, hàng đợi rỗng)" if cov.get("complete")
                   else "VẪN LÀ CẬN DƯỚI — còn cửa sổ chưa kết thúc tự nhiên: %d (xem coverage_fixed.json)" %
                        len(cov.get("pending_windows", [])))}
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(os.path.join("viec3", "data", "recount.json"), "w"), ensure_ascii=False, indent=1)
