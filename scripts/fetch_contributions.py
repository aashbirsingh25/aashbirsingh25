import os
import json
import requests
from datetime import datetime, timedelta

GRAPHQL_QUERY = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            color
            contributionLevel
          }
        }
      }
    }
  }
}
"""

def compute_streaks(all_days):
    """
    Computes longest streak and current streak from a chronological list of contribution days.
    Each item in all_days is a dict with 'date' and 'contributionCount'.
    """
    if not all_days:
        return 0, 0

    # Sort days by date
    sorted_days = sorted(all_days, key=lambda d: d['date'])
    
    longest_streak = 0
    temp_streak = 0

    for day in sorted_days:
        if day['contributionCount'] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Current streak calculation: count backwards from latest day
    current_streak = 0
    idx = len(sorted_days) - 1
    
    # If today has 0 contributions, check yesterday
    if sorted_days and sorted_days[idx]['contributionCount'] == 0:
        idx -= 1

    while idx >= 0 and sorted_days[idx]['contributionCount'] > 0:
        current_streak += 1
        idx -= 1

    return current_streak, longest_streak

def generate_fallback_data(username="aashbirsingh25"):
    """
    Generates fallback contribution data if GitHub API token is unavailable or request fails.
    """
    import random
    today = datetime.now()
    # Find start date (approx 52 weeks ago, aligned to Sunday)
    start_date = today - timedelta(days=364)
    while start_date.weekday() != 6:  # 6 is Sunday in Python datetime (Monday=0 ... Sunday=6)
        start_date -= timedelta(days=1)

    weeks = []
    current_date = start_date
    total_contribs = 0
    all_days = []

    # Map levels to GitHub standard colors
    color_map = {
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353"
    }

    # Seed random for repeatable data if needed
    random.seed(42)

    for w in range(53):
        week_days = []
        for d in range(7):
            if current_date > today:
                break
            
            # Generate realistic activity pattern
            is_weekend = d in (0, 6)
            prob = 0.3 if is_weekend else 0.75
            
            if random.random() < prob:
                count = random.choice([1, 2, 3, 4, 5, 8, 12])
            else:
                count = 0

            total_contribs += count
            
            if count == 0:
                level = 0
            elif count <= 3:
                level = 1
            elif count <= 6:
                level = 2
            elif count <= 9:
                level = 3
            else:
                level = 4

            day_obj = {
                "date": current_date.strftime("%Y-%m-%d"),
                "contributionCount": count,
                "color": color_map[level],
                "contributionLevel": ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"][level]
            }
            week_days.append(day_obj)
            all_days.append(day_obj)
            current_date += timedelta(days=1)
            
        if week_days:
            weeks.append({"contributionDays": week_days})

    current_streak, longest_streak = compute_streaks(all_days)

    return {
        "username": username,
        "totalContributions": total_contribs,
        "currentStreak": current_streak,
        "longestStreak": longest_streak,
        "weeks": weeks
    }

def fetch_contributions(username="aashbirsingh25", token=None):
    token = token or os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print("[fetch_contributions] No GH_PAT or GITHUB_TOKEN provided. Using fallback generator / existing data.")
        return generate_fallback_data(username)

    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": "GitHub-Profile-Art-Fetcher"
    }

    url = "https://api.github.com/graphql"

    try:
        res = requests.post(url, json={"query": GRAPHQL_QUERY, "variables": {"username": username}}, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if "errors" in data:
                print(f"[fetch_contributions] GraphQL errors: {data['errors']}")
                return generate_fallback_data(username)
            
            calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            total_contribs = calendar["totalContributions"]
            weeks = calendar["weeks"]

            all_days = []
            for w in weeks:
                for d in w["contributionDays"]:
                    all_days.append(d)

            current_streak, longest_streak = compute_streaks(all_days)

            return {
                "username": username,
                "totalContributions": total_contribs,
                "currentStreak": current_streak,
                "longestStreak": longest_streak,
                "weeks": weeks
            }
        else:
            print(f"[fetch_contributions] API returned status code {res.status_code}: {res.text}")
            return generate_fallback_data(username)

    except Exception as e:
        print(f"[fetch_contributions] Exception occurred while fetching: {e}")
        return generate_fallback_data(username)

if __name__ == "__main__":
    data = fetch_contributions()
    print(f"Fetched contribution data for {data['username']}: {data['totalContributions']} total contributions, current streak: {data['currentStreak']}d, longest streak: {data['longestStreak']}d")
