# AVENTURA

Homenaje al clasico **Adventure** de Atari 2600 para el core de video de
FPGA 6502 (`vc`). Programado en C con **cc65** y pensado para cargarse en el
monitor desde `$0800`.

![Pantalla de inicio](doc/pantalla.png)

## Objetivo

Recupera el **caliz** de la camara sellada del **Castillo Negro** y llevalo al
**pedestal de oro** del **Castillo de Oro** (habitacion inicial). Tienes 5
vidas.

## Controles

| Boton       | Accion                                  |
|-------------|-----------------------------------------|
| Joystick    | Mover al aventurero                     |
| Fuego       | Coger / soltar el objeto que este cerca |
| Fuego (victoria/derrota) | Reintentar                  |

El juego arranca directamente en el Castillo de Oro (sin pantalla de titulo).

Solo se puede llevar **un objeto a la vez**. Las llaves se consumen solas al
tocar su puerta correspondiente: las puertas se abren para siempre.

## Como jugar (progresion recomendada)

1. **Castillo de Oro**: coge la **llave amarilla** y abre la puerta norte.
2. En el bosque baja por el **agujero** de la sala *Entrada* para ir a las
   catacumbas, pero antes recoge la **espada** (Bosque 5) y el **puente**
   (Bosque 6).
3. **Catacumbas**:
   - Coge el **iman** (Catac. 2).
   - Coloca el **puente** sobre la pared central de Catac. 3 para cruzar.
   - Recoge la **llave blanca** (Catac. 4).
4. Vuelve al bosque. En *Bosque 4* la **llave blanca** abre la puerta norte
   del **Castillo Blanco**; dentro esta la **llave negra** (cuidado con el
   dragon amarillo: la espada los mata).
5. En la sala del **Foso**, coloca el **puente** sobre el agua. La **llave
   negra** abre la puerta norte del **Castillo Negro**.
6. Con el **iman**, atrae el caliz a traves del muro de la camara sellada.
   Cuando lo tengas cerca, pulsa fuego para cambiar el iman por el caliz.
7. Lleva el **caliz** al pedestal del Castillo de Oro y gana.

## Mapa de habitaciones

Rejilla del mundo exterior (indice = fila * 4 + columna):

```
+------------+------------+------------+------------+
| 0 BOSQUE 1 | 1 BOSQUE 2 | 2 CAST.NEGRO| 3 CAST.BLANCO
|  E,S       |  W,S       |  S (negra) |  S (blanca)
+------------+------------+------------+------------+
| 4 BOSQUE 3 | 5 ENTRADA  | 6 FOSO     | 7 BOSQUE 4
| N,E,S      | agujero    | N (negra)  | N (blanca)
| S (amarilla)            | agua       |
+------------+------------+------------+------------+
| 8 CAST.ORO | 9 BOSQUE 5 | 10 BOSQUE 6| 11 BOSQUE 7
| inicio     | espada     | puente     |            |
| N (amarilla)                          |
+------------+------------+------------+------------+
```

Catacumbas (se accede por el agujero de la sala 5):

```
12 CATAC.1 <-> 13 CATAC.2 <-> 14 CATAC.3 <-> 15 CATAC.4
 escaleras      iman           muro+puente     llave blanca
                dragon verde
```

## Objetos y enemigos

- **Caliz**: camara sellada del Castillo Negro (se saca con el iman). Usa el
  diseno **con asas** (patron de sprite 0) y borde blanco para distinguirse.
- **Espada**: Bosque 5. Hoja blanca y empuñadura dorada. Mata dragones al
  tocarlos (tambien tirada en el suelo).
- **Puente**: Bosque 6. Se coloca sobre agua o sobre la pared de Catac. 3.
  Tiene **dos sprites**: vertical en el Foso (cruce arriba/abajo) y horizontal
  en Catac. 3 (cruce izquierda/derecha).
- **Iman**: Catac. 2. Herradura roja con polos blancos; atrae el caliz a traves
  de los muros con movimiento continuo (1 px por frame).
