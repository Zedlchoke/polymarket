# chain-edge-cycle —_cycle tìm edge bằng reverse engineer ví blockchain (chỉ giấy)

Đọc theo thứ tự khi tiếp tục dự án ở phiên mới:

1. `00_CHARTER.md` — hiến pháp: ranh giới cứng, cổng giết, quy trình wave. **Không bao giờ vi phạm.**
2. `state/checkpoint.md` — đã làm tới đâu, còn thiếu gì, chạy tiếp từ đâu.
3. `state/box_table.md` — bảng 3 hộp (SỐNG / CHẾT / THIẾU DỮ LIỆU).
4. `state/wave_log.md` — từng wave: cơ chế, spec hash, verdict, trạng thái kiểm toán.
5. `wave01_new_listing_early_buy/` — wave đang chạy.
6. `logs/request_log.csv` — mọi request đã gửi; `logs/rate_events.log` — mọi 429/403.

## Cây thư mục

```
chain-edge-cycle/
├── 00_CHARTER.md          # hiến pháp (ranh giới + cổng giết + quy trình)
├── README.md
├── tools/                 # script: fetch_common.py (luật request), budget_config.json, probe, discovery, backtest
├── logs/                  # request_log.csv, rate_events.log
├── state/                 # checkpoint, box_table, wave_log, daily_counts.json, discovery_*.json
├── data/                  # dữ liệu thô nội bộ (địa chỉ đầy đủ được phép ở đây, không doxx)
│   ├── gt/                # geckoterminal: new_pools raw + extract, ohlcv
│   ├── dexscreener/
│   └── rpc/
└── wave01_new_listing_early_buy/
    ├── step0_universe.md  # vũ trụ — đóng băng TRƯỚC khi xem lãi
    ├── step1_describe.md  # mô tả, không tính điểm
    ├── spec_v1.md         # spec + sha256, đóng băng trước backtest
    ├── backtest/          # kết quả + báo cáo wave (5 mục) — DỪNG chờ kiểm toán
    └── report_wave01.md
```

## Luật chạy tools

- Mọi script đều qua `tools/fetch_common.py`: tự log, tự nghỉ đúng khoảng, tự dừng khi vượt trần ngày
  hoặc khi 429/403 (khóa API tới hết phiên process). **Không gọi API ngoài fetch_common.**
- Chạy discovery: `python3 tools/discover_new_pools.py --network base --until <ISO-UTC> --max-calls 600`
  (resume được: đọc `state/discovery_base.json`).
- **TUYỆT ĐỐI KHÔNG** sửa/chạy bất cứ thứ gì ngoài thư mục này (PaperDesk, spec Polymarket là vùng cấm).
