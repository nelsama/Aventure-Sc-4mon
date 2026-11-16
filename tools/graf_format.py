#!/usr/bin/env python3
"""Nucleo del formato GRAF.DAT (patrones del juego AVENTURA).

Formato (1024 bytes = 64 registros de 16 bytes):

    offset 0   : planos de tiles de fondo (22 registros)
    offset 352 : planos de sprites (42 registros)

Cada registro es un patron 8x8 con DOS planos de 8 bytes:

    registro[0:8]   plano 0   (bit 7 = pixel de la izquierda)
    registro[8:16]  plano 1

El indice de color de un pixel es  (plano1 << 1) | plano0 , y va de 0 a 3.
El color 0 es transparente en el juego.

Este modulo no depende de Tkinter: lo usa la GUI (tools/graf_editor.py) y
tambien se puede usar desde la linea de ordenes.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAF_PATH = os.path.join(ROOT, "assets", "GRAF.DAT")

REC = 16            # bytes por registro
W = H = 8           # tamano del patron
TILE = W * H        # pixeles

# Paletas reales del juego (bg_pal y spr_pal en game.c).
BG_PAL = {
    0: [(0x00, 0x00, 0x00), (0x00, 0xAA, 0x44), (0x00, 0x55, 0x22), (0xFF, 0xFF, 0xFF)],
    1: [(0x00, 0x00, 0x00), (0xFF, 0xCC, 0x00), (0x88, 0x44, 0x00), (0xFF, 0xFF, 0xFF)],
    2: [(0x00, 0x00, 0x00), (0x33, 0x66, 0xAA), (0x11, 0x22, 0x44), (0xFF, 0xFF, 0xFF)],
    3: [(0x00, 0x00, 0x00), (0xDD, 0xDD, 0xDD), (0x77, 0x77, 0x77), (0xFF, 0xFF, 0xFF)],
}

SPR_PAL = {
    0: [(0x00, 0x00, 0x00), (0x2E, 0x5B, 0xFF), (0xFF, 0xCC, 0x00), (0x10, 0x10, 0x18)],
    1: [(0x00, 0x00, 0x00), (0xFF, 0xCC, 0x00), (0x99, 0x55, 0x00), (0xFF, 0xFF, 0xFF)],
    2: [(0x00, 0x00, 0x00), (0xFF, 0x00, 0x00), (0xFF, 0x88, 0x00), (0xFF, 0xFF, 0xFF)],
    3: [(0x00, 0x00, 0x00), (0x00, 0xFF, 0x00), (0x00, 0x88, 0x00), (0xFF, 0xFF, 0xFF)],
}


def default_n_bg(size):
    """Numero de registros de fondo a partir del tamano del fichero."""
    n = size // REC
    if n == 64:
        return 22
    return max(0, n - 42)


class GrafFile:
    """Coleccion de registros de 16 bytes con su ruta de origen."""

    def __init__(self, records=None, n_bg=22, path=None):
        self.records = [bytearray(r) for r in (records or [])]
        self.n_bg = n_bg
        self.path = path

    # -- E/S ---------------------------------------------------------------
    @classmethod
    def load(cls, path=GRAF_PATH):
        with open(path, "rb") as f:
            data = f.read()
        n = len(data) // REC
        recs = [data[i * REC:(i + 1) * REC] for i in range(n)]
        return cls(recs, default_n_bg(len(data)), path)

    def save(self, path=None, backup=True):
        path = path or self.path
        if not path:
            raise ValueError("sin ruta de destino")
        data = b"".join(bytes(r) for r in self.records)
        if backup and os.path.exists(path):
            with open(path, "rb") as f:
                old = f.read()
            with open(path + ".bak", "wb") as f:
                f.write(old)
        with open(path, "wb") as f:
            f.write(data)
        self.path = path

    # -- Utilidades --------------------------------------------------------
    def __len__(self):
        return len(self.records)

    def get(self, i):
        return bytes(self.records[i])

    def set(self, i, rec):
        self.records[i] = bytearray(rec)

    def is_sprite(self, i):
        return i >= self.n_bg

    def pal_for(self, i, pal=None):
        """Paleta con la que se ve el registro i en el juego."""
        if pal is not None:
            return (BG_PAL if not self.is_sprite(i) else SPR_PAL)[pal]
        return SPR_PAL[0] if self.is_sprite(i) else BG_PAL[0]


# ---------------------------------------------------------------------------
# Conversiones registro <-> pixeles
# ---------------------------------------------------------------------------
def record_to_pixels(rec):
    """Devuelve 8 filas de 8 indices de color (0-3)."""
    p0, p1 = rec[:8], rec[8:16]
    rows = []
    for y in range(H):
        row = []
        for x in range(W):
            bit = 7 - x
            row.append((((p1[y] >> bit) & 1) << 1) | ((p0[y] >> bit) & 1))
        rows.append(row)
    return rows


def pixels_to_record(rows):
    """Convierte 8 filas de 8 indices de color en un registro de 16 bytes."""
    p0 = bytearray(8)
    p1 = bytearray(8)
    for y in range(min(H, len(rows))):
        row = rows[y]
        for x in range(min(W, len(row))):
            idx = int(row[x]) & 3
            bit = 7 - x
            if idx & 1:
                p0[y] |= 1 << bit
            if idx & 2:
                p1[y] |= 1 << bit
    return bytes(p0 + p1)


def record_to_image(rec, pal, scale=8, transparente=True):
    """Renderiza un registro 8x8 como imagen PIL (RGBA si transparente)."""
    from PIL import Image

    modo = "RGBA" if transparente else "RGB"
    im = Image.new(modo, (W * scale, H * scale), (0, 0, 0, 0) if transparente else (0, 0, 0))
    px = im.load()
    rows = record_to_pixels(rec)
    for y in range(H):
        for x in range(W):
            idx = rows[y][x]
            col = pal[idx]
            if transparente:
                if idx == 0:
                    continue
                color = (col[0], col[1], col[2], 255)
            else:
                color = col
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = color
    return im


def image_to_pixels(im, pal):
    """Ajusta una imagen (8x8 o 16x16) a los indices de color de la paleta."""
    from PIL import Image

    if im.mode != "RGBA":
        im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                row.append(0)
                continue
            best, bestd = 0, None
            for idx in range(1, 4):
                c = pal[idx]
                d = (r - c[0]) ** 2 + (g - c[1]) ** 2 + (b - c[2]) ** 2
                if bestd is None or d < bestd:
                    best, bestd = idx, d
            row.append(best)
        rows.append(row)
    return rows


def _shrink(im, w, h):
    """Reduce una imagen (escala entera) al tamano w x h sin interpolar."""
    from PIL import Image

    if im.size == (w, h):
        return im
    if (im.size[0] % w == 0 and im.size[1] % h == 0
            and im.size[0] >= w and im.size[1] >= h):
        return im.resize((w, h), Image.NEAREST)
    raise ValueError("la imagen debe ser de %dx%d (o un multiplo exacto)" % (w, h))


def image_to_record(im, pal):
    """Convierte una imagen 8x8 (o su multipliplo) en un registro."""
    if im.size != (W, H):
        im = _shrink(im, W, H)
    return pixels_to_record(image_to_pixels(im, pal))


def image16_to_records(im, pal):
    """Convierte una imagen 16x16 (o su multipliplo) en 4 registros."""
    from PIL import Image

    if im.size != (2 * W, 2 * H):
        im = _shrink(im, 2 * W, 2 * H)
    recs = []
    for oy in (0, H):
        for ox in (0, W):
            recs.append(image_to_record(im.crop((ox, oy, ox + W, oy + H)), pal))
    return recs


def composite(records, pal, scale=8, transparente=True):
    """Compone 4 registros (TL, TR, BL, BR) en una imagen 16x16."""
    from PIL import Image

    out = Image.new("RGBA" if transparente else "RGB",
                    (2 * W * scale, 2 * H * scale),
                    (0, 0, 0, 0) if transparente else (0, 0, 0))
    for i, rec in enumerate(records[:4]):
        ox = (i % 2) * W * scale
        oy = (i // 2) * H * scale
        out.paste(record_to_image(rec, pal, scale, transparente), (ox, oy))
    return out


def record_to_text(rec):
    """Volcado legible de un registro (plano 0 / plano 1 en hexadecimal)."""
    filas = []
    for y in range(H):
        filas.append("%02X  %02X" % (rec[y], rec[8 + y]))
    return "\n".join(filas)


def text_to_record(texto):
    """Interpreta el volcado de record_to_text()."""
    p0 = bytearray(8)
    p1 = bytearray(8)
    for y, linea in enumerate(texto.strip().splitlines()[:8]):
        partes = linea.replace(",", " ").split()
        if len(partes) < 2:
            raise ValueError("linea %d incompleta" % (y + 1))
        p0[y] = int(partes[0], 16) & 0xFF
        p1[y] = int(partes[1], 16) & 0xFF
    return bytes(p0 + p1)


if __name__ == "__main__":
    # Volcado rapido por linea de ordenes.
    import sys

    g = GrafFile.load(sys.argv[1] if len(sys.argv) > 1 else GRAF_PATH)
    print("%s: %d registros (%d fondo + %d sprites)"
          % (g.path, len(g), g.n_bg, len(g) - g.n_bg))
    for i in range(len(g)):
        kind = "sprite" if g.is_sprite(i) else "fondo "
        print("%02d %s %s" % (i, kind, record_to_text(g.get(i)).replace("\n", " | ")))
