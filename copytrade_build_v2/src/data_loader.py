# -*- coding: utf-8 -*-
"""Data loader — Gamma + Data API v2, phân trang cursor, checkpoint, ngân sách, luật dừng.
Trong bước xây này KHÔNG gọi API thật: transport bọc ngoài có thể tiêm (tests dùng giả lập).
Luật dừng: 429/403/5xx/lỗi mạng/độ trễ tăng bất thường -> dừng toàn bộ, không retry ngay."""
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def floor_seconds_utc(rfc3339):
    """§19.6 (đã duyệt): RFC3339 -> epoch giây UTC, làm tròn XUỐNG tới giây."""
    s = rfc3339.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() // 1.0)


class StopProbe(Exception):
    """Kích hoạt khi gặp 429/403/5xx/lỗi mạng/độ trễ bất thường — dừng toàn bộ, không retry."""


class BudgetHttp:
    """GET có ngân sách + checkpoint + log. transport(url) -> (status, body_str, headers, latency_s)."""

    def __init__(self, out_dir, max_requests=200, sleep_s=10.0, transport=None, latency_watch=True):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.max_requests = max_requests
        self.sleep_s = sleep_s
        self.n_requests = 0
        self.latencies = []
        self.transport = transport or self._default_transport
        self.latency_watch = latency_watch
        self.log_path = os.path.join(out_dir, "requests.log")
        self.ckpt_path = os.path.join(out_dir, "checkpoint.json")

    @staticmethod
    def _default_transport(url):
        import ssl
        ctx = None
        for ca in ("/etc/ssl/cert.pem", "/private/etc/ssl/cert.pem"):
            if os.path.exists(ca):
                ctx = ssl.create_default_context(cafile=ca)
                break
        t0 = time.time()
        req = urllib.request.Request(url, headers={
            "User-Agent": "copytrade-paper/1.0 (read-only research)",
            "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                return r.status, r.read().decode("utf-8", "replace"), dict(r.headers), time.time() - t0
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")[:2000], dict(e.headers or {}), time.time() - t0

    def _log(self, **kw):
        kw["ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(kw, ensure_ascii=False) + "\n")

    def checkpoint(self, step, status, summary=None):
        ck = {}
        if os.path.exists(self.ckpt_path):
            try:
                ck = json.load(open(self.ckpt_path, encoding="utf-8"))
            except Exception:
                ck = {}
        ck[step] = {"status": status,
                    "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "summary": summary}
        json.dump(ck, open(self.ckpt_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def get_json(self, url, tag):
        if self.n_requests >= self.max_requests:
            raise StopProbe("vượt ngân sách %d request" % self.max_requests)
        self.n_requests += 1
        status, body, headers, latency = self.transport(url)
        self.latencies.append(latency)
        self._log(tag=tag, url=url, status=status, latency_ms=int(latency * 1000),
                  retry_after=headers.get("Retry-After"))
        if status in (429, 403):
            raise StopProbe("HTTP %d — Retry-After=%s" % (status, headers.get("Retry-After")))
        if status is None or status >= 500:
            raise StopProbe("HTTP %s (lỗi máy chủ)" % status)
        if self.latency_watch and len(self.latencies) >= 6 and latency > 3.0:
            med = statistics.median(self.latencies[:-1])
            if latency > max(3.0 * med, med + 3.0):
                raise StopProbe("độ trễ bất thường %.1fs vs trung vị %.1fs" % (latency, med))
        if status == 404:
            return None, status
        try:
            doc = json.loads(body)
        except Exception:
            doc = {"_raw": body[:2000]}
        return doc, status

    def paginate(self, url_first, tag, max_pages=None):
        from . import config as _cfg
        if max_pages is None:
            max_pages = _cfg.MAX_PAGES  # TỰ CHỌN — xem config.SELF_CHOSEN
        """Đi hết trang tới next_cursor null. Trần max_pages — chạm trần thì trả cờ capped."""
        rows, cursor, capped, npages = [], None, False, 0
        url = url_first
        while True:
            doc, st = self.get_json(url, "%s_p%d" % (tag, npages + 1))
            if not isinstance(doc, dict):
                break
            rows.extend(doc.get("data") or [])
            pag = doc.get("pagination") or {}
            npages += 1
            nc = pag.get("next_cursor")
            if not nc or not pag.get("has_more"):
                break
            if npages >= max_pages:
                capped = True
                cursor = nc
                break
            cursor = nc
            sep = "&" if "?" in url_first else "?"
            url = url_first + sep + "cursor=" + __import__("urllib.parse", fromlist=["quote"]).quote(nc, safe="")
            time.sleep(self.sleep_s)
        return {"rows": rows, "pages": npages, "next_cursor": cursor,
                "capped": capped, "status": st}


# --- Đường gọi đúng dạng đã xác nhận ở thăm dò V1/V2 ---

def url_gamma_markets_by_conditions(conditions, include_tag=True):
    """Gamma /markets: LẶP condition_ids cho từng mã + closed=any (comma KHÔNG hoạt động —
    đã chứng minh V2 Việc 1). include_tag=true bắt buộc nếu muốn tags (V2 Việc 3)."""
    from urllib.parse import urlencode
    q = [("condition_ids", c) for c in conditions]
    q += [("closed", "any"), ("limit", str(min(20, max(1, len(conditions)))))]
    if include_tag:
        q.append(("include_tag", "true"))
    return "https://gamma-api.polymarket.com/markets?" + urlencode(q)


def url_data_trades(user, start, end, taker_only=False, limit=500):
    from urllib.parse import urlencode
    return "https://data-api.polymarket.com/v2/trades?" + urlencode({
        "user": user, "taker_only": "true" if taker_only else "false",
        "start": start, "end": end, "limit": limit})


def url_data_activity(user, start, end, limit=500):
    from urllib.parse import urlencode
    return "https://data-api.polymarket.com/v2/activity?" + urlencode({
        "user": user, "type": "TRADE", "start": start, "end": end, "limit": limit})


def url_resolutions(conditions):
    from urllib.parse import urlencode
    return "https://data-api.polymarket.com/v2/resolutions?" + urlencode(
        {"condition": ",".join(conditions[:20])})
