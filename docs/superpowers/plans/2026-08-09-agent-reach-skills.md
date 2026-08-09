# Agent-Reach-Inspired Headless Capability Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add five new native `SKILL.md` skills to Hermes — RSS one-shot reads, Bilibili, V2EX, Xueqiu (雪球), and a free cookie-based Twitter/X alternative — filling capability gaps identified by comparing Hermes against the Agent-Reach project, scoped to platforms that work headless on Hermes's production Hetzner VPS.

**Architecture:** Each skill is a self-contained `skills/<category>/<name>/SKILL.md` (+ optional `scripts/*.py` helper) following the existing convention used by `skills/social-media/xitter` and `skills/media/youtube-content`. Skill discovery in Hermes is filesystem-based (`tools/skills_hub.py` scans for `SKILL.md`) — no registry file needs updating. The five skills are functionally independent (different categories, no shared code); each task below is a separately completable unit.

**Tech Stack:** Markdown (`SKILL.md` frontmatter + docs), Python 3 stdlib (`urllib`, `http.cookiejar`, `argparse`, `json`) for helper scripts, `feedparser` (new pip dependency, RSS only). Two skills (Bilibili, V2EX) need no helper script — they document CLI/curl commands directly, matching the `xitter` skill's pattern of not vendoring an implementation.

**Testing approach — deviation from strict TDD:** This codebase has no existing test-suite precedent for skill helper scripts (verified: no test file references `youtube-content` or `fetch_transcript`, the closest analog). Per the design spec's own Testing/Verification section, verification here is manual CLI invocation against real upstream services, not `pytest`. Each task's steps include a concrete manual verification command and expected output instead of a `pytest` step. This matches established codebase convention (skills are markdown + thin script content, not `tools/`-level application code) — see `superpowers:writing-plans`' own guidance to follow existing patterns rather than unilaterally introducing a new one.

**Spec:** `docs/superpowers/specs/2026-08-09-agent-reach-skills-design.md`

---

### Task 1: RSS reader skill (`skills/feeds/rss-reader/`)

**Files:**
- Create: `skills/feeds/rss-reader/scripts/fetch_feed.py`
- Create: `skills/feeds/rss-reader/SKILL.md`

- [ ] **Step 1: Create the scripts directory and write the helper script**

```bash
mkdir -p skills/feeds/rss-reader/scripts
```

Write `skills/feeds/rss-reader/scripts/fetch_feed.py`:

```python
#!/usr/bin/env python3
"""
Fetch a single RSS/Atom feed URL and output its entries as structured JSON.

Usage:
    python fetch_feed.py <feed_url> [--limit N] [--text-only]

Install dependency:  pip install feedparser
"""

import argparse
import json
import sys


def fetch_feed(url: str, limit: int = 10) -> dict:
    """Fetch and parse a feed URL, returning structured feed + entries data."""
    try:
        import feedparser
    except ImportError:
        print("Error: feedparser not installed. Run: pip install feedparser", file=sys.stderr)
        sys.exit(1)

    parsed = feedparser.parse(url)

    if parsed.bozo and not parsed.entries:
        message = str(parsed.get("bozo_exception", "unknown parse error"))
        print(f"Error: could not parse feed at {url}: {message}", file=sys.stderr)
        sys.exit(1)

    feed_info = parsed.get("feed", {})
    entries = []
    for entry in parsed.entries[:limit]:
        entries.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", entry.get("updated", "")),
            "summary": entry.get("summary", "")[:500],
        })

    return {
        "feed_title": feed_info.get("title", ""),
        "feed_link": feed_info.get("link", url),
        "entries": entries,
    }


def format_text(data: dict) -> str:
    """Render feed data as plain text for quick reading."""
    lines = [f"{data['feed_title']} ({data['feed_link']})", ""]
    for entry in data["entries"]:
        lines.append(f"- {entry['title']}")
        lines.append(f"  {entry['link']}")
        if entry["published"]:
            lines.append(f"  Published: {entry['published']}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch and parse an RSS/Atom feed URL")
    parser.add_argument("url", help="Feed URL to fetch")
    parser.add_argument("--limit", type=int, default=10, help="Max entries to return (default: 10)")
    parser.add_argument("--text-only", action="store_true", help="Output plain text instead of JSON")
    args = parser.parse_args()

    data = fetch_feed(args.url, limit=args.limit)

    if args.text_only:
        print(format_text(data))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Manually verify the script against a real public feed**

```bash
pip install feedparser
python3 skills/feeds/rss-reader/scripts/fetch_feed.py "https://xkcd.com/atom.xml" --limit 3
```

Expected: valid JSON printed to stdout with `feed_title` containing "xkcd", and an `entries` array with 3 items each having non-empty `title` and `link`.

Also verify text mode:

```bash
python3 skills/feeds/rss-reader/scripts/fetch_feed.py "https://xkcd.com/atom.xml" --limit 2 --text-only
```

Expected: human-readable text output, not JSON.

- [ ] **Step 3: Write the SKILL.md**

Write `skills/feeds/rss-reader/SKILL.md`:

```markdown
---
name: rss-reader
description: Fetch and read the contents of a single RSS/Atom feed URL on demand — titles, links, publish dates, and summaries for its most recent entries. Use for one-off "what's new on this feed" requests. For ongoing tracked subscriptions across many blogs with read/unread state, use the blogwatcher skill instead.
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  commands: [python3]
  python_packages: [feedparser]
