---
summary: "CLI reference for `nemo logs` (tail gateway logs via RPC)"
read_when:
  - You need to tail Gateway logs remotely (without SSH)
  - You want JSON log lines for tooling
title: "logs"
---

# `nemo logs`

Tail Gateway file logs over RPC (works in remote mode).

Related:

- Logging overview: [Logging](/logging)

## Examples

```bash
nemo logs
nemo logs --follow
nemo logs --json
nemo logs --limit 500
nemo logs --local-time
nemo logs --follow --local-time
```

Use `--local-time` to render timestamps in your local timezone.
