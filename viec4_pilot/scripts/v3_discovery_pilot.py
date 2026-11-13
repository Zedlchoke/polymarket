# v3_discovery_pilot.py — PILOT KHÁM PHÁ cho spec v3 (lấy theo VÍ), lệnh chủ nhân "A" ngày 13/11.
# Mục tiêu đo BẰNG SỐ THẬT 3 đại lượng để viết spec v3 nháp:
#   (1) Lấy mẫu fill từ các thị trường LỚN (theo volumeNum mô tả) → bảng tần suất ví: mẫu có
#       bắt được "ví nghiêm túc" (xuất hiện ở nhiều thị trường) không, tốn bao nhiêu request.
#   (2) Với top ví xuất hiện nhiều nhất: fetch TOÀN BỘ lịch sử Đ1 theo VÍ (user=..., cursor
#       phân trang) → đo CHI PHÍ THẬT/ví (request, fill) — đây là con số quyết định v3.
#   (3) Ví whales đắt cỡ nào (trần an toàn 40 request/ví như probe; chạm trần = cận dưới).
# KHÔNG tính điểm, KHÔNG chọn ví giỏi, KHÔNG dùng dữ liệu tương lai cho lựa chọn nào
# (volumeNum chỉ dùng để CHỌN thị trường lấy mẫu — khai rõ; tần suất Đ1 là thông tin trong đoạn 1).
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "viec3", "scripts"))
from viec3_lib import Http, StopRun, DATA_API, T0, T1, acquire_lock, release_lock, jdump
import urllib.parse
from collections import Counter, defaultdict

DATA = "viec3/data"
OUT = "viec4_pilot/data/v3discovery"
os.makedirs(OUT, exist_ok=True)
LOCK = os.path.join(DATA, "viec3.lock")
lock_rec, lock_old = acquire_lock(LOCK, "v3_discovery_pilot")
if lock_rec is None:
    print("TỪ CHỐI: khóa đang giữ pid sống %s" % lock_old.get("pid")); sys.exit(3)

MAX_REQ = int(sys.argv[1]) if len(sys.argv) > 1 else 170
h = Http(DATA, phase="v3disc", max_req=MAX_REQ)

# ---- Pha 1: mẫu fill từ 20 thị trường lớn nhất (volumeNum, chỉ để chọn mẫu) ----
recs = [json.loads(l) for l in open(os.path.join(DATA, "listing", "listing_slim.jsonl.valid_FULL"), encoding="utf-8")]
big = sorted(recs, key=lambda r: -(r.get("volumeNum_chi_mo_ta_khong_dung_loc") or 0))[:20]
mid = T0 + (T1 - T0) // 2
wallet_markets = defaultdict(set)   # ví -> tập thị trường xuất hiện
wallet_fills = Counter()
fills_seen = 0
try:
    for i, r in enumerate(big):
        for a, b in ((T0, mid), (mid, T1)):
            q = {"condition_id": r["conditionId"], "taker_only": "false",
                 "start": str(a), "end": str(b), "limit": "500"}
            doc, st = h.get(DATA_API + "/v2/trades?" + urllib.parse.urlencode(q),
                            "d3_m%d_%s" % (i + 1, r["slug"][:20] if r.get("slug") else r["id"]))
            d = doc.get("data") or [] if isinstance(doc, dict) else []
            for f in d:
                w = f.get("proxy_wallet")
                if w:
                    wallet_markets[w].add(r["conditionId"])
                    wallet_fills[w] += 1
                fills_seen += 1
        h.checkpoint(step="v3disc_p1", market=i + 1, of=20, wallets=len(wallet_markets), req=h.count_phase)
        print("mẫu %d/20: %s | lũy kế %d ví, %d fill, req=%d" %
              (i + 1, (r.get("question") or "")[:40], len(wallet_markets), fills_seen, h.count_phase), flush=True)
except StopRun as e:
    print("DỪNG THEO LUẬT (pha 1): %s" % e)

rank = sorted(wallet_fills, key=lambda w: (-len(wallet_markets[w]), -wallet_fills[w]))
top10 = [{"wallet": w, "n_markets": len(wallet_markets[w]), "n_fills_mau": wallet_fills[w]} for w in rank[:10]]
jdump(os.path.join(OUT, "phase1_wallet_rank.json"),
      {"markets_sampled": len(big), "fills_seen": fills_seen,
       "distinct_wallets": len(wallet_markets), "requests_used": h.count_phase, "top10": top10})
print("PHA 1 XONG: %d ví riêng biệt, %d fill; top 10 theo số thị trường:" % (len(wallet_markets), fills_seen))
for t in top10:
    print("   %s | %d thị trường | %d fill mẫu" % (t["wallet"][:14], t["n_markets"], t["n_fills_mau"]))

# ---- Pha 2: fetch toàn bộ Đ1 theo VÍ cho top 3 (cursor phân trang) ----
results = []
for j, t in enumerate(top10[:3]):
    w = t["wallet"]
    url = DATA_API + "/v2/trades?" + urllib.parse.urlencode(
        {"user": w, "taker_only": "false", "start": str(T0), "end": str(T1), "limit": "500"})
    rows, pages, capped = [], 0, False
    try:
        while pages < 40:
            doc, st = h.get(url, "d3_w%d_p%d" % (j + 1, pages + 1))
            d = doc.get("data") or [] if isinstance(doc, dict) else []
            nc = doc.get("next_cursor") if isinstance(doc, dict) else None
            pages += 1
            rows.extend(d)
            h.checkpoint(step="v3disc_p2", wallet=j + 1, pages=pages, rows=len(rows), req=h.count_phase)
            if not nc:
                break
            sep = "&" if "?" in url else "?"
            url = (url.split("&cursor=")[0] if "&cursor=" in url else url) + sep + "cursor=" + urllib.parse.quote(nc, safe="")
        else:
            capped = True
    except StopRun as e:
        print("DỪNG THEO LUẬT (pha 2, ví %d): %s" % (j + 1, e)); capped = True
    usd = 0.0
    mkts = set()
    for f in rows:
        try: usd += float(f.get("price") or 0) * float(f.get("size") or 0)
        except Exception: pass
        if f.get("condition_id"): mkts.add(f["condition_id"])
    rec = {"wallet": w, "pages": pages, "fills": len(rows), "usd": round(usd, 2),
           "markets": len(mkts), "pages_capped_40": capped, "requests": pages}
    results.append(rec)
    print("VÍ %d (%s…): %d trang, %d fill, %.0f USD, %d thị trường%s" %
          (j + 1, w[:12], pages, len(rows), usd, len(mkts), " | CHẠM TRẦN 40 (CẬN DƯỚI)" if capped else ""), flush=True)
    if h.count_phase >= h.max_req:
        print("hết ngân sách pilot — dừng sau %d ví" % (j + 1)); break

jdump(os.path.join(OUT, "phase2_whale_cost.json"),
      {"results": results,
       "note": "chi phí/ví đo thật; chạm trần 40 trang = cận dưới"})
h.checkpoint(step="v3disc_DONE", phase1_wallets=len(wallet_markets), whales_measured=len(results))
print("PILOT KHÁM PHÁ XONG | request=%d (ngày %d)" % (h.count_phase, h.count_today + h.count_phase))
release_lock(LOCK)
