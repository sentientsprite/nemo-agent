#!/bin/bash
# Lead Generator Skill Setup Script
# Run this to configure the AI voice lead generation system

set -e

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║     🤖 LEAD GENERATOR SKILL SETUP                ║"
echo "║     AI Voice Calling + Appointment Booking       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"
echo ""

MISSING=()

if ! command -v node &> /dev/null; then
    MISSING+=("Node.js 18+")
fi

if ! command -v npm &> /dev/null; then
    MISSING+=("npm")
fi

if [ ${#MISSING[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing prerequisites:${NC}"
    printf '%s\n' "${MISSING[@]}"
    echo ""
    echo "Install Node.js from https://nodejs.org"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node -v)${NC}"
echo -e "${GREEN}✅ npm $(npm -v)${NC}"
echo ""

# Step 1: Choose Voice Platform
echo -e "${BLUE}🎙️  Step 1: Choose Voice Platform${NC}"
echo ""
echo "Recommended: Bland AI ($0.09/min, most realistic)"
echo "Alternative: Retell AI ($0.07/min, voice cloning)"
echo "Budget: Synthflow ($0.05/min, no-code)"
echo ""

read -p "Which platform? (bland/retell/synthflow) [bland]: " VOICE_PLATFORM
VOICE_PLATFORM=${VOICE_PLATFORM:-bland}

case $VOICE_PLATFORM in
    bland|bland-ai)
        VOICE_PROVIDER="bland-ai"
        echo ""
        echo -e "${YELLOW}1. Go to https://bland.ai and create account${NC}"
        echo -e "${YELLOW}2. Get API key from Settings > API${NC}"
        echo -e "${YELLOW}3. Purchase a phone number (or use trial)${NC}"
        echo ""
        read -p "Enter your Bland API key: " BLAND_KEY
        read -p "Enter your Bland phone number: " BLAND_PHONE
        
        cat > .env <<EOF
VOICE_PROVIDER=bland-ai
BLAND_API_KEY=${BLAND_KEY}
BLAND_PHONE_NUMBER=${BLAND_PHONE}
EOF
        ;;
    
    retell|retell-ai)
        VOICE_PROVIDER="retell-ai"
        echo ""
        echo -e "${YELLOW}1. Go to https://retellai.com and create account${NC}"
        echo -e "${YELLOW}2. Get API key from Dashboard${NC}"
        echo ""
        read -p "Enter your Retell API key: " RETELL_KEY
        
        cat > .env <<EOF
VOICE_PROVIDER=retell-ai
RETELL_API_KEY=${RETELL_KEY}
EOF
        ;;
    
    synthflow)
        VOICE_PROVIDER="synthflow"
        echo ""
        echo -e "${YELLOW}1. Go to https://synthflow.ai and create account${NC}"
        echo -e "${YELLOW}2. Build your voice agent in their UI${NC}"
        echo -e "${YELLOW}3. Get webhook URL${NC}"
        echo ""
        read -p "Enter your Synthflow webhook URL: " SYNTHFLOW_URL
        
        cat > .env <<EOF
VOICE_PROVIDER=synthflow
SYNTHFLOW_WEBHOOK_URL=${SYNTHFLOW_URL}
EOF
        ;;
    
    *)
        echo -e "${RED}Invalid option. Using Bland AI as default.${NC}"
        VOICE_PROVIDER="bland-ai"
        ;;
esac

echo -e "${GREEN}✅ Voice platform configured${NC}"
echo ""

# Step 2: Calendar Integration
echo -e "${BLUE}📅 Step 2: Calendar Integration${NC}"
echo ""
echo "Connect your closer's calendar for automatic booking"
echo ""

read -p "Calendar provider? (calendly/calcom/google) [calendly]: " CAL_PROVIDER
CAL_PROVIDER=${CAL_PROVIDER:-calendly}

case $CAL_PROVIDER in
    calendly)
        echo ""
        echo -e "${YELLOW}1. Go to https://calendly.com/integrations/api-webhooks${NC}"
        echo -e "${YELLOW}2. Copy your Personal Access Token${NC}"
        echo -e "${YELLOW}3. Get your event type link (e.g., calendly.com/yourname/30min)${NC}"
        echo ""
        read -p "Enter Calendly API key: " CALENDLY_KEY
        read -p "Enter Calendly event URL: " CALENDLY_URL
        
        cat >> .env <<EOF
