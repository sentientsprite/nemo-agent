#!/usr/bin/env bash
# NEMODock - Docker helpers for NEMO
# Inspired by Simon Willison's "Running NEMO in Docker"
# https://til.simonwillison.net/llms/nemo-docker
#
# Installation:
#   mkdir -p ~/.nemodock && curl -sL https://raw.githubusercontent.com/nemo/nemo/main/scripts/shell-helpers/nemodock-helpers.sh -o ~/.nemodock/nemodock-helpers.sh
#   echo 'source ~/.nemodock/nemodock-helpers.sh' >> ~/.zshrc
#
# Usage:
#   nemodock-help    # Show all available commands

# =============================================================================
# Colors
# =============================================================================
_CLR_RESET='\033[0m'
_CLR_BOLD='\033[1m'
_CLR_DIM='\033[2m'
_CLR_GREEN='\033[0;32m'
_CLR_YELLOW='\033[1;33m'
_CLR_BLUE='\033[0;34m'
_CLR_MAGENTA='\033[0;35m'
_CLR_CYAN='\033[0;36m'
_CLR_RED='\033[0;31m'

# Styled command output (green + bold)
_clr_cmd() {
  echo -e "${_CLR_GREEN}${_CLR_BOLD}$1${_CLR_RESET}"
}

# Inline command for use in sentences
_cmd() {
  echo "${_CLR_GREEN}${_CLR_BOLD}$1${_CLR_RESET}"
}

# =============================================================================
# Config
# =============================================================================
CLAWDOCK_CONFIG="${HOME}/.nemodock/config"

# Common paths to check for NEMO
CLAWDOCK_COMMON_PATHS=(
  "${HOME}/nemo"
  "${HOME}/workspace/nemo"
  "${HOME}/projects/nemo"
  "${HOME}/dev/nemo"
  "${HOME}/code/nemo"
  "${HOME}/src/nemo"
)

_nemodock_filter_warnings() {
  grep -v "^WARN\|^time="
}

_nemodock_trim_quotes() {
  local value="$1"
  value="${value#\"}"
  value="${value%\"}"
  printf "%s" "$value"
}

_nemodock_read_config_dir() {
  if [[ ! -f "$CLAWDOCK_CONFIG" ]]; then
    return 1
  fi
  local raw
  raw=$(sed -n 's/^CLAWDOCK_DIR=//p' "$CLAWDOCK_CONFIG" | head -n 1)
  if [[ -z "$raw" ]]; then
    return 1
  fi
  _nemodock_trim_quotes "$raw"
}

# Ensure CLAWDOCK_DIR is set and valid
_nemodock_ensure_dir() {
  # Already set and valid?
  if [[ -n "$CLAWDOCK_DIR" && -f "${CLAWDOCK_DIR}/docker-compose.yml" ]]; then
    return 0
  fi

  # Try loading from config
  local config_dir
  config_dir=$(_nemodock_read_config_dir)
  if [[ -n "$config_dir" && -f "${config_dir}/docker-compose.yml" ]]; then
    CLAWDOCK_DIR="$config_dir"
    return 0
  fi

  # Auto-detect from common paths
  local found_path=""
  for path in "${CLAWDOCK_COMMON_PATHS[@]}"; do
    if [[ -f "${path}/docker-compose.yml" ]]; then
      found_path="$path"
      break
    fi
  done

  if [[ -n "$found_path" ]]; then
    echo ""
    echo "🦞 Found NEMO at: $found_path"
    echo -n "   Use this location? [Y/n] "
    read -r response
    if [[ "$response" =~ ^[Nn] ]]; then
      echo ""
      echo "Set CLAWDOCK_DIR manually:"
      echo "  export CLAWDOCK_DIR=/path/to/nemo"
      return 1
    fi
    CLAWDOCK_DIR="$found_path"
  else
    echo ""
    echo "❌ NEMO not found in common locations."
    echo ""
    echo "Clone it first:"
    echo ""
    echo "  git clone https://github.com/nemo/nemo.git ~/nemo"
    echo "  cd ~/nemo && ./docker-setup.sh"
    echo ""
    echo "Or set CLAWDOCK_DIR if it's elsewhere:"
    echo ""
    echo "  export CLAWDOCK_DIR=/path/to/nemo"
    echo ""
    return 1
  fi

  # Save to config
  if [[ ! -d "${HOME}/.nemodock" ]]; then
    /bin/mkdir -p "${HOME}/.nemodock"
  fi
  echo "CLAWDOCK_DIR=\"$CLAWDOCK_DIR\"" > "$CLAWDOCK_CONFIG"
  echo "✅ Saved to $CLAWDOCK_CONFIG"
  echo ""
  return 0
}

