#!/usr/bin/env python3
"""Phát hiện vũ trụ pool mới cho Wave 1 (bước 0) — KHÔNG trích trường giá.

Phân trang /networks/{net}/new_pools?page=N từ trang 1 (hoặc resume từ state), lưu raw JSON
mỗi trang, extract CSV chỉ gồm trường cấu trúc (đúng wave01/step0_universe.md mục 2).
Dừng khi: chạm --until, hết dữ liệu/trang lặp, chạm --max-calls, 429/403 hoặc vượt trần ngày
(fetch_common tự Raise — script dừng sạch và ghi lý do vào state).
Chạy lại để tiếp tục: nhớ số trang cuối trong state/discovery_{net}.json.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_common as fc

ROOT = fc.ROOT


def parse_iso(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", required=True, help="ví dụ: base, solana")
    ap.add_argument("--until", required=True, help="ISO UTC — dừng khi pool cũ nhất cũ hơn mốc này")
    ap.add_argument("--max-calls", type=int, default=600)
    ap.add_argument("--reserve-daily", type=int, default=600,
                    help="giữ lại ít nhất N request GT trong trần ngày cho việc khác")
    args = ap.parse_args()

    until = parse_iso(args.until)
    raw_dir = os.path.join(ROOT, "data", "gt", "new_pools", args.network)
    os.makedirs(raw_dir, exist_ok=True)
    extract = os.path.join(raw_dir, "universe_extract.csv")
    state_f = os.path.join(ROOT, "state", f"discovery_{args.network}.json")

    state = {"last_page": 0, "pages_done": 0, "oldest_seen": "", "stopped_reason": ""}
    if os.path.exists(state_f):
        with open(state_f, encoding="utf-8") as f:
            state = json.load(f)

    new_extract = not os.path.exists(extract)
    out = open(extract, "a", encoding="utf-8")
    if new_extract:
        out.write("pool_address,quote_symbol,base_token_address,pool_created_at_utc,page,discovered_at_utc,dex_id\n")

    used_today = fc._load_daily().get("geckoterminal", 0)
    cap = min(args.max_calls,
              max(0, fc.BUDGETS["geckoterminal"]["daily_cap"] - args.reserve_daily - used_today))
    calls = 0
    page = state["last_page"] + 1
    reason = f"max-calls ({args.max_calls})"
    prev_oldest = state.get("oldest_seen") or None

    try:
        while calls < cap:
            st, js = fc.http_json("geckoterminal", f"networks/{args.network}/new_pools?page={page}")
            calls += 1
            data = js.get("data", [])
            if not data:
                reason = "hết dữ liệu (trang rỗng)"
                break
            with open(os.path.join(raw_dir, f"page_{page:05d}.json"), "w", encoding="utf-8") as f:
                json.dump(js, f, ensure_ascii=False)
            oldest = None
            for item in data:
                a = item["attributes"]
                ca = a.get("pool_created_at")
                if ca and (oldest is None or ca < oldest):
                    oldest = ca
                rel = item.get("relationships", {})
                base_tok = rel.get("base_token", {}).get("data", {}).get("id", "")
                base_addr = base_tok.split("_", 1)[-1] if "_" in base_tok else ""
                dex_id = rel.get("dex", {}).get("data", {}).get("id", "")
                name = a.get("name", "")
                quote_sym = name.split("/")[-1].strip() if "/" in name else ""
                out.write(",".join([a.get("address", ""), quote_sym, base_addr, ca or "",
                                    str(page), fc.utcnow_iso(), dex_id]) + "\n")
            out.flush()
            state.update({"last_page": page, "pages_done": state["pages_done"] + 1, "oldest_seen": oldest or ""})
            with open(state_f, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False)
            if page % 10 == 0:
                print(f"[{fc.utcnow_iso()}] page {page}; cũ nhất trang: {oldest}; calls={calls}/{cap}", flush=True)
            if oldest is None:
                reason = "trang không có pool_created_at — dừng an toàn"
                break
            if oldest == prev_oldest:
                reason = "không tiến (trang lặp) — dừng"
                break
            prev_oldest = oldest
            if parse_iso(oldest) < until:
                reason = f"đạt mốc until ({args.until})"
                break
            page += 1
    except (fc.RateLimited, fc.BudgetExceeded) as e:
        reason = f"DỪNG THEO LUẬT: {type(e).__name__}: {e}"
    finally:
        out.close()
        state["stopped_reason"] = f"[{fc.utcnow_iso()}] {reason}"
        with open(state_f, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)
        print(f"[{fc.utcnow_iso()}] DỪNG: {reason}; tổng trang đã xong: {state['pages_done']}; cuối: page {state['last_page']}; cũ nhất đã thấy: {state['oldest_seen']}")
        if os.path.exists(extract):
            with open(extract, encoding="utf-8") as f:
                n = sum(1 for _ in f) - 1
            print(f"extract hiện có {n} dòng.")


if __name__ == "__main__":
    main()
