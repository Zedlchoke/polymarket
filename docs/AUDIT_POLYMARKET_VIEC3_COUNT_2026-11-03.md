# KIỂM TOÁN ĐỘC LẬP VIỆC 3 — ĐẾM MÔ TẢ POOL V2 (NGÀY 1+2) — 2026-11-03

**KẾT LUẬN: BUG FOUND.** Verdict gốc của agent Việc 3 (commit 85f8732): *"CHƯA CÓ VERDICT SỐNG/CHẾT — chỉ đếm mô tả; kết luận VƯỢT 14 NGÀY cho hồ sơ chính (ước 5.000–12.000 request ≈ 25–60 ngày @200/ngày); DỪNG chờ chủ nhân."*

- Mọi số đếm trong báo cáo được tôi tính lại độc lập từ dữ liệu gốc trên đĩa và **khớp chính xác 100%** (28.992 dòng trang; 16.748 id duy nhất; 2.743 hợp lệ; 8.557/257/4.720/166/305; 845/862/786/250; 6/9 đạt; 236 ví; sổ ngày 1 = 193/184).
- **NHƯNG** bản thân việc liệt kê **chưa hoàn tất**: bisection dừng giữa chừng với **24 lát CAP không có lát con** (chưa từng có 1 request nào cho lát 1–2 ngày — chứng minh từ ledger), trong khi 28 lát dò-trước trả 100 dòng ở offset 2000 chứng minh mỗi cửa sổ đó có **≥2.100 dòng** mà đĩa chỉ giữ 128–3.324 id. Báo cáo khẳng định *"liệt kê xong 105/105 ngày / 11 lát hoàn chỉnh ghép phủ kín"* là **SAI** — phủ kín theo khoảng ngày ≠ đủ theo dòng. Do đó **16.748 và 2.743 là số đếm chính xác CỦA ĐĨA nhưng chỉ là CẬN DƯỚI của pool thật** → **verdict đếm TREO, phải đếm lại phần liệt kê** (xem mục 6).
- Không ảnh hưởng xấu đến kết luận ngân sách: pool thật ≥ 16.748 → hợp lệ thật ≥ 2.743 → kết luận "VƯỢT 14 NGÀY" càng vững (chi tiết mục 7).

Kiểm toán hoàn toàn OFFLINE (không gọi API Polymarket nào), chỉ đọc đĩa + git, tự tính bằng code riêng trong `/tmp/audit_viec3/` (không ghi vào `viec3/`).

---

## 1. Danh sách file đã mở + hash/commit

