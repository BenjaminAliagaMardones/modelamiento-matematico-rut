"""Pruebas de la transformación general <-> canónica.

Ejecutar:  /usr/bin/python3 tests/test_canonica.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conicas.algebra import Fraccion
from src.conicas.canonica import canonica_a_general, general_a_canonica
from src.conicas.clasificador import clasificar
from src.conicas.constructor import construir_ecuacion

# RUTs válidos que producen cada tipo con puntos reales.
CASOS = {
    "10010108-4": "circunferencia",
    "10020104-6": "elipse",
    "23456781-0": "hipérbola",
    "11111233-9": "parábola",
}


def _es_proporcional(orig: dict, rec: dict) -> bool:
    "Verifica que rec = lambda * orig coeficiente a coeficiente."
    lam = None
    for k in "ABCDE":
        o, r = orig[k], rec[k]
        if o.es_cero() and r.es_cero():
            continue
        if o.es_cero() or r.es_cero():
            return False
        ratio = r / o
        if lam is None:
            lam = ratio
        elif not (ratio == lam):
            return False
    return lam is not None and not lam.es_cero()


def test_clasificacion_de_casos() -> None:
    for rut, tipo in CASOS.items():
        coef = construir_ecuacion(rut)["coeficientes_frac"]
        assert clasificar(coef)["tipo"] == tipo, rut


def test_roundtrip_proporcional() -> None:
    for rut, tipo in CASOS.items():
        coef = construir_ecuacion(rut)["coeficientes_frac"]
        can = general_a_canonica(coef, tipo)
        inv = canonica_a_general(can["parametros"], tipo)
        assert _es_proporcional(coef, inv["coeficientes"]), rut


def test_circunferencia_centro_y_radio() -> None:
    coef = construir_ecuacion("10010108-4")["coeficientes_frac"]
    p = general_a_canonica(coef, "circunferencia")["parametros"]
    assert p["h"] == Fraccion(2)
    assert p["k"] == Fraccion(16)
    assert p["r2"] == Fraccion(256)
    assert abs(p["r"] - 16) < 1e-9


def test_parabola_vertice_y_orientacion() -> None:
    coef = construir_ecuacion("11111233-9")["coeficientes_frac"]
    p = general_a_canonica(coef, "parábola")["parametros"]
    assert p["orientacion"] == "horizontal"
    assert p["h"] == Fraccion(-23, 2)
    assert p["k"] == Fraccion(27, 2)


def test_pasos_no_vacios() -> None:
    for rut, tipo in CASOS.items():
        coef = construir_ecuacion(rut)["coeficientes_frac"]
        can = general_a_canonica(coef, tipo)
        inv = canonica_a_general(can["parametros"], tipo)
        assert len(can["pasos"]) >= 4, rut
        assert len(inv["pasos"]) >= 3, rut
        assert "Forma canónica" in "\n".join(can["pasos"]) or can["forma_canonica"]


def _correr_todos() -> None:
    pruebas = [
        test_clasificacion_de_casos,
        test_roundtrip_proporcional,
        test_circunferencia_centro_y_radio,
        test_parabola_vertice_y_orientacion,
        test_pasos_no_vacios,
    ]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")


if __name__ == "__main__":
    _correr_todos()