- **Llave amarilla**: Castillo de Oro. Abre la puerta norte de ese castillo.
- **Llave blanca**: Catac. 4. Abre la puerta del Castillo Blanco.
- **Llave negra**: Castillo Blanco. Abre la puerta del Castillo Negro.
- **Dragones**: rojo (Castillo Negro), verde (Catac. 2), amarillo (Castillo
  Blanco). Ahora **te persiguen** y, si huyes con uno cerca, **te sigue a la
  sala siguiente**. Matan al tocarte si no llevas la espada.
- **Murcielago**: Bosque 3. Ahora **te persigue**, te **roba el objeto** que
  lleves y **huye unos instantes** tras tocarte; **no quita vida**. El dragon
  sigue siendo el enemigo realmente peligroso.

Los dragones usan el diseño **Poison Drake** del pack, a 16x16, recoloreado en
rojo/verde/dorado y con **volteo horizontal** según la dirección en que vuelan:

![Poison Drake en el juego](doc/dragon.png)

## Compilar

Requiere [cc65](https://cc65.github.io/) en `D:/cc65` (o pasa `CC65_HOME`).

```sh
make CC65_HOME=D:/cc65
```

Genera:

- `output/aventura.bin` (13461 bytes, se carga en `$0800`)
- `output/aventura.map` (mapa de memoria)
- `assets/GRAF.DAT` (1024 bytes: 64 registros de 16 bytes; 22 tiles de fondo + 42 sprites)

## Cargar en el emulador

La SD debe contener **`GRAF.DAT`** ademas del binario. Para inyectarlo en la
imagen del emulador (una sola vez):

```sh
python D:/Proyectos/EmuladorFpga6502/tools/sd_tool.py inject tarjeta.img assets/GRAF.DAT GRAF.DAT
```

Con el monitor en marcha y la SD montada:

```
LOAD AVENTURA.BI 0800
R 0800
```

> MicroFS limita los nombres a 11 caracteres, por eso el fichero aparece como
> `AVENTURA.BI` (no `AVENTURA.BIN`).

Si falta `GRAF.DAT`, el juego muestra **`FALTA GRAF.DAT / COPIALO EN LA SD`** y
se detiene: sin patrones no hay graficos.

## Detalles tecnicos

- Objetivo `none` de cc65, CPU 6502. Binario autocontenido cargado en `$0800`.
- Pantalla de texto 40x30. HUD en filas 1-2 y pista en la 28; juego en 3-27.
- El jugador y los dragones son objetos **16x16 (2x2 sprites)** dibujados con
  `vc_sprite16_set()`. El jugador (caballero azul + oro) tiene 4 patrones por
  direccion y **2 fotogramas de caminar** para izquierda/derecha (24 patrones
  en total); los dragones usan el diseño **Poison Drake** con **2 fotogramas de
  aleteo** y la direccion izquierda se dibuja **espejada por codigo** (FLIP_X +
  intercambio de cuadrantes) para no duplicar patrones.
- IA de dragones: persiguen al jugador por ambos ejes (deslizan por las paredes)
  y, si huyes con uno a menos de 64 px, te sigue a la sala siguiente. Emiten
  gruñidos cuando estan cerca y un rugido al entrar contigo.
- Sprites: jugador en los slots OAM 12-15, dragones en 16-19, objetos en
  1-11 y el murcielago en el 20 (dibujado encima del jugador). Como maximo
  8 sprites por scanline; hay 32 en OAM.
- Para evitar parpadeos por la carrera con VBLANK, solo se apagan los slots
  que no se redibujan ese frame; la llave y los objetos se sobrescriben cada
  frame. El jugador no parpadea (la invulnerabilidad no lo oculta).
- La celda donde esta el jugador siempre es transitable: si recoges el puente
  estando encima, puedes salir de la pared. Al soltarlo cerca de su sitio, se
  repone en la pared en vez de caer al lado.
- **Los patrones de sprites y tiles ya no viven en el binario**: se cargan al
  arrancar desde `GRAF.DAT` (SD) con la ROM API (`rom_mfs_open` /
  `rom_mfs_read_via_zp` / `rom_mfs_close`), en streaming de 16 bytes, y se
  escriben directamente en la VRAM con `vc_load_spr_pattern` /
  `vc_load_bg_pattern`. Solo se usa un buffer de 16 bytes en RAM; el binario
  queda en **13.461 bytes**.
- El **agujero** de la sala 5, la **escalera** de Catacumbas 1 y el **altar**
  del caliz son imagenes de **16x16 formadas por 4 tiles de fondo** cada una
  (no un tile repetido):
  - agujero: marco de madera y escalera de mano (paleta 1, `0x8A-0x8D`);
  - escalera: piedra gris (paleta 3, `0x8E-0x91`);
  - altar: mesa de patas en perfil (paleta 1, `0x92-0x95`), con el patron del
    suelo del castillo como fondo para que no quede dentro de un cuadrado.
  Las hojas de diseno estan en `doc/hole_options.png` y
  `doc/pedestal_options.png`.
- HUD: las vidas se muestran como **corazones** (sprite 41, paleta 2, slots OAM
  21-25) y al lado de `LLEVA` aparece el **icono del objeto** que llevas (slot
  26). Ambos se redibujan cuando cambia el HUD, sin tocar la RAM del juego.
- No hay pantalla de titulo (se recorto para liberar RAM); el juego arranca
  directamente en el Castillo de Oro.
- El HUD usa nombres de sala cortos (B1, C2, ORO...) y pistas de una palabra
  para ahorrar RAM.
- Los tiles de fondo personalizados viven fuera de `$20-$7F`.
- VRAM y OAM se escriben en VBLANK a traves de `lib/vc.lib`.
- Colision por software con un unico punto central `(x+4, y+4)` contra la
  rejilla de celdas; asi se puede cruzar el puente de forma fiable.
- Sonido SID no bloqueante (`sound.c`): recoger/soltar, llave, gruñido, rugido,
  muerte y victoria. El ancho de pulso se fija a ~50% (si es 0, el pulso no
  suena en el SID).
- Para que todo quepa en RAM se enlaza contra la **libreria modular** de
  `videocore-6502-cc65` (`video.o`, `gfx_vram.o`, `gfx_tiles.o`, `gfx_text.o`,
  `gfx_pal.o`). Al no usar `vc_sprite_disable` (se apaga el sprite escribiendo
  OAM directamente) se descartan `gfx.o` y `collide.o`, ahorrando ~400 bytes.

- Las islas verdes del bosque usan el tile de fondo `0x81` rediseñado como
  **árbol** (copa verde, sombra y tronco). Al ser tile de fondo no consume OAM
  ni patrones de sprite extra; también decora el borde del bosque.

![Bosque con islas de árboles](doc/bosque.png)

Mapa de memoria final:

| Segmento | Inicio | Fin    |
|----------|--------|--------|
| ZEROPAGE | `$0020`| `$0065`|
| CODE     | `$0847`| `$38F8`|
| RODATA   | `$38F9`| `$3C94`|
| BSS      | `$3C95`| `$3D0D`|

Termina en `$3D0D`, dejando unos **625 bytes libres** en la zona RAM del
programa (la pila de cc65 tiene ademas sus 256 bytes en `$3F7F-$3FFF`).

## Herramienta de pruebas

`tools/emu_play.py` ayuda a probar en el emulador de forma sincronizada
(posiciona el jugador por coordenadas en vez de por tiempo, porque la tasa de
frames del emulador varia):

```sh
python tools/emu_play.py state                 # estado actual
python tools/emu_play.py obj                   # posicion de los objetos
python tools/emu_play.py walk left 96          # moverse hasta px <= 96
python tools/emu_play.py seq "walk:up:72;tap:fire:140"
```

`tools/gen_player_A.py` genera el caballero A en 4 direcciones (azul + oro), y
`tools/gen_poison_drake.py` extrae el Poison Drake del pack y genera sus
patrones (1 frame + 2 direcciones):

```sh
python tools/gen_player_A.py preview     # doc/player_A_game.png
python tools/gen_player_A.py c           # patrones para game.c
python tools/gen_poison_drake.py c       # patrones + doc/poison_drake_ingame.png
```

`tools/dragon_pack_sheet.py` y `tools/dragon_pack_quant.py` generan las hojas
comparativas del Basic Asset Pack.
