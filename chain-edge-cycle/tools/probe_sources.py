#!/usr/bin/env python3
"""Thăm dò nguồn dữ liệu công khai KHÔNG CẦN KEY cho cycle tìm edge.

Mục đích: xác nhận (1) gọi được không, (2) trả trường gì, (3) lịch sử sâu bao nhiêu.
KHÔNG tính bất kỳ số liệu lãi/lỗ nào ở đây — kết quả chỉ để ghi vào state/checkpoint.md.
Tổng ~15 request, nằm trong ngân sách ngày.
"""
import datetime
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_common as fc

# Uniswap v3 USDC/WETH 0.05% trên Ethereum — pool lớn, ổn định, để đo độ sâu nến
ETH_USDC_POOL = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"


def utc(ts):
    try:
        return datetime.datetime.fromtimestamp(int(float(ts)), datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "?"


def parse_iso(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def new_pools_facts(net):
    st, js = fc.http_json("geckoterminal", f"networks/{net}/new_pools?page=1")
    data = js.get("data", [])
    if not data:
        print("  (trang rỗng)")
        return None
    a0 = data[0]["attributes"]
    created = [x["attributes"].get("pool_created_at") for x in data if x["attributes"].get("pool_created_at")]
    print(f"  HTTP {st}; số pool/trang: {len(data)}; links.next: {'có' if js.get('links', {}).get('next') else 'KHÔNG'}")
    print(f"  trường attributes: {sorted(a0.keys())}")
    if created:
        print(f"  pool_created_at mới nhất trang 1: {created[0]}")
        print(f"  pool_created_at cũ nhất trang 1: {created[-1]}")
        if len(created) >= 2:
            t0, t1 = parse_iso(created[0]), parse_iso(created[-1])
            span_h = max((t0 - t1).total_seconds() / 3600.0, 1e-9)
            print(f"  mật độ ước tính: {len(created) / span_h * 24:,.0f} pool/ngày")
    print(f"  ví dụ name: {a0.get('name')!r}; dex: {data[0].get('relationships', {}).get('dex', {}).get('data', {}).get('id')}")
    # chọn 1 pool đã >3h tuổi để thử nến giờ/phút
    for x in data:
        ca = x["attributes"].get("pool_created_at")
        if ca and (datetime.datetime.now(datetime.timezone.utc) - parse_iso(ca)).total_seconds() > 3 * 3600:
            return x["attributes"]["address"]
    return None


def ohlcv_facts(net, pool, timeframe, limit=1000, extra=""):
    # LƯU Ý 2026-11-02: day?limit=10 CÓ nến; limit>=100 (hour lẫn day) → 200 rỗng (nghi
    # ngưỡng limit ẩn cho anonymous). trước_timestamp chưa kiểm chứng được. Nến là newest-first.
    # Sửa lỗi cũ: nhận xét trước đây đổ lỗi cho param aggregate/currency là SAI — 2 lần 400
    # hôm đó do bug đảo tham số trong script test (xem state/checkpoint.md 2026-11-02).
    st, js = fc.http_json(
        "geckoterminal",
        f"networks/{net}/pools/{pool}/ohlcv/{timeframe}?limit={limit}{extra}",
    )
    lst = (js.get("data", {}).get("attributes", {}) or {}).get("ohlc_list") or []
    if not lst:
        print(f"  {timeframe}: KHÔNG có nến")
        return None
    print(f"  {timeframe}: {len(lst)} nến; cũ nhất {utc(lst[0][0])}; mới nhất {utc(lst[-1][0])}")
    return lst[0][0]


print("=== A. GeckoTerminal new_pools: base ===")
try:
    base_old_pool = new_pools_facts("base")
except Exception as e:
    print(f"  LỖI {type(e).__name__}: {e}")
    base_old_pool = None

print("\n=== B. GeckoTerminal new_pools: solana ===")
try:
    new_pools_facts("solana")
except Exception as e:
    print(f"  LỖI {type(e).__name__}: {e}")

print("\n=== C. GT OHLCV pool lớn (eth, USDC/WETH uni-v3) ===")
try:
    ohlcv_facts("eth", ETH_USDC_POOL, "day")
    oldest_hour = ohlcv_facts("eth", ETH_USDC_POOL, "hour")
    if oldest_hour:
        ohlcv_facts("eth", ETH_USDC_POOL, "hour", 1000, extra=f"&before_timestamp={int(oldest_hour)}")
except Exception as e:
    print(f"  LỖI {type(e).__name__}: {e}")

print("\n=== D. GT OHLCV pool MỚI trên base (nến giờ + phút có tồn tại không) ===")
if base_old_pool:
    try:
        print(f"  pool thử: {base_old_pool}")
        ohlcv_facts("base", base_old_pool, "hour", limit=10)
        ohlcv_facts("base", base_old_pool, "minute", limit=10)
    except Exception as e:
        print(f"  LỖI {type(e).__name__}: {e}")
else:
    print("  (bỏ qua — không có pool nào >3h tuổi trong trang 1)")

print("\n=== E. DexScreener ===")
try:
    st, js = fc.http_json("dexscreener", f"latest/dex/pairs/ethereum/{ETH_USDC_POOL}")
    pairs = js.get("pairs") or []
    if pairs:
        p = pairs[0]
        print(f"  HTTP {st}; pairs: {len(pairs)}")
        print(f"  pairCreatedAt: {p.get('pairCreatedAt')} ({utc((p.get('pairCreatedAt') or 0) / 1000)})")
        print(f"  liquidity.usd: {p.get('liquidity', {}).get('usd')}")
        print(f"  trường: {sorted(p.keys())}")
except Exception as e:
    print(f"  LỖI {type(e).__name__}: {e}")
try:
    st, js = fc.http_json("dexscreener", "token-profiles/latest/v1")
    if isinstance(js, list):
        cnt = Counter(x.get("chainId") for x in js)
        print(f"  token-profiles: {len(js)} mục; theo chuỗi: {dict(cnt)}")
    else:
        print(f"  token-profiles: dạng khác list: {type(js)}")
except Exception as e:
    print(f"  LỖI {type(e).__name__}: {e}")

print("\n=== F. RPC công khai (không key) ===")
for api in ("solana_rpc", "base_rpc", "arbitrum_rpc", "bsc_rpc", "eth_rpc"):
    try:
        if api == "solana_rpc":
            st, body = fc.http_json(api, "", method="POST", payload={"jsonrpc": "2.0", "id": 1, "method": "getVersion"})
            print(f"  {api}: HTTP {st}; solana-core {body.get('result', {}).get('solana-core', '?')}")
        else:
            st, body = fc.http_json(api, "", method="POST", payload={"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber"})
            print(f"  {api}: HTTP {st}; block #{int(body.get('result', '0x0'), 16)}")
    except Exception as e:
        print(f"  {api}: LỖI {type(e).__name__}: {e}")

print("\nXong. Ghi kết quả vào state/checkpoint.md (thủ công).")
