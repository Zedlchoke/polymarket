# -*- coding: utf-8 -*-
"""Bộ test DỮ LIỆU GIẢ có đáp án biết trước — theo yêu cầu Việc 2 của prompt xây.
KHÔNG gọi API thật. Test fail -> sửa code, KHÔNG sửa đáp án mong đợi.
Mỗi test ghi (tên, dữ liệu vào, đáp án mong đợi, kết quả thật, pass/fail) vào test_report.json."""
import json
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config, data_loader, killgate, kopt, ledger, overlap, report, selection, sports_filter  # noqa: E402

RESULTS = []


def rec(name, input_desc, expected, actual, tol=None):
    if tol is None:
        ok = expected == actual
    else:
        ok = (expected is actual is None) or (
            expected is not None and actual is not None
            and abs(float(expected) - float(actual)) <= tol)
    RESULTS.append({"test": name, "input": input_desc,
                    "expected": str(expected), "actual": str(actual),
                    "pass": bool(ok)})
    if not ok:
        raise AssertionError("%s: mong đợi %r, thật %r" % (name, expected, actual))


R6 = 1e-6


class T01Fee(unittest.TestCase):
    def test_fee_050_r003(self):
        # yêu cầu prompt: phí giá 0,50 rate 0,03 = 200 cp × 0,03 × 0,50 × 0,50
        rec("phí @0.50 rate 0.03", "shares=200, price=0.50, rate=0.03",
            1.50, round(ledger.entry_fee(200, 0.50, 0.03), 10), tol=R6)

    def test_fee_050_r005(self):
        rec("phí @0.50 rate 0.05", "shares=200, price=0.50, rate=0.05",
            2.50, ledger.entry_fee(200, 0.50, 0.05), tol=R6)

    def test_fee_via_copy_price(self):
        # giá copy 0,52 → shares=100/0,52; phí = shares×0,03×0,52×0,48 = 100×0,03×0,48
        px = ledger.copy_price(0.50, None)
        sh = ledger.shares_for(px)
        rec("phí theo giá copy 0.52", "stake 100, giá copy 0.52, rate 0.03",
            1.44, ledger.entry_fee(sh, px, 0.03), tol=R6)


class T02Resolution(unittest.TestCase):
    """Yêu cầu prompt: chốt 0 / 0,5 / 1; hòa = cổ phần × 0,5, KHÔNG trả lại stake."""

    def setUp(self):
        self.px = ledger.copy_price(0.50, None)   # 0.52
        self.sh = ledger.shares_for(self.px)      # 192.307692...
        self.fee = ledger.entry_fee(self.sh, self.px, 0.03)  # 1.44

    def test_win(self):
        expected = 100 / 0.52 - 100 - 1.44
        rec("lãi thắng res=1", "shares=100/0.52, res=1, fee=1.44",
            round(expected, 6), round(ledger.signal_pnl(self.sh, 1.0, self.fee), 6), tol=R6)

    def test_lose(self):
        rec("lãi thua res=0", "shares=100/0.52, res=0, fee=1.44",
            -101.44, ledger.signal_pnl(self.sh, 0.0, self.fee), tol=R6)

    def test_tie_not_stake_back(self):
        tie = ledger.signal_pnl(self.sh, 0.5, self.fee)
        stake_back = -self.fee  # sai: "trả lại stake" = chỉ mất phí
        rec("hòa 0.5 = cp×0.5−100−phí", "shares=100/0.52, res=0.5, fee=1.44",
            round(100 / 0.52 * 0.5 - 100 - 1.44, 6), round(tie, 6), tol=R6)
        self.assertTrue(abs(tie - stake_back) > 1.0,
                        "hòa phải là cp×0.5−100−phí, không phải trả lại stake")

    def test_resolve_price_from_payouts(self):
        rec("giá chốt từ payouts", "payouts=[1000000,0], idx=0",
            1.0, ledger.resolve_price([1000000, 0], 0)[1])
        rec("giá chốt hòa payouts", "payouts=[500000,0], idx=0",
            0.5, ledger.resolve_price([500000, 0], 0)[1])
        rec("trạng thái ok kèm giá", "payouts=[1000000,0], idx=0",
            ("ok", 1.0), ledger.resolve_price([1000000, 0], 0))

    def test_resolution_decision_ok(self):
        st, price = ledger.resolution_decision(
            {"payouts": [1000000, 0]}, {"outcomePrices": ["1", "0"]})
        rec("nguồn chốt khớp", "payouts=[1000000,0] vs outcomePrices=['1','0']",
            "ok", st)

    def test_resolution_decision_mismatch_stops(self):
        st, _ = ledger.resolution_decision(
            {"payouts": [0, 1000000]}, {"outcomePrices": ["1", "0"]})
        rec("nguồn chốt lệch -> dừng", "payouts=[0,1000000] vs gamma ['1','0']",
            "mismatch", st)
        st2, _ = ledger.resolution_decision({"payouts": [700000, 0]}, None)
        rec("payouts 0.7 bất thường -> dừng", "payouts=[700000,0]",
            "mismatch", st2)

    def test_resolution_decision_missing(self):
        st, _ = ledger.resolution_decision(None, {"umaResolutionStatus": "resolved"})
        rec("thiếu resolutions -> missing", "res_row=None",
            "missing", st)

    def test_999_unlabeled(self):
        rec("outcome_index 999 -> thiếu nhãn", "payouts=[1000000,0], idx=999",
            "thiếu_nhãn_999", ledger.resolve_price([1000000, 0], 999)[0])
        t = report.table_unlabeled_999(1000, 60)
        rec("báo động 999 trên 5%", "60/1000 dòng",
            True, t["alert"])
        t2 = report.table_unlabeled_999(1000, 50)
        rec("không báo động khi =5%", "50/1000 dòng",
            False, t2["alert"])


