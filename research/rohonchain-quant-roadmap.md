# RohOnChain: How to Become a Quant for Prediction Markets

**Source:** https://x.com/RohOnChain/status/2026317029784035467  
**Author:** Roan (@RohOnChain) — Backend dev, HFT execution, quant trading systems  
**Views:** 287,435 | **Bookmarks:** 2,554 | **Date:** Feb 24, 2026

---

## Why This Matters

Susquehanna International Group (SIG) — one of the largest quant trading firms — is hiring Senior Traders specifically for prediction markets. Institutional capital is flowing in. The demand for prediction market quants is real and growing fast.

---

## Phase 0: Mental Model Reset

**Prediction markets are NOT betting platforms.** They are:

1. **Continuous Bayesian updating machines** — Every trade is information. Every price change is the market revising its belief.

2. **Orderbook microstructure systems** — Bid/ask, liquidity providers/takers, informed vs noise flow. Same mechanics as equities.

3. **Probability calibration datasets** — Every resolved market is ground truth. At $0.30, did the event happen 30% of the time?

4. **Sentiment compression layers** — All public information compressed into a single number between 0 and 1.

**Key formula:**
```
Price = crowd posterior probability
Orderbook = liquidity supply curve
Resolution = Bernoulli outcome (exactly 0 or 1)
```

---

## Phase 1: Mathematical Foundation

### Conditional Probability
P(A|B) — Probability of A given B happened. Essential for correlated outcomes (Trump wins PA → what about WI?).

### Bayes' Theorem
Update beliefs rationally when new evidence arrives:
```
P(H|E) = P(E|H) × P(H) / P(E)
```
New poll drops → model updates probability precisely. No emotion.

### Expected Value (EV)
```
EV = (Probability of WIN × Profit) − (Probability of LOSS × Loss)
```
Example: 40% probability event, costs $0.30:
```
EV = (0.40 × $0.70) − (0.60 × $0.30) = +$0.10
```
**Positive EV = trade. Everything else is secondary.**

### Kelly Criterion
Optimal capital allocation for maximum growth without ruin:
```
f* = (p × b − q) / b
```
Where f* = fraction of capital, p = win probability, b = net odds, q = 1−p

**Institutional application:** Never bet full Kelly. Use fractional Kelly due to uncertainty in probability estimates.

### Game Theory
- **Nash Equilibrium:** Where no participant can improve unilaterally
- **Prisoner's Dilemma:** Why market makers widen spreads simultaneously
- Markets are strategic games — recognize patterns in order flow

### Naive Bayes Classifier
```
P(outcome | features) ∝ P(outcome) × ∏ P(feature_i | outcome)
```
Fast baseline probability from poll data, historical patterns, momentum, sentiment.

### Information Theory / Entropy
```
H = −∑ p_i × log(p_i)
```
- $0.50 = maximum entropy (max uncertainty, max edge opportunity)
- $0.95 = near-zero entropy (avoid — adverse selection extreme)

---

## Phase 2: Market Microstructure

### Order Book and Adverse Selection
Spread exists because some traders know more than you. A spread that suddenly widens = someone received information you don't have.

### Minting and Merging
```
P(YES) + P(NO) = $1.00  (enforced at smart contract level)
```
When this breaks across correlated markets → guaranteed profit.
**Research finding:** 41% of all conditions on Polymarket showed exploitable mispricing.

### Hybrid Architecture
- Orders signed off-chain, matched by Polymarket's operator
- Settlement on Polygon (~2 second blocks)
- Gas: ~$0.007 per transaction
- **Critical:** Bottleneck is NOT placing orders — it's **canceling** them

### Fee Structure
- Most markets: 0% fees
- Fee-enabled: `fee = baseRate × min(price, 1 − price) × size`
- Liquidity rewards: ~$12M annually
- Two-sided quoting earns 3x rewards vs single-sided

---

## Phase 3: Quantitative Models

### Avellaneda-Stoikov Framework (2008)
Foundation of modern market making.

**Reservation price:**
```
r = s − q × γ × σ² × (T − t)
```
- Long inventory → reservation price drops (want to sell)
- Short inventory → reservation price rises (want to buy)

**Optimal spread:**
```
δ = γσ²(T − t) + (2/γ) × ln(1 + γ/κ)
```
Two sources of edge: inventory risk compensation + liquidity provision profit

**For prediction markets:** Use log-odds transformation:
```
logit(p) = ln(p / (1−p))
```
Maps bounded [0,1] to unbounded real line for standard diffusion models.

