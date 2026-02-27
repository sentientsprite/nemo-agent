# Spryte Engine Codebase Map

Source: `~/spryte-engine/` (forked from OpenClaw v2026.2.12, MIT licensed)

## Key Files
- `src/agents/system-prompt.ts` — SOUL.md injection at line ~560
- `src/plugins/registry.ts` — registerTool at line ~168
- `src/agents/skills/workspace.ts` — loadSkillEntries at line ~101
- `src/discord/` — Discord integration directory
- `src/config/` — Configuration system
- `src/gateway/` — Gateway server
- `src/auto-reply/` — Message handling and reply logic

## Architecture
- TypeScript ESM codebase (~490K lines in src/)
- Plugin-based architecture with extension system
- Multi-channel support (Discord, Telegram, Signal, Slack, WhatsApp, iMessage)
- Embedded AI agent with tool system
- Session management with transcript persistence
- Memory system with vector embeddings

## Independence Plan
1. Replace pi-agent-core (307 lines) — core agent loop
2. Replace pi-ai — LLM abstraction layer
3. Custom tool registry
4. Custom personality system
5. Independent update mechanism
