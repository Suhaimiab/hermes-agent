# Hermes Web UI Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy nesquena/hermes-webui as a systemd service on the Hetzner VPS, accessible over HTTPS via the existing Cloudflare tunnel.

**Architecture:** Clone the webui repo alongside the existing hermes-agent installation on the Hetzner VPS (`37.27.9.144`). Run it as a systemd service (`hermes-webui.service`) that discovers the Hermes agent directly via `HERMES_WEBUI_AGENT_DIR`. Expose it via an additional Cloudflare tunnel ingress rule — no new infrastructure required.

**Tech Stack:** Python 3 (virtualenv), systemd, ufw, cloudflared (already on box), nesquena/hermes-webui (vanilla JS + Python HTTP server)

---

## Pre-flight Checklist

Before starting, confirm over SSH:
- [ ] You can SSH into `ubuntu@37.27.9.144`
- [ ] `hermes.service` is running: `sudo systemctl status hermes.service`
- [ ] `cloudflared` is running: `sudo systemctl status cloudflared`
- [ ] `ufw` is active: `sudo ufw status`
- [ ] Hermes agent is at `/home/ubuntu/hermes` and contains `run_agent.py`: `ls /home/ubuntu/hermes/run_agent.py`

---

## Task 1: Clone repo and install Python dependencies

**Files:**
- Create: `/home/ubuntu/hermes-webui/` (cloned repo)
- Create: `/home/ubuntu/hermes-webui/.venv/` (Python virtualenv)

- [ ] **Step 1.1: SSH into the server**

```bash
ssh ubuntu@37.27.9.144
```

- [ ] **Step 1.2: Clone the repo into /home/ubuntu**

```bash
cd /home/ubuntu
git clone https://github.com/nesquena/hermes-webui.git hermes-webui
```

Expected: repo cloned to `/home/ubuntu/hermes-webui/`

- [ ] **Step 1.3: Verify key files exist**

```bash
ls /home/ubuntu/hermes-webui/server.py /home/ubuntu/hermes-webui/start.sh /home/ubuntu/hermes-webui/requirements.txt
```

Expected: all three files listed without error

- [ ] **Step 1.4: Create virtualenv and install dependencies**

```bash
cd /home/ubuntu/hermes-webui
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Expected: `Successfully installed ...` with no errors. This may take 1–2 minutes.

- [ ] **Step 1.5: Verify the server module is importable**

```bash
.venv/bin/python3 -c "import server; print('OK')"
```

Expected: `OK`

---

## Task 2: Firewall and secrets setup

**Files:**
- Create: `/etc/hermes-webui/env` (mode 600, root-owned)

- [ ] **Step 2.1: Check port 8787 is free**

```bash
ss -tlnp | grep 8787
```

Expected: no output. If output appears, choose a different port (e.g. 8788) and replace `8787` in all subsequent steps.

- [ ] **Step 2.2: Block port 8787 from public internet (BEFORE the service starts)**

```bash
sudo ufw deny 8787
sudo ufw status | grep 8787
```

Expected: `8787  DENY Anywhere` (and `8787 (v6)  DENY Anywhere (v6)`)

- [ ] **Step 2.3: Create secrets directory**

```bash
sudo mkdir -p /etc/hermes-webui
sudo chmod 700 /etc/hermes-webui
```

- [ ] **Step 2.4: Write the secrets file with a strong password**

Generate a password first:
```bash
openssl rand -hex 24
```

Copy the output, then:
```bash
sudo tee /etc/hermes-webui/env > /dev/null <<'EOF'
HERMES_WEBUI_PASSWORD=REPLACE_WITH_GENERATED_PASSWORD
EOF
sudo chmod 600 /etc/hermes-webui/env
sudo chown root:root /etc/hermes-webui/env
```

- [ ] **Step 2.5: Verify the secrets file is protected**

```bash
sudo cat /etc/hermes-webui/env
ls -la /etc/hermes-webui/env
```

Expected: file shows `HERMES_WEBUI_PASSWORD=...` and permissions show `-rw-------  root root`

---

## Task 3: Create and enable the systemd service

**Files:**
- Create: `/etc/systemd/system/hermes-webui.service`

- [ ] **Step 3.1: Write the systemd unit file**

```bash
sudo tee /etc/systemd/system/hermes-webui.service > /dev/null <<'EOF'
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
EOF
```

- [ ] **Step 3.2: Verify unit file content looks correct**

```bash
sudo systemctl cat hermes-webui
```

Expected: unit file printed with correct `ExecStart`, `EnvironmentFile`, and all `Environment=` lines. Confirm `HERMES_WEBUI_PASSWORD` does **not** appear (it's in the separate EnvironmentFile).

- [ ] **Step 3.3: Reload systemd and enable the service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable hermes-webui
```

Expected: `Created symlink /etc/systemd/system/multi-user.target.wants/hermes-webui.service → /etc/systemd/system/hermes-webui.service`

---

## Task 4: Start the service and verify locally

- [ ] **Step 4.1: Start the service**

```bash
sudo systemctl start hermes-webui
```

- [ ] **Step 4.2: Check service status**

```bash
sudo systemctl status hermes-webui
```

Expected: `active (running)` with a PID. If it shows `failed` or `activating`, check logs in the next step.

- [ ] **Step 4.3: Check logs for startup errors**

```bash
journalctl -u hermes-webui -n 50 --no-pager
```

Expected: lines like `[server] Listening on 0.0.0.0:8787` with no ERROR or CRITICAL lines. Common issues:
- `Address already in use` → port conflict; re-check Step 2.1, kill the conflicting process
- `AIAgent not available` → `HERMES_WEBUI_AGENT_DIR` is wrong or `run_agent.py` missing
- `No such file: start.sh` → repo wasn't cloned to the right path