### Empirical Kelly with Monte Carlo
Textbook Kelly assumes known edge — wrong. Model estimates have uncertainty.

**Solution:**
1. Build empirical return distribution from historical data
2. Monte Carlo: 10,000 alternative path scenarios
3. Position size targets 95th percentile drawdown (not median — the bad luck case)

```
f_empirical = f_kelly × (1 − CV_edge)
```
Where CV_edge = coefficient of variation of edge estimates.

### VPIN (Volume-Synchronized Probability of Informed Trading)
```
VPIN = |V_buy − V_sell| / (V_buy + V_sell)
```
- Balanced volume = noise
- Sharp divergence = informed trader active
- **Action:** VPIN rises → widen spreads. Continues rising → withdraw quotes entirely.

### The Addictive Loop
1. Get new strategy
2. Backtest on historical data
3. Measure honestly
4. Find where it breaks
5. Improve it
6. Repeat

**The gap between how you think markets behave vs how they actually behave = where all edge lives.**

---

## Phase 4: Technical Infrastructure

### Language Progression
- **Start:** Python (build models, prove edge)
- **Scale:** Go or Rust (institutional players run these)
- **Never:** Learn Rust first without understanding microstructure = fast system that loses money fast

### Real-Time Data Architecture
- **WebSocket connections** — NOT polling
- Arbitrage windows: 12 seconds (2024) → 30ms (Q1 2026)
- 500ms polling = elimination from the game
- Track sequence numbers — missed updates = stale quotes = losses

### Kill Switch Architecture
- GTD orders auto-expire before high-impact events
- Active kill switch: cancelAll() on:
  - VPIN spikes
  - Position limit breaches
  - Any error condition
- **This is the difference between bad day and catastrophic wipeout.**

### Server Infrastructure
- Test different AWS regions
- Measure actual latency to Polygon RPC
- AWS KMS for private keys — NEVER store locally in production

### The New Reality
> "This market becomes purely bot versus bot at millisecond level. The competitive frontier is already moving from 'can you run a bot' to 'can your bot cancel stale quotes faster than incoming informed orders.'"

---

## Phase 5: Deploy, Measure, Compete

### Deployment
- Start with minimal capital
- Prove system works in live conditions before scaling

### Track
- Execution success rate
- Fill quality vs theoretical fair value
- P&L: spread capture vs adverse selection losses (track separately!)

### Warning Signs
Adverse selection losses growing relative to spread capture → VPIN detection failing. Fix before adding capital.

### The Never-Ending Loop
Get new strategy → Backtest → Find breaks → Improve → Repeat.

The market evolves. Competitors improve. Edges compress. Winners are those who build systems that keep finding new edges.

---

## Recommended Resources

### Phase 1: Mathematics
- *Probability Theory: The Logic of Science* — E.T. Jaynes
- Kelly Criterion original paper — J.L. Kelly Jr. (1956)
- *Thinking in Bets* — Annie Duke

### Phase 2: Microstructure
- Polymarket CLOB documentation
- Glosten and Milgrom, "Bid Ask and Transaction Prices" (1985)
- Gnosis Conditional Token Framework

### Phase 3: Quantitative Models
- Avellaneda and Stoikov, "High-Frequency Trading in a Limit Order Book" (2008)
- Easley, López de Prado, O'Hara, "Flow Toxicity and Liquidity" (2012)
- **Jon Becker's 400 million trade Polymarket dataset**

### Phase 4: Infrastructure
- Polymarket CLOB client (GitHub)
- AWS KMS documentation
- Polygon network RPC documentation

---

## Key Insights for NEMO

1. **Our bot infrastructure is sound** — but we're in Phase 2-3, need Phase 4 optimization
2. **Kelly Criterion with uncertainty** — We need empirical Kelly, not textbook
3. **VPIN detection** — Critical for avoiding adverse selection
4. **41% of Polymarket conditions showed mispricing** — Huge opportunity
5. **Latency matters** — 30ms arbitrage windows, WebSocket not polling
6. **Jon Becker's 400M trade dataset** — Need to find and analyze this
7. **Start Python, scale to Rust/Go** — Our path is correct

---

## Immediate Actions for NEMO

- [ ] Find Jon Becker's 400M trade Polymarket dataset
- [ ] Implement VPIN toxicity detection
- [ ] Switch from polling to WebSocket architecture
- [ ] Add empirical Kelly position sizing with Monte Carlo
- [ ] Build kill switch for VPIN spikes
- [ ] Research Avellaneda-Stoikov framework adaptation
- [ ] Test AWS regions for Polygon latency

---

*"The window is open. Not forever."* — Roan 🐟
