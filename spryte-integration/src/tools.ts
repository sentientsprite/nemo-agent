/**
 * Tool Adapter - Bridge NEMO tools to Spryte format
 * 
 * NEMO tools use a different format than Spryte tools.
 * This adapter converts between the two formats.
 */

import type { Tool as SpryteTool } from '@spryte/agent-core';

// NEMO tool format (from existing codebase)
export interface NemoTool {
  name: string;
  description: string;
  parameters: Record<string, any>;
  handler: (args: any) => Promise<any>;
}

// Extended Spryte tool with our metadata
export interface AdaptedTool extends SpryteTool {
  nemoMetadata?: {
    originalName: string;
    category: string;
    enabled: boolean;
  };
}

/**
 * ToolAdapter - Converts NEMO tools to Spryte format
 */
export class ToolAdapter {
  private static tools: Map<string, AdaptedTool> = new Map();

  /**
   * Register a NEMO tool as a Spryte tool
   * 
   * @param name - Tool name
   * @param tool - NEMO tool definition
   * @returns Adapted Spryte tool
   */
  static register(name: string, tool: NemoTool): AdaptedTool {
    const adaptedTool: AdaptedTool = {
      name: tool.name,
      description: tool.description,
      parameters: {
        type: 'object',
        properties: this.convertParameters(tool.parameters),
        required: Object.keys(tool.parameters),
      },
      handler: tool.handler,
      nemoMetadata: {
        originalName: name,
        category: this.inferCategory(name),
        enabled: true,
      },
    };

    this.tools.set(name, adaptedTool);
    return adaptedTool;
  }

  /**
   * Convert NEMO parameters to JSON Schema
   * 
   * @param params - NEMO parameter definitions
   * @returns JSON Schema properties
   */
  static convertParameters(params: Record<string, any>): Record<string, any> {
    const properties: Record<string, any> = {};

    for (const [key, value] of Object.entries(params)) {
      if (typeof value === 'string') {
        // Simple type shorthand: "string", "number", "boolean"
        properties[key] = { type: value };
      } else if (typeof value === 'object') {
        // Full parameter definition
        properties[key] = {
          type: value.type || 'string',
          description: value.description,
          enum: value.enum,
          default: value.default,
        };
      } else {
        // Default to string
        properties[key] = { type: 'string' };
      }
    }

    return properties;
  }

  /**
   * Get all registered tools
   * 
   * @returns Array of adapted tools
   */
  static getAll(): AdaptedTool[] {
    return Array.from(this.tools.values());
  }

  /**
   * Get a specific tool
   * 
   * @param name - Tool name
   * @returns Tool or undefined
   */
  static get(name: string): AdaptedTool | undefined {
    return this.tools.get(name);
  }

  /**
   * Enable/disable a tool
   * 
   * @param name - Tool name
   * @param enabled - Enable status
   */
  static setEnabled(name: string, enabled: boolean): void {
    const tool = this.tools.get(name);
    if (tool && tool.nemoMetadata) {
      tool.nemoMetadata.enabled = enabled;
    }
  }

  /**
   * Get tools by category
   * 
   * @param category - Category name
   * @returns Filtered tools
   */
  static getByCategory(category: string): AdaptedTool[] {
    return this.getAll().filter(
      tool => tool.nemoMetadata?.category === category && tool.nemoMetadata?.enabled
    );
  }

  /**
   * Get enabled tools only
   * 
   * @returns Enabled tools
   */
  static getEnabled(): AdaptedTool[] {
    return this.getAll().filter(tool => tool.nemoMetadata?.enabled);
  }

  /**
   * Unregister a tool
   * 
   * @param name - Tool name
   */
  static unregister(name: string): void {
    this.tools.delete(name);
  }

  /**
   * Clear all tools
   */
  static clear(): void {
    this.tools.clear();
  }

  /**
   * Infer tool category from name
   * 
   * @param name - Tool name
   * @returns Category
   */
  private static inferCategory(name: string): string {
    const categories: Record<string, string[]> = {
      web: ['web_search', 'web_fetch', 'browser', 'snapshot'],
      file: ['file_read', 'file_write', 'file_edit', 'read', 'write', 'edit'],
      system: ['exec', 'process', 'cron', 'gateway'],
      communication: ['message', 'sessions_send', 'sessions_spawn'],
      data: ['memory_search', 'memory_get', 'sessions_list', 'sessions_history'],
      media: ['image', 'tts'],
      search: ['agents_list'],
    };

    for (const [category, patterns] of Object.entries(categories)) {
      if (patterns.some(p => name.includes(p))) {
        return category;
      }
    }

    return 'other';
  }

  /**
   * Create common NEMO tools preset
   * 
   * @returns Pre-configured tools
   */
  static createDefaultTools(): NemoTool[] {
    return [
      {
        name: 'web_search',
        description: 'Search the web using Brave Search API',
        parameters: {
          query: { type: 'string', description: 'Search query' },
          count: { type: 'number', description: 'Number of results', default: 5 },
        },
        handler: async () => '[Tool not implemented - placeholder]',
      },
      {
        name: 'web_fetch',
        description: 'Fetch and extract content from a URL',
        parameters: {
          url: { type: 'string', description: 'URL to fetch' },
        },
        handler: async () => '[Tool not implemented - placeholder]',
      },
      {
        name: 'file_read',
        description: 'Read a file from the workspace',
        parameters: {
          path: { type: 'string', description: 'File path' },
        },
        handler: async () => '[Tool not implemented - placeholder]',
      },
      {
        name: 'file_write',
        description: 'Write content to a file',
        parameters: {
          path: { type: 'string', description: 'File path' },
          content: { type: 'string', description: 'File content' },
        },
        handler: async () => '[Tool not implemented - placeholder]',
      },
      {
        name: 'exec',
        description: 'Execute a shell command',
        parameters: {
          command: { type: 'string', description: 'Command to execute' },
        },
        handler: async () => '[Tool not implemented - placeholder]',
      },
      {
        name: 'memory_search',
        description: 'Search memory files',
        parameters: {
          query: { type: 'string', description: 'Search query' },
        },
        handler: async () => '[Tool not implemented - placeholder]',
      },
    ];
  }
}

export default ToolAdapter;
