# Lead Generator Skill for Marketing Agency

## Overview
AI-powered lead generation agent that qualifies prospects via voice calls and schedules appointments with closers.

## Voice Calling Platforms (Ranked)

### 1. **Bland AI** (Recommended)
- **Pricing:** $0.09/minute (~$5.40/hour of talk time)
- **Features:** 
  - Ultra-realistic voices (sub-1000ms latency)
  - Built-in appointment scheduling
  - Calendar integration (Google, Outlook)
  - Call recording & analytics
  - Webhook support for CRM integration
- **API:** RESTful, easy integration
- **Best for:** High-volume outbound, appointment setting

### 2. **Retell AI**
- **Pricing:** $0.07/minute
- **Features:**
  - Voice cloning (use your own voice)
  - Multi-language support
  - Real-time transcription
  - Sentiment analysis
- **Best for:** Personalized outreach, international markets

### 3. **Synthflow**
- **Pricing:** $0.05/minute (starter), $0.08/minute (pro)
- **Features:**
  - Visual workflow builder (no-code)
  - Pre-built templates for sales
  - Integration with 5000+ apps via Zapier
  - A/B testing for scripts
- **Best for:** Non-technical setup, rapid deployment

### 4. **Twilio + OpenAI Realtime API**
- **Pricing:** Twilio ($0.013/min) + OpenAI ($0.06/min) = ~$0.073/min
- **Features:**
  - Full control over prompts
  - Custom voice models
  - Bring your own LLM
- **Best for:** Custom solutions, technical teams

## Recommended Stack

**Primary:** Bland AI + Calendly/Cal.com
- Bland AI handles the voice conversation
- Calendar integration books appointments automatically
- Webhook notifies your closer

**Alternative:** Retell AI + Custom CRM
- If you want voice cloning (use cracked salesguy's voice)
- Better for personalized follow-ups

## Lead Generator Agent Architecture

### Core Components

1. **Prospect Data Input**
   - CSV upload (name, phone, company, industry)
   - API integration (Apollo, ZoomInfo, etc.)
   - Website lead capture forms

2. **Qualification Script Engine**
   - Dynamic conversation flows
   - BANT qualification (Budget, Authority, Need, Timeline)
   - Objection handling
   - Automatic disqualification

3. **Voice Call Orchestration**
   - Batch dialing campaigns
   - Timezone-aware scheduling
   - Retry logic (no answer, voicemail)
   - Call recording storage

4. **Appointment Scheduling**
   - Calendar integration
   - Closer availability checking
   - Automatic booking + confirmation SMS
   - Reminder calls (24hr, 1hr before)

5. **CRM Integration**
   - Lead scoring
   - Status tracking (called, qualified, booked, no-show)
   - Handoff notes to closer

### Conversation Flow

```
1. Greeting & Hook (15 seconds)
   "Hi [Name], this is [AI Name] from [Agency]. We help [industry] companies 
   [value proposition]. Do you have 2 minutes?"

2. Qualification Questions (2-3 minutes)
   - "What's your current [problem] situation?"
   - "How is that affecting your [metric]?"
   - "Have you considered [solution category] before?"
   - "What's your timeline for solving this?"

3. Value Bridge (30 seconds)
   "Based on what you're saying, it sounds like we could [solution]. 
   We should get you on a call with [Closer Name], our [specialist]."

4. Scheduling (1-2 minutes)
   "I can see [Closer] has availability [time options]. 
   Which works better for you?"

5. Confirmation & Next Steps (30 seconds)
   "Great! You're booked for [time]. I'll send a confirmation text. 
   [Closer] will call you then. Any questions before we wrap up?"
```

## Skill File Structure

```yaml
# skills/lead-generator/SKILL.md
name: lead-generator
description: AI voice lead generation with appointment scheduling
version: 1.0.0

providers:
  voice:
    - bland-ai  # Primary
    - retell-ai # Backup
  
  calendar:
    - calendly
    - cal-com
    - google-calendar
  
  data:
    - apollo
    - zoominfo
    - csv-upload

features:
  - batch-calling
  - qualification-scripts
  - appointment-scheduling
  - crm-sync
  - call-recording
  - analytics-dashboard

pricing:
  bland-ai: "$0.09/min (~$5.40/hour talk time)"
  estimated-cost: "~$200-500/month for 1000 calls"
```

## Implementation Phases

### Phase 1: MVP (Week 1)
- Set up Bland AI account
- Create 1 qualification script
- Connect Calendly
- Test with 10 prospects

### Phase 2: Scale (Week 2-3)
- Import prospect list (CSV)
- A/B test 2-3 scripts
- Set up retry logic
- Basic CRM integration

### Phase 3: Optimize (Week 4)
- Analytics dashboard
- Lead scoring
- Closer handoff optimization
- Advanced objection handling

## Sample Costs

**Monthly Estimate (1000 calls):**
- Voice calls: ~$450 (avg 5 min per call)
- Phone numbers: $10
- CRM (HubSpot free tier): $0
- Calendar (Calendly free): $0
- **Total: ~$460/month**

**ROI Calculation:**
- 1000 calls → 100 qualified leads (10% rate)
- 100 qualified → 30 booked appointments (30% rate)
- 30 appointments → 5 closed deals (15% close rate)
- If deal value = $5,000 → $25,000 revenue
- **ROI: 5,400%** on $460 spend

## Next Steps

1. Choose voice platform (recommend: Bland AI)
2. Set up account & API keys
3. Write qualification script
4. Create this skill file
5. Test with small batch (10 calls)
6. Scale based on results

## Integration with Closer

The lead generator should hand off to your cracked salesguy with:
- Prospect contact info
- Qualification answers (BANT)
- Call recording link
- Lead temperature (hot/warm/cold)
- Best time to reach
- Objections raised

This gives your closer everything needed to close the deal.
