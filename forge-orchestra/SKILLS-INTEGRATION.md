# Skills Integration Guide

## Overview

ForgeOrchestra workspaces integrate with OpenClaw skills to provide specialized capabilities. This document defines which skills are relevant and how they connect to the ForgeOrchestra product family.

---

## Core Skills for ForgeOrchestra

### 1. Skill Creator (`skill-creator`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/skill-creator/SKILL.md`

**Purpose:** Create, edit, audit, and improve AgentSkills.

**ForgeOrchestra Integration:**
- Use for building ForgeOrchestra-specific skills
- Create product-specific automation skills (ForgeCalendar-sched, ForgePipeline-deploy, etc.)
- Audit existing skills for brand consistency
- Maintain skill documentation standards

**Usage Triggers:**
- "Create a skill for ForgeOrchestra"
- "Audit the ForgePipeline skill"
- "Improve this skill's documentation"
- "Clean up the skill directory"

---

### 2. Coding Agent (`coding-agent`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/coding-agent/SKILL.md`

**Purpose:** Delegate coding tasks to Codex, Claude Code, or Pi agents.

**ForgeOrchestra Integration:**
- Build new ForgeOrchestra product features
- Refactor large codebases across product family
- Review PRs for product consistency
- Iterative UI/UX development

**Usage Patterns:**
```bash
# Spawn sub-agent for feature development
sessions_spawn runtime="acp" task="Build ForgeCalendar timeline view"

# Spawn for PR review (temp dir)
sessions_spawn runtime="acp" task="Review PR #42 for ForgePipeline"
```

**Constraints:**
- NOT for simple one-liner fixes (use `edit` tool)
- NOT for reading code (use `read` tool)
- NEVER spawn agents in `~/clawd` workspace
- Thread-bound ACP harness requests use `sessions_spawn` with `runtime:"acp"`

---

### 3. Healthcheck (`healthcheck`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/healthcheck/SKILL.md`

**Purpose:** Host security hardening and risk-tolerance configuration.

**ForgeOrchestra Integration:**
- Security audits for ForgeOrchestra deployments
- Firewall/SSH/update hardening
- Risk posture reviews
- OpenClaw cron scheduling for periodic checks
- Version status checks on production machines

**Usage Triggers:**
- "Run security audit on ForgeOrchestra deployment"
- "Check risk posture for production"
- "Schedule periodic healthchecks"
- "Review exposure on titan host"

---

### 4. Node Connect (`node-connect`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/node-connect/SKILL.md`

**Purpose:** Diagnose OpenClaw node connection and pairing failures.

**ForgeOrchestra Integration:**
- Debug node pairing for ForgeOrchestra companion apps
- Fix QR/setup code/manual connect failures
- Resolve Wi-Fi vs VPS/tailnet connectivity issues
- Diagnose pairing token errors

**Error Patterns:**
- "pairing required"
- "unauthorized"
- "bootstrap token invalid/expired"
- "gateway.bind" errors
- "gateway.remote.url" issues
- Tailscale connectivity failures

---

### 5. TMUX (`tmux`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/tmux/SKILL.md`

**Purpose:** Remote-control tmux sessions for interactive CLIs.

**ForgeOrchestra Integration:**
- Monitor long-running ForgePipeline deployments
- Interactive debugging sessions
- Remote server management
- Multi-pane workflow orchestration

**Usage:**
- Send keystrokes to tmux panes
- Scrape pane output for status
- Control remote interactive sessions

---

### 6. Video Frames (`video-frames`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/video-frames/SKILL.md`

**Purpose:** Extract frames or short clips from videos using ffmpeg.

**ForgeOrchestra Integration:**
- ForgeDisplay: Extract frames for presentation assets
- Create thumbnail previews for video content
- Generate clip summaries for dashboards

**Usage:**
```bash
# Extract frames
ffmpeg -i input.mp4 -vf "fps=1" frame-%03d.png

# Create short clip
ffmpeg -i input.mp4 -ss 00:00:10 -t 00:00:30 -c copy clip.mp4
```

---

### 7. Weather (`weather`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/weather/SKILL.md`

**Purpose:** Get current weather and forecasts via wttr.in or Open-Meteo.

**ForgeOrchestra Integration:**
- ForgeCalendar: Weather overlays for event planning
- Dashboard widgets for location-aware scheduling
- Contextual reminders based on conditions

