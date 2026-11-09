# KIỂM TOÁN ĐỘC LẬP TOÀN BỘ VIỆC 3 + BẢN SỬA LIỆT KÊ — 2026-11-09

## KẾT LUẬN: CONFIRMED

Toàn bộ số chính của báo cáo bản sửa (@9c3698f) được tính lại độc lập từ đĩa và KHỚP 100%: 71.351 duy nhất / 19.230 HỢP LỆ (T9 1.346, T10 4.128, T11 10.555, T12 3.201), mọi bucket lọc, 1.305 request thật đúng trần từng ngày, 63/63 lá tự nhiên + 105/105 ngày + hàng đợi rỗng theo đúng luật hoàn tất. 5 phát hiện nhỏ (mục "Phát hiện lệch chi tiết") đều là nhãn/đếm-mỹ-thuật/khẩu ngữ, KHÔNG con số chính nào sai. Không phát hiện lỗi mới chưa khai.

---

## Danh sách file đã mở + hash/commit

- docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md — blob e5b45ecf61e46dce7b552c2269bc946b26aff6b0 @8727bcc == HEAD; shasum-256 ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8
- docs/AUDIT_POLYMARKET_VIEC2_FREEZE_SPECV2_2026-11-03.md — blob c593dda1 @0514c51 == HEAD
- docs/AUDIT_POLYMARKET_VIEC3_COUNT_2026-11-03.md — blob cc0a1491 @d8f2bb9 == HEAD
- docs/polymarket-copytrade-20-VIEC3-FIX-FINAL-2026-11-09.md @9c3698f (bị kiểm chính); 5 interims @f2cd581/7634d8b/040802a/02d8f3f/c1a7cd4; báo cáo gốc @85f8732; missing_slices_pre_run @b0527d8
- viec3/data/: ledger.jsonl (1.351 dòng), listing/ (22 page gốc + slices/ 282 + slices3/ 942 page gz = 1.246 file), listing_slim.jsonl.valid_FULL, coverage_fixed.json, recount.json, final_completion_verification.json, final_stats.json, final_numbers.json, slices3_status.json, slices3_progress.json, list3_run_day5/6/6b/6c/8/9.log, smoke/ (g_market_body, k_offset100, h_condition_id…), recheck/ (spotcheck_lateenddate, closedany_p1, recheck_*), viec3.lock.dead.log; listing_slim.jsonl.valid @85f8732 (lấy qua git show)
- viec3/scripts/v3_phase_list3.py (đọc để hiểu luật/định dạng; tính lại bằng script riêng /tmp/audit_b_count.py, /tmp/audit_c_tree.py, /tmp/audit_de_ledger.py, /tmp/audit_e_oldset.py — không dùng code của bước)
- HEAD khi kiểm toán: 9c3698f (main); agent kiểm toán: độc lập, offline 100% (0 request ra ngoài)

## A. Nguyên vẹn chuỗi

ĐẠT. shasum-256 spec hiện tại = ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8 == hash luật == `git show 8727bcc:<spec> | shasum -a 256`; blob git e5b45ecf giống nhau @8727bcc và @HEAD; `git diff 8727bcc..HEAD -- <spec>` rỗng. Audit cũ: blob VIEC2 c593dda1 không đổi 0514c51→HEAD (diff rỗng); blob VIEC3 cc0a1491 không đổi d8f2bb9→HEAD (diff rỗng). Ghi chú trung thực: `git diff 0514c51..HEAD -- docs/AUDIT*` không rỗng hoàn toàn — vì file audit VIEC3 được TẠO tại d8f2bb9 (sau 0514c51); đã đối chiếu blob từng cặp để loại trừ mọi sửa đổi. Ngoài ra mỗi log chạy ngày 5/6/6b/6c/8/09 ghi đầu log "Hash spec khớp luật ae504a97…" / preflight "HASH SPEC: KHỚP".

## B. Số đầy đủ (tính lại độc lập từ 1.246 trang gz)

KHỚP 100%, không lệch con số nào:
- Tổng dòng trang: 111.672 (báo cáo: 111.672) — UNION THEO id: **71.351** (báo cáo: 71.351)
- Bucket theo luật (tag label đúng chữ 'Sports' + smt ≠ rỗng + 1757721600 ≤ epoch(gst, làm tròn xuống) < 1765497600): tag_rỗng **0** / anomaly (không Sports, có smt) **978** / phi_thao (không Sports, không smt) **40.104** / mùa_vụ (Sports, smt rỗng) **9.361** / thiếu_gst **229** / gst_trước T0 **159** / gst_sau T1 **1.290** / HỢP_LỆ **19.230** — tổng đúng 71.351. Cả 8 số khớp báo cáo.
- Tháng gst HỢP_LỆ: T9 **1.346** · T10 **4.128** · T11 **10.555** · T12 **3.201** — khớp.
- listing_slim.jsonl.valid_FULL: 19.230 dòng; 19.230 id duy nhất; 19.230 conditionId duy nhất; TẬP HỢP HỢP_LỆ tính từ đĩa == tập hợp valid_FULL TRỌN VẸN (giao 19.230, chênh lệch 2 phía = 0); 抽查 30 dòng: gameStartTime_epoch tính lại từ chuỗi gốc trong trang gz khớp 30/30.

