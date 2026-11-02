# Trả lời 10 câu hỏi — BẢN ĐỀ XUẤT, CHƯA ĐÓNG BĂNG
Ngày: 2026-11-02. Đây là đáp án do tôi nghiên cứu và đề xuất thay bạn.
Chưa phải spec đóng băng. Chỉ khi bạn duyệt cả bộ này, tôi mới viết spec đóng băng + hash, rồi mới chạy.
Không lệnh thật, không tiền thật ở bất cứ bước nào dưới đây.

## Sửa quan trọng sau khi nghiên cứu lại

Bản nháp trước chỉ tính phạt trễ 0,02. Nghiên cứu mới cho thấy chưa đủ:
- Polymarket nay thu phí người mua khớp ngay (taker). Thể thao là 0,05, công thức: phí = số cổ phần × 0,05 × giá × (1 − giá).
- Ví dụ: giá 0,50, mua 200 cổ phần bằng 100 USD giấy thì phí = 200 × 0,05 × 0,50 × 0,50 = 2,50 USD.
- Người đặt lệnh chờ (maker) thì phí 0, nhưng người copy đuổi theo giá thì là taker, nên phải chịu phí này.
- Vì vậy Q5 dưới đây tính cả phí taker + phạt trễ 0,02. Nếu bỏ phí, kết quả sẽ đẹp giả.

Một sửa nữa về dữ liệu, rút từ chính lịch sử nhóm:
- Tài liệu ghi giới hạn Data API v2 khá cao theo 10 giây, nhưng nhóm đã dính chặn 429 tới 3 lần khi kéo nhiều trận liên tục, dù đã đi chậm 1 giây rồi 2,5 giây.
- Nghĩa là giới hạn thực tế có tính tích lũy, không chỉ tính theo giây. Bước thăm dò phải kéo ít, kéo chậm, theo cửa sổ thời gian, và dùng v2, không cày hàng nghìn thị trường một lúc.
- Data API mặc định chỉ hiện lệnh taker (takerOnly=true), lệnh maker bị giấu. Khi lấy lịch sử phải đặt takerOnly=false, nếu không sẽ thiếu một phía của ví.

## Dòng thời gian chống gian lận mẫu — áp cho mọi câu dưới

Chia quá khứ làm 3 đoạn liên tiếp, không trùng nhau:
- Đoạn 1 — Chọn người: 90 ngày.
- Đoạn 2 — Tìm k tốt nhất (in-sample): 90 ngày ngay sau đoạn 1.
- Đoạn 3 — Test k đã khóa (holdout): 90 ngày ngay sau đoạn 2.
Tổng cần khoảng 9 tháng lịch sử. Người được chọn bằng đoạn 1, rồi mới copy ở đoạn 2 và 3. Không được chọn người bằng đoạn 2 rồi lại test trên đoạn 2.
Nếu thăm dò cho thấy không lấy đủ 9 tháng cho cả 20 ví, thì rút mỗi đoạn xuống 60 ngày trong bản nháp mới, không hạ cổng giết 200 tín hiệu.

## Q1. Phạm vi thị trường — Đáp án: CHỈ THỂ THAO

- Chỉ thể thao, tất cả các môn thể thao, không trộn chính trị, crypto, thời tiết.
- Lý do 1: thể thao chốt nhanh. Thị trường thể thao chốt trong vài giờ sau khi trận xong, trong khi thị trường chính trị có thể giữ vốn hàng tháng.
- Lý do 2: có nhiều trận mỗi ngày, nên đủ tín hiệu nhanh hơn chính trị.
- Lý do 3: phí thể thao 0,05 thấp hơn crypto 0,07, và crypto 15 phút thì bot chiếm ưu thế về tốc độ, người copy càng bất lợi.
- Nhược điểm phải báo cáo: World Cup có thể làm lệch. Báo cáo chính vẫn tính cả World Cup, nhưng báo cáo phụ tách riêng World Cup. Nếu lãi holdout chỉ nhờ World Cup thì ghi rõ là yếu, dù có qua cổng giết.

## Q2. Cửa sổ chọn 20 tài khoản — Đáp án: 90 NGÀY, TRƯỚC ĐOẠN TEST

- 90 ngày, là đoạn 1 ở trên, kết thúc ngay trước đoạn in-sample.
- Không dùng 30 ngày: 30 ngày quá ngắn, một chuỗi may mắn vài tuần đã lên top.
- Không dùng 6 tháng: 6 tháng trộn nhiều mùa giải và người đã nghỉ vẫn còn trong bảng.
- Không dùng mọi thời đại: top mọi thời đại đa số là người bầu cử 2024, nhiều người đã không chơi từ 2024.
- Thêm điều kiện còn chơi: ít nhất 1 lệnh trong 7 ngày cuối của đoạn chọn.

## Q3. Luật chọn 20 tài khoản — Đáp án: LỌC TRƯỚC, RỒI XẾP THEO LÃI RÒNG

