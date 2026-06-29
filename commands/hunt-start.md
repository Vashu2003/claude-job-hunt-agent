---
description: Start the autonomous job hunt loop
allowed-tools: Read, Write, Bash, Skill
---

# Start the autonomous job hunt

1. Delete the `STOP` file in your JobSearch dir if it exists (so cycles can run).
2. Send a Telegram message via
   `python "<JOBSEARCH_DIR>/scripts/telegram-bridge.py" send "<msg>"`:
   "▶️ Autonomous job hunt STARTED. Every ~10 min I'll find fresh roles, auto-apply to strong matches (and
   message you each one), ask you here on borderline ones, and watch Gmail for replies. Text: status / stop / tweaks."
3. Start the recurring loop: invoke the **loop** skill with argument `10m /hunt` so the `/hunt` cycle runs
   every 10 minutes until stopped.

That's it — from here everything happens automatically and all updates come to Telegram. You only ever
need `/hunt-start` and `/hunt-stop` (or texting the bot).
