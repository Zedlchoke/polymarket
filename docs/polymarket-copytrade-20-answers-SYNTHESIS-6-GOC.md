# 10 đáp án cuối sau khi tổng hợp 6 góc nhìn — CHƯA ĐÓNG BĂNG
Ngày: 2026-11-02. Nguồn: bản nháp + bản đề xuất 10 đáp án, soi lại bởi 6 góc nhìn:
phê bình đối kháng, dữ liệu/API, thống kê, thể thao, người copy thật, kiểm toán spec.
Đây là bản tổng hợp tốt nhất theo tôi, chưa phải spec đóng băng.
Chỉ khi bạn duyệt (kể cả 5 quyết định mở ở cuối), tôi mới viết spec đóng băng + hash.

Không lệnh thật, không tiền thật ở bất cứ bước nào.

## Kết luận tổng hợp, nói trước

- 6 góc nhìn đồng ý hướng gốc: chỉ thể thao, chọn người bằng quá khứ, tìm k trên đoạn trong mẫu rồi khóa lại test trên đoạn ngoài mẫu.
- 6 góc nhìn cùng phản đối 3 chỗ cũ, nên 3 chỗ này bắt buộc phải sửa trước khi đóng băng:
  1. Chọn người bằng lãi tuyệt đối + test giữ tới chốt là đo sai kỹ năng. Phải chọn bằng lãi giữ-tới-chốt trên mỗi đồng đặt.
  2. Giá copy cũ mua rẻ giả: giao dịch đầu tiên không kiểm tra độ sâu, phạt 0,02 không đo từ spread, phí không tính theo ngày.
  3. Đếm ví không phải đếm người: cửa sổ 24 giờ + đếm mua gộp + gộp nhóm hẹp làm k mất ý nghĩa.
- Điểm mới quan trọng nhất từ góc thống kê: 200 tín hiệu chỉ đủ sàng lọc, không đủ kết luận cuối.
  Lãi 5% ở 200 tín hiệu vẫn nằm trong nhiễu. Phán xét cuối cần khoảng tin cậy 95% nằm hoàn toàn trên 0,
  và thường cần từ 500 tín hiệu trở lên ở test giấy về trước.

## Bảng đồng thuận nhanh

| Câu | 6 góc nhìn đồng ý | Chỗ cãi nhau lớn nhất | Cách tổng hợp chọn |
|---|---|---|---|
| Q1 chỉ thể thao | Đồng ý | Trước trận hay cả trong trận | Chỉ trước trận ở v1, trong trận để v2 |
| Q2 90 ngày | Đồng ý | Có rút xuống 60 ngày khi thiếu dữ liệu không | Không rút, thiếu thì ghi thiếu mẫu |
| Q3 chọn 20 | Đồng ý lọc trước | Xếp theo lãi tuyệt đối hay lãi trên mỗi đồng | Xếp theo lãi giữ-tới-chốt trên mỗi đồng |
| Q4 overlap | Đồng ý khung | 24 giờ hay 6 giờ, 50 USD hay 200 USD | 24 giờ + chặn giá chạy quá 0,10, mỗi nhóm từ 100 USD |
| Q5 giá copy | Đồng ý tính phí | Thứ tự tính, spread, phí theo ngày | Giá VWAP đủ 100 USD + phạt = max(0,02, spread) + phí theo ngày |
| Q6 100 USD | Đồng ý | Có giới hạn vốn mở không | Có, tối đa 10 lệnh mở cùng lúc |
| Q7 giữ tới chốt | Đồng ý cho v1 | Tên gọi và tín hiệu chưa chốt | Đổi tên thành "copy lệnh vào, giữ tới chốt", ân hạn 14 ngày |
| Q8 k = 1–5 | Đồng ý khung | Chọn k* bằng lãi thô hay lãi trừ nhiễu | Chọn bằng ROI − sai số, cần từ 100 tín hiệu |
| Q9 cổng giết | Đồng ý hướng | 200 có đủ kết luận không | 200 chỉ sàng lọc, thêm tầng xác nhận bằng khoảng tin cậy |
| Q10 test về trước | Đồng ý 200 + 90 ngày | Cohort cũ hay chọn lại người mới | Chọn lại bằng đúng luật cũ tại ngày GO, vì test này test luật, không test 20 ví cũ |

## Dòng thời gian và mốc giờ — áp cho mọi câu

