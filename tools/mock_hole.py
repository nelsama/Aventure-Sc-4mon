#!/usr/bin/env python3
"""Genera una hoja de opciones para el hoyo/escalera de 16x16 (4 tiles 8x8).

Lee T_GRASS de assets/AVENTUR.DAT para dibujar el fondo real del bosque y
compone cada opcion como una imagen de 2x2 celdas.

Uso: python tools/mock_hole.py
Salida: doc/hole_options.png
"""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAT = os.path.join(ROOT, "assets", "AVENTUR.DAT")
OUT = os.path.join(ROOT, "doc", "hole_options.png")

# Paletas reales del juego (bg_pal en game.c), indices 0-3.
PAL = {
    0: [(0x00, 0x00, 0x00), (0x00, 0xAA, 0x44), (0x00, 0x55, 0x22), (0xFF, 0xFF, 0xFF)],
    1: [(0x00, 0x00, 0x00), (0xFF, 0xCC, 0x00), (0x88, 0x44, 0x00), (0xFF, 0xFF, 0xFF)],
    2: [(0x00, 0x00, 0x00), (0x33, 0x66, 0xAA), (0x11, 0x22, 0x44), (0xFF, 0xFF, 0xFF)],
    3: [(0x00, 0x00, 0x00), (0xDD, 0xDD, 0xDD), (0x77, 0x77, 0x77), (0xFF, 0xFF, 0xFF)],
}


def tile_from_record(rec, pal):
    """Convierte un registro AVENTUR.DAT (2 planos de 8 B) en una imagen 8x8."""
    p0, p1 = rec[:8], rec[8:16]
    im = Image.new("RGB", (8, 8))
    px = im.load()
    colors = PAL[pal]
    for y in range(8):
        for x in range(8):
            bit = 7 - x
            idx = (((p1[y] >> bit) & 1) << 1) | ((p0[y] >> bit) & 1)
            px[x, y] = colors[idx]
    return im


def grid_to_image(rows, pal):
    """Convierte filas de texto (.,1,2,3) en una imagen 16x16."""
    colors = PAL[pal]
    im = Image.new("RGB", (16, 16))
    px = im.load()
    for y, row in enumerate(rows):
        assert len(row) == 16, f"fila {y} mide {len(row)}: {row!r}"
        for x, ch in enumerate(row):
            if ch in (".", "0"):
                idx = 0
            elif ch in ("1", "g"):
                idx = 1
            elif ch in ("2", "G"):
                idx = 2
            else:
                idx = 3
            px[x, y] = colors[idx]
    return im


# ---------------------------------------------------------------------------
# Disenos (16x16).  . = color 0 (negro/transparente)   1/2/3 = colores
# ---------------------------------------------------------------------------

# A: hoyo natural con borde de cesped (paleta 0: verde / verde oscuro)
A_NATURAL = [
    "gggggggggggggggg",
    "gGGGGGGGGGGGGGGg",
    "gGGGGGGGGGGGGGGg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gG............Gg",
    "gGGGGGGGGGGGGGGg",
    "gggggggggggggggg",
]

# B: escalera de piedra (paleta 3: gris claro / gris / blanco)
B_STONE_STAIRS = [
    "2222222222222222",
    "2222111111112222",
    "2222333333332222",
    "2222222222222222",
    "2222000000002222",
    "2221111111111222",
    "2223333333333222",
    "2222222222222222",
    "2200000000000022",
    "2211111111111122",
    "2233333333333322",
    "2222222222222222",
    "2000000000000002",
    "2111111111111112",
    "2333333333333332",
    "2222222222222222",
]

# C: hoyo con escalera de mano (paleta 1: dorado / marron)
C_LADDER = [
    "gggggggggggggggg",
    "gGGGGGGGGGGGGGGg",
    "gG............Gg",
    "gG...1....1...Gg",
    "gG...1....1...Gg",
    "gG...111111...Gg",
    "gG...1....1...Gg",
    "gG...1....1...Gg",
    "gG...111111...Gg",
    "gG...1....1...Gg",
    "gG...1....1...Gg",
    "gG...111111...Gg",
    "gG...1....1...Gg",
    "gG...1....1...Gg",
    "gGGGGGGGGGGGGGGg",
    "gggggggggggggggg",
]

# D: pozo de piedra sobre losa (paleta 3)
def make_well_rows():
    rows = []
    for y in range(16):
        row = ""
        for x in range(16):
            dx = x - 7.5
            dy = y - 7.5
            r2 = dx * dx + dy * dy
            if r2 <= 20:
                row += "0"   # fondo del pozo
            elif r2 <= 33:
                row += "1"   # borde claro
            elif r2 <= 46:
                row += "3"   # borde blanco
            else:
                row += "2"   # losa
        rows.append(row)
    return rows


D_WELL = make_well_rows()

