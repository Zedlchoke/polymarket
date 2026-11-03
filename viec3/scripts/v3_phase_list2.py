# v3_phase_list2.py — LIỆT KÊ (bản 2, chống cụt): Gamma /markets closed=true&include_tag=true
# + cửa sổ end_date [min,max], order=id asc, limit=100. Phát hiện cụt: 21 trang đầy + trang
# offset 2100 rỗng => GIỚI HẠN ~2.100 dòng/query (đã đo) => CHIA ĐÔI cửa sổ end_date (bisection)
# tới khi mỗi lát phân trang kết thúc tự nhiên (trang ngắn <100 hoặc trang rỗng ở offset <2100).
# Lát 1 ngày vẫn cụt => ghi UNRESOLVED (báo cáo trung thực).
# Dedupe toàn cục theo id; phân loại giữ nguyên luật run 1; mọi trang lưu đĩa; checkpoint liên tục.
import sys, os, json, gzip, shutil
from collections import Counter, deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, StopRun, GAMMA_API, T0, T1, jdump

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
MAX_REQ = int(sys.argv[2]) if len(sys.argv) > 2 else 150
WIN_MIN, WIN_MAX = "2025-09-13", "2025-12-26"   # T0 … T1+14 ngày (đệm chốt trễ)
CAP_ROWS = 2100                                   # 21 trang x 100 — ngưỡng nghi cụt (đo được)
LD = os.path.join(DATA, "listing")
SL = os.path.join(LD, "slices")
os.makedirs(SL, exist_ok=True)

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

def d2i(s):
    import datetime
    return datetime.date.fromisoformat(s).toordinal()

def i2d(o):
    import datetime
    return datetime.date.fromordinal(o).isoformat()

# ---- trạng thái: nạp lại phân loại từ các file slim của run trước (id duy nhất) ----
slim_path = os.path.join(LD, "listing_slim.jsonl")
BUCKETS = ["valid", "seasonal", "missing_gst", "fallback", "anomaly"]
seen = {}   # id -> bucket
for b in BUCKETS:
    p = slim_path + "." + b
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            try:
                r = json.loads(l)
                bk = r.get("bucket") or b
                if bk == "valid_D1":
                    bk = "valid"
                seen[r["id"]] = bk
            except Exception:
                pass
counts = Counter(seen.values())
extra_counts = {"pages": 0, "rows_returned": 0, "dup_rows": 0,
                "gst_before_D1": 0, "gst_after_D1": 0, "non_sports": 0,
                "tag_conflict_sports_politics": 0,
                "empty_tags_fallback_gst_in_D1": 0}
# đếm phụ theo bucket ghi sẵn (run trước không lưu hết các nhánh này vào slim) — tính lại từ pages sau

h = Http(DATA, phase="list2", max_req=MAX_REQ)


def classify(r):
    """Trả (bucket, rec) theo luật §2.1; không đổi luật run 1."""
    mid = r.get("id")
    tags = r.get("tags") or []
    labels = [t.get("label") for t in tags if isinstance(t, dict)]
    has_sports = "Sports" in labels
    smt = r.get("sportsMarketType") or ""
    gst = parse_epoch(r.get("gameStartTime"))
    rec = {"id": mid, "conditionId": r.get("conditionId"), "question": r.get("question"),
           "slug": r.get("slug"), "sportsMarketType": smt,
           "gameStartTime": r.get("gameStartTime"), "gameStartTime_epoch": gst,
           "startDate": r.get("startDate"), "endDate": r.get("endDate"),
           "closedTime": r.get("closedTime"), "tag_labels": labels,
           "volumeNum_chi_mo_ta_khong_dung_loc": r.get("volumeNum"), "bucket": None}
    if has_sports and "Politics" in labels:
        extra_counts["tag_conflict_sports_politics"] += 1
    if not labels:
        rec["bucket"] = "fallback"
        if smt and gst is not None and T0 <= gst < T1:
            extra_counts["empty_tags_fallback_gst_in_D1"] += 1
        return "fallback", rec
    if not has_sports:
        extra_counts["non_sports"] += 1
        if smt:
            return "anomaly", rec
        return None, rec   # phi thể thao thường — không ghi slim
    if not smt:
        return "seasonal", rec
    if gst is None:
        return "missing_gst", rec
    if T0 <= gst < T1:
        return "valid", rec
    extra_counts["gst_before_D1" if gst < T0 else "gst_after_D1"] += 1
    return "side", rec  # sports, smt, gst có nhưng ngoài đoạn 1 — không vào pool, không ghi slim

