#!/usr/bin/env python3
"""Chặng 3 — giá + ví + mẫu gas cho W1, CHỈ trên pool trong data/w1_base/universe.csv.

A) GIÁ: getLogs(address=pool, creation-2 .. creation+43200) → Swap (V3-style: data 5 từ 32 byte)
   → giá quote/base theo orientation token0/token1 (từ universe_raw.csv), chuẩn hóa decimals,
   cross-check sqrtPriceX96 (chênh >5% → suspicious=1).
B) GAS MẪU: receipt của ≤12 tx swap thật → gasUsed×effectiveGasPrice → ghi gas_sample.json
   (median, min, max, n). Nếu <10 mẫu → ghi cờ "THIẾU MẪU GAS".
C) VÍ: getLogs(address=base_token, topics=[Transfer], cùng range) → hướng chuyển so với địa chỉ
   pool: wallet→pool = BÁN base; pool→wallet = MUA base. Tổng hợp per (pool, wallet) + per wallet.

Luật: 3 lỗi liên tiếp giống nhau ở một pha → dừng pha đó (ghi rõ), sang pha khác.
Mọi request qua fetch_common. Raw log lưu file ngay (không giữ trong bộ nhớ).
"""
import csv
import datetime
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_common as fc

ROOT = fc.ROOT
RPC = "base_pubnode"
B_ANCHOR, TS_ANCHOR, SLOPE = 53420288, 1793629923, 2.0
DEC_SIG = "0x313ce567"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
QUOTE_DEC = {  # khóa theo ĐỊA CHỈ (universe.csv lưu địa chỉ ở cột quote)
    "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": 6,   # USDC
    "0xd9aaec86b65d86f6a7b5b1b0c42ffa5337d0d3fa": 6,   # USDbC
    "0x4200000000000000000000000000000000000006": 18,  # WETH
}
OUT = os.path.join(ROOT, "data", "w1_base")
SWAP_DIR = os.path.join(OUT, "swaps")
TR_DIR = os.path.join(OUT, "transfers")
os.makedirs(SWAP_DIR, exist_ok=True)
os.makedirs(TR_DIR, exist_ok=True)


def ts_of(b):
    return TS_ANCHOR - (B_ANCHOR - b) * SLOPE


