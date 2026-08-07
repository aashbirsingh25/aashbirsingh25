"""
Fetch a GitHub user's public contribution calendar.

GitHub serves this as plain HTML at /users/<username>/contributions -
the same fragment the profile page itself renders. No auth, no token,
no GraphQL API needed.
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "aashbirsingh25")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join("data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.select("td.ContributionCalendar-day") or soup.select("[data-date]")
    for cell in cells:
        date = cell.get("data-date")
        count = cell.get("data-count") or cell.get("data-level")
        if date is None:
            continue
        try:
            count = int(count) if count is not None else 0
        except ValueError:
            count = 0
        days.append({"date": date, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})

    longest = current = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
    }


def main():
    try:
        days = fetch_days()
    except Exception as exc:
        print(f"fetch failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not days:
        print("no contribution cells parsed — GitHub markup may have changed", file=sys.stderr)
        sys.exit(1)

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": derive_stats(days),
    }

    os.makedirs("data", exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"wrote {len(days)} days to {OUT_PATH}")


if __name__ == "__main__":
    main()
