---
name: lead-generator
description: AI voice lead generation agent that qualifies prospects and schedules appointments with closers
version: 1.0.0
author: NEMO
---

# Lead Generator Skill

## Overview

Autonomous lead generation agent using AI voice calls to qualify prospects and book appointments with your sales closer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LEAD GENERATOR                           │
├─────────────────────────────────────────────────────────────┤
│  Input Layer          │  Processing Layer   │  Output Layer │
│  ───────────          │  ───────────────    │  ───────────  │
│  • CSV Upload         │  • Qualification    │  • Voice Call │
│  • API (Apollo/etc)   │  • Script Engine    │  • Calendar   │
│  • Web Forms          │  • Lead Scoring     │  • CRM Sync   │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Voice Platform    │
                    │  (Bland AI)        │
                    └────────────────────┘
```

## Configuration

### Required Environment Variables

```bash
# Voice Platform (Bland AI Recommended)
BLAND_API_KEY=your_bland_api_key
BLAND_PHONE_NUMBER=your_bland_number

# Calendar Integration
CALENDLY_API_KEY=your_calendly_key
CALENDLY_EVENT_URL=https://calendly.com/your-closer/30min

# CRM (Optional)
HUBSPOT_API_KEY=your_hubspot_key
# or
AIRTABLE_API_KEY=your_airtable_key

# Data Sources
APOLLO_API_KEY=optional_for_prospect_data
```

### Provider Options

#### Voice Platform (Choose One)

**Option A: Bland AI** (Recommended)
```bash
# Pricing: $0.09/minute
# Best for: High-volume, realistic voices
export VOICE_PROVIDER=bland-ai
export BLAND_API_KEY=sk-...
```

**Option B: Retell AI**
```bash
# Pricing: $0.07/minute  
# Best for: Voice cloning (use your salesguy's voice)
export VOICE_PROVIDER=retell-ai
export RETELL_API_KEY=...
```

**Option C: Synthflow**
```bash
# Pricing: $0.05-0.08/minute
# Best for: No-code setup
export VOICE_PROVIDER=synthflow
export SYNTHFLOW_API_KEY=...
```

#### Calendar (Choose One)

```bash
# Option 1: Calendly
export CALENDAR_PROVIDER=calendly
export CALENDLY_EVENT_URL=https://calendly.com/closer/30min

# Option 2: Cal.com
export CALENDAR_PROVIDER=cal-com
export CALCOM_EVENT_TYPE_ID=123

# Option 3: Google Calendar (via Calendly)
export CALENDAR_PROVIDER=google
export GCAL_CLIENT_ID=...
export GCAL_CLIENT_SECRET=...
```

## Quick Start

### 1. Install Prerequisites

```bash
# Install this skill
npx skills add sentientsprite/nemo-skills@lead-generator

# Or manually clone
git clone https://github.com/sentientsprite/nemo-skills.git
cd nemo-skills/lead-generator
npm install
```

### 2. Set Up Voice Platform

```bash
# Sign up at bland.ai
# Get API key from dashboard
export BLAND_API_KEY=sk-your-key-here

# Purchase phone number (or use provided)
export BLAND_PHONE_NUMBER=+1-555-123-4567
```

### 3. Configure Calendar

```bash
# Connect Calendly
# 1. Go to calendly.com/integrations/api-webhooks
# 2. Copy your API key
export CALENDLY_API_KEY=eyJ...

# 3. Get event type URL
export CALENDLY_EVENT_URL=https://calendly.com/your-closer/sales-call
```

### 4. Create First Campaign

```bash
# Create campaign config
cat > campaign.yaml <<EOF
name: "Agency Launch Campaign"
description: "Outbound to small business owners"

# Target audience
target:
  industry: ["ecommerce", "saas", "local-services"]
  company_size: "10-50 employees"
  title_keywords: ["owner", "founder", "ceo", "marketing director"]

# Voice settings
voice:
  provider: bland-ai
  voice_id: "maya"  # Options: maya, josh, mark, etc.
  language: "en-US"
  speed: 1.0

