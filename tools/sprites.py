"""Sprites originais do tema: rosa azul, coroa com fechadura, bola e galho de espinhos."""
import math

def _grid(w, h):
    return [["." for _ in range(w)] for _ in range(h)]


def _outline(g, fill_char="o"):
    h, w = len(g), len(g[0])
    out = [row[:] for row in g]
    for y in range(h):
        for x in range(w):
            if g[y][x] == ".":
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or g[ny][nx] == ".":
                    out[y][x] = fill_char
                    break
    return out


HALF_WIDTH = [2.5, 4.5, 6.5, 7.5, 8.5, 9.5, 10, 10.5, 10.5, 10, 9.5, 9, 8.5, 7.5, 6.5, 5.5, 4.5, 3, 2]


def _rose_head():
    """Cabeça da rosa por regiões de pétala: botão (B), pétalas esquerda (L), direita (R) e da frente (F)."""
    w, h = 22, len(HALF_WIDTH)
    xc = 10.5
    region = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            dx = x - xc
            if abs(dx) > HALF_WIDTH[y]:
                continue
            front_top = 9 - 3.2 * (dx / 8.5) ** 2
            if y >= front_top and abs(dx) <= 8.5:
                region[y][x] = "F"
            elif (dx / 6.2) ** 2 + ((y - 6.5) / 6.5) ** 2 <= 1 and y <= 8:
                region[y][x] = "B"
            else:
                region[y][x] = "L" if dx < 0 else "R"

    g = _grid(w, h)
    for y in range(h):
        for x in range(w):
            r = region[y][x]
            if r is None:
                continue
            dx = x - xc
            if r == "L":
                g[y][x] = "h" if (dx < -8.5 and y <= 8) else "l"
            elif r == "R":
                g[y][x] = "l" if (dx > 8.5 and y <= 7) else ("d" if dx > 7 else "m")
            elif r == "F":
                t = (dx + 8.5) / 17
                g[y][x] = "lbbmmd"[min(5, int(t * 6))] if y < 15 else "bmmdd"[min(4, int(t * 5))]
            else:
                g[y][x] = "l" if dx < -2 else ("b" if dx < 3 else "m")

    # contorno entre pétalas: onde a região muda para a direita ou para baixo
    for y in range(h):
        for x in range(w):
            r = region[y][x]
            if r is None:
                continue
            for nx, ny in ((x + 1, y), (x, y + 1)):
                if nx < w and ny < h and region[ny][nx] not in (None, r):
                    g[y][x] = "o"

    # espiral do botão
    for i in range(0, 300):
        t = i / 30.0
        rr = 0.7 * t
        if rr > 5.0:
            break
        x = int(round(xc + rr * math.cos(t + 1.2)))
        y = int(round(4.5 + 0.75 * rr * math.sin(t + 1.2)))
        if 0 <= y < h and region[y][x] == "B":
            g[y][x] = "o"
    # brilho na borda da pétala da frente e reflexo do botão
    for x in range(w):
        dx = x - xc
        y = int(math.ceil(9 - 3.2 * (dx / 8.5) ** 2))
        if abs(dx) <= 7.5 and 0 <= y + 1 < h and region[y + 1][x] == "F" and dx < 2:
            g[y + 1][x] = "h"
    g[2][7] = "w"
    g[3][6] = "w"
    return [list(r) for r in _outline(g)]


def rose(stem_rows=24, leaves=True):
    head = _rose_head()
    hw = len(head[0])
    w, h = hw + 12, len(head) + stem_rows
    g = _grid(w, h)
    ox = 6
    for y, row in enumerate(head):
        for x, c in enumerate(row):
            if c != ".":
                g[y][x + ox] = c
    cx = ox + hw // 2 - 1
    base_y = len(head)

    # sépalas
    for dx, length in ((-2, 3), (2, 3)):
        for k in range(length):
            x = cx + dx + (k if dx > 0 else -k)
            y = base_y - 3 + k
            g[y][x] = "m"
            g[y][x + 1] = "d"

    # caule com espinhos
    stem = []
    for y in range(base_y, h):
        x = cx + int(round(1.6 * math.sin((y - base_y) / 4.5)))
        stem.append((x, y))
    for x, y in stem:
        g[y][x] = "b"
        g[y][x + 1] = "m"
    for k, (x, y) in enumerate(stem[3:], start=3):
        if k % 6 == 3:
            g[y][x - 1] = "l"
            g[y - 1][x - 2] = "l"
        if k % 6 == 0:
            g[y][x + 2] = "m"
            g[y - 1][x + 3] = "m"

    def stamp(rows, ox_, oy_):
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c != "." and 0 <= oy_ + j < h and 0 <= ox_ + i < w:
                    g[oy_ + j][ox_ + i] = c

    leaf = [
        "ooo........",
        "ohlooo.....",
        "olbbmmoo...",
        ".ombbmmmoo.",
        "..ooommmddo",
        ".....ooooo.",
    ]
    if leaves:
        sx, sy = stem[min(11, len(stem) - 3)]
        stamp(leaf, sx - 11, sy - 4)
        sx, sy = stem[4]
        stamp([r[::-1] for r in leaf], sx + 2, sy - 4)
    return ["".join(r) for r in g]


