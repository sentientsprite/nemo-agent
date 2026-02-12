---
name: nemohub
description: Use the NEMOHub CLI to search, install, update, and publish agent skills from nemohub.com. Use when you need to fetch new skills on the fly, sync installed skills to latest or a specific version, or publish new/updated skill folders with the npm-installed nemohub CLI.
metadata:
  {
    "nemo":
      {
        "requires": { "bins": ["nemohub"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "nemohub",
              "bins": ["nemohub"],
              "label": "Install NEMOHub CLI (npm)",
            },
          ],
      },
  }
---

# NEMOHub CLI

Install

```bash
npm i -g nemohub
```

Auth (publish)

```bash
nemohub login
nemohub whoami
```

Search

```bash
nemohub search "postgres backups"
```

Install

```bash
nemohub install my-skill
nemohub install my-skill --version 1.2.3
```

Update (hash-based match + upgrade)

```bash
nemohub update my-skill
nemohub update my-skill --version 1.2.3
nemohub update --all
nemohub update my-skill --force
nemohub update --all --no-input --force
```

List

```bash
nemohub list
```

Publish

```bash
nemohub publish ./my-skill --slug my-skill --name "My Skill" --version 1.2.0 --changelog "Fixes + docs"
```

Notes

- Default registry: https://nemohub.com (override with CLAWHUB_REGISTRY or --registry)
- Default workdir: cwd (falls back to NEMO workspace); install dir: ./skills (override with --workdir / --dir / CLAWHUB_WORKDIR)
- Update command hashes local files, resolves matching version, and upgrades to latest unless --version is set
