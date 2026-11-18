#!/usr/bin/env python3
"""Helper para probar Aventura en el emulador de forma robusta.

El emulador corre a una tasa de frames variable, asi que NO usamos tiempos
fijos: mantenemos la direccion pulsada y sondeamos la RAM hasta alcanzar el
objetivo, cambiar de habitacion o quedarnos bloqueados.

Uso:
  python emu_play.py state
  python emu_play.py tap <press> [hold_ms]      # pulso corto
  python emu_play.py walk <up|down|left|right> <limite> [max_ms]
      - left : avanza hasta px <= limite
      - right: avanza hasta px >= limite
      - up   : avanza hasta py <= limite
      - down : avanza hasta py >= limite
      Para cruzar una salida usa un limite fuera de pantalla (p.ej. 320).
  python emu_play.py seq "cmd;cmd;..."          # varios comandos
      cmd = walk:dir:lim  |  tap:press:ms
"""
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8080"
import os
import re

MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "output", "aventura.map")


def bss_base():
    """Lee la direccion de BSS del mapa para no hardcodearla."""
    try:
        with open(MAP_PATH, "r", encoding="latin-1") as f:
            for line in f:
                parts = line.split()
                if (len(parts) >= 3 and parts[0] == "BSS"
                        and "Offs=" not in parts[1]):
                    return int(parts[1], 16)
    except OSError:
        pass
    return 0x3B0D


BSS = bss_base()
# Orden de variables static en game.c (pat_buf[16] + graf_ok delante)
OFF_STATE = 17
OFF_ROOM = 18
OFF_PX = 19
OFF_PY = 21
OFF_FACE = 22
OFF_CARRY = 23
OFF_LIVES = 24
OFF_INVULN = 25
OFF_FRAME = 26
OFF_STEAL = 28
OFF_HUD = 29
OFF_GATES = 30
OFF_MENU = 33
OFF_OBJROOM = 34
OFF_OBJX = 45
OFF_OBJY = 67
OFF_OBJACT = 78


def get(path):
    return urllib.request.urlopen(BASE + path, timeout=10).read()


def state():
    d = get(f"/ram.bin?start=0x{BSS + OFF_STATE:x}&len=14")
    room = d[OFF_ROOM - OFF_STATE]
    px = d[OFF_PX - OFF_STATE] | (d[OFF_PX - OFF_STATE + 1] << 8)
    py = d[OFF_PY - OFF_STATE]
    face = d[OFF_FACE - OFF_STATE]
    carry = d[OFF_CARRY - OFF_STATE]
    lives = d[OFF_LIVES - OFF_STATE]
    invuln = d[OFF_INVULN - OFF_STATE]
    frame = d[OFF_FRAME - OFF_STATE]
    gates = list(get(f"/ram.bin?start=0x{BSS + OFF_GATES:x}&len=3"))
    return {
        "room": room, "px": px, "py": py, "face": face, "carry": carry,
        "lives": lives, "invuln": invuln, "frame": frame,
        "gates": gates,
    }


def objects():
    rooms = list(get(f"/ram.bin?start=0x{BSS + OFF_OBJROOM:x}&len=11"))
    xb = get(f"/ram.bin?start=0x{BSS + OFF_OBJX:x}&len=22")
    yb = get(f"/ram.bin?start=0x{BSS + OFF_OBJY:x}&len=11")
    act = list(get(f"/ram.bin?start=0x{BSS + OFF_OBJACT:x}&len=11"))
    xs = [xb[i * 2] | (xb[i * 2 + 1] << 8) for i in range(11)]
    out = []
    for i in range(11):
        out.append((i, rooms[i], xs[i], yb[i], act[i]))
    return out


def show_objs():
    for i, r, x, y, a in objects():
        print(f"obj{i}: room={r} x={x} y={y} active={a}")


def show(s):
    print(f"room={s['room']} px={s['px']} py={s['py']} face={s['face']} "
          f"carry={s['carry']} lives={s['lives']} invuln={s['invuln']} "
          f"frame={s['frame']} gates={s['gates']}")


def press(name, hold=0):
    get(f"/joy?press={name}&hold={hold}")


def release():
    get("/joy?release=1")


def tap(name, hold=120):
    press(name, hold)
    time.sleep((hold + 60) / 1000.0)
    release()


def walk(direction, limit, max_ms=4000):
    start = state()
    start_room = start["room"]
    press(direction, 0)
    t0 = time.time()
    last = (start["px"], start["py"], start["room"])
    stable = 0
    s = start
    while True:
        time.sleep(0.04)
        s = state()
        cur = (s["px"], s["py"], s["room"])
        done = False
        if s["room"] != start_room:
            done = True
        elif direction == "left" and s["px"] <= limit:
            done = True
        elif direction == "right" and s["px"] >= limit:
            done = True
        elif direction == "up" and s["py"] <= limit:
            done = True
        elif direction == "down" and s["py"] >= limit:
            done = True
        elif cur == last:
            stable += 1
            if stable >= 6:  # ~240 ms sin avanzar => bloqueado
                done = True
        else:
            stable = 0
        last = cur
        if done or (time.time() - t0) * 1000 > max_ms:
            break
    release()
    time.sleep(0.1)
    return state()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "state":
        show(state())
        return 0
    if cmd == "obj":
        show_objs()
        return 0
    if cmd == "tap":
        name = sys.argv[2]
        hold = int(sys.argv[3]) if len(sys.argv) > 3 else 120
        tap(name, hold)
        show(state())
        return 0
    if cmd == "walk":
        d = sys.argv[2]
        lim = int(sys.argv[3])
        mx = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
        print(f"[walk {d} {lim}] ", end="")
        show(walk(d, lim, mx))
        return 0
    if cmd == "seq":
        # Comandos separados por ';' ->  walk:dir:lim  |  tap:press:ms
        for token in sys.argv[2].split(";"):
            token = token.strip()
            if not token:
                continue
            parts = token.split(":")
            if parts[0] == "walk":
                print(f"[{token}] ", end="")
                show(walk(parts[1], int(parts[2]),
                          int(parts[3]) if len(parts) > 3 else 4000))
            elif parts[0] == "tap":
                tap(parts[1], int(parts[2]) if len(parts) > 2 else 120)
                print(f"[{token}] ", end="")
                show(state())
            elif parts[0] == "wait":
                time.sleep(int(parts[1]) / 1000.0)
                print(f"[{token}] ", end="")
                show(state())
        return 0
    print("comando desconocido")
    return 2


if __name__ == "__main__":
    sys.exit(main())
