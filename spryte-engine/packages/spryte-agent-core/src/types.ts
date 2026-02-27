/**
 * Spryte Agent Core - Minimal agent loop implementation
 * Replaces @mariozechner/pi-agent-core
 */

export interface Message {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
  tool_calls?: ToolCall[];
  tool_call_id?: string;
}

export interface ToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

export interface ToolResult {
  tool_call_id: string;
  role: 'tool';
  name: string;
  content: string;
}

export interface AgentConfig {
  name: string;
  systemPrompt: string;
  model: string;
  maxTokens?: number;
  temperature?: number;
  tools?: Tool[];
  mode?: 'steering' | 'follow-up';
}

export interface AgentState {
  messages: Message[];
  isProcessing: boolean;
  steeringQueue: string[];
}

export interface LoopOptions {
  maxIterations?: number;
  timeoutMs?: number;
}
