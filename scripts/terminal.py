#!/usr/bin/env python3
"""Generates assets/terminal.svg, the animated terminal at the top of the README.

Edit SCRIPT below and run:  python3 scripts/terminal.py
Each entry is either ("cmd", "text") for a typed command or ("out", [segments])
for output that appears all at once. Segments are (color, text) pairs.
"""
import json
import os
import urllib.request
from datetime import date
from html import escape
from pathlib import Path

USER = "MarioSantosLP"


def contributions():
    """Returns (total in the last year, current daily streak), or None without a token."""
    token = os.environ.get("GH_TOKEN")
    if not token:
        return None
    q = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{'
         'totalContributions weeks{contributionDays{date contributionCount}}}}}}')
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"] if d["date"] <= date.today().isoformat()]
    if days and days[-1]["contributionCount"] == 0:
        days = days[:-1]  # today isn't over yet, so it doesn't break the streak
    streak = 0
    for d in reversed(days):
        if d["contributionCount"] == 0:
            break
        streak += 1
    return cal["totalContributions"], streak

PROMPT = [("green", "mario@aveiro"), ("dim", ":~$ ")]

SCRIPT = [
    ("cmd", "whoami"),
    ("out", [("fg", "Mario Santos"), ("dim", "  // Computer Engineering student @ University of Aveiro")]),
    ("gap", None),
    ("cmd", "neofetch --short"),
    ("out", [("cyan", "  langs    "), ("fg", "Python · Java · C · JavaScript · SQL · Bash")]),
    ("out", [("cyan", "  web      "), ("fg", "React · HTML · CSS")]),
    ("out", [("cyan", "  tools    "), ("fg", "Git · Linux · Docker")]),
    ("out", [("cyan", "  now      "), ("yellow", "SND, an AI agent that deploys 5G networks")]),
    ("out", [("cyan", "  offline  "), ("fg", "basketball")]),
    ("activity", None),
    ("gap", None),
    ("end", None),
]

COLORS = {
    "fg": "#e6edf3", "dim": "#8b949e", "green": "#7ee787", "cyan": "#79c0ff",
    "yellow": "#f2cc60", "violet": "#d2a8ff",
}
W, PAD, TOP, LH, FS, CW = 860, 24, 58, 25, 15, 9.0  # CW = char width forced on typed text
TYPE_SPEED, START = 0.07, 0.6                        # seconds per char, initial delay
FONT = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def tspans(segs):
    return "".join(f'<tspan fill="{COLORS[c]}">{escape(t)}</tspan>' for c, t in segs)


def build():
    rows, y, t = [], TOP, START
    prompt_w = sum(len(s) for _, s in PROMPT) * CW
    for kind, val in SCRIPT:
        if kind == "activity":
            stats = contributions()
            if not stats:
                continue
            total, streak = stats
            segs = [("cyan", "  activity "), ("green", f"{total:,}"), ("fg", " contributions in the last year")]
            if streak > 1:
                segs += [("dim", " · "), ("green", f"{streak}"), ("fg", "-day streak")]
            kind, val = "out", segs
        if kind == "gap":
            y += LH * 0.45
            continue
        if kind == "out":
            rows.append(f'<text x="{PAD}" y="{y}" opacity="0">{tspans(val)}'
                        f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></text>')
            t += 0.12
            y += LH
            continue
        # command or final prompt
        rows.append(f'<text x="{PAD}" y="{y}" opacity="0" textLength="{prompt_w}" lengthAdjust="spacing">'
                    f'{tspans(PROMPT)}<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></text>')
        x0 = PAD + prompt_w
        if kind == "end":
            rows.append(f'<rect x="{x0}" y="{y - FS + 2}" width="{CW}" height="{FS + 3}" fill="{COLORS["fg"]}" opacity="0">'
                        f'<animate attributeName="opacity" values="1;0" dur="1.1s" calcMode="discrete" '
                        f'begin="{t:.2f}s" repeatCount="indefinite"/></rect>')
            break
        n = len(val)
        t += 0.45
        clip = f"c{len(rows)}"
        widths = ";".join(f"{i * CW:.1f}" for i in range(n + 1))
        xs = ";".join(f"{x0 + i * CW:.1f}" for i in range(n + 1))
        dur = n * TYPE_SPEED
        rows.append(
            f'<clipPath id="{clip}"><rect x="{x0}" y="{y - LH}" height="{LH + 6}" width="0">'
            f'<animate attributeName="width" values="{widths}" calcMode="discrete" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'</rect></clipPath>'
            f'<text x="{x0}" y="{y}" fill="{COLORS["fg"]}" clip-path="url(#{clip})" textLength="{n * CW}" '
            f'lengthAdjust="spacing">{escape(val)}</text>'
            f'<rect x="{x0}" y="{y - FS + 2}" width="{CW}" height="{FS + 3}" fill="{COLORS["fg"]}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{t - 0.45:.2f}s"/>'
            f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{t + dur + 0.25:.2f}s" fill="freeze"/></rect>'
        )
        t += dur + 0.35
        y += LH
    h = int(y + 22)
    dots = "".join(f'<circle cx="{22 + i * 20}" cy="18" r="6" fill="{c}"/>'
                   for i, c in enumerate(["#ff7b72", "#f2cc60", "#7ee787"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Terminal: Mario Santos, Computer Engineering student at the University of Aveiro. Python, Java, C, JavaScript, SQL, Bash, React. Working on SND, an AI agent that deploys 5G networks.">
<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="10" fill="#010409" stroke="#30363d"/>
<path d="M0.5 10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V36 H0.5Z" fill="#161b22"/>
<line x1="0.5" y1="36" x2="{W - 0.5}" y2="36" stroke="#30363d"/>
{dots}
<text x="{W / 2}" y="23" text-anchor="middle" fill="#8b949e" font-family="{FONT}" font-size="12">mario@aveiro: ~</text>
<g font-family="{FONT}" font-size="{FS}" xml:space="preserve">
{chr(10).join(rows)}
</g>
</svg>
'''


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}")