# Wrapper to run docker compose commands
_nemodock_compose() {
  _nemodock_ensure_dir || return 1
  command docker compose -f "${CLAWDOCK_DIR}/docker-compose.yml" "$@"
}

_nemodock_read_env_token() {
  _nemodock_ensure_dir || return 1
  if [[ ! -f "${CLAWDOCK_DIR}/.env" ]]; then
    return 1
  fi
  local raw
  raw=$(sed -n 's/^NEMO_GATEWAY_TOKEN=//p' "${CLAWDOCK_DIR}/.env" | head -n 1)
  if [[ -z "$raw" ]]; then
    return 1
  fi
  _nemodock_trim_quotes "$raw"
}

# Basic Operations
nemodock-start() {
  _nemodock_compose up -d nemo-gateway
}

nemodock-stop() {
  _nemodock_compose down
}

nemodock-restart() {
  _nemodock_compose restart nemo-gateway
}

nemodock-logs() {
  _nemodock_compose logs -f nemo-gateway
}

nemodock-status() {
  _nemodock_compose ps
}

# Navigation
nemodock-cd() {
  _nemodock_ensure_dir || return 1
  cd "${CLAWDOCK_DIR}"
}

nemodock-config() {
  cd ~/.nemo
}

nemodock-workspace() {
  cd ~/.nemo/workspace
}

# Container Access
nemodock-shell() {
  _nemodock_compose exec nemo-gateway \
    bash -c 'echo "alias nemo=\"./nemo.mjs\"" > /tmp/.bashrc_nemo && bash --rcfile /tmp/.bashrc_nemo'
}

nemodock-exec() {
  _nemodock_compose exec nemo-gateway "$@"
}

nemodock-cli() {
  _nemodock_compose run --rm nemo-cli "$@"
}

# Maintenance
nemodock-rebuild() {
  _nemodock_compose build nemo-gateway
}

nemodock-clean() {
  _nemodock_compose down -v --remove-orphans
}

# Health check
nemodock-health() {
  _nemodock_ensure_dir || return 1
  local token
  token=$(_nemodock_read_env_token)
  if [[ -z "$token" ]]; then
    echo "❌ Error: Could not find gateway token"
    echo "   Check: ${CLAWDOCK_DIR}/.env"
    return 1
  fi
  _nemodock_compose exec -e "NEMO_GATEWAY_TOKEN=$token" nemo-gateway \
    node dist/index.js health
}

# Show gateway token
nemodock-token() {
  _nemodock_read_env_token
}

