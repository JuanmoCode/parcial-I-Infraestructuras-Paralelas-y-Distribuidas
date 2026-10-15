

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
    filas, columnas = tablero.shape

    # Tablero toroidal: se rodea con un marco de una celda que copia
    # los bordes opuestos.
    ext = np.pad(tablero, 1, mode="wrap")

    # Contar vecinos vivos de cada celda.
    vecinos = np.zeros_like(tablero, dtype=np.uint8)

    for di in range(3):
        for dj in range(3):
            if di == 1 and dj == 1:
                continue
            vecinos += ext[di:di + filas, dj:dj + columnas]

    # Reglas de Conway:
    # con 3 vecinos la celda queda viva (nace o sobrevive);
    # con 2 vecinos solo queda viva si ya estaba viva;
    # en cualquier otro caso queda muerta.
    return ((vecinos == 3) | ((tablero == 1) & (vecinos == 2))).astype(np.uint8)


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
