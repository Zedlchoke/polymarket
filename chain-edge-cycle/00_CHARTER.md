# 00_CHARTER.md — Hiến pháp cycle "Tìm edge bằng reverse engineer ví blockchain"

- Ngày lập theo lệnh chủ nhân: **2026-11-02**. Trạng thái: **ACTIVE**.
- Cycle chạy song song với dự án Polymarket copytrade, tách hoàn toàn: **không đụng code PaperDesk,
  không đổi spec Polymarket đã đóng băng, không chạy việc B/C của Polymarket**. Mọi file của cycle nằm
  trong thư mục `chain-edge-cycle/` này.
- Mục tiêu cuối: tìm được **MỘT cơ chế có bằng chứng thật** (spec đóng băng + backtest qua cổng giết +
  kiểm toán độc lập CONFIRMED), hoặc ghi rõ **từng cơ chế đã chết vì sao**. Không copy mù ví lãi nhất.

---

## 1. Ranh giới cứng — giữ nguyên cho cả cycle, không ngoại lệ

1. Chỉ nghiên cứu trên giấy: **0 đồng, không lệnh thật, không tiền thật, không nối ví, không ký giao dịch**.
2. Không tạo tài khoản mới, không mua dữ liệu trả phí, không dùng VPN lách giới hạn địa lý.
3. Chỉ dùng dữ liệu công khai trên chuỗi + API công khai **không cần key**. Nguồn nào đòi key mới /
   đăng ký mới / trả phí → dừng nguồn đó, ghi **"thiếu dữ liệu"** (đường tới Box 3), không tự tạo tài khoản.
4. Không tìm, không đoán, không lưu private key / seed phrase / mật khẩu của bất kỳ ví nào.
   Không quét thư mục ví trên máy.
5. Không cố định danh người thật. Báo cáo công khai chỉ dùng **địa chỉ rút gọn**; địa chỉ đầy đủ chỉ nằm
   trong `data/` (nội bộ, phục vụ tái hiện). Không gắn tên người, không gắn tài khoản mạng xã hội.
6. Không xây bot thật, không MEV thật, không front-run thật, không sandwich thật.
7. Gặp 429/403/throttle/response chậm bất thường: **dừng bước đang chạy**, ghi log lỗi + Retry-After
   (`logs/rate_events.log`), không tăng tốc bù, không đổi endpoint để lách.
8. Không tự đổi spec sau khi thấy kết quả. Muốn đổi → viết spec mới, tên mới, kỷ nguyên mới.
9. Không chọn cơ chế "tốt nhất" sau khi xem kết quả. Mỗi cơ chế: spec riêng, đóng băng riêng, test riêng.
10. Không chạy lệnh thật, không áp cơ chế vào PaperDesk hay Polymarket khi chưa có **lệnh GO riêng của
    chủ nhân** sau khi kiểm toán wave đó trả về **CONFIRMED**.

## 2. Nguồn dữ liệu được phép (trạng thái thăm dò 2026-11-02)

| Nguồn | Key | Trạng thái | Ghi chú |
|---|---|---|---|
| GeckoTerminal `/api/v2` | không | **CHẶN MỀM máy này (xác nhận 2026-11-03T00:01Z)**: 3 call đo lại sau thời gian tạm dừng đều 200-rỗng, kể cả câu đối chứng `day?limit=10` đã từng có nến ngày 2026-11-02 13:41Z | `new_pools`: có `pool_created_at`, page 1-10 OK, page ≥ 30 → 401 (chỉ ~nửa ngày lịch sử); OHLCV: KHÔNG dùng được từ máy này cho tới khi có thay đổi — không tạo key mới, không VPN lách (theo ranh giới cứng) |
| DexScreener | không | OK | pairs có `pairCreatedAt`, `liquidity.usd`; token-profiles/latest/v1 OK |
| Solana RPC công khai (`api.mainnet-beta.solana.com`) | không | OK (solana-core 4.3.2) | lịch sử giao dịch theo địa chỉ có thể bị prune — đo ở từng wave |
| Base RPC (`mainnet.base.org`) | không | OK | |
| Arbitrum RPC (`arb1.arbitrum.io/rpc`) | không | OK | |
| BNB RPC (`bsc-dataseed.binance.org`) | không | OK | |
| Ethereum RPC (`eth.llamarpc.com`) | không | **CHẾT** (connection refused) | chuỗi Ethereum là cuối cùng; khi cần sẽ thử RPC công khai khác, không đăng ký key |
| API key có sẵn trên máy | — | **không có** (đã kiểm kê 2026-11-02: không file .env, không biến môi trường dữ liệu) | |

## 3. Thứ tự chuỗi và nguyên tắc escalation

1. **Solana và Base trước** (phí thấp, dữ liệu dễ lấy) → 2. **Arbitrum và BNB** → 3. **Ethereum cuối**,
   chỉ khi một cơ chế đã SỐNG ở chuỗi rẻ, để kiểm tra nó có sống trên chuỗi đắt không.
