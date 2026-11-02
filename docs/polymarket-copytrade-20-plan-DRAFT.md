# Dự án copy trade 20 tài khoản Polymarket — BẢN NHÁP KẾ HOẠCH
Ngày viết: 2026-11-02. Trạng thái: BẢN NHÁP, CHƯA ĐÓNG BĂNG, CHƯA CHẠY.
Không có lệnh thật, không có tiền thật, không nối ví, không vượt rào địa lý.
Chỉ nghiên cứu trên giấy cho tới khi có: spec đóng băng + hash + kiểm toán độc lập + lệnh GO của chủ nhân.

## 1. Kết luận kiểm toán trước khi làm (nói thẳng)

- Ý tưởng copy theo số tài khoản trùng nhau CÓ THỂ test được trên giấy, vì lịch sử ví Polymarket là công khai.
- Nhưng copy mù rất dễ thua, dù tài khoản gốc thắng. Lý do lớn nhất không phải chọn sai người, mà là: giá đã chạy sau khi cá lớn đặt, và nhiều ví trùng nhau thực ra là cùng một người.
- Vì vậy dự án này KHÔNG được duyệt làm lệnh thật từ bản nháp này. Nó chỉ được đi tiếp theo từng cửa: thăm dò dữ liệu → hồ sơ 20 tài khoản → spec đóng băng → backtest giấy → kiểm toán → test giấy về trước.

## 2. Điểm mạnh của ý tưởng

1. Dữ liệu công khai, không cần tài khoản, không tốn tiền để đọc: Data API v2 cho vị thế, hoạt động, giao dịch theo ví.
2. Tín hiệu trùng nhau có thể lọc nhiễu: một lệnh đơn lẻ có thể là may rủi, nhiều ví độc lập cùng vào một cửa thì ít may rủi hơn — nếu chứng minh được họ độc lập.
3. Có thể đo được độ trễ và giá trượt: ta không dùng giá của cá lớn, ta dùng giá mà người copy thực sự mua được sau đó.
4. Có thể tách theo loại thị trường: thể thao, chính trị, crypto, thời tiết... mỗi loại có tốc độ và thanh khoản khác nhau.

## 3. Điểm yếu — đây là phần quan trọng nhất

1. **Trùng ví không bằng trùng người.** Ví dụ đã thấy ngoài đời: một người có thể cầm tới 11 ví. Đếm 5 ví mà thực ra là 1 người thì tín hiệu bị thổi phồng.
2. **Người thắng dài hạn cũ có thể đã nghỉ.** Top lãi mọi thời đại đa số là người đặt bầu cử 2024, giao dịch gần nhất từ 2024. Chọn theo mọi thời đại sẽ copy người không còn chơi.
3. **Market maker (người tạo thanh khoản) trông rất thắng về khối lượng nhưng không phải dân đoán hướng.** Họ mua cả hai cửa, lãi nhỏ trên chênh lệch. Copy một phía của họ là copy nửa lệnh.
4. **Độ trễ giết edge.** Dữ liệu công khai bị trễ so với lệnh thật. Nghiên cứu ngoài đã ghi: thăm dò API 3–10 giây, WebSocket 1–3 giây, còn cửa arbitrage rút ngắn còn ~2,7 giây. Người copy mua sau thì giá đã xấu hơn.
5. **Giá trượt và thanh khoản.** Thị trường nhỏ: lệnh copy chen vào làm giá xấu thêm. Thị trường lớn: cá lớn đã đẩy giá trước khi ta thấy.
6. **Đếm mua mà quên bán.** Chỉ đếm lệnh mua sẽ đếm trùng người đã bán ra sau đó, hoặc người đang phòng hộ (hedge) cửa ngược lại ở ví khác.
7. **Chọn 20 người sau khi đã thấy họ thắng = chọn lọc may rủi.** Nếu chọn 20 người vì họ vừa thắng, rồi lại test trên cùng đoạn họ vừa thắng, kết quả sẽ đẹp giả.
8. **Tín hiệu trùng nhau hiếm.** Đòi 5/20 trùng một lệnh thì số tín hiệu có thể quá ít để kết luận. Đòi 2/20 thì nhiễu nhiều.
9. **Giới hạn API.** Nhóm đã từng dính HTTP 429 ở Polymarket data_api ngày 2026-10-23. Luật: gặp 429 thì dừng, không cày lại, không lách.
10. **Pháp lý và tài khoản.** Không làm lệnh thật, không tạo tài khoản mới, không dùng cách lách rào địa lý để vào sàn. Phần này chỉ là nghiên cứu giấy.

## 4. Định nghĩa phải đóng băng trước khi chạy — không được sửa sau khi thấy kết quả

Mỗi mục dưới đây phải có đáp án của chủ nhân rồi mới đóng băng:

