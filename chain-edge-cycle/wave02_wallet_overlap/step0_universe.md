# WAVE 2 — BƯỚC 0: VŨ TRỤ VÍ (overlap ví độc lập mua cùng token trong 24h)

> **TRẠNG THÁI: DRAFT — sẽ được đóng băng ở chặng 5 của loop 10h (2026-11-02/03),
> TRƯỜC khi mở bất kỳ bảng tổng hợp lợi nhuận/volumes nào của ví.**
> Kể từ thời điểm đóng băng, mọi thay đổi phải thành file spec v2 mới.

## 1. Đơn vị phân tích

Ví (địa chỉ) giao dịch token thuộc vũ trụ token W2. Đếm theo NHÓM ví sau ghép cụm, không đếm ví rời.

## 2. Vũ trụ token W2 (cho loop 10h này)

- Các pool thuộc vũ trụ W1 đã đóng băng (step0_universe.md W1): 123 pool pancakev3 trên Base,
  epoch 21 ngày đã định, quote ∈ {USDC, USDbC, WETH}, dedupe theo base token.
- **Ghi nhận hạn chế lớn**: đây là vũ trụ token HẸP (thiên lệch 3-factory đã ghi ở W1 step0).
  W2 thật sự cần gần như toàn bộ token hoạt động của chuỗi — nguồn đó chưa có trong loop này.
  Mọi mô tả W2 trong loop 10h chỉ là MÔ TẢ TIÊN PHONG trên tập hẹp, không đại diện vũ trụ W2 đầy đủ.

## 3. Dữ liệu ví (đã có / sẽ có trong loop)

- Transfer logs của base token từng pool (24h đầu từ creation) → hướng so với pool:
  ví→pool = BÁN, pool→ví = MUA. Thời điểm = block (nội suy 2s/block).
- KHÔNG có trong loop: lịch sử nạp đầu tiên của ví (cần quét từ block 0 — đắt),
  code của địa chỉ (eth_getCode từng ví — tốn call), nhãn sàn/launchpad.
  → các tiêu chí cần dữ liệu đó được ghi "thiếu dữ liệu, không áp được", không thay bằng đoán.

## 4. Tiêu chí loại ví rác (đề xuất đóng băng)

- Loại: địa chỉ của chính pool, địa chỉ zero (mint/burn), địa chỉ xuất hiện với tần suất
  giao dịch > 200 lệnh/24h trên một token (nghi bot làm thị trường/lặp) — CỜ, không loại
  (vì chưa phân biệt được bot MM với bot sniping; ghi cờ để mô tả).
- Cờ đơn-token: ví chỉ giao dịch đúng 1 token trong dữ liệu → cờ, không loại.
- Ghép cụm nghi ngờ (không chứng minh): hai ví MUA cùng token trong cùng khung 5 phút,
  và lặp lại mẫu này ở ≥ 3 token → ghép vào một NHÓM nghi.

## 5. Ngưỡng tối thiểu (đề xuất đóng băng)

- Ví thuộc vũ trụ mô tả: ≥ 2 lệnh mua trên các token vũ trụ trong 24h đầu của token.
- Nếu tổng ví sau lọc < 20 nhóm → ghi thiếu mẫu (đúng luật W1), không hạ ngưỡng.

## 6. Kỳ nguyên W2

Tái dùng 3 epoch 7 ngày của W1 (cùng biên block đã đóng băng) — không định nghĩa lại,
không chồng lấn. Mọi tính toán W2 sau này (ngoài loop) tách theo epoch này.

## 7. Điều kiện để W2 đi tiếp sau loop

Cần nguồn token-vũ-trụ rộng (GT sau khi đo lại, hoặc thu thập RPC dài hạn) + dữ liệu ví
đa chuỗi-kỳ. Trong loop 10h: CHỈ đóng băng tiêu chí + mô tả sơ bộ. Không spec, không backtest.

---

## ĐÓNG BĂNG: 2026-11-02T15:47Z (chặng 5, loop 10h)

- Tiêu chí mục 2-6 ở trên đóng băng NGAY TRƯỚC khi mở file wallet_summary.csv / wallets.csv.
- Minh bạch: script pha ví in ra màn hình con số tổng "414 ví duy nhất" trước thời điểm đóng băng
  (tôi không thể "ngơ" nó). Con số đó KHÔNG dùng để chỉnh tiêu chí nào — tiêu chí giữ nguyên
  từng chữ như bản DRAFT viết lúc 15:1xZ, TRƯỚC khi pha ví chạy. Ghi rõ để kiểm toán đánh giá.
- Từ thời điểm này: đổi tiêu chí = phải lập file v2, kỷ nguyên mới.
