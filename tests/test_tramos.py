"""Pruebas del constructor y motor de límites de funciones por tramos.

Ejecutar:  python3 tests/test_tramos.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tramos.constructor import construir_funcion
from src.tramos.limites import analizar_limites
from src.tramos.tablas import generar_tabla_valores


def test_caso_infinita_12345678_5() -> None:
    # d8 = 8 -> 8 % 3 = 2 -> infinita
    # d3 = 3 -> a = 3
    r = construir_funcion("12345678-5")
    assert r["tipo"] == "infinita"
    assert r["a"] == 3
    
    lim = analizar_limites(r)
    assert lim["limite_izquierdo"] == "-infinito"
    assert lim["limite_derecho"] == "+infinito"
    assert lim["existe_limite"] is False
    assert "Discontinuidad INFINITA" in lim["conclusion"]


def test_caso_salto_12345677_7() -> None:
    # d8 = 7 -> 7 % 3 = 1 -> salto
    # d3 = 3 -> a = 3
    # d2 = 2, d4 = 4
    # Rama izq (x < 3): x + 2 -> lim_izq = 5
    # Rama der (x >= 3): x + 4 -> lim_der = 7
    r = construir_funcion("12345677-7")
    assert r["tipo"] == "salto"
    assert r["a"] == 3
    
    lim = analizar_limites(r)
    assert lim["limite_izquierdo"] == 5
    assert lim["limite_derecho"] == 7
    assert lim["existe_limite"] is False
    assert "Discontinuidad de SALTO FINITO" in lim["conclusion"]


def test_caso_removible_12345676_9() -> None:
    # d8 = 6 -> 6 % 3 = 0 -> removible
    # d3 = 3 -> a = 3
    # d1 = 1
    # f(x) = (x - 3)(x + 1) / (x - 3) -> lim = 3 + 1 = 4
    r = construir_funcion("12345676-9")
    assert r["tipo"] == "removible"
    assert r["a"] == 3
    
    lim = analizar_limites(r)
    assert lim["limite_izquierdo"] == 4
    assert lim["limite_derecho"] == 4
    assert lim["existe_limite"] is True
    assert "Discontinuidad REMOVIBLE" in lim["conclusion"]


def test_generar_tabla() -> None:
    r = construir_funcion("12345678-5")
    tabla = generar_tabla_valores(r)
    assert len(tabla["pasos"]) > 0


def _correr_todos() -> None:
    pruebas = [
        test_caso_infinita_12345678_5,
        test_caso_salto_12345677_7,
        test_caso_removible_12345676_9,
        test_generar_tabla,
    ]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")


if __name__ == "__main__":
    _correr_todos()