- **Q1. Phạm vi thị trường:** tất cả, hay chỉ một loại (đề xuất bắt đầu: chỉ một loại, ví dụ thể thao, để khỏi trộn tốc độ khác nhau)?
- **Q2. Cửa sổ chọn 20 tài khoản:** 30 ngày, 90 ngày, hay 6 tháng gần nhất? Tuyệt đối không dùng mọi thời đại.
- **Q3. Luật chọn 20 tài khoản (viết trước, không nhìn kết quả overlap):** ví dụ: lãi trong cửa sổ + tối thiểu bao nhiêu lệnh + còn hoạt động trong 7 ngày gần nhất + loại market maker bằng cách nào.
- **Q4. Overlap là gì, đúng từng chữ:** cùng một mã thị trường (conditionId) + cùng một cửa (YES hay NO) + trong bao nhiêu giờ + mỗi ví tối thiểu bao nhiêu tiền + tính theo ví hay tính theo người (gộp ví nghi cùng chủ)?
- **Q5. Giá copy trên giấy:** giá tại thời điểm phát hiện + phạt trễ (ví dụ cộng thêm chênh lệch giá), không dùng giá gốc của cá lớn.
- **Q6. Tiền giấy mỗi tín hiệu:** cố định (ví dụ 100 USD giấy), không gấp thếp, không dồn vốn.
- **Q7. Thoát lệnh trên giấy:** giữ tới khi thị trường chốt, hay thoát khi giá tới một mức? Phải chọn một, không đổi giữa chừng.
- **Q8. Ngưỡng k cần test:** k = 2, 3, 4, 5... trên 20. Chỉ tối ưu k trên tập trong mẫu (in-sample), rồi khóa k lại và test trên tập chưa nhìn (holdout). Không được đổi k sau khi thấy holdout xấu.
- **Q9. Cổng giết (kill gate):** đề xuất: tối thiểu 200 tín hiệu overlap, lãi ròng sau phạt trễ và trượt giá phải dương ở cả in-sample và holdout, và không được chỉ thắng nhờ 1–2 lệnh lớn.
- **Q10. Thời gian test giấy về trước:** đủ tín hiệu + đủ tháng, không hứa ngày thắng trước khi đo tốc độ thật.

## 5. Các bước làm, theo thứ tự

### Bước 0 — Chủ nhân chốt Q1–Q10
Chưa chốt thì chưa đóng băng, chưa chạy. Bản này vẫn là nháp.

### Bước 1 — Thăm dò dữ liệu, chỉ đọc (0 đồng)
- Thử thật 1 lần mỗi đầu mối cần dùng: Data API v2 `/positions`, `/activity`, `/trades`, và bảng xếp hạng công khai; Gamma API để lấy tên thị trường và kết quả chốt.
- Ghi lại: trường nào là mã thị trường, trường nào là cửa YES/NO, trường nào là giá, trường nào là thời gian, phân trang ra sao, dữ liệu trễ bao nhiêu, giới hạn gọi bao nhiêu.
- Đo tỷ lệ khớp (overlap) giữa mã thị trường của Data API và Gamma. Không khớp được thì dừng ở đây, ghi là thiếu dữ liệu, không đoán.
- Gặp 429, 403, timeout: ghi đúng lỗi, dừng, không cày lại.

### Bước 2 — Hồ sơ 20 tài khoản, chỉ mô tả, chưa kết luận
Với mỗi tài khoản, tính trên cùng cửa sổ Q2:
- lãi/lỗ, khối lượng, số lệnh, số thị trường, loại thị trường hay chơi, tỷ lệ thắng, tiền trung bình mỗi lệnh, thời gian giữ lệnh, còn hoạt động gần nhất khi nào.
- Tỷ lệ mua cả hai cửa (dấu hiệu market maker / phòng hộ).
- Ma trận trùng nhau giữa các tài khoản: cặp nào hay cùng vào một lệnh, cùng giờ, cùng cỡ tiền — dấu hiệu nghi cùng một người.
- Xếp nhóm kiểu chơi: cá lớn tập trung, market maker, chuyên một môn, săn nhanh (sniper), còn lại.
- Bước này không được dùng để đổi luật chọn người. Người đã chọn là người đã chọn.

### Bước 3 — Đóng băng spec v1 + hash
- Viết spec đầy đủ một file, ghi rõ Q1–Q10, công thức tính, và phép tính số mẫu tối đa: số tín hiệu overlap tối đa = tốc độ đo ở Bước 1 × độ dài cửa sổ. Nếu số tối đa còn dưới 200 thì không đóng băng — phải nới cửa sổ hoặc đổi định nghĩa overlap trong bản nháp mới, không hạ cổng giết.
- Ghi sha256 của file spec trước khi chạy bất cứ test nào tính điểm.

