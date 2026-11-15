#!/usr/bin/env python3
"""Disena el dragon 16x16 (2x2 sprites, 2 fotogramas) y genera el C.

Uso:
  python tools/gen_dragon.py preview
  python tools/gen_dragon.py c
"""
import sys
from PIL import Image

# '.'=0 transparente, '#'=color1 (rojo/verde/oro), '+'=color2 (sombra),
# '@'=color3 (blanco: ojos, dientes, cuernos, garras)
FRAME_A = [
    "@..............@",
    "@@............@@",
    ".@@..........@@.",
    "..@@........@@..",
    "..@##......##@..",
    ".@####++++####@.",
    ".@##@@####@@##@.",
    ".@##@+####+@##@.",
    ".@###########@..",
    "..@##@@@@@@##@..",
    "..@#@@++++@@#@..",
    "..@##++++++##@..",
    "...@########@...",
    "...@##@@@@##@...",
    "....@######@....",
    "....@#....#@....",
]

FRAME_B = [
    "................",
    "@..............@",
    "@@............@@",
    ".@@..........@@.",
    "..@##......##@..",
    ".@####++++####@.",
    ".@##@@####@@##@.",
    ".@##@+####+@##@.",
    ".@###########@..",
    "..@##++++++##@..",
    "..@####@@####@..",
    "..@#++++++++#@..",
    "...@########@...",
    "...@##@@@@##@...",
    "....@######@....",
    "....@#....#@....",
]

COLORS = {
    ".": (0, 0, 0, 0),
    "#": (220, 30, 30, 255),
    "+": (150, 20, 20, 255),
    "@": (255, 255, 255, 255),
}


def check(grid, name):
    if len(grid) != 16:
        raise SystemExit(f"{name}: {len(grid)} filas (deben ser 16)")
    for i, row in enumerate(grid):
        if len(row) != 16:
            raise SystemExit(f"{name} fila {i}: {len(row)} cols -> {row!r}")


def quadrant(grid, qx, qy):
    return [grid[qy * 8 + y][qx * 8:qx * 8 + 8] for y in range(8)]


def plane_rows(quad):
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
    grids = [("FRAME_A", FRAME_A), ("FRAME_B", FRAME_B)]
    for name, g in grids:
        check(g, name)

    if len(sys.argv) > 1 and sys.argv[1] == "c":
        for name, g in grids:
            print(f"    /* {name} */")
            for qy in range(2):
                for qx in range(2):
                    p0, p1 = plane_rows(quadrant(g, qx, qy))
                    a = ",".join(f"0x{v:02X}" for v in p0)
                    b = ",".join(f"0x{v:02X}" for v in p1)
                    print(f"    {{ {{{a}}}, {{{b}}} }},")
        return 0

    scale = 10
    imgs = [render(g, scale) for _, g in grids]
    gap = 24
    w = sum(i.width for i in imgs) + gap
    h = imgs[0].height
    out = Image.new("RGBA", (w, h), (30, 30, 40, 255))
    x = 0
    for im in imgs:
        out.paste(im, (x, 0), im)
        x += im.width + gap
    out.save("tools/dragon_preview.png")
    print("tools/dragon_preview.png", out.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
