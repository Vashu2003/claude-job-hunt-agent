# Contributing to Claude Job-Hunt Agent

Thanks for your interest! This project is a [Claude Code](https://claude.com/claude-code)–driven automation
system, so most contributions are to the **slash commands** (`commands/`), the **scripts** (`scripts/`), the
**example configs/templates**, or the **docs**. PRs and issues are very welcome.

## 🔒 The one hard rule: never commit personal data

This repo ships only **sanitized templates and examples**. Real tokens, profiles, trackers, and resumes live
in a separate working folder and are **git-ignored** (see [`.gitignore`](.gitignore)). Before every commit:

- Do **not** add a real `telegram-config.json`, `hunt-config.json`, `PROFILE.md`, `tracker.csv`,
  `screening-qa.json`, resumes, or any file with a real name, email, phone, bot token, or chat ID.
- Keep example files suffixed with `.example` (e.g. `hunt-config.example.json`) and use `<PLACEHOLDER>` values.
- Quick self-check before pushing:
  ```bash
  git grep -niE "bot[_-]?token|[0-9]{9,}:[A-Za-z0-9_-]{30,}|@gmail\.com|@.*\.com" -- ':!*.example.*' ':!README.md'
  ```
  (Adjust patterns to your case — the goal is zero real secrets/PII in tracked files.)

## 🛠️ Ways to contribute

| Area | Examples |
|---|---|
| **New job sources** | Add a source block to `hunt-config.example.json` + discovery/routing notes in `commands/hunt.md` |
| **ATS form handlers** | Document reliable patterns for Greenhouse / Lever / Ashby / Workable apply flows |
| **Scoring** | Improve the 0–100 fit heuristic against `PROFILE.md` |
| **Platform support** | macOS/Linux path handling, shell differences |
| **Docs** | Setup clarity, screenshots, troubleshooting |
| **Safety** | Better rate-limit defaults, detection-avoidance-free anti-ban hygiene, kill-switch coverage |

## 🚀 Dev setup

1. Fork and clone the repo.
2. Follow the [README setup](README.md#-setup) to create your own **private** working folder (outside the repo)
   with your real config — never inside the cloned repo.
3. Test changes against your own Telegram bot and accounts.
4. The Telegram bridge uses only the Python standard library — no dependencies to install.

## 📐 Conventions

- **Config-driven, never hardcoded.** Behavior belongs in `hunt-config.json`; the commands read it at runtime.
- Match the existing style of the command markdown and JSON comments.
- Keep the safety rails intact: caps, randomized delays, quiet hours, STOP kill switch, honest screening answers,
  and "never enter passwords / create accounts / enter payment info."
- One logical change per PR; describe what you tested.

## 🐛 Reporting issues

Open an issue with: what you tried, what happened, the source/platform involved, and any **redacted** logs
(strip tokens, emails, names). Feature ideas are welcome too.

## 📜 License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
