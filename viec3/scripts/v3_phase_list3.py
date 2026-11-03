# v3_phase_list3.py — SỬA LIỆT KÊ Việc 3 sau BUG FOUND (kiểm toán d8f2bb9), ngày 04/11/2026.
# LỖI CŨ đã sửa: "trang rỗng ở offset 2100" bị coi là kết thúc tự nhiên -> SAI. Luật MỚI:
#   KẾT THÚC TỰ NHIÊN = trang cuối ngắn <100 dòng ở offset <2100, HOẶC trang rỗng ở offset <2100.
#   TRANG RỖNG Ở offset >= 2100 = DẤU HIỆU CỤT -> phải chia nhỏ tiếp (đúng lời chủ nhân + kiểm toán).
# Cây bisection dựng lại từ cửa sổ gốc [2025-09-13, 2025-12-26] (tên lát giống hệt run cũ để ăn cache),
# mỗi lát ghi cha-con vào slices_tree.json. Khi lát 1 NGÀY cụt -> chia theo GIỜ trong ngày
# (end_date_min/max dạng datetime, phải xác minh bằng 1 request — nếu API không nhận datetime thì
#  dừng sạch và ghi DATETIME_NOT_SUPPORTED để báo chủ nhân, không tự đổi kỹ thuật).
# Trần: 200 request/ngày dương lịch Asia/Saigon, cộng dồn mọi tiến trình (đếm trong viec3_lib).
# Khóa tiến trình: viec3/data/viec3.lock — không chạy trùng 2 tiến trình.
import sys, os, json, gzip
from collections import deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import (Http, StopRun, GAMMA_API, T0, T1, jdump,
                       acquire_lock, release_lock, saigon_date)

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
MAX_REQ = int(sys.argv[2]) if len(sys.argv) > 2 else 200
SPEC_HASH = "ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8"
WIN_MIN, WIN_MAX = "2025-09-13", "2025-12-26"
LD = os.path.join(DATA, "listing")
SL = os.path.join(LD, "slices3")     # cây MỚI, tham chiếu cache từ slices/ cũ
OLD_SL = os.path.join(LD, "slices")
LOCK = os.path.join(DATA, "viec3.lock")

# ---- khóa tiến trình ----
import hashlib
spec_now = hashlib.sha256(open(os.path.join(os.path.dirname(os.path.dirname(DATA)), "docs",
                                            "polymarket-copytrade-20-SPEC-V2-FROZEN.md"), "rb").read()).hexdigest() \
    if os.path.exists(os.path.join("docs", "polymarket-copytrade-20-SPEC-V2-FROZEN.md")) else None
lock_rec, lock_old = acquire_lock(LOCK, "v3_phase_list3 max_req=%d" % MAX_REQ)
if lock_rec is None:
    print("TỪ CHỐI CHẠY: khóa đang giữ bởi tiến trình sống pid=%s (%s)" % (lock_old.get("pid"), lock_old.get("cmd")))
    sys.exit(3)

# ---- hash spec trước khi sửa ----
if spec_now != SPEC_HASH:
    print("DỪNG: hash spec khác luật (%s)" % spec_now)
    release_lock(LOCK)
    sys.exit(2)
print("Hash spec khớp luật:", spec_now[:16], "…")

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

# ---- trạng thái phân loại (nạp từ slim cũ + flat pages, như list2) ----
slim_path = os.path.join(LD, "listing_slim.jsonl")
BUCKETS = ["valid", "seasonal", "missing_gst", "fallback", "anomaly"]
seen = {}
for b in BUCKETS:
    p = slim_path + "." + b
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            try:
                r = json.loads(l)
                seen[r["id"]] = (r.get("bucket") or b)
            except Exception:
                pass
extra = {"tag_conflict_sports_politics": 0, "gst_truoc_D1": 0, "gst_sau_D1": 0,
         "non_sports": 0, "tag_rong_fallback_gst_in_D1": 0, "rows_returned": 0, "pages": 0}

def classify(r):
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
        extra["tag_conflict_sports_politics"] += 1
    if not labels:
        rec["bucket"] = "fallback"
        if smt and gst is not None and T0 <= gst < T1:
            extra["tag_rong_fallback_gst_in_D1"] += 1
        return "fallback", rec
    if not has_sports:
        extra["non_sports"] += 1
        return ("anomaly" if smt else None), rec
    if not smt:
        return "seasonal", rec
    if gst is None:
        return "missing_gst", rec
    if T0 <= gst < T1:
        return "valid", rec
    extra["gst_truoc_D1" if gst < T0 else "gst_sau_D1"] += 1
    return None, rec

