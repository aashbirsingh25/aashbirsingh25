import os
import sys

# Ensure scripts directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fetch_contributions import fetch_contributions

def render_svg(data):
    total_contribs = data.get("totalContributions", 0)
    current_streak = data.get("currentStreak", 0)
    longest_streak = data.get("longestStreak", 0)
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

    color_map = {
        "NONE": "#161b22",
        "FIRST_QUARTILE": "#0e4429",
        "SECOND_QUARTILE": "#006d32",
        "THIRD_QUARTILE": "#26a641",
        "FOURTH_QUARTILE": "#39d353"
    }

    for week_idx, week in enumerate(weeks):
        x = start_x + (week_idx * step)
        days = week.get("contributionDays", [])
        for day_idx, day in enumerate(days):
            y = start_y + (day_idx * step)
            color = day.get("color")
            if not color or color == "#ebedf0" or color == "#9be9a8":
                level = day.get("contributionLevel", "NONE")
                color = color_map.get(level, "#161b22")
            
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

def main():
    print("[render_heatmap_svg] Fetching contribution data...")
    data = fetch_contributions()
    svg_content = render_svg(data)
    
    # Path to target SVG output
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(root_dir, "contrib-heatmap.svg")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[render_heatmap_svg] Successfully updated {output_path}")

if __name__ == "__main__":
    main()