# Fix token configuration (run this once after setup)
nemodock-fix-token() {
  _nemodock_ensure_dir || return 1

  echo "🔧 Configuring gateway token..."
  local token
  token=$(nemodock-token)
  if [[ -z "$token" ]]; then
    echo "❌ Error: Could not find gateway token"
    echo "   Check: ${CLAWDOCK_DIR}/.env"
    return 1
  fi

  echo "📝 Setting token: ${token:0:20}..."

  _nemodock_compose exec -e "TOKEN=$token" nemo-gateway \
    bash -c './nemo.mjs config set gateway.remote.token "$TOKEN" && ./nemo.mjs config set gateway.auth.token "$TOKEN"' 2>&1 | _nemodock_filter_warnings

  echo "🔍 Verifying token was saved..."
  local saved_token
  saved_token=$(_nemodock_compose exec nemo-gateway \
    bash -c "./nemo.mjs config get gateway.remote.token 2>/dev/null" 2>&1 | _nemodock_filter_warnings | tr -d '\r\n' | head -c 64)

  if [[ "$saved_token" == "$token" ]]; then
    echo "✅ Token saved correctly!"
  else
    echo "⚠️  Token mismatch detected"
    echo "   Expected: ${token:0:20}..."
    echo "   Got: ${saved_token:0:20}..."
  fi

  echo "🔄 Restarting gateway..."
  _nemodock_compose restart nemo-gateway 2>&1 | _nemodock_filter_warnings

  echo "⏳ Waiting for gateway to start..."
  sleep 5

  echo "✅ Configuration complete!"
  echo -e "   Try: $(_cmd nemodock-devices)"
}

# Open dashboard in browser
nemodock-dashboard() {
  _nemodock_ensure_dir || return 1

  echo "🦞 Getting dashboard URL..."
  local output status url
  output=$(_nemodock_compose run --rm nemo-cli dashboard --no-open 2>&1)
  status=$?
  url=$(printf "%s\n" "$output" | _nemodock_filter_warnings | grep -o 'http[s]\?://[^[:space:]]*' | head -n 1)
  if [[ $status -ne 0 ]]; then
    echo "❌ Failed to get dashboard URL"
    echo -e "   Try restarting: $(_cmd nemodock-restart)"
    return 1
  fi

  if [[ -n "$url" ]]; then
    echo "✅ Opening: $url"
    open "$url" 2>/dev/null || xdg-open "$url" 2>/dev/null || echo "   Please open manually: $url"
    echo ""
    echo -e "${_CLR_CYAN}💡 If you see 'pairing required' error:${_CLR_RESET}"
    echo -e "   1. Run: $(_cmd nemodock-devices)"
    echo "   2. Copy the Request ID from the Pending table"
    echo -e "   3. Run: $(_cmd 'nemodock-approve <request-id>')"
  else
    echo "❌ Failed to get dashboard URL"
    echo -e "   Try restarting: $(_cmd nemodock-restart)"
  fi
}

# List device pairings
nemodock-devices() {
  _nemodock_ensure_dir || return 1

  echo "🔍 Checking device pairings..."
  local output status
  output=$(_nemodock_compose exec nemo-gateway node dist/index.js devices list 2>&1)
  status=$?
  printf "%s\n" "$output" | _nemodock_filter_warnings
  if [ $status -ne 0 ]; then
    echo ""
    echo -e "${_CLR_CYAN}💡 If you see token errors above:${_CLR_RESET}"
    echo -e "   1. Verify token is set: $(_cmd nemodock-token)"
    echo "   2. Try manual config inside container:"
    echo -e "      $(_cmd nemodock-shell)"
    echo -e "      $(_cmd 'nemo config get gateway.remote.token')"
    return 1
  fi

  echo ""
  echo -e "${_CLR_CYAN}💡 To approve a pairing request:${_CLR_RESET}"
  echo -e "   $(_cmd 'nemodock-approve <request-id>')"
}

# Approve device pairing request
nemodock-approve() {
  _nemodock_ensure_dir || return 1

  if [[ -z "$1" ]]; then
    echo -e "❌ Usage: $(_cmd 'nemodock-approve <request-id>')"
    echo ""
    echo -e "${_CLR_CYAN}💡 How to approve a device:${_CLR_RESET}"
    echo -e "   1. Run: $(_cmd nemodock-devices)"
    echo "   2. Find the Request ID in the Pending table (long UUID)"
    echo -e "   3. Run: $(_cmd 'nemodock-approve <that-request-id>')"
    echo ""
    echo "Example:"
    echo -e "   $(_cmd 'nemodock-approve 6f9db1bd-a1cc-4d3f-b643-2c195262464e')"
    return 1
  fi

  echo "✅ Approving device: $1"
  _nemodock_compose exec nemo-gateway \
    node dist/index.js devices approve "$1" 2>&1 | _nemodock_filter_warnings

  echo ""
  echo "✅ Device approved! Refresh your browser."
}

