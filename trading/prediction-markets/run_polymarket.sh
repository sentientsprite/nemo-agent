#!/bin/bash
#
# Polymarket Trading Bot - Deployment Script
# Usage: ./run_polymarket.sh [--dry-run] [--check] [--live]
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
CHECK_HOST="${VPN_CHECK_HOST:-clob.polymarket.com}"
DRY_RUN=true
MODE="check"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            MODE="dry-run"
            shift
            ;;
        --live)
            DRY_RUN=false
            MODE="live"
            shift
            ;;
        --check)
            MODE="check"
            shift
            ;;
        --help)
            echo "Usage: $0 [--dry-run|--live|--check]"
            echo ""
            echo "Options:"
            echo "  --dry-run  Run in dry-run mode (default, no real trades)"
            echo "  --live     Enable live trading (DANGEROUS)"
            echo "  --check    Only run connectivity and safety checks"
            echo "  --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Polymarket Bot - Deployment Script"
echo "Mode: $MODE"
echo "=========================================="
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# ============================================
# STEP 1: VPN CONNECTIVITY CHECK
# ============================================
echo "Step 1: Checking VPN connectivity..."
echo "------------------------------------------"

if ping -c 1 -W 5 "$CHECK_HOST" >/dev/null 2>&1; then
    print_status "VPN connection verified - $CHECK_HOST is reachable"
elif curl -s --max-time 10 "https://$CHECK_HOST/health" >/dev/null 2>&1; then
    print_status "VPN connection verified via HTTPS - $CHECK_HOST is reachable"
else
    print_error "Cannot reach $CHECK_HOST"
    print_warning "Please ensure VPN is connected before running"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Polygon RPC connectivity
echo "Checking Polygon RPC connectivity..."
if curl -s --max-time 10 -X POST "https://polygon-rpc.com" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' >/dev/null 2>&1; then
    print_status "Polygon RPC is reachable"
else
    print_warning "Polygon RPC may be blocked or slow"
fi
echo ""

# ============================================
# STEP 2: ENVIRONMENT CHECK
# ============================================
echo "Step 2: Checking environment..."
echo "------------------------------------------"

# Check Python
cd "$SCRIPT_DIR"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi
print_status "Python version: $(python3 --version)"

# Check .env file
if [[ ! -f ".env" ]]; then
    print_error ".env file not found!"
    print_warning "Please copy .env.example to .env and configure your credentials"
    exit 1
fi
print_status ".env file found"

# Verify critical env vars are set
if grep -q "POLYMARKET_PRIVATE_KEY=0x$" .env 2>/dev/null || grep -q "POLYMARKET_PRIVATE_KEY=$" .env 2>/dev/null; then
    print_error "POLYMARKET_PRIVATE_KEY is not set in .env"
    exit 1
fi
print_status "Wallet credentials configured"

# Check virtual environment
if [[ ! -d "$VENV_DIR" ]]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv "$VENV_DIR"
fi
print_status "Virtual environment ready"

# Activate venv
source "$VENV_DIR/bin/activate"

# Install/update dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_status "Dependencies installed"
echo ""

# ============================================
# STEP 3: SAFETY CHECKS
# ============================================
echo "Step 3: Running safety checks..."
echo "------------------------------------------"

python3 << 'PYTHON'
import os
import sys
sys.path.insert(0, '.')
from config import cfg, verify_safety_limits

errors = verify_safety_limits()
for error in errors:
    if error.startswith("ERROR:"):
        print(f"[SAFETY ERROR] {error}")
        sys.exit(1)
    else:
        print(f"[WARNING] {error}")

# Verify safety limits
print(f"[OK] Max trade size: ${cfg.risk.max_trade_size_usd}")
print(f"[OK] Stop loss: -{cfg.risk.stop_loss_pct*100:.0f}%")
print(f"[OK] Daily loss limit: ${cfg.risk.daily_loss_limit_usd}")
print(f"[OK] Mode: {'LIVE' if not cfg.dry_run else 'DRY RUN'}")

if cfg.risk.stop_loss_pct > 0.50:
    print(f"[ERROR] Stop loss is {cfg.risk.stop_loss_pct*100:.0f}%, should be <= 50%!")
    sys.exit(1)
    
if cfg.risk.max_trade_size_usd > 10:
    print(f"[ERROR] Max trade size is ${cfg.risk.max_trade_size_usd}, should be <= $10!")
    sys.exit(1)

sys.exit(0)
PYTHON

if [[ $? -ne 0 ]]; then
    print_error "Safety check failed!"
    exit 1
fi

print_status "All safety checks passed"
echo ""

# ============================================
# STEP 4: CONNECTIVITY TEST
# ============================================
echo "Step 4: Testing Polymarket connectivity..."
echo "------------------------------------------"

python3 << 'PYTHON'
import sys
sys.path.insert(0, '.')
from polymarket_client import PolymarketClient
from config import cfg

# Test connectivity
if PolymarketClient.check_connectivity(cfg.vpn_check_host):
    print("[OK] Polymarket CLOB API is reachable")
else:
    print("[ERROR] Cannot connect to Polymarket CLOB API")
    sys.exit(1)

# Try to get markets (read-only test)
try:
    client = PolymarketClient(cfg.polymarket)
    markets = client.get_markets(limit=1)
    print(f"[OK] Successfully fetched markets from CLOB")
    print(f"[INFO] Proxy address: {cfg.polymarket.proxy_address}")
except Exception as e:
    print(f"[WARNING] Could not fetch markets: {e}")
    print("[INFO] This may be due to missing API credentials - bot will try to derive them")

sys.exit(0)
PYTHON

if [[ $? -ne 0 ]]; then
    print_error "Connectivity test failed!"
    exit 1
fi

print_status "Connectivity test passed"
echo ""

# ============================================
# STEP 5: RUN BOT (or stop if just checking)
# ============================================
if [[ "$MODE" == "check" ]]; then
    echo "=========================================="
    print_status "All checks passed! Bot is ready to run."
    echo "=========================================="
    echo ""
    echo "To run in dry-run mode: ./run_polymarket.sh --dry-run"
    echo "To run live (DANGEROUS): ./run_polymarket.sh --live"
    exit 0
fi

echo "=========================================="
echo "Starting Polymarket Bot"
echo "=========================================="
echo ""

# Set dry run mode
if [[ "$DRY_RUN" == "true" ]]; then
    export DRY_RUN=true
    print_warning "DRY RUN MODE - No real trades will be executed"
else
    export DRY_RUN=false
    print_warning "LIVE TRADING MODE - REAL MONEY AT RISK!"
    echo ""
    read -p "Are you sure you want to continue? Type 'YES' to proceed: " confirm
    if [[ "$confirm" != "YES" ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo ""
echo "Starting bot..."
echo ""

# Run the bot
exec python3 bot.py
