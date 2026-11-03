# v3_phase_trades2.py — ĐO NGƯỠNG 10.000 USD + ĐẾM VÍ, bản 2 (đúng endpoint đã kiểm chứng):
# /v2/trades?condition_id=<cid>&taker_only=false&start=<a>&end=<b>&limit=500
# KHÔNG có cursor/offset (đã chứng minh 400/None) → nếu trang đủ 500 dòng: CHIA ĐÔI cửa sổ
# thời gian đệ quy tới khi mỗi mảnh <500 dòng (= đầy đủ mảnh đó). Dedupe fill theo
# (transaction_hash, token_id, timestamp, side, size). USD đoạn 1 = Σ price×size trên fill duy nhất.
# Mẫu hệ thống theo thứ tự conditionId (cố định, KHÔNG dính lãi/khối lượng).
import sys, os, json, gzip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, StopRun, DATA_API, T0, T1, jdump, jlappend

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
MAX_REQ = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SAMPLE_N = int(sys.argv[3]) if len(sys.argv) > 3 else 8
DAY_BOUNDARY = sys.argv[4] if len(sys.argv) > 4 else None
MIN_CHUNK_S = 60  # mảnh hẹp nhất 60 giây; nếu vẫn 500 dòng → ghi CẬN DƯỚI (burst)

LD = os.path.join(DATA, "listing")
TD = os.path.join(DATA, "trades")
recs = [json.loads(l) for l in open(os.path.join(LD, "listing_slim.jsonl.valid_FULL"), encoding="utf-8")]
recs.sort(key=lambda r: r.get("conditionId") or "")
# bỏ 2 thị trường đã đo ở debug (Bears O/U, 49ers spread) khỏi mẫu để tránh trùng
SKIP = {"nfl-chi-was-2025-10-13-total-49pt5"}
pool = [r for r in recs if r.get("slug") not in SKIP]
k = max(1, len(pool) // SAMPLE_N)
sample = [pool[i] for i in range(0, len(pool), k)][:SAMPLE_N]
print("Tổng hợp lệ=%d | mẫu hệ thống k=%d → %d thị trường" % (len(pool), k, len(sample)))

h = Http(DATA, phase="trades2", max_req=MAX_REQ, day_boundary_ts=DAY_BOUNDARY)

def fetch_window(cid, a, b, depth=0):
    """Lấy toàn bộ fill trong [a,b): trả (fills list, requests dùng, capped bool)."""
    fills, reqs, capped = [], 0, False
    q = {"condition_id": cid, "taker_only": "false",
         "start": str(a), "end": str(b), "limit": "500"}
    doc, st = h.get(DATA_API + "/v2/trades?" + urllib.parse.urlencode(q),
                    "t2_%s_%d_%d" % (cid[2:8], a, b))
    reqs += 1
    d = doc.get("data") or [] if isinstance(doc, dict) else []
    if len(d) < 500:
        return d, reqs, False
    # đầy 500 → chia đôi (đệ quy); mảnh hẹp nhất vẫn 500 → CẬN DƯỚI
    if b - a <= MIN_CHUNK_S or depth > 40:
        return d, reqs, True
    mid = a + (b - a) // 2
    for aa, bb in ((a, mid), (mid, b)):
        f2, r2, c2 = fetch_window(cid, aa, bb, depth + 1)
        fills.extend(f2); reqs += r2; capped = capped or c2
        if h.count_phase >= h.max_req:
            return fills, reqs, True
    return fills, reqs, capped

summ_path = os.path.join(TD, "sample_summary.jsonl")
wallets_all = set()
done = 0
for idx, rec in enumerate(sample):
    cid = rec["conditionId"]
    dp = os.path.join(TD, cid + ".summary2.json")
    if os.path.exists(dp):
        s = json.load(open(dp, encoding="utf-8"))
        wallets_all |= set(s.get("wallets", []))
        print("[%d/%d] ĐÃ CÓ %s (req=%s usd=%s)" % (idx + 1, len(sample), cid[:14], s.get("requests"), s.get("usd_d1")))
        continue
    try:
        rows, reqs, capped = fetch_window(cid, T0, T1)
    except StopRun as e:
        print("DỪNG THEO LUẬT/NGÂN SÁCH: %s" % e)
        break
    uniq = {}
    wallets = set()
    for r in rows:
        key = (r.get("transaction_hash"), r.get("token_id"), r.get("timestamp"), r.get("side"), r.get("size"))
        if key not in uniq:
            try:
                uniq[key] = float(r.get("price") or 0) * float(r.get("size") or 0)
            except Exception:
                uniq[key] = 0.0
        if r.get("proxy_wallet"):
            wallets.add(r["proxy_wallet"])
    usd = round(sum(uniq.values()), 2)
    s = {"conditionId": cid, "question": rec.get("question"), "slug": rec.get("slug"),
         "sportsMarketType": rec.get("sportsMarketType"),
         "gameStartTime": rec.get("gameStartTime"),
         "requests": reqs, "fills": len(uniq), "usd_d1": usd,
         "pass_10k": usd >= 10000.0, "window_capped": capped,
         "wallets_n": len(wallets), "wallets": sorted(wallets)}
    jdump(dp, s)
    jlappend(summ_path, {kk: vv for kk, vv in s.items() if kk != "wallets"})
    wallets_all |= wallets
    done += 1
    print("[%d/%d] %s | %s | req=%d fills=%d USD=%.2f %s | ví=%d%s" %
          (idx + 1, len(sample), cid[:14], (rec.get("slug") or "")[:40], reqs, len(uniq), usd,
           "≥10k ✓" if s["pass_10k"] else "<10k", len(wallets),
           " | CẬN DƯỚI (burst)" if capped else ""), flush=True)
    if h.count_phase >= h.max_req:
        print("CHẠM max_req — dừng mẫu tại %d/%d" % (idx + 1, len(sample)))
        break

jdump(os.path.join(TD, "wallets_union2.json"),
      {"wallets_union_sample": sorted(wallets_all), "n": len(wallets_all),
       "sample_done": done, "sample_target": len(sample)})
h.checkpoint(step="trades2_DONE_or_PAUSED", wallets_union=len(wallets_all), sample_done=done)
print("XONG: %d/%d thị trường đo | ví hợp nhất mẫu: %d | requests pha=%d" %
      (done, len(sample), len(wallets_all), h.count_phase))
