# Project Blueprint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a comprehensive `BLUEPRINT.md` onboarding document for new developers joining the Hermes Agent team.

**Architecture:** Single markdown file at project root. Seven sections covering project overview, architecture deep-dive, six component guides, design rationale, tribal knowledge, and a structured first-week onboarding path. Content is derived from reading actual source files — not fabricated.

**Tech Stack:** Markdown. Source verification via reading Python files.

**Spec:** `docs/superpowers/specs/2026-04-05-project-blueprint-design.md`

---

## File Structure

- **Create:** `BLUEPRINT.md` (project root) — the single deliverable

**Key source files to reference (read-only):**
- `run_agent.py` — AIAgent class, `run_conversation()` loop
- `model_tools.py` — `_discover_tools()`, `handle_function_call()`, `_run_async()`
- `toolsets.py` — toolset definitions, `resolve_toolset()`
- `tools/registry.py` — `ToolRegistry`, `register()`, `dispatch()`
- `agent/prompt_builder.py` — system prompt assembly order
- `agent/context_compressor.py` — compression trigger and 5-phase algorithm
- `hermes_state.py` — `SessionDB`, FTS5 schema, WAL mode
- `agent/credential_pool.py` — `CredentialPool`, selection strategies
- `cli.py` — `HermesCLI` lifecycle
- `hermes_cli/commands.py` — `CommandDef`, `COMMAND_REGISTRY`
- `hermes_cli/skin_engine.py` — skin system
- `gateway/run.py` — `GatewayRunner`
- `gateway/platforms/base.py` — `BasePlatformAdapter` ABC
- `gateway/session.py` — `SessionStore`, `SessionSource`, PII hashing
- `batch_runner.py` — `BatchRunner`, parallel trajectory generation
- `trajectory_compressor.py` — `CompressionConfig`, compression strategy
- `environments/hermes_base_env.py` — `HermesAgentBaseEnv`, subclass interface
- `rl_cli.py` — RL training CLI
- `mini_swe_runner.py` — SWE task executor
- `mcp_serve.py` — MCP server, 10 tools
- `honcho_integration/session.py` — `HonchoSessionManager`
- `cron/scheduler.py` — cron system

---

### Task 1: Create BLUEPRINT.md with Table of Contents and Section 1 (Welcome & Quick Start)

**Files:**
- Create: `BLUEPRINT.md`

**Reference files to read:**
- `CONTRIBUTING.md:54-110` (dev setup, prerequisites)
- `hermes_cli/main.py:1-30` (CLI entry point)
- `gateway/run.py:1-30` (gateway entry)
- `batch_runner.py:1-30` (batch entry)

- [ ] **Step 1: Read source files for accuracy**

Read the reference files above to verify:
- Current dev setup steps (Python version, uv commands)
- Exact CLI entry command
- Gateway invocation command
- Batch runner invocation

- [ ] **Step 2: Write the file header, TOC, and Section 1**

