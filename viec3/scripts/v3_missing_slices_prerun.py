# v3_missing_slices_prerun.py — BƯỚC 0 (lệnh chủ nhân tối 03/11): in danh sách lát thiếu
# TRƯỚC khi wrapper 00:05 ngày 04/11 tốn request API. HOÀN TOÀN OFFLINE (0 request):
# dựng lại cây bisection từ cửa sổ gốc [2025-09-13, 2025-12-26] bằng CACHE TRANG TRÊN ĐĨA,
# dùng đúng hàm con của v3_phase_list3.py. Luật hoàn tất (đã sửa): NATURAL = trang ngắn <100
# hoặc rỗng ở offset <2100; rỗng ở >=2100 = CAP; probe-only (page_2000=100, không page_0) = CAP.
import sys, os, json, gzip, glob, datetime
from collections import deque

LD = "viec3/data/listing"
ROOTS = [os.path.join(LD, "slices3"), os.path.join(LD, "slices")]

def slice_offsets(a, b):
    offs = {}
    for root in ROOTS:
        d = os.path.join(root, "%s_%s" % (a, b))
        for p in glob.glob(os.path.join(d, "page_*.json.gz")):
            off = int(os.path.basename(p)[5:12])
            if off not in offs:
                with gzip.open(p, "rt", encoding="utf-8") as f:
                    offs[off] = len(json.load(f))
    return offs

def status(a, b):
    offs = slice_offsets(a, b)
    if not offs:
        return "NO_DATA", offs, "chưa từng fetch"
    if 0 not in offs:
        if offs.get(2000) == 100:
            return "CAP", offs, "dò offset 2000 trả đủ 100 dòng (cache) → ≥2.100 dòng thật"
        return "PARTIAL", offs, "chỉ có trang rời (không page_0) — cần đi từ đầu"
    o, last_full = 0, None
    while True:
        if o not in offs:
            return "PARTIAL", offs, "chuỗi dừng ở offset %d, chưa có trang chốt" % o
        n = offs[o]
        if n == 0:
            if o >= 2100:
                return "CAP", offs, "trang rỗng ngay offset %d ≥2100 → CỤT (đúng dấu offset-cap)" % o
            return "NATURAL", offs, "trang rỗng ở offset %d <2100 → hết thật" % o
        if n < 100:
            if o >= 2100:
                return "CAP", offs, "trang ngắn ở offset ≥2100 (bất khả) → CỤT"
            return "NATURAL", offs, "trang ngắn %d dòng ở offset %d <2100 → hết thật" % (n, o)
        o += 100
        if o > 2100:
            return "CAP", offs, "chuỗi đầy tới offset 2000 → CỤT ở 2100"

def d2o(s):
    return datetime.date.fromisoformat(s[:10]).toordinal()

