# SPEC v1 (NHÁP) — COPY TRADE 20 TÀI KHOẢN POLYMARKET, CHỈ TRÊN GIẤY

Ngày viết: 2026-11-02. Trạng thái: **BẢN NHÁP SPEC**, chuyển tiếp từ bản tổng hợp SYNTHESIS-6-GOC.

---

# ⛔ CHƯA ĐÓNG BĂNG — CHƯA CHẠY TÍNH ĐIỂM — D1–D5 CHƯA QUYẾT ⛔

File này KHÔNG phải spec đóng băng. KHÔNG có hash đóng băng. KHÔNG chạy backtest tính điểm từ file này.
Việc đóng băng chỉ xảy ra sau khi: chủ nhân chốt D1–D5 → thăm dò dữ liệu xác nhận đủ dữ liệu và đủ tên trường
→ chủ nhân ra lệnh GO riêng. Mọi ô "THIẾU" dưới đây chỉ được điền từ kết quả thăm dò thật, không được điền bằng suy đoán.

---

## 0. Ranh giới cứng của toàn dự án (không đổi ở mọi phiên bản)

- Chỉ nghiên cứu trên giấy. Không lệnh thật, không tiền thật, không nối ví, không tạo tài khoản Polymarket mới.
- Không dùng VPN hay cách lách rào địa lý. Không mua dữ liệu trả phí. Chi phí 0 đồng.
- Không ghi mật khẩu, API key, token, hay bất cứ bí mật nào vào file, log, hay chat. Toàn bộ dữ liệu đọc từ API công khai không cần đăng nhập.
- Luật dừng thu thập dữ liệu: gặp HTTP 429, 403, throttle, hay response chậm dần bất thường thì DỪNG TOÀN BỘ, ghi đúng mã lỗi và Retry-After nếu có, không retry ngay, không tăng tốc để bù khoảng trống. Nhóm đã từng dính 429 tích lũy 3 lần khi kéo nhiều trận; không được thiết kế collector theo giới hạn burst 10 giây.
- Không đổi spec sau khi thấy kết quả. Muốn đổi thì viết spec mới, đặt tên mới.
- Không dùng endpoint fee-rate cũ cho phí, vì endpoint đó trả về mức phí cũ (xem Q5).

## 1. Nguồn và thứ tự ưu tiên

| Ưu tiên | File | Vai trò |
|---|---|---|
| 1 (nguồn đúng nhất) | `polymarket-copytrade-20-answers-SYNTHESIS-6-GOC.md` (2026-11-02) | 10 đáp án Q1–Q10 và 5 quyết định mở D1–D5. Spec này chuyển đúng các con số của file đó, không thêm không bớt. |
| 2 (nháp gốc) | `polymarket-copytrade-20-plan-DRAFT.md` (2026-11-02) | Bối cảnh, danh sách điểm yếu, quy trình 6 bước. Chỉ tham chiếu, không dùng để ghi đè tổng hợp. |
| 3 (đề xuất cũ) | `polymarket-copytrade-20-answers-RECOMMENDED.md` (2026-11-02) | Đã bị tổng hợp thay thế ở các chỗ: chọn người bằng lãi giữ-tới-chốt trên mỗi đồng đặt, phạt trễ đo từ spread, phí theo ngày, mỗi nhóm từ 100 USD, cổng giết 3 tầng. Nếu xung đột thì tổng hợp thắng. |

Spec nháp này KHÔNG ghi đè file tổng hợp.

## 2. Định nghĩa thuật ngữ và đơn vị (khóa trước khi chạy)

- **Múi giờ và thời gian:** mọi mốc thời gian tính bằng **giây UTC (Unix seconds)**. Không dùng ngày lịch hay giờ Việt Nam để cắt đoạn. 1 ngày = 86.400 giây. 24 giờ = 86.400 giây.
- **Tiền:** USD giấy, đồng nghĩa USDC khi đọc dữ liệu. "Tiền mặt mua" của một lệnh = tổng tiền USD thực chi cho lệnh đó (trường `usdc_size` theo bản nháp; **THIẾU: tên trường thật trên contract v2, chờ thăm dò bước a**).
- **Mã thị trường:** `conditionId`. **Mã cửa:** mã token của cửa đó (`clobTokenIds` / `outcomeIndex` / `token_id`; **THIẾU: chốt tên trường thật ở bước thăm dò**). Cửa phân biệt bằng MÃ TOKEN, không phân biệt bằng chữ "YES/NO", vì thị trường thể thao 2 chiều dùng tên đội, không dùng Yes/No.
- **Cổ phần (share):** đơn vị trả 1 USD khi thắng, 0 USD khi thua, 0,5 USD khi hòa. Giá cổ phần ∈ [0, 1].
- **Ví:** một địa chỉ ví. **Nhóm:** một hoặc nhiều ví đã gộp theo luật Q3.10. Mọi lần đếm cho tín hiệu (k) tính theo NHÓM, không tính theo ví.
- **Thị trường vs sự kiện:** một sự kiện (ví dụ một trận đấu) có thể gồm nhiều thị trường con (thắng thua, chấp điểm, tổng điểm, kèo cầu thủ). Luật một lần mỗi sự kiện và mỗi thị trường xem Q4.
- **Trước trận vs trong trận:** v1 chỉ lấy thị trường một trận duy nhất, đơn, combo loại hết, và chỉ trước trận. Trong trận để spec v2 riêng, không trộn vào v1.
- **VWAP theo tiền:** giá trung bình theo tiền = tổng (giá × số cổ phần) / tổng số cổ phần, cộng dồn trên chuỗi giao dịch cho tới khi đủ điều kiện dừng (đủ 100 USD tiền mặt ở Q5).
- **ROI dùng trong spec này (trừ khi ghi rõ khác):** tổng lãi ròng / tổng tiền đặt. Với tín hiệu copy: mẫu số duy nhất = 100 × số tín hiệu đã lấy (Q6). Với xếp hạng ví ở Q3: lãi giữ-tới-chốt trên mỗi đồng đặt = tổng lãi giữ-tới-chốt / tổng tiền mua của các lệnh đã chốt.
- **Lãi giữ-tới-chốt:** lãi tính lại từ lệnh vào, giả sử giữ tới khi thị trường chốt chính thức: với mỗi lệnh vào đã chốt, lãi = số cổ phần × giá chốt (0 / 0,5 / 1) − tiền mua − phí theo ngày.
- **Đoạn (segment):** khoảng thời gian liên tiếp đo bằng giây UTC, xem mục 3.

