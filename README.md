# Polymarket — Copy Trade 20 Tài Khoản (Nghiên Cứu Trên Giấy)

Dự án nghiên cứu **hoàn toàn trên giấy** (paper-only) về chiến lược copy trade 20 tài khoản Polymarket.
**Không có lệnh thật, không tiền thật, không nối ví, không bot.** Chi phí 0 đồng; mọi dữ liệu từ API công khai.

## Trạng thái hiện tại (2026-11-02)

- **Spec v1 ĐÃ ĐÓNG BĂNG** — `polymarket-copytrade-20-SPEC-V1-FROZEN.md`
  - SHA256 toàn file (mã chuẩn): `e98691e2c555a326c59a92633a22864e04152109c9e48b8cc8457f9b7a5cb61f`
  - SHA256 nội dung (trừ dòng hash, tham khảo): `d7b4c39b7dda6a43f4ff3d4717bf5e63fed734e305496bc1813e952c3be6a9f7`
- Đang chờ coordinator kiểm toán gói đóng băng; **chưa chạy backtest, chưa chọn k\*, chưa có verdict**.
- Quyết định đã chốt: D1 cờ / D2 nhóm mới / D3 100-500 USD / D4 24h+0,10 / D5 80 lệnh; mốc B (T0 2025-09-13 → T3 2026-06-10).

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `polymarket-copytrade-20-FREEZE-PACKAGE-V1/` | Gói đóng băng cho coordinator: spec đóng băng, FREEZE_LOG, MANIFEST đầy đủ hash, quyết định, diff, code V2, test report |
| `docs/` | Toàn bộ tài liệu dự án: tổng hợp 6 góc nhìn (nguồn luật), quyết định D1–D5, spec nháp V1/V2, spec ứng viên V1/V2, báo cáo thăm dò V1/V2 |
| `probe/` | Script thăm dò chỉ đọc (V1 + V2) + dữ liệu thô `probe_out/`, `probe_out_v2/` (log từng request, checkpoint) |
| `copytrade_build_v1/`, `copytrade_build_v2/` | Code theo spec (loader, sports filter, selection, overlap, ledger, k-optimizer, kill gate, report) + bộ test dữ liệu giả (V2: 69 test / 120 record, 120 pass) |

## Luật dự án (tóm tắt)

3 đoạn 90 ngày liền nhau (chọn người → in-sample tìm k* → holdout test đúng 1 lần); copy giá VWAP đủ 100 USD + phạt trễ max(0,02; spread); phí theo feeSchedule từng thị trường; cổng giết 3 tầng (sàng lọc → khoảng tin cậy 95% bootstrap theo sự kiện → cờ mô tả); verdict chỉ là SỐNG / CHẾT / CHƯA ĐỦ BẰNG CHỨNG. Chi tiết đầy đủ trong spec đóng băng.

## Lưu ý dữ liệu

`probe/probe_out*/` chứa dữ liệu thô từ API công khai Polymarket (Data API v2, Gamma, CLOB) lấy ngày 2026-11-02 theo cửa sổ mẫu nhỏ, kèm log từng request và checkpoint. Không chứa bất kỳ khóa/bí mật nào.
