# Test bộ máy backtest trên dữ liệu giả — loop 10h 2026-11-02

Kết quả: **15/15 PASS**

| Test | Kết quả | Chi tiết |
|---|---|---|
| so_hoc_phi_bang_tay | PASS | net=7.3055 vs 7.3055 |
| hoa_vong_tinh_dung | PASS | net=-0.3080 (điểm hòa ~101.6) |
| entry_open_bar_sau_khong_close_bar_hien_tai | PASS |  |
| exit_open_bar_dung_luat | PASS |  |
| thieu_du_lieu_danh_dau_truncated | PASS |  |
| khong_du_bar_khong_tao_tin_hieu | PASS |  |
| bootstrap_clu_khong_bi_lua_boi_1_token | PASS | CI=(-0.500,7.075) |
| bootstrap_clu_qua_khi_that_su_deu | PASS | CI=(2.000,2.000) |
| bootstrap_deterministic_theo_seed | PASS |  |
| cong_t1_dung_khi_day_du | PASS |  |
| cong_t1_tu_choi_khi_thieu_tin_hieu | PASS |  |
| cong_t1_bat_tap_trung_top1 | PASS |  |
| stress_phi_20pt_dung_cong_thuc | PASS | 6.9800 |
| cong_t1_tu_choi_khi_stress_am | PASS |  |
| chon_tham_so_median_insample | PASS |  |

Bộ máy chưa từng chạm dữ liệu thật. Backtest thật chỉ chạy sau khi spec đóng băng + có sha256 + lệnh GO.