- 3 đoạn liên tiếp, không trùng, không khoảng trống, tính bằng giây UTC, không dùng ngày lịch hay giờ Việt Nam để cắt đoạn.
- Đoạn 1 chọn người: 90 ngày. Đoạn 2 trong mẫu: 90 ngày ngay sau. Đoạn 3 ngoài mẫu: 90 ngày ngay sau.
- Mọi con số ở đoạn 1 chỉ tính từ dữ liệu đã biết tới cuối đoạn 1. Lệnh đặt trong đoạn 1 nhưng chốt sau đoạn 1 thì không tính lãi vào lúc chọn người.
- Tín hiệu gán theo thời điểm kích hoạt, không gán theo thời điểm chốt. Tín hiệu kích hoạt ở đoạn 2 mà chốt ở đoạn 3 vẫn tính cho đoạn 2.
- Tên trường dữ liệu thật (mã thị trường, mã cửa, giá, tiền, thời gian, kết quả chốt) phải ghi vào spec sau bước thăm dò, trước khi đóng băng. Không có bảng tên trường thì chưa đủ điều kiện đóng băng.

## Q1. Chỉ thể thao — Đáp án tổng hợp

- Chỉ thể thao, chỉ thị trường một trận duy nhất, chỉ trước trận, thị trường đơn, không combo.
- Loại khỏi v1: vô địch cả mùa, giải thưởng mùa, thị trường nhiều trận gộp, thị trường đang đá trực tiếp.
  Lý do: trước trận giá chạy chậm, người copy còn kịp; trong trận giá nhảy theo từng bàn thắng, phạt trễ khác hẳn, trộn chung sẽ giấu chỗ thua.
  Trong trận để cho spec v2 riêng, không trộn vào v1.
- Thể thao xác định bằng trường dữ liệu của Gamma (tag / category / event), ghi rõ trường nào và giá trị nào, và cách xử lý thị trường mang 2 tag.
  Thị trường 2 cửa và thị trường nhiều cửa phải phân biệt bằng mã token, không phân biệt bằng chữ "YES/NO",
  vì thị trường thể thao 2 chiều dùng tên đội, không dùng Yes/No.
- Báo cáo bắt buộc tách theo: môn, loại thị trường (thắng thua / chấp điểm / tổng điểm / kèo cầu thủ),
  mùa thường / playoff / giải lớn, dải giá, độ lớn thị trường. Không chỉ báo cáo tổng.

## Q2. Cửa sổ chọn 90 ngày — Đáp án tổng hợp

- Giữ 90 ngày, là đoạn 1, kết thúc ngay trước đoạn trong mẫu.
- Không rút xuống 60 ngày khi thiếu lịch sử. Nếu không đủ 90 + 90 + 90 ngày cho đủ ví thì ghi là thiếu lịch sử / thiếu mẫu,
  không hạ cửa để đủ 20 người.
- Điều kiện còn chơi được siết lại so với bản cũ: ít nhất 3 lệnh trong 14 ngày cuối của đoạn chọn
  (thay cho 1 lệnh trong 7 ngày cuối, vì 1 lệnh quá dễ lọt).
- Báo cáo hao hụt: có bao nhiêu trong 20 ví / nhóm còn hoạt động ở đoạn trong mẫu và đoạn ngoài mẫu.
  Nếu ngoài mẫu chỉ còn một nửa hoạt động thì đó không còn là cùng một chiến lược, phải ghi rõ.
- Lưu ý mùa giải: ghi rõ 3 đoạn rơi vào mùa nào, playoff hay mùa thường. Không tính 90 ngày lịch một cách mù
  khi môn chính đang nghỉ dài, nhưng cũng không tự ý đổi thành 90 ngày thi đấu sau khi thấy kết quả.
  Cách tính ngày phải khóa trước khi đóng băng, và ghi rõ trong spec.

## Q3. Luật chọn 20 — Đáp án tổng hợp (thay đổi lớn nhất)

Tất cả tính chỉ trên thể thao trước trận, chỉ trong đoạn chọn 90 ngày, bằng dữ liệu đã biết tới cuối đoạn chọn.

Một ví muốn vào danh sách phải qua hết:
1. Khối lượng thể thao ≥ 50.000 USD. Định nghĩa: tổng tiền mặt mua (usdc_size) từ lịch sử giao dịch của ví,
   sau khi nối Gamma để chỉ giữ thị trường thể thao. Không lấy khối lượng từ bảng xếp hạng, vì bảng đó tính bằng cổ phần, không phải USD, và không cho cửa sổ 90 ngày tùy ý.
