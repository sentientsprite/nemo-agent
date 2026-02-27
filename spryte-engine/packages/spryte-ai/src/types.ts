/**
 * Spryte AI - Unified LLM provider abstraction
 * Replaces @mariozechner/pi-ai
 */

export interface Message {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
  tool_call_id?: string;
}

export interface Tool {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: Record<string, unknown>;
  };
}

export interface ToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

export interface StreamChunk {
  type: 'text' | 'tool_call';
  content?: string;
  tool_call?: ToolCall;
}

export interface LLMRequest {
  messages: Message[];
  tools?: Tool[];
  model: string;
  maxTokens?: number;
  temperature?: number;
}

export interface LLMProvider {
  name: string;
  stream(request: LLMRequest): AsyncGenerator<StreamChunk, void, unknown>;
  complete(request: LLMRequest): Promise<string>;
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  contextWindow: number;
  maxTokens: number;
  supportsTools: boolean;
  supportsStreaming: boolean;
}
