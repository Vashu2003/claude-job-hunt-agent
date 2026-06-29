---
description: Lightweight Telegram poll (every ~2 min) — acknowledge button taps + handle text messages. No job scanning.
allowed-tools: Read, Write, Bash
---

# Lightweight Telegram Poll (no discovery)

Fast and cheap — this runs every ~2 min ONLY to keep Telegram buttons/messages responsive.
Do NOT open a browser, do NOT search jobs, do NOT apply. (The full `/hunt` cycle handles discovery + applying.)

1. `python "<JOBSEARCH_DIR>/scripts/telegram-bridge.py" poll`
   (This acknowledges button taps — answers the callback + edits the message to ✅/❌ — and records
   approve/reject decisions to the queue. Just running it makes the buttons feel responsive.)
2. `python ...\telegram-bridge.py inbox` — for each text message, act + reply via `send`:
   - **stop/pause** → create `STOP` file, reply "Paused ⏸️".
   - **resume** → delete STOP, reply "Resumed ▶️".
   - **status** → reply today's counts from tracker.csv.
   - **targeting tweaks** (skip X, only Y, salary, every N) → edit `hunt-config.json`, confirm.
   - **question** → answer via `send`.
   - **answer to a pending screening question** (if `screening-qa.json` `pending[]` is non-empty and the text
     looks like an answer, not a command) → save `{q,a,added}` to `answers[]`, remove from `pending[]`,
     reply "🧠 Saved — I'll reuse that for '<question>' from now on."
3. For any **approved** items now in `list-decided`: reply via `send` "👍 Approved <role> @ <company> — I'll
   submit it on the next scan." (Leave them in the decided queue; the next `/hunt` does the actual apply.
   Do NOT apply here — no browser in this lightweight cycle.)
4. If nothing happened, stay silent.

Keep it to these bridge calls only — this must stay cheap since it runs frequently.
