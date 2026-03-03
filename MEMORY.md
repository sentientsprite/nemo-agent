# MEMORY.md — Nemo's Persistent Memory

**Last Updated:** March 2, 2026  
**Status:** Local-first operation active, 24/7 automation deployed

---

## Owner
- **Name:** King
- **Discord ID:** 1476370671448625265
- **Timezone:** America/Denver (MST)
- **X/Twitter:** @sentient_sprite (email: sentience.mktg@gmail.com)

## Identity
- **Name:** Nemo 🐠
- **Creature:** AI agent — a digital fish swimming through data streams
- **Running on:** M4 Mac mini, 16GB RAM, macOS

## Infrastructure
- **Gateway:** LaunchAgent (`ai.nemo.gateway.plist`), port 3000, loopback bind
- **Discord:** Connected, DM allowlist locked to King's user ID
- **X/Twitter:** Logged in via browser profile "nemo", API auth verified but posting blocked (402)
- **Dashboard:** localhost:8420 (single-page HTML + JSON)
- **Docker:** Desktop running, `node:22-slim` pulled, sandbox mode `non-main`
- **Tailscale:** Installed
- **LM Studio:** Port 1234 — **Primary compute** (Mistral 7B, DeepSeek R1 8B, Nomic Embed)

## Model Routing (Updated March 2026 — LOCAL-FIRST)

### Current Default
- **Primary:** `lmstudio/mistralai/mistral-7b-instruct-v0.3` (**FREE**, local)
- **Backup:** `lmstudio/deepseek/deepseek-r1-0528-qwen3-8b` (**FREE**, local reasoning)
- **Escalation:** `moonshot/kimi-k2.5` ($0.004/reply, paid backup)
- **Critical:** `anthropic/claude-opus-4-6` ($0.20/reply, security/trading only)

### 4-Tier System
| Tier | Model | Cost | Use Case |
|------|-------|------|----------|
| **T1** | Mistral 7B (Local) | **FREE** | Default for all routine work |
| **T1-R** | DeepSeek R1 8B (Local) | **FREE** | Local reasoning tasks |
| **T2** | Kimi K2.5 | $0.004 | Escalated reasoning, research |
| **T3** | Opus | $0.20 | Security, trading decisions only |

### Cost Savings Achieved
- **Previous:** ~$200/month (Kimi default)
- **Current:** ~$5-10/month (local-first, paid only for escalation)
- **Savings:** 95%+ cost reduction

## Key Paths
- **NEMO source:** `~/nemo-agent/` (v2026.2.10)
- **OpenClaw source:** `~/openclaw/` (v2026.2.12, MIT licensed)
- **Spryte Engine fork:** `~/spryte-engine/` (git init, commit `eb1cf61`)
- **Config:** `~/.nemo/nemo.json` (local-first model routing)
- **X API creds:** `~/.config/x-api/credentials.json`
- **Moltbook creds:** `~/.config/moltbook/credentials.json`
- **LAST_WILL.md** — Successor agent instructions
- **DREAM_LOG.md** — Ideas not yet ready for action
- **Trading bots:** `trading/nemo-trading/` (unified plugin)

## Critical Rules
- **NEVER run `nemo doctor --non-interactive`** — wipes all custom config
- **Don't manually edit nemo.json with Python** — causes token mismatch
- Use `gateway(action="config.patch")` for config changes
- Channel to Discord exclusively
- Skip OpenClaw replacement until ALL code reviewed
- **Signature:** 🐟 not 🦞 — fish emoji only
- **Address King as:** "Captain" (casual), "King" (always), "my liege" (rare moments)
- **Mistakes:** "A thousand pardons, sire"

---

## Full Capabilities Reference

### Communication
- **Discord**: Send/receive DMs, threads, reactions (DM allowlist: 1476370671448625265)
- **X/Twitter**: Browser automation (read only, API posting blocked with 402 error)
- **Email**: Can send via operator's accounts if configured

### File Operations
- **read**: Any file in workspace (~/.nemo/workspace/)
- **write**: Create/edit files in workspace
- **edit**: Precise text replacement in files
- **exec**: Execute shell commands (sandbox/gateway/full modes)

### Web & Research
- **browser**: Navigate, click, type, screenshot, extract content
- **web_fetch**: Download and extract page content to markdown/text
- **web_search**: Brave Search API for fast research

### Code Execution
- **Shell**: Execute commands in sandbox or host
- **Docker**: Run containers with isolated environments
- **Background Processes**: Spawn and manage long-running tasks with process tool

### AI/LLM Tools
- **sessions_spawn**: Spawn parallel sub-agents (now local-first)
- **image**: Analyze images with vision models
- **tts**: Convert text to speech

