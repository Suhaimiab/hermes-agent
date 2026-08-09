#!/usr/bin/env python3
"""
Query Xueqiu (雪球) for stock quotes, search, hot posts, and hot stock rankings.

Usage:
    python xueqiu_api.py quote <symbol>
    python xueqiu_api.py search <query> [--limit N]
    python xueqiu_api.py hot-posts [--limit N]
    python xueqiu_api.py hot-stocks [--limit N] [--type 10|12]

No login required. A session cookie is warmed by visiting xueqiu.com once
before calling the data API, since a stateless request is rejected.

KNOWN LIMITATION (as of 2026-08-09): Xueqiu's Aliyun WAF now serves a
JavaScript-challenge page instead of the real homepage, which defeats this
plain-HTTP cookie warm-up, so all commands currently fail — see the warning
at the top of SKILL.md for details and the recommended fallback.
"""

import argparse
import http.cookiejar
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
_REFERER = "https://xueqiu.com/"
_TIMEOUT = 10
_HOME = "https://xueqiu.com"

_cookie_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_cookie_jar))
_warmed = False


def _warm_cookies():
    """Visit the Xueqiu homepage once to pick up the anti-bot session cookie."""
    global _warmed
    if _warmed:
        return
    req = urllib.request.Request(_HOME, headers={"User-Agent": _UA})
    _opener.open(req, timeout=_TIMEOUT)
    _warmed = True


def _get_json(url: str):
    _warm_cookies()
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Referer": _REFERER})
    with _opener.open(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_quote(symbol: str):
    encoded = urllib.parse.quote(symbol, safe="")
    data = _get_json(f"https://stock.xueqiu.com/v5/stock/quote.json?symbol={encoded}&extend=detail")
    q = (data.get("data") or {}).get("quote") or {}
    if not q:
        print(f"Error: no quote data for symbol '{symbol}' — check the symbol format (see SKILL.md).", file=sys.stderr)
        sys.exit(1)
    return {
        "symbol": q.get("symbol", symbol),
        "name": q.get("name", ""),
        "current": q.get("current"),
        "percent": q.get("percent"),
        "chg": q.get("chg"),
        "high": q.get("high"),
        "low": q.get("low"),
        "open": q.get("open"),
        "last_close": q.get("last_close"),
        "volume": q.get("volume"),
        "market_capital": q.get("market_capital"),
        "pe_ttm": q.get("pe_ttm"),
        "timestamp": q.get("timestamp"),
    }


def cmd_search(query: str, limit: int):
    data = _get_json(f"https://xueqiu.com/stock/search.json?code={urllib.parse.quote(query)}&size={limit}")
    stocks = data.get("stocks") or []
    return [
        {"symbol": s.get("code", ""), "name": s.get("name", ""), "exchange": s.get("exchange", "")}
        for s in stocks[:limit]
    ]


def cmd_hot_posts(limit: int):
    limit = min(max(limit, 0), 50)
    if limit == 0:
        return []
    data = _get_json(
        "https://xueqiu.com/v4/statuses/public_timeline_by_category.json"
        f"?since_id=-1&max_id=-1&count={limit}&category=-1"
    )
    results = []
    for item in (data.get("list") or [])[:limit]:
        try:
            post = json.loads(item["data"]) if isinstance(item.get("data"), str) else {}
        except (json.JSONDecodeError, KeyError):
            post = {}
        user = post.get("user") or {}
        target = post.get("target", "")
        results.append({
            "title": post.get("title") or "",
            "text": (post.get("text") or post.get("description") or "")[:200],
            "author": user.get("screen_name", ""),
            "likes": post.get("like_count", 0),
            "url": f"https://xueqiu.com{target}" if target else "",
        })
    return results


def cmd_hot_stocks(limit: int, stock_type: int):
    data = _get_json(f"https://stock.xueqiu.com/v5/stock/hot_stock/list.json?size={limit}&type={stock_type}")
    items = (data.get("data") or {}).get("items") or []
    return [
        {
            "symbol": item.get("code") or item.get("symbol", ""),
            "name": item.get("name", ""),
            "current": item.get("current"),
            "percent": item.get("percent"),
            "rank": idx,
        }
        for idx, item in enumerate(items[:limit], 1)
    ]


def main():
    parser = argparse.ArgumentParser(description="Query Xueqiu stock data")
    sub = parser.add_subparsers(dest="command", required=True)

    p_quote = sub.add_parser("quote")
    p_quote.add_argument("symbol")

    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=10)

    p_hot_posts = sub.add_parser("hot-posts")
    p_hot_posts.add_argument("--limit", type=int, default=20)

    p_hot_stocks = sub.add_parser("hot-stocks")
    p_hot_stocks.add_argument("--limit", type=int, default=10)
    p_hot_stocks.add_argument("--type", type=int, default=10, choices=[10, 12])

    args = parser.parse_args()

    try:
        if args.command == "quote":
            result = cmd_quote(args.symbol)
        elif args.command == "search":
            result = cmd_search(args.query, args.limit)
        elif args.command == "hot-posts":
            result = cmd_hot_posts(args.limit)
        elif args.command == "hot-stocks":
            result = cmd_hot_stocks(args.limit, args.type)
    except urllib.error.URLError as e:
        print(f"Error: network request failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
