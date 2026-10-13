
import pygame
import numpy as np
import time

from sec_version import create_board
from parallelt import avanzar_hilos


# =========================================================
# CONFIGURACION GENERAL
# =========================================================

pygame.init()

ANCHO = 1100
ALTO = 820
PANEL_ALTO = 190
AREA_ALTO = ALTO - PANEL_ALTO

FPS = 60

TAMANOS = [100, 500, 1000]

# Paleta retro FPS
FONDO = (9, 10, 10)
PANEL = (35, 32, 30)
PANEL_OSCURO = (20, 19, 18)
METAL = (75, 68, 59)
BORDE = (130, 83, 54)
ROJO = (190, 35, 24)
ROJO_OSCURO = (95, 22, 18)
VERDE = (100, 255, 100)
VERDE_OSCURO = (30, 115, 40)
BLANCO = (225, 218, 195)
GRIS = (145, 137, 120)
AMARILLO = (255, 190, 65)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("CELL DOOM // Conway Simulation")

reloj = pygame.time.Clock()

fuente = pygame.font.SysFont("monospace", 18, bold=True)
fuente_pequena = pygame.font.SysFont("monospace", 13, bold=True)
fuente_grande = pygame.font.SysFont("monospace", 27, bold=True)
fuente_titulo = pygame.font.SysFont("monospace", 30, bold=True)


# =========================================================
# ESTADO DEL JUEGO
# =========================================================

tamano = 100
tablero = create_board(tamano)

ejecutando = False
velocidad = 10
generacion = 0
acumulado = 0.0

tiempo_generacion = 0.0


# =========================================================
# UTILIDADES GRAFICAS
# =========================================================

def texto(superficie, contenido, x, y, color=BLANCO, font=fuente):
    imagen = font.render(str(contenido), False, color)
    superficie.blit(imagen, (x, y))


def panel_rect(rect, color=PANEL, borde=BORDE):
    pygame.draw.rect(pantalla, color, rect)
    pygame.draw.rect(pantalla, borde, rect, 2)