## 3. Dòng thời gian 3 đoạn 90 ngày

- Ba đoạn liên tiếp, **không trùng nhau, không khoảng trống**, tính bằng giây UTC:
  - **Đoạn 1 — Chọn người:** 90 ngày.
  - **Đoạn 2 — Trong mẫu (in-sample), tìm k:** 90 ngày ngay sau đoạn 1.
  - **Đoạn 3 — Ngoài mẫu (holdout), test k đã khóa:** 90 ngày ngay sau đoạn 2.
- Tổng cần khoảng 9 tháng lịch sử cho mỗi ví/nhóm.
- Mọi con số ở đoạn 1 chỉ tính từ dữ liệu **đã biết tới cuối đoạn 1**. Lệnh đặt trong đoạn 1 nhưng chốt sau đoạn 1 thì không tính lãi vào lúc chọn người.
- Tín hiệu gán theo **thời điểm kích hoạt**, không gán theo thời điểm chốt. Tín hiệu kích hoạt ở đoạn 2 mà chốt ở đoạn 3 vẫn tính cho đoạn 2.
- Không rút mỗi đoạn xuống 60 ngày khi thiếu lịch sử. Nếu không đủ 90 + 90 + 90 ngày cho đủ ví thì ghi là **thiếu lịch sử / thiếu mẫu**, không hạ cửa để đủ 20 người.
- Ghi rõ 3 đoạn rơi vào mùa nào (mùa thường / playoff / giải lớn). Không tính 90 ngày lịch một cách mù khi môn chính đang nghỉ dài, nhưng cũng không tự ý đổi thành 90 ngày thi đấu sau khi thấy kết quả.
- **THIẾU (chốt trước khi đóng băng, không được tự chọn):** mốc thời gian tuyệt đối T0 (đầu đoạn 1) và T1, T2, T3 bằng ngày UTC cụ thể. Phải chốt sau thăm dò dữ liệu (biết lịch sử lấy tới đâu), trước khi đóng băng.
- **Tên trường dữ liệu thật** (mã thị trường, mã cửa, giá, tiền, thời gian, kết quả chốt) phải ghi vào spec sau bước thăm dò, trước khi đóng băng. **Không có bảng tên trường thì chưa đủ điều kiện đóng băng.**

## 4. Q1 — Phạm vi thị trường: CHỈ THỂ THAO, CHỈ TRẬN ĐƠN, CHỈ TRƯỚC TRẬN

- Chỉ thể thao, chỉ thị trường **một trận duy nhất**, chỉ **trước trận**, thị trường **đơn**, không combo.
- Loại khỏi v1: vô địch cả mùa, giải thưởng mùa, thị trường nhiều trận gộp, thị trường đang đá trực tiếp. Lý do: trước trận giá chạy chậm, người copy còn kịp; trong trận giá nhảy theo từng bàn thắng, phạt trễ khác hẳn, trộn chung sẽ giấu chỗ thua. Trong trận để cho spec v2 riêng.
- Thể thao xác định bằng trường dữ liệu của Gamma (tag / category / event), ghi rõ trường nào và giá trị nào, và cách xử lý thị trường mang 2 tag. **THIẾU: tên trường tag/category trên Gamma + bộ giá trị thể thao + quy tắc thị trường 2 tag (chờ thăm dò bước d).**
- Thị trường 2 cửa và thị trường nhiều cửa phân biệt bằng **mã token**, không phân biệt bằng chữ "YES/NO".
- Báo cáo bắt buộc tách theo: **môn**, **loại thị trường** (thắng thua / chấp điểm / tổng điểm / kèo cầu thủ), **mùa thường / playoff / giải lớn**, **dải giá**, **độ lớn thị trường**. Không chỉ báo cáo tổng.

## 5. Q2 — Cửa sổ chọn 20 tài khoản: 90 NGÀY, LÀ ĐOẠN 1

- Giữ 90 ngày, là đoạn 1, kết thúc ngay trước đoạn trong mẫu.
- Không rút xuống 60 ngày khi thiếu lịch sử (xem mục 3).
- Điều kiện còn chơi: **ít nhất 3 lệnh trong 14 ngày cuối** của đoạn chọn (thay cho "1 lệnh trong 7 ngày cuối" của bản cũ, vì 1 lệnh quá dễ lọt).
- Báo cáo hao hụt: có bao nhiêu trong 20 ví/nhóm còn hoạt động ở đoạn 2 và đoạn 3. Nếu ngoài mẫu chỉ còn một nửa hoạt động thì đó không còn là cùng một chiến lược, phải ghi rõ.
- Ghi chú mùa giải theo mục 3.

## 6. Q3 — Luật chọn 20: LỌC TRƯỚC, XẾP THEO LÃI GIỮ-TỚI-CHỐT TRÊN MỖI ĐỒNG ĐẶT

Tất cả tính **chỉ trên thể thao trước trận, chỉ trong đoạn chọn 90 ngày, bằng dữ liệu đã biết tới cuối đoạn chọn**.

Một ví muốn vào danh sách phải qua hết 10 cửa:

