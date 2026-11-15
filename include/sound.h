/**
 * ============================================================================
 * sound.h - Efectos de sonido para el SID 6581 ($D400-$D41F)
 * ============================================================================
 * Efectos cortos y no bloqueantes. snd_update() se llama una vez por frame.
 * ============================================================================
 */
#ifndef SOUND_H
#define SOUND_H

#include <stdint.h>

void snd_init(void);
void snd_pick(void);
void snd_drop(void);
void snd_key(void);
void snd_kill(void);
void snd_growl(void);
void snd_roar(void);
void snd_bat(void);
void snd_death(void);
void snd_win(void);
void snd_stairs(uint8_t up);
void snd_update(void);
void snd_silence(void);

#endif
