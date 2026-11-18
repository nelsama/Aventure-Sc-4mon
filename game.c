/**
 * ============================================================================
 * game.c - AVENTURA (homenaje a Adventure de Atari 2600)
 * ============================================================================
 * Core de video vc / monitor 6502.
 * 16 habitaciones (12 de superficie + 4 catacumbas), objetos, dragones,
 * murcielago, puente, magnet, llaves y caliz.
 * ============================================================================
 */

#include <stdint.h>
#include "video.h"
#include "romapi.h"
#include "joy.h"
#include "sound.h"

/* ===========================================================================
 * CONSTANTES DE JUEGO
 * =========================================================================== */
#define ST_MENU    0
#define ST_PLAY    1
#define ST_WIN     2
#define ST_OVER    3

#define FACE_D     0
#define FACE_U     1
#define FACE_L     2
#define FACE_R     3

#define EX_N       0x01
#define EX_S       0x02
#define EX_W       0x04
#define EX_E       0x08

#define GATE_NONE  0
#define GATE_N     1
#define GATE_S     2

#define KEY_Y      1
#define KEY_W      2
#define KEY_B      3

#define OBJ_CHALICE 0
#define OBJ_SWORD   1
#define OBJ_BRIDGE  2
#define OBJ_MAGNET  3
#define OBJ_KEY_Y   4
#define OBJ_KEY_W   5
#define OBJ_KEY_B   6
#define OBJ_DRAG_R  7
#define OBJ_DRAG_G  8
#define OBJ_DRAG_Y  9
#define OBJ_BAT     10
#define NUM_OBJ     11
#define OBJ_NONE    0xFF

#define NUM_BG_PAT  22
#define NUM_SPR_PAT 42

/* Corazon del HUD (sprite 41, paleta 2). */
#define HEART_PAT   41

/* Patrones del jugador 16x16: 4 por direccion (TL, TR, BL, BR). */
#define SPR_PLAYER_DOWN  8
#define SPR_PLAYER_UP    12
#define SPR_PLAYER_LEFT  20   /* patron que mira visualmente a la izquierda */
#define SPR_PLAYER_RIGHT 16   /* patron que mira visualmente a la derecha  */
#define SPR_PLAYER_WALK  8    /* offset al 2o frame de caminar (izq/der) */
#define PLAYER_SPR_FIRST 12   /* slots OAM 12..15 */

/* Poison Drake 16x16: 2 frames (aleteo) mirando a la derecha; la izquierda
 * se dibuja espejando por codigo. */
#define DRAGON_PAT_BASE   32
#define DRAGON_FRAME_OFF  4
#define DRAGON_SPR_FIRST  16   /* slots OAM 16..19 */

/* Puente: dos patrones segun el sentido del cruce. */
#define BRIDGE_PAT_V      2
#define BRIDGE_PAT_H      40

#define T_GRASS     0x80
#define T_BUSH      0x81
#define T_CFLOOR    0x82
#define T_WALL      0x83
#define T_KFLOOR    0x84
#define T_WATER     0x85
#define T_GATE      0x86
/* Hoyo 16x16 = 2x2 tiles (TL, TR, BL, BR); se cargan desde AVENTUR.DAT. */
#define T_HOLE_TL   0x8A
#define T_HOLE_TR   0x8B
#define T_HOLE_BL   0x8C
#define T_HOLE_BR   0x8D
/* Escalera de piedra 16x16 = 2x2 tiles (Catacumbas). */
#define T_STAIRS_TL 0x8E
#define T_STAIRS_TR 0x8F
#define T_STAIRS_BL 0x90
#define T_STAIRS_BR 0x91
/* Mesa/altar del caliz 16x16 = 2x2 tiles (Castillo de Oro). */
#define T_ALTAR_TL  0x92
#define T_ALTAR_TR  0x93
#define T_ALTAR_BL  0x94
#define T_ALTAR_BR  0x95

/* ===========================================================================
 * PATRONES DE FONDO (2 planos: color = (plano1<<1)|plano0)
 * =========================================================================== */
/* Patrones cargados desde AVENTUR.DAT (SD) al arrancar: ya no ocupan RODATA.
 * pat_buf guarda un registro de 16 bytes = plano 0 (8 B) + plano 1 (8 B). */
static uint8_t pat_buf[16];
static uint8_t graf_ok;

/* ===========================================================================
 * PALETAS
 * =========================================================================== */
static const uint16_t bg_pal[4][4] = {
    { 0, VC_RGB888(0x00AA44), VC_RGB888(0x005522), VC_RGB888(0xFFFFFF) },
    { 0, VC_RGB888(0xFFCC00), VC_RGB888(0x884400), VC_RGB888(0xFFFFFF) },
    { 0, VC_RGB888(0x3366AA), VC_RGB888(0x112244), VC_RGB888(0xFFFFFF) },
    { 0, VC_RGB888(0xDDDDDD), VC_RGB888(0x777777), VC_RGB888(0xFFFFFF) }
};

static const uint16_t spr_pal[4][4] = {
    { 0, VC_RGB888(0x2E5BFF), VC_RGB888(0xFFCC00), VC_RGB888(0x101018) },
    { 0, VC_RGB888(0xFFCC00), VC_RGB888(0x995500), VC_RGB888(0xFFFFFF) },
    { 0, VC_RGB888(0xFF0000), VC_RGB888(0xFF8800), VC_RGB888(0xFFFFFF) },
    { 0, VC_RGB888(0x00FF00), VC_RGB888(0x008800), VC_RGB888(0xFFFFFF) }
};

/* ===========================================================================
 * DEFINICION DE HABITACIONES
 * =========================================================================== */
typedef struct {
    const uint8_t *walls;
    const char    *name;
    const char    *hint;
    uint8_t nwalls;
    uint8_t floor;
    uint8_t wall;
    uint8_t fpal;
    uint8_t wpal;
    uint8_t exits;
    uint8_t gate;
    uint8_t gkey;
} Room;

static const uint8_t w0[] = { 8,6,4,2, 24,8,3,3, 14,18,5,2, 5,20,3,3 };
static const uint8_t w1[] = { 8,7,3,3, 24,6,4,3, 14,17,5,2, 6,20,3,2 };
static const uint8_t w2[] = { 28,6,11,1, 28,6,1,7, 28,12,11,1,
                              10,7,1,8, 10,19,1,6, 18,10,8,1 };
