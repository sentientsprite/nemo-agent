# 📚 Research

## Recent Findings

| Title | Category | Date | Agent | Key Finding |
|-------|----------|------|-------|-------------|
| Polymarket Intelligence Report | Market | 2026-02-27 | Researcher | News arbitrage most profitable |
| Trading Bot Code Review | Infrastructure | 2026-02-27 | Coder | 3 critical bugs found |
| Coinbase 8hr Test Analysis | Trading | 2026-02-26 | NEMO | Momentum failed in chop (-6.31%) |
| Polymarket Fees Impact | Market | 2026-02-26 | NEMO | 3.15% taker fees kill arbitrage |
| High Win Rate Strategies | Trading | 2026-02-26 | NEMO | Snipe + Maker 70-80% win rate |

---

## Detailed Research

### Polymarket Intelligence Report (2026-02-27)

**Source**: Researcher Agent  
**File**: `mission-control/agents/researcher/output/polymarket-intelligence-2026-02-27.md`

**Successful Strategies (30 days)**:

1. **News/Event Arbitrage**
   - Front-running market-moving information
   - Example: $1M+ profits on ZachXBT investigation market
   - 12+ wallets profited >$1M

2. **Cross-Platform Arbitrage**
   - Price discrepancies between Polymarket, Kalshi, traditional platforms
   - Geographic restrictions create opportunities

3. **Whale Tracking**
   - Following smart money
   - One trader: $0.14 → $411,000

4. **Volmex Volatility Trading**
   - New BTC/ETH 30-day implied volatility
   - Less competition than directionals

**Regulatory Updates (USA)**:
- CFTC Chairman declared "do-over" on prediction market policy
- Withdrawing Biden-era restrictions
- Fighting states for federal jurisdiction
- $10B yearly revenue forecast by 2030

**Action Items**:
- [ ] Position for Volmex products
- [ ] Monitor CFTC announcements
- [ ] Build news/event monitoring
- [ ] Track regulatory arbitrage

---

### Code Review Findings (2026-02-27)

**Source**: Coder Agent  
**File**: `mission-control/agents/coder/output/code-review-2026-02-27.md`

**Critical Issues (All Fixed)**:

1. **Hardcoded Price (0.75)**
   - Location: `strategies/snipe.py:103`
   - Issue: Exit decisions used fixed price instead of market data
   - Fix: Now uses `order_book.mid_price`

2. **VPIN Fail-Open**
   - Location: `main.py:243`
   - Issue: If VPIN crashed, trading continued without protection
   - Fix: Now returns "withdraw" on error (fail-closed)

3. **Random Data in Production**
   - Location: `main.py:449-453`
   - Issue: VPIN using simulated trade data
   - Fix: Only runs in `dry_run` mode

**Security Concerns**:
- Log files in world-writable `/tmp/`
- No credential validation
- P&L data logged (sensitivity)

**Recommendations**:
- Fix log permissions before live trading
- Add circuit breaker for repeated errors
- Validate credentials before connections

---

### Coinbase 8-Hour Test Analysis (2026-02-26)

**File**: `research/coinbase-8hr-analysis.md`

**Results**:
- Trades: 86
- Win Rate: 33.7%
- P&L: -$381 (-6.31%)
- Verdict: Momentum strategy failed in range-bound BTC

**Lessons**:
- Momentum fails in chop
- Need volatility filter
- Snipe + Maker better for sideways markets

---

### Polymarket Fees Impact (2026-02-26)

**File**: `research/polymarket-fees-impact-report.md`

**Finding**: 3.15% taker fees make YES+NO arbitrage unprofitable

**Combined cost**: <1¢ arbitrage needs >3.15% edge → impossible

**Solution**: Snipe + Maker strategy
- Taker entry (pay fee once)
- Maker exit at 90¢ (no fee)
- 70-80% expected win rate

---

## Research Sources

| Source | Type | Value |
|--------|------|-------|
| X/Twitter Threads | Intelligence | High |
| Moltbook Research | Competitor | High |
| GitHub (poly-bot-backup) | Code | Critical |
| Autonomous-Agents Papers | Academic | Medium |
| Kalshi/Polymarket Docs | Platform | High |

---

**Last Updated**: 2026-02-27 00:15 MST
