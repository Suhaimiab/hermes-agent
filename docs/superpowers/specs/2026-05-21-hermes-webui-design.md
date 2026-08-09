# Design: Hermes Web UI Deployment (nesquena/hermes-webui)

**Date:** 2026-05-21  
**Status:** Approved  

---

## Problem

Hermes is currently only accessible via CLI and the Telegram `/sindbad` command. There is no browser-based interface for chatting with the agent, managing sessions, or monitoring jobs. ChatBox (previously trialled) had streaming/rendering incompatibilities.

## Goal

Deploy a stable, self-hosted web UI for Hermes on the existing Hetzner VPS (`37.27.9.144`), accessible over HTTPS via the existing Cloudflare tunnel.

---

## Solution: nesquena/hermes-webui via systemd

**Chosen project:** [nesquena/hermes-webui](https://github.com/nesquena/hermes-webui)  
**Why:** 8.1k stars, 426 releases, MIT license, Python-based (same stack as Hermes), connects directly to the Hermes agent installation via auto-discovered agent directory rather than going through the OpenAI API layer.

**Deployment method:** systemd service — consistent with how `hermes.service` and the webhook service are already managed on this box.

---

## Architecture

```
Browser (HTTPS)
     │
     ▼
Cloudflare Tunnel  (new ingress rule → localhost:8787)
     │
     ▼
hermes-webui.service  (port 8787, bound to 0.0.0.0)
     │   ↑ ufw blocks 8787 from public internet (applied BEFORE service starts)
     ▼  direct process integration via HERMES_WEBUI_AGENT_DIR
hermes-agent installation  (/home/ubuntu/hermes)
     │
     ▼
OpenRouter / model providers
```

---

## Implementation Steps

### 1. Clone the repo
```bash
cd /home/ubuntu
git clone https://github.com/nesquena/hermes-webui.git hermes-webui
```

### 2. Install Python dependencies
```bash
cd /home/ubuntu/hermes-webui
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
This installs webui deps into a local `.venv`. At runtime, `start.sh` will prefer the hermes agent's venv (which already has `run_agent.py` on the path) if it includes all webui deps; otherwise it falls back to this `.venv`.

Do **not** run `bootstrap.py` interactively — it would start a detached server process that would then block port 8787 when the systemd service starts.

### 3. Verify port is free
```bash
ss -tlnp | grep 8787
```
If occupied, choose a different port and update Steps 4, 6, and 8 accordingly.

### 4. Block port 8787 from public internet (BEFORE service starts)
```bash
sudo ufw deny 8787
sudo ufw status
```
Port 8787 is bound to `0.0.0.0` so Cloudflare tunnel can reach it via loopback. The firewall ensures no direct public access bypasses the tunnel. Apply this **before** starting the service to avoid any exposure window.

### 5. Create secrets file
```bash
sudo mkdir -p /etc/hermes-webui
sudo chmod 700 /etc/hermes-webui
sudo tee /etc/hermes-webui/env > /dev/null <<'EOF'
HERMES_WEBUI_PASSWORD=<strong-secret-here>
EOF
sudo chmod 600 /etc/hermes-webui/env
```
A separate secrets file prevents the password appearing in world-readable systemd unit output (`systemctl cat`).

### 6. Create systemd service unit
File: `/etc/systemd/system/hermes-webui.service`

```ini
[Unit]
Description=Hermes Web UI
After=network.target
Wants=hermes.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hermes-webui
EnvironmentFile=/etc/hermes-webui/env
Environment=HERMES_WEBUI_HOST=0.0.0.0
Environment=HERMES_WEBUI_PORT=8787
Environment=HERMES_WEBUI_AGENT_DIR=/home/ubuntu/hermes
Environment=HERMES_HOME=/home/ubuntu/.hermes
ExecStart=/bin/bash /home/ubuntu/hermes-webui/start.sh --foreground
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Notes on this unit:**

- `HOME` is **not** overridden — systemd derives it from the `ubuntu` user's passwd entry (`/home/ubuntu`). Setting it to `.hermes` would break `Path.home()` throughout the app.
- `HERMES_HOME` (distinct from `HOME`) tells Hermes where its state lives — correctly set to `/home/ubuntu/.hermes`.
- `Wants=hermes.service` expresses a preference but does not block the WebUI from starting if the agent is down. This allows the UI to show session history when the agent is temporarily offline. Use `After=hermes.service` instead if you want hard ordering.
- `--foreground` causes `start.sh`/`bootstrap.py` to `os.execv` into `server.py` so systemd tracks the long-lived process PID (not the short-lived bootstrap wrapper). This is explicitly documented in `docs/supervisor.md`. Note: systemd also auto-detects foreground mode via `INVOCATION_ID`/`JOURNAL_STREAM`, but the flag makes intent explicit.

### 7. Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable hermes-webui
sudo systemctl start hermes-webui
sudo systemctl status hermes-webui
```

### 8. Add Cloudflare tunnel ingress rule
Edit the tunnel config — find the file with:
```bash
sudo cat /etc/cloudflared/config.yml
# or
ls ~/.cloudflared/
```

Add an ingress entry before the catch-all rule:
```yaml
ingress:
  # ... existing rules ...
  - hostname: webui.yourdomain.com
    service: http://localhost:8787
  - service: http_status:404   # catch-all must remain last
```

Then restart cloudflared:
```bash
sudo systemctl restart cloudflared
```

Also add a DNS record in Cloudflare dashboard: `webui.yourdomain.com` → CNAME → your tunnel's `.cfargotunnel.com` hostname.

### 9. Verify
```bash
# Liveness probe
curl http://localhost:8787/health

# Readiness probe (checks agent integration and session DB)
curl "http://localhost:8787/health?deep=1"

# Check service logs
journalctl -u hermes-webui -f
```

Then open `https://webui.yourdomain.com` in a browser and log in with the configured password.

---

## Configuration Reference

| Variable | Value | Where set |
|---|---|---|
| `HERMES_WEBUI_HOST` | `0.0.0.0` | Unit inline env |
| `HERMES_WEBUI_PORT` | `8787` | Unit inline env |
| `HERMES_WEBUI_AGENT_DIR` | `/home/ubuntu/hermes` | Unit inline env |
| `HERMES_WEBUI_PASSWORD` | strong secret | `/etc/hermes-webui/env` |
| `HERMES_HOME` | `/home/ubuntu/.hermes` | Unit inline env |

---

## Security

- Password auth via `HERMES_WEBUI_PASSWORD` (PBKDF2-SHA256 hashed, HMAC-signed cookie, 24h TTL)
- Password stored in `/etc/hermes-webui/env` (mode 600, root-owned) — not in the unit file
- HTTPS enforced by Cloudflare tunnel (TLS termination at edge)
- Port 8787 blocked from public internet via `ufw deny 8787` — applied before service starts
- Only Cloudflare tunnel (loopback) reaches the port
- Hermes API server (`hermes.service` on port 8880) remains unchanged

---

## Out of Scope

- Modifying nesquena/hermes-webui source code
- Changing existing `hermes.service` configuration
- Exposing raw port 8787 publicly

---

## Success Criteria

- `hermes-webui.service` shows `active (running)` via `systemctl status`
- `curl http://localhost:8787/health` returns `{"status": "ok", ...}`
- `curl "http://localhost:8787/health?deep=1"` returns without error (confirms agent integration)
- Browser loads the web UI over HTTPS via Cloudflare tunnel
- Can send a message to Hermes and receive a streamed response
- Service restarts automatically after a reboot
- `ufw status` shows port 8787 denied for external traffic