static const uint8_t w3[] = { 10,7,1,9, 10,20,1,6, 20,6,1,8, 20,18,8,1 };
static const uint8_t w4[] = { 8,8,4,2, 26,6,4,3, 12,19,6,2, 6,16,2,4 };
static const uint8_t w5[] = { 6,6,4,2, 28,6,4,4, 12,20,4,2, 24,18,6,2 };
static const uint8_t w6[] = { 6,5,3,2, 30,5,3,2, 6,20,3,2, 30,20,3,2 };
static const uint8_t w7[] = { 8,7,3,3, 24,6,4,2, 14,18,5,2, 28,18,3,4 };
static const uint8_t w8[] = { 7,7,1,8, 7,19,1,7, 32,7,1,8, 32,19,1,7,
                              4,12,10,1, 26,12,10,1, 12,5,1,4, 27,5,1,4 };
static const uint8_t w9[] = { 6,7,4,2, 24,7,4,3, 10,18,8,2, 28,17,4,3 };
static const uint8_t w10[] = { 8,6,3,3, 26,6,4,2, 12,16,4,3, 24,18,5,2 };
static const uint8_t w11[] = { 8,8,4,3, 24,10,4,4, 16,19,8,2, 5,17,3,3 };
static const uint8_t w12[] = { 6,7,2,10, 30,6,2,7, 12,20,10,1 };
static const uint8_t w13[] = { 8,7,1,8, 8,19,1,6, 14,13,12,1, 24,20,8,1 };
static const uint8_t w14[] = { 19,4,1,23, 6,6,1,5, 6,20,1,5, 33,6,1,5, 33,20,1,5 };
static const uint8_t w15[] = { 6,7,1,10, 33,7,1,10, 12,20,16,1 };

/* Pistas compartidas (breves, para dejar sitio a la animacion del dragon). */
static const char h_expl[]     = "EXPLORA";
static const char h_bat[]      = "BAT";
static const char h_key[]      = "LLAVE";
static const char h_water[]    = "AGUA";
static const char h_wall[]     = "MURO";
static const char h_hole[]     = "HOYO";
static const char h_iman[]     = "IMAN";
static const char h_sword[]    = "ESP.";
static const char h_stairs[]   = "ESC.";
static const char h_chalice[]  = "CALIZ";
static const char h_takebr[]   = "PTE.";

static const Room rooms[16] = {
  { w0, "B1", h_expl, 4, T_GRASS, T_BUSH, 0, 0, EX_E|EX_S, GATE_NONE, 0 },
  { w1, "B2", h_hole, 4, T_GRASS, T_BUSH, 0, 0, EX_W|EX_S, GATE_NONE, 0 },
  { w2, "NEG.", h_iman, 6, T_CFLOOR, T_WALL, 2, 2, EX_S, GATE_S, KEY_B },
  { w3, "BLAN.", h_key, 4, T_CFLOOR, T_WALL, 3, 3, EX_S, GATE_S, KEY_W },
  { w4, "B3", h_bat, 4, T_GRASS, T_BUSH, 0, 0, EX_N|EX_E|EX_S, GATE_S, KEY_Y },
  { w5, "ENT.", h_takebr, 4, T_GRASS, T_BUSH, 0, 0, EX_N|EX_S|EX_W|EX_E, GATE_NONE, 0 },
  { w6, "FOSO", h_water, 4, T_GRASS, T_BUSH, 0, 0, EX_N|EX_S|EX_W|EX_E, GATE_N, KEY_B },
  { w7, "B4", h_key, 4, T_GRASS, T_BUSH, 0, 0, EX_N|EX_W|EX_S, GATE_N, KEY_W },
  { w8, "ORO", h_key, 8, T_CFLOOR, T_WALL, 1, 1, EX_N, GATE_N, KEY_Y },
  { w9, "B5", h_sword, 4, T_GRASS, T_BUSH, 0, 0, EX_N|EX_E, GATE_NONE, 0 },
  { w10, "B6", h_takebr, 4, T_GRASS, T_BUSH, 0, 0, EX_N|EX_W|EX_E, GATE_NONE, 0 },
  { w11, "B7", h_expl, 4, T_GRASS, T_BUSH, 0, 0, EX_N|EX_W, GATE_NONE, 0 },
  { w12, "C1", h_stairs, 3, T_KFLOOR, T_WALL, 2, 2, EX_E, GATE_NONE, 0 },
  { w13, "C2", h_iman, 4, T_KFLOOR, T_WALL, 2, 2, EX_W|EX_E, GATE_NONE, 0 },
  { w14, "C3", h_wall, 5, T_KFLOOR, T_WALL, 2, 2, EX_W|EX_E, GATE_NONE, 0 },
  { w15, "C4", h_key, 3, T_KFLOOR, T_WALL, 2, 2, EX_W, GATE_NONE, 0 }
};

static const char *const item_names[7] = {
    "CAL.", "ESP.", "PTE.", "IMAN", "AMAR.", "BLAN.", "NEG."
};

static const uint8_t obj_spawn[NUM_OBJ][3] = {
    { 2,33,9 },   /* caliz en la camara sellada */
    { 9,19,20 },  /* espada */
    { 10,30,10 }, /* puente */
    { 13,30,8 },  /* iman */
    { 8,12,10 },  /* llave amarilla */
    { 15,20,8 },  /* llave blanca */
    { 3,16,8 },   /* llave negra */
    { 2,12,18 },  /* dragon rojo */
    { 13,12,18 }, /* dragon verde */
    { 3,12,18 },  /* dragon amarillo */
    { 4,10,10 }   /* murcielago */
};

/* ===========================================================================
 * ESTADO
 * =========================================================================== */
static uint8_t  state;
static uint8_t  current_room;
static uint16_t px;
static uint8_t  py;
static uint8_t  face;
static uint8_t  carry;
static uint8_t  lives;
static uint8_t  invuln;
static uint8_t  frame;
static uint8_t  rnd_state;
static uint8_t  steal_cd;
static uint8_t  hud_dirty;
static uint8_t  gate_open[3];
static uint8_t  menu_sel;   /* 0 = JUGAR, 1 = SALIR */

static uint8_t  obj_room[NUM_OBJ];
static uint16_t obj_x[NUM_OBJ];
static uint8_t  obj_y[NUM_OBJ];
static uint8_t  obj_active[NUM_OBJ];
static int8_t   obj_dx[NUM_OBJ];
static int8_t   obj_dy[NUM_OBJ];
static uint8_t  growl_cd;   /* pausa entre gruñidos de dragon */
static uint8_t  dragon_dir[3]; /* 0 = derecha, 1 = izquierda (ultima) */
static uint8_t  walk_anim;     /* contador de animacion al caminar */
static uint8_t  player_tiles;  /* clave de los tiles ya escritos del jugador */
static uint8_t  dragon_tiles;  /* clave de los tiles ya escritos del dragon */

