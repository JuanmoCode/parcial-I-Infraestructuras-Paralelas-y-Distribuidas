"""Prueba de corrección: paralela vs secuencial, celda por celda."""

import numpy as np

from sec_version import siguiente_generacion
from par_version import simular


def secuencial(tablero, generaciones):
    for _ in range(generaciones):
        tablero = siguiente_generacion(tablero)
    return tablero


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    todo_ok = True

    # 100 filas con 3 procesos NO divide exacto: caso importante.
    for tamano in (100, 500, 1000):
        inicial = rng.integers(0, 2, size=(tamano, tamano), dtype=np.uint8)

        for procesos in (1, 2, 3, 4):
            for generaciones in (1, 10, 50):
                esperado = secuencial(inicial.copy(), generaciones)
                obtenido, seg = simular(inicial.copy(), procesos, generaciones)
                ok = np.array_equal(esperado, obtenido)
                todo_ok &= ok
                print(f"tam={tamano:4d} P={procesos} gen={generaciones:3d} "
                      f"{'OK ' if ok else 'FALLA'} ({seg:.3f}s)")

    print("\nRESULTADO:", "TODO CORRECTO" if todo_ok else "HAY DIFERENCIAS")