#!/usr/bin/env bash
# trading-analysis.sh — Post-session trading analysis
# Usage: ./trading-analysis.sh [log_path] [session_name]

LOG_PATH="${1:-/tmp/nemo-trading-fixed.log}"
SESSION_NAME="${2:-$(date '+%Y-%m-%d-%H%M')}"
OUTPUT_DIR="${3:-~/.nemo/workspace/trading/nemo-trading/analysis}"

mkdir -p "$OUTPUT_DIR"
OUTPUT_FILE="$OUTPUT_DIR/session-analysis-$SESSION_NAME.md"

echo "=== Trading Session Analysis ==="
echo "Log: $LOG_PATH"
echo "Session: $SESSION_NAME"
echo "Output: $OUTPUT_FILE"
echo ""

# Check log exists
if [ ! -f "$LOG_PATH" ]; then
    echo "❌ Log file not found: $LOG_PATH"
    exit 1
fi

# Extract basic metrics
echo "📊 Extracting metrics..."
START_TIME=$(head -1 "$LOG_PATH" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
END_TIME=$(tail -1 "$LOG_PATH" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
TOTAL_LINES=$(wc -l < "$LOG_PATH")

# Count trades
TRADES=$(grep -c "entry filled" "$LOG_PATH" 2>/dev/null || echo "0")
POSITIONS=$(grep -c "Position opened" "$LOG_PATH" 2>/dev/null || echo "0")

# Count errors and warnings
ERRORS=$(grep -c "ERROR" "$LOG_PATH" 2>/dev/null || echo "0")
WARNINGS=$(grep -c "WARNING" "$LOG_PATH" 2>/dev/null || echo "0")
VPIN_KILLS=$(grep -c "VPIN KILL" "$LOG_PATH" 2>/dev/null || echo "0")

# Get latest metrics
LATEST_METRIC=$(grep -E "Balance:|P&L:|Trades:|Win Rate:" "$LOG_PATH" | tail -1)
BALANCE=$(echo "$LATEST_METRIC" | grep -oE '\$[0-9.]+' | head -1 | tr -d '$')
PNL=$(echo "$LATEST_METRIC" | grep -oE 'P&L: \$[^|]+' || echo "N/A")
WIN_RATE=$(echo "$LATEST_METRIC" | grep -oE 'Win Rate: [^|]+' || echo "N/A")

# Calculate error rate
CYCLES=$(grep -c "cycle" "$LOG_PATH" 2>/dev/null || echo "1")
ERROR_RATE=$(echo "scale=2; ($ERRORS / $CYCLES) * 100" | bc 2>/dev/null || echo "0")

# Generate report
cat > "$OUTPUT_FILE" << EOF
# Trading Session Analysis — $SESSION_NAME

## Session Info
| Metric | Value |
|--------|-------|
| Log File | $LOG_PATH |
| Start | $START_TIME |
| End | $END_TIME |
| Total Lines | $TOTAL_LINES |

## Performance Summary
| Metric | Value |
|--------|-------|
| Trades Executed | $TRADES |
| Positions Opened | $POSITIONS |
| Final Balance | \$$BALANCE |
| $PNL |
| $WIN_RATE |

## Issues & Warnings
| Type | Count |
|------|-------|
| Errors | $ERRORS |
| Warnings | $WARNINGS |
| VPIN Kill Switches | $VPIN_KILLS |
| Error Rate | ${ERROR_RATE}% |

## Error Analysis
EOF

if [ "$ERRORS" -gt 0 ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "### Errors Found" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    grep "ERROR" "$LOG_PATH" | tail -10 >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Categorize errors
    DIV_BY_ZERO=$(grep -c "division by zero" "$LOG_PATH" 2>/dev/null || echo "0")
    API_ERRORS=$(grep -c "API error\|Connection" "$LOG_PATH" 2>/dev/null || echo "0")
    STRATEGY_ERRORS=$(grep -c "Strategy error" "$LOG_PATH" 2>/dev/null || echo "0")
    
    echo "| Error Type | Count |" >> "$OUTPUT_FILE"
    echo "|------------|-------|" >> "$OUTPUT_FILE"
    echo "| Division by Zero | $DIV_BY_ZERO |" >> "$OUTPUT_FILE"
    echo "| API/Connection | $API_ERRORS |" >> "$OUTPUT_FILE"
    echo "| Strategy | $STRATEGY_ERRORS |" >> "$OUTPUT_FILE"
else
    echo "✅ No errors detected in this session." >> "$OUTPUT_FILE"
fi

# Warning analysis
echo "" >> "$OUTPUT_FILE"
echo "## Warning Analysis" >> "$OUTPUT_FILE"

VPIN_ALERTS=$(grep -c "VPIN Alert" "$LOG_PATH" 2>/dev/null || echo "0")
echo "" >> "$OUTPUT_FILE"
echo "- VPIN Alerts: $VPIN_ALERTS" >> "$OUTPUT_FILE"

if [ "$VPIN_ALERTS" -gt 0 ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "### VPIN Activity" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    grep "VPIN Alert" "$LOG_PATH" | tail -5 >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
fi

# Trade analysis
echo "" >> "$OUTPUT_FILE"
echo "## Trade Patterns" >> "$OUTPUT_FILE"

if [ "$TRADES" -gt 0 ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "### Recent Trades" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    grep "entry filled" "$LOG_PATH" | tail -10 >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    
    # Analyze snipe signals
    SNIPE_SIGNALS=$(grep -c "SNIPE SIGNAL" "$LOG_PATH" 2>/dev/null || echo "0")
    echo "" >> "$OUTPUT_FILE"
    echo "- Snipe Signals Detected: $SNIPE_SIGNALS" >> "$OUTPUT_FILE"
else
    echo "⚠️ No trades executed in this session." >> "$OUTPUT_FILE"
fi

# Generate recommendations
echo "" >> "$OUTPUT_FILE"
echo "## Recommendations" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ "$ERRORS" -gt 5 ]; then
    echo "🔴 **High Error Rate**: ${ERROR_RATE}% errors detected. Investigate and fix before next session." >> "$OUTPUT_FILE"
fi

if [ "$VPIN_KILLS" -gt 10 ]; then
    echo "🟡 **Frequent VPIN Kills**: Consider reducing trade frequency or adjusting VPIN threshold." >> "$OUTPUT_FILE"
fi

if [ "$TRADES" -eq 0 ]; then
    echo "🟡 **No Trades**: Check if entry criteria are too strict or market conditions were unfavorable." >> "$OUTPUT_FILE"
fi

if [ "$ERRORS" -eq 0 ] && [ "$TRADES" -gt 0 ]; then
    echo "✅ **Session looks healthy**. Continue monitoring for patterns." >> "$OUTPUT_FILE"
fi

# Raw data appendix
echo "" >> "$OUTPUT_FILE"
echo "## Raw Log Sample" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
tail -20 "$LOG_PATH" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"

echo ""
echo "✅ Analysis complete: $OUTPUT_FILE"
echo ""
cat "$OUTPUT_FILE"