# Conversation script
script:
  opening: |
    Hi {{first_name}}, this is Maya from {{agency_name}}. 
    We help {{industry}} companies double their qualified leads in 90 days. 
    Do you have 2 minutes?
  
  qualification_questions:
    - "What's your current lead generation process?"
    - "How many qualified leads are you getting per month?"
    - "What's your target cost per lead?"
    - "Are you the decision maker for marketing?"
  
  value_proposition: |
    We've helped similar {{industry}} companies increase leads by 150% 
    while reducing cost per acquisition by 40%.
  
  close: |
    I'd love to have you speak with {{closer_name}}, our lead generation specialist. 
    He has a few openings this week. What works better, Tuesday or Thursday?

# Scheduling
scheduling:
  timezone_aware: true
  business_hours: "9am-5pm"
  retry_attempts: 3
  retry_interval: "24h"

# Disqualification criteria
disqualify:
  - "not interested"
  - "no budget"
  - "wrong person"
  - "do not call"

# Handoff to closer
handoff:
  send_recording: true
  send_transcript: true
  send_notes: true
  notification_method: "email"  # email, slack, webhook
EOF
```

### 5. Run Campaign

```bash
# Upload prospect list
./lead-generator upload-prospects --file prospects.csv --campaign campaign.yaml

# Start calling
./lead-generator start-campaign --campaign campaign.yaml

# Monitor dashboard
./lead-generator dashboard
```

## Commands

### Campaign Management

```bash
# Create new campaign
lead-generator create-campaign --name "Q1 Outreach"

# Upload prospects
lead-generator upload --file leads.csv --campaign my-campaign

# Start calling
lead-generator start --campaign my-campaign

# Pause campaign
lead-generator pause --campaign my-campaign

# Resume campaign
lead-generator resume --campaign my-campaign

# Get campaign stats
lead-generator stats --campaign my-campaign
```

### Testing

```bash
# Test single call
lead-generator test-call --phone +1234567890 --script my-script.yaml

# Test voice quality
lead-generator test-voice --voice maya

# Test calendar booking
lead-generator test-calendar --email test@example.com
```

### Analytics

```bash
# Show dashboard
lead-generator dashboard

# Export results
lead-generator export --campaign my-campaign --format csv

# Get call recordings
lead-generator recordings --campaign my-campaign
```

## Conversation Script Templates

### Template 1: Direct Pitch

```yaml
name: "Direct Pitch - 2min"
target: "Warm leads (downloaded content, attended webinar)"

greeting: |
  Hi {{first_name}}, this is {{ai_name}} from {{agency_name}}.
  You downloaded our {{lead_magnet}} last week. 
  Have you had a chance to look at it?

qualification:
  - "What resonated most with what you saw?"
  - "What's your biggest challenge with {{problem}} right now?"
  - "If we could solve that, what would it mean for your business?"

bridge: |
  Based on what you're saying, it sounds like you're a perfect fit 
  for our {{program}}. {{closer_name}} has helped 50+ companies 
  in {{industry}} solve exactly this.

close: |
  He's got a couple openings this week. 
  Are mornings or afternoons better for you?

voicemail: |
  Hi {{first_name}}, this is {{ai_name}} from {{agency_name}}.
  You downloaded our {{lead_magnet}}. I'd love to chat about 
  what we found works in {{industry}}. Call me back at 
  {{callback_number}} or grab time at {{calendar_link}}.
```

### Template 2: Referral Approach

```yaml
name: "Referral - 3min"
target: "Cold leads from purchased lists"

greeting: |
  Hi {{first_name}}, this is {{ai_name}} from {{agency_name}}.
  We were referred to you by {{mutual_connection}}.
  Do you have a quick minute?

qualification:
  - "How do you currently handle {{problem}}?"
  - "What would solving this be worth to you monthly?"
  - "When are you looking to make a change?"

objection_handling:
  "not interested": |
    Totally understand. Can I ask - is it the timing, 
    or are you happy with your current solution?
  
  "send me an email": |
    I'd love to, but honestly, our best results come from 
    a 10-minute conversation. What time works tomorrow?
  
  "too expensive": |
    I hear that. Most of our clients say that upfront. 
    But they're seeing 3-5x ROI in the first month. 
    Worth a 15-minute call to see the numbers?

close: |
  {{closer_name}} is our {{specialist}}. He has 15 years 
  in {{industry}} specifically. Can I book you for 
  a quick strategy call?
