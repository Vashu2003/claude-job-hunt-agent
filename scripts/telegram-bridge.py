#!/usr/bin/env python3
"""Telegram bridge for the autonomous job-hunt approval loop.

No external dependencies (uses only the Python standard library).

Commands:
  whoami
      Show chats that have messaged the bot, so you can find your chat_id.
  send "<text>"
      Send a plain notification (e.g. "auto-applied to X").
  ask --id ID --role R --company C --link L --score N [--why W] [--posted P]
      Send an approval request with Approve/Reject buttons; records it as pending.
  poll
      Fetch new Telegram updates, record button taps. Prints one "ID|decision" line
      per newly decided item (decision = approved | rejected).
  list-pending
      Print pending approval items as JSON.
  list-decided
      Print decided-but-not-yet-handled items as JSON.
  resolve --id ID [--status applied]
      Remove an item from the decided queue once the loop has acted on it.

Config: telegram-config.json next to this script -> {"bot_token": "...", "chat_id": "..."}
        (env vars TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID override the file.)
State:  telegram-state.json (auto-managed; tracks update offset + queues).
"""
import sys, os, json, argparse, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "telegram-config.json")
STATE = os.path.join(HERE, "telegram-state.json")
API = "https://api.telegram.org/bot{token}/{method}"


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def cfg():
    c = load_json(CONFIG, {})
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or c.get("bot_token")
    chat = os.environ.get("TELEGRAM_CHAT_ID") or c.get("chat_id")
    return token, chat


def api(method, params=None):
    token = cfg()[0]
    if not token:
        raise SystemExit("No bot token. Fill telegram-config.json (bot_token) first.")
    url = API.format(token=token, method=method)
    data = urllib.parse.urlencode(params or {}).encode()
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": e.read().decode()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def state():
    return load_json(STATE, {"offset": 0, "pending": {}, "decided": []})


def cmd_whoami(args):
    res = api("getUpdates", {"timeout": 0})
    chats = {}
    for u in res.get("result", []):
        msg = u.get("message") or u.get("edited_message") or {}
        ch = msg.get("chat")
        if ch:
            chats[ch["id"]] = ch.get("username") or ch.get("first_name") or ""
    if not chats:
        print("No messages yet. In Telegram, send any message to your bot, then re-run whoami.")
        return
    for cid, name in chats.items():
        print(f"chat_id: {cid}  ({name})")


def cmd_send(args):
    _, chat = cfg()
    res = api("sendMessage", {"chat_id": chat, "text": args.text, "parse_mode": "HTML"})
    print("sent" if res.get("ok") else res)


def cmd_ask(args):
    _, chat = cfg()
    st = state()
    text = (f"\U0001F914 <b>Approve application?</b>\n\n"
            f"<b>{args.role}</b> @ <b>{args.company}</b>\n"
            f"Score: {args.score}/100\n"
            + (f"Posted: {args.posted}\n" if args.posted else "")
            + (f"\n{args.why}\n" if args.why else "")
            + (f"\n{args.link}" if args.link else ""))
    kb = {"inline_keyboard": [[
        {"text": "✅ Approve", "callback_data": f"approve:{args.id}"},
        {"text": "❌ Reject", "callback_data": f"reject:{args.id}"},
    ]]}
    res = api("sendMessage", {"chat_id": chat, "text": text, "parse_mode": "HTML",
                              "reply_markup": json.dumps(kb)})
    if res.get("ok"):
        st["pending"][args.id] = {
            "id": args.id, "role": args.role, "company": args.company,
            "link": args.link, "score": args.score, "why": args.why,
            "posted": args.posted, "message_id": res.get("result", {}).get("message_id"),
        }
        save_json(STATE, st)
        print("asked")
    else:
        print(res)


def cmd_poll(args):
    _, chat = cfg()
    st = state()
    res = api("getUpdates", {"offset": st["offset"], "timeout": 0})
    decisions = []
    for u in res.get("result", []):
        st["offset"] = max(st["offset"], u["update_id"] + 1)
        # Capture any free-text message the user sends into the inbox (read via the 'inbox' command).
        m = u.get("message")
        if m and m.get("text"):
            st.setdefault("inbox", []).append({
                "text": m["text"],
                "from": (m.get("from") or {}).get("first_name", ""),
                "date": m.get("date"),
            })
        cq = u.get("callback_query")
        if not cq or ":" not in cq.get("data", ""):
            continue
        action, jid = cq["data"].split(":", 1)
        decision = "approved" if action == "approve" else "rejected"
        item = st["pending"].pop(jid, None)
        if item is None:
            # Already decided (duplicate tap) or unknown id — acknowledge and skip to dedupe.
            api("answerCallbackQuery", {"callback_query_id": cq["id"], "text": "Already recorded."})
            continue
        item["decision"] = decision
        st["decided"].append(item)
        decisions.append((jid, decision))
        api("answerCallbackQuery", {"callback_query_id": cq["id"], "text": f"Marked {decision}."})
        msg = cq.get("message", {})
        if msg.get("message_id"):
            mark = "✅ APPROVED" if decision == "approved" else "❌ REJECTED"
            api("editMessageText", {"chat_id": chat, "message_id": msg["message_id"],
                                    "text": msg.get("text", "") + f"\n\n<b>{mark}</b>",
                                    "parse_mode": "HTML"})
    save_json(STATE, st)
    for jid, d in decisions:
        print(f"{jid}|{d}")


def cmd_inbox(args):
    """Print free-text messages the user sent the bot since last read, then clear them
    (run `poll` first to fetch new updates from Telegram). Use --keep to not clear."""
    st = state()
    msgs = st.get("inbox", [])
    print(json.dumps(msgs, indent=2))
    if msgs and not args.keep:
        st["inbox"] = []
        save_json(STATE, st)


def cmd_list_pending(args):
    print(json.dumps(list(state()["pending"].values()), indent=2))


def cmd_list_decided(args):
    print(json.dumps(state()["decided"], indent=2))


def cmd_resolve(args):
    st = state()
    st["decided"] = [d for d in st["decided"] if d.get("id") != args.id]
    save_json(STATE, st)
    print(f"resolved {args.id} ({args.status})")


def main():
    p = argparse.ArgumentParser(description="Telegram bridge for job-hunt approvals")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    s = sub.add_parser("send"); s.add_argument("text")
    a = sub.add_parser("ask")
    for n in ["id", "role", "company", "link", "score"]:
        a.add_argument("--" + n, required=True)
    a.add_argument("--why", default=""); a.add_argument("--posted", default="")
    sub.add_parser("poll")
    ib = sub.add_parser("inbox"); ib.add_argument("--keep", action="store_true")
    sub.add_parser("list-pending")
    sub.add_parser("list-decided")
    r = sub.add_parser("resolve"); r.add_argument("--id", required=True); r.add_argument("--status", default="applied")
    args = p.parse_args()
    {
        "whoami": cmd_whoami, "send": cmd_send, "ask": cmd_ask, "poll": cmd_poll,
        "inbox": cmd_inbox,
        "list-pending": cmd_list_pending, "list-decided": cmd_list_decided, "resolve": cmd_resolve,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
