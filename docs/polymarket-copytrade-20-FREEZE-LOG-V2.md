# FREEZE LOG — SPEC v2 ĐÓNG BĂNG — DỰ ÁN COPY TRADE 20 TÀI KHOẢN POLYMARKET

## Thông tin đóng băng

- **Ngày đóng băng:** 2026-11-03.
- **File đóng băng:** `docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md` (repo GitHub `Zedlchoke/polymarket`, branch `main`).
- **Căn cứ lệnh:** prompt Việc 2 của chủ nhân ngày 2026-11-03 — duyệt ngưỡng 10.000 USD (mục 2.2 của nháp) thành LUẬT, lệnh đóng băng + ghi hash + DỪNG; sau kiểm toán coordinator spec v2 nháp kết luận **KHÔNG LỆCH LUẬT (2026-11-03)**.
- **Chuẩn hash v2 (theo lệnh Việc 2, khác v1):** SHA256 **TOÀN FILE** bằng `sha256sum`/`shasum -a 256` thông thường — **KHÔNG dùng hash trừ dòng hash làm chuẩn**. File spec đóng băng KHÔNG chứa dòng hash của chính nó; con số duy nhất để kiểm tra là hash toàn file dưới đây.
- **Điểm dừng bắt buộc đã giữ:** Việc 2 xong thì **DỪNG** — chờ chủ nhân kiểm tra hash v2 **bằng văn bản**, sau đó mới có **lệnh GO riêng** cho Việc 3. KHÔNG đếm pool, KHÔNG chọn ví, KHÔNG tính điểm, KHÔNG backtest, KHÔNG về trước, KHÔNG áp dụng vào PaperDesk.

## Mã hash

| Đại lượng | Giá trị |
|---|---|
| **SHA256 TOÀN FILE spec v2 đóng băng** (`docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md`) — CHUẨN | `ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8` |
| SHA256 toàn file nháp nguồn, không đổi (`docs/polymarket-copytrade-20-SPEC-V2-DRAFT.md`, commit `d62dc6f`, 141 dòng) | `b9d6cf8974b309716701745f9631c6fd2116b7cac73c4ed55292d7bb0b643954` |
| SHA256 toàn file spec v1 đóng băng (tham chiếu, trùng FREEZE-LOG-V1) | `e98691e2c555a326c59a92633a22864e04152109c9e48b8cc8457f9b7a5cb61f` |

**Công thức kiểm chứng (bất kỳ ai cũng lặp lại được):** `shasum -a 256 docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md` — phải ra `ae504a97…bee55d8`.

## File quyết định ngưỡng — tình trạng thực tế

Lệnh Việc 2 yêu cầu ghi "hash của file quyết định ngưỡng". **Đã rà và xác nhận: KHÔNG tồn tại file riêng nào ghi quyết định duyệt ngưỡng 10.000 USD ngày 2026-11-03** — đã kiểm toàn bộ repo (kể cả lịch sử commit a518331 → d62dc6f → b8fe9f9), `~/workspace/your_files/`, và mọi file `.md` được sửa trong ngày 03/11. Quyết định duyệt nằm trong **prompt Việc 2 của chủ nhân ngày 2026-11-03 (văn bản lệnh trong chat)** — đúng tiền lệ FREEZE-LOG-V1 đã ghi nguồn "Prompt chủ nhân 2026-11-02 | văn bản lệnh trong chat". Vì không có file nên **không có hash để ghi**; trích nguyên văn phần duyệt từ lệnh Việc 2:

> "chủ nhân đã duyệt ngưỡng 10.000 USD thành luật ngày 2026-11-03" — ngưỡng "thị trường có tổng giao dịch trong đoạn 1 ≥ 10.000 USD mới vào bước lấy chi tiết" đổi từ "ĐỀ XUẤT CHỜ DUYỆT" thành "LUẬT ĐÃ DUYỆT ngày 2026-11-03", kèm 3 điều kiện giữ nguyên: tổng giao dịch đo từ dữ liệu trade trong đoạn 1, không dùng volumeNum cuối; khi chạy phải báo tổng thị trường, số giữ, số bỏ; cấm sàng lọc theo lãi / PnL / kết quả backtest.

Không coi đây là lệch lệnh: chính văn bản duyệt đó (lệnh Việc 2) đã ra lệnh đóng băng. Nếu chủ nhân muốn có file quyết định riêng, sẽ lập khi được yêu cầu — như một tài liệu tham chiếu MỚI, spec đã đóng băng vẫn không bị sửa.

## Đối chiếu nháp với danh sách luật trong lệnh Việc 2 — KẾT QUẢ: KHÔNG LỆCH

