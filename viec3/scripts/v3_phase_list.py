# v3_phase_list.py — PHA LIỆT KÊ Việc 3: phân trang Gamma /markets trong cửa sổ end_date,
# lọc client-side theo luật spec v2 đóng băng §2.1 (tag 'Sports' + sportsMarketType +
# gameStartTime ∈ [T0,T1)), đếm TỪNG BƯỚC, ghi checkpoint sau mỗi trang.
# Kỹ thuật liệt kê (báo cáo theo §5.3): closed=true&include_tag=true&end_date_min/max ISO
# (2025-09-13 → 2025-12-26, đệm +14 ngày cho chốt trễ) + order=id asc + limit=100 + offset.
# KHÔNG dùng volumeNum cho bất kỳ quyết định nào (chỉ lưu lại mô tả).
import sys, os, json, gzip, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, GAMMA_API, T0, T1, jdump, jlappend

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
MAX_REQ = int(sys.argv[2]) if len(sys.argv) > 2 else 120
END_MIN, END_MAX = "2025-09-13", "2025-12-26"   # T0 → T1+14 ngày
LD = os.path.join(DATA, "listing")

def parse_epoch(v):
    if v in (None, ""): return None
    if isinstance(v, (int, float)): return int(v)
    s = str(v).strip()
    if s.isdigit(): return int(s)
    try:
        import datetime
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
        return int(d.timestamp())  # làm tròn XUỐNG tới giây (luật quy đổi)
    except Exception:
        return None

h = Http(DATA, phase="list", max_req=MAX_REQ)

def page_url(offset):
    q = {"closed": "true", "include_tag": "true",
         "end_date_min": END_MIN, "end_date_max": END_MAX,
         "order": "id", "ascending": "true", "limit": "100", "offset": str(offset)}
    return GAMMA_API + "/markets?" + urllib.parse.urlencode(q)

slim_path = os.path.join(LD, "listing_slim.jsonl")
counts = {"pages": 0, "rows_returned": 0, "unique_ids": 0, "dup_rows": 0,
          "sports_tag": 0, "non_sports": 0, "tag_conflict_sports_politics": 0,
          "seasonal_smt_empty": 0, "smt_set_gst_missing": 0,
          "valid_D1": 0, "gst_before_D1": 0, "gst_after_D1": 0,
          "empty_tags_fallback_suspect": 0, "empty_tags_fallback_gst_in_D1": 0,
          "anomaly_smt_set_no_sports_tag": 0, "non_null_tags_but_no_sports_smt_empty": 0}
seen = {}
offset = 0
max_pages = 400

# resume: bỏ qua trang đã có file
def page_path(off):
    return os.path.join(LD, "page_%07d.json.gz" % off)

while counts["pages"] < max_pages:
    if os.path.exists(page_path(offset)):
        # đã lấy trong lần chạy trước — nạp lại để phân loại tiếp
        with gzip.open(page_path(offset), "rt", encoding="utf-8") as f:
            rows = json.load(f)
        from_server = False
    else:
        url = page_url(offset)
        doc, st = h.get(url, "list_p%d_off%d" % (counts["pages"] + 1, offset))
        rows = doc if isinstance(doc, list) else []
        with gzip.open(page_path(offset) + ".tmp", "wt", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
        os.replace(page_path(offset) + ".tmp", page_path(offset))
        from_server = True
    if not isinstance(rows, list) or not rows:
        counts["pages"] += 1
        print("TRANG TRỐNG/LỖI tại offset %d — coi như hết (rows=%s)" % (offset, len(rows) if isinstance(rows, list) else rows))
        break
    counts["pages"] += 1
    counts["rows_returned"] += len(rows)
    for r in rows:
        mid = r.get("id")
        if mid in seen:
            counts["dup_rows"] += 1
            continue
        seen[mid] = True
        counts["unique_ids"] += 1
        tags = r.get("tags") or []
        labels = [t.get("label") for t in tags if isinstance(t, dict)]
        has_sports = "Sports" in labels
        smt = r.get("sportsMarketType") or ""
        gst = parse_epoch(r.get("gameStartTime"))
        rec = {"id": mid, "conditionId": r.get("conditionId"), "question": r.get("question"),
               "slug": r.get("slug"), "sportsMarketType": smt,
               "gameStartTime": r.get("gameStartTime"), "gameStartTime_epoch": gst,
               "startDate": r.get("startDate"), "endDate": r.get("endDate"),
               "closedTime": r.get("closedTime"),
               "tag_labels": labels,
               "volumeNum_chi_mo_ta_khong_dung_loc": r.get("volumeNum")}
        if has_sports and "Politics" in labels:
            counts["tag_conflict_sports_politics"] += 1
        if not labels:
            # tags rỗng sau include_tag=true — đường dự phòng v1: smt+gst đều có => nghi thể thao trận đơn
            counts["empty_tags_fallback_suspect"] += 1
            if smt and gst is not None and T0 <= gst < T1:
                counts["empty_tags_fallback_gst_in_D1"] += 1
            rec["bucket"] = "empty_tags_fallback"
            jlappend(slim_path + ".fallback", rec)
            continue
        if not has_sports:
            counts["non_sports"] += 1
            if smt:
                counts["anomaly_smt_set_no_sports_tag"] += 1
                rec["bucket"] = "anomaly_smt_no_sportstag"
                jlappend(slim_path + ".anomaly", rec)
            continue
        counts["sports_tag"] += 1
        if not smt:
            counts["seasonal_smt_empty"] += 1
            rec["bucket"] = "seasonal"
            jlappend(slim_path + ".seasonal", rec)
            continue
        if gst is None:
            counts["smt_set_gst_missing"] += 1
            rec["bucket"] = "smt_gst_missing"
            jlappend(slim_path + ".missing_gst", rec)
            continue
        if T0 <= gst < T1:
            counts["valid_D1"] += 1
            rec["bucket"] = "valid_D1"
            jlappend(slim_path + ".valid", rec)
        elif gst < T0:
            counts["gst_before_D1"] += 1
        else:
            counts["gst_after_D1"] += 1
    h.checkpoint(step="listing", next_offset=offset + len(rows),
                 counts=counts, last_page_rows=len(rows), from_server=from_server)
    print("trang %d off=%d rows=%d | unique=%d valid_D1=%d | requests pha=%d (hôm nay %d)" %
          (counts["pages"], offset, len(rows), counts["unique_ids"], counts["valid_D1"],
           h.count_phase, h.count_today + h.count_phase), flush=True)
    if len(rows) < 100:
        print("TRANG CUỐI (rows=%d < 100) — LIỆT KÊ XONG" % len(rows))
        break
    offset += len(rows)

counts["window"] = {"end_date_min": END_MIN, "end_date_max": END_MAX,
                    "T0": T0, "T1": T1,
                    "total_pages": counts["pages"],
                    "note": "volumeNum chỉ mô tả; ngưỡng 10k đo từ trade đoạn 1"}
jdump(os.path.join(LD, "counts.json"), counts)
h.checkpoint(step="listing_DONE", counts=counts)
print("COUNTS:", json.dumps(counts, ensure_ascii=False, indent=1))
