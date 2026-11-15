#!/usr/bin/env python3
"""Opciones de arbusto 8x8 para las islas del bosque.

Cada opcion se muestra como isla 3x3 sobre un campo de cesped 5x5.
Salida: doc/bush_options.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

# Paleta del bosque (BG0)
BG   = (5, 5, 5, 255)
C1   = (0, 170, 68, 255)    # verde
C2   = (0, 85, 34, 255)     # verde oscuro
C3   = (255, 255, 255, 255) # blanco
PAL  = {0: BG, 1: C1, 2: C2, 3: C3}

# Patron de cesped 0x80 (plan0, plan1)
GRASS_P0 = [0x00, 0x00, 0x20, 0x00, 0x02, 0x00, 0x08, 0x00]
GRASS_P1 = [0xFF, 0xFF, 0xDF, 0xFF, 0xFD, 0xFF, 0xF7, 0xFF]

# '.'=0, '#'=1 verde, '+'=2 verde oscuro, '@'=3 blanco
A = [  # original (oval con borde oscuro)
    "+++##+++",
    "++####++",
    "+######+",
    "########",
    "########",
    "########",
    "+######+",
    "++####++",
]
B = [  # redondo liso
    "..####..",
    ".######.",
    "########",
    "########",
    "########",
    ".######.",
    "..####..",
    "........",
]
C = [  # con flores blancas
    "..####..",
    ".#@##@#.",
    "###@@###",
    "########",
    "########",
    ".#@##@#.",
    "..####..",
    "........",
]
D = [  # seto alto
    ".######.",
    "########",
    "##@##@##",
    "########",
    "########",
    "###@@###",
    ".######.",
    "..####..",
]
E = [  # matas de hierba
    "........",
    ".#..#.#.",
    ".##.##..",
    ".#.###..",
    ".##.##..",
    "..####..",
    "........",
    "........",
]
F = [  # bayas
    "..####..",
    ".#@##@#.",
    "########",
    "##@##@##",
    "########",
    ".#@##@#.",
    "..####..",
    "........",
]
G = [  # frondoso con textura
    ".+####+.",
    "##+##+##",
    "########",
    "##+##+##",
    "########",
    "##+##+##",
    ".+####+.",
    "........",
]

OPTIONS = [
    ("1 ORIGINAL", A),
    ("2 REDONDO", B),
    ("3 FLORES", C),
    ("4 SETO", D),
    ("5 HIERBA", E),
    ("6 BAYAS", F),
    ("7 FRONDOSO", G),
]


def check(g, name):
    if len(g) != 8:
        raise SystemExit(f"{name}: {len(g)} filas")
    for i, row in enumerate(g):
        if len(row) != 8:
            raise SystemExit(f"{name} fila {i}: {len(row)} -> {row!r}")


def draw_tile(img, x, y, scale, grid):
    px = img.load()
    for yy in range(8):
        for xx in range(8):
            ch = grid[yy][xx]
            c = {".": 0, "#": 1, "+": 2, "@": 3}[ch]
            col = PAL[c]
            for dy in range(scale):
                for dx in range(scale):
                    px[x + xx * scale + dx, y + yy * scale + dy] = col


def draw_grass(img, x, y, scale):
    px = img.load()
    for ty in range(5):
        for tx in range(5):
            for yy in range(8):
                p0 = GRASS_P0[yy]
                p1 = GRASS_P1[yy]
                for xx in range(8):
                    c = (((p1 >> (7 - xx)) & 1) << 1) | ((p0 >> (7 - xx)) & 1)
                    col = PAL[c]
                    for dy in range(scale):
                        for dx in range(scale):
                            px[x + (tx * 8 + xx) * scale + dx,
                               y + (ty * 8 + yy) * scale + dy] = col


def draw_island(img, x, y, scale, grid):
    # 3x3 isla centrada en el campo 5x5
    for ty in range(3):
        for tx in range(3):
            draw_tile(img, x + (1 + tx) * 8 * scale,
                      y + (1 + ty) * 8 * scale, scale, grid)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def main():
    for name, g in OPTIONS:
        check(g, name)
    scale = 6
    field = 5 * 8 * scale
    gap = 22
    margin = 24
    n = len(OPTIONS)
    w = margin * 2 + n * field + (n - 1) * gap
    h = margin * 2 + 50 + field + 34
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((margin, 12), "OPCIONES DE ARBUSTO (isla 3x3 sobre cesped)",
           font=font(22), fill=(240, 220, 140, 255))
    for i, (name, grid) in enumerate(OPTIONS):
        x = margin + i * (field + gap)
        y = margin + 44
        draw_grass(img, x, y, scale)
        draw_island(img, x, y, scale, grid)
        d.rectangle([x - 1, y - 1, x + field, y + field],
                    outline=(80, 80, 110, 255))
        d.text((x, y + field + 6), name, font=font(15),
               fill=(225, 225, 235, 255))
    img.save("doc/bush_options.png")
    print("doc/bush_options.png", img.size)


if __name__ == "__main__":
    sys.exit(main())
