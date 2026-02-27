# Polymarket Trading Bot - VPN Deployment Guide

## Required VPN Settings

### Hosts to Whitelist
For proper operation, ensure the VPN allows traffic to:

1. **Polymarket CLOB API**
   - `clob.polymarket.com` (primary)
   - `api.polymarket.com`
   - `polymarket.com`

2. **Polygon Blockchain RPC**
   - `polygon-rpc.com` (default)
   - `rpc.ankr.com` (alternative)
   - `polygon.llamarpc.com` (alternative)

3. **Polymarket APIs**
   - `gamma-api.polymarket.com`
   - `data.polymarket.com`

### Port Requirements
- HTTPS (443): All API communication
- WebSocket (wss://): Real-time market data

### Geographic Considerations
- Polymarket is not available to users in certain jurisdictions
- VPN should terminate in a supported region (e.g., Canada, UK, EU)
- Verify your VPN exit node location before trading

## Wallet Credentials

### Required in .env file:
```bash
POLYMARKET_PRIVATE_KEY=0x...        # Your wallet private key
POLYMARKET_FUNDER=                  # Optional: delegated funder
```

### Proxy/Delegate Address
**Confirmed proxy address for delegated trading:**
```
0x6Ca15Ec1764A7cE16B7ada4eC29934923f756a8a
```

This address is used when:
- Trading through a proxy contract
- Delegating trade execution
- Using a Gnosis Safe or similar

## RPC Configuration for VPN

If default RPC is blocked, update `.env`:
```bash
# Option 1: Ankr (reliable)
POLYMARKET_RPC_URL=https://rpc.ankr.com/polygon

# Option 2: LlamaNodes
POLYMARKET_RPC_URL=https://polygon.llamarpc.com

# Option 3: QuickNode (requires API key)
POLYMARKET_RPC_URL=https://your-quicknode-endpoint
```

## Pre-Flight Checklist

Before running the bot:

- [ ] VPN connected and verified
- [ ] Can ping `clob.polymarket.com`
- [ ] `.env` file created from `.env.example`
- [ ] `POLYMARKET_PRIVATE_KEY` set (with 0x prefix)
- [ ] `RISK_MAX_TRADE_SIZE_USD` ≤ $10
- [ ] `RISK_STOP_LOSS_PCT` = 0.50 (50%, not 75%)
- [ ] `RISK_DAILY_LOSS_LIMIT_USD` active
- [ ] `DRY_RUN=true` for testing

## Testing Connectivity

```bash
# Test VPN connection
./run_polymarket.sh --check

# Test in dry-run mode
./run_polymarket.sh --dry-run

# Run live (requires confirmation)
./run_polymarket.sh --live
```

## Troubleshooting

### "Cannot reach clob.polymarket.com"
- Verify VPN is connected
- Check if host is blocked by firewall
- Try alternative DNS (8.8.8.8, 1.1.1.1)

### "Polygon RPC timeout"
- Switch to alternative RPC URL in .env
- Check VPN allows blockchain RPC traffic

### "API credentials error"
- Normal on first run - bot will derive credentials from private key
- Ensure private key has funds for gas
- Check chain_id matches your wallet (137 for Polygon mainnet)

## Emergency Stop

To immediately halt trading:
1. Press Ctrl+C to stop the bot
2. Cancel all open orders manually via Polymarket UI
3. Set `DRY_RUN=true` in .env before restarting
