# Trading Platform Research Report

**Date**: February 26, 2026  
**Purpose**: Technical reference for building automated trading integrations

---

## 1. Coinbase Advanced Trade API

### Authentication

Coinbase Advanced Trade API supports two authentication methods:

| Method | Use Case | Details |
|--------|----------|---------|
| **API Key (CDP)** | Server-side bots | Create via Coinbase Developer Platform (CDP). Generates API key + API secret. Sign requests with HMAC-SHA256 or use the CDP SDK which handles signing. |
| **OAuth2** | User-delegated apps | For apps acting on behalf of other users. Requires OAuth flow with scopes. Not needed for personal bot trading. |

**For bot trading**: Use CDP API keys. Create at [https://portal.cdp.coinbase.com/](https://portal.cdp.coinbase.com/). Keys have configurable permissions (view, trade, transfer).

### REST Endpoints

Base URL: `https://api.coinbase.com/api/v3/brokerage`

| Operation | Method | Endpoint |
|-----------|--------|----------|
| **List Accounts** | GET | `/accounts` |
| **Get Account** | GET | `/accounts/{account_uuid}` |
| **Place Order** | POST | `/orders` |
| **Cancel Orders** | POST | `/orders/batch_cancel` |
| **Get Order** | GET | `/orders/historical/{order_id}` |
| **List Fills** | GET | `/orders/historical/fills` |
| **Get Product** | GET | `/products/{product_id}` |
| **List Products** | GET | `/products` |
| **Product Candles** | GET | `/products/{product_id}/candles` |
| **Market Trades** | GET | `/products/{product_id}/ticker` |
| **Get Best Bid/Ask** | GET | `/best_bid_ask` |

**Order types supported**: Market, Limit (GTC/GTD/IOC/FOK), Stop-Limit, Trigger Bracket.

### WebSocket Feed

- **Endpoint**: `wss://advanced-trade-ws.coinbase.com`
- **Channels**:
  - `heartbeats` — connection keepalive
  - `candles` — OHLCV candle updates
  - `market_trades` — real-time trade feed
  - `status` — product status changes
  - `ticker` / `ticker_batch` — price ticker updates
  - `level2` — order book updates (L2)
  - `user` — authenticated user order/fill events

Authentication required for `user` channel; public channels need API key signature for subscription but no special permissions.

### Fee Structure

Coinbase Advanced uses a maker/taker model based on 30-day trailing volume:

| 30-Day Volume (USD) | Maker Fee | Taker Fee |
|---------------------|-----------|-----------|
| $0 – $1K | 0.60% | 0.80% |
| $1K – $10K | 0.40% | 0.60% |
| $10K – $50K | 0.25% | 0.40% |
| $50K – $100K | 0.15% | 0.25% |
| $100K – $1M | 0.10% | 0.18% |
| $1M – $15M | 0.08% | 0.12% |
| $15M+ | 0.05% | 0.08% |

**Stablecoin pairs** (e.g., USDC-USD) may have reduced or zero fees. Check current schedule at [https://www.coinbase.com/advanced-fees](https://www.coinbase.com/advanced-fees).

### Rate Limits

- **REST API**: 30 requests/second per API key (private endpoints). Public endpoints: 10 req/sec unauthenticated, higher authenticated.
- **WebSocket**: 750 messages/second per connection. Max 20 connections per API key.
- Rate limit headers returned: `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset`.

### Python SDK / Libraries

| Library | Notes |
|---------|-------|
| **`coinbase-advanced-py`** | Official Coinbase Python SDK. `pip install coinbase-advanced-py`. Wraps REST + WebSocket. |
| **`ccxt`** | Multi-exchange library. Supports Coinbase Advanced under `coinbaseadvanced` exchange ID. Good for multi-exchange bots. |

Official SDK: [https://github.com/coinbase/coinbase-advanced-py](https://github.com/coinbase/coinbase-advanced-py)

```python
from coinbase.rest import RESTClient
client = RESTClient(api_key="key", api_secret="secret")
accounts = client.get_accounts()
order = client.create_order(
    client_order_id="unique-id",
    product_id="BTC-USDC",
    side="BUY",
    order_configuration={"market_market_ioc": {"quote_size": "100"}}
)
```

### USDC Trading Pairs

Coinbase offers extensive USDC pairs. Major ones include:

BTC-USDC, ETH-USDC, SOL-USDC, DOGE-USDC, AVAX-USDC, LINK-USDC, UNI-USDC, MATIC-USDC, ADA-USDC, DOT-USDC, NEAR-USDC, ARB-USDC, OP-USDC, AAVE-USDC, MKR-USDC, and many more (100+ pairs).

Full list available via `GET /products?product_type=SPOT` filtered by quote currency `USDC`.

### Bot/Automated Trading Restrictions

- **Allowed**: Coinbase explicitly supports API-based automated trading. No restrictions on bot trading.
- **Requirements**: Must comply with API rate limits. No spoofing/wash trading.
- **Geofencing**: Available in US (most states), EU, UK, and many other jurisdictions. Some products restricted by state.
- **No special approval needed** for API trading — just create CDP API keys.

**Docs**: [https://docs.cdp.coinbase.com/advanced-trade/docs/welcome](https://docs.cdp.coinbase.com/advanced-trade/docs/welcome)

---

## 2. Kalshi API

### Getting API Access

1. **Create account** at [https://kalshi.com](https://kalshi.com) — standard identity verification (SSN, government ID)
2. **API access is automatic** — once your account is verified and funded, API access is available
3. **API keys**: Generate at [https://kalshi.com/account/api-keys](https://kalshi.com/account/api-keys)
4. **Demo environment**: Available at `https://demo-api.kalshi.co` for paper trading

No special approval process for API access. Just a verified, funded account.

### REST Endpoints

Base URL: `https://trading-api.kalshi.com/trade-api/v2`  
Demo: `https://demo-api.kalshi.co/trade-api/v2`

| Operation | Method | Endpoint |
|-----------|--------|----------|
| **Login** | POST | `/login` |
| **List Events** | GET | `/events` |
| **List Markets** | GET | `/markets` |
| **Get Market** | GET | `/markets/{ticker}` |
| **Get Orderbook** | GET | `/markets/{ticker}/orderbook` |
| **Place Order** | POST | `/portfolio/orders` |
| **Cancel Order** | DELETE | `/portfolio/orders/{order_id}` |
| **Get Orders** | GET | `/portfolio/orders` |
| **Get Positions** | GET | `/portfolio/positions` |
| **Get Fills** | GET | `/portfolio/fills` |
| **Get Balance** | GET | `/portfolio/balance` |
| **Get Settlements** | GET | `/portfolio/settlements` |
| **Get Market History** | GET | `/markets/{ticker}/history` |

Authentication: Bearer token from `/login` endpoint (email + password), or API key auth via headers.

### Real-Time Data Feeds

- **WebSocket**: `wss://trading-api.kalshi.com/trade-api/ws/v2`
  - Channels: `orderbook_delta`, `ticker`, `trade`, `fill` (authenticated)
  - Subscribe by sending JSON messages with channel + market ticker
- **Polling**: REST endpoints work fine for markets that update slowly (daily/weekly)
- **Recommended**: WebSocket for active trading; polling every 5-15s adequate for daily markets

### Fee Structure

| Component | Fee |
|-----------|-----|
| **Trading fee** | $0.02–$0.07 per contract (varies by market, typically ~$0.035) |
| **Contract value** | $0 or $1 at settlement |
| **Price range** | $0.01 – $0.99 per contract |
| **Withdrawal fee** | Free (ACH), wire fees vary |
| **No monthly fees** | — |

Fees are per-contract and deducted at trade time. Maker/taker distinction not prominently tiered — fees are generally flat per contract.

### Market Types

Kalshi offers markets across many categories:

| Category | Examples |
|----------|---------|
| **Economics** | Fed rate decisions, CPI, GDP, unemployment |
| **Weather** | Temperature records, hurricane landfalls, snowfall |
| **Finance** | S&P 500 ranges, Bitcoin price, stock earnings |
| **Politics** | Election outcomes, policy decisions |
| **Tech** | Product launches, AI milestones |
| **Entertainment** | Awards, box office |
| **Climate** | Carbon levels, natural disasters |
| **Sports** | (Limited, expanding) |

### USA Legal Status

**Fully legal for US residents.** Kalshi is:
- A **CFTC-regulated** Designated Contract Market (DCM)
- Licensed since 2020, operational since mid-2021
- Legal in all 50 US states (though some contract types may have state restrictions)
- Won a federal court case in 2023 against CFTC to offer election-related contracts
- Compliant with US financial regulations (KYC/AML)
- FDIC-insured deposits (held at partner banks)

This is the key differentiator vs Polymarket, which is **not available to US residents** for real-money trading.

### Python SDK

| Library | Notes |
|---------|-------|
| **`kalshi-python`** | Official SDK. `pip install kalshi-python`. Wraps REST API. |
| **Community clients** | Several on GitHub; official one is recommended. |

```python
import kalshi_python
config = kalshi_python.Configuration()
config.host = "https://trading-api.kalshi.com/trade-api/v2"
api_client = kalshi_python.ApiInstance(config)
api_client.login(email="...", password="...")
markets = api_client.get_markets(limit=100, status="open")
```

Official SDK: [https://github.com/Kalshi/kalshi-python](https://github.com/Kalshi/kalshi-python)

### Kalshi vs Polymarket Comparison

| Feature | Kalshi | Polymarket |
|---------|--------|------------|
| **Regulation** | CFTC-regulated DCM | Unregulated (crypto-based) |
| **US Access** | ✅ Legal in all 50 states | ❌ Blocked for US residents |
| **Currency** | USD (bank transfer) | USDC on Polygon |
| **Settlement** | Binary ($0 or $1) | Binary (0 or 1 USDC) |
| **Order Types** | Limit, market | CLOB limit orders |
| **Contract Price** | $0.01–$0.99 | $0.01–$0.99 |
| **Fees** | ~$0.02–$0.07/contract | Free trading, ~2% on winnings |
| **Liquidity** | Growing, moderate | Higher on popular markets |
| **Market Creation** | Kalshi-created only | Anyone can create |
| **API** | REST + WebSocket | REST + WebSocket (CLOB) |
| **Settlement** | Automated by Kalshi | Oracle-based (UMA) |
| **Deposit Insurance** | FDIC-insured partner banks | None (crypto custody) |

**Key differences**: Kalshi is the regulated, US-legal option with USD banking. Polymarket has deeper liquidity on major events but requires crypto and is not US-accessible.

**Docs**: [https://trading-api.readme.io/reference](https://trading-api.readme.io/reference)

---

## 3. Copy Trading / Signal Following Architecture

### How Copy-Trading Bots Work

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  Leader   │────▶│  Signal      │────▶│  Follower    │
│  Trader   │     │  Processor   │     │  Executor    │
└──────────┘     └──────────────┘     └──────────────┘
                       │
                  ┌────┴────┐
                  │  Risk   │
                  │  Engine │
                  └─────────┘
```

1. **Leader Detection**: Monitor a leader's trades/positions via API, webhook, or public feed
2. **Signal Generation**: Transform leader action into a normalized signal (buy/sell, size, market)
3. **Risk Adjustment**: Scale position size relative to follower's capital and risk parameters
4. **Execution**: Place orders on follower's account via exchange API
5. **Reconciliation**: Track divergence between leader and follower positions

### Main Approaches

| Approach | Latency | Reliability | Complexity |
|----------|---------|-------------|------------|
| **Webhook-based** | Low (sub-second) | High (push model) | Medium — leader system sends HTTP POST on trade events |
| **API Polling** | Medium (1-30s) | High | Low — poll leader's positions/orders endpoint periodically |
| **Social Feed Scraping** | High (seconds-minutes) | Low | High — parse Twitter/Discord/Telegram for trade signals |
| **Exchange Copy Feature** | Low | High | None — use exchange's built-in copy trading (Bybit, Bitget) |
| **Shared Signal Bus** | Low | High | Medium — pub/sub system (Redis, NATS) between agents |

**For prediction markets (Kalshi)**: API polling every 5-15 seconds is adequate. Most Kalshi markets resolve over hours/days, not seconds.

### Latency Considerations

| Market Type | Acceptable Latency | Approach |
|-------------|-------------------|----------|
| **Crypto spot** (Coinbase) | < 100ms | WebSocket + direct API |
| **Kalshi daily markets** | < 30s | API polling fine |
| **Kalshi hourly/5-min** | < 5s | WebSocket preferred |
| **Kalshi event markets** | < 60s | Polling adequate |

For prediction markets, the edge is rarely in speed — it's in signal quality. A few seconds of latency is acceptable for most Kalshi markets.

### Risk Management for Copy Trading

| Parameter | Description | Typical Setting |
|-----------|-------------|-----------------|
| **Position Sizing** | Scale leader's position by capital ratio | `follower_size = leader_size × (follower_capital / leader_capital) × risk_factor` |
| **Max Position %** | Cap any single position as % of portfolio | 5-15% of portfolio |
| **Max Daily Loss** | Stop copying after X% daily drawdown | 3-5% of portfolio |
| **Slippage Guard** | Skip if price moved > X% since leader's fill | 1-3% |
| **Staleness Filter** | Skip if signal older than X seconds | 30-300s depending on market type |
| **Diversification** | Max positions across correlated markets | Limit per category |
| **Leader Drawdown** | Pause copying if leader hits drawdown | -10% from peak |

---

## 4. Sub-Agent Architecture for Trading

### Recommended Plugin Structure

```
┌─────────────────────────────────────────┐
│              Core Agent (NEMO)           │
│  ┌─────────┐ ┌────────┐ ┌───────────┐  │
│  │ Memory  │ │ Comms  │ │ Scheduler │  │
│  └────┬────┘ └───┬────┘ └─────┬─────┘  │
│       │          │             │         │
│  ─────┴──────────┴─────────────┴─────── │
│              Event Bus                   │
│  ──────────────────────────────────────  │
│       │          │             │         │
│  ┌────┴────┐ ┌───┴────┐ ┌─────┴─────┐  │
│  │ Trading │ │Research│ │ Portfolio  │  │
│  │ Plugin  │ │ Plugin │ │  Tracker   │  │
│  └─────────┘ └────────┘ └───────────┘  │
└─────────────────────────────────────────┘
```

### State the Trading Plugin Must Maintain

| State | Storage | Update Frequency |
|-------|---------|-----------------|
| **Open Positions** | In-memory + persistent JSON/SQLite | On every fill |
| **Pending Orders** | In-memory + persistent | On order place/cancel/fill |
| **P&L (realized + unrealized)** | Computed from positions + market data | On price update |
| **Market Data Cache** | In-memory (TTL-based) | Real-time via WebSocket |
| **Trade History** | Append-only log (JSONL) | On every fill |
| **Account Balance** | Cached, refreshed periodically | Every 30-60s |
| **Risk Metrics** | Computed (drawdown, exposure) | On position change |
| **Configuration** | File-based (JSON/YAML) | On manual update |

### Communication with Parent Agent

| Method | Use Case | Implementation |
|--------|----------|----------------|
| **Events (recommended)** | Trade signals, fills, alerts | EventEmitter / message bus. Plugin emits `trade.filled`, `risk.alert`, etc. |
| **Shared State** | Position/balance queries | Plugin exposes read-only state via getter methods or shared memory file |
| **Tool Registration** | On-demand actions | Plugin registers tools (`place_order`, `get_positions`) that the core agent can call |
| **Webhooks** | External signal ingestion | Plugin runs HTTP listener for TradingView alerts, etc. |

**Recommended for NEMO**: Register trading functions as tools the agent can invoke. Plugin maintains its own state, emits events for important changes, and the core agent's memory captures summaries.

### Boundary: Core Agent vs Trading Plugin

| Core Agent Responsibilities | Trading Plugin Responsibilities |
|----------------------------|-------------------------------|
| Strategy decisions ("should I buy?") | Order execution mechanics |
| Risk approval ("is this within limits?") | Exchange API communication |
| User communication | Position tracking |
| Memory / learning | Market data streaming |
| Scheduling / cron triggers | Order book management |
| Multi-plugin coordination | Fill reconciliation |
| High-level portfolio allocation | Fee calculation |

**Principle**: The core agent decides *what* to trade and *how much*. The trading plugin handles *how* to execute and *tracks* the results.

### Open-Source References

| Project | Description | URL |
|---------|-------------|-----|
| **Hummingbot** | Modular market-making / trading bot framework. Plugin architecture with strategies as modules. | [https://github.com/hummingbot/hummingbot](https://github.com/hummingbot/hummingbot) |
| **Freqtrade** | Python crypto trading bot with strategy plugins, backtesting, and REST API. | [https://github.com/freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) |
| **Jesse** | Python trading framework with modular strategy architecture. | [https://github.com/jesse-ai/jesse](https://github.com/jesse-ai/jesse) |
| **AutoGPT + Trading** | AutoGPT plugins for trading demonstrate sub-agent patterns. | [https://github.com/Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) |
| **CrewAI** | Multi-agent framework with tool-based architecture — good reference for agent ↔ plugin boundaries. | [https://github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) |
| **LangChain Tools** | Tool abstraction pattern for LLM agents; trading tools follow same interface. | [https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) |

### Recommended Architecture for NEMO Trading Plugin

```
extensions/trading/
├── package.json          # Plugin manifest
├── src/
│   ├── index.ts          # Plugin entry: registers tools + event handlers
│   ├── exchanges/
│   │   ├── coinbase.ts   # Coinbase API wrapper
│   │   └── kalshi.ts     # Kalshi API wrapper
│   ├── state/
│   │   ├── positions.ts  # Position tracker
│   │   ├── orders.ts     # Order manager
│   │   └── portfolio.ts  # P&L calculator
│   ├── risk/
│   │   └── limits.ts     # Risk checks (max position, drawdown)
│   ├── signals/
│   │   ├── copy.ts       # Copy-trading signal processor
│   │   └── webhook.ts    # Incoming webhook handler
│   └── tools/
│       ├── trade.ts      # place_order, cancel_order tools
│       ├── query.ts      # get_positions, get_balance tools
│       └── market.ts     # get_price, get_orderbook tools
├── data/
│   ├── trades.jsonl      # Trade log
│   └── state.json        # Persisted state
└── config.json           # Exchange keys, risk params
```

**Key design decisions**:
1. Each exchange is an adapter behind a common interface
2. Risk checks are mandatory middleware before any order
3. State persists to disk on every mutation (crash recovery)
4. Tools are the public API; internal state is encapsulated
5. Events flow up to core agent for logging/memory

---

## Summary & Next Steps

| Platform | Status | Priority Action |
|----------|--------|-----------------|
| **Coinbase Advanced** | Well-documented, official Python SDK | Get CDP API key, test with small USDC trades |
| **Kalshi** | Fully legal, API straightforward | Create account, fund with small amount, test demo API |
| **Copy Trading** | Architecture clear | Design signal format, build risk engine first |
| **Plugin Architecture** | Reference patterns available | Scaffold `extensions/trading/` with tool registration |

### Recommended Implementation Order

1. **Week 1**: Kalshi demo API integration (paper trading)
2. **Week 2**: Coinbase Advanced API integration (read-only first)
3. **Week 3**: Risk engine + position tracking
4. **Week 4**: Copy-trading signal processor
5. **Week 5**: Live trading with small capital ($50-100)
