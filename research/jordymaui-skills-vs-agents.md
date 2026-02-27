# jordymaui: Skills Beat Agents - OpenClaw Guide

**Source:** https://x.com/jordymaui/status/2024251460553199935  
**Author:** jordy (@jordymaui)  
**Views:** 352,291 | **Bookmarks:** 3,271 | **Date:** Feb 18, 2026

---

## The Multi-Agent Trap

The author had **8 agents running simultaneously**: Opus "brain" coordinating Kimi agents for writing, dev, design, research. Each with separate API keys, context, bills.

**The problems:**
- Agents forgot what others were doing
- Context lost between handoffs
- More time managing agents than working
- **Cost:** Hundreds of dollars in token costs

---

## Skills vs Agents

| Agents | Skills |
|--------|--------|
| Separate brains | Same brain, new capability |
| Own memory/context | Shared memory |
| Spin up = new employee | Like learning new skill |
| No context sharing | Full context retention |
| High cost (8x tokens) | Low cost (skill file = few hundred lines) |

**Analogy:** You don't hire a new person for every task — you learn skills. Skills are the "limitless pill but permanent."

---

## jordy's Skill Setup

**Momo (his agent)** uses:
- **X skill** — scanning, writing tweets, engagement analysis
- **Writing skill** — his voice, banned words, sentence structure
- **Finance skill** — budget, income, business accounting
- **Sport.Fun skill** — work-related brand voice, strategy, product
- **Larry skill** — @oliverhenry's social media engine (TikTok, scheduling)

**How it works:**
- `#x-scan` Discord channel → loads X skill
- `#finances` channel → loads finance skill
- Same agent, same memory, different capability

---

## When Multi-Agent Makes Sense

1. **Heavy isolated tasks** — 30 min deep research, spawn sub-agent, report back
2. **Different models for different jobs** — cheap model for scraping, good model for analysis
3. **Shared environments** — multiple people, separate permissions

**For personal use:** One agent + skills = done.

---

## The Cost Reality

**Multi-agent:**
- 8 agents × context loading
- 8 × personality files
- 8 × memory retrieval
- Handoff costs between agents

**Single agent + skills:**
- Load SOUL.md once
- Load USER.md once
- Skill file = few hundred lines

**Author's cost:** $90/month Claude Max subscription vs hundreds/week on multi-agent.

---

## Skill Setup

```
workspace/
└── skills/
    └── email/
        └── SKILL.md
```

**SKILL.md example:**
```markdown
When writing emails for [name]:
- Keep them short. 3-5 sentences max.
- Start with the person's name, no "Dear"
- Sign off with just your name
- Never use "just following up"
- Don't use mdashes
```

**Community skills:** Install from ClawHub — `install the [name] skill`

---

## Larry Skill Success Story

**@oliverhenry's "Larry" agent:**
- One skill file
- Content creation + scheduling + posting
- **Results:** 8M TikTok views in one week, $4K in 24 hours
- **Tool:** Postiz (open-source social media scheduler)

**Install:** `install Larry skill` from ClawHub

---

## Recommended Setup

1. **One main agent** — proper personality, SOUL.md, USER.md
2. **Skills for repeating tasks** — do it twice? Make a skill
3. **Channels as departments** — each channel maps to skill
4. **Sub-agents for heavy lifting only** — background tasks, not daily ops
5. **Memory files for continuity** — daily notes, heartbeat checks

---

## Key Insight for NEMO

This validates our **Mission Control architecture:**
- **Commander** (main agent) = one brain, full context
- **Specialized agents** = skills, not separate instances
- **Cost efficiency** = Kimi for sub-tasks, Opus for critical

**We're building it right** — one commander delegating to skill-based sub-agents, not 8 separate brains.

---

## Action Items

- [ ] Create SKILL.md templates for Researcher, Coder, Trader
- [ ] Test "skill" approach vs full agent spawning
- [ ] Evaluate cost difference between skill-loading vs agent-spawning
- [ ] Consider Larry skill for content marketing

---

*"The best AI setup isn't the most complex one. It's the one that disappears into your workflow and just helps."* — jordy 🐟