# Show all available nemodock helper commands
nemodock-help() {
  echo -e "\n${_CLR_BOLD}${_CLR_CYAN}🦞 NEMODock - Docker Helpers for NEMO${_CLR_RESET}\n"

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}⚡ Basic Operations${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-start)       ${_CLR_DIM}Start the gateway${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-stop)        ${_CLR_DIM}Stop the gateway${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-restart)     ${_CLR_DIM}Restart the gateway${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-status)      ${_CLR_DIM}Check container status${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-logs)        ${_CLR_DIM}View live logs (follows)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🐚 Container Access${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-shell)       ${_CLR_DIM}Shell into container (nemo alias ready)${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-cli)         ${_CLR_DIM}Run CLI commands (e.g., nemodock-cli status)${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-exec) ${_CLR_CYAN}<cmd>${_CLR_RESET}  ${_CLR_DIM}Execute command in gateway container${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🌐 Web UI & Devices${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-dashboard)   ${_CLR_DIM}Open web UI in browser ${_CLR_CYAN}(auto-guides you)${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-devices)     ${_CLR_DIM}List device pairings ${_CLR_CYAN}(auto-guides you)${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-approve) ${_CLR_CYAN}<id>${_CLR_RESET} ${_CLR_DIM}Approve device pairing ${_CLR_CYAN}(with examples)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}⚙️  Setup & Configuration${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-fix-token)   ${_CLR_DIM}Configure gateway token ${_CLR_CYAN}(run once)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🔧 Maintenance${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-rebuild)     ${_CLR_DIM}Rebuild Docker image${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-clean)       ${_CLR_RED}⚠️  Remove containers & volumes (nuclear)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🛠️  Utilities${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-health)      ${_CLR_DIM}Run health check${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-token)       ${_CLR_DIM}Show gateway auth token${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-cd)          ${_CLR_DIM}Jump to nemo project directory${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-config)      ${_CLR_DIM}Open config directory (~/.nemo)${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-workspace)   ${_CLR_DIM}Open workspace directory${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${_CLR_RESET}"
  echo -e "${_CLR_BOLD}${_CLR_GREEN}🚀 First Time Setup${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  1.${_CLR_RESET} $(_cmd nemodock-start)          ${_CLR_DIM}# Start the gateway${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  2.${_CLR_RESET} $(_cmd nemodock-fix-token)      ${_CLR_DIM}# Configure token${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  3.${_CLR_RESET} $(_cmd nemodock-dashboard)      ${_CLR_DIM}# Open web UI${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  4.${_CLR_RESET} $(_cmd nemodock-devices)        ${_CLR_DIM}# If pairing needed${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  5.${_CLR_RESET} $(_cmd nemodock-approve) ${_CLR_CYAN}<id>${_CLR_RESET}   ${_CLR_DIM}# Approve pairing${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_GREEN}💬 WhatsApp Setup${_CLR_RESET}"
  echo -e "  $(_cmd nemodock-shell)"
  echo -e "    ${_CLR_BLUE}>${_CLR_RESET} $(_cmd 'nemo channels login --channel whatsapp')"
  echo -e "    ${_CLR_BLUE}>${_CLR_RESET} $(_cmd 'nemo status')"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_CYAN}💡 All commands guide you through next steps!${_CLR_RESET}"
  echo -e "${_CLR_BLUE}📚 Docs: ${_CLR_RESET}${_CLR_CYAN}https://docs.nemo.ai${_CLR_RESET}"
  echo ""
}
