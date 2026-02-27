#!/bin/bash
# NEMO Social Media Presence — Tool Installation Script
# Run this to set up all required dependencies

set -e

echo "🐟 Setting up NEMO Social Media Presence tools..."
echo "================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Node.js
echo -e "${YELLOW}Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js installed: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found. Installing...${NC}"
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install node
    # Linux
    else
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
fi

# Create project directory
PROJECT_DIR="$HOME/.nemo/workspace/projects/social-presence"
cd "$PROJECT_DIR"

# Initialize npm project
echo -e "${YELLOW}Initializing npm project...${NC}"
if [ ! -f "package.json" ]; then
    npm init -y
    echo -e "${GREEN}✓ package.json created${NC}"
fi

# Install node-canvas
echo -e "${YELLOW}Installing node-canvas (for image overlays)...${NC}"
npm install canvas || {
    echo -e "${RED}✗ node-canvas installation failed${NC}"
    echo "You may need build tools:"
    echo "  macOS: xcode-select --install"
    echo "  Linux: sudo apt-get install build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev"
}

# Install other dependencies
echo -e "${YELLOW}Installing other dependencies...${NC}"
npm install dotenv axios node-cron sharp

# Check for n8n
echo -e "${YELLOW}Checking n8n...${NC}"
if command -v n8n &> /dev/null; then
    echo -e "${GREEN}✓ n8n installed${NC}"
else
    echo -e "${YELLOW}Installing n8n...${NC}"
    npm install n8n -g
fi

# Create environment file
echo -e "${YELLOW}Setting up environment file...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Upload-Post API
UPLOAD_POST_API_KEY=your_key_here

# OpenAI
OPENAI_API_KEY=your_key_here

# Platform Credentials (fill in after account creation)
TIKTOK_USERNAME=
TIKTOK_PASSWORD=
X_API_KEY=
X_API_SECRET=
INSTAGRAM_USERNAME=
INSTAGRAM_PASSWORD=

# Optional: RevenueCat
REVENUECAT_API_KEY=
EOF
    echo -e "${GREEN}✓ .env template created${NC}"
    echo -e "${YELLOW}⚠ Remember to fill in your API keys!${NC}"
fi

# Create directories
echo -e "${YELLOW}Creating content directories...${NC}"
mkdir -p content/{drafts,published,templates}
mkdir -p assets/{images,videos,fonts}
mkdir -p analytics/{daily,weekly}
mkdir -p scripts

# Create .gitignore
echo -e "${YELLOW}Creating .gitignore...${NC}"
cat > .gitignore << 'EOF'
# Environment
.env
.env.local

# Dependencies
node_modules/
package-lock.json

# Content (generated)
content/drafts/*
assets/temp/

# Analytics (personal data)
analytics/*

# Credentials
config/platform-credentials.json
config/api-keys.env

# Logs
*.log
logs/

# OS files
.DS_Store
Thumbs.db
EOF

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Next steps:"
echo "1. Fill in API keys in .env file"
echo "2. Create social media accounts (see docs/account-setup-checklist.md)"
echo "3. Run: node scripts/test-connection.js"
echo "4. Review growth strategy (docs/growth-strategy.md)"
echo ""
echo "🐟 Ready to make waves, Captain!"
