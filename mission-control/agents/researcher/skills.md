# Research Agent Skills

## Purpose
Information gathering, web search, content extraction, and synthesis.

## Capabilities
- `web_search`: Search the web using Brave API
- `web_fetch`: Extract readable content from URLs
- `memory_search`: Search NEMO's memory files
- `read`: Read local files and documentation

## Best For
- Market research and competitive analysis
- Gathering intelligence on trading strategies
- Finding documentation and tutorials
- Synthesizing information from multiple sources

## Example Tasks
- "Research Polymarket fee structure changes"
- "Find profitable BTC trading strategies on X"
- "Gather documentation on Kalshi API"
- "Analyze competitor agent strategies"

## Output Format
```json
{
  "findings": [...],
  "sources": [...],
  "confidence": 0-1,
  "recommendations": [...]
}
```

## Cost Profile
- Avg task: $0.004
- Typical tasks/day: 20-50
- Daily budget: $5
