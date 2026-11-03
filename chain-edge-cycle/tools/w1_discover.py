#!/usr/bin/env python3
"""Chặng 2 — discovery vũ trụ W1 (Base, 3 factory cổ điển, epoch đã đóng băng).

Input: epoch blocks (đóng băng trong step0 mục 7), factory addresses.
Output:
  data/rpc/pool_created/{factory}/chunk_XXXXX_YYYYY.json  (raw, giữ nguyên)
  data/w1_base/universe_raw.csv   (mọi PoolCreated trong epoch, mọi factory)
  data/w1_base/universe.csv       (sau tiêu chí đóng băng: quote theo ĐỊA CHỈ, dedupe theo base token)
  in ra: số lượng từng bước + theo epoch.
Resume được: bỏ qua chunk đã có file. Mọi request qua fetch_common.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_common as fc

RPC = "base_pubnode"
POOL_CREATED = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118"
EPOCHS = {"E1": (52513088, 52815488), "E2": (52815488, 53117888), "E3": (53117888, 53420288)}
E1_START, E3_END = EPOCHS["E1"][0], EPOCHS["E3"][1]
B_ANCHOR, TS_ANCHOR, SLOPE = 53420288, 1793629923, 2.0

QUOTES = {  # ánh xạ đóng băng trong step0
    "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": ("USDC", 6),
    "0xd9aaec86b65d86f6a7b5b1b0c42ffa5337d0d3fa": ("USDbC", 6),
    "0x4200000000000000000000000000000000000006": ("WETH", 18),
}
FACTORIES = {
    "univ3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    "aerodrome": "0x420DD381b31b62cF37E8F6CC62c9a7757CE5A312",
    "pancakev3": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
}
CHUNK = 50000  # giới hạn đo được của publicnode

ROOT = fc.ROOT
RAW_DIR = os.path.join(ROOT, "data", "rpc", "pool_created")
OUT_DIR = os.path.join(ROOT, "data", "w1_base")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)


def ts_of_block(b):
    return TS_ANCHOR - (B_ANCHOR - b) * SLOPE


def word_addr(hexword):
    return "0x" + hexword[-40:].lower()


def parse_created(factory, log):
    """Trả (pool, token0, token1) theo layout V3-style; aerodrome layout riêng."""
    topics = log.get("topics", [])
    data = log.get("data", "0x")
    if factory == "aerodrome":
        # Velodrome-style: PoolCreated(token0?, token1?, stable?, pool) — token có thể indexed hoặc trong data
        cands = []
        for t in topics[1:]:
            w = t[2:]
            if len(w) == 64 and int(w, 16) >> 160 == 0:
                cands.append(word_addr(t))
        for i in range(0, len(data) - 1, 64 + 2):
            w = data[i + 2:i + 2 + 64]
            if len(w) == 64 and int(w, 16) >> 160 == 0:
                cands.append(word_addr("0x" + w))
        addrs = [c for c in cands if c not in QUOTES]
        if len(cands) >= 3:
            return cands[2], cands[0], cands[1]  # pool là từ thứ 3 (quan sát thực tế sẽ hiệu chỉnh)
        return None
    # univ3/pancakev3: topics[1]=token0, topics[2]=token1, topics[3]=fee; data word0=tickSpacing, word1=pool
    if len(topics) < 3 or len(data) < 130:
        return None
    pool = word_addr(data[2 + 64:2 + 128])
    return pool, word_addr(topics[1]), word_addr(topics[2])


def getlogs(addr, frm, to):
    st, js = fc.http_json(RPC, "", method="POST",
                          payload={"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                                   "params": [{"address": addr, "fromBlock": hex(frm), "toBlock": hex(to),
                                               "topics": [POOL_CREATED]}]})
    if "error" in js:
        raise RuntimeError(str(js["error"])[:160])
    return js.get("result", [])


def main():
    rows = []  # (pool, factory, token0, token1, block, epoch)
    n_err = 0
    for fac_name, fac_addr in FACTORIES.items():
        fac_dir = os.path.join(RAW_DIR, fac_name)
        os.makedirs(fac_dir, exist_ok=True)
        frm = E1_START
        while frm <= E3_END:
            to = min(frm + CHUNK - 1, E3_END)
            fn = os.path.join(fac_dir, f"chunk_{frm}_{to}.json")
            if os.path.exists(fn):
                with open(fn, encoding="utf-8") as f:
                    logs = json.load(f)
            else:
                try:
                    logs = getlogs(fac_addr, frm, to)
                except Exception as e:
                    n_err += 1
                    print(f"[{fac_name}] chunk {frm}-{to}: LỖI {str(e)[:100]}", flush=True)
                    if n_err >= 3:
                        print("DỪNG theo luật 3 lỗi liên tiếp", flush=True)
                        return finish(rows)
                    frm = to + 1
                    continue
                with open(fn, "w", encoding="utf-8") as f:
                    json.dump(logs, f, ensure_ascii=False)
            for lg in logs:
                b = int(lg["blockNumber"], 16)
                parsed = parse_created(fac_name, lg)
                if not parsed:
                    continue
                pool, t0, t1 = parsed
                ep = next((e for e, (a, z) in EPOCHS.items() if a <= b < z), None)
                if ep:
                    rows.append((pool, fac_name, t0, t1, b, ep))
            frm = to + 1
        print(f"[{fac_name}] xong", flush=True)
    finish(rows)


def finish(rows):
    with open(os.path.join(OUT_DIR, "universe_raw.csv"), "w", encoding="utf-8") as f:
        f.write("pool,factory,token0,token1,creation_block,epoch\n")
        for r in rows:
            f.write(",".join(map(str, r)) + "\n")

    # tiêu chí đóng băng: quote theo địa chỉ, dedupe theo base token (giữ pool ĐẦU TIÊN theo block)
    kept, dropped_dupes, dropped_quote = {}, 0, 0
    for pool, fac, t0, t1, b, ep in sorted(rows, key=lambda r: r[4]):
        q = next((a for a in (t0, t1) if a in QUOTES), None)
        if q is None:
            dropped_quote += 1
            continue
        base = t1 if q == t0 else t0
        if base in kept:
            dropped_dupes += 1
            continue
        kept[base] = (pool, fac, q, base, b, ep)
    with open(os.path.join(OUT_DIR, "universe.csv"), "w", encoding="utf-8") as f:
        f.write("pool,factory,quote,base_token,creation_block,creation_time_est_utc,epoch\n")
        import datetime
        for base, (pool, fac, q, b_tok, b, ep) in sorted(kept.items(), key=lambda kv: kv[1][4]):
            t = datetime.datetime.fromtimestamp(ts_of_block(b), datetime.timezone.utc).isoformat()
            f.write(f"{pool},{fac},{q},{b_tok},{b},{t},{ep}\n")
    from collections import Counter
    cnt = Counter(v[5] for v in kept.values())
    fac_cnt = Counter(v[1] for v in kept.values())
    q_cnt = Counter(v[2] for v in kept.values())
    print(f"\nRAW PoolCreated trong epoch: {len(rows)}")
    print(f"Bỏ vì quote ngoài bộ: {dropped_quote}; bỏ vì trùng base token: {dropped_dupes}")
    print(f"UNIVERSE: {len(kept)} pool — theo epoch: {dict(cnt)}; theo factory: {dict(fac_cnt)}; theo quote: {dict(q_cnt)}")


if __name__ == "__main__":
    main()
