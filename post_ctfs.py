import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

CTFTIME_API = "https://ctftime.org/api/v1/events/"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1462493741364543498/RbspM_RHJHKU2qQsNOYzcaXjuyxjLZQ4VICUeOv3nNHcDlT0evOCFM8YT1yXCLLWaLPA"

STATE_FILE = Path("posted_ids.json")

if not STATE_FILE.exists():
    STATE_FILE.write_text("[]")

posted_ids = set(json.loads(STATE_FILE.read_text()))

now = int(time.time())
future = int((datetime.utcnow() + timedelta(days=30)).timestamp())

params = {
    "limit": 20,
    "start": now,
    "finish": future,
}

events = requests.get(CTFTIME_API, params=params, timeout=15).json()
new_ids = set()

for e in events:
    eid = e["id"]
    if eid in posted_ids:
        continue

    if e["onsite"]:
        continue

    title = e["title"]
    start = e["start"]
    end = e["finish"]
    url = e["url"]
    format_ = e["format"]

    body = (
        f"**Format:** {format_}\n"
        f"**Start:** {start}\n"
        f"**End:** {end}\n"
        f"**CTFtime:** {url}\n\n"
        "🕒 **Availability**\n"
        "Comment below:\n"
        "- ✅ In\n"
        "- ❌ Out\n"
        "- 🤔 Maybe (add notes)"
    )

    payload = {"thread_name": title, "content": body}

    r = requests.post(DISCORD_WEBHOOK, json=payload, timeout=15)
    if r.status_code in (200, 204):
        new_ids.add(eid)

if new_ids:
    posted_ids |= new_ids
    STATE_FILE.write_text(json.dumps(sorted(posted_ids), indent=2))
