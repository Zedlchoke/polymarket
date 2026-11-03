#!/usr/bin/env python3
"""Test bộ máy backtest trên DỮ LIỆU GIẢ có đáp án biết trước (chặng 4 loop 10h).

Không dùng dữ liệu thật. Mỗi test khai báo:input giả → kết quả ĐÚNG biết trước → so sánh.
Kết quả: data/w1_base/synth_test_report.md
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt_core as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "w1_base", "synth_test_report.md")
results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


# ---------- T1: số học phí/lãi ----------
# entry=100, exit=110, slip 50bps mỗi chiều, fee 30bps mỗi chiều (2 chiều), gas 1, size 100
# entry_eff=100.5, exit_eff=109.45 → gross = 100*(109.45/100.5-1)=8.906
# fees = 100*0.003*2 = 0.6 → net = 8.906-0.6-1 = 7.306
n = bt.net_return(100, 110, fee_bps=30, slippage_bps=50, gas_usd=1.0, size_usd=100.0)
check("so_hoc_phi_bang_tay", abs(n - 7.3055) < 0.01, f"net={n:.4f} vs 7.3055")

# exit thấp hơn entry nhưng cao hơn điểm hòa: kiểm tra hướng đúng
n2 = bt.net_return(100, 101.3, fee_bps=30, slippage_bps=50, gas_usd=0.0, size_usd=100.0)
check("hoa_vong_tinh_dung", n2 < 0, f"net={n2:.4f} (điểm hòa ~101.6)")

# ---------- T2: chống nhìn tương lai ----------
# bar0 = trigger (close 100). bar1 open = 100 (entry). bar sau tăng vọt.
bars = [(90, 100), (100, 100), (100, 50), (200, 200)]
r = bt.simulate_signal(bars, hold_bars=2, trigger_idx=0)
# entry ở open bar1=100; exit ở open bar3=200 (không phải close bar2=50)
check("entry_open_bar_sau_khong_close_bar_hien_tai", r["entry_idx"] == 1)
check("exit_open_bar_dung_luat", r["exit_idx"] == 3 and abs(r["net_usd"] - bt.net_return(100, 200, gas_usd=0.0)) < 1e-9)

# hết dữ liệu giữa chừng → exit bar cuối + cờ truncated (không bị bỏ âm ẩn)
bars2 = [(90, 100), (100, 100), (100, 10)]
r2 = bt.simulate_signal(bars2, hold_bars=5, trigger_idx=0)
check("thieu_du_lieu_danh_dau_truncated", r2["is_truncated"] and r2["exit_idx"] == 2)

# không đủ bar vào lệnh → None (đếm vào tỷ lệ bỏ, không thành tín hiệu ảo)
check("khong_du_bar_khong_tao_tin_hieu", bt.simulate_signal([(90, 100)], 1, trigger_idx=0) is None)

# ---------- T3: bootstrap gom theo token ----------
# 1 token (A) lãi khổng lồ, 19 token thua nhỏ → naive CI dương, CI gom theo token phải 含 0
profits, groups = [], []
for i in range(100):
    profits.append(50.0)
    groups.append("A")
for t in "BCDEFGHIJKLMNOPQRST":
    for i in range(100):
        profits.append(-0.5)
        groups.append(t)
lo, hi, mean = bt.bootstrap_ci_clustered(profits, groups, B=1500)
check("bootstrap_clu_khong_bi_lua_boi_1_token", lo <= 0 <= hi, f"CI=({lo:.3f},{hi:.3f})")

# trường hợp thật sự đều: mọi token cùng lãi nhỏ → CI hoàn toàn trên 0
profits2, groups2 = [], []
for t in [f"T{i}" for i in range(20)]:
    for i in range(50):
        profits2.append(2.0)
        groups2.append(t)
lo2, hi2, _ = bt.bootstrap_ci_clustered(profits2, groups2, B=1500)
check("bootstrap_clu_qua_khi_that_su_deu", lo2 > 0, f"CI=({lo2:.3f},{hi2:.3f})")

# deterministic theo seed
a = bt.bootstrap_ci_clustered(profits2, groups2, B=300, seed=7)
b = bt.bootstrap_ci_clustered(profits2, groups2, B=300, seed=7)
check("bootstrap_deterministic_theo_seed", a == b)

# ---------- T4: cổng tầng 1 ----------
c = bt.gate_t1(signals_count=250,
               net_profits=[1.0] * 250,
               token_of=[f"t{i % 20}" for i in range(250)],
               drop_rate=0.1)
ok = c["du_200_tin_hieu"] and c["lai_rong_duong"] and c["top1_duoi_25pt"] and c["ty_le_bo_duoi_30pt"]
check("cong_t1_dung_khi_day_du", ok)

c2 = bt.gate_t1(signals_count=150, net_profits=[1.0] * 150,
                token_of=[f"t{i}" for i in range(150)], drop_rate=0.1)
check("cong_t1_tu_choi_khi_thieu_tin_hieu", not c2["du_200_tin_hieu"])

# top1 chiếm >25% tổng lãi → trượt
nets = [100.0] + [0.4] * 249  # tổng 199.6, top1 = 50.2%
toks = ["BIG"] + [f"t{i}" for i in range(249)]
c3 = bt.gate_t1(250, nets, token_of=toks, drop_rate=0.05)
check("cong_t1_bat_tap_trung_top1", not c3["top1_duoi_25pt"])

# stress phí +20%: net' = net - 0.2*(phí+gas)
nets4 = bt.stress_fees_20pct([7.3], [0.6 + 1.0])
check("stress_phi_20pt_dung_cong_thuc", abs(nets4[0] - (7.3 - 0.32)) < 1e-9, f"{nets4[0]:.4f}")
check("cong_t1_tu_choi_khi_stress_am", not bt.gate_t1_stressed([-1.0]))

# ---------- T5: chọn 1 tham số chính trên in-sample ----------
grid = {1: [1.0] * 50, 6: [3.0] * 50, 24: [0.5] * 50}
check("chon_tham_so_median_insample", bt.select_param_insample(grid) == 6)

# ---------- ghi báo cáo ----------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
n_pass = sum(1 for _, okk, _ in results if okk)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("# Test bộ máy backtest trên dữ liệu giả — loop 10h 2026-11-02\n\n")
    f.write(f"Kết quả: **{n_pass}/{len(results)} PASS**\n\n")
    f.write("| Test | Kết quả | Chi tiết |\n|---|---|---|\n")
    for name, okk, detail in results:
        f.write(f"| {name} | {'PASS' if okk else '**FAIL**'} | {detail} |\n")
    f.write("\nBộ máy chưa từng chạm dữ liệu thật. Backtest thật chỉ chạy sau khi spec đóng băng + có sha256 + lệnh GO.\n")
print(f"\n{n_pass}/{len(results)} PASS — báo cáo: {OUT}")
sys.exit(0 if n_pass == len(results) else 1)
