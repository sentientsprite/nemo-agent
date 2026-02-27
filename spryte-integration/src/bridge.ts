/**
 * Spryte Bridge - Integration layer for NEMO
 * 
 * Provides pi-agent-core compatible interface over Spryte Engine.
 * Allows gradual migration without breaking existing code.
 */

import { Agent, AgentLoop, StateManager } from '@spryte/agent-core';
import { AnthropicProvider, OpenAIProvider, registry } from '@spryte/ai';
import type { 
  AgentConfig as SpryteConfig, 
  Message, 
  Tool 
} from '@spryte/agent-core';

// Configuration types
export interface BridgeConfig {
  provider: 'anthropic' | 'openai' | 'moonshot';
  model: string;
  apiKey: string;
  tools?: Tool[];
  systemPrompt?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface ProcessOptions {
  stream?: boolean;
  timeout?: number;
  tools?: string[]; // Filter to specific tools
}

/**
 * SpryteBridge - Main integration class
 * 
 * Wraps Spryte Engine to provide pi-agent-core compatible interface.
 */
export class SpryteBridge {
  private agent: Agent;
  private loop: AgentLoop;
  private state: StateManager;
  private config: BridgeConfig;
  private tools: Map<string, Tool> = new Map();

  constructor(config: BridgeConfig) {
    this.config = config;
    
    // Initialize provider
    const provider = this.initializeProvider(config);
    
    // Create Spryte agent config
    const spryteConfig: SpryteConfig = {
      systemPrompt: config.systemPrompt,
      maxTokens: config.maxTokens || 4096,
      temperature: config.temperature ?? 0.7,
    };
    
    // Initialize components
    this.state = new StateManager(spryteConfig);
    this.loop = new AgentLoop(spryteConfig, provider);
    this.agent = new Agent(spryteConfig, provider);
    
    // Register tools
    if (config.tools) {
      config.tools.forEach(tool => this.registerTool(tool));
    }
  }

  /**
   * Initialize the appropriate LLM provider
   */
  private initializeProvider(config: BridgeConfig) {
    switch (config.provider) {
      case 'anthropic':
        return new AnthropicProvider({
          apiKey: config.apiKey,
          model: config.model,
        });
      
      case 'openai':
        return new OpenAIProvider({
          apiKey: config.apiKey,
          model: config.model,
        });
      
      case 'moonshot':
        // Use Anthropic provider with Moonshot endpoint
        return new AnthropicProvider({
          apiKey: config.apiKey,
          model: config.model,
          baseURL: 'https://api.moonshot.cn/v1',
        });
      
      default:
        throw new Error(`Unknown provider: ${config.provider}`);
    }
  }

  /**
   * Process a message (pi-agent-core compatible)
   * 
   * @param message - User message
   * @param options - Processing options
   * @returns Response text
   */
  async processMessage(message: string, options?: ProcessOptions): Promise<string> {
    try {
      // Filter tools if specified
      const activeTools = options?.tools 
        ? Array.from(this.tools.values()).filter(t => options.tools?.includes(t.name))
        : Array.from(this.tools.values());
      
      // Register active tools with agent
      activeTools.forEach(tool => {
        this.agent.registerTool(
          tool.name,
          tool,
          this.wrapToolHandler(tool.handler)
        );
      });

      // Process message
      let response = '';
      for await (const chunk of this.agent.process(message)) {
        response += chunk;
      }

      return response;
    } catch (error) {
      console.error('SpryteBridge.processMessage error:', error);
      throw error;
    }
  }

  /**
   * Stream a message response
   * 
   * @param message - User message
   * @yields Response chunks
   */
  async *streamMessage(message: string): AsyncGenerator<string> {
    yield* this.agent.process(message);
  }

  /**
   * Register a tool
   * 
   * @param tool - Tool definition
   */
  registerTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
    
    // Also register with agent
    this.agent.registerTool(
      tool.name,
      tool,
      this.wrapToolHandler(tool.handler)
    );
  }

  /**
   * Unregister a tool
   * 
   * @param name - Tool name
   */
  unregisterTool(name: string): void {
    this.tools.delete(name);
    // Note: Spryte doesn't support unregistering, but we can filter in processMessage
  }

  /**
   * Get conversation history
   * 
   * @returns Array of messages
   */
  getHistory(): Message[] {
    return this.agent.getMessages();
  }

  /**
   * Clear conversation history
   */
  clear(): void {
    this.agent.clear();
  }

  /**
   * Get conversation state
   * 
   * @returns Current state
   */
  getState() {
    return {
      messages: this.getHistory(),
      tools: Array.from(this.tools.keys()),
      config: this.config,
    };
  }

  /**
   * Wrap tool handler for Spryte compatibility
   * 
   * Spryte expects (args) => Promise<string>
   * Our tools might have different signatures
   */
  private wrapToolHandler(handler: Function) {
    return async (args: Record<string, unknown>): Promise<string> => {
      try {
        const result = await handler(args);
        
        // Convert result to string if needed
        if (typeof result === 'string') {
          return result;
        }
        
        return JSON.stringify(result, null, 2);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        return `Error: ${errorMessage}`;
      }
    };
  }
}

/**
 * Create a default bridge instance from environment
 */
export function createDefaultBridge(): SpryteBridge {
  const provider = process.env.LLM_PROVIDER || 'anthropic';
  const apiKey = process.env.ANTHROPIC_API_KEY || process.env.OPENAI_API_KEY || '';
  const model = process.env.LLM_MODEL || 'claude-opus-4';

  if (!apiKey) {
    throw new Error('No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.');
  }

  return new SpryteBridge({
    provider: provider as any,
    model,
    apiKey,
    systemPrompt: 'You are NEMO, an autonomous AI agent.',
  });
}

export default SpryteBridge;
