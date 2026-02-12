import path from "node:path";
import { describe, expect, it } from "vitest";
import { resolveGatewayStateDir } from "./paths.js";

describe("resolveGatewayStateDir", () => {
  it("uses the default state dir when no overrides are set", () => {
    const env = { HOME: "/Users/test" };
    expect(resolveGatewayStateDir(env)).toBe(path.join("/Users/test", ".nemo"));
  });

  it("appends the profile suffix when set", () => {
    const env = { HOME: "/Users/test", NEMO_PROFILE: "rescue" };
    expect(resolveGatewayStateDir(env)).toBe(path.join("/Users/test", ".nemo-rescue"));
  });

  it("treats default profiles as the base state dir", () => {
    const env = { HOME: "/Users/test", NEMO_PROFILE: "Default" };
    expect(resolveGatewayStateDir(env)).toBe(path.join("/Users/test", ".nemo"));
  });

  it("uses NEMO_STATE_DIR when provided", () => {
    const env = { HOME: "/Users/test", NEMO_STATE_DIR: "/var/lib/nemo" };
    expect(resolveGatewayStateDir(env)).toBe(path.resolve("/var/lib/nemo"));
  });

  it("expands ~ in NEMO_STATE_DIR", () => {
    const env = { HOME: "/Users/test", NEMO_STATE_DIR: "~/nemo-state" };
    expect(resolveGatewayStateDir(env)).toBe(path.resolve("/Users/test/nemo-state"));
  });

  it("preserves Windows absolute paths without HOME", () => {
    const env = { NEMO_STATE_DIR: "C:\\State\\nemo" };
    expect(resolveGatewayStateDir(env)).toBe("C:\\State\\nemo");
  });
});
