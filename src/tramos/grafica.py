"Cálculo de puntos densos y coordenadas para graficar la función por tramos."

from __future__ import annotations


def obtener_puntos_grafica(datos_funcion: dict) -> dict:
    tipo = datos_funcion["tipo"]
    a = datos_funcion["a"]
    tramos = datos_funcion["tramos"]

    xmin, xmax = a - 8, a + 8
    ymin, ymax = -10, 10

    puntos = []
    # Marcadores especiales en el punto crítico: (x, y, "abierto"|"cerrado").
    marcadores: list[tuple[float, float, str]] = []
    # Posición de una asíntota vertical, si corresponde.
    asintota_x = None

    pasos = 250

    if tipo == "removible":
        # f(x) = x + d1, para x != a  ->  recta con un hueco en (a, a + d1)
        d1 = tramos["d1"]
        for i in range(pasos + 1):
            x = xmin + (xmax - xmin) * (i / pasos)
            if abs(x - a) > 0.05:
                y = x + d1
                if ymin <= y <= ymax:
                    puntos.append((x, y))
        y_hueco = a + d1
        if ymin <= y_hueco <= ymax:
            marcadores.append((float(a), float(y_hueco), "abierto"))

    elif tipo == "salto":
        # Rama izquierda (x < a): f1(x) = x + d2  ->  extremo abierto en a
        for i in range(pasos + 1):
            x = xmin + (a - xmin) * (i / pasos)
            if x < a:
                y = x + tramos["d2"]
                if ymin <= y <= ymax:
                    puntos.append((x, y))
        # Rama derecha (x >= a): f2(x) = x + d4  ->  extremo cerrado en a
        for i in range(pasos + 1):
            x = a + (xmax - a) * (i / pasos)
            if x >= a:
                y = x + tramos["d4"]
                if ymin <= y <= ymax:
                    puntos.append((x, y))
        y_izq = a + tramos["d2"]
        y_der = a + tramos["d4"]
        if ymin <= y_izq <= ymax:
            marcadores.append((float(a), float(y_izq), "abierto"))
        if ymin <= y_der <= ymax:
            marcadores.append((float(a), float(y_der), "cerrado"))

    elif tipo == "infinita":
        # f(x) = numerador / (x - a)  ->  asíntota vertical en x = a
        numerador = tramos["numerador"]
        for i in range(pasos + 1):
            x = xmin + (xmax - xmin) * (i / pasos)
            if abs(x - a) > 0.08:  # Evitamos la división por cero exacta en la asíntota
                y = numerador / (x - a)
                if ymin <= y <= ymax:
                    puntos.append((x, y))
        asintota_x = float(a)

    return {
        "ventana": (xmin, xmax, ymin, ymax),
        "puntos": puntos,
        "marcadores": marcadores,
        "asintota_x": asintota_x,
    }
