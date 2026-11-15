#!/usr/bin/env python3
"""Disena el sprite 16x16 del jugador (4x8x8) y genera el C.

Uso:
  python tools/gen_player.py preview   -> tools/player_preview.png
  python tools/gen_player.py c         -> imprime el inicializador C
"""
import sys
from PIL import Image

# Color: '.'=0 transparente, '#'=1 blanco, '+'=2 gris, '@'=3 negro
DOWN = [
    "......@@@@......",
    "....@@####@@....",
    "...@##++++##@...",
    "..@###++++###@..",
    "..@#++####++#@..",
    "..@#@######@#@..",
    "..@###++++###@..",
    "...@##++++##@...",
    "...@#++++++#@...",
    "..@@@######@@@..",
    "..@##@####@##@..",
    "..@##@#++#@##@..",
    "..@##@####@##@..",
    "...@@######@@...",
    "....@##@@##@....",
    "....@##@@##@....",
]

UP = [
    "......@@@@......",
    "....@@####@@....",
    "...@##++++##@...",
    "..@###++++###@..",
    "..@##++++++##@..",
    "..@##++++++##@..",
    "..@###++++###@..",
    "...@##++++##@...",
    "...@#++++++#@...",
    "..@@@######@@@..",
    "..@##@####@##@..",
    "..@##@####@##@..",
    "..@##@####@##@..",
    "...@@######@@...",
    "....@##@@##@....",
    "....@##@@##@....",
]

LEFT = [
    ".....@@@@@@.....",
    "...@@######@@...",
    "..@##########@..",
    "..@#++++++###@..",
    ".@##@########@..",
    ".@###########@..",
    "..@##########@..",
    "..@#++++++++#@..",
    "..@##@####@##@..",
    "..@##@####@##@..",
    "..@##@#++#@##@..",
    "..@##@####@##@..",
    "...@@######@@...",
    "....@##@@##@....",
    "....@##@@##@....",
    ".....@@@@@@.....",
]

COLORS = {
    ".": (0, 0, 0, 0),
    "#": (255, 255, 255, 255),
    "+": (150, 150, 160, 255),
    "@": (20, 20, 20, 255),
}


def check(grid, name):
    if len(grid) != 16:
        raise SystemExit(f"{name}: {len(grid)} filas (deben ser 16)")
    for i, row in enumerate(grid):
        if len(row) != 16:
            raise SystemExit(f"{name} fila {i}: {len(row)} cols -> {row!r}")


def mirror(grid):
    return [row[::-1] for row in grid]


def quadrant(grid, qx, qy):
    out = []
    for y in range(8):
        out.append(grid[qy * 8 + y][qx * 8:qx * 8 + 8])
    return out


def plane_rows(quad):
    """Devuelve (plan0, plan1) como listas de 8 bytes."""
    p0, p1 = [], []
    for row in quad:
        b0 = b1 = 0
        for x, ch in enumerate(row):
            c = {".": 0, "#": 1, "+": 2, "@": 3}[ch]
            if c & 1:
                b0 |= 0x80 >> x
            if c & 2:
                b1 |= 0x80 >> x
        p0.append(b0)
        p1.append(b1)
    return p0, p1


def render(grid, scale=10):
    img = Image.new("RGBA", (16, 16), (30, 30, 40, 255))
    px = img.load()
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            px[x, y] = COLORS[ch]
    return img.resize((16 * scale, 16 * scale), Image.NEAREST)


def main():
    grids = {"DOWN": DOWN, "UP": UP, "LEFT": LEFT, "RIGHT": mirror(LEFT)}
    for name, g in grids.items():
        check(g, name)

    if len(sys.argv) > 1 and sys.argv[1] == "c":
        order = ["DOWN", "UP", "LEFT", "RIGHT"]
        for name in order:
            g = grids[name]
            print(f"    /* {name} */")
            for qy in range(2):
                for qx in range(2):
                    quad = quadrant(g, qx, qy)
                    p0, p1 = plane_rows(quad)
                    a = ",".join(f"0x{v:02X}" for v in p0)
                    b = ",".join(f"0x{v:02X}" for v in p1)
                    print(f"    {{ {{{a}}}, {{{b}}} }},")
        return 0

    # preview
    scale = 10
    imgs = [render(grids[n], scale) for n in ["DOWN", "UP", "LEFT", "RIGHT"]]
    gap = 20
    w = sum(i.width for i in imgs) + gap * 3
    h = imgs[0].height
    out = Image.new("RGBA", (w, h), (30, 30, 40, 255))
    x = 0
    for im in imgs:
        out.paste(im, (x, 0), im)
        x += im.width + gap
    out.save("tools/player_preview.png")
    print("tools/player_preview.png", out.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
