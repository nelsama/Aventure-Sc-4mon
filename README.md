# AVENTURA

Homenaje al clasico **Adventure** de Atari 2600 para el core de video de
FPGA 6502 (`vc`). Programado en C con **cc65** y pensado para cargarse en el
monitor desde `$0800`.

> **Dependencia de `AVENTUR.DAT`:** el binario **no** lleva los graficos dentro:
> al arrancar carga los patrones de tiles y sprites desde **`AVENTUR.DAT`** en la
> SD. El fichero esta incluido en el repositorio (`assets/AVENTUR.DAT`, 1024
> bytes) y hay que copiarlo a la SD junto al binario. Si falta, el juego muestra
> `FALTA AVENTUR.DAT / COPIALO EN LA SD` y se detiene.

![Menu inicial](doc/menu.png)

![En el juego](doc/pantalla.png)

## Objetivo

Recupera el **caliz** de la camara sellada del **Castillo Negro** y llevalo al
**pedestal de oro** del **Castillo de Oro** (habitacion inicial). Tienes 3
vidas.

## Controles

| Boton       | Accion                                  |
|-------------|-----------------------------------------|
| Joystick arriba/abajo | Elegir opcion en el menu       |
| Fuego       | Confirmar la opcion del menu            |
| Joystick    | Mover al aventurero                     |
| Fuego       | Coger / soltar el objeto que este cerca |

