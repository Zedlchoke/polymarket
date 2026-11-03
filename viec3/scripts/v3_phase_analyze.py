# v3_phase_analyze.py — PHÂN TÍCH OFFLINE (không gọi API): đếm từng bước lọc, sổ request
# theo ngày-chạy, ước tính request/ngày cho hồ sơ chính (Việc 4), kết luận 14 ngày.
# Không chọn ví, không tính điểm, không dùng volumeNum cho bất kỳ ngưỡng nào.
import sys, os, json, glob, gzip
from collections import Counter

DATA = sys.argv[1] if len(sys.argv) > 1 else "viec3/data"
LD = os.path.join(DATA, "listing")
TD = os.path.join(DATA, "trades")

# ---------- sổ request ----------
led = [json.loads(l) for l in open(os.path.join(DATA, "ledger.jsonl"), encoding="utf-8")]
bnd_idx = [i for i, l in enumerate(led) if l.get("tag") == "DAY_BOUNDARY"]
day1 = led[:bnd_idx[0]] if bnd_idx else led
day2 = led[bnd_idx[0]:] if bnd_idx else []
def stats(ls):
    api = [l for l in ls if l.get("status") is not None and l.get("tag") != "DAY_BOUNDARY"]
    return {"dong_so": len(ls), "api_requests": len(api),
            "http200": sum(1 for l in api if l.get("status") == 200),
            "http422": sum(1 for l in api if l.get("status") == 422),
            "khac": sum(1 for l in api if l.get("status") not in (200, 422)),
            "khong_phan_hoi": sum(1 for l in ls if l.get("status") is None),
            "theo_phase": dict(Counter(l.get("phase") for l in ls if l.get("tag") != "DAY_BOUNDARY"))}
s1, s2 = stats(day1), stats(day2)
print("SỔ NGÀY 1:", json.dumps(s1, ensure_ascii=False))
print("SỔ NGÀY 2:", json.dumps(s2, ensure_ascii=False))
print("chênh 193-184 ngày 1 =", 193 - 184, "dòng không phải API:",
      [l.get("tag") for l in day1 if l.get("status") is None])

# ---------- đếm từng bước lọc (từ buckets đã phân loại) ----------
seen = {}
for b in ["valid", "seasonal", "missing_gst", "fallback", "anomaly"]:
    p = os.path.join(LD, "listing_slim.jsonl." + b)
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            seen[r["id"]] = r.get("bucket") or b
# đếm lại toàn bộ bucket phụ từ mọi trang đã lưu (phi thể thao / gst ngoài đoạn)
sub = Counter()
for p in glob.glob(os.path.join(LD, "slices", "*", "page_*.json.gz")) + \
        glob.glob(os.path.join(LD, "page_*.json.gz")):
    with gzip.open(p, "rt", encoding="utf-8") as f:
        for r in json.load(f):
            if r.get("id") in seen:
                continue
            labels = [t.get("label") for t in (r.get("tags") or []) if isinstance(t, dict)]
            smt = r.get("sportsMarketType") or ""
            import datetime
            def pe(v):
                if v in (None, ""): return None
                s = str(v).strip()
                if s.isdigit(): return int(s)
                try:
                    d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00").replace("+00", "+00:00"))
                    return int(d.timestamp())
                except Exception:
                    return None
            gst = pe(r.get("gameStartTime"))
            if not labels: sub["tag_rong"] += 1
            elif "Sports" not in labels: sub["phi_theo_thao"] += 1
            elif not smt: sub["mua_vu"] += 1
            elif gst is None: sub["thieu_gst"] += 1
            elif 1757721600 <= gst < 1765497600: sub["valid"] += 1
            elif gst < 1757721600: sub["gst_truoc_D1"] += 1
            else: sub["gst_sau_D1"] += 1
