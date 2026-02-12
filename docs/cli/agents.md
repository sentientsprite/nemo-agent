---
summary: "CLI reference for `nemo agents` (list/add/delete/set identity)"
read_when:
  - You want multiple isolated agents (workspaces + routing + auth)
title: "agents"
---

# `nemo agents`

Manage isolated agents (workspaces + auth + routing).

Related:

- Multi-agent routing: [Multi-Agent Routing](/concepts/multi-agent)
- Agent workspace: [Agent workspace](/concepts/agent-workspace)

## Examples

```bash
nemo agents list
nemo agents add work --workspace ~/.nemo/workspace-work
nemo agents set-identity --workspace ~/.nemo/workspace --from-identity
nemo agents set-identity --agent main --avatar avatars/nemo.png
nemo agents delete work
```

## Identity files

Each agent workspace can include an `IDENTITY.md` at the workspace root:

- Example path: `~/.nemo/workspace/IDENTITY.md`
- `set-identity --from-identity` reads from the workspace root (or an explicit `--identity-file`)

Avatar paths resolve relative to the workspace root.

## Set identity

`set-identity` writes fields into `agents.list[].identity`:

- `name`
- `theme`
- `emoji`
- `avatar` (workspace-relative path, http(s) URL, or data URI)

Load from `IDENTITY.md`:

```bash
nemo agents set-identity --workspace ~/.nemo/workspace --from-identity
```

Override fields explicitly:

```bash
nemo agents set-identity --agent main --name "NEMO" --emoji "🦞" --avatar avatars/nemo.png
```

Config sample:

```json5
{
  agents: {
    list: [
      {
        id: "main",
        identity: {
          name: "NEMO",
          theme: "space lobster",
          emoji: "🦞",
          avatar: "avatars/nemo.png",
        },
      },
    ],
  },
}
```
