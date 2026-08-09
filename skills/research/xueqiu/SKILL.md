---
name: xueqiu
description: Look up real-time stock quotes, search for stocks, and read trending posts/hot stock rankings from Xueqiu (雪球), a Chinese stock market community. Covers A-share, Hong Kong, and US symbols. No login required for these endpoints. Use for "what's this stock trading at", "search for this stock on Xueqiu", "what's trending in the Xueqiu community" requests.
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  commands: [python3]
metadata:
  hermes:
    tags: [xueqiu, stocks, finance, china, market-data]
    homepage: https://xueqiu.com
---

# Xueqiu (雪球) — stock quotes and community data

Xueqiu's quote/search/trending endpoints work without a logged-in account, but they need a warmed anti-bot session cookie: a plain, stateless `curl` call to the API alone will fail. A helper script handles the two-step cookie warm-up (visit homepage first, then call the API with that session).

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file.

```bash
# Real-time stock quote (SH/SZ = mainland China, plain number = Hong Kong, ticker = US)
python3 SKILL_DIR/scripts/xueqiu_api.py quote SH600519
python3 SKILL_DIR/scripts/xueqiu_api.py quote 00700
python3 SKILL_DIR/scripts/xueqiu_api.py quote AAPL

# Search for a stock by code or Chinese name
python3 SKILL_DIR/scripts/xueqiu_api.py search "茅台"

# Community hot posts
python3 SKILL_DIR/scripts/xueqiu_api.py hot-posts --limit 20

# Hot stock ranking (10 = popularity rank [default], 12 = watchlist rank)
python3 SKILL_DIR/scripts/xueqiu_api.py hot-stocks --limit 10
python3 SKILL_DIR/scripts/xueqiu_api.py hot-stocks --limit 10 --type 12
```

All commands print JSON to stdout.

## Symbol Format

- Mainland China (A-share): prefix with exchange — `SH600519` (Shanghai), `SZ000858` (Shenzhen)
- Hong Kong: plain 5-digit code, e.g. `00700`
- US: plain ticker, e.g. `AAPL`

## Workflow

1. For a quote request, resolve the symbol format above (ask the user for the exchange if genuinely ambiguous — e.g. a bare "600519" needs to become "SH600519").
2. If unsure of the exact symbol, run `search` first to confirm it before quoting.
3. For "what's trending on Xueqiu" style requests, use `hot-posts` (community discussion) or `hot-stocks` (price-ranked lists) depending on what the user means.

## Error Handling

- **Empty quote result**: the symbol format is probably wrong — try `search` to find the correct one.
- **Connection/cookie warm-up failure**: the script visits `https://xueqiu.com` first to pick up the anti-bot cookie before calling the API; if that homepage request itself fails, Xueqiu may be geo-blocking the server's IP — note this to the user rather than retrying repeatedly.

## Notes

- These endpoints work anonymously; a real logged-in cookie is only needed for authenticated actions (posting, following), which are out of scope for this skill.
- If Xueqiu changes its anti-bot behavior and the warm-up stops working, check whether the API now requires additional headers by comparing against a browser's network tab on xueqiu.com.