2. Số lệnh ≥ 80 lệnh giao dịch (trade rows, không phải số vị thế đã đóng). Nâng từ 50 lên 80 để bớt may rủi.
   Nếu sau lọc còn dưới 20 ví thì ghi thiếu mẫu, không hạ xuống 50 để đủ người.
3. Số thị trường khác nhau ≥ 20 mã thị trường (conditionId).
4. Lãi giữ-tới-chốt trên mỗi đồng đặt > 0, và lãi đã chốt thật > 0. Đây là điểm sửa cốt lõi:
   - Lãi chính để xếp hạng là lãi giữ-tới-chốt tính lại từ lệnh vào: với mỗi lệnh vào đã chốt trước cuối đoạn chọn,
     lãi = số cổ phần × giá chốt (0 / 0,5 / 1) − tiền mua − phí theo ngày.
   - Lãi đã chốt thật chỉ làm cửa lọc phụ, vì người gốc bán sớm giỏi không có nghĩa là lệnh vào của họ giữ tới chốt cũng thắng.
   - Nếu một ví lãi đã chốt cao nhưng lãi giữ-tới-chốt âm thì loại, vì chiến lược copy ở Q7 là giữ tới chốt.
5. Còn chơi: ít nhất 3 lệnh trong 14 ngày cuối đoạn chọn.
6. Một thị trường không chiếm quá 50% tổng lãi giữ-tới-chốt.
7. Loại market maker / phòng hộ: một thị trường được tính là cả hai cửa nếu tại bất kỳ thời điểm nào trong đoạn chọn,
   ví đó đồng thời giữ số cổ phần > 0 của cả hai token của cùng một mã thị trường, tính lại từ chuỗi giao dịch TRADE
   (loại SPLIT, MERGE, REWARD, MAKER_REBATE). Nếu trên 30% số thị trường của ví đó là cả hai cửa thì loại.
   Không tính "từng giữ trong 90 ngày" rồi cộng dồn, vì người đổi phe khi tin tức đổi không phải market maker.
8. Loại bot tạo thanh khoản: trên 2.000 lệnh và lãi / khối lượng < 1% thì loại.
9. Xếp hạng: sau khi lọc, xếp theo lãi giữ-tới-chốt trên mỗi đồng đặt
   (tổng lãi giữ-tới-chốt / tổng tiền mua cho các lệnh đã chốt đó), từ cao xuống thấp, lấy 20 đầu.
   Hòa nhau thì nhiều thị trường hơn trước, rồi nhiều lệnh hơn, rồi mã ví theo thứ tự chữ cái.
   Không xếp theo lãi tuyệt đối, vì lãi tuyệt đối xếp theo cỡ ví, không xếp theo giỏi trên mỗi đồng.
10. Gộp nhóm nghi cùng một người, làm trước khi xếp hạng cuối:
    - Hai ví được gộp nếu số lệnh trùng / số lệnh ít hơn trong hai ví ≥ 50%, và số lệnh trùng ≥ 20 lệnh,
      trong đó trùng nghĩa là cùng mã thị trường, cùng mã token cửa, và hai lệnh cách nhau không quá 60 phút.
    - Gộp theo cặp đã duyệt theo thứ tự lãi giảm dần: giữ ví lãi cao hơn, bỏ ví sau nếu nó trùng với bất kỳ ví nào đã giữ.
    - Sau gộp, k tính trên số nhóm, không tính trên số ví. Nếu sau gộp chỉ còn 12 nhóm thì danh sách là 12 nhóm,
      và phải bù bằng ví xếp hạng tiếp theo cho tới khi đủ 20 nhóm, nếu không đủ thì ghi thiếu mẫu.
    - Nhóm này được đóng băng từ đoạn chọn và dùng cho cả đoạn trong mẫu và ngoài mẫu, không tính lại nhóm từ dữ liệu đoạn test,
      vì tính lại từ đoạn test là dùng tương lai để định nghĩa tín hiệu trong chính đoạn đó.
    - Ghi rõ: gộp chỉ là nghi ngờ, không phải chứng minh cùng người. Người cố tình lệch giờ, lệch cỡ tiền vẫn có thể lọt, đó là giới hạn phải ghi trong báo cáo.

