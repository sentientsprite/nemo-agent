---
summary: "CLI reference for `nemo config` (get/set/unset config values)"
read_when:
  - You want to read or edit config non-interactively
title: "config"
---

# `nemo config`

Config helpers: get/set/unset values by path. Run without a subcommand to open
the configure wizard (same as `nemo configure`).

## Examples

```bash
nemo config get browser.executablePath
nemo config set browser.executablePath "/usr/bin/google-chrome"
nemo config set agents.defaults.heartbeat.every "2h"
nemo config set agents.list[0].tools.exec.node "node-id-or-name"
nemo config unset tools.web.search.apiKey
```

## Paths

Paths use dot or bracket notation:

```bash
nemo config get agents.defaults.workspace
nemo config get agents.list[0].id
```

Use the agent list index to target a specific agent:

```bash
nemo config get agents.list
nemo config set agents.list[1].tools.exec.node "node-id-or-name"
```

## Values

Values are parsed as JSON5 when possible; otherwise they are treated as strings.
Use `--json` to require JSON5 parsing.

```bash
nemo config set agents.defaults.heartbeat.every "0m"
nemo config set gateway.port 19001 --json
nemo config set channels.whatsapp.groups '["*"]' --json
```

Restart the gateway after edits.