def process_rows(rows):
    from collections import Counter
    global counts
    for r in rows:
        if not isinstance(r, dict): continue
        mid = r.get("id")
        if mid in seen:
            continue
        b, rec = classify(r)
        seen[mid] = b or "non_sports_plain"
        if b in BUCKETS:
            rec["bucket"] = b
            with open(slim_path + "." + b, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        counts[seen[mid]] = counts.get(seen[mid], 0) + 1

counts = {}
# nạp flat pages ngày 1 (như list2)
import glob as _glob
for p in sorted(_glob.glob(os.path.join(LD, "page_*.json.gz"))):
    with gzip.open(p, "rt", encoding="utf-8") as f:
        process_rows(json.load(f))

h = Http(DATA, phase="list3", max_req=MAX_REQ)

def slice_dir(a, b):
    d = os.path.join(SL, "%s_%s" % (a, b))
    os.makedirs(d, exist_ok=True)
    return d

def old_cache(a, b, offset):
    """Trang cũ của run trước (slices/ hoặc slices3/) nếu có."""
    for base in (SL, OLD_SL):
        p = os.path.join(base, "%s_%s" % (a, b), "page_%07d.json.gz" % offset)
        if os.path.exists(p):
            return p
    return None

def page_path(d, offset):
    return os.path.join(d, "page_%07d.json.gz" % offset)

def fetch_page(a, b, offset):
    """Trả (rows, from_cache). Dùng cache cũ nếu có; nếu không, request."""
    c = old_cache(a, b, offset)
    if c:
        with gzip.open(c, "rt", encoding="utf-8") as f:
            return json.load(f), True
    q = {"closed": "true", "include_tag": "true",
         "end_date_min": a, "end_date_max": b,
         "order": "id", "ascending": "true", "limit": "100", "offset": str(offset)}
    doc, st = h.get(GAMMA_API + "/markets?" + urllib.parse.urlencode(q),
                    "l3_%s_%s_off%d" % (a[:10], b[:10], offset))
    rows = doc if isinstance(doc, list) else []
    d = slice_dir(a, b)
    with gzip.open(page_path(d, offset) + ".tmp", "wt", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    os.replace(page_path(d, offset) + ".tmp", page_path(d, offset))
    return rows, False

def slice_status(a, b):
    """Đánh giá lát theo LUẬT MỚI từ đĩa: NATURAL / CAP / PARTIAL (chưa đi hết chuỗi).
    Lát probe-only (chỉ page_2000 = 100 dòng, không page_0): CAP ngay theo bằng chứng probe
    (>=2.100 dòng thật) — không đi lại 20 trang giữa (giữ tối ưu dò-trước của run cũ)."""
    import glob as _g
    offs = {}
    for p in (_g.glob(os.path.join(SL, "%s_%s" % (a, b), "page_*.json.gz")) +
              _g.glob(os.path.join(OLD_SL, "%s_%s" % (a, b), "page_*.json.gz"))):
        off = int(os.path.basename(p)[5:12])
        if off not in offs:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                offs[off] = len(json.load(f))
    if 0 not in offs:
        if offs.get(2000) == 100:
            return ("CAP", 2000), offs          # bằng chứng probe cũ: >=2.100 dòng -> CỤT
        return ("PARTIAL", 0), offs
    o = 0
    while True:
        if o not in offs:
            return ("PARTIAL", o), offs
        n = offs[o]
        if n == 0:
            return ("NATURAL" if o < 2100 else "CAP", o), offs   # *** LUẬT MỚI: rỗng ở >=2100 là CỤT ***
        if n < 100:
            return ("NATURAL" if o < 2100 else "CAP", o), offs
        o += 100
        if o > 2100:
            return ("CAP", o), offs

def d2ord(s):
    import datetime
    return datetime.date.fromisoformat(s[:10]).toordinal()

def children_of(a, b):
    """Lát con: nhiều ngày => chia đôi theo ngày; 1 NGÀY => chia theo GIỜ
    (định dạng 'YYYY-MM-DDTHH'; API phải nhận datetime trong end_date_min/max —
    sẽ xác minh bằng 1 request ở lát giờ đầu tiên)."""
    import datetime
    if len(a) == 10 and len(b) == 10:
        o0, o1 = d2ord(a), d2ord(b)
        if o1 - o0 >= 1:
            mid = datetime.date.fromordinal(o0 + (o1 - o0) // 2).isoformat()
            return [(a, mid), (datetime.date.fromordinal(d2ord(mid) + 1).isoformat(), b)]
        # đúng 1 ngày -> hai nửa ngày theo giờ
        return [(a + "T00", a + "T12"), (a + "T12", b + "T23")]
    f = "%Y-%m-%dT%H"
    ta = datetime.datetime.strptime(a, f)
    tb = datetime.datetime.strptime(b, f)
    if (tb - ta) <= datetime.timedelta(hours=1):
        return None  # mức nhỏ nhất 1 giờ — nếu vẫn cụt: UNRESOLVED (báo chủ nhân)
    tm = ta + (tb - ta) // 2
    return [(a, tm.strftime(f)), (tm.strftime(f), b)]

tree = []
queue = deque([(WIN_MIN, WIN_MAX, None)])
unresolved = []
print("Bắt đầu sửa liệt kê — cây từ gốc %s→%s, đã thấy %d id" % (WIN_MIN, WIN_MAX, len(seen)), flush=True)
datetime_verified = {"ok": None}  # None=chưa cần, True/False sau request xác minh đầu tiên

try:
    while queue:
        a, b, parent = queue.popleft()
        (st, off), offs = slice_status(a, b)
        if st == "PARTIAL":
            # đi tiếp chuỗi từ offset đang có (cache-aware)
            o = 0
            while True:
                rows, cached = fetch_page(a, b, o)
                extra["pages"] += 1
                extra["rows_returned"] += len(rows)
                process_rows(rows)
                h.checkpoint(step="list3", slice=[a, b], offset=o + len(rows), seen=len(seen),
                             valid=counts.get("valid", 0), req_phase=h.count_phase)
                if len(rows) == 0:
                    st = "NATURAL" if o < 2100 else "CAP"
                    break
                if len(rows) < 100:
                    st = "NATURAL" if o < 2100 else "CAP"
                    break
                o += 100
                if o > 2100:
                    st = "CAP"
                    break
        if st == "NATURAL":
            tree.append({"slice": [a, b], "parent": parent, "status": "NATURAL"})
            print("LÁT %s→%s: NATURAL | seen=%d valid=%d | req pha=%d (ngày %s: %d)" %
                  (a, b, len(seen), counts.get("valid", 0), h.count_phase,
                   saigon_date(), h.count_today + h.count_phase), flush=True)
            continue
        # CAP -> chia con
        ch = children_of(a, b)
        if ch is None:
            unresolved.append([a, b])
            tree.append({"slice": [a, b], "parent": parent, "status": "UNRESOLVED_1HOUR"})
            print("LÁT %s→%s: CỤT tới mức 1 GIỜ vẫn cụt — UNRESOLVED", a, b, flush=True)
            continue
        # nếu con là lát GIỜ: xác minh API nhận datetime (1 request, 1 lần)
        if len(ch[0][0]) > 10 and datetime_verified["ok"] is None:
            rows, cached = fetch_page(ch[0][0], ch[0][1], 0)
            if cached:
                datetime_verified["ok"] = True
            else:
                datetime_verified["ok"] = len(rows) >= 0  # HTTP 200 => nhận datetime; 4xx đã ghi ledger
                if h.count_phase and rows == [] and not cached:
                    # phân biệt 200-rỗng hợp lệ với lỗi: đọc ledger dòng cuối
                    last = [json.loads(l) for l in open(h.ledger_path, encoding="utf-8")][-1]
                    if last.get("status") in (400, 422):
                        datetime_verified["ok"] = False
            if datetime_verified["ok"] is False:
                print("DATETIME_NOT_SUPPORTED: end_date_min/max không nhận giờ — DỪNG SẠCH, báo chủ nhân", flush=True)
                jdump(os.path.join(LD, "slices3_status.json"),
                      {"stopped": "DATETIME_NOT_SUPPORTED", "queue": list(queue) + [[a, b, parent]],
                       "tree": tree, "unresolved": unresolved})
                release_lock(LOCK)
                sys.exit(4)
        tree.append({"slice": [a, b], "parent": parent, "status": "CAP_split"})
        for ca, cb in ch:
            queue.append((ca, cb, [a, b]))
        jdump(os.path.join(LD, "slices3_progress.json"),
              {"queue": list(queue), "tree": tree, "unresolved": unresolved})
except StopRun as e:
    jdump(os.path.join(LD, "slices3_progress.json"),
          {"queue": list(queue), "tree": tree, "unresolved": unresolved, "stopped": str(e)})
    print("DỪNG THEO LUẬT: %s — tiến độ lưu, chạy lại để tiếp tục (cache giữ nguyên)" % e, flush=True)
    release_lock(LOCK)
    sys.exit(0)

n_nat = sum(1 for t in tree if t["status"] == "NATURAL")
final = {"window": [WIN_MIN, WIN_MAX], "complete": len(queue) == 0 and not unresolved and all(t["status"] == "NATURAL" for t in tree),
         "total_slices": len(tree), "natural": n_nat, "unresolved": unresolved,
         "requests_phase": h.count_phase, "requests_day": h.count_today + h.count_phase,
         "day_saigon": saigon_date(), "tree": tree,
         "note": "LUẬT MỚI: rỗng ở offset>=2100 = CỤT (lỗi cũ đã sửa); tự nhiên = ngắn <100 hoặc rỗng ở <2100"}
jdump(os.path.join(LD, "slices3_status.json"), final)
h.checkpoint(step="list3_DONE" if final["complete"] else "list3_PAUSED", **{"final": {k: v for k, v in final.items() if k != "tree"}})
print("KẾT THÚC: complete=%s | lát=%d (natural=%d) | req pha=%d | ngày %s đã dùng %d" %
      (final["complete"], len(tree), n_nat, h.count_phase, saigon_date(), h.count_today + h.count_phase))
release_lock(LOCK)