| File | Nguồn | SHA-256 (12–16 ký tự đầu) | Kết quả |
|---|---|---|---|
| `docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md` | đĩa @HEAD 85f8732 | `ae504a97feb50204…` (nguyên vẹn) | **KHỚP** hash tuyên bố; blob tại commit đóng băng 8727bcc cũng = `ae504a97feb50204…`; `git diff 8727bcc..85f8733 -- <file>` rỗng → **spec không đổi trong suốt Việc 3** |
| `docs/polymarket-copytrade-20-VIEC3-COUNT-REPORT.md` | blob @85f8732 | `c1f72979cbf3ce96…` (nguyên vẹn) | File trên đĩa identical với blob; đây là bản dùng đối chiếu |
| Báo cáo giữa kỳ ngày 1 | commit `294a51e` | — | **Không có file docs/ nào của Việc 3 tại 294a51e** — "báo cáo giữa kỳ" chính là commit message; nội dung message nhất quán với ledger ngày 1 (193 dòng, offset-cap 422, dừng watchdog) |
| `viec3/data/ledger.jsonl` | đĩa = git HEAD | `1994340c233d` | 393 dòng |
| `viec3/data/final_numbers.json` | đĩa = git HEAD | `d90265e5c21c` | |
| `viec3/data/listing/coverage_disk.json` | đĩa = git HEAD | `c39e73e17b40` | artifact tự viết, không có script sinh (grep toàn scripts/ không thấy) — xem bug mục 6 |
| `viec3/data/listing/listing_slim.jsonl.valid_FULL` | đĩa = git HEAD | `916a3fd52cc0` | 2.743 dòng, nguyên vẹn |
| `viec3/data/trades/wallets_union2.json` | đĩa = git HEAD | `4c767b7387d0` | |
| `viec3/data/smoke/i_cid_window.json` | đĩa = git HEAD | `9f8b4e492b2c` | 445 fill thô (thị trường debug) |
| `viec3/data/recheck/recheck2_result.json` | đĩa = git HEAD | `2aa353c06032` | |
| `viec3/scripts/v3_phase_list2.py` | đĩa | `60b9d7b0e27ae161…` | |
| `viec3/scripts/v3_phase_trades2.py` | đĩa | `bd28d20d34bdf725…` | |
| `viec3/scripts/viec3_lib.py` | đĩa | `6f9a958ad33fbfcb…` | |
| `viec3/scripts/v3_phase_analyze.py`, `v3_phase_recheck.py`, ledger_days.json, checkpoint.json, slices_progress.json, các log `listing2_*.log`, toàn bộ 304 trang gz, 41 lát, 8 summary2, recheck/*, smoke/* | đĩa | — | đã đọc/phân tích |

**File không mở được / không tồn tại (quan trọng):**
- `viec3/data/analysis_counts.json`, `analysis_trades.json` — **không tồn tại trên đĩa, không từng được commit** (chỉ là output trung gian của script phân tích cũ; số 22.287 chỉ流传 trong chat — xem mục 6.4).
- **Dữ liệu thô fills của 8 thị trường mẫu trades2 KHÔNG được lưu** (summary2.json chỉ chứa số gộp + danh sách ví) → tôi không thể tái tính hoàn toàn độc lập USD của 8 thị trường đó offline; chỉ tái tính được thị trường debug từ `smoke/i_cid_window.json` (mục 4c). Giới hạn bằng chứng, không phải lỗi số.
- Dữ liệu thô phản hồi recheck lần 2 (có tag) không lưu — chỉ có summary `recheck2_result.json` (mục 6.3).

---

## 2. Bảng đối chiếu TỪNG số của báo cáo với dữ liệu gốc

| # | Số tuyên bố (báo cáo @85f8732) | Tự tính lại từ đĩa | Kết luận |
|---|---|---|---|
| 1 | Hash spec v2 = ae504a97… | `shasum -a 256` toàn file = ae504a97feb50204…bee55d8 | KHỚP |
| 2 | Tổng dòng Gamma mọi trang mọi lát = 28.992 | Σ 304 file gz = 28.992 (23 trang run-1 + 281 trang lát; gồm bản copy) | KHỚP (nhưng là "tổng dòng trên đĩa", không phải toàn pool — mục 6) |
| 3 | Thị trường duy nhất = 16.748 | union id = 16.748 (12.244 dòng trùng giữa các trang; **0 mâu thuẫn phân loại** giữa các bản sao) | KHỚP — là cận dưới |
| 4 | Phi thể thao = 8.557 | 8.557 | KHỚP |
| 5 | Anomaly có smt không tag Sports = 257 | 257 | KHỚP |
| 6 | Mùa vụ (Sports + smt rỗng) = 4.720 | 4.720 | KHỚP |
| 7 | Thiếu gameStartTime = 166 | 166 | KHỚP |
| 8 | gst ngoài đoạn 1 = 305 (159 trước T0 + 146 sau T1) | 305 = 159 + 146 | KHỚP |
| 9 | Tag rỗng = 0 | 0 | KHỚP |
| 10 | Hợp lệ = 2.743 | 2.743; **id-set trùng 100%** với bucket valid tôi phân loại độc lập; lọc bằng `gameStartTime ∈ [T0=1757721600, T1=1765497600)` — **đúng luật, KHÔNG lọc bằng end_date tới 26/12** (đối chiếu từng dòng: 0 epoch lệch chuỗi gốc trong trang gz; max gst = 2025-12-11 < T1) | KHỚP — là cận dưới |
| 11 | Cộng các bước lọc = 16.748 | 8.557+257+4.720+166+159+146+2.743 = 16.748 | KHỚP |
| 12 | gst theo tháng: T9=845, T10=862, T11=786, T12→12/12=250 | 845 / 862 / 786 / 250 (tính từ epoch) | KHỚP |
| 13 | Mẫu 9 thị trường (8 hệ thống theo conditionId + 1 debug nfl-chi-was) | Tái lập được: sort valid_FULL theo conditionId, bỏ slug debug, k=2742//8=342 → đúng 8 cid của 8 file summary2; debug đo từ smoke | KHỚP |
| 14 | fills/USD/ví từng thị trường (bảng mục 4 báo cáo) | 8/8 khớp đồng thời 4 nguồn (báo cáo ↔ summary2.json ↔ final_numbers.json ↔ sample_summary.json); mỗi thị trường 1 request, không cửa sổ bị cắt | KHỚP (raw không lưu → tin mức artifact, mục 4c) |
| 15 | Debug: 445 fill, 54.603 USD, 83 ví | Tự tính từ raw: 445 fill duy nhất, **54.603,29 USD**, 83 ví, 0 timestamp ngoài [T0,T1) | KHỚP (làm tròn hiển thị) |
| 16 | Tỷ lệ đạt 6/9 (67%) → ước ~1.829 giữ / ~914 bỏ | 6/9 ✓; 2743×6/9 = 1.828,7; 2743×3/9 = 914,3 | KHỚP (ước hợp lệ, CI rộng đã khai) |
| 17 | 236 ví = union mẫu 8 thị trường (KHÔNG phải pool) | union wallets của 8 summary = 236, trùng khớp `wallets_union2.json` | KHỚP — đúng là chỉ mẫu 8 |
| 18 | smt quan sát: moneyline 1.784, totals 449, spreads 381, bts 83, **các loại tennis 37**, nrfi 6, team_totals 4, child_moneyline 9 | 1.784 ✓ 449 ✓ 381 ✓ 83 ✓ 6 ✓ 4 ✓ 9 ✓; **tennis = 27** (12+9+2+2+2), không phải 37 (tổng báo cáo 2.753 > 2.743 — bất khả) | **LỆCH nhỏ (37→27)** — lỗi cộng/mô tả, không đổi bucket nào (mọi smt ≠ rỗng đều qua lọc như nhau) |
| 19 | Ngày 1: 193 dòng sổ / 184 request thật (174×200 + 10×422) | 193 dòng trước DAY_BOUNDARY đầu (dòng 194); 184 có status = 174×200+10×422; 9 không status = 1 lỗi SSL + 8 SSL_FALLBACK_UNVERIFIED | KHỚP |
| 20 | Ngày 2: 200 dòng / **175 request thật** | 200 dòng; 175 có status (154×200 + 4×422 + 17×400) **NHƯNG** 1 dòng (tag `E_market_body`) là **ghi tay**: status=400, latency=None, err=`doc-tham-so` → không chạm server → request thật chạm server = **174** | **LỆCH −1** (khai báo, không đổi số đếm chính) |
| 21 | Tổng request thật ngày 1+2 = 359 | 184 + 174 = **358** | **LỆCH −1** |
| 22 | Giải thích 9 dòng chênh ngày 1 (1 SSL + 8 fallback) | đúng như ledger | KHỚP |
| 23 | Giải thích 25 dòng chênh ngày 2: "10 dòng DAY_BOUNDARY + nhật ký SSL + 2 dòng ghi 400 nhưng thật ra lỗi SSL cục bộ (E_market_body, F_condition_id)" | **SAI cấu trúc**: thật = **13 DAY_BOUNDARY + 12 SSL_FALLBACK_UNVERIFIED**; `E_market_body` NẰM TRONG nhóm 175 (có status, ghi tay "doc-tham-so", không phải nhóm 25, không phải "lỗi SSL"); **`F_condition_id` KHÔNG tồn tại trong sổ** (grep toàn ledger) | **LỆCH — lỗi KHAI BÁO** (mục 6.5) |
| 24 | 2 tiến trình trùng ~11 phút: 33 khoảng liên tiếp <9s, nhỏ nhất 3,0s | 33 khoảng <9s (18×8s, 9×7s, 5×6s, 1×3,0s), **đều trong ngày 2**; ngày 1 sạch (min 10,0s) | KHỚP |
| 25 | Request trùng URL có trong ledger; tổng không nhiễm trùng id | **33 cặp (tag,url) trùng** = 66 dòng = 33 request thừa (34 URL trùng nếu bỏ qua tag); dedupe theo id khiến 16.748 KHÔNG bị nhiễm (0 mâu thuẫn phân loại) | KHỚP — lỗi quy trình nhịp, không lỗi dữ liệu đếm |
| 26 | Tra-lại-theo-mã: 8/8 trả về, 0 lệch thật; lần đầu thiếu include_tag gây 8 lệch giả | `recheck_batch.json` (lần 1): tags rỗng 8/8 nhưng smt+gameStartTime khớp 8/8 với trang gốc → khớp giải thích; `recheck2_result.json` = {returned: 8, real_diffs: 0} | KHỚP ở mức artifact (raw lần 2 không lưu — không tái kiểm được 100%) |
| 27 | closed=any + end_date trả 0 dòng, không kết luận được | `closedany_p1.json` = validation error của server → đúng là không kết luận được, khai trung thực | KHỚP |
| 28 | Dò rò chốt sau 26/12 (27/12→31/01, trang 1): 0 hợp lệ lọt | `spotcheck_lateenddate.json`: 100 dòng trang 1, 0 leak | KHỚP (mức trang mẫu, đã ghi rõ) |
| 29 | "Liệt kê xong 105/105 ngày", "11 lát hoàn chỉnh ghép phủ kín 105/105 ngày cửa sổ" | **SAI** — xem mục 6.1–6.3: 24 lát CAP không có lát con; không lát 1–2 ngày nào từng được request; slices_progress cuối còn queue 6 lát; chỉ 2 lát kết thúc tự nhiên | **LỆCH — LỖI HOÀN TẤT LIỆT KÊ (bug chính)** |

---

## 3. Kết quả tính lại độc lập (code riêng trong /tmp/audit_viec3/)

**(a) Union id từ mọi trang gz → bucket:** đọc cả 304 file (listing/ + slices/*/), phân loại lại từ đầu theo luật §2.1 (tag Sports, smt, gameStartTime epoch tự parse): 28.992 dòng → **16.748 id duy nhất**; valid **2.743** / seasonal **4.720** / missing_gst **166** / anomaly **257** / phi thể thao thường **8.557** / gst trước **159** + sau **146** / tag rỗng **0**. Tổng = 16.748. **Khớp 100%, sai số 0.**

