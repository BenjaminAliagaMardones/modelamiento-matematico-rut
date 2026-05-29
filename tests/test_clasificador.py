"""Pruebas del clasificador de cónicas.

Ejecutar:  /usr/bin/python3 tests/test_clasificador.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conicas.algebra import Fraccion
from src.conicas.clasificador import clasificar
from src.conicas.constructor import construir_ecuacion


def _coef(A, B):
    return {"A": Fraccion(*A) if isinstance(A, tuple) else Fraccion(A),
            "B": Fraccion(*B) if isinstance(B, tuple) else Fraccion(B),
            "C": Fraccion(0), "D": Fraccion(0), "E": Fraccion(0)}


def test_circunferencia() -> None:
    assert clasificar(_coef(2, 2))["tipo"] == "circunferencia"


def test_elipse() -> None:
    assert clasificar(_coef((3, 5), (7, 5)))["tipo"] == "elipse"


def test_hiperbola() -> None:
    assert clasificar(_coef((5, 11), (-9, 11)))["tipo"] == "hipérbola"


def test_parabola() -> None:
    assert clasificar(_coef(0, 3))["tipo"] == "parábola"
    assert clasificar(_coef(3, 0))["tipo"] == "parábola"


def test_degenerada() -> None:
    assert clasificar(_coef(0, 0))["tipo"] == "degenerada"


def test_integracion_con_constructor() -> None:
    casos = {
        "11111111-1": "circunferencia",
        "12345678-5": "elipse",
        "23456781-0": "hipérbola",
        "11111233-9": "parábola",
    }
    for rut, esperado in casos.items():
        coef = construir_ecuacion(rut)["coeficientes_frac"]
        assert clasificar(coef)["tipo"] == esperado, rut


def _correr_todos() -> None:
    pruebas = [
        test_circunferencia, test_elipse, test_hiperbola,
        test_parabola, test_degenerada, test_integracion_con_constructor,
    ]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")


if __name__ == "__main__":
    _correr_todos()