Tất cả tính chỉ trên thể thao, chỉ trong đoạn chọn 90 ngày. Một ví muốn vào top phải qua hết các cửa sau:
1. Khối lượng thể thao ≥ 50.000 USD trong 90 ngày. Cửa này loại ví nhỏ lãi % khủng nhưng tiền thật quá ít.
2. Số lệnh đã chốt ≥ 50 lệnh. Loại người thắng 1–2 lệnh lớn.
3. Số thị trường khác nhau ≥ 20 thị trường. Loại người chỉ thắng một sự kiện.
4. Lãi ròng đã chốt > 0 USD. Lãi chưa chốt không tính.
5. Còn hoạt động: ≥ 1 lệnh trong 7 ngày cuối đoạn chọn.
6. Một thị trường không chiếm quá 50% tổng lãi. Loại người thắng nhờ một trận duy nhất.
7. Loại market maker / phòng hộ: nếu trên 30% số thị trường của ví đó từng giữ cả YES và NO cùng lúc thì loại.
8. Loại bot tạo thanh khoản: nếu trên 2.000 lệnh trong 90 ngày mà lãi / khối lượng < 1% thì loại, dù lãi ròng dương.
9. Sau khi lọc, xếp theo lãi ròng đã chốt từ cao xuống thấp, lấy 20 ví đầu.
10. Gộp nhóm nghi cùng một người: nếu 2 ví có ≥ 70% lệnh trùng nhau (cùng thị trường, cùng cửa, trong 10 phút) thì chỉ giữ ví lãi cao hơn, lấy ví xếp hạng tiếp theo bù vào. Số nhóm sau khi gộp mới là số đếm cho Q4.

## Q4. Overlap là gì — Đáp án: VIẾT ĐÚNG TỪNG CHỮ NHƯ SAU

Một tín hiệu overlap được tính khi đủ hết:
- Cùng một mã thị trường (conditionId).
- Cùng một cửa: cùng YES hoặc cùng NO, không tính cửa ngược.
- Trong cửa sổ trượt 24 giờ: ví thứ k vào trong 24 giờ tính từ ví đầu tiên trong nhóm, không phải theo ngày lịch.
- Kích hoạt ngay khi ví thứ k vào, không chờ hết 24 giờ mới copy.
- Mỗi ví đếm phải mua ít nhất 50 USD tiền mặt (số cổ phần × giá) cho cửa đó.
- Ví nào trong 24 giờ đó cũng mua cửa ngược của cùng thị trường thì ví đó không được đếm (đang phòng hộ).
- Thị trường tại lúc kích hoạt phải có tổng khối lượng ≥ 10.000 USD.
- Giá copy sau phạt (xem Q5) phải nằm trong 0,10–0,90. Ngoài khoảng này thì bỏ tín hiệu, vì lãi tối đa quá nhỏ so với phí, hoặc quá giống vé số.
- Mỗi cặp thị trường + cửa chỉ copy đúng 1 lần, là lần kích hoạt đầu tiên. Khi k tăng lên 6, 7 sau đó thì không mua thêm.

## Q5. Giá copy trên giấy — Đáp án: GIÁ SAU KÍCH HOẠT + PHẠT TRỄ + PHÍ TAKER

- Không dùng giá của cá lớn. Giá copy = giá của giao dịch đầu tiên trong cùng thị trường đó, xảy ra sau thời điểm kích hoạt.
- Nếu trong 60 phút sau kích hoạt không có giao dịch nào thì bỏ tín hiệu, không tự đoán giá khớp.
- Cộng phạt trễ 0,02 vào giá mua (mua YES giá 0,50 thì tính như mua 0,52).
- Cộng phí taker thể thao: phí = số cổ phần × 0,05 × giá × (1 − giá), với giá là giá copy trước phí.
- Tỷ lệ phí phải xác nhận lại ở bước thăm dò trước khi đóng băng, vì sàn đã đổi phí từ 0,03 lên 0,05 trong năm 2026. Nếu thăm dò thấy khác 0,05 thì sửa spec trước khi đóng băng, không sửa sau khi thấy kết quả.
- Báo cáo nhạy cảm: tính lại kết quả với phạt trễ 0,05 thay cho 0,02. Nếu đổi phạt mà lãi thành âm thì ghi rõ là mong manh.

## Q6. Tiền giấy mỗi tín hiệu — Đáp án: 100 USD GIẤY CỐ ĐỊNH

- Mỗi tín hiệu copy đúng 100 USD giấy để mua cổ phần, chưa tính phí. Phí tính thêm ngoài 100 USD.
- Thắng thì nhận số cổ phần × 1 USD. Thua thì mất 100 USD + phí.
- Không gấp thếp, không dồn lãi vào lệnh sau, không nhân đôi khi thua.
- Vốn giấy danh nghĩa 10.000 USD chỉ để trình bày, không dùng để tính lãi kép. Lãi tính trên tổng tiền đã đặt (tổng stake), không tính trên vốn danh nghĩa.
- Không giới hạn số tín hiệu mỗi ngày trong v1, để khỏi làm méo mẫu. Nhưng nếu một ngày có trên 20 tín hiệu thì báo cáo phải gắn cờ tập trung ngày đó.

## Q7. Thoát lệnh trên giấy — Đáp án: GIỮ TỚI KHI CHỐT, KHÔNG BÁN GIỮA CHỪNG

- Giữ tới khi thị trường chốt chính thức. Thắng nhận 1 USD mỗi cổ phần, thua nhận 0.
- Không đặt chốt lãi, không đặt cắt lỗ, không bán sớm vì giá đẹp. V1 phải có một luật thoát duy nhất, không tối ưu luật thoát.
- Thị trường tranh chấp: chờ chốt cuối cùng, không tính theo đề xuất chưa chốt.
- Thị trường hủy / trả 50-50: trả lại 100 USD stake, phí đã mất không lấy lại, tín hiệu đó ghi riêng là hủy, không tính là thắng hay thua.
- Nhược điểm phải ghi rõ: cá lớn có thể bán sớm lấy lãi, còn bản copy giữ tới chốt thì kết quả khác với lãi thật của cá lớn. Đó là một phần của test, không phải lỗi tính.

## Q8. Ngưỡng k cần test — Đáp án: THỬ k = 1 ĐẾN 5, CHỈ TỐI ƯU TRÊN IN-SAMPLE

- Thử k = 1, 2, 3, 4, 5. Trong đó k = 1 là mốc đối chứng: copy bất cứ lệnh nào của top 20, không cần trùng nhau.
- Chỉ tìm k tốt nhất trên đoạn in-sample (đoạn 2). Một k muốn được chọn phải có ít nhất 50 tín hiệu trong in-sample.
- k* = k có lãi ròng trên tổng stake cao nhất trong in-sample, trong số k đủ 50 tín hiệu. Nếu bằng nhau thì chọn k có nhiều tín hiệu hơn.
- Khóa k* lại, test đúng một lần trên holdout (đoạn 3). Không được đổi k* sau khi thấy holdout.
- Báo cáo phụ, không dùng để chọn k*: đếm theo tổng tiền của nhóm trùng nhau, thay vì đếm theo số ví. Nếu đếm theo tiền thắng mà đếm theo ví thua thì ghi rõ hai bảng khác nhau.

## Q9. Cổng giết — Đáp án: PHẢI QUA HẾT, THIẾU MỘT LÀ CHẾT

Tất cả tính ở k* đã khóa, trên holdout, sau phí taker + phạt trễ 0,02:
1. Số tín hiệu: in-sample ≥ 100, holdout ≥ 100, tổng ≥ 200.
2. Holdout lãi ròng > 0.
3. Holdout lãi ròng vẫn > 0 khi đổi phạt trễ lên 0,05 (test độ cứng).
4. Holdout lãi / tổng stake > 5%.
5. Holdout lãi / tổng stake cao hơn mốc k = 1. Overlap phải hơn copy đơn lẻ, nếu không thì overlap không thêm giá trị.
6. 5 tín hiệu lãi lớn nhất trong holdout đóng góp dưới 50% tổng lãi holdout. Tránh thắng nhờ 1–2 trận may mắn.
- Nếu thiếu bất cứ điều nào thì verdict là CHẾT, không sửa k, không sửa giá, không sửa luật chọn người. Muốn thử hướng khác thì viết spec v2 mới.

## Q10. Thời gian test giấy về trước — Đáp án: ĐỦ 200 TÍN HIỆU + ĐỦ 90 NGÀY

- Chỉ làm bước này sau khi backtest qua cổng giết và kiểm toán độc lập CONFIRMED.
- Thu thập tín hiệu mới phát sinh, ghi sổ giấy, không đặt lệnh thật.
- Ngày phán xét: khi đủ 200 tín hiệu mới đã chốt + đã qua ít nhất 90 ngày, lấy mốc nào tới sau.
- Giới hạn xem lại: sau 180 ngày mà chưa đủ 200 tín hiệu đã chốt thì dừng và ghi là THIẾU MẪU, không phải thắng, không kéo dài vô hạn để chờ một chuỗi đẹp.
- Tốc độ tín hiệu thực tế đo ở backtest sẽ cho ước tính trước, nhưng ngày phán xét chính thức vẫn theo quy tắc 200 + 90 ngày ở trên, không theo ước tính.

## Bước tiếp theo nếu bạn duyệt

1. Bạn duyệt cả 10 đáp án này (hoặc sửa từng đáp án).
2. Tôi viết spec đóng băng v1 từ đúng 10 đáp án này, ghi sha256, đưa bạn kiểm tra.
3. Thăm dò dữ liệu nhỏ, chậm, v2, takerOnly=false, theo cửa sổ thời gian. Gặp 429 thì dừng và báo, không cày lại.
4. Chỉ sau khi thăm dò xác nhận đủ dữ liệu + phí đúng 0,05 thì mới chạy backtest theo spec đã đóng băng.
