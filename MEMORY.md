# MEMORY.md — Nemo's Persistent Memory

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
- **LM Studio:** Port 1234 — DeepSeek R1 8B, Mistral 7B, Qwen3 VL 8B, Nomic Embed

## Model Routing
- **Main conversation:** Opus (complex reasoning, King interaction)
- **Sub-agents/cron:** Kimi K2.5 (~$0.004/task, ~50x cheaper than Opus)
  - **Model string:** `moonshot/kimi-k2.5` (NOT `anthropic/kimi-k2.5`)
  - **Status:** Switched Feb 26 after Anthropic credit exhaustion
- **Embeddings/memory:** Nomic Embed via LM Studio (free)

## Key Paths
- **NEMO source:** `~/nemo-agent/` (v2026.2.10)
- **OpenClaw source:** `~/openclaw/` (v2026.2.12, MIT licensed)
- **Spryte Engine fork:** `~/spryte-engine/` (git init, commit `eb1cf61`)
- **Config:** `~/.nemo/nemo.json`
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

## Session History
- **2026-02-25:** Full setup session — Discord, X, gateway, dashboard, security hardening, URL queue (41/41 processed), OpenClaw fork, token efficiency, skills installed, GitHub repo prepared
- **2026-02-26:** Trading bots built (Coinbase + prediction markets), 8-hour dry-run test (-6.31%), Agent Body Framework completed, LAST_WILL.md and DREAM_LOG.md created, Snipe + Maker and Crowd Fade strategies implemented, Polymarket VPN deployment ready, X intelligence gathered (fees killed arbitrage), Spryte Engine core packages built, **24-hour Snipe + Maker test started**

## Active Tests
### 24-Hour Snipe + Maker Test
- **Started:** 2026-02-26 19:41 MST
- **Ends:** 2026-02-27 19:41 MST
- **PID:** 14486
- **Log:** `/tmp/nemo-trading.log`
- **Mode:** Dry-run (Polymarket)
- **Expected win rate:** 70-80%
- **Monitoring:** Hourly cron checks (job ID: 52ffa0f6-d68c-4e58-87ab-f210b1154df5)

## Trading Architecture Decisions (from King)
- Trading bot = sub-agent/plugin, configurable for Polymarket, Kalshi, AND crypto CEX/DEXs
- Coinbase first (Strategies A & B), then Kalshi/Polymarket copy trading (C & D)
- Core Nemo stays operational — trading is modular
- $200/month max on API credits — track and report
- Friend's poly-bot at `github.com/sentientsprite/poly-bot-backup` (a21ai/poly-bot)
- Poly-bot analysis: `poly-bot-analysis.md`, platform research: `research/trading-platform-research.md`
- **Agent Body Framework: COMPLETE** — see LAST_WILL.md, DREAM_LOG.md

## Trading Bots Built
- **Unified NEMO Trading plugin** (`trading/nemo-trading/`): 5 strategies, GitHub committed (c25ed0c)
  - Momentum (EMA + MACD)
  - Mean Reversion (RSI + Bollinger)
  - Snipe + Maker (late entry, maker exit)
  - Crowd Fade (bet against 80%+ consensus)
  - Copy Trading (mirror profitable wallets)
- **24-hour Snipe + Maker test running** — results tomorrow

## Test Results
### Coinbase 8-Hour Test (Feb 26)
- **Result:** -6.31% (-$381)
- **Win rate:** 33.7%
- **Verdict:** Momentum failed in range-bound BTC
- **Infrastructure:** Perfect — risk management, execution, logging all worked

## Wallet (Polymarket testing only)
- Proxy address: 0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a
- Key in `/tmp/poly-bot-backup/.env` only — rotate after testing

## Pending
- 24-hour Snipe + Maker test results (tomorrow 19:41 MST)
- X account password change
- Spryte Engine core integration testing
- Moltbook claim (X OAuth broken, code: `current-7DMC`)
- Trading sub-agent: Live deployment pending Captain's approval
- **Multi-Agent Mission Control:** Phase 1 complete, Phase 2 (live agents) pending

## 🌙 Night Shift Operations (In Progress)
**Deployed:** 2026-02-26 22:00 MST  
**Captain's Request:** Implement 5 critical upgrades while sleeping

### Deployed Sub-Agents
1. **Dataset Hunter** — Find Jon Becker's 400M trade dataset
2. **Oracle Integrator** — Chainlink BTC/USD price feed
3. **Kelly Calculator** — 0.25x fractional Kelly sizing
4. **Toxicity Detector** — VPIN flow toxicity detection
5. **WebSocket Architect** — <100ms latency connections

### Monitoring
- **Hourly checks:** Cron job `a3272754-640d-4047-91e3-dc1bae8a9d1c`
- **Morning report:** 06:00 MST `a509eb5c-a1c6-440e-a3ad-1825b9015cfa`
- **Log:** `night-shift-operations.md`
- **ETA:** Complete by morning (2026-02-27 06:00 MST)

## Multi-Agent Mission Control
- **Status:** Phase 1 Complete (Design + Commander)
- **Location:** `mission-control/`
- **Agents defined:** 9 (Researcher, Coder, Trader, Analyst, Security, Writer, Monitor, Planner, Learner)
- **Commander:** `core/commander.py` — task routing and delegation
- **Phase 2:** Spawn live sub-agents via `sessions_spawn`