Pool ứng viên là nút thắt dữ liệu lớn nhất: bảng xếp hạng chỉ cho DAY / WEEK / MONTH / ALL, không cho 90 ngày tùy ý.
Vì vậy pool ứng viên lấy từ đâu (ví dụ leaderboard MONTH rồi tự tính 90 ngày cho pool đó) phải ghi rõ trong spec trước khi chạy,
vì pool đó tự nó tạo ra thiên lệch chọn mẫu. Không được lấy leaderboard MONTH rồi giả vờ đó là 90 ngày.

## Q4. Overlap là gì — Đáp án tổng hợp

Một tín hiệu được tính khi đủ hết, tính bằng giây UTC:
- Cùng một mã thị trường (conditionId) và cùng một mã token cửa (outcomeIndex / token_id), không phải cùng chữ YES/NO.
- Cùng một sự kiện cũng chỉ tính một lần: mỗi sự kiện, mỗi đoạn, chỉ copy lần đầu tiên kích hoạt.
  Các thị trường con khác của cùng sự kiện trong cùng đoạn bị bỏ qua ở bảng chính, ghi vào bảng phụ.
  Lý do: copy thắng, chấp điểm, tổng điểm của cùng một trận thực ra là nhân 3 lần cùng một ván cược.
- Mỗi thị trường chỉ copy một lần đầu tiên trong mỗi đoạn. Phe nào kích hoạt trước thì thắng, phe ngược sau đó của cùng thị trường trong cùng đoạn bị bỏ qua.
- Thuật toán cửa sổ trượt, viết từng bước: tại mỗi lệnh mua ròng, nhìn lại các nhóm khác nhau đã tăng vị thế ròng cho cùng cửa đó;
  nếu thời điểm của nhóm thứ k trừ thời điểm của nhóm đầu tiên trong nhóm k nhóm đó ≤ 24 giờ (86.400 giây) thì kích hoạt ngay tại lệnh thứ k.
  Không chờ hết 24 giờ, không dùng cửa sổ ngày lịch.
- Đếm theo vị thế ròng tăng, không đếm mua gộp: một nhóm được đếm khi trong cửa sổ đó, vị thế ròng của nhóm cho cửa đó
  tăng ít nhất 100 USD tiền mặt, sau khi trừ đi phần bán cùng cửa trong cùng cửa sổ. Ví đã mua rồi bán hết thì không được đếm.
  Nhóm nào trong cửa sổ cũng mua cửa ngược của cùng thị trường thì nhóm đó không được đếm.
- Tiền: mỗi nhóm đếm từ 100 USD ròng trở lên, tổng tiền ròng của các nhóm đếm từ 500 USD trở lên.
  Mức 50 USD cũ gần như không lọc gì, mức 200 USD của góc thực hành thì loại quá nhiều ví nhỏ nghiêm túc.
  Mức 100 USD là điểm giữa, và báo cáo phụ với 50 USD và 200 USD chỉ để mô tả, không dùng để chọn k.
- Khối lượng thị trường tại kích hoạt ≥ 10.000 USD, tính bằng tổng tiền giao dịch của thị trường đó tính tới thời điểm kích hoạt,
  không dùng khối lượng cuối cùng từ Gamma, vì khối lượng cuối cùng chứa giao dịch sau kích hoạt, là rò rỉ tương lai.
- Chặn giá chạy: nếu giá copy thô đã chạy quá 0,10 so với giá của nhóm đầu tiên trong nhóm kích hoạt thì bỏ tín hiệu.
  Lý do: 5 người mua ở 5 mức giá khác nhau trong 1 ngày không còn là cùng một kèo.
- Khoảng giá: giá copy sau phạt phải nằm trong 0,10–0,90. Ngoài khoảng này thì bỏ tín hiệu, ghi riêng số bị loại.
  Nếu số bị loại vì giá trên 20% tổng kích hoạt thì bảng chính không còn đại diện cho chiến lược gốc, phải ghi rõ.

## Q5. Giá copy — Đáp án tổng hợp

Thứ tự tính phải khóa đúng như sau, không được đổi thứ tự:
1. Giá gốc = giá trung bình theo tiền (VWAP) của các giao dịch sau kích hoạt, cộng dồn cho tới khi đủ 100 USD tiền mặt,
   trong tối đa 60 phút sau kích hoạt (trước trận). Nếu trong 60 phút không đủ 100 USD thì bỏ tín hiệu, ghi là bỏ vì thiếu độ sâu.
   Không dùng giá của một giao dịch nhỏ đầu tiên làm giá khớp cho 100 USD, vì lệnh nhỏ không chứng minh khớp đủ 100 USD.