**(b) valid_FULL theo tháng gst:** 845 / 862 / 786 / 250; 0 dòng có epoch ngoài [T0,T1); 2.743 conditionId duy nhất; đối chiếu ngược từng dòng với chuỗi `gameStartTime` gốc trong trang gz: **0 lệch epoch, 0 lệch smt, 0 thiếu tag Sports**. **Khớp 100%.**

**(c) USD đoạn 1 tính từ dữ liệu thô:** thị trường debug nfl-chi-was-2025-10-13 từ `smoke/i_cid_window.json`: dedupe khóa (transaction_hash, token_id, timestamp, side, size) → 445 fill duy nhất (445 dòng thô, 0 trùng), Σ price×size = **54.603,29** (báo cáo 54.603 — khớp làm tròn), 83 ví, 100% timestamp ∈ [T0,T1). Thị trường 0x0025… (12.378,26): raw không lưu trên đĩa — đối chiếu chéo 4 nguồn artifact đều = 12.378,26, không thể tự sum lại từ raw (giới hạn ghi nhận). Mã `v3_phase_trades2.py` xác nhận **KHÔNG dùng volumeNum**, đúng Σ price×size, cửa sổ start=T0&end=T1.

**(d) Tỷ lệ 6/9 và ước 1.829/914:** 6/9 đạt ✓ (5/8 hệ thống + debug); 2.743×6/9 = 1.828,7 ≈ 1.829; 2.743×3/9 = 914,3 ≈ 914. **Khớp.** Ví union 8 thị trường = 236 ✓ (tái hợp từ 8 file, trùng `wallets_union2.json`); đúng là số ví MẪU, không phải pool.