| Luật theo lệnh Việc 2 | Vị trí trong nháp d62dc6f | Kết quả |
|---|---|---|
| Pool quét thị trường đoạn 1 | §2 (2.1–2.5) | KHỚP |
| Xác minh từng thị trường bằng gameStartTime ∈ [T0, T1), T0 2025-09-13 (1757721600), T1 2025-12-12 (1765497600) | dòng 48; §2.1 bước 1–2 | KHỚP |
| Q1–Q10 | mục 1, mục 1–10 | KHỚP |
| D1–D5 | dòng 48 | KHỚP |
| Mốc B (T0/T1/T2/T3, 90 ngày/đoạn) | dòng 48 | KHỚP |
| Phí / làm tròn / FEE_MISSING | dòng 36–38 (Q5) | KHỚP |
| Spread 5 phút | dòng 46–47 (Q10) | KHỚP |
| Giải lớn chỉ mô tả | dòng 50 | KHỚP |
| 50 ví đối chứng | dòng 50; §2.5(f) | KHỚP |
| 18 bảng | dòng 51 | KHỚP |
| Ngân sách ~200 request/ngày, 10 giây/request | dòng 51; §2.3 | KHỚP |
| Luật dừng 429/403 | dòng 52; §2.3 | KHỚP |
| Overlap kỷ nguyên B không áp dụng / thiếu mẫu | §3.1 | KHỚP |
| Overlap chỉ ở về trước, sau backtest qua tầng 1+2 + kiểm toán CONFIRMED + bộ ánh xạ theo spec riêng | §3.2–3.3 | KHỚP |

## Danh sách dòng đổi so với nháp (minh bạch toàn bộ, phục vụ kiểm tra "chỉ đổi 1 trạng thái")

Phần luật từ `## 0.` đến hết file là NGUYÊN VĂN nháp đã kiểm toán; chỉ 5 dòng dưới đây đổi (1 thay đổi luật + 4 nhãn trạng thái/goi lại tiêu đề cho đúng giai đoạn đóng băng):

| Dòng nháp | Trước | Sau |
|---|---|---|
| 68 (tiêu đề §2.2) | "ngưỡng là ĐỀ XUẤT CHỜ DUYỆT" | "ngưỡng là LUẬT ĐÃ DUYỆT ngày 2026-11-03" |
| 72 (§2.2) | "**Ngưỡng 10.000 USD là ĐỀ XUẤT CHỜ DUYỆT, chưa phải luật đã chốt.**" | "**Ngưỡng 10.000 USD là LUẬT ĐÃ DUYỆT ngày 2026-11-03.**" (câu "Phải báo: tổng thị trường đoạn 1, số giữ lại, số bị sàng lọc bỏ là bao nhiêu" giữ nguyên) |
| 128 (tiêu đề §5) | "…trong bản nháp này" | "…trong spec này (sau đóng băng)" |
| 130 (§5.1) | "— ĐỀ XUẤT, chưa luật." | "— LUẬT ĐÃ DUYỆT ngày 2026-11-03, kèm 3 điều kiện giữ nguyên tại mục 2.2." |
| 139 (§6) | "Không đóng băng trong file này; không chạy…" | bỏ mệnh đề lỗi thời "Không đóng băng trong file này;" (file đã đóng băng rồi; ràng buộc không-sửa đã nằm ở đầu file) |

Đầu file (dòng 1–10 của nháp): tiêu đề "NHÁP" → "ĐÓNG BĂNG (FROZEN)"; khối banner "⛔ CHƯA ĐÓNG BĂNG" thay bằng khối "✅ ĐÃ ĐÓNG BĂNG" + danh sách quyết định đã chốt — đúng yêu cầu bắt buộc của lệnh Việc 2 ("đầu file ghi rõ ĐÃ ĐÓNG BĂNG, ngày đóng băng, danh sách quyết định đã chốt…"). Hai câu luật nguyên văn nháp được giữ trong khối này: (a) kế thừa v1 kèm hash `e98691e2…`; (b) "chạy hồ sơ/backtest/về trước chỉ xảy ra sau lệnh GO riêng cho từng bước; lựa chọn 'làm cả hai' của chủ nhân KHÔNG phải lệnh GO."

## Trạng thái tại thời điểm ghi log này

- Việc 2: XONG (file đóng băng + hash toàn file + log này + push GitHub cùng commit).
- Việc 3 (đếm mô tả pool): **CHƯA CHẠY** — chờ chủ nhân kiểm tra hash v2 bằng văn bản + lệnh GO riêng.
- Việc 4 (hồ sơ + backtest v2): **CHƯA CHẠY**.
- Việc 5 (về trước): **CHƯA CHẠY**.
- Chưa đếm pool, chưa chọn ví, chưa tính điểm, chưa backtest, chưa về trước, chưa áp dụng cơ chế nào vào PaperDesk hay Polymarket.

## Xác nhận bằng chữ (theo mẫu bắt buộc của lệnh Việc 2)

1. Chỉ đổi đúng 1 trạng thái ngưỡng 10.000 USD từ đề xuất thành luật đã duyệt; mọi luật khác giữ nguyên nháp đã kiểm toán (bảng dòng đổi ở trên là toàn bộ khác biệt).
2. Chưa chạy hồ sơ, chưa chạy backtest, chưa chạy về trước.
3. Chưa sửa spec sau khi đóng băng; sau khi tính hash và sau khi push KHÔNG sửa file nào nữa.
4. Chưa áp dụng cơ chế nào vào PaperDesk hay Polymarket.
