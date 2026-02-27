import type { LLMProvider, ModelInfo } from '../types.js';
import { AnthropicProvider } from './anthropic.js';
import { OpenAIProvider } from './openai.js';

export class ProviderRegistry {
  private providers: Map<string, LLMProvider> = new Map();
  private models: Map<string, ModelInfo> = new Map();

  constructor() {
    this.registerBuiltInProviders();
    this.registerBuiltInModels();
  }

  private registerBuiltInProviders(): void {
    this.register('anthropic', new AnthropicProvider());
    this.register('openai', new OpenAIProvider());
  }

  private registerBuiltInModels(): void {
    // Anthropic models
    this.registerModel({
      id: 'claude-3-opus-20240229',
      name: 'Claude 3 Opus',
      provider: 'anthropic',
      contextWindow: 200000,
      maxTokens: 4096,
      supportsTools: true,
      supportsStreaming: true,
    });
    this.registerModel({
      id: 'claude-3-sonnet-20240229',
      name: 'Claude 3 Sonnet',
      provider: 'anthropic',
      contextWindow: 200000,
      maxTokens: 4096,
      supportsTools: true,
      supportsStreaming: true,
    });
    this.registerModel({
      id: 'claude-3-haiku-20240307',
      name: 'Claude 3 Haiku',
      provider: 'anthropic',
      contextWindow: 200000,
      maxTokens: 4096,
      supportsTools: true,
      supportsStreaming: true,
    });

    // OpenAI models
    this.registerModel({
      id: 'gpt-4-turbo-preview',
      name: 'GPT-4 Turbo',
      provider: 'openai',
      contextWindow: 128000,
      maxTokens: 4096,
      supportsTools: true,
      supportsStreaming: true,
    });
    this.registerModel({
      id: 'gpt-4',
      name: 'GPT-4',
      provider: 'openai',
      contextWindow: 8192,
      maxTokens: 4096,
      supportsTools: true,
      supportsStreaming: true,
    });
    this.registerModel({
      id: 'gpt-3.5-turbo',
      name: 'GPT-3.5 Turbo',
      provider: 'openai',
      contextWindow: 16385,
      maxTokens: 4096,
      supportsTools: true,
      supportsStreaming: true,
    });
  }

  register(name: string, provider: LLMProvider): void {
    this.providers.set(name, provider);
  }

  get(name: string): LLMProvider | undefined {
    return this.providers.get(name);
  }

  registerModel(model: ModelInfo): void {
    this.models.set(model.id, model);
  }

  getModel(modelId: string): ModelInfo | undefined {
    return this.models.get(modelId);
  }

  getProviderForModel(modelId: string): LLMProvider | undefined {
    const model = this.models.get(modelId);
    if (!model) return undefined;
    return this.providers.get(model.provider);
  }

  listModels(): ModelInfo[] {
    return Array.from(this.models.values());
  }

  listProviders(): string[] {
    return Array.from(this.providers.keys());
  }
}

// Singleton instance
export const registry = new ProviderRegistry();
