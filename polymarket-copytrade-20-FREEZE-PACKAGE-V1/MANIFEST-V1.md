# MANIFEST — GÓI ĐÓNG BĂNG V1 — DỰ ÁN COPY TRADE 20 TÀI KHOẢN POLYMARKET

Ngày đóng gói: 2026-11-02 (UTC). Đóng gói theo lệnh của chủ nhân (prompt "chỉ đóng gói file đóng băng để chuyển coordinator, không chạy Việc B/C").
Gói này được tạo sau khi Việc A (đóng băng) hoàn tất và TRƯỚC khi chủ nhân kiểm tra hash. **Việc B (hồ sơ + backtest) và Việc C (overlap PaperDesk) hoàn toàn chưa chạy tại thời điểm đóng gói.**

## Quy ước hash

- Mọi sha256 tính trên TOÀN BỘ file đúng như nó nằm trong gói (kiểm chứng bằng `shasum -a 256 <file>` / `sha256sum <file>`).
- Riêng SPEC-V1-FROZEN có 2 mã: (1) **mã toàn file = mã chuẩn** kiểm chứng bằng lệnh thường; (2) mã nội bộ trừ dòng hash — chỉ tham khảo, KHÔNG phải mã chuẩn.

## Bảng đầy đủ 20 file (19 file thuộc 9 nhóm + MANIFEST này)

| # | File trong gói | Nguồn gốc | Byte | sha256 (toàn file) |
|---|---|---|---|---|
| 1 | polymarket-copytrade-20-SPEC-V1-FROZEN.md | ~/workspace/your_files/ | 22.494 | e98691e2c555a326c59a92633a22864e04152109c9e48b8cc8457f9b7a5cb61f |
| 2 | polymarket-copytrade-20-FREEZE-LOG-V1.md | ~/workspace/your_files/ | 4.880 | 8379c3f412d1d3280506559c195891b8cf015858dcdfecfa7dc071187ec36d89 |
| 3 | polymarket-copytrade-20-SPEC-V1-CANDIDATE-V2.md | ~/workspace/your_files/ | 28.300 | 2f69fdc103dafebabe5a2be8e67167c432b7ee9d97879ed203c3faa3c8dac276 |
| 4 | copytrade_build_v2/src/__init__.py | ~/Downloads/Polymarket/copytrade_build_v2/ | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| 5 | copytrade_build_v2/src/config.py | như trên | 7.533 | 13d531276267aaedae92a8dea458e8f11c29ebaff82ef35301e321a9a403bb14 |
| 6 | copytrade_build_v2/src/data_loader.py | như trên | 7.005 | a0490a75aa56b6f751acb0a8b87822fd70d858dd76eff65ac8be4726e1f0f62a |
| 7 | copytrade_build_v2/src/killgate.py | như trên | 4.390 | 19d55e93348f15f95c6f110cad9cbe463babe86974b55c0a9df4d18cd732ebf4 |
| 8 | copytrade_build_v2/src/kopt.py | như trên | 1.746 | e5aa01c82e101b456ff46ec544e890f568076fbf3f5af1eee65805541f7f2126 |
| 9 | copytrade_build_v2/src/ledger.py | như trên | 7.408 | 5fc42a0906104a6014b5db2e244bd4b9096f95a1d7729df4285a1ecf3c30cc9e |
| 10 | copytrade_build_v2/src/overlap.py | như trên | 4.113 | 33ec4d52b91d5d5b8dbaeeac654dbc0e08b6c6e8f09cb027d7f9cddba5949ec2 |
| 11 | copytrade_build_v2/src/report.py | như trên | 5.827 | 4e8d5073561833cefa7e053e126616b9956797a0907dad2a1004cfa0407b5816 |
| 12 | copytrade_build_v2/src/selection.py | như trên | 6.717 | 9dd786dac265c52bdf6b6efdb30aece75613baf3444ac8dd12cd74c42ece2910 |
| 13 | copytrade_build_v2/src/sports_filter.py | như trên | 2.426 | 61b5a7f5e5b5023577e7f9c394960ea5f2c7ae5b6641407405fb80c0d16696ea |
| 14 | copytrade_build_v2/tests/test_synthetic.py | như trên | 41.863 | df5b2b7dff2f6a1a58e8cdf7302c44031762742cb389af1f2607829e38abdd83 |
| 15 | copytrade_build_v2/tests/test_report_v2.json | như trên | 24.582 | 0dd4f85ae6ace3cef4c22e68f32925c8bfa1e7e41746a5c587a6d75e184e5357 |
| 16 | polymarket-copytrade-20-SPEC-V1-DRAFT-V2.md | ~/workspace/your_files/ | 48.501 | 8e108e30612c0997ca3a708468247f890916a92058d79a934e9dc7ba08153406 |
| 17 | polymarket-copytrade-20-PROBE-REPORT-V2.md | ~/workspace/your_files/ | 29.100 | 2782eb5cd6bd3b03264c9fa5717245e541605bab0589fdd54865c1a529b43c32 |
| 18 | polymarket-copytrade-20-QUYET_DINH_OWNER_2026-11-02.md (**BẢN CHUẨN coordinator**) | ~/workspace/your_files/ | 5.677 | 01248d550391824d208a5bf49ca6650054d8f179950e32b4fcc11edce939a3a0 |
| 19 | polymarket-copytrade-20-QUYET_DINH_OWNER_2026-11-02_BAN-DAN-CHAT-DAU.md (bằng chứng, **KHÔNG phải bản chuẩn**) | ~/workspace/your_files/ | 5.593 | 6772eec7a4eeda6102b017a8ba241f325d11f9ff0afd40b3ab9a24214a511c7f |
| 20 | QUYET_DINH-diff-banchat-vs-coordinator-SINH-KHI-DONG-GOI-2026-11-02.txt (xem ghi chú A dưới) | sinh tại đóng gói | 9.662 | 89c6d0eafcc648547cb409d35d5fb2babf7b8d360ea7f67fedf742da0a507e5b |
| — | MANIFEST-V1.md (file này; báo cáo đóng gói, không thuộc 9 nhóm) | sinh tại đóng gói | — | (tự tham chiếu, không hash chính nó) |

