"""Builds assets/languages.svg (a donut chart of your most used languages)
from the public repositories of GH_USER. Runs inside GitHub Actions, so the
chart is hosted in your own repo and never depends on a third-party server."""
import json, math, os, urllib.request

USER = os.environ.get("GH_USER", "Pawani2000")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
COLORS = ["#a78bfa", "#22d3ee", "#f472b6", "#60a5fa", "#34d399", "#9ca3af"]
FONT = "'Segoe UI','Helvetica Neue',Arial,sans-serif"


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "lang-chart"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    totals, page = {}, 1
    while True:
        repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}")
        if not repos:
            break
        for repo in repos:
            if repo.get("fork"):
                continue
            for lang, n in api(repo["languages_url"]).items():
                totals[lang] = totals.get(lang, 0) + n
        page += 1
    return totals


def render(totals):
    items = sorted(totals.items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in items) or 1
    top = items[:5]
    other = sum(v for _, v in items[5:])
    if other:
        top.append(("Others", other))
    r, c = 62, 2 * math.pi * 62
    arcs, legend, offset = "", "", 0.0
    for i, (name, v) in enumerate(top):
        pct = v / total * 100
        length = c * v / total
        col = COLORS[i % len(COLORS)]
        arcs += (f'<circle cx="110" cy="125" r="{r}" fill="none" stroke="{col}" stroke-width="26" '
                 f'stroke-dasharray="{max(length - 2, 0.1):.2f} {c:.2f}" stroke-dashoffset="{-offset:.2f}" '
                 f'transform="rotate(-90 110 125)"/>')
        y = 70 + i * 30
        legend += (f'<circle cx="236" cy="{y - 5}" r="6" fill="{col}"/>'
                   f'<text x="252" y="{y}" fill="#e5e7eb" font-size="16">{name}</text>'
                   f'<text x="400" y="{y}" fill="#c4b5fd" font-size="16" text-anchor="end">{pct:.1f}%</text>')
        offset += length
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 250" font-family="{FONT}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0c2e"/><stop offset="1" stop-color="#1b1056"/></linearGradient></defs>
<rect x="1" y="1" width="418" height="248" rx="18" fill="url(#bg)" stroke="#4c3b9a"/>
<circle cx="110" cy="125" r="{r}" fill="none" stroke="#1e1b4b" stroke-width="26"/>
{arcs}
<text x="110" y="131" text-anchor="middle" fill="#fff" font-size="15" font-weight="700">Languages</text>
{legend}
</svg>'''


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    with open("assets/languages.svg", "w", encoding="utf-8") as f:
        f.write(render(collect()))
    print("assets/languages.svg updated")
