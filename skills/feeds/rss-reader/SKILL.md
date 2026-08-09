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

```bash
pip install feedparser
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file.

```bash
# JSON output (default) — latest 10 entries
python3 SKILL_DIR/scripts/fetch_feed.py "https://example.com/feed.xml"

# Limit entry count
python3 SKILL_DIR/scripts/fetch_feed.py "https://example.com/feed.xml" --limit 5

# Plain text output (good for quick reading, not further JSON processing)
python3 SKILL_DIR/scripts/fetch_feed.py "https://example.com/feed.xml" --text-only
```

### Output (JSON mode)

```json
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
```

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
