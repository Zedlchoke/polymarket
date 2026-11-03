#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W1 đêm 2026-11-02 — probe + (nếu probe qua) điền epoch + discovery getLogs trên Base RPC.

Chạy bằng cron 18:05Z 2026-11-02 (giải lao sau 429 lúc 14:23:44Z). Mọi call qua tools/fetch_common.py.
Luật: 429/403 → DỪNG hẳn nguồn cho đêm; lỗi lặp 3 lần cùng một loại → dừng bước; checkpoint sau mỗi đợt.

Chạy:  python3 -I tools/w1_night_rpc.py            (probe → quyết định → discovery)
       python3 -I tools/w1_night_rpc.py --probe-only
       python3 -I tools/w1_night_rpc.py --dry-run  (không gọi mạng, in kế hoạch)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fetch_common as fc  # noqa: E402

DRY = "--dry-run" in sys.argv
PROBE_ONLY = "--probe-only" in sys.argv

# Factory + sự kiện — chỉ dùng địa chỉ đã ghi trong state/checkpoint.md §4.2.
# UniswapV3 PoolCreated(address,address,address,uint24,int24,address): topic0 chuỗi nổi tiếng;
# Aerodrome: CHƯA biết chữ ký sự kiện trên chắc → đo thực nghiệm bằng getLogs không topic trên range hẹp.
UNIV3_FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
AERODROME_FACTORY = "0x420DD381b31b62cF37E8F6CC62c9a7757CE5A312"
TOPIC0_UNIV3_POOLCREATED = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118"
BASE_BLOCK_TIME_S = 2.0          # Base 2s/block — dùng quy đổi range↔thời gian (đối chiếu khi có blockNumber)
RANGES_TO_TRY = [50000, 10000, 2000]   # thử range rộng trước, thu hẹp theo lỗi THỰC TẾ của RPC
MAX_DISCOVERY_CALLS = 60         # trần đợt đêm (để dư budget ngày; cap base_rpc = 150, đã dùng 5)

DATA_DIR = os.path.join(ROOT, "data", "rpc", "base")
os.makedirs(DATA_DIR, exist_ok=True)
NIGHT_STATE = os.path.join(ROOT, "state", "night_w1_rpc.json")


