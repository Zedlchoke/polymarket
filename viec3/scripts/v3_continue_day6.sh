#!/bin/zsh
# v3_continue_day6.sh — CHẠY TIẾP 89 REQUEST CÒN LẠI NGÀY 06/11 (lệnh chủ nhân 09:27):
# nhịp 20 giây, KHÔNG retry sau watchdog (watchdog lại → DỪNG NGAY, hết hôm nay).
cd /Users/hoangminhlong/Downloads/Polymarket
LOG=viec3/data/list3_run_day6b.log
{
echo "=== PREFLIGHT CHẠY TIẾP 89 REQUEST NGÀY 06/11 — $(date '+%Y-%m-%d %H:%M:%S %z') ==="
H=$(shasum -a 256 docs/polymarket-copytrade-20-SPEC-V2-FROZEN.md | cut -d' ' -f1)
if [ "$H" = "ae504a97feb50204c7028644f78bfd0d1728b8d3f0c9b7a52d0dfb64cbee55d8" ]; then
  echo "HASH SPEC: KHỚP ae504a97…bee55d8"
else
  echo "HASH SPEC: KHÁC ($H) — DỪNG"; exit 2
fi
python3 - <<'PY'
src = open("viec3/scripts/v3_phase_list3.py", encoding="utf-8").read()
seg = src[src.index("DÒ-TRƯỚC"):src.index('if st == "PARTIAL":\n                # đi tiếp chuỗi')]
c1 = ('rows_probe, _ = fetch_page(a, b, 2000)' in seg and 'if len(rows_probe) == 100:' in seg and 'st = "CAP"' in seg)
c2 = ('NATURAL' not in seg)
print("  Dò-trước điểm 1 (chỉ phán CAP rồi chia tiếp, không lấy 21 trang): " + ("ĐẠT" if c1 else "LỖI"))
print("  Dò-trước điểm 2 (không dùng dò để kết luận xong; luật hoàn tất nguyên bản): " + ("ĐẠT" if c2 else "LỖI"))
exit(0 if (c1 and c2) else 1)
PY
[ $? -ne 0 ] && { echo "KIỂM TRA DÒ-TRƯỚC: LỖI — DỪNG"; exit 3; }
if [ -f viec3/data/viec3.lock ]; then
  PID=$(python3 -c "import json; print(json.load(open('viec3/data/viec3.lock')).get('pid'))")
  if ps -p $PID > /dev/null 2>&1; then echo "KHÓA: còn tiến trình sống pid=$PID — DỪNG"; exit 4; fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) khóa sót pid=$PID đã chết (ps trống) -> xóa có ghi dead.log" >> viec3/data/viec3.lock.dead.log
  rm viec3/data/viec3.lock
  echo "KHÓA: sót pid chết $PID — đã xác minh + xóa (dead.log)"
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
echo "SỔ NGÀY 06/11 trước khi chạy tiếp: $N6 request thật (kỳ vọng đúng 111)"
if [ "$N6" != "111" ]; then echo "SỔ KHÁC 111 — DỪNG, KHÔNG CHẠY TIẾP"; exit 5; fi
echo "NHỊP PHẦN CHẠY TIẾP: 20 giây/request — WATCHDOG LẠI SẼ DỪNG NGAY, KHÔNG RETRY HÔM NAY"
echo "=== HẾT PREFLIGHT — BẮT ĐẦU CHẠY TIẾP (tối đa 89 request) ==="
} > $LOG 2>&1
[ $? -eq 0 ] || exit 9
VIEC3_SLEEP=20 python3 viec3/scripts/v3_phase_list3.py viec3/data 89 >> $LOG 2>&1
# KHÔNG có nhánh retry — watchdog nào cũng dừng hẳn phần chạy tiếp theo lệnh chủ nhân
python3 viec3/scripts/v3_coverage_check.py > viec3/data/coverage_after_day6b.log 2>&1
python3 viec3/scripts/v3_recount.py > viec3/data/recount_after_day6b.log 2>&1
echo "CONTINUE DAY6 DONE $(date '+%Y-%m-%d %H:%M:%S %z')"