def crown_tilted():
    """Coroa desenhada direto na grade, inclinada em degraus regulares: sem sobras de pixel por construção."""
    w, h = 32, 28
    g = _grid(w, h)

    def tilt(x):
        return x // 8  # desce 1 linha a cada 8 colunas: a coroa tomba para a direita

    def band_top(x):
        return 16 + tilt(x)

    def band_bottom(x):
        return 22 + tilt(x) + (1 if 8 <= x <= 23 else 0)  # barriga do aro no centro

    # pontas de trás, baixas e na sombra
    for cx in (11, 20):
        tip = 11 + tilt(cx)
        for y in range(tip, band_top(cx) + 1):
            half = (y - tip) // 2
            for x in range(cx - half, cx + half + 1):
                g[y][x] = "Y"
    # pontas da frente: face clara à esquerda, escura à direita, aresta de brilho no meio
    tips = {}
    for cx, lift in ((6, 0), (15, 2), (25, 0)):
        tip = 7 + tilt(cx) - lift
        tips[cx] = tip
        for y in range(tip, band_top(cx) + 1):
            half = 1 + (y - tip) // 2  # a ponta já nasce com 3 pixels: o miolo sobrevive ao contorno
            for x in range(cx - half, cx + half + 1):
                g[y][x] = "L" if x == cx else ("G" if x < cx else "y")
    # faixa do aro
    for x in range(2, 30):
        for y in range(band_top(x), band_bottom(x) + 1):
            g[y][x] = "G" if x < 11 else ("y" if x < 22 else "Y")
        g[band_top(x)][x] = "L" if x < 20 else "G"  # filete de brilho na borda de cima
        g[band_bottom(x)][x] = "Y"
    # pedras e fechadura
    for gx in (6, 25):
        gy = band_top(gx) + 2
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            g[gy + dy][gx + dx] = "h" if (dx, dy) == (0, 0) else "b"
    ky = band_top(15) + 2
    for dy, row in enumerate([".kk.", "kkkk", ".kk.", "kkkk"]):  # cabeça redonda, fenda e base que alarga
        for dx, c in enumerate(row):
            if c == "k":
                g[ky + dy][14 + dx] = "k"
    g = _outline(g, "n")
    # pérolas carimbadas exatamente na ponta
    pearl = [".nnn.", "nwWWn", "nWWWn", ".nnn."]
    for cx, tip in tips.items():
        top = tip - 3  # o contorno de baixo da pérola coincide com o contorno do topo da ponta
        for dy, row in enumerate(pearl):
            for dx, c in enumerate(row):
                if c != "." and 0 <= top + dy < h:
                    g[top + dy][cx - 2 + dx] = c
    return ["".join(r) for r in g]


def ball():
    return [
        "...oooo...",
        ".ooWWWWoo.",
        ".oWsWWsWo.",
        "oWWssssWWo",
        "oWsWssWsWo",
        "oWWsWWsWWo",
        "oWWWssWWWo",
        ".oWsWWsWo.",
        ".ooWWWWoo.",
        "...oooo...",
    ]


def vine_tile(width=16, height=9):
    """Duas hastes em seno que se cruzam como corrente, com espinho no alto de cada curva."""
    g = _grid(width, height)
    mid = (height - 1) / 2
    for x in range(width):
        a = math.sin(2 * math.pi * x / width)
        ya, yb = int(round(mid - 2.6 * a)), int(round(mid + 2.6 * a))
        g[ya][x] = "b"
        g[yb][x] = "m" if g[yb][x] == "." else g[yb][x]
    for x, up in ((width // 4, True), (3 * width // 4, False)):
        y = 0 if up else height - 1
        g[y][x] = "l"
    return ["".join(r) for r in g]


if __name__ == "__main__":
    print("\n".join(rose()))
