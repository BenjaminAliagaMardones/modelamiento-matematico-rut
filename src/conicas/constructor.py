"Construcción de la ecuación general de segundo grado a partir del RUT."

from __future__ import annotations

import sys

from src.rut.validador import validar_rut


def _fmt(x: float) -> str:
    if x == int(x):
        return str(int(x))
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return s


def _termino(coef: float, simbolo: str) -> str | None:
    if coef == 0:
        return None
    abs_coef = abs(coef)
    if abs_coef == 1 and simbolo:
        cuerpo = simbolo
    else:
        cuerpo = f"{_fmt(abs_coef)}{simbolo}"
    return ("-" if coef < 0 else "") + cuerpo


def _construir_ecuacion_str(A: float, B: float, C: float, D: float, E: float) -> str:
    partes = []
    for coef, simbolo in [(A, "x²"), (B, "y²"), (C, "x"), (D, "y"), (E, "")]:
        t = _termino(coef, simbolo)
        if t is None:
            continue
        if not partes:
            partes.append(t)
        elif t.startswith("-"):
            partes.append(f"- {t[1:]}")
        else:
            partes.append(f"+ {t}")
    if not partes:
        return "0 = 0"
    return " ".join(partes) + " = 0"


def construir_ecuacion(entrada: str) -> dict:
    "Construye la ecuación general Ax² + By² + Cx + Dy + E = 0 desde un RUT válido."
    rut = validar_rut(entrada)
    if not rut["es_valido"]:
        raise ValueError(
            f"RUT inválido. DV esperado: {rut['dv_calculado']}, "
            f"DV ingresado: {rut['dv_ingresado']}."
        )

    d = rut["digitos"]
    v = rut["v"]
    pasos: list[str] = []
    reglas: list[str] = []

    pasos.append(
        "Dígitos extraídos: " + ", ".join(f"d{i}={d[f'd{i}']}" for i in range(1, 9))
    )
    pasos.append(f"Valor auxiliar v = {v}  (DV='{rut['dv_ingresado']}')")
    pasos.append("")
    pasos.append("Cálculo de los coeficientes base:")

    suma_AB = d["d1"] + d["d2"]
    A = suma_AB / v
    pasos.append(
        f"  A = (d1 + d2) / v = ({d['d1']} + {d['d2']}) / {v} = {suma_AB}/{v} = {_fmt(A)}"
    )

    suma_B = d["d3"] + d["d4"]
    B = suma_B / v
    pasos.append(
        f"  B = (d3 + d4) / v = ({d['d3']} + {d['d4']}) / {v} = {suma_B}/{v} = {_fmt(B)}"
    )

    C = -(d["d5"] + d["d6"])
    pasos.append(f"  C = -(d5 + d6) = -({d['d5']} + {d['d6']}) = {C}")

    D = -(d["d7"] + d["d8"])
    pasos.append(f"  D = -(d7 + d8) = -({d['d7']} + {d['d8']}) = {D}")

    E = d["d1"] + d["d3"] + d["d5"] + d["d7"]
    pasos.append(
        f"  E = d1 + d3 + d5 + d7 = "
        f"{d['d1']} + {d['d3']} + {d['d5']} + {d['d7']} = {E}"
    )

    A_base, B_base = A, B

    pasos.append("")
    pasos.append("Aplicación de reglas de ajuste (orden del enunciado):")

    if d["d8"] % 2 == 1:
        B = -B
        pasos.append(f"  Regla 1: d8={d['d8']} es impar  →  B := -B = {_fmt(B)}")
        reglas.append("d8 impar (B = -B)")
    else:
        pasos.append(f"  Regla 1: d8={d['d8']} es par  →  no se aplica.")

    if d["d1"] == d["d2"]:
        B = A
        pasos.append(f"  Regla 2: d1 = d2 = {d['d1']}  →  B := A = {_fmt(B)}")
        reglas.append("d1 == d2 (B = A)")
    else:
        pasos.append(
            f"  Regla 2: d1={d['d1']} ≠ d2={d['d2']}  →  no se aplica."
        )

    suma_56 = d["d5"] + d["d6"]
    if suma_56 % 3 == 0:
        if d["d7"] % 2 == 0:
            B = 0.0
            pasos.append(
                f"  Regla 3: d5+d6 = {suma_56} es múltiplo de 3 y d7={d['d7']} es par"
                f"  →  B := 0 (parábola eje vertical)"
            )
            reglas.append("parábola eje vertical (B = 0)")
        else:
            A = 0.0
            pasos.append(
                f"  Regla 3: d5+d6 = {suma_56} es múltiplo de 3 y d7={d['d7']} es impar"
                f"  →  A := 0 (parábola eje horizontal)"
            )
            reglas.append("parábola eje horizontal (A = 0)")
    else:
        pasos.append(
            f"  Regla 3: d5+d6 = {suma_56} no es múltiplo de 3  →  no se aplica."
        )

    ecuacion = _construir_ecuacion_str(A, B, C, D, E)
    pasos.append("")
    pasos.append(f"Ecuación general resultante:  {ecuacion}")

    return {
        "rut": rut,
        "coeficientes_base": {"A": A_base, "B": B_base, "C": C, "D": D, "E": E},
        "coeficientes": {"A": A, "B": B, "C": C, "D": D, "E": E},
        "reglas_aplicadas": reglas,
        "pasos": pasos,
        "ecuacion": ecuacion,
    }


def _main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python3 -m src.conicas.constructor <RUT>")
        print("Ejemplo: python3 -m src.conicas.constructor 12345678-5")
        sys.exit(1)
    try:
        resultado = construir_ecuacion(sys.argv[1])
    except ValueError as err:
        print(f"Error: {err}")
        sys.exit(1)
    for linea in resultado["pasos"]:
        print(linea)


if __name__ == "__main__":
    _main()
