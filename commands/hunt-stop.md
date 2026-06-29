---
description: Stop / pause the autonomous job hunt loop
allowed-tools: Read, Write, Bash
---

# Stop the autonomous job hunt

1. Create the `STOP` file in your JobSearch dir (every `/hunt` cycle checks for it and aborts immediately).
   ```bash
   touch "<JOBSEARCH_DIR>/STOP"
   ```
2. Send a Telegram confirmation:
   `python "<JOBSEARCH_DIR>/scripts/telegram-bridge.py" send "⏸️ Job hunt paused. Text 'resume' or run /hunt-start to restart."`

Any in-flight cycle finishes its current step and then halts. No new discovery or applies happen while STOP exists.
