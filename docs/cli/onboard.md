---
summary: "CLI reference for `nemo onboard` (interactive onboarding wizard)"
read_when:
  - You want guided setup for gateway, workspace, auth, channels, and skills
title: "onboard"
---

# `nemo onboard`

Interactive onboarding wizard (local or remote Gateway setup).

## Related guides

- CLI onboarding hub: [Onboarding Wizard (CLI)](/start/wizard)
- Onboarding overview: [Onboarding Overview](/start/onboarding-overview)
- CLI onboarding reference: [CLI Onboarding Reference](/start/wizard-cli-reference)
- CLI automation: [CLI Automation](/start/wizard-cli-automation)
- macOS onboarding: [Onboarding (macOS App)](/start/onboarding)

## Examples

```bash
nemo onboard
nemo onboard --flow quickstart
nemo onboard --flow manual
nemo onboard --mode remote --remote-url ws://gateway-host:18789
```

Non-interactive custom provider:

```bash
nemo onboard --non-interactive \
  --auth-choice custom-api-key \
  --custom-base-url "https://llm.example.com/v1" \
  --custom-model-id "foo-large" \
  --custom-api-key "$CUSTOM_API_KEY" \
  --custom-compatibility openai
```

`--custom-api-key` is optional in non-interactive mode. If omitted, onboarding checks `CUSTOM_API_KEY`.

Flow notes:

- `quickstart`: minimal prompts, auto-generates a gateway token.
- `manual`: full prompts for port/bind/auth (alias of `advanced`).
- Fastest first chat: `nemo dashboard` (Control UI, no channel setup).
- Custom Provider: connect any OpenAI or Anthropic compatible endpoint,
  including hosted providers not listed. Use Unknown to auto-detect.

## Common follow-up commands

```bash
nemo configure
nemo agents add <name>
```

<Note>
`--json` does not imply non-interactive mode. Use `--non-interactive` for scripts.
</Note>
