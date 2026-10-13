"""
Versión paralela del Juego de la Vida con multiprocessing y paso de mensajes.

Diseño:
- Los procesos se crean UNA sola vez; cada uno posee una franja de filas.
- Cada generación, los vecinos (arriba/abajo, tablero toroidal) intercambian
  solo sus filas frontera por colas dedicadas (variante B).
- El proceso principal manda órdenes por una cola por trabajador:
      ("AVANZA", n)  -> haz n generaciones y devuelve la franja
      ("TERMINA",)   -> sal del bucle
- Los trabajadores responden por una cola de resultados:
      ("FRANJA", id, arreglo)
"""

import multiprocessing as mp
import time

import numpy as np

from sec_version import siguiente_generacion


# =========================================================
# TRABAJADOR
# =========================================================

def trabajador(id_, franja, cola_ordenes, cola_resultados,
               entrada_desde_arriba, entrada_desde_abajo,
               salida_hacia_arriba, salida_hacia_abajo):
    """
    entrada_desde_arriba : donde el vecino de arriba deja SU última fila.
    entrada_desde_abajo  : donde el vecino de abajo deja SU primera fila.
    salida_hacia_arriba  : cola 'desde_abajo' del vecino de arriba.
    salida_hacia_abajo   : cola 'desde_arriba' del vecino de abajo.
    """
    while True:
        orden = cola_ordenes.get()

        if orden[0] == "TERMINA":
            break

        n = orden[1]

        for _ in range(n):
            # 1) Enviar primero (put no bloquea), así nadie se interbloquea.
            salida_hacia_arriba.put(franja[0].copy())
            salida_hacia_abajo.put(franja[-1].copy())

            # 2) Recibir las filas fantasma (get bloquea hasta que lleguen).
            fantasma_superior = entrada_desde_arriba.get()
            fantasma_inferior = entrada_desde_abajo.get()

            # 3) Bloque ampliado: fantasma + filas reales + fantasma.
            bloque = np.vstack((
                fantasma_superior[np.newaxis, :],
                franja,
                fantasma_inferior[np.newaxis, :],
            ))

            # 4) Calcular y quedarse solo con las filas reales.
            #    Las filas fantasma del resultado son incorrectas (np.roll
            #    envuelve en filas) pero se descartan.
            franja = siguiente_generacion(bloque)[1:-1]

        cola_resultados.put(("FRANJA", id_, franja))


# =========================================================
# MOTOR (lado del proceso principal)
# =========================================================

class MotorParalelo:
    def __init__(self, tablero, num_procesos):
        filas = tablero.shape[0]
        if num_procesos < 1 or num_procesos > filas:
            raise ValueError("num_procesos debe estar entre 1 y el número de filas")

        self.P = num_procesos
        self.procesos = []

        # Reparto: N // P filas para todos y una extra para los primeros N % P.
        franjas = np.array_split(tablero, self.P, axis=0)

        # Colas: se crean aquí, antes de lanzar los procesos.
        self.ordenes = [mp.Queue() for _ in range(self.P)]
        self.resultados = mp.Queue()
        self.desde_arriba = [mp.Queue() for _ in range(self.P)]
        self.desde_abajo = [mp.Queue() for _ in range(self.P)]

        for i in range(self.P):
            arriba = (i - 1) % self.P
            abajo = (i + 1) % self.P

            p = mp.Process(
                target=trabajador,
                args=(
                    i,
                    franjas[i].copy(),
                    self.ordenes[i],
                    self.resultados,
                    self.desde_arriba[i],
                    self.desde_abajo[i],
                    # Cruce: mi primera fila es la "desde abajo" del de arriba,
                    # mi última fila es la "desde arriba" del de abajo.
                    self.desde_abajo[arriba],
                    self.desde_arriba[abajo],
                ),
            )
            self.procesos.append(p)
            p.start()

    def solicitar(self, n=1):
        """Envía la orden AVANZA a todos los trabajadores (no espera)."""
        for q in self.ordenes:
            q.put(("AVANZA", n))

    def recolectar(self):
        """Espera las P franjas, las ordena por id y reconstruye el tablero."""
        partes = [None] * self.P
        for _ in range(self.P):
            _, id_, franja = self.resultados.get()
            partes[id_] = franja
        return np.vstack(partes)

    def avanzar(self, n=1):
        """Versión bloqueante: pide n generaciones y devuelve el tablero."""
        self.solicitar(n)
        return self.recolectar()

    def cerrar(self):
        for q in self.ordenes:
            q.put(("TERMINA",))
        for p in self.procesos:
            p.join()


# =========================================================
# MODO MEDICIÓN (sin GUI)
# =========================================================

def simular(tablero, num_procesos, generaciones):
    """Devuelve (tablero_final, segundos). El cronómetro excluye la creación
    de los procesos: empieza al enviar la orden y termina al recibir todo."""
    motor = MotorParalelo(tablero, num_procesos)
    try:
        inicio = time.perf_counter()
        final = motor.avanzar(generaciones)
        segundos = time.perf_counter() - inicio
    finally:
        motor.cerrar()
    return final, segundos