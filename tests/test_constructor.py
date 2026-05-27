"""Pruebas del constructor de la ecuación general.

Ejecutar:  python3 tests/test_constructor.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conicas.constructor import construir_ecuacion


def _coef(rut: str) -> dict:
    return construir_ecuacion(rut)["coeficientes"]


def test_rechaza_rut_invalido() -> None:
    try:
        construir_ecuacion("12345678-9")
    except ValueError:
        return
    raise AssertionError("Se esperaba ValueError con RUT inválido")


def test_caso_sin_reglas_12345678_5() -> None:
    r = construir_ecuacion("12345678-5")
    c = r["coeficientes"]
    assert abs(c["A"] - 3 / 5) < 1e-9
    assert abs(c["B"] - 7 / 5) < 1e-9
    assert c["C"] == -11
    assert c["D"] == -15
    assert c["E"] == 16
    assert r["reglas_aplicadas"] == []


def test_circunferencia_11111111_1() -> None:
    r = construir_ecuacion("11111111-1")
    c = r["coeficientes"]
    assert c["A"] == c["B"] != 0
    assert "d1 == d2 (B = A)" in r["reglas_aplicadas"]
    assert "d8 impar (B = -B)" in r["reglas_aplicadas"]


def test_hiperbola_23456781_0() -> None:
    r = construir_ecuacion("23456781-0")
    c = r["coeficientes"]
    assert c["A"] > 0 and c["B"] < 0
    assert "d8 impar (B = -B)" in r["reglas_aplicadas"]


def test_parabola_eje_horizontal_11111233_9() -> None:
    r = construir_ecuacion("11111233-9")
    c = r["coeficientes"]
    assert c["A"] == 0
    assert c["B"] != 0
    assert "parábola eje horizontal (A = 0)" in r["reglas_aplicadas"]


def test_pasos_contienen_secciones_clave() -> None:
    r = construir_ecuacion("12345678-5")
    texto = "\n".join(r["pasos"])
    assert "Dígitos extraídos" in texto
    assert "Valor auxiliar v" in texto
    assert "A = (d1 + d2) / v" in texto
    assert "Aplicación de reglas de ajuste" in texto
    assert "Ecuación general resultante" in texto


def test_ecuacion_string_formato() -> None:
    r = construir_ecuacion("12345678-5")
    assert r["ecuacion"] == "0.6x² + 1.4y² - 11x - 15y + 16 = 0"


def _correr_todos() -> None:
    pruebas = [
        test_rechaza_rut_invalido,
        test_caso_sin_reglas_12345678_5,
        test_circunferencia_11111111_1,
        test_hiperbola_23456781_0,
        test_parabola_eje_horizontal_11111233_9,
        test_pasos_contienen_secciones_clave,
        test_ecuacion_string_formato,
    ]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")


if __name__ == "__main__":
    _correr_todos()
