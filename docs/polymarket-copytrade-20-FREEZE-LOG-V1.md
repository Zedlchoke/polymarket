# FREEZE LOG — SPEC v1 ĐÓNG BĂNG — DỰ ÁN COPY TRADE 20 TÀI KHOẢN POLYMARKET

## Thông tin đóng băng

- **Ngày đóng băng:** 2026-11-02 (UTC).
- **File đóng băng:** `~/workspace/your_files/polymarket-copytrade-20-SPEC-V1-FROZEN.md`
- **Căn cứ lệnh:** prompt của chủ nhân ngày 2026-11-02 ("đóng băng, backtest, kiểm tra overlap với PaperDesk"), sau khi chủ nhân chọn **mốc B** và duyệt hết theo khuyến nghị; coordinator chọn B theo ủy quyền.
- **Điểm dừng bắt buộc đã giữ:** Việc A (đóng băng) xong thì **DỪNG**, chờ chủ nhân kiểm tra hash và ra lệnh "hash đúng, chạy tiếp" thì mới chạy Việc B (hồ sơ + backtest) và Việc C (overlap). **Prompt lần này KHÔNG chứa câu "bỏ qua kiểm tra hash, chạy luôn" nên không có lệnh bỏ qua nào được ghi ở đây.**

## Mã hash

| Đại lượng | Giá trị |
|---|---|
| **SHA256 nội dung spec đóng băng, không kể dòng hash** (con số in ở đầu file spec) | `d7b4c39b7dda6a43f4ff3d4717bf5e63fed734e305496bc1813e952c3be6a9f7` |
| SHA256 toàn file (kể cả dòng hash) | `e98691e2c555a326c59a92633a22864e04152109c9e48b8cc8457f9b7a5cb61f` |

**Công thức kiểm chứng (bất kỳ ai cũng lặp lại được):**

```python
import hashlib
p = "polymarket-copytrade-20-SPEC-V1-FROZEN.md"
lines = open(p, encoding="utf-8").read().split("\n")
i = [k for k, l in enumerate(lines) if l.startswith("SHA256 (tính trên")][0]
content_wo = "\n".join(lines[:i] + lines[i+1:])          # xóa hẳn dòng hash
print(hashlib.sha256(content_wo.encode()).hexdigest())   # phải ra d7b4c39b…be6a9f7
print(hashlib.sha256(open(p, "rb").read()).hexdigest())  # phải ra e98691e2…a5cb61f
```

## File nguồn và hash

| File | sha256 | Vai trò |
|---|---|---|
| `polymarket-copytrade-20-answers-SYNTHESIS-6-GOC.md` | `cf6f7560c4dc6a1ff4f56bfb7925ba955bcc67b6768072d7cc088868764a4617` | Q1–Q10, công thức, cổng giết 3 tầng |
| `polymarket-copytrade-20-QUYET_DINH_OWNER_2026-11-02.md` (bản coordinator) | `01248d550391824d208a5bf49ca6650054d8f179950e32b4fcc11edce939a3a0` | D1–D5, §19 |
| Prompt chủ nhân 2026-11-02 (đóng băng/backtest/overlap) | văn bản lệnh trong chat | Mốc B + 7 mục duyệt chi tiết (liệt kê nguyên văn tại mục 15 spec đóng băng) |
| `polymarket-copytrade-20-SPEC-V1-CANDIDATE-V2.md` | `2f69fdc103dafebabe5a2be8e67167c432b7ee9d97879ed203c3faa3c8dac276` | Bản ứng viên đã đối chiếu — KHÔNG lệch với 7 quyết định (bảng dưới) |
| `polymarket-copytrade-20-PROBE-REPORT-V2.md` | `2782eb5cd6bd3b03264c9fa5717245e541605bab0589fdd54865c1a529b43c32` | Tên trường, phí đo thật, resolutions |
| `polymarket-copytrade-20-SPEC-V1-DRAFT-V2.md` | `8e108e30612c0997ca3a708468247f890916a92058d79a934e9dc7ba08153406` | Spec nháp V2 (nguồn tên trường) |
| `polymarket-copytrade-20-SPEC-V1-CANDIDATE.md` | `0cc4680515f02d7f585a6f393b87ce662058ac37ce96fe03c75de95be979938f` | Bản ứng viên V1 (lịch sử) |
| `polymarket-copytrade-20-QUYET_DINH_OWNER_2026-11-02_BAN-DAN-CHAT-DAU.md` | `6772eec7a4eeda6102b017a8ba241f325d11f9ff0afd40b3ab9a24214a511c7f` | Bằng chứng bản chat (không dùng làm chuẩn) |

Code đi kèm: `~/Downloads/Polymarket/copytrade_build_v2/` — 10 file, test dữ liệu giả 120/120 pass (`tests/test_report_v2.json`). Không thay đổi code sau thời điểm đóng băng (trừ lỗi cpy pháp không chạm luật — nếu có phải ghi bổ sung vào log này).

## Đối chiếu spec ứng viên V2 với 7 quyết định trước khi đóng băng (bắt buộc, kết quả: KHÔNG LỆCH)

| Quyết định | Spec ứng viên V2 ghi | Kết quả |
|---|---|---|
| Mốc B (T0 13-09-2025, T1 12-12-2025, T2 12-03-2026, T3 10-06-2026) | Đề xuất B mục 2 — trùng từng ngày | KHỚP |
| FEE_MISSING bỏ+đếm riêng+báo động >5%, không cổng | Mục 7 + 20.5 | KHỚP |
| Giải lớn: volume cộng dồn cuối đoạn, ≥8, top 5%, chỉ mô tả | Mục 20.4 | KHỚP |
| 50 ví đối chứng + missed 20% chỉ đo+báo động | Mục 20.6 | KHỚP |
| Spread 5 phút, /book 1 lần, best_ask−best_bid, rỗng→0,02 | Mục 12 | KHỚP |
| Làm tròn 4 chữ số / số lẻ / xu / so ngưỡng trước | Mục 20.3 | KHỚP |
| Tags dự phòng chỉ khi rỗng sau include_tag, đếm tỷ lệ dùng | Mục 20.1 | KHỚP |

## Trạng thái tại thời điểm ghi log này

- Việc A: XONG (file đóng băng + hash + log này).
- Việc B (hồ sơ 20 nhóm + backtest): **CHƯA CHẠY** — chờ chủ nhân kiểm tra hash.
- Việc C (overlap PaperDesk): **CHƯA CHẠY** — chờ cùng lệnh trên.
- Chưa chạy hồ sơ tính điểm, chưa chạy backtest tính điểm, chưa chọn k*, chưa có verdict.
