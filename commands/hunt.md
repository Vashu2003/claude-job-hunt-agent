---
description: One AUTONOMOUS cycle — discover, score, auto-apply strong matches, ask Telegram on borderline, monitor Gmail
allowed-tools: Read, Write, Edit, Bash, WebSearch, WebFetch, mcp__claude-in-chrome__*, mcp__claude_ai_Gmail__*
---

# Autonomous Job-Hunt Cycle

Run ONE cycle. Fast, safe, quiet. Read all rules from `hunt-config.json`; never hardcode.

**TELEGRAM IS THE ONLY CHANNEL TO THE USER** (they're away). Send every result/question/warning via the
bridge: `python "<JOBSEARCH_DIR>/scripts/telegram-bridge.py" <cmd>`. Never block waiting.

> Replace `<JOBSEARCH_DIR>` with the absolute path to your own JobSearch folder (see README).

## 0. Pre-flight (abort if any fail)
1. Read `hunt-config.json`. Confirm `runMode.autoApply` is true (else this is hybrid — skip applies).
2. If `STOP` file exists in the JobSearch dir → print "🛑 STOP" and END.
3. If local time within quietHours → print "😴 Quiet hours" and END.
4. Read `tracker.csv` for dedupe + today's auto-apply count. If `[auto]` count today >= dailyAutoApplyCap →
   skip the auto-apply step (still discover, handle approvals, check Gmail).

## 1. Handle Telegram first
1. `python ...\telegram-bridge.py poll` then `inbox`. Act on messages: stop→STOP file+END; resume→delete STOP;
   status→reply counts; targeting tweaks→edit hunt-config + confirm; questions→answer.
2. `python ...\telegram-bridge.py list-decided`. For each **approved** → apply now (section 3) + log +
   `resolve --id <id> --status applied`. For **rejected** → `resolve --id <id> --status rejected`.

## 2. Discover (browser) — multi-source
Ensure browser: `tabs_context_mcp`. Search each ENABLED source in `sources`, rotating a keyword from
`match.includeTitles` in `match.locations`, last 24h, newest first:
- **LinkedIn** — search WITHOUT the Easy-Apply-only filter (drop `f_AL=true`) so external-apply roles also
  appear. Tag each result `linkedinEasyApply` (shows "Easy Apply") or `linkedinExternal` (no Easy Apply).
- **Naukri** (`sources.naukri.enabled`) — works via the user's AUTHENTICATED Chrome (logged in → Akamai
  allows it; headless/un-logged-in gets bot-blocked). Navigate naukri.com search URLs in the controlled tab,
  e.g. `https://www.naukri.com/full-stack-developer-jobs-in-bangalore?experience=1` (rotate keyword; add
  `&wfh=true` for remote). Read JDs via get_page_text. Tag `naukri`. Routing for STRONG matches:
  open the job, check the apply button — **direct Naukri "Apply" (one-click)** → AUTO-APPLY (submits saved
  Naukri profile/resume; if a chatbot/screening modal pops up, answer from `applicationDefaults`, else
  skip + send-link). **"Apply on company site"** (external redirect) → SEND-LINK. Naukri auto-applies count
  toward `dailyAutoApplyCap`/`maxAppliesPerCycle`. Keep human-paced; if a scan hits an Akamai/"unusual
  activity" block, skip Naukri that cycle (Gmail Naukri alerts are the fallback).
- **Indeed** (`sources.indeed.enabled`) — use the **Indeed CONNECTOR** tools (`mcp__claude_ai_Indeed__*`:
  Job Search / Job Details / Company Information), NOT the browser (Cloudflare-blocks it). Read-only →
  always send-link (never auto-apply; connector has no apply tool). Tag `indeed`.
