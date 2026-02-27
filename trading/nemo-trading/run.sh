#!/bin/bash
# NEMO Trading — Run Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

# Setup venv if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install deps if needed
if [ ! -f "venv/.deps_installed" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -q -r requirements.txt
    touch venv/.deps_installed
fi

# Check .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env not found. Copying from .env.example${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env with your API keys before live trading${NC}"
fi

# Parse arguments
PRESET=""
LIVE=""
STRATEGY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --preset)
            PRESET="--preset $2"
            shift 2
            ;;
        --live)
            LIVE="--live"
            shift
            ;;
        --strategy)
            STRATEGY="--strategy $2"
            shift 2
            ;;
        --help)
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --preset <name>     Use predefined config (coinbase_momentum, polymarket_snipe, etc.)"
            echo "  --strategy <name>   Override strategy (momentum, snipe, crowd_fade, copy)"
            echo "  --live              Enable live trading (default: dry-run)"
            echo "  --help              Show this help"
            echo ""
            echo "Examples:"
            echo "  ./run.sh --preset polymarket_snipe"
            echo "  ./run.sh --preset polymarket_snipe --live"
            echo "  ./run.sh --exchange polymarket --strategy snipe"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Confirm live trading
if [ -n "$LIVE" ]; then
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  WARNING: LIVE TRADING MODE                           ║${NC}"
    echo -e "${RED}║  Real money will be used!                             ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    read -p "Type YES to confirm: " confirm
    if [ "$confirm" != "YES" ]; then
        echo -e "${YELLOW}Aborted.${NC}"
        exit 1
    fi
fi

# Run bot
echo -e "${GREEN}Starting NEMO Trading Bot...${NC}"
python main.py $PRESET $LIVE $STRATEGY "$@"
