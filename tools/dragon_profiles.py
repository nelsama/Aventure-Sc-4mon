#!/usr/bin/env python3
"""Opciones de dragon 16x16 DE PERFIL (mirando a la derecha y volteado).

Salida: doc/dragon_profiles.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

# '.'=transparente, '#'=principal, '+'=secundario, '@'=blanco
P_RED = {".": (0, 0, 0, 0), "#": (220, 30, 30, 255),
         "+": (150, 20, 20, 255), "@": (250, 250, 250, 255)}
P_GREEN = {".": (0, 0, 0, 0), "#": (40, 210, 60, 255),
           "+": (20, 120, 40, 255), "@": (250, 250, 250, 255)}
P_GOLD = {".": (0, 0, 0, 0), "#": (235, 190, 30, 255),
          "+": (150, 105, 20, 255), "@": (250, 250, 250, 255)}

# Cada diseño mira a la DERECHA. Se voltea para mirar a la izquierda.
P1 = [  # Alado, cabeza alta
    "...........@....",
    "..........@@@...",
    ".........@###@..",
    "........@##@##@.",
    ".......@##@###@.",
    "......@##@####@.",
    ".....@##@@@@@@@.",
    "....@##@#@@#@@..",
    "...@##@##@@#@...",
    "..@##@###@#@....",
    ".@##@####@#@....",
    "@##@#####@#@....",
    "@#@@####@#@.....",
    "@@..@###@#@.....",
    "....@#@#@#......",
    "...@@@.@@@......",
]

P2 = [  # Serpiente alargada
    "..............@.",
    ".............@@@",
    "............@###",
    "...........@##@#",
    "..........@##@##",
    "........@##@####",
    ".......@##@@@@@@",
    "...@@@@@##@#@@..",
    "..@##@@##@#@....",
    ".@##@@##@#@.....",
    "@##@@##@#@......",
    "@#@@##@#@.......",
    "@@.@##@#@.......",
    "....@#@#@.......",
    "...@@@.@@.......",
    "................",
]

P3 = [  # Acorazado con púas
    ".....@.....@....",
    "....@@@...@@@...",
    "...@###@.@###@..",
    "..@##@##@##@##@.",
    "..@#@####@#@##@.",
    "..@##@@@@@###@@.",
    "..@#@@@#@@@#@@..",
    ".@##@##@#@#@....",
    "@##@####@#@.....",
    "@#@@####@#@.....",
    "@@..@###@#@.....",
    "....@#@#@#@.....",
    "....@#@.@#@.....",
    "...@@@...@@@....",
    "................",
    "................",
]

P4 = [  # Escupe fuego
    "...........@....",
    "..........@@@...",
    ".........@###@..",
    "........@##@##@.",
    ".......@##@###@.",
    "......@##@####@.",
    ".@...@@##@@@@@@@",
    "@@@.@##@#@@#@@..",
    ".@@@##@##@@#@...",
    "..@@##@###@#@...",
    "..@##@####@#@...",
    ".@##@#####@#@...",
    "@##@#####@#@....",
    "@#@@####@#@.....",
    "@@..@###@#@.....",
    "....@@@.@@@.....",
]

P5 = [  # Rechoncho, estilo Atari
    "................",
    "....@@@@@@......",
    "...@######@.....",
    "..@##@@@@##@....",
    "..@##@#@##@.....",
    "..@######@......",
    "...@####@.......",
    "..@##@@@@@@@....",
    ".@##@#######@...",
    "@##@#########@..",
    "@#@@########@...",
    "@@..@######@....",
    "....@##@@##@....",
    "....@#@.@#@.....",
    "...@@@...@@@....",
    "................",
]

DESIGNS = [
    ("A  ALADO", P1),
    ("B  SERPIENTE", P2),
    ("C  ACORAZADO", P3),
    ("D  FUEGO", P4),
    ("E  ATARI", P5),
]


def check(g, name):
    if len(g) != 16:
        raise SystemExit(f"{name}: {len(g)} filas")
    for i, row in enumerate(g):
        if len(row) != 16:
            raise SystemExit(f"{name} fila {i}: {len(row)} -> {row!r}")


def mirror(g):
    return [row[::-1] for row in g]


def render(g, pal, scale=8):
    img = Image.new("RGBA", (16, 16), (35, 35, 48, 255))
    px = img.load()
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            px[x, y] = pal[ch]
    return img.resize((16 * scale, 16 * scale), Image.NEAREST)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def main():
    for name, g in DESIGNS:
        check(g, name)
    scale = 9
    cell = 16 * scale
    gap = 16
    margin = 22
    n = len(DESIGNS)
    # 2 columnas por diseño (derecha / izquierda) -> 10 celdas
    cols = n * 2
    w = margin * 2 + cols * cell + (cols - 1) * gap
    h = margin * 2 + 46 + cell + 30
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((margin, 10), "DRAGONES DE PERFIL (derecha / izquierda)",
           font=font(24), fill=(240, 220, 140, 255))
    y = margin + 44
    for i, (name, g) in enumerate(DESIGNS):
        for j, (sub, grid) in enumerate([(">>", g), ("<<", mirror(g))]):
            x = margin + (i * 2 + j) * (cell + gap)
            d.rectangle([x - 2, y - 2, x + cell + 1, y + cell + 1],
                        outline=(80, 80, 110, 255))
            spr = render(grid, P_RED, scale)
            img.paste(spr, (x, y), spr)
            label = name if j == 0 else sub
            d.text((x, y + cell + 6), label if j == 0 else "",
                   font=font(15), fill=(225, 225, 235, 255))
    # etiquetas de las parejas debajo
    for i, (name, g) in enumerate(DESIGNS):
        x = margin + (i * 2) * (cell + gap)
        d.text((x, y + cell + 6), name, font=font(15),
               fill=(225, 225, 235, 255))
    img.save("doc/dragon_profiles.png")
    print("doc/dragon_profiles.png", img.size)

    # Extra: misma fila en verde y dorado para el diseño elegido luego.
    return 0


if __name__ == "__main__":
    sys.exit(main())
