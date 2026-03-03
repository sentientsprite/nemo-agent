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

## Token Efficiency Protocol
1. **Acknowledgments**: Use local model (Mistral via LM Studio) — FREE
2. **Routine tasks**: Use Kimi K2.5 — $0.004/reply
3. **High-level thinking**: Use Kimi first, escalate to Opus only if needed — $0.20/reply
4. **Heartbeats**: Minimal context (50 tokens), local model preferred

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
