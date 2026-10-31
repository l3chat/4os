#!/usr/bin/env python3
"""Render the repository event log without network access."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

REPOSITORY = Path(__file__).resolve().parents[2]


def products():
    data = json.loads((REPOSITORY / "history/events.json").read_text(encoding="utf-8"))
    if data["schema_version"] != 1:
        raise ValueError("Unsupported history schema")
    seen = set()
    events = data["events"]
    previous = None
    for event in events:
        if event["id"] in seen:
            raise ValueError("Duplicate history event")
        seen.add(event["id"])
        when = datetime.fromisoformat(event["occurred_at"])
        if when.tzinfo is None or (previous and when < previous):
            raise ValueError("Events must be chronological and timezone aware")
        previous = when
        if event.get("commit") and not re.fullmatch(r"[0-9a-f]{40}", event["commit"]):
            raise ValueError("Invalid history commit")
        if event["kind"] not in {"infrastructure", "research", "presentation", "fix", "documentation"}:
            raise ValueError("Invalid event kind")
    lines = ["# История событий 4os", "", "Время указано по Europe/Berlin. Источник — `history/events.json`; история репозитория Git сохраняет точный состав каждого изменения.", ""]
    for event in reversed(events):
        when = datetime.fromisoformat(event["occurred_at"]).astimezone(ZoneInfo("Europe/Berlin"))
        lines += [f"## {when.strftime('%d.%m.%Y %H:%M')} — {event['title']}", "", event["description"], ""]
        if event.get("commit"):
            lines += [f"[Коммит {event['commit'][:7]}](https://github.com/l3chat/4os/commit/{event['commit']})", ""]
    text = "\n".join(lines).rstrip() + "\n"
    front = "---\nlayout: default\ntitle: История проекта\nlang: ru\n---\n\n"
    return {REPOSITORY / "CHANGELOG.md": text, REPOSITORY / "literary-competitions/docs/history.md": front + text}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, content in products().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise SystemExit("Run scripts/render_history.py to refresh event history")
        else:
            path.write_text(content, encoding="utf-8")
    print("Event history validated; generated history " + ("is current." if args.check else "updated."))


if __name__ == "__main__":
    main()