2. Mỗi chuỗi là một báo cáo riêng. **Không trộn PnL các chuỗi thành một con số chung.**
3. Cơ chế sống ở chuỗi rẻ nhưng chết vì gas trên Ethereum = **phát hiện có giá trị**, ghi rõ:
   sống ở đâu, chết ở đâu, vì chi phí nào (không phải chết vì hướng sai).

## 4. Quy trình mỗi wave (một cơ chế / wave, lặp tới khi có Box 1 hoặc hết cơ chế mới)

**Bước 0 — Chọn vũ trụ, viết TRƯỚC khi xem lãi.** Cách tìm ví (nguồn, khoảng thời gian, ngưỡng tối thiểu:
≥50 giao dịch, ≥20 token, khối lượng tối thiểu — hoặc tương đương với token/pool nếu cơ chế theo token);
cách loại ví rác (wash, một-token, chỉ nhận airdrop, market-maker hai chiều lãi <1% trên khối lượng);
cách gộp ví nghi cùng người (cùng nguồn nạp đầu, cùng khung giờ hoạt động, cùng token trong 60') —
gộp là **nghi ngờ**, sau gộp đếm **nhóm**. Vũ trụ < 20 nhóm → ghi **thiếu mẫu**, không hạ ngưỡng.

**Bước 1 — Mô tả, không tính điểm.** Token hay giao dịch nhất, thời gian giữ, giờ hoạt động, cỡ lệnh
trung bình, tần suất, tỷ lệ thắng thô (chưa trừ phí), lỗ lớn nhất. Nhóm chỉ lãi nhờ 1 giao dịch / 1 token
→ ghi **cờ tập trung**. Không chọn cơ chế, không tuyên bố edge ở bước này.

**Bước 2 — Spec đóng băng RỒI mới test.** Bắt buộc có trước khi chạy:
- Định nghĩa vào: điều kiện kích hoạt chính xác.
- Định nghĩa ra: giữ tới khi nào, không đổi sau khi xem kết quả.
- Chi phí đầy đủ: gas **thật tại thời điểm** (không dùng gas trung bình), phí swap, trượt giá ước tính
  từ thanh khoản. Không lấy được gas thật → ghi **"thiếu dữ liệu chi phí"**, không tính lãi ròng giả.
- Epoch: đoạn chọn ví / đoạn trong mẫu (chỉ tối ưu **đúng 1 tham số chính**) / đoạn holdout test
  **đúng 1 lần** — liền nhau, không chồng lấn, tính bằng giây UTC.
- Cổng giết 3 tầng (mục 5).
- `shasum -a 256 spec_v1.md` ghi vào spec + `state/wave_log.md` **trước** khi chạy backtest.
  Test chạy trước khi đóng băng = không tính.

**Bước 3 — Backtest, rồi kiểm toán độc lập.** Không sửa code giữa chừng để pass. Báo cáo tách theo
chuỗi / token / dải giá / cỡ lệnh; đếm tín hiệu bỏ vì thanh khoản, vì gas, vì thiếu giá. Verdict đúng một
trong ba: **SỐNG / CHẾT / CHƯA ĐỦ BẰNG CHỨNG** theo cổng giết. Sau wave: viết báo cáo, **DỪNG**, chờ
kiểm toán độc lập (subagent không tham gia viết code) trả lời 3 câu: (1) làm đúng spec chưa,
(2) đã cố gắng hết sức trong luật đã đóng băng chưa, (3) còn đường hợp lệ nào hay đã tịt hẳn.
- Kiểm toán **CONFIRMED** → verdict có hiệu lực.
- **BUG FOUND** → sửa, chạy lại sạch.
- **SPEC FLAW** → viết thiết kế v2 công bằng, **không chạy v2 trong cùng wave**.

**Bước 4 — Ghi bảng 3 hộp, sang wave mới** (khác hẳn cơ chế, không phải cắt lại cơ chế chết với ngưỡng khác).
- **Box 1 — SỐNG có bằng chứng**: spec hash + backtest qua cổng + audit CONFIRMED.
- **Box 2 — CHẾT hẳn**: đã qua cổng giết, kiểm toán xác nhận không còn đường hợp lệ trong cùng luật.
- **Box 3 — THIẾU DỮ LIỆU**: chỉ khi dữ liệu bị khóa/chặn/lịch sử không đủ — **không phải vì kết quả xấu**.

## 5. Cổng giết 3 tầng (giữ nguyên cho mọi wave)

- **Tầng 1 — sàng lọc**: đủ **≥200 tín hiệu**; lãi ròng (đã trừ đủ chi phí) **> 0**; lãi ròng vẫn **> 0**
  khi tăng mọi phí **+20%**; **top-1 token < 25%** tổng lãi; **top-5 token < 50%** tổng lãi;
  tỷ lệ tín hiệu bị bỏ (thanh khoản/gas/thiếu giá) **< 30%**.
- **Tầng 2 — khoảng tin cậy 95%** gom theo token hoặc sự kiện phải nằm **hoàn toàn trên 0**.
- **Tầng 3 — cờ tập trung**: một token, một chuỗi, một ví **không được là nguồn lãi duy nhất**.
- Qua T1 nhưng trượt T2 → **CHƯA ĐỦ BẰNG CHỨNG** (không phải sống, không phải chết).
- Trượt T1 (sau khi đã khai thác hết đường hợp lệ trong luật, kiểm toán xác nhận) → **CHẾT**.

## 6. Quản lý cycle dài

- **Checkpoint** sau mỗi bước: `state/checkpoint.md` ghi rõ dữ liệu lấy tới đâu, còn thiếu gì.
- **Ngân sách request**: `tools/budget_config.json` — trần/ngày từng API + nghỉ tối thiểu giữa 2 call;
  mọi request log vào `logs/request_log.csv`. Chuỗi bị chặn liên tục → chuyển chuỗi khác, không đấm ăn xôi.
- **Hạn wave**: tối đa **14 ngày** hồ sơ + backtest/wave. Hết hạn chưa đủ mẫu → ghi thiếu mẫu, sang wave khác.
- **Báo cáo sau mỗi wave** (đúng 5 mục): (1) cơ chế + spec hash + nơi lưu; (2) tín hiệu từng đoạn +
  lãi ròng + từng cổng + verdict; (3) bảng tách chuỗi/token/dải giá + cờ tập trung; (4) chi phí đã trừ +
  tỷ lệ tín hiệu bỏ; (5) wave kế tiếp khác hẳn là gì + dữ liệu còn thiếu. Không báo cáo dài dòng từng ví.
- Sau mỗi wave **DỪNG chờ kiểm toán**; không tự sang wave mới mà không ghi rõ wave mới là gì.

## 7. Hàng đợi wave (thứ tự chọn theo KHẢ NĂNG DỮ LIỆU, chọn trước khi thấy bất kỳ kết quả nào)

| Wave | Cơ chế | Chuỗi dự kiến | Lý do thứ tự |
|---|---|---|---|
| **W1** (đang chạy) | M1: mua sớm token mới niêm yết DEX trong X giờ đầu, bán theo luật cố định, lọc thanh khoản | Base (Solana dự kiến Box 3) | Nguồn không-key có sẵn ngay (GT new_pools + OHLCV); Base ~493 pool/ngày nằm trong ngân sách, Solana ~38.400 pool/ngày (chủ yếu pump-fun) vượt hạn mức lấy vũ trụ không thiên lệch |
| W2 | M3: nhiều ví độc lập cùng mua 1 token trong 24h (overlap on-chain) | Base (eth_getLogs), Solana nếu lịch sử RPC đủ | Tương tự ý Polymarket nhưng trên chuỗi; rủi ro Box 3 cao vì dữ liệu theo ví |
| W3 | M6: mua lại token sau khi ví lớn bán xong (cửa sổ cố định) | tùy W2 | dùng lại hạ tầng dữ liệu ví của W2 |
| W4 | M2: theo dõi ví tạo LP (rút trước khi giá rơi / thêm trước khi giá tăng) | Base/BNB | cần sự kiện Mint/Burn của LP — getLogs được |
| W5 | M4: bán theo dấu hiệu ví lớn nạp token lên CEX | tùy | cần địa chỉ nạp CEX (công khai) |
| W6 | M5: arbitrage 2 DEX cùng chuỗi, chỉ tính khi trừ gas + trượt giá còn lãi | Base/Arbitrum | từ dữ liệu giá lịch sử nhiều pool cùng token |
| W7+ | replicate cơ chế SỐNG: Base/Solana → Arbitrum/BNB → Ethereum (kiểm tra gas) | theoescalation | nguyên tắc mục 3 |

## 8. Nhật ký thay đổi ngân sách (chỉ được GIẢM giữa chừng; TĂNG phải đợi wave mới + ghi lý do)

- 2026-11-02: GT `min_interval_sec` 2.5 → **10**, `daily_cap` 2500 → **1200**, sau lỗi 429
  (Retry-After=0) khi gọi dồn. Nguyên tắc: đi chậm hơn, không bù tốc.

## 9. Quy tắc địa chỉ & dữ liệu nội bộ

- `data/` là nội bộ: được giữ địa chỉ đầy đủ để tái hiện; KHÔNG dùng để doxx.
- Mọi file báo cáo (`wave*/report*.md`, tóm tắt công khai) chỉ dùng địa chỉ rút gọn (ví dụ `0x1234…abcd`).
- Không gắn tên người/tài khoản mạng xã hội vào địa chỉ ở bất kỳ đâu.
