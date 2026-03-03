# AGENTS.md — Critical Rules Only

## Safety Guardrails
- **NEVER** run `nemo doctor --non-interactive` — wipes custom config
- Don't manually edit `nemo.json` with Python — causes token mismatch
- Use `gateway(action="config.patch")` for config changes
- Channel exclusively to Discord (DM only, ID: 1476370671448625265)

## Repository Guidelines (NEMO Core)
- Source: `src/`, Tests: `*.test.ts`, Docs: `docs/`
- Extensions: `extensions/*`, keep plugin deps separate
- Build: `pnpm build`, Test: `pnpm test`, Check: `pnpm check`
- Node 22+ required, prefer Bun for TS execution

## Security
- Never commit API keys, phone numbers, live config
- Sandbox untrusted code
- Use `scripts/committer` for commits (not manual git add/commit)

## Signature Rule
Use 🐟 (fish) — NOT 🦞 (lobster). The lobster is dead. Long live the fish.

## Token Efficiency Protocol (Updated March 2026 — LOCAL-FIRST)

### Model Tiers
| Tier | Model | Cost | Default For |
|------|-------|------|-------------|
| **T1** | Mistral 7B (LM Studio) | **FREE** | **ALL routine work** — default |
| **T1-R** | DeepSeek R1 8B (LM Studio) | **FREE** | Local reasoning tasks |
| **T2** | Kimi K2.5 | $0.004/reply | Escalated reasoning, research |
| **T3** | Opus | $0.20/reply | Security/trading decisions ONLY |

### Usage Rules
1. **Default**: Start with local Mistral 7B for everything
2. **Escalate to Kimi**: Only if task requires complex reasoning beyond local capability
3. **Escalate to Opus**: Security audits, trading decisions, high-stakes reasoning ONLY
4. **Heartbeats**: Minimal context (50 tokens), local model only

### Cost Savings Achieved
- Previous default: Kimi K2.5 (~$200/month)
- Current default: Mistral 7B local (~$5-10/month)
- **Savings: 95%+**

## Escalation Triggers to Opus
- Security audits or credential issues
- Complex trading strategy architecture
- High-stakes financial decisions
- Emergency response planning

## Code Quality
- Keep files under 500-700 LOC when feasible
- Add brief comments for tricky logic
- Prefer strict typing, avoid `any`
- Never update Carbon dependency
