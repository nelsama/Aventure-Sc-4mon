#!/usr/bin/env python3
"""Opciones de pedestal/altar del caliz en VISTA DE PERFIL (16x16 = 4 tiles).

El fondo de cada tile es el patron real del suelo del Castillo de Oro
(T_CFLOOR, registro 2, paleta 1), asi el altar no queda dentro de un cuadrado.
Uso: python tools/mock_pedestal.py
Salida: doc/pedestal_options.png
"""
from PIL import Image, ImageDraw
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_hole import PAL, tile_from_record, font, GRAF, char_index  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "pedestal_options.png")
SCALE = 8
BG_TILES = 5
OFF = 12

FLOOR_REC = 2
FLOOR_PAL = 1

# Patron 8x8 del suelo T_CFLOOR tal como sale en GRAF.DAT (2=madera, 0=junta)
FLOOR = [
    "22222222",
    "22222222",
    "00000000",
    "22222222",
    "22222222",
    "00000000",
    "22222222",
    "22222222",
]

# ---------------------------------------------------------------------------
# Disenos de perfil.  '.' = fondo (suelo)   1=dorado   2=marron   3=blanco
# ---------------------------------------------------------------------------

# A: pedestal clasico (tapa ancha, columna, base)
A_PEDESTAL = [
    "................",
    "................",
    "................",
    ".33333333333333.",
    ".11111111111111.",
    ".22222222222222.",
    ".....311112.....",
    ".....311112.....",
    ".....311112.....",
    ".....311112.....",
    ".....311112.....",
    ".....311112.....",
    ".....311112.....",
    "...3333333333...",
    "...1111111111...",
    "...2222222222...",
]

# B: altar macizo (bloque con tapa y base)
B_BLOCK = [
    "................",
    "................",
    "................",
    ".33333333333333.",
    ".11111111111111.",
    ".22222222222222.",
    "...3111111112...",
    "...3111111112...",
    "...3111111112...",
    "...3111111112...",
    "...3111111112...",
    "...3111111112...",
    "...3111111112...",
    "...3333333333...",
    "...1111111111...",
    "...2222222222...",
]

# C: mesa/altar de patas
C_TABLE = [
    "................",
    "................",
    "................",
    ".33333333333333.",
    ".11111111111111.",
    ".22222222222222.",
    "..12........12..",
    "..12........12..",
    "..12........12..",
    "..12........12..",
    "..333333333333..",
    "..111111111111..",
    "..12........12..",
    "..12........12..",
    "..12........12..",
    "..22........22..",
]

# D: altar escalonado (tres niveles, de perfil)
D_STEPS = [
    "................",
    "................",
    "................",
    ".....333333.....",
    ".....111111.....",
    ".....111111.....",
    ".....222222.....",
    "...3333333333...",
    "...1111111111...",
    "...1111111111...",
    "...2222222222...",
    ".33333333333333.",
    ".11111111111111.",
    ".11111111111111.",
    ".22222222222222.",
    "................",
]

OPTIONS = [
    ("A", "Pedestal clasico", A_PEDESTAL),
    ("B", "Altar macizo", B_BLOCK),
    ("C", "Mesa de patas", C_TABLE),
    ("D", "Altar escalonado", D_STEPS),
]


def compose(rows):
    """Mezcla el diseno sobre el patron del suelo: '.' conserva el fondo."""
    grid = [[int(FLOOR[y % 8][x % 8]) for x in range(16)] for y in range(16)]
    for y, row in enumerate(rows):
        assert len(row) == 16, f"fila {y} mide {len(row)}"
        for x, ch in enumerate(row):
            if ch != ".":
                grid[y][x] = char_index(ch)
    return grid


def grid_to_image(grid, pal):
    colors = PAL[pal]
    im = Image.new("RGB", (16, 16))
    px = im.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = colors[grid[y][x]]
    return im


