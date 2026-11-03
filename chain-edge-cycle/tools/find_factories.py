#!/usr/bin/env python3
"""Tìm các factory DEX đang thật sự tạo pool mới trên Base (chặng 1, loop 10h).

Nguyên tắc:
- MẪU LỆCH (DexScreener token-profiles/boosts) chỉ dùng để nhận diện TOPOLOGY (địa chỉ factory).
  Vũ trụ thật luôn lấy bằng getLogs trên factory → không thiên lệch chọn.
- Với pool mẫu: block tạo ≈ pairCreatedAt (DS) → getLogs(address=pool, block±2) → txHash →
  receipt.to = factory (pool do factory tạo ra).
- Kiểm chứng mỗi factory bằng getLogs 50k block đếm PoolCreated.

Mọi request qua fetch_common (log + ngân sách). Kết quả ghi state/factories_base.json.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_common as fc

ROOT = fc.ROOT
RPC = "base_pubnode"
BLOCKS_PER_SEC = 0.5  # 2 giây/block — đã chuẩn đo ở chặng 1 (slope 2.0000)
B0_TS_ANCHOR = None   # điền lúc chạy: timestamp của block hiện tại

POOL_CREATED = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118"


def rpc(method, params):
    st, js = fc.http_json(RPC, "", method="POST",
                          payload={"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if "error" in js:
        raise RuntimeError(f"{method}: {str(js['error'])[:160]}")
    return js["result"]


def ds(path):
    st, js = fc.http_json("dexscreener", path)
    return js


def main():
    # 1) lấy block hiện tại + timestamp làm mốc nội suy
    b_now = int(rpc("eth_blockNumber", []), 16)
    blk = rpc("eth_getBlockByNumber", [hex(b_now), False])
    ts_now = int(blk["timestamp"], 16)
    print(f"B={b_now} ts={ts_now}")

    def block_at(ts_ms):
        return b_now - int((ts_now * 1000 - ts_ms) / 1000 * BLOCKS_PER_SEC)

    # 2) mẫu token từ DexScreener (profiles + boosts)
    tokens = {}
    for ep in ("token-profiles/latest/v1", "token-boosts/latest/v1", "token-boosts/top/v1"):
        try:
            arr = ds(ep)
            if isinstance(arr, list):
                for x in arr:
                    if x.get("chainId") == "base" and x.get("tokenAddress"):
                        tokens[x["tokenAddress"]] = ep
        except Exception as e:
            print(f"DS {ep}: LỖI {type(e).__name__}: {e}")
    print(f"mẫu token base: {len(tokens)} (từ {len(set(tokens.values()))} endpoint)")
    if not tokens:
        print("THIẾU MẪU — dừng")
        return

    # 3) pairs của các token mẫu (batch ≤30 địa chỉ)
    addrs = list(tokens)
    pairs = []
    for i in range(0, len(addrs), 30):
        batch = ",".join(addrs[i:i + 30])
        js = ds(f"tokens/v1/base/{batch}")
        if isinstance(js, list):
            pairs.extend([p for p in js if p.get("chainId") == "base"])
    print(f"pairs lấy được: {len(pairs)}")
    # chỉ giữ pair tạo gần đây (≤ 21 ngày) — mục đích nhận diện factory ĐANG hoạt động
    cutoff_ms = (ts_now - 21 * 86400) * 1000
    recent = [p for p in pairs if (p.get("pairCreatedAt") or 0) >= cutoff_ms]
    print(f"pair tạo ≤21 ngày: {len(recent)}")
    from collections import Counter
    dex_cnt = Counter(p.get("dexId") for p in recent)
    print("theo dexId:", dict(dex_cnt))

    # 4) với tối đa 4 pool mẫu gần nhất: truy ngược factory
    factories = {}
    recent.sort(key=lambda p: p.get("pairCreatedAt") or 0, reverse=True)
    for p in recent[:4]:
        pair = p.get("pairAddress")
        created = p.get("pairCreatedAt")
        if not pair or not created:
            continue
        b_est = block_at(created)
        try:
            js = fc.http_json(RPC, "", method="POST",
                              payload={"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                                       "params": [{"address": pair, "fromBlock": hex(b_est - 3), "toBlock": hex(b_est + 3)}]})[1]
            logs = js.get("result", []) if "error" not in js else []
            if not logs:
                print(f"pool {pair[:10]}…: không có log gần block tạo — bỏ")
                continue
            tx = logs[0]["transactionHash"]
            rc = rpc("eth_getTransactionReceipt", [tx])
            fac = rc.get("to", "")
            print(f"pool {pair[:10]}… (dex={p.get('dexId')}): tx.to = {fac}")
            if fac:
                factories[fac] = p.get("dexId")
        except Exception as e:
            print(f"pool {pair[:10]}…: LỖI {type(e).__name__}: {str(e)[:120]}")

    # thêm các factory đã biết để đo cùng lúc
    factories.setdefault("0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865", "pancakev3-biết-sẵn")
    factories.setdefault("0x1F98431c8aD98523631AE4a59f267346ea31F984", "univ3-biết-sẵn")
    factories.setdefault("0x420DD381b31b62cF37E8F6CC62c9a7757CE5A312", "aerodrome-biết-sẵn")

    # 5) đo tốc độ tạo pool của từng factory (50k block)
    out = {"measured_at": fc.utcnow_iso(), "b_now": b_now, "factories": {}}
    for fac, tag in factories.items():
        try:
            st, js = fc.http_json(RPC, "", method="POST",
                                  payload={"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                                           "params": [{"address": fac, "fromBlock": hex(b_now - 50000 + 1), "toBlock": hex(b_now),
                                                       "topics": [POOL_CREATED]}]})[1]
            if "error" in js:
                print(f"factory {fac} ({tag}): LỖI {str(js['error'])[:120]}")
                continue
            logs = js.get("result", [])
            per_day = len(logs) * 43200 / 50000
            print(f"factory {fac} ({tag}): {len(logs)} PoolCreated/50k ≈ {per_day:,.0f}/ngày")
            out["factories"][fac] = {"tag": tag, "per_day_est": per_day, "last50k": len(logs)}
        except Exception as e:
            print(f"factory {fac} ({tag}): LỖI {type(e).__name__}: {str(e)[:120]}")

    with open(os.path.join(ROOT, "state", "factories_base.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("đã ghi state/factories_base.json")


if __name__ == "__main__":
    main()