cnt = Counter(seen.values()) + sub
# map tên bucket nội bộ sang tên báo cáo
report_counts = {
    "tong_id_duy_nhat_da_thay": sum(cnt.values()),
    "tag_rong_fallback": cnt.get("fallback", 0) + cnt.get("tag_rong", 0),
    "phi_theo_thao": cnt.get("non_sports_plain", 0) + cnt.get("phi_theo_thao", 0),
    "mua_vu_smt_rong": cnt.get("seasonal", 0) + cnt.get("mua_vu", 0),
    "thieu_gameStartTime": cnt.get("missing_gst", 0) + cnt.get("thieu_gst", 0),
    "hop_le_gameStart_trong_D1": cnt.get("valid", 0),
    "gst_truoc_D1": cnt.get("side", 0) if "side" in cnt else cnt.get("gst_truoc_D1", 0),
    "anomaly_smt_khong_co_tag_Sports": cnt.get("anomaly", 0),
}
print("ĐẾM TỪNG BƯỚC (đến thời điểm hiện tại):", json.dumps(report_counts, ensure_ascii=False, indent=1))

# ---------- mẫu trade ----------
samples = []
sp = os.path.join(TD, "sample_summary.jsonl")
if os.path.exists(sp):
    samples = [json.loads(l) for l in open(sp, encoding="utf-8")]
if samples:
    pages = [s["pages"] for s in samples]
    usd = [s["usd_d1"] for s in samples]
    passed = [s for s in samples if s["pass_10k"]]
    print("MẪU TRADE: n=%d | trang/trường: min=%d med=%.1f max=%d | USD đoạn 1: min=%.0f med=%.0f max=%.0f" %
          (len(samples), min(pages), sorted(pages)[len(pages)//2], max(pages),
           min(usd), sorted(usd)[len(usd)//2], max(usd)))
    print("  đạt ≥10k: %d/%d | chạm trần 40 trang: %d" % (len(passed), len(samples),
          sum(1 for s in samples if s.get("hit_page_cap"))))
    wu = os.path.join(TD, "wallets_union.json")
    if os.path.exists(wu):
        w = json.load(open(wu))
        print("  ví hợp nhất mẫu: %d (mẫu %d thị trường)" % (w["n_wallets_union_sample"], w["sample_n"]))
    # ước tính hồ sơ chính
    N_valid = report_counts["hop_le_gameStart_trong_D1"]
    avg_pages = sum(pages) / len(pages)
    est_pages_all_valid = N_valid * avg_pages
    kept_rate = len(passed) / len(samples)
    est_kept = N_valid * kept_rate
    est_pages_kept = sum(s["pages"] for s in passed) / max(1, len(passed)) * est_kept
    print("ƯỚC TÍNH (mẫu %d, ngoại suy tuyến tính):" % len(samples))
    print("  trung bình %.1f trang/thị trường → đo ngưỡng hết %d valid ≈ %.0f request ≈ %.1f ngày @200/ngày" %
          (avg_pages, N_valid, est_pages_all_valid, est_pages_all_valid / 200))
    print("  tỷ lệ đạt ngưỡng %.0f%% → giữ ~%.0f thị trường; lấy hết trade phần giữ ≈ %.0f request ≈ %.1f ngày @200/ngày" %
          (100 * kept_rate, est_kept, est_pages_kept, est_pages_kept / 200))
    print("  KẾT LUẬN 14 NGÀY: %s" % ("VƯỢT" if est_pages_kept / 200 > 14 else "KỊP (cần kiểm lại)"))
    json.dump({"samples": samples, "est": {"avg_pages": avg_pages, "N_valid": N_valid,
                "est_pages_all_valid": est_pages_all_valid, "kept_rate": kept_rate,
                "est_kept": est_kept, "est_pages_kept": est_pages_kept,
                "days_all_valid": est_pages_all_valid / 200, "days_kept": est_pages_kept / 200}},
              open(os.path.join(DATA, "analysis_trades.json"), "w"), ensure_ascii=False, indent=1)
else:
    print("CHƯA có mẫu trade")
json.dump({"day1": s1, "day2": s2, "counts": report_counts},
          open(os.path.join(DATA, "analysis_counts.json"), "w"), ensure_ascii=False, indent=1)
