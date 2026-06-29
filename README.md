# 🤖 Claude Job-Hunt Agent

> **An autonomous AI job-application bot** that auto-applies to jobs on **LinkedIn**, **Naukri**, **Indeed**,
> and startup boards — controlled entirely from **Telegram**. Built on [Claude Code](https://claude.com/claude-code)
> with browser automation, Gmail reply-tracking, and a human-in-the-loop approval flow.

<p>
<img alt="Built with Claude Code" src="https://img.shields.io/badge/built%20with-Claude%20Code-8A2BE2">
<img alt="Python 3" src="https://img.shields.io/badge/python-3.x-blue">
<img alt="PowerShell" src="https://img.shields.io/badge/PowerShell-5391FE?logo=powershell&logoColor=white">
<img alt="Platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey">
<img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green">
<img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen">
</p>

It discovers fresh roles across multiple sources, scores each one against your profile, **auto-applies** to
strong matches, asks you on **Telegram** for borderline ones, watches **Gmail** for replies, and drafts
referral & cold-emails for you to review — all while you're away from the keyboard.

> You text a Telegram bot `status` / `stop` / `resume` / tweaks. Everything else runs itself.

**Keywords:** automated job search · LinkedIn Easy Apply bot · Naukri auto-apply · AI job application agent ·
Claude Code automation · Telegram bot · browser automation · Gmail integration · job hunt automation · LLM agent.

---

## ✨ What it does

| Capability | How |
|---|---|
| **Multi-source discovery** | LinkedIn, Naukri, Indeed (connector), Wellfound / Cutshort / Instahyre |
| **Smart scoring** | Reads the *actual* job description and scores 0–100 against your `PROFILE.md` |
| **Auto-apply** | LinkedIn Easy Apply + Naukri one-click, with rate limits & randomized delays |
| **Send-link** | External / company-site roles get pushed to your phone via Telegram to apply manually |
| **Human-in-the-loop** | Borderline scores → Approve/Reject buttons in Telegram |
| **Screening memory** | Remembers answers to recruiter questions and reuses them next time |
| **Gmail watch** | Detects application replies and pings you |
| **Referrals & cold-email** | Drafts alumni DMs and personalized cold-emails (as Gmail *drafts* you approve) |
| **Kill switch + quiet hours** | A `STOP` file halts everything; configurable quiet window |

---

## 🧱 Architecture

```
Claude Code (the agent)
   │
   ├── /hunt        ← one full cycle: discover → score → apply → ask → report
   ├── /poll        ← lightweight 2-min Telegram poll (keeps buttons responsive)
   ├── /hunt-start  ← delete STOP + start the recurring loop
   └── /hunt-stop   ← create STOP (kill switch)
   │
   ├── Browser automation (Claude-in-Chrome) → LinkedIn / Naukri / startup sites
   ├── Gmail connector                        → read replies, draft cold-emails
   ├── Indeed connector                       → search (read-only)
   │
   └── scripts/
        ├── telegram-bridge.py  ← all Telegram I/O (stdlib only, no pip installs)
        └── job-tracker.ps1     ← append/report on tracker.csv
```

**Config-driven, never hardcoded.** All behavior (thresholds, sources, caps, target titles) lives in
`hunt-config.json`. Your identity lives in `PROFILE.md`. The agent reads both every cycle.

---

## 🚀 Setup

### 1. Prerequisites
- [Claude Code](https://claude.com/claude-code) installed and signed in
- **Python 3** (the Telegram bridge uses only the standard library — no `pip install`)
- A Chrome browser with the **Claude-in-Chrome** extension (for LinkedIn/Naukri automation)
- *(Optional)* Gmail + Indeed connectors enabled in Claude for reply-watching and Indeed search

### 2. Create your working folder
Pick a folder for your private data (referred to as `<JOBSEARCH_DIR>` below), e.g. `~/JobSearch`. Copy the
example files into it and drop the `.example` suffix:

```
<JOBSEARCH_DIR>/
├── scripts/
│   ├── telegram-bridge.py        # copied from this repo
│   ├── job-tracker.ps1           # copied from this repo
│   └── telegram-config.json      # from config/telegram-config.example.json — YOUR token
├── hunt-config.json              # from config/hunt-config.example.json — YOUR rules
├── PROFILE.md                    # from templates/PROFILE.example.md — YOUR profile
├── screening-qa.json             # from templates/screening-qa.example.json
├── cold-email.md                 # from templates/cold-email.example.md
├── outreach.md                   # from templates/outreach.example.md
└── tracker.csv                   # from templates/tracker.example.csv
```

### 3. Install the slash commands
Copy the four files in `commands/` into your Claude Code commands folder
(`~/.claude/commands/` on macOS/Linux, `%USERPROFILE%\.claude\commands\` on Windows), then **edit each one**
to replace `<JOBSEARCH_DIR>` with the absolute path to your folder.

### 4. Create a Telegram bot
1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the **token**.
2. Send any message to your new bot once.
3. Run `python scripts/telegram-bridge.py whoami` to find your numeric **chat_id**.
4. Put both into `telegram-config.json`.

### 5. Fill in `PROFILE.md` and `hunt-config.json`
The match quality is only as good as your profile. Be specific and honest. Set your target titles, exclude
patterns, salary, notice period, and location in `hunt-config.json`.

### 6. Run it
```
/hunt-start      # starts the autonomous loop; all updates go to Telegram
/hunt-stop       # pauses everything (creates the STOP file)
```
Or just text the bot: `status`, `stop`, `resume`, or tweaks like "only remote" / "skip Acme".

---

## ⚙️ Key config knobs (`hunt-config.json`)

| Key | Meaning |
|---|---|
| `runMode.autoApply` | `true` = auto-submit strong matches; `false` = discover + ask only (safer) |
| `scoring.autoApplyThreshold` / `approvalThreshold` | ≥auto = submit, between = ask, below = discard |
| `safetyRails.dailyAutoApplyCap` / `maxAppliesPerCycle` | Hard limits on submissions |
| `safetyRails.quietHours` | Don't act during these local hours |
| `match.includeTitles` / `excludePatterns` / `maxYearsExperienceRequired` | Targeting filters |
| `sources.*` | Enable/disable each job board and set its apply strategy |
| `applicationDefaults` | Standard honest answers to screening questions |

---

## 🛡️ Safety & ethics

This system is built with guardrails on by default:
- **Never** enters passwords, creates accounts, or enters payment info — it skips those jobs.
- **Never** fabricates answers to screening questions; unknown ones are escalated to you on Telegram.
- Cold-emails are saved as **drafts for your review**, never auto-sent — and only to *verified* addresses.
- Rate limits + randomized delays + a JD-reading quality gate keep it human-paced.
- A `STOP` file is an instant kill switch checked every cycle.

Use it on your own accounts, within each platform's terms. Auto-apply is a convenience, not a spam cannon —
keep the caps conservative.

---

## 📂 Repo layout

```
commands/    slash commands for Claude Code (hunt, poll, hunt-start, hunt-stop)
scripts/     telegram-bridge.py (Telegram I/O) + job-tracker.ps1 (CSV tracker)
config/      *.example.json  → copy, rename, fill in
templates/   PROFILE / screening-qa / cold-email / outreach / tracker examples
```

> All real data (tokens, profile, tracker, resumes) is **git-ignored** — see `.gitignore`.

---

## 🙋 Who is this for?

- Job seekers who want to **apply to more roles in less time** without sitting at the keyboard all day.
- Developers who want a **real-world Claude Code agent** example: browser automation + connectors + a
  Telegram control plane + config-driven behavior + human-in-the-loop approvals.
- Anyone building **autonomous LLM agents** who wants a worked example of safety rails, rate limiting,
  approval queues, and answer-memory.

## ❓ FAQ

**Does it auto-apply on LinkedIn?** Yes — LinkedIn Easy Apply and Naukri one-click are auto-submitted (within
your caps). External/company-site roles are sent to your phone as a link to apply manually.

**Is it safe / will my account get banned?** It's built to be conservative: rate limits, randomized delays,
quiet hours, a `STOP` kill switch, and a JD-reading quality gate. Keep the caps low. Use at your own risk and
within each platform's terms.

**Do I need to write code?** No — you fill in `PROFILE.md` and `hunt-config.json`, create a Telegram bot, and
run the slash commands. Everything is config-driven.

**Does it cost money?** It runs on Claude Code (your subscription) + a free Telegram bot. No paid scraping tools.

**Can I use it without auto-apply?** Yes — set `runMode.autoApply: false` for "discover + notify only" (hybrid) mode.

## 🤝 Contributing

PRs and issues welcome — new job sources, ATS form handlers, better scoring, or platform support. Please don't
commit any personal data (the `.gitignore` is set up to prevent it).

## 🏷️ Topics

`claude` · `claude-code` · `anthropic` · `ai-agent` · `llm` · `job-search` · `job-application` · `automation` ·
`telegram-bot` · `browser-automation` · `linkedin` · `naukri` · `indeed` · `gmail-api` · `web-scraping` ·
`autonomous-agent` · `recruiting` · `python` · `powershell` · `productivity`

## 📜 License

MIT — see [LICENSE](LICENSE). Built with [Claude Code](https://claude.com/claude-code).

---

*Tags: automated job application bot, LinkedIn auto apply, Naukri automation, AI job hunt assistant, Claude
Code agent example, Telegram-controlled automation, autonomous job search agent, LLM browser automation.*
