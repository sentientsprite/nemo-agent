import type { Message, ToolResult, AgentState } from './types.js';

export class StateManager {
  private state: AgentState;

  constructor(systemPrompt: string) {
    this.state = {
      messages: [{ role: 'system', content: systemPrompt }],
      isProcessing: false,
      steeringQueue: [],
    };
  }

  get messages(): Message[] {
    return this.state.messages;
  }

  get isProcessing(): boolean {
    return this.state.isProcessing;
  }

  setProcessing(value: boolean): void {
    this.state.isProcessing = value;
  }

  addUserMessage(content: string): void {
    this.state.messages.push({ role: 'user', content });
  }

  addAssistantMessage(content: string, toolCalls?: ToolCall[]): void {
    this.state.messages.push({
      role: 'assistant',
      content,
      tool_calls: toolCalls,
    });
  }

  addToolResult(result: ToolResult): void {
    this.state.messages.push({
      role: 'tool',
      content: result.content,
      name: result.name,
      tool_call_id: result.tool_call_id,
    });
  }

  queueSteering(input: string): void {
    this.state.steeringQueue.push(input);
  }

  dequeueSteering(): string | undefined {
    return this.state.steeringQueue.shift();
  }

  hasSteeringQueued(): boolean {
    return this.state.steeringQueue.length > 0;
  }

  clear(): void {
    const systemPrompt = this.state.messages[0];
    this.state.messages = [systemPrompt];
    this.state.isProcessing = false;
    this.state.steeringQueue = [];
  }

  getContextWindow(): number {
    // Rough token estimation: 4 chars per token
    const totalChars = this.state.messages.reduce((acc, m) => acc + m.content.length, 0);
    return Math.floor(totalChars / 4);
  }
}

import type { ToolCall } from './types.js';
