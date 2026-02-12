---
summary: "CLI reference for `nemo reset` (reset local state/config)"
read_when:
  - You want to wipe local state while keeping the CLI installed
  - You want a dry-run of what would be removed
title: "reset"
---

# `nemo reset`

Reset local config/state (keeps the CLI installed).

```bash
nemo reset
nemo reset --dry-run
nemo reset --scope config+creds+sessions --yes --non-interactive
```