metadata:
  hermes:
    tags: [rss, atom, feeds, syndication]
    homepage: https://github.com/kurtmckee/feedparser
---

# RSS Reader — one-shot feed fetch

Fetch a single RSS/Atom feed URL and return its entries as structured data. This skill is for one-off reads — "what's new on this feed", "summarize the latest posts from this blog" — not for ongoing subscription tracking.

## When to use this vs. blogwatcher

- **Use this skill (`rss-reader`)** for a single ad-hoc feed URL the user just gave you, with no setup and no state to maintain.
- **Use the `blogwatcher` skill** (`skills/research/blogwatcher/SKILL.md`) instead when the user wants to track multiple blogs over time, get notified of new posts across scans, or manage read/unread status. `blogwatcher` requires installing a separate Go binary and maintains a SQLite database — worthwhile for durable monitoring, unnecessary overhead for a single one-off fetch.

## Install

\`\`\`bash
pip install feedparser
\`\`\`

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file.

\`\`\`bash
# JSON output (default) — latest 10 entries
python3 SKILL_DIR/scripts/fetch_feed.py "https://example.com/feed.xml"

# Limit entry count
python3 SKILL_DIR/scripts/fetch_feed.py "https://example.com/feed.xml" --limit 5

# Plain text output (good for quick reading, not further JSON processing)
python3 SKILL_DIR/scripts/fetch_feed.py "https://example.com/feed.xml" --text-only
\`\`\`

### Output (JSON mode)

\`\`\`json
{
  "feed_title": "Example Blog",
  "feed_link": "https://example.com",
  "entries": [
    {
      "title": "Post Title",
      "link": "https://example.com/post-1",
      "published": "2026-08-01T12:00:00Z",
      "summary": "First few hundred characters of the post..."
    }
  ]
}
\`\`\`

## Workflow

1. Run the helper script against the feed URL the user gave you.
2. If the URL is a blog homepage rather than a direct feed URL, try common suffixes first: `/feed`, `/rss`, `/atom.xml`, `/feed.xml`, `/rss.xml`. If none work, tell the user you need the direct feed URL, or use Hermes's `web_extract_tool` to read the page and look for a `<link rel="alternate" type="application/rss+xml">` tag.
3. Present entries in the format the user asked for (list, summary, table). If they didn't specify, default to a simple list of title + link + date.
4. For full article content (feeds often only include summaries), follow up with Hermes's `web_extract_tool` on individual entry links.

## Error Handling

- **Empty entries list**: the URL may not be a valid feed. Verify by checking the raw response starts with `<?xml` or `<rss` or `<feed`.
- **`feedparser` not installed**: run `pip install feedparser` and retry.
- **Malformed feed**: `feedparser` is lenient and will parse most broken XML; if it still returns nothing useful, fall back to `web_extract_tool` on the page directly.

## Notes

- This skill maintains no state between calls — every invocation re-fetches the feed from scratch. That's the point: zero setup, but no memory of what you've already seen. For that, use `blogwatcher`.
```

- [ ] **Step 4: Commit**

```bash
git add skills/feeds/rss-reader/
git commit -m "feat: add rss-reader skill for one-shot RSS/Atom feed reads"
```

---

### Task 2: Bilibili skill (`skills/social-media/bilibili/`)

**Files:**
- Create: `skills/social-media/bilibili/SKILL.md`