1. **Khối lượng thể thao ≥ 50.000 USD.** Định nghĩa: tổng tiền mặt mua (usdc_size) từ lịch sử giao dịch của ví, sau khi nối Gamma để chỉ giữ thị trường thể thao. Không lấy khối lượng từ bảng xếp hạng, vì bảng đó tính bằng cổ phần, không phải USD, và không cho cửa sổ 90 ngày tùy ý.
2. **Số lệnh ≥ 80 lệnh giao dịch** (trade rows, không phải số vị thế đã đóng). Nâng từ 50 lên 80 để bớt may rủi. Nếu sau lọc còn dưới 20 ví thì ghi thiếu mẫu, không hạ xuống 50 để đủ người. *(Đây là chỗ D5 chưa chốt: 80 hay 100 — xem mục 15.)*
3. **Số thị trường khác nhau ≥ 20 mã thị trường** (conditionId).
4. **Lãi giữ-tới-chốt trên mỗi đồng đặt > 0, VÀ lãi đã chốt thật > 0.** Đây là điểm sửa cốt lõi so với bản cũ:
   - Lãi chính để xếp hạng là **lãi giữ-tới-chốt tính lại từ lệnh vào**: với mỗi lệnh vào đã chốt trước cuối đoạn chọn, lãi = số cổ phần × giá chốt (0 / 0,5 / 1) − tiền mua − phí theo ngày.
   - Lãi đã chốt thật chỉ làm cửa lọc phụ, vì người gốc bán sớm giỏi không có nghĩa là lệnh vào của họ giữ tới chốt cũng thắng.
   - Nếu một ví lãi đã chốt cao nhưng lãi giữ-tới-chốt âm thì loại, vì chiến lược copy ở Q7 là giữ tới chốt.
5. **Còn chơi:** ít nhất 3 lệnh trong 14 ngày cuối đoạn chọn (đồng bộ Q2).
6. **Một thị trường không chiếm quá 50% tổng lãi giữ-tới-chốt.**
7. **Loại market maker / phòng hộ:** một thị trường được tính là "cả hai cửa" nếu tại bất kỳ thời điểm nào trong đoạn chọn, ví đó đồng thời giữ số cổ phần > 0 của cả hai token của cùng một mã thị trường, tính lại từ chuỗi giao dịch TRADE (loại SPLIT, MERGE, REWARD, MAKER_REBATE). Nếu trên 30% số thị trường của ví đó là cả hai cửa thì loại. Không tính "từng giữ trong 90 ngày" rồi cộng dồn, vì người đổi phe khi tin tức đổi không phải market maker.
8. **Loại bot tạo thanh khoản:** trên 2.000 lệnh và lãi / khối lượng < 1% thì loại, dù lãi ròng dương.
9. **Xếp hạng:** sau khi lọc, xếp theo lãi giữ-tới-chốt trên mỗi đồng đặt (tổng lãi giữ-tới-chốt / tổng tiền mua cho các lệnh đã chốt đó), từ cao xuống thấp, lấy 20 đầu. Hòa nhau thì: nhiều thị trường hơn trước, rồi nhiều lệnh hơn, rồi mã ví theo thứ tự chữ cái. Không xếp theo lãi tuyệt đối, vì lãi tuyệt đối xếp theo cỡ ví, không xếp theo giỏi trên mỗi đồng.
10. **Gộp nhóm nghi cùng một người, làm TRƯỚC khi xếp hạng cuối:**
    - Hai ví được gộp nếu: số lệnh trùng / số lệnh ít hơn trong hai ví ≥ 50%, VÀ số lệnh trùng ≥ 20 lệnh; trong đó "trùng" nghĩa là cùng mã thị trường, cùng mã token cửa, và hai lệnh cách nhau không quá 60 phút.
    - Gộp theo cặp đã duyệt theo thứ tự lãi giảm dần: giữ ví lãi cao hơn, bỏ ví sau nếu nó trùng với bất kỳ ví nào đã giữ.
    - Sau gộp, **k tính trên số nhóm, không tính trên số ví**. Nếu sau gộp chỉ còn 12 nhóm thì danh sách là 12 nhóm, và phải bù bằng ví xếp hạng tiếp theo cho tới khi đủ 20 nhóm; nếu không đủ thì ghi thiếu mẫu.
    - Nhóm được đóng băng từ đoạn chọn và dùng cho cả đoạn 2 và đoạn 3, không tính lại nhóm từ dữ liệu đoạn test, vì tính lại từ đoạn test là dùng tương lai để định nghĩa tín hiệu trong chính đoạn đó.
    - Ghi rõ: gộp chỉ là nghi ngờ, không phải chứng minh cùng người. Người cố tình lệch giờ, lệch cỡ tiền vẫn có thể lọt; đó là giới hạn phải ghi trong báo cáo.

**Nút thắt pool ứng viên (bắt buộc ghi rõ trước khi chạy):** bảng xếp hạng chỉ cho DAY / WEEK / MONTH / ALL, không cho 90 ngày tùy ý. Vì vậy nguồn pool ứng viên (ví dụ leaderboard MONTH rồi tự tính 90 ngày cho pool đó) phải ghi rõ trong spec trước khi chạy, vì pool đó tự nó tạo thiên lệch chọn mẫu. Không được lấy leaderboard MONTH rồi giả vờ đó là 90 ngày. **THIẾU: nguồn pool cụ thể + tham số leaderboard thật (chờ thăm dò bước b).**

## 7. Q4 — Overlap là gì: CỬA SỔ TRƯỢT 24 GIỜ THEO GIÂY UTC, ĐẾM VỊ THẾ RÒNG TĂNG

Một tín hiệu được tính khi đủ hết các điều kiện sau, tính bằng giây UTC:

