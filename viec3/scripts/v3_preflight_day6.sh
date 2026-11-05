#!/bin/zsh
# v3_preflight_day6.sh — preflight NGÀY 06/11 (lệnh chủ nhân): ghi vào ĐẦU log chạy
# kết quả kiểm tra bắt buộc về dò-trước + hash + trạng thái khóa/sổ. 0 request API.
cd /Users/hoangminhlong/Downloads/Polymarket
LOG=viec3/data/list3_run_day6.log
{
echo "=== PREFLIGHT NGÀY 06/11 — $(date '+%Y-%m-%d %H:%M:%S %z') ==="
H=$(shasum -a 256 docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md | cut -d' ' -f1)
if [ "$H" = "ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8" ]; then
  echo "HASH SPEC: KHỚP ae504a97…bee55d8"
else
  echo "HASH SPEC: KHÁC ($H) — DỪNG, KHÔNG CHẠY"; exit 2
fi
echo "KIỂM TRA DÒ-TRƯỚC (theo lệnh chủ nhân, 2 điểm bắt buộc):"
python3 - <<'PY'
src = open("viec3/scripts/v3_phase_list3.py", encoding="utf-8").read()
seg = src[src.index("DÒ-TRƯỚC"):src.index('if st == "PARTIAL":\n                # đi tiếp chuỗi')]
c1 = ('rows_probe, _ = fetch_page(a, b, 2000)' in seg and 'if len(rows_probe) == 100:' in seg and 'st = "CAP"' in seg)
c2 = ('NATURAL' not in seg)
print("  Điểm 1 — dò = 1 request @offset 2000; đủ 100 dòng => phán CAP rồi chia tiếp, KHÔNG lấy 21 trang: " + ("ĐẠT" if c1 else "LỖI"))
print("  Điểm 2 — dò-trước KHÔNG được dùng để kết luận lát đã xong (không nhánh NATURAL trong đoạn dò; luật hoàn tất nguyên bản: tự nhiên = trang ngắn <100 hoặc rỗng ở offset <2100; rỗng ở >=2100 = CỤT): " + ("ĐẠT" if c2 else "LỖI"))
exit(0 if (c1 and c2) else 1)
PY
RC=$?
if [ $RC -ne 0 ]; then echo "KIỂM TRA DÒ-TRƯỚC: LỖI — DỪNG, KHÔNG CHẠY"; exit 3; fi
if [ -f viec3/data/viec3.lock ]; then
  PID=$(python3 -c "import json; print(json.load(open('viec3/data/viec3.lock')).get('pid'))")
  if ps -p $PID > /dev/null 2>&1; then
    echo "KHÓA: còn tiến trình sống pid=$PID — DỪNG, KHÔNG CHẠY"; exit 4
  else
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) khóa sót pid=$PID đã chết (ps trống) -> xóa có ghi dead.log" >> viec3/data/viec3.lock.dead.log
    rm viec3/data/viec3.lock
    echo "KHÓA: sót từ tiến trình chết pid=$PID — đã xác minh + xóa (ghi dead.log)"
  fi
else
  echo "KHÓA: sạch"
fi
N6=$(python3 -c "
import json, datetime
ls=[json.loads(l) for l in open('viec3/data/ledger.jsonl',encoding='utf-8')]
def sg(ts):
    d=datetime.datetime.strptime(ts,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime('%Y-%m-%d')
print(sum(1 for l in ls if l.get('status') is not None and l.get('latency_ms') is not None and sg(l['ts'])=='2026-11-06'))")
echo "SỔ NGÀY 06/11 trước khi chạy: $N6 request thật"
echo "=== HẾT PREFLIGHT — BẮT ĐẦU CHẠY THEO GO ==="
} > $LOG 2>&1
[ $? -eq 0 ] || exit 9
python3 viec3/scripts/v3_phase_list3.py viec3/data 200 >> $LOG 2>&1
if grep -q "CHẬM BẤT THƯỜNG" $LOG 2>/dev/null; then
  sleep 1020
  VIEC3_SLEEP=15 python3 viec3/scripts/v3_phase_list3.py viec3/data 200 >> $LOG 2>&1
fi
python3 viec3/scripts/v3_coverage_check.py > viec3/data/coverage_after_day6.log 2>&1
python3 viec3/scripts/v3_recount.py > viec3/data/recount_after_day6.log 2>&1
echo "WRAPPER DAY6 DONE $(date '+%Y-%m-%d %H:%M:%S %z')"