OPTIONS = [
    ("A", "Hoyo natural", 0, A_NATURAL),
    ("B", "Escalera de piedra", 3, B_STONE_STAIRS),
    ("C", "Hoyo con escalera", 1, C_LADDER),
    ("D", "Pozo de piedra", 3, D_WELL),
]

SCALE = 8
BG_TILES = 5          # fondo de 40x40 px de cesped
OFF = 12              # posicion del hoyo dentro del fondo


def load_grass():
    data = open(DAT, "rb").read()
    return tile_from_record(data[0:16], 0)  # registro 0 = T_GRASS


def make_panel(rows, pal, grass):
    bg = Image.new("RGB", (40, 40))
    for ty in range(BG_TILES):
        for tx in range(BG_TILES):
            bg.paste(grass, (tx * 8, ty * 8))
    art = grid_to_image(rows, pal)
    bg.paste(art, (OFF, OFF))
    return bg.resize((40 * SCALE, 40 * SCALE), Image.NEAREST)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def char_index(ch):
    if ch in (".", "0"):
        return 0
    if ch in ("1", "g"):
        return 1
    if ch in ("2", "G"):
        return 2
    return 3


def encode_tile(rows, ox, oy):
    """Codifica un tile 8x8 en el formato de AVENTUR.DAT: plano0 (8 B) + plano1."""
    p0 = [0] * 8
    p1 = [0] * 8
    for y in range(8):
        for x in range(8):
            idx = char_index(rows[oy + y][ox + x])
            bit = 7 - x
            if idx & 1:
                p0[y] |= 1 << bit
            if idx & 2:
                p1[y] |= 1 << bit
    return bytes(p0 + p1)


def write_graf():
    """Inserta los tiles del hoyo (C) y de la escalera (B) en assets/AVENTUR.DAT.

    Formato: [N_BG tiles][41 sprites]. Se toman los 10 tiles de fondo
    originales y se anaden detras el hoyo (4) y la escalera (4), dejando
    los sprites intactos. Es idempotente: se puede ejecutar varias veces.
    """
    data = open(DAT, "rb").read()
    n_bg = len(data) // 16 - 41
    if n_bg < 10:
        raise SystemExit(f"AVENTUR.DAT inesperado: {len(data)} bytes")

    base_bg = data[:160]
    spr = data[n_bg * 16:]
    hole = b"".join(encode_tile(C_LADDER, ox, oy)
                    for oy in (0, 8) for ox in (0, 8))
    stairs = b"".join(encode_tile(B_STONE_STAIRS, ox, oy)
                      for oy in (0, 8) for ox in (0, 8))
    assert len(hole) == 64 and len(stairs) == 64

    out = base_bg + hole + stairs + spr
    open(DAT, "wb").write(out)
    print(f"{DAT}: {len(out)} bytes "
          f"({len(base_bg) // 16} fondo + 4 hoyo + 4 escalera + {len(spr) // 16} sprites)")


def main():
    grass = load_grass()
    margin = 24
    gap = 24
    panel = 40 * SCALE
    width = margin * 2 + panel * 4 + gap * 3
    height = 560
    im = Image.new("RGB", (width, height), (20, 20, 30))
    d = ImageDraw.Draw(im)
    f_title = font(24)
    f_sub = font(15)
    f_label = font(17)
    f_small = font(13)

    d.text((margin, 16), "OPCIONES DE HOYO / ESCALERA  (16x16 = 4 patrones de 8x8)",
           font=f_title, fill=(240, 220, 140))
    d.text((margin, 48),
           "Cada opcion se compone como 2x2 celdas. Fondo: T_GRASS real del juego.",
           font=f_sub, fill=(190, 190, 205))

    for i, (letter, name, pal, rows) in enumerate(OPTIONS):
        x = margin + i * (panel + gap)
        y = 84
        img = make_panel(rows, pal, grass)
        im.paste(img, (x, y))
        elegida = letter in ("B", "C")
        outline = (80, 210, 120) if elegida else (70, 70, 95)
        d.rectangle([x - 1, y - 1, x + panel, y + panel], outline=outline,
                    width=2 if elegida else 1)
        # etiquetas
        color = (120, 240, 150) if elegida else (235, 235, 245)
        sufijo = "  (elegida)" if elegida else ""
        d.text((x, y + panel + 10), f"{letter}. {name}{sufijo}", font=f_label,
               fill=color)
        d.text((x, y + panel + 32), f"paleta {pal}", font=f_small,
               fill=(160, 160, 180))

    footer_y = 84 + panel + 70
    d.text((margin, footer_y),
           "Coste: 4 patrones de fondo nuevos = 64 B mas en AVENTUR.DAT y 0 B de RAM.",
           font=f_sub, fill=(160, 220, 170))
    d.text((margin, footer_y + 24),
           "ELEGIDAS: C para el agujero (sala 5) y B para la escalera (Catacumbas).",
           font=f_sub, fill=(150, 235, 160))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT)
    print(OUT)


if __name__ == "__main__":
    import sys
    if "--write-graf" in sys.argv:
        write_graf()
    else:
        main()
