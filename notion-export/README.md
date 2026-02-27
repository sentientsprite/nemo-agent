# NEMO Notion Workspace Export

**Created**: 2026-02-27  
**Purpose**: Structured backup of all NEMO projects and data  
**Import**: Use Notion's Markdown import feature

---

## How to Import into Notion

1. **Create Notion Account**:
   - Go to https://notion.so
   - Sign up with `sentience.mktg@gmail.com` or new email
   - Create new workspace called "NEMO"

2. **Import This Export**:
   - In Notion: Settings & Members → Import → Markdown & CSV
   - Upload this entire folder as ZIP
   - Or copy-paste individual .md files into pages

3. **Set Up Databases**:
   - Projects, Tasks, Agents, Research are database templates
   - Copy the tables into Notion databases
   - Add properties as specified

---

## Workspace Structure

```
NEMO/
├── 🏠 Dashboard
├── 📊 Projects
│   ├── Trading Bot (24hr Test)
│   ├── Spryte Engine Integration
│   ├── Mission Control
│   └── Social Media Launch
├── ✅ Tasks
│   ├── In Progress
│   ├── Backlog
│   └── Completed
├── 🤖 Agents
│   ├── Active Sub-Agents
│   └── Agent History
├── 📚 Research
│   ├── Polymarket Intelligence
│   ├── Trading Strategies
│   └── Market Analysis
├── 📝 Daily Logs
│   └── 2026-02-27.md
└── 🔒 Secrets (DO NOT IMPORT)
    └── Credentials (excluded)
```

---

## Database Schemas

### Projects Database

| Property | Type | Options |
|----------|------|---------|
| Name | Title | - |
| Status | Select | Active, Paused, Complete, Blocked |
| Priority | Select | Critical, High, Medium, Low |
| Category | Multi-select | Trading, Infrastructure, Research, Marketing |
| Progress | Number | 0-100% |
| Start Date | Date | - |
| Target Date | Date | - |
| Agent Lead | Relation | → Agents |
| Related Tasks | Relation | → Tasks |

### Tasks Database

| Property | Type | Options |
|----------|------|---------|
| Name | Title | - |
| Status | Select | Not Started, In Progress, Done, Blocked |
| Priority | Select | Critical, High, Medium, Low |
| Project | Relation | → Projects |
| Assigned To | Relation | → Agents |
| Due Date | Date | - |
| Estimated Hours | Number | - |
| Actual Hours | Number | - |
| Tags | Multi-select | Bug, Feature, Research, Documentation |

### Agents Database

| Property | Type | Options |
|----------|------|---------|
| Name | Title | - |
| Role | Select | Researcher, Coder, Trader, Analyst, Security, Monitor, Planner, Writer, Learner |
| Status | Select | Idle, Running, Complete, Error |
| Model | Select | Opus, Kimi K2.5, Local |
| Session Key | Text | - |
| Tasks Completed | Number | - |
| Success Rate | Number | % |
| Cost to Date | Number | $ |

### Research Database

| Property | Type | Options |
|----------|------|---------|
| Title | Title | - |
| Category | Select | Trading, Market, Competitor, Regulatory |
| Source | URL | - |
| Date | Date | - |
| Agent | Relation | → Agents |
| Key Findings | Text | - |
| Action Items | Text | - |
| File Path | Text | Local file location |

---

## Excluded Data

**DO NOT IMPORT to Notion**:
- API keys and tokens
- Private keys
- Wallet addresses
- Credentials
- `.env` files

**Keep these in local encrypted storage only.**

---

## Automation Ideas

Once imported, consider:
- Daily sync from `memory/` folder
- Weekly project status updates
- Agent cost tracking dashboard
- Research findings auto-import

---

**NEMO Workspace Export Ready** 🐟