class T03SlidingWindow(unittest.TestCase):
    """Yêu cầu prompt: ví thứ k vào trong 24h từ ví đầu -> kích hoạt; sau 24h -> không."""

    def _ev(self, group, ts, cash, price=0.5):
        return {"group": group, "ts": ts, "cash": cash, "price": price}

    def test_k2_within_24h(self):
        evs = [self._ev("A", 1000, 300), self._ev("B", 1000 + 86399, 250)]
        tr = overlap.detect_side(evs)
        rec("k=2 trong 24h kích hoạt", "A@t0 ròng300, B@t0+86399 ròng250 (tổng 550)",
            True, 2 in tr)

    def test_k2_after_24h_no_trigger(self):
        evs = [self._ev("A", 1000, 300), self._ev("B", 1000 + 86401, 250)]
        tr = overlap.detect_side(evs)
        rec("k=2 sau 24h KHÔNG kích hoạt", "A@t0, B@t0+86401",
            False, 2 in tr)

    def test_sell_net_excluded(self):
        evs = [self._ev("A", 1000, 300), {"group": "A", "ts": 2000, "cash": -300, "price": 0.5},
               self._ev("B", 3000, 600)]
        tr = overlap.detect_side(evs)
        rec("A mua 300 bán 300 -> không đếm", "A ròng=0, B ròng 600",
            False, 2 in tr)

    def test_k1_needs_total_500(self):
        tr = overlap.detect_side([self._ev("A", 1000, 300)])
        rec("k=1 ròng 300 (tổng<500) không kích hoạt", "A ròng 300",
            False, 1 in tr)
        tr2 = overlap.detect_side([self._ev("A", 1000, 300), self._ev("A", 1500, 300)])
        rec("k=1 ròng 600 (tổng>=500) kích hoạt", "A 300+300",
            True, 1 in tr2)

    def test_opposite_side_buyer_excluded(self):
        evs = [self._ev("A", 1000, 300), self._ev("B", 2000, 250)]
        tr = overlap.detect_side(evs, opposite_buyers={"B"})
        rec("B mua cửa ngược -> không đếm", "A ròng300, B ròng250 nhưng B mua 2 chiều",
            False, 2 in tr)

    def test_total_net_500_required(self):
        evs = [self._ev("A", 1000, 150), self._ev("B", 2000, 150)]  # tổng 300 < 500
        tr = overlap.detect_side(evs)
        rec("tổng ròng các nhóm <500 -> không kích hoạt", "A 150 + B 150",
            False, 2 in tr)


class T04Grouping(unittest.TestCase):
    """Yêu cầu prompt: trùng/số-lệnh-ít-hơn + ngưỡng >=20 lệnh trùng."""

    @staticmethod
    def _mk(i, cond="c", tok="tok"):
        return {"condition_id": "%s%d" % (cond, i % 10), "token_id": "%s%d" % (tok, i % 10),
                "timestamp": i * 60, "side": "BUY", "usdc_size": 120.0, "price": 0.5}

    def test_merge_high_overlap(self):
        X = [self._mk(i) for i in range(100)]
        Y = [self._mk(i) for i in range(55)] + [self._mk(1000 + i, "z", "zt") for i in range(5)]
        shared, ratio = selection.pair_overlap(X, Y)
        rec("trùng 55, tỉ lệ 55/60", "X 100 lệnh, Y 60 lệnh, 55 trùng",
            (55, round(55 / 60, 6)), (shared, round(ratio, 6)))
        rec("gộp khi đủ 50% + >=20", "shared=55",
            True, selection.should_merge(X, Y))

    def test_no_merge_below_20(self):
        X = [self._mk(i) for i in range(100)]
        Z = [self._mk(i) for i in range(15)] + [self._mk(2000 + i, "z", "zt") for i in range(50)]
        rec("trùng 15 <20 -> không gộp", "shared=15",
            False, selection.should_merge(X, Z))

    def test_no_merge_ratio_below_half(self):
        # Q3.10: tỉ lệ = trùng / SỐ LỆNH ÍT HƠN. X=100, W=200 (70 trùng) -> 70/100=0.70 -> GỘP.
        # Muốn tỉ lệ <0.5 phải trùng <50: W2=40 trùng + 160 lệnh riêng -> 40/100=0.40 -> không gộp.
        X = [self._mk(i) for i in range(100)]
        W = [self._mk(i) for i in range(70)] + [self._mk(3000 + i, "w", "wt") for i in range(130)]
        shared, ratio = selection.pair_overlap(X, W)
        rec("trùng 70, ít hơn là 100 -> tỉ lệ 0.70 -> GỘP (đúng luật chia số lệnh ít hơn)",
            "shared=70, min(100,200)=100",
            (70, 0.70), (shared, round(ratio, 6)))
        W2 = [self._mk(i) for i in range(40)] + [self._mk(4000 + i, "v", "vt") for i in range(160)]
        shared2, ratio2 = selection.pair_overlap(X, W2)
        rec("trùng 40/100=0.40 <0.5 -> không gộp", "shared=40",
            (False, 0.40), (selection.should_merge(X, W2), round(ratio2, 6)))

    def test_merge_groups_greedy(self):
        cand = [
            {"address": "0xB", "stats": {"hold_roi": 0.10, "n_markets": 50, "n_trades": 60,
                                         "hold_pnl": 1, "cash_volume": 1, "max_market_pnl_share": 0.1},
             "trades": [self._mk(i) for i in range(55)]},
            {"address": "0xA", "stats": {"hold_roi": 0.12, "n_markets": 50, "n_trades": 100,
                                         "hold_pnl": 1, "cash_volume": 1, "max_market_pnl_share": 0.1},
             "trades": [self._mk(i) for i in range(100)]},
            {"address": "0xC", "stats": {"hold_roi": 0.09, "n_markets": 40, "n_trades": 40,
                                         "hold_pnl": 1, "cash_volume": 1, "max_market_pnl_share": 0.1},
             "trades": [self._mk(5000 + i, "q", "qt") for i in range(40)]},
        ]
        chosen, info = selection.select_groups(cand, n_target=2)
        rec("số nhóm = 2 (A+B gộp 1 nhóm, C riêng)", "3 ứng viên, A~B trùng 55",
            2, len(chosen))
        rec("nhóm đứng đầu chứa {0xA, 0xB} (roi.best = 0xA)", "",
            {"0xA", "0xB"}, {m["address"] for m in chosen[0]["members"]})
        rec("nhóm thứ hai là 0xC riêng", "",
            {"0xC"}, {m["address"] for m in chosen[1]["members"]})


