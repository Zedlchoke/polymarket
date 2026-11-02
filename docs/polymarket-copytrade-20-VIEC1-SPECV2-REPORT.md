# BÁO CÁO VIỆC 1 — SPEC V2 NHÁP — 2026-11-02

File spec v2 nháp: polymarket-copytrade-20-SPEC-V2-DRAFT.md (CHƯA ĐÓNG BĂNG, CHƯA CÓ HASH, CHƯA CHẠY TÍNH ĐIỂM).

## 4 mục đúng theo prompt

1. **File ở đâu:** ~/workspace/your_files/polymarket-copytrade-20-SPEC-V2-DRAFT.md (và bản push GitHub trong repo Zedlchoke/polymarket).

2. **Khác với spec v1 — đúng 2 thay đổi, luật khác giữ nguyên (liệt kê 12 nhóm giữ nguyên tại mục 1 của file):**
   - THAY ĐỔI 1 — POOL: từ leaderboard tháng sang quét thị trường đoạn 1: (2.1) Gamma include_tag=true, ưu tiên start_date_min/max + sports_market_types + closed, BẮT BUỘC xác minh bằng gameStartTime ∈ [T0, T1); tra mã = lặp condition_ids + closed=any; hợp lệ = tag 'Sports' + smt + gst trong đoạn 1, trận đơn, không mùa vụ, mùa vụ đếm riêng; (2.2) sàng lọc rẻ THEO KHỐI LƯỢNG cộng dồn TRONG ĐOẠN 1 (không volumeNum cuối), không theo lãi; (2.3) trades/activity taker_only=false CHỈ timestamp đoạn 1, cursor tới null, checkpoint ts+conditionId, 200 req/ngày 10 giây; (2.4) tổng hợp ví + đúng 10 cửa Q3 + gộp nhóm v1, lãi giữ-tới-chốt chỉ tính lệnh chốt tới cuối đoạn 1.
   - THAY ĐỔI 2 — OVERLAP: kỷ nguyên B = KHÔNG ÁP DỤNG / THIẾU MẪU (sổ PaperDesk chỉ phủ 07–31/10/2026; 0/32 lệnh trong kỷ nguyên; không trường ánh xạ); cấm ghi "0% overlap"/"hai hệ thống khác nhau"; overlap chuyển sang giai đoạn về trước, SAU khi có bộ ánh xạ match_id+home/away+kickoff_utc → conditionId/token (spec riêng; >20% không ánh xạ = THIẾT DỮ LIỆU ÁNH XẠ); bản nháp chỉ ghi yêu cầu, không xây; quy tắc chạy giữ nguyên v1 (chỉ mô tả, CẤM cứu verdict, 24h trước, <30 = thiếu mẫu).

3. **Đề xuất chờ duyệt:** (i) ngưỡng sàng lọc thị trường ≥10.000 USD giao dịch trong đoạn 1 (mục 2.2) — ĐỀ XUẤT, phải báo số thị trường bị bỏ; (ii) kỹ thuật liệt kê start_date_min/max phải xác minh bằng gameStartTime, endpoint không lọc được thì quét phân trang + lọc client, số request báo ở bước đếm; (iii) không ngưỡng mới nào khác (các ngưỡng 5%/20%/50 ví/8+5%/5 phút là v1 đã duyệt, giữ nguyên).

4. **Xác nhận:** chưa đóng băng v2, chưa chạy hồ sơ, chưa chạy backtest, chưa chạy về trước. Không dùng kết quả v1 nào (v1 không có kết quả tính điểm). Lựa chọn "làm cả hai" chưa phải lệnh GO.
