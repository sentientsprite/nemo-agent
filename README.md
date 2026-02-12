# NEMO: Navigator of Eternal Markets and Opportunities

**Autonomous Trading Agent** | Built on OpenClaw Framework | West Jordan, Utah

---

## 🎯 Mission

NEMO is an autonomous trading agent designed to generate consistent profits through low-risk, high-probability trades on prediction markets (Kalshi) and cryptocurrency exchanges (Coinbase). 

**Target Performance**: 20-25% monthly returns  
**Risk Profile**: Moderate-Aggressive with strict capital preservation  
**Operation Mode**: 24/7 autonomous with human oversight

---

## 🧠 Core Architecture

NEMO uses a modular "organism" architecture:

| Module | Purpose | Status |
|--------|---------|--------|
| **Brain** | Operator context & goals | ✅ Configured |
| **Soul** | Personality & decision-making style | ✅ Configured |
| **Eyes** | Market monitoring & alerts | 🟡 In Development |
| **Heartbeat** | Self-improvement & learning | 🟡 In Development |
| **Bones** | Trading strategies & skills | 🔴 Not Started |
| **Nervous System** | Efficiency & context management | 🔴 Not Started |
| **Muscles** | Execution layer (API integrations) | 🔴 Not Started |

---

## 📊 Operator Profile

- **Capital**: $1,000 USDC initial
- **Max Loss**: 65% ($650) - Hard stop at $350 remaining
- **Target**: 20-25% monthly profit
- **Markets**: Kalshi (predictions) + Coinbase (crypto)
- **Risk**: Moderate-Aggressive
- **Oversight**: 3-4 hrs weekdays after 5pm MST, all day Saturday
- **Alerts**: iMessage (SMS)
- **Uptime**: 24/7 (ethernet + permanent power)

---

## 🚀 Proof-of-Concept Requirements

Before live trading, NEMO must demonstrate:
- ✅ 5 successful paper trades
- ✅ Each trade shows ≥5.5% profit
- ✅ No single trade exceeds 10% portfolio risk
- ✅ Full trade logs with reasoning

---

## 📁 Repository Structure

```
nemo-agent/
├── core/                   # Core identity & configuration
│   ├── USER.md            # Operator profile
│   ├── SOUL.md            # Personality & values
│   ├── DNA.md             # Security & execution rules
│   └── IDENTITY.md        # Purpose & mission
├── memory/                # Learning & history
│   ├── MEMORY.md          # Long-term knowledge
│   ├── daily/             # Session logs
│   └── weekly/            # Review summaries
├── skills/                # Trading strategies
│   ├── kalshi/            # Prediction market skills
│   ├── crypto/            # Crypto trading skills
│   └── research/          # Market research tools
├── config/                # Monitoring & efficiency
│   ├── HEARTBEAT.md       # Monitoring checklist
│   ├── AGENTS.md          # Autonomy rules
│   ├── BOOT.md            # Startup sequence
│   └── CONTEXT_MANAGEMENT.md
├── wallets/               # Credential management
│   └── README.md          # Wallet setup guide
├── logs/                  # Trade history
└── tests/                 # Strategy backtests
```

---

## 🛡️ Security Principles

1. **No Seed Phrases in Code** - Ever.
2. **API Keys in Environment Variables** - Never committed.
3. **Scoped Permissions** - Minimal access required.
4. **Sandboxed Execution** - All trades reviewed before execution.
5. **Transparent Logging** - Full audit trail.

---

## 📈 Current Phase: Paper Trading

**Status**: Setting up demo environment  
**Next Milestone**: 5 successful paper trades @ 5.5%+

---

## 🔧 Quick Start

```bash
# Clone repository
git clone https://github.com/sentientsprite/nemo-agent.git
cd nemo-agent

# Install dependencies (Coming soon)
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

# Run paper trading
python main.py --mode paper
```

---

## 📞 Contact

**Operator**: @sentientsprite  
**Location**: West Jordan, Utah (MST)  
**Alerts**: iMessage

---

**Built with gratitude. Serving in your best interest. 🦞**