# Juego de la Vida — Versión Paralela con Hilos

## 1. Descripción del proyecto

Esta implementación del Juego de la Vida de Conway utiliza programación concurrente con hilos (`threading`) y operaciones vectorizadas de NumPy para calcular varias generaciones del tablero.

El objetivo es dividir el trabajo entre varios hilos, de manera que cada uno calcule una franja de filas del tablero. Todos los hilos trabajan sobre un mismo espacio de memoria y utilizan un mecanismo de sincronización para garantizar que las generaciones se calculen correctamente.

La implementación utiliza tres mecanismos principales:

- **Descomposición de datos:** el tablero se divide en franjas horizontales.
- **Doble buffer:** se utilizan dos matrices para separar la generación actual de la siguiente.
- **Barrier:** sincroniza los hilos al terminar cada generación.

## 2. Tecnologías utilizadas

- **Python:** lenguaje de programación.
- **NumPy:** almacenamiento de matrices y operaciones vectorizadas para contar los vecinos de las células.
- **Threading:** creación y ejecución de hilos.
- **Barrier:** sincronización entre los hilos al finalizar cada generación.

## 3. Reglas del Juego de la Vida

Cada célula puede estar viva (`1`) o muerta (`0`). Su estado en la siguiente generación depende de sus ocho vecinos.

Las reglas son:

1. Una célula viva con menos de dos vecinos vivos muere por aislamiento.
2. Una célula viva con dos o tres vecinos vivos sobrevive.
3. Una célula viva con más de tres vecinos vivos muere por sobrepoblación.
4. Una célula muerta con exactamente tres vecinos vivos nace.

El tablero utiliza condiciones de borde toroidales: los bordes opuestos se consideran conectados. Por tanto, las células de la primera fila tienen como vecinas a las de la última fila, y lo mismo ocurre con las columnas.

## 4. Estrategia de paralelización

Se utiliza una estrategia de **paralelismo por datos**. En lugar de asignar tareas diferentes a cada hilo, todos realizan la misma operación sobre una parte diferente del tablero.

Por ejemplo, si el tablero tiene 12 filas y se utilizan 3 hilos, la distribución sería:

| Hilo | Filas asignadas |
|---|---|
| Hilo 0 | 0–3 |
| Hilo 1 | 4–7 |
| Hilo 2 | 8–11 |

Cada hilo calcula exclusivamente las filas que le corresponden. Sin embargo, para calcular correctamente las células de los extremos de su franja, también necesita consultar las filas vecinas.

Como todos los hilos comparten memoria, pueden leer directamente el tablero actual sin intercambiar filas mediante colas o mensajes entre procesos.

## 5. Doble buffer

El algoritmo utiliza dos matrices:

- `bufs[0]`: contiene el tablero inicial o una generación calculada anteriormente.
- `bufs[1]`: almacena la siguiente generación.

Durante cada generación, todos los hilos leen de una matriz y escriben en la otra. En la generación siguiente, intercambian sus funciones.

Por ejemplo:

| Generación | Matriz de lectura | Matriz de escritura |
|---|---|---|
| 0 → 1 | `bufs[0]` | `bufs[1]` |
| 1 → 2 | `bufs[1]` | `bufs[0]` |
| 2 → 3 | `bufs[0]` | `bufs[1]` |

Esta estrategia evita que un hilo modifique una célula mientras otro todavía está leyendo su estado en la generación actual.

## 6. Funcionamiento de la función `_franja()`

La función `_franja(actual, dst, r0, r1)` realiza el cálculo de una parte del tablero.

Sus parámetros son:

- `actual`: matriz de la generación actual.
- `dst`: matriz donde se almacena la siguiente generación.
- `r0`: índice de la primera fila asignada al hilo.
- `r1`: límite final de las filas, sin incluirlo.

El cálculo se divide en cuatro etapas.

### 6.1. Selección de las filas necesarias

Se seleccionan las filas de la franja y las filas adyacentes que necesita para consultar los vecinos superiores e inferiores.

El uso del operador módulo permite envolver los índices de fila, implementando el comportamiento toroidal.

### 6.2. Extensión de las columnas

