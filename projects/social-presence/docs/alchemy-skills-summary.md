# Alchemy Skills — Installation Summary

**Date:** 2026-02-26  
**Installed:** 2 skills from Alchemy Platform

---

## ✅ Installed Skills

### 1. `alchemy-api`
**Purpose:** Access Alchemy APIs with an API key  
**Location:** `~/.nemo/workspace/.agents/skills/alchemy-api/`  
**Security:** Snyk Med Risk

**Use When:**
- You have an `ALCHEMY_API_KEY` environment variable set
- Making standard Alchemy API calls (RPC, NFT, Prices, Portfolio)
- Want direct API access without authentication flows

**Supported APIs:**
| Product | Endpoint Pattern |
|---------|------------------|
| Ethereum RPC | `eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` |
| Base RPC | `base-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` |
| Arbitrum RPC | `arb-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` |
| Solana RPC | `solana-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY` |
| NFT API | `<network>.g.alchemy.com/nft/v3/$ALCHEMY_API_KEY` |
| Prices API | `api.g.alchemy.com/prices/v1/$ALCHEMY_API_KEY` |
| Portfolio API | `api.g.alchemy.com/data/v1/$ALCHEMY_API_KEY` |

**Quick Example:**
```bash
curl "https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

---

### 2. `agentic-gateway`
**Purpose:** Access Alchemy APIs WITHOUT an API key  
**Location:** `~/.nemo/workspace/.agents/skills/agentic-gateway/`  
**Security:** Snyk Med Risk

**Use When:**
- No `ALCHEMY_API_KEY` is set (default path)
- Want agent-autonomous authentication
- Willing to pay for API usage via x402 protocol (USDC on Base)

**Authentication Flow:**
1. **Wallet Setup** — Create/fund Ethereum wallet
2. **SIWE Token** — Sign-In With Ethereum authentication
3. **Payment** — x402 protocol handles per-request micropayments
4. **Request** — Send authenticated calls to gateway

**Gateway URLs:**
| Product | Gateway URL |
|---------|-------------|
| Node JSON-RPC | `https://x402.alchemy.com/{chainNetwork}/v2` |
| NFT API | `https://x402.alchemy.com/{chainNetwork}/nft/v3/*` |
| Prices API | `https://x402.alchemy.com/prices/v1/*` |
| Portfolio API | `https://x402.alchemy.com/data/v1/*` |

**Key Commands:**
```bash
# Install x402 CLI
npm install -g @alchemy/x402

# Create SIWE token
npx @alchemy/x402 sign-siwe --private-key ./wallet-key.txt

# Make authenticated request
npx @alchemy/x402 fetch https://x402.alchemy.com/eth-mainnet/v2 \
  -X POST \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

---

## 🔑 Required Setup

### Option A: API Key (Simpler)
1. Sign up at [alchemy.com](https://alchemy.com)
2. Create an app, copy API key
3. Set environment variable:
   ```bash
   export ALCHEMY_API_KEY="your_key_here"
   ```
4. Use `alchemy-api` skill

### Option B: Agentic Gateway (Autonomous)
1. Install `@alchemy/x402` CLI: `npm install -g @alchemy/x402`
2. Create/fund wallet with USDC on Base
3. Generate SIWE token
4. Use `agentic-gateway` skill (no API key needed)

---

## 📚 Reference Files

Both skills include detailed documentation:

### alchemy-api
- `references/node-json-rpc.md` — EVM RPC methods
- `references/node-websocket-subscriptions.md` — Realtime events
- `references/data-token-api.md` — Token balances/metadata
- `references/data-nft-api.md` — NFT ownership/metadata
- `references/data-prices-api.md` — Token prices
- `references/data-portfolio-apis.md` — Multi-chain portfolio
- `references/data-simulation-api.md` — Transaction simulation

### agentic-gateway
- `rules/wallet-bootstrap.md` — Wallet setup
- `rules/authentication.md` — SIWE token creation
- `rules/making-requests.md` — SDK integration
- `rules/payment.md` — x402 payment handling
- `rules/curl-workflow.md` — Quick command-line queries

---

## 🎯 Use Cases for NEMO

### Immediate Applications
1. **Portfolio Tracking** — Monitor wallet balances across chains
2. **Price Feeds** — Get real-time token prices (alternative to Chainlink)
3. **Transaction Simulation** — Test trades before executing
4. **NFT Analysis** — Track NFT holdings, values
5. **Multi-Chain Monitoring** — Base, Arbitrum, Ethereum in one API

### For Trading Bot
- Validate Polymarket transactions before signing
- Get faster price data for arbitrage detection
- Monitor gas prices across L2s
- Track USDC balances on Base for x402 payments

---

## ⚠️ Important Notes

1. **Skill Routing:** If `ALCHEMY_API_KEY` is set, use `alchemy-api`. If not, use `agentic-gateway`.
2. **No Mixing:** Don't mix behaviors from both skills in the same workflow.
3. **Wallet Security:** Never commit private keys to git. Use `.env` files.
4. **Cost Awareness:** Agentic gateway charges per-request via x402. API key has free tier limits.
5. **Testnet First:** Always test on Base Sepolia before mainnet.

---

## 🔗 Next Steps

1. **Choose Path:** API key (easier) or agentic gateway (more autonomous)?
2. **Set Up:** Follow wallet-bootstrap.md or get API key
3. **Test:** Run quick query to verify setup
4. **Integrate:** Use in NEMO trading bot for enhanced data

**Learn More:** https://skills.sh/alchemyplatform/skills
