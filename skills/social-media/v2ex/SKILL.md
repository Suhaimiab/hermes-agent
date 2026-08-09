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

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json"
```

Returns an array of topic objects: `id`, `title`, `url`, `replies`, `node` (with `name`/`title`), `content`, `created`.

### Node topics

Latest topics in a specific node (e.g. `python`, `tech`, `jobs`, `qna`):

```bash
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1"
```

### Topic detail + replies

```bash
# Topic detail (id is from the topic URL, e.g. v2ex.com/t/123456 -> id=123456)
curl -s "https://www.v2ex.com/api/topics/show.json?id=123456"

# Replies (paginated)
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=123456&page=1"
```

Note: `topics/show.json?id=X` returns a JSON array (even for a single ID) — take the first element.

### User lookup

```bash
curl -s "https://www.v2ex.com/api/members/show.json?username=someuser"
```

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
- **API generation note**: the endpoints above (`/api/topics/hot.json`, `/api/topics/show.json`, `/api/replies/show.json`, `/api/members/show.json`) are V2EX's legacy, unauthenticated public JSON endpoints — they are distinct from, and not documented on, the authenticated `/api/v2/` REST API described at the `homepage` link in this skill's frontmatter (which requires a Bearer personal-access-token and returns 401 without one). The legacy endpoints were chosen deliberately to preserve zero-setup, no-auth access; they are undocumented and could be deprecated or change behavior without notice, so if a call starts failing unexpectedly, check whether V2EX has retired them before assuming a bug in this skill — do not "fix" this by migrating to `/api/v2/`, since that reintroduces an auth requirement.