- [ ] **Step 1: Write the SKILL.md**

Write `skills/social-media/bilibili/SKILL.md`:

```markdown
---
name: bilibili
description: Search Bilibili and read video details, subtitles (where public), hot/trending lists, and user info via the bili-cli terminal client. No login required for these read-only operations. Use for "what's this Bilibili video about", "search Bilibili for X", "what's trending on Bilibili" requests.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [bili]
metadata:
  hermes:
    tags: [bilibili, video, china, search]
    homepage: https://github.com/jackwener/bilibili-cli
---

# Bilibili — search and read via bili-cli

Use `bili` (from `bilibili-cli`) for no-login Bilibili search, video details, subtitles where public, trending/ranking lists, and user profiles.

This skill intentionally does not vendor a separate implementation. Install and use upstream `bili-cli` instead.

## Scope

This skill covers **read-only, no-login operations only**:
- Search videos and users
- Video details, subtitles (where available without login), related videos
- Trending (`hot`) and site-wide ranking (`rank`)
- User profile and video list lookup

**Out of scope** (require an authenticated session, not usable on a headless server):
- `bili login` — interactive QR-code login
- Write actions: `like`, `coin`, `triple`, `dynamic-post`, `dynamic-delete`, `unfollow`
- Personal feed/collections requiring login: `feed`, `my-dynamics`, `favorites`, `following`, `watch-later`, `history`

If a user asks for any of the above, tell them it requires an authenticated session that this headless deployment doesn't support.

## Install

\`\`\`bash
uv tool install bilibili-cli
# or
pipx install bilibili-cli
\`\`\`

Upgrade later with:

\`\`\`bash
uv tool upgrade bilibili-cli
\`\`\`

Verify:

\`\`\`bash
bili --help
\`\`\`

## No-Login Verification

`bilibili-cli` auto-detects local browser cookies for its default auth mode. On a fresh headless machine with no browser profile and no `~/.bilibili-cli/credential.json`, confirm the read-only commands below still work — they're documented upstream as not requiring login, but verify directly since auth auto-detection is the library's default path:

\`\`\`bash
bili status        # expect: reports "not logged in", but the command itself succeeds
bili search "测试" --type video --max 3
\`\`\`

If `bili status` errors out entirely (rather than just reporting "not logged in"), something about the environment is wrong — check `bili --help` and the upstream README.

## Common Commands

### Search

\`\`\`bash
bili search "关键词"                     # Search users
bili search "关键词" --type video --max 5 # Search videos (top 5)
bili search "关键词" --page 2
\`\`\`

### Video Details

\`\`\`bash
bili video BV1ABcsztEcY                            # Video details
bili video BV1ABcsztEcY --subtitle                  # With subtitles (plain text, if public)
bili video BV1ABcsztEcY --subtitle-timeline         # With timeline
bili video BV1ABcsztEcY -st --subtitle-format srt   # Export as SRT
bili video BV1ABcsztEcY --ai                        # AI summary
bili video BV1ABcsztEcY --comments                  # Top comments
bili video BV1ABcsztEcY --related                   # Related videos
bili video BV1ABcsztEcY --json                      # Structured JSON output
\`\`\`

### Discovery

\`\`\`bash
bili hot                     # Trending videos (page 1)
bili hot --page 2 --max 10
bili rank                    # Site-wide ranking (3-day)
bili rank --day 7 --max 30
\`\`\`

### Users

\`\`\`bash
bili user 946974             # UP profile by UID
bili user "影视飓风"           # Search by name
bili user-videos 946974 --max 20
\`\`\`

## Output Modes

Non-TTY stdout defaults to YAML automatically; use `--json` for strict JSON parsing, `--yaml` explicitly if preferred. Use `--max` to cap result counts.

## Fallback: Search API Only (no bili-cli installed)

If `bili` isn't installed and can't be, Bilibili's public search API is reachable directly via curl for **search only** (no video details, no subtitles). Requires a browser `User-Agent` header — Bilibili's risk control 412-blocks requests without one:

\`\`\`bash
curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \\
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=%E5%85%B3%E9%94%AE%E8%AF%8D&page=1"
\`\`\`

A `code: 0` in the JSON response means success. This is a fallback only — prefer `bili-cli` for anything beyond search, since it also covers video details and subtitles.

## Pitfalls

- **yt-dlp does not work for Bilibili**: Bilibili's risk control 412-blocks yt-dlp in every configuration (live-verified 2026-06). Don't fall back to yt-dlp for Bilibili; use `bili-cli` or the search-API fallback above. (yt-dlp remains correct for YouTube.)
- **Subtitles may be missing**: not all videos have public subtitles; `--subtitle` will come back empty in that case, not error.
- **`bili-cli` upstream update cadence**: if commands stop matching this doc, check `bili --help` and https://github.com/jackwener/bilibili-cli for changes.

## Notes

- Prefer `--json` when extracting fields for further processing.
- Use BV IDs (e.g. `BV1ABcsztEcY`) or full video URLs interchangeably where the upstream tool supports it — check `bili video --help` if a raw URL doesn't parse.
```