---

## 4. Sổ và request (chi tiết hơn mục 2)

- Ngày 1 = 193 dòng (trước DAY_BOUNDARY đầu tại dòng 194): 174×200 + 10×422 + 1 SSL-error + 8 SSL_FALLBACK. 10×422 đều offset ≥2100 (bằng chứng offset-cap). **Khai báo đúng.**
- Ngày 2 = 200 dòng: 154×200 + 4×422 + 17×400 + 13 DAY_BOUNDARY + 12 SSL_FALLBACK. Trong 17×400: **`E_market_body` là dòng ghi tay** (latency=None, err="doc-tham-so" — ghi sau khi thử tham số thất bại cục bộ, không tới server) → request thật chạm server ngày 2 = **174**, tổng 2 ngày = **358** (báo cáo 359). Đây là **lỗi KHAI BÁO + đếm "request thật" sai 1 đơn vị**, không phải lỗi dữ liệu sổ (ledger trung thực).
- Mô tả thành phần 25 dòng ngày 2 trong báo cáo **SAI** (xem dòng 23 bảng trên): thật là 13 biên phiên + 12 nhật ký SSL; không có "2 dòng ghi 400 nhưng thật ra SSL" nào trong nhóm 25; `F_condition_id` không tồn tại. Mức độ: sai mô tả khai báo; **không làm sai bất kỳ số đếm chính nào** (16.748 / 2.743 / 6-9 / 236 / 845-862-786-250 đều không phụ thuộc dòng này).
- 2 tiến trình trùng: 33 cặp request trùng (tag+URL) — có trong ledger, minh bạch; nhịp ngày 1 hoàn toàn sạch (≥10s), 33 lần <9s đều trong cửa sổ trùng ngày 2. Dedupe theo id triệt tiêu nhiễm trùng (0 mâu thuẫn). **Lỗi quy trình (nhịp + 33 request lãng phí), không lỗi số đếm.**

