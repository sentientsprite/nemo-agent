import type { AgentConfig, Message, Tool, ToolResult } from './types.js';
import type { LLMProvider } from '@spryte/ai';
import { AgentLoop } from './loop.js';

export class Agent {
  private loop: AgentLoop;
  private config: AgentConfig;

  constructor(config: AgentConfig, provider: LLMProvider) {
    this.config = config;
    this.loop = new AgentLoop(config, provider);
  }

  /**
   * Process user input and stream the response
   */
  async *process(input: string): AsyncGenerator<string, void, unknown> {
    yield* this.loop.run(input);
  }

  /**
   * Register a tool with the agent
   */
  registerTool(
    name: string,
    tool: Tool,
    implementation: (args: Record<string, unknown>) => Promise<string>
  ): void {
    this.loop.registerTool(name, tool, implementation);
  }

  /**
   * Get conversation history
   */
  getMessages(): Message[] {
    return this.loop.getMessages();
  }

  /**
   * Clear conversation history (keep system prompt)
   */
  clear(): void {
    this.loop.clear();
  }

  /**
   * Queue a steering input (for steering mode)
   */
  steer(input: string): void {
    if (this.config.mode === 'steering') {
      // Steering logic handled in loop
      this.loop['state'].queueSteering(input);
    }
  }
}

export * from './types.js';
export { AgentLoop } from './loop.js';
export { StateManager } from './state.js';