class T05SelectionGates(unittest.TestCase):
    BASE = {"n_trades": 200, "n_markets": 30, "hold_pnl": 2000.0, "hold_cash": 20000.0,
            "hold_roi": 0.10, "max_market_pnl_share": 0.3, "cash_volume": 80000.0,
            "per_market_pnl": {}}

    def _pass(self, stats=None, both=0.05, active=5, realized=True):
        st = dict(self.BASE)
        st.update(stats or {})
        return selection.passes_gates(st, both, active, realized)

    def test_all_pass(self):
        ok, fails = self._pass()
        rec("ví đạt hết 10 cửa", "vol 80k, 200 lệnh, 30 thị trường, roi 0.10",
            True, ok)

    def test_each_gate(self):
        cases = [
            ("vol 49999 trượt cổng khối lượng", {"cash_volume": 49999.0}, "vol"),
            ("79 lệnh trượt cổng lệnh (D5=80)", {"n_trades": 79}, "trades"),
            ("19 thị trường trượt cổng thị trường", {"n_markets": 19}, "markets"),
            ("hold_roi âm trượt", {"hold_roi": -0.01}, "hold_roi"),
            ("1 thị trường chiếm 60% lãi trượt", {"max_market_pnl_share": 0.6}, "concentration"),
        ]
        for name, patch, gate in cases:
            ok, fails = self._pass(patch)
            rec(name, str(patch), (False, gate), (ok, fails[0] if fails else None))
        ok, fails = self._pass(both=0.4)
        rec("giữ 2 cửa 40% thị trường -> loại", "both=0.4",
            (False, "both_sides"), (ok, fails[0]))
        ok, fails = self._pass(active=2)
        rec("chỉ 2 lệnh trong 14 ngày cuối -> trượt cổng còn chơi", "active=2",
            (False, "active"), (ok, fails[0]))
        ok, fails = self._pass(stats={"n_trades": 2500, "hold_pnl": 40000.0,
                                      "cash_volume": 5_000_000.0, "hold_cash": 5_000_000.0,
                                      "hold_roi": 40000 / 5_000_000})
        rec("bot: >2000 lệnh và lãi/khối lượng<1% -> loại", "2500 lệnh, 0.8%",
            (False, "bot"), (ok, fails[-1]))

    def test_hold_pnl_and_ranking(self):
        t = {"usdc_size": 100.0, "price": 0.5, "side": "BUY",
             "condition_id": "c1", "token_id": "t1", "timestamp": 10}
        rec("hold_pnl thắng fee 0", "100 USD @0.5, res 1.0",
            100.0, selection.hold_pnl(t, 1.0, 0.0), tol=R6)
        rec("hold_pnl hòa fee 0", "res 0.5",
            0.0, selection.hold_pnl(t, 0.5, 0.0), tol=R6)
        rec("hold_pnl thắng fee 0.03", "res 1.0",
            98.5, selection.hold_pnl(t, 1.0, 0.03), tol=R6)
        a = {"address": "0xA", "stats": {**self.BASE, "hold_roi": 0.10, "n_markets": 40, "n_trades": 300}}
        b = {"address": "0xB", "stats": {**self.BASE, "hold_roi": 0.10, "n_markets": 50, "n_trades": 200}}
        c = {"address": "0xC", "stats": {**self.BASE, "hold_roi": 0.10, "n_markets": 50, "n_trades": 200}}
        order = [w["address"] for w in sorted([c, a, b], key=selection.rank_key)]
        rec("hòa ROI: nhiều thị trường trước, rồi nhiều lệnh, rồi chữ cái",
            "A roi=10%/40tt/300l, B roi=10%/50tt/200l, C=B nhưng địa chỉ sau",
            ["0xB", "0xC", "0xA"], order)

    def test_both_sides_ratio(self):
        mk = lambda c, tok, s: {"condition_id": c, "token_id": tok, "side": s,
                                "usdc_size": 100.0, "price": 0.5, "timestamp": 1,
                                "type": "TRADE"}
        both = [mk("c1", "YES", "BUY"), mk("c1", "NO", "BUY")]
        rec("mua 2 cửa cùng lúc -> tỉ lệ 1.0", "1 thị trường giữ 2 cửa",
            1.0, selection.both_sides_ratio(both))
        one = [mk("c1", "YES", "BUY"), mk("c2", "YES", "BUY")]
        rec("chỉ 1 cửa -> tỉ lệ 0", "",
            0.0, selection.both_sides_ratio(one))
        reward = [mk("c1", "YES", "BUY"),
                  {"condition_id": "c1", "token_id": "YES", "side": "BUY",
                   "usdc_size": 100.0, "price": 0.5, "timestamp": 2, "type": "REWARD"}]
        rec("REWARD không tính vào chuỗi vị thế", "",
            0.0, selection.both_sides_ratio(reward))


