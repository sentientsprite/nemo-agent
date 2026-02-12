---
summary: "CLI reference for `nemo voicecall` (voice-call plugin command surface)"
read_when:
  - You use the voice-call plugin and want the CLI entry points
  - You want quick examples for `voicecall call|continue|status|tail|expose`
title: "voicecall"
---

# `nemo voicecall`

`voicecall` is a plugin-provided command. It only appears if the voice-call plugin is installed and enabled.

Primary doc:

- Voice-call plugin: [Voice Call](/plugins/voice-call)

## Common commands

```bash
nemo voicecall status --call-id <id>
nemo voicecall call --to "+15555550123" --message "Hello" --mode notify
nemo voicecall continue --call-id <id> --message "Any questions?"
nemo voicecall end --call-id <id>
```

## Exposing webhooks (Tailscale)

```bash
nemo voicecall expose --mode serve
nemo voicecall expose --mode funnel
nemo voicecall unexpose
```

Security note: only expose the webhook endpoint to networks you trust. Prefer Tailscale Serve over Funnel when possible.
