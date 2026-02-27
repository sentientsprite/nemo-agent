# k1rallik: $600k Polymarket Trading Bot

**Source:** https://x.com/k1rallik/status/2027097016937979985  
**Author:** BuBBliK (@k1rallik)  
**Views:** 7,574 | **Date:** Feb 26, 2026 (TODAY)

---

## The Bot's Performance

**Account:** @0x1d0034134e on Polymarket  
**Registered:** January 2026 (brand new!)  
**Rank:** #167 globally

### Stats
- **$600,000** in one month on 5-15m markets
- **$150,000** in a single day
- **63.2%** win rate across 19,000+ positions
- **320+ trades per day** — pure algorithm, zero emotion
- **Total gains:** +$1,265,851
- **Max drawdown:** -$641,536

---

## The Strategy

**NOT gambling on "UP or DOWN"** — this is institutional-level quant trading:

1. **Arbitrages mispriced BTC 5m/15m Up/Down markets**
2. **Entry condition:** Model edge >3%
3. **Position sizing:** 0.25x Kelly Criterion
4. **Risk management:** Keeps book delta-neutral

**What it actually trades:**
- **Implied volatility spreads** between model fair price and market price
- Treats Polymarket like an **options exchange, not a casino**

---

## Key Insights

### This is a ClawdBot
> "He's probably another clawdbot that trades according to a specific algorithm and makes money." — @kirillk_web3

**Clawd + model fair price = this exact PnL curve**

### The Formula
> "Start with Chainlink oracles + 5m BTC vol model"

**Requirements:**
1. Chainlink price oracles (data feed)
2. 5-minute BTC volatility model
3. Fair price calculation
4. Edge detection (>3%)
5. Kelly position sizing (0.25x)
6. Delta-neutral book management

### The Brutal Reality
> "You're providing liquidity to Kelly criterion all day" — @k1rallik

Most retail traders are the **counterparty** to bots like this. They don't even know it.

---

## Comparison to NEMO

| Aspect | $600k Bot | NEMO Current |
|--------|-----------|--------------|
| Strategy | Vol arb / edge detection | Snipe + Maker |
| Kelly sizing | 0.25x fractional | Fixed size |
| Model | Chainlink + vol model | Price delta |
| Delta neutral | Yes | No |
| Edge threshold | >3% | Fixed $5 delta |
| Trades/day | 320+ | Pending |
| Win rate | 63.2% | TBD |

**Gap:** We need:
1. Chainlink oracle integration
2. BTC volatility model
3. Fair price calculation
4. Kelly position sizing
5. Delta-neutral hedging

---

## Action Items for NEMO

- [ ] Integrate Chainlink BTC/USD oracle
- [ ] Build 5-minute BTC volatility model
- [ ] Calculate fair price vs market price
- [ ] Implement Kelly Criterion sizing (0.25x fractional)
- [ ] Track @0x1d0034134e for copy-trading signals
- [ ] Monitor ratio_dot_you for similar wallets

---

## Resources

- **Wallet tracker:** @ratio_dot_you (access code: FQA4TMK3)
- **Bot profile:** https://polymarket.com/@0x1d0034134e
- **Chainlink oracles:** docs.chain.link

---

*"Most people gamble on 'UP or DOWN'. This bot trades implied volatility spreads."* — BuBBliK 🐟
