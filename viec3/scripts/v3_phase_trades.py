# v3_phase_trades.py — PHA ĐO NGƯỠNG 10.000 USD + ĐẾM VÍ (mẫu hệ thống, KHÔNG theo lãi):
# với mỗi thị trường hợp lệ được chọn: phân trang /v2/trades?market=<cid>&taker_only=false
# &start=T0&end=T1&limit=500 (CHỈ trade trong đoạn 1), tính:
#   - số trang, số dòng, số fill duy nhất (khóa txHash+tokenId+timestamp+side+size)
#   - tổng USD đoạn 1 = Σ(price×size) trên fill duy nhất  [KHÔNG dùng volumeNum]
#   - đạt/không đạt ngưỡng 10.000 USD; tập ví (proxyWallet) từng giao dịch
# Mẫu chọn: hệ thống (mỗi k-thị trường theo thứ tự conditionId — cố định, không dính lãi/khối lượng).
import sys, os, json, gzip, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.parse
from viec3_lib import Http, DATA_API, T0, T1, jdump, jlappend

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
MAX_REQ = int(sys.argv[2]) if len(sys.argv) > 2 else 60
SAMPLE_N = int(sys.argv[3]) if len(sys.argv) > 3 else 6
MAX_PAGES_PER_MARKET = 40   # trần an toàn như probe V2 (chạm trần = ghi rõ CẬN DƯỚI)

LD = os.path.join(DATA, "listing")
TD = os.path.join(DATA, "trades")
valid_path = LD + "_slim.jsonl.valid"
recs = []
with open(valid_path, encoding="utf-8") as f:
    for line in f:
        recs.append(json.loads(line))
N = len(recs)
if N == 0:
    print("KHÔNG có thị trường hợp lệ — dừng"); sys.exit(0)
recs.sort(key=lambda r: r.get("conditionId") or "")   # thứ tự cố định, không dính lãi
k = max(1, N // SAMPLE_N)
sample = [recs[i] for i in range(0, N, k)][:SAMPLE_N]
print("Tổng hợp lệ=%d | mẫu hệ thống k=%d → %d thị trường" % (N, k, len(sample)))

h = Http(DATA, phase="trades", max_req=MAX_REQ)
summ_path = os.path.join(TD, "sample_summary.jsonl")
wallets_all = set()

for idx, rec in enumerate(sample):
    cid = rec["conditionId"]
    done_path = os.path.join(TD, cid + ".summary.json")
    if os.path.exists(done_path):
        s = json.load(open(done_path, encoding="utf-8"))
        wallets_all |= set(s.get("wallets", []))
        print("[%d/%d] ĐÃ CÓ %s (pages=%s usd=%s)" % (idx + 1, len(sample), cid[:14], s.get("pages"), s.get("usd_d1")))
        continue
    q = {"market": cid, "taker_only": "false", "start": str(T0), "end": str(T1), "limit": "500"}
    url = DATA_API + "/v2/trades?" + urllib.parse.urlencode(q)
    rows, pages, nc = [], 0, None
    hit_cap = False
    rawf = os.path.join(TD, cid + ".jsonl.gz")
    os.makedirs(TD, exist_ok=True)
    out = gzip.open(rawf, "wt", encoding="utf-8")
    while pages < MAX_PAGES_PER_MARKET:
        doc, st = h.get(url, "tr_m%d_p%d" % (idx + 1, pages + 1))
        if isinstance(doc, dict):
            data = doc.get("data") or []
            nc = doc.get("next_cursor")
        elif isinstance(doc, list):
            data, nc = doc, None
        else:
            data, nc = [], None
        pages += 1
        for r in data:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
        rows.extend(data)
        h.checkpoint(step="trades", market=cid, market_idx=idx + 1, of=len(sample),
                     pages_this_market=pages, rows=len(rows))
        if not nc:
            break
        sep = "&" if "?" in url else "?"
        url = (url.split("&cursor=")[0] if "&cursor=" in url else url) + sep + "cursor=" + urllib.parse.quote(nc, safe="")
    else:
        hit_cap = True  # vòng while kết thúc vì chạm trần trang
    out.close()
    fills = {}
    wallets = set()
    for r in rows:
        key = (r.get("transactionHash"), r.get("tokenId"), r.get("timestamp"), r.get("side"), r.get("size"))
        if key not in fills:
            try:
                usd = float(r.get("price") or 0) * float(r.get("size") or 0)
            except Exception:
                usd = 0.0
            fills[key] = usd
        if r.get("proxyWallet"):
            wallets.add(r["proxyWallet"])
    usd_d1 = round(sum(fills.values()), 2)
    s = {"conditionId": cid, "question": rec.get("question"), "sportsMarketType": rec.get("sportsMarketType"),
         "gameStartTime": rec.get("gameStartTime"), "pages": pages, "rows": len(rows),
         "unique_fills": len(fills), "usd_d1": usd_d1,
         "pass_10k": usd_d1 >= 10000.0, "hit_page_cap": hit_cap,
         "wallets_n": len(wallets), "wallets": sorted(wallets),
         "row_keys_sample": sorted(rows[0].keys()) if rows else []}
    jdump(done_path, s)
    jlappend(summ_path, {k2: v for k2, v in s.items() if k2 != "wallets"})
    wallets_all |= wallets
    print("[%d/%d] %s | pages=%d rows=%d fills=%d USD=%.2f %s | ví=%d%s" %
          (idx + 1, len(sample), cid[:14], pages, len(rows), len(fills), usd_d1,
           "≥10k ✓" if s["pass_10k"] else "<10k", len(wallets),
           " | CHẠM TRẦN 40 TRANG (CẬN DƯỚI)" if hit_cap else ""), flush=True)

jdump(os.path.join(TD, "wallets_union.json"), {"wallets_union_sample": sorted(wallets_all),
                                               "n_wallets_union_sample": len(wallets_all),
                                               "sample_n": len(sample), "k": k, "N_valid": N})
h.checkpoint(step="trades_DONE", wallets_union=len(wallets_all))
print("XONG. Ví hợp nhất trong mẫu: %d | requests pha=%d (hôm nay %d)" %
      (len(wallets_all), h.count_phase, h.count_today + h.count_phase))
