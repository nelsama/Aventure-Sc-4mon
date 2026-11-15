/**
 * ============================================================================
 * sound.c - Efectos de sonido para el SID 6581
 * ============================================================================
 * Voces:
 *   0: efectos cortos (coger, soltar, llave)
 *   1: muerte del jugador (barrido) / melodia de victoria
 *   2: ruido (dragon) y refuerzos
 *
 * No se leen registros del SID: el estado vive en RAM.
 * ============================================================================
 */

#include <stdint.h>
#include "sound.h"

#define SID ((volatile uint8_t *)0xD400)

#define WF_TRI   0x11
#define WF_SAW   0x21
#define WF_PULSE 0x41
#define WF_NOISE 0x81

static uint8_t fx0_t;       /* temporizador voz 0 */
static uint8_t fx1_t;       /* temporizador voz 1 */
static uint8_t fx2_t;       /* temporizador voz 2 */
static uint8_t fx1_kind;    /* 1 = muerte, 2 = victoria */
static uint16_t sweep;

static void voice_freq(uint8_t v, uint16_t f) {
    volatile uint8_t *p = SID + (uint16_t)v * 7;
    p[0] = (uint8_t)f;
    p[1] = (uint8_t)(f >> 8);
}

static void voice_on(uint8_t v, uint16_t f, uint8_t wave, uint8_t ad, uint8_t sr) {
    volatile uint8_t *p = SID + (uint16_t)v * 7;
    p[0] = (uint8_t)f;
    p[1] = (uint8_t)(f >> 8);
    p[2] = 0x00;            /* PW bajo                                     */
    p[3] = 0x08;            /* PW alto: ~50% (si es 0, el pulso no suena)  */
    p[5] = ad;
    p[6] = sr;
    p[4] = wave;
}

static void voice_off(uint8_t v) {
    volatile uint8_t *p = SID + (uint16_t)v * 7;
    p[4] = 0x00;
}

void snd_init(void) {
    voice_off(0);
    voice_off(1);
    voice_off(2);
    SID[0x18] = 0x0F;       /* volumen master, filtro off */
    fx0_t = 0;
    fx1_t = 0;
    fx2_t = 0;
    sweep = 0;
}

void snd_silence(void) {
    voice_off(0);
    voice_off(1);
    voice_off(2);
    fx0_t = 0;
    fx1_t = 0;
    fx2_t = 0;
    sweep = 0;
}

void snd_pick(void) {
    voice_on(0, 0x1A7C, WF_PULSE, 0x00, 0x84);
    fx0_t = 5;
}

void snd_drop(void) {
    voice_on(0, 0x1126, WF_PULSE, 0x00, 0x84);
    fx0_t = 5;
}

void snd_key(void) {
    voice_on(0, 0x1585, WF_PULSE, 0x00, 0xA8);
    fx0_t = 18;
}

void snd_kill(void) {
    voice_on(2, 0x3000, WF_NOISE, 0x00, 0xA8);
    fx2_t = 16;
}

/* Gruñido corto: cuando un dragon ronda cerca del jugador. */
void snd_growl(void) {
    voice_on(2, 0x1600, WF_NOISE, 0x00, 0x86);
    fx2_t = 10;
}

/* Rugido largo: cuando un dragon te persigue a otra habitacion. */
void snd_roar(void) {
    voice_on(2, 0x0E00, WF_NOISE, 0x02, 0xA9);
    fx2_t = 30;
}

/* Chillido corto del murcielago. */
void snd_bat(void) {
    voice_on(2, 0x3000, WF_NOISE, 0x00, 0x85);
    fx2_t = 8;
}

void snd_death(void) {
    sweep = 0x2400;
    fx1_kind = 1;
    fx1_t = 45;
    voice_on(1, sweep, WF_SAW, 0x00, 0xA8);
}

void snd_win(void) {
    sweep = 0x0800;
    fx1_kind = 2;
    fx1_t = 30;
    voice_on(1, sweep, WF_PULSE, 0x00, 0xA8);
}

void snd_update(void) {
    /* Voz 0: efectos cortos */
    if (fx0_t) {
        fx0_t--;
        if (fx0_t == 9 && fx1_kind == 0) {
            /* la llave hace un pequeño intervalo ascendente */
            voice_freq(0, 0x224C);
        }
        if (fx0_t == 0) voice_off(0);
    }

    /* Voz 1: muerte (barrido) o victoria (melodia) */
    if (fx1_t) {
        fx1_t--;
        if (fx1_kind == 1) {
            if (sweep > 0x0800) sweep -= 0x0070;
            voice_freq(1, sweep);
            if (fx1_t == 0) voice_off(1);
        } else if (fx1_kind == 2) {
            if (sweep < 0x3000) sweep = (uint16_t)(sweep + 0x0080);
            voice_freq(1, sweep);
            if (fx1_t == 0) voice_off(1);
        }
    }

    /* Voz 2: ruido */
    if (fx2_t) {
        fx2_t--;
        if (fx2_t == 0) voice_off(2);
    }
}