def rpc(method, params, note=""):
    """1 JSON-RPC call qua fetch_common. Trả (ok, result_or_error)."""
    if DRY:
        print("  [dry-run] sẽ gọi %s %s %s" % (method, str(params)[:80], note))
        fake = hex(30_000_000) if method == "eth_blockNumber" else []
        return True, fake
    try:
        status, body = fc.http("base_rpc", "", method="POST", payload={
            "jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    except fc.RateLimited as e:
        log_night("429/403 khi %s: %s → DỪNG nguồn base_rpc cho đêm" % (method, e))
        raise
    except fc.BudgetExceeded as e:
        log_night("vượt trần ngân sách: %s" % e)
        raise
    doc = json.loads(body.decode())
    if "error" in doc:
        return False, doc["error"]
    return True, doc.get("result")


def log_night(msg):
    line = "[%s] %s" % (fc.utcnow_iso(), msg)
    print(line, flush=True)
    with open(os.path.join(ROOT, "state", "night_log.md"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def save_state(obj):
    obj["updated"] = fc.utcnow_iso()
    json.dump(obj, open(NIGHT_STATE, "w"), indent=1, ensure_ascii=False)


def main():
    st = {"stage": "start"}
    save_state(st)
    # --- 1) khối hiện tại ---
    ok, res = rpc("eth_blockNumber", [])
    if not ok:
        log_night("eth_blockNumber lỗi: %s — DỪNG (không đo được mốc)" % res)
        return
    head = int(res, 16)
    st["head_block"] = head
    log_night("head block = %d" % head)
    save_state(st)

    # --- 2) probe UniV3 PoolCreated theo range giảm dần ---
    chosen_range = None
    for rng in RANGES_TO_TRY:
        frm, to = head - rng, head - 1
        ok, res = rpc("eth_getLogs", [{
            "fromBlock": hex(frm), "toBlock": hex(to),
            "address": UNIV3_FACTORY, "topics": [TOPIC0_UNIV3_POOLCREATED]}],
            note="UniV3 range %d" % rng)
        if ok:
            n = len(res) if isinstance(res, list) else -1
            log_night("UniV3 getLogs range %d block: OK, %d log (≈ %.1f ngày)" %
                      (rng, n, rng * BASE_BLOCK_TIME_S / 86400))
            chosen_range, logs = rng, res
            st["univ3_probe"] = {"range": rng, "n_logs": n}
            break
        else:
            log_night("UniV3 range %d bị từ chối: %s → thu hẹp" % (rng, str(res)[:120]))
    if chosen_range is None:
        st["stage"] = "probe_thất_bại_base_box3"
        save_state(st)
        log_night("Mọi range đều bị từ chối → ghi Box 3 cho Base (W1) đêm nay, không hạ ngưỡng.")
        return
    # --- 3) đo Aerodrome bằng range hẹp KHÔNG topic (không đoán chữ ký sự kiện) ---
    ok2, res2 = rpc("eth_getLogs", [{
        "fromBlock": hex(head - 2000), "toBlock": hex(head - 1),
        "address": AERODROME_FACTORY}], note="Aerodrome no-topic 2000 block")
    if ok2 and isinstance(res2, list):
        from collections import Counter
        topics = Counter(l["topics"][0] for l in res2 if l.get("topics"))
        st["aerodrome_probe"] = {"n_logs": len(res2),
                                 "topic0_counts": {k[:20]: v for k, v in topics.most_common(5)}}
        log_night("Aerodrome 2000 block không topic: %d log; topic0 nhiều nhất: %s" %
                  (len(res2), topics.most_common(3)))
    else:
        st["aerodrome_probe"] = {"error": str(res2)[:160]}
        log_night("Aerodrome probe lỗi: %s (không chặn UniV3)" % str(res2)[:120])
    save_state(st)
    if PROBE_ONLY or DRY:
        st["stage"] = "probe_xong"
        save_state(st)
        return

    # --- 4) D = số ngày lấy được trong ngân sách (đo, không đoán) ---
    calls_for_42d = int(42 * 86400 / BASE_BLOCK_TIME_S / chosen_range) + 1
    calls_for_21d = int(21 * 86400 / BASE_BLOCK_TIME_S / chosen_range) + 1
    budget_left = fc.BUDGETS["base_rpc"]["daily_cap"] - _used_today()
    budget_left = max(0, min(budget_left, MAX_DISCOVERY_CALLS))
    st.update({"chosen_range": chosen_range, "calls_42d": calls_for_42d,
               "calls_21d": calls_for_21d, "budget_left": budget_left})
    if calls_for_42d <= budget_left:
        D = 42
    elif calls_for_21d <= budget_left:
        D = (budget_left // calls_for_21d) * 21
        D = max(D, 21) if calls_for_21d <= budget_left else 0
    else:
        D = 0
    st["D_days"] = D
    log_night("range=%d → 42d cần %d call, 21d cần %d call, còn budget %d → D=%d ngày" %
              (chosen_range, calls_for_42d, calls_for_21d, budget_left, D))
    if D < 21:
        st["stage"] = "box3_base_không_đủ_sâu"
        save_state(st)
        log_night("D < 21 → Base ghi dự kiến Box 3 (giới hạn nguồn, không phải kết quả). Dừng discovery đêm.")
        return

    # --- 5) điền epoch §7 theo đúng luật đã đóng băng (D>=42: 3×14d, E3 kết thúc tại discovery) ---
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    seg_days = 14 if D >= 42 else max(7, D // 3)
    e3_end = now
    e3_start = e3_end - dt.timedelta(days=seg_days)
    e2_start = e3_start - dt.timedelta(days=seg_days)
    e1_start = e2_start - dt.timedelta(days=seg_days)
    st["epoch"] = {"E1": e1_start.isoformat(), "E2": e2_start.isoformat(),
                   "E3": e3_start.isoformat(), "E3_end": e3_end.isoformat(),
                   "seg_days": seg_days, "rule": "đã đóng băng step0 §7"}
    log_night("epoch điền: E1=%s … E3_end=%s (%d ngày/đoạn)" %
              (e1_start.isoformat(), e3_end.isoformat(), seg_days))
    save_state(st)

    # --- 6) discovery: getLogs lùi từ E3_end về E1_start, ghi raw từng chunk ---
    total_blocks = int((e3_end - e1_start).total_seconds() // BASE_BLOCK_TIME_S)
    n_chunks = (total_blocks // chosen_range) + 1
    log_night("discovery: %d block = %d chunk × %d call" % (total_blocks, n_chunks, chosen_range))
    out_raw = os.path.join(DATA_DIR, "univ3_poolcreated_%s.jsonl" % fc.utcnow_iso()[:10])
    n_logs_total = 0
    to_block = int(e3_end.timestamp() // BASE_BLOCK_TIME_S)
    end_block = int(e1_start.timestamp() // BASE_BLOCK_TIME_S)
    calls_used = 0
    with open(out_raw, "a") as f:
        while to_block > end_block and calls_used < budget_left:
            frm = max(to_block - chosen_range, end_block)
            ok, res = rpc("eth_getLogs", [{
                "fromBlock": hex(frm), "toBlock": hex(to_block),
                "address": UNIV3_FACTORY, "topics": [TOPIC0_UNIV3_POOLCREATED]}],
                note="chunk %d" % calls_used)
            if not ok:
                log_night("chunk lỗi: %s — DỪNG discovery, giữ dữ liệu đã có" % str(res)[:120])
                break
            for l in res or []:
                f.write(json.dumps(l) + "\n")
            n_logs_total += len(res or [])
            calls_used += 1
            to_block = frm - 1
            st.update({"calls_used": calls_used, "logs_so_far": n_logs_total,
                       "pulled_to_block": to_block, "raw_file": out_raw})
            save_state(st)
            if calls_used % 10 == 0:
                log_night("  tick: %d call, %d log, còn tới block %d" %
                          (calls_used, n_logs_total, to_block))
    st["stage"] = "discovery_xong" if to_block <= end_block else "discovery_dừng_giữa"
    st["n_logs_total"] = n_logs_total
    save_state(st)
    log_night("KẾT THÚC đợt RPC: %d call, %d log PoolCreated UniV3, raw tại %s" %
              (calls_used, n_logs_total, out_raw))


def _used_today():
    d = fc._load_daily()
    return d.get(fc._today(), {}).get("base_rpc", 0)


if __name__ == "__main__":
    main()