Create `BLUEPRINT.md` with:
- Title: "# Hermes Agent — Project Blueprint"
- Subtitle: "Comprehensive onboarding guide for new team members"
- Note about complementing AGENTS.md and CONTRIBUTING.md
- Full table of contents with anchor links to all 6 sections and subsections
- Section 1: Welcome & Quick Start
  - One-paragraph project identity
  - Dev setup summary (reference CONTRIBUTING.md, don't duplicate)
  - Three runtime modes with one-liner examples
  - `~/.hermes/` directory layout table

- [ ] **Step 3: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs: add BLUEPRINT.md with TOC and Welcome section"
```

---

### Task 2: Write Section 2 — Architecture Deep-Dive

**Files:**
- Modify: `BLUEPRINT.md`

**Reference files to read:**
- `run_agent.py` — find `run_conversation()`, understand the loop structure (iteration budget, tool_choice, termination conditions)
- `model_tools.py` — find `handle_function_call()` and `_run_async()`
- `agent/prompt_builder.py` — find the main build function, note the assembly order
- `agent/context_compressor.py` — find `should_compress()`, `compress()`, the 5-phase algorithm
- `agent/model_metadata.py` — find token estimation functions
- `hermes_state.py` — find `SessionDB` class, table schemas, FTS5 setup
- `agent/credential_pool.py` — find `CredentialPool`, selection strategies
- `hermes_cli/auth.py` — find provider resolution flow
- `agent/anthropic_adapter.py` — understand what it adapts

- [ ] **Step 1: Read source files and extract architecture details**

For each file above, read the relevant sections and note:
- Exact method signatures for key functions
- Loop structure in `run_conversation()`
- Prompt assembly order in `prompt_builder.py`
- Compression phases in `context_compressor.py`
- Table schemas in `hermes_state.py`
- The import chain from `tools/registry.py` up

- [ ] **Step 2: Write Section 2**

Append to `BLUEPRINT.md`:
- ASCII system diagram showing: CLI/Gateway/Batch → AIAgent → LLM providers / tool registry / session DB / memory
- Agent loop walkthrough with pseudocode matching actual `run_conversation()` structure
- Message format explanation (OpenAI schema, reasoning field, tool results)
- Provider abstraction: how the same agent works with different providers, role of `anthropic_adapter.py`, credential resolution chain, credential pooling
- Prompt assembly pipeline: exact order from `prompt_builder.py`, why order matters for caching
- Context management: when compression triggers, 5-phase algorithm summary
- Session persistence: SQLite WAL + FTS5, key tables, JSON logs
- File dependency chain diagram

- [ ] **Step 3: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add architecture deep-dive section"
```

---

### Task 3: Write Section 3a-3b — Tool System and CLI/TUI Component Guides

**Files:**
- Modify: `BLUEPRINT.md`

**Reference files to read:**
- `tools/registry.py` — `ToolRegistry` class, `register()` signature, `dispatch()` method
- `model_tools.py` — `_discover_tools()` module list, agent-level tool interception
- `toolsets.py` — `_HERMES_CORE_TOOLS`, platform presets, `resolve_toolset()`
- `tools/approval.py` — dangerous command patterns
- `tools/environments/base.py` (or similar) — `BaseEnvironment` ABC
- `cli.py` — `HermesCLI` class init and lifecycle
- `hermes_cli/commands.py` — `CommandDef` class, `COMMAND_REGISTRY`
- `hermes_cli/skin_engine.py` — `SkinConfig`, built-in skins, `init_skin_from_config()`
- `hermes_cli/callbacks.py` — callback types

- [ ] **Step 1: Read source files for tool system details**

Extract: registry API, toolset names, approval patterns, environment backends list.

- [ ] **Step 2: Read source files for CLI/TUI details**

Extract: HermesCLI init sequence, CommandDef fields, skin customization points, callback types.

- [ ] **Step 3: Write Sections 3a and 3b**

Append to `BLUEPRINT.md`:
- 3a: Tool System — registration pattern, tool anatomy, dispatch flow, async bridging, toolsets, approval, agent-level tools, terminal backends
- 3b: CLI & TUI — lifecycle, slash command registry, skin engine, callbacks, profiles

- [ ] **Step 4: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add tool system and CLI component guides"
```

---

### Task 4: Write Section 3c — Gateway & Messaging Platforms

**Files:**
- Modify: `BLUEPRINT.md`

**Reference files to read:**
- `gateway/platforms/base.py` — `BasePlatformAdapter` ABC methods, `MessageEvent`, `SendResult`, `SessionSource`
- `gateway/run.py` — `GatewayRunner.__init__()`, key state (agent cache, running agents, platform adapters)
- `gateway/session.py` — `SessionStore`, `SessionContext`, `build_session_key()`, PII hashing functions
- `gateway/config.py` — platform configuration

- [ ] **Step 1: Read source files for gateway details**

Extract: ABC method signatures (4 required, optional overrides), GatewayRunner init state, session key generation, PII redaction approach, media caching.

- [ ] **Step 2: Write Section 3c**

Append to `BLUEPRINT.md`:
- GatewayRunner architecture overview
- Platform adapter contract (required + optional methods with signatures)
- Full platform list (15 adapters)
- Message flow diagram: platform event → normalization → handle_message → AIAgent → response → adapter
- Session management: key generation, PII redaction, context prompt injection
- Media caching and cleanup
- Token locks for profile isolation
- How to add a new platform adapter

- [ ] **Step 3: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add gateway and messaging platforms guide"
```

---

### Task 5: Write Section 3d — Skills System

**Files:**
- Modify: `BLUEPRINT.md`

**Reference files to read:**
- `agent/prompt_builder.py` — `build_skills_system_prompt()`, `_skill_should_show()`, skill loading
- `tools/skills_guard.py` — security scanning
- `hermes_cli/skills_hub.py` — hub discovery, installation
- `skills/research/` — example skill for SKILL.md format reference
- `CONTRIBUTING.md:300-460` — existing skill documentation (reference, don't duplicate)

- [ ] **Step 1: Read source files for skills details**

Extract: skill loading pipeline, caching strategy, conditional activation logic, guard scanning approach, hub workflow.

- [ ] **Step 2: Write Section 3d**

Append to `BLUEPRINT.md`:
- Skills vs tools decision framework
- SKILL.md format with frontmatter schema
- Skill loading pipeline (prompt_builder → cache → system prompt)
- Conditional activation (fallback_for/requires toolsets/tools)
- Platform filtering
- Skill categories (bundled, optional, hub)
- Self-improvement loop (agent-created skills)
- Skills Hub workflow
- Setup metadata and skills guard
- Reference CONTRIBUTING.md for the full authoring recipe

- [ ] **Step 3: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add skills system guide"
```

---

### Task 6: Write Section 3e — RL Training & Trajectory System

**Files:**
- Modify: `BLUEPRINT.md`

**Reference files to read:**
- `agent/trajectory.py` — trajectory saving helpers
- `batch_runner.py` — `BatchRunner`, `_process_single_prompt()`, checkpointing, config options
- `trajectory_compressor.py` — `CompressionConfig`, compression phases, output format
- `environments/hermes_base_env.py` — `HermesAgentBaseEnv`, `HermesAgentEnvConfig`, subclass interface
- `environments/web_research_env.py` — example environment (reward functions)
- `rl_cli.py` — commands, config, RL_MAX_ITERATIONS
- `mini_swe_runner.py` — `MiniSWERunner`, environment types, invocation

- [ ] **Step 1: Read source files for RL/trajectory details**

Extract: trajectory format, batch runner config, compression phases, environment subclass interface, existing environments, RL CLI commands, mini SWE runner usage.

- [ ] **Step 2: Write Section 3e**

Append to `BLUEPRINT.md`:
- Trajectory saving overview
- Batch runner: architecture, config options, invocation, checkpointing, output format
- Trajectory compression: CompressionConfig, 5-phase algorithm, output format with metrics
- RL environments: base class, config, subclass interface (5 required methods), existing environments
- RL CLI: commands, configuration, tinker-atropos integration
- Mini SWE runner: purpose, backends, invocation

- [ ] **Step 3: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add RL training and trajectory system guide"
```

---

### Task 7: Write Section 3f — Supporting Systems

**Files:**
- Modify: `BLUEPRINT.md`

**Reference files to read:**
- `cron/scheduler.py` — scheduler architecture
- `cron/jobs.py` — job definitions
- `mcp_serve.py` — MCP server setup, 10 tool decorators
- `acp_adapter/` — ACP server purpose and interface
- `honcho_integration/session.py` — `HonchoSessionManager`, write frequency
- `honcho_integration/client.py` — client singleton

- [ ] **Step 1: Read source files for supporting system details**

Extract: cron architecture, MCP tool list, ACP purpose, Honcho session management.

- [ ] **Step 2: Write Section 3f**

Append to `BLUEPRINT.md`:
- Cron scheduler: architecture, job creation, croniter integration
- MCP server: 10-tool surface with brief descriptions, data sources
- ACP adapter: IDE integration purpose
- Honcho: session management, write frequency, relationship to SQLite + file memory

- [ ] **Step 3: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add supporting systems guide"
```

---

### Task 8: Write Section 4 — Design Decisions & Rationale

**Files:**
- Modify: `BLUEPRINT.md`

No additional source files needed — content comes directly from the approved spec Section 4, which was validated during brainstorming.

- [ ] **Step 1: Write Section 4**

Append to `BLUEPRINT.md`:
- 11 design decisions, each with: the decision, the rationale (why), and the practical implication
- Decisions: OpenAI message format, synchronous loop, self-registering tools, skills over tools, SQLite FTS5, prompt caching constraint, HERMES_HOME isolation, ephemeral injection, pluggable backends, WAL jitter retry, credential pooling

- [ ] **Step 2: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add design decisions and rationale"
```

---

### Task 9: Write Section 5 — Gotchas & Tribal Knowledge

**Files:**
- Modify: `BLUEPRINT.md`

**Reference files to read:**
- `AGENTS.md:420-470` — verify the "Known Pitfalls" section exists (for cross-reference)

No additional source reading needed — content comes from the approved spec Section 5, which was specifically rewritten to provide architectural reasoning distinct from AGENTS.md coding rules.

- [ ] **Step 1: Write Section 5**

Append to `BLUEPRINT.md`:
- Opening note: reference AGENTS.md "Known Pitfalls" for specific coding rules
- 8 architectural gotchas with full reasoning:
  - Profile isolation load order
  - Prompt caching economics
  - Two dispatch layers
  - Async bridging contexts
  - Cross-platform requirement
  - Test isolation fixtures
  - Config migration versioning
  - Context file safety limits

- [ ] **Step 2: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add gotchas and tribal knowledge"
```

---

### Task 10: Write Section 6 — Your First Week (Onboarding)

**Files:**
- Modify: `BLUEPRINT.md`

- [ ] **Step 1: Write Section 6**

Append to `BLUEPRINT.md`:
- Day 1-2: Get Oriented (setup, test suite, trace a message)
- Day 3: Tools & Skills (read examples, create toy tool, load skill)
- Day 4: Gateway (run Telegram bot, trace gateway message, read adapter contract)
- Day 5: RL & Trajectories (save trajectory, read compressor, run batch)
- Day 6-7: Go Deeper (read a bug fix PR, make small improvement, submit first PR)

- [ ] **Step 2: Add Cross-References footer**

Append the cross-references section linking to AGENTS.md, CONTRIBUTING.md, cli-config.yaml.example, .env.example.

- [ ] **Step 3: Commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): add onboarding guide and cross-references"
```

---

### Task 11: Final Review and Polish

**Files:**
- Modify: `BLUEPRINT.md`

- [ ] **Step 1: Read the complete BLUEPRINT.md end to end**

Check for:
- Broken anchor links in TOC
- Inconsistent terminology
- Missing cross-references between sections
- Any placeholder text left behind

- [ ] **Step 2: Fix any issues found**

- [ ] **Step 3: Final commit**

```bash
git add BLUEPRINT.md
git commit -m "docs(blueprint): polish and finalize"
```
