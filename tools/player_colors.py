#!/usr/bin/env python3
"""Player A (caballero) con varias paletas de color -> doc/player_colors.png"""
import sys
from PIL import Image, ImageDraw, ImageFont

PL_A = [
    "......@@@.......",
    ".....@###@......",
    "....@#####@.....",
    "....@#+++#@.....",
    "....@#@#@#@.....",
    "....@#####@.....",
    ".....@###@......",
    "...@@#####@@....",
    "..@##@###@##@...",
    "..@##@###@##@...",
    "..@##@#+#@##@...",
    "..@##@###@##@...",
    "...@@#####@@....",
    "....@##@##@.....",
    "....@##@##@.....",
    "....@@@@@@@.....",
]

# '#'=color1 (principal), '+'=color2 (detalle), '@'=color3 (contorno)
SCHEMES = [
    ("1 AZUL + ORO", (46, 91, 255, 255), (255, 204, 0, 255), (16, 16, 24, 255)),
    ("2 VERDE + ORO", (31, 168, 74, 255), (232, 192, 64, 255), (12, 20, 14, 255)),
    ("3 ROJO + ORO", (216, 50, 50, 255), (240, 192, 64, 255), (20, 10, 10, 255)),
    ("4 PURPURA + PLATA", (122, 79, 208, 255), (192, 192, 208, 255), (14, 10, 22, 255)),
    ("5 TURQUESA + NARANJA", (32, 178, 170, 255), (255, 154, 48, 255), (10, 20, 20, 255)),
]


def check(g):
    for i, row in enumerate(g):
        if len(row) != 16:
            raise SystemExit(f"fila {i}: {len(row)}")


def render(main, sec, dark, scale=12):
    pal = {".": (0, 0, 0, 0), "#": main, "+": sec, "@": dark}
    img = Image.new("RGBA", (16, 16), (35, 35, 48, 255))
    px = img.load()
    for y, row in enumerate(PL_A):
        for x, ch in enumerate(row):
            px[x, y] = pal[ch]
    return img.resize((16 * scale, 16 * scale), Image.NEAREST)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def main():
    check(PL_A)
    scale = 12
    cell = 16 * scale
    gap = 28
    margin = 24
    n = len(SCHEMES)
    w = margin * 2 + n * cell + (n - 1) * gap
    h = margin * 2 + 46 + cell + 30
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((margin, 10), "JUGADOR A - PALETAS DE COLOR", font=font(24),
           fill=(240, 220, 140, 255))
    for i, (label, main_c, sec_c, dark_c) in enumerate(SCHEMES):
        x = margin + i * (cell + gap)
        y = margin + 44
        d.rectangle([x - 2, y - 2, x + cell + 1, y + cell + 1],
                    outline=(80, 80, 110, 255))
        spr = render(main_c, sec_c, dark_c, scale)
        img.paste(spr, (x, y), spr)
        d.text((x, y + cell + 6), label, font=font(16),
               fill=(225, 225, 235, 255))
    img.save("doc/player_colors.png")
    print("doc/player_colors.png", img.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