def make_panel(rows, floor):
    bg = Image.new("RGB", (40, 40))
    for ty in range(BG_TILES):
        for tx in range(BG_TILES):
            bg.paste(floor, (tx * 8, ty * 8))
    bg.paste(grid_to_image(compose(rows), FLOOR_PAL), (OFF, OFF))
    return bg.resize((40 * SCALE, 40 * SCALE), Image.NEAREST)


def encode_tile(grid, ox, oy):
    """Codifica un tile 8x8 del grid en formato GRAF.DAT (plano0 + plano1)."""
    p0 = [0] * 8
    p1 = [0] * 8
    for y in range(8):
        for x in range(8):
            idx = grid[oy + y][ox + x]
            bit = 7 - x
            if idx & 1:
                p0[y] |= 1 << bit
            if idx & 2:
                p1[y] |= 1 << bit
    return bytes(p0 + p1)


def write_graf():
    """Anade los 4 tiles de la mesa (opcion C) a assets/GRAF.DAT.

    Deja el fichero como [10 fondo base][4 hoyo][4 escalera][4 mesa][41 sprites].
    Es idempotente. Requiere que el hoyo y la escalera ya esten insertados.
    """
    data = open(GRAF, "rb").read()
    n_bg = len(data) // 16 - 41
    if n_bg < 18:
        raise SystemExit("GRAF.DAT sin hoyo/escalera: ejecuta antes "
                         "python tools/mock_hole.py --write-graf")

    base = data[:160]
    hole_stairs = data[160:160 + 128]
    spr = data[n_bg * 16:]
    grid = compose(C_TABLE)
    altar = b"".join(encode_tile(grid, ox, oy)
                     for oy in (0, 8) for ox in (0, 8))
    assert len(altar) == 64
    out = base + hole_stairs + altar + spr
    open(GRAF, "wb").write(out)
    print(f"{GRAF}: {len(out)} bytes (mesa insertada en 0x92-0x95)")


def main():
    data = open(GRAF, "rb").read()
    floor = tile_from_record(data[FLOOR_REC * 16:FLOOR_REC * 16 + 16], FLOOR_PAL)

    margin, gap = 24, 24
    panel = 40 * SCALE
    width = margin * 2 + panel * 4 + gap * 3
    height = 560
    im = Image.new("RGB", (width, height), (20, 20, 30))
    d = ImageDraw.Draw(im)
    f_title, f_sub = font(24), font(15)
    f_label, f_small = font(17), font(13)

    d.text((margin, 16),
           "PEDESTAL / ALTAR DEL CALIZ - VISTA DE PERFIL (16x16 = 4 tiles)",
           font=f_title, fill=(240, 220, 140))
    d.text((margin, 48),
           "Fondo: suelo real del castillo; el altar se dibuja encima del patron.",
           font=f_sub, fill=(190, 190, 205))

    for i, (letter, name, rows) in enumerate(OPTIONS):
        x = margin + i * (panel + gap)
        y = 84
        im.paste(make_panel(rows, floor), (x, y))
        elegida = letter == "C"
        outline = (80, 210, 120) if elegida else (70, 70, 95)
        d.rectangle([x - 1, y - 1, x + panel, y + panel], outline=outline,
                    width=2 if elegida else 1)
        color = (120, 240, 150) if elegida else (235, 235, 245)
        sufijo = "  (elegida)" if elegida else ""
        d.text((x, y + panel + 10), f"{letter}. {name}{sufijo}", font=f_label,
               fill=color)
        d.text((x, y + panel + 32), "perfil, paleta 1", font=f_small,
               fill=(160, 160, 180))

    footer_y = 84 + panel + 70
    d.text((margin, footer_y),
           "ELEGIDA: C (mesa de patas) para el altar del caliz.",
           font=f_sub, fill=(150, 235, 160))
    d.text((margin, footer_y + 24),
           "Cada opcion: 4 patrones = 64 B en GRAF.DAT y 0 B de RAM.",
           font=f_sub, fill=(160, 220, 170))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT)
    print(OUT)


if __name__ == "__main__":
    import sys
    if "--write-graf" in sys.argv:
        write_graf()
    else:
        main()
