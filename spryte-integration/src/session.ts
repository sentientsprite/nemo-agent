/**
 * Session Wrapper - NEMO session management with Spryte
 * 
 * Provides session persistence compatible with NEMO's
 * existing session storage format.
 */

import { promises as fs } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

export interface SessionConfig {
  sessionId: string;
  persistPath: string;
  maxHistory?: number;
  autoSave?: boolean;
}

export interface SessionData {
  id: string;
  createdAt: string;
  updatedAt: string;
  messages: any[];
  metadata: Record<string, any>;
  state: Record<string, any>;
}

/**
 * SpryteSession - Session management with persistence
 */
export class SpryteSession {
  private config: SessionConfig;
  private data: SessionData;
  private dirty: boolean = false;

  constructor(config: SessionConfig) {
    this.config = {
      maxHistory: 100,
      autoSave: true,
      ...config,
    };

    // Expand home directory in path
    this.config.persistPath = this.config.persistPath.replace('~', homedir());

    // Initialize empty session
    this.data = {
      id: config.sessionId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [],
      metadata: {},
      state: {},
    };
  }

  /**
   * Load session from disk
   */
  async load(): Promise<void> {
    try {
      const filePath = this.getSessionPath();
      
      // Ensure directory exists
      await fs.mkdir(this.config.persistPath, { recursive: true });
      
      // Try to load existing session
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        const loaded = JSON.parse(content);
        
        this.data = {
          ...this.data,
          ...loaded,
          id: this.config.sessionId, // Ensure ID matches
        };
        
        console.log(`Session loaded: ${this.config.sessionId}`);
      } catch (error) {
        // File doesn't exist, create new session
        console.log(`New session created: ${this.config.sessionId}`);
        await this.save();
      }
    } catch (error) {
      console.error('Failed to load session:', error);
      throw error;
    }
  }

  /**
   * Save session to disk
   */
  async save(): Promise<void> {
    try {
      const filePath = this.getSessionPath();
      
      // Ensure directory exists
      await fs.mkdir(this.config.persistPath, { recursive: true });
      
      // Update timestamp
      this.data.updatedAt = new Date().toISOString();
      
      // Write to file
      await fs.writeFile(filePath, JSON.stringify(this.data, null, 2));
      
      this.dirty = false;
    } catch (error) {
      console.error('Failed to save session:', error);
      throw error;
    }
  }

  /**
   * Add a message to the session
   * 
   * @param role - Message role (user, assistant, system)
   * @param content - Message content
   */
  addMessage(role: string, content: string): void {
    this.data.messages.push({
      role,
      content,
      timestamp: new Date().toISOString(),
    });

    // Trim history if needed
    if (this.data.messages.length > (this.config.maxHistory || 100)) {
      this.data.messages = this.data.messages.slice(-this.config.maxHistory!);
    }

    this.dirty = true;

    if (this.config.autoSave) {
      this.save().catch(console.error);
    }
  }

  /**
   * Get all messages
   * 
   * @returns Array of messages
   */
  getMessages(): any[] {
    return [...this.data.messages];
  }

  /**
   * Clear all messages
   */
  clearMessages(): void {
    this.data.messages = [];
    this.dirty = true;
  }

  /**
   * Set metadata value
   * 
   * @param key - Metadata key
   * @param value - Metadata value
   */
  setMetadata(key: string, value: any): void {
    this.data.metadata[key] = value;
    this.dirty = true;
  }

  /**
   * Get metadata value
   * 
   * @param key - Metadata key
   * @returns Metadata value
   */
  getMetadata(key: string): any {
    return this.data.metadata[key];
  }

  /**
   * Get all metadata
   * 
   * @returns Metadata object
   */
  getAllMetadata(): Record<string, any> {
    return { ...this.data.metadata };
  }

  /**
   * Set state value
   * 
   * @param key - State key
   * @param value - State value
   */
  setState(key: string, value: any): void {
    this.data.state[key] = value;
    this.dirty = true;
  }

  /**
   * Get state value
   * 
   * @param key - State key
   * @returns State value
   */
  getState(key: string): any {
    return this.data.state[key];
  }

  /**
   * Get session ID
   * 
   * @returns Session ID
   */
  getId(): string {
    return this.config.sessionId;
  }

  /**
   * Get session creation time
   * 
   * @returns ISO timestamp
   */
  getCreatedAt(): string {
    return this.data.createdAt;
  }

  /**
   * Get session last update time
   * 
   * @returns ISO timestamp
   */
  getUpdatedAt(): string {
    return this.data.updatedAt;
  }

  /**
   * Check if session has unsaved changes
   * 
   * @returns True if dirty
   */
  isDirty(): boolean {
    return this.dirty;
  }

  /**
   * Get session file path
   * 
   * @returns Full path to session file
   */
  private getSessionPath(): string {
    return join(this.config.persistPath, `${this.config.sessionId}.json`);
  }

  /**
   * Export session to JSON
   * 
   * @returns JSON string
   */
  export(): string {
    return JSON.stringify(this.data, null, 2);
  }

  /**
   * Import session from JSON
   * 
   * @param json - JSON string
   */
  import(json: string): void {
    this.data = JSON.parse(json);
    this.dirty = true;
  }

  /**
   * Delete session file
   */
  async delete(): Promise<void> {
    try {
      const filePath = this.getSessionPath();
      await fs.unlink(filePath);
      console.log(`Session deleted: ${this.config.sessionId}`);
    } catch (error) {
      // File might not exist
      console.log(`Session file not found: ${this.config.sessionId}`);
    }
  }
}

export default SpryteSession;
