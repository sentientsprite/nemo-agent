#!/usr/bin/env bash
# trading-monitor.sh — Quick trading bot health check
# Usage: ./trading-monitor.sh [log_path]

LOG_PATH="${1:-/tmp/nemo-trading-fixed.log}"
PID_PATTERN="python.*main\.py.*polymarket"

echo "=== Trading Bot Health Check ==="
echo "Log: $LOG_PATH"
echo "Time: $(date)"
echo ""

# Check if process is running
echo "🔍 Process Status:"
PID=$(pgrep -f "$PID_PATTERN" | head -1)
if [ -n "$PID" ]; then
    echo "  Status: 🟢 RUNNING"
    echo "  PID: $PID"
    ps -p "$PID" -o etime= | xargs echo "  Runtime:"
    ps -p "$PID" -o %cpu= | xargs echo "  CPU:"
    ps -p "$PID" -o %mem= | xargs echo "  Memory:"
else
    echo "  Status: 🔴 STOPPED"
fi
echo ""

# Check log file exists
if [ ! -f "$LOG_PATH" ]; then
    echo "❌ Log file not found: $LOG_PATH"
    exit 1
fi

# Extract latest metrics
echo "📊 Latest Metrics:"
tail -100 "$LOG_PATH" | grep -E "Balance:" | tail -1 | sed 's/^/  /'
tail -100 "$LOG_PATH" | grep -E "Trades:" | tail -1 | sed 's/^/  /'
tail -100 "$LOG_PATH" | grep -E "Win Rate:" | tail -1 | sed 's/^/  /'
tail -100 "$LOG_PATH" | grep -E "VPIN:" | tail -1 | sed 's/^/  /'
echo ""

# Count errors (last hour)
echo "⚠️  Issues (Last Hour):"
HOUR=$(date '+%Y-%m-%d %H:')
ERRORS=$(grep "$HOUR" "$LOG_PATH" 2>/dev/null | grep -c "ERROR" || echo "0")
WARNINGS=$(grep "$HOUR" "$LOG_PATH" 2>/dev/null | grep -c "WARNING" || echo "0")
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

# Recent trades
echo "💰 Recent Trades:"
grep -E "(SNIPE SIGNAL|entry filled|Position opened)" "$LOG_PATH" | tail -5 | sed 's/^/  /'
echo ""

# VPIN status
echo "🛡️  VPIN Activity:"
VPIN_KILLS=$(grep -c "VPIN KILL SWITCH ACTIVATED" "$LOG_PATH" 2>/dev/null || echo "0")
echo "  Total kill switches: $VPIN_KILLS"
tail -50 "$LOG_PATH" | grep -E "VPIN Alert|kill switch" | tail -3 | sed 's/^/  /'
echo ""

# Last 3 log entries
echo "📝 Last 3 Log Entries:"
tail -3 "$LOG_PATH" | sed 's/^/  /'