```

## Integration with Closer

### Handoff Data

When appointment is booked, closer receives:

```json
{
  "prospect": {
    "name": "John Smith",
    "phone": "+1-555-123-4567",
    "email": "john@company.com",
    "company": "Acme Inc",
    "industry": "SaaS"
  },
  "qualification": {
    "budget": "$5k-10k/month",
    "authority": "Decision maker",
    "need": "More qualified leads",
    "timeline": "30 days"
  },
  "call_data": {
    "recording_url": "https://...",
    "transcript": "Hi John...",
    "duration": "4m32s",
    "sentiment": "positive",
    "objections_raised": ["price"]
  },
  "appointment": {
    "datetime": "2026-03-03T14:00:00Z",
    "timezone": "America/Denver",
    "calendar_link": "https://calendly.com/..."
  },
  "lead_score": 85
}
```

### Notification Methods

```bash
# Email notification
export NOTIFICATION_METHOD=email
export CLOSER_EMAIL=sales@youragency.com

# Slack notification
export NOTIFICATION_METHOD=slack
export SLACK_WEBHOOK=https://hooks.slack.com/...

# Webhook (for custom CRM)
export NOTIFICATION_METHOD=webhook
export WEBHOOK_URL=https://your-crm.com/api/new-lead
```

## Advanced Features

### Lead Scoring

Automatic scoring based on:
- Engagement level (questions asked)
- Budget disclosed
- Timeline urgency
- Authority level
- Sentiment analysis

```bash
# High-quality leads (score > 80) → Priority booking
# Medium-quality (50-80) → Standard booking
# Low-quality (<50) → Nurture sequence
```

### A/B Testing

```bash
# Test two scripts
lead-generator test --campaign my-campaign --script-a script-a.yaml --script-b script-b.yaml --sample 50

# Get results
lead-generator test-results --test-id abc123
```

### Follow-up Sequences

```bash
# If no answer, schedule retry
lead-generator schedule-followup --campaign my-campaign --delay 24h

# If voicemail left, send SMS
lead-generator send-sms --template voicemail-followup
```

## Analytics Dashboard

Metrics tracked:
- **Calls Made** — Total attempts
- **Connect Rate** — % who answered
- **Qualification Rate** — % who passed BANT
- **Appointment Rate** — % who booked
- **Cost Per Lead** — Total spend / qualified leads
- **Cost Per Appointment** — Total spend / appointments
- **Pipeline Value** — Est. revenue from booked calls

## Troubleshooting

### Common Issues

**"No answer" rate too high**
- Check calling times (best: Tue-Thu, 10am-4pm)
- Verify phone numbers
- Add local caller ID

**Low qualification rate**
- Refine prospect list (better targeting)
- Adjust opening hook
- Add pre-qualification questions

**Appointments not showing up**
- Add confirmation SMS
- Call reminder 24hr before
- Call reminder 1hr before
- Send prep email with agenda

**High cost per lead**
- A/B test scripts
- Improve targeting
- Add disqualification earlier
- Test different voices

## Cost Optimization

### Budget Scenarios

**Starter ($200/month)**
- ~400 minutes talk time
- ~100 calls
- ~10-15 appointments
- Break-even: 1-2 closed deals

**Growth ($500/month)**
- ~1000 minutes talk time
- ~250 calls
- ~25-40 appointments
- Break-even: 2-4 closed deals

**Scale ($1000/month)**
- ~2000 minutes talk time
- ~500 calls
- ~50-75 appointments
- Break-even: 3-6 closed deals

## Compliance

### TCPA Compliance

- Only call 9am-8pm local time
- Honor DNC (Do Not Call) list
- Provide opt-out mechanism
- Keep call records for 4 years

### GDPR (if calling EU)

- Consent required
- Right to be forgotten
- Data processing disclosure

## Support

### Getting Help

```bash
# Documentation
lead-generator docs

# Check status
lead-generator status

# Debug mode
lead-generator debug --campaign my-campaign

# Contact support
lead-generator support
```

### Community

- Discord: https://discord.gg/nemo
- Issues: https://github.com/sentientsprite/nemo-skills/issues

## Roadmap

### v1.1 (Next)
- [ ] WhatsApp integration
- [ ] Email follow-up sequences
- [ ] Advanced sentiment analysis
- [ ] CRM integrations (Salesforce, HubSpot)

### v1.2
- [ ] Multi-language support
- [ ] Voice cloning for your salesguy
- [ ] AI script optimization
- [ ] Competitor mention detection

## License

MIT — Use freely for your agency
