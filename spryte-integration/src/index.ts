// Main exports for Spryte Integration

export { SpryteBridge, createDefaultBridge } from './bridge.js';
export type { BridgeConfig, ProcessOptions } from './bridge.js';

export { ToolAdapter } from './tools.js';
export type { NemoTool, AdaptedTool } from './tools.js';

export { SpryteSession } from './session.js';
export type { SessionConfig, SessionData } from './session.js';

// Version
export const version = '1.0.0';
