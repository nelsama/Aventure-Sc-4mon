#!/usr/bin/env python3
"""Vista detallada del Poison Drake: 4 frames originales y a 3 colores."""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = "img/Basic Asset Pack/Basic Dragon Animations/Poison Drake/PoisonDrake.png"
OUT = "doc/poison_drake.png"

# Paleta verde del juego: oscuro, principal, blanco
PAL = [(20, 100, 40, 255), (40, 210, 60, 255), (245, 255, 245, 255)]


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def quant(frame):
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    px = out.load()
    src = frame.load()
    for y in range(16):
        for x in range(16):
            r, g, b, a = src[x, y]
            if a < 40:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < 70:
                px[x, y] = PAL[0]
            elif lum < 200:
                px[x, y] = PAL[1]
            else:
                px[x, y] = PAL[2]
    return out


def mirror(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def main():
    strip = Image.open(SRC).convert("RGBA")
    frames = [strip.crop((i * 16, 0, i * 16 + 16, 16)) for i in range(4)]
    scale = 12
    cell = 16 * scale
    gap = 18
    margin = 22
    # 4 columnas (frames) x 3 filas (original, 3 colores, espejado 3 colores)
    w = margin * 2 + 4 * cell + 3 * gap
    h = margin * 2 + 50 + 3 * (cell + 34)
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((margin, 10), "POISON DRAKE - frames 0..3", font=font(24),
           fill=(240, 220, 140, 255))
    rows = [
        ("ORIGINAL", frames),
        ("3 COLORES", [quant(f) for f in frames]),
        ("3 COLORES + FLIP", [mirror(quant(f)) for f in frames]),
    ]
    for ri, (label, imgs) in enumerate(rows):
        y = margin + 44 + ri * (cell + 34)
        d.text((margin, y - 18), label, font=font(15),
               fill=(200, 220, 255, 255))
        for ci, spr in enumerate(imgs):
            x = margin + ci * (cell + gap)
            bg = Image.new("RGBA", (16, 16), (38, 38, 52, 255))
            bg.alpha_composite(spr)
            big = bg.resize((cell, cell), Image.NEAREST)
            d.rectangle([x - 1, y - 1, x + cell, y + cell],
                        outline=(75, 75, 100, 255))
            img.paste(big, (x, y))
            d.text((x, y + cell + 4), f"frame {ci}", font=font(13),
                   fill=(225, 225, 235, 255))
    img.save(OUT)
    print(OUT, img.size)


if __name__ == "__main__":
    main()
