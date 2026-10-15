"""Compara tiempos secuencial vs paralelo con HILOS y genera CSV + gráfica."""

import csv
import os
import time

import matplotlib.pyplot as plt

from sec_version import create_board, step_sequential

from parallelt import avanzar_hilos


SIZES = [100, 500, 1000, 1500, 2000, 2500, 3000]
THREAD_COUNTS = [2, 4, 8, 16]
GENERATIONS = 100
REPEATS = 5


def measure_sequential(board):
    start = time.perf_counter()
    current = board.copy()
    for _ in range(GENERATIONS):
        current = step_sequential(current)
    return (time.perf_counter() - start) / GENERATIONS


def measure_threads(board, threads):
    # Calentamiento inicial para no medir el arranque de los hilos.
    avanzar_hilos(board, 1, threads)
    start = time.perf_counter()
    avanzar_hilos(board, GENERATIONS, threads)
    return (time.perf_counter() - start) / GENERATIONS


def main():
    rows = []
    for size in SIZES:
        print(f"\nTablero {size}x{size}")
        board = create_board(size)

        seq_samples = [measure_sequential(board) for _ in range(REPEATS)]
        seq_time = min(seq_samples)
        rows.append({
            "size": size, "mode": "SEQ", "workers": 1,
            "seconds_per_generation": seq_time, "speedup": 1.0
        })
        print(f"  SEQ: {seq_time:.6f} s/generación")

        for threads in THREAD_COUNTS:
            if threads > os.cpu_count():
                continue
            samples = [measure_threads(board, threads) for _ in range(REPEATS)]
            par_time = min(samples)
            speedup = seq_time / par_time
            rows.append({
                "size": size, "mode": "HILOS", "workers": threads,
                "seconds_per_generation": par_time, "speedup": speedup
            })
            print(f"  HILOS ({threads}): {par_time:.6f} s/gen; speedup={speedup:.2f}x")

    with open("benchmark_hilos_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "size", "mode", "workers", "seconds_per_generation", "speedup"
        ])
        writer.writeheader()
        writer.writerows(rows)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for mode, workers, label in [
        ("SEQ", 1, "Secuencial"),
        *(("HILOS", threads, f"{threads} hilos") for threads in THREAD_COUNTS),
    ]:
        subset = [r for r in rows if r["mode"] == mode and r["workers"] == workers]
        if subset:
            axes[0].plot(
                [r["size"] for r in subset],
                [r["seconds_per_generation"] for r in subset],
                marker="o", label=label
            )

    axes[0].set_title("Tiempo por generación")
    axes[0].set_xlabel("Tamaño del tablero")
    axes[0].set_ylabel("Segundos")
    axes[0].set_xticks(SIZES)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    for threads in THREAD_COUNTS:
        subset = [r for r in rows if r["mode"] == "HILOS" and r["workers"] == threads]
        if subset:
            axes[1].plot(
                [r["size"] for r in subset],
                [r["speedup"] for r in subset],
                marker="o", label=f"{threads} hilos"
            )

    axes[1].axhline(1.0, linestyle="--", label="Sin aceleración")
    axes[1].set_title("Speedup = tiempo secuencial / paralelo")
    axes[1].set_xlabel("Tamaño del tablero")
    axes[1].set_ylabel("Aceleración")
    axes[1].set_xticks(SIZES)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig("benchmark_hilos_results.png", dpi=160)
    print("\nArchivos creados: benchmark_hilos_results.csv y benchmark_hilos_results.png")


if __name__ == "__main__":
    main()