#!/usr/bin/env python3
"""Opciones de tile de escaleras (8x8) para las catacumbas.

Cada opcion se muestra como bloque 2x2 sobre un campo 5x5 del suelo.
Salida: doc/stairs_options.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

# Paleta BG2 (catacumbas): 0=fondo, 1=azul, 2=azul oscuro, 3=blanco
BG  = (5, 5, 5, 255)
C1  = (0x33, 0x66, 0xAA, 255)
C2  = (0x11, 0x22, 0x44, 255)
C3  = (255, 255, 255, 255)
PAL = {0: BG, 1: C1, 2: C2, 3: C3}

# Suelo de catacumbas 0x84
FLOOR_P0 = [0x00, 0x00, 0x22, 0x00, 0x00, 0x00, 0x44, 0x00]
FLOOR_P1 = [0xFF, 0xFF, 0xDD, 0xFF, 0xFF, 0xFF, 0xBB, 0xFF]

# '.'=0, '#'=1 azul, '+'=2 azul oscuro, '@'=3 blanco
A = [  # peldaños clásicos
    "@@@@@@@@",
    "########",
    "++++++++",
    "++++++++",
    "@@@@@@@@",
    "########",
    "++++++++",
    "++++++++",
]
B = [  # peldaños 3D
    "@@######",
    "@#######",
    "########",
    "++++++++",
    "@@@@@@@@",
    "########",
    "++++++++",
    "++++++++",
]
C = [  # escalera de mano
    "@######@",
    "@#++++#@",
    "@######@",
    "@#++++#@",
    "@######@",
    "@#++++#@",
    "@######@",
    "@######@",
]
D = [  # con barandilla
    "@@######",
    "@@######",
    "##++++++",
    "##++++++",
    "@@######",
    "@@######",
    "##++++++",
    "##++++++",
]
E = [  # piedra irregular
    "@@@####+",
    "###++##+",
    "##++++++",
    "++++++++",
    "@@@####+",
    "###++##+",
    "##++++++",
    "++++++++",
]
F = [  # minimal (bandas)
    "@@@@@@@@",
    "++++++++",
    "++++++++",
    "@@@@@@@@",
    "++++++++",
    "++++++++",
    "@@@@@@@@",
    "++++++++",
]
G = [  # escalones con huella y contrahuella
    "++@@@@@@",
    "++######",
    "++######",
    "++++++++",
    "++@@@@@@",
    "++######",
    "++######",
    "++++++++",
]

OPTIONS = [
    ("1 CLASICA", A),
    ("2 3D", B),
    ("3 ESCALERA", C),
    ("4 BARANDILLA", D),
    ("5 PIEDRA", E),
    ("6 MINIMAL", F),
    ("7 HUELLA", G),
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
            c = {".": 0, "#": 1, "+": 2, "@": 3}[grid[yy][xx]]
            col = PAL[c]
            for dy in range(scale):
                for dx in range(scale):
                    px[x + xx * scale + dx, y + yy * scale + dy] = col


def draw_floor(img, x, y, scale):
    px = img.load()
    for ty in range(5):
        for tx in range(5):
            for yy in range(8):
                p0, p1 = FLOOR_P0[yy], FLOOR_P1[yy]
                for xx in range(8):
                    c = (((p1 >> (7 - xx)) & 1) << 1) | ((p0 >> (7 - xx)) & 1)
                    col = PAL[c]
                    for dy in range(scale):
                        for dx in range(scale):
                            px[x + (tx * 8 + xx) * scale + dx,
                               y + (ty * 8 + yy) * scale + dy] = col


def draw_stairs(img, x, y, scale, grid):
    # bloque 2x2 centrado en el campo 5x5
    for ty in range(2):
        for tx in range(2):
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
    d.text((margin, 12), "OPCIONES DE ESCALERAS (bloque 2x2 sobre suelo)",
           font=font(22), fill=(240, 220, 140, 255))
    for i, (name, grid) in enumerate(OPTIONS):
        x = margin + i * (field + gap)
        y = margin + 44
        draw_floor(img, x, y, scale)
        draw_stairs(img, x, y, scale, grid)
        d.rectangle([x - 1, y - 1, x + field, y + field],
                    outline=(80, 80, 110, 255))
        d.text((x, y + field + 6), name, font=font(15),
               fill=(225, 225, 235, 255))
    img.save("doc/stairs_options.png")
    print("doc/stairs_options.png", img.size)


if __name__ == "__main__":
    sys.exit(main())
