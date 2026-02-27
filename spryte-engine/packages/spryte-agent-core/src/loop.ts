import type { LLMProvider, StreamChunk } from '@spryte/ai';
import type {
  AgentConfig,
  Message,
  Tool,
  ToolCall,
  ToolResult,
  LoopOptions,
} from './types.js';
import { StateManager } from './state.js';

export class AgentLoop {
  private state: StateManager;
  private provider: LLMProvider;
  private config: AgentConfig;
  private tools: Map<string, Tool>;
  private toolImplementations: Map<string, (args: Record<string, unknown>) => Promise<string>>;

  constructor(config: AgentConfig, provider: LLMProvider) {
    this.config = config;
    this.provider = provider;
    this.state = new StateManager(config.systemPrompt);
    this.tools = new Map();
    this.toolImplementations = new Map();

    // Register tools
    config.tools?.forEach((tool) => {
      this.tools.set(tool.name, tool);
    });
  }

  registerTool(
    name: string,
    tool: Tool,
    implementation: (args: Record<string, unknown>) => Promise<string>
  ): void {
    this.tools.set(name, tool);
    this.toolImplementations.set(name, implementation);
  }

  async *run(input: string, options: LoopOptions = {}): AsyncGenerator<string, void, unknown> {
    const { maxIterations = 10 } = options;

    // Add user message
    this.state.addUserMessage(input);
    this.state.setProcessing(true);

    try {
      for (let iteration = 0; iteration < maxIterations; iteration++) {
        // Stream LLM response
        const stream = this.provider.stream({
          messages: this.state.messages,
          tools: Array.from(this.tools.values()),
          model: this.config.model,
          maxTokens: this.config.maxTokens,
          temperature: this.config.temperature,
        });

        let assistantContent = '';
        let toolCalls: ToolCall[] = [];

        for await (const chunk of stream) {
          if (chunk.type === 'text') {
            assistantContent += chunk.content;
            yield chunk.content;
          } else if (chunk.type === 'tool_call') {
            toolCalls.push(chunk.tool_call);
          }
        }

        // Add assistant message to state
        this.state.addAssistantMessage(assistantContent, toolCalls.length > 0 ? toolCalls : undefined);

        // Execute tools if any
        if (toolCalls.length === 0) {
          break; // No tools called, we're done
        }

        // Execute tools and add results
        for (const toolCall of toolCalls) {
          const result = await this.executeTool(toolCall);
          this.state.addToolResult(result);
          
          // Yield tool execution notice
          yield `\n[Executing ${toolCall.function.name}]\n`;
        }

        // Check for steering mode
        if (this.config.mode === 'steering' && this.state.hasSteeringQueued()) {
          const steeringInput = this.state.dequeueSteering();
          if (steeringInput) {
            this.state.addUserMessage(`[Steering] ${steeringInput}`);
          }
        }
      }
    } finally {
      this.state.setProcessing(false);
    }
  }

  private async executeTool(toolCall: ToolCall): Promise<ToolResult> {
    const { name } = toolCall.function;
    const implementation = this.toolImplementations.get(name);

    if (!implementation) {
      return {
        tool_call_id: toolCall.id,
        role: 'tool',
        name,
        content: `Error: Tool ${name} not implemented`,
      };
    }

    try {
      const args = JSON.parse(toolCall.function.arguments);
      const result = await implementation(args);
      return {
        tool_call_id: toolCall.id,
        role: 'tool',
        name,
        content: result,
      };
    } catch (error) {
      return {
        tool_call_id: toolCall.id,
        role: 'tool',
        name,
        content: `Error: ${error instanceof Error ? error.message : String(error)}`,
      };
    }
  }

  getMessages(): Message[] {
    return this.state.messages;
  }

  clear(): void {
    this.state.clear();
  }
}
