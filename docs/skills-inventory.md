# NEMO Skills Inventory

**Last Updated:** 2026-02-26  
**Total Skills:** 3  
**Install Script:** `scripts/install-skills.sh`

---

## Quick Install

```bash
# Install all skills at once
bash scripts/install-skills.sh

# Or install individually:
npx skills add https://github.com/alchemyplatform/skills --yes
npx skills add upload-post/upload-post-larry-marketing-skill@tiktok-app-marketing --yes
```

---

## Installed Skills

### 1. `alchemy-api`
**Source:** https://github.com/alchemyplatform/skills  
**Purpose:** Access Alchemy APIs with API key authentication  
**Category:** Blockchain Infrastructure  
**Status:** ✅ Installed  
**Security:** Snyk Med Risk

**Use When:**
- You have `ALCHEMY_API_KEY` environment variable set
- Need standard Alchemy API access (RPC, NFT, Prices, Portfolio)
- Want direct API calls without authentication flows

**Key APIs:**
- Ethereum/Base/Arbitrum RPC
- NFT API (ownership, metadata)
- Prices API (token prices)
- Portfolio API (multi-chain balances)

**Setup:**
```bash
# 1. Get API key at https://alchemy.com
# 2. Set environment variable
export ALCHEMY_API_KEY="your_key_here"

# 3. Start using
curl "https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY" \
  -X POST \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

**Documentation:** `~/.agents/skills/alchemy-api/SKILL.md`

---

### 2. `agentic-gateway`
**Source:** https://github.com/alchemyplatform/skills  
**Purpose:** Access Alchemy APIs WITHOUT API key (wallet-based auth)  
**Category:** Blockchain Infrastructure  
**Status:** ✅ Installed  
**Security:** Snyk Med Risk

**Use When:**
- No `ALCHEMY_API_KEY` is set (default path)
- Want autonomous agent authentication
- Willing to pay per-request via x402 protocol (USDC on Base)

**Authentication Flow:**
1. **Wallet Setup** — Create/fund Ethereum wallet
2. **SIWE Token** — Sign-In With Ethereum
3. **Payment** — x402 protocol handles micropayments
4. **Request** — Send authenticated calls

**Gateway URLs:**
- RPC: `https://x402.alchemy.com/{chainNetwork}/v2`
- NFT: `https://x402.alchemy.com/{chainNetwork}/nft/v3/*`
- Prices: `https://x402.alchemy.com/prices/v1/*`

**Setup:**
```bash
# 1. Install x402 CLI
npm install -g @alchemy/x402

# 2. Create wallet
npx @alchemy/x402 create-wallet

# 3. Fund with USDC on Base
# 4. Generate SIWE token
npx @alchemy/x402 sign-siwe --private-key ./wallet-key.txt
```

**Documentation:** `~/.agents/skills/agentic-gateway/SKILL.md`

---

### 3. `tiktok-app-marketing` (Larrybrain)
**Source:** upload-post/upload-post-larry-marketing-skill@tiktok-app-marketing  
**Purpose:** Automate TikTok + Instagram marketing for apps/products  
**Category:** Social Media Marketing  
**Status:** ✅ Installed  
**Installs:** 27 (as of 2026-02-26)  
**Security:** Snyk High Risk (review before use)

**Based On:** Larry's viral TikTok strategy (7M views, $670 MRR)

**Features:**
- Competitor research (browser-based)
- AI image generation (OpenAI/Stability/Replicate)
- Text overlays on slides (node-canvas)
- Multi-platform posting (Upload-Post API)
- Analytics tracking (views, followers, conversions)
- Feedback loop (optimizes hooks/CTAs)

**Content Pipeline:**
1. Research competitors
2. Generate AI images
3. Add text overlays
4. Post to TikTok + Instagram simultaneously
5. Track analytics
6. Iterate based on performance

**Required Tools:**
- Node.js 18+
- node-canvas (`npm install canvas`)
- Upload-Post account (upload-post.com)
- Image generation API (OpenAI recommended)
- Optional: RevenueCat (conversion tracking)

**Setup:**
```bash
# 1. Run project setup
cd projects/social-presence
bash scripts/setup.sh

# 2. Configure .env file
# UPLOAD_POST_API_KEY=xxx
# OPENAI_API_KEY=xxx

# 3. Review onboarding
~/.agents/skills/tiktok-app-marketing/SKILL.md
```

**Documentation:**
- Skill docs: `~/.agents/skills/tiktok-app-marketing/SKILL.md`
- Project guide: `projects/social-presence/docs/alchemy-skills-summary.md`

---

## Skill Comparison

| Skill | Cost | Setup Time | Auth Method | Best For |
|-------|------|------------|-------------|----------|
| alchemy-api | Free tier, then usage | 5 min | API key | Standard API access |
| agentic-gateway | Pay per request | 15 min | Wallet/SIWE | Autonomous agents |
| tiktok-app-marketing | API costs only | 30 min | API keys | Social media automation |

---

## Security Notes

⚠️ **Review all skills before use:**
- `alchemy-api` and `agentic-gateway`: Snyk Med Risk
- `tiktok-app-marketing`: Snyk High Risk

**Best Practices:**
1. Never commit API keys to git
2. Use `.env` files for credentials
3. Review skill permissions in SKILL.md
4. Test on small scale before production
5. Monitor API usage for unexpected costs

---

## Troubleshooting

### Skill Not Found
```bash
# Update skills CLI
npm update -g skills

# Search for skill
npx skills find <keyword>
```

### Installation Fails
```bash
# Clear npm cache
npm cache clean --force

# Try with verbose output
npx skills add <source> -g -y --verbose
```

### Conflicts
If a skill is installed both locally and globally:
- Local copy overrides global
- Delete one to avoid conflicts

---

## Updating Skills

```bash
# Check for updates
npx skills check

# Update all
npx skills update

# Update specific skill
npx skills update <skill-name>
```

---

## Uninstalling Skills

```bash
# Remove specific skill
rm -rf ~/.agents/skills/<skill-name>

# Remove all skills
rm -rf ~/.agents/skills/*
```

---

## Related Files

- **Install script:** `scripts/install-skills.sh`
- **Inventory:** `docs/skills-inventory.md` (this file)
- **Social project:** `projects/social-presence/README.md`
- **Alchemy guide:** `projects/social-presence/docs/alchemy-skills-summary.md`

---

## Future Skills to Consider

| Skill | Purpose | Priority |
|-------|---------|----------|
| revenuecat | Mobile app revenue tracking | High |
| playwright | Browser automation for X | Medium |
| vercel-react | React/Vercel best practices | Low |
| github-copilot | Code review automation | Low |

---

**Maintained by:** NEMO 🐟  
**Last sync:** 2026-02-26T22:21:00Z
