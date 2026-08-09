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

```bash
uv tool install bilibili-cli
# or
pipx install bilibili-cli
```

Upgrade later with:

```bash
uv tool upgrade bilibili-cli
```

Verify:

```bash
bili --help
```

## No-Login Verification

`bilibili-cli` auto-detects local browser cookies for its default auth mode. On a fresh headless machine with no browser profile and no `~/.bilibili-cli/credential.json`, confirm the read-only commands below still work — they're documented upstream as not requiring login, but verify directly since auth auto-detection is the library's default path:

```bash
bili status        # expect: reports "not logged in", but the command itself succeeds
bili search "测试" --type video --max 3
```

If `bili status` errors out entirely (rather than just reporting "not logged in"), something about the environment is wrong — check `bili --help` and the upstream README.

## Common Commands

### Search

```bash
bili search "关键词"                     # Search users
bili search "关键词" --type video --max 5 # Search videos (top 5)
bili search "关键词" --page 2
```

### Video Details

```bash
bili video BV1ABcsztEcY                            # Video details
bili video BV1ABcsztEcY --subtitle                  # With subtitles (plain text, if public)
bili video BV1ABcsztEcY --subtitle-timeline         # With timeline
bili video BV1ABcsztEcY -st --subtitle-format srt   # Export as SRT
bili video BV1ABcsztEcY --ai                        # AI summary
bili video BV1ABcsztEcY --comments                  # Top comments
bili video BV1ABcsztEcY --related                   # Related videos
bili video BV1ABcsztEcY --json                      # Structured JSON output
```

### Discovery

```bash
bili hot                     # Trending videos (page 1)
bili hot --page 2 --max 10
bili rank                    # Site-wide ranking (3-day)
bili rank --day 7 --max 30
```

### Users

```bash
bili user 946974             # UP profile by UID
bili user "影视飓风"           # Search by name
bili user-videos 946974 --max 20
```

## Output Modes

Non-TTY stdout defaults to YAML automatically; use `--json` for strict JSON parsing, `--yaml` explicitly if preferred. Use `--max` to cap result counts.

## Fallback: Search API Only (no bili-cli installed)

If `bili` isn't installed and can't be, Bilibili's public search API is reachable directly via curl for **search only** (no video details, no subtitles). Requires a browser `User-Agent` header — Bilibili's risk control 412-blocks requests without one:

```bash
curl -s --max-time 10 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=%E5%85%B3%E9%94%AE%E8%AF%8D&page=1"
```

A `code: 0` in the JSON response means success. This is a fallback only — prefer `bili-cli` for anything beyond search, since it also covers video details and subtitles.

## Pitfalls

- **yt-dlp does not work for Bilibili**: Bilibili's risk control 412-blocks yt-dlp in every configuration (live-verified 2026-06). Don't fall back to yt-dlp for Bilibili; use `bili-cli` or the search-API fallback above. (yt-dlp remains correct for YouTube.)
- **Subtitles may be missing**: not all videos have public subtitles; `--subtitle` will come back empty in that case, not error.
- **`bili-cli` upstream update cadence**: if commands stop matching this doc, check `bili --help` and https://github.com/jackwener/bilibili-cli for changes.

## Notes

- Prefer `--json` when extracting fields for further processing.
- Use BV IDs (e.g. `BV1ABcsztEcY`) or full video URLs interchangeably where the upstream tool supports it — check `bili video --help` if a raw URL doesn't parse.