Al arrancar aparece el **menu** con dos opciones: **JUGAR** empieza una partida
y **SALIR** termina el programa igual que el comando `QB` del monitor (reset con
autoboot, ver [Cargar en el emulador](#cargar-en-el-emulador)). Cuando pierdes
las 3 vidas o dejas el caliz en el pedestal vuelves a ese mismo menu, que muestra
el aviso `GAME OVER` o `VICTORIA!` en la fila 18.

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
6. Con el **iman**, atrae el caliz, la espada o las llaves a traves de los muros.
   Cuando el objeto este cerca, pulsa fuego para cambiar el iman por el.
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

Al subir por las escaleras de Catac. 1 vuelves a la sala *Entrada* (apareces
encima del agujero). Tanto al subir como al bajar suena un efecto de **pasos**:
tres golpes que ascienden al subir y descienden al bajar.

## Objetos y enemigos

- **Caliz**: camara sellada del Castillo Negro (se saca con el iman). Usa el
  diseno **con asas** (patron de sprite 0) y borde blanco para distinguirse.
- **Espada**: Bosque 5. Hoja blanca y empuñadura dorada. Mata dragones al
  tocarlos (tambien tirada en el suelo).
- **Puente**: Bosque 6. Se coloca sobre agua o sobre la pared de Catac. 3.
  Tiene **dos sprites**: vertical en el Foso (cruce arriba/abajo) y horizontal
  en Catac. 3 (cruce izquierda/derecha).
- **Iman**: Catac. 2. Herradura roja con polos blancos; atrae el **caliz, la
  espada y las tres llaves** a traves de los muros con movimiento continuo (1 px
  por frame). Atrae tanto **en la mano** (los objetos van al jugador) como
  **tirado en el suelo** (los objetos van hacia el iman). Pulsa fuego para
  cambiar el iman por el objeto atraido mas cercano.
- **Llave amarilla**: Castillo de Oro. Abre la puerta norte de ese castillo.
- **Llave blanca**: Catac. 4. Abre la puerta del Castillo Blanco.
- **Llave negra**: Castillo Blanco. Abre la puerta del Castillo Negro.
- **Dragones**: rojo (Castillo Negro), verde (Catac. 2), amarillo (Castillo
  Blanco). Ahora **te persiguen** y, si huyes con uno cerca, **te sigue a la
  sala siguiente**. Matan al tocarte si no llevas la espada.
- **Murcielago**: Bosque 3. Ahora **te persigue** y te **roba el objeto** que
  lleves. Mientras huye, el objeto **vuela pegado a el**; tienes que alcanzarlo
  y pulsar **fuego** para quitarselo. **No quita vida**. El dragon sigue siendo
  el enemigo realmente peligroso.

Los dragones usan el diseño **Poison Drake** del pack, a 16x16, recoloreado en
rojo/verde/dorado y con **volteo horizontal** según la dirección en que vuelan:

![Poison Drake en el juego](doc/dragon.png)

## Compilar

Requiere [cc65](https://cc65.github.io/) en `D:/cc65` (o pasa `CC65_HOME`).

```sh
make CC65_HOME=D:/cc65
```

Genera:

- `output/aventura.bin` (13980 bytes, se carga en `$0800`)
- `output/aventura.map` (mapa de memoria)

`make` **no genera los graficos**: el binario usa `assets/AVENTUR.DAT` (1024
bytes: 64 registros de 16 bytes = 22 tiles de fondo + 42 sprites), que ya viene
en el repositorio y hay que copiar a la SD junto al binario.

## Cargar en el emulador

La SD debe contener **`AVENTURA.BI`** (el binario), **`AVENTUR.DAT`** (los
patrones) y, si quieres que funcione la opcion **SALIR** / el autoboot,
**`BOOT.INI`** con el texto `AVENTURA.BI`. Si aun no tienes la imagen de SD del
emulador, creala de 16 MB y copia los tres ficheros:

```sh
python D:/Proyectos/EmuladorFpga6502/tools/sd_tool.py format tarjeta.img 16
python D:/Proyectos/EmuladorFpga6502/tools/sd_tool.py inject tarjeta.img assets/AVENTUR.DAT AVENTUR.DAT
python D:/Proyectos/EmuladorFpga6502/tools/sd_tool.py inject tarjeta.img output/aventura.bin AVENTURA.BI
python D:/Proyectos/EmuladorFpga6502/tools/sd_tool.py inject tarjeta.img assets/BOOT.INI BOOT.INI
```

Con el monitor en marcha y la SD montada:

```
LOAD AVENTURA.BI 0800
R 0800
```

> MicroFS limita los nombres a **11 caracteres**, por eso el fichero aparece
> como `AVENTURA.BI` (no `AVENTURA.BIN`) y los patrones se llaman
> `AVENTUR.DAT` (no `AVENTURA.DAT`, que son 12 y no caben).

**Salir y autoboot:** `SALIR` escribe `0` en `$C004` y salta a la rutina de
reset, exactamente lo que hace `QB` en el monitor. Si la SD tiene `BOOT.INI`, el
firmware vuelve a cargar y ejecutar `AVENTURA.BI` (vuelves al menu); si no lo
tiene, el reset deja el **prompt del monitor**. MicroFS admite **16 ficheros**:
si la SD esta llena hay que borrar alguno antes de copiar `BOOT.INI`.

Si falta `AVENTUR.DAT`, el juego muestra **`FALTA AVENTUR.DAT / COPIALO EN LA
SD`** y se detiene: sin patrones no hay graficos.

## Graficos (`AVENTUR.DAT`)

`assets/AVENTUR.DAT` es un fichero plano de 1024 bytes dividido en 64 registros de
16 bytes. Cada registro es un patron 8x8 con **dos planos** (8 B de plano 0 +
8 B de plano 1, color 0-3):

- registros 0-9: tiles de fondo base (suelo, hierba, agua, muro...);
- registros 10-13: **agujero**; 14-17: **escalera**; 18-21: **altar** (4 tiles
  16x16 cada uno);
- registros 22-63: **42 patrones de sprite** (jugador, dragones, objetos, caliz,
  corazon del HUD...).

**El `.dat` no guarda los colores RGB**, solo el indice 0-3 de cada pixel (el
color 0 es transparente). Los colores estan en `game.c` (`bg_pal[4][4]` y
`spr_pal[4][4]`, lineas 115-129) y se suben a la RAM de paletas del core de
video al arrancar (`vc_pal_load_bg` / `vc_pal_load_spr`). Por eso el mismo
patron puede verse en colores distintos: los tres dragones usan los mismos 8
registros (54-61) y solo cambia la paleta con la que se dibujan (`obj_pal`:
rojo=2, verde=3, dorado=1).

Para cambiar un color hay que tocar `game.c` (y recompilar), no el `.dat`. El
editor lee las paletas de `game.c` automaticamente, asi que la vista previa es
siempre la real, y tiene en cuenta que el hardware solo guarda 4 bits por canal
(RGB444) y los expande con `(v << 4) | v`: asi `0x2E5BFF` (azul del caballero)
se ve como `#2255FF` y `0x00AA44` (hierba) se queda en `#00AA44`.

El caballero (casco azul con visera y penacho dorado) ocupa los 24 registros
30-53: una imagen de 2x2 por direccion mas dos fotogramas de caminar hacia cada
lado. Las hojas de referencia de esos fotogramas, exportadas con el propio
editor, estan en `doc/GRAF_38_16x16.png` (de frente a la derecha),
`doc/GRAF_38_16x16_left.png` (a la izquierda) y
`doc/GRAF_38_16x16_rigth_walk.png` (caminando a la derecha).

El juego lo lee al arrancar con `rom_mfs_open` / `rom_mfs_read_via_zp` /
`rom_mfs_close`, en streaming de 16 bytes, y lo escribe en la VRAM con
`vc_load_bg_pattern` / `vc_load_spr_pattern`. Solo usa 16 bytes de buffer en
RAM, asi que los graficos no ocupan ni RODATA ni RAM.

Si cambias un diseno, vuelve a escribir `AVENTUR.DAT` y copialo a la SD:

```sh
python tools/gen_hud.py                    # corazon del HUD (sprite 41)
python tools/mock_hole.py --write-graf     # agujero (0x8A-0x8D) y escalera (0x8E-0x91)
python tools/mock_pedestal.py --write-graf # altar (0x92-0x95)
python tools/mock_chalice.py --write-graf  # caliz con asas (sprite 0)
```

### Editor grafico (GUI)

Para **extraer** y **anadir** patrones sin tocar el binario a mano hay una
aplicacion de escritorio (Tkinter, sin instalar nada mas que Pillow):

```sh
python tools/graf_editor.py            # abre assets/AVENTUR.DAT
python tools/graf_editor.py otro.dat   # o cualquier otro fichero
python tools/graf_editor.py assets/AVENTUR.DAT 36   # abre con un registro elegido
```

En Windows tambien se puede lanzar con doble clic en `tools/graf_editor.bat`.

![Editor de AVENTUR.DAT](doc/graf_editor.png)

- Miniaturas de los 64 registros (22 de fondo + 42 de sprites) con la **paleta
  real del juego**; se puede forzar otra paleta desde el desplegable.
- La **paleta cambia sola al seleccionar un patron**: es la que le pone el juego
  (hoyo en madera, escalera en gris, altar en oro, jugador en azul/oro, iman y
  dragon en rojo, corazon en rojo...). Los botones de color y la vista previa
  siguen esa paleta, y el desplegable permite forzar otra para ver como
  quedaria con otros colores.
- Las paletas **se leen de `game.c` al arrancar** (no estan copiadas dentro del
  editor) y se convierten igual que el hardware: `VC_RGB888` se queda con el
  nibble alto de cada canal (RGB444) y el core lo expande con `(v << 4) | v`.
  Asi la vista previa coincide pixel a pixel con la pantalla: el azul del
  caballero `0x2E5BFF` se ve `#2255FF`, no `#EEBBFF`.
- Pintar pixel a pixel el registro elegido: **clic izquierdo** pinta el color
  marcado y **clic derecho** pone el color 0 (transparente). Junto al patrón
  hay botones para **Limpiar** (vaciarlo), **Todo color 1** y **Todo color 2**
  (rellenarlo de un color), un **Flip horizontal** (espeja el patrón) y una
  **cruceta de flechas** (▲ ◄ ▼ ►) a la derecha del patrón que lo desplazan un
  píxel; las flechas del teclado hacen lo mismo cuando el lienzo tiene el foco.
  El desplazamiento **no da la vuelta**: lo que sale por un lado se pierde y por
  el otro entra el color 0 (transparente).
- Vista del **grupo de 4 registros** que forma cada imagen de 16x16 (hoyo,
  escalera, altar, jugador, dragones). Cada cuadrante (TL, TR, BL, BR) tiene su
  propio selector para **elegir que patron se pone en cada uno**, asi que se
  pueden componer imagenes 16x16 con patrones de cualquier parte del fichero:
  - al seleccionar un registro, el grupo se ajusta solo a la imagen a la que
    pertenece (por ejemplo, el registro 11 es la parte superior derecha del
    agujero);
  - clic en un cuadrante del mosaico: edita ese patron;
  - **Aplicar a 4 registros**: escribe los 4 patrones del grupo en los 4
    registros de la imagen (con confirmacion y deshacer);
  - **Flip horizontal**: espeja el mosaico entero (espeja cada cuadrante e
    intercambia TL<->TR y BL<->BR) y lo escribe en los 4 registros de la imagen;
  - **Exportar PNG (16x16)** exporta el mosaico tal y como se ve, con la paleta
    de cada patron.
- **Exportar PNG (8x8)** y **Exportar PNG (16x16)**: saca el patron como imagen
  con la paleta del juego.
- **Importar PNG (8x8)** y **Importar PNG (16x16)**: una imagen de 16x16 entra
  como 4 registros (TL, TR, BL, BR) y una de 8x8 como un registro. Los pixeles
  se ajustan al color mas cercano de la paleta.
- Volcado hexadecimal de los dos planos del registro, copiar, pegar y deshacer.
- Al guardar deja una copia `AVENTUR.DAT.bak` y avisa en la barra de estado.
- **Enviar a la SD y reiniciar**: copia el `AVENTUR.DAT` a la tarjeta SD del
  emulador y reinicia la partida (el juego lee los patrones de la SD **solo al
  arrancar**, asi que sin reiniciar no se ve ningun cambio). Ojo: el emulador
  guarda su propia copia del sistema de ficheros de la SD en memoria y puede
  volcarla sobre `tarjeta.img`, asi que el editor escribe el fichero por el
  protocolo del propio emulador (`/sdcard/write`, que ya remonta la tarjeta) y
  solo recurre a `sd_tool.py` si el emulador esta apagado. El reinicio se pide
  con un `POST /run` (con el binario de vuelta) porque el servidor del emulador
  reutilizaba el cuerpo de la peticion anterior en las peticiones que no eran
  POST (fallo corregido en el emulador, commit `ef9aeec`): con un `GET` el
  `.dat` acababa escrito en la SD con el nombre del binario y lo corrompia.

La logica del formato esta separada en `tools/graf_format.py` (no depende de
Tkinter), por si se quiere usar desde la linea de ordenes:

```sh
python tools/graf_format.py assets/AVENTUR.DAT   # volcado de los 64 registros
```

## Detalles tecnicos

- Objetivo `none` de cc65, CPU 6502. Binario autocontenido cargado en `$0800`.
- Pantalla de texto 40x30. HUD en filas 1-2 y pista en la 28; juego en 3-27.
- El jugador y los dragones son objetos **16x16 (2x2 sprites)**. El jugador
  (caballero azul + oro) tiene 4 patrones por direccion y **2 fotogramas de
  caminar** para izquierda/derecha (24 patrones en total); los dragones usan el
  diseno **Poison Drake** con **2 fotogramas de aleteo** y la direccion
  izquierda se dibuja **espejada por codigo** (FLIP_X + intercambio de
  cuadrantes) para no duplicar patrones.
- El dibujo 16x16 (`draw16_fast`) escribe en cada frame solo X/Y/FLAGS de los 4
  cuadrantes; los TILES se reescriben solo cuando cambia el patron o el
  espejado. Antes cada cuadrante escribia tambien COLL y los tiles, y el
  dragon se quedaba fuera del VBLANK.
- IA de dragones: persiguen al jugador por ambos ejes (deslizan por las paredes)
  y, si huyes con uno a menos de 64 px, te sigue a la sala siguiente. Emiten
  gruñidos cuando estan cerca y un rugido al entrar contigo.
- Sprites: jugador en los slots OAM 12-15, dragones en 16-19, objetos en
  1-11 y el murcielago en el 20 (dibujado encima del jugador). Como maximo
  8 sprites por scanline; hay 32 en OAM.
- Para evitar parpadeos por la carrera con VBLANK, `draw_actors()` se llama
  justo despues de `vc_wait_vblank()` y antes de leer el joystick/actualizar el
  juego. El dragon se dibuja el primero, con `draw16_fast`, y sus slots no se
  apagan antes si esta presente; asi sus 4 sprites se escriben dentro del
  VBLANK. El jugador no parpadea (la invulnerabilidad no lo oculta).
- La celda donde esta el jugador siempre es transitable: si recoges el puente
  estando encima, puedes salir de la pared. Al soltarlo cerca de su sitio, se
  repone en la pared en vez de caer al lado.
- **Los patrones de sprites y tiles ya no viven en el binario**: se cargan al
  arrancar desde `AVENTUR.DAT` (SD) con la ROM API (`rom_mfs_open` /
  `rom_mfs_read_via_zp` / `rom_mfs_close`), en streaming de 16 bytes, y se
  escriben directamente en la VRAM con `vc_load_spr_pattern` /
  `vc_load_bg_pattern`. Solo se usa un buffer de 16 bytes en RAM; el binario
  queda en **13.980 bytes**.
- El **agujero** de la sala 5, la **escalera** de Catacumbas 1 y el **altar**
  del caliz son imagenes de **16x16 formadas por 4 tiles de fondo** cada una
  (no un tile repetido):
  - agujero: marco de madera y escalera de mano (paleta 1, `0x8A-0x8D`);
  - escalera: piedra gris (paleta 3, `0x8E-0x91`);
  - altar: mesa de patas en perfil (paleta 1, `0x92-0x95`), con el patron del
    suelo del castillo como fondo para que no quede dentro de un cuadrado.
  Las hojas de diseno estan en `doc/hole_options.png` y
  `doc/pedestal_options.png`.
- HUD: las vidas se muestran como **corazones** (sprite 41, paleta 2, uno por
  vida en los slots OAM 21-25) y al lado de `LLEVA` aparece el **icono del
  objeto** que llevas (slot 26). Ambos se redibujan cuando cambia el HUD, sin
  tocar la RAM del juego.
- **Menu inicial** en modo texto (`ST_MENU`): `JUGAR` llama a `start_game()` y
  `SALIR` escribe `0` en `$C004` y hace `JMP ($FFFC)`, el mismo reset con
  autoboot que `QB`. Solo ocupa un byte de RAM (`menu_sel`). Al ganar o perder,
  `ST_WIN` / `ST_OVER` vuelven al menu y pintan `VICTORIA!` o `GAME OVER` en la
  fila 18; el aviso usa la paleta 1 porque el color 3 de la paleta 3 es el
  `BG_COLOR` global (el texto saldria invisible).
- **Ojo con la BSS y la ROM API:** `load_patterns()` llama a la ROM API, que usa
  su **propia pila** (la del monitor, en `$3E00-$3FFF`) y puede dejar basura en
  la BSS del juego. Por eso `menu_sel` se pone a 0 en `main` **despues** de
  cargar los patrones; el resto del estado lo inicializa `start_game()`.
- El HUD usa nombres de sala cortos (B1, C2, ORO...) y pistas de una palabra
  para ahorrar RAM.
- Los tiles de fondo personalizados viven fuera de `$20-$7F`.
- VRAM y OAM se escriben en VBLANK a traves de `lib/vc.lib`.
- Colision por software con un unico punto central `(x+4, y+4)` contra la
  rejilla de celdas; asi se puede cruzar el puente de forma fiable.
- Sonido SID no bloqueante (`sound.c`): recoger/soltar, llave, gruñido, rugido,
  muerte, victoria y **pasos al subir/bajar las escaleras** (tres golpes de
  pulso que ascienden al subir y descienden al bajar). El ancho de pulso se
  fija a ~50% (si es 0, el pulso no suena en el SID).
- Para que todo quepa en RAM se enlaza contra la **libreria modular** de
  `videocore-6502-cc65` (`video.o`, `gfx_vram.o`, `gfx_tiles.o`, `gfx_text.o`,
  `gfx_pal.o`). Al no usar `vc_sprite_disable` (se apaga el sprite escribiendo
  OAM directamente) se descartan `gfx.o` y `collide.o`, ahorrando ~400 bytes.
- Las distancias absolutas se calculan con una unica funcion `adist()`. El
  ternario de 16 bits que habia repetido en cada comprobacion ocupaba ~50 B por
  uso; centralizarlo libero mas de 300 B y dejo sitio para el iman ampliado.

- Las islas verdes del bosque usan el tile de fondo `0x81` rediseñado como
  **árbol** (copa verde, sombra y tronco). Al ser tile de fondo no consume OAM
  ni patrones de sprite extra; también decora el borde del bosque.

![Bosque con islas de árboles](doc/bosque.png)

Mapa de memoria final:

| Segmento | Inicio | Fin    |
|----------|--------|--------|
| ZEROPAGE | `$0020`| `$0053`|
| CODE     | `$0847`| `$3B0E`|
| RODATA   | `$3B0F`| `$3E9B`|
| BSS      | `$3E9C`| `$3F1C`|

Termina en `$3F1C`, dejando unos **98 bytes libres** en la zona RAM del
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
