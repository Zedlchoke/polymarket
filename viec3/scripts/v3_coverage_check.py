# v3_coverage_check.py — KIỂM TRA ĐỘ PHỦ ĐÚNG LUẬT (đã sửa lỗi BUG FOUND của kiểm toán d8f2bb9).
#
# LỖI CŨ (đã xóa): script kiểm tra độ phủ nội tuyến dùng trong Việc 3 ngày 2 (chạy heredoc,
#   không lưu thành script) có mệnh đề:  `if o > 2100: ok = False`  trong khi chuỗi trang
#   kết thúc bằng TRANG RỎNG ngay tại offset == 2100 được coi là "hoàn chỉnh" — SAI, vì
#   trang rỗng ở offset >= 2100 chính là DẤU HIỆU CỤT của Gamma (offset-cap).
# NGƯỠNG MỚI (file này): lát HOÀN CHỈNH (NATURAL) chỉ khi:
#   - có page_0, và
#   - chuỗi trang kết thúc bằng: trang ngắn 0 < n < 100 ở offset < 2100, HOẶC trang rỗng ở offset < 2100.
#   Trang rỗng ở offset >= 2100 => CỤT (không hoàn chỉnh). Lát probe-only (page_2000=100, không page_0) => CỤT.
import sys, os, json, gzip, glob
from collections import deque

SL_ROOTS = [os.path.join("viec3", "data", "listing", "slices3"),
            os.path.join("viec3", "data", "listing", "slices")]

def slice_offsets(a, b):
    offs = {}
    for root in SL_ROOTS:
        d = os.path.join(root, "%s_%s" % (a, b))
        for p in glob.glob(os.path.join(d, "page_*.json.gz")):
            off = int(os.path.basename(p)[5:12])
            if off not in offs:
                with gzip.open(p, "rt", encoding="utf-8") as f:
                    offs[off] = len(json.load(f))
    return offs

def status(a, b):
    offs = slice_offsets(a, b)
    if 0 not in offs:
        return ("CAP" if offs.get(2000) == 100 else "PARTIAL"), offs
    o = 0
    while True:
        if o not in offs:
            return "PARTIAL", offs
        n = offs[o]
        if n == 0:
            return ("NATURAL" if o < 2100 else "CAP"), offs
        if n < 100:
            return ("NATURAL" if o < 2100 else "CAP"), offs
        o += 100
        if o > 2100:
            return "CAP", offs

def d2ord(s):
    import datetime
    return datetime.date.fromisoformat(s[:10]).toordinal()

def i2d(o):
    import datetime
    return datetime.date.fromordinal(o).isoformat()

def children(a, b):
    import datetime
    if len(a) == 10 and len(b) == 10:
        o0, o1 = d2ord(a), d2ord(b)
        if o1 - o0 >= 1:
            mid = datetime.date.fromordinal(o0 + (o1 - o0) // 2).isoformat()
            return [(a, mid), (datetime.date.fromordinal(d2ord(mid) + 1).isoformat(), b)]
        return [(a + "T00", a + "T12"), (a + "T12", b + "T23")]
    f = "%Y-%m-%dT%H"
    ta = datetime.datetime.strptime(a, f)
    tb = datetime.datetime.strptime(b, f)
    if (tb - ta) <= datetime.timedelta(hours=1):
        return None
    tm = ta + (tb - ta) // 2
    return [(a, tm.strftime(f)), (tm.strftime(f), b)]

def main():
    WIN = ("2025-09-13", "2025-12-26")
    queue = deque([(WIN[0], WIN[1])])
    tree, natural, capped, unresolved = [], [], [], []
    while queue:
        a, b = queue.popleft()
        st, offs = status(a, b)
        tree.append({"slice": [a, b], "status": st})
        if st == "NATURAL":
            natural.append((a, b))
        elif st == "CAP":
            ch = children(a, b)
            if ch is None:
                unresolved.append((a, b))
            else:
                capped.append((a, b))
                queue.extend(ch)
        else:  # PARTIAL — chưa đi hết chuỗi (tiến trình chưa chạy tới)
            capped.append((a, b))
            ch = children(a, b)
            if ch:
                queue.extend(ch)
    # phủ theo NGÀY: chỉ các lát NATURAL theo ngày (lát giờ quy về ngày của nó)
    day_status = {}
    for a, b in natural:
        for o in range(d2ord(a), d2ord(b) + 1):
            day_status.setdefault(i2d(o), 0)
            day_status[i2d(o)] += 1
    win_days = [i2d(o) for o in range(d2ord(WIN[0]), d2ord(WIN[1]) + 1)]
    missing = [d for d in win_days if day_status.get(d, 0) == 0]
    complete = (not missing) and (not unresolved) and all(t["status"] == "NATURAL" for t in tree)
    out = {"complete": complete, "total_slices": len(tree), "natural": len(natural),
           "cap_split": len(capped), "unresolved_1hour": [list(x) for x in unresolved],
           "days_covered_natural": len(day_status), "days_window": len(win_days),
           "days_missing_natural": missing,
           "pending_windows": [list(x) for x in capped],
           "threshold_note": "NATURAL = trang ngắn <100 hoặc rỗng ở offset <2100; rỗng ở >=2100 = CỤT (lỗi cũ đã sửa)"}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    json.dump(out, open(os.path.join("viec3", "data", "listing", "coverage_fixed.json"), "w"),
              ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