---

## 5. Trả lời 3 câu hỏi bắt buộc

**(1) Làm đúng chưa?** — *Số học: đúng. Tính hoàn tất: SAI.* Mọi con số trên đĩa tái lập chính xác tuyệt đối; luật lọc đúng theo spec (gst ∈ [T0,T1), tag Sports, smt ≠ rỗng — KHÔNG lọc bằng end_date); không đổi spec (hash nguyên vẹn từ 8727bcc tới 85f8732); không tự thu hẹp pool / đổi ngưỡng / bỏ thị trường (valid_FULL nguyên 2.743 dòng; mẫu hệ thống theo conditionId, không dính lãi); ngưỡng đo bằng Σ price×size đúng luật đã duyệt, không dùng volumeNum. NHƯNG nhiệm vụ cốt lõi là ĐẾM POOL mà phép liệt kê chưa xong (mục 6) thì báo cáo khẳng định "liệt kê xong 105/105 ngày" là khẳng định sai về tính đầy đủ → chưa làm đúng ở đúng chỗ trọng yếu nhất của việc ĐẾM.

**(2) Cố gắng hết sức chưa?** — Nỗ lực kỹ thuật đáng ghi nhận: phát hiện offset-cap 2100 và thiết kế bisection; kỷ luật sổ/checkpoint/watchdog; dừng đúng luật; khai trung thực lỗi 2 tiến trình và 33 request trùng; tái chạy recheck đúng (include_tag); không thử lách luật. NHƯNG: trước khi chốt "xong", agent không đối chiếu chính file trạng thái của mình (`slices_progress.json` cuối vẫn còn queue 6 lát; log day2c kết thúc giữa chừng không có dòng FINAL) và không nhận ra rằng 28 lát probe-only đều CAP mà không có lát con — tức bisection chưa bao giờ xuống tới lá. Kiểm tra chéo đó là điều tối thiểu để tuyên bố "phủ kín". Về nỗ lực: đạt ~90%, thiếu đúng bước xác minh hoàn tất.

**(3) Còn đường hợp lệ chưa thử không?** — CÓ, cho phần đếm: **chạy tiếp bisection từ cache trang** (trang cũ giữ nguyên, chỉ fetch lát còn thiếu: 24 nhánh + xuống lá tự nhiên; ước vài trăm request ≈ 1–3 ngày @200/ngày) rồi đếm lại union/bucket/valid_FULL từ đĩa. Rủi ro phải thử trước (1 request): nếu MỘT NGÀY đơn lẻ có >2.100 dòng thì phải chia nhỏ hơn nữa bằng timestamp trong end_date_min/max (chưa kiểm chứng — smoke mới kiểm chứng end_date theo ngày). Với kết luận 14 ngày: **không cần đường mới** — cận dưới đã đủ (mục 7). Pilot 100 thị trường chỉ chặt ước 67% và đuôi >500 fill, không bắt buộc cho kết luận vượt. Thu hẹp pool theo luật không-dựa-trên-lãi (nâng ngưỡng khối lượng, giới hạn môn/ngày) là quyết định của chủ nhân — đổi tham số trong khuôn khổ luật hiện hành, không nhất thiết spec mới hoàn toàn, nhưng phải do chủ nhân duyệt bằng văn bản (báo cáo Việc 3 cũng dừng đúng chỗ đó).

