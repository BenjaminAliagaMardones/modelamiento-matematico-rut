"Cálculo de tabla de valores en torno al punto de acumulación."

from __future__ import annotations


def _fmt_num(valor: float) -> str:
    "Formatea un número sin ceros sobrantes (ej: 5.0 -> '5', 4.999 -> '4.999')."
    if valor == int(valor):
        return str(int(valor))
    return f"{valor:.3f}".rstrip("0").rstrip(".")


def generar_tabla_valores(datos_funcion: dict) -> dict:

    tipo = datos_funcion["tipo"]
    a = datos_funcion["a"]
    tramos = datos_funcion["tramos"]

    # Valores que se acercan al punto a por izquierda y por derecha,
    # tal como pide la pauta (a ± 1, a ± 0.1, a ± 0.01, a ± 0.001).
    valores_x = [
        a - 1, a - 0.1, a - 0.01, a - 0.001,
        a,
        a + 0.001, a + 0.01, a + 0.1, a + 1,
    ]
    filas = []

    for x in valores_x:
        y_val = None

        if tipo == "removible":
            # f(x) = ((x - a)(x + d1)) / (x - a) -> Equivalente a x + d1 para x != a
            d1 = tramos["d1"]
            if x == a:
                y_val = "No def"
            else:
                y_val = round(float(x + d1), 4)

        elif tipo == "salto":
            # Rama izquierda si x < a, rama derecha si x >= a
            if x < a:
                y_val = round(float(x + tramos["d2"]), 4)
            else:
                y_val = round(float(x + tramos["d4"]), 4)

        elif tipo == "infinita":
            # f(x) = numerador / (x - a)
            if x == a:
                y_val = "No def"
            else:
                y_val = round(float(tramos["numerador"] / (x - a)), 4)

        filas.append({"x": x, "y": y_val})

    # Construimos las líneas de texto formateadas de la tabla
    pasos = [
        "",
        "--- Tabla de Valores (acercándose al punto a por ambos lados) ---",
        f"  {'x':>8} | {'f(x)':>12}",
        f"  {'-'*8}-+-{'-'*12}",
    ]
    for f in filas:
        x_str = _fmt_num(f["x"])
        y_str = f["y"] if isinstance(f["y"], str) else _fmt_num(f["y"])
        pasos.append(f"  {x_str:>8} | {y_str:>12}")

    return {
        "filas": filas,
        "pasos": pasos
    }