- [ ] **Step 2: Manually verify against the real bili-cli (if installable in this environment)**

```bash
uv tool install bilibili-cli
bili --help
bili status
bili search "python" --type video --max 3
```

Expected: `bili --help` prints usage; `bili status` succeeds (reports not-logged-in, doesn't error); `bili search` returns at least one result without requiring login.

If `bili-cli` cannot be installed in the current environment (e.g. no `uv`/`pipx` available), verify the curl fallback instead:

```bash
curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=python&page=1" | head -c 300
```

Expected: JSON response containing `"code":0`.

- [ ] **Step 3: Commit**

```bash
git add skills/social-media/bilibili/
git commit -m "feat: add bilibili skill for no-login search and video reads"
```

---

### Task 3: V2EX skill (`skills/social-media/v2ex/`)

**Files:**
- Create: `skills/social-media/v2ex/SKILL.md`

- [ ] **Step 1: Write the SKILL.md**

Write `skills/social-media/v2ex/SKILL.md`:

```markdown
---
name: v2ex
description: Read V2EX (a Chinese tech community forum) — hot topics, node-specific topics, topic details with replies, and user profiles, via V2EX's public JSON API. Zero setup, no auth, no CLI tool required. Use for "what's trending on V2EX", "read this V2EX topic", "look up this V2EX user" requests.
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  commands: [curl]
metadata:
  hermes:
    tags: [v2ex, forum, china, community]
    homepage: https://www.v2ex.com/help/api
---

# V2EX — public API reads

V2EX exposes a public, unauthenticated JSON API. No CLI tool, no credentials, no setup — just HTTPS GET requests.

## Endpoints

Base URL: `https://www.v2ex.com`

### Hot topics

\`\`\`bash
curl -s "https://www.v2ex.com/api/topics/hot.json"
\`\`\`

Returns an array of topic objects: `id`, `title`, `url`, `replies`, `node` (with `name`/`title`), `content`, `created`.

### Node topics

Latest topics in a specific node (e.g. `python`, `tech`, `jobs`, `qna`):

\`\`\`bash
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1"
\`\`\`

### Topic detail + replies

\`\`\`bash
# Topic detail (id is from the topic URL, e.g. v2ex.com/t/123456 -> id=123456)
curl -s "https://www.v2ex.com/api/topics/show.json?id=123456"

# Replies (paginated)
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=123456&page=1"
\`\`\`

Note: `topics/show.json?id=X` returns a JSON array (even for a single ID) — take the first element.

### User lookup

\`\`\`bash
curl -s "https://www.v2ex.com/api/members/show.json?username=someuser"
\`\`\`

## Search

**V2EX's public API has no full-text search endpoint.** For search requests, use one of:

- Hermes's existing `web_search_tool` (Exa) with a `site:v2ex.com` query, e.g. search for `"site:v2ex.com <query>"`.
- Direct browse: `https://www.v2ex.com/?q=<query>` via `web_extract_tool` (unstructured HTML, no JSON).

Don't try to guess a `/api/search.json` endpoint — it doesn't exist.

## Workflow

1. For "what's trending/hot on V2EX" — call the hot topics endpoint.
2. For "what's new in node X" — call the node topics endpoint with that node name.
3. For a specific topic URL — extract the numeric ID from the URL path (`v2ex.com/t/<id>`) and call topic detail + replies.
4. For a user profile URL — extract the username from the URL path (`v2ex.com/member/<username>`) and call the user lookup endpoint.
5. For anything search-like — redirect to `web_search_tool` with `site:v2ex.com`, per above.

## Error Handling

- **Connection failure**: V2EX may be geo-restricted or rate-limiting; note this to the user rather than retrying in a loop.
- **Empty array from node topics**: the node name may be wrong — node names are lowercase slugs (e.g. `python`, not `Python`), visible in a topic's `node.name` field from the hot-topics response.

## Notes

- All responses are plain JSON — no auth headers, no rate-limit key required for these read endpoints.
- If V2EX ever requires TLS negotiation quirks that Python's `urllib`/`requests` can't handle (rare), retry the same URL via `curl` directly — curl uses the OS TLS stack which can succeed where a bundled TLS stack fails.
```

- [ ] **Step 2: Manually verify against the real V2EX API**

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" | head -c 300
echo
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" | head -c 300
```

Expected: both print valid JSON arrays with `title`/`url`/`node` fields visible in the first few entries.

- [ ] **Step 3: Commit**

```bash
git add skills/social-media/v2ex/
git commit -m "feat: add v2ex skill for public API reads"
```

---

### Task 4: Xueqiu skill (`skills/research/xueqiu/`)

**Files:**
- Create: `skills/research/xueqiu/scripts/xueqiu_api.py`
- Create: `skills/research/xueqiu/SKILL.md`

- [ ] **Step 1: Create the scripts directory and write the helper script**

```bash
mkdir -p skills/research/xueqiu/scripts
```

Write `skills/research/xueqiu/scripts/xueqiu_api.py`:

```python
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
```

- [ ] **Step 2: Manually verify the script cold (no prior cookie state), against real Xueqiu endpoints**

```bash
python3 skills/research/xueqiu/scripts/xueqiu_api.py quote SH600519
```

Expected: JSON with `"symbol": "SH600519"`, `"name"` containing "贵州茅台" (Kweichow Moutai), and non-null `current`/`percent` fields. This confirms the two-step cookie warm-up works from a completely cold process.

```bash
python3 skills/research/xueqiu/scripts/xueqiu_api.py search "茅台"
python3 skills/research/xueqiu/scripts/xueqiu_api.py hot-posts --limit 5
python3 skills/research/xueqiu/scripts/xueqiu_api.py hot-stocks --limit 5
```

Expected: each prints a non-empty JSON array.

- [ ] **Step 3: Write the SKILL.md**

Write `skills/research/xueqiu/SKILL.md`:

```markdown
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

\`\`\`bash
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
\`\`\`

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
```

- [ ] **Step 4: Commit**

```bash
git add skills/research/xueqiu/
git commit -m "feat: add xueqiu skill for stock quotes and community data"
```

---

### Task 5: Twitter-free skill (`skills/social-media/twitter-free/`)

**Files:**
- Create: `skills/social-media/twitter-free/SKILL.md`

- [ ] **Step 1: Write the SKILL.md**

Write `skills/social-media/twitter-free/SKILL.md`:

```markdown
---
name: twitter-free
description: Free, cookie-based alternative for reading Twitter/X (feed, search, tweets, user lookups, bookmarks) via twitter-cli, for when official paid X API access (see the xitter skill) isn't available. Requires manually exported browser cookies from a secondary/burner X account due to ban risk.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
prerequisites:
  commands: [uv]
  env_vars: [TWITTER_AUTH_TOKEN, TWITTER_CT0]
metadata:
  hermes:
    tags: [twitter, x, social-media, twitter-cli, free]
    homepage: https://github.com/jackwener/twitter-cli
---

# Twitter-Free — cookie-based X/Twitter reading via twitter-cli

⚠️ **Ban-risk warning: use a burner/secondary X account, not your primary one.** Cookie-based automated access is against X's terms of service and can trigger account detection and suspension. This is the trade-off for avoiding X's paid official API (see the `xitter` skill for that path). If the user hasn't set up a dedicated account for this, ask them to before proceeding.

This skill is an **alternative to `xitter`**, not a replacement — `xitter` (official paid API) stays the preferred path for anyone who has it configured. Use this skill when the user explicitly wants a free option and accepts the ban risk.

## Install

\`\`\`bash
uv tool install twitter-cli
# or
pipx install twitter-cli
\`\`\`

Verify (does not make an authenticated request):

\`\`\`bash
twitter --help
\`\`\`

## Credentials

Twitter-cli auth is entirely cookie-based via two environment variables:

\`\`\`bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
\`\`\`

### Getting the cookie values

1. Install the [Cookie-Editor](https://cookie-editor.com/) browser extension.
2. Log into x.com **on the burner/secondary account**.
3. Click Cookie-Editor → Export → Header String (or find `auth_token` and `ct0` individually in the cookie list).
4. Set both as environment variables in the shell/session this skill runs in — `TWITTER_AUTH_TOKEN` from `auth_token`, `TWITTER_CT0` from `ct0`.

**Do not** attempt to auto-extract these from a browser profile — export manually via Cookie-Editor only. Twitter-cli itself does not read this skill's config; the two env vars must be present in whatever process actually runs `twitter`.

## Quick Verification

\`\`\`bash
twitter search "test" -n 1
\`\`\`

If this returns a result, credentials are working.

## Common Commands

### Feed

\`\`\`bash
twitter feed                    # For You timeline
twitter feed -t following       # Following timeline
twitter feed --max 50
\`\`\`

### Search

\`\`\`bash
twitter search "Claude Code"
twitter search "AI agent" -t Latest --max 50
twitter search "python" --from elonmusk --lang en --since 2026-01-01
twitter search --from bbc --exclude retweets --has links
\`\`\`

### Tweet detail

\`\`\`bash
twitter tweet 1234567890
twitter tweet https://x.com/user/status/1234567890
twitter tweet 1234567890 --full-text
\`\`\`

### User

\`\`\`bash
twitter user elonmusk
twitter user-posts elonmusk --max 20
twitter followers elonmusk --max 50
\`\`\`

### Bookmarks

\`\`\`bash
twitter bookmarks
twitter bookmarks --max 30 --yaml
\`\`\`

## Output Modes

Non-TTY stdout defaults to YAML automatically. Use `--json` when the agent needs strict JSON, `--full-text` to disable truncation in table output.

## Troubleshooting

- **226 "automated behavior" error on ANY command, including reads**: this can happen even with correctly-set `TWITTER_AUTH_TOKEN`/`TWITTER_CT0` — it's not limited to write actions. If it happens, wait before retrying (don't hammer retries, that makes detection more likely) and consider whether the account has been flagged. This is a real risk of the cookie-based approach, not a bug in this skill.
- **Missing credentials**: if `twitter` falls back to trying to read browser cookies automatically when explicit env vars are absent/invalid, that's upstream behavior this skill does not rely on or endorse — always set both env vars explicitly per above.
- **Rate limits**: cookie-based access has tighter, less predictable limits than the official API. Space out requests.

## Notes

- Read-focused: this skill emphasizes read commands. Write actions (`post`, `delete`, `like`, `retweet`) exist upstream but carry higher ban risk when used with a burner account's cookies — confirm explicitly with the user before using them.
- If credentials rotate (burner account re-login), re-export via Cookie-Editor and update both env vars.
```

- [ ] **Step 2: Manual verification (requires a burner account — user-side step)**

This step cannot be completed by an automated worker without real burner-account credentials. Document this clearly rather than skipping verification silently:

```bash
uv tool install twitter-cli
twitter --help
```

Expected: install succeeds, `--help` prints usage without requiring credentials.

Full read verification (`twitter search "test" -n 1`) requires `TWITTER_AUTH_TOKEN`/`TWITTER_CT0` from a real burner account's exported cookies — flag this to the user as a manual follow-up step they need to perform themselves, since it requires their own X account and Cookie-Editor export.

- [ ] **Step 3: Commit**

```bash
git add skills/social-media/twitter-free/
git commit -m "feat: add twitter-free skill for cookie-based X reading"
```

---

### Task 6: Push to fork

**Files:** None (git operation only)

- [ ] **Step 1: Verify all five commits are present**

```bash
git log --oneline -6
```

Expected: 5 feature commits (rss-reader, bilibili, v2ex, xueqiu, twitter-free) on top of the prior history.

- [ ] **Step 2: Push**

```bash
git push fork main
```

Expected: push succeeds, fast-forward, no conflicts.

---

## Post-Plan Notes

- **Deployment to the live Hetzner instance is explicitly out of scope** (per the spec's Non-goals) — this plan only changes the git repo. Deploying to `37.27.9.144` (`git pull` + `sudo systemctl restart hermes`) is a separate, later step if/when desired.
- **`skills/research/ml-paper-writing` and `skills/software-development/code-review`** were found to be empty directories during the repo-corruption recovery earlier in this session — unrelated to this plan, but worth noting to the user at some point since they're currently dead weight in the repo (not addressed here — out of scope for this plan).
