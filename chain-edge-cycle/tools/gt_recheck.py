#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đo lại GeckoTerminal sau thời gian dừng tới 2026-11-03 — đúng trình tự state/checkpoint.md §4.1:
  (1) day?limit=10 (đối chứng) → (2) hour?limit=10 → (3) nếu (2) có nến: hour?limit=10&before_timestamp=<cũ nhất>
  → (4) day?limit=100. TỐI ĐA 4 call, nghỉ ≥10s (fetch_common), 429/403 → DỪNG hẳn GT cho đêm.
Chạy bằng cron ~00:05Z 2026-11-03. Pool đối chứng: pool ETH đã dùng hôm 13:49 (giữ tính so sánh).
  python3 -I tools/gt_recheck.py           (chạy thật)
  python3 -I tools/gt_recheck.py --dry-run (chỉ in kế hoạch)
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fetch_common as fc  # noqa: E402

DRY = "--dry-run" in sys.argv
POOL_ETH = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"   # pool đối chứng của phiên 13:49 hôm 2026-11-02
OUT = os.path.join(ROOT, "state", "gt_recheck_20261103.json")


def call(path, note):
    if DRY:
        print("  [dry-run] GET %s (%s)" % (path, note))
        return {"dry": True, "n_candles": 10, "oldest_ts": 1735689600}
    status, body = fc.http("geckoterminal", path)
    try:
        doc = json.loads(body.decode())
    except Exception:
        doc = {"_raw": body[:300].decode("utf-8", "replace")}
    ohlcvs = (doc.get("data") or {}).get("ohlcvs") or [] if isinstance(doc, dict) else []
    n = len(ohlcvs)
    oldest = min((int(o[0]) for o in ohlcvs if o and o[0] is not None), default=None)
    print("  %s → HTTP %s, %s nến (cũ nhất %s)" % (note, status, n, oldest), flush=True)
    return {"status": status, "n_candles": n, "oldest_ts": oldest}


def main():
    # Chốt an toàn: cam kết dừng GT tới 2026-11-03 — chưa tới giờ thì CHỜ (không gọi sớm)
    import datetime as dt
    gate = dt.datetime(2026, 11, 3, 0, 0, 0, tzinfo=dt.timezone.utc)
    while dt.datetime.now(dt.timezone.utc) < gate:
        wait = (gate - dt.datetime.now(dt.timezone.utc)).total_seconds()
        print("chờ tới %s (còn %.0f phút)…" % (gate.isoformat(), wait / 60), flush=True)
        time.sleep(min(wait, 300))
    res = {}
    base = "networks/eth/pools/%s/ohlcv/" % POOL_ETH
    print("[%s] GT recheck bắt đầu" % fc.utcnow_iso(), flush=True)
    res["1_day_limit10"] = call(base + "day?limit=10", "đối chứng day limit=10")
    res["2_hour_limit10"] = call(base + "hour?limit=10", "hour limit=10")
    if (res["2_hour_limit10"] or {}).get("n_candles"):
        # trước_timestamp chưa có giá trị cũ nhất trong dry-run → dùng mốc giả lập découverte
        oldest = res["2_hour_limit10"].get("oldest_ts") or 1735689600  # placeholder nếu dry-run
        res["3_hour_before_ts"] = call(base + "hour?limit=10&before_timestamp=%s" % oldest,
                                       "hour limit=10 + before_timestamp")
    res["4_day_limit100"] = call(base + "day?limit=100", "day limit=100 (ngưỡng nghi vấn)")
    json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
    print("kết quả lưu: %s" % OUT, flush=True)
    # kết luận thô cho checkpoint (không đổi luật)
    if not DRY:
        ok_hour = bool((res.get("2_hour_limit10") or {}).get("n_candles"))
        ok_day100 = bool((res.get("4_day_limit100") or {}).get("n_candles"))
        concl = "hour-candle %s; day?limit=100 %s" % (
            "CÓ nến" if ok_hour else "RỖNG (ngưỡng limit ẩn vẫn còn)",
            "CÓ nến" if ok_day100 else "RỖNG (ngưỡng limit ẩn vẫn còn)")
        with open(os.path.join(ROOT, "state", "night_log.md"), "a", encoding="utf-8") as f:
            f.write("[%s] GT recheck: %s\n" % (fc.utcnow_iso(), concl))
        print("KẾT LUẬN: " + concl)


if __name__ == "__main__":
    main()