def rpc(method, params):
    st, js = fc.http_json(RPC, "", method="POST",
                          payload={"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if "error" in js:
        raise RuntimeError(str(js["error"])[:150])
    return js["result"]


def get_logs_paginated(addr, frm, to, topics=None, depth=0):
    q = {"address": addr, "fromBlock": hex(frm), "toBlock": hex(to)}
    if topics:
        q["topics"] = topics
    try:
        return rpc("eth_getLogs", [q])
    except RuntimeError as e:
        if depth < 3 and ("10000" in str(e) or "too many" in str(e).lower() or "query returned" in str(e).lower()):
            mid = (frm + to) // 2
            return (get_logs_paginated(addr, frm, mid, topics, depth + 1)
                    + get_logs_paginated(addr, mid + 1, to, topics, depth + 1))
        raise


def s256(w):
    v = int(w, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def load_universe():
    raw = {}
    with open(os.path.join(OUT, "universe_raw.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            raw[r["pool"]] = r  # token0/token1 theo pool
    uni = []
    with open(os.path.join(OUT, "universe.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["token0"], r["token1"] = raw[r["pool"]]["token0"], raw[r["pool"]]["token1"]
            uni.append(r)
    return uni


def phase_prices(uni, state):
    dec_cache = {}
    gas = state.get("gas_samples", [])
    path = os.path.join(OUT, "prices.csv")
    new = not os.path.exists(path)
    pf = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(pf)
    if new:
        w.writerow(["pool", "quote", "base_token", "block", "ts_est_utc", "hour_bucket",
                    "price_quote_per_base", "quote_amount", "sqrt_ok", "suspicious"])
    cons = 0
    for i, u in enumerate(uni):
        pool, cb = u["pool"], int(u["creation_block"])
        base, quote = u["base_token"], u["quote"]
        t0, t1 = u["token0"], u["token1"]
        fn = os.path.join(SWAP_DIR, pool + ".json")
        try:
            if os.path.exists(fn):
                logs = json.load(open(fn, encoding="utf-8"))
            else:
                logs = get_logs_paginated(pool, max(cb - 2, 0), cb + 43200)
                json.dump(logs, open(fn, "w", encoding="utf-8"))
            cons = 0
        except Exception as e:
            cons += 1
            print(f"[{i+1}/{len(uni)}] {pool[:12]}… SWAP LỖI {str(e)[:90]}", flush=True)
            if cons >= 3:
                print("DỪNG pha giá (3 lỗi liên tiếp)", flush=True)
                break
            continue
        swaps = [l for l in logs if len(l.get("data", "0x")) == 322 and l.get("topics")]
        if base not in dec_cache and swaps:
            try:
                dec_cache[base] = int(rpc("eth_call", [{"to": base, "data": DEC_SIG}, "latest"]), 16)
            except Exception:
                dec_cache[base] = None
        db, dq = dec_cache.get(base), QUOTE_DEC[quote.lower()]
        if i == 0:
            t0c = Counter(l["topics"][0] for l in logs if l.get("topics"))
            print("  (đối chiếu) histogram topic0 pool đầu:", {k[:16] + "…": v for k, v in t0c.most_common(5)})
        for l in swaps:
            d = l["data"][2:]
            a0, a1 = s256("0x" + d[0:64]), s256("0x" + d[64:128])
            sqrt_p = (int(d[128:192], 16) / 2 ** 96) ** 2  # token1 per token0 (raw)
            b = int(l["blockNumber"], 16)
            ts = ts_of(b)
            if db is None or abs(a0) == 0 or abs(a1) == 0:
                continue
            if t1 == quote:   # token0=base, token1=quote
                price = (abs(a1) / abs(a0)) * 10 ** (db - dq)
                q_amt = abs(a1) / 10 ** dq
                sqrt_price = sqrt_p * 10 ** (db - dq)
            else:             # token0=quote, token1=base
                price = (abs(a0) / abs(a1)) * 10 ** (db - dq)
                q_amt = abs(a0) / 10 ** dq
                sqrt_price = (1 / sqrt_p) * 10 ** (db - dq) if sqrt_p > 0 else 0
            susp = 0
            if sqrt_price > 0 and abs(price - sqrt_price) / max(sqrt_price, 1e-12) > 0.05:
                susp = 1
            w.writerow([pool, quote, base, b,
                        datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat(),
                        int(ts // 3600 * 3600), f"{price:.10g}", f"{q_amt:.6f}",
                        int(sqrt_price > 0), susp])
        pf.flush()
        # gas mẫu: receipt của 1 swap tx từ pool này (tối đa 12 mẫu toàn cục)
        if len(gas) < 12 and swaps:
            try:
                txh = swaps[0]["transactionHash"]
                rc = rpc("eth_getTransactionReceipt", [txh])
                if rc.get("gasUsed"):
                    gas.append({"tx": txh, "gasUsed": int(rc["gasUsed"], 16),
                                "gasPrice_gwei": int(rc.get("effectiveGasPrice", "0x0"), 16) / 1e9})
            except Exception:
                pass
        state["gas_samples"] = gas
        state["prices_done"] = i + 1
        json.dump(state, open(os.path.join(OUT, "stage3_state.json"), "w"))
        print(f"[{i+1}/{len(uni)}] {pool[:12]}… swaps={len(swaps)} gas_mẫu={len(gas)}", flush=True)
        if (i + 1) % 10 == 0:
            used = fc._load_daily().get("base_pubnode", 0)
            with open(os.path.join(ROOT, "state", "checkpoint.md"), "a", encoding="utf-8") as cf:
                cf.write(f"- [giá {fc.utcnow_iso()}] pool {i+1}/{len(uni)}; publicnode đã dùng {used}/400 hôm nay\n")
    pf.close()
    if gas:
        costs = [g["gasUsed"] * g["gasPrice_gwei"] / 1e9 for g in gas]  # ETH
        json.dump({"n": len(gas), "median_gwei_cost_eth": statistics.median(costs),
                   "min": min(costs), "max": max(costs),
                   "du_mau_10": len(gas) >= 10, "raw": gas},
                  open(os.path.join(OUT, "gas_sample.json"), "w"), indent=1)
        print(f"GAS MẪU: n={len(gas)}, median={statistics.median(costs):.10f} ETH/tx")


def phase_wallets(uni, state, limit=None):
    if limit:
        uni = uni[:limit]
    path = os.path.join(OUT, "wallets.csv")
    new = not os.path.exists(path)
    wf = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(wf)
    if new:
        w.writerow(["pool", "wallet", "n_mua", "n_ban", "vol_mua_token", "vol_ban_token",
                    "block_dau", "block_cuoi"])
    cons = 0
    agg = defaultdict(lambda: [0, 0, 0.0, 0.0, None, None])
    for i, u in enumerate(uni):
        base, pool, cb = u["base_token"], u["pool"], int(u["creation_block"])
        fn = os.path.join(TR_DIR, base + ".json")
        try:
            if os.path.exists(fn):
                logs = json.load(open(fn, encoding="utf-8"))
            else:
                logs = get_logs_paginated(base, max(cb - 2, 0), cb + 43200, topics=[TRANSFER])
                json.dump(logs, open(fn, "w", encoding="utf-8"))
            cons = 0
        except Exception as e:
            cons += 1
            print(f"[{i+1}/{len(uni)}] {base[:12]}… TRANSFER LỖI {str(e)[:90]}", flush=True)
            if cons >= 3:
                print("DỪNG pha ví (3 lỗi liên tiếp)", flush=True)
                break
            continue
        for l in logs:
            tops = l.get("topics", [])
            if len(tops) < 3:
                continue
            src, dst = addr_of(tops[1]), addr_of(tops[2])
            val = int(l["data"], 16) if l.get("data", "0x") not in ("", "0x") else 0
            b = int(l["blockNumber"], 16)
            ZERO = "0x" + "0" * 40
            if src == ZERO or dst == ZERO:
                continue
            for who, is_buy in ((dst, True), (src, False)):
                if who == pool:
                    continue  # dòng của chính pool không tính là ví
                a = agg[(pool, who)]
                if is_buy:
                    a[0] += 1
                    a[2] += val / 1e18  # tạm chuẩn 18 — sẽ ghi chú nếu lệch decimals
                else:
                    a[1] += 1
                    a[3] += val / 1e18
                a[4] = b if a[4] is None else min(a[4], b)
                a[5] = b if a[5] is None else max(a[5], b)
        state["wallets_done"] = i + 1
        json.dump(state, open(os.path.join(OUT, "stage3_state.json"), "w"))
        print(f"[{i+1}/{len(uni)}] ví {base[:12]}… xong", flush=True)
    for (pool, who), a in sorted(agg.items()):
        w.writerow([pool, who, a[0], a[1], f"{a[2]:.6f}", f"{a[3]:.6f}", a[4], a[5]])
    wf.close()
    # tổng hợp per wallet (qua các pool)
    per = defaultdict(lambda: [set(), 0, 0])
    for (pool, who), a in agg.items():
        per[who][0].add(pool)
        per[who][1] += a[0]
        per[who][2] += a[1]
    with open(os.path.join(OUT, "wallet_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w2 = csv.writer(f)
        w2.writerow(["wallet", "so_pool", "so_token", "n_mua", "n_ban"])
        for who, (pools, nb, ns) in sorted(per.items(), key=lambda kv: -kv[1][1]):
            w2.writerow([who, len(pools), len(pools), nb, ns])
    print(f"VÍ: {len(per)} ví duy nhất; ghi wallet_summary.csv")
    note = ("LUU Y: vol token quy ước 18 decimals cho mọi token — báo cáo mô tả chỉ dùng ĐẾM LỆNH "
            "(không phụ thuộc decimals), volume thô để tham khảo.")
    open(os.path.join(OUT, "wallets_NOTE.txt"), "w", encoding="utf-8").write(note)


def addr_of(t):
    return "0x" + t[-40:]


if __name__ == "__main__":
    uni = load_universe()
    print(f"vũ trụ: {len(uni)} pool")
    state_path = os.path.join(OUT, "stage3_state.json")
    state = {}
    if os.path.exists(state_path):
        state = json.load(open(state_path))
    phase = sys.argv[1] if len(sys.argv) > 1 else "prices"
    if phase == "prices":
        phase_prices(uni, state)
    elif phase == "wallets":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
        phase_wallets(uni, state, limit)
    else:
        phase_prices(uni, state)
        phase_wallets(uni, state)
