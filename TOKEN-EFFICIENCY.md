# TOKEN-EFFICIENCY.md — Cost Optimization Rules

## Model Routing Strategy

| Task Type | Model | Cost | Notes |
|-----------|-------|------|-------|
| Main conversation | Opus | $$$ | Complex reasoning, King interaction |
| Sub-agents | Kimi K2.5 | ~$0.004/task | `moonshot/kimi-k2.5` |
| Cron jobs | Kimi K2.5 | ~$0.004/task | Daily security audit etc. |
| Embeddings | Nomic Embed | FREE | LM Studio localhost:1234 |
| Memory search | Nomic Embed | FREE | Local embeddings |

## Kimi K2.5 Details
- **Provider:** moonshot
- **Base URL:** https://api.moonshot.ai/v1
- **Pricing:** $0.60/MTok in, $3.00/MTok out (~50x cheaper than Opus)
- **Models:** `kimi-k2.5` (non-reasoning), `kimi-k2-thinking` (reasoning)
- **API Key:** Configured in gateway env `MOONSHOT_API_KEY`

## Browser Efficiency Rules
- Always use `compact: true` for snapshots
- Keep `maxChars` between 800-1500
- Use `grep`/`head`/`tail` before full file reads
- Keep replies concise

## LM Studio (localhost:1234)
- DeepSeek R1 8B — local reasoning
- Mistral 7B — general tasks
- Qwen3 VL 8B — vision tasks
- Nomic Embed Text v1.5 — embeddings (always loaded)

## Gateway Config
- `memorySearch.remote.baseUrl` → LM Studio for free embeddings
- `compaction.memoryFlush.enabled: true`
- `memorySearch.experimental.sessionMemory: true`
- Sub-agent model routing via `agents.defaults.models` allowlist