## C. Hoàn tất theo luật (dựng lại cây bằng code riêng)

ĐẠT THEO LUẬT. Dựng lại toàn cây từ gốc [2025-09-13 → 2025-12-26] với luật: tự nhiên = trang ngắn <100 hoặc rỗng @<2100; rỗng @≥2100 = CỤT phải chia; probe-only (page_2000=100, không page_0) = CAP:
- **63/63 LÁ tự nhiên**; 0 lá CỤT/PARTIAL/CAP chưa chia (BAD_MISSING_CHILD=0); 0 cửa sổ mồ côi ngoài cây; 0 lát GIỜ (0 unresolved-giờ).
- Phủ **105/105 ngày** [2025-09-13→2025-12-26]: không thiếu ngày, không trùng ngày.
- Trạng thái cây: 125 node duy nhất = 63 NATURAL + 25 CỤT(rỗng@≥2100) + 37 CAP (9 CAP kết luận nhờ dò-trước trong slices3/).
- Log list3_run_day9.log: có dòng "KẾT THÚC" bình thường (kèm "lát=129 (natural=63)"), **0 lần "DỪNG THEO LUẬT"** trong log ngày 09/11 (các log ngày 5/6/6b/6c/8 có 1-2 lần dừng đúng luật của interim — đúng bản chất từng ngày).
- Nhận định "complete=false chỉ là lỗi công thức": ĐÚNG. Công thức tại v3_phase_list3.py đòi `all(node.status=='NATURAL')` trên CẢ node CHA đã chia (CAP_split/CAP_probe) — vốn không thể NATURAL theo thiết kế → complete mãi mãi False dù luật đã đạt. Điều kiện luật thật (mọi LÁ tự nhiên + hàng đợi rỗng) tôi đã xác minh độc lập ở trên. (slices3_progress.json còn queue=11 chỉ là checkpoint giữa chừng; trạng thái cuối là slices3_status.json + final_completion_verification.json, khớp dựng lại của tôi.)

## D. Sổ & trần request

KHỚP 100%. Đếm lại từ ledger.jsonl (thật = status VÀ latency_ms; ngày = ts+7h Saigon): 03/11 **358** · 04 **200** · 05 **200** · 06 **172** · 07 **0** (không dòng nào) · 08 **200** · 09 **175** — tổng **1.305** (1.351 dòng sổ = 1.305 thật + 46 không-phải-request). Khoảng cách <9s giữa request thật liên tiếp: 03/11 = **33** (đúng như khai lỗi 2 tiến trình; nhỏ nhất 3,0s); từ 04/11 = **0** mọi ngày (nhịp chặt nhất 10–11s). Không có 429/403 nào. Dòng E_market_body (status 400, latency None, error "doc-tham-so") đúng là ghi tay không tới server; tag F_condition_id KHÔNG tồn tại trong sổ (request thật tương ứng là H_condition_id, status 200). Mỗi ngày 04–09/11 ≤ 200 theo luật hiện hành; 03/11=358 là lịch sử chạy theo luật phiên cũ (ngày-chạy 1 = 184, phiên 2 = 174, mỗi phiên ≤200 theo trần thời điểm đó) — đã kê khai trung thực, đánh giá theo luật thời điểm đó: CHẤP NHẬN. Ghi chú nhỏ: 1 dòng 06/11 (l3_10-12_10-13_off700, latency 4040, status None) có thể đã chạm server nhưng không được bộ đếm status+latency tính — vô hại với trần (06/11 = 172+28 = 200 theo khai báo watchdog).

## E. Khai báo lỗi/dự phòng (tự xác minh từng con số)

