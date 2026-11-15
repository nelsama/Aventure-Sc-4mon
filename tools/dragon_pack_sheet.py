#!/usr/bin/env python3
"""Contact sheet de todos los dragones del Basic Asset Pack (4 frames 16x16)."""
import glob
import os
from PIL import Image, ImageDraw, ImageFont

BASE = "img/Basic Asset Pack/Basic Dragon Animations"
OUT = "doc/dragon_pack_sheet.png"


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def main():
    files = sorted(glob.glob(BASE + "/*/*.png"))
    scale = 4
    fw, fh = 16 * scale, 16 * scale
    label_w = 190
    gap = 8
    rows = len(files)
    w = label_w + 4 * (fw + 6) + 20
    h = rows * (fh + gap) + 60
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    d.text((16, 12), "BASIC ASSET PACK - DRAGONES (4 frames de 16x16)",
           font=font(22), fill=(240, 220, 140, 255))
    y = 48
    for p in files:
        name = os.path.basename(os.path.dirname(p))
        strip = Image.open(p).convert("RGBA")
        d.text((16, y + fh // 2 - 8), name, font=font(15),
               fill=(225, 225, 235, 255))
        for f in range(4):
            frame = strip.crop((f * 16, 0, f * 16 + 16, 16))
            bg = Image.new("RGBA", (16, 16), (38, 38, 52, 255))
            bg.alpha_composite(frame)
            big = bg.resize((fw, fh), Image.NEAREST)
            x = label_w + f * (fw + 6)
            d.rectangle([x - 1, y - 1, x + fw, y + fh],
                        outline=(75, 75, 100, 255))
            img.paste(big, (x, y))
        y += fh + gap
    img.save(OUT)
    print(OUT, img.size)


if __name__ == "__main__":
    main()
