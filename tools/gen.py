"""Gera assets/banner.svg e assets/ficha.svg. Uso: python3 tools/gen.py (na pasta perfil-github)."""
import json
import re
from pathlib import Path

from pixel import PALETTE as PALETTE_UI, sprite_rects, text_rects, text_width, wrap
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


def svg(width, height, title, desc, body, style="", background=True):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-labelledby="t d" shape-rendering="crispEdges">\n'
        f"<title id=\"t\">{title}</title>\n<desc id=\"d\">{desc}</desc>\n"
        + (f"<style>{style}</style>\n" if style else "")
        + (f'<rect width="{width}" height="{height}" fill="{BG}"/>\n' if background else "")
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
    for x in range(150, 960, len(tile[0]) * 3):
        body += sprite_rects(tile, x, 280, 3)

    body += sprite_rects(rose(stem_rows=14), 8, 92, 7)
    # a coroa inclinada, apoiada no alto da rosa
    body += sprite_rects(crown_tilted(), 100, 22, 4)

    body += text_rects("CARLOS GARCIA", 296, 34, 6, BLOND)
    body += text_rects("DEV FULL STACK", 296, 112, 4, GOLD)
    body += text_rects("O IMPOSSÍVEL NÃO EXISTE.", 296, 160, 4, ICE)

    # o 10 dourado com sombra de um pixel, como o número da camisa
    body += text_rects("10", 846, 14, 8, GOLD_DARK)
    body += text_rects("10", 840, 8, 8, GOLD)

    # a bola do chute: atravessa o galho em alta velocidade e para no fim
    trail = "".join(
        f'<rect x="{-length}" y="{y}" width="{length}" height="3" fill="{color}"/>'
        for length, y, color in ((120, 9, "#5B8FE8"), (80, 15, ICE), (160, 21, "#2E63C7"))
    )
    ball_rects = "".join(sprite_rects(ball(), 0, 0, 2))
    body.append(f'<g transform="translate(300 264)"><g class="shot"><g class="trail">{trail}</g>{ball_rects}</g></g>')

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
    w, h = 800, 316
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
    body.append(f'<rect x="24" y="96" width="{box}" height="156" fill="#18151A"/>')
    body.append(f'<rect x="24" y="96" width="{box}" height="4" fill="{GOLD}"/>')
    body += text_rects("68", 24 + (box - text_width("68", 8)) // 2, 106, 8, BLOND)
    body += text_rects("REPOSITÓRIOS", 24 + (box - text_width("REPOSITÓRIOS", 2)) // 2, 206, 2, TEXT)

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
        ly = 142 + row * 28
        body.append(f'<rect x="{lx}" y="{ly + 6}" width="12" height="12" fill="{color}"/>')
        body += text_rects(name, lx + 22, ly, 2, TEXT)
        body += text_rects(pct, lx + col_w - text_width(pct, 2), ly, 2, GOLD)

    body += text_rects("BYTES DE CÓDIGO, MEDIDO EM 21/10/2026", 24, 266, 2, "#9AA1B2")
    title = "Linguagens no GitHub de Carlos Garcia"
    desc = (
        "Ficha com a divisão das linguagens por bytes de código em 68 repositórios, "
        "medida em 21/10/2026: Java 52,2%, TypeScript 33,5%, JavaScript 3,3%, Dart 2,4%, CSS 2,3%, HTML 2,1% e outras 4,2%."
    )
    return svg(w, h, title, desc, body)


CARD_W = 800

# Experiência: do mais recente para o mais antigo (só o ano; os meses não foram informados)
EXPERIENCE = [
    ("2026 - atual", "Gerente de Tecnologia", "EMATER Goiás",
     "Agência Goiana de Assistência Técnica, Extensão Rural e Pesquisa Agropecuária",
     "Desenvolvo a intranet e os sistemas internos que melhoram o fluxo de trabalho das equipes."),
    ("2026 - atual", "Gerente de Tecnologia", "ASBRAER",
     "Associação Brasileira das Entidades Estaduais de Assistência Técnica e Extensão Rural",
     "Desenvolvi o portal do Censo da ASBRAER para os usuários."),
    ("2025 - 2026", "Desenvolvedor Ruby on Rails", "ALEGO", "Assembleia Legislativa do Estado de Goiás", None),
]
FRAME = "#2A2D3A"
SURFACE = "#18151A"

# Stack (levantada do sistema da EMATER e dos repositórios): (nome na placa, ícone do Simple Icons)
STACK = [
    ("Back", [("Java 21", "openjdk"), ("Spring Boot", "springboot"), ("Spring Security", "springsecurity"),
              ("Keycloak", "keycloak"), ("Ruby on Rails", "rubyonrails"), ("RabbitMQ", "rabbitmq")]),
    ("Front", [("React", "react"), ("TypeScript", "typescript"), ("Vite", "vite"), ("Tailwind CSS", "tailwindcss"),
               ("TanStack Query", "reactquery"), ("React Router", "reactrouter"), ("Next.js", "nextdotjs")]),
    ("Dados", [("PostgreSQL", "postgresql"), ("Flyway", "flyway"), ("Redis", "redis")]),
    ("Testes", [("JUnit 5", "junit5"), ("Vitest", "vitest"), ("Playwright", None)]),
    ("Mobile", [("Flutter", "flutter")]),
    ("Entrega", [("Docker", "docker"), ("Nginx", "nginx")]),
]

ICONS = Path(__file__).resolve().parent / "icons"
ICON_COLORS = json.loads((ICONS / "cores.json").read_text(encoding="utf-8"))


def icon(slug, x, y, size):
    """Logotipo oficial (Simple Icons, CC0) na cor da marca, ou claro quando a cor some no fundo."""
    if slug is None:  # sem logotipo na biblioteca: um sinal neutro em pixel, não um logotipo inventado
        return sprite_rects(["l....", "lll..", "lllll", "lll..", "l...."], x + 1, y + 2, size // 6)
    d = re.search(r' d="([^"]+)"', (ICONS / f"{slug}.svg").read_text(encoding="utf-8")).group(1)
    color = ICON_COLORS[slug]["use"]
    return [f'<path d="{d}" fill="{color}" transform="translate({x} {y}) scale({size / 24})" shape-rendering="geometricPrecision"/>']

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
    # sem fundo: a barra fica direto sobre o fundo do GitHub, sem faixa de outro tom
    return svg(w, h, text.capitalize(), f"Título da seção: {text.capitalize()}.", body, background=False)


def chip(label, slug, x, y):
    tw = text_width(label, 2)
    w, h = tw + 46, 32
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{SURFACE}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="3" fill="#2E63C7"/>',
        f'<rect x="{x}" y="{y + h - 3}" width="{w}" height="3" fill="{FRAME}"/>',
    ]
    out += icon(slug, x + 9, y + 7, 18)
    out += text_rects(label, x + 35, y + 4, 2, TEXT)
    return out, w, h


def stack_card():
    body = []
    body += title_bar("STACK")
    y = 88
    label_w = 110
    for group, items in STACK:
        body += text_rects(group, 28, y + 4, 2, GOLD)
        x = 28 + label_w
        row_h = 0
        for label, slug in items:
            _, cw, ch = chip(label, slug, 0, 0)
            if x + cw > CARD_W - 28:
                x = 28 + label_w
                y += ch + 8
            body += chip(label, slug, x, y)[0]
            x += cw + 8
            row_h = ch
        y += row_h + 14
    h = y + 12
    rows = "; ".join(f"{g}: {', '.join(label for label, _ in i)}" for g, i in STACK)
    return svg(CARD_W, h, "Stack", f"Stack de Carlos Garcia. {rows}.", frame(CARD_W, h) + body)


def education_card():
    """Formação: só o que está confirmado (curso e instituição), com um capelo em pixel."""
    body = title_bar("FORMAÇÃO")
    cap = [  # capelo: tampo em losango, copa embaixo e borla dourada pendurada na ponta direita
        ".......n.......",
        ".....nnhnn.....",
        "...nnhhhhhnn...",
        ".nnhhlllllhhnn.",
        "nhhlllllllllhhn",
        ".nnbbbbbbbbbnGn",
        "...nnbbbbbnn.G.",
        "....nmmmmmn..G.",
        "....nmmmmmn.GGG",
        "....nnnnnnn.GGG",
    ]
    body += sprite_rects(cap, 28, 92, 5, {**PALETTE_UI, "n": "#0A1230"})
    body += text_rects("Engenharia de Software", 112, 92, 3, BLOND)
    body += text_rects("Faculdade SENAI FATESG", 112, 128, 2, ICE)
    body += text_rects("Curso superior, em andamento", 112, 152, 2, "#9AA1B2")
    h = 196
    desc = "Formação: Engenharia de Software, curso superior em andamento na Faculdade SENAI FATESG."
    return svg(CARD_W, h, "Formação", desc, frame(CARD_W, h) + body)


def footer():
    """Fecho do README: o galho de espinhos atravessa e termina na rosa coroada, com a coroa de lado
    no ombro da rosa, na mesma proporção do banner."""
    w, h = CARD_W, 180
    body = []
    rose_cell, rose_x = 4, w - 150
    rose_rows = rose(stem_rows=8, leaves=False)
    rose_y = h - len(rose_rows) * rose_cell - 2
    stem_x = rose_x + 16 * rose_cell  # onde o caule fica, para o galho terminar nele
    tile = vine_tile()
    for x in range(0, stem_x, len(tile[0]) * 3):
        body += sprite_rects(tile, x, h - 42, 3)  # o meio do galho cruza o caule, não a flor
    body += sprite_rects(rose_rows, rose_x, rose_y, rose_cell)
    # banner: coroa 92 px à direita e 70 px acima da rosa de célula 7 -> mesma proporção aqui
    body += sprite_rects(crown_tilted(), rose_x + round(92 * rose_cell / 7), rose_y - round(70 * rose_cell / 7), 2)
    return svg(w, h, "Fecho", "Galho de espinhos que termina numa rosa azul com a coroa de lado.", body, background=False)


def experience_card():
    """Linha do tempo: período em dourado à esquerda; cargo, instituição e o que foi feito à direita."""
    body = title_bar("EXPERIÊNCIA")
    x_period, x_rail, x_text = 28, 190, 214
    width = CARD_W - 28 - x_text
    y = 92
    rail_top = y + 8
    for period, role, org, org_full, did in EXPERIENCE:
        body += text_rects(period, x_period, y, 2, GOLD)
        body += sprite_rects(["obbo", "bhlb", "blbm", "obmo"], x_rail - 6, y + 4, 3)
        body += text_rects(role, x_text, y - 2, 3, BLOND)
        body += text_rects(org, x_text, y + 34, 2, ICE)
        line_y = y + 58
        for line in wrap(org_full, width, 2):
            body += text_rects(line, x_text, line_y, 2, "#9AA1B2")
            line_y += 22
        if did:
            line_y += 6
            for line in wrap(did, width, 2):
                body += text_rects(line, x_text, line_y, 2, TEXT)
                line_y += 22
        y = line_y + 22
    body.insert(0, f'<rect x="{x_rail - 1}" y="{rail_top}" width="2" height="{y - rail_top - 40}" fill="#1F3E8C"/>')
    h = y + 8
    parts = []
    for p_, r, o, full, did in EXPERIENCE:
        parts.append(f"{p_}: {r}, {o} ({full})." + (f" {did}" if did else ""))
    return svg(CARD_W, h, "Experiência", "Experiência. " + " ".join(parts), frame(CARD_W, h) + body)


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
    body += sprite_rects(rose(stem_rows=3, leaves=False), -8, 176, 12)
    body += sprite_rects(crown_tilted(), 150, 30, 7)
    return svg(w, h, "Rosa azul coroada", "Pixel art de uma rosa azul com uma coroa dourada inclinada sobre ela.", body)


if __name__ == "__main__":
    out = ROOT / "assets"
    (out / "avatar.svg").write_text(avatar(), encoding="utf-8")
    (out / "stack.svg").write_text(stack_card(), encoding="utf-8")
    (out / "experiencia.svg").write_text(experience_card(), encoding="utf-8")
    (out / "formacao.svg").write_text(education_card(), encoding="utf-8")
    (out / "fecho.svg").write_text(footer(), encoding="utf-8")
    for slug, title in (("sobre", "SOBRE"),):
        (out / f"titulo-{slug}.svg").write_text(section_title(title), encoding="utf-8")
    print(sorted(p.name for p in out.iterdir()))
