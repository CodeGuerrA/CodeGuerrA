"""Gera assets/contribuicoes.svg: o quadro de contribuições do último ano no tema (azul da rosa, dia mais forte em dourado).

Lê o calendário pela API GraphQL do GitHub. Com "Private contributions" ligado no perfil, o total já inclui o
trabalho privado, de forma anônima. Token: GITHUB_TOKEN (na Action) ou GH_TOKEN; sem nenhum, usa o `gh` local.
Uso: python3 tools/contrib.py [usuario]
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

from gen import BG, BLOND, CARD_W, GOLD, ICE, frame, svg, title_bar
from pixel import text_rects, text_width

ROOT = Path(__file__).resolve().parent.parent
QUERY = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date contributionCount contributionLevel } } } } } }"""
LEVELS = {"NONE": "#1A1C26", "FIRST_QUARTILE": "#14244F", "SECOND_QUARTILE": "#1F3E8C",
          "THIRD_QUARTILE": "#2E63C7", "FOURTH_QUARTILE": "#5B8FE8"}
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def fetch(login):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
        request = urllib.request.Request(
            "https://api.github.com/graphql", data=body,
            headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
        )
        data = json.load(urllib.request.urlopen(request, timeout=30))
    else:
        out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={login}"],
                             check=True, capture_output=True, text=True).stdout
        data = json.loads(out)
    if data.get("errors") or not (data.get("data") or {}).get("user"):
        raise SystemExit(f"A API do GitHub não devolveu o calendário: {data.get('errors')}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def previous_total(path):
    """Total gravado no quadro atual (fica na descrição do SVG), ou None se ainda não existe."""
    if not path.exists():
        return None
    match = re.search(r"últim[oa] ano: ([\d.]+) contribuições", path.read_text(encoding="utf-8"))
    return int(match.group(1).replace(".", "")) if match else None


def thousands(n):
    return f"{n:,}".replace(",", ".")


def chart(calendar):
    weeks = calendar["weeks"]
    days = [d for week in weeks for d in week["contributionDays"]]
    best = max(days, key=lambda d: d["contributionCount"])
    cell, gap = 12, 2
    x0, y0 = 28, 120
    body = title_bar("CONTRIBUIÇÕES")
    total = thousands(calendar["totalContributions"])
    body += text_rects(total, CARD_W - 28 - text_width(total, 3) - text_width(" no último ano", 2), 30, 3, BLOND)
    body += text_rects(" no último ano", CARD_W - 28 - text_width(" no último ano", 2), 36, 2, ICE)
    last_month = None
    for i, week in enumerate(weeks):
        x = x0 + i * (cell + gap)
        first = date.fromisoformat(week["contributionDays"][0]["date"])
        if first.month != last_month and first.day <= 7 and i < len(weeks) - 2:
            body += text_rects(MONTHS[first.month - 1], x, 84, 2, "#9AA1B2")
            last_month = first.month
        for d in week["contributionDays"]:
            weekday = (date.fromisoformat(d["date"]).weekday() + 1) % 7  # domingo no alto, como no GitHub
            y = y0 + weekday * (cell + gap)
            color = GOLD if d is best and d["contributionCount"] > 0 else LEVELS[d["contributionLevel"]]
            body.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}"/>')
    # legenda: do vazio ao mais forte, e o dourado escrito, nunca só cor
    ly = y0 + 7 * (cell + gap) + 18
    body += text_rects("menos", x0, ly, 2, "#9AA1B2")
    lx = x0 + text_width("menos", 2) + 10
    for color in LEVELS.values():
        body.append(f'<rect x="{lx}" y="{ly + 6}" width="{cell}" height="{cell}" fill="{color}"/>')
        lx += cell + gap
    body += text_rects("mais", lx + 8, ly, 2, "#9AA1B2")
    best_label = f"dia mais forte: {date.fromisoformat(best['date']).strftime('%d/%m/%Y')}, {best['contributionCount']} contribuições"
    bx = CARD_W - 28 - text_width(best_label, 2)
    body.append(f'<rect x="{bx - 20}" y="{ly + 6}" width="{cell}" height="{cell}" fill="{GOLD}"/>')
    body += text_rects(best_label, bx, ly, 2, GOLD)
    h = ly + 44
    desc = (
        f"Quadro de contribuições do último ano: {total} contribuições, públicas e privadas. "
        f"Dia mais forte: {best['date']}, com {best['contributionCount']}."
    )
    return svg(CARD_W, h, "Contribuições no último ano", desc, frame(CARD_W, h) + body)


if __name__ == "__main__":
    login = sys.argv[1] if len(sys.argv) > 1 else "CodeGuerrA"
    cal = fetch(login)
    out = ROOT / "assets" / "contribuicoes.svg"
    before = previous_total(out)
    # Trava: numa janela de um ano o total não cai pela metade de um dia para o outro. Se cair, o token
    # provavelmente não enxerga as contribuições privadas; melhor a Action falhar do que publicar número errado.
    if before and cal["totalContributions"] < before / 2:
        raise SystemExit(
            f"Total caiu de {before} para {cal['totalContributions']}: o token não deve estar vendo as "
            "contribuições privadas. O quadro não foi alterado."
        )
    out.write_text(chart(cal), encoding="utf-8")
    print(out, cal["totalContributions"])
