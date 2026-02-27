#!/usr/bin/env bash
# live-toggle.sh — Safely toggle live trading on/off
# Usage: ./live-toggle.sh [on|off|status] [safety_key]

CONFIG_FILE="${CONFIG_FILE:-config.py}"
ENV_FILE="${ENV_FILE:-.env}"

cd "$(dirname "$0")" || exit 1

show_status() {
    echo "=== Live Trading Status ==="
    
    # Check if config has live trading enabled
    if grep -q "live_trading_enabled:.*True" config.py 2>/dev/null; then
        echo "🟢 Live Trading: ENABLED"
    else
        echo "🟡 Live Trading: DISABLED (dry-run mode)"
    fi
    
    # Check if safety key is set
    if grep -q "LIVE_TRADING_SAFETY_KEY" .env 2>/dev/null; then
        echo "✅ Safety key: SET"
    else
        echo "⚠️  Safety key: NOT SET"
    fi
    
    # Check dry_run
    if grep -q "dry_run.*=.*True" config.py 2>/dev/null; then
        echo "✅ Dry run: ACTIVE (safe mode)"
    else
        echo "🔴 Dry run: OFF (live mode possible)"
    fi
    
    echo ""
    echo "To enable live trading:"
    echo "  1. Set LIVE_TRADING_SAFETY_KEY in .env"
    echo "  2. Run: ./live-toggle.sh on YOUR_SAFETY_KEY"
    echo ""
    echo "To disable live trading:"
    echo "  Run: ./live-toggle.sh off"
}

enable_live() {
    SAFETY_KEY="$1"
    
    if [ -z "$SAFETY_KEY" ]; then
        echo "❌ Error: Safety key required"
        echo "Usage: ./live-toggle.sh on YOUR_SAFETY_KEY"
        exit 1
    fi
    
    # Verify safety key matches
    if ! grep -q "LIVE_TRADING_SAFETY_KEY=$SAFETY_KEY" .env 2>/dev/null; then
        echo "❌ Error: Safety key does not match .env"
        echo "Check LIVE_TRADING_SAFETY_KEY in your .env file"
        exit 1
    fi
    
    echo "🔴 ENABLING LIVE TRADING 🔴"
    echo ""
    echo "⚠️  WARNING: Real money will be at risk!"
    echo ""
    echo "Current settings:"
    grep "daily_loss_limit\|max_drawdown" config.py | head -2
    echo ""
    
    read -p "Are you sure? Type 'YES' to confirm: " CONFIRM
    
    if [ "$CONFIRM" != "YES" ]; then
        echo "❌ Cancelled. Live trading NOT enabled."
        exit 0
    fi
    
    # Enable live trading in config
    sed -i '' 's/live_trading_enabled:.*=.*/live_trading_enabled: bool = True/' config.py 2>/dev/null || \
    sed -i 's/live_trading_enabled:.*=.*/live_trading_enabled: bool = True/' config.py
    
    # Disable dry_run
    sed -i '' 's/dry_run.*=.*True/dry_run: bool = False/' config.py 2>/dev/null || \
    sed -i 's/dry_run.*=.*True/dry_run: bool = False/' config.py
    
    echo ""
    echo "✅ Live trading ENABLED"
    echo "🚨 BOT WILL TRADE WITH REAL MONEY ON NEXT START"
    echo ""
    echo "To disable: ./live-toggle.sh off"
}

disable_live() {
    echo "🟡 Disabling live trading..."
    
    # Disable live trading
    sed -i '' 's/live_trading_enabled:.*=.*/live_trading_enabled: bool = False/' config.py 2>/dev/null || \
    sed -i 's/live_trading_enabled:.*=.*/live_trading_enabled: bool = False/' config.py
    
    # Enable dry_run
    sed -i '' 's/dry_run.*=.*False/dry_run: bool = True/' config.py 2>/dev/null || \
    sed -i 's/dry_run.*=.*False/dry_run: bool = True/' config.py
    
    echo "✅ Live trading DISABLED"
    echo "✅ Dry-run mode ACTIVE (safe)"
}

# Main
case "${1:-status}" in
    on|enable)
        enable_live "$2"
        ;;
    off|disable)
        disable_live
        ;;
    status|*)
        show_status
        ;;
esac
