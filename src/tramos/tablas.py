"Cálculo de tabla de valores en torno al punto de acumulación."

from __future__ import annotations


def generar_tabla_valores(datos_funcion: dict) -> dict:

    tipo = datos_funcion["tipo"]
    a = datos_funcion["a"]
    tramos = datos_funcion["tramos"]

    valores_x = [a - 5, a - 4, a - 3, a - 2, a - 1, a, a + 1, a + 2, a + 3, a + 4, a + 5]
    filas = []

    for x in valores_x:
        y_val = None
        
        if tipo == "removible":
            # f(x) = ((x - a)(x + d1)) / (x - a) -> Equivalente a x + d1 para x != a
            d1 = tramos["d1"]
            if x == a:
                y_val = "No def"
            else:
                y_val = round(float(x + d1), 2)

        elif tipo == "salto":
            # Rama izquierda si x < a, rama derecha si x >= a
            if x < a:
                y_val = round(float(x + tramos["d2"]), 2)
            else:
                y_val = round(float(x + tramos["d4"]), 2)

        elif tipo == "infinita":
            # f(x) = numerador / (x - a)
            if x == a:
                y_val = "No def"
            else:
                y_val = round(float(tramos["numerador"] / (x - a)), 2)

        filas.append({"x": x, "y": y_val})

    # Construimos las líneas de texto formateadas de la tabla
    pasos = [
        "",
        "--- Tabla de Valores (Evolución en el entorno de a) ---",
        f"  {'x':>5} | {'f(x)':>8}",
        f"  {'-'*5}-+-{'-'*8}"
    ]
    for f in filas:
        x_str = f"{f['x']}"
        y_str = f"{f['y']}"
        pasos.append(f"  {x_str:>5} | {y_str:>8}")

    return {
        "filas": filas,
        "pasos": pasos
    }