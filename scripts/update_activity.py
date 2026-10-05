"""Refresh the profile's public metadata card, using only the Python stdlib."""
import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

USERNAME = "qalmurzayeev"
ROOT = Path(__file__).resolve().parents[1]


def api(endpoint):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "qalmurzayeev-profile"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/{endpoint}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def main():
    user = api(f"users/{USERNAME}")
    repos = []
    page = 1
    while True:
        batch = api(f"users/{USERNAME}/repos?per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    original = [r for r in repos if not r["fork"]]
    languages = Counter(r["language"] for r in original if r["language"])
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="252" viewBox="0 0 960 252">',
           '<style>text{font-family:Segoe UI,Arial,sans-serif}.mono{font-family:Consolas,Courier New,monospace}</style>',
           '<rect x="1" y="1" width="958" height="250" rx="14" fill="#07121e" stroke="#173c58"/>',
           '<text x="28" y="31" class="mono" font-size="12" letter-spacing="2" fill="#80a6c3">PUBLIC SIGNAL / GITHUB</text>']
    metrics = [(user["public_repos"], "PUBLIC REPOSITORIES"),
               (len(original), "ORIGINAL REPOSITORIES"),
               (len(languages), "PRIMARY LANGUAGES")]
    for i, (number, label) in enumerate(metrics):
        x = 28 + i * 310
        svg.append(f'<text x="{x}" y="99" font-size="49" font-weight="800" fill="#edf8ff">{number}</text><text x="{x}" y="126" class="mono" font-size="12" fill="#38bdf8">{label}</text>')
    svg.append('<path d="M28 149h904" stroke="#17374e"/>')
    svg.append('<text x="28" y="176" class="mono" font-size="11" fill="#88abc4">REPOSITORIES BY PRIMARY LANGUAGE</text>')
    colors = ["#38bdf8", "#3b82f6", "#60a5fa", "#93c5fd", "#b6dfff"]
    x = 28
    total = sum(languages.values())
    for i, (lang, count) in enumerate(languages.most_common()):
        width = 904 * count / total
        color = colors[i % len(colors)]
        svg.append(f'<rect x="{x:.2f}" y="187" width="{width:.2f}" height="7" fill="{color}"/>')
        x += width
    legend = "   /   ".join(f"{lang} {count}" for lang, count in languages.most_common(6))
    svg.append(f'<text x="28" y="218" class="mono" font-size="13" fill="#d0e8f7">{escape(legend)}</text>')
    svg.append(f'<text x="932" y="239" text-anchor="end" class="mono" font-size="10" fill="#678ba6">PUBLIC DATA / UPDATED {date} UTC</text></svg>')
    (ROOT / "assets" / "activity.svg").write_text("\n".join(svg), encoding="utf-8")
    print(f"Updated activity: {user['public_repos']} public repositories, {len(languages)} primary languages")


if __name__ == "__main__":
    main()
