#!/usr/bin/env python3
"""Opciones de sprites 8x8 para espada, iman y puente.

Salida: doc/item_options.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

# Paletas reales del juego
P_SWORD = {".": (0, 0, 0, 0), "#": (255, 204, 0, 255),
           "+": (153, 85, 0, 255), "@": (255, 255, 255, 255)}
P_MAGNET = {".": (0, 0, 0, 0), "#": (255, 0, 0, 255),
            "+": (255, 136, 0, 255), "@": (255, 255, 255, 255)}
P_BRIDGE = {".": (0, 0, 0, 0), "#": (255, 204, 0, 255),
            "+": (153, 85, 0, 255), "@": (255, 255, 255, 255)}

SWORDS = [
    ("1 VERTICAL", [
        "...@@...",
        "...@@...",
        "...@@...",
        "...@@...",
        "...@@...",
        "..####..",
        "...##...",
        "...##...",
    ]),
    ("2 DIAGONAL", [
        "......@@",
        ".....@@.",
        "....@@..",
        "...@@...",
        "..@@....",
        ".####...",
        "..##....",
        "..#.....",
    ]),
    ("3 ANCHA", [
        "..@@@@..",
        "..@@@@..",
        "..@@@@..",
        "..@@@@..",
        "..@@@@..",
        ".######.",
        "..####..",
        "...##...",
    ]),
    ("4 SABLE", [
        ".....@@.",
        "....@@..",
        "...@@...",
        "..@@....",
        ".@@.....",
        ".#@.....",
        "###.....",
        "#.......",
    ]),
    ("5 DAGA", [
        "...@@...",
        "...@@...",
        "...@@...",
        "..####..",
        "...##...",
        "...##...",
        "........",
        "........",
    ]),
]

MAGNETS = [
    ("1 HERRADURA", [
        ".@@..@@.",
        ".##..##.",
        ".##..##.",
        ".##..##.",
        ".##..##.",
        ".######.",
        ".######.",
        "........",
    ]),
    ("2 HERRADURA 2", [
        ".######.",
        ".######.",
        ".##..##.",
        ".##..##.",
        ".##..##.",
        ".##..##.",
        ".@@..@@.",
        "........",
    ]),
    ("3 BARRA", [
        "........",
        ".######.",
        ".#@@@@#.",
        ".#@@@@#.",
        ".#@@@@#.",
        ".######.",
        "........",
        "........",
    ]),
    ("4 BOBINA", [
        "..####..",
        ".#@@@@#.",
        ".#@@@@#.",
        ".#@@@@#.",
        "..####..",
        "...##...",
        "...##...",
        "...##...",
    ]),
    ("5 DOBLE", [
        ".##..##.",
        ".##..##.",
        ".######.",
        ".######.",
        ".##..##.",
        ".##..##.",
        ".@@..@@.",
        "........",
    ]),
]

BRIDGES = [
    ("1 TABLONES", [
        "@......@",
        "@######@",
        "@++++++@",
        "@######@",
        "@++++++@",
        "@######@",
        "@......@",
        "........",
    ]),
    ("2 MADERA", [
        "@......@",
        "@++++++@",
        "@++++++@",
        "@++++++@",
        "@++++++@",
        "@++++++@",
        "@......@",
        "........",
    ]),
    ("3 CUERDAS", [
        "@......@",
        ".######.",
        ".######.",
        ".######.",
        ".######.",
        ".######.",
        "@......@",
        "........",
    ]),
    ("4 PIEDRA", [
        "........",
        "@@@@@@@@",
        "########",
        "########",
        "########",
        "++++++++",
        "++++++++",
        "........",
    ]),
    ("5 SIMPLE", [
        "........",
        "@@@@@@@@",
        "++++++++",
        "++++++++",
        "++++++++",
        "@@@@@@@@",
        "........",
        "........",
    ]),
]


def check(g, name):
    if len(g) != 8:
        raise SystemExit(f"{name}: {len(g)} filas")
    for i, row in enumerate(g):
        if len(row) != 8:
            raise SystemExit(f"{name} fila {i}: {len(row)} -> {row!r}")


def render(grid, pal, scale=10):
    img = Image.new("RGBA", (16, 16), (40, 40, 55, 255))
    px = img.load()
    for y in range(8):
        for x in range(8):
            ch = grid[y][x]
            if ch == ".":
                continue
            col = pal[ch]
            for dy in range(2):
                for dx in range(2):
                    px[x * 2 + dx, y * 2 + dy] = col
    return img.resize((16 * scale, 16 * scale), Image.NEAREST)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def main():
    palette = {"SWORDS": P_SWORD, "MAGNETS": P_MAGNET, "BRIDGES": P_BRIDGE}
    rows = [("ESPADA", SWORDS, P_SWORD), ("IMAN", MAGNETS, P_MAGNET),
            ("PUENTE", BRIDGES, P_BRIDGE)]
    for title, opts, _ in rows:
        for name, g in opts:
            check(g, f"{title} {name}")
    scale = 10
    cell = 16 * scale
    gap = 14
    label_w = 90
    margin = 22
    n = 5
    w = margin * 2 + label_w + n * (cell + gap)
    h = margin * 2 + 50 + len(rows) * (cell + 30)
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((margin, 12), "OPCIONES DE OBJETOS (sprites 8x8)",
           font=font(22), fill=(240, 220, 140, 255))
    for ri, (title, opts, pal) in enumerate(rows):
        y = margin + 44 + ri * (cell + 30)
        d.text((margin, y + cell // 2 - 10), title, font=font(18),
               fill=(240, 220, 140, 255))
        for ci, (name, grid) in enumerate(opts):
            x = margin + label_w + ci * (cell + gap)
            spr = render(grid, pal, scale)
            d.rectangle([x - 1, y - 1, x + cell, y + cell],
                        outline=(80, 80, 110, 255))
            img.paste(spr, (x, y), spr)
            d.text((x, y + cell + 3), name, font=font(13),
                   fill=(225, 225, 235, 255))
    img.save("doc/item_options.png")
    print("doc/item_options.png", img.size)


if __name__ == "__main__":
    sys.exit(main())
