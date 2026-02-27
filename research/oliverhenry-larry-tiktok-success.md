# Oliver Henry: Larry's TikTok Success (7M Views)

**Source:** https://x.com/oliverhenry/status/2022011925903667547  
**Author:** Oliver Henry (@oliverhenry) & Larry  
**Views:** 7,009,333 | **Bookmarks:** 36,506 | **Date:** Feb 12, 2026

---

## The Results

Larry (AI agent) achieved in **under one week**:
- **500K+** total TikTok views
- **234K** views on top post
- **4 posts** over 100K views
- **108** paying subscribers
- **$588/month** MRR
- **$4,000** earned in 5 days (from meme coin community)

**Cost per post:** ~$0.50 in API calls ($0.25 with Batch API)
**Time Ollie spends:** ~60 seconds to add music and publish

---

## Who is Larry?

Larry is an OpenClaw agent running on an old gaming PC (NVIDIA 2070 Super, Ubuntu).

**Larry's capabilities:**
- Personality and memory that persists
- Read/write files
- Generate images via OpenAI API (gpt-image-1.5)
- Code for text overlays
- Post to TikTok via Postiz API
- Skill files for workflows
- Memory files for lessons learned

**Communication:** WhatsApp for research requests.

---

## The Slideshow Format

**Why TikTok slideshows:**
- 2.9x more comments
- 1.9x more likes
- 2.6x more shares
- Algorithm pushing photo content in 2026

**Format specs:**
- **6 slides exactly** (sweet spot for engagement)
- Text overlay on slide 1 (the hook)
- Story-style caption, mentions app naturally
- Max 5 hashtags

---

## Image Generation

**Model:** gpt-image-1.5 via OpenAI API

**Why this model:**
1. Matches Snugly app's output (marketing = product)
2. "iPhone photo" + "realistic lighting" = looks like real phone photo

**Prompt engineering for room transformations:**

Lock the architecture, change only style:
```
iPhone photo of a small UK rental kitchen. Narrow galley style, 
2.5m x 4m. Shot from doorway at near end. Countertops along right 
wall. Small window on far wall, centered, 80cm wide, white UPVC. 
Left wall bare except small fridge freezer. Vinyl flooring. White 
ceiling, fluorescent strip. Natural phone camera quality.

**Beautiful modern country style. Sage green shaker cabinets, 
oak butcher block, white metro tile splashback...**
```

**Bold part** = only thing that changes across 6 slides.

---

## Posting Workflow

**Tool:** Postiz (social media scheduler with API)
- Uploads slideshows as **drafts** (`privacy_level: "SELF_ONLY"`)
- Can't add music via API → manual step
- Ollie adds trending sound, pastes caption, publishes (60 seconds)

**Why drafts?** Music is everything on TikTok. Trending sounds change constantly.

---

## How Larry Learns

**Skill files:** Markdown docs teaching specific workflows
- TikTok skill file: **500+ lines**
- Every rule, spec, lesson learned

**Memory files:** Long-term persistence
- Every post, view count, insight logged
- Brainstorms hooks using actual performance data

**Planning:**
- Brainstorm 10-15 hooks at once
- Reference performance data
- Batch generate via OpenAI Batch API (50% cheaper)

**RevenueCat Integration:**
- Tracks MRR, subscribers, churn
- Daily reports on marketing conversion

---

## Failures (Before Success)

### 1. Stable Diffusion (Local Generation)
- Image quality not photorealistic
- "Uncanny" AI look = scroll past
- API costs ($0.50/post) cheaper than time wrestling with local models

### 2. Wrong Image Specs
- 1536x1024 (landscape) → black bars
- 1024x1536 (portrait) = correct

### 3. Vague Prompts
- Rooms looked different every slide
- Windows appearing/disappearing
- Looked fake (was fake — different rooms, not same room redesigned)

### 4. Unreadable Text
- Font too small (5% vs 6.5%)
- Positioned too high (hidden by status bar)
- Text squashed (lines too long for max width)

### 5. Self-Focused Hooks (All Bombed)
- "Why does my flat look like a student loan" → 905 views
- "See your room in 12+ styles" → 879 views
- "$500 vs $5000 taste" → 2,671 views

---

## Success Formula

**Winning hook formula:**
```
[Another person] + [conflict/doubt] → showed them AI → they changed mind
```

**Winning hooks:**
- "My landlord said I can't change anything so I showed her what AI thinks" → **234,000 views**
- "I showed my mum what AI thinks our living room could be" → **167,000 views**
- "My landlord wouldn't let me decorate until I showed her these" → **147,000 views**

**Key insight:** It's not about the app — it's about the human moment. Create a tiny story in the viewer's head.

---

## Setup Guide

### Requirements
1. **Computer:** 2GB RAM, 1-2 vCPU, 20GB SSD (any old PC/Raspberry Pi/VPS)
2. **OpenClaw:** Free, open source
3. **OpenAI API key:** ~$0.50/post
4. **Postiz:** API for TikTok posting
5. **Skill files:** Markdown docs

### Skill File Contents
- Image sizes/formats (1024x1536 portrait)
- Prompt templates with locked architecture
- Text overlay rules (font size, positioning, line length)
- Caption formulas and hashtag strategy
- Hook formats that work
- **Failure log** (never repeat mistakes)

---

## Key Insights for NEMO

### Content Marketing Application
- **6-slide format** for trading recaps?
- **Hook formula** → "My portfolio was down 50% until I showed my friend this strategy"
- **Batch generation** via OpenAI Batch API (50% cheaper)
- **Postiz scheduling** for X/TikTok

### Agent Learning System
- **Skill files** = 500+ line markdown docs
- **Failure logging** → rules → never repeat
- **Success formulas** → templates
- **Performance data** → informs future hooks

### Cost Efficiency
- $0.50/post with real-time API
- $0.25/post with Batch API
- 60 seconds human time per post
- **Compounding improvement** via skill file iteration

---

## Resources

- **Oliver Henry:** @oliverhenry
- **Larry (the agent):** @LarryClawerence
- **Postiz:** https://affiliate.postiz.com/ollie-warren (affiliate)
- **RevenueCat Skill:** https://clawhub.ai/jeiting/revenuecat
- **Bird (X browsing):** @steipete

---

*"The real unlock isn't the AI itself. It's the system you build around it."* — Ollie & Larry 🐟