**Tổng: 19 file thuộc 9 nhóm + 1 MANIFEST = 20 file; tổng byte của 19 file nhóm = 267.817 byte** (MANIFEST này cộng thêm).

## Đối chiếu 9 nhóm theo lệnh đóng gói

1. Spec đóng băng → file #1 ✓ · 2. FREEZE_LOG → #2 ✓ · 3. Spec ứng viên V2 → #3 ✓ · 4. Code V2 (src/ 10 file + tests/ 2 file) → #4–15 ✓ · 5. test_report_v2.json → #15 ✓ · 6. Spec nháp V2 (tên đầy đủ `polymarket-copytrade-20-SPEC-V1-DRAFT-V2.md`) → #16 ✓ · 7. Báo cáo thăm dò V2 (tên đầy đủ `polymarket-copytrade-20-PROBE-REPORT-V2.md`) → #17 ✓ · 8. Quyết định coordinator (hash 01248d55…) → #18 ✓ + bản dán chat bằng chứng → #19 ✓ + file diff → #20 (ghi chú A) · 9. File quyết định bổ sung chọn mốc B → **CHƯA NHẬN** (ghi chú B).

**Kiểm chứng nguyên văn:** cả 19 file nhóm đã so **byte-for-byte (cmp)** với file gốc — GIỐNG HỆT toàn bộ. Không file nào trong danh mục THIẾU.

## Hai mã hash của SPEC-V1-FROZEN

- **Mã chuẩn (toàn file, kiểm chứng `shasum -a 256`):** `e98691e2c555a326c59a92633a22864e04152109c9e48b8cc8457f9b7a5cb61f` — **khớp đúng mã e986… đã báo ở Việc A** (đã tính lại trên file trong gói).
- Mã nội bộ trừ dòng hash (CHỈ THAM KHẢO, không phải mã chuẩn): `d7b4c39b7dda6a43f4ff3d4717bf5e63fed734e305496bc1813e952c3be6a9f7` — khớp báo cáo trước.

## Ghi chú minh bạch

**A — File diff (#20):** trước thời điểm đóng gói, phép diff giữa bản dán chat và bản coordinator CHỈ được chạy trong terminal (kết quả nằm trong báo cáo chat Sửa 1), **chưa từng được lưu thành file**. File #20 được SINH tại thời điểm đóng gói bằng `diff -u <#19> <#18>`, không đổi nội dung nào của 2 file nguồn (2 file này có hash riêng ở trên nên coordinator tái tạo và đối chiếu được). Nội dung diff: khác 31→35 dòng, toàn định dạng markdown, không khác nội dung.
**B — Nhóm 9 (quyết định bổ sung mốc B):** chủ nhân CHƯA chuyển file riêng nào chọn mốc B. Mốc B đến từ văn bản lệnh chat ngày 2026-11-02 (đã trích nguyên văn giá trị vào mục 15 của spec đóng băng và FREEZE_LOG). Không tự tạo file.
**Lỗi ghi nhận trong quá trình đóng gói:** một script kiểm tra nhanh in cờ "LỆCH" cho file #18 do lỗi gõ chuỗi kỳ vọng trong script; kiểm chứng lại bằng cmp byte-for-byte + shasum trực tiếp xác nhận file ĐÚNG (hash 01248d55…). Ghi ra đây để minh bạch.

## Cam kết sau đóng gói

Sau khi hash xong, KHÔNG file nào trong gói bị sửa. Nếu cần sửa gì thì lập gói mới có phiên bản mới, tính lại toàn bộ hash. Việc B và Việc C chỉ chạy sau lệnh văn bản "hash đúng, chạy tiếp" của chủ nhân.
