#!/usr/bin/env python3
"""Draws the static artwork of the profile README into assets/.

Hero (name, the two degrees and the Faro to Braga line on a map of Portugal)
and the project cards, each in a dark and a light variant. Standard library
only. Run it after changing the text, the colours or the list of cards:

    python3 scripts/build_assets.py

The activity ring is drawn separately by scripts/activity.py.
"""
import base64, math, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

THEMES = {
    "dark":  dict(text="#F0F4FA", sub="#8FA8D6", muted="#8B9BB4", line="#2E4570", faint="#1E2D45", accent="#8FA8D6", land="#131F33", live="#7CCB9A"),
    "light": dict(text="#0F1B2D", sub="#2E4570", muted="#5B6B82", line="#B9C7E0", faint="#DCE4F2", accent="#2E4570", land="#F3F6FB", live="#2E9E62"),
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# ---------- Portugal outline (lon, lat), simplified ----------
BORDER = [(-8.87,41.87),(-8.75,41.97),(-8.52,42.08),(-8.20,42.15),(-8.08,42.02),(-8.22,41.91),(-7.90,41.85),(-7.70,41.90),
(-7.45,41.82),(-7.18,41.88),(-6.98,41.95),(-6.60,41.94),(-6.52,41.87),(-6.55,41.68),(-6.19,41.57),(-6.32,41.40),(-6.48,41.27),
(-6.65,41.24),(-6.80,41.04),(-6.93,41.03),(-6.80,40.85),(-6.82,40.60),(-6.79,40.36),(-6.86,40.27),(-7.01,40.19),(-6.90,40.02),
(-6.87,39.87),(-7.02,39.67),(-7.53,39.66),(-7.30,39.47),(-7.14,39.17),(-6.96,39.03),(-7.03,38.88),(-7.26,38.72),(-7.32,38.45),
(-7.10,38.19),(-6.93,38.21),(-7.00,38.02),(-7.25,37.98),(-7.51,37.55),(-7.41,37.18),(-7.89,36.97),(-8.20,37.08),(-8.67,37.09),
(-8.95,36.99),(-9.00,37.03),(-8.86,37.30),(-8.79,37.72),(-8.88,37.95),(-8.80,38.20),(-8.77,38.42),(-8.92,38.49),(-9.22,38.41),
(-9.18,38.66),(-9.48,38.70),(-9.50,38.79),(-9.42,38.97),(-9.33,39.20),(-9.41,39.37),(-9.07,39.60),(-8.90,40.05),(-8.87,40.18),
(-8.75,40.64),(-8.66,40.95),(-8.68,41.15),(-8.78,41.42),(-8.84,41.69)]
ROUTE = [(-7.93,37.02),(-8.25,37.20),(-8.50,37.75),(-8.60,38.20),(-8.91,38.63),(-9.10,38.77),(-8.72,39.22),(-8.47,39.46),
(-8.63,39.91),(-8.43,40.21),(-8.64,40.64),(-8.60,41.15),(-8.42,41.55)]
STOPS = [(-9.10,38.77),(-8.43,40.21),(-8.60,41.15)]  # Lisboa, Coimbra, Porto (unlabelled ticks)

def proj(scale, ox, oy):
    k = math.cos(math.radians(39.6))
    return lambda p: (ox + (p[0] + 9.55) * k * scale, oy + (42.2 - p[1]) * scale)

def smooth(pts):
    """Catmull-Rom to cubic bezier path."""
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C {c1[0]:.1f} {c1[1]:.1f}, {c2[0]:.1f} {c2[1]:.1f}, {p2[0]:.1f} {p2[1]:.1f}"
    return d

def hero(t):
    W, H = 1000, 440
    P = proj(70, 742, 28)
    land = " ".join(f"{x:.1f},{y:.1f}" for x, y in map(P, BORDER))
    rpts = list(map(P, ROUTE)); route = smooth(rpts)
    faro, braga = rpts[0], rpts[-1]
    ticks = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{t["land"]}" stroke="{t["line"]}" stroke-width="1.4"/>' for x, y in map(P, STOPS))
    L = 2000
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
  <title>David Serreira: MSc student in Informatics Engineering. From Faro (BSc, University of Algarve) to Braga (MSc, University of Minho).</title>
  <!-- left: identity -->
  <g>
    <text x="40" y="150" fill="{t["text"]}" font-size="64" font-weight="700" letter-spacing="-1.8">David Serreira
      <animate attributeName="opacity" from="0" to="1" dur="0.9s" fill="freeze"/>
    </text>
    <text x="43" y="190" fill="{t["sub"]}" font-size="21" font-weight="500">MSc Student · Informatics Engineering
      <animate attributeName="opacity" values="0;0;1" keyTimes="0;0.4;1" dur="1.4s" fill="freeze"/>
    </text>
    <line x1="43" y1="228" x2="43" y2="228" stroke="{t["line"]}" stroke-width="1.5">
      <animate attributeName="x2" from="43" to="560" begin="0.6s" dur="1.4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>
    </line>
    <!-- two stops -->
    <g font-size="15">
      <text x="43" y="276" fill="{t["muted"]}" font-size="12" font-weight="600" letter-spacing="2.2">2022 – 2025 · FARO</text>
      <text x="43" y="300" fill="{t["text"]}" font-weight="600">BSc in Informatics Engineering</text>
      <text x="43" y="321" fill="{t["muted"]}">University of Algarve</text>

      <text x="323" y="276" fill="{t["accent"]}" font-size="12" font-weight="600" letter-spacing="2.2">2026 – 2028 · BRAGA</text>
      <text x="323" y="300" fill="{t["text"]}" font-weight="600">MSc in Informatics Engineering</text>
      <text x="323" y="321" fill="{t["muted"]}">University of Minho</text>
      <animate attributeName="opacity" values="0;0;1" keyTimes="0;0.6;1" dur="2s" fill="freeze"/>
    </g>
  </g>

  <!-- right: map with the line south to north -->
  <polygon points="{land}" fill="{t["land"]}" stroke="{t["line"]}" stroke-width="1.5" stroke-linejoin="round"/>
  <path id="route" d="{route}" fill="none" stroke="{t["accent"]}" stroke-width="2.6" stroke-linecap="round" stroke-dasharray="{L}" stroke-dashoffset="{L}" pathLength="{L}">
    <animate attributeName="stroke-dashoffset" from="{L}" to="0" begin="0.8s" dur="3.2s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.45 0 0.2 1"/>
  </path>
  <g opacity="0">{ticks}
    <animate attributeName="opacity" from="0" to="1" begin="3.2s" dur="0.6s" fill="freeze"/>
  </g>
  <!-- train: travels the line, repeating -->
  <circle r="4.5" fill="{t["text"]}" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.92;1" begin="4.4s" dur="6s" repeatCount="indefinite"/>
    <animateMotion begin="4.4s" dur="6s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines="0.45 0 0.3 1"><mpath xlink:href="#route"/></animateMotion>
  </circle>
  <!-- Faro -->
  <circle cx="{faro[0]:.1f}" cy="{faro[1]:.1f}" r="5.5" fill="{t["land"]}" stroke="{t["muted"]}" stroke-width="2.2"/>
  <text x="{faro[0]+16:.1f}" y="{faro[1]+22:.1f}" fill="{t["muted"]}" font-size="12" font-weight="600" letter-spacing="2.2">FARO</text>
  <!-- Braga -->
  <circle cx="{braga[0]:.1f}" cy="{braga[1]:.1f}" r="6" fill="none" stroke="{t["accent"]}" stroke-width="1.5" opacity="0">
    <animate attributeName="r" values="6;18" begin="4s" dur="2.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0" begin="4s" dur="2.4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{braga[0]:.1f}" cy="{braga[1]:.1f}" r="5.5" fill="{t["accent"]}" stroke="{t["land"]}" stroke-width="2"/>
  <text x="{braga[0]+18:.1f}" y="{braga[1]+4:.1f}" fill="{t["accent"]}" font-size="12" font-weight="600" letter-spacing="2.2">BRAGA</text>
</svg>
'''

# One entry per card in "Selected work". Add a project here, run the script and
# reference assets/<slug>-dark.svg and assets/<slug>-light.svg from the README.
#   status: "live" (green pulse), "progress" (accent pulse) or "private" (no dot)
#   link:   True draws the arrow; use it when the README wraps the card in a link
#   shot:   optional screenshot in assets/, shown on the right of the card
CARDS = [
    dict(slug="vetstock", label="TEAM PROJECT", status="live", title="VetStock",
         text="Purchasing and stock management for a veterinary clinic.",
         tags=["React", "TypeScript", "Node.js", "PostgreSQL", "Prisma", "Docker"], link=True),
    dict(slug="picturas", label="MSC · TEAM PROJECT", status="progress", title="PictuRAS",
         text="Image and video editor with AI tools, built as microservices.",
         tags=["TypeScript", "Python", "RabbitMQ", "Docker"], link=True),
    dict(slug="casacota", label="PERSONAL PROJECT", status="live", title="Casa Cota",
         text="Shared-house chores: calendar, stats and a roulette.",
         tags=["React", "TypeScript", "Express", "SQLite"], link=True, shot="casacota-shot.jpg"),
    dict(slug="faroliga", label="PERSONAL PROJECT", status="live", title="Faro Liga",
         text="Points league that turns a store team's sales into a weekly podium.",
         tags=["React", "TypeScript", "Express", "Tailwind"], link=False),
    dict(slug="marcaqui", label="CLIENT WORK", status="private", title="Marcaqui",
         text="Online booking for a barbershop: schedule, clients and reminders.",
         tags=["React", "TypeScript", "PHP", "SQL"], link=False),
    dict(slug="sdvm", label="MSC · TEAM PROJECT", status="private", title="SDVM Parser",
         text="Parser and AST for the SDVM language, with grammar extensions.",
         tags=["Python", "Parsing", "Testing"], link=False),
]
STATUS = {"live": "LIVE", "progress": "IN PROGRESS", "private": "PRIVATE"}


def card(t, c):
    W, H = 600, 210
    x, tags = 34, ""
    for s in c["tags"]:
        w = 9 + len(s) * 7.1 + 9
        tags += f'<rect x="{x:.0f}" y="150" width="{w:.0f}" height="24" rx="12" fill="none" stroke="{t["line"]}" stroke-width="1.2"/><text x="{x+w/2:.1f}" y="166.5" text-anchor="middle" fill="{t["sub"]}" font-size="12">{s}</text>'
        x += w + 7
    status_x, dot = W - 34, ""
    if c["status"] != "private":
        colour = t["live"] if c["status"] == "live" else t["accent"]
        dot = f'<circle cx="{W-38}" cy="46" r="4" fill="{colour}"><animate attributeName="opacity" values="1;0.35;1" dur="2s" repeatCount="indefinite"/></circle>'
        status_x = W - 50
    arrow = f'<text x="{W-34}" y="92" text-anchor="end" fill="{t["accent"]}" font-size="20">↗</text>' if c["link"] else ""
    shot = ""
    if c.get("shot"):
        # the status moves left and the arrow goes away to make room for the picture
        data = base64.b64encode(open(os.path.join(OUT, c["shot"]), "rb").read()).decode()
        sw, sh, sx, sy = 146, 178, W - 146 - 16, 16
        shot = (f'<clipPath id="shot"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10"/></clipPath>'
                f'<image href="data:image/jpeg;base64,{data}" x="{sx}" y="{sy}" width="{sw}" height="{sh}" preserveAspectRatio="xMidYMin slice" clip-path="url(#shot)"/>'
                f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="none" stroke="{t["line"]}" stroke-width="1.2"/>')
        arrow = ""
        dot = dot.replace(f'cx="{W-38}"', f'cx="{sx-20}"')
        status_x = sx - 32
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
  <title>{c["title"]}: {c["text"]}</title>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{t["land"]}" stroke="{t["line"]}" stroke-width="1.5"/>
  <text x="34" y="50" fill="{t["muted"]}" font-size="11.5" font-weight="600" letter-spacing="2.4">{c["label"]}</text>
  {dot}
  <text x="{status_x}" y="50" text-anchor="end" fill="{t["muted"]}" font-size="11.5" font-weight="600" letter-spacing="2.4">{STATUS[c["status"]]}</text>
  <text x="34" y="92" fill="{t["text"]}" font-size="30" font-weight="700" letter-spacing="-0.6">{c["title"]}</text>
  <text x="34" y="122" fill="{t["muted"]}" font-size="14.5">{c["text"]}</text>
  {tags}
  {arrow}
  {shot}
</svg>
"""


for name, t in THEMES.items():
    with open(f"{OUT}/hero-{name}.svg", "w", encoding="utf-8") as f:
        f.write(hero(t))
    for c in CARDS:
        with open(f"{OUT}/{c['slug']}-{name}.svg", "w", encoding="utf-8") as f:
            f.write(card(t, c))
print("Wrote", ", ".join(sorted(os.listdir(OUT))))