CALENDAR_PROVIDER=calendly
CALENDLY_API_KEY=${CALENDLY_KEY}
CALENDLY_EVENT_URL=${CALENDLY_URL}
EOF
        ;;
    
    calcom|cal-com)
        echo ""
        read -p "Enter Cal.com API key: " CALCOM_KEY
        read -p "Enter Cal.com event type ID: " CALCOM_EVENT
        
        cat >> .env <<EOF
CALENDAR_PROVIDER=cal-com
CALCOM_API_KEY=${CALCOM_KEY}
CALCOM_EVENT_TYPE_ID=${CALCOM_EVENT}
EOF
        ;;
    
    google)
        echo ""
        echo -e "${YELLOW}Note: Google Calendar requires OAuth setup${NC}"
        read -p "Continue? (y/n) [n]: " GOOGLE_CONTINUE
        if [ "$GOOGLE_CONTINUE" = "y" ]; then
            echo "See docs for Google OAuth setup"
        fi
        ;;
esac

echo -e "${GREEN}✅ Calendar configured${NC}"
echo ""

# Step 3: Closer Notification
echo -e "${BLUE}📧 Step 3: Closer Notification${NC}"
echo ""
echo "How should we notify your salesguy when appointments are booked?"
echo ""

read -p "Notification method? (email/slack/webhook) [email]: " NOTIFY_METHOD
NOTIFY_METHOD=${NOTIFY_METHOD:-email}

case $NOTIFY_METHOD in
    email)
        read -p "Enter closer's email: " CLOSER_EMAIL
        cat >> .env <<EOF
NOTIFICATION_METHOD=email
CLOSER_EMAIL=${CLOSER_EMAIL}
EOF
        ;;
    
    slack)
        echo ""
        echo -e "${YELLOW}1. Go to https://api.slack.com/apps${NC}"
        echo -e "${YELLOW}2. Create app > Incoming Webhooks${NC}"
        echo -e "${YELLOW}3. Copy webhook URL${NC}"
        echo ""
        read -p "Enter Slack webhook URL: " SLACK_URL
        cat >> .env <<EOF
NOTIFICATION_METHOD=slack
SLACK_WEBHOOK_URL=${SLACK_URL}
EOF
        ;;
    
    webhook)
        read -p "Enter your webhook URL: " WEBHOOK_URL
        cat >> .env <<EOF
NOTIFICATION_METHOD=webhook
WEBHOOK_URL=${WEBHOOK_URL}
EOF
        ;;
esac

echo -e "${GREEN}✅ Notifications configured${NC}"
echo ""

# Step 4: Agency Info
echo -e "${BLUE}🏢 Step 4: Agency Information${NC}"
echo ""

read -p "Agency name: " AGENCY_NAME
read -p "Your name (AI will use): " AI_NAME
read -p "Closer's name: " CLOSER_NAME
read -p "Industry you serve (e.g., SaaS, e-commerce): " INDUSTRY
read -p "Main problem you solve: " PROBLEM_SOLVED

cat >> .env <<EOF

# Agency Configuration
AGENCY_NAME=${AGENCY_NAME}
AI_NAME=${AI_NAME}
CLOSER_NAME=${CLOSER_NAME}
TARGET_INDUSTRY=${INDUSTRY}
PROBLEM_SOLVED=${PROBLEM_SOLVED}
EOF

echo -e "${GREEN}✅ Agency info saved${NC}"
echo ""

# Step 5: Install Dependencies
echo -e "${BLUE}📦 Step 5: Installing dependencies...${NC}"
echo ""

if [ -f "package.json" ]; then
    npm install
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  No package.json found. Skipping npm install.${NC}"
fi

echo ""

# Summary
echo "╔════════════════════════════════════════════════════╗"
echo "║          ✅ SETUP COMPLETE!                        ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Configuration saved to: .env"
echo ""
echo "Next steps:"
echo ""
echo "1. Test the setup:"
echo "   ./lead-generator test-call --phone YOUR_NUMBER"
echo ""
echo "2. Create your first campaign:"
echo "   ./lead-generator create-campaign --name 'Launch Campaign'"
echo ""
echo "3. Upload prospects:"
echo "   ./lead-generator upload --file prospects.csv"
echo ""
echo "4. Start calling:"
echo "   ./lead-generator start --campaign 'Launch Campaign'"
echo ""
echo "📖 Full docs: ./skills/lead-generator/SKILL.md"
echo ""
