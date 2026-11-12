# v4_pilot.py — PILOT 100 THỊ TRƯỜNG (luật sửa 2026-11-12): 100 thị trường ĐẦU theo thứ tự id
# trong tập hợp lệ có volumeNum ≥ 100.000 USD (volumeNum CHỈ dùng để CHỌN MẪU pilot — disclosed;
# pipeline thật đo ngưỡng từ trade). Với từng thị trường: lấy TOÀN BỘ fill đoạn 1 bằng
# /v2/trades?condition_id=…&start=T0&end=T1&limit=500 + CHIA CỬA SỔ THỜI GIAN khi trang đầy 500
# (kỹ thuật đã kiểm chứng). Đo: request dùng, fill duy nhất, USD đoạn 1 (Σ price×size dedupe),
# đạt/không đạt 100k THEO TRADE, số ví. KHÔNG tính điểm, KHÔNG chọn ví giỏi.
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "viec3", "scripts"))
from viec3_lib import Http, StopRun, DATA_API, T0, T1, acquire_lock, release_lock, jdump, jlappend
import urllib.parse

DATA = "viec3/data"
OUT = "viec4_pilot/data"
os.makedirs(OUT, exist_ok=True)
MAX_REQ = int(sys.argv[1]) if len(sys.argv) > 1 else 195
SAMPLE_N = 100
TH = 100000.0
MIN_CHUNK_S = 60

LOCK = os.path.join(DATA, "viec3.lock")
lock_rec, lock_old = acquire_lock(LOCK, "v4_pilot max_req=%d" % MAX_REQ)
if lock_rec is None:
    print("TỪ CHỐI: khóa đang giữ bởi pid sống %s" % lock_old.get("pid")); sys.exit(3)

recs = [json.loads(l) for l in open(os.path.join(DATA, "listing", "listing_slim.jsonl.valid_FULL"), encoding="utf-8")]
pool = [r for r in recs if (r.get("volumeNum_chi_mo_ta_khong_dung_loc") or 0) >= TH]
pool.sort(key=lambda r: r["id"])  # thứ tự id — cố định, tính lại được
sample = pool[:SAMPLE_N]
print("Tập ≥100k (mô tả, chọn mẫu): %d thị trường → pilot %d đầu theo id" % (len(pool), len(sample)))
jdump(os.path.join(OUT, "pilot_sample.json"),
      {"n_pool_ge100k": len(pool), "n_pilot": len(sample),
       "sample": [{"id": r["id"], "conditionId": r["conditionId"], "question": r["question"],
                   "slug": r["slug"], "volumeNum_mo_ta": r.get("volumeNum_chi_mo_ta_khong_dung_loc")} for r in sample]})

h = Http(DATA, phase="pilot4", max_req=MAX_REQ)

def fetch_window(cid, a, b, depth=0):
    fills, reqs, capped = [], 0, False
    q = {"condition_id": cid, "taker_only": "false", "start": str(a), "end": str(b), "limit": "500"}
    doc, st = h.get(DATA_API + "/v2/trades?" + urllib.parse.urlencode(q),
                    "p4_%s_%d" % (cid[2:8], a))
    reqs += 1
    d = doc.get("data") or [] if isinstance(doc, dict) else []
    if len(d) < 500:
        return d, reqs, False
    if b - a <= MIN_CHUNK_S or depth > 40:
        return d, reqs, True
    mid = a + (b - a) // 2
    for aa, bb in ((a, mid), (mid, b)):
        f2, r2, c2 = fetch_window(cid, aa, bb, depth + 1)
        fills.extend(f2); reqs += r2; capped = capped or c2
        if h.count_phase >= h.max_req:
            return fills, reqs, True
    return fills, reqs, capped

summ_path = os.path.join(OUT, "pilot_summary.jsonl")
wallets_all = set()
done = 0
try:
    for i, rec in enumerate(sample):
        dp = os.path.join(OUT, rec["conditionId"] + ".summary.json")
        if os.path.exists(dp):
            s = json.load(open(dp, encoding="utf-8"))
            wallets_all |= set(s.get("wallets", []))
            done += 1
            continue
        cid = rec["conditionId"]
        rows, reqs, capped = fetch_window(cid, T0, T1)
        uniq, wallets = {}, set()
        for r in rows:
            k = (r.get("transaction_hash"), r.get("token_id"), r.get("timestamp"), r.get("side"), r.get("size"))
            if k not in uniq:
                try: uniq[k] = float(r.get("price") or 0) * float(r.get("size") or 0)
                except Exception: uniq[k] = 0.0
            if r.get("proxy_wallet"): wallets.add(r["proxy_wallet"])
        usd = round(sum(uniq.values()), 2)
        s = {"id": rec["id"], "conditionId": cid, "question": rec["question"], "slug": rec["slug"],
             "requests": reqs, "fills": len(uniq), "usd_d1_trade": usd,
             "pass_100k_by_trade": usd >= TH, "volumeNum_mo_ta": rec.get("volumeNum_chi_mo_ta_khong_dung_loc"),
             "window_capped": capped, "wallets_n": len(wallets), "wallets": sorted(wallets)}
        jdump(dp, s)
        jlappend(summ_path, {k: v for k, v in s.items() if k != "wallets"})
        wallets_all |= wallets
        done += 1
        print("[%d/%d] %s | req=%d fills=%d USD=%.0f %s | ví=%d%s" %
              (i + 1, len(sample), (rec.get("slug") or "")[:38], reqs, len(uniq), usd,
               "≥100k✓" if s["pass_100k_by_trade"] else "<100k", len(wallets),
               " | CẬN DƯỚI(burst)" if capped else ""), flush=True)
        h.checkpoint(step="pilot4", market=i + 1, of=len(sample), req=h.count_phase,
                     day=h.count_today + h.count_phase, wallets_union=len(wallets_all))
        if h.count_phase >= h.max_req:
            print("CHẠM max_req — dừng pilot tại %d/%d (đủ ước tính)" % (i + 1, len(sample)))
            break
except StopRun as e:
    print("DỪNG THEO LUẬT: %s — pilot đo được %d/%d thị trường" % (e, done, len(sample)))

jdump(os.path.join(OUT, "pilot_wallets_union.json"),
      {"n": len(wallets_all), "measured_markets": done, "target": len(sample)})
h.checkpoint(step="pilot4_DONE_or_PAUSED", measured=done, wallets=len(wallets_all))
print("PILOT XONG PHẦN NGÂN SÁCH: đo %d/%d | ví hợp nhất: %d | request pha=%d (ngày %d)" %
      (done, len(sample), len(wallets_all), h.count_phase, h.count_today + h.count_phase))
release_lock(LOCK)
