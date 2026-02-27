# jordymaui: OpenClaw Setup Guide (Beginner)

**Source:** https://x.com/jordymaui/status/2023421221744877903  
**Author:** jordy (@jordymaui)  
**Views:** 3,295,021 | **Bookmarks:** 33,347 | **Date:** Feb 16, 2026

---

## The Cost of Learning

jordy wasted **80 hours and $800** making mistakes so you don't have to.

**Mistakes made:**
- AWS servers, remote setups, wrong API keys, wrong models
- $800 burned on Anthropic API tokens alone
- 8 agents running simultaneously with different brains
- Context always got lost between agents

**What you actually need:** 4 accounts, 30 minutes, copy/paste skills.

---

## Requirements (Bare Minimum)

### Hardware
- **2GB RAM**
- **1-2 CPU cores**
- **20GB storage**
- Any computer that stays on (old laptop, Raspberry Pi, Mac Mini)

### Four Accounts Needed

| Account | Purpose | Cost |
|---------|---------|------|
| **Claude Pro/Max** | The brain | $20-90/month |
| **Brave Search** | Web search | Free |
| **Groq** | Voice transcription | Free |
| **Telegram** | Messaging | Free |

**CRITICAL:** Use **Claude membership token**, NOT Anthropic console API. The membership is way cheaper than pay-per-use.

---

## Setup Steps

### Step 1: Get Claude Token
```bash
curl -fsSL https://claude.ai/install.sh | bash
claude setup-token
```
Copy token (remove any trailing spaces!).

### Step 2: Install Homebrew & Node
```bash
brew install node
```

### Step 3: Install OpenClaw
```bash
npm install -g openclaw
```

### Step 4: Onboarding
- Select **ANTHROPIC** (not Anthropic API)
- Select **ANTHROPIC TOKEN** (first option)
- Paste your Claude token

### Step 5: Connect Telegram
- Message @BotFather `/newbot`
- Get API token
- Paste into Terminal

### Step 6: First Skills
- Select 'npm'
- Skip the preset skills (noise)
- Skip Google Places, ElevenLabs
- Enable all 3 hooks

### Step 7: Hatch
Select 'hatch in TUI' to wake bot.

**HTTPS error?** Check Claude token for spaces.

### Step 8: Connect Telegram
Send to bot:
```
Hey, your name is [botname], my name is [your name], let's continue 
on Telegram. Here's my pairing key [pastekey].
```

Type pairing key in Telegram. Done!

### Final Step: Add Tools
Tell your bot:
- "Setup Brave Search — here's my API key"
- "Setup Groq — here's my key"
- "Install the QMD skill"

**Important:** Install QMD from the start, not halfway through.

---

## Make It Yours (The Important Bit!)

### Three Key Files

| File | Purpose |
|------|---------|
| **SOUL.md** | Agent's personality, voice, style |
| **USER.md** | Info about you, preferences, habits |
| **MEMORY.md** | Long-term memory between conversations |

### Quick Setup Method
Tell your agent:
```
You just came online. Ask me questions to get to know me — 
my name, what I do, goals, how I want you to talk, tools I use. 
Ask one at a time. Use answers to fill out SOUL.md and USER.md.
```

**Pro tip:** Reply with voice notes. More natural answers.

---

## Skills vs Agents (Don't Waste Money)

❌ **Wrong:** 5-10 agents, "hivebrain," agents talking to agents  
✅ **Right:** One agent with proper skills

Multi-agent = expensive, confusing, mostly bollocks.

---

## Mistakes to Avoid

| # | Mistake | Solution |
|---|---------|----------|
| 1 | Paid per use vs Claude Max | Get membership, use token |
| 2 | 8 agents on Telegram | One agent with skills |
| 3 | Spent hundreds on AWS | Mac Mini next to TV |
| 4 | Left context files empty | Fill SOUL.md + USER.md |
| 5 | Installed QMD halfway | Install from start |
| 6 | Ignored voice messages | Setup Groq day one |
| 7 | Space in Claude token | Check for trailing spaces |

---

## Key Insights for NEMO

### Setup Validation
- ✅ Mac Mini — correct choice
- ✅ Claude Pro/Max — correct
- ✅ SOUL.md + USER.md — already done
- ✅ Memory files — already implemented
- ⏳ QMD skill — consider installing
- ⏳ Groq voice — could add

### Cost Optimization
- Claude Max ($90/month) > Anthropic API pay-per-use
- Brave Search (free) for web search
- Groq (free) for voice

### Architecture Confirmation
- One agent (NEMO) with skills > Multi-agent confusion
- Skills = capabilities without losing context
- Our Mission Control approach is correct

---

## Action Items

- [ ] Consider installing QMD skill (95% token reduction)
- [ ] Evaluate Groq for voice interactions
- [ ] Review skill file approach vs agent spawning
- [ ] Ensure QMD installed from start (not retrofitted)

---

*"Every mistake I made so you don't have to."* — jordy 🐟