static const uint8_t obj_pat[NUM_OBJ] = { 0,1,2,3,4,7,7,0,0,0,5 };
static const uint8_t obj_pal[NUM_OBJ] = { 1,1,1,2,1,1,0,2,3,1,0 };
static const uint8_t obj_slot[NUM_OBJ] = { 5,6,7,8,9,10,11,2,3,4,20 };

/* Prototipos */
static void die(void);
static void draw_actors(void);
static void draw_hud(void);
static void start_game(void);
static void draw_menu(const char *msg);
static void salir(void);
static void update_game(uint8_t actions, uint8_t fire);

/* Distancia absoluta entre dos coordenadas. Centralizarla ahorra mucho
 * codigo: el ternario de 16 bits ocupa ~50 B cada vez que se repite. */
static uint16_t adist(uint16_t a, uint16_t b) {
    return (a > b) ? (uint16_t)(a - b) : (uint16_t)(b - a);
}

/* ===========================================================================
 * UTILIDADES DE DIBUJO
 * =========================================================================== */
static void fill_row(uint8_t col, uint8_t row, uint8_t count,
                     uint8_t tile, uint8_t pal) {
    uint16_t a = VC_CELL(col, row);
    while (count--) {
        VC_WRITE(VC_AREA_TILEMAP, a, tile);
        VC_WRITE(VC_AREA_ATTR, a, pal);
        a++;
    }
}

static void fill_rect(uint8_t x, uint8_t y, uint8_t w, uint8_t h,
                      uint8_t tile, uint8_t pal) {
    while (h--) {
        fill_row(x, y, w, tile, pal);
        y++;
    }
}

/* ===========================================================================
 * SETUP DE VIDEO
 * =========================================================================== */
/* Carga los patrones de AVENTUR.DAT en streaming: 16 bytes por registro.
 * Formato: NUM_BG_PAT registros de fondo (tiles T_GRASS..) y despues
 * NUM_SPR_PAT registros de sprite (0..NUM_SPR_PAT-1). */
static void load_patterns(void) {
    uint8_t i, total = (uint8_t)(NUM_BG_PAT + NUM_SPR_PAT);

    graf_ok = 0;
    if (rom_mfs_open("AVENTUR.DAT") != MFS_OK) return;
    if (rom_mfs_get_size() != (uint16_t)(total * 16)) {
        rom_mfs_close();
        return;
    }
    for (i = 0; i < total; i++) {
        if (rom_mfs_read_via_zp(pat_buf, 16) != 16) break;
        if (i < NUM_BG_PAT)
            vc_load_bg_pattern((uint8_t)(T_GRASS + i), pat_buf, pat_buf + 8);
        else
            vc_load_spr_pattern((uint8_t)(i - NUM_BG_PAT), pat_buf, pat_buf + 8);
    }
    rom_mfs_close();
    graf_ok = (uint8_t)(i == total);
}

static void setup_video(void) {
    uint8_t i;
    vc_wait_ready();
    vc_wait_vblank();
    vc_clear_vram();
    for (i = 0; i < 4; i++) {
        vc_pal_load_bg(i, bg_pal[i]);
        vc_pal_load_spr(i, spr_pal[i]);
    }
    vc_set_bgcolor(VC_RGB888(0x050505));
    load_patterns();
    vc_clear_oam();
    vc_wait_vblank_end();
}

/* Limpia toda la pantalla a texto (espacio, paleta 0). */
static void clear_text_screen(void) {
    uint8_t r;
    vc_clear_oam();
    for (r = 0; r < 30; r++) fill_row(0, r, 40, VC_CHAR_SPACE, 0);
}

static void put_text(uint8_t col, uint8_t row, const char *s, uint8_t pal) {
    vc_put_str_pal(col, row, s, pal);
}

/* ===========================================================================
 * RENDER DE HABITACION
 * =========================================================================== */
static uint8_t gate_pal(uint8_t k) {
    if (k == KEY_W) return 3;
    if (k == KEY_B) return 2;
    return 1;
}

static void render_room(void) {
    const Room *r = &rooms[current_room];
    const uint8_t *w;
    uint8_t i, c, row;

    /* suelo */
    for (row = 3; row <= 27; row++) fill_row(0, row, 40, r->floor, r->fpal);

    /* borde superior e inferior */
    for (c = 0; c < 40; c++) {
        if (!((c >= 18 && c <= 21) && (r->exits & EX_N)))
            fill_row(c, 3, 1, r->wall, r->wpal);
        if (!((c >= 18 && c <= 21) && (r->exits & EX_S)))
            fill_row(c, 27, 1, r->wall, r->wpal);
    }
    /* borde izquierdo y derecho */
    for (row = 4; row <= 26; row++) {
        if (!((row >= 13 && row <= 16) && (r->exits & EX_W)))
            fill_row(0, row, 1, r->wall, r->wpal);
        if (!((row >= 13 && row <= 16) && (r->exits & EX_E)))
            fill_row(39, row, 1, r->wall, r->wpal);
    }

    /* paredes interiores */
    w = r->walls;
    for (i = 0; i < r->nwalls; i++) {
        fill_rect(w[0], w[1], w[2], w[3], r->wall, r->wpal);
        w += 4;
    }

    /* agua del foso */
    if (current_room == 6) fill_row(1, 12, 38, T_WATER, 2);

    /* tiles especiales: hoyo del bosque y escalera de Catacumbas (2x2) */
    if (current_room == 5 || current_room == 12) {
        uint8_t base = (current_room == 5) ? T_HOLE_TL : T_STAIRS_TL;
        uint8_t pal = (current_room == 5) ? 1 : 3;
        for (i = 0; i < 4; i++)
            fill_row((uint8_t)(19 + (i & 1)), (uint8_t)(15 + (i >> 1)), 1,
                     (uint8_t)(base + i), pal);
    }
    if (current_room == 8)
        for (i = 0; i < 4; i++)
            fill_row((uint8_t)(19 + (i & 1)), (uint8_t)(8 + (i >> 1)), 1,
                     (uint8_t)(T_ALTAR_TL + i), 1);

    /* puerta cerrada */
    if (r->gate && !gate_open[r->gkey - 1]) {
        row = (r->gate == GATE_N) ? 3 : 27;
        fill_row(18, row, 4, T_GATE, gate_pal(r->gkey));
    }
}

