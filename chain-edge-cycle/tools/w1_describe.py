#!/usr/bin/env python3
"""Bước 1 W1 — MÔ TẢ, KHÔNG TÍNH ĐIỂM (không lãi ròng, không chọn pool/ví tốt nhất).

Đọc: universe.csv, prices.csv, wallets.csv, wallet_summary.csv, gas_sample.json
Xuất: wave01_new_listing_early_buy/step1_describe.md — chỉ số mô tả thô + cờ tập trung.
"""
import csv
import json
import os
import statistics
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "w1_base")
W = os.path.join(ROOT, "wave01_new_listing_early_buy")

uni = list(csv.DictReader(open(os.path.join(D, "universe.csv"), encoding="utf-8")))
prices = list(csv.DictReader(open(os.path.join(D, "prices.csv"), encoding="utf-8"))) if os.path.exists(os.path.join(D, "prices.csv")) else []

swaps_per_pool = Counter()
h0_quote_vol = defaultdict(float)
susp_per_pool = Counter()
for r in prices:
    swaps_per_pool[r["pool"]] += 1
    h0 = int(r["hour_bucket"])
    # giờ H0 = giờ chứa creation — xấp xỉ bằng bucket đầu tiên của pool
    # (lưu đủ để mô tả; không tính lãi)
    susp_per_pool[r["pool"]] += int(r.get("suspicious", 0))

with_pool = [(u, swaps_per_pool.get(u["pool"], 0)) for u in uni]
n_any = sum(1 for _, n in with_pool if n > 0)
n_two = sum(1 for _, n in with_pool if n >= 2)
n_zero = sum(1 for _, n in with_pool if n == 0)
by_epoch = defaultdict(lambda: [0, 0])
for u, n in with_pool:
    by_epoch[u["epoch"]][0] += 1
    by_epoch[u["epoch"]][1] += 1 if n > 0 else 0

vols = [h0_quote_vol[p] for p in h0_quote_vol] or [0]
wallets = list(csv.DictReader(open(os.path.join(D, "wallet_summary.csv"), encoding="utf-8"))) if os.path.exists(os.path.join(D, "wallet_summary.csv")) else []

gas = json.load(open(os.path.join(D, "gas_sample.json"), encoding="utf-8")) if os.path.exists(os.path.join(D, "gas_sample.json")) else {}

lines = []
lines.append("# W1 — Bước 1: MÔ TẢ (không tính điểm, không lãi ròng) — 2026-11-02 loop 10h\n")
lines.append("## Vũ trụ (đã đóng băng ở bước 0)")
lines.append(f"- Tổng pool: {len(uni)}. Có ≥1 swap trong 24h đầu: {n_any}. Có ≥2 swap: {n_two}. "
             f"KHÔNG swap nào (chết ngay / thiếu giá tuyệt đối): {n_zero} ({n_zero/max(len(uni),1):.0%}).")
for e in ("E1", "E2", "E3"):
    t, a = by_epoch[e]
    lines.append(f"- {e}: {t} pool, {a} pool có swap.")
lines.append(f"- Số swap/pool (chỉ pool có swap): median={statistics.median([n for _,n in with_pool if n>0]) if n_any else 0}, "
             f"max={max([n for _,n in with_pool], default=0)}.")
lines.append("\n## Cờ tập trung")
top_by_swaps = sorted(with_pool, key=lambda x: -x[1])[:5]
for u, n in top_by_swaps:
    lines.append(f"- pool {u['pool'][:8]}…{u['pool'][-4:]} ({u['epoch']}, quote {'USDC' if u['quote'].startswith('0x8335') else 'WETH' if u['quote'].endswith('0006') else 'USDbC'}): {n} swap.")
if n_any:
    share = top_by_swaps[0][1] / max(sum(n for _, n in with_pool), 1)
    lines.append(f"- Pool đứng đầu chiếm {share:.0%} tổng số swap — cờ tập trung (dữ liệu quá mỏng để kết luận).")
lines.append("\n## Ví (từ Transfer logs — mô tả thô)")
if wallets:
    n_buys = [int(w["n_mua"]) for w in wallets]
    lines.append(f"- Số ví duy nhất xuất hiện: {len(wallets)}. ")
    lines.append(f"- Số lệnh mua/ví: median={statistics.median(n_buys)}, max={max(n_buys)}.")
    multi = sum(1 for w in wallets if int(w["so_pool"]) >= 2)
    lines.append(f"- Ví giao dịch ≥2 pool trong dữ liệu: {multi}.")
else:
    lines.append("- (chưa có dữ liệu ví — pha wallets chưa chạy xong)")
lines.append("\n## Gas mẫu (nếu có)")
if gas:
    lines.append(f"- n={gas.get('n')}, median={gas.get('median_gwei_cost_eth')} ETH/tx, đủ mẫu 10: {gas.get('du_mau_10')}.")
else:
    lines.append("- chưa có (gặp lỗi hoặc chưa đủ pool có swap)")
lines.append("\n## Kết luận mô tả (không phải verdict)")
lines.append(f"- Vũ trụ 3-factory hầu như là POOL CHẾT NGAY: {n_zero}/{len(uni)} pool không có lấy một swap nào "
             "trong 24h đầu → 'tỷ lệ bỏ vì thiếu giá' sẽ vượt xa mức 30% của cổng T1 nếu backtest thật.")
lines.append("- Số liệu này là MÔ TẢ cấu trúc dữ liệu, không phải kết quả backtest, không phải verdict.")

open(os.path.join(W, "step1_describe.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
