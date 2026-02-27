# Spryte Engine Core Replacement Plan

## Overview
Replace `@mariozechner/pi-agent-core` and `@mariozechner/pi-ai` with Spryte-native implementations.

## Current Dependencies

### pi-agent-core (~400 lines core)
- **Agent class**: State management, message queues, steering/follow-up modes
- **agent-loop**: Main LLM interaction loop with tool calling
- **proxy**: Attachment handling
- **types**: TypeScript interfaces

### pi-ai (~12K lines)
- **Provider abstractions**: Anthropic, OpenAI, Google, Azure, Vertex
- **Model registry**: Auto-discovery, configuration
- **Streaming**: Unified streaming interface
- **API registry**: Tool schema handling
- **Utils**: Validation, OAuth, event streaming

## Replacement Strategy

### Phase 1: pi-agent-core replacement (spryte-agent-core)
Create minimal agent loop with:
- State management (messages, tools, system prompt)
- Basic tool calling loop
- Streaming support
- Steering queue (one-at-a-time mode)

### Phase 2: pi-ai replacement (spryte-ai)
Create simplified LLM abstraction:
- Unified provider interface
- Anthropic + OpenAI providers (80% of use cases)
- Model selection/routing
- Basic streaming

### Phase 3: Integration
- Update imports in Spryte Engine
- Maintain backward compatibility
- Test with existing agents

## Architecture

```
spryte-agent-core/
├── agent.ts          # Main Agent class
├── loop.ts           # Agent execution loop
├── state.ts          # State management
└── types.ts          # Interfaces

spryte-ai/
├── index.ts          # Main exports
├── providers/
│   ├── anthropic.ts  # Claude API
│   ├── openai.ts     # OpenAI API
│   └── registry.ts   # Provider registration
├── models.ts         # Model definitions
├── stream.ts         # Streaming utilities
└── types.ts          # Shared types
```

## Key Design Decisions

1. **Simpler is better**: Don't replicate all features. Focus on what NEMO actually uses.
2. **TypeScript-first**: No compiled JS, source is TypeScript.
3. **Modern APIs**: Use latest provider SDKs (Anthropic SDK v0.73, OpenAI v4+)
4. **Streaming-native**: Built around streaming responses, not bolted on.
5. **Tool-first**: Design for function calling from the ground up.

## Implementation Notes

### Agent Loop Pseudocode
```typescript
async function agentLoop(agent: Agent, input: string) {
  // 1. Add user message
  agent.addMessage({ role: 'user', content: input });
  
  // 2. Stream LLM response
  for await (const chunk of llm.stream(agent.messages, agent.tools)) {
    if (chunk.type === 'text') yield chunk.content;
    if (chunk.type === 'tool_call') {
      // 3. Execute tool
      const result = await executeTool(chunk.tool, chunk.args);
      agent.addMessage({ role: 'tool', content: result });
      // 4. Continue loop
      yield* agentLoop(agent, null);
    }
  }
}
```

### Provider Interface
```typescript
interface Provider {
  name: string;
  stream(messages: Message[], tools: Tool[]): AsyncIterable<StreamChunk>;
  getModel(id: string): Model;
}
```

## Progress Tracking

- [ ] Create spryte-agent-core package structure
- [ ] Implement Agent class with state management
- [ ] Implement basic agent loop
- [ ] Create spryte-ai package structure
- [ ] Implement Anthropic provider
- [ ] Implement OpenAI provider
- [ ] Add model registry
- [ ] Test with simple agent
- [ ] Integrate into Spryte Engine
- [ ] Remove pi-* dependencies

## Status
**Current**: Planning complete — DEFERRED
**Phase 1 Done**: Architecture analysis, scoping, design document
**Phase 2 Deferred**: Implementation (spryte-agent-core, spryte-ai packages)
**Rationale**: ~13K lines to replace (pi-agent-core + pi-ai). Focus on using NEMO/OpenClaw effectively before building custom engine.

**When to Resume**:
- After mastering multi-agent patterns
- When specific limitations in pi-* packages block progress
- As a longer-term independence goal

**Reference**: Plan preserved for future implementation.
