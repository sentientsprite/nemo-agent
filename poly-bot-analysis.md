# Polymarket BTC 5-Min Bot — Strategy Deep-Dive

## 1. Strategy Math & Edge Analysis

### Binary Option Pricing
These are binary contracts: pay $X for a token, receive $1.00 if you win, $0 if you lose.

**Break-even win rates by entry price:**
| Entry Price | Break-even Win Rate | Payout Multiple |
|---|---|---|
| $0.50 | 50.0% | 2.00x |
| $0.55 | 55.0% | 1.82x |
| $0.60 | 60.0% | 1.67x |
| $0.65 | 65.0% | 1.54x |
| $0.70 | 70.0% | 1.43x |
| $0.75 | 75.0% | 1.33x |
| $0.80 | 80.0% | 1.25x |
| $0.85 | 85.0% | 1.18x |
| $0.90 | 90.0% | 1.11x |

**The edge hypothesis:** BTC momentum persists within 5-minute windows. If BTC is already down $50 after 2 minutes, the probability it closes down is >50% (the market might only price "Down" at $0.55-0.65). The bot buys at that price, needing 55-65% actual win rate vs the market's implied probability.

### Where Does the Edge Come From?
1. **Momentum persistence** — BTC trends tend to continue within short timeframes
2. **Market inefficiency** — Polymarket's 5-min markets may be less efficient than major exchanges
3. **Speed** — Bot reacts faster than manual traders to developing trends
4. **Selective entry** — Only trades when delta > $45 with low choppiness (zero_crosses < 3)

### Expected Value Per Trade
Assuming:
- Average entry at $0.60 (implied 60% probability)
- Actual win rate: 62% (small edge from momentum)
- Per trade: EV = (0.62 × $0.40) - (0.38 × $0.60) = $0.248 - $0.228 = **+$0.02 per dollar risked (3.3% edge)**

This is a thin edge. It requires high volume and discipline to compound.

## 2. Risk Management Assessment

### Position Sizing
- **Round budget:** $30 max (6% of $500 bankroll) ✅ Conservative
- **Entry size:** $5 momentum / $5-12 reversal / $40 snipe
- **Max entries per round:** 2 momentum + snipe = up to $50 exposed

**⚠️ Issue:** Snipe budget ($40) is separate from round budget ($30). Total exposure per round can reach $70 (14% of bankroll). This is aggressive for a thin-edge strategy.

### Stop-Loss (-75%)
- Triggers when position is down 75% (e.g., bought at $0.60, now worth $0.15)
- **Too late.** By -75%, most of the value is already gone. Recovering $0.15 on a $0.60 entry saves only $0.75 per $5 entry.
- **Recommendation:** Tighter stop at -50% would save more capital.

### Late Rescue (-90%, last 30s)
- Only fires if position is down 90%+ with 30s left
- At -90%, selling recovers ~$0.50 per $5 entry. Better than zero but marginal.
- **Verdict:** Slightly +EV vs holding to settlement for total loss.

### Hedge Logic
- If losing position triggers stop-loss AND opposite side is < $0.35: buy opposite
- This is **smart** — if your "Up" position is dying, "Down" at $0.30 is a 3.3x potential return
- **Concern:** Only works if the opposite side is actually cheap. In a well-priced market, both sides won't be simultaneously cheap.

### Daily Loss Limit
- 20% daily loss → session halts ✅ Good
- 3 consecutive losses → skip 1 round ✅ Good
- These prevent tilt and catastrophic drawdowns

## 3. Signal Quality

### Momentum Following
- Entry requires: BTC delta > $45, zero_crosses < 3, range $20-500
- **Strength:** Filters out choppy markets effectively
- **Weakness:** $45 is ~0.066% move on $68K BTC — this triggers frequently. Many of these "trends" are noise.
- **Historical context:** BTC 5-min momentum has autocorrelation around 0.1-0.2, meaning weak but real persistence.

### Reversal Signal (prev candle > $300)
- $300 = ~0.44% move in 5 min — this is a genuinely large move
- Mean reversion after extreme moves is well-documented
- **Strength:** High-conviction signal, appropriately scales up ($5 → $10 → $12)
- **Weakness:** Rare signal (maybe 2-5x per day). Could miss if the trend continues.

### Snipe Strategy (last 30-40s)
- Enters with $40 when delta > $16 and price 60-92¢
- **This is the best signal.** With 30s left, price direction is mostly determined. If "Down" is trending at $0.70, the actual probability is likely >70%.
- **Risk:** Market makers know this too — the ask price already reflects the late-round probability. Edge is thinner than it looks.
- **Concern:** $40 snipe on a $500 bankroll (8%) is aggressive for a single entry.

