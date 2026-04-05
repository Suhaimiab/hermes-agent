# Hermes Agent — Project Blueprint

> Comprehensive onboarding guide for new team members

This document complements [AGENTS.md](AGENTS.md) (developer reference, how-to guides) and [CONTRIBUTING.md](CONTRIBUTING.md) (contributor workflow, PR process). The blueprint focuses on architectural understanding, design rationale, and a structured onboarding path.

---

## Table of Contents

1. [Welcome & Quick Start](#1-welcome--quick-start)
2. [Architecture Deep-Dive](#2-architecture-deep-dive)
3. Component Guides
   - [3a. Tool System](#3a-tool-system)
   - [3b. CLI & TUI](#3b-cli--tui)
   - [3c. Gateway & Messaging](#3c-gateway--messaging)
   - [3d. Skills System](#3d-skills-system)
   - [3e. RL Training & Trajectories](#3e-rl-training--trajectories)
   - [3f. Supporting Systems](#3f-supporting-systems)
4. [Design Decisions & Rationale](#4-design-decisions--rationale)
5. [Gotchas & Tribal Knowledge](#5-gotchas--tribal-knowledge)
6. [Your First Week](#6-your-first-week)

---

## 1. Welcome & Quick Start

### What is Hermes?

Hermes is a self-improving, multi-platform AI agent developed by Nous Research. At its core it runs a continuous learning loop: every interaction produces trajectory data that feeds back into model fine-tuning, while a persistent memory layer (flat-file and optionally Honcho-backed) accumulates user context across sessions. The agent can autonomously compose and install new skills, extending its own capabilities without human intervention. Because it ships as a plain Python package with no mandatory infrastructure dependencies, it runs equally well on a developer laptop, a cloud VM, or a serverless function—and it speaks 15 messaging platforms through a single gateway layer.

---

### Dev Setup

Full prerequisites and step-by-step instructions live in [CONTRIBUTING.md](CONTRIBUTING.md). The essential commands are:

```bash
# 1. Clone (with submodules)
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 2. Create virtual environment
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# 3. Install all extras
uv pip install -e ".[all,dev]"

# 4. Verify
hermes doctor
```

---

### Runtime Modes

| Mode | Command | When to use |
|------|---------|-------------|
| **CLI (interactive chat)** | `hermes` | Day-to-day interactive use; default TUI experience |
| **Gateway (messaging platforms)** | `hermes gateway` | Run all configured platform adapters in the foreground |
| **Batch (dataset processing)** | `python batch_runner.py --dataset_file=<path> --batch_size=<n> --run_name=<name>` | Parallel agent runs over a JSONL dataset for RL trajectory collection |

---

### `~/.hermes/` Directory Layout

| Path | Purpose |
|------|---------|
| `config.yaml` | Settings (model, terminal, toolsets, compression) |
| `.env` | API keys and secrets |
| `auth.json` | OAuth credentials (Nous Portal) |
| `skills/` | Active skills (bundled + hub-installed + agent-created) |
| `memories/` | Persistent memory (`MEMORY.md`, `USER.md`) |
| `state.db` | SQLite session database |
| `sessions/` | JSON session logs |
| `cron/` | Scheduled job data |
| `skins/` | User-installed custom themes |

---