- [ ] **Step 4.4: HTTP liveness check**

```bash
curl -s http://localhost:8787/health
```

Expected: JSON like `{"status": "ok", "uptime": ..., "active_streams": 0}`

- [ ] **Step 4.5: Deep readiness check (confirms agent integration)**

```bash
curl -s "http://localhost:8787/health?deep=1"
```

Expected: JSON with `"status": "ok"` and no errors. If agent integration fails, check `HERMES_WEBUI_AGENT_DIR` matches the actual path.

- [ ] **Step 4.6: Verify service survives a restart simulation**

```bash
sudo systemctl restart hermes-webui
sleep 3
curl -s http://localhost:8787/health
```

Expected: `{"status": "ok", ...}` after restart

---

## Task 5: Configure Cloudflare tunnel

- [ ] **Step 5.1: Find the cloudflared config file and extract your domain**

```bash
sudo cat /etc/cloudflared/config.yml 2>/dev/null || cat ~/.cloudflared/config.yml 2>/dev/null
```

Note:
1. The **config file path** (e.g. `/etc/cloudflared/config.yml`)
2. Your **domain** — read it from the existing `hostname:` lines in the `ingress` block (e.g. if you see `hostname: hermes.example.com`, your domain is `example.com`)

Export it for use in subsequent steps:
```bash
export MY_DOMAIN=example.com   # replace with your actual domain
export CF_CONFIG=/etc/cloudflared/config.yml   # replace with actual path
```

- [ ] **Step 5.2: Add webui ingress rule**

```bash
sudo nano $CF_CONFIG
```

Add this entry **before** the catch-all `http_status:404` line:

```yaml
  - hostname: webui.<YOUR_DOMAIN>
    service: http://localhost:8787
```

For example, if your existing config looks like:
```yaml
ingress:
  - hostname: hermes.example.com
    service: http://localhost:8880
  - service: http_status:404
```

It should become:
```yaml
ingress:
  - hostname: hermes.example.com
    service: http://localhost:8880
  - hostname: webui.example.com      # new rule
    service: http://localhost:8787
  - service: http_status:404         # catch-all — must stay last
```

- [ ] **Step 5.3: Validate the cloudflared config**

```bash
cloudflared tunnel ingress validate
```

Expected: `Validating rules from <config_path>` followed by `OK` for each rule with no errors.

- [ ] **Step 5.4: Restart cloudflared**

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

Expected: `active (running)`

- [ ] **Step 5.5: Add DNS CNAME record in Cloudflare dashboard**

In the Cloudflare dashboard:
1. Go to DNS for your domain
2. Add record: Type `CNAME`, Name `webui`, Target = your tunnel's `.cfargotunnel.com` hostname (same one used for existing subdomains)
3. Proxy status: Proxied (orange cloud)

---

## Task 6: End-to-end verification

- [ ] **Step 6.1: Test HTTPS access from local machine**

From your local machine (not the server), replace `webui.example.com` with the hostname you added in Task 5:
```bash
curl -s -o /dev/null -w "%{http_code}" https://webui.example.com/health
```

Expected: `200`

If you get `521` (origin unreachable) or `502` (bad gateway), check:
- `cloudflared` is running on the VPS
- The ingress rule hostname matches the DNS record exactly
- DNS record is saved and propagated (may take a minute)

- [ ] **Step 6.2: Open in browser and log in**

1. Navigate to `https://webui.example.com` (your chosen hostname) in a browser
2. You should see a login page
3. Enter the password from `/etc/hermes-webui/env`
4. Expected: three-panel layout loads (left sidebar, center chat, right workspace)

- [ ] **Step 6.3: Send a test message to Hermes**

1. In the chat panel, type: `Hello, are you there?`
2. Send the message
3. Expected: response streams in from Hermes agent

If the agent doesn't respond, check:
```bash
journalctl -u hermes-webui -f
```
Look for errors related to agent invocation.

- [ ] **Step 6.4: Verify service auto-starts after reboot**

```bash
sudo reboot
```

After ~30 seconds, SSH back in and check:
```bash
sudo systemctl status hermes-webui
curl -s http://localhost:8787/health
```

Expected: both show the service running and healthy.

---

## Rollback

If the deployment needs to be undone:

```bash
# Stop and disable service
sudo systemctl stop hermes-webui
sudo systemctl disable hermes-webui

# Remove unit file and secrets
sudo rm /etc/systemd/system/hermes-webui.service
sudo rm -rf /etc/hermes-webui
sudo systemctl daemon-reload

# Re-open port if needed (only if you want to reverse the ufw deny)
sudo ufw delete deny 8787

# Remove cloned repo
rm -rf /home/ubuntu/hermes-webui
```

Remove the Cloudflare ingress rule from the config file and restart cloudflared. Delete the DNS CNAME from the Cloudflare dashboard.

---

## Troubleshooting Reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Service fails to start, "Address in use" | Port 8787 taken | `ss -tlnp \| grep 8787`, kill the process |
| Service starts but `/health` returns nothing | `start.sh` using wrong Python | Check `journalctl -u hermes-webui` for Python path errors |
| `/health?deep=1` shows agent error | Wrong `HERMES_WEBUI_AGENT_DIR` | Verify `ls /home/ubuntu/hermes/run_agent.py` exists |
| Browser shows Cloudflare 521 | cloudflared not running or bad ingress | `sudo systemctl status cloudflared`, re-check config |
| Login page doesn't appear | Password not set | Check `/etc/hermes-webui/env` has `HERMES_WEBUI_PASSWORD=` |
| Chat sends but no response | Agent service down | `sudo systemctl status hermes.service` |
