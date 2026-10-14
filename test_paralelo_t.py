"""Benchmark: versiones secuencial, multiproceso y con hilos del Juego de la Vida."""

import time

import numpy as np

from par_version import simular
from parallelt import avanzar_hilos
from sec_version import step_sequential


def secuencial(tablero, generaciones):
    for _ in range(generaciones):
        tablero = step_sequential(tablero)
    return tablero


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    todo_ok = True

    for tamano in (100, 500, 1000):
        inicial = rng.integers(0, 2, size=(tamano, tamano), dtype=np.uint8)

        for generaciones in (50, 100, 500):
            inicio_sec = time.perf_counter()
            esperado = secuencial(inicial.copy(), generaciones)
            tiempo_sec = time.perf_counter() - inicio_sec

            for procesos in (2, 4):
                obtenido, tiempo_par = simular(
                    inicial.copy(), procesos, generaciones
                )
                ok = np.array_equal(esperado, obtenido)
                todo_ok &= ok
                speedup = tiempo_sec / tiempo_par if tiempo_par > 0 else 0.0
                print(
                    f"tam={tamano:4d} P={procesos} gen={generaciones:3d} "
                    f"| sec={tiempo_sec:6.3f}s par={tiempo_par:6.3f}s "
                    f"speedup={speedup:4.2f}x {'OK' if ok else 'FALLA'}"
                )

            for hilos in (2, 4):
                inicio_hilos = time.perf_counter()
                obtenido_hilos = avanzar_hilos(
                    inicial.copy(), generaciones, hilos
                )
                tiempo_hilos = time.perf_counter() - inicio_hilos
                ok_hilos = np.array_equal(esperado, obtenido_hilos)
                todo_ok &= ok_hilos
                speedup_hilos = (
                    tiempo_sec / tiempo_hilos if tiempo_hilos > 0 else 0.0
                )
                print(
                    f"tam={tamano:4d} H={hilos} gen={generaciones:3d} "
                    f"| sec={tiempo_sec:6.3f}s hilos={tiempo_hilos:6.3f}s "
                    f"speedup={speedup_hilos:4.2f}x "
                    f"{'OK' if ok_hilos else 'FALLA'}"
                )

    print("\nRESULTADO:", "TODO CORRECTO" if todo_ok else "HAY DIFERENCIAS")