class T06KOptimizer(unittest.TestCase):
    """Yêu cầu prompt: ROI thô cao nhất nhưng sai số lớn thì KHÔNG được chọn
    nếu Điểm không cao nhất; và phải hơn k=1 ít nhất 3 điểm %."""

    @staticmethod
    def _mk(mean, std, n):
        # danh sách pnl có đúng mean/std mẫu (chuẩn bị tay, không ngẫu nhiên)
        half = std / 2.0
        rows = []
        for i in range(n):
            v = mean + (half if i % 2 == 0 else -half)
            rows.append(v)
        return rows

    def test_high_raw_roi_big_error_not_chosen(self):
        k1 = [3.0] * 150                       # roi 0.03
        k2 = self._mk(10.0, 60.0, 150)         # roi 0.10, std 60 -> se lớn
        k3 = self._mk(7.0, 4.0, 200)           # roi 0.07, std nhỏ
        k_star, why = kopt.select_k({1: k1, 2: k2, 3: k3})
        m = {k: kopt.k_metrics(v) for k, v in ((1, k1), (2, k2), (3, k3))}
        rec("k2 ROI thô cao nhất nhưng Điểm thấp hơn k3 -> chọn k3",
            "k1 roi .03 | k2 roi .10 se=%.4f | k3 roi .07 se=%.4f" % (m[2]["se"], m[3]["se"]),
            3, k_star)

    def test_edge_vs_k1_3pp(self):
        k1 = [3.0] * 150
        k2 = self._mk(5.5, 0.0, 150)   # roi 0.055 < 0.03+0.03 -> không đủ
        k3 = self._mk(8.0, 45.0, 200)  # roi 0.08 đủ diem dương nhưng nhỏ
        k_star, _ = kopt.select_k({1: k1, 2: k2, 3: k3})
        rec("roi 0.055 không hơn k1 đủ 3đ% -> bỏ qua dù Điểm cao",
            "k2 diem=0.055 (cao nhất) nhưng không đủ điều kiện",
            3, k_star)

    def test_none_eligible(self):
        k1 = [10.0] * 150                      # roi 0.10
        k2 = self._mk(5.0, 0.0, 150)           # roi 0.05 < 0.13
        k_star, why = kopt.select_k({1: k1, 2: k2})
        rec("không k nào hơn k1 3đ% -> không chọn k*", "",
            (None, "không_k_nào_thỏa_cả_ba_điều_kiện"), (k_star, why))

    def test_min_100_signals(self):
        k1 = [3.0] * 150
        k2 = [10.0] * 99                       # thiếu mẫu
        k3 = self._mk(8.0, 1.0, 120)
        k_star, _ = kopt.select_k({1: k1, 2: k2, 3: k3})
        rec("k chỉ 99 tín hiệu (<100) không được xét", "",
            3, k_star)

    def test_tie_diem_choose_more_signals(self):
        k1 = [3.0] * 150
        k3 = self._mk(7.0, 2.0, 200)   # diem ≈ 0.07 − 0.02/√200=0.06859
        k4 = self._mk(7.0, 2.05, 300)  # diem ≈ 0.07 − 0.0205/√300=0.06882
        d3, d4 = kopt.k_metrics(k3)["diem"], kopt.k_metrics(k4)["diem"]
        self.assertLess(abs(d3 - d4), config.K_TIE_EPS)
        k_star, why = kopt.select_k({1: k1, 3: k3, 4: k4})
        rec("chênh Điểm <0.02 -> chọn k nhiều tín hiệu hơn", "diem3=%.5f diem4=%.5f" % (d3, d4),
            (4, "hòa_điểm_dưới_0.02_chọn_k_nhiều_tín_hiệu_hơn"), (k_star, why))


class T07KillGate(unittest.TestCase):
    """Yêu cầu prompt: top1 >25% hay top5 >50% -> không qua, dù tổng lãi dương."""

    def _m(self, pnls):
        n = len(pnls)
        total = sum(pnls)
        return {"in_n": 150, "out_n": n, "in_pnl": 500.0, "in_roi": 0.06,
                "out_pnl": total, "out_pnl_sens005": total * 0.5,
                "out_roi": total / (100.0 * n), "k1_out_roi": 0.01,
                "k1_in_roi": 0.01, "pnls_out": pnls,
                "skip_rate": 0.10, "unresolved_rate": 0.02}

    def test_concentration_fails(self):
        pnls = [10.0] * 100 + [400.0]   # tổng 1400; top1=28.6%>25%; top5=31.4%<50%
        t1 = killgate.tier1(self._m(pnls))
        rec("top1 28.6% > 25% -> cổng 7 trượt dù tổng dương và ROI 13.9%",
            "100 tín hiệu +10 và 1 tín hiệu +400 (đủ 101 tín hiệu)",
            (False, ["7_tập_trung"]), (t1["pass"], t1["fails"]))

    def test_healthy_pass_tier1(self):
        pnls = [10.0] * 150                    # top1 = 10/1500 = 0.7%
        t1 = killgate.tier1(self._m(pnls))
        rec("phân bố đều -> qua tầng 1", "150 tín hiệu +10",
            True, t1["pass"])

    def test_ex10_negative_fails(self):
        pnls = [1000.0] + [(-2.0)] * 100 + [70.0] * 4
        # tổng 1080, ROI 10.3% (>5%); top10=1280 > tổng -> bỏ top-10 lãi âm; top1 92.6%
        t1 = killgate.tier1(self._m(pnls))
        rec("bỏ top-10 mà tổng lãi còn lại âm -> trượt cổng 7 (ROI vẫn >5%)", "",
            (False, ["7_tập_trung"]), (t1["pass"], t1["fails"]))

    def test_bootstrap_all_positive(self):
        sig = [{"event_id": "e%02d" % e, "pnl": 20.0} for e in range(30) for _ in range(5)]
        passed, lo, hi, roi = killgate.tier2_bootstrap(sig)
        rec("bootstrap gom sự kiện: tất cả dương -> CI trên 0",
            "30 sự kiện × 5 tín hiệu +20",
            True, passed)
        self.assertGreater(lo, 0.0)

    def test_bootstrap_mixed_contains_zero(self):
        sig = ([{"event_id": "eA%02d" % e, "pnl": 100.0} for e in range(10) for _ in range(5)]
               + [{"event_id": "eB%02d" % e, "pnl": -100.0} for e in range(10) for _ in range(5)])
        passed, lo, hi, roi = killgate.tier2_bootstrap(sig)
        rec("nửa sự kiện lỗ -> CI chứa 0 -> không qua tầng 2", "",
            False, passed)

    def test_verdict_flow(self):
        rec("thiếu tầng 1 -> CHẾT", "", "CHẾT", killgate.verdict(False, True)[0])
        rec("qua T1 thiếu T2 -> CHƯA ĐỦ BẰNG CHỨNG", "",
            "CHƯA ĐỦ BẰNG CHỨNG", killgate.verdict(True, False)[0])
        rec("qua cả hai -> SỐNG (backtest)", "", "SỐNG_ở_backtest",
            killgate.verdict(True, True)[0])

    def test_tier3_flags_only(self):
        flags = killgate.tier3_flags({"World Cup": 800.0, "khác": 100.0},
                                     {"soccer": 900.0}, 100.0, True)
        rec("D1: giải lớn 88.9% -> cờ bật, KHÔNG lật verdict", "",
            True, flags["cờ_giải_lớn_trên_50%"])