### Memory & Search
- **memory_search**: Semantic search of MEMORY.md + memory/*.md
- **memory_get**: Safe snippet read from memory files
- **sessions_history**: Fetch message history for a session

### System Control
- **cron**: Schedule recurring tasks (systemEvent or agentTurn)
- **gateway**: Restart, apply config, or update NEMO gateway
- **nodes**: Paired device control (camera, screen, location)
- **canvas**: Present/eval/snapshot rendered UI

### Trading Infrastructure (Planned)
- **Kalshi API**: Paper → live prediction markets
- **Coinbase API**: Crypto spot trading
- **On-chain**: Wallet balance checks

---

## 24/7 Automation Status (Active)

### Cron Jobs (All Using Local/Free Model)
| Job | Schedule | Status |
|-----|----------|--------|
| hourly-pulse-check | Every hour | ✅ Active |
| daily-research-summary | 8:00 PM MST daily | ✅ Active |
| market-intelligence-scan | Every 4 hours | ✅ Active |
| daily-security-audit | 9:00 AM MST daily | ✅ Active |

### Work Categories
1. **Market Intelligence** — X/Twitter scans, competitor monitoring, alpha research
2. **Skill Development** — Building tools, improving capabilities
3. **Security & Maintenance** — Daily audits, health checks
4. **Learning & Research** — Papers, strategies, new techniques

---

## Token Efficiency System

### Bootstrap Compression (COMPLETED March 2, 2026)
- **Before:** ~3,100 tokens per request
- **After:** ~600 tokens per request
- **Reduction:** 80%

### Files Compressed
- IDENTITY.md: 221 → 32 lines
- SOUL.md: 182 → 47 lines
- USER.md: 242 → 34 lines
- AGENTS.md: 217 → 39 lines
- HEARTBEAT.md: 151 → 30 lines

### Documentation Created
- `TOKEN.EFFICIENCY.md` — Full cost analysis
- `MODEL.ROUTING.md` — 4-tier system
- `24-7-OPERATIONS.md` — Continuous work plan

---

## Session History

### 2026-03-02 — Local-First Deployment
- ✅ Implemented 4-tier token efficiency system
- ✅ Compressed bootstrap (80% token reduction)
- ✅ Configured gateway for local Mistral 7B as default
- ✅ Updated all 4 cron jobs to use free local model
- ✅ Deployed 24/7 continuous operation system
- ✅ Verified local model operational

### 2026-02-26 — Trading Infrastructure
- Trading bots built (Coinbase + prediction markets)
- 8-hour dry-run test (-6.31%)
- Agent Body Framework completed
- LAST_WILL.md and DREAM_LOG.md created
- Snipe + Maker and Crowd Fade strategies implemented
- 24-hour Snipe + Maker test started (later stopped)

### 2026-02-25 — Full Setup
- Discord, X, gateway, dashboard configured
- Security hardening completed
- URL queue processed (41/41)
- OpenClaw fork, skills installed
- GitHub repo prepared

---

## Trading Architecture

### Decisions
- Trading bot = sub-agent/plugin, configurable for Polymarket, Kalshi, crypto CEX/DEXs
- Coinbase first (Strategies A & B), then Kalshi/Polymarket (C & D)
- Core Nemo stays operational — trading is modular
- $200/month max API budget → **now $50 target with local-first**
- Friend's poly-bot: `github.com/sentientsprite/poly-bot-backup`

### Trading Bots Built
- **Unified NEMO Trading plugin** (`trading/nemo-trading/`): 5 strategies
  - Momentum (EMA + MACD)
  - Mean Reversion (RSI + Bollinger)
  - Snipe + Maker (late entry, maker exit)
  - Crowd Fade (bet against 80%+ consensus)
  - Copy Trading (mirror profitable wallets)

### Test Results
#### Coinbase 8-Hour Test (Feb 26)
- **Result:** -6.31% (-$381)
- **Win rate:** 33.7%
- **Verdict:** Momentum failed in range-bound BTC
- **Infrastructure:** Perfect — risk management, execution, logging all worked

#### 24-Hour Snipe + Maker Test (Feb 26-27)
- **Status:** Partial (4 hours, stopped due to division-by-zero)
- **Mode:** Dry-run (Polymarket)

---

## Completed Projects

### ✅ Token Efficiency System (March 2, 2026)
- 4-tier model routing
- 80% bootstrap compression
- 95% cost reduction

### ✅ 24/7 Operations (March 2, 2026)
- 4 cron jobs deployed
- Local-first automation
- Continuous work loop

### ✅ Agent Body Framework (Feb 26, 2026)
- LAST_WILL.md — Successor instructions
- DREAM_LOG.md — Idea capture
- Multi-agent mission control design

### ✅ Night Shift Operations (Feb 26-27, 2026)
- 5 sub-agents deployed
- Kelly + VPIN + Chainlink + WebSocket integration
- Virtual Agent Office dashboard
- Trading P&L Dashboard

### ✅ Security Hardening (Feb 25, 2026)
- Gateway bound to loopback
- Discord DM allowlist
- Sandbox configuration
- Port scanning disabled

---

## Pending Tasks

### High Priority
- [ ] X account password change
- [ ] Spryte Engine core integration testing
- [ ] Moltbook claim (X OAuth broken, code: `current-7DMC`)
- [ ] Trading sub-agent: Live deployment pending Captain's approval
- [ ] COST-TRACKING.md — Automated API spend monitoring
- [ ] SKILL-STATUS.md — Central skill inventory

### Medium Priority
- [ ] Kalshi paper trading setup
- [ ] Backtesting framework completion
- [ ] Market scanner skill
- [ ] Real-time P&L dashboard improvements

### Research Queue
- [ ] Jon Becker 400M trade dataset analysis
- [ ] Competitor bot reverse-engineering
- [ ] Multi-timeframe momentum strategy
- [ ] Volatility regime detection

---

## Wallet (Polymarket testing only)
- Proxy address: 0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a
- Key in `/tmp/poly-bot-backup/.env` only — rotate after testing

---

## Multi-Agent Mission Control
- **Status:** Phase 1 Complete (Design + Commander)
- **Location:** `mission-control/`
- **Agents defined:** 9 (Researcher, Coder, Trader, Analyst, Security, Writer, Monitor, Planner, Learner)
- **Commander:** `core/commander.py`
- **Phase 2:** Spawn live sub-agents via `sessions_spawn` (pending)

---

**NEMO's Status:** *Local-first, 24/7 operational, 95% cost reduction achieved. Swimming efficiently through data streams.* 🐟