- **Startup sources** (`sources.wellfound` / `instahyre` / `cutshort`, all `login_required`) — junior-friendly,
  less competition. Work via the user's AUTHENTICATED Chrome (must be logged in). Navigate each site's search
  in the controlled tab, read JDs, score. Route = **SEND-LINK** for strong matches (apply flows are bespoke /
  founder-message forms; don't auto-apply). Tag `wellfound`/`instahyre`/`cutshort`. If a site shows a
  login/onboarding wall or block, skip it that cycle (don't create accounts or log in). Rotate ~1 startup
  source per cycle so cycles stay fast — don't scan all of them every time.

For each result:
- Dedupe: skip if URL/company+role already in `tracker.csv` or `list-pending`.
- Skip if company in `match.excludeCompanies`.
- Skip if the job's type is in `match.excludeJobTypes` (Contract / Part-time / Internship / Temporary / Freelance / AI-trainer gigs) — for permanent full-time only.
- **Read the ACTUAL JD**, not just the card title. Apply `excludePatterns` + `maxYearsExperienceRequired`.
- Score 0–100 vs `PROFILE.md`. Note posting age + applicant count. Record the source tag + apply-type.
- Stable id = lowercase `company-role` slug.

## 3. Act (sorted freshest / fewest-applicants first)
Route each scored role by **score** AND **source/apply-type**:

**A) Strong (score ≥ autoApplyThreshold):**
- **LinkedIn Easy Apply** → AUTO-APPLY (submit), up to `maxAppliesPerCycle`, under dailyAutoApplyCap.
  Log with " [auto] score=N", then `send "✅ Applied: <Role> @ <Company> (score N, ~Xth applicant)"`.
  Wait random `minSecondsBetweenApplies`..`maxSecondsBetweenApplies` between applies.
- **Everything else** (linkedinExternal / naukri / indeed — can't safely auto-apply) → **SEND-LINK**:
  `send "📩 Apply from your phone (strong match, score N): <Role> @ <Company> [<source>]\n<link>\nWhy: <1-line>"`.
  Log: `.\scripts\job-tracker.ps1 add -Company .. -Role .. -Location .. -Link .. -Source "<source>" -Status "Lead" -Notes "link-sent score=N <source>"`.
  Do NOT auto-apply these.

**B) Borderline (approvalThreshold ≤ score < autoApplyThreshold):** Telegram `ask` with Approve/Reject
(regardless of source). On approval next cycle: if Easy Apply → auto-apply; else → send-link.

**C) Discard (< approvalThreshold).**

Cap the number of send-link messages per cycle to ~5 so you don't flood the user.

**Cold-email drafts:** if a scanned listing/JD exposes a VERIFIED recruiter/HR/founder email (e.g. "apply to
x@company.com" in the JD), create a personalized Gmail DRAFT to it using the template in `cold-email.md`
(lead with concrete impact wins + your GitHub), log it in `cold-email.md` Queue, and mention it in the
report. Never email a GUESSED address. Keep to ~3–5 cold-email drafts/day total.

## 3b. Gmail replies
Search Gmail (read-only, last 24h) for application replies (companies in tracker.csv; subjects/bodies with
application/interview/shortlisted/candidature/assessment/"next steps"; exclude LinkedIn job-alert senders).
Dedupe via `seen-emails.json`. New reply → Telegram 1-line summary + bump tracker status.

## 4. Report
Telegram a 1-line summary ONLY if something happened: applied M (names) · asked K · replies R. Else stay silent.

## LinkedIn Easy Apply form rules (learned)
- Resume step: SELECT the stored resume named `applicationDefaults.linkedInResumeName`;
  LinkedIn's pre-selected file may be wrong; the upload tool can't push new files.
- Screening answers from `applicationDefaults`. Comp/notice fields are NUMERIC — plain numbers.
- Fill via element refs + `form_input`, NOT coordinates (modal scrolls; clicks misalign). Screenshot to verify.
- Years dropdowns: focus the select, type the digit (e.g. "1").
- Screening questions NOT in `applicationDefaults` → check `screening-qa.json` `answers[]` for a
  semantically-matching question (companies reword the same ones) and REUSE that answer. If still unknown,
  do NOT invent: append `{q, company, role, link}` to `screening-qa.json` `pending[]`, Telegram-ask
  `❓ <Company> asks: "<question>" — reply with the answer and I'll remember it`, and send-link that job
  (skip auto-submit) so the user can finish it manually. Never fabricate sensitive/factual answers.
- When the user replies to a pending screening question (handled in step 1 / poll): save `{q,a,added}` to
  `screening-qa.json` `answers[]`, remove it from `pending[]`, confirm, and reuse automatically next time.

## Hard safety rules
- Never enter passwords, create accounts, or enter payment info (skip those jobs).
- Never exceed dailyAutoApplyCap or maxAppliesPerCycle. Respect STOP + quiet hours every cycle.
- If a step needs a decision you can't make safely → Telegram it and skip; don't guess on consequential things.
- Answer all screening questions HONESTLY.
