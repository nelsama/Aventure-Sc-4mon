#!/usr/bin/env python3
"""Anade el patron del corazon (sprite 41) a assets/GRAF.DAT.

Formato actual: [22 tiles de fondo][41 sprites] = 1008 B.
El corazon se anade como sprite 41; el fichero queda en 1024 B.
Uso: python tools/gen_hud.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_chalice import encode_sprite  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAF = os.path.join(ROOT, "assets", "GRAF.DAT")

# Paleta de sprite 2: 1 = rojo, 3 = blanco
HEART = [
    "........",
    ".11.11..",
    "1111111.",
    "1131111.",
    ".11111..",
    "..111...",
    "...1....",
    "........",
]

SPR_OFF = 22 * 16   # 22 tiles de fondo delante


def main():
    data = bytearray(open(GRAF, "rb").read())
    n_spr = (len(data) - SPR_OFF) // 16
    rec = encode_sprite(HEART)

    if n_spr == 41:
        data += rec
    elif n_spr == 42:
        data[SPR_OFF + 41 * 16:SPR_OFF + 42 * 16] = rec
    else:
        raise SystemExit(f"GRAF.DAT inesperado: {len(data)} B, {n_spr} sprites")

    open(GRAF, "wb").write(data)
    print(f"{GRAF}: {len(data)} bytes (corazon = sprite 41)")


if __name__ == "__main__":
    main()
