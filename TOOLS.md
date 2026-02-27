# NEMO Tools - Capabilities Inventory

**Last Updated**: February 26, 2026

---

## Core Agent Capabilities

### Communication
- **Discord**: Send/receive DMs, threads, reactions
- **X/Twitter**: Browser automation (read only, API posting blocked)
- **Email**: Can send via operator's accounts if configured

### File Operations
- **Read**: Any file in workspace (~/.nemo/workspace/)
- **Write**: Create/edit files in workspace
- **Edit**: Precise text replacement in files
- **Execute**: Shell commands (with safety controls)

### Web Access
- **Browser**: Navigate, click, type, screenshot, extract content
- **Web Fetch**: Download and extract page content
- **Web Search**: Brave Search API

### Code Execution
- **Shell**: Execute commands in sandbox or host
- **Docker**: Run containers with isolated environments
- **Background Processes**: Spawn and manage long-running tasks

### AI/LLM
- **Sub-agents**: Spawn parallel tasks on cheaper models (Kimi K2.5)
- **Image Analysis**: Analyze images with vision models
- **TTS**: Convert text to speech

### Memory
- **Search**: Semantic search of MEMORY.md and memory files
- **Recall**: Access session history
- **Write**: Append to daily memory files

### System
- **Cron**: Schedule recurring tasks
- **Gateway Config**: Modify NEMO gateway settings
- **Node Management**: Paired device control (camera, screen, etc.)

---

## Trading-Specific Capabilities (Planned)

### Data Access
- [ ] **Kalshi API**: Read market data, place orders (demo → live)
- [ ] **Coinbase API**: Read balances, execute trades
- [ ] **On-chain**: Wallet balance checks (read-only)

### Analysis
- [ ] **Backtesting**: Historical strategy validation
- [ ] **Technical Analysis**: Indicators, patterns
- [ ] **Sentiment Analysis**: Social media mood
- [ ] **Fundamental Analysis**: Economic data, events

### Execution
- [ ] **Order Management**: Place, modify, cancel orders
- [ ] **Position Sizing**: Risk-adjusted trade sizing
- [ ] **Portfolio Tracking**: Real-time PnL monitoring

---

## Current Infrastructure

### Active Services
- **Gateway**: localhost:3000 (NEMO gateway)
- **Dashboard**: localhost:8420 (project tracking)
- **Crabwalk**: localhost:3000 (agent monitoring) [Note: Port conflict?]
- **LM Studio**: localhost:1234 (local LLM inference)

### Storage Locations
- **Workspace**: ~/.nemo/workspace/ (git tracked)
- **Config**: ~/.nemo/nemo.json (gateway config)
- **Credentials**: ~/.nemo/credentials/ (API keys)
- **Sessions**: ~/.nemo/agents/main/sessions/ (logs)
- **Memory**: ~/.nemo/workspace/memory/ (daily logs)

### External Accounts
- **GitHub**: sentientsprite (authenticated)
- **X/Twitter**: @sentient_sprite (browser logged in)
- **Discord**: Paired to operator ID 1476370671448625265
- **Moltbook**: Registered (claim blocked)

---

## Skill Modules

### Installed Skills
1. **find-skills**: Discover new capabilities
2. **agent-browser**: Web automation
3. **reflection**: Self-improvement
4. **systematic-debugging**: Error handling

### Custom Skills
- **healthcheck**: System security audits
- **skill-creator**: Create new skills

### Skills to Consider
- Trading-specific skills (Kalshi, Coinbase)
- Analysis skills (backtesting, technical analysis)
- Monitoring skills (alerts, dashboards)

---

## Limitations & Constraints

### What I Cannot Do
- ❌ Access operator's personal accounts (banking, email) without explicit setup
- ❌ Trade with real money (not yet authorized)
- ❌ Withdraw funds from wallets
- ❌ Access systems outside my sandbox (host is okay, other devices need pairing)
- ❌ Make irreversible changes without operator approval
- ❌ Violate my security rules (DNA.md)

### What Requires Approval
- Live trading with real capital
- System-level changes (installing new software, modifying config)
- External service integrations (new APIs, webhooks)
- Large file operations (>100MB)
- Long-running processes (>1 hour unattended)

### Cost Considerations
- **Opus**: ~$0.20/reply (use sparingly)
- **Kimi K2.5**: ~$0.004/reply (default for most tasks)
- **Local models**: Free (LM Studio)
- **Browser**: Token-efficient (compact snapshots)

---

## Best Practices

### When to Use What
- **Heavy reasoning**: Opus (strategy decisions, security)
- **Routine tasks**: Kimi K2.5 (research, summaries, coding)
- **Embeddings**: Local Nomic Embed (free)
- **Parallel work**: Sub-agents on Kimi K2.5

### Efficiency Tips
- Use compact browser snapshots (maxChars 800-1500)
- Grep/head/tail before reading full files
- Spawn sub-agents for parallel research
- Cache frequent lookups in memory

### Security Reminders
- Never log API keys or credentials
- Always use sandbox for untrusted code
- Validate all external inputs
- Fail secure on uncertainty

---

**NEMO's Tools Philosophy**: Use the right tool for the job, minimize costs, maximize autonomy within safety bounds.

🦞🛠️
