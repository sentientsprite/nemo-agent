import { describe, expect, it } from "vitest";
import { resolveIrcInboundTarget } from "./monitor.js";

describe("irc monitor inbound target", () => {
  it("keeps channel target for group messages", () => {
    expect(
      resolveIrcInboundTarget({
        target: "#nemo",
        senderNick: "alice",
      }),
    ).toEqual({
      isGroup: true,
      target: "#nemo",
      rawTarget: "#nemo",
    });
  });

  it("maps DM target to sender nick and preserves raw target", () => {
    expect(
      resolveIrcInboundTarget({
        target: "nemo-bot",
        senderNick: "alice",
      }),
    ).toEqual({
      isGroup: false,
      target: "alice",
      rawTarget: "nemo-bot",
    });
  });

  it("falls back to raw target when sender nick is empty", () => {
    expect(
      resolveIrcInboundTarget({
        target: "nemo-bot",
        senderNick: " ",
      }),
    ).toEqual({
      isGroup: false,
      target: "nemo-bot",
      rawTarget: "nemo-bot",
    });
  });
});