TẤT CẢ KHỚP:
- 25 dòng ngày-chạy 2: DAY_BOUNDARY = **13** (khớp tuyệt đối, toàn bộ 03/11) + SSL_FALLBACK phiên 2 = **12** (hòa giải trọn vẹn toàn cục: 03/11 có 35 dòng không-phải-request = 13 DAY_B + 20 SSL + 1 smoke-SSL + 1 E_market_body; phiên 1 = 9 dòng = 1 smoke-SSL + 8 SSL, đúng 193−184=9; phiên 2 = 25 = 13+12, đúng 200 dòng − 174 thật − 1 E_market_body tay). Báo cáo cũ ghi "10 + SSL + 2 dòng 400" — SAI, errata ĐÚNG.
- 358 ≠ 359: ĐÚNG (358 thật).
- tennis smt = **27**: dựng lại tập hợp thời điểm báo cáo gốc (union chỉ listing/ + slices/ → 16.748 duy nhất, 2.743 hợp lệ — khớp tuyệt đối báo cáo cũ) → tennis_* = 12+9+2+2+2 = **27**; đồng thời toàn bộ số smt khác trong câu mô tả cũ khớp (moneyline 1.784, totals 449, spreads 381, btts 83, nrfi 6, team_totals 4, child_moneyline 9) → errata #3 chính xác. (Lưu ý: trong valid_FULL 19.230 hiện tại tennis_* = 106 — errata nói về mô tả của báo cáo cũ, đúng ngữ cảnh.)
- Ngày 05/11: đúng **9 lát 22-trang cụt** trong slices3 mtime 05/11 (2025-11-12→11-14 … 12-08→12-10, mỗi lát đủ 22 trang offset 0→2100, trang cuối rỗng @2100). Lát thứ 10 trong khai báo "10 lát" (12-11→12-13) có 21 trang chốt 08:29 ngày 05/11, 2 trang cuối xong 00:05 ngày 06/11 — khai "10 lát" chấp nhận được, đĩa xác nhận 9 lát hoàn tất trong ngày 05/11.
- Dò-trước: ledger tag _off2000 = **91** (03/11: 8, 04: 6, 05: 9, 06: 19, 08: 20, 09: 29); dirs probe-only (page_2000=100, không page_0) trong slices3 = **9** — khớp "9 CAP-nhờ-dò". Preflight 2-điểm ghi đầu log ngày 06/6b/08/09 (ĐẠT/ĐẠT).
- Watchdog (latency_ms trong ledger): 06/11 đúng 3 lần **5.437 / 5.235 / 12.202** ms + đúng 1 DNS gaierror; 08/11 đúng 2 lần, max **8.235** ms; 09/11 **0** lần ≥5.000, max **4.567** ms — khớp từng con số. (03/11 có 5.697 và 40.053 ms — đều đã khai trong báo cáo cũ.)

## F. Đối chiếu báo cáo bản sửa mục 1-7

KHỚP TỪNG SỐ:
1. Hash spec ae504a97… — khớp (mục A) + ghi đầu mọi log chạy.
2. 63/63 lá, 105/105 ngày, hàng đợi rỗng, khai lỗi công thức complete — xác minh độc lập ĐẠT (mục C).
3. Lát theo từng ngày: 04/11 (3 lát mới mtime 11-04 kết thúc tự nhiên 81/9/54 dòng + 3 lát xác nhận lại từ cache + lát dở 10-14→16) khớp đĩa; 05/11 (9 lát cụt đầy 2.100) khớp; "Tổng cây 129 node" = 125 node duy nhất + 4 lát bị đếm trùng 2 dòng (CAP_probe + CAP_split cùng lát) — see Phát hiện #1.
4. Bảng request từng ngày + 1.305 + dò 91/9 — khớp tuyệt đối (mục D/E).
5. Bảng số đầy đủ 71.351 + 8 bucket + 4 tháng + valid_FULL — khớp tuyệt đối (mục B).
6. Errata 3 lỗi — cả 3 xác minh ĐÚNG (mục E).
7. Phép tính 14 ngày BẤT BIẾN ĐÚNG: 19.230 thị trường × ≥1 request (bằng chứng smoke/g_market_body.json HTTP 400 — tham số market bị từ chối, phải lọc theo condition từng thị trường; smoke/k_offset100.json HTTP 400 — offset không được hỗ trợ) = ≥19.230 request; hạn 14 ngày = 200×14 = 2.800; 19.230/200 = 96,15 ≈ **96 ngày** > 14 ngày, vượt ≈ 82 ngày — đúng số "~96 ngày / vượt 82+ ngày". Ghi chú khẩu ngữ: cụm "endpoint không cursor/offset" không chặt (chính file k_offset100 cho thấy endpoint phân trang cursor-only; bản chất đúng là: không offset + không gom nhiều thị trường → tối thiểu 1 request/thị trường) — see Phát hiện #3; phép nhân bất biến không đổi.

## G. Rủi ro còn lại (mô tả, không chạy)

