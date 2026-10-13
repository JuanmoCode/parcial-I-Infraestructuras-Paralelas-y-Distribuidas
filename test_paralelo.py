"""Benchmark: versión secuencial vs paralela del Juego de la Vida."""

import numpy as np
import time
from sec_version import step_sequential
from par_version import simular


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
                obtenido, seg = simular(inicial.copy(), procesos, generaciones)
                ok = np.array_equal(esperado, obtenido)
                todo_ok &= ok
                speedup = tiempo_sec / seg if seg > 0 else 0.0
                print(f"tam={tamano:4d} P={procesos} gen={generaciones:3d} "
                      f"| sec={tiempo_sec:6.3f}s par={seg:6.3f}s "
                      f"speedup={speedup:4.2f}x {'OK ' if ok else 'FALLA'}")

    print("\nRESULTADO:", "TODO CORRECTO" if todo_ok else "HAY DIFERENCIAS")    