def process_rows(rows):
    for r in rows:
        if not isinstance(r, dict): continue
        mid = r.get("id")
        if mid in seen:
            extra_counts["dup_rows"] += 1
            continue
        b, rec = classify(r)
        seen[mid] = b or ("non_sports_plain" if rec else "skip")
        if b in BUCKETS:
            rec["bucket"] = b
            with open(slim_path + "." + b, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        counts[b or seen[mid]] += 1

# ---- nạp lại 22 trang run 1 (bổ sung id chưa ghi slim: phi thể thao thường, gst ngoài đoạn 1) ----
for p in [os.path.join(LD, f) for f in sorted(os.listdir(LD))
          if f.startswith("page_") and f.endswith(".json.gz")]:
    with gzip.open(p, "rt", encoding="utf-8") as f:
        process_rows(json.load(f))
print("Sau khi nạp run 1: seen=%d | buckets=%s | extra=%s" %
      (len(seen), dict(counts), extra_counts), flush=True)

# ---- nhập 22 trang run 1 làm lát cửa-sổ-đủ (chỉ để có sẵn dedupe; sẽ bị chia đôi lại) ----
flat = sorted(glob := [f for f in os.listdir(LD) if f.startswith("page_") and f.endswith(".json.gz")])
full_dir = os.path.join(SL, WIN_MIN + "_" + WIN_MAX)
os.makedirs(full_dir, exist_ok=True)
for fn in flat:
    dst = os.path.join(full_dir, fn)
    if not os.path.exists(dst):
        shutil.copy2(os.path.join(LD, fn), dst)

def slice_dir(dmin, dmax):
    d = os.path.join(SL, dmin + "_" + dmax)
    os.makedirs(d, exist_ok=True)
    return d

def page_path(d, offset):
    return os.path.join(d, "page_%07d.json.gz" % offset)

def fetch_slice(dmin, dmax):
    """Trả (status, n_pages): 'DONE' | 'CAP' | 'EMPTY'. Phân trang với cache + dedupe."""
    d = slice_dir(dmin, dmax)
    offset, full_pages = 0, 0
    while True:
        pp = page_path(d, offset)
        if os.path.exists(pp):
            with gzip.open(pp, "rt", encoding="utf-8") as f:
                rows = json.load(f)
        else:
            q = {"closed": "true", "include_tag": "true",
                 "end_date_min": dmin, "end_date_max": dmax,
                 "order": "id", "ascending": "true", "limit": "100", "offset": str(offset)}
            doc, st = h.get(GAMMA_API + "/markets?" + urllib.parse.urlencode(q),
                            "l2_%s_%s_off%d" % (dmin, dmax, offset))
            rows = doc if isinstance(doc, list) else []
            with gzip.open(pp + ".tmp", "wt", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False)
            os.replace(pp + ".tmp", pp)
        extra_counts["pages"] += 1
        extra_counts["rows_returned"] += len(rows)
        if not rows:
            return ("CAP" if offset >= CAP_ROWS else "DONE"), offset // 100
        process_rows(rows)
        h.checkpoint(step="list2", slice=[dmin, dmax], offset=offset + len(rows),
                     seen=len(seen), valid=counts.get("valid", 0), requests_phase=h.count_phase)
        if len(rows) < 100:
            return "DONE", offset // 100 + 1
        offset += len(rows)
        if offset >= CAP_ROWS + 100:
            return "CAP", offset // 100

queue = deque([(WIN_MIN, WIN_MAX)])
unresolved = []
slices_done = []
print("Bắt đầu bisection cửa sổ %s → %s | đã thấy %d id (valid=%d)" %
      (WIN_MIN, WIN_MAX, len(seen), counts.get("valid", 0)), flush=True)
while queue:
    try:
        dmin, dmax = queue.popleft()
        status, np_ = fetch_slice(dmin, dmax)
    except StopRun as e:
        jdump(os.path.join(LD, "slices_progress.json"),
              {"queue": list(queue) + ([[dmin, dmax]] if 'dmin' in dir() else []),
               "unresolved": unresolved, "slices_done": slices_done,
               "stopped": str(e)})
        print("DỪNG THEO LUẬT: %s — tiến độ đã lưu, chạy lại script để tiếp tục (cache trang giữ nguyên)" % e)
        sys.exit(0)
    slices_done.append({"slice": [dmin, dmax], "status": status, "pages": np_})
    print("LÁT %s→%s: %s (%d trang) | seen=%d valid=%d | req pha=%d (hôm nay %d)" %
          (dmin, dmax, status, np_, len(seen), counts.get("valid", 0),
           h.count_phase, h.count_today + h.count_phase), flush=True)
    if status == "CAP":
        o0, o1 = d2i(dmin), d2i(dmax)
        if o1 - o0 >= 1:
            mid = i2d(o0 + (o1 - o0) // 2)
            queue.append((dmin, mid))
            queue.append((i2d(d2i(mid) + 1), dmax) if d2i(mid) + 1 <= o1 else (mid, dmax))
        else:
            unresolved.append([dmin, dmax])
    jdump(os.path.join(LD, "slices_progress.json"),
          {"queue": list(queue), "unresolved": unresolved, "slices_done": slices_done})

final = {"window": [WIN_MIN, WIN_MAX], "T0": T0, "T1": T1,
         "cap_rows_per_query": CAP_ROWS,
         "unique_ids_seen": len(seen),
         "buckets": dict(counts), "extra": extra_counts,
         "slices": slices_done, "unresolved_1day_slices": unresolved,
         "note": "liệt kê bằng /markets + cửa sổ end_date chia lát chống cụt ~2.100 dòng/query; "
                 "xác minh gameStartTime client-side; volumeNum chỉ mô tả"}
jdump(os.path.join(LD, "counts2.json"), final)
h.checkpoint(step="list2_DONE" if not unresolved and not queue else "list2_PAUSED", **{"final": final})
print("FINAL:", json.dumps(final, ensure_ascii=False, indent=1)[:2000])