def boton(rect, etiqueta, activo=False, color=ROJO):
    """Dibuja un boton con relieve estilo juego retro."""

    x, y, ancho, alto = rect

    base = color if activo else METAL
    sombra = ROJO_OSCURO if activo else PANEL_OSCURO
    luz = (235, 100, 65) if activo else (125, 115, 95)

    pygame.draw.rect(pantalla, sombra, (x + 3, y + 3, ancho, alto))
    pygame.draw.rect(pantalla, base, rect)

    # Bordes superior/izquierdo e inferior/derecho
    pygame.draw.line(pantalla, luz, (x, y), (x + ancho - 1, y), 2)
    pygame.draw.line(pantalla, luz, (x, y), (x, y + alto - 1), 2)
    pygame.draw.line(
        pantalla, PANEL_OSCURO,
        (x, y + alto - 1), (x + ancho - 1, y + alto - 1), 2
    )
    pygame.draw.line(
        pantalla, PANEL_OSCURO,
        (x + ancho - 1, y), (x + ancho - 1, y + alto - 1), 2
    )

    imagen = fuente_pequena.render(etiqueta, False, BLANCO)
    pantalla.blit(
        imagen,
        imagen.get_rect(center=(x + ancho // 2, y + alto // 2))
    )


def dibujar_luces(x, y, cantidad=3):
    for i in range(cantidad):
        color = VERDE if i < cantidad - 1 else ROJO
        pygame.draw.rect(pantalla, color, (x + i * 17, y, 10, 8))


# =========================================================
# TABLERO
# =========================================================

def dibujar_tablero():
    pantalla.fill(FONDO, (0, 0, ANCHO, AREA_ALTO))

    # Marco del visor
    pygame.draw.rect(
        pantalla, BORDE,
        (8, 8, ANCHO - 16, AREA_ALTO - 16), 3
    )

    margen = 15
    ancho_util = ANCHO - margen * 2
    alto_util = AREA_ALTO - margen * 2

    ancho_celda = ancho_util / tamano
    alto_celda = alto_util / tamano

    filas, columnas = np.nonzero(tablero)

    # Para tamaños grandes, usar dibujo por filas.
    if tamano >= 500:
        imagen = np.zeros((tamano, tamano, 3), dtype=np.uint8)
        imagen[tablero == 1] = VERDE

        superficie = pygame.surfarray.make_surface(
            np.transpose(imagen, (1, 0, 2))
        )

        superficie = pygame.transform.scale(
            superficie, (int(ancho_util), int(alto_util))
        )

        pantalla.blit(superficie, (margen, margen))

    else:
        for fila, columna in zip(filas, columnas):
            x = margen + int(columna * ancho_celda)
            y = margen + int(fila * alto_celda)

            rect = pygame.Rect(
                x, y,
                max(1, int(np.ceil(ancho_celda))),
                max(1, int(np.ceil(alto_celda)))
            )

            pygame.draw.rect(pantalla, VERDE, rect)

    # Cabecera del visor
    pygame.draw.rect(pantalla, PANEL_OSCURO, (15, 15, 245, 27))
    texto(pantalla, "LIVE FEED // CELLULAR GRID", 22, 20, VERDE,
          fuente_pequena)

    pygame.draw.rect(
        pantalla, PANEL_OSCURO,
        (ANCHO - 210, 15, 190, 27)
    )

    texto(
        pantalla,
        "REC ●" if ejecutando else "REC OFF",
        ANCHO - 200, 20,
        ROJO if ejecutando else GRIS,
        fuente_pequena
    )


# =========================================================
# PANEL DE CONTROL
# =========================================================

def dibujar_panel():
    y = AREA_ALTO

    pygame.draw.rect(pantalla, PANEL, (0, y, ANCHO, PANEL_ALTO))
    pygame.draw.line(pantalla, ROJO, (0, y), (ANCHO, y), 4)

    # Titulo
    texto(pantalla, "CELL DOOM", 20, y + 12, ROJO, fuente_titulo)
    texto(pantalla, "// LIFE SIMULATION SYSTEM", 245, y + 23,
          GRIS, fuente_pequena)

    dibujar_luces(ANCHO - 80, y + 23)

    # Panel de botones
    panel_rect((15, y + 52, 430, 120), PANEL_OSCURO)

    texto(pantalla, "SYSTEM CONTROLS", 28, y + 59, AMARILLO,
          fuente_pequena)

    boton(
        (28, y + 85, 92, 34),
        "RUN",
        activo=ejecutando,
        color=VERDE_OSCURO
    )

    boton(
        (130, y + 85, 92, 34),
        "PAUSE",
        activo=not ejecutando,
        color=ROJO_OSCURO
    )

    boton((232, y + 85, 92, 34), "STEP", color=METAL)
    boton((334, y + 85, 92, 34), "RESET", color=ROJO_OSCURO)

    texto(pantalla, "SPACE: RUN/PAUSE   N: STEP   R: RESET",
          28, y + 139, GRIS, fuente_pequena)

    # Panel de configuracion
    panel_rect((460, y + 52, 310, 120), PANEL_OSCURO)

    texto(pantalla, "GRID SIZE", 475, y + 59, AMARILLO,
          fuente_pequena)

    for i, size in enumerate(TAMANOS):
        boton(
            (475 + i * 94, y + 85, 85, 34),
            str(size),
            activo=(tamano == size),
            color=VERDE_OSCURO
        )

    texto(pantalla, "SELECT MATRIX RESOLUTION",
          475, y + 139, GRIS, fuente_pequena)

    # Panel de telemetria
    panel_rect((785, y + 52, 300, 120), PANEL_OSCURO)

    texto(pantalla, "TELEMETRY", 800, y + 59, AMARILLO,
          fuente_pequena)

    texto(pantalla, f"GEN: {generacion}", 800, y + 83, VERDE,
          fuente_pequena)

    texto(pantalla, f"ALIVE: {int(np.sum(tablero))}", 800, y + 105,
          BLANCO, fuente_pequena)

    texto(pantalla, f"SPEED: {velocidad} GEN/S", 800, y + 127,
          BLANCO, fuente_pequena)

    texto(pantalla, "FPS: 60 // CONWAY ENGINE",
          800, y + 151, GRIS, fuente_pequena)


# =========================================================
# ACCIONES
# =========================================================

def reiniciar(nuevo_tamano=None):
    global tablero, tamano, ejecutando, generacion, acumulado

    if nuevo_tamano is not None:
        tamano = nuevo_tamano

    tablero = create_board(tamano)
    ejecutando = False
    generacion = 0
    acumulado = 0.0


def avanzar():
    global tablero, generacion, tiempo_generacion

    inicio = time.perf_counter()
    tablero = avanzar_hilos(tablero)
    tiempo_generacion = time.perf_counter() - inicio
    generacion += 1


def procesar_click(posicion):
    global ejecutando

    x, y = posicion
    panel_y = AREA_ALTO

    if not (panel_y <= y < ALTO):
        return

    y_local = y - panel_y

    # Botones de control
    if panel_y + 85 <= y < panel_y + 119:
        if 28 <= x < 120:
            ejecutando = True
        elif 130 <= x < 222:
            ejecutando = False
        elif 232 <= x < 324 and not ejecutando:
            avanzar()
        elif 334 <= x < 426:
            reiniciar()

        # Selector de tamaño
        if panel_y + 85 <= y < panel_y + 119:
            for i, size in enumerate(TAMANOS):
                x_inicio = 475 + i * 94

                if x_inicio <= x < x_inicio + 85:
                    reiniciar(size)


# =========================================================
# BUCLE PRINCIPAL
# =========================================================

def main():
    global ejecutando, velocidad, acumulado

    corriendo = True

    while corriendo:
        dt = reloj.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    procesar_click(evento.pos)

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    ejecutando = not ejecutando
                    acumulado = 0.0

                elif evento.key == pygame.K_n and not ejecutando:
                    avanzar()

                elif evento.key == pygame.K_r:
                    reiniciar()

                elif evento.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    indice = evento.key - pygame.K_1
                    reiniciar(TAMANOS[indice])

                elif evento.key in (pygame.K_PLUS, pygame.K_EQUALS,
                                     pygame.K_KP_PLUS):
                    velocidad = min(60, velocidad + 1)

                elif evento.key in (pygame.K_MINUS,
                                     pygame.K_KP_MINUS):
                    velocidad = max(1, velocidad - 1)

        if ejecutando:
            acumulado += dt
            intervalo = 1.0 / velocidad

            while acumulado >= intervalo:
                avanzar()
                acumulado -= intervalo

        dibujar_tablero()
        dibujar_panel()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