class T08LedgerMisc(unittest.TestCase):
    def test_vwap(self):
        fills = [{"ts": 0, "price": 0.5, "cash": 60.0},
                 {"ts": 60, "price": 0.6, "cash": 40.0}]
        v, used = ledger.vwap_fill(fills)
        exp = 100.0 / (60 / 0.5 + 40 / 0.6)
        rec("VWAP đủ 100 USD từ 2 lệnh", "60@0.5 + 40@0.6",
            round(exp, 10), round(v, 10), tol=R6)

    def test_vwap_insufficient(self):
        fills = [{"ts": 0, "price": 0.5, "cash": 60.0}]
        v, why = ledger.vwap_fill(fills)
        rec("không đủ 100 USD trong 60 phút -> bỏ (thiếu độ sâu)", "",
            "thiếu_độ_sâu_60_phút", why)

    def test_vwap_outside_window(self):
        fills = [{"ts": 0, "price": 0.5, "cash": 60.0},
                 {"ts": 3601, "price": 0.1, "cash": 1000.0}]
        v, why = ledger.vwap_fill(fills)
        rec("lệnh thứ 2 sau 60 phút không dùng", "",
            "thiếu_độ_sâu_60_phút", why)

    def test_penalty(self):
        rec("phạt mặc định 0.02 (backtest không spread)", "spread=None",
            0.02, ledger.late_penalty(None))
        rec("spread 0.005 -> phạt 0.02", "", 0.02, ledger.late_penalty(0.005))
        rec("spread 0.07 -> phạt 0.07", "", 0.07, ledger.late_penalty(0.07))

    def test_sensitivity_replace_not_add(self):
        px02 = ledger.copy_price(0.50, None)          # 0.52
        px05 = ledger.copy_price(0.50, 0.05)          # 0.55 (THAY THẾ, không 0.57)
        rec("phạt nhạy cảm THAY THẾ: 0.50+0.05=0.55 (không phải 0.57)", "",
            0.55, px05, tol=R6)
        sh = ledger.shares_for(px05)
        fee = ledger.entry_fee(sh, px05, 0.03)
        rec("phí tính lại theo giá mới 0.55", "",
            round(100 * 0.03 * 0.45, 6), round(fee, 6), tol=R6)

    def test_open_cap_10(self):
        sigs = [{"id": i, "trigger_ts": 100 + i, "close_ts": 10000} for i in range(11)]
        sigs.append({"id": 99, "trigger_ts": 10001, "close_ts": 20000})
        acc, skip = ledger.schedule_open_cap(sigs)
        rec("tín hiệu 11 (id=10) bị bỏ vì đầy 10 lệnh mở; tín hiệu id=99 sau khi đóng được nhận",
            "10 lệnh mở tới t=10000, tín hiệu 11 t=110, tín hiệu 99 t=10001",
            ([10], [99]), (skip, acc[-1:] and [acc[-1]]))

    def test_grace_14_days(self):
        seg_end = 1000
        sigs = [{"id": "ok", "close_ts": seg_end + 13 * 86400},
                {"id": "muộn", "close_ts": seg_end + 15 * 86400},
                {"id": "chưa", "close_ts": None}]
        closed, unresolved = ledger.grace_status(sigs, seg_end)
        rec("ân hạn 14 ngày: 13 ngày -> đã chốt; 15 ngày/chưa -> chưa chốt", "",
            (["ok"], ["muộn", "chưa"]), (closed, unresolved))

    def test_fee_by_date(self):
        rec("feeSchedule có sẵn -> dùng rate thị trường", "rate 0.05, ts bất kỳ",
            (0.05, "feeSchedule"),
            ledger.fee_rate({"feeSchedule": {"rate": 0.05}}, 1770681600))
        rec("10-02-2026 -> phí 0 (bảng dự phòng)", "",
            (0.0, "bảng_ngày_dự_phòng"), ledger.fee_rate({}, 1770681600))
        rec("10-05-2026 -> phí 0.03", "",
            (0.03, "bảng_ngày_dự_phòng"), ledger.fee_rate({}, 1778371200))
        rec("10-08-2026 -> phí 0.05", "",
            (0.05, "bảng_ngày_dự_phòng"), ledger.fee_rate({}, 1786320000))
        rec("05-07-2026 khoảng trống -> FEE_MISSING, không đoán (V2/Sửa 3 đổi mã)", "",
            (None, "FEE_MISSING"), ledger.fee_rate({}, 1783209600))


class T09Sports(unittest.TestCase):
    def test_law_and_fallback(self):
        m = {"tags": [{"label": "Sports"}, {"label": "NBA"}]}
        rec("tag 'Sports' -> thể thao (luật đã duyệt)", "",
            (True, "tag"), sports_filter.is_sports(m))
        m2 = {"tags": [], "sportsMarketType": "moneyline", "gameStartTime": "2026-11-02 19:00:00+00"}
        rec("tags rỗng + sportsMarketType -> dự phòng coi là thể thao (§20.1 ĐỀ XUẤT)", "",
            (True, "dự_phòng_smt"), sports_filter.is_sports(m2))
        m3 = {"tags": [], "gameStartTime": "2026-06-01 00:00:00+00"}
        rec("tags rỗng + chỉ gameStartTime (deadline phi thể thao) -> KHÔNG thể thao", "",
            (False, "dự_phòng_không_xác_định"), sports_filter.is_sports(m3))

    def test_v1_scope(self):
        kings = {"tags": [{"label": "Sports"}, {"label": "NBA"}],
                 "sportsMarketType": None, "gameStartTime": None}
        rec("thể thao mùa vụ (Kings NBA Finals) -> ngoài phạm vi v1, đếm riêng", "",
            (False, "thể_thao_mùa_vụ_ngoài_v1"), sports_filter.in_v1_scope(kings))
        game = {"tags": [{"label": "Sports"}], "sportsMarketType": "moneyline",
                "gameStartTime": "2026-11-02 19:00:00+00"}
        rec("lệnh trước giờ bóng -> trong phạm vi", "trade_ts < gameStartTime",
            (True, "ok"), sports_filter.in_v1_scope(game, trade_ts=1780000000))
        rec("lệnh sau giờ bóng -> trong trận, loại khỏi v1", "trade_ts >= gameStartTime",
            (False, "trong_trận_hoặc_sau_giờ_bóng"),
            sports_filter.in_v1_scope(game, trade_ts=2000000000))

    def test_sport_label(self):
        m = {"tags": [{"label": "Sports"}, {"label": "NBA"}, {"label": "Games"}]}
        rec("tên môn lấy tag cụ thể đầu tiên (bỏ tag chung)", "",
            "NBA", sports_filter.sport_label(m))


class T10OverlapMisc(unittest.TestCase):
    def test_price_run_and_band(self):
        rec("giá chạy 0.15 > 0.10 -> bỏ", "raw 0.65 vs nhóm đầu 0.50",
            True, overlap.price_run_blocked(0.65, 0.50))
        rec("giá chạy đúng 0.10 -> không bỏ (ngưỡng 'quá')", "",
            False, overlap.price_run_blocked(0.60, 0.50))
        for p, want in ((0.95, False), (0.90, True), (0.10, True), (0.08, False)):
            rec("dải giá sau phạt %.2f -> %s" % (p, "được" if want else "bỏ"), "",
                want, overlap.band_ok(p))
        rec("khối lượng tại kích hoạt 9.999 -> không đủ 10.000", "",
            False, overlap.volume_ok(9999.0))
        rec("khối lượng đúng 10.000 -> đủ", "", True, overlap.volume_ok(10000.0))

    def test_segment_state(self):
        st = overlap.SegmentState()
        rec("thị trường đầu của sự kiện -> copy", "",
            ("copy", None), st.admit("m1", "e1"))
        st.mark("m1", "e1")
        rec("thị trường sau cùng mã -> bỏ (đã copy)", "",
            ("bỏ", "thị_trường_đã_copy"), st.admit("m1", "e1"))
        rec("thị trường khác cùng sự kiện -> bỏ, ghi bảng 16", "",
            ("bỏ", "cùng_sự_kiện_đã_copy"), st.admit("m2", "e1"))
        rec("bảng 16 ghi 1 dòng", "", 1, len(st.suppressed_same_event))
        rec("thị trường sự kiện khác -> copy", "",
            ("copy", None), st.admit("m3", "e2"))


class T11TimeAndLoader(unittest.TestCase):
    def test_floor_seconds(self):
        rec("RFC3339 lẻ giây -> làm tròn XUỐNG (§19.6)", "2026-07-19T22:53:46.999Z",
            1784501626, data_loader.floor_seconds_utc("2026-07-19T22:53:46.999Z"))
        rec("1970 + 59.999s -> 59", "", 59,
            data_loader.floor_seconds_utc("1970-01-01T00:00:59.999Z"))

    def test_fake_transport_pagination(self):
        pages = [
            {"data": [1, 2], "pagination": {"next_cursor": "c1", "has_more": True}},
            {"data": [3], "pagination": {"next_cursor": None, "has_more": False}},
        ]
        calls = {"n": 0}

        def transport(url):
            calls["n"] += 1
            return 200, json.dumps(pages[calls["n"] - 1]), {}, 0.05

        h = data_loader.BudgetHttp(out_dir="/tmp/ct_test_loader", max_requests=10,
                                   sleep_s=0, transport=transport, latency_watch=False)
        res = h.paginate("https://x/v2/trades?user=0x1", "t")
        rec("phân trang cursor tới null gộp 3 dòng 2 trang", "",
            (3, 2, False), (len(res["rows"]), res["pages"], res["capped"]))

    def test_stop_on_429(self):
        def transport(url):
            return 429, "{}", {"Retry-After": "60"}, 0.05
        h = data_loader.BudgetHttp(out_dir="/tmp/ct_test_loader", max_requests=10,
                                   sleep_s=0, transport=transport, latency_watch=False)
        try:
            h.get_json("https://x", "t429")
            raised = "không có"
        except data_loader.StopProbe as e:
            raised = str(e)
        rec("HTTP 429 -> DỪNG TOÀN BỘ, ghi Retry-After", "",
            "HTTP 429 — Retry-After=60", raised)

    def test_budget_cap(self):
        def transport(url):
            return 200, "{}", {}, 0.05
        h = data_loader.BudgetHttp(out_dir="/tmp/ct_test_loader", max_requests=1,
                                   sleep_s=0, transport=transport, latency_watch=False)
        h.get_json("https://x", "a")
        try:
            h.get_json("https://x", "b")
            raised = "không có"
        except data_loader.StopProbe as e:
            raised = str(e)
        rec("vượt ngân sách request -> dừng", "", "vượt ngân sách 1 request", raised)

    def test_latency_watchdog(self):
        state = {"n": 0}

        def transport(url):
            state["n"] += 1
            lat = 0.1 if state["n"] < 6 else 7.0
            return 200, "{}", {}, lat
        h = data_loader.BudgetHttp(out_dir="/tmp/ct_test_loader", max_requests=10,
                                   sleep_s=0, transport=transport, latency_watch=True)
        stopped = "không có"
        for i in range(7):
            try:
                h.get_json("https://x%d" % i, "w%d" % i)
            except data_loader.StopProbe as e:
                stopped = str(e)
                break
        rec("response chậm bất thường -> watchdog dừng", "5 request 0.1s rồi 1 request 7s",
            True, stopped.startswith("độ trễ bất thường"))