/* Pinta de nuevo el hueco de la puerta (abierta). */
static void redraw_gate(void) {
    const Room *r = &rooms[current_room];
    uint8_t row = (r->gate == GATE_N) ? 3 : 27;
    fill_row(18, row, 4, r->floor, r->fpal);
}

/* ===========================================================================
 * COLISION CON EL FONDO
 * =========================================================================== */
static uint8_t cell_solid(uint8_t col, uint8_t row) {
    const Room *r = &rooms[current_room];
    const uint8_t *w;
    uint8_t i;

    if (col > 39 || row < 3 || row > 27) return 1;

    /* bordes */
    if (row == 3) {
        if (col >= 18 && col <= 21 && (r->exits & EX_N)) {
            if (r->gate == GATE_N && !gate_open[r->gkey - 1]) return 1;
            return 0;
        }
        return 1;
    }
    if (row == 27) {
        if (col >= 18 && col <= 21 && (r->exits & EX_S)) {
            if (r->gate == GATE_S && !gate_open[r->gkey - 1]) return 1;
            return 0;
        }
        return 1;
    }
    if (col == 0) {
        if (row >= 13 && row <= 16 && (r->exits & EX_W)) return 0;
        return 1;
    }
    if (col == 39) {
        if (row >= 13 && row <= 16 && (r->exits & EX_E)) return 0;
        return 1;
    }

    /* La celda donde esta el jugador siempre es transitable: evita quedar
     * atrapado si el puente o un muro desaparece bajo sus pies. */
    if (col == (uint8_t)((px + 4) >> 3) && row == (uint8_t)((py + 4) >> 3))
        return 0;

    /* puente colocado: hace transitable su celda */
    if (obj_active[OBJ_BRIDGE] && carry != OBJ_BRIDGE &&
        obj_room[OBJ_BRIDGE] == current_room) {
        if (((obj_x[OBJ_BRIDGE] >> 3) == col) &&
            ((obj_y[OBJ_BRIDGE] >> 3) == row)) return 0;
    }

    /* paredes interiores */
    w = r->walls;
    for (i = 0; i < r->nwalls; i++) {
        if (col >= w[0] && col < (uint8_t)(w[0] + w[2]) &&
            row >= w[1] && row < (uint8_t)(w[1] + w[3])) return 1;
        w += 4;
    }

    /* agua */
    if (current_room == 6 && row == 12 && col >= 1 && col <= 38) return 1;

    return 0;
}

/* Intenta abrir la puerta de la habitacion actual si el jugador lleva
 * la llave correcta. Devuelve 1 si la celda queda transitable. */
static uint8_t try_gate(uint8_t col, uint8_t row) {
    const Room *r = &rooms[current_room];
    uint8_t gi, krow;

    if (r->gate == GATE_N) krow = 3;
    else if (r->gate == GATE_S) krow = 27;
    else return 0;

    if (row != krow || col < 18 || col > 21) return 0;

    gi = (uint8_t)(r->gkey - 1);
    if (gate_open[gi]) return 1;
    if (carry != (uint8_t)(OBJ_KEY_Y + gi)) return 0;

    gate_open[gi] = 1;
    obj_active[carry] = 0;
    carry = OBJ_NONE;
    redraw_gate();
    snd_key();
    hud_dirty = 1;
    return 1;
}

static uint8_t player_point_ok(uint16_t x, uint8_t y) {
    uint8_t col = (uint8_t)((x + 4) >> 3);
    uint8_t row = (uint8_t)((y + 4) >> 3);
    if (!cell_solid(col, row)) return 1;
    return try_gate(col, row);
}

static uint8_t actor_point_ok(uint16_t x, uint8_t y) {
    uint8_t col = (uint8_t)((x + 4) >> 3);
    uint8_t row = (uint8_t)((y + 4) >> 3);
    return (uint8_t)!cell_solid(col, row);
}

/* ===========================================================================
 * CAMBIO DE HABITACION
 * =========================================================================== */
/* Dragon activo en esta habitacion lo bastante cerca para perseguirte. */
static uint8_t dragon_following(void) {
    uint8_t i;
    uint16_t dx, dy;
    for (i = OBJ_DRAG_R; i <= OBJ_DRAG_Y; i++) {
        if (!obj_active[i] || obj_room[i] != current_room) continue;
        dx = adist(px, obj_x[i]);
        dy = adist(py, obj_y[i]);
        if (dx <= 64 && dy <= 64) return i;
    }
    return OBJ_NONE;
}

static void change_room(uint8_t dest, uint8_t dir) {
    uint8_t fol = dragon_following();

    current_room = dest;
    if (dir == 0) px = 304;            /* salir por el oeste */
    else if (dir == 1) px = 8;         /* salir por el este  */
    else if (dir == 2) py = 208;       /* salir por el norte */
    else py = 32;                      /* salir por el sur   */

    /* Si un dragon te perseguia, aparece contigo en la nueva sala. */
    if (fol != OBJ_NONE) {
        obj_room[fol] = dest;
        if (dir < 2) {
            obj_x[fol] = (dir == 0) ? 304 : 8;
            obj_y[fol] = (py >= 136) ? (uint8_t)(py - 24)
                                     : (uint8_t)(py + 24);
        } else {
            obj_y[fol] = (dir == 2) ? 208 : 32;
            obj_x[fol] = (px >= 160) ? (uint16_t)(px - 24)
                                     : (uint16_t)(px + 24);
        }
        if (obj_y[fol] < 32) obj_y[fol] = 32;
        if (obj_y[fol] > 208) obj_y[fol] = 208;
        invuln = 60;           /* respiro al entrar */
        growl_cd = 40;
        snd_roar();
    }

    render_room();
    hud_dirty = 1;
}

/* ===========================================================================
 * MOVIMIENTO DEL JUGADOR
 * =========================================================================== */