Se añaden temporalmente las columnas de los extremos opuestos del tablero. Esto permite que las células de la primera y última columna también tengan sus ocho vecinos.

### 6.3. Conteo de vecinos

Se crea una matriz de contadores llamada `vec`, inicialmente llena de ceros.

Mediante dos bucles, se recorren las ocho posiciones que rodean a cada célula. En cada iteración se utiliza `np.add()` para sumar una región desplazada de la matriz ampliada.

El argumento `out=vec` indica que el resultado se almacena directamente en la matriz de contadores, evitando crear un nuevo arreglo para cada suma.

Al finalizar el proceso, cada posición de `vec` contiene la cantidad de vecinos vivos de la célula correspondiente.

### 6.4. Aplicación de las reglas

Una vez calculados los vecinos, se evalúan las reglas del Juego de la Vida mediante operaciones vectorizadas de NumPy.

El hilo escribe el resultado únicamente en las filas que tiene asignadas dentro de `dst`.

## 7. Sincronización mediante Barrier

Se utiliza `threading.Barrier(hilos)` para coordinar a todos los hilos.

Al terminar de calcular su franja, cada hilo ejecuta:

```python
barrera.wait()
```

Esta instrucción bloquea al hilo hasta que todos los participantes hayan alcanzado la barrera.

Cuando todos han terminado la generación actual, pueden continuar y comenzar la siguiente.

La barrera evita que un hilo empiece a leer un buffer como generación actual mientras otro todavía está escribiendo en ese mismo buffer los resultados de la generación anterior.

No se necesita un `Lock` para proteger las escrituras del tablero porque cada hilo escribe en un rango diferente de filas y todos leen de una matriz distinta de la que están modificando.

Esta garantía depende de que las franjas no se superpongan y de que todos los hilos alcancen correctamente la barrera en cada generación.

## 8. Funciones principales

### `avanzar_hilos(tablero, n=1, hilos=4)`

Es la función principal de la implementación.

Recibe el tablero inicial, el número de generaciones que se quieren calcular y la cantidad de hilos.

Sus pasos son:

1. Preparar los dos buffers.
2. Dividir las filas entre los hilos.
3. Crear la barrera de sincronización.
4. Iniciar los hilos.
5. Calcular las generaciones mediante doble buffer.
6. Esperar a que todos los hilos terminen mediante `join()`.
7. Devolver el tablero de la última generación.

### `siguiente_generacion_hilos(tablero, hilos=4)`

Es una función auxiliar que utiliza `avanzar_hilos()` para calcular una sola generación.

## 9. Ejemplo de uso

Si el archivo de implementación se llama `paralela_hilos.py`, se puede utilizar desde otro archivo Python de la siguiente manera:

```python
import numpy as np
from paralela_hilos import avanzar_hilos

# Crear un tablero inicial de 100 x 100.
tablero = np.random.randint(
    0, 2, size=(100, 100), dtype=np.uint8
)

# Calcular 50 generaciones utilizando 4 hilos.
resultado = avanzar_hilos(
    tablero,
    n=50,
    hilos=4
)

print("Tablero final:")
print(resultado)
```

El resultado contiene el estado del tablero después de las 50 generaciones.

## 10. Ventajas y limitaciones

### Ventajas

- Los hilos comparten memoria y pueden acceder directamente a los arreglos NumPy.
- No es necesario transferir matrices entre procesos mediante colas.
- El doble buffer evita mezclar estados de generaciones diferentes.
- La barrera garantiza la sincronización entre generaciones.
- Las operaciones vectorizadas permiten procesar muchas células en cada operación de NumPy.

### Limitaciones

- La creación y sincronización de los hilos tiene un coste.
- El GIL de CPython puede limitar el paralelismo de las operaciones que ejecutan código Python.
- El rendimiento depende de qué operaciones de NumPy liberan el GIL, del tamaño del tablero y del ancho de banda de memoria.
- Todos los hilos deben llegar a la barrera; si uno falla durante el cálculo, los demás pueden quedar bloqueados.
- Para tableros pequeños, el coste de coordinación puede superar las ventajas del paralelismo.

Por estas razones, no se debe asumir que utilizar más hilos siempre produce una ejecución más rápida.

