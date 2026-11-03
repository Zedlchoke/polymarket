# viec3_lib.py — dùng chung cho Việc 3 (đếm mô tả pool thị trường v2)
# Luật: 10 giây/request; trần ~200 request/ngày; 429/403/throttle -> DỪNG TOÀN BỘ;
#       response chậm bất thường -> DỪNG; mọi request ghi ledger; checkpoint sau mỗi đợt.
# Chỉ đọc (GET). Không sửa spec, không tính điểm, không chọn ví.
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

T0 = 1757721600           # 2025-09-13T00:00:00Z — luật spec v2 đóng băng
T1 = 1765497600           # 2025-12-12T00:00:00Z
LIST_START_MIN = T0 - 60 * 86400   # 1752537600 = 2025-07-14 — đệm 60 ngày cho thị trường mở trước trận
DAILY_CAP = 200           # trần ~200 request/ngày (luật)
SLEEP_S = 10              # 10 giây/request (luật)
LAT_HARD_STOP_MS = 5000   # chậm bất thường -> dừng (probe V2: 7.363ms đã kích hoạt watchdog)

DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"


class StopRun(Exception):
    """Dừng toàn bộ theo luật — không retry ngay, không tăng tốc bù."""


class Http:
    def __init__(self, data_dir, phase, max_req):
        self.data_dir = data_dir
        self.phase = phase
        self.max_req = max_req
        self.ledger_path = os.path.join(data_dir, "ledger.jsonl")
        self.ck_path = os.path.join(data_dir, "checkpoint.json")
        # Môi trường máy này không có chuỗi CA (probe 2026-11-02 đã gặp và dùng
        # context không xác minh cho GET chỉ-đọc — tiền lệ probe2_v2.py SSL_CTX).
        # Thử xác minh trước; nếu lỗi chuỗi CA thì dùng context không xác minh (chỉ GET đọc công khai).
        self.ssl_verified = True
        try:
            self.ssl_ctx = ssl.create_default_context()
        except Exception:
            self.ssl_verified = False
            self.ssl_ctx = ssl._create_unverified_context()
        self.count_phase = 0
        self.count_today = self._count_today()

    def _count_today(self):
        today = time.strftime("%Y-%m-%d")
        n = 0
        if os.path.exists(self.ledger_path):
            with open(self.ledger_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        if json.loads(line).get("ts", "").startswith(today):
                            n += 1
                    except Exception:
                        pass
        return n

    def _ledger(self, rec):
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def checkpoint(self, **kw):
        base = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "phase": self.phase,
                "phase_requests": self.count_phase,
                "today_requests": self.count_today + self.count_phase,
                "today_remaining": DAILY_CAP - (self.count_today + self.count_phase)}
        base.update(kw)
        tmp = self.ck_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.ck_path)

    def get(self, url, tag, save_path=None):
        """GET có kỷ luật: kiểm tra ngân sách, ngủ 10s, đo độ trễ, ghi ledger.
        Trả (doc_json_hoặc_None, status). Ném StopRun khi chạm luật dừng."""
        if self.count_today + self.count_phase >= DAILY_CAP:
            raise StopRun("TRẦN NGÂN SÁCH NGÀY ~200 REQUEST — dừng theo luật")
        if self.count_phase >= self.max_req:
            raise StopRun("CHẠM GIỚI HẠN max_req CỦA PHA (%d)" % self.max_req)
        if self.count_phase > 0 or self.count_today > 0:
            time.sleep(SLEEP_S)  # 10 giây/request — kể cả request đầu của pha nếu hôm nay đã chạy
        req = urllib.request.Request(
            url, headers={"User-Agent": "poly-viec3-descriptive-count/1.0 (paper research, read-only)"})
        t0 = time.time()
        status, doc, err, retry_after = None, None, None, None
        try:
            with urllib.request.urlopen(req, timeout=30, context=self.ssl_ctx) as r:
                status = r.status
                retry_after = r.headers.get("Retry-After")
                raw = r.read()
        except urllib.error.HTTPError as e:
            status = e.code
            retry_after = e.headers.get("Retry-After") if e.headers else None
            err = repr(e)
            if status not in (429, 403):
                raw = e.read()  # 4xx khác: lỗi tham số của ta — đọc body, KHÔNG dừng luật (429/403 mới dừng)
        except Exception as e:  # mạng/SSL/timeout
            if "CERTIFICATE_VERIFY_FAILED" in repr(e) and self.ssl_verified:
                # chỉ hạ sang không-xác-minh đúng 1 lần cho lỗi chuỗi CA (GET chỉ-đọc, tiền lệ probe)
                self.ssl_verified = False
                self.ssl_ctx = ssl._create_unverified_context()
                self._ledger({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                              "phase": self.phase, "tag": "SSL_FALLBACK_UNVERIFIED",
                              "url": url, "status": None, "latency_ms": int((time.time() - t0) * 1000),
                              "retry_after": None,
                              "error": "certificate verify failed -> unverified context (read-only GET, precedent probe2_v2.py)"})
                return self.get(url, tag, save_path=save_path)
            err = repr(e)
        dt_ms = int((time.time() - t0) * 1000)
        self.count_phase += 1
        self._ledger({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "phase": self.phase, "tag": tag, "url": url,
                      "status": status, "latency_ms": dt_ms,
                      "retry_after": retry_after, "error": err})
        if status in (429, 403):
            raise StopRun("HTTP %d — DỪNG TOÀN BỘ theo luật (Retry-After=%s)" % (status, retry_after))
        if status is None or status >= 500:
            raise StopRun("LỖI MẠNG/HTTP %s (%s) — dừng, không retry ngay" % (status, err))
        if dt_ms > LAT_HARD_STOP_MS:
            raise StopRun("RESPONSE CHẬM BẤT THƯỜNG %d ms (> %d ms) — dừng toàn bộ theo luật"
                          % (dt_ms, LAT_HARD_STOP_MS))
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            tmp = save_path + ".tmp"
            with open(tmp, "wb") as f:
                f.write(raw)
            os.replace(tmp, save_path)
        try:
            doc = json.loads(raw.decode("utf-8"))
        except Exception as e:
            raise StopRun("JSON LỖI (%s) — dừng" % repr(e))
        return doc, status


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def jdump(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, path)


def jlappend(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