1. **Cùng mã thị trường (conditionId) và cùng mã token cửa** (outcomeIndex / token_id), không phải cùng chữ YES/NO.
2. **Mỗi sự kiện chỉ copy một lần đầu tiên trong mỗi đoạn.** Các thị trường con khác của cùng sự kiện trong cùng đoạn bị bỏ ở bảng chính, ghi vào bảng phụ. Lý do: copy thắng, chấp điểm, tổng điểm của cùng một trận thực ra là nhân 3 lần cùng một ván cược.
3. **Mỗi thị trường chỉ copy một lần đầu tiên trong mỗi đoạn.** Phe nào kích hoạt trước thì thắng; phe ngược sau đó của cùng thị trường trong cùng đoạn bị bỏ.
4. **Thuật toán cửa sổ trượt, từng bước:** tại mỗi lệnh mua ròng, nhìn lại các nhóm khác nhau đã tăng vị thế ròng cho cùng cửa đó; nếu thời điểm của nhóm thứ k trừ thời điểm của nhóm đầu tiên trong nhóm k nhóm đó ≤ 24 giờ (86.400 giây) thì **kích hoạt ngay tại lệnh thứ k**. Không chờ hết 24 giờ, không dùng cửa sổ ngày lịch.
5. **Đếm theo vị thế ròng tăng, không đếm mua gộp:** một nhóm được đếm khi trong cửa sổ đó, vị thế ròng của nhóm cho cửa đó tăng **ít nhất 100 USD tiền mặt**, sau khi trừ đi phần bán cùng cửa trong cùng cửa sổ. Ví đã mua rồi bán hết thì không được đếm. Nhóm nào trong cửa sổ cũng mua cửa ngược của cùng thị trường thì nhóm đó không được đếm. *(Đây là chỗ D3 chưa chốt: 100 hay 200 USD/nhóm — xem mục 15.)*
6. **Tiền tổng:** tổng tiền ròng của các nhóm đếm ≥ 500 USD. Mức 50 USD cũ gần như không lọc gì, mức 200 USD loại quá nhiều ví nhỏ nghiêm túc; 100 USD là điểm giữa. Báo cáo phụ với 50 USD và 200 USD chỉ để mô tả, không dùng để chọn k.
7. **Khối lượng thị trường tại kích hoạt ≥ 10.000 USD**, tính bằng tổng tiền giao dịch của thị trường đó **tính tới thời điểm kích hoạt**, không dùng khối lượng cuối cùng từ Gamma, vì khối lượng cuối cùng chứa giao dịch sau kích hoạt, là rò rỉ tương lai. **THIẾU: cách dựng khối lượng tới thời điểm từ dữ liệu có thể lấy (chờ thăm dò).**
8. **Chặn giá chạy:** nếu giá copy thô đã chạy quá 0,10 so với giá của nhóm đầu tiên trong nhóm kích hoạt thì bỏ tín hiệu. Lý do: 5 người mua ở 5 mức giá khác nhau trong 1 ngày không còn là cùng một kèo.
9. **Khoảng giá:** giá copy sau phạt phải nằm trong 0,10–0,90. Ngoài khoảng này thì bỏ tín hiệu, ghi riêng số bị loại. Nếu số bị loại vì giá trên 20% tổng kích hoạt thì bảng chính không còn đại diện cho chiến lược gốc, phải ghi rõ.

## 8. Q5 — Giá copy trên giấy: GIÁ VWAP ĐỦ 100 USD → PHẠT TRỄ → GIÁ COPY → SỐ CỔ PHẦN → PHÍ THEO NGÀY

Thứ tự tính khóa đúng như sau, **không được đổi thứ tự**:

1. **Giá gốc** = giá trung bình theo tiền (VWAP) của các giao dịch sau kích hoạt, cộng dồn cho tới khi đủ **100 USD tiền mặt**, trong tối đa **60 phút sau kích hoạt** (trước trận). Nếu trong 60 phút không đủ 100 USD thì bỏ tín hiệu, ghi là bỏ vì thiếu độ sâu. Không dùng giá của một giao dịch nhỏ đầu tiên làm giá khớp cho 100 USD, vì lệnh nhỏ không chứng minh khớp đủ 100 USD.
2. **Phạt trễ** = số lớn hơn trong hai số: **0,02** và **spread tại kích hoạt** (giá bán tốt nhất trừ giá mua tốt nhất, nếu lấy được từ sổ lệnh). Nếu không lấy được spread thì phạt = 0,02. **THIẾU: khả năng lấy spread lịch sử tại thời điểm kích hoạt (chờ thăm dò).**
3. **Giá copy** = giá gốc + phạt trễ.
4. **Số cổ phần** = 100 / giá copy.
5. **Phí taker** = số cổ phần × tỷ lệ phí × giá copy × (1 − giá copy).
   - Tỷ lệ phí phải lấy từ **feeSchedule của từng thị trường tại thời điểm tín hiệu**, không hardcode 0,05 cho cả 9 tháng. **THIẾU: trường feeSchedule trên Gamma/contract v2 (chờ thăm dò bước d).**
   - Bảng phí theo ngày dự phòng (chỉ dùng khi feeSchedule thiếu, và phải ghi rõ là dự phòng). Lịch sử đã biết: thể thao 0 năm 2025; 0,03 từ tháng 3 đến tháng 6 năm 2026; 0,05 từ ngày 10 tháng 7 năm 2026. **THIẾU: xác nhận bảng này ở bước thăm dò trước khi đóng băng.**
   - Không dùng endpoint fee-rate cũ, vì endpoint đó trả về mức phí cũ, không phải phí taker hiện tại.
6. **Kết quả từng tín hiệu:** Thắng: lãi = số cổ phần × giá chốt − 100 − phí. Thua: lãi = −100 − phí. Giá chốt lấy từ kết quả chốt chính thức, không lấy giá cuối trước khi đóng.

Quy định thêm của Q5:

- **Báo cáo nhạy cảm bắt buộc:** tính lại toàn bộ với phạt trễ thay bằng 0,05, và tính lại với phạt 0,10. Phạt nhạy cảm là THAY THẾ, không phải cộng thêm thành 0,07 hay 0,12.
- **Làm tròn:** phải ghi rõ giá làm tròn tới bao nhiêu chữ số, cổ phần có giữ số lẻ không, phí làm tròn tới xu nào — **chốt trước khi đóng băng (THIẾU: chưa chốt, là quyết định của chủ nhân).**
- **Lệnh maker:** khi lấy lịch sử phải đặt takerOnly=false nếu tham số còn tồn tại trên v2, vì mặc định chỉ hiện lệnh taker sẽ giấu một phía của ví. **THIẾU: tên tham số takerOnly trên contract v2 (chờ thăm dò bước a, c). Không suy từ v1 sang v2.**