class T12Report(unittest.TestCase):
    def test_price_band_table(self):
        sigs = [{"copy_price": 0.2, "pnl": 10.0, "event_id": "e1", "sport": "NBA"},
                {"copy_price": 0.5, "pnl": -5.0, "event_id": "e2", "sport": "NFL"},
                {"copy_price": 0.8, "pnl": 20.0, "event_id": "e1", "sport": "NBA"}]
        t = report.table_price_band(sigs)
        rec("bảng dải giá đủ 3 dải đúng nhóm", "",
            3, len(t))
        rec("dải 0.10–0.30 có 1 tín hiệu pnl 10", "",
            (1, 10.0), (t["0.10–0.30"]["n_signals"], t["0.10–0.30"]["pnl"]))

    def test_skip_rate_gate(self):
        rec_ = report.table_skip({"n_took": 70, "lý_do_đầy_vốn": 10, "lý_do_ngoài_dải": 5})
        rec("tỷ lệ bỏ 15/85=17.6% -> qua cổng <=30%", "",
            (0.176471, True), (round(rec_["skip_rate"], 6), rec_["gate_pass"]))
        rec2_ = report.table_skip({"n_took": 70, "lý_do_đầy_vốn": 35})
        rec("tỷ lệ bỏ 33.3% -> trượt cổng", "",
            False, rec2_["gate_pass"])

    def test_registry_18_tables_labeled(self):
        rec("đủ 18 bảng, mỗi bảng ghi rõ tính điểm/mô tả", "",
            18, len(report.TABLE_REGISTRY))
        scoring = [i for i, _, kind in report.TABLE_REGISTRY if "TÍNH ĐIỂM" in kind]
        rec("các bảng chạm verdict: 8, 9, 10, 12", "",
            [8, 9, 10, 12], scoring)
        desc11 = dict((i, k) for i, _, k in report.TABLE_REGISTRY)[11]
        rec("bảng 11 ghi CẤM cứu verdict", "",
            True, "CẤM cứu verdict" in desc11)




# =====================================================================
# V2 — AUDIT: 1 lỗi code thật + 6 lỗi soạn thảo test của bản V1 (Sửa 7)
# Mỗi lỗi: trước-sau, và dòng luật trong tổng hợp/quyết định chứng minh đáp án sau sửa đúng.
V1_FIX_AUDIT = [
    {"lỗi": "code thật — thứ tự trả về resolve_price không nhất quán với resolution_decision",
     "trước": "resolve_price trả (giá_trị, trạng_thái); resolution_decision trả (trạng_thái, giá_trị)",
     "sau": "cả hai trả (trạng_thái, giá_trị) — resolve_price V2: ('ok', 1.0)",
     "chứng_minh": "§19.2 quyết định chủ nhân: trạng thái nguồn chốt phải đọc được đồng nhất trước khi lấy giá; giao diện nhất quán là điều kiện kiểm tra dừng-được khi lệch"},
    {"lỗi": "test soạn thảo — chia sai mẫu số tỉ lệ gộp nhóm",
     "trước": "kỳ vọng trùng 70 / 200 = 0,35 <0,5 -> không gộp",
     "sau": "tỉ lệ = trùng / SỐ LỆNH ÍT HƠN = 70 / min(100,200) = 0,70 -> GỘP; thêm W2 40/100=0,40 -> không gộp",
     "chứng_minh": "Tổng hợp Q3.10: 'số lệnh trùng / số lệnh ít hơn trong hai ví ≥ 50%'"},
    {"lỗi": "test soạn thảo — input 21 tín hiệu làm cổng 1 tự trượt",
     "trước": "20 tín hiệu +10 và 1 tín hiệu +400 (out_n=21 <100)",
     "sau": "100 tín hiệu +10 và 1 tín hiệu +400 (out_n=101; top1=28,6%>25%; ROI 13,9%>5%)",
     "chứng_minh": "Tổng hợp Q9 tầng 1 cổng 1: ngoài mẫu ≥ 100 tín hiệu"},
    {"lỗi": "test soạn thảo — input ex-top10 có ROI 2,3% tự trượt cổng 4",
     "trước": "[500] + 100×(−5) + 4×60 → tổng 240, ROI 2,3% <5%",
     "sau": "[1000] + 100×(−2) + 4×70 → tổng 1080, ROI 10,3% >5%; bỏ top-10 còn −200 <0",
     "chứng_minh": "Tổng hợp Q9 tầng 1 cổng 4 (ROI >5%) và cổng 7 (bỏ 10 lãi nhất vẫn >0)"},
    {"lỗi": "test soạn thảo — đảo thứ tự tuple (skip, accepted)",
     "trước": "mong đợi ([99],[10])",
     "sau": "mong đợi (skip=[10], accepted_cuối=[99])",
     "chứng_minh": "Tổng hợp Q6: tín hiệu mới khi đủ 10 lệnh mở thì bị bỏ, ghi riêng số bị bỏ vì đầy vốn"},
    {"lỗi": "test soạn thảo — so float đủ độ chính xác với giá trị đã làm tròn",
     "trước": "0.17647058823529413 so với round(...,6)",
     "sau": "hai bên cùng round 6 chữ số",
     "chứng_minh": "hạ tầng kỹ thuật của test, không đổi luật"},
    {"lỗi": "test soạn thảo — import hold_pnl từ ledger thay vì selection",
     "trước": "ledger.hold_pnl (không tồn tại)",
     "sau": "selection.hold_pnl",
     "chứng_minh": "hold_pnl là luật Q3.4, đặt ở module selection"},
]


class T13V2FeeMissing(unittest.TestCase):
    """Sửa 3 — tín hiệu rơi vào khoảng thiếu phí phải BỎ + đếm riêng, không tính phí 0."""

    def test_gap_returns_fee_missing(self):
        st = ledger.fee_for_signal({}, 1783209600)  # 05-07-2026, không feeSchedule
        rec("khoảng 01→09-07 không feeSchedule -> FEE_MISSING", "ts=05-07-2026",
            "FEE_MISSING", st["status"])

    def test_gap_never_zero(self):
        rate, source = ledger.fee_rate({}, 1783209600)
        rec("khoảng thiếu phí KHÔNG trả 0 hay 0,03/0,05", "",
            (None, "FEE_MISSING"), (rate, source))

    def test_split_signals_skips_and_counts(self):
        sigs = [
            {"id": "a", "ts": 1783209600, "market": {}},                       # thiếu phí
            {"id": "b", "ts": 1786320000, "market": {}},                       # 10-08 -> 0.05
            {"id": "c", "ts": 1778371200, "market": {"feeSchedule": {"rate": 0.03}}},
        ]
        taken, skipped = ledger.split_signals_by_fee(sigs)
        rec("tín hiệu thiếu phí bị bỏ, 2 tín hiệu còn lấy", "",
            (["b", "c"], [{"id": "a", "lý_do": "thiếu_phí"}]),
            (taken and [t["id"] for t in taken], [{"id": s["id"], "lý_do": s["lý_do"]} for s in skipped]))
        self.assertFalse(any(t["id"] == "a" for t in taken), "tín hiệu thiếu phí không được tính lãi với phí 0")

    def test_skip_table_includes_fee_missing(self):
        t = report.table_skip({"n_took": 19, "lý_do_thiếu_phí": 1})
        rec("bảng bỏ có mục lý_do_thiếu_phí, tỷ lệ 1/20", "",
            (1, 0.05, True), (t["counts"]["lý_do_thiếu_phí"], round(t["skip_rate"], 6), t["gate_pass"]))


