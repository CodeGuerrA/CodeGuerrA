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


def crown_tilted(angle=16):
    """Coroa inclinada de lado. A forma é matemática (aro curvo e pontas em triângulo); cada pixel final é
    amostrado na coroa em pé (4 amostras, voto da maioria). Fechadura, safiras e pérolas entram como carimbos
    desenhados à mão, sem girar, na posição girada: nada deforma e nenhuma borda vaza."""
    ang = math.radians(angle)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    half_band = 12.5

    def top(u):
        return 2 * (1 - (u / half_band) ** 2)  # borda de cima do aro, curva

    def bottom(u):
        return 6 + 3 * (1 - (u / half_band) ** 2)  # borda de baixo, curva mais funda

    front = ((-9.5, -7.5), (0.0, -10.0), (9.5, -7.5))  # (posição, altura da ponta) das pontas da frente

    def spike(u, v, u0, tip, base_half):
        if not tip <= v <= top(u0) + 0.5:
            return False
        return abs(u - u0) <= base_half * (v - tip) / (top(u0) - tip) + 1.3  # topo com 2 a 3 pixels

    def color(u, v):
        if abs(u) <= half_band and top(u) <= v <= bottom(u):
            if v - top(u) < 1:
                return "L" if u < 4 else "G"
            if bottom(u) - v < 1:
                return "Y"
            return "G" if u < -4 else ("y" if u < 5 else "Y")
        for u0, tip in front:
            if spike(u, v, u0, tip, 3.6):
                d = u - u0
                return "L" if abs(d) < 0.55 else ("G" if d < 0 else "y")
        return None

    def to_screen(u, v):  # em pé -> inclinada (horário)
        return u * cos_a - v * sin_a, u * sin_a + v * cos_a

    def to_upright(x, y):
        return x * cos_a + y * sin_a, -x * sin_a + y * cos_a

    corners = [to_screen(u, v) for u in (-15, 15) for v in (-14, 11)]
    minx, maxx = min(c[0] for c in corners), max(c[0] for c in corners)
    miny, maxy = min(c[1] for c in corners), max(c[1] for c in corners)
    w, h = int(maxx - minx) + 2, int(maxy - miny) + 2
    g = _grid(w, h)
    for gy in range(h):
        for gx in range(w):
            votes = {}
            for sx in (0.25, 0.75):
                for sy in (0.25, 0.75):
                    c = color(*to_upright(gx + sx + minx, gy + sy + miny))
                    if c:
                        votes[c] = votes.get(c, 0) + 1
            if sum(votes.values()) >= 2:
                g[gy][gx] = max(votes, key=votes.get)

    def cell(u, v):
        x, y = to_screen(u, v)
        return int(x - minx), int(y - miny)

    # tira pixel pendurado (só encosta por um lado) antes do contorno
    for _ in range(2):
        for y in range(h):
            for x in range(w):
                if g[y][x] != "." and sum(
                    1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= y + dy < h and 0 <= x + dx < w and g[y + dy][x + dx] != "."
                ) <= 1:
                    g[y][x] = "."

    def stamp(rows, cx, cy, skip_outline_on_gold=False):
        for dy, row in enumerate(rows):
            for dx, c in enumerate(row):
                x, y = cx + dx, cy + dy
                if c != "." and 0 <= y < h and 0 <= x < w:
                    g[y][x] = c

    # safiras e fechadura, retas, no meio da faixa girada
    for u in (-8.0, 8.0):
        x, y = cell(u, 4.6)
        stamp(["hb", "bb"], x, y - 1)
    x, y = cell(0.2, 5.2)
    stamp([".kk.", "kkkk", ".kk.", "kkkk"], x - 2, y - 2)
    g = _outline(g, "n")
    # pérolas: acham o pixel de ouro mais alto da ponta e sentam com o contorno coincidindo com o dela
    for u0, tip in front:
        x, _ = cell(u0, tip)
        top_cell = min(
            ((cx, cy) for cy in range(h) for cx in range(max(0, x - 2), min(w, x + 3)) if g[cy][cx] in "GLyY"),
            key=lambda c: (c[1], abs(c[0] - x)),
        )
        stamp([".nnn.", "nwWWn", "nWWWn", ".nnn."], top_cell[0] - 2, top_cell[1] - 4)
    return ["".join(r) for r in g]


def ball(size=15):
    """Bola de futebol: círculo com pentágono escuro no centro e cinco gomos cortados na borda,
    sombra embaixo à direita e reflexo no alto à esquerda."""
    g = _grid(size, size)
    c = (size - 1) / 2
    r = size / 2 - 0.6

    def pentagon(px, py, x, y, radius, turn):
        # ponto dentro de um pentágono regular (centro px, py) pela distância às 5 arestas
        dx, dy = x - px, y - py
        for k in range(5):
            a = turn + 2 * math.pi * k / 5
            if dx * math.cos(a) + dy * math.sin(a) > radius * math.cos(math.pi / 5):
                return False
        return True

    for y in range(size):
        for x in range(size):
            if (x - c) ** 2 + (y - c) ** 2 > r * r:
                continue
            g[y][x] = "q" if (x - c) * 0.6 + (y - c) * 0.8 > 2.6 else "W"
            if pentagon(c, c, x, y, 2.6, -math.pi / 2):
                g[y][x] = "s"
            for k in range(5):
                a = -math.pi / 2 + math.pi / 5 + 2 * math.pi * k / 5
                if pentagon(c + 6.6 * math.cos(a), c + 6.6 * math.sin(a), x, y, 2.4, a + math.pi):
                    g[y][x] = "s"
    for x, y in ((4, 3), (3, 4), (4, 4)):
        if g[y][x] == "W":
            g[y][x] = "w"
    return ["".join(row) for row in _outline(g, "o")]


def vine_tile(width=24, height=13):
    """Caule de roseira: 3 pixels de espessura (brilho, meio e sombra), ondulando de leve, com espinhos
    em triângulo cheio (base larga no caule, ponta fina inclinada para a frente), alternando cima e baixo."""
    g = _grid(width, height)
    mid = height // 2
    center = [mid + int(round(0.9 * math.sin(2 * math.pi * x / width))) for x in range(width)]
    for x, y in enumerate(center):
        g[y - 1][x] = "l"
        g[y][x] = "b"
        g[y + 1][x] = "d"

    def thorn(x0, up):
        y = center[x0]
        rows = [(4, "m"), (3, "b"), (2, "b"), (1, "l")]  # largura de cada degrau, da base para a ponta
        for i, (span, c) in enumerate(rows):
            yy = y - 2 - i if up else y + 2 + i
            for dx in range(span):
                xx = x0 + i + dx  # cada degrau anda um pixel para a frente: o espinho inclina
                if 0 <= yy < height and 0 <= xx < width:
                    g[yy][xx] = c if up else ("m" if c == "l" else c)
        tip_y = y - 6 if up else y + 6
        if 0 <= tip_y < height and x0 + 4 < width:
            g[tip_y][x0 + 4] = "h"

    thorn(3, up=True)
    thorn(15, up=False)
    return ["".join(r) for r in g]


if __name__ == "__main__":
    print("\n".join(rose()))