static void move_player(uint8_t actions) {
    const Room *r;
    uint8_t dx = 0, dy = 0;
    uint16_t nx;
    uint8_t ny;

    if (actions & (JOY_A_LEFT | JOY_A_RIGHT | JOY_A_UP | JOY_A_DOWN))
        walk_anim++;
    else
        walk_anim = 0;

    if (actions & JOY_A_LEFT) { dx = 1; face = FACE_L; }
    else if (actions & JOY_A_RIGHT) { dx = 2; face = FACE_R; }

    if (actions & JOY_A_UP) { dy = 1; face = FACE_U; }
    else if (actions & JOY_A_DOWN) { dy = 2; face = FACE_D; }

    if (dx == 1) {
        nx = (px >= 2) ? (uint16_t)(px - 2) : 0;
        if (player_point_ok(nx, py)) px = nx;
    } else if (dx == 2) {
        nx = (px <= 310) ? (uint16_t)(px + 2) : 312;
        if (player_point_ok(nx, py)) px = nx;
    }

    if (dy == 1) {
        ny = (py >= 2) ? (uint8_t)(py - 2) : 0;
        if (player_point_ok(px, ny)) py = ny;
    } else if (dy == 2) {
        ny = (py <= 214) ? (uint8_t)(py + 2) : 216;
        if (player_point_ok(px, ny)) py = ny;
    }

    r = &rooms[current_room];

    if (px == 0 && (r->exits & EX_W)) {
        change_room((uint8_t)(current_room - 1), 0);
        return;
    }
    if (px == 312 && (r->exits & EX_E)) {
        change_room((uint8_t)(current_room + 1), 1);
        return;
    }
    if (py == 24 && (r->exits & EX_N)) {
        change_room((uint8_t)(current_room - 4), 2);
        return;
    }
    if (py == 216 && (r->exits & EX_S)) {
        change_room((uint8_t)(current_room + 4), 3);
        return;
    }

    /* agujero / escaleras de las catacumbas */
    if (current_room == 5 || current_room == 12) {
        uint8_t pc = (uint8_t)((px + 4) >> 3);
        uint8_t pr = (uint8_t)((py + 4) >> 3);
        if (pc >= 19 && pc <= 20 && pr >= 15 && pr <= 16) {
            if (current_room == 5) {
                current_room = 12;       /* el agujero baja a Catacumbas */
                snd_stairs(0);
                py = 136;                /* aparece al pie de la escalera */
            } else {
                current_room = 5;        /* las escaleras suben al bosque */
                snd_stairs(1);
                py = 112;                /* aparece arriba, fuera del hoyo */
            }
            px = 156;
            render_room();
            hud_dirty = 1;
        }
    }
}

/* ===========================================================================
 * OBJETOS
 * =========================================================================== */
static uint8_t hit(uint16_t ax, uint8_t ay, uint16_t bx, uint8_t by) {
    return (uint8_t)(adist(ax, bx) < 6 && adist(ay, by) < 6);
}

/* Suelta el objeto que lleva el jugador en la celda de enfrente. */
static void drop_carried(void) {
    uint8_t it = carry;
    uint8_t tx = (uint8_t)((px + 4) >> 3);
    uint8_t ty = (uint8_t)((py + 4) >> 3);

    if (face == FACE_L && tx > 0) tx--;
    else if (face == FACE_R && tx < 39) tx++;
    else if (face == FACE_U && ty > 3) ty--;
    else if (face == FACE_D && ty < 27) ty++;

    if (tx < 1) tx = 1;
    if (tx > 38) tx = 38;
    if (ty < 4) ty = 4;
    if (ty > 26) ty = 26;

    /* Si sueltas el puente cerca de donde estaba (p.ej. encima de la pared),
     * se repone en su celda en vez de caer al lado. */
    if (it == OBJ_BRIDGE) {
        uint16_t ddx = adist(px, obj_x[OBJ_BRIDGE]);
        uint8_t ddy = (uint8_t)adist(py, obj_y[OBJ_BRIDGE]);
        if (ddx <= 4 && ddy <= 4) {
            tx = (uint8_t)(obj_x[OBJ_BRIDGE] >> 3);
            ty = (uint8_t)(obj_y[OBJ_BRIDGE] >> 3);
        }
    }

    /* Los objetos normales no se pierden en muros ni agua. */
    if (it != OBJ_BRIDGE && cell_solid(tx, ty)) {
        tx = (uint8_t)((px + 4) >> 3);
        ty = (uint8_t)((py + 4) >> 3);
    }

    obj_room[it] = current_room;
    obj_x[it] = (uint16_t)((uint16_t)tx << 3);
    obj_y[it] = (uint8_t)(ty << 3);
    obj_active[it] = 1;
    carry = OBJ_NONE;
    hud_dirty = 1;
    snd_drop();
}

/* Coge el objeto mas cercano que este a menos de 12 px. */
static void pick_item(void) {
    uint8_t i, best = OBJ_NONE, bd = 255;
    for (i = 0; i < 7; i++) {
        uint16_t dx, dy, d;
        if (!obj_active[i] || obj_room[i] != current_room || i == carry) continue;
        dx = adist(px, obj_x[i]);
        dy = adist(py, obj_y[i]);
        if (dx >= 12 || dy >= 12) continue;
        d = (uint16_t)(dx + dy);
        if (d < bd) { bd = (uint8_t)d; best = i; }
    }
    if (best != OBJ_NONE) {
        carry = best;
        hud_dirty = 1;
        snd_pick();
    }
}

static void handle_fire(void) {
    /* Caso especial: con el iman, cambiar el objeto atraido mas cercano. */
    if (carry == OBJ_MAGNET) {
        uint8_t i, best = OBJ_NONE, bd = 255;
        for (i = 0; i < 7; i++) {
            uint16_t dx, dy, d;
            if (i == OBJ_BRIDGE || i == OBJ_MAGNET) continue;
            if (!obj_active[i] || obj_room[i] != current_room) continue;
            dx = adist(px, obj_x[i]);
            dy = adist(py, obj_y[i]);
            if (dx > 10 || dy > 10) continue;
            d = (uint16_t)(dx + dy);
            if (d < bd) { bd = (uint8_t)d; best = i; }
        }
        if (best != OBJ_NONE) {
            obj_room[OBJ_MAGNET] = current_room;
            obj_x[OBJ_MAGNET] = px;
            obj_y[OBJ_MAGNET] = py;
            obj_active[OBJ_MAGNET] = 1;
            carry = best;
            hud_dirty = 1;
            snd_pick();
            return;
        }
    }
    if (carry != OBJ_NONE) drop_carried();
    else pick_item();
}

/* Suelta lo que lleve el jugador justo donde esta (al morir). */
static void drop_here(void) {
    uint8_t it = carry;
    if (it == OBJ_NONE) return;
    obj_room[it] = current_room;
    obj_x[it] = px;
    obj_y[it] = py;
    obj_active[it] = 1;
    carry = OBJ_NONE;
    hud_dirty = 1;
}

static void kill_dragon(uint8_t i) {
    obj_active[i] = 0;
    snd_kill();
}

