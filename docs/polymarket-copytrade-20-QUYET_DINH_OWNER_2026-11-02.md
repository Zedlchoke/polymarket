# QUYẾT ĐỊNH CỦA CHỦ NHÂN — DỰ ÁN COPY TRADE 20 TÀI KHOẢN POLYMARKET
Ngày ghi: 2026-11-02, sau khi chủ nhân nói "okay làm v đi" với phương án "nếu tôi là bạn" đã đề xuất.
Trạng thái: ĐÃ QUYẾT VỀ HƯỚNG VÀ CÁC ĐÁP ÁN D1–D5, CHƯA ĐÓNG BĂNG, CHƯA CÓ LỆNH GO CHO BACKTEST.
File này chỉ ghi quyết định, không phải spec đóng băng, không có hash đóng băng.

## Tin nhắn lỗi trước đó
Tin nhắn chỉ toàn dấu nháy ngay trước câu "okay làm v đi" được hiểu là gửi nhầm, không phải một nhiệm vụ mới.
Công việc đang làm không bị bỏ, vẫn tiếp tục theo câu "okay làm v đi".

## Quyết định D1–D5 — đã chốt theo đáp án đề xuất

- D1: Giải lớn chiếm trên 50% lãi ngoài mẫu chỉ là CỜ CẢNH BÁO, không phải cổng giết ở v1.
  Báo cáo phải ghi rõ khi cờ này bật, nhưng cờ này không tự lật verdict chính.
- D2: Test giấy về trước dùng NHÓM MỚI, chọn lại bằng đúng luật Q3 từ 90 ngày trước ngày GO.
  Test này test luật, không test 20 ví cũ đã 12–15 tháng.
- D3: Mỗi nhóm đếm từ 100 USD ròng trở lên, tổng tiền ròng các nhóm đếm từ 500 USD trở lên.
  Không dùng mức 200 USD của góc thực hành.
- D4: Cửa sổ overlap 24 giờ, kèm chặn giá chạy quá 0,10 so với giá của nhóm đầu tiên.
  Không dùng cửa sổ 6 giờ ở v1. Cửa sổ 6 giờ chỉ là báo cáo phụ, không dùng để chọn k*.
- D5: Ngưỡng chọn người là 80 lệnh giao dịch trong 90 ngày chọn, kèm các lọc Q3 khác.
  Không dùng ngưỡng 100 lệnh ở v1.

## Quyết định §19 — đã chốt theo hướng đề xuất, trừ các mục cần đọc văn bản trong file V2

- 19.1 Nhận diện thể thao bằng tag 'Sports': DUYỆT VỀ HƯỚNG, với điều kiện file V2 cho thấy đủ 23 mẫu thật và luật viết thành từng bước.
- 19.2 Ưu tiên nguồn chốt là resolutions.payouts, lệch thì dừng và báo: DUYỆT.
- 19.3 Cửa 999 loại ra + đếm riêng + báo động trên 5%: DUYỆT LÀM BÁO ĐỘNG, chưa nâng thành cổng giết.
- 19.4 Nguồn tiền mặt chính là usdc_size trên activity, trades dùng để đối chiếu: DUYỆT.
- 19.5 Pool ứng viên bắt đầu từ leaderboard tháng, rồi tự tính 90 ngày cho pool đó, kèm cách đo thiên lệch: DUYỆT VỀ HƯỚNG, với điều kiện cách đo thiên lệch phải được viết rõ trong spec.
- 19.6 Ngày chốt đổi về giây UTC, làm tròn xuống giây: DUYỆT.
- 19.7 Làm tròn giá / cổ phần / phí: CHƯA DUYỆT CHI TIẾT, phải đọc văn bản đề xuất trong file V2 rồi mới duyệt.
- 19.8 Cách chọn mốc tuyệt đối T0–T3: CHƯA DUYỆT CHI TIẾT, phải chốt mốc tuyệt đối sau khi kiểm toán file V2.
- 19.9 Đo spread cho test về trước: DUYỆT VỀ HƯỚNG, với điều kiện chu kỳ thăm dò và cách tính spread phải được viết rõ trong spec.

## Kế hoạch tiếp theo đã duyệt — theo đúng thứ tự, không đảo thứ tự

1. Chuyển file V2: chủ nhân chuyển spec V2 + báo cáo V2, tốt nhất kèm log thăm dò, cho coordinator qua link lưu trữ kèm mã hash từng file.
   Coordinator mở file gốc và kiểm toán từng dòng, từng bảng, từng đề xuất §19, trước khi viết spec đóng băng.
   Nếu file V2 không khớp với bản tóm tắt đã gửi qua chat thì dừng và báo lệch, không dùng bản tóm tắt thay file gốc.
2. Viết spec đóng băng v1 từ file tổng hợp 6 góc nhìn + các quyết định trên + văn bản §19 đã duyệt chi tiết.
   Ghi sha256 của spec đóng băng, đưa chủ nhân kiểm tra, rồi mới có lệnh GO riêng cho bước tiếp theo.
   Không có lệnh GO riêng thì không chạy hồ sơ 20 nhóm, không chạy backtest, không chạy test giấy về trước.
3. Hồ sơ 20 nhóm + backtest dưới spec đã đóng băng, với trần ngân sách đã duyệt:
   - Sàng lọc rẻ trước: kiểm tra cả hai cửa, khối lượng, lãi giữ-tới-chốt trên mẫu nhỏ, ví nào qua cửa mới đi sâu.
     Ví nhiều lệnh kiểu UpTheBlues không được đi hết lịch sử bằng mọi giá.
   - Tối đa khoảng 200 request/ngày, đi chậm 10 giây/request, gặp watchdog chậm bất thường, 429 hay 403 thì dừng và nghỉ, không tăng tốc bù.
   - Hạn 14 ngày cho bước hồ sơ. Hết hạn mà k≥3 vẫn không đủ 100 tín hiệu trong mẫu thì chấp nhận theo luật đã viết:
     chuyển sang k đủ mẫu hoặc ghi thiếu mẫu, không hạ ngưỡng, không đổi cửa sổ, không đổi k sau khi thấy ngoài mẫu.
4. Ưu tiên học tập trong tuần này: LJ2 hạn chủ nhật 08/11/2026 17:00, không được nộp muộn, vẫn là việc cần xong trước.
   Việc đóng băng Polymarket có thể chờ sau khi kiểm toán file V2, không cần vội mà sai.

## Việc KHÔNG làm theo quyết định này

- Không đánh tiền thật, không xây bot copy thật, không nối ví, không tạo tài khoản mới, không dùng VPN.
- Không sửa spec sau khi thấy kết quả hồ sơ hay backtest. Muốn đổi thì viết spec mới, đặt tên mới.
- Không dùng bản tóm tắt chat thay cho file gốc để đóng băng.
- Không tự ý nâng cờ D1 hay báo động 999 thành cổng giết sau khi đã đóng băng.
