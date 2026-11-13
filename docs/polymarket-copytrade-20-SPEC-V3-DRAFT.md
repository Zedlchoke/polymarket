# SPEC v3 NHÁP — POOL THEO VÍ (STAGED FUNNEL) — 2026-11-13

**⛔ CHƯA ĐÓNG BĂNG — CHƯA CÓ HASH — CHƯA CHẠY GÌ THEO SPEC NÀY.** Nháp để chủ nhân duyệt + kiểm toán độc lập + đóng băng, đúng quy trình v2 đã đi.

## 0. Vì sao phải có v3 (số đo thật, không đoán)

- Pilot 12/11 (`b32983a`): lấy trade theo TỪNG THỊ TRƯỜNG thất bại về chi phí — 1 trận NFL lớn một mình >189 request; ước 46–308 ngày ở ngưỡng 100k; nâng ngưỡng không giúp (tiền tập trung vào trận nhiều lệnh).
- Pilot khám phá 13/11 (hôm nay, 45/200 request): **40 request lấy mẫu 20 trận lớn nhất → 3.290 ví riêng biệt** (20.000 fill mẫu) — tức "ví nghiêm túc" phát hiện được RẺ; nhưng **cursor phân trang theo ví ĐÃ BIẾN MẤT** (đúng limit dòng + cursor=None kể cả không cửa sổ; ngày 03/11 probe còn phân trang 35 trang được) → phải **chia cửa sổ thời gian start/end theo từng ví** (đã xác nhận cửa sổ con hoạt động, timestamp newest-first).

## 1. GIỮ NGUYÊN TỪ v2 (không viết lại)

Mọi luật v2 đóng băng (`ae504a97…`) trừ nguồn pool: Q1–Q10, D1–D5, mốc B (T0 2025-09-13 → T1 2025-12-12, 90 ngày/đoạn), cổng giết 3 tầng, phí/làm tròn/FEE_MISSING, 18 bảng, 50 ví đối chứng, giấy-0-đồng-không-lệnh-thật, kiểm toán độc lập sau mỗi việc, GO riêng từng bước.

## 2. THAY ĐỔI — POOL THEO VÍ QUA PHỄU 4 TẦNG (mọi số dưới đã đo hoặc là cận)

- **Tầng 1 — Lấy mẫu phát hiện (rẻ, đã đo):** top-K thị trường hợp lệ lớn nhất (chọn mẫu bằng volumeNum — CHỈ để chọn thị trường lấy mẫu, khai rõ; pipeline không dùng volumeNum cho ngưỡng) × mỗi thị trường M cửa sổ thời gian × 500 fill → bảng tần suất ví. Đo: K=20, M=2 → 40 request → 3.290 ví. Với K=40, M=4 (kéo dài khắp Đ1) → ~160 request, ước ~8.000–12.000 ví.
- **Tầng 2 — Sàng ứng viên (đề xuất, chờ duyệt):** ví xuất hiện trong ≥N thị trường mẫu (đề xuất N=5) → ước vài trăm – ~1.500 ví "nghiêm túc". Tiêu chí KHÔNG dựa trên lãi (chỉ tần suất/biên độ Đ1 — không tương lai).
- **Tầng 3 — Đo đầy đủ từng ứng viên:** toàn bộ fill Đ1 theo VÍ bằng **chia cửa sổ thời gian** (user + start/end + limit 500; trang đầy 500 → chia đôi cửa sổ đệ quy — kỹ thuật đã kiểm chứng). CHI PHÍ = 2×số_fill/500 request/ví. Ước (cần pilot v3 xác nhận): ví thường 2–20 request; ví nặng 100–800 request (whales là đắt nhất — trần an toàn 40 trang/ví như probe, chạm trần = CẬN DƯỚI, ghi rõ).
- **Tầng 4 — Q3 + gộp nhóm + chọn 20:** đúng luật v2 (10 cửa, ≥20 nhóm, bù đủ) trên dữ liệu tầng 3.
- **Khối lượng công việc (khoảng, chờ pilot v3 đo):** tầng 3 ≈ 5.000–20.000 request ≈ **25–100 ngày @200/ngày** — TỐT HƠN hướng thị trường (46–308) nhưng KHÔNG rẻ. Hạn hồ sơ phải do chủ nhân chốt lại theo số pilot v3.

## 3. Pilot xác nhận v3 (bắt buộc trước khi duyệt hạn): ~150 request, 1 ngày
(1) Tầng 1 mở rộng K=40/M=4; (2) tầng 2 với N=5; (3) đo đầy đủ ~20 ứng viên đầu (trần 40 request/ví) → phân phối request/ví THẬT → chốt ước tổng + hạn. Sau đó: kiểm toán v3 nháp → chủ nhân duyệt + chốt hạn → ĐÓNG BĂNG v3 → mới GO Việc 4 theo v3.

## 4. Rủi ro phải khai sẵn
- Cursor biến mất có thể là thay đổi phía server tạm thời/vĩnh viễn — v3 không phụ thuộc cursor (chia cửa sổ), nhưng phải đo lại ở pilot v3.
- Whales đắt: nếu top-20 tiềm năng toàn whales 300k+ fill → tầng 3 có thể vượt 20.000 request → khi đó trình chủ nhân chọn: trần độ sâu/ví (đổi luật thống kê — phải duyệt) hoặc kéo dài hạn.
- Mẫu tầng 1 lệch về cuối Đ1 nếu cửa sổ mẫu không trải đều — pilot v3 phải trải M cửa sổ đều toàn Đ1.
- volumeNum dùng chọn thị trường lấy mẫu: chỉ mô tả/khai rõ; không ảnh hưởng chọn ví.

## 5. KHÔNG làm (giữ nguyên)
Không chạy hồ sơ/backtest/về trước theo v3 trước khi đóng băng; không sửa spec v2 đã đóng băng; không tính điểm ví nào trong pilot; giấy, 0 đồng, không đụng PaperDesk/Polymarket thật; trần 200/ngày dương lịch giờ VN; kiểm toán độc lập sau mỗi việc.
