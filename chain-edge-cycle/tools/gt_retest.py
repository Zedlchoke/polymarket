#!/usr/bin/env python3
"""3 call GT chậm để trả lời câu OHLCV còn treo — CHỈ chạy khi đã >= 2026-11-03T00:00:00Z
(hết thời gian tạm dừng GT đã cam kết). Đúng 3 call, cách nhau >= 10 giây.

Ma trận (chốt từ checkpoint chặng 1):
  1. day?limit=10    — đối chứng (đã chạy được ngày 2026-11-02 13:41Z)
  2. hour?limit=10   — câu hỏi chính: hour có chịu limit nhỏ?
  3. day?limit=100   — tìm ngưỡng limit bị 200-rỗng (đã biết >=100 rỗng ở pool này hôm 2026-11-02)
Kết quả ghi data/gt_retest_2026-11-03.json + 1 dòng checkpoint.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_common as fc

ROOT = fc.ROOT
P = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"  # pool đối chứng, giống lần trước

now = datetime.datetime.now(datetime.timezone.utc)
if now < datetime.datetime(2026, 11, 3, tzinfo=datetime.timezone.utc):
    print("CHƯA hết thời gian dừng GT — từ chối chạy, giữ lời cam kết.")
    sys.exit(2)

out = {"ran_at": fc.utcnow_iso(), "calls": []}
for label, q in [("day_limit10", f"networks/eth/pools/{P}/ohlcv/day?limit=10"),
                 ("hour_limit10", f"networks/eth/pools/{P}/ohlcv/hour?limit=10"),
                 ("day_limit100", f"networks/eth/pools/{P}/ohlcv/day?limit=100")]:
    try:
        st, js = fc.http_json("geckoterminal", q)
        lst = (js.get("data", {}).get("attributes", {}) or {}).get("ohlc_list") or []
        out["calls"].append({"label": label, "query": q, "status": st, "n_candles": len(lst),
                             "oldest": lst[-1][0] if lst else None})
        print(f"{label}: HTTP {st}, {len(lst)} nến" + (f", cũ nhất {lst[-1][0]}" if lst else " (RỖNG)"))
    except Exception as e:
        out["calls"].append({"label": label, "query": q, "error": f"{type(e).__name__}: {e}"})
        print(f"{label}: LỖI {type(e).__name__}: {e}")

json.dump(out, open(os.path.join(ROOT, "data", "gt_retest_2026-11-03.json"), "w"), indent=1)
with open(os.path.join(ROOT, "state", "checkpoint.md"), "a", encoding="utf-8") as f:
    f.write(f"\n- [GT đo lại {fc.utcnow_iso()}] " + "; ".join(
        f"{c['label']}={c.get('n_candles', 'ERR')}" for c in out["calls"]) + "\n")
print("đã ghi data/gt_retest_2026-11-03.json + dòng checkpoint")