def children(a, b):
    if len(a) == 10 and len(b) == 10:
        o0, o1 = d2o(a), d2o(b)
        if o1 - o0 >= 1:
            mid = datetime.date.fromordinal(o0 + (o1 - o0) // 2).isoformat()
            return [(a, mid), (datetime.date.fromordinal(d2o(mid) + 1).isoformat(), b)]
        return [(a + "T00", a + "T12"), (a + "T12", b + "T23")]
    f = "%Y-%m-%dT%H"
    ta = datetime.datetime.strptime(a, f)
    tb = datetime.datetime.strptime(b, f)
    if (tb - ta) <= datetime.timedelta(hours=1):
        return None
    tm = ta + (tb - ta) // 2
    return [(a, tm.strftime(f)), (tm.strftime(f), b)]

# ---- dựng cây từ gốc, chỉ từ cache ----
queue = deque([("2025-09-13", "2025-12-26", None)])
nodes, pending_leaves = [], []
while queue:
    a, b, parent = queue.popleft()
    st, offs, ev = status(a, b)
    node = {"slice": [a, b], "parent": parent, "status": st, "evidence": ev,
            "pages_cached": len(offs)}
    nodes.append(node)
    if st == "NATURAL":
        continue
    ch = children(a, b)
    if ch is None:
        node["status"] = "UNRESOLVED_1HOUR"
        pending_leaves.append(node)
        continue
    if st in ("CAP", "PARTIAL"):
        node["pending_reason"] = ("CỤT, phải chia tiếp" if st == "CAP" else "chưa đi hết chuỗi trang")
        # chỉ theo dir con CÓ THẬT trên đĩa (không phóng đại chia giả định cửa sổ chưa fetch);
        # không có dir con -> chính node này là leaf việc-cần-làm của bản đồ hiện trạng
        kids_on_disk = [c for c in ch if slice_offsets(*c)]
        if kids_on_disk:
            node["children_on_disk"] = [[c[0], c[1]] for c in kids_on_disk]
            for ca, cb in ch:
                queue.append((ca, cb, [a, b]))
        else:
            pending_leaves.append(node)
    else:  # NO_DATA — cửa sổ chưa từng fetch: leaf việc-cần-làm (chạy thật sẽ ĐI chuỗi trước, không chia giả định)
        pending_leaves.append(node)

# ---- đối chiếu với danh sách kiểm toán ----
AUDIT_QUEUE6 = [["2025-10-10", "2025-10-22"], ["2025-10-23", "2025-11-04"], ["2025-11-05", "2025-11-17"],
                ["2025-11-18", "2025-11-30"], ["2025-12-01", "2025-12-13"], ["2025-12-14", "2025-12-26"]]
AUDIT_DITHERED = ["2025-10-14", "2025-10-16"]
node_by_slice = {tuple(n["slice"]): n for n in nodes}
recon = []
for q in AUDIT_QUEUE6:
    n = node_by_slice.get(tuple(q))
    recon.append({"kiem_toan": "queue-6", "slice": q,
                  "trang_thai_toi": n["status"] if n else "KHÔNG CÓ TRONG CÂY",
                  "bang_chung": n["evidence"] if n else "-",
                  "la_leaf_viec_can_lam": n in pending_leaves if n else False,
                  "children_on_disk": n.get("children_on_disk") if n else None})
n = node_by_slice.get(tuple(AUDIT_DITHERED))
recon.append({"kiem_toan": "lát dở", "slice": AUDIT_DITHERED,
              "trang_thai_toi": n["status"] if n else "KHÔNG CÓ TRONG CÂY",
              "bang_chung": n["evidence"] if n else "-",
              "la_leaf_viec_can_lam": n in pending_leaves if n else False})
# 24 nhánh CAP không con + 28 dò-only + 2 tự nhiên: đối chiếu theo tổng cấu thành
probe_only = [n for n in nodes if 0 not in slice_offsets(*n["slice"]) and slice_offsets(*n["slice"]).get(2000) == 100]
natural_nodes = [n for n in nodes if n["status"] == "NATURAL"]
caps_no_kids_on_disk = [n for n in nodes if n["status"] == "CAP" and not n.get("children_on_disk")]

out = {
 "ngay_tao": "2026-11-03 (tối, trước wrapper 00:05 04/11)", "api_requests_dung": 0,
 "luat_hoan_tat": "NATURAL = trang ngắn <100 hoặc rỗng ở offset <2100; rỗng ở >=2100 hoặc chuỗi đầy tới 2000 = CAP; probe-only = CAP",
 "cay": {"tong_node": len(nodes), "tong_leaf_viec_can_lam": len(pending_leaves)},
 "leaves_viec_can_lam": [{"slice": n["slice"], "parent": n["parent"], "status": n["status"],
                          "evidence": n["evidence"], "pages_cached": n["pages_cached"]}
                         for n in pending_leaves],
 "thong_ke_dia": {"probe_only_tong": len(probe_only),
                  "probe_only_khong_dir_con": len([n for n in probe_only if not n.get("children_on_disk")]),
                  "probe_only_co_dir_con": len([n for n in probe_only if n.get("children_on_disk")]),
                  "natural": len(natural_nodes),
                  "cap_khong_dir_con": len(caps_no_kids_on_disk)},
 "doi_chieu_kiem_toan": recon,
 "giai_thich_queue9_vs_queue6": (
   "Queue-6 (kiểm toán, từ slices_progress.json run cuối ngày 2) và queue-9 (dry-run a74a382, slices3_progress.json) "
   "là HAI ẢNH CHỤP BFS ở hai thời điểm khác nhau của cùng cây việc. Queue-9 gồm: 5/6 lát queue của kiểm toán "
   "(10-23→11-04, 11-05→11-17, 11-18→11-30, 12-01→12-13, 12-14→12-26 — bị pop rồi phán quyết CAP từ cache probe rồi "
   "re-enqueue con) + 4 lát con MỚI sinh do dry-run chia tiếp 2 nhánh [09-13→09-26] và [09-27→10-09] mà run cũ "
   "chưa từng tới (09-13→09-19, 09-20→09-26, 09-27→10-03, 10-04→10-09). Lát thứ 6 của kiểm toán "
   "(10-10→10-22) là lát ĐANG XỬ LÝ lúc dry-run dừng nên không xuất hiện trong file queue — vô hại vì cây "
   "dựng lại từ đĩa luôn nhận ra nó là PARTIAL (18 trang, chưa có trang chốt). Không nhánh nào bị mất."),
 "bo_dem_tran": ("Bộ đếm trần (viec3_lib._count_today, đã sửa tối 03/11): đếm dòng sổ CÓ status VÀ CÓ latency_ms "
                 "(= request thật chạm server). Ngày 03/11: 358 (loại đúng 1 dòng ghi tay E_market_body có status 400 "
                 "nhưng latency=None, không tới server). Trước sửa chỉ đếm status → 359; đã sửa tại _count_today, "
                 "thêm điều kiện latency_ms is None → bỏ qua."),
}
json.dump(out, open(os.path.join("viec3/data", "missing_slices_pre_run_2026-11-04.json"), "w"),
          ensure_ascii=False, indent=1)
print("Node cây:", len(nodes), "| leaf việc-cần-làm:", len(pending_leaves))
print("Thống kê đĩa:", out["thong_ke_dia"])
for n in pending_leaves:
    print("  LEAF:", n["slice"], "| cha:", n["parent"], "|", n["status"], "|", n["evidence"])
print("\nĐối chiếu queue-6 + lát dở:")
for r in recon:
    print("  ", r["kiem_toan"], r["slice"], "→", r["trang_thai_toi"], "| leaf:", r["la_leaf_viec_can_lam"],
          "| con trên đĩa:", r.get("children_on_disk"))
