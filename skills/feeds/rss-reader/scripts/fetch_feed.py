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