**Usage Triggers:**
- "What's the weather in London?"
- "Forecast for this weekend"
- "Temperature for outdoor event"

**Constraints:**
- NOT for historical weather data
- NOT for severe weather alerts
- NOT for detailed meteorological analysis

---

### 8. ClawHub (`clawhub`)

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/clawhub/SKILL.md`

**Purpose:** Search, install, update, and publish agent skills from clawhub.com.

**ForgeOrchestra Integration:**
- Fetch new skills on the fly
- Sync installed skills to latest version
- Publish ForgeOrchestra skills to clawhub.com
- Manage skill dependencies

**Usage:**
```bash
# Install skill
clawhub install forge-calendar-sched

# Update skills
clawhub sync

# Publish new skill
clawhub publish ./forge-pipeline-deploy
```

---

## Session Management Skills

### Sessions List

**Purpose:** List other sessions (incl. sub-agents) with filters/last.

**ForgeOrchestra Usage:**
- Monitor active ForgeOrchestra product sessions
- Check sub-agent status for pipeline runs
- Track concurrent workflow executions

---

### Sessions History

**Purpose:** Fetch history for another session/sub-agent.

**ForgeOrchestra Usage:**
- Review past ForgePipeline execution logs
- Audit ForgeCalendar scheduling decisions
- Debug failed agent runs

---

### Sessions Send

**Purpose:** Send a message to another session/sub-agent.

**ForgeOrchestra Usage:**
- Notify completion of long-running tasks
- Coordinate between product sessions
- Deliver results to main session

---

### Sessions Spawn

**Purpose:** Spawn isolated sub-agent or ACP coding session.

**ForgeOrchestra Usage:**
```json
{
  "runtime": "acp",
  "task": "Deploy ForgePipeline to production",
  "thread": true,
  "mode": "session"
}
```

**Patterns:**
- Discord thread-bound persistent sessions (`thread: true`)
- ACP harness requests use `runtime: "acp"`
- Set `agentId` explicitly unless `acp.defaultAgent` configured

---

### Subagents

**Purpose:** List, steer, or kill sub-agent runs.

**ForgeOrchestra Usage:**
- Monitor active ForgeOrchestra sub-agents
- Steer long-running pipeline executions
- Kill stuck or failed agent runs

---

### Sessions Yield

**Purpose:** End current turn after spawning subagents.

**Usage:**
```
Spawn sub-agent → sessions_yield → receive results next message
```

---

## Memory Skills

### Memory Search

**Purpose:** Mandatory recall step - semantically search MEMORY.md + memory/*.md.

**ForgeOrchestra Usage:**
- Search prior workflow decisions
- Recall deployment configurations
- Find past integration patterns
- Check team preferences

**Rule:** Always run before answering questions about prior work, decisions, dates, people, preferences, or todos.

---

### Memory Get

**Purpose:** Safe snippet read from MEMORY.md or memory/*.md.

**Usage:**
- Pull only needed lines after memory_search
- Keep context small
- Include source citations

---

## Infrastructure Skills

### Gateway

**Purpose:** Restart, apply config, or run updates on OpenClaw process.

**ForgeOrchestra Usage:**
- Apply ForgeOrchestra config changes
- Restart after skill updates
- Run self-update when explicitly requested

**Actions:**
- `config.schema.lookup` - inspect config subtree
- `config.patch` - partial update (safe, merges)
- `config.apply` - full config replacement
- `update.run` - update deps or git

---

### Cron

**Purpose:** Manage cron jobs and wake events.

**ForgeOrchestra Usage:**
- Schedule periodic healthchecks
- Set reminders for deployments
- Batch periodic checks (inbox + calendar + notifications)
- One-shot reminders ("remind me in 20 minutes")

**Job Types:**
- `systemEvent` → main session
- `agentTurn` → isolated session

**Schedule Types:**
- `at` - one-shot timestamp
- `every` - recurring interval
- `cron` - cron expression

---

### Nodes

**Purpose:** Discover and control paired nodes.

**ForgeOrchestra Usage:**
- Control node canvases (ForgeDisplay)
- Camera snapshots for monitoring
- Screen recording for demos
- Location data for context-aware scheduling
- Notifications for completion alerts

---

### Canvas

**Purpose:** Control node canvases (present/hide/navigate/eval/snapshot).

**ForgeOrchestra Usage:**
- ForgeDisplay: Present dashboard canvases
- Capture rendered UI for documentation
- Evaluate JavaScript for interactive displays

---

### Browser

**Purpose:** Control web browser via OpenClaw's browser control server.

**ForgeOrchestra Usage:**
- ForgeDisplay: Web-based dashboards
- UI automation for testing
- Screenshot capture for documentation
- PDF generation for reports

**Profiles:**
- Omit profile → isolated OpenClaw-managed browser
- `profile="user"` → logged-in user browser

---

### Message

**Purpose:** Send messages and channel actions.

**ForgeOrchestra Usage:**
- Deliver completion notifications
- Send updates to Discord/Slack/Telegram
- Channel actions (polls, reactions)
- Cross-session messaging

**Rule:** If using `message` (`action=send`) to deliver user-visible reply, respond with `NO_REPLY` to avoid duplicates.

---

### TTS

**Purpose:** Convert text to speech.

**ForgeOrchestra Usage:**
- ForgeDisplay: Voice storytelling
- Audio summaries for dashboards
- "Storytime" moments with funny voices

**Rule:** Reply with `NO_REPLY` after successful call to avoid duplicate messages.

---

### Web Search

**Purpose:** Search the web using DuckDuckGo.

**ForgeOrchestra Usage:**
- Research integration patterns
- Check skill documentation
- Find best practices
- Competitive analysis

---

### Web Fetch

**Purpose:** Fetch and extract readable content from URL.

**ForgeOrchestra Usage:**
- Extract documentation from URLs
- Convert HTML → markdown
- Lightweight page access without browser

---

## Skill Integration Checklist

When spinning up a new ForgeOrchestra workspace:

### Core Skills
- [ ] `skill-creator` - for building ForgeOrchestra skills
- [ ] `coding-agent` - for product development
- [ ] `healthcheck` - for security audits
- [ ] `node-connect` - for node pairing
- [ ] `clawhub` - for skill management

### Product-Specific Skills
- [ ] `tmux` - for pipeline monitoring
- [ ] `video-frames` - for ForgeDisplay assets
- [ ] `weather` - for ForgeCalendar context

### Session Management
- [ ] `sessions_spawn` - for sub-agent orchestration
- [ ] `sessions_list` - for monitoring
- [ ] `sessions_history` - for audit
- [ ] `sessions_send` - for coordination
- [ ] `subagents` - for steering
- [ ] `sessions_yield` - for completion

### Memory
- [ ] `memory_search` - mandatory recall
- [ ] `memory_get` - snippet retrieval

### Infrastructure
- [ ] `gateway` - config/update management
- [ ] `cron` - scheduling
- [ ] `nodes` - device control
- [ ] `canvas` - display control
- [ ] `browser` - web automation
- [ ] `message` - notifications
- [ ] `tts` - voice output
- [ ] `web_search` - research
- [ ] `web_fetch` - content extraction

---

## Workspace Skills Directory

ForgeOrchestra workspaces should include:

```
forge-orchestra/
├── skills/
│   ├── forge-calendar-sched/
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── scripts/
│   ├── forge-pipeline-deploy/
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── scripts/
│   └── forge-display-render/
│       ├── SKILL.md
│       ├── README.md
│       └── scripts/
└── SKILLS-INTEGRATION.md  # This file
```

---

## Skill Development Standards

All ForgeOrchestra skills must:

1. Follow AgentSkills spec
2. Include complete SKILL.md documentation
3. Use consistent naming: `forge-[product]-[function]`
4. Respect brand guidelines in documentation
5. Include usage examples
6. Define clear triggers
7. List constraints and boundaries
8. Test before publishing to clawhub

---

## Skill Publishing Workflow

```bash
# 1. Develop skill locally
cd forge-orchestra/skills/forge-calendar-sched

# 2. Audit with skill-creator
openclaw skill audit ./forge-calendar-sched

# 3. Test skill
openclaw skill test ./forge-calendar-sched

# 4. Publish to clawhub
clawhub publish ./forge-calendar-sched

# 5. Sync across installations
clawhub sync
```

---

**Skills are the instruments. ForgeOrchestra is the conductor.**