class T14V2MajorTournament(unittest.TestCase):
    """Sửa 5 — khối lượng giải lớn tính TỚI CUỐI ĐOẠN, không dùng volumeNum cuối."""

    def _ev(self, n): return {"market_ids": ["m%d" % i for i in range(n)]}

    def test_final_volume_not_used(self):
        # sự kiện: volume CUỐI CÙNG 1.000.000 (tương lai) nhưng tới cuối đoạn chỉ 4.000
        res = report.classify_major_tournament(
            self._ev(10), seg_end_cum_volume=4000.0,
            universe_seg_end_volumes=[4000.0, 5000.0, 6000.0, 7000.0, 8000.0,
                                      90000.0, 95000.0, 99000.0, 100000.0, 100000.0,
                                      100000.0, 100000.0, 100000.0, 100000.0, 100000.0,
                                      100000.0, 100000.0, 100000.0, 100000.0, 100000.0])
        rec("volume cuối đoạn thấp -> KHÔNG phải giải lớn dù volumeNum cuối cao",
            "8 markets, seg_end 4.000/20 sự kiện (ngưỡng top 5% = 100.000)",
            False, res["is_major"])

    def test_seg_end_volume_used(self):
        res = report.classify_major_tournament(
            self._ev(10), seg_end_cum_volume=150000.0,
            universe_seg_end_volumes=[4000.0, 5000.0, 6000.0, 7000.0, 8000.0,
                                      90000.0, 95000.0, 99000.0, 100000.0, 100000.0,
                                      100000.0, 100000.0, 100000.0, 100000.0, 100000.0,
                                      100000.0, 100000.0, 100000.0, 100000.0, 100000.0])
        rec("volume cuối đoạn ở top 5% -> là giải lớn cho đoạn đó",
            "seg_end 150.000 >= ngưỡng 100.000",
            True, res["is_major"])

    def test_only_final_volume_descriptive(self):
        res = report.classify_major_tournament(
            self._ev(10), seg_end_cum_volume=None, universe_seg_end_volumes=None)
        rec("chỉ có volumeNum cuối -> trả chưa phân loại, chỉ mô tả sau chốt",
            "", (None, "chỉ_có_volumeNum_cuối_chỉ_mô_tả_sau_chốt"),
            (res["is_major"], res["lý_do"]))

    def test_min_markets_gate(self):
        res = report.classify_major_tournament(
            self._ev(7), seg_end_cum_volume=999999.0,
            universe_seg_end_volumes=[1.0])
        rec("dưới 8 thị trường con -> không phải giải lớn", "",
            False, res["is_major"])


class T15V2StatusAndConstants(unittest.TestCase):
    """Sửa 2 — bảng trạng thái §19 khớp file quyết định; Sửa 6 — hằng tự chọn đủ ghi chú."""

    def test_s19_status_table(self):
        expected_kind = {
            "19.1": "DUYỆT VỀ HƯỚNG", "19.2": "ĐÃ DUYỆT", "19.3": "ĐÃ DUYỆT",
            "19.4": "ĐÃ DUYỆT", "19.5": "DUYỆT VỀ HƯỚNG", "19.6": "ĐÃ DUYỆT",
            "19.7": "CHƯA DUYỆT", "19.8": "CHƯA DUYỆT", "19.9": "DUYỆT VỀ HƯỚNG"}
        def kind(v):
            if v.startswith("ĐÃ DUYỆT"):
                return "ĐÃ DUYỆT"
            if v.startswith("DUYỆT VỀ HƯỚNG"):
                return "DUYỆT VỀ HƯỚNG"
            if v.startswith("CHƯA DUYỆT"):
                return "CHƯA DUYỆT"
            return "KHÔNG_RÕ"
        got = {k: kind(v) for k, v in config.S19_STATUS.items()}
        rec("bảng trạng thái §19 = 3 mục duyệt hường, 4 mục đã duyệt, 2 chưa duyệt",
            "theo file quyết định hash 01248d55…",
            expected_kind, got)

    def test_self_chosen_registry(self):
        rec("mọi hằng TỰ CHỌN đều nằm trong registry SELF_CHOSEN (7 hằng)",
            "FEE_MISSING_ALERT, MAJOR_MIN_MARKETS, MAJOR_TOP_SHARE, K_CONTROL, N_BOOT, BOOTSTRAP_SEED, MAX_PAGES",
            7, len(config.SELF_CHOSEN))
        for name, (val, note) in config.SELF_CHOSEN.items():
            self.assertTrue(hasattr(config, name), name)
            self.assertTrue(note and ("ĐỀ XUẤT" in note or "TỰ CHỌN" in note), name)

    def test_bootstrap_seed_reproducible(self):
        sig = [{"event_id": "e%02d" % e, "pnl": 20.0} for e in range(10) for _ in range(5)]
        r1 = killgate.tier2_bootstrap(sig)
        r2 = killgate.tier2_bootstrap(sig)
        rec("bootstrap seed cố định -> hai lần chạy cho CI giống hệt", "",
            True, r1 == r2)


def tearDownModule():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_report_v2.json")
    n_pass = sum(1 for r in RESULTS if r["pass"])
    json.dump({"n_pass": n_pass, "n_fail": len(RESULTS) - n_pass, "results": RESULTS,
               "v1_fix_audit": V1_FIX_AUDIT},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n=== TEST REPORT: %d pass / %d fail -> %s ===" %
          (n_pass, len(RESULTS) - n_pass, out))


if __name__ == "__main__":
    unittest.main(verbosity=2)
