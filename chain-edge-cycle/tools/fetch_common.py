"""Bộ giao tiếp API dùng chung — cycle tìm edge bằng reverse engineer (chỉ nghiên cứu trên giấy).

Luật áp cho MỌI request (xem 00_CHARTER.md):
- log đầy đủ vào logs/request_log.csv;
- nghỉ tối thiểu giữa 2 request cùng API (tools/budget_config.json);
- trần request/ngày từng API, vượt trần là dừng (không kéo bù, không đổi endpoint);
- 429/403: ghi logs/rate_events.log kèm Retry-After, khoá API trong phiên này,
  ném RateLimited để bước đang chạy DỪNG. Không tăng tốc, không lách endpoint.
"""
import csv
import datetime
import json
import os
import ssl
import time
import urllib.error
import urllib.request


def _make_ssl_ctx():
    """macOS: python.org Python thường thiếu CA mặc định — thử certifi, rồi /etc/ssl/cert.pem."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    for ca in ("/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"):
        if os.path.exists(ca):
            return ssl.create_default_context(cafile=ca)
    return ssl.create_default_context()


_SSL_CTX = _make_ssl_ctx()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT, "logs")
STATE_DIR = os.path.join(ROOT, "state")
REQ_LOG = os.path.join(LOG_DIR, "request_log.csv")
RATE_LOG = os.path.join(LOG_DIR, "rate_events.log")
DAILY = os.path.join(STATE_DIR, "daily_counts.json")

with open(os.path.join(ROOT, "tools", "budget_config.json"), encoding="utf-8") as _f:
    BUDGETS = json.load(_f)

_last_call = {}
_halted = set()


class RateLimited(Exception):
    """429/403 — dừng bước đang chạy, ghi log, không lách."""


class BudgetExceeded(Exception):
    """Vượt trần ngày — dừng hẳn tới hôm sau, không kéo bù."""


def utcnow_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _today():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def _load_daily():
    """Trả dict {api: count} của HÔM NAY (UTC). File có dạng {"YYYY-MM-DD": {api: n}}."""
    try:
        with open(DAILY, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        d = {}
    t = _today()
    if t in d and isinstance(d[t], dict):
        return dict(d[t])
    # tương thích file cũ bị ghi phẳng (bug 2026-11-02 đã sửa): không có khóa ngày → đếm lại từ log
    return {}


def _save_daily(inner):
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        with open(DAILY, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        d = {}
    t = _today()
    d = {k: v for k, v in d.items() if k == t}
    d[t] = inner
    with open(DAILY, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def _log_row(api, endpoint, status, elapsed_ms, note=""):
    os.makedirs(LOG_DIR, exist_ok=True)
    new = not os.path.exists(REQ_LOG)
    with open(REQ_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts_utc", "api", "endpoint", "status", "elapsed_ms", "note"])
        w.writerow([utcnow_iso(), api, endpoint, status, elapsed_ms, note])


def http(api, path, method="GET", payload=None, headers=None, timeout=30):
    """Gửi 1 request trong ngân sách. Trả (status, body_bytes). Ngoại lệ = dừng theo luật."""
    if api in _halted:
        raise RateLimited(f"{api} bị khoá từ lỗi rate-limit trước đó trong phiên.")
    cfg = BUDGETS[api]
    daily = _load_daily()
    used = daily.get(api, 0)
    if used >= cfg["daily_cap"]:
        raise BudgetExceeded(f"{api} vượt trần ngày {cfg['daily_cap']} (đã dùng {used}). Dừng, không kéo bù.")

    wait = _last_call.get(api, 0.0) + cfg["min_interval_sec"] - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_call[api] = time.time()

    url = cfg["base_url"].rstrip("/") + "/" + path.lstrip("/")
    # header HTTP chỉ cho phép latin-1: không dùng dấu tiếng Việt ở đây
    h = {"User-Agent": cfg.get("user_agent", "edge-research-paper/0.1 paper-only no-trading")}
    if headers:
        h.update(headers)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
            status, body = r.status, r.read()
            retry_after = r.headers.get("Retry-After")
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            body = e.read()
        except Exception:
            body = b""
        retry_after = e.headers.get("Retry-After") if e.headers else None
        elapsed = int((time.time() - t0) * 1000)
        if status in (429, 403):
            _halted.add(api)
            os.makedirs(LOG_DIR, exist_ok=True)
            with open(RATE_LOG, "a", encoding="utf-8") as f:
                f.write(f"{utcnow_iso()}\t{api}\t{path}\t{status}\tRetry-After={retry_after}\n")
            _log_row(api, path, status, elapsed, f"RATE-LIMIT Retry-After={retry_after} -> DỪNG API")
            raise RateLimited(f"{api} trả {status}, Retry-After={retry_after}. Dừng theo luật, không lách.")
        _log_row(api, path, status, elapsed)
        raise
    elapsed = int((time.time() - t0) * 1000)
    _log_row(api, path, status, elapsed)
    daily[api] = used + 1
    _save_daily(daily)
    return status, body


def http_json(api, path, **kw):
    status, body = http(api, path, **kw)
    return status, json.loads(body.decode("utf-8"))
