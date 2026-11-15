#!/usr/bin/env python3
"""Dragones de perfil inspirados en Adventure (8x20 -> 16x16).

Salida: doc/dragon_profiles2.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

P_RED = {".": (0, 0, 0, 0), "#": (220, 30, 30, 255),
         "+": (150, 20, 20, 255), "@": (250, 250, 250, 255)}

# Todos miran a la IZQUIERDA; se voltean para la derecha.
S1 = [  # Caballito de mar (estilo Atari)
    "....@@@.........",
    "...@###@........",
    "..@##@##@.......",
    ".@##@####@......",
    ".@##@#####@.....",
    "..@##@####@.....",
    "...@##@###@.....",
    "....@##@##@.....",
    ".....@##@##@....",
    "....@##@####@...",
    "...@##@##@###@..",
    "..@##@#@@@##@...",
    ".@##@#@..@##@...",
    "@##@#@....@#@...",
    "@#@@......@@@...",
    "@@..............",
]

S2 = [  # Perfil horizontal, cabeza a la izquierda
    "................",
    "....@...........",
    "...@@@..........",
    "..@###@.........",
    ".@##@##@........",
    ".@##@###@.......",
    ".@##@#@@@@@.....",
    ".@##@@@#@@@.....",
    "..@##@##@.......",
    "...@##@#@.......",
    "..@##@####@.....",
    ".@##@#####@.....",
    "@##@#@@@##@.....",
    "@#@#@..@##@.....",
    "@@.@@...@@@.....",
    "................",
]

S3 = [  # Perfil con cuernos
    ".@...@..........",
    ".@@.@@@.........",
    "..@###@.........",
    ".@##@##@........",
    ".@##@###@.......",
    ".@##@#@@@@@.....",
    ".@##@@@#@@@.....",
    "..@##@##@.......",
    "...@##@##@......",
    "....@##@##@.....",
    "...@##@####@....",
    "..@##@######@...",
    ".@##@#@@@####@..",
    "@##@#@..@####@..",
    "@#@@....@##@....",
    "@@.......@@.....",
]

S4 = [  # Perfil acorazado con púas
    ".@..@..@..@.....",
    ".@@.@@.@@.@@....",
    "..@###@###@.....",
    ".@##@#####@.....",
    ".@##@#@@@@@.....",
    ".@##@@@#@@@.....",
    "..@##@##@.......",
    "...@##@##@......",
    "..@##@####@.....",
    ".@##@######@....",
    "@##@#@@@####@...",
    "@#@#@..@#####@..",
    "@@.@....@####@..",
    "........@##@....",
    "........@#@.....",
    "........@@......",
]

DESIGNS = [
    ("1 SEAHORSE", S1),
    ("2 PERFIL", S2),
    ("3 CUERNOS", S3),
    ("4 ACORAZADO", S4),
]


def check(g, name):
    if len(g) != 16:
        raise SystemExit(f"{name}: {len(g)} filas")
    for i, row in enumerate(g):
        if len(row) != 16:
            raise SystemExit(f"{name} fila {i}: {len(row)} -> {row!r}")


def mirror(g):
    return [row[::-1] for row in g]


def render(g, pal, scale=9):
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
    gap = 14
    margin = 22
    w = margin * 2 + 8 * cell + 7 * gap
    h = margin * 2 + 46 + cell + 30
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((margin, 10), "DRAGONES DE PERFIL  (izquierda / derecha)",
           font=font(23), fill=(240, 220, 140, 255))
    y = margin + 44
    for i, (name, g) in enumerate(DESIGNS):
        for j, grid in enumerate([g, mirror(g)]):
            x = margin + (i * 2 + j) * (cell + gap)
            d.rectangle([x - 2, y - 2, x + cell + 1, y + cell + 1],
                        outline=(80, 80, 110, 255))
            spr = render(grid, P_RED, scale)
            img.paste(spr, (x, y), spr)
        d.text((margin + i * 2 * (cell + gap), y + cell + 6), name,
               font=font(15), fill=(225, 225, 235, 255))
    img.save("doc/dragon_profiles2.png")
    print("doc/dragon_profiles2.png", img.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
