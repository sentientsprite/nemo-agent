import Anthropic from '@anthropic-ai/sdk';
import type {
  LLMProvider,
  LLMRequest,
  Message,
  Tool,
  StreamChunk,
  ToolCall,
} from '../types.js';

export class AnthropicProvider implements LLMProvider {
  name = 'anthropic';
  private client: Anthropic;

  constructor(apiKey?: string) {
    this.client = new Anthropic({
      apiKey: apiKey || process.env.ANTHROPIC_API_KEY,
    });
  }

  async *stream(request: LLMRequest): AsyncGenerator<StreamChunk, void, unknown> {
    const messages = this.convertMessages(request.messages);
    const tools = request.tools?.map(this.convertTool);

    const stream = await this.client.messages.create({
      model: request.model,
      max_tokens: request.maxTokens || 4096,
      temperature: request.temperature ?? 0.7,
      messages,
      tools,
      stream: true,
    });

    for await (const chunk of stream) {
      if (chunk.type === 'content_block_delta') {
        if (chunk.delta.type === 'text_delta') {
          yield {
            type: 'text',
            content: chunk.delta.text,
          };
        }
      } else if (chunk.type === 'content_block_start') {
        if (chunk.content_block.type === 'tool_use') {
          yield {
            type: 'tool_call',
            tool_call: {
              id: chunk.content_block.id,
              type: 'function',
              function: {
                name: chunk.content_block.name,
                arguments: JSON.stringify(chunk.content_block.input),
              },
            },
          };
        }
      }
    }
  }

  async complete(request: LLMRequest): Promise<string> {
    const messages = this.convertMessages(request.messages);
    const tools = request.tools?.map(this.convertTool);

    const response = await this.client.messages.create({
      model: request.model,
      max_tokens: request.maxTokens || 4096,
      temperature: request.temperature ?? 0.7,
      messages,
      tools,
    });

    const content = response.content[0];
    if (content.type === 'text') {
      return content.text;
    }
    return '';
  }

  private convertMessages(messages: Message[]): Anthropic.MessageParam[] {
    return messages.map((m) => {
      if (m.role === 'tool') {
        return {
          role: 'user',
          content: [
            {
              type: 'tool_result',
              tool_use_id: m.tool_call_id || '',
              content: m.content,
            },
          ],
        };
      }
      return {
        role: m.role === 'system' ? 'user' : m.role,
        content: m.content,
      };
    });
  }

  private convertTool(tool: Tool): Anthropic.Tool {
    return {
      name: tool.function.name,
      description: tool.function.description,
      input_schema: tool.function.parameters as Anthropic.Tool.InputSchema,
    };
  }
}
