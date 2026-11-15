#!/usr/bin/env python3
"""Compara candidatos: original vs reducido a 3 colores + transparencia."""
import os
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

BASE = "img/Basic Asset Pack/Basic Dragon Animations"
CANDIDATES = [
    ("Adult Green Dragon", "green"),
    ("Adult White Dragon", "white"),
    ("Aqua Drake", "green"),
    ("Mature Bronze Dragon", "gold"),
    ("Mud Wyvern", "gold"),
    ("Poison Drake", "green"),
    ("Viridian Drake", "green"),
    ("Young Red Dragon", "red"),
]

PALS = {
    "red":   [(120, 10, 10, 255), (220, 30, 30, 255), (255, 200, 200, 255)],
    "green": [(20, 100, 40, 255), (40, 210, 60, 255), (220, 255, 220, 255)],
    "gold":  [(120, 80, 10, 255), (235, 190, 30, 255), (255, 250, 210, 255)],
    "white": [(90, 90, 110, 255), (190, 190, 210, 255), (255, 255, 255, 255)],
}


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def quantize(frame, pal):
    """Mapea por luminancia a 3 tonos + transparente."""
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    px = out.load()
    src = frame.load()
    for y in range(frame.height):
        for x in range(frame.width):
            r, g, b, a = src[x, y]
            if a < 40:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < 90:
                px[x, y] = pal[0]
            elif lum < 175:
                px[x, y] = pal[1]
            else:
                px[x, y] = pal[2]
    return out


def main():
    scale = 9
    cell = 16 * scale
    row_h = cell + 34
    w = 20 + len(CANDIDATES) * (cell + 14) + 20
    h = 60 + 2 * row_h + 30
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((16, 12), "ORIGINAL (arriba) vs 3 COLORES + TRANSPARENTE (abajo)",
           font=font(22), fill=(240, 220, 140, 255))
    for i, (name, palette) in enumerate(CANDIDATES):
        path = os.path.join(BASE, name, name.replace(" ", "") + ".png")
        if not os.path.exists(path):
            # fallback: first png in folder
            folder = os.path.join(BASE, name)
            path = next(os.path.join(folder, f) for f in os.listdir(folder)
                        if f.lower().endswith(".png"))
        strip = Image.open(path).convert("RGBA")
        frame = strip.crop((0, 0, 16, 16))
        colors = Counter(p for p in frame.getdata() if p[3] > 40)
        print(f"{name}: {len(colors)} colores opacos -> {colors.most_common(5)}")
        pal = PALS[palette]
        quant = quantize(frame, pal)
        for row, spr in enumerate([frame, quant]):
            y = 48 + row * row_h
            x = 20 + i * (cell + 14)
            bg = Image.new("RGBA", (16, 16), (38, 38, 52, 255))
            bg.alpha_composite(spr)
            big = bg.resize((cell, cell), Image.NEAREST)
            d.rectangle([x - 1, y - 1, x + cell, y + cell],
                        outline=(75, 75, 100, 255))
            img.paste(big, (x, y))
        d.text((20 + i * (cell + 14), 48 + 2 * row_h + 4), name,
               font=font(13), fill=(225, 225, 235, 255))
    img.save("doc/dragon_pack_quant.png")
    print("doc/dragon_pack_quant.png", img.size)


if __name__ == "__main__":
    main()
