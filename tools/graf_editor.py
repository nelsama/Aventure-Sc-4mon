#!/usr/bin/env python3
"""Editor grafico de GRAF.DAT (patrones de tiles y sprites del juego AVENTURA).

Permite:
  - abrir y guardar assets/GRAF.DAT (con copia .bak);
  - ver los 64 registros (22 de fondo + 42 de sprites) en miniatura;
  - pintar pixel a pixel el registro elegido (2 planos, 4 colores);
  - exportar un registro (o un grupo de 4 registros) a PNG;
  - importar un PNG de 8x8 (1 registro) o de 16x16 (4 registros);
  - copiar/pegar/deshacer.

Uso:
  python tools/graf_editor.py [fichero.dat]
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageTk          # noqa: E402
import graf_format as gf                # noqa: E402

ROOT = gf.ROOT
ZOOM_DEFAULT = 16
THUMB_SCALE = 4


def rgb_to_hex(col):
    return "#%02X%02X%02X" % col


class Editor(tk.Tk):
    def __init__(self, path=None):
        super().__init__()
        self.title("GRAF.DAT - editor de patrones")
        self.geometry("1180x780")
        self.minsize(1000, 700)

        self.graf = None
        self.sel = 0
        self.color = 1
        self.zoom = ZOOM_DEFAULT
        self.thumb_scale = THUMB_SCALE
        self.thumb_cols = 8
        self.pal_mode = "auto"          # auto | 0..3
        self.undo_stack = []
        self.clipboard = None
        self.thumb_photos = []
        self.thumb_rects = []

        self._build()
        self._bind_keys()

        if path:
            self.abrir(path)
        else:
            self.abrir(gf.GRAF_PATH, silencioso=True)

    # ------------------------------------------------------------------
    # Interfaz
    # ------------------------------------------------------------------
    def _build(self):
        # --- barra superior -------------------------------------------
        top = ttk.Frame(self, padding=(6, 6, 6, 2))
        top.pack(side="top", fill="x")
        ttk.Label(top, text="Fichero:").pack(side="left")
        self.lbl_path = ttk.Label(top, text="-", width=60, anchor="w")
        self.lbl_path.pack(side="left", padx=(4, 8))
        ttk.Button(top, text="Abrir", command=self.abrir).pack(side="left")
        ttk.Button(top, text="Guardar", command=self.guardar).pack(side="left", padx=2)
        ttk.Button(top, text="Guardar como...", command=self.guardar_como).pack(side="left")
        ttk.Button(top, text="Recargar", command=self.recargar).pack(side="left", padx=2)

        body = ttk.Frame(self, padding=(6, 2, 6, 2))
        body.pack(side="top", fill="both", expand=True)

        # --- izquierda: miniaturas -------------------------------------
        left = ttk.Frame(body)
        left.pack(side="left", fill="y")

        pal_row = ttk.Frame(left)
        pal_row.pack(side="top", fill="x", pady=(0, 4))
        ttk.Label(pal_row, text="Paleta:").pack(side="left")
        self.cmb_pal = ttk.Combobox(pal_row, state="readonly", width=14,
                                    values=["auto", "fondo 0", "fondo 1", "fondo 2",
                                            "fondo 3", "sprite 0", "sprite 1",
                                            "sprite 2", "sprite 3"])
        self.cmb_pal.current(0)
        self.cmb_pal.pack(side="left", padx=4)
        self.cmb_pal.bind("<<ComboboxSelected>>", lambda e: self.refrescar())

        self.lbl_thumb = ttk.Label(left, text="Registros")
        self.lbl_thumb.pack(side="top", anchor="w")

        wrap = ttk.Frame(left)
        wrap.pack(side="top", fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical")
        self.canvas_thumbs = tk.Canvas(wrap, bg="#202030", width=420, height=480,
                                       highlightthickness=0, yscrollcommand=sb.set)
        sb.config(command=self.canvas_thumbs.yview)
        sb.pack(side="right", fill="y")
        self.canvas_thumbs.pack(side="left", fill="both", expand=True)
        self.canvas_thumbs.bind("<Configure>", self._resize_thumbs)
        self.canvas_thumbs.bind("<MouseWheel>", self._scroll_thumbs)

        # --- derecha: editor -------------------------------------------
        right = ttk.Frame(body, padding=(10, 0, 0, 0))
        right.pack(side="left", fill="both", expand=True)

        self.lbl_info = ttk.Label(right, text="", font=("Consolas", 10))
        self.lbl_info.pack(side="top", anchor="w")

        mid = ttk.Frame(right)
        mid.pack(side="top", anchor="w", pady=6)

        # lienzo 8x8
        l1 = ttk.Frame(mid)
        l1.pack(side="left", padx=(0, 14))
        ttk.Label(l1, text="Patron 8x8 (2 planos)").pack(anchor="w")
        self.canvas_edit = tk.Canvas(l1, bg="#101018", highlightthickness=0,
                                     width=ZOOM_DEFAULT * 8, height=ZOOM_DEFAULT * 8)
        self.canvas_edit.pack()
        self.canvas_edit.bind("<Button-1>", self._paint)
        self.canvas_edit.bind("<B1-Motion>", self._paint)
        self.canvas_edit.bind("<Button-3>", self._paint)
        self.canvas_edit.bind("<B3-Motion>", self._paint)

        # lienzo 16x16
        l2 = ttk.Frame(mid)
        l2.pack(side="left", padx=(0, 14))
        ttk.Label(l2, text="Grupo de 4 registros (16x16)").pack(anchor="w")
        self.canvas_grp = tk.Canvas(l2, bg="#101018", highlightthickness=0,
                                    width=ZOOM_DEFAULT * 16, height=ZOOM_DEFAULT * 16)
        self.canvas_grp.pack()

        # paleta de colores
        pal_frame = ttk.Frame(right)
        pal_frame.pack(side="top", anchor="w", pady=(4, 4))
        ttk.Label(pal_frame, text="Color:").pack(side="left", padx=(0, 6))
        self.color_buttons = []
        for i in range(4):
            b = tk.Button(pal_frame, width=3, text=str(i), command=(lambda k: self.set_color(k))(i))
            b.pack(side="left", padx=2)
            self.color_buttons.append(b)

        # volcado hexadecimal
        self.txt_hex = tk.Text(right, width=44, height=10, font=("Consolas", 10),
                               wrap="none", bg="#101018", fg="#c0c0d0")
        self.txt_hex.pack(side="top", anchor="w", pady=6)

        # botones
        b1 = ttk.Frame(right)
        b1.pack(side="top", fill="x")
        ttk.Button(b1, text="Exportar PNG (8x8)", command=self.exportar_png).pack(side="left")
        ttk.Button(b1, text="Exportar PNG (16x16)", command=self.exportar_png16).pack(side="left", padx=2)
        ttk.Button(b1, text="Importar PNG (8x8)", command=self.importar_png).pack(side="left", padx=2)
        ttk.Button(b1, text="Importar PNG (16x16)", command=self.importar_png16).pack(side="left")

        b2 = ttk.Frame(right)
        b2.pack(side="top", fill="x", pady=4)
        ttk.Button(b2, text="Copiar", command=self.copiar).pack(side="left")
        ttk.Button(b2, text="Pegar", command=self.pegar).pack(side="left", padx=2)
        ttk.Button(b2, text="Deshacer", command=self.deshacer).pack(side="left")
        ttk.Button(b2, text="Limpiar", command=self.limpiar).pack(side="left", padx=2)
        ttk.Label(b2, text="Zoom:").pack(side="left", padx=(12, 2))
        self.spin_zoom = ttk.Spinbox(b2, from_=8, to=32, width=4)
        self.spin_zoom.set(self.zoom)
        self.spin_zoom.pack(side="left")
        self.spin_zoom.bind("<Return>", lambda e: self.set_zoom())
        ttk.Button(b2, text="Aplicar", command=self.set_zoom).pack(side="left", padx=2)

        self.lbl_status = ttk.Label(self, text="Clic izquierdo: pintar   Clic derecho: color 0 (transparente)   Ctrl+S: guardar   Ctrl+Z: deshacer",
                                    relief="sunken", anchor="w")
        self.lbl_status.pack(side="bottom", fill="x")

    def _bind_keys(self):
        self.bind_all("<Control-s>", lambda e: self.guardar())
        self.bind_all("<Control-o>", lambda e: self.abrir())
        self.bind_all("<Control-z>", lambda e: self.deshacer())
        self.bind_all("<Control-c>", lambda e: self.copiar())
        self.bind_all("<Control-v>", lambda e: self.pegar())

    # ------------------------------------------------------------------
    # Paleta y refresco
    # ------------------------------------------------------------------
    def paleta(self, i=None):
        """Paleta (4 colores RGB) con la que se ve el registro i."""
        i = self.sel if i is None else i
        modo = self.cmb_pal.get()
        if self.graf is None:
            return gf.BG_PAL[0]
        if modo == "auto":
            return gf.SPR_PAL[0] if self.graf.is_sprite(i) else gf.BG_PAL[0]
        if modo.startswith("fondo"):
            return gf.BG_PAL[int(modo[-1])]
        return gf.SPR_PAL[int(modo[-1])]

    def set_color(self, k):
        self.color = k
        self.refrescar_colores()

    def refrescar_colores(self):
        pal = self.paleta()
        for k, b in enumerate(self.color_buttons):
            if k == 0:
                b.config(bg="#404048", fg="#d0d0d0",
                         activebackground="#404048")
            else:
                b.config(bg=rgb_to_hex(pal[k]), fg="#101018",
                         activebackground=rgb_to_hex(pal[k]))
            b.config(relief="sunken" if k == self.color else "raised")

    def refrescar(self):
        if not self.graf:
            return
        self.lbl_path.config(text=self.graf.path or "-")
        self.refrescar_colores()
        self.refrescar_thumbs()
        self.refrescar_editor()

    def _resize_thumbs(self, event):
        """Recoloca las miniaturas cuando cambia el ancho del panel."""
        celda = 8 * self.thumb_scale + 14
        cols = max(1, (event.width - 8) // celda)
        if cols != self.thumb_cols:
            self.thumb_cols = cols
            self.refrescar_thumbs()
        self.canvas_thumbs.configure(scrollregion=self.canvas_thumbs.bbox("all"))

    def refrescar_thumbs(self):
        cv = self.canvas_thumbs
        cv.delete("all")
        self.thumb_photos = []
        self.thumb_rects = []
        if not self.graf:
            return
        celda = 8 * self.thumb_scale + 14
        cols = max(1, self.thumb_cols)
        for i in range(len(self.graf)):
            pal = self.paleta(i)
            img = gf.record_to_image(self.graf.get(i), pal, self.thumb_scale,
                                     transparente=False)
            photo = ImageTk.PhotoImage(img)
            self.thumb_photos.append(photo)
            col, fila = i % cols, i // cols
            x, y = col * celda + 4, fila * celda + 4
            tag = "rec%d" % i
            cv.create_image(x, y, image=photo, anchor="nw", tags=(tag,))
            cv.create_rectangle(x - 1, y - 1, x + 8 * self.thumb_scale,
                                y + 8 * self.thumb_scale,
                                outline="#606070" if i != self.sel else "#ffcc00",
                                tags=(tag,))
            cv.create_text(x + 8 * self.thumb_scale // 2, y + 8 * self.thumb_scale + 6,
                           text="%d" % i, fill="#c0c0d0", font=("Consolas", 7),
                           tags=(tag,))
            cv.tag_bind(tag, "<Button-1>", lambda e, k=i: self.seleccionar(k))
            self.thumb_rects.append((x - 1, y - 1))

    def refrescar_editor(self):
        if not self.graf:
            return
        i = self.sel
        rec = self.graf.get(i)
        pal = self.paleta(i)
        self.lbl_info.config(text="registro %d (%s)  offset %d"
                             % (i, "sprite" if self.graf.is_sprite(i) else "fondo",
                                i * gf.REC))
        # lienzo 8x8
        cv = self.canvas_edit
        cv.delete("all")
        z = self.zoom
        cv.configure(width=z * gf.W, height=z * gf.H)
        pix = gf.record_to_pixels(rec)
        for y in range(gf.H):
            for x in range(gf.W):
                idx = pix[y][x]
                if idx == 0:
                    col = "#303040"
                else:
                    col = rgb_to_hex(pal[idx])
                cv.create_rectangle(x * z, y * z, (x + 1) * z - 1, (y + 1) * z - 1,
                                    fill=col, outline="#181820")
        # grupo de 4
        base = (i // 4) * 4
        cv2 = self.canvas_grp
        cv2.delete("all")
        cv2.configure(width=z * 2 * gf.W, height=z * 2 * gf.H)
        for k in range(4):
            r = self.graf.get(min(base + k, len(self.graf) - 1))
            pix = gf.record_to_pixels(r)
            ox = (k % 2) * gf.W * z
            oy = (k // 2) * gf.H * z
            for y in range(gf.H):
                for x in range(gf.W):
                    idx = pix[y][x]
                    col = "#303040" if idx == 0 else rgb_to_hex(pal[idx])
                    cv2.create_rectangle(ox + x * z, oy + y * z,
                                         ox + (x + 1) * z - 1, oy + (y + 1) * z - 1,
                                         fill=col, outline="#181820")
        # volcado hex
        self.txt_hex.delete("1.0", "end")
        self.txt_hex.insert("1.0", "plano0  plano1\n")
        self.txt_hex.insert("end", gf.record_to_text(rec) + "\n")
        self.txt_hex.config(state="disabled")

    def refrescar_estado(self, msg=""):
        if msg:
            self.lbl_status.config(text=msg)

    # ------------------------------------------------------------------
    # Seleccion y pintura
    # ------------------------------------------------------------------
    def seleccionar(self, i):
        if not self.graf or i >= len(self.graf):
            return
        self.sel = i
        self.refrescar_thumbs()
        self.refrescar_editor()
        self.refrescar_estado("registro %d seleccionado" % i)

    def _paint(self, event):
        if not self.graf:
            return
        x = event.x // self.zoom
        y = event.y // self.zoom
        if not (0 <= x < gf.W and 0 <= y < gf.H):
            return
        col = 0 if event.num == 3 else self.color
        pix = gf.record_to_pixels(self.graf.get(self.sel))
        if pix[y][x] == col:
            return
        self._push_undo()
        pix[y][x] = col
        self.graf.set(self.sel, gf.pixels_to_record(pix))
        self.refrescar_thumbs()
        self.refrescar_editor()
        self.refrescar_estado("pintado (%d,%d) = color %d" % (x, y, col))

    def _push_undo(self):
        self.undo_stack.append([bytes(r) for r in self.graf.records])
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)

    def deshacer(self):
        if not self.undo_stack:
            self.refrescar_estado("no hay nada que deshacer")
            return
        estado = self.undo_stack.pop()
        self.graf.records = [bytearray(r) for r in estado]
        self.refrescar()
        self.refrescar_estado("deshecho")

    def copiar(self):
        if not self.graf:
            return
        self.clipboard = self.graf.get(self.sel)
        self.refrescar_estado("copiado el registro %d" % self.sel)

    def pegar(self):
        if not self.graf or self.clipboard is None:
            self.refrescar_estado("no hay nada en el portapapeles")
            return
        self._push_undo()
        self.graf.set(self.sel, self.clipboard)
        self.refrescar()
        self.refrescar_estado("pegado en el registro %d" % self.sel)

    def limpiar(self):
        if not self.graf:
            return
        self._push_undo()
        self.graf.set(self.sel, bytes(gf.REC))
        self.refrescar()
        self.refrescar_estado("registro %d vaciado" % self.sel)

    def set_zoom(self):
        try:
            self.zoom = max(4, min(32, int(self.spin_zoom.get())))
        except ValueError:
            self.zoom = ZOOM_DEFAULT
        self.spin_zoom.set(self.zoom)
        self.refrescar_editor()

    # ------------------------------------------------------------------
    # Fichero
    # ------------------------------------------------------------------
    def abrir(self, path=None, silencioso=False):
        if path is None:
            path = filedialog.askopenfilename(
                title="Abrir GRAF.DAT",
                initialdir=os.path.join(ROOT, "assets"),
                filetypes=[("GRAF.DAT", "*.DAT"), ("Todos", "*.*")])
            if not path:
                return
        try:
            self.graf = gf.GrafFile.load(path)
        except OSError as exc:
            messagebox.showerror("Abrir", "No se pudo abrir:\n%s" % exc)
            return
        self.undo_stack = []
        self.sel = 0
        self.refrescar()
        if not silencioso:
            self.refrescar_estado("abierto %s (%d registros)" % (path, len(self.graf)))

    def guardar(self):
        if not self.graf:
            return
        path = self.graf.path or os.path.join(ROOT, "assets", "GRAF.DAT")
        self._escribir(path)

    def guardar_como(self):
        if not self.graf:
            return
        path = filedialog.asksaveasfilename(
            title="Guardar como", defaultextension=".DAT",
            initialdir=os.path.join(ROOT, "assets"),
            initialfile=os.path.basename(self.graf.path or "GRAF.DAT"),
            filetypes=[("GRAF.DAT", "*.DAT"), ("Todos", "*.*")])
        if path:
            self._escribir(path)

    def _escribir(self, path):
        try:
            self.graf.save(path)
        except OSError as exc:
            messagebox.showerror("Guardar", "No se pudo guardar:\n%s" % exc)
            return
        self.refrescar_estado("guardado %s (copia en %s.bak)" % (path, path))

    def recargar(self):
        if not self.graf or not self.graf.path:
            return
        if not messagebox.askyesno("Recargar", "Descartar los cambios sin guardar?"):
            return
        self.abrir(self.graf.path, silencioso=True)

    # ------------------------------------------------------------------
    # PNG
    # ------------------------------------------------------------------
    def _ruta_export(self, sufijo):
        base = os.path.basename(self.graf.path or "GRAF.DAT")
        return filedialog.asksaveasfilename(
            title="Exportar PNG", defaultextension=".png", initialdir=os.path.join(ROOT, "doc"),
            initialfile="%s_%02d%s.png" % (base.split(".")[0], self.sel, sufijo),
            filetypes=[("PNG", "*.png")])

    def exportar_png(self):
        if not self.graf:
            return
        ruta = self._ruta_export("")
        if not ruta:
            return
        im = gf.record_to_image(self.graf.get(self.sel), self.paleta(), 16, transparente=True)
        im.save(ruta)
        self.refrescar_estado("exportado %s" % ruta)

    def exportar_png16(self):
        if not self.graf:
            return
        ruta = self._ruta_export("_16x16")
        if not ruta:
            return
        base = (self.sel // 4) * 4
        recs = [self.graf.get(base + k) for k in range(4) if base + k < len(self.graf)]
        im = gf.composite(recs, self.paleta(), 16, transparente=True)
        im.save(ruta)
        self.refrescar_estado("exportado %s" % ruta)

    def _importar(self, ruta, n):
        if not self.graf:
            return
        try:
            im = Image.open(ruta)
        except OSError as exc:
            messagebox.showerror("Importar", "No se pudo abrir la imagen:\n%s" % exc)
            return
        im = im.convert("RGBA")
        w, h = im.size
        if n == 1 and (w, h) == (2 * gf.W, 2 * gf.H):
            if messagebox.askyesno(
                    "Importar",
                    "La imagen es de 16x16.\n\n"
                    "Si: importarla como 4 registros (TL, TR, BL, BR).\n"
                    "No: importarla como un solo registro 8x8 (reducida)."):
                n = 4
        if n == 4 and (w, h) == (gf.W, gf.H):
            messagebox.showerror(
                "Importar",
                "La imagen es de 8x8: usaba el boton \"Importar PNG (8x8)\".")
            return
        pal = self.paleta()
        try:
            if n == 1:
                recs = [gf.image_to_record(im, pal)]
            else:
                recs = gf.image16_to_records(im, pal)
        except ValueError as exc:
            messagebox.showerror("Importar", str(exc))
            return
        if self.sel + len(recs) > len(self.graf):
            messagebox.showerror("Importar", "No caben %d registros a partir del %d."
                                 % (len(recs), self.sel))
            return
        self._push_undo()
        for k, rec in enumerate(recs):
            self.graf.set(self.sel + k, rec)
        self.refrescar()
        self.refrescar_estado("importado %s (%dx%d) en los registros %d..%d"
                              % (os.path.basename(ruta), w, h, self.sel,
                                 self.sel + len(recs) - 1))

    def importar_png(self):
        ruta = filedialog.askopenfilename(
            title="Importar patron 8x8", initialdir=os.path.join(ROOT, "doc"),
            filetypes=[("PNG", "*.png"), ("Todos", "*.*")])
        if ruta:
            self._importar(ruta, 1)

    def importar_png16(self):
        ruta = filedialog.askopenfilename(
            title="Importar patron 16x16 (4 registros)", initialdir=os.path.join(ROOT, "doc"),
            filetypes=[("PNG", "*.png"), ("Todos", "*.*")])
        if ruta:
            self._importar(ruta, 4)

    def _scroll_thumbs(self, event):
        self.canvas_thumbs.yview_scroll(-1 * (event.delta // 120), "units")


def main(argv):
    path = argv[1] if len(argv) > 1 else None
    app = Editor(path)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
