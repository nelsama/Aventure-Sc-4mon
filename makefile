# ============================================================================
# makefile - AVENTURA (homenaje a Adventure de Atari 2600) para Core de Video
# ============================================================================
# Genera output/aventura.bin (se carga en $0800 con el monitor).
# Uso:
#   make          compila
#   make info     tamano
#   make map      mapa de memoria
#   make clean
# ============================================================================

CC65_HOME ?= D:/cc65

CC   = $(CC65_HOME)/bin/cl65.exe
CA65 = $(CC65_HOME)/bin/ca65.exe
LD   = $(CC65_HOME)/bin/ld65.exe

BUILD_DIR  = build
OUTPUT_DIR = output
LD_CONFIG  = config/programa.cfg
LIB        = lib/vc.lib

PROGRAM = $(OUTPUT_DIR)/aventura.bin
MAPFILE = $(OUTPUT_DIR)/aventura.map

APP_C   = game.c sound.c joy.c
APP_OBJ = $(BUILD_DIR)/game.o $(BUILD_DIR)/sound.o $(BUILD_DIR)/joy.o $(BUILD_DIR)/startup.o

CFLAGS  = -t none -O --cpu 6502 -I include
ASFLAGS = -t none --cpu 6502

all: dirs $(PROGRAM)

dirs:
	@mkdir -p $(BUILD_DIR) $(OUTPUT_DIR)

$(BUILD_DIR)/game.o: game.c include/video.h include/romapi.h include/joy.h include/sound.h
	$(CC) -c $(CFLAGS) -o $@ game.c

$(BUILD_DIR)/sound.o: sound.c include/sound.h
	$(CC) -c $(CFLAGS) -o $@ sound.c

$(BUILD_DIR)/joy.o: joy.c include/joy.h
	$(CC) -c $(CFLAGS) -o $@ joy.c

$(BUILD_DIR)/startup.o: startup.s
	$(CA65) $(ASFLAGS) -o $@ startup.s

$(PROGRAM): $(APP_OBJ) $(LIB)
	$(LD) -C $(LD_CONFIG) -m $(MAPFILE) -o $@ $(APP_OBJ) $(LIB) $(CC65_HOME)/lib/none.lib

info:
	@if [ -f $(PROGRAM) ]; then ls -l $(PROGRAM); else echo "no compilado"; fi

map:
	@cat $(MAPFILE)

clean:
	rm -rf $(BUILD_DIR) $(OUTPUT_DIR)
	@echo "Limpieza completa (lib/vc.lib se conserva)"

.PHONY: all dirs clean info map
