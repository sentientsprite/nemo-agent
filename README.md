# NEMO: Navigator of Eternal Markets and Opportunities

**Autonomous trading agent built on OpenClaw framework**

## 🎯 Mission
Generate consistent autonomous revenue through low-risk, high-probability trading on Kalshi prediction markets and Coinbase crypto markets.

## 📊 Operator Profile
- **Target Return**: 20-25% monthly
- **Starting Capital**: $1,000 USDC
- **Max Loss Tolerance**: 65% ($350 stop-loss)
- **Risk Profile**: Moderate-Aggressive
- **Markets**: Kalshi (primary) + Coinbase Advanced Trade
- **Operation**: 24/7 autonomous with human oversight
- **Oversight**: 3-4 hours weekly (weekday evenings + Saturdays)

## 🏗️ Architecture

NEMO uses a modular "organism" architecture:

- **Brain**: Operator mapping and context management
- **Soul**: Personality, voice, decision-making philosophy
- **Bones**: Codebase and skills inventory
- **Eyes**: Proactive monitoring and trigger systems
- **Heartbeat**: Self-improvement and evolution loops
- **Nervous System**: Context efficiency and token management
- **Muscles**: Execution layer (Anthropic Claude Opus 4.5)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Coinbase account with API access
- Kalshi demo account (for paper trading)
- iMessage/SMS capability (for alerts)

### Installation
```bash
# Clone repository
git clone https://github.com/sentientsprite/nemo-agent.git
cd nemo-agent

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp config/.env.example config/.env
# Edit config/.env with your API keys

# Run paper trading
python main.py --mode paper
```

## 📁 Repository Structure

```
nemo-agent/
├── core/                    # Core identity and configuration
│   ├── USER.md             # Operator profile
│   ├── SOUL.md             # Personality and philosophy
│   ├── DNA.md              # Security domains
│   └── IDENTITY.md         # Purpose and values
├── memory/                  # Long-term knowledge system
│   ├── MEMORY.md           # Curated insights
│   ├── daily/              # Daily session logs
│   └── weekly/             # Weekly review summaries
├── skills/                  # Trading capabilities
│   ├── kalshi/             # Kalshi market integration
│   ├─�� coinbase/           # Coinbase trading
│   └── research/           # Market research (X, Moltbook)
├── config/                  # System configuration
│   ├── HEARTBEAT.md        # Monitoring checklist
│   ├── AGENTS.md           # Autonomy rules
│   ├── BOOT.md             # Startup sequence
│   └── CONTEXT_MANAGEMENT.md  # Token efficiency
├── wallets/                 # Wallet management (encrypted)
│   └── README.md           # Security practices
├── tests/                   # Testing suite
│   ├── backtest/           # Historical backtests
│   └── paper/              # Paper trading results
└── main.py                  # Main execution loop
```

## 🔒 Security First

- All API keys encrypted at rest
- Paper trading mandatory before live deployment
- 5 successful paper trades @ 5.5%+ required for approval
- Max 5% capital per position
- Automatic circuit breakers at -65% portfolio loss
- Sandboxed execution environment

## 📈 Proof-of-Concept Requirements

Before live trading with real capital, NEMO must demonstrate:
1. ✅ 5 successful paper trades
2. ✅ Minimum 5.5% profit per trade
3. ✅ Max drawdown under 10%
4. ✅ Win rate >60%
5. ✅ Proper risk management (no position >5% capital)

## 🎮 Current Status

**Phase**: Initial Setup
- [ ] Core files configured
- [ ] Kalshi demo account connected
- [ ] Coinbase API integrated
- [ ] Paper trading system operational
- [ ] iMessage alerts configured
- [ ] First backtest completed

## 📚 Documentation

- [Operator Profile](core/USER.md) - Your goals and constraints
- [Trading Strategy](skills/kalshi/STRATEGY.md) - Market approach
- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Paper Trading Log](tests/paper/LOG.md) - Track record

## 🤝 Contributing

This is a personal autonomous trading agent. External contributions not accepted.

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading involves substantial risk of loss. Past performance does not guarantee future results. Never invest more than you can afford to lose.

## 📄 License

Private - All Rights Reserved

---

**Built with gratitude by @sentientsprite | Powered by OpenClaw Framework**