2. Phạt trễ = số lớn hơn trong hai số: 0,02 và spread tại kích hoạt (giá bán tốt nhất trừ giá mua tốt nhất, nếu lấy được từ sổ lệnh).
   Nếu không lấy được spread thì phạt = 0,02.
3. Giá copy = giá gốc + phạt trễ.
4. Số cổ phần = 100 / giá copy.
5. Phí taker = số cổ phần × tỷ lệ phí × giá copy × (1 − giá copy).
   Tỷ lệ phí phải lấy từ feeSchedule của từng thị trường tại thời điểm tín hiệu, không hardcode 0,05 cho cả 9 tháng.
   Lịch sử đã biết: thể thao 0 năm 2025, 0,03 từ tháng 3 đến tháng 6 năm 2026, 0,05 từ ngày 10 tháng 7 năm 2026.
   Nếu feeSchedule thiếu thì dùng bảng theo ngày làm dự phòng, và ghi rõ đó là dự phòng.
   Không dùng endpoint fee-rate cũ, vì endpoint đó trả về mức phí cũ, không phải phí taker hiện tại.
6. Thắng: lãi = số cổ phần × giá chốt − 100 − phí. Thua: lãi = −100 − phí.
   Giá chốt lấy từ kết quả chốt chính thức, không lấy giá cuối trước khi đóng.
- Báo cáo nhạy cảm bắt buộc: tính lại toàn bộ với phạt trễ thay bằng 0,05, và tính lại với phạt 0,10 để xem độ mong manh.
  Phạt nhạy cảm là thay thế, không phải cộng thêm thành 0,07 hay 0,12.
- Làm tròn: ghi rõ giá làm tròn tới bao nhiêu chữ số, cổ phần có giữ số lẻ không, phí làm tròn tới xu nào, trước khi đóng băng.
- Lệnh maker: khi lấy lịch sử phải đặt takerOnly=false nếu tham số còn tồn tại trên v2, vì mặc định chỉ hiện lệnh taker sẽ giấu một phía của ví.
  Tên tham số trên v2 phải xác nhận lại từ tài liệu v2, không suy từ v1 sang v2.

## Q6. Tiền giấy — Đáp án tổng hợp

- Giữ 100 USD giấy cố định mỗi tín hiệu, không gấp thếp, không dồn lãi.
- Mẫu số lãi duy nhất cho mọi bảng: tổng lãi ròng / (100 × số tín hiệu đã lấy). Không dùng vốn danh nghĩa 10.000 USD làm mẫu số.
- Giới hạn vốn mở mới, bắt buộc: tối đa 10 lệnh đang mở cùng lúc, tức tối đa 1.000 USD giấy đang phơi ngoài thị trường.
  Tín hiệu mới khi đã đủ 10 lệnh thì bị bỏ qua theo thứ tự thời gian, ghi riêng số bị bỏ vì đầy vốn, không được giấu đi.
- Tín hiệu bị bỏ vì thiếu độ sâu, không có giao dịch trong 60 phút, đầy vốn, hay ngoài khoảng giá đều được đếm riêng.
  Tỷ lệ bỏ = số bị bỏ / (số đã lấy + số bị bỏ). Nếu tỷ lệ bỏ trên 30% thì kết quả chỉ áp dụng cho thị trường thanh khoản và có vốn trống,
  không được suy ra cho mọi thị trường. Ở cổng giết, tỷ lệ bỏ trên 30% được tính là một cổng không qua (xem Q9).
- Báo cáo bắt buộc tách lãi theo dải giá: 0,10–0,30, 0,30–0,70, 0,70–0,90, và tách theo môn, theo sự kiện.
  Nếu tổng lãi dương nhưng chỉ nhờ một dải giá hay một sự kiện thì ghi rõ là mong manh.

## Q7. Thoát lệnh — Đáp án tổng hợp

- Đổi tên chiến lược cho đúng: "copy lệnh vào, giữ tới chốt". Đây không còn là copy đúng nghĩa, vì ví gốc có thể bán sớm.
  Báo cáo phải dùng đúng tên này, không được nói "copy trade thắng" như thể đã copy cả lúc bán của ví gốc.
- Luật chính: giữ tới khi chốt chính thức. Nguồn chốt chính thức phải khóa trước: Gamma resolutionStatus = resolved,
  hoặc đầu mối resolutions của Data API, và ghi rõ nguồn nào thắng khi hai nguồn lệch nhau.
  Không tính theo đề xuất chốt chưa xong, không tính theo ngày trận xong, không tính theo ngày thị trường đóng.
- Giá chốt: thắng 1, thua 0, hòa 0,5. Công thức đúng cho hòa: lãi = số cổ phần × 0,5 − 100 − phí.
  Bản cũ viết "hòa thì trả lại stake" là sai, trừ khi giá mua đúng 0,50. Thị trường hủy cũng phải lấy giá chốt thực tế từ nguồn chốt,
  không áp 0,5 mặc định, vì có thị trường hủy sẽ chốt theo luật riêng của thị trường đó.
- Tín hiệu chưa chốt: tín hiệu kích hoạt trong đoạn nhưng chưa chốt tới cuối đoạn thì được ân hạn 14 ngày sau đoạn để chốt.
  Sau ân hạn vẫn chưa chốt thì ghi riêng là chưa chốt, không tính là thắng hay thua, không đưa vào mẫu số lãi cho tới khi nó chốt.
  Nếu tỷ lệ chưa chốt sau ân hạn trên 10% tổng tín hiệu kích hoạt thì cổng giết không qua, vì loại đúng những thị trường chậm chốt sẽ làm đẹp mẫu.
- Thị trường tranh chấp có thể chờ 4–6 ngày mới chốt, và trong thời gian đó vốn giấy bị kẹt trong giới hạn 10 lệnh mở ở Q6.
  Thời gian chờ chốt thực tế phải báo cáo riêng.

## Q8. Ngưỡng k — Đáp án tổng hợp

- Thử k = 1, 2, 3, 4, 5. k tính trên số nhóm sau gộp, không tính trên số ví.
- k = 1 là mốc đối chứng, định nghĩa giống hệt các k khác: lần đầu tiên bất kỳ nhóm nào vào một sự kiện + cửa,
  cùng các lọc Q4, cùng giá Q5, cùng giữ tới chốt Q7, mỗi sự kiện chỉ tính 1 lần.
  Không được định nghĩa k = 1 lỏng hơn rồi so sánh với k ≥ 2 chặt hơn.
- Chỉ tìm k tốt nhất trên đoạn trong mẫu. Một k muốn được xét phải có ít nhất 100 tín hiệu trong mẫu, không phải 50.
- Công thức chọn k*, thay cho "lãi cao nhất thô":
  Điểm_k = ROI_k − sai số_k, trong đó sai số_k = độ lệch chuẩn lãi mỗi tín hiệu của k đó / 100 / căn(n_k).
  Chọn k có Điểm_k cao nhất, và k đó phải thỏa cả ba: Điểm_k > 0, ROI_k > 0, và ROI_k ≥ ROI_1 + 0,03 (hơn k = 1 ít nhất 3 điểm phần trăm).
  Nếu không có k nào thỏa cả ba thì dừng ở sàng lọc, không chọn k* nào.
  Nếu Điểm_k của hai k tốt nhất chênh nhau dưới 0,02 thì chọn k có nhiều tín hiệu hơn, vì nó bền hơn.
- Khóa k* lại, test đúng một lần trên đoạn ngoài mẫu. Đoạn ngoài mẫu đã dùng một lần thì không được quay lại thử k khác trên cùng đoạn đó.
- Báo cáo phụ đếm theo tổng tiền chỉ để mô tả, không bao giờ được dùng để cứu verdict khi bảng chính thua.
  Chỉ k mới được tối ưu trên đoạn trong mẫu. Không được tối ưu thêm cửa sổ, ngưỡng tiền, khoảng giá hay luật chọn người
  trên cùng đoạn trong mẫu rồi vẫn gọi là "chỉ tối ưu k".

## Q9. Cổng giết — Đáp án tổng hợp, 3 tầng

Cổng này áp cho k* đã khóa, sau phí theo ngày + phạt trễ chính. Tất cả các ngưỡng đều là lớn hơn hẳn, không làm tròn lên.
Ví dụ 99 tín hiệu là trượt, 4,9% không làm tròn thành 5%.

