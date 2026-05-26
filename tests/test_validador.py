"""Pruebas manuales del validador de RUT.

Ejecutar con:  python tests/test_validador.py
Si no se imprime ningún error, todas las pruebas pasan.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rut.parser import parsear_rut
from src.rut.validador import calcular_dv, validar_rut


def _esperar_error(entrada: str) -> None:
    try:
        parsear_rut(entrada)
    except ValueError:
        return
    raise AssertionError(f"Se esperaba ValueError para entrada: {entrada!r}")


def test_parser_acepta_formatos_validos() -> None:
    assert parsear_rut("12345678-5") == ("12345678", "5")
    assert parsear_rut("  12345678-5  ") == ("12345678", "5")
    assert parsear_rut("12345670-k") == ("12345670", "K")
    assert parsear_rut("12345670-K") == ("12345670", "K")
    assert parsear_rut("9999999-3") == ("9999999", "3")


def test_parser_rechaza_formatos_invalidos() -> None:
    _esperar_error("")
    _esperar_error("   ")
    _esperar_error("12.345.678-5")
    _esperar_error("123456789")
    _esperar_error("12345678 5")
    _esperar_error("abc-1")
    _esperar_error("12345678-AB")
    _esperar_error("123456-7")
    _esperar_error("123456789-0")


def test_calcular_dv_casos_conocidos() -> None:
    assert calcular_dv("12345678")[0] == "5"
    assert calcular_dv("11111111")[0] == "1"
    assert calcular_dv("23456781")[0] == "0"
    assert calcular_dv("12345670")[0] == "K"
    assert calcular_dv("9999999")[0] == "3"


def test_validar_rut_valido() -> None:
    r = validar_rut("12345678-5")
    assert r["es_valido"] is True
    assert r["dv_calculado"] == "5"
    assert r["digitos"] == {
        "d1": 1, "d2": 2, "d3": 3, "d4": 4,
        "d5": 5, "d6": 6, "d7": 7, "d8": 8,
    }
    assert r["v"] == 5


def test_validar_rut_invalido() -> None:
    r = validar_rut("12345678-9")
    assert r["es_valido"] is False
    assert r["dv_calculado"] == "5"


def test_validar_rut_con_dv_k_y_0() -> None:
    rk = validar_rut("12345670-K")
    assert rk["es_valido"] is True
    assert rk["v"] == 10

    r0 = validar_rut("23456781-0")
    assert r0["es_valido"] is True
    assert r0["v"] == 11


def test_validar_rut_7_digitos_rellena_d1_con_cero() -> None:
    r = validar_rut("9999999-3")
    assert r["es_valido"] is True
    assert r["digitos"]["d1"] == 0
    assert r["digitos"]["d2"] == 9
    assert r["digitos"]["d8"] == 9


def test_traza_incluye_suma_y_resto() -> None:
    r = validar_rut("12345678-5")
    traza = r["traza"]
    assert len(traza["filas"]) == 8
    assert traza["suma_total"] == sum(f["producto"] for f in traza["filas"])
    assert traza["resto"] == traza["suma_total"] % 11


def _correr_todos() -> None:
    pruebas = [
        test_parser_acepta_formatos_validos,
        test_parser_rechaza_formatos_invalidos,
        test_calcular_dv_casos_conocidos,
        test_validar_rut_valido,
        test_validar_rut_invalido,
        test_validar_rut_con_dv_k_y_0,
        test_validar_rut_7_digitos_rellena_d1_con_cero,
        test_traza_incluye_suma_y_resto,
    ]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")


if __name__ == "__main__":
    _correr_todos()