---

## 6. BUG FOUND — lỗi ở đâu, cần đếm lại phần nào

**6.1. Bisection chưa hoàn tất (lỗi chính — tính đầy đủ):**
- Trên đĩa có **41 lát**: 12 lát đa trang (9 lát CAP 22 trang offset 0→2100 + 10-01_10-03, 10-07_10-09, 10-10_10-22, 10-14_10-16) và **28 lát CHỈ CÓ 1 trang probe offset-2000 (100 dòng)** → mọi lát đó trả về CAP và theo code phải **tách tiếp thành lát con**, nhưng **KHÔNG có bất kỳ lát 1–2 ngày nào trên đĩa** — ledger cũng chứng minh **0 request cho lát ≤2 ngày** (grep toàn bộ tag `l2_*`/`l2probe_*`). 24 nhánh CAP như vậy không có con = **chưa giải quyết**.
- `slices_progress.json` (file tiến độ do chính script ghi) trạng thái cuối: **queue còn 6 lát** `[10-10→10-22, 10-23→11-04, 11-05→11-17, 11-18→11-30, 12-01→12-13, 12-14→12-26]` — đúng như nhận định của coordinator: file này phản ánh run cuối đã dừng, không phải "hoàn tất".
- Log `listing2_day2c.log` kết thúc ở "LÁT 2025-09-27→2025-10-09: CAP … req pha=21" — không có dòng FINAL.

**6.2. Bằng chứng thiếu hụt định lượng (offline, không cần API):** ngữ nghĩa probe đã được kiểm chứng chéo: cửa sổ nhỏ (10-01→10-03: 1.628 dòng; 10-07→10-09: 1.364 dòng) probe offset-2000 trả **0 dòng**; vậy 28 lát probe trả **100 dòng** chứng minh mỗi cửa sổ đó có **≥2.100 dòng thật** (tham số end_date lọc đúng — 100% dòng probe có endDate trong cửa sổ). So với id duy nhất trên đĩa theo cửa sổ: `[12-21→12-26]` đĩa chỉ **128** (thiếu ≥1.972 dòng chưa từng thấy), `[09-17→09-19]` 499 (thiếu ≥1.601), `[10-23→10-29]` 299 (thiếu ≥1.801), `[11-25→11-30]` 331, `[12-14→12-20]` 459, `[12-08→12-13]` 496… Chỉ 2 lát kết thúc THẬT tự nhiên (trang ngắn <100 ở offset <2100): 10-01→10-03 và 10-07→10-09; lát 10-14→10-16 dừng ở 400 dòng không trang ngắn (bị ngắt). Ví dụ cụ thể về hệ quả id: probe `[09-13→09-16]` chứa 100 id liên tiếp 596.411–596.510 (endDate 2025-09-13) mà **0 id nào** nằm trong 2.100 dòng đã phân trang của cửa sổ cha `[09-13→09-26]` (id ≤ 594.685) → khoảng id giữa hai tập gần như trống trên đĩa (chỉ 124 id bất kỳ endDate) — đúng hình dạng "giữa còn chưa lấy".

**6.3. Khẳng định sai trong báo cáo + artifact:** mục 2 điều 3 ("11 lát hoàn chỉnh ghép phủ kín 105/105 ngày") và thông điệp commit ("liệt kê xong 105/105 ngày") là **SAI**; `coverage_disk.json` (`coverage_days: 105, merged [[2025-09-13, 2025-12-26]]`, viết tay, không script sinh) đánh đồng "các lát phủ kín khoảng ngày" với "đã lấy đủ dòng trong từng lát". Số đúng phải đọc: **16.748 = số id đã thấy (cận dưới pool)**; **2.743 = cận dưới hợp lệ**.

