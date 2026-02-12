import path from "node:path";
import { afterEach, describe, expect, it, vi } from "vitest";
import { resolveStorePath } from "./paths.js";

describe("resolveStorePath", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("uses NEMO_HOME for tilde expansion", () => {
    vi.stubEnv("NEMO_HOME", "/srv/nemo-home");
    vi.stubEnv("HOME", "/home/other");

    const resolved = resolveStorePath("~/.nemo/agents/{agentId}/sessions/sessions.json", {
      agentId: "research",
    });

    expect(resolved).toBe(
      path.resolve("/srv/nemo-home/.nemo/agents/research/sessions/sessions.json"),
    );
  });
});
