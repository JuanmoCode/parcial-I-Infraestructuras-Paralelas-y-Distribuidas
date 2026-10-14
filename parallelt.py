"""Game of Life paralelo con HILOS (threading) + Barrier + doble buffer.
Un solo tablero compartido por todos los hilos (misma memoria, sin copiar).
Cada hilo ESCRIBE solo sus filas de 'siguiente' y LEE 'actual' (incluidos los
bordes de sus vecinos) -> no hay condiciones de carrera ni hacen falta Locks.
La Barrier garantiza que nadie empieza la generacion g+1 antes de que todos
terminen la g."""
import threading

import numpy as np


def _franja(actual, dst, r0, r1):
    filas, cols = actual.shape
    idx = np.arange(r0 - 1, r1 + 1) % filas
    ext = actual[idx]
    ext = np.concatenate((ext[:, -1:], ext, ext[:, :1]), axis=1)
    h = r1 - r0
    vec = np.zeros((h, cols), dtype=np.uint8)
    for di in range(3):
        for dj in range(3):
            if di == 1 and dj == 1:
                continue
            np.add(vec, ext[di:di + h, dj:dj + cols], out=vec)
    centro = actual[r0:r1]
    dst[r0:r1] = (vec == 3) | ((centro == 1) & (vec == 2))


def avanzar_hilos(tablero, n=1, hilos=4):
    """Devuelve el tablero tras n generaciones usando `hilos` hilos."""
    filas = tablero.shape[0]
    hilos = max(1, min(hilos, filas))
    bufs = [np.ascontiguousarray(tablero, dtype=np.uint8).copy(),
            np.empty_like(tablero, dtype=np.uint8)]
    lim = np.linspace(0, filas, hilos + 1).astype(int)
    barrera = threading.Barrier(hilos)

    def trabajo(k):
        for g in range(n):
            _franja(bufs[g % 2], bufs[(g + 1) % 2], lim[k], lim[k + 1])
            barrera.wait()

    ths = [threading.Thread(target=trabajo, args=(k,)) for k in range(hilos)]
    for t in ths: t.start()
    for t in ths: t.join()
    return bufs[n % 2]


def siguiente_generacion_hilos(tablero, hilos=4):
    return avanzar_hilos(tablero, 1, hilos)