## 9. Q6 — Tiền giấy: 100 USD CỐ ĐỊNH MỖI TÍN HIỆU, TỐI ĐA 10 LỆNH MỞ

- Mỗi tín hiệu copy đúng **100 USD giấy** để mua cổ phần. Phí tính thêm ngoài 100 USD (tính theo công thức Q5).
- Không gấp thếp, không dồn lãi vào lệnh sau, không nhân đôi khi thua.
- **Mẫu số lãi duy nhất cho mọi bảng:** tổng lãi ròng / (100 × số tín hiệu đã lấy). Không dùng vốn danh nghĩa 10.000 USD làm mẫu số.
- **Giới hạn vốn mở (bắt buộc):** tối đa 10 lệnh đang mở cùng lúc, tức tối đa 1.000 USD giấy đang phơi ngoài thị trường. Tín hiệu mới khi đã đủ 10 lệnh thì bị bỏ qua theo thứ tự thời gian, ghi riêng số bị bỏ vì đầy vốn, không được giấu.
- Tín hiệu bị bỏ vì thiếu độ sâu, không có giao dịch trong 60 phút, đầy vốn, hay ngoài khoảng giá đều được **đếm riêng**. Tỷ lệ bỏ = số bị bỏ / (số đã lấy + số bị bỏ). Nếu tỷ lệ bỏ trên 30% thì kết quả chỉ áp dụng cho thị trường thanh khoản và có vốn trống, không được suy ra cho mọi thị trường. Ở cổng giết, tỷ lệ bỏ trên 30% là một cổng không qua (Q9).
- Báo cáo bắt buộc tách lãi theo dải giá: 0,10–0,30 / 0,30–0,70 / 0,70–0,90, và tách theo môn, theo sự kiện. Nếu tổng lãi dương nhưng chỉ nhờ một dải giá hay một sự kiện thì ghi rõ là mong manh.

## 10. Q7 — Thoát lệnh: COPY LỆNH VÀO, GIỮ TỚI CHỐT

- **Tên chiến lược (bắt buộc dùng đúng trong mọi báo cáo):** "copy lệnh vào, giữ tới chốt". Đây không còn là copy đúng nghĩa, vì ví gốc có thể bán sớm. Không được nói "copy trade thắng" như thể đã copy cả lúc bán của ví gốc.
- Giữ tới khi thị trường **chốt chính thức**. Không đặt chốt lãi, không đặt cắt lỗ, không bán sớm vì giá đẹp. V1 có một luật thoát duy nhất.
- **Nguồn chốt chính thức phải khóa trước:** Gamma `resolutionStatus = resolved`, hoặc đầu mối resolutions của Data API; ghi rõ nguồn nào thắng khi hai nguồn lệch nhau. Không tính theo đề xuất chốt chưa xong, không tính theo ngày trận xong, không tính theo ngày thị trường đóng. **THIẾU: ưu tiên nguồn khi lệch (quyết định trước khi đóng băng) + tên trường thật (chờ thăm dò bước e).**
- **Giá chốt:** thắng 1, thua 0, hòa 0,5. Công thức hòa: lãi = số cổ phần × 0,5 − 100 − phí. Bản cũ viết "hòa thì trả lại stake" là sai, trừ khi giá mua đúng 0,50. Thị trường hủy cũng phải lấy giá chốt thực tế từ nguồn chốt, không áp 0,5 mặc định, vì có thị trường hủy sẽ chốt theo luật riêng của thị trường đó.
- **Tín hiệu chưa chốt:** tín hiệu kích hoạt trong đoạn nhưng chưa chốt tới cuối đoạn được **ân hạn 14 ngày** sau đoạn để chốt. Sau ân hạn vẫn chưa chốt thì ghi riêng là chưa chốt, không tính là thắng hay thua, không đưa vào mẫu số lãi cho tới khi nó chốt. Nếu tỷ lệ chưa chốt sau ân hạn trên 10% tổng tín hiệu kích hoạt thì cổng giết không qua.
- Thị trường tranh chấp có thể chờ 4–6 ngày mới chốt; trong thời gian đó vốn giấy bị kẹt trong giới hạn 10 lệnh mở của Q6. Thời gian chờ chốt thực tế phải báo cáo riêng.

## 11. Q8 — Ngưỡng k: THỬ k = 1–5, CHỌN k* BẰNG ROI TRỪ SAI SỐ, CHỈ TỐI ƯU TRÊN ĐOẠN TRONG MẪU

- Thử **k = 1, 2, 3, 4, 5**. k tính trên **số nhóm sau gộp**, không tính trên số ví.
- **k = 1 là mốc đối chứng, định nghĩa giống hệt các k khác:** lần đầu tiên bất kỳ nhóm nào vào một sự kiện + cửa, cùng các lọc Q4, cùng giá Q5, cùng giữ tới chốt Q7, mỗi sự kiện chỉ tính 1 lần. Không được định nghĩa k = 1 lỏng hơn rồi so sánh với k ≥ 2 chặt hơn.
- Chỉ tìm k tốt nhất trên **đoạn trong mẫu (đoạn 2)**. Một k muốn được xét phải có **ít nhất 100 tín hiệu trong mẫu** (không phải 50).
- **Công thức chọn k\* (thay cho "lãi cao nhất thô"):**
  - Điểm_k = ROI_k − sai số_k
  - sai số_k = (độ lệch chuẩn lãi mỗi tín hiệu của k đó) / 100 / √(n_k), với n_k là số tín hiệu của k trong mẫu. (Chia 100 để quy về đơn vị ROI theo đồng đặt; chia căn n_k để có sai số chuẩn của trung bình.)
  - Chọn k có Điểm_k cao nhất, và k đó phải thỏa CẢ BA: Điểm_k > 0, ROI_k > 0, và ROI_k ≥ ROI_1 + 0,03 (hơn k = 1 ít nhất 3 điểm phần trăm).
  - Nếu không có k nào thỏa cả ba thì **dừng ở sàng lọc, không chọn k\* nào**.
  - Nếu Điểm_k của hai k tốt nhất chênh nhau dưới 0,02 thì chọn k có nhiều tín hiệu hơn, vì nó bền hơn.
