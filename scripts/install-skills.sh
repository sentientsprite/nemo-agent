#!/bin/bash
# NEMO Skills Installation Script
# Run this to install all required skills for the NEMO agent

set -e

echo "🐟 NEMO Skills Installer"
echo "========================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track successes and failures
INSTALLED=()
FAILED=()

# Function to install a skill
install_skill() {
    local source=$1
    local name=$2
    
    echo -e "${BLUE}Installing $name...${NC}"
    if npx skills add "$source" -g -y 2>&1 | grep -q "Installation complete"; then
        echo -e "${GREEN}✓ $name installed${NC}"
        INSTALLED+=("$name")
    else
        echo -e "${RED}✗ $name failed${NC}"
        FAILED+=("$name")
    fi
    echo ""
}

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo -e "${RED}Error: npx not found. Please install Node.js first.${NC}"
    echo "  macOS: brew install node"
    echo "  Linux: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi

echo -e "${YELLOW}This will install the following skills:${NC}"
echo "  1. alchemy-api — Alchemy API integration (API key auth)"
echo "  2. agentic-gateway — Alchemy gateway (wallet auth, no API key)"
echo "  3. tiktok-app-marketing — Larry's TikTok marketing automation"
echo ""
echo -e "${YELLOW}Continue? (y/n)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "Starting installation..."
echo "========================"
echo ""

# Install Alchemy skills
install_skill "https://github.com/alchemyplatform/skills" "alchemy-api"
install_skill "https://github.com/alchemyplatform/skills" "agentic-gateway"

# Install Larrybrain (TikTok marketing)
install_skill "upload-post/upload-post-larry-marketing-skill@tiktok-app-marketing" "tiktok-app-marketing"

echo ""
echo "========================"
echo -e "${GREEN}Installation Summary${NC}"
echo "========================"
echo ""

if [ ${#INSTALLED[@]} -gt 0 ]; then
    echo -e "${GREEN}Successfully installed (${#INSTALLED[@]}):${NC}"
    for skill in "${INSTALLED[@]}"; do
        echo "  ✓ $skill"
    done
fi

if [ ${#FAILED[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Failed to install (${#FAILED[@]}):${NC}"
    for skill in "${FAILED[@]}"; do
        echo "  ✗ $skill"
    done
fi

echo ""
echo "========================"
echo "Next Steps:"
echo "========================"
echo ""
echo "1. Alchemy Skills:"
echo "   Option A: Get API key at https://alchemy.com"
echo "   Option B: Use agentic-gateway (wallet-based, no API key)"
echo "   See: projects/social-presence/docs/alchemy-skills-summary.md"
echo ""
echo "2. TikTok Marketing (Larrybrain):"
echo "   - Review SKILL.md in ~/.agents/skills/tiktok-app-marketing/"
echo "   - Set up Upload-Post account at https://upload-post.com"
echo "   - Configure OpenAI API key for image generation"
echo "   - Run: cd projects/social-presence && bash scripts/setup.sh"
echo ""
echo "3. Verify installation:"
echo "   ls -la ~/.agents/skills/"
echo ""
echo "🐟 Skills installation complete!"