**6.4. (Xác nhận các điểm coordinator giao, tự kiểm chứng):** (i) script phân tích CŨ `v3_phase_analyze.py` đếm `sub` KHÔNG khử trùng id qua các trang chồng lái — tôi chạy lại logic đó ra đúng **22.287** (sai), số đúng là 16.748 như final_numbers/coverage_disk; file output analysis_*.json không tồn tại/từng commit — không ảnh hưởng số cuối; (ii) slices_progress chỉ phản ánh run cuối — xác nhận ở 6.1; (iii) recheck lần 1 thiếu include_tag → 8 "chênh lệch" giả (tags rỗng 8/8 trong recheck_batch.json, smt/gst vẫn khớp 8/8) — giải thích trong báo cáo ĐÚNG; recheck2 = 8/8, 0 lệch (mức artifact); (iv) closedany_p1 = validation error → không kết luận được — báo cáo khai trung thực ĐÚNG; (v) mô tả 25 dòng ngày 2 — xác nhận SAI (mục 4 trên), mức độ lỗi KHAI BÁO, không làm sai số đếm chính.

**6.5. Các lệch khai báo nhỏ khác:** smt "các loại tennis 37" → thật 27; "175 request thật ngày 2 / tổng 359" → thật 174 / 358 (E_market_body ghi tay không chạm server); "F_condition_id" không tồn tại trong sổ. Không số đếm chính nào phụ thuộc các dòng này.

**CẦN ĐẾM LẠI:** toàn bộ phần liệt kê còn thiếu — chạy tiếp bisection cho 24 nhánh + queue còn lại tới lá kết thúc tự nhiên (trang ngắn <100 hoặc rỗng ở offset <2100), kiểm tra trước bằng 1 request xem 1 ngày có vượt 2.100 dòng không (nếu có phải chia timestamp); sau đó đếm lại union/bucket/valid_FULL từ đĩa và sửa báo cáo: 16.748/2.743 chỉ được ghi là CẬN DƯỚI cho tới khi liệt kê xong. Cache trang giữ nguyên nên việc đếm lại không tốn lại request cũ.

---

## 7. Kết luận "VƯỢT 14 NGÀY" — độ vững (dù đếm treo)

- Thành phần VỮNG CHẮC (bất biến, bất kể giả định): mỗi thị trường hợp lệ cần ≥1 request trades (endpoint không cursor/offset — chứng minh 400 trong sổ) → **≥2.743 request ≥ 13,7 ngày @200/ngày**, gần cạn toàn bộ hạn 2.800 của 14 ngày, chưa tính resolutions+phí (~≥1.829 nếu giữ theo ước) và query ví (236 ví chỉ từ 8 thị trường mẫu). Vì 2.743 là CẬN DƯỚI (pool thật lớn hơn do thiếu hụt liệt kê), pool thật càng lớn thì request càng nhiều → **kết luận VƯỢT chỉ mạnh lên, không yếu đi**. Verdict "vượt tối thiểu" đủ để kết luận VƯỢT.
- Thành phần CHỈ LÀ ƯỚC (đã khai đúng mức): tỷ lệ đạt 67% từ n=9 (CI rộng — đã ghi "khoảng tin cậy rộng"); đuôi >500 fill chưa đo; tổng số ví pool chưa biết; khung 5.000–12.000 request ≈ 25–60 ngày là ngoại suy.
- Kiểm tra tuân thủ: spec hash không đổi; valid_FULL nguyên 2.743 dòng; không tự thu hẹp pool/đổi ngưỡng 10.000 USD/bỏ thị trường; mẫu chọn theo conditionId không dính lãi/khối lượng. Agent dừng đúng chỗ theo lệnh, không chạy Việc 4.

**Số có hiệu lực dùng cho quyết hồ sơ tại thời điểm này:** hợp lệ ≥ 2.743 (cận dưới, đã kiểm chứng từng dòng); vượt 14 ngày cho hồ sơ chính là kết luận vững; số đếm pool (16.748/8.557/4.720/…) chỉ hợp lệ như CẬN DƯỚI đến khi đếm lại xong. **Việc 4 vẫn cần lệnh GO riêng của chủ nhân; kiểm toán này KHÔNG phải lệnh GO cho pilot hay Việc 4.**

---

Tôi xác nhận đã đọc file gốc, không dựa vào bản tóm tắt chat. Tôi không sửa file nào của Việc 3, không chạy lại Việc 3 để thay kết quả, không áp dụng cơ chế nào vào hệ thống thật.