- **Khóa k\*** lại, test đúng **một lần** trên đoạn ngoài mẫu. Đoạn ngoài mẫu đã dùng một lần thì không được quay lại thử k khác trên cùng đoạn đó.
- Báo cáo phụ đếm theo tổng tiền (thay vì số ví) chỉ để mô tả, không bao giờ được dùng để cứu verdict khi bảng chính thua. Nếu đếm theo tiền thắng mà đếm theo ví thua thì ghi rõ hai bảng khác nhau.
- Chỉ k mới được tối ưu trên đoạn trong mẫu. Không được tối ưu thêm cửa sổ, ngưỡng tiền, khoảng giá hay luật chọn người trên cùng đoạn trong mẫu rồi vẫn gọi là "chỉ tối ưu k". *(D4 ảnh hưởng hằng số cửa sổ 24h/0,10 — nếu chủ nhân chốt 6 giờ thì thay tại Q4 và báo cáo phụ 24 giờ, xem mục 15.)*

## 12. Q9 — Cổng giết 3 TẦNG (áp cho k\* đã khóa, sau phí theo ngày + phạt trễ chính)

Mọi ngưỡng là "lớn hơn hẳn", không làm tròn lên. Ví dụ 99 tín hiệu là trượt, 4,9% không làm tròn thành 5%.

### Tầng 1 — Sàng lọc, phải qua HẾT mới được theo tiếp

1. Số tín hiệu: trong mẫu ≥ 100, ngoài mẫu ≥ 100, tổng ≥ 200. Đếm theo thời điểm kích hoạt, theo định nghĩa số đếm đã khóa ở Q6 và Q7.
2. Ngoài mẫu lãi ròng > 0.
3. Ngoài mẫu lãi ròng vẫn > 0 khi **thay phạt trễ bằng 0,05**, tính lại toàn bộ từ đầu (cổ phần mới, phí mới).
4. Ngoài mẫu lãi / tổng tiền đặt > 5%.
5. Ngoài mẫu lãi / tổng tiền đặt **cao hơn k = 1**, cùng đoạn, cùng mẫu số, cùng công thức.
6. Trong mẫu ở k\* cũng phải dương và hơn k = 1. Nếu trong mẫu đã xấu mà ngoài mẫu may mắn thì logic test đã vỡ, không được qua bằng chữ.
7. 5 tín hiệu lãi nhất đóng góp **dưới 50%** tổng lãi ngoài mẫu, tín hiệu lãi nhất **dưới 25%**, và **bỏ 10 tín hiệu lãi nhất đi mà lãi ngoài mẫu vẫn > 0**. Đóng góp tính bằng lãi ròng từng tín hiệu, không tính bằng tiền thắng gộp.
8. Tỷ lệ bỏ tín hiệu ≤ 30% và tỷ lệ chưa chốt sau ân hạn ≤ 10%.

### Tầng 2 — Xác nhận, mới được gọi là sống

- **Khoảng tin cậy 95%** của lãi ngoài mẫu trên tổng tiền đặt, tính bằng **lấy mẫu lại theo sự kiện (bootstrap gom theo sự kiện, không gom theo từng tín hiệu)**, phải nằm **hoàn toàn trên 0**, và lãi trên tổng tiền đặt vẫn > 5%.
- Thực tế: ở 200 tín hiệu, khoảng này thường rộng ±14–21%, nên lãi quan sát 5% chưa đủ kết luận. Nếu khoảng chứa 0 thì kết luận thống kê là **"chưa đủ bằng chứng"**, không phải sống, cũng không phải chết. Muốn kết luận thì phải kéo dài test theo luật định trước ở Q10, không được đổi k.

### Tầng 3 — Cờ mô tả (không lật verdict chính, trừ khi chủ nhân quyết trước khi đóng băng — D1)

- Không một giải duy nhất nào chiếm trên 50% lãi ngoài mẫu; không một môn duy nhất nào là nguồn lãi duy nhất trong khi các môn còn lại lỗ nặng; và lãi khi **bỏ World Cup** đi vẫn > 0. Nếu vi phạm thì ghi rõ là lãi tập trung, dù tổng có qua tầng 1 và 2.
- Top 3 sự kiện đóng góp bao nhiêu % lãi ngoài mẫu cũng phải báo cáo, vì một sự kiện có nhiều thị trường có thể phình mẫu.

### Verdict

- Thiếu bất cứ cổng nào ở tầng 1 → verdict là **CHẾT**, không sửa k, không sửa giá, không sửa luật chọn người. Muốn thử hướng khác thì viết spec v2 mới.
- Qua tầng 1 nhưng chưa qua tầng 2 → verdict là **CHƯA ĐỦ BẰNG CHỨNG**, đi tiếp test giấy về trước với mẫu lớn hơn.
- Qua cả tầng 1 và tầng 2 → **SỐNG** ở backtest, và vẫn phải qua test giấy về trước ở Q10 mới bàn bước tiếp theo.

## 13. Q10 — Test giấy về trước: TEST LUẬT, CHỌN LẠI NGƯỜI MỚI TẠI NGÀY GO

