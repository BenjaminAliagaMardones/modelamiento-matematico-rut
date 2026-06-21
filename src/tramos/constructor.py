"Construcción de la función por tramos a partir del RUT."

from __future__ import annotations

from src.rut.validador import validar_rut
from src.tramos.clasificador import clasificar_tramo


def construir_funcion(entrada: str) -> dict:
    """
    Valida el RUT, determina el caso y construye las expresiones
    matemáticas de la función según la pauta.
    """
    # 1. Validar RUT
    rut = validar_rut(entrada)
    if not rut["es_valido"]:
        raise ValueError(
            f"RUT inválido. DV esperado: {rut['dv_calculado']}, "
            f"DV ingresado: {rut['dv_ingresado']}."
        )

    d = rut["digitos"]
    pasos = []

    pasos.append("Dígitos del RUT: " +
                 ", ".join(f"d{i}={d[f'd{i}']}" for i in range(1, 9)))

    # 2. Definir el punto de análisis 'a'
    a = d["d3"]
    pasos.append(f"El punto de análisis se define como a = d3 = {a}.")

    # 3. Clasificar el tramo
    clasificacion = clasificar_tramo(d["d8"])
    tipo = clasificacion["tipo"]
    pasos.extend(clasificacion["pasos"])

    # 4. Construir la función según el tipo
    funcion_str = ""
    tramos = {}

    if tipo == "removible":
        d1 = d["d1"]
        pasos.append(
            f"Construimos el Caso 1 (Discontinuidad removible) usando d1 = {d1}.")

        # Ajuste visual para evitar "x + -2" o "x - -2"
        signo_d1 = f"+ {d1}" if d1 >= 0 else f"- {abs(d1)}"
        signo_a = f"- {a}" if a >= 0 else f"+ {abs(a)}"

        f_expr = f"((x {signo_a})(x {signo_d1})) / (x {signo_a})"
        funcion_str = f"f(x) = {f_expr}  (para x ≠ {a})"

        # Guardamos los datos puros para el motor de límites posterior
        tramos = {
            "f_expr": f_expr,
            "d1": d1
        }

    elif tipo == "salto":
        d2 = d["d2"]
        d4 = d["d4"]
        pasos.append(
            f"Construimos el Caso 2 (Discontinuidad de salto) usando d2 = {d2} y d4 = {d4}.")

        signo_d2 = f"+ {d2}" if d2 >= 0 else f"- {abs(d2)}"
        signo_d4 = f"+ {d4}" if d4 >= 0 else f"- {abs(d4)}"

        f1_expr = f"x {signo_d2}"
        f2_expr = f"x {signo_d4}"

        funcion_str = f"f(x) = {{ {f1_expr}, si x < {a}  ;  {f2_expr}, si x ≥ {a} }}"
        tramos = {
            "f1_expr": f1_expr,
            "f2_expr": f2_expr,
            "d2": d2,
            "d4": d4
        }

    elif tipo == "infinita":
        d5 = d["d5"]
        numerador = d5 + 1
        pasos.append(
            f"Construimos el Caso 3 (Discontinuidad infinita) usando d5 = {d5}.")

        signo_a = f"- {a}" if a >= 0 else f"+ {abs(a)}"

        f_expr = f"{numerador} / (x {signo_a})"
        funcion_str = f"f(x) = {f_expr}"
        tramos = {
            "f_expr": f_expr,
            "numerador": numerador
        }

    pasos.append("")
    pasos.append(f"Función generada:  {funcion_str}")

    return {
        "rut": rut,
        "a": a,
        "tipo": tipo,
        "funcion_str": funcion_str,
        "tramos": tramos,
        "pasos": pasos
    }
