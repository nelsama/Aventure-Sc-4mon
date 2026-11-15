#!/usr/bin/env python3
"""Jugador A (caballero) en 4 direcciones, 16x16, con paleta azul+oro.

Salida:
  doc/player_A_game.png  (preview)
  volcado C con 16 patrones (down, up, left, right)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

# '#'=color1 (azul), '+'=color2 (oro), '@'=color3 (negro)
DOWN = [
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
UP = [
    "......@@@.......",
    ".....@###@......",
    "....@#####@.....",
    "....@+++++@.....",
    "....@#####@.....",
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
LEFT = [
    "....@@@@@.......",
    "...@#####@......",
    "...@#++++#@.....",
    "..@##@####@.....",
    "..@##@####@.....",
    "...@#++++#@.....",
    "....@###@.......",
    "...@@###@@......",
    "..@##@###@......",
    "..@##@###@......",
    "..@##@#+#@......",
    "..@##@###@......",
    "...@@###@@......",
    "....@##@##@.....",
    "....@##@##@.....",
    "....@@@@@@@.....",
]
RIGHT = [row[::-1] for row in LEFT]

LEFT_B = [  # segundo fotograma de caminar (piernas desplazadas)
    "....@@@@@.......",
    "...@#####@......",
    "...@#++++#@.....",
    "..@##@####@.....",
    "..@##@####@.....",
    "...@#++++#@.....",
    "....@###@.......",
    "...@@###@@......",
    "..@##@###@......",
    "..@##@###@......",
    "..@##@#+#@......",
    "..@##@###@......",
    "...@@###@@......",
    "...@##@##@......",
    "..@##@##@.......",
    "..@@@.@@@@......",
]
RIGHT_B = [row[::-1] for row in LEFT_B]

PAL = {".": (0, 0, 0, 0),
       "#": (46, 91, 255, 255),    # azul
       "+": (255, 204, 0, 255),    # oro
       "@": (16, 16, 24, 255)}     # negro


def check(g, name):
    if len(g) != 16:
        raise SystemExit(f"{name}: {len(g)} filas")
    for i, row in enumerate(g):
        if len(row) != 16:
            raise SystemExit(f"{name} fila {i}: {len(row)} -> {row!r}")


def quadrant(grid, qx, qy):
    return [grid[qy * 8 + y][qx * 8:qx * 8 + 8] for y in range(8)]


def planes(quad):
    b0, b1 = [], []
    for row in quad:
        p0 = p1 = 0
        for x, ch in enumerate(row):
            c = {".": 0, "#": 1, "+": 2, "@": 3}[ch]
            if c & 1:
                p0 |= 0x80 >> x
            if c & 2:
                p1 |= 0x80 >> x
        b0.append(p0)
        b1.append(p1)
    return b0, b1


def emit():
    for name, grid in [("DOWN", DOWN), ("UP", UP),
                       ("LEFT A", LEFT), ("RIGHT A", RIGHT),
                       ("LEFT B", LEFT_B), ("RIGHT B", RIGHT_B)]:
        print(f"    /* {name} */")
        for qy in range(2):
            for qx in range(2):
                b0, b1 = planes(quadrant(grid, qx, qy))
                a = ",".join(f"0x{v:02X}" for v in b0)
                b = ",".join(f"0x{v:02X}" for v in b1)
                print(f"    {{ {{{a}}}, {{{b}}} }},")


def preview():
    scale = 10
    cell = 16 * scale
    gap = 14
    frames = [("ABAJO", DOWN), ("ARRIBA", UP),
              ("IZQ A", LEFT), ("IZQ B", LEFT_B),
              ("DER A", RIGHT), ("DER B", RIGHT_B)]
    w = 20 + len(frames) * (cell + gap)
    h = 60 + cell + 30
    img = Image.new("RGBA", (w, h), (24, 24, 34, 255))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.load_default(size=16)
    except Exception:
        f = ImageFont.load_default()
    d.text((16, 12), "JUGADOR A - DIRECCIONES + CAMINAR (azul + oro)", font=f,
           fill=(240, 220, 140, 255))
    for i, (name, grid) in enumerate(frames):
        x = 20 + i * (cell + gap)
        y = 50
        bg = Image.new("RGBA", (16, 16), (60, 45, 30, 255))
        px = bg.load()
        for yy in range(16):
            for xx in range(16):
                px[xx, yy] = PAL[grid[yy][xx]]
        big = bg.resize((cell, cell), Image.NEAREST)
        d.rectangle([x - 1, y - 1, x + cell, y + cell],
                    outline=(75, 75, 100, 255))
        img.paste(big, (x, y))
        d.text((x, y + cell + 4), name, font=f, fill=(225, 225, 235, 255))
    img.save("doc/player_A_game.png")
    print("doc/player_A_game.png", img.size)


def main():
    for name, g in [("DOWN", DOWN), ("UP", UP), ("LEFT", LEFT),
                    ("RIGHT", RIGHT), ("LEFT_B", LEFT_B),
                    ("RIGHT_B", RIGHT_B)]:
        check(g, name)
    preview()
    if len(sys.argv) > 1 and sys.argv[1] == "c":
        emit()


if __name__ == "__main__":
    main()