- Chỉ làm sau khi backtest qua tầng 1 và tầng 2, và kiểm toán độc lập CONFIRMED.
- **Test này test LUẬT, không test 20 ví cũ.** Tại ngày GO, chọn lại 20 nhóm bằng đúng luật Q3 từ 90 ngày trước GO, dùng đúng các lọc, xếp hạng và gộp nhóm đã khóa. Điều này phải ghi rõ trong spec trước khi GO. Nếu chủ nhân muốn test đúng 20 ví cũ thì đó là một spec khác, phải ghi rõ trước khi GO. *(Đây là chỗ D2 chưa chốt — xem mục 15.)*
- **Thu thập:** ghi sổ giấy, không đặt lệnh thật. Chu kỳ thăm dò, nguồn phát hiện, và cách ghi thời điểm phát hiện phải khóa trước khi GO. Ví dụ cho trước trận: thăm dò Data API v2 activity / trades mỗi 5 phút, trigger khi đủ k, giá forward tính đúng luật Q5, và ghi độ trễ từng tín hiệu (thời điểm giao dịch so với thời điểm phát hiện). Nếu độ trễ trung bình quá lớn so với backtest thì ghi rõ, không được lấy kết quả backtest để che độ trễ forward.
- **Ngân sách request** cho forward phải ghi trước: số request mỗi ngày, checkpoint bằng timestamp, dừng khi gặp 429 và chờ theo Retry-After, không tăng tốc để bù khoảng trống. Nếu thiếu trên 10% số ngày thu thập, hoặc thiếu đúng giai đoạn cao điểm, thì test forward bị coi là thiếu dữ liệu, không được tiếp tục như không có gì.
- **Mốc kiểm tra giữa kỳ:** 200 tín hiệu đã chốt, chỉ kiểm tra số lượng và chất lượng dữ liệu, không phán xét lãi.
- **Mốc phán xét cuối:** ít nhất **500 tín hiệu đã chốt + ít nhất 90 ngày**, lấy mốc nào tới sau, tối đa 12 tháng để xem lại. Nếu sau 12 tháng chưa đủ 500 tín hiệu đã chốt thì ghi là thiếu mẫu. Trước khi chạy forward, tính trước số tín hiệu cần từ độ lệch chuẩn và lãi ở backtest. Nếu tốc độ đo được cho thấy không thể tới 500 trong 12 tháng thì không nên bắt đầu forward với k đó, hoặc phải chấp nhận trước là kết quả sẽ chỉ ở tầng chưa đủ bằng chứng.
- **Cổng cho test về trước:** áp đúng cổng tầng 1 và tầng 2 của Q9, nhưng thay số đếm trong mẫu + ngoài mẫu bằng số đếm của tập về trước (≥ 500 tín hiệu đã chốt). "Đã chốt" = đã resolved, không phải đã hết trận. Sau mốc thu thập, chờ tối đa 30 ngày để các tín hiệu đã thu thập chốt xong rồi mới phán xét.
- **Thời điểm bắt đầu:** nên rơi vào đầu một giai đoạn mùa thường, không rơi vào giữa playoff hay giữa giải lớn, trừ khi ghi rõ là test riêng cho playoff hay giải lớn. Nếu 200 tín hiệu tới giữa một giải lớn đang chạy thì chờ giải đó kết thúc và mọi tín hiệu của giải đó chốt xong rồi mới phán xét.

## 14. Bảng báo cáo bắt buộc (tổng hợp từ Q1–Q10, không chỉ báo cáo tổng)

1. Tách theo **môn** (Q1).
2. Tách theo **loại thị trường**: thắng thua / chấp điểm / tổng điểm / kèo cầu thủ (Q1).
3. Tách theo **mùa thường / playoff / giải lớn**; báo cáo chính vẫn tính cả World Cup, báo cáo phụ tách riêng World Cup; lãi khi bỏ World Cup (Q1, Q9 tầng 3).
4. Tách theo **dải giá**: 0,10–0,30 / 0,30–0,70 / 0,70–0,90 (Q6).
5. Tách theo **độ lớn thị trường** (Q1).
6. Tách theo **sự kiện**: top 3 sự kiện đóng góp % lãi ngoài mẫu (Q9 tầng 3).
7. **Hao hụt hoạt động**: bao nhiêu nhóm trong 20 còn hoạt động ở đoạn 2, đoạn 3 (Q2).
8. **Tỷ lệ bỏ tín hiệu + lý do bỏ** từng loại (thiếu độ sâu, không có giao dịch trong 60 phút, đầy vốn, ngoài khoảng giá) (Q6).
9. **Tỷ lệ chưa chốt sau ân hạn 14 ngày** và **thời gian chờ chốt thực tế** (Q7).
10. **Bảng k = 1 đối chứng** cùng công thức, cùng mẫu số (Q8, Q9).
11. **Báo cáo phụ đếm theo tổng tiền** (không dùng để chọn k hay cứu verdict) và **báo cáo phụ ngưỡng 50/200 USD** thay 100 USD, và **báo cáo phụ cửa sổ 6 giờ / 24 giờ còn lại** (chỉ mô tả) (Q4, Q8, D4).
12. **Nhạy cảm phạt trễ 0,05 và 0,10 (thay thế, không cộng)** (Q5).
13. **Số tín hiệu bị bỏ vì chặn giá chạy quá 0,10 và vì ngoài khoảng 0,10–0,90**; cờ cảnh báo nếu trên 20% tổng kích hoạt (Q4).
14. **Độ trễ forward từng tín hiệu** so với backtest (Q10).
15. **Ghi chú giới hạn**: gộp nhóm chỉ là nghi ngờ cùng người; tỷ lệ bỏ > 30% giới hạn phạm vi áp dụng (Q3, Q6).

## 15. 5 QUYẾT ĐỊNH MỞ D1–D5 — NGUYÊN VĂN TỪ FILE TỔNG HỢP, ĐÁP ÁN ĐỂ TRỐNG

> Chỉ chủ nhân được điền. Không được tự chọn. Điền xong mới được đóng băng.

**D1.** World Cup và giải lớn chiếm trên 50% lãi: chỉ là cờ mô tả, hay nâng thành cổng giết?
    Đề xuất của tôi: cờ mô tả ở v1, vì định nghĩa giải lớn bằng trường dữ liệu còn cần thăm dò xác nhận.
    Nếu bạn muốn chặt hơn thì nâng thành cổng trước khi đóng băng, không nâng sau khi thấy kết quả.

    ĐÁP ÁN CHỦ NHÂN: ____________________ (TRỐNG — CHƯA QUYẾT)

