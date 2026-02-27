# Polymarket Intelligence Report — X Research

**Date:** 2026-02-26  
**Source:** Captain's X feed  
**Analyst:** NEMO 🐟

---

## 🎯 High-Value Signals

### 1. 0x_Discover — Arbitrage King
- **Claim:** $400K in under a month
- **Performance:** ~$5/sec, ~$300/hour, ~$7K/day
- **Strategy:** 
  - 5-min BTC Up/Down markets ONLY
  - Buys YES + NO in first ~4 minutes
  - Enters when combined price < $1 (arbitrage)
  - Locks spread before expiry
  - 6,823 trades, pure arbitrage (no directional bias)
- **Edge:** Compounds tiny pricing inefficiencies
- **Copy Trade:** Telegram @PolyGunSniperBot
- **Confidence:** 85% — Detailed proof provided

**Actionable:** Implement YES+NO arbitrage in our PM bot

---

### 2. ventry089 — 4-Bot Deathmatch
Tournament: 4 strategies, $500 each, 7 days

| Bot | Strategy | Final | Key Lesson |
|-----|----------|-------|------------|
| **Contrarian** | Fade 80%+ confidence | **$1,740** 🏆 | One explosion wins all |
| **Weather** | 3 models agree | $1,120 | Patience, few trades |
| **Whale Copier** | Mirror top wallets | $780 | Boring survival |
| **Scalper** | Binance/PM arb | $82 💀 | **Temporary edge killed it** |

**Key Insight:** "Dumbest" bot (contrarian) won by waiting for crowd errors. "Smartest" (scalper) died when edge decayed.

**Actionable:** 
- Add contrarian mode to PM bot
- Implement edge decay detection for scalper
- Weather fusion for our data sources

---

### 3. AleiahLock — Whale Hunter
- **Target:** $1.6M gains, 87.2% win rate
- **Tool:** ratio_dot_you for wallet copy
- **Claim:** "Make same gains in 1 minute"
- **Confidence:** 60% — Promotional, needs verification

**Actionable:** Research ratio_dot_you API integration

---

### 4. Jasper BΞll — Copy Trading Guide
- **Content:** Detailed automatic vs manual copy trading thread
- **Value:** Educational, strategy framework
- **Confidence:** 80% — Legitimate analysis

**Actionable:** Review thread for implementation details

---

## ⚠️ Warnings & Noise

### Insider Trading Risk
- **ZachXBT investigation:** AxiomExchange employees insider trading
- **Lesson:** Even successful platforms have leaks
- **Mitigation:** Don't rely on single data source

### Scam Indicators
- Multiple accounts posting identical $400K results
- "Make millions with 1 click" posts
- Unsubstantiated win rate claims without proof

---

## 🧠 Strategic Recommendations

### For Our PM Bot (priority order):

1. **YES+NO Arbitrage** (0x_Discover method)
   - Monitor combined price < $1
   - Enter first 4 minutes
   - Lock spread before expiry

2. **Contrarian Mode** (ventry winner)
   - Detect 80%+ crowd consensus
   - Fade extreme confidence
   - Wait for crowd errors

3. **Edge Decay Detection** (prevent scalper death)
   - Track arbitrage opportunity duration
   - Auto-disable strategies when edge shrinks
   - Rotate to alternative approaches

4. **Multi-Source Fusion** (weather bot method)
   - Require multiple signals to agree
   - Reduce false positives
   - Patience over frequency

5. **Whale Copy** (steady baseline)
   - Mirror proven profitable wallets
   - Boring but consistent
   - Good for steady bankroll growth

---

## 🔧 Implementation Notes

### New Signal Sources to Add:
- [ ] PolyGunSniperBot Telegram integration
- [ ] ratio_dot_you wallet tracking
- [ ] Crowd consensus monitoring (80%+ detection)
- [ ] Combined price arbitrage scanner
- [ ] Edge decay tracking per strategy

### Code to Port from Kalshi Bot:
- Copy engine with proportional sizing
- Risk engine with correlation limits
- Leader wallet monitoring
- Performance tracking vs leaders

### Testing Protocol:
1. Dry-run each strategy independently
2. A/B test against baseline
3. Measure edge decay over time
4. Only deploy profitable edges live

---

## 📊 Confidence Summary

| Source | Value | Confidence |
|--------|-------|------------|
| 0x_Discover arbitrage | HIGH | 85% |
| ventry deathmatch | HIGH | 90% |
| AleiahLock whale | MEDIUM | 60% |
| Jasper BΞll guide | MEDIUM | 80% |
| General copy trading | LOW | 40% |

---

## Next Steps

1. **Immediate:** Implement YES+NO arbitrage in PM bot
2. **Short-term:** Add contrarian mode with 80% threshold
3. **Medium-term:** Multi-strategy tournament framework
4. **Ongoing:** Monitor edge decay, rotate strategies

---

*Compiled by NEMO 🐟 | For Captain's review*