/* ===========================================================================
 * IA DE ACTORES
 * =========================================================================== */
static void actor_move(uint8_t i, uint8_t speed) {
    uint8_t moved = 0;
    uint16_t nx;
    uint8_t ny;

    if (obj_dx[i] > 0) nx = (uint16_t)(obj_x[i] + speed);
    else if (obj_dx[i] < 0) nx = (uint16_t)(obj_x[i] - speed);
    else nx = obj_x[i];

    if (nx >= 8 && nx <= 304 && actor_point_ok(nx, obj_y[i])) {
        obj_x[i] = nx;
        moved = 1;
    } else if (obj_dx[i] != 0) {
        obj_dx[i] = (int8_t)-obj_dx[i];
    }

    if (obj_dy[i] > 0) ny = (uint8_t)(obj_y[i] + speed);
    else if (obj_dy[i] < 0) ny = (uint8_t)(obj_y[i] - speed);
    else ny = obj_y[i];

    if (ny >= 32 && ny <= 208 && actor_point_ok(obj_x[i], ny)) {
        obj_y[i] = ny;
        moved = 1;
    } else if (obj_dy[i] != 0) {
        obj_dy[i] = (int8_t)-obj_dy[i];
    }

    if (!moved) {
        obj_dx[i] = (int8_t)-obj_dx[i];
        obj_dy[i] = (int8_t)-obj_dy[i];
    }
}

/* Persecucion: apunta hacia el jugador y deja que actor_move deslice por
 * los ejes y rebote si choca. */
static void dragon_think(uint8_t i) {
    obj_dx[i] = (px > obj_x[i]) ? 1 : ((px < obj_x[i]) ? -1 : 0);
    obj_dy[i] = (py > obj_y[i]) ? 1 : ((py < obj_y[i]) ? -1 : 0);
    if (i >= OBJ_DRAG_R && i <= OBJ_DRAG_Y) {
        if (obj_dx[i] > 0) dragon_dir[i - OBJ_DRAG_R] = 0;
        else if (obj_dx[i] < 0) dragon_dir[i - OBJ_DRAG_R] = 1;
    }
}

static void update_dragons(void) {
    uint8_t i;
    uint16_t ddx, ddy;

    for (i = OBJ_DRAG_R; i <= OBJ_DRAG_Y; i++) {
        if (!obj_active[i] || obj_room[i] != current_room) continue;

        dragon_think(i);
        actor_move(i, 1);

        /* gruñido cuando ronda cerca */
        if (!growl_cd) {
            ddx = adist(px, obj_x[i]);
            ddy = adist(py, obj_y[i]);
            if (ddx <= 48 && ddy <= 48) {
                snd_growl();
                growl_cd = 40;
            }
        }

        /* espada tirada en el suelo mata al dragon */
        if (obj_active[OBJ_SWORD] && carry != OBJ_SWORD &&
            obj_room[OBJ_SWORD] == current_room &&
            hit(obj_x[OBJ_SWORD], obj_y[OBJ_SWORD], obj_x[i], obj_y[i])) {
            kill_dragon(i);
            continue;
        }

        if (hit(px, py, obj_x[i], obj_y[i])) {
            if (carry == OBJ_SWORD) {
                kill_dragon(i);
            } else if (!invuln) {
                die();
                return;
            }
        }
    }
    if (growl_cd) growl_cd--;
}

static void update_bat(void) {
    if (!obj_active[OBJ_BAT] || current_room != 4) return;

    if (steal_cd) {
        /* Tras tocar al jugador, se aleja durante un tiempo. */
        actor_move(OBJ_BAT, 1);
        steal_cd--;
        return;
    }

    dragon_think(OBJ_BAT);
    actor_move(OBJ_BAT, 1);

    if (!invuln && hit(px, py, obj_x[OBJ_BAT], obj_y[OBJ_BAT])) {
        if (carry != OBJ_NONE) {
            uint8_t it = carry;
            obj_room[it] = 4;
            obj_x[it] = obj_x[OBJ_BAT];
            obj_y[it] = obj_y[OBJ_BAT];
            obj_active[it] = 1;
            carry = OBJ_NONE;
            hud_dirty = 1;
        }
        /* Huye en direccion contraria al jugador. */
        obj_dx[OBJ_BAT] = (px > obj_x[OBJ_BAT]) ? -1 : 1;
        obj_dy[OBJ_BAT] = (py > obj_y[OBJ_BAT]) ? -1 : 1;
        snd_bat();
        steal_cd = 60;
    }
}

/* El iman arrastra el caliz, la espada y las llaves a traves de los muros. */
static void update_magnet(void) {
    uint8_t i;

    if (carry != OBJ_MAGNET) return;

    for (i = 0; i < 7; i++) {
        uint16_t cx, cy, dx, dy;

        if (i == OBJ_BRIDGE || i == OBJ_MAGNET) continue;
        if (!obj_active[i] || obj_room[i] != current_room) continue;

        cx = obj_x[i];
        cy = obj_y[i];

        dx = adist(cx, px);
        dy = adist(cy, py);
        if (dx <= 8 && dy <= 8) continue;

        /* 1 px por frame: antes saltaba 8 px cada 8 frames y se veia a tirones. */
        if (cx < px) cx = (uint16_t)(cx + 1);
        else if (cx > px) cx = (uint16_t)(cx - 1);
        if (cy < py) cy = (uint16_t)(cy + 1);
        else if (cy > py) cy = (uint16_t)(cy - 1);

        if (cx < 8) cx = 8;
        if (cx > 304) cx = 304;
        if (cy < 32) cy = 32;
        if (cy > 208) cy = 208;

        obj_x[i] = cx;
        obj_y[i] = (uint8_t)cy;
    }
}

/* ===========================================================================
 * MUERTE Y REINICIO
 * =========================================================================== */
static void die(void) {
    snd_death();
    drop_here();
    if (lives) lives--;
    if (!lives) {
        state = ST_OVER;
        return;
    }
    current_room = 8;
    px = 160;
    py = 160;
    face = FACE_D;
    invuln = 120;
    render_room();
    hud_dirty = 1;
}

