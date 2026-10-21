"""Gera assets/banner.svg e assets/ficha.svg. Uso: python3 tools/gen.py (na pasta perfil-github)."""
from pathlib import Path

from pixel import sprite_rects, text_rects, text_width, wrap
from sprites import ball, crown_tilted, rose, vine_tile

ROOT = Path(__file__).resolve().parent.parent
BG = "#0E0D12"
BLOND = "#F4E5BA"
GOLD = "#B8954A"
GOLD_DARK = "#6B5225"
ICE = "#A9C8FF"
TEXT = "#E9ECF3"
STREAK = "#1F3E8C"

# Linguagens medidas pela API do GitHub em 21/10/2026: bytes de código em 68 repositórios (públicos e privados).
LANGUAGES = [
    ("JAVA", "52,2%", 52.2, GOLD),
    ("TYPESCRIPT", "33,5%", 33.5, "#5B8FE8"),
    ("JAVASCRIPT", "3,3%", 3.3, BLOND),
    ("DART", "2,4%", 2.4, ICE),
    ("CSS", "2,3%", 2.3, "#C23B30"),
    ("HTML", "2,1%", 2.1, "#7D8597"),
    ("OUTRAS", "4,2%", 4.2, "#757189"),
]


def svg(width, height, title, desc, body, style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-labelledby="t d" shape-rendering="crispEdges">\n'
        f"<title id=\"t\">{title}</title>\n<desc id=\"d\">{desc}</desc>\n"
        + (f"<style>{style}</style>\n" if style else "")
        + f'<rect width="{width}" height="{height}" fill="{BG}"/>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def banner():
    w, h = 960, 330
    body = []

    # linhas de velocidade do chute, só na faixa de baixo
    for x, y, length in ((360, 238, 140), (590, 228, 110), (480, 264, 180)):
        body.append(f'<rect x="{x}" y="{y}" width="{length}" height="3" fill="#14244F"/>')

    # galho de espinhos: sai do caule da rosa e corre embaixo do texto
    tile = vine_tile()
    for x in range(150, 960, 48):
        body += sprite_rects(tile, x, 282, 3)

    body += sprite_rects(rose(stem_rows=14), 8, 92, 7)
    # a coroa inclinada, apoiada no alto da rosa
    body += sprite_rects(crown_tilted(), 118, 24, 4)

    body += text_rects("CARLOS GARCIA", 296, 34, 6, BLOND)
    body += text_rects("DEV FULL STACK", 296, 112, 4, GOLD)
    body += text_rects("O IMPOSSÍVEL NÃO EXISTE.", 296, 160, 4, ICE)

    # o 10 dourado com sombra de um pixel, como o número da camisa
    body += text_rects("10", 846, 14, 8, GOLD_DARK)
    body += text_rects("10", 840, 8, 8, GOLD)

    # a bola do Kaiser Impact: sai da coroa, atravessa o galho e para no fim
    trail = "".join(
        f'<rect x="{-length}" y="{y}" width="{length}" height="3" fill="{color}"/>'
        for length, y, color in ((120, 9, "#5B8FE8"), (80, 15, ICE), (160, 21, "#2E63C7"))
    )
    ball_rects = "".join(sprite_rects(ball(), 0, 0, 3))
    body.append(f'<g transform="translate(300 252)"><g class="shot"><g class="trail">{trail}</g>{ball_rects}</g></g>')

    style = (
        ".shot{animation:shot 7s infinite;transform:translateX(590px)}"
        ".trail{animation:trail 7s infinite;opacity:0}"
        "@keyframes shot{0%{transform:translateX(0);opacity:0;animation-timing-function:cubic-bezier(.23,1,.32,1)}"
        "3%{opacity:1}24%{transform:translateX(590px)}80%{transform:translateX(590px);opacity:1}"
        "88%,100%{transform:translateX(590px);opacity:0}}"
        "@keyframes trail{0%,3%{opacity:1}22%{opacity:0}100%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.shot{animation:none;opacity:1}.trail{animation:none}}"
    )
    title = "Carlos Garcia, dev full stack"
    desc = (
        "Pixel art de uma rosa azul com caule de espinhos e uma coroa dourada com fechadura inclinada sobre ela. "
        "Texto: Carlos Garcia. Dev full stack. O impossível não existe."
    )
    return svg(w, h, title, desc, body, style)


def ficha():
    w, h = 800, 380
    body = []
    frame = "#2A2D3A"
    body.append(f'<rect x="8" y="8" width="{w - 16}" height="4" fill="{frame}"/>')
    body.append(f'<rect x="8" y="{h - 12}" width="{w - 16}" height="4" fill="{frame}"/>')
    body.append(f'<rect x="8" y="8" width="4" height="{h - 16}" fill="{frame}"/>')
    body.append(f'<rect x="{w - 12}" y="8" width="4" height="{h - 16}" fill="{frame}"/>')

    # barra de título inclinada, na gramática da ficha do mangá
    body.append(f'<polygon points="24,28 560,28 536,68 24,68" fill="{GOLD}"/>')
    body += text_rects("LINGUAGENS NO GITHUB", 40, 30, 3, BG)

    # caixa do total, como o TOTAL da ficha
    box = 168
    body.append(f'<rect x="24" y="96" width="{box}" height="196" fill="#18151A"/>')
    body.append(f'<rect x="24" y="96" width="{box}" height="4" fill="{GOLD}"/>')
    body += text_rects("68", 24 + (box - text_width("68", 10)) // 2, 112, 10, BLOND)
    body += text_rects("REPOSITÓRIOS", 24 + (box - text_width("REPOSITÓRIOS", 2)) // 2, 236, 2, TEXT)

    # barra empilhada, como a barra de linguagens do próprio GitHub
    bar_x, bar_w = 216, 560
    x = bar_x
    for i, (_, _, value, color) in enumerate(LANGUAGES):
        width = round(bar_w * value / 100) if i < len(LANGUAGES) - 1 else bar_x + bar_w - x
        # vão de 2 px entre segmentos: vizinhos de cor parecida continuam separados
        gap = 2 if i < len(LANGUAGES) - 1 else 0
        body.append(f'<rect x="{x}" y="100" width="{width - gap}" height="28" fill="{color}"/>')
        x += width

    # legenda: nome e porcentagem escritos, a cor nunca sozinha
    columns = ((bar_x, 318), (bar_x + 340, bar_w - 340))
    for i, (name, pct, _, color) in enumerate(LANGUAGES):
        col, row = divmod(i, 4)
        lx, col_w = columns[col]
        ly = 146 + row * 40
        body.append(f'<rect x="{lx}" y="{ly + 10}" width="16" height="16" fill="{color}"/>')
        body += text_rects(name, lx + 28, ly, 3, TEXT)
        body += text_rects(pct, lx + col_w - text_width(pct, 3), ly, 3, GOLD)

    body += text_rects("BYTES DE CÓDIGO, MEDIDO EM 21/10/2026", 24, 318, 2, "#9AA1B2")
    title = "Linguagens no GitHub de Carlos Garcia"
    desc = (
        "Ficha com a divisão das linguagens por bytes de código em 68 repositórios, "
        "medida em 21/10/2026: Java 52,2%, TypeScript 33,5%, JavaScript 3,3%, Dart 2,4%, CSS 2,3%, HTML 2,1% e outras 4,2%."
    )
    return svg(w, h, title, desc, body)


CARD_W = 800
FRAME = "#2A2D3A"
SURFACE = "#18151A"

STACK = [
    ("Back", ["Java 21", "Spring Boot", "Spring Security", "OAuth2", "Keycloak"]),
    ("Dados", ["PostgreSQL", "Flyway", "Redis"]),
    ("Front", ["React", "TypeScript", "Next.js", "Vite", "Tailwind CSS", "Angular"]),
    ("Mobile", ["Flutter"]),
    ("Entrega", ["Docker"]),
]

PROJECTS = [
    ("bot-chamados-glpi-alego", "Chatbot de service desk pelo WhatsApp, integrado ao GLPI.",
     "Java 21, Spring Boot, arquitetura hexagonal e Redis"),
    ("simulador-precificacao-saas", "Ajuda a decidir o preço e o número de clientes de um serviço por assinatura.",
     "Next.js, React e TypeScript"),
    ("PI-Personal-Finance", "App de finanças pessoais, com API e app de celular.", "Spring Boot e Flutter"),
    ("keycloak-spring", "Login com Keycloak numa API Spring Boot.", "Java 21, Spring Security e Keycloak"),
]


def frame(w, h):
    return [
        f'<rect x="8" y="8" width="{w - 16}" height="4" fill="{FRAME}"/>',
        f'<rect x="8" y="{h - 12}" width="{w - 16}" height="4" fill="{FRAME}"/>',
        f'<rect x="8" y="8" width="4" height="{h - 16}" fill="{FRAME}"/>',
        f'<rect x="{w - 12}" y="8" width="4" height="{h - 16}" fill="{FRAME}"/>',
    ]


def title_bar(text, x=24, y=28):
    """Barra dourada inclinada com o título, a mesma da ficha de linguagens."""
    width = text_width(text, 3) + 64
    return [f'<polygon points="{x},{y} {x + width},{y} {x + width - 24},{y + 40} {x},{y + 40}" fill="{GOLD}"/>'] + text_rects(
        text, x + 16, y + 2, 3, BG
    )


def section_title(text):
    w, h = CARD_W, 64
    body = title_bar(text, 0, 12)
    return svg(w, h, text.capitalize(), f"Título da seção: {text.capitalize()}.", body)


def chip(label, x, y):
    tw = text_width(label, 3)
    w, h = tw + 28, 44
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{SURFACE}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="4" fill="#2E63C7"/>',
        f'<rect x="{x}" y="{y + h - 4}" width="{w}" height="4" fill="{FRAME}"/>',
    ]
    out += text_rects(label, x + 14, y + 4, 3, TEXT)
    return out, w, h


def stack_card():
    body = []
    body += title_bar("STACK")
    y = 92
    label_w = 150
    for group, items in STACK:
        body += text_rects(group, 28, y + 4, 3, GOLD)
        x = 28 + label_w
        row_h = 0
        for item in items:
            parts, cw, ch = chip(item, 0, 0)
            if x + cw > CARD_W - 28:
                x = 28 + label_w
                y += ch + 10
            body += chip(item, x, y)[0]
            x += cw + 10
            row_h = ch
        y += row_h + 22
    h = y + 12
    rows = "; ".join(f"{g}: {', '.join(i)}" for g, i in STACK)
    return svg(CARD_W, h, "Stack", f"Stack de Carlos Garcia. {rows}.", frame(CARD_W, h) + body)


def project_card(name, description, made_with):
    body = []
    # nome do projeto em destaque, com a pedra azul ao lado
    body += sprite_rects(["obbo", "bhlb", "blbm", "obmo"], 28, 34, 4)
    body += text_rects(name, 56, 24, 4, BLOND)
    y = 82
    for line in wrap(description, CARD_W - 56, 3):
        body += text_rects(line, 28, y, 3, TEXT)
        y += 34
    y += 6
    body += text_rects("Feito com", 28, y, 3, GOLD)
    x0 = 28 + text_width("Feito com", 3) + 18
    for i, line in enumerate(wrap(made_with, CARD_W - 28 - x0, 3)):
        body += text_rects(line, x0, y + i * 34, 3, ICE)
    y += 34 * len(wrap(made_with, CARD_W - 28 - x0, 3))
    h = y + 22
    desc = f"Projeto {name}: {description} Feito com {made_with}."
    return svg(CARD_W, h, name, desc, frame(CARD_W, h) + body)


if __name__ == "__main__":
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    (out / "banner.svg").write_text(banner(), encoding="utf-8")
    (out / "ficha.svg").write_text(ficha(), encoding="utf-8")
    for name in ("banner.svg", "ficha.svg"):
        print(out / name, (out / name).stat().st_size, "bytes")


def avatar():
    """Foto de perfil: a rosa coroada no centro, pensada para o recorte redondo do GitHub."""
    w = h = 460
    body = [f'<circle cx="230" cy="230" r="230" fill="#14244F" opacity="0.35"/>']
    body += sprite_rects(rose(stem_rows=5, leaves=False), -8, 150, 12)
    body += sprite_rects(crown_tilted(), 184, 30, 7)
    return svg(w, h, "Rosa azul coroada", "Pixel art de uma rosa azul com uma coroa dourada inclinada sobre ela.", body)


if __name__ == "__main__":
    out = ROOT / "assets"
    (out / "avatar.svg").write_text(avatar(), encoding="utf-8")
    (out / "stack.svg").write_text(stack_card(), encoding="utf-8")
    for slug, title in (("sobre", "SOBRE"), ("em-campo", "EM CAMPO")):
        (out / f"titulo-{slug}.svg").write_text(section_title(title), encoding="utf-8")
    for name, description, made_with in PROJECTS:
        (out / f"projeto-{name.lower()}.svg").write_text(project_card(name, description, made_with), encoding="utf-8")
    print(sorted(p.name for p in out.iterdir()))
