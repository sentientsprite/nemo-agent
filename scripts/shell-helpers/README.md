# NEMODock <!-- omit in toc -->

Stop typing `docker-compose` commands. Just type `nemodock-start`.

Inspired by Simon Willison's [Running NEMO in Docker](https://til.simonwillison.net/llms/nemo-docker).

- [Quickstart](#quickstart)
- [Available Commands](#available-commands)
  - [Basic Operations](#basic-operations)
  - [Container Access](#container-access)
  - [Web UI \& Devices](#web-ui--devices)
  - [Setup \& Configuration](#setup--configuration)
  - [Maintenance](#maintenance)
  - [Utilities](#utilities)
- [Common Workflows](#common-workflows)
  - [Check Status and Logs](#check-status-and-logs)
  - [Set Up WhatsApp Bot](#set-up-whatsapp-bot)
  - [Troubleshooting Device Pairing](#troubleshooting-device-pairing)
  - [Fix Token Mismatch Issues](#fix-token-mismatch-issues)
  - [Permission Denied](#permission-denied)
- [Requirements](#requirements)

## Quickstart

**Install:**

```bash
mkdir -p ~/.nemodock && curl -sL https://raw.githubusercontent.com/nemo/nemo/main/scripts/shell-helpers/nemodock-helpers.sh -o ~/.nemodock/nemodock-helpers.sh
```

```bash
echo 'source ~/.nemodock/nemodock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

**See what you get:**

```bash
nemodock-help
```

On first command, NEMODock auto-detects your NEMO directory:

- Checks common paths (`~/nemo`, `~/workspace/nemo`, etc.)
- If found, asks you to confirm
- Saves to `~/.nemodock/config`

**First time setup:**

```bash
nemodock-start
```

```bash
nemodock-fix-token
```

```bash
nemodock-dashboard
```

If you see "pairing required":

```bash
nemodock-devices
```

And approve the request for the specific device:

```bash
nemodock-approve <request-id>
```

## Available Commands

### Basic Operations

| Command            | Description                     |
| ------------------ | ------------------------------- |
| `nemodock-start`   | Start the gateway               |
| `nemodock-stop`    | Stop the gateway                |
| `nemodock-restart` | Restart the gateway             |
| `nemodock-status`  | Check container status          |
| `nemodock-logs`    | View live logs (follows output) |

### Container Access

| Command                   | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `nemodock-shell`          | Interactive shell inside the gateway container |
| `nemodock-cli <command>`  | Run NEMO CLI commands                      |
| `nemodock-exec <command>` | Execute arbitrary commands in the container    |

### Web UI & Devices

| Command                 | Description                                |
| ----------------------- | ------------------------------------------ |
| `nemodock-dashboard`    | Open web UI in browser with authentication |
| `nemodock-devices`      | List device pairing requests               |
| `nemodock-approve <id>` | Approve a device pairing request           |

### Setup & Configuration

| Command              | Description                                       |
| -------------------- | ------------------------------------------------- |
| `nemodock-fix-token` | Configure gateway authentication token (run once) |

### Maintenance

| Command            | Description                                      |
| ------------------ | ------------------------------------------------ |
| `nemodock-rebuild` | Rebuild the Docker image                         |
| `nemodock-clean`   | Remove all containers and volumes (destructive!) |

### Utilities

| Command              | Description                               |
| -------------------- | ----------------------------------------- |
| `nemodock-health`    | Run gateway health check                  |
| `nemodock-token`     | Display the gateway authentication token  |
| `nemodock-cd`        | Jump to the NEMO project directory    |
| `nemodock-config`    | Open the NEMO config directory        |
| `nemodock-workspace` | Open the workspace directory              |
| `nemodock-help`      | Show all available commands with examples |

## Common Workflows

### Check Status and Logs

**Restart the gateway:**

```bash
nemodock-restart
```

**Check container status:**

```bash
nemodock-status
```

**View live logs:**

```bash
nemodock-logs
```

### Set Up WhatsApp Bot

**Shell into the container:**

```bash
nemodock-shell
```

**Inside the container, login to WhatsApp:**

```bash
nemo channels login --channel whatsapp --verbose
```

Scan the QR code with WhatsApp on your phone.

**Verify connection:**

```bash
nemo status
```

### Troubleshooting Device Pairing

**Check for pending pairing requests:**

```bash
nemodock-devices
```

**Copy the Request ID from the "Pending" table, then approve:**

```bash
nemodock-approve <request-id>
```

Then refresh your browser.

### Fix Token Mismatch Issues

If you see "gateway token mismatch" errors:

```bash
nemodock-fix-token
```

This will:

1. Read the token from your `.env` file
2. Configure it in the NEMO config
3. Restart the gateway
4. Verify the configuration

### Permission Denied

**Ensure Docker is running and you have permission:**

```bash
docker ps
```

## Requirements

- Docker and Docker Compose installed
- Bash or Zsh shell
- NEMO project (from `docker-setup.sh`)

## Development

**Test with fresh config (mimics first-time install):**

```bash
unset CLAWDOCK_DIR && rm -f ~/.nemodock/config && source scripts/shell-helpers/nemodock-helpers.sh
```

Then run any command to trigger auto-detect:

```bash
nemodock-start
```
