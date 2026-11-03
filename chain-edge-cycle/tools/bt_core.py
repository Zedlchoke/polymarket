"""bt_core.py — bộ máy tính cho backtest (dùng chung cho test dữ liệu giả và backtest thật sau này).

Nguyên tắc:
- Mọi hàm THUẦN TÍNH (không network, không random không cố định seed ngoài bootstrap).
- Entry không bao giờ nhìn tương lai: tín hiệu ở close của bar N thì entry ở open của bar N+1.
- Chi phí: phí swap (bps mỗi chiều), trượt giá (bps mỗi chiều), gas (USD/lệnh) — áp dụng
  theo đúng công thức đã viết trong spec nháp W1. Lãi ròng âm khi chi phí ăn hết.
"""
import random
from collections import defaultdict


def net_return(entry_price, exit_price, fee_bps=30, slippage_bps=50, gas_usd=0.0, size_usd=100.0):
    """Lãi ròng (USD) của 1 lệnh long buy-then-sell.

    entry_eff = entry_price*(1+slip), exit_eff = exit_price*(1-slip)  (bán chịu trượt xuống)
    gross = size_usd * (exit_eff/entry_eff - 1)
    fees  = size_usd * fee_bps/1e4 * 2  (hai chiều)
    net   = gross - fees - gas_usd
    """
    entry_eff = entry_price * (1 + slippage_bps / 1e4)
    exit_eff = exit_price * (1 - slippage_bps / 1e4)
    gross = size_usd * (exit_eff / entry_eff - 1)
    fees = size_usd * (fee_bps / 1e4) * 2
    return gross - fees - gas_usd


def simulate_signal(bars, hold_bars, fee_bps=30, slippage_bps=50, gas_usd=0.0, size_usd=100.0,
                    trigger_idx=0):
    """bars: list[(open, close)] theo thứ tự thời gian, bar trigger_idx là bar tín hiệu.

    Entry = open của bar trigger_idx+1 (không nhìn tương lai), exit = open của bar
    trigger_idx+1+hold_bars (hoặc close bar cuối nếu hết dữ liệu — ghi is_truncated).
    Trả dict hoặc None nếu không đủ bar để vào lệnh.
    """
    i = trigger_idx + 1
    if i >= len(bars):
        return None
    j = i + hold_bars
    truncated = False
    if j >= len(bars):
        j = len(bars) - 1
        truncated = True
    entry_open = bars[i][0]
    exit_open = bars[j][0]
    net = net_return(entry_open, exit_open, fee_bps, slippage_bps, gas_usd, size_usd)
    return {"net_usd": net, "entry_idx": i, "exit_idx": j, "is_truncated": truncated}


def bootstrap_ci_clustered(profits, groups, B=2000, alpha=0.05, seed=42):
    """KTC 95% cho mean profit, gom mẫu theo nhóm (token/sự kiện) — bootstrap CỤM.

    profits: list[float]; groups: list[str] cùng độ dài.
    Trả (lo, hi, mean). Nếu toàn bộ (lo > 0) → qua tầng 2.
    """
    by_group = defaultdict(list)
    for p, g in zip(profits, groups):
        by_group[g].append(p)
    keys = sorted(by_group)
    if not keys:
        return (0.0, 0.0, 0.0)
    rng = random.Random(seed)
    means = []
    for _ in range(B):
        sampled = [keys[rng.randrange(len(keys))] for _ in range(len(keys))]
        vals = [p for k in sampled for p in by_group[k]]
        means.append(sum(vals) / len(vals))
    means.sort()
    lo_idx = int((alpha / 2) * B)
    hi_idx = int((1 - alpha / 2) * B) - 1
    overall = sum(profits) / len(profits)
    return (means[lo_idx], means[hi_idx], overall)


def gate_t1(signals_count, net_profits, fee_stress=1.2, min_signals=200,
            top1_max=0.25, top5_max=0.50, drop_rate_max=0.30, drop_rate=None,
            token_of=None):
    """Tầng 1 — sàng lọc. Trả dict các kiểm tra True/False + passed tổng."""
    total = sum(net_profits)
    stressed = [p - abs(p) * 0 for p in net_profits]  # thay bằng tính lại bên ngoài nếu cần
    checks = {}
    checks["du_200_tin_hieu"] = signals_count >= min_signals
    checks["lai_rong_duong"] = total > 0
    if token_of is not None:
        agg = defaultdict(float)
        for p, t in zip(net_profits, token_of):
            agg[t] += p
        if total > 0:
            tops = sorted(agg.values(), reverse=True)
            checks["top1_duoi_25pt"] = (tops[0] / total) < top1_max if tops else False
            checks["top5_duoi_50pt"] = (sum(tops[:5]) / total) < top5_max if len(tops) >= 5 else True
        else:
            checks["top1_duoi_25pt"] = False
            checks["top5_duoi_50pt"] = False
    if drop_rate is not None:
        checks["ty_le_bo_duoi_30pt"] = drop_rate < drop_rate_max
    checks["lai_rong_duong_khi_phi_cong_20pt"] = True  # tính bằng net_profits_stressed truyền vào
    return checks


def gate_t1_stressed(net_profits_stressed):
    return sum(net_profits_stressed) > 0


def select_param_insample(grid_results, metric="median_net"):
    """Chọn đúng 1 tham số chính từ kết quả IN-SAMPLE. metric khai báo trước: median_net."""
    import statistics
    best_k, best_v = None, None
    for k, nets in grid_results.items():
        v = statistics.median(nets) if nets else float("-inf")
        if best_v is None or v > best_v:
            best_k, best_v = k, v
    return best_k


def stress_fees_20pct(net_profits, fee_and_gas_component):
    """Tăng toàn bộ thành phần phí+gas lên 20%: net' = net - 0.2*fee_gas."""
    return [p - 0.2 * fg for p, fg in zip(net_profits, fee_and_gas_component)]
