"Clasificación de la cónica a partir de los coeficientes A y B."

from __future__ import annotations

from src.conicas.algebra import Fraccion


def clasificar(coef_frac: dict) -> dict:
    "Determina el tipo de cónica según los criterios del enunciado."
    A: Fraccion = coef_frac["A"]
    B: Fraccion = coef_frac["B"]

    a_cero = A.es_cero()
    b_cero = B.es_cero()

    if a_cero and b_cero:
        tipo = "degenerada"
        razon = "No hay términos cuadráticos (A = 0 y B = 0): no es una cónica."
    elif a_cero or b_cero:
        tipo = "parábola"
        cual = "A" if a_cero else "B"
        razon = f"Solo un término cuadrático es cero ({cual} = 0): es una parábola."
    elif A == B:
        tipo = "circunferencia"
        razon = f"A y B son iguales (A = B = {A}): es una circunferencia."
    elif A.signo() == B.signo():
        tipo = "elipse"
        razon = "A y B tienen el mismo signo pero son distintos: es una elipse."
    else:
        tipo = "hipérbola"
        razon = "A y B tienen signos opuestos: es una hipérbola."

    pasos = [f"Miramos A = {A} y B = {B}.", razon]
    return {"tipo": tipo, "razon": razon, "pasos": pasos}
