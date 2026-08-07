import json
import os
import sys

# Ensure scripts directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_contributions import derive_stats, fetch_days


def get_color(count):
    if count == 0:
        return "#161b22"
    elif count <= 3:
        return "#0e4429"
    elif count <= 6:
        return "#006d32"
    elif count <= 9:
        return "#26a641"
    else:
        return "#39d353"


def render_svg(data):
    stats = data.get("stats", {})
    total_contribs = stats.get("total", data.get("totalContributions", 0))
    current_streak = stats.get("current_streak", data.get("currentStreak", 0))
    longest_streak = stats.get("longest_streak", data.get("longestStreak", 0))

    days_list = data.get("days", [])
    if days_list:
        # Group flat days into weeks (7 days per column)
        weeks = [days_list[i : i + 7] for i in range(0, len(days_list), 7)]
    else:
        weeks = data.get("weeks", [])

    svg_header = """<svg width="860" height="200" viewBox="0 0 860 200" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, SFMono-Regular, 'JetBrains Mono', Consolas, Menlo, monospace">
  <defs>
    <style>
      .bg { fill: #0a0e14; }
      .chrome { fill: #11161f; }
      .title { fill: #565b66; font-size: 12px; letter-spacing: 0.5px; }
      .lbl { fill: #565b66; font-size: 11px; }
    </style>
  </defs>
  <rect class="bg" width="860" height="200" rx="10"/>
  <rect class="chrome" width="860" height="34" rx="10"/>
  <rect class="chrome" x="0" y="20" width="860" height="14"/>
  <circle cx="22" cy="17" r="5" fill="#f26d78"/>
  <circle cx="40" cy="17" r="5" fill="#ffb454"/>
  <circle cx="58" cy="17" r="5" fill="#7fd962"/>
  <text x="430" y="22" class="title" text-anchor="middle">./contributions.sh --last-year</text>

  <g>
"""

    cells_svg = []
    start_x = 30
    start_y = 54
    cell_size = 11
    step = 14
    delay = 0.1

    for week_idx, week in enumerate(weeks):
        x = start_x + (week_idx * step)
        if isinstance(week, dict):
            day_items = week.get("contributionDays", [])
        else:
            day_items = week

        for day_idx, day in enumerate(day_items):
            y = start_y + (day_idx * step)
            if "color" in day:
                color = day["color"]
            else:
                count = day.get("count", day.get("contributionCount", 0))
                color = get_color(count)

            anim = f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.25s" fill="freeze"/>'
            rect = f'<rect class="cell" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{color}">{anim}</rect>'
            cells_svg.append(rect)
            delay += 0.006

    svg_body = "".join(cells_svg)

    svg_footer = f"""
  </g>

  <text x="30" y="182" class="lbl">Less</text>
  <rect x="62" y="172" width="11" height="11" rx="2.5" fill="#161b22"/>
  <rect x="76" y="172" width="11" height="11" rx="2.5" fill="#0e4429"/>
  <rect x="90" y="172" width="11" height="11" rx="2.5" fill="#006d32"/>
  <rect x="104" y="172" width="11" height="11" rx="2.5" fill="#26a641"/>
  <rect x="118" y="172" width="11" height="11" rx="2.5" fill="#39d353"/>
  <text x="134" y="182" class="lbl">More</text>
  <text x="820" y="182" class="lbl" text-anchor="end">{total_contribs} contributions in the last year · current streak {current_streak}d · longest {longest_streak}d</text>
</svg>
"""

    return svg_header + svg_body + svg_footer


def load_data():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(root_dir, "data", "contributions.json")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    days = fetch_days()
    return {
        "days": days,
        "stats": derive_stats(days),
    }


def main():
    print("[render_heatmap_svg] Fetching contribution data...")
    data = load_data()
    svg_content = render_svg(data)

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(root_dir, "contrib-heatmap.svg")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[render_heatmap_svg] Successfully updated {output_path}")


if __name__ == "__main__":
    main()