static void reset_objects(void) {
    uint8_t i;
    for (i = 0; i < NUM_OBJ; i++) {
        obj_room[i] = obj_spawn[i][0];
        obj_x[i] = (uint16_t)((uint16_t)obj_spawn[i][1] << 3);
        obj_y[i] = (uint8_t)(obj_spawn[i][2] << 3);
        obj_active[i] = 1;
        obj_dx[i] = 0;
        obj_dy[i] = 0;
    }
    obj_dx[OBJ_DRAG_R] = 1;
    obj_dy[OBJ_DRAG_R] = 1;
    obj_dx[OBJ_DRAG_G] = 0;
    obj_dy[OBJ_DRAG_G] = 1;
    obj_dx[OBJ_DRAG_Y] = -1;
    obj_dy[OBJ_DRAG_Y] = 0;
    obj_dx[OBJ_BAT] = 1;
    obj_dy[OBJ_BAT] = -1;
}

static void start_game(void) {
    lives = 3;
    carry = OBJ_NONE;
    current_room = 8;
    px = 160;
    py = 160;
    face = FACE_D;
    invuln = 0;
    frame = 0;
    rnd_state = 0xA5;
    steal_cd = 0;
    growl_cd = 0;
    dragon_dir[0] = 0;
    dragon_dir[1] = 0;
    dragon_dir[2] = 0;
    walk_anim = 0;
    gate_open[0] = 0;
    gate_open[1] = 0;
    gate_open[2] = 0;
    reset_objects();
    render_room();
    hud_dirty = 1;
    state = ST_PLAY;
}

/* ===========================================================================
 * HUD
 * =========================================================================== */
static const char *carry_name(uint8_t c) {
    if (c == OBJ_NONE) return "NADA";
    return item_names[c];
}

static void draw_hud(void) {
    uint8_t k;

    fill_row(1, 1, 38, VC_CHAR_SPACE, 1);
    put_text(1, 1, "AVENTURA", 1);
    put_text(27, 1, "VIDAS:", 1);

    fill_row(1, 2, 38, VC_CHAR_SPACE, 1);
    put_text(1, 2, "LLEVA", 1);
    put_text(9, 2, carry_name(carry), 1);
    put_text(21, 2, "SALA:", 1);
    put_text(27, 2, rooms[current_room].name, 1);

    /* Vidas como corazones (slots OAM 21-25) y objeto llevado (slot 26). */
    for (k = 0; k < 5; k++) {
        if (k < lives) {
            vc_sprite_move((uint8_t)(21 + k), (uint16_t)(272 + k * 8), 8, 2);
            vc_oam_put((uint8_t)(21 + k), VC_OAM_TILE, HEART_PAT);
        } else {
            vc_oam_put((uint8_t)(21 + k), VC_OAM_Y, VC_SPR_DISABLED);
        }
    }
    if (carry != OBJ_NONE) {
        uint8_t pat = obj_pat[carry];
        if (carry == OBJ_BRIDGE) pat = BRIDGE_PAT_V;
        vc_sprite_move(26, 56, 16, obj_pal[carry]);
        vc_oam_put(26, VC_OAM_TILE, pat);
    } else {
        vc_oam_put(26, VC_OAM_Y, VC_SPR_DISABLED);
    }

    fill_row(0, 28, 40, VC_CHAR_SPACE, 1);
    if (carry == OBJ_CHALICE)
        put_text(1, 28, h_chalice, 1);
    else
        put_text(1, 28, rooms[current_room].hint, 1);

    hud_dirty = 0;
}

/* ===========================================================================
 * DIBUJO DE SPRITES
 * =========================================================================== */
/* Dibuja un objeto 16x16 (4 sprites) escribiendo solo lo necesario:
 * X/Y/FLAGS de cada cuadrante en cada frame y los TILES solo cuando cambia
 * el patron o el espejado. Asi entra holgado en el VBLANK. */
static void draw16_fast(uint8_t first, uint16_t x, uint8_t y,
                        uint8_t tile0, uint8_t flags, uint8_t mirror,
                        uint8_t *key) {
    uint8_t k = (uint8_t)(tile0 | (mirror ? 0x80 : 0));
    uint8_t f = flags;

    if (mirror) f |= VC_SPR_FLIP_X;

    vc_sprite_move(first, x, y, f);
    vc_sprite_move((uint8_t)(first + 1), (uint16_t)(x + 8), y, f);
    vc_sprite_move((uint8_t)(first + 2), x, (uint8_t)(y + 8), f);
    vc_sprite_move((uint8_t)(first + 3), (uint16_t)(x + 8),
                   (uint8_t)(y + 8), f);

    if (k == *key) return;
    *key = k;

    if (mirror) {
        vc_oam_put((uint8_t)(first + 0), VC_OAM_TILE, (uint8_t)(tile0 + 1));
        vc_oam_put((uint8_t)(first + 1), VC_OAM_TILE, tile0);
        vc_oam_put((uint8_t)(first + 2), VC_OAM_TILE, (uint8_t)(tile0 + 3));
        vc_oam_put((uint8_t)(first + 3), VC_OAM_TILE, (uint8_t)(tile0 + 2));
    } else {
        vc_oam_put((uint8_t)(first + 0), VC_OAM_TILE, tile0);
        vc_oam_put((uint8_t)(first + 1), VC_OAM_TILE, (uint8_t)(tile0 + 1));
        vc_oam_put((uint8_t)(first + 2), VC_OAM_TILE, (uint8_t)(tile0 + 2));
        vc_oam_put((uint8_t)(first + 3), VC_OAM_TILE, (uint8_t)(tile0 + 3));
    }
}

/* Dibuja el dragon i en los slots 16-19. Se llama lo primero de draw_actors
 * para que sus sprites se escriban dentro del VBLANK. */
static void draw_dragon(uint8_t i) {
    uint8_t pat = DRAGON_PAT_BASE;
    uint16_t sx;
    uint8_t sy;

    if ((frame >> 3) & 1) pat += DRAGON_FRAME_OFF;
    sx = (obj_x[i] >= 4) ? (uint16_t)(obj_x[i] - 4) : 0;
    if (sx > 304) sx = 304;
    sy = (obj_y[i] >= 4) ? (uint8_t)(obj_y[i] - 4) : 0;
    if (sy < 24) sy = 24;
    if (sy > 208) sy = 208;
    draw16_fast(DRAGON_SPR_FIRST, sx, sy, pat, obj_pal[i],
                (uint8_t)dragon_dir[i - OBJ_DRAG_R], &dragon_tiles);
}

