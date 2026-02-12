import type {
  AnyAgentTool,
  NEMOPluginApi,
  NEMOPluginToolFactory,
} from "../../src/plugins/types.js";
import { createLobsterTool } from "./src/lobster-tool.js";

export default function register(api: NEMOPluginApi) {
  api.registerTool(
    ((ctx) => {
      if (ctx.sandboxed) {
        return null;
      }
      return createLobsterTool(api) as AnyAgentTool;
    }) as NEMOPluginToolFactory,
    { optional: true },
  );
}