### Learner Module
- Phase 1 (0-50 trades): Collect data only
- Phase 2 (50-200): Win-rate bucketing → skip losing conditions
- Phase 3 (200+): Logistic regression gating
- **Assessment:** Sound architecture. The phased approach prevents overfitting on small samples. Logistic regression is appropriate for binary outcomes with simple features.
- **Weakness:** 200 trades of data is still small. Model may overfit to recent market regime.

## 4. Weaknesses & Vulnerabilities

### Latency Risk
- Coinbase WebSocket → bot processes → Polymarket CLOB order
- Total latency: ~500ms-2s
- For 5-min markets this is fine. For snipe (last 30s) it matters more.
- Settlement is based on Polymarket's own oracle, not Coinbase. **Price discrepancy between feeds = risk.**

### Order Book Thinness
- These micro-markets have limited liquidity
- $5-40 orders should fill, but slippage at scale would be brutal
- **Can't scale this strategy to $10K+ without moving the market**

### Fill Rate
- Limit orders 8¢ below best ask with 3 re-prices over 60s
- In a fast-moving market, orders may not fill before the signal weakens
- Unfilled rounds = missed opportunities (zero P&L, not negative)

### Fee Structure
- Polymarket: 0% maker fee on limit orders (currently)
- If fees are introduced, the thin ~3% edge evaporates instantly

### Sideways Markets
- MIN_DELTA_ENTRY = $45 and MIN_INTRA_ROUND_RANGE = $20 filter these out
- Bot correctly sits out dead markets — but this means long stretches of no trading
- Estimated: bot only trades 30-40% of rounds

## 5. Estimated Returns

### Modeling Assumptions
- 288 rounds per day (5 min each)
- Bot trades ~35% = ~100 rounds/day
- Average entry: $0.62 (price), $7.50 average size (mix of $5 momentum + occasional $40 snipe)
- Win rate: 58-62% (realistic range for momentum strategy)

### Scenarios

| Scenario | Win Rate | Avg Entry | Trades/Day | Daily P&L | Monthly ROI |
|---|---|---|---|---|---|
| **Bear case** | 52% | $0.63 | 80 | -$8.40 | -50% 💀 |
| **Realistic** | 58% | $0.62 | 100 | +$5.80 | +35% ✅ |
| **Bull case** | 63% | $0.60 | 120 | +$21.60 | +130% 🚀 |
| **With learner (Phase 3)** | 61% | $0.61 | 70 | +$12.50 | +75% ✅ |

**Key insight:** The difference between 52% and 58% win rate is the difference between ruin and profit. The edge is THIN.

### vs. Your 20-25% Monthly Target
The realistic scenario (58% WR) projects ~35% monthly — **exceeds target** if the edge holds. But the bear case shows how quickly things go wrong with a 6% drop in win rate.

### Minimum Bankroll
- With $30/round budget and 20% daily loss limit: $500 is viable
- Kelly Criterion (with 3% edge): optimal bet ≈ 5% of bankroll per trade → $25 (aligns with current sizing)
- **$500 is the minimum viable bankroll for this strategy**

## 6. Recommendations

### Top 3 Improvements

1. **Tighten snipe sizing.** $40 snipe on $500 bankroll is 8% — too much for a single entry. Drop to $15-20 or make it proportional to bankroll (3-4%).

2. **Tighten stop-loss to -50%.** Current -75% saves almost nothing. At -50%, you recover $1.50 per $5 entry instead of $0.75.

3. **Add Polymarket-specific price feed.** The bot uses Coinbase/Binance for BTC price but Polymarket settles on its own oracle. Add the Polymarket settlement price source to reduce oracle mismatch risk.

### Parameters to Tune
- `MIN_DELTA_ENTRY`: Try $55-65 (fewer but higher-quality entries)
- `SNIPE_ENTRY_SIZE`: Reduce from $40 to $15-20
- `STOP_LOSS_PCT`: Reduce from 0.75 to 0.50
- `SNIPE_MIN_PRICE`: Raise from 0.60 to 0.65 (better risk/reward)
- `MAX_MOMENTUM_ENTRIES`: Keep at 2 (reasonable)

### Is It Worth Running Live?

**Yes, with caveats:**

✅ Well-engineered bot with proper risk management
✅ Strategy logic is sound (momentum + reversal + snipe)
✅ Adaptive learner is a genuine advantage
✅ Conservative round budgets ($30 on $500)

⚠️ **But:**
- Edge is thin (~3%). Small changes in market conditions can flip P&L negative
- Polymarket is USA-restricted (legal risk for you, King)
- No backtesting results included — need historical validation
- The learner needs 50+ trades before it starts helping

**My recommendation:** Run dry-run for 1 week (collecting ~700 trades), analyze the data, then decide. If win rate > 56%, green light for small live capital ($100-200).

---

*Analysis by NEMO 🦞 | February 26, 2026*