### Tầng 1 — Sàng lọc, phải qua hết mới được theo tiếp
1. Số tín hiệu: trong mẫu ≥ 100, ngoài mẫu ≥ 100, tổng ≥ 200. Đếm theo thời điểm kích hoạt, theo định nghĩa số đếm đã khóa ở Q6 và Q7.
2. Ngoài mẫu lãi ròng > 0.
3. Ngoài mẫu lãi ròng vẫn > 0 khi thay phạt trễ bằng 0,05, tính lại toàn bộ từ đầu (cổ phần mới, phí mới).
4. Ngoài mẫu lãi / tổng tiền đặt > 5%.
5. Ngoài mẫu lãi / tổng tiền đặt cao hơn k = 1, cùng đoạn, cùng mẫu số, cùng công thức.
6. Trong mẫu ở k* cũng phải dương và hơn k = 1. Nếu trong mẫu đã xấu mà ngoài mẫu may mắn thì logic test đã vỡ, không được qua bằng chữ.
7. 5 tín hiệu lãi nhất đóng góp dưới 50% tổng lãi ngoài mẫu, tín hiệu lãi nhất dưới 25%, và bỏ 10 tín hiệu lãi nhất đi mà lãi ngoài mẫu vẫn > 0.
   Đóng góp tính bằng lãi ròng từng tín hiệu, không tính bằng tiền thắng gộp.
8. Tỷ lệ bỏ tín hiệu ≤ 30% và tỷ lệ chưa chốt sau ân hạn ≤ 10%.

### Tầng 2 — Xác nhận, mới được gọi là sống
- Khoảng tin cậy 95% của lãi ngoài mẫu trên tổng tiền đặt, tính bằng cách lấy mẫu lại theo sự kiện (bootstrap gom theo sự kiện, không gom theo từng tín hiệu),
  phải nằm hoàn toàn trên 0, và lãi trên tổng tiền đặt vẫn > 5%.
- Thực tế: ở 200 tín hiệu, khoảng này thường rộng ±14–21%, nên lãi quan sát 5% chưa đủ kết luận.
  Nếu khoảng chứa 0 thì kết luận thống kê là "chưa đủ bằng chứng", không phải sống, cũng không phải chết.
  Muốn kết luận thì phải kéo dài test theo luật định trước ở Q10, không được đổi k.

### Tầng 3 — Cờ mô tả, không lật verdict chính trừ khi bạn quyết trước khi đóng băng
- Không một giải duy nhất nào chiếm trên 50% lãi ngoài mẫu, không một môn duy nhất nào là nguồn lãi duy nhất trong khi các môn còn lại lỗ nặng,
  và lãi khi bỏ World Cup đi vẫn > 0. Nếu vi phạm thì ghi rõ là lãi tập trung, dù tổng có qua tầng 1 và 2.
- Top 3 sự kiện đóng góp bao nhiêu % lãi ngoài mẫu cũng phải báo cáo, vì một sự kiện có nhiều thị trường có thể phình mẫu.

Nếu thiếu bất cứ cổng nào ở tầng 1 thì verdict là CHẾT, không sửa k, không sửa giá, không sửa luật chọn người.
Nếu qua tầng 1 nhưng chưa qua tầng 2 thì verdict là CHƯA ĐỦ BẰNG CHỨNG, đi tiếp test giấy về trước với mẫu lớn hơn.
Chỉ qua cả tầng 1 và tầng 2 mới được gọi là SỐNG ở backtest, và vẫn phải qua test giấy về trước ở Q10 mới bàn bước tiếp theo.

## Q10. Test giấy về trước — Đáp án tổng hợp

- Chỉ làm sau khi backtest qua tầng 1 và tầng 2, và kiểm toán độc lập CONFIRMED.
- Test này test LUẬT, không test 20 ví cũ. Vì vậy tại ngày GO, chọn lại 20 nhóm bằng đúng luật Q3 từ 90 ngày trước GO,
  dùng đúng các lọc, xếp hạng và gộp nhóm đã khóa. Đây phải được ghi rõ trong spec trước khi GO, không phải là thay người giữa chừng.
  Nếu bạn muốn test đúng 20 ví cũ thì đó là một spec khác, phải ghi rõ trước khi GO, và kết quả đó chỉ đo cohort cũ, không đo luật chạy thật.
- Thu thập: ghi sổ giấy, không đặt lệnh thật. Chu kỳ thăm dò, nguồn phát hiện, và cách ghi thời điểm phát hiện phải khóa trước khi GO.
  Ví dụ cho trước trận: thăm dò Data API v2 activity / trades mỗi 5 phút, trigger khi đủ k, giá forward tính đúng luật Q5,
  và ghi độ trễ từng tín hiệu (thời điểm giao dịch so với thời điểm phát hiện). Nếu độ trễ trung bình quá lớn so với backtest thì ghi rõ,
  không được lấy kết quả backtest để che độ trễ forward.
- Ngân sách request cho forward phải ghi trước: số request mỗi ngày, checkpoint bằng timestamp, dừng khi gặp 429 và chờ theo Retry-After,
  không tăng tốc để bù khoảng trống. Nếu thiếu trên 10% số ngày thu thập, hoặc thiếu đúng giai đoạn cao điểm, thì test forward bị coi là thiếu dữ liệu, không được tiếp tục như không có gì.
- Mốc kiểm tra giữa kỳ: 200 tín hiệu đã chốt, chỉ kiểm tra số lượng và chất lượng dữ liệu, không phán xét lãi.
- Mốc phán xét cuối: ít nhất 500 tín hiệu đã chốt + ít nhất 90 ngày, lấy mốc nào tới sau, tối đa 12 tháng để xem lại.
  Nếu sau 12 tháng chưa đủ 500 tín hiệu đã chốt thì ghi là thiếu mẫu.
  Trước khi chạy forward, tính trước số tín hiệu cần từ độ lệch chuẩn và lãi ở backtest. Nếu tốc độ đo được cho thấy không thể tới 500 trong 12 tháng
  thì không nên bắt đầu forward với k đó, hoặc phải chấp nhận trước là kết quả sẽ chỉ ở tầng chưa đủ bằng chứng.
- Cổng cho test về trước: áp đúng các cổng tầng 1 và tầng 2 của Q9, nhưng thay số đếm trong mẫu + ngoài mẫu bằng số đếm của tập về trước (≥ 500 tín hiệu đã chốt).
  "Đã chốt" ở đây nghĩa là đã resolved, không phải đã hết trận. Sau mốc thu thập, chờ tối đa 30 ngày để các tín hiệu đã thu thập chốt xong rồi mới phán xét.
- Ngày bắt đầu nên rơi vào đầu một giai đoạn mùa thường, không rơi vào giữa playoff hay giữa giải lớn, trừ khi ghi rõ là test riêng cho playoff hay giải lớn.
  Nếu 200 tín hiệu tới giữa một giải lớn đang chạy thì chờ giải đó kết thúc và mọi tín hiệu của giải đó chốt xong rồi mới phán xét.

## 5 quyết định mở — cần bạn chốt trước khi viết spec đóng băng

D1. World Cup và giải lớn chiếm trên 50% lãi: chỉ là cờ mô tả, hay nâng thành cổng giết?
    Đề xuất của tôi: cờ mô tả ở v1, vì định nghĩa giải lớn bằng trường dữ liệu còn cần thăm dò xác nhận.
    Nếu bạn muốn chặt hơn thì nâng thành cổng trước khi đóng băng, không nâng sau khi thấy kết quả.

D2. Test giấy về trước dùng cohort mới chọn lại bằng đúng luật cũ (đề xuất của tôi), hay dùng đúng 20 ví cũ từ backtest?
    Đề xuất: cohort mới, vì test luật chạy thật. Cohort cũ chỉ đo nhóm người đã cũ 12–15 tháng.

D3. Mỗi nhóm đếm từ 100 USD ròng (đề xuất của tôi) hay 200 USD như góc thực hành?
    100 USD giữ được nhiều ví nhỏ nghiêm túc hơn, 200 USD lọc nhiễu tốt hơn nhưng làm mẫu nhỏ đi.

D4. Cửa sổ overlap 24 giờ + chặn giá chạy quá 0,10 (đề xuất của tôi) hay 6 giờ như góc phê bình và góc thực hành?
    24 giờ + chặn giá giữ được tín hiệu trước trận ra tin trong ngày, 6 giờ giảm hiệu ứng bầy đàn nhưng có thể làm mẫu nhỏ đi.
    Dù chọn cách nào thì cửa sổ 6 giờ và 24 giờ còn lại cũng được báo cáo phụ, không dùng để đổi k*.

D5. Ngưỡng lệnh chọn người là 80 lệnh (đề xuất của tôi) hay 100 lệnh như góc phê bình?
    80 lệnh giữ được chuyên gia môn ít trận hơn, 100 lệnh bớt may rủi hơn nhưng có thể loại chuyên gia NFL và trận nhỏ.

Nếu bạn duyệt cả bộ này và chốt D1–D5, bước tiếp theo của tôi là: viết spec đóng băng v1 từ đúng bộ này,
ghi sha256, đưa bạn kiểm tra, rồi mới thăm dò dữ liệu nhỏ, chậm, theo checklist của góc dữ liệu. Gặp 429 thì dừng và báo, không cày lại.
