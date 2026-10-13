

import numpy as np
import time


TAMANOS = {
    "1": (100, 100),
    "2": (500, 500),
    "3": (1000, 1000)
}


def create_board(tamano):
    """Crea una matriz aleatoria de ceros y unos."""
    return np.random.randint(0, 2, size=(tamano, tamano), dtype=np.uint8)


def step_sequential(tablero):
    """Calcula la siguiente generación del Juego de la Vida."""

    # Contar vecinos vivos de cada celda.
    vecinos = np.zeros_like(tablero, dtype=np.uint8)

    for desplazamiento_fila in (-1, 0, 1):
        for desplazamiento_columna in (-1, 0, 1):

            if desplazamiento_fila == 0 and desplazamiento_columna == 0:
                continue

            vecinos += np.roll(
                np.roll(tablero, desplazamiento_fila, axis=0),
                desplazamiento_columna,
                axis=1
            )

    # Reglas de Conway.
    sobrevive = (tablero == 1) & (
        (vecinos == 2) | (vecinos == 3)
    )

    nace = (tablero == 0) & (vecinos == 3)

    # Las celdas vivas se representan con 1 y las muertas con 0.
    return (sobrevive | nace).astype(np.uint8)


def mostrar_tablero(tablero):
    """Imprime la matriz en consola."""
    print(tablero)


def main():
    print("=== JUEGO DE LA VIDA DE CONWAY ===")
    print("1. Grid de 100 x 100")
    print("2. Grid de 500 x 500")
    print("3. Grid de 1000 x 1000")

    opcion = input("Selecciona el tamaño del grid: ").strip()

    if opcion not in TAMANOS:
        print("Opción no válida.")
        return

    filas, columnas = TAMANOS[opcion]
    tablero = create_board(filas)

    generaciones = int(input("Número de generaciones: "))

    if generaciones < 0:
        print("El número de generaciones no puede ser negativo.")
        return

    print(f"\nTamaño del tablero: {filas} x {columnas}")
    print("\nGeneración inicial:")
    mostrar_tablero(tablero)

    inicio = time.perf_counter()

    for generacion in range(1, generaciones + 1):
        tablero = step_sequential(tablero)

        print(f"\nGeneración {generacion}:")
        mostrar_tablero(tablero)

    fin = time.perf_counter()

    print(f"\nTiempo de simulación: {fin - inicio:.4f} segundos")
    print(f"Celdas vivas finales: {np.sum(tablero)}")


if __name__ == "__main__":
    main()
