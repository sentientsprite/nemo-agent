import OpenAI from 'openai';
import type {
  LLMProvider,
  LLMRequest,
  Message,
  Tool,
  StreamChunk,
} from '../types.js';

export class OpenAIProvider implements LLMProvider {
  name = 'openai';
  private client: OpenAI;

  constructor(apiKey?: string) {
    this.client = new OpenAI({
      apiKey: apiKey || process.env.OPENAI_API_KEY,
    });
  }

  async *stream(request: LLMRequest): AsyncGenerator<StreamChunk, void, unknown> {
    const messages = this.convertMessages(request.messages);
    const tools = request.tools?.map(this.convertTool);

    const stream = await this.client.chat.completions.create({
      model: request.model,
      max_tokens: request.maxTokens,
      temperature: request.temperature,
      messages,
      tools: tools?.length ? tools : undefined,
      stream: true,
    });

    let currentToolCall: {
      id: string;
      name: string;
      arguments: string;
    } | null = null;

    for await (const chunk of stream) {
      const delta = chunk.choices[0]?.delta;

      // Handle content
      if (delta?.content) {
        yield {
          type: 'text',
          content: delta.content,
        };
      }

      // Handle tool calls
      if (delta?.tool_calls) {
        for (const toolCall of delta.tool_calls) {
          if (toolCall.id) {
            // New tool call starting
            if (currentToolCall) {
              // Emit previous tool call
              yield {
                type: 'tool_call',
                tool_call: {
                  id: currentToolCall.id,
                  type: 'function',
                  function: {
                    name: currentToolCall.name,
                    arguments: currentToolCall.arguments,
                  },
                },
              };
            }
            currentToolCall = {
              id: toolCall.id,
              name: toolCall.function?.name || '',
              arguments: toolCall.function?.arguments || '',
            };
          } else if (currentToolCall && toolCall.function?.arguments) {
            // Continue building arguments
            currentToolCall.arguments += toolCall.function.arguments;
          }
        }
      }
    }

    // Emit final tool call if any
    if (currentToolCall) {
      yield {
        type: 'tool_call',
        tool_call: {
          id: currentToolCall.id,
          type: 'function',
          function: {
            name: currentToolCall.name,
            arguments: currentToolCall.arguments,
          },
        },
      };
    }
  }

  async complete(request: LLMRequest): Promise<string> {
    const messages = this.convertMessages(request.messages);
    const tools = request.tools?.map(this.convertTool);

    const response = await this.client.chat.completions.create({
      model: request.model,
      max_tokens: request.maxTokens,
      temperature: request.temperature,
      messages,
      tools: tools?.length ? tools : undefined,
    });

    return response.choices[0]?.message?.content || '';
  }

  private convertMessages(messages: Message[]): OpenAI.Chat.ChatCompletionMessageParam[] {
    return messages.map((m) => {
      if (m.role === 'tool') {
        return {
          role: 'tool',
          tool_call_id: m.tool_call_id || '',
          content: m.content,
        };
      }
      return {
        role: m.role,
        content: m.content,
        name: m.name,
      } as OpenAI.Chat.ChatCompletionMessageParam;
    });
  }

  private convertTool(tool: Tool): OpenAI.Chat.ChatCompletionTool {
    return {
      type: 'function',
      function: {
        name: tool.function.name,
        description: tool.function.description,
        parameters: tool.function.parameters,
      },
    };
  }
}
