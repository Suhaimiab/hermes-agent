# Design: Agent-Reach-inspired headless capability skills

**Date:** 2026-08-09
**Status:** Approved for planning

## Summary

Add five new Hermes skills, modeled on the platform selections documented in
[Agent-Reach](https://github.com/Panniantong/Agent-Reach), that give Hermes
read access to RSS/Atom feeds, Bilibili, V2EX, Xueqiu (雪球), and a free
cookie-based Twitter/X alternative. Skills are native to Hermes (no
dependency on the `agent-reach` Python package itself) and follow the
existing `SKILL.md` convention already used by `skills/social-media/xitter`
and `skills/media/youtube-content`.

## Background

Agent-Reach is a capability layer that installs and routes between
upstream CLIs per platform for shell-capable agents. Reviewing it against
Hermes's current codebase surfaced:

- Hermes already has native `web_search_tool`/`web_extract_tool`
  (Exa/Tavily/Firecrawl/Parallel backends) and a full GitHub skill set
  (`skills/github/*`), and a transcript-only YouTube skill
  (`skills/media/youtube-content`). Agent-Reach's web-reading, GitHub, and
  YouTube-transcript channels are therefore redundant and out of scope.
- Agent-Reach's Reddit/Facebook/Instagram/XiaoHongShu channels depend on
  OpenCLI reusing a **desktop Chrome login session**. Hermes's production
  deployment is a headless Hetzner VPS (`37.27.9.144`, systemd unit
  `hermes.service`) with no desktop browser session available, so these
  channels cannot function there and are excluded from this design.
- The remaining channels — RSS, Bilibili, V2EX, Xueqiu, and a free-tier
  Twitter path — work headless (pure HTTP/CLI, no interactive browser
  login) and fill real gaps: `skills/feeds/` is currently an empty
  placeholder category, and Bilibili/V2EX/Xueqiu have no existing skill.
- Skill discovery in Hermes is filesystem-based (`tools/skills_hub.py`
  scans for `SKILL.md` under `skills/<category>/<name>/`), so no registry
  or manifest needs to be updated — adding a directory is sufficient.

## Decisions from brainstorming

1. **Platform scope:** headless-compatible platforms only (RSS, Bilibili,
   V2EX, Xueqiu, free-tier Twitter). Reddit/Facebook/Instagram/XiaoHongShu
   explicitly excluded.
2. **Install target:** commit to the Hermes git repo under `skills/`, not
   a live-instance-only deploy.
3. **Implementation style:** native Hermes-owned `SKILL.md` files that
   install/call upstream CLIs or APIs directly. No dependency on the
   `agent-reach` pip package or its routing/doctor layer.
4. **Twitter/X handling:** add a new free/cookie-based skill alongside the
   existing paid-API `xitter` skill (not a replacement). Existing `xitter`
   is untouched.

## New skills

### 1. `skills/feeds/rss-reader/SKILL.md`

- Fills the currently-empty `feeds/` category.
- Dependency: `pip install feedparser` (pure Python library, zero
  external CLI, zero config, no API key).
- Ships `scripts/fetch_feed.py`: takes a feed URL, returns structured
  JSON (`title`, `link`, `published`, `summary` per entry), following the
  same helper-script pattern as `skills/media/youtube-content/scripts/fetch_transcript.py`.
- Covers: reading an arbitrary RSS/Atom URL, filtering entries by
  recency, extracting entry links for follow-up reads via Hermes's
  existing `web_extract_tool`.

### 2. `skills/social-media/bilibili/SKILL.md`

- Primary backend: `bili` CLI from
  [`bilibili-cli`](https://github.com/jackwener/bilibili-cli)
  (`uv tool install bilibili-cli` / `pipx install bilibili-cli`).
  No-login commands only: `bili video <BV>` (details, `--subtitle` where
  public), `bili search`, `bili hot`, `bili rank`, `bili user`,
  `bili user-videos`.
- Fallback (if `bili` isn't installed): direct curl to Bilibili's public
  search API (`https://api.bilibili.com/x/web-interface/search/all/v2`),
  search-only, requires a browser `User-Agent` header to avoid a 412
  block (per Agent-Reach's live-verified note that Bilibili's risk
  control blocks default/undeclared clients).
- Explicitly out of scope: `bili login` (interactive QR code — can't run
  headless) and write actions (`like`, `coin`, `dynamic-post`, etc.),
  which require an authenticated session.

### 3. `skills/social-media/v2ex/SKILL.md`

- Pure public JSON API over HTTPS
  (`https://www.v2ex.com/api/{topics,replies,members}/...`). No CLI, no
  auth, no dependency beyond `curl`.
- Covers: hot topics (`/api/topics/hot.json`), node topics
  (`/api/topics/show.json?node_name=X`), topic detail + replies
  (`/api/topics/show.json?id=X` + `/api/replies/show.json?topic_id=X`),
  user lookup (`/api/members/show.json?username=X`).
- No full-text search endpoint exists on V2EX's public API — SKILL.md
  documents falling back to Hermes's existing `web_search_tool` (Exa)
  with a `site:v2ex.com` query.

### 4. `skills/research/xueqiu/SKILL.md`

- Fits `research/`'s existing "market data" scope in its
  `DESCRIPTION.md`.
- Quote/search/hot-posts/hot-stocks work without a logged-in account, but
  require a warmed anti-bot session cookie: one GET to `https://xueqiu.com`
  first, cookie jar carried into the subsequent API call. A single
  stateless curl will not work.
- Ships `scripts/xueqiu_api.py`: stdlib `urllib` + `http.cookiejar` only
  (no new dependency), handling the two-step cookie warm-up and exposing
  `quote <symbol>`, `search <query>`, `hot-posts`, `hot-stocks`
  subcommands with JSON output.
- Covers Chinese A-share (`SH`/`SZ` prefix), Hong Kong, and US symbols
  (e.g. `SH600519`, `00700`, `AAPL`), per the upstream API's symbol format.

### 5. `skills/social-media/twitter-free/SKILL.md`

- Alternative to (not a replacement for) the existing `xitter` skill.
  `xitter` stays as-is for anyone with paid official X API access.
- Backend: `twitter-cli` (`uv tool install twitter-cli` /
  `pipx install twitter-cli`), cookie-based via `TWITTER_AUTH_TOKEN` and
  `TWITTER_CT0` environment variables.
- Credential acquisition is manual and explicit: install the
  Cookie-Editor browser extension, log into x.com, export cookies, set
  the two env vars. No automated browser-cookie extraction — matches
  Agent-Reach's own policy of never silently reading browser credential
  stores.
- **Leads with a ban-risk warning**: recommend a burner/secondary X
  account, not the user's primary, since cookie-based automated access
  can trigger platform detection.
- Covers: `twitter feed`, `twitter search`, `twitter tweet <id>`,
  `twitter user <handle>`, `twitter user-posts <handle>`,
  `twitter bookmarks`. Write actions (post/delete/like/retweet) are
  documented as available upstream but not emphasized, consistent with
  this skill's read-focused purpose.

## Non-goals

- No changes to `skills/social-media/xitter` or `skills/github/*`.
- No YouTube search capability (only transcripts, already covered by
  `youtube-content`) — Agent-Reach's YouTube search is a minor add and
  not worth the scope for this pass.
- No Reddit/Facebook/Instagram/XiaoHongShu skills (desktop-session-only,
  incompatible with the headless VPS deployment).
- No dependency on the `agent-reach` pip package itself, its
  `~/.agent-reach/` config directory, or its `doctor`/routing CLI.
- No deployment to the live Hetzner instance as part of this work — this
  is a repo change; deploying is a separate, later step (`git pull` +
  restart on the box) if/when desired.

## Testing / verification

Each skill is a `SKILL.md` (+ optional `scripts/`) — there's no Python
application code under `tools/` to unit test. Verification is manual, per
skill, after install:

- RSS: fetch a known-good public feed (e.g. an active blog's `/feed`)
  and confirm structured entries come back.
- Bilibili: `bili search "关键词"` and `bili video <a known BV id>`
  without any login; confirm the curl fallback path separately by
  temporarily renaming/hiding `bili` from `PATH`.
- V2EX: `curl` the hot-topics and a node-topics endpoint, confirm valid
  JSON with expected keys.
- Xueqiu: run `scripts/xueqiu_api.py quote SH600519` cold (no prior
  cookie state) and confirm it succeeds via the two-step warm-up.
- Twitter-free: with a burner account's exported cookies set as env
  vars, run `twitter search "test" -n 1` and confirm a result.

No changes to existing test suites (`tests/`) are required since this
adds skill content, not Python source under `tools/`/`agent/`/`gateway/`.
