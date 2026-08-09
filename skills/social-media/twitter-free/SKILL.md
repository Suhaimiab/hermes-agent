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

```bash
uv tool install twitter-cli
# or
pipx install twitter-cli
```

Verify (does not make an authenticated request):

```bash
twitter --help
```

## Credentials

Twitter-cli auth is entirely cookie-based via two environment variables:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

### Getting the cookie values

1. Install the [Cookie-Editor](https://cookie-editor.com/) browser extension.
2. Log into x.com **on the burner/secondary account**.
3. Click Cookie-Editor → Export → Header String (or find `auth_token` and `ct0` individually in the cookie list).
4. Set both as environment variables in the shell/session this skill runs in — `TWITTER_AUTH_TOKEN` from `auth_token`, `TWITTER_CT0` from `ct0`.

**Do not** attempt to auto-extract these from a browser profile — export manually via Cookie-Editor only. Twitter-cli itself does not read this skill's config; the two env vars must be present in whatever process actually runs `twitter`.

## Quick Verification

```bash
twitter search "test" -n 1
```

If this returns a result, credentials are working.

## Common Commands

### Feed

```bash
twitter feed                    # For You timeline
twitter feed -t following       # Following timeline
twitter feed --max 50
```

### Search

```bash
twitter search "Claude Code"
twitter search "AI agent" -t Latest --max 50
twitter search "python" --from elonmusk --lang en --since 2026-01-01
twitter search --from bbc --exclude retweets --has links
```

### Tweet detail

```bash
twitter tweet 1234567890
twitter tweet https://x.com/user/status/1234567890
twitter tweet 1234567890 --full-text
```

### User

```bash
twitter user elonmusk
twitter user-posts elonmusk --max 20
twitter followers elonmusk --max 50
```

### Bookmarks

```bash
twitter bookmarks
twitter bookmarks --max 30 --yaml
```

## Output Modes

Non-TTY stdout defaults to YAML automatically. Use `--json` when the agent needs strict JSON, `--full-text` to disable truncation in table output.

## Troubleshooting

- **226 "automated behavior" error on ANY command, including reads**: this can happen even with correctly-set `TWITTER_AUTH_TOKEN`/`TWITTER_CT0` — it's not limited to write actions. If it happens, wait before retrying (don't hammer retries, that makes detection more likely) and consider whether the account has been flagged. This is a real risk of the cookie-based approach, not a bug in this skill.
- **Missing credentials**: if `twitter` falls back to trying to read browser cookies automatically when explicit env vars are absent/invalid, that's upstream behavior this skill does not rely on or endorse — always set both env vars explicitly per above.
- **Rate limits**: cookie-based access has tighter, less predictable limits than the official API. Space out requests.

## Notes

- Read-focused: this skill emphasizes read commands. Write actions (`post`, `delete`, `like`, `retweet`) exist upstream but carry higher ban risk when used with a burner account's cookies — confirm explicitly with the user before using them.
- If credentials rotate (burner account re-login), re-export via Cookie-Editor and update both env vars.
