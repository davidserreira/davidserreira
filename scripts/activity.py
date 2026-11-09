#!/usr/bin/env python3
"""Draws the "year ring" activity chart for the profile README.

Reads the contribution calendar of GH_LOGIN from the GitHub GraphQL API
(GITHUB_TOKEN) and writes activity-dark.svg and activity-light.svg to the
output directory. Standard library only.

    python3 scripts/activity.py [--out DIR] [--from-json FILE]

--from-json takes a file with {"days": [["YYYY-MM-DD", count], ...]} and is
only meant for previewing the chart locally.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import urllib.request

THEMES = {
    "dark": dict(text="#F0F4FA", sub="#8FA8D6", muted="#8B9BB4", line="#2E4570", faint="#243652", accent="#8FA8D6", land="#131F33"),
    "light": dict(text="#0F1B2D", sub="#2E4570", muted="#5B6B82", line="#B9C7E0", faint="#C9D4E8", accent="#2E4570", land="#F3F6FB"),
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def fetch(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-activity-chart"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if data.get("errors"):
        raise SystemExit(f"GitHub API error: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]


def summarise(days):
    counts = [c for _, c in days]
    best = max(range(len(days)), key=lambda i: counts[i])
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    return dict(
        total=sum(counts),
        active=sum(1 for c in counts if c),
        n=len(days),
        longest=longest,
        best_count=counts[best],
        best_date=dt.date.fromisoformat(days[best][0]),
    )


def render(days, t):
    s = summarise(days)
    W, H = 1000, 340
    cx, cy, r0, max_len = 838, 170, 98, 56
    n = len(days)
    gap = 12.0  # degrees left open between the oldest day and today
    peak = max(s["best_count"], 1)

    def angle(i):
        return math.radians(-90 + gap / 2 + i * (360 - gap) / max(n - 1, 1))

    def point(a, r):
        return cx + r * math.cos(a), cy + r * math.sin(a)

    ticks, labels = [], []
    last_label = -99
    for i, (date, c) in enumerate(days):
        a = angle(i)
        if c:
            ratio = math.sqrt(c) / math.sqrt(peak)
            x1, y1 = point(a, r0)
            x2, y2 = point(a, r0 + 4 + ratio * (max_len - 4))
            colour = t["text"] if c == peak else t["accent"]
            ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colour}" stroke-opacity="{0.5 + 0.5 * ratio:.2f}"/>')
        else:
            x, y = point(a, r0 + 1)
            ticks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.7" fill="{t["faint"]}"/>')
        d = dt.date.fromisoformat(date)
        if d.day == 1 and i - last_label > 20 and 8 < i < n - 8:
            x, y = point(a, r0 - 17)
            labels.append(f'<text x="{x:.1f}" y="{y + 3:.1f}" text-anchor="middle">{MONTHS[d.month - 1]}</text>')
            last_label = i

    tx, ty = point(angle(n - 1), r0 + 1)
    r_mid, band = r0 + max_len / 2, max_len + 16
    circ = 2 * math.pi * r_mid
    best = s["best_date"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
  <title>{s["total"]} contributions in the last 12 months. {s["active"]} active days, longest streak {s["longest"]} days, busiest day {s["best_count"]} contributions.</title>
  <defs>
    <mask id="sweep" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <circle cx="{cx}" cy="{cy}" r="{r_mid:.1f}" fill="none" stroke="#fff" stroke-width="{band}" stroke-dasharray="{circ:.1f}" transform="rotate(-90 {cx} {cy})">
        <animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="0" begin="0.3s" dur="2.6s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.45 0 0.2 1"/>
        <set attributeName="stroke-dashoffset" to="{circ:.1f}" begin="0s" end="0.3s"/>
      </circle>
    </mask>
  </defs>

  <text x="40" y="118" fill="{t["text"]}" font-size="64" font-weight="700" letter-spacing="-1.8">{s["total"]}</text>
  <text x="43" y="156" fill="{t["sub"]}" font-size="21" font-weight="500">contributions in the last 12 months</text>
  <line x1="43" y1="194" x2="560" y2="194" stroke="{t["line"]}" stroke-width="1.5"/>
  <g>
    <text x="43" y="240" fill="{t["muted"]}" font-size="12" font-weight="600" letter-spacing="2.2">ACTIVE DAYS</text>
    <text x="43" y="270" fill="{t["text"]}" font-size="24" font-weight="700">{s["active"]}</text>
    <text x="43" y="291" fill="{t["muted"]}" font-size="14">out of {s["n"]}</text>

    <text x="223" y="240" fill="{t["muted"]}" font-size="12" font-weight="600" letter-spacing="2.2">LONGEST STREAK</text>
    <text x="223" y="270" fill="{t["text"]}" font-size="24" font-weight="700">{s["longest"]}</text>
    <text x="223" y="291" fill="{t["muted"]}" font-size="14">days in a row</text>

    <text x="423" y="240" fill="{t["accent"]}" font-size="12" font-weight="600" letter-spacing="2.2">BUSIEST DAY</text>
    <text x="423" y="270" fill="{t["text"]}" font-size="24" font-weight="700">{s["best_count"]}</text>
    <text x="423" y="291" fill="{t["muted"]}" font-size="14">on {best.day} {MONTHS[best.month - 1].title()} {best.year}</text>
  </g>

  <circle cx="{cx}" cy="{cy}" r="{r0 - 4}" fill="none" stroke="{t["line"]}" stroke-width="1" opacity="0.6"/>
  <g mask="url(#sweep)">
    <g stroke-width="1.6" stroke-linecap="round">{"".join(ticks)}</g>
  </g>
  <g fill="{t["muted"]}" font-size="9.5" font-weight="600" letter-spacing="1.2">{"".join(labels)}</g>
  <text x="{cx}" y="{cy - 2}" text-anchor="middle" fill="{t["text"]}" font-size="15" font-weight="600">One year</text>
  <text x="{cx}" y="{cy + 17}" text-anchor="middle" fill="{t["muted"]}" font-size="12">one line per day</text>
  <circle cx="{tx:.1f}" cy="{ty:.1f}" r="3" fill="none" stroke="{t["accent"]}" stroke-width="1.2" opacity="0">
    <animate attributeName="r" values="3;11" begin="3s" dur="2.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0" begin="3s" dur="2.4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{tx:.1f}" cy="{ty:.1f}" r="3" fill="{t["text"]}"/>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    ap.add_argument("--from-json")
    args = ap.parse_args()
    if args.from_json:
        days = [tuple(d) for d in json.load(open(args.from_json))["days"]]
    else:
        token, login = os.environ.get("GITHUB_TOKEN"), os.environ.get("GH_LOGIN")
        if not token or not login:
            raise SystemExit("GITHUB_TOKEN and GH_LOGIN must be set")
        days = fetch(login, token)
    days = days[-366:]
    if len(days) < 300:
        raise SystemExit(f"Unexpected calendar length: {len(days)} days")
    os.makedirs(args.out, exist_ok=True)
    for name, theme in THEMES.items():
        with open(os.path.join(args.out, f"activity-{name}.svg"), "w", encoding="utf-8") as f:
            f.write(render(days, theme))
    print(f"Wrote activity charts for {len(days)} days to {args.out}/", file=sys.stderr)


if __name__ == "__main__":
    main()