static void draw_actors(void) {
    uint8_t i, pat, pal, dragon = OBJ_NONE;
    uint16_t sx;
    uint8_t sy;

    /* Los dragones van PRIMERO y sin apagarlos antes: son los unicos que
     * ocupaban slots fijos y, si el apagado/redibujado caia a mitad del
     * barrido, desaparecian un frame (el "titileo" del dragon). */
    for (i = OBJ_DRAG_R; i <= OBJ_DRAG_Y; i++) {
        if (obj_active[i] && obj_room[i] == current_room)
            dragon = i;
    }
    if (dragon != OBJ_NONE) {
        draw_dragon(dragon);
    } else {
        for (i = DRAGON_SPR_FIRST; i < (uint8_t)(DRAGON_SPR_FIRST + 4); i++)
            vc_oam_put(i, VC_OAM_Y, VC_SPR_DISABLED);
    }

    /* Slot 0 sin usar. Los objetos (1-11) y el jugador (12-15) se
     * sobrescriben cada frame, asi que no hace falta apagarlos. */
    vc_oam_put(0, VC_OAM_Y, VC_SPR_DISABLED);

    {
        if (face == FACE_D)      pat = SPR_PLAYER_DOWN;
        else if (face == FACE_U) pat = SPR_PLAYER_UP;
        else if (face == FACE_L) {
            pat = SPR_PLAYER_LEFT;
            if ((walk_anim >> 4) & 1) pat += SPR_PLAYER_WALK;
        } else {
            pat = SPR_PLAYER_RIGHT;
            if ((walk_anim >> 4) & 1) pat += SPR_PLAYER_WALK;
        }

        /* Centra el 16x16 en el punto de colision (px+4, py+4). */
        sx = (px >= 4) ? (uint16_t)(px - 4) : 0;
        if (sx > 304) sx = 304;
        sy = (py >= 4) ? (uint8_t)(py - 4) : 0;
        if (sy < 24) sy = 24;
        if (sy > 208) sy = 208;
        draw16_fast(PLAYER_SPR_FIRST, sx, sy, pat, VC_SPPAL_0, 0,
                    &player_tiles);
    }

    for (i = 0; i < NUM_OBJ; i++) {
        if (i >= OBJ_DRAG_R && i <= OBJ_DRAG_Y) continue;
        if (!obj_active[i] || i == carry || obj_room[i] != current_room) {
            /* Los objetos no dibujados se apagan aqui, no antes de dibujar. */
            vc_oam_put(obj_slot[i], VC_OAM_Y, VC_SPR_DISABLED);
            continue;
        }

        if (i == OBJ_BRIDGE) {
            /* Foso (6): cruce vertical; Catac. 3 (14): cruce horizontal. */
            pat = (current_room == 6) ? BRIDGE_PAT_V : BRIDGE_PAT_H;
        } else {
            pat = obj_pat[i];
            if (i == OBJ_BAT)
                pat = (uint8_t)(pat + ((frame >> 2) & 1));
        }
        pal = obj_pal[i];
        vc_sprite_move(obj_slot[i], obj_x[i], obj_y[i], pal);
        vc_oam_put(obj_slot[i], VC_OAM_TILE, pat);
    }
}

/* ===========================================================================
 * VICTORIA / ACTUALIZACION
 * =========================================================================== */
static void check_win(void) {
    uint8_t pc, pr;
    if (carry != OBJ_CHALICE || current_room != 8) return;
    pc = (uint8_t)((px + 4) >> 3);
    pr = (uint8_t)((py + 4) >> 3);
    if (pc >= 19 && pc <= 20 && pr >= 8 && pr <= 9) {
        carry = OBJ_NONE;
        obj_active[OBJ_CHALICE] = 0;
        snd_win();
        state = ST_WIN;
    }
}

static void update_game(uint8_t actions, uint8_t fire) {
    if (fire) handle_fire();
    move_player(actions);
    update_dragons();
    if (state != ST_PLAY) return;
    update_bat();
    update_magnet();
    check_win();
    if (state != ST_PLAY) return;
    if (invuln) invuln--;
    frame++;
    if (hud_dirty) draw_hud();
}

/* ===========================================================================
 * MENU Y SALIDA
 * =========================================================================== */
static void salir(void) {
    /* Igual que el comando QB del monitor: reset con autoboot (BOOT.INI) del
     * FPGA. El flag de $C004 sobrevive al reset; 0 = permitir autoboot. */
    (*(volatile uint8_t *)0xC004) = 0;
    __asm__ ("jmp ($FFFC)");
}

static void draw_menu(const char *msg) {
    clear_text_screen();
    put_text(16, 4, "AVENTURA", 1);
    put_text(17, 12, "JUGAR", 1);
    put_text(17, 14, "SALIR", 1);
    put_text(15, (uint8_t)(12 + menu_sel * 2), ">", 1);
    put_text(13, 24, "MUEVE + FUEGO", 0);
    /* Paleta 1 para el aviso: la 3 no vale porque su color 3 es el BG_COLOR
     * (entrada 15), y el texto saldria del color del fondo. */
    if (msg) put_text(15, 18, msg, 1);
}

/* ===========================================================================
 * MAIN
 * =========================================================================== */
int main(void) {
    uint8_t actions, fire, nav, prev = 0;

    joy_init();
    snd_init();
    setup_video();

    /* Sin AVENTUR.DAT no hay graficos: avisa y detente. */
    if (!graf_ok) {
        vc_wait_vblank();
        put_text(9, 13, "FALTA AVENTUR.DAT", 2);
        put_text(7, 15, "COPIALO EN LA SD", 1);
        while (1) { }
    }

    menu_sel = 0;
    draw_menu(0);
    state = ST_MENU;

    while (1) {
        vc_wait_vblank();

        /* Dibujar justo al entrar en VBLANK. update_game tarda mas que el
         * VBLANK (45 lineas): si se dibujaba despues, las escrituras al OAM
         * caian a mitad del barrido y el dragon parpadeaba. */
        if (state == ST_PLAY) draw_actors();

        actions = joy_read();
        fire = (uint8_t)((actions & JOY_A_FIRE) && !(prev & JOY_A_FIRE));
        nav = (uint8_t)((actions & (JOY_A_UP | JOY_A_DOWN)) &&
                        !(prev & (JOY_A_UP | JOY_A_DOWN)));
        prev = actions;

        if (state == ST_PLAY) {
            update_game(actions, fire);
        } else if (state == ST_MENU) {
            if (nav) {
                menu_sel ^= 1;
                draw_menu(0);
            }
            if (fire) {
                if (menu_sel) salir();
                else start_game();
            }
        } else {
            /* VICTORIA o GAME OVER: se vuelve al menu. */
            draw_menu(state == ST_WIN ? "VICTORIA!" : "GAME OVER");
            state = ST_MENU;
        }

        snd_update();
        vc_wait_vblank_end();
    }
}
