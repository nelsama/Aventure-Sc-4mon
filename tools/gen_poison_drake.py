#!/usr/bin/env python3
"""Genera los patrones del Poison Drake (16x16, 2 frames, 2 direcciones).

Salida:
  - volcado C por stdout (16 patrones, 8 por direccion)
  - doc/poison_drake_ingame.png (preview con la paleta verde)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

SRC = "img/Basic Asset Pack/Basic Dragon Animations/Poison Drake/PoisonDrake.png"
FRAMES = [0, 1]

PAL = {1: (40, 210, 60, 255),   # principal
       2: (20, 100, 40, 255),   # oscuro
       3: (245, 255, 245, 255), # blanco
       0: (0, 0, 0, 0)}


def load_frame(idx):
    im = Image.open(SRC).convert("RGBA")
    fr = im.crop((idx * 16, 0, idx * 16 + 16, 16))
    grid = []
    for y in range(16):
        row = []
        for x in range(16):
            r, g, b, a = fr.getpixel((x, y))
            if a < 40:
                row.append(0)
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < 70:
                row.append(2)
            elif lum < 200:
                row.append(1)
            else:
                row.append(3)
        grid.append(row)
    return grid


def mirror(grid):
    return [row[::-1] for row in grid]


def quadrant(grid, qx, qy):
    return [[grid[qy * 8 + y][qx * 8 + x] for x in range(8)]
            for y in range(8)]


def planes(quad):
    p0 = p1 = 0
    b0, b1 = [], []
    for row in quad:
        p0 = p1 = 0
        for x, c in enumerate(row):
            if c & 1:
                p0 |= 0x80 >> x
            if c & 2:
                p1 |= 0x80 >> x
        b0.append(p0)
        b1.append(p1)
    return b0, b1


def emit(grids, names):
    for grid, name in zip(grids, names):
        print(f"    /* {name} */")
        for qy in range(2):
            for qx in range(2):
                b0, b1 = planes(quadrant(grid, qx, qy))
                a = ",".join(f"0x{v:02X}" for v in b0)
                b = ",".join(f"0x{v:02X}" for v in b1)
                print(f"    {{ {{{a}}}, {{{b}}} }},")


def preview(grids, names, path="doc/poison_drake_ingame.png"):
    scale = 14
    cell = 16 * scale
    gap = 18
    w = 20 + len(grids) * (cell + gap)
    h = 60 + cell + 30
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.load_default(size=18)
    except Exception:
        f = ImageFont.load_default()
    d.text((16, 12), "POISON DRAKE EN EL JUEGO (verde)", font=f,
           fill=(240, 220, 140, 255))
    for i, (g, name) in enumerate(zip(grids, names)):
        x = 20 + i * (cell + gap)
        y = 50
        bg = Image.new("RGBA", (16, 16), (38, 38, 52, 255))
        px = bg.load()
        for yy in range(16):
            for xx in range(16):
                px[xx, yy] = PAL[g[yy][xx]]
        big = bg.resize((cell, cell), Image.NEAREST)
        d.rectangle([x - 1, y - 1, x + cell, y + cell],
                    outline=(75, 75, 100, 255))
        img.paste(big, (x, y))
        d.text((x, y + cell + 4), name, font=f, fill=(225, 225, 235, 255))
    img.save(path)
    print(path, img.size)


def main():
    a = load_frame(FRAMES[0])
    b = load_frame(FRAMES[1])
    grids = [a, b, mirror(a), mirror(b)]
    names = ["frame A derecha", "frame B derecha",
             "frame A izquierda", "frame B izquierda"]
    preview(grids, names)
    if len(sys.argv) > 1 and sys.argv[1] == "c":
        emit(grids, names)


if __name__ == "__main__":
    main()