- Rò thị trường chốt sau 26/12 nhưng game trong đoạn 1: chỉ được spot-check 1 trang (recheck/spotcheck_lateenddate.json: page1_rows=100, leak_found_on_page1=[]) — bằng chứng MẪU, không chứng minh vô rò. Nếu tồn tại, số 71.351/19.230 là CẬN DƯỚI của tập thật (thiếu, không thừa). Mức độ: có thể làm sai số chính về mặt "đầy đủ tuyệt đối" nhưng không sai tính toàn vẹn của những gì đã liệt kê; rủi ro đã được khai.
- closed=any + end_date: recheck/closedany_p1.json là LỖI VALIDATION (closed=any đòi kèm id/slug/…) — không trả 0 dòng theo nghĩa dữ liệu, truy vấn chưa chạy được → không kết luận được gì. Không ảnh hưởng số chính.
- Mẫu ngưỡng 10k n=9 (6/9 đạt, final_numbers.json sample): chỉ mô tả, không dùng làm luật — đúng nghĩa khai báo. Không ảnh hưởng 71.351/19.230.
- Nhãn bucket "Phi thể thao (không tag Sports) 40.104" trong bảng: 40.104 là nhóm không-Sports VÀ không smt; tổng không-Sports thật = 41.082 (gồm 978 anomaly có smt — dòng con "—anomaly" đã bộc lộ). Bảng cộng đúng 71.351 — chỉ là cách đặt nhãn, see Phát hiện #4.

## H. 3 câu luật

1. **Làm đúng chưa? ĐÚNG.** Mọi số khai báo trong báo cáo bản sửa được tính lại độc lập từ đĩa và khớp tuyệt đối (0 lệch ở 71.351, 8 bucket, 4 tháng, 19.230, 1.305, 6 ngày trần, 63 lá, 105 ngày, 91 dò, 9 CAP-dò, 13 DAY_BOUNDARY, 27 tennis, 3/2/0 watchdog). Điều kiện hoàn tất luật đạt; spec/audit/báo cáo cũ không bị sửa tại chỗ.
2. **Cố gắng hết sức chưa? ĐÚNG.** 6 ngày chạy kỷ luật (0 gap <9s từ 04/11, 0 lần 429/403, watchdog/DNS xử lý đúng giao thức chặt và khai đủ), tối ưu dò-trước khôi phục đúng luật (chỉ phán CAP, không phán xong — preflight 2 điểm đạt từng ngày), 3 lỗi khai báo cũ tự phát hiện và sửa đúng (errata xác minh 3/3), lỗi công thức complete tự chẩn đoán đúng bản chất.
3. **Còn đường hợp lệ cho hồ sơ ≤14 ngày không? KHÔNG.** Chỉ riêng trade đoạn 1 cho 19.230 thị trường hợp lệ đã cần ≥19.230 request ≈ 96 ngày @200/ngày > hạn 2.800 (14 ngày) — bất biến theo bằng chứng endpoint. Pilot/thu-hẹp/đổi-thiết kế/kéo-dài là QUYỀN VÀ QUYẾT ĐỊNH CỦA CHỦ NHÂN (luật KHÔNG dựa trên lãi), đã được mô tả đầy đủ để chủ nhân quyết — agent không tự quyết: đúng phận.

## Phát hiện lệch chi tiết (không đổi số chính, không cần làm lại)

1. "Tổng cây: 129 node" (báo cáo mục 3 + dòng KẾT THÚC log ngày 09/11): đếm trùng — cây có 125 node duy nhất; 4 lát probe-cap được ghi 2 dòng tree (CAP_probe + CAP_split cùng lát) → 129. Mỹ thuật đếm, vô hại.
2. "Ngày 05/11: 10 lát" : 9 lát hoàn tất trong ngày (mtime 05/11), lát thứ 10 (12-11→12-13) xong 00:05 ngày 06/11. Khai theo phiên chấp nhận được.
3. Cụm "endpoint không cursor/offset" (mục 7): không chặt chữ nghĩa (k_offset100 chứng minh có cursor-only); bất biến "≥1 request/thị trường" vẫn đúng — kết luận 96 ngày không đổi.
4. Nhãn "Phi thể thao (không tag Sports) 40.104": nên đọc "không tag Sports VÀ smt rỗng"; tổng không-Sports = 41.082. Bảng tự cân bằng 71.351 nhờ dòng anomaly.
5. 1 dòng ledger 06/11 có latency nhưng status None có thể đã chạm server mà không vào bộ đếm trần — hệ quả = 0 với mọi kết luận.
Các lỗi ĐÃ KHAI + đã sửa trong quá trình (nhịp 03/11 33 gap do 2 tiến trình — xác minh đúng 33, đã khai trong báo cáo cũ, hết từ 04/11; E/F — xác minh đúng như errata; công thức complete — chẩn đoán đúng): đều là lỗi kỷ luật khai báo/trạng thái, không chạm dữ liệu, đã sửa ngay trong quá trình — mức độ NHẸ, xử lý trung thực.

---

Tôi xác nhận đã đọc file gốc, không dựa vào bản tóm tắt chat. Tôi không sửa file nào của bước đó, không chạy lại bước đó để thay kết quả, không áp dụng cơ chế nào vào hệ thống thật.
