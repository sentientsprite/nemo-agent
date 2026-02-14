import { describe, expect, it } from "vitest";
import {
  buildParseArgv,
  getFlagValue,
  getCommandPath,
  getPrimaryCommand,
  getPositiveIntFlagValue,
  getVerboseFlag,
  hasHelpOrVersion,
  hasFlag,
  shouldMigrateState,
  shouldMigrateStateFromPath,
} from "./argv.js";

describe("argv helpers", () => {
  it("detects help/version flags", () => {
    expect(hasHelpOrVersion(["node", "nemo", "--help"])).toBe(true);
    expect(hasHelpOrVersion(["node", "nemo", "-V"])).toBe(true);
    expect(hasHelpOrVersion(["node", "nemo", "status"])).toBe(false);
  });

  it("extracts command path ignoring flags and terminator", () => {
    expect(getCommandPath(["node", "nemo", "status", "--json"], 2)).toEqual(["status"]);
    expect(getCommandPath(["node", "nemo", "agents", "list"], 2)).toEqual(["agents", "list"]);
    expect(getCommandPath(["node", "nemo", "status", "--", "ignored"], 2)).toEqual(["status"]);
  });

  it("returns primary command", () => {
    expect(getPrimaryCommand(["node", "nemo", "agents", "list"])).toBe("agents");
    expect(getPrimaryCommand(["node", "nemo"])).toBeNull();
  });

  it("parses boolean flags and ignores terminator", () => {
    expect(hasFlag(["node", "nemo", "status", "--json"], "--json")).toBe(true);
    expect(hasFlag(["node", "nemo", "--", "--json"], "--json")).toBe(false);
  });

  it("extracts flag values with equals and missing values", () => {
    expect(getFlagValue(["node", "nemo", "status", "--timeout", "5000"], "--timeout")).toBe("5000");
    expect(getFlagValue(["node", "nemo", "status", "--timeout=2500"], "--timeout")).toBe("2500");
    expect(getFlagValue(["node", "nemo", "status", "--timeout"], "--timeout")).toBeNull();
    expect(getFlagValue(["node", "nemo", "status", "--timeout", "--json"], "--timeout")).toBe(null);
    expect(getFlagValue(["node", "nemo", "--", "--timeout=99"], "--timeout")).toBeUndefined();
  });

  it("parses verbose flags", () => {
    expect(getVerboseFlag(["node", "nemo", "status", "--verbose"])).toBe(true);
    expect(getVerboseFlag(["node", "nemo", "status", "--debug"])).toBe(false);
    expect(getVerboseFlag(["node", "nemo", "status", "--debug"], { includeDebug: true })).toBe(
      true,
    );
  });

  it("parses positive integer flag values", () => {
    expect(getPositiveIntFlagValue(["node", "nemo", "status"], "--timeout")).toBeUndefined();
    expect(
      getPositiveIntFlagValue(["node", "nemo", "status", "--timeout"], "--timeout"),
    ).toBeNull();
    expect(
      getPositiveIntFlagValue(["node", "nemo", "status", "--timeout", "5000"], "--timeout"),
    ).toBe(5000);
    expect(
      getPositiveIntFlagValue(["node", "nemo", "status", "--timeout", "nope"], "--timeout"),
    ).toBeUndefined();
  });

  it("builds parse argv from raw args", () => {
    const nodeArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["node", "nemo", "status"],
    });
    expect(nodeArgv).toEqual(["node", "nemo", "status"]);

    const versionedNodeArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["node-22", "nemo", "status"],
    });
    expect(versionedNodeArgv).toEqual(["node-22", "nemo", "status"]);

    const versionedNodeWindowsArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["node-22.2.0.exe", "nemo", "status"],
    });
    expect(versionedNodeWindowsArgv).toEqual(["node-22.2.0.exe", "nemo", "status"]);

    const versionedNodePatchlessArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["node-22.2", "nemo", "status"],
    });
    expect(versionedNodePatchlessArgv).toEqual(["node-22.2", "nemo", "status"]);

    const versionedNodeWindowsPatchlessArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["node-22.2.exe", "nemo", "status"],
    });
    expect(versionedNodeWindowsPatchlessArgv).toEqual(["node-22.2.exe", "nemo", "status"]);

    const versionedNodeWithPathArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["/usr/bin/node-22.2.0", "nemo", "status"],
    });
    expect(versionedNodeWithPathArgv).toEqual(["/usr/bin/node-22.2.0", "nemo", "status"]);

    const nodejsArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["nodejs", "nemo", "status"],
    });
    expect(nodejsArgv).toEqual(["nodejs", "nemo", "status"]);

    const nonVersionedNodeArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["node-dev", "nemo", "status"],
    });
    expect(nonVersionedNodeArgv).toEqual(["node", "nemo", "node-dev", "nemo", "status"]);

    const directArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["nemo", "status"],
    });
    expect(directArgv).toEqual(["node", "nemo", "status"]);

    const bunArgv = buildParseArgv({
      programName: "nemo",
      rawArgs: ["bun", "src/entry.ts", "status"],
    });
    expect(bunArgv).toEqual(["bun", "src/entry.ts", "status"]);
  });

  it("builds parse argv from fallback args", () => {
    const fallbackArgv = buildParseArgv({
      programName: "nemo",
      fallbackArgv: ["status"],
    });
    expect(fallbackArgv).toEqual(["node", "nemo", "status"]);
  });

  it("decides when to migrate state", () => {
    expect(shouldMigrateState(["node", "nemo", "status"])).toBe(false);
    expect(shouldMigrateState(["node", "nemo", "health"])).toBe(false);
    expect(shouldMigrateState(["node", "nemo", "sessions"])).toBe(false);
    expect(shouldMigrateState(["node", "nemo", "memory", "status"])).toBe(false);
    expect(shouldMigrateState(["node", "nemo", "agent", "--message", "hi"])).toBe(false);
    expect(shouldMigrateState(["node", "nemo", "agents", "list"])).toBe(true);
    expect(shouldMigrateState(["node", "nemo", "message", "send"])).toBe(true);
  });

  it("reuses command path for migrate state decisions", () => {
    expect(shouldMigrateStateFromPath(["status"])).toBe(false);
    expect(shouldMigrateStateFromPath(["agents", "list"])).toBe(true);
  });
});
