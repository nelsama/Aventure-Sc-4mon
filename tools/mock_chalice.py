#!/usr/bin/env python3
"""Opciones para el sprite del caliz (8x8, patron de sprite 0).

Fondo: suelo real de la sala 2 (T_CFLOOR, paleta 2), donde empieza el caliz.
Uso: python tools/mock_chalice.py
Salida: doc/chalice_options.png
"""
from PIL import Image, ImageDraw
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_hole import PAL, tile_from_record, font, GRAF  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "doc", "chalice_options.png")

SCALE = 10
PANEL = 24  # 24x24 px de suelo alrededor del sprite
OFF = 8
FLOOR_REC = 2
FLOOR_PAL = 2

# Paleta de sprite 1 real (spr_pal[1]): 0 transparente, 1 dorado, 2 marron, 3 blanco
SPR_PAL = [(0, 0, 0), (0xFF, 0xCC, 0x00), (0x99, 0x55, 0x00), (0xFF, 0xFF, 0xFF)]

# '.' = transparente   1 = dorado   2 = marron   3 = blanco
ACTUAL = [
    "..1..1..",
    "..1111..",
    "..1111..",
    "...11...",
    "..1111..",
    ".111111.",
    ".111111.",
    ".111111.",
]

A_CLASSIC = [
    ".333333.",
    ".311113.",
    ".311113.",
    "..1111..",
    "...11...",
    "...11...",
    "..3333..",
    "........",
]

B_WIDE = [
    ".333333.",
    ".311113.",
    ".311113.",
    ".311113.",
    "..3333..",
    "...11...",
    "..3333..",
    "........",
]

C_HANDLES = [
    "3.3333.3",
    "31311313",
    "31311313",
    ".311113.",
    "..1111..",
    "...11...",
    "..3333..",
    "........",
]

D_JEWEL = [
    ".333333.",
    ".311113.",
    ".313113.",
    ".311113.",
    "..1111..",
    "...11...",
    "..3333..",
    "........",
]

E_TALL = [
    ".333333.",
    ".311113.",
    ".311113.",
    "..1111..",
    "...11...",
    "...11...",
    "...11...",
    "..3333..",
]

F_GRAIL = [
    ".333333.",
    ".311113.",
    ".311113.",
    ".311113.",
    "..3113..",
    "...11...",
    ".333333.",
    "........",
]

OPTIONS = [
    ("A", "Caliz clasico", A_CLASSIC),
    ("B", "Copa ancha", B_WIDE),
    ("C", "Con asas", C_HANDLES),
    ("D", "Enjoyado", D_JEWEL),
    ("E", "Caliz alto", E_TALL),
    ("F", "Grial", F_GRAIL),
]


def sprite_image(rows):
    im = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(rows):
        assert len(row) == 8, f"fila {y} mide {len(row)}"
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            px[x, y] = SPR_PAL[int(ch)] + (255,)
    return im


def encode_sprite(rows):
    """Codifica un sprite 8x8 en 2 planos (16 B), formato GRAF.DAT."""
    p0 = [0] * 8
    p1 = [0] * 8
    for y in range(8):
        for x in range(8):
            ch = rows[y][x]
            idx = 0 if ch == "." else int(ch)
            bit = 7 - x
            if idx & 1:
                p0[y] |= 1 << bit
            if idx & 2:
                p1[y] |= 1 << bit
    return bytes(p0 + p1)


def write_graf():
    """Reemplaza el patron de sprite 0 (caliz) por la opcion C (con asas)."""
    data = bytearray(open(GRAF, "rb").read())
    n_bg = len(data) // 16 - 41
    if n_bg < 22:
        raise SystemExit("GRAF.DAT sin los tiles de fondo esperados")
    off = n_bg * 16          # primer registro de sprite (patron 0)
    rec = encode_sprite(C_HANDLES)
    assert len(rec) == 16
    data[off:off + 16] = rec
    open(GRAF, "wb").write(data)
    print(f"{GRAF}: caliz 'con asas' escrito en el patron de sprite 0")


def make_panel(rows, floor, chosen=False):
    bg = Image.new("RGB", (PANEL, PANEL))
    for ty in range(PANEL // 8):
        for tx in range(PANEL // 8):
            bg.paste(floor, (tx * 8, ty * 8))
    bg.paste(sprite_image(rows), (OFF, OFF), sprite_image(rows))
    im = bg.resize((PANEL * SCALE, PANEL * SCALE), Image.NEAREST)
    return im


def main():
    data = open(GRAF, "rb").read()
    floor = tile_from_record(data[FLOOR_REC * 16:FLOOR_REC * 16 + 16], FLOOR_PAL)

    margin, gap = 24, 20
    panel = PANEL * SCALE
    cols, rows_n = 4, 2
    width = margin * 2 + panel * cols + gap * (cols - 1)
    height = 90 + rows_n * (panel + 46) + 80
    im = Image.new("RGB", (width, height), (20, 20, 30))
    d = ImageDraw.Draw(im)
    f_title, f_sub = font(24), font(15)
    f_label, f_small = font(17), font(12)

    d.text((margin, 16),
           "OPCIONES DE CALIZ  (sprite 8x8, paleta 1)",
           font=f_title, fill=(240, 220, 140))
    d.text((margin, 48),
           "Fondo: suelo real de la Sala 2. El caliz se dibuja encima.",
           font=f_sub, fill=(190, 190, 205))

    items = [("ANTES", "Anterior", ACTUAL, True)] + \
            [(l, n, r, False) for l, n, r in OPTIONS]

    for idx, (letter, name, rows, is_actual) in enumerate(items):
        cx = idx % cols
        cy = idx // cols
        x = margin + cx * (panel + gap)
        y = 84 + cy * (panel + 46)
        im.paste(make_panel(rows, floor, is_actual), (x, y))
        elegida = letter == "C"
        outline = (80, 210, 120) if elegida else (
            (220, 90, 90) if is_actual else (70, 70, 95))
        d.rectangle([x - 1, y - 1, x + panel, y + panel], outline=outline,
                    width=2 if (elegida or is_actual) else 1)
        if elegida:
            color = (120, 240, 150)
        elif is_actual:
            color = (240, 140, 140)
        else:
            color = (235, 235, 245)
        sufijo = "  (elegida)" if elegida else ""
        d.text((x, y + panel + 6), f"{letter}. {name}{sufijo}", font=f_label,
               fill=color)
        d.text((x, y + panel + 25), "8x8", font=f_small, fill=(160, 160, 180))

    footer_y = 84 + rows_n * (panel + 46) + 6
    d.text((margin, footer_y),
           "ELEGIDA: C (con asas) para el caliz.",
           font=f_sub, fill=(150, 235, 160))
    d.text((margin, footer_y + 24),
           "Cambiar el caliz no cuesta RAM: es 1 patron de sprite en GRAF.DAT.",
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
