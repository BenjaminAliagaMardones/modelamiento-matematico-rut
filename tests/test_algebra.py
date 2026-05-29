"""Pruebas de las utilidades matemáticas manuales.

Ejecutar:  /usr/bin/python3 tests/test_algebra.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conicas.algebra import Fraccion, raiz_cuadrada, fmt_frac_dec


def test_fraccion_normaliza() -> None:
    assert str(Fraccion(2, 4)) == "1/2"
    assert str(Fraccion(6, 3)) == "2"
    assert str(Fraccion(-2, 4)) == "-1/2"
    assert str(Fraccion(2, -4)) == "-1/2"


def test_fraccion_operaciones() -> None:
    assert Fraccion(1, 2) + Fraccion(1, 3) == Fraccion(5, 6)
    assert Fraccion(1, 2) - Fraccion(1, 3) == Fraccion(1, 6)
    assert Fraccion(2, 3) * Fraccion(3, 4) == Fraccion(1, 2)
    assert Fraccion(2, 3) / Fraccion(4, 3) == Fraccion(1, 2)
    assert 2 + Fraccion(1, 2) == Fraccion(5, 2)
    assert -Fraccion(3, 5) == Fraccion(-3, 5)


def test_fraccion_signo_y_decimal() -> None:
    assert Fraccion(3, 5).signo() == 1
    assert Fraccion(-3, 5).signo() == -1
    assert Fraccion(0).signo() == 0
    assert Fraccion(0).es_cero()
    assert abs(Fraccion(3, 5).a_decimal() - 0.6) < 1e-12


def test_raiz_cuadrada() -> None:
    assert abs(raiz_cuadrada(4) - 2) < 1e-9
    assert abs(raiz_cuadrada(2) - 1.41421356237) < 1e-9
    assert raiz_cuadrada(0) == 0.0
    assert abs(raiz_cuadrada(9.8) ** 2 - 9.8) < 1e-9
    try:
        raiz_cuadrada(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("Se esperaba ValueError con raíz de negativo")


def test_fmt_frac_dec() -> None:
    assert fmt_frac_dec(Fraccion(16)) == "16"
    assert fmt_frac_dec(Fraccion(49, 5)) == "49/5 = 9.8"


def _correr_todos() -> None:
    pruebas = [
        test_fraccion_normaliza,
        test_fraccion_operaciones,
        test_fraccion_signo_y_decimal,
        test_raiz_cuadrada,
        test_fmt_frac_dec,
    ]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")


if __name__ == "__main__":
    _correr_todos()