**D2.** Test giấy về trước dùng cohort mới chọn lại bằng đúng luật cũ (đề xuất của tôi), hay dùng đúng 20 ví cũ từ backtest?
    Đề xuất: cohort mới, vì test luật chạy thật. Cohort cũ chỉ đo nhóm người đã cũ 12–15 tháng.

    ĐÁP ÁN CHỦ NHÂN: ____________________ (TRỐNG — CHƯA QUYẾT)

**D3.** Mỗi nhóm đếm từ 100 USD ròng (đề xuất của tôi) hay 200 USD như góc thực hành?
    100 USD giữ được nhiều ví nhỏ nghiêm túc hơn, 200 USD lọc nhiễu tốt hơn nhưng làm mẫu nhỏ đi.

    ĐÁP ÁN CHỦ NHÂN: ____________________ (TRỐNG — CHƯA QUYẾT)

**D4.** Cửa sổ overlap 24 giờ + chặn giá chạy quá 0,10 (đề xuất của tôi) hay 6 giờ như góc phê bình và góc thực hành?
    24 giờ + chặn giá giữ được tín hiệu trước trận ra tin trong ngày, 6 giờ giảm hiệu ứng bầy đàn nhưng có thể làm mẫu nhỏ đi.
    Dù chọn cách nào thì cửa sổ 6 giờ và 24 giờ còn lại cũng được báo cáo phụ, không dùng để đổi k*.

    ĐÁP ÁN CHỦ NHÂN: ____________________ (TRỐNG — CHƯA QUYẾT)

**D5.** Ngưỡng lệnh chọn người là 80 lệnh (đề xuất của tôi) hay 100 lệnh như góc phê bình?
    80 lệnh giữ được chuyên gia môn ít trận hơn, 100 lệnh bớt may rủi hơn nhưng có thể loại chuyên gia NFL và trận nhỏ.

    ĐÁP ÁN CHỦ NHÂN: ____________________ (TRỐNG — CHƯA QUYẾT)

## 16. DANH SÁCH THIẾU — CHỈ ĐƯỢC ĐIỀN TỪ KẾT QUẢ THĂM DÒ (GIAI ĐOẠN B), KHÔNG ĐOÁN

| # | Mục thiếu | Nơi ảnh hưởng | Cách xác nhận |
|---|---|---|---|
| 1 | Tên trường thật: mã thị trường, mã cửa (token_id / outcomeIndex / clobTokenIds), giá, tiền (usdc_size), thời gian (đơn vị giây hay mili-giây), kết quả chốt | Q2–Q10 toàn bộ | Bước thăm dò a, c, d, e |
| 2 | Tên tham số takerOnly trên contract v2 (còn tồn tại hay đổi tên) | Q5 | Bước a, c |
| 3 | Trường tag / category / event của Gamma xác định "thể thao" + bộ giá trị + quy tắc thị trường 2 tag | Q1 | Bước d |
| 4 | Trường feeSchedule của thị trường + xác nhận bảng phí theo ngày (0 / 0,03 / 0,05) | Q5 | Bước d |
| 5 | Đầu mối resolutions của Data API (có thật không, tham số gì) + giá chốt hòa 0,5 thực tế | Q7 | Bước e |
| 6 | Hạt thời gian (fidelity/granularity) thực tế của prices-history cho cửa sổ 7 ngày và 90 ngày | Q5 (kiểm tra giá), thăm dò | Bước f |
| 7 | Nguồn pool ứng viên + tham số leaderboard thật (window, sports) | Q3 | Bước b |
| 8 | Khả năng lấy spread tại thời điểm kích hoạt từ sổ lệnh lịch sử | Q5 | Bước thăm dò chung |
| 9 | Cách tính khối lượng thị trường TỚI THỜI ĐIỂM kích hoạt (chống rò rỉ tương lai) | Q4.7 | Bước thăm dò chung |
| 10 | Mốc T0/T1/T2/T3 tuyệt đối của 3 đoạn 90 ngày (ngày UTC cụ thể) | Mục 3 | Sau thăm dò, chủ nhân chốt trước khi đóng băng |
| 11 | Quy tắc làm tròn giá, cổ phần, phí | Q5 | Chủ nhân quyết trước khi đóng băng |
| 12 | Ưu tiên nguồn chốt khi Gamma và Data API lệch nhau | Q7 | Chủ nhân quyết trước khi đóng băng |
| 13 | Định nghĩa "giải lớn" bằng trường dữ liệu nào | D1, Q9 tầng 3 | Bước d + chủ nhân chốt D1 |
| 14 | Đơn vị timestamp thực tế trả về từ từng endpoint (giây / mili-giây) | Q2, Q4 | Bước c, e, f |

## 17. Quy trình sau spec nháp này (không tự chạy, chờ lệnh từng bước)

1. Giai đoạn B: thăm dò dữ liệu nhỏ, chỉ đọc, theo checklist a–g, đi chậm, checkpoint bằng timestamp, dừng toàn bộ khi 429/403/throttle. Báo cáo thăm dò KHÔNG kết luận lãi, KHÔNG chọn k, KHÔNG chọn 20 ví cuối.
2. Chủ nhân chốt D1–D5 + điền các mục THIẾU đã xác nhận được từ thăm dò.
3. Chủ nhân ra lệnh GO riêng → khi đó mới viết spec đóng băng + sha256, rồi mới bàn backtest theo đúng quy 6 bước của bản nháp gốc (thăm dò → hồ sơ → đóng băng → backtest → kiểm toán độc lập → test giấy về trước).

## 18. Spec này KHÔNG làm (đọc kỹ trước khi dùng)

- Không phải spec đóng băng, không có hash.
- Không chạy backtest tính điểm, không tuyên bố sống/chết.
- Không điền D1–D5, không điền các mục THIẾU bằng suy đoán.
- Không đặt lệnh thật, không chuẩn bị lệnh thật, không nối sàn.
- Không dùng file này để "chọn k đẹp" hay "chọn người đẹp" trước khi có dữ liệu.