### Bước 4 — Backtest giấy, giá copy (không phải giá gốc)
- Với mỗi tín hiệu overlap đạt ngưỡng k, mô phỏng mua trên giấy tại giá phát hiện + phạt trễ + trượt giá.
- Tính lãi/lỗ tới khi chốt thị trường, theo từng k, theo từng loại thị trường, theo từng nhóm tài khoản.
- Báo cáo phải tách: lãi do giá chạy đúng hướng, và phần mất do mua muộn / trượt giá. Nếu lãi gộp dương nhưng sau phạt trễ thành âm thì kết luận là âm.
- Chia in-sample / holdout theo thời gian, không xáo trộn. Tối ưu k chỉ trên in-sample.

### Bước 5 — Kiểm toán độc lập (bắt buộc trước khi tính là verdict)
Kiểm toán trả lời 3 câu:
1. Làm có chuẩn không (đúng spec, đúng mã, không rò rỉ dữ liệu tương lai, không dùng giá gốc thay giá copy)?
2. Đã cố hết sức trong luật đóng băng chưa?
3. Còn đường hợp lệ nào không, hay đã tịt hẳn? Đường tiếp theo (nếu có) phải là spec mới, không sửa lén spec cũ.
- Kết quả: CONFIRMED / BUG FOUND (dừng verdict, sửa mã, chạy lại spec cũ sạch) / SPEC FLAW (viết spec v2 mới, không chạy lén).

### Bước 6 — Chỉ khi Bước 5 CONFIRMED và backtest qua cổng giết: test giấy về trước
- Thu thập tín hiệu mới phát sinh, ghi sổ giấy, không đặt lệnh thật.
- Ngày phán xét đặt trước, dựa trên tốc độ tín hiệu thật: đủ 200 tín hiệu + đủ tháng, không phán sớm vì vài tuần đầu đẹp.

## 6. Cách tối ưu quy luật overlap — đúng luật, không tối ưu lén

- Đừng tìm k đẹp nhất trên toàn bộ dữ liệu rồi báo cáo k đó như thể đã thắng. Đó là gian lận mẫu.
- Cách đúng: chia thời gian làm 2. Tìm k tốt nhất trên nửa đầu, khóa k, chỉ test một lần trên nửa sau.
- So sánh thêm 2 biến, nhưng cũng phải khóa trước: đếm theo ví hay đếm theo tiền (ví dụ tổng tiền của nhóm trùng nhau), và cửa sổ trùng nhau là 1 giờ, 6 giờ hay 24 giờ.
- Nếu k cao cho lãi cao nhưng tín hiệu quá ít, đó không phải là thắng — đó là thiếu mẫu. Ghi rõ, không gộp tín hiệu ít với tín hiệu nhiều để làm đẹp.
- Nếu nhiều ví trùng nhau nhưng thực ra là cùng một người, phải báo cáo cả hai bảng: đếm theo ví và đếm sau khi gộp nhóm nghi cùng chủ. Bảng gộp mới là bảng tính điểm chính nếu nghi ngờ có căn cứ.

## 7. Kết quả cuối cùng sẽ rơi vào đúng 1 hộp

1. **Sống (Box 1):** spec đóng băng + backtest qua cổng giết + kiểm toán CONFIRMED + test giấy về trước đạt. Khi đó mới bàn bước tiếp theo, vẫn chưa phải lệnh thật.
2. **Chết (Box 2):** không qua cổng giết, hoặc lãi bay hết sau phạt trễ. Ghi rõ chết vì đâu: trễ, trượt giá, trùng người, hay tín hiệu quá ít.
3. **Thiếu dữ liệu (Box 3):** API chặn, không lấy đủ lịch sử, không khớp mã thị trường, hoặc tín hiệu tối đa dưới 200 mà không nới được cửa sổ trong luật 0 đồng.

## 8. Việc KHÔNG làm trong dự án này

- Không nối ví, không tạo tài khoản Polymarket mới, không đặt lệnh thật.
- Không dùng VPN hay cách lách rào địa lý.
- Không mua dữ liệu trả phí, không thuê bot copy có sẵn.
- Không đổi spec sau khi thấy kết quả. Muốn đổi thì viết spec mới, đặt tên mới.
- Không báo cáo kết quả thăm dò (Bước 1–2) như thể đã là verdict.

## Nguồn tra cứu cho bản nháp này (đọc ngày 2026-11-02)

- Data API công khai, không cần đăng nhập để đọc vị thế / hoạt động / giao dịch theo ví; v2 là bản hiện tại.
- Bảng xếp hạng công khai theo lãi / khối lượng; top mọi thời đại khác xa top đang hoạt động gần đây.
- Nghiên cứu ngoài ghi nhận: một người có thể cầm nhiều ví; độ trễ phát hiện 3–10 giây khi thăm dò, 1–3 giây khi dùng WebSocket; không có backtest hệ thống nghiêm ngặt nào đã công bố cho copy trade Polymarket.
- Lưu ý: các nguồn ngoài có thể cũ hoặc khác bản API hiện tại. Bước 1 thăm dò thật sẽ là căn cứ cuối cùng, không phải bài viết ngoài